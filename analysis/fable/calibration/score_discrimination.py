"""Score a development discrimination screen under the protocol's fixed-denominator rules
(§4.3; Astra 0.6 review §1). Recomputes D and both p bounds at full precision from the
archived T_k.csv files with the estimator in e2e_benchmark.py, and classifies each intended
trial with its `outcome` rule; an intended trial with no completed record is `missing`.

Null gate: every non-accept counts as a rejection. Power: only `reject` is a detection.
The raw logged p (lower bound, shortfalls ignored) is kept as a diagnostic.

Usage: python score_discrimination.py RUNDIR N_INTENDED OUTCSV ARM [ARM ...]
"""
import csv, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_benchmark import p_bounds, outcome, ALPHA

OUTCOMES = ("reject", "accept", "indet_calib", "indet_obsfit", "indet_straddle", "indet_cov", "missing")


def main():
    rundir, n_int, outcsv, arms = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4:]
    rows, summary = [], {}
    for arm in arms:
        res = json.load(open(os.path.join(rundir, arm, "e2e_results.json")))
        R = res["meta"]["R_train"]
        logged = {r["outer"]: r for r in res["outer"]}
        counts = dict.fromkeys(OUTCOMES, 0)
        raw_reject = 0
        for k in range(n_int):
            row = {"arm": arm, "outer": k}
            tpath = os.path.join(rundir, arm, f"T_{k}.csv")
            if k not in logged or not os.path.exists(tpath):
                row["outcome"] = "missing"; counts["missing"] += 1; rows.append(row); continue
            lg = logged[k]
            T = np.genfromtxt(tpath, delimiter=",", names=True)
            s = p_bounds(np.column_stack([T["T1"], T["T2"], T["T3"], T["T4"]]), R)
            row |= {"shortfall": lg["shortfall"], "max_lib_dist": lg["max_lib_dist"],
                    "raw_p": lg["p"]} | {x: s.get(x, "") for x in
                                        ("train_fail", "test_fail", "cond", "D_obs", "p_lo", "p_hi")}
            if isinstance(lg["p"], float) and lg["p"] < ALPHA:
                raw_reject += 1
            if s["status"] == "ok" and abs(s["p_lo"] - lg["p"]) > 1e-12:
                raise SystemExit(f"{arm} outer {k}: recomputed p {s['p_lo']} != logged {lg['p']}")
            row["outcome"] = outcome(lg["shortfall"], s); counts[row["outcome"]] += 1; rows.append(row)
        counts["raw_p_below_alpha"] = raw_reject
        counts["null_gate_count"] = n_int - counts["accept"]
        counts["detections"] = counts["reject"]
        summary[arm] = counts
    keys = ["arm", "outer", "outcome", "shortfall", "raw_p", "p_lo", "p_hi", "D_obs",
            "train_fail", "test_fail", "cond", "max_lib_dist"]
    with open(outcsv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in keys})
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
