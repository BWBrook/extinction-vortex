"""Stage 1a no-fit report (review 1657 §4; report rule bound in the settings). Reads a validated collect.json.
  p2_report.py COLLECT_JSON SETTINGS_JSON OUT_JSON
  p2_report.py tables REPORT_JSON OUT_MD          Markdown tables for the report note
Time to K = 2,000 retained paths per setting, in CPU-hours: observed through the crossing batch where the hit stop was
reached; otherwise a rate-based projection (full-stream hits/proposals and CPU per proposal), with an interval from the
setting's suffix retention interval (formal for completed settings, sensitivity-only for censored ones). Zero-hit settings
are unresolved; their lower bound uses the one-sided 3/N retention bound. A setting censored before any proposal has no
exposure and is excluded from cost means (reported separately). Stage 1b inventory: the planned noisy design is
9 populations x 4 scenarios x n in {30, 300} x 200 outers, plus one n = 0 control per population-outer pair. Each cell's
cost is scaled from its 10 pilot outers (mean x 200), with a bootstrap over those outers; the pilot outers' own hits
count toward their libraries. Projections only: not measured costs and not validation evidence."""
import json, sys
import numpy as np

K, OUTERS_1B, BOOT = 2000, 200, 4000
POPS = ("wild_dog", "marmot", "ms_woodpecker", "rc_woodpecker", "golden_plover", "whooping_crane", "hawaiian_crow",
        "wood_turtle_A", "wood_turtle_B")
SCEN = ("null_prior_predictive", "null_low_s", "MA_betamin", "MA_d10_0.5")


def cost(r):
    """(kind, point, lo, hi) CPU-hours to K retained paths for one setting."""
    cpp = r["cpu_seconds"] / r["proposals"] / 3600 if r["proposals"] else None
    if r.get("stop") == "hits":
        t = r["observed_cpu_hours_to_crossing_batch"]; return "observed", t, t, t
    if not r["hits"]:
        lb = K / (3.0 / r["proposals"]) * cpp if cpp else None
        return "unresolved", None, lb, None
    rate = r["hits"] / r["proposals"]; iv = r.get("ci95_suffix") or r.get("sensitivity_interval95_suffix")
    lo = K / iv[1] * cpp if iv and iv[1] > 0 else None
    hi = K / iv[0] * cpp if iv and iv[0] > 0 else None
    return ("projected" if r["status"] == "complete" else "projected_censored"), K / rate * cpp, lo, hi


def q(v, ps=(0, 0.1, 0.25, 0.5, 0.75, 0.9, 1)):
    v = np.sort(np.array([x for x in v if x is not None], float))
    return {"n": int(len(v)), **({f"q{int(p * 100)}": float(np.quantile(v, p)) for p in ps} if len(v) else {})}


