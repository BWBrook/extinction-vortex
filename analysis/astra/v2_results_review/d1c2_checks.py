"""Bounded independent D1c2/D2 audit of retained synthetic trial rows.

Run with an existing NumPy/SciPy Python environment. No banks, neighbour-ID
archives, empirical statistics, population simulation or population-model fits
are loaded/run. The only fitted models are the 24 diagnostic logistic regressions
on the already-retained outcomes. The peer's main() is never imported or run.
"""
import ast
from collections import Counter
from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path
import platform
import subprocess
from zoneinfo import ZoneInfo

import numpy as np
import scipy
from scipy import optimize, special, stats
from scipy.spatial import cKDTree

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEV = ROOT / "analysis/fable/calibration/v2_dev"
FIELDS = ("s", "f", "sigma", "lam_nominal", "lam_mean", "pen")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path):
    with gzip.open(path, "rt") as stream:
        return [json.loads(line) for line in stream]


def rounded(values):
    return [round(float(v), 4) for v in values]


def logistic(x, y):
    """Independent score-root solution with observed-information Wald interval."""
    z = (x - x.mean()) / x.std(ddof=0)
    design = np.column_stack((np.ones(len(z)), z))

    def score(coef):
        return design.T @ (special.expit(design @ coef) - y)

    def information(coef):
        prob = special.expit(design @ coef)
        return design.T @ ((prob * (1 - prob))[:, None] * design)

    fit = optimize.root(score, [special.logit(y.mean()), 0.], jac=information)
    assert fit.success and np.abs(score(fit.x)).max() < 1e-7
    se = np.sqrt(np.linalg.inv(information(fit.x))[1, 1])
    return rounded((fit.x[1], fit.x[1] - 1.96 * se, fit.x[1] + 1.96 * se))


def rate(k, n):
    interval = stats.binomtest(k, n).proportion_ci(.95, method="exact")
    return [int(k), int(n), *rounded((k / n, interval.low, interval.high))]


