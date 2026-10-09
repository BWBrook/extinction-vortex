"""Score development runs under the protocol's fixed-denominator rules (§4.3). Recomputes D
and both p bounds at full precision from each trial's T_k.csv and classifies every intended
trial; an intended trial with no completed record is `missing`.

Input contracts (FORMAT):
  v1  archived hard-tolerance runs (discrimination_v1): ARM/e2e_results.json with fields
      outer, shortfall, max_lib_dist, p (lower bound, diagnostic); T files have columns
      set, T1-T4, failed. A shortfall makes the trial indet_calib.
  v2  k-NN runs (current e2e_benchmark.py): ARM/e2e_rows.jsonl and ARM/e2e_meta.json; the
      logged p_lo, p_hi and outcome must match the recomputation exactly.
Malformed T files (not exactly sets 0..2R in order) are indet_malformed in both formats.

Null gate: every non-accept counts as a rejection. Power: only `reject` is a detection.

Usage: python score_discrimination.py FORMAT RUNDIR N_INTENDED OUTCSV ARM [ARM ...]
"""
import csv, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_benchmark import p_bounds, outcome, read_T, ALPHA

OUTCOMES = ("reject", "accept", "indet_calib", "indet_malformed", "indet_obsfit", "indet_train",
            "indet_cov", "indet_straddle", "missing")


def read_T_v1(path, R):
    T = np.genfromtxt(path, delimiter=",", names=True)
    if T.ndim != 1 or len(T) != 2 * R + 1 or not np.array_equal(T["set"], np.arange(2 * R + 1)):
        return None
    return np.column_stack([T["T1"], T["T2"], T["T3"], T["T4"]])


def load_arm(fmt, rundir, arm):
    if fmt == "v1":
        res = json.load(open(os.path.join(rundir, arm, "e2e_results.json")))
        return res["meta"]["R_train"], {r["outer"]: r for r in res["outer"]}
    meta = json.load(open(os.path.join(rundir, arm, "e2e_meta.json")))
    rows = [json.loads(x) for x in open(os.path.join(rundir, arm, "e2e_rows.jsonl"))]
    return meta["R_train"], {r["outer"]: r for r in rows}


def main():
    fmt, rundir, n_int, outcsv, arms = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5:]
    assert fmt in ("v1", "v2")
    rows, summary = [], {}
    for arm in arms:
        R, logged = load_arm(fmt, rundir, arm)
        counts = dict.fromkeys(OUTCOMES, 0)
        raw_reject = 0
        for k in range(n_int):
            row = {"arm": arm, "outer": k}
            tpath = os.path.join(rundir, arm, f"T_{k}.csv")
            if k not in logged or not os.path.exists(tpath):
                row["outcome"] = "missing"; counts["missing"] += 1; rows.append(row); continue
            lg = logged[k]
            if fmt == "v1":
                s = p_bounds(read_T_v1(tpath, R), R)
                shortfall, diag = lg["shortfall"], lg["p"]
                row |= {"shortfall": shortfall, "dist": lg["max_lib_dist"]}
            else:
                T = read_T(tpath, R)
                s = p_bounds(None if T is None else T[0], R)
                shortfall, diag = "", lg["p_diagnostic"]
                row |= {"dist": lg["kth_dist"], "fallback": lg.get("fallback", "")}
            row |= {"raw_p": diag} | {x: s.get(x, "") for x in
                                      ("train_fail", "test_fail", "cond", "D_obs", "p_lo", "p_hi")}
            if isinstance(diag, float) and diag < ALPHA:
                raw_reject += 1
            oc = outcome(s, shortfall)
            if s["status"] == "ok" and abs(s["p_lo"] - (lg["p"] if fmt == "v1" else lg["p_lo"])) > 1e-12:
                raise SystemExit(f"{arm} outer {k}: recomputed p_lo {s['p_lo']} differs from the log")
            if fmt == "v2" and oc != lg["outcome"]:
                raise SystemExit(f"{arm} outer {k}: recomputed outcome {oc} != logged {lg['outcome']}")
            row["outcome"] = oc; counts[oc] += 1; rows.append(row)
        counts["raw_p_below_alpha"] = raw_reject
        counts["null_gate_count"] = n_int - counts["accept"]
        counts["detections"] = counts["reject"]
        summary[arm] = counts
    keys = ["arm", "outer", "outcome", "shortfall", "raw_p", "p_lo", "p_hi", "D_obs",
            "train_fail", "test_fail", "fallback", "cond", "dist"]
    with open(outcsv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in keys})
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