def main(collect_json, settings_json, out):
    c = json.load(open(collect_json)); b = json.load(open(settings_json))
    if not c["collection_ok"]:
        raise SystemExit("collection not ok")
    rows = c["rows"]
    for r in rows:
        r["_kind"], r["_t"], r["_lo"], r["_hi"] = cost(r)
    rep = {"scope": __doc__, "collect_binding": c["binding"], "status": c["status"], "run_complete": c["run_complete"],
           "provenance_complete": c["provenance_complete"]}
    rep["exposure"] = {"proposals": sum(r["proposals"] for r in rows), "paths": sum(r["paths"] for r in rows),
                       "selected_SA": sum(r["selected_SA"] for r in rows), "hits": sum(r["hits"] for r in rows),
                       "boundary_hits": sum(r["boundary"] for r in rows),
                       "worker_cpu_hours": sum(r["cpu_seconds"] for r in rows) / 3600,
                       "planned_proposals": sum(s["proposal_budget"] for s in b["settings"]),
                       "peak_rss_gib": max(w["peak_rss_gib"] for w in c["workers"]),
                       "hosts": len({w["host"] for w in c["workers"]})}
    wall = {}
    for r in rows:
        wall[r["worker"]] = wall.get(r["worker"], 0.0) + r["wall_seconds"]
    jobs = {}
    for w, sec in wall.items():
        jobs[w // 8] = max(jobs.get(w // 8, 0.0), sec)
    rep["allocation_estimate"] = {"node_jobs": len(jobs), "job_busy_hours": q([v / 3600 for v in jobs.values()]),
                                  "node_cpu_h_lower_estimate": sum(8 * v for v in jobs.values()) / 3600,
                                  "note": "8 x the slowest worker's sampling wall time per job; excludes setup and the collector; "
                                          "PBS accounting (resources_used.walltime) is authoritative"}
    rep["stops"] = {f"n={n}": {k: sum(1 for r in rows if r["n"] == n and (r["status"], r.get("stop")) == v)
                               for k, v in (("hit_stop", ("complete", "hits")), ("budget", ("complete", "budget")),
                                            ("censored", ("censored", None)))} for n in (0, 30, 300)}
    rep["censored"] = [{k: r[k] for k in ("index", "pop", "outer", "n", "worker", "proposals", "proposal_budget", "hits")}
                       for r in rows if r["status"] == "censored"]
    rep["zero_hit"] = [{k: r[k] for k in ("index", "pop", "outer", "n", "status", "proposals")} | {"cpu_h_lower_bound": r["_lo"]}
                       for r in rows if not r["hits"]]
    rep["throughput_realised_over_smoke"] = q([r["proposals"] / r["cpu_seconds"] / b["settings"][r["index"]]["proposal_budget"]
                                               * b["settings"][r["index"]]["expected_seconds"] for r in rows if r["cpu_seconds"] > 0
                                               and r["status"] == "complete"])
    rep["retention_per_proposal"] = {p: {f"n={n}": q([r["hits"] / r["proposals"] for r in rows if r["pop"] == p and r["n"] == n
                                                      and r["proposals"]]) for n in (0, 30, 300)} for p in POPS}
    rep["cpu_hours_to_K"] = {
        "by_n": {f"n={n}": q([r["_t"] for r in rows if r["n"] == n]) for n in (0, 30, 300)},
        "by_pop_n": {p: {f"n={n}": q([r["_t"] for r in rows if r["pop"] == p and r["n"] == n]) for n in (0, 30, 300)} for p in POPS},
        "by_scenario_n": {s: {f"n={n}": q([r["_t"] for r in rows if r["outer"].startswith(s + "/") and r["n"] == n])
                              for n in (0, 30, 300)} for s in SCEN},
        "kinds": {k: sum(1 for r in rows if r["_kind"] == k) for k in ("observed", "projected", "projected_censored", "unresolved")}}
    rep["most_expensive"] = [{k: r[k] for k in ("index", "pop", "outer", "n", "hits", "proposals", "status")} |
                             {"cpu_h": r["_t"], "interval": [r["_lo"], r["_hi"]], "kind": r["_kind"]}
                             for r in sorted((r for r in rows if r["_t"] is not None), key=lambda r: -r["_t"])[:15]]
    # complete-nine-population availability: a (scenario, trial, n) dataset needs all nine populations' libraries
    avail = {}
    for n in (30, 300):
        sets = []
        for s in SCEN:
            for t in range(10):
                rs = [next(r for r in rows if r["pop"] == p and r["outer"] == f"{s}/{t}" and r["n"] == n) for p in POPS]
                worst = None if any(r["_t"] is None for r in rs) else max(r["_t"] for r in rs)
                sets.append({"outer": f"{s}/{t}", "reached_K": sum(r.get("stop") == "hits" for r in rs),
                             "max_pop_cpu_h": worst, "sum_cpu_h": None if worst is None else sum(r["_t"] for r in rs),
                             "unresolved_pops": [r["pop"] for r in rs if r["_t"] is None]})
        avail[f"n={n}"] = {"complete_at_pilot_budget": sum(x["reached_K"] == 9 for x in sets),
                           "within_cap": {f"{cap}h": sum(x["max_pop_cpu_h"] is not None and x["max_pop_cpu_h"] <= cap for x in sets)
                                          for cap in (5, 10, 25, 50, 100, 250, 500, 1000)},
                           "unresolved_datasets": sum(x["max_pop_cpu_h"] is None for x in sets), "datasets": sets}
    rep["nine_population_availability"] = avail
    # Stage 1b inventory: scale each (pop, scenario, n) cell's 10 pilot outers to 200; bootstrap over outers
    rng = np.random.default_rng([20261016, 1])
    cells, boot = [], np.zeros(BOOT)
    for p in POPS:
        for s in SCEN:
            for n in (0, 30, 300):
                rs = [r for r in rows if r["pop"] == p and r["outer"].startswith(s + "/") and r["n"] == n]
                vals = [r["_t"] if r["_t"] is not None else r["_lo"] for r in rs]               # unresolved: lower bound
                t = np.array([v for v in vals if v is not None], float)                        # no exposure: excluded
                done = sum(min(r["hits"], K) for r in rs)
                cells.append({"pop": p, "scenario": s, "n": n, "pilot_outers": len(rs), "no_exposure": int(sum(v is None for v in vals)),
                              "unresolved": int(sum(r["_t"] is None for r in rs) - sum(v is None for v in vals)),
                              "mean_cpu_h": float(t.mean()), "max_cpu_h": float(t.max()), "cpu_h_200_outers": float(t.mean() * OUTERS_1B),
                              "pilot_hits_counted": done})
                boot += t[rng.integers(0, len(t), (BOOT, len(t)))].mean(1) * OUTERS_1B
    tot = {n: sum(x["cpu_h_200_outers"] for x in cells if x["n"] == n) for n in (0, 30, 300)}
    rep["stage1b_inventory"] = {
        "design": "9 pops x 4 scenarios x n in {30, 300} x 200 outers (14,400 noisy population-outer-cells) + 7,200 n = 0 controls",
        "cpu_h_by_n": tot, "cpu_h_total": sum(tot.values()),
        "bootstrap_total_q": {f"q{int(p * 100)}": float(np.quantile(boot, p)) for p in (0.05, 0.5, 0.95)},
        "unresolved_settings_at_lower_bound": sum(x["unresolved"] for x in cells),
        "top_cells": sorted(cells, key=lambda x: -x["cpu_h_200_outers"])[:12], "cells": cells,
        "note": "projections from 10 pilot outers per cell; heavy tails make the mean and the total uncertain; "
                "zero-hit settings enter at their lower bound, so the total is not an upper bound"}
    json.dump(rep, open(out, "w"), indent=1)
    print(json.dumps({k: rep[k] for k in ("status", "exposure", "stops")}, indent=1))
    print("cpu_h_to_K by n", json.dumps(rep["cpu_hours_to_K"]["by_n"]))
    print("kinds", rep["cpu_hours_to_K"]["kinds"])
    print("availability", {k: {kk: v[kk] for kk in ("complete_at_pilot_budget", "within_cap", "unresolved_datasets")} for k, v in avail.items()})
    print("stage1b", {k: rep["stage1b_inventory"][k] for k in ("cpu_h_by_n", "cpu_h_total", "bootstrap_total_q", "unresolved_settings_at_lower_bound")})
    print("top cells", [(x["pop"], x["scenario"], x["n"], round(x["cpu_h_200_outers"])) for x in rep["stage1b_inventory"]["top_cells"][:8]])
    print("throughput realised/smoke", rep["throughput_realised_over_smoke"])
    print("allocation estimate", rep["allocation_estimate"])
    print("zero-hit / no exposure", rep["zero_hit"])


def tables(report_json, out_md):
    r = json.load(open(report_json)); L = []
    f = lambda x: "–" if x is None else (f"{x:.1f}" if x < 100 else f"{x:,.0f}")
    L += ["**CPU-hours to K = 2,000 retained paths per setting** (median [IQR], max over 40 outers; observed or projected)", "",
          "| Population | n = 0 | n = 30 | n = 300 |", "|---|---|---|---|"]
    for p in POPS:
        cells = []
        for n in (0, 30, 300):
            d = r["cpu_hours_to_K"]["by_pop_n"][p][f"n={n}"]
            cells.append(f"{f(d['q50'])} [{f(d['q25'])}–{f(d['q75'])}], {f(d['q100'])}" + (f" ({40 - d['n']} unresolved)" if d["n"] < 40 else ""))
        L.append(f"| {p} | " + " | ".join(cells) + " |")
    L += ["", "| Scenario | n = 0 | n = 30 | n = 300 |", "|---|---|---|---|"]
    for sc in SCEN:
        cells = []
        for n in (0, 30, 300):
            d = r["cpu_hours_to_K"]["by_scenario_n"][sc][f"n={n}"]
            cells.append(f"{f(d['q50'])} [{f(d['q25'])}–{f(d['q75'])}], {f(d['q100'])}")
        L.append(f"| {sc} | " + " | ".join(cells) + " |")
    L += ["", "**Most expensive settings** (CPU-h to K; interval from the suffix retention interval)", "",
          "| Setting | Population | Outer | n | Hits | CPU-h | 95% interval | Kind |", "|---|---|---|---|---|---|---|---|"]
    for x in r["most_expensive"][:10]:
        L.append(f"| {x['index']} | {x['pop']} | {x['outer']} | {x['n']} | {x['hits']} | {f(x['cpu_h'])} | "
                 f"{f(x['interval'][0])}–{f(x['interval'][1])} | {x['kind']} |")
    L += ["", "**Stage 1b inventory by cell** (12 largest; mean of 10 pilot outers x 200)", "",
          "| Population | Scenario | n | Mean CPU-h | Max CPU-h | CPU-h for 200 outers | Unresolved |", "|---|---|---|---|---|---|---|"]
    for x in r["stage1b_inventory"]["top_cells"]:
        L.append(f"| {x['pop']} | {x['scenario']} | {x['n']} | {f(x['mean_cpu_h'])} | {f(x['max_cpu_h'])} | {f(x['cpu_h_200_outers'])} | {x['unresolved']} |")
    open(out_md, "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    if sys.argv[1] == "tables":
        tables(*sys.argv[2:])
    else:
        main(*sys.argv[1:])