def main():
    source = DEV / "knn_nuisance_c.py"
    current_summary = json.loads((DEV / "d1c2_summary.json").read_text())
    old_summary = json.loads((DEV / "d1c_summary.json").read_text())
    current_rows = read_rows(DEV / "d1c2_trials.jsonl.gz")
    old_rows = read_rows(DEV / "d1c_trials.jsonl.gz")
    audit_path = ROOT / "analysis/astra/validation_v1_audit/raw_score.json.gz"
    with gzip.open(audit_path, "rt") as stream:
        v1_audit = json.load(stream)
    null_audit = {b["summary"]["name"]: b for b in v1_audit["blocks"]
                  if b["summary"]["role"] == "null"}
    assert current_summary["script_sha256"] == sha(source)
    assert current_summary["manifest_digest"] == old_summary["manifest_digest"] == v1_audit["manifest_sha256"]
    assert current_summary["K"] == old_summary["K"] == 2000
    for rows in (current_rows, old_rows):
        assert len(rows) == len({(r["block"], r["trial_id"]) for r in rows}) == 4000
    old_map = {(r["block"], r["trial_id"]): r for r in old_rows}
    assert set(old_map) == {(r["block"], r["trial_id"]) for r in current_rows}
    assert set(null_audit) == set(current_summary["blocks"])

    # Isolate only the pure midrank helper, avoiding bank/module imports.
    tree = ast.parse(source.read_text())
    helper = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "midrank")
    scope = {"np": np}
    exec(compile(ast.Module(body=[helper], type_ignores=[]), str(source), "exec"), scope)
    ranks = scope["midrank"](np.full((3, 4), 5), np.array([4, 5, 6]))
    assert ranks.tolist() == [0., .5, 1.]
    main_node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    queries = [n for n in ast.walk(main_node) if isinstance(n, ast.Assign)
               and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute)
               and ast.unparse(n.value.func) == "tree.query"]
    query_contract = [{"target": ast.unparse(n.targets[0]),
                       "k": ast.unparse(next(k.value for k in n.value.keywords if k.arg == "k"))}
                      for n in queries]
    assert query_contract == [{"target": "(dist, idx)", "k": "K"},
                              {"target": "(d1, _)", "k": "K + 1"}]
    # The same tiny fixture that motivated the repair; not a population simulation.
    fixture_tree = cKDTree(np.zeros((8, 2)))
    direct = fixture_tree.query([0., 0.], k=3)[1].tolist()
    truncated = fixture_tree.query([0., 0.], k=4)[1][:3].tolist()
    assert set(direct) != set(truncated)

    results = {}
    minor_rounding = []

    def compare_rounded(label, computed, reported, exact=False):
        difference = float(np.max(np.abs(np.asarray(computed) - np.asarray(reported))))
        assert difference <= (1e-12 if exact else 1.000001e-4), (label, computed, reported)
        if difference > 1e-12:
            minor_rounding.append({"field": label, "recomputed": computed, "reported": reported})

    for block, report in current_summary["blocks"].items():
        rows = [r for r in current_rows if r["block"] == block]
        reference = {r["trial_id"]: r for r in null_audit[block]["rows"]}
        assert len(rows) == 1000 and {r["trial_id"] for r in rows} == set(reference)
        populations = list(rows[0]["pop"])
        assert len(populations) == 9
        ties = Counter()
        constants = Counter()
        constant_values = Counter()
        digest_changes = 0
        rank_changes = Counter()
        restored_pen_ranks = 0
        for row in rows:
            old = old_map[(block, row["trial_id"])]
            original = reference[row["trial_id"]]
            assert row["outcome"] == old["outcome"] == original["outcome"]
            assert row["p_hi"] == old["p_hi"] == original["p_hi"]
            assert list(row["pop"]) == populations
            assert max(p["kth"] for p in row["pop"].values()) == original["largest_radius_logged"]
            for population, value in row["pop"].items():
                previous = old["pop"][population]
                assert value["kth"] == value["kth_v1"] == previous["kth"] == previous["kth_v1"]
                assert value["tie"] == previous["tie"]
                assert all(value[k] is not None and np.isfinite(value[k]) and 0 <= value[k] <= 1 for k in FIELDS)
                changed = value["nbr"] != previous["nbr"]
                digest_changes += changed
                assert not changed or value["tie"]
                ties[population] += value["tie"]
                constants[population] += value["const_pen"]
                if value["const_pen"]:
                    assert value["pen"] in (0., .5, 1.)
                    constant_values[str(value["pen"])] += 1
                if previous["pen"] is None:
                    restored_pen_ranks += 1
                    assert value["const_pen"]
                for field in FIELDS:
                    if previous[field] is not None and value[field] != previous[field]:
                        rank_changes[field] += 1
                        assert changed
        assert sum(ties.values()) == report["reconstruction"]["boundary_ties"]
        assert dict(constants) == report["constant_penultimate_library"]
        assert restored_pen_ranks == sum(constants.values())
        assert digest_changes == report["membership_vs_version1"]["sets_changed"]
        assert report["membership_vs_version1"]["sets_changed_without_tie_flag"] == 0

        # Midranks lie on 1/(2K). Four-decimal rounding error is less than half
        # the 1/4000 lattice spacing, so the mathematical ranks are recoverable.
        lattice = 2 * current_summary["K"]
        rank_arrays = {}
        max_rounding = 0.
        for field in FIELDS:
            stored = np.array([[r["pop"][p][field] for p in populations] for r in rows])
            recovered = np.rint(stored * lattice) / lattice
            max_rounding = max(max_rounding, float(np.abs(stored - recovered).max()))
            assert np.abs(stored - recovered).max() <= .000050000001
            rank_arrays[field] = recovered
        summaries = {field: value.mean(axis=1) - .5 for field, value in rank_arrays.items()}
        outcome = np.array([r["outcome"] == "reject" for r in rows], dtype=float)
        p_hi = np.array([r["p_hi"] for r in rows])
        assert int(outcome.sum()) == report["rejections"] == null_audit[block]["summary"]["reject"]
        association = {}
        for field, summary in summaries.items():
            observed = report["association"][field]
            fitted = logistic(summary, outcome)
            compare_rounded(f"{block}/{field}/logistic", fitted, observed["logistic_slope_per_sd"], exact=True)
            cutpoints = np.quantile(summary, [1 / 3, 2 / 3])
            group = np.searchsorted(cutpoints, summary, side="right")
            tertiles = [rate(int(outcome[group == j].sum()), int((group == j).sum())) for j in range(3)]
            compare_rounded(f"{block}/{field}/tertiles", tertiles, observed["reject_by_tertile"], exact=True)
            spearman = round(float(stats.spearmanr(summary, p_hi).statistic), 4)
            compare_rounded(f"{block}/{field}/spearman_p_hi", spearman, observed["spearman_with_p_hi"])
            compare_rounded(f"{block}/{field}/trial_quantiles", rounded(np.quantile(summary, [.1, .5, .9])),
                            report["trial_summary_q10_50_90"][field])
            association[field] = {"logistic_slope_per_sd": fitted, "reject_by_tertile": tertiles,
                                  "spearman_with_p_hi": spearman,
                                  "previous_logistic_slope_per_sd": old_summary["blocks"][block]["association"][field]["logistic_slope_per_sd"]}
            for j, population in enumerate(populations):
                values = rank_arrays[field][:, j]
                previous = report["per_population"][population]
                compare_rounded(f"{block}/{population}/{field}/mean", round(float(values.mean()), 4),
                                previous[f"{field}_rank_mean"])
                if field in ("s", "lam_mean", "pen"):
                    compare_rounded(f"{block}/{population}/{field}/quantiles", rounded(np.quantile(values, [.1, .5, .9])),
                                    previous[f"{field}_rank_q10_50_90"])
            for other in FIELDS:
                compare_rounded(f"{block}/{field}/{other}/spearman", round(float(stats.spearmanr(summary, summaries[other]).statistic), 4),
                                report["trial_summary_spearman"][field][other])
        results[block] = {"unique_trials": len(rows), "matched_population_distances": 9 * len(rows),
                          "rejections": int(outcome.sum()), "valid_midrank_populations_per_trial": 9,
                          "boundary_ties": sum(ties.values()), "changed_neighbour_digests": digest_changes,
                          "changed_without_tie": 0, "changed_rank_cells": dict(rank_changes),
                          "restored_constant_pen_ranks": restored_pen_ranks,
                          "constant_pen_rank_values": dict(constant_values),
                          "max_rounding_distance_to_rank_lattice": max_rounding,
                          "association_recomputed": association,
                          "members_changed_max_unverified_report": report["membership_vs_version1"]["members_changed_max"]}

    inputs = [source, DEV / "d1c2_summary.json", DEV / "d1c2_trials.jsonl.gz",
              DEV / "d1c_summary.json", DEV / "d1c_trials.jsonl.gz", audit_path]
    result = {
        "reviewed_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "time_hobart": datetime.now(ZoneInfo("Australia/Hobart")).isoformat(),
        "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
        "input_sha256": {str(path.relative_to(ROOT)): sha(path) for path in inputs},
        "method": "Independent arithmetic and score-root logistic fit from retained synthetic trial ranks/outcomes; mathematical midranks recovered on the 1/(2K) lattice.",
        "query_contract": query_contract,
        "constant_library_fixture": {"library": [5, 5, 5, 5], "observations": [4, 5, 6], "ranks": ranks.tolist()},
        "tie_fixture": {"query_K": direct, "truncated_query_K_plus_1": truncated},
        "blocks": results,
        "rounding_level_differences_at_most_0_0001": minor_rounding,
        "limits": [
            "No bank or full neighbour archive loaded. Digest changes establish changes between archived D1c versions; historical v1 membership itself is not independently proven.",
            "Maximum changed members per neighbourhood (10,27,30,16) cannot be reproduced from digests alone.",
            "Bank/source verification counts, neighbour NPZ hash, n0 checks and true/library median means remain peer-reported; this review checks current diagnostic-source hash and manifest-digest agreement only.",
            "Four-decimal midranks recover the mathematical 1/(2K) lattice, but not every original floating-point evaluation. Quantiles and Spearman correlations may differ in their final fourth decimal; all logistic estimates/intervals and all tertile counts/intervals reproduce exactly as reported.",
            "These are exposed v1 development diagnostics, not prospective validation, causal attribution, or empirical inference."
        ]
    }
    (HERE / "d1c2_checks.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"rows_reconciled": len(current_rows), "logistic_estimates_and_intervals_exact": 24,
                      "tertile_rows_exact": 72, "minor_rounding_differences": len(minor_rounding),
                      "changed_digests": [b["changed_neighbour_digests"] for b in results.values()]}, indent=2))


if __name__ == "__main__":
    main()
