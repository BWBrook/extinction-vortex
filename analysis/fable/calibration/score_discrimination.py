"""Score runs under the protocol's fixed-denominator rules (§4.3). Recomputes D and both p
bounds at full precision from each trial's T file and classifies every intended trial; an
intended trial with no completed record is `missing`.

Input contracts (FORMAT):
  v1  archived hard-tolerance runs (discrimination_v1): DIR/e2e_results.json with fields
      outer, shortfall, max_lib_dist, p (lower bound, diagnostic); T files have columns
      set, T1-T4, failed. A shortfall makes the trial indet_calib.
  v2  k-NN runs written by e2e_benchmark.py up to f8546ec (power_screen_v1,
      dev_screen200_v1): DIR/e2e_rows.jsonl keyed by `outer`, DIR/e2e_meta.json, T_<outer>.csv.
  v3  current e2e_benchmark.py (run_chunk): rows keyed by `trial_id`, T_<trial_id>.csv,
      selected-draw provenance, and indet_sampling rows (no fits) for budget failures.
In v2 and v3 the logged p_lo, p_hi (finite) and outcome must match the recomputation.
Malformed T files (ragged, or not exactly sets 0..2R in order) are indet_malformed. An absent
directory, results file or checkpoint, or an unparseable row, leaves trials `missing`;
duplicate trial keys are refused.

Fit-failure accounting (v2/v3): per trial with a usable T file, the failed datasets are those
with any missing T1-T4 among its 2R+1 (observed, training, test); a malformed or missing T
file after a sampled trial counts all 2R+1 as failed; indet_sampling trials have no fits and
are excluded from both numerator and denominator.

Null gate: every non-accept counts as a rejection. Power: only `reject` is a detection.

Usage: python score_discrimination.py FORMAT RUNDIR N_INTENDED OUTCSV ARM [ARM ...]
(intended trial keys 0..N_INTENDED-1 in every ARM directory)
"""
import csv, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_benchmark import p_bounds, outcome, read_T, ALPHA

OUTCOMES = ("reject", "accept", "indet_calib", "indet_sampling", "indet_malformed", "indet_obsfit",
            "indet_train", "indet_cov", "indet_straddle", "missing")


def read_T_v1(path, R):
    try:
        T = np.genfromtxt(path, delimiter=",", names=True)
    except ValueError:
        return None
    if T.ndim != 1 or len(T) != 2 * R + 1 or not np.array_equal(T["set"], np.arange(2 * R + 1)):
        return None
    return np.column_stack([T["T1"], T["T2"], T["T3"], T["T4"]])


def load_dir(fmt, d):
    """R and the logged rows by trial key; (None, {}) when the records are absent."""
    if fmt == "v1":
        if not os.path.exists(os.path.join(d, "e2e_results.json")):
            return None, {}
        res = json.load(open(os.path.join(d, "e2e_results.json")))
        return res["meta"]["R_train"], {r["outer"]: r for r in res["outer"]}
    if not (os.path.exists(os.path.join(d, "e2e_meta.json")) and os.path.exists(os.path.join(d, "e2e_rows.jsonl"))):
        return None, {}
    key = "outer" if fmt == "v2" else "trial_id"
    rows = {}
    for line in open(os.path.join(d, "e2e_rows.jsonl")):
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r[key] in rows:
            raise SystemExit(f"{d}: duplicate trial {r[key]}")
        rows[r[key]] = r
    return json.load(open(os.path.join(d, "e2e_meta.json")))["R_train"], rows


def score_dir(fmt, d, intended):
    """Per-trial rows, outcome counts and fit-failure totals for the intended trial keys."""
    R, logged = load_dir(fmt, d)
    counts = dict.fromkeys(OUTCOMES, 0)
    rows, raw_reject, fail_num, fail_den = [], 0, 0, 0
    for k in intended:
        row = {"trial": k}
        if k not in logged:
            row["outcome"] = "missing"; counts["missing"] += 1; rows.append(row); continue
        lg = logged[k]
        if fmt == "v3" and lg.get("outcome") == "indet_sampling":
            if not lg.get("sampling_failed"):
                raise SystemExit(f"{d} trial {k}: indet_sampling without failed populations")
            row |= {"outcome": "indet_sampling", "sampling_failed": ";".join(lg["sampling_failed"])}
            counts["indet_sampling"] += 1; rows.append(row); continue
        tpath = os.path.join(d, f"T_{k}.csv")
        if fmt == "v1":
            s = p_bounds(read_T_v1(tpath, R) if os.path.exists(tpath) else None, R)
            shortfall, diag = lg["shortfall"], lg["p"]
            row |= {"shortfall": shortfall, "dist": lg["max_lib_dist"]}
        else:
            T = read_T(tpath, R) if os.path.exists(tpath) else None
            s = p_bounds(None if T is None else T[0], R)
            shortfall, diag = "", lg["p_diagnostic"]
            row |= {"dist": lg["kth_dist"], "fallback": lg.get("fallback", "")}
            fail_den += 2 * R + 1
            fail_num += (2 * R + 1) if T is None else int(np.nansum(T[1]))
        row |= {"raw_p": diag} | {x: s.get(x, "") for x in
                                  ("train_fail", "test_fail", "cond", "D_obs", "p_lo", "p_hi")}
        if isinstance(diag, float) and diag < ALPHA:
            raw_reject += 1
        oc = outcome(s, shortfall)
        if s["status"] == "ok":
            bounds = {"p_lo": lg["p"]} if fmt == "v1" else {"p_lo": lg.get("p_lo"), "p_hi": lg.get("p_hi")}
            for key, v in bounds.items():
                if not (isinstance(v, float) and np.isfinite(v)) or abs(s[key] - v) > 1e-12:
                    raise SystemExit(f"{d} trial {k}: recomputed {key} {s[key]} does not match logged {v!r}")
        if fmt != "v1" and oc != lg["outcome"]:
            raise SystemExit(f"{d} trial {k}: recomputed outcome {oc} != logged {lg['outcome']}")
        row["outcome"] = oc; counts[oc] += 1; rows.append(row)
    counts["raw_p_below_alpha"] = raw_reject
    counts["null_gate_count"] = len(intended) - counts["accept"]
    counts["detections"] = counts["reject"]
    return rows, counts, {"failed_datasets": fail_num, "fitted_datasets": fail_den}


def main():
    fmt, rundir, n_int, outcsv, arms = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5:]
    assert fmt in ("v1", "v2", "v3")
    rows, summary = [], {}
    for arm in arms:
        r, counts, fails = score_dir(fmt, os.path.join(rundir, arm), range(n_int))
        rows += [x | {"arm": arm} for x in r]
        summary[arm] = counts | (fails if fmt != "v1" else {})
    keys = ["arm", "trial", "outcome", "shortfall", "sampling_failed", "raw_p", "p_lo", "p_hi", "D_obs",
            "train_fail", "test_fail", "fallback", "cond", "dist"]
    with open(outcsv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in keys})
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
