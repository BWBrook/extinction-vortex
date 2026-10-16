"""Stage 1b/1c inventory and pricing from the Stage 1a pilot (no sampling, no fits). Projections only.
  p2_inventory.py REPORT_JSON COLLECT_JSON OUT_JSON
Per-setting cost: projected expected worker CPU-hours to K = 2,000 at observed throughput (s1a_report cost rule);
zero-hit settings at their approximate one-sided lower limit; setting 576 (no exposure) takes its cell's mean.
Each (population, scenario, n) cell scales its 10 pilot outers to 200 (each pilot outer stands for 20).
Caps: a per-setting cap c bounds each setting's charge at c; settings projected above c are expected
failures-to-fill. Independent-library check: per scenario, the pilot outer (trials 0-9) whose n = 300
nine-population summed cost is the lower median ("ordinary") and the largest resolved ("difficult"), all
three n and nine populations: 8 outers x 27 = 216 libraries. Fitting: 0.5 worker CPU-h per analysis (v1/D3
measured 0.34-0.48)."""
import json, sys
import numpy as np

K, SCALE = 2000, 20
POPS = ("wild_dog", "marmot", "ms_woodpecker", "rc_woodpecker", "golden_plover", "whooping_crane", "hawaiian_crow",
        "wood_turtle_A", "wood_turtle_B")
SCEN = ("null_prior_predictive", "null_low_s", "MA_betamin", "MA_d10_0.5")
FIT_CPU_H, CORES = 0.5, 3000


def main(report_json, collect_json, out):
    c = json.load(open(collect_json)); rows = c["rows"]
    rep = json.load(open(report_json))
    sys.path.insert(0, __file__.rsplit("/", 1)[0])
    from p2_report import cost
    t = {}
    for r in rows:
        kind, pt, lo, hi = cost(r)
        t[r["index"]] = pt if pt is not None else lo
    for r in rows:                                       # no exposure: the cell mean of its other outers
        if t[r["index"]] is None:
            same = [t[x["index"]] for x in rows if x["pop"] == r["pop"] and x["n"] == r["n"] and x["index"] != r["index"]
                    and x["outer"].split("/")[0] == r["outer"].split("/")[0] and t[x["index"]] is not None]
            t[r["index"]] = float(np.mean(same))
    spent = sum(r["cpu_seconds"] for r in rows) / 3600
    inv = {"scope": __doc__}
    waves = {"W1 (n = 0 and 30)": (0, 30), "W2 (n = 300)": (300,)}
    gross = {w: SCALE * sum(t[r["index"]] for r in rows if r["n"] in ns) for w, ns in waves.items()}
    inv["gross_by_wave"] = gross; inv["gross_total"] = sum(gross.values()); inv["pilot_worker_cpu_h_spent"] = spent
    inv["additional_total"] = inv["gross_total"] - spent
    caps = {}
    for cap in (100, 250, 500, 1000, 2000, 5000, None):
        k = "uncapped" if cap is None else f"{cap}h"
        caps[k] = {w: {"expected_cpu_h": SCALE * sum(min(t[r["index"]], cap or np.inf) for r in rows if r["n"] in ns),
                       "expected_failures_to_fill": SCALE * sum(1 for r in rows if r["n"] in ns and cap and t[r["index"]] > cap)}
                   for w, ns in waves.items()}
        caps[k]["total_cpu_h"] = sum(v["expected_cpu_h"] for v in caps[k].values())
        caps[k]["total_failures_to_fill_of_21600"] = sum(v["expected_failures_to_fill"] for kk, v in caps[k].items() if kk.startswith("W"))
        caps[k]["datasets_with_a_failure"] = {
            f"n={n}": SCALE * sum(1 for s in SCEN for tr in range(10)
                                  if cap and any(t[r["index"]] > cap for r in rows if r["n"] == n and r["outer"] == f"{s}/{tr}"))
            for n in (30, 300)}
    inv["caps"] = caps
    chk = []
    for s in SCEN:
        sums = []
        for tr in range(10):
            rs = [r for r in rows if r["n"] == 300 and r["outer"] == f"{s}/{tr}"]
            sums.append((sum(t[r["index"]] for r in rs), tr, all(r["hits"] for r in rs)))
        resolved = sorted(x for x in sums if x[2])
        ordinary = sorted(sums)[(len(sums) - 1) // 2][1]; difficult = resolved[-1][1]
        for role, tr in (("ordinary", ordinary), ("difficult", difficult)):
            libs = [r for r in rows if r["outer"] == f"{s}/{tr}"]
            chk.append({"scenario": s, "trial": tr, "role": role, "libraries": len(libs),
                        "cpu_h": sum(t[r["index"]] for r in libs),
                        "cpu_h_by_n": {n: sum(t[r["index"]] for r in libs if r["n"] == n) for n in (0, 30, 300)}})
    inv["independent_library_check"] = {"rule": "per scenario: lower-median and largest resolved n = 300 nine-population "
                                                "summed pilot cost among trials 0-9; all n, all populations",
                                        "outers": chk, "libraries": sum(x["libraries"] for x in chk),
                                        "analyses": 8 * 3, "cpu_h": sum(x["cpu_h"] for x in chk)}
    n_fit = 1600 + 800 + inv["independent_library_check"]["analyses"]
    inv["fitting"] = {"primary_analyses": 2400, "check_analyses": inv["independent_library_check"]["analyses"],
                      "cpu_h_per_analysis": FIT_CPU_H, "cpu_h": n_fit * FIT_CPU_H}
    hits_bytes = sum(r["journal_bytes"] for r in rows) / sum(r["hits"] for r in rows)
    inv["storage"] = {"bytes_per_retained_pair": hits_bytes, "libraries": 21600, "pairs": 21600 * K,
                      "gb_primary": 21600 * K * hits_bytes / 1e9}
    inv["wall_days_at_cores"] = {str(CORES): inv["gross_total"] / CORES / 24}
    json.dump(inv, open(out, "w"), indent=1)
    print("gross by wave", {k: round(v) for k, v in gross.items()}, "total", round(inv["gross_total"]), "additional", round(inv["additional_total"]))
    for k, v in caps.items():
        print(f"cap {k:9s} total {v['total_cpu_h']:>10,.0f}  W1 {v['W1 (n = 0 and 30)']['expected_cpu_h']:>9,.0f} "
              f"W2 {v['W2 (n = 300)']['expected_cpu_h']:>9,.0f}  failures-to-fill {v['total_failures_to_fill_of_21600']:>5} "
              f"datasets with a failure {v['datasets_with_a_failure']}")
    print("library check", [(x["scenario"], x["trial"], x["role"], round(x["cpu_h"])) for x in chk], "total", round(inv["independent_library_check"]["cpu_h"]))
    print("fitting", inv["fitting"], "storage GB", round(inv["storage"]["gb_primary"], 1), "days at 3000 cores", round(inv["wall_days_at_cores"]["3000"], 1))


if __name__ == "__main__":
    main(*sys.argv[1:])
