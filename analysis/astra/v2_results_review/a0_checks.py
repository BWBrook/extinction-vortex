"""Bounded A0 review: deterministic features and stored-summary arithmetic only.

No simulator, bank, fitter, remote resource or empirical statistic is invoked.
Run from any directory: python3 /path/to/a0_checks.py
"""
from __future__ import annotations

import ast
from collections import defaultdict
from datetime import datetime
import gzip
import hashlib
import json
import math
from pathlib import Path
import platform
from zoneinfo import ZoneInfo

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
DEV = ROOT / "analysis/fable/calibration/v2_dev"
PARAMS = ("s", "f", "sigma", "lam_mean")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def isolated_function(path, name):
    """Execute just the inspected numerical function, without source imports."""
    tree = ast.parse(path.read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    namespace = {"np": np}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(path), "exec"), namespace)
    return namespace[name]


def independent_ols(row):
    """Scalar transition construction plus least squares; flat case explicit."""
    x = np.asarray([1.0 / row[t] for t in range(len(row) - 2)])
    d = [math.log(row[t + 1] / row[t]) for t in range(len(row) - 2)]
    dbar = sum(d) / len(d)
    y = np.asarray([(v - dbar) ** 2 for v in d])
    flat = all(v == row[0] for v in row[:-2])
    if flat:
        return np.asarray([0.0, float(y.mean())]), flat
    design = np.column_stack((x, np.ones(len(x))))
    return np.linalg.lstsq(design, y, rcond=None)[0], flat


