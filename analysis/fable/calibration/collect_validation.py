"""Assemble validation chunks into the declared scenarios and evaluate the gates (protocol
§4.3; freeze package §6). Every intended trial ID is scored from its chunk (contract v3);
missing trials stay in the denominators, rows outside a chunk's intended IDs are refused,
and duplicates are refused by the scorer.

Gates (fixed sample sizes, no optional stopping):
  null blocks (role "null"): pass iff non-accepts <= 60 of 1,000, i.e. the one-sided upper
    98.75% Clopper-Pearson bound <= 0.08 (Bonferroni over the four); unresolved and missing
    trials count as rejections. Any failure is V-fail.
  power block (role "power"): the O1 power gate passes iff detections >= 224 of 300, i.e. the
    one-sided lower 95% bound >= 0.70; unresolved and missing trials are nondetections.
  fit-failure stop: in any gating (null or power) block, failed / fitted datasets > 0.02
    stops validation (score_discrimination.py defines both counts; sampling failures are
    excluded from both and reported separately). Descriptive blocks report the rate.
  descriptive blocks: detection rate with an exact two-sided 95% interval.
  stress block: rejection-rate bounds with unresolved trials counted as non-rejections
    (lower) and as rejections (upper), each with an exact 95% interval; not a gate.

Usage: python collect_validation.py MANIFEST OUT_JSON
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from score_discrimination import score_dir, load_dir
from compare_nulls import clopper_pearson

NULL_MAX, POWER_MIN, FIT_MAX = 60, 224, 0.02


def ci(k, n, a=0.05):
    lo, hi = clopper_pearson(k, n, a)
    return [k, n, round(k / n, 5), round(lo, 5), round(hi, 5)]


def collect_scenario(s):
    counts, fails = {}, {"failed_datasets": 0, "fitted_datasets": 0}
    for c in s["chunks"]:
        ids = range(*c["trial_ids"])
        _, logged = load_dir("v3", c["dir"])
        extra = set(logged) - set(ids)
        if extra:
            raise SystemExit(f"{c['dir']}: rows outside the chunk's trial IDs: {sorted(extra)[:5]}")
        _, cc, ff = score_dir("v3", c["dir"], ids)
        for k, v in cc.items():
            counts[k] = counts.get(k, 0) + v
        for k in fails:
            fails[k] += ff[k]
    n = s["n_trials"]
    assert sum(counts[k] for k in counts if not k.startswith(("raw", "null_gate", "detections"))) == n
    rate = fails["failed_datasets"] / fails["fitted_datasets"] if fails["fitted_datasets"] else None
    out = {"block": s["block"], "name": s["name"], "role": s["role"], "n": n, "counts": counts,
           "fit_failures": fails | {"rate": rate}}
    rej, acc = counts["reject"], counts["accept"]
    unresolved = n - rej - acc
    if s["role"] == "null":
        out["null_gate"] = {"non_accepts": n - acc, "max_allowed": NULL_MAX, "pass": n - acc <= NULL_MAX,
                            "upper_98.75": round(clopper_pearson(n - acc, n, 0.025)[1], 5)}
    elif s["role"] == "power":
        out["power_gate"] = {"detections": rej, "min_required": POWER_MIN, "pass": rej >= POWER_MIN,
                             "lower_95": round(clopper_pearson(rej, n, 0.10)[0], 5)}
    elif s["role"] == "stress":
        out["stress_bounds"] = {"unresolved": unresolved, "lower": ci(rej, n), "upper": ci(rej + unresolved, n)}
    else:
        out["detection"] = ci(rej, n)
    if s["role"] in ("null", "power"):
        out["fit_stop"] = rate is not None and rate > FIT_MAX
    return out


def main():
    man = json.load(open(sys.argv[1]))
    res = [collect_scenario(s) for s in man["scenarios"]]
    vfail = any(not r["null_gate"]["pass"] for r in res if "null_gate" in r)
    stop = any(r.get("fit_stop") for r in res)
    power = next(r["power_gate"]["pass"] for r in res if "power_gate" in r)
    summary = {"manifest": sys.argv[1], "code_commit": man.get("code_commit"), "v_fail": vfail,
               "fit_stop": stop, "power_gate_pass": power,
               "labels_available": [] if (vfail or stop) else (["O1", "O2"] if power else ["O2", "O3"]),
               "scenarios": res}
    json.dump(summary, open(sys.argv[2], "w"), indent=1)
    print(json.dumps({k: summary[k] for k in ("v_fail", "fit_stop", "power_gate_pass", "labels_available")}))


if __name__ == "__main__":
    main()
