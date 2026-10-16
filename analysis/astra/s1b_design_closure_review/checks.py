"""Bounded saved-data arithmetic for Stage 1b design/report closure; no sampling or fits."""
import contextlib
import hashlib
import importlib.util
import io
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.stats import beta, binom

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "analysis/fable/calibration/v2_dev"
DATA = SRC / "p2/s1a_main"
OUT = Path(__file__).resolve().parent
K, SCALE = 2000, 20
SCEN = ("null_prior_predictive", "null_low_s", "MA_betamin", "MA_d10_0.5")


def read(path):
    return json.loads(path.read_text())


def load(name):
    spec = importlib.util.spec_from_file_location(name, SRC / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


collect = read(DATA / "collect_deep.json")
saved_report = read(DATA / "s1a_report.json")
saved_inv = read(DATA / "s1b_inventory.json")
rows = collect["rows"]
assert len(rows) == 1080 and collect["collection_ok"]

# Independently reconstruct the plug-in costs, retaining which are lower limits.
costs, unresolved, no_exposure = {}, [], []
for row in rows:
    i = row["index"]
    if row.get("stop") == "hits":
        costs[i] = row["observed_cpu_hours_to_crossing_batch"]
    elif row["hits"]:
        costs[i] = K * row["cpu_seconds"] / 3600 / row["hits"]
    elif row["proposals"]:
        upper = -math.expm1(math.log(.05) / row["suffix_proposals"])
        lower = K * row["cpu_seconds"] / row["proposals"] / 3600 / upper
        costs[i] = lower
        unresolved.append({"index": i, "outer": row["outer"], "pop": row["pop"],
                           "expected_cost_lower_limit_cpu_h": lower})
    else:
        no_exposure.append(i)
for row in rows:
    if row["index"] in no_exposure:
        vals = [costs[r["index"]] for r in rows if r["index"] in costs
                and r["pop"] == row["pop"] and r["n"] == row["n"]
                and r["outer"].split("/")[0] == row["outer"].split("/")[0]]
        costs[row["index"]] = sum(vals) / len(vals)

gross_by_n = {str(n): SCALE * sum(costs[r["index"]] for r in rows if r["n"] == n)
              for n in (0, 30, 300)}
gross = sum(gross_by_n.values())
spent = sum(r["cpu_seconds"] for r in rows) / 3600
assert math.isclose(gross, saved_inv["gross_total"], abs_tol=1e-8)
assert math.isclose(gross-spent, saved_inv["additional_total"], abs_tol=1e-8)
assert [r["index"] for r in rows if r.get("stop") == "hits"] == [772]

cap_rows = {}
for cap in (500, 1000, 2000):
    charge = SCALE * sum(min(v, cap) for v in costs.values())
    exceed = SCALE * sum(v > cap for v in costs.values())
    datasets = {str(n): SCALE * sum(any(costs[r["index"]] > cap for r in rows
                                      if r["outer"] == f"{sc}/{t}" and r["n"] == n)
                                 for sc in SCEN for t in range(10)) for n in (30, 300)}
    recorded = saved_inv["caps"][f"{cap}h"]
    assert math.isclose(charge, recorded["total_cpu_h"], abs_tol=1e-8)
    assert exceed == recorded["total_failures_to_fill_of_21600"]
    assert datasets == {k[2:]: v for k, v in recorded["datasets_with_a_failure"].items()}
    cap_rows[str(cap)] = {"plug_in_charge_cpu_h": charge, "plug_in_exceedances": exceed,
                          "plug_in_datasets_exceeding": datasets,
                          "zero_hit_pilot_settings_with_unknown_completion": len(unresolved),
                          "scaled_unknown_zero_hit_settings": SCALE*len(unresolved)}

check_cases, rankings = [], {}
for sc in SCEN:
    rank = []
    for t in range(10):
        rs = [r for r in rows if r["outer"] == f"{sc}/{t}" and r["n"] == 300]
        rank.append((sum(costs[r["index"]] for r in rs), t, all(r["hits"] > 0 for r in rs)))
    ordinary = sorted(rank)[4]
    difficult = max(x for x in rank if x[2])
    rankings[sc] = [{"trial": x[1], "n300_cpu_h": x[0], "resolved": x[2]} for x in sorted(rank)]
    for role, selected in (("ordinary", ordinary), ("difficult", difficult)):
        rs = [r for r in rows if r["outer"] == f"{sc}/{selected[1]}"]
        check_cases.append({"scenario": sc, "trial": selected[1], "role": role,
                            "libraries": len(rs), "n300_resolved": selected[2],
                            "cpu_h": sum(costs[r["index"]] for r in rs),
                            "cpu_h_by_n": {str(n): sum(costs[r["index"]] for r in rs if r["n"] == n)
                                           for n in (0, 30, 300)}})
for expected, recorded in zip(check_cases, saved_inv["independent_library_check"]["outers"]):
    assert all(expected[k] == recorded[k] for k in ("scenario", "trial", "role", "libraries"))
    assert math.isclose(expected["cpu_h"], recorded["cpu_h"], abs_tol=1e-8)
check_by_n = {str(n): sum(c["cpu_h_by_n"][str(n)] for c in check_cases) for n in (0, 30, 300)}

# Exact binomial gate arithmetic; no stochastic samples.
upper = lambda x: 1. if x == 200 else float(beta.ppf(.9875, x+1, 200-x))
lower = lambda x: 0. if x == 0 else float(beta.ppf(.05, x, 201-x))
null_max = max(x for x in range(201) if upper(x) <= .08)
power_min = min(x for x in range(201) if lower(x) >= .70)
assert (null_max, power_min) == (7, 152)

# Replay the two report-only scripts into this audit's owned directory.
reporter, inventory = load("p2_report"), load("p2_inventory")
log = io.StringIO()
with contextlib.redirect_stdout(log):
    reporter.main(str(DATA/"collect_deep.json"), str(SRC/"p2/p2_settings_s1a.json"), str(OUT/"replayed_report.json"))
    reporter.tables(str(OUT/"replayed_report.json"), str(OUT/"replayed_tables.md"))
    inventory.main(str(OUT/"replayed_report.json"), str(DATA/"collect_deep.json"), str(OUT/"replayed_inventory.json"))
assert read(OUT/"replayed_report.json") == saved_report
assert read(OUT/"replayed_inventory.json") == saved_inv
assert (OUT/"replayed_tables.md").read_text() == (DATA/"s1a_tables.md").read_text()
(OUT/"replay.log").write_text(log.getvalue())

receipt = {
    "scope": __doc__, "reviewed_commit": "e11b9b0171463c4b10e1dbce87b67e0949931db7",
    "input_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in [DATA/"collect_deep.json", DATA/"s1a_report.json", DATA/"s1b_inventory.json",
                               SRC/"p2_report.py", SRC/"p2_inventory.py"]},
    "replay_saved_report_inventory_and_tables_identical": True,
    "count_inventory": {"primary_libraries": 9*4*200*3, "primary_retained_pairs": 9*4*200*3*K,
                        "new_population_outer_pairs": 9*4*190, "total_population_outer_pairs": 9*4*200,
                        "check_libraries": 216, "check_retained_pairs": 216*K,
                        "primary_analyses": 2400, "check_analyses": 24,
                        "T_evaluations_primary": 2400*4001, "T_evaluations_all": 2424*4001},
    "gross_cpu_h_by_n": gross_by_n, "gross_cpu_h": gross, "additional_cpu_h": gross-spent,
    "zero_hit_lower_limits": unresolved, "no_exposure_cell_mean_cpu_h": {str(i): costs[i] for i in no_exposure},
    "cap_projection": cap_rows, "check_cases": check_cases, "n300_rankings": rankings,
    "check_cpu_h_by_n": check_by_n, "check_total_cpu_h": sum(check_by_n.values()),
    "primary_plus_check_wave_cpu_h": {"W1": gross_by_n["0"]+gross_by_n["30"]+check_by_n["0"]+check_by_n["30"],
                                       "W2": gross_by_n["300"]+check_by_n["300"]},
    "full_sampling_plus_fitting_cpu_h": gross+sum(check_by_n.values())+2424*.5,
    "gate_math": {"max_null_nonaccepts": null_max, "null_upper_7": upper(7), "null_upper_8": upper(8),
                  "min_detections": power_min, "power_lower_151": lower(151), "power_lower_152": lower(152),
                  "null_pass_probabilities": {str(p): float(binom.cdf(7, 200, p)) for p in (.01,.02,.03,.04,.05,.06)},
                  "power_pass_probabilities": {str(p): float(binom.sf(151,200,p)) for p in (.75,.8,.85)}},
    "paired_resampling_omitted_mean_contribution_cpu_h": SCALE*sum(costs[i] for i in no_exposure),
    "versions": {"python": sys.version.split()[0], "numpy": np.__version__},
}
(OUT/"checks.json").write_text(json.dumps(receipt, indent=2)+"\n")
print(json.dumps({k: receipt[k] for k in ("replay_saved_report_inventory_and_tables_identical", "gross_cpu_h", "additional_cpu_h",
                                         "check_total_cpu_h", "primary_plus_check_wave_cpu_h", "full_sampling_plus_fitting_cpu_h",
                                         "paired_resampling_omitted_mean_contribution_cpu_h")}, indent=2))