def main():
    h_features = isolated_function(DEV / "a0_cplus.py", "h_features")
    fixtures = [
        [10, 10, 10, 10, 0],
        [10, 10, 10, 4, 0],
        [40, 20, 10, 4, 1],
        [9, 14, 6, 11, 3, 0],
        [7, 7, 2, 1],
        [7, 3, 0],
    ]
    checks = []
    for i, row in enumerate(fixtures):
        observed, flat = h_features(np.asarray([row]))
        expected, expected_flat = independent_ols(row)
        np.testing.assert_allclose(observed[0], expected, atol=1e-10, rtol=1e-10)
        assert bool(flat[0]) == expected_flat
        checks.append({"fixture": i, "counts": row, "h": observed[0].tolist(),
                       "flat": bool(flat[0]), "max_abs_error": float(np.max(abs(observed[0] - expected)))})
    # The terminal observation must not affect either summary.
    terminal_rows = np.asarray([[40, 20, 10, 4, last] for last in (0, 1, 999)])
    hh, ff = h_features(terminal_rows)
    np.testing.assert_array_equal(hh, np.repeat(hh[:1], 3, axis=0))
    assert not ff.any()
    # Changing the penultimate count changes the last included transition.
    changed, _ = h_features(np.asarray([[40, 20, 10, 8, 0]]))
    assert not np.allclose(changed[0], hh[0])
    # Changing count units scales the slope but not the intercept.
    scaled, _ = h_features(terminal_rows[:1] * 10)
    np.testing.assert_allclose(scaled[0], hh[0] * [10, 1], atol=1e-10, rtol=1e-10)

    a0 = json.loads((DEV / "a0_cplus.json").read_text())
    d1 = json.loads((DEV / "d1c2_summary.json").read_text())
    assert a0["script_sha256"] == sha(DEV / "a0_cplus.py")
    assert a0["manifest_digest"] == d1["manifest_digest"]
    assert a0["K"] == d1["K"] == 2000
    d1_ranks = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    with gzip.open(DEV / "d1c2_trials.jsonl.gz", "rt") as fh:
        for line in fh:
            row = json.loads(line)
            for pop, values in row["pop"].items():
                for p in ("s", "lam_mean"):
                    d1_ranks[row["block"]][pop][p].append(values[p])
    blocks = {}
    all_ratios = []
    rounding_differences = []
    nmeans = nquantiles = nranges = 0
    for block, values in a0["blocks"].items():
        pops = {n: e for n, e in values.items() if n != "_summary"}
        assert len(pops) == 9
        for lab in ("C", "C+"):
            for p in PARAMS:
                means = [e[lab][p + "_rank_mean"] for e in pops.values()]
                assert values["_summary"][lab][p] == [round(min(means), 3), round(max(means), 3)]
                nranges += 1
        ratios = {}
        for pop, e in pops.items():
            baseline = d1["blocks"][block]["per_population"][pop]
            for p in PARAMS:
                assert e["C"][p + "_rank_mean"] == baseline[p + "_rank_mean"]
                nmeans += 1
            for p in ("s", "lam_mean"):
                q = np.quantile(d1_ranks[block][pop][p], [.1, .5, .9])
                a0_q = e["C"][p + "_rank_q10_50_90"]
                d1_q = baseline[p + "_rank_q10_50_90"]
                assert a0_q == q.round(4).tolist()
                assert d1_q == [round(float(v), 4) for v in q]
                if a0_q != d1_q:
                    rounding_differences.append({"block": block, "population": pop, "parameter": p,
                                                 "A0_numpy_round": a0_q, "D1c2_python_round": d1_q})
                nquantiles += 3
            ratios[pop] = e["C+"]["origC_max_dist_q10_50_90"][1] / e["C"]["origC_max_dist_q10_50_90"][1]
        all_ratios.extend(ratios.values())
        blocks[block] = {
            "population_count": len(pops),
            "reported_rank_ranges": values["_summary"],
            "rank_mean_change_by_parameter": {
                p: {"min": min(e["C+"][p + "_rank_mean"] - e["C"][p + "_rank_mean"] for e in pops.values()),
                    "max": max(e["C+"][p + "_rank_mean"] - e["C"][p + "_rank_mean"] for e in pops.values())}
                for p in PARAMS
            },
            "median_max_origC_distance_ratio_Cplus_over_C": ratios,
            "distance_ratio_min_median_max": [min(ratios.values()), float(np.median(list(ratios.values()))), max(ratios.values())],
            "constant_predictor_outer_total": sum(e["flat_predictor_outer"] for e in pops.values()),
            "positive_constant_predictor_bank_fractions": {n: e["flat_predictor_bank_frac"] for n, e in pops.items() if e["flat_predictor_bank_frac"] > 0},
            "dropped_features": {n: e["dropped_C+"] for n, e in pops.items() if e["dropped_C+"]},
        }
    result = {
        "scope": "A0 feature fixtures and stored summary arithmetic; no bank reload or statistical fitting",
        "reviewed_source_commit": "7b41881c8b73f70b64a915d0957e1ea2f308c114",
        "timestamp_hobart": datetime.now(ZoneInfo("Australia/Hobart")).isoformat(),
        "runtime": {"python": platform.python_version(), "numpy": np.__version__},
        "inputs_sha256": {str((DEV / name).relative_to(ROOT)): sha(DEV / name) for name in ("a0_cplus.py", "a0_cplus.json", "d1c2_summary.json", "d1c2_trials.jsonl.gz")},
        "feature_fixtures": checks,
        "properties_passed": ["terminal exclusion", "penultimate inclusion", "count-scale equivariance"],
        "A0_C_vs_D1c2_equal_rank_means": nmeans,
        "A0_C_quantiles_replayed_from_D1c2_rows": nquantiles,
        "rounding_differences_fully_explained_by_numpy_vs_python_round": rounding_differences,
        "recomputed_summary_ranges": nranges,
        "all_population_block_distance_ratio_min_median_max": [min(all_ratios), float(np.median(all_ratios)), max(all_ratios)],
        "blocks": blocks,
        "limits": [
            "Computed changes and ratios use stored rounded summaries, not individual A0 rank records.",
            "No bank, neighbour archive or A0 raw trial rows were loaded.",
            "Matching the C summaries corroborates aggregate replay; it does not independently prove exact membership.",
            "A0 contains no fitted calibration or power outcomes.",
        ],
    }
    target = Path(__file__).with_suffix(".json")
    target.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"output": str(target), "feature_fixtures": len(checks),
                      "properties": len(result["properties_passed"]), "means": nmeans,
                      "quantiles": nquantiles, "ranges": nranges,
                      "distance_ratios": result["all_population_block_distance_ratio_min_median_max"]}))


if __name__ == "__main__":
    main()
