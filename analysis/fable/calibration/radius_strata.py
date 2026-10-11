"""Predeclared radius-stratified rejection rates (protocol 3.4 step 3; freeze package 5) for
validation_v1, plus descriptive p-value deciles and per-population k-th-neighbour radii.
Radius = largest per-population K-th-neighbour distance (as empirical_position.py).
Usage: python radius_strata.py MANIFEST BASE OUT_JSON"""
import json, sys, os
import numpy as np
EDGES = [0.2050, 0.2956, 0.4049, 0.5613]
man = json.load(open(sys.argv[1])); base = sys.argv[2]
out = {"edges": EDGES, "tie_rule": "lower bin", "radius": "max over populations of kth_dist", "scenarios": []}
for s in man["scenarios"]:
    rows = []
    for c in s["chunks"]:
        rows += [json.loads(l) for l in open(os.path.join(base, c["dir"], "e2e_rows.jsonl"))]
    kd = [json.loads(r["kth_dist"]) for r in rows]
    rad = np.array([max(k.values()) for k in kd])
    rej = np.array([r["outcome"] == "reject" for r in rows])
    p = np.array([r["p_hi"] for r in rows], float)
    b = np.searchsorted(EDGES, rad, side="left")
    pops = list(kd[0])
    out["scenarios"].append({
        "block": s["block"], "name": s["name"], "role": s["role"], "n": len(rows),
        "radius_quantiles_10_50_90": [round(float(q), 4) for q in np.quantile(rad, [.1, .5, .9])],
        "by_bin": [{"bin": i + 1, "n": int((b == i).sum()), "reject": int(rej[b == i].sum()),
                    "rate": round(float(rej[b == i].mean()), 4) if (b == i).any() else None} for i in range(5)],
        "p_hi_deciles_counts": np.histogram(p, bins=np.linspace(0, 1, 11))[0].tolist(),
        "median_kth_by_population": {n: round(float(np.median([k[n] for k in kd])), 4) for n in pops},
        "reject_rate_by_argmax_population": {n: [int(sum(1 for k, r in zip(kd, rej) if max(k, key=k.get) == n)),
                                                 int(sum(r for k, r in zip(kd, rej) if max(k, key=k.get) == n))]
                                             for n in pops}})
json.dump(out, open(sys.argv[3], "w"), indent=1)
for s in out["scenarios"]:
    if s["role"] in ("null", "stress"):
        print(s["block"], s["name"], s["radius_quantiles_10_50_90"], [(x["n"], x["reject"]) for x in s["by_bin"]])
        print("   p deciles", s["p_hi_deciles_counts"])
        print("   median kth", s["median_kth_by_population"])
