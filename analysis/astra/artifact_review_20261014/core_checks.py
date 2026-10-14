#!/usr/bin/env python3
"""Small source/receipt and arithmetic audit; no empirical fits or simulation.

Run from the repository root:
python3 analysis/astra/artifact_review_20261014/core_checks.py OUTPUT.json
"""
import collections
import hashlib
import json
import math
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
FROZEN = "52779d01468dac186c19810b59c8295dbedd212f"
TARGET = "ec72dd0330b6acd440aa85d2507c28e465ed2020"


def read_json(path):
    return json.loads((ROOT / path).read_text())


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def mapped_changes(years, counts):
    """The frozen R input mapping, on explicit arithmetic examples only."""
    values = counts[:-1] + [1]
    return [{"s": years[-1] - years[j],
             "D": math.log(values[j] / values[j - 1]),
             "earlier_year": years[j - 1], "later_year": years[j]}
            for j in range(1, len(years)) if years[j] - years[j - 1] == 1]


def main():
    sources = {}
    for name in ["tstats_batch.R", "bank.py", "effect_target.py", "e2e_benchmark.py"]:
        path = "analysis/fable/calibration/" + name
        frozen = subprocess.check_output(["git", "show", FROZEN + ":" + path], cwd=ROOT)
        same = frozen == (ROOT / path).read_bytes()
        assert same, f"Source differs from frozen version: {path}"
        sources[path] = {"sha256": sha(path), "identical_to_frozen": same}
    effect_path = "analysis/fable/calibration/freeze_v1/effect_target_ar_cat.json"
    effect = read_json(effect_path)
    chosen = effect["beta_min"]
    first_hit = next(r for r in effect["grid"] if r["diff"] >= .10)
    assert chosen == first_hit and effect["n0"] == 20
    g10 = math.exp(-chosen["beta"] * (1 / 10 - 1 / 50))
    assert math.isclose(1 - g10, chosen["delta10"], abs_tol=1e-14)
    preceding = [r for r in effect["grid"] if r["delta10"] < chosen["delta10"]][-1]
    assert preceding["diff"] < .10

    validation_path = "analysis/fable/calibration/validation_v1/validation_summary.json"
    validation = read_json(validation_path)
    expected = [46, 41, 148, 30, 21, 25, 16, 26, 17, 15, 17, 42, 40, 28, 118, 206, 11]
    rows = validation["scenarios"]
    assert [r["counts"]["reject"] for r in rows] == expected
    assert sum(r["n"] for r in rows) == 7900
    assert sum(r["fit_failures"]["failed_datasets"] for r in rows) == 4
    assert not validation["fit_stop"] and validation["v_fail"] and not validation["power_gate_pass"]
    meta_path = "analysis/fable/calibration/freeze_v1/bank_primary_meta.json"
    meta = read_json(meta_path)
    retained = collections.Counter()
    for row in meta["tasks"]:
        retained[row["population"]] += row["selected"]
    assert meta["shards"] * meta["shard_draws"] == 2_000_000_000

    toy = mapped_changes([0, 1, 2], [20, 10, 0])
    reverse_counts = {2: 20, 1: 10, 0: 1}
    assert all(math.isclose(r["D"], math.log(reverse_counts[r["s"]] / reverse_counts[r["s"] + 1])) for r in toy)
    assert toy[0]["D"] > toy[1]["D"] and toy[0]["s"] > toy[1]["s"]
    gap = mapped_changes([0, 1, 3, 4], [20, 10, 5, 0])
    assert [r["s"] for r in gap] == [3, 0]
    assert [r["later_year"] for r in gap] == [1, 4]
    report = {
        "scope": "Read archived receipts and unchanged frozen source; two hand-specified arithmetic fixtures; no fits, simulation or raw-bank reload",
        "reviewed_commit": TARGET, "frozen_source": FROZEN,
        "manuscript_sha256": sha("notes/vortex_manuscript_core_draft_20261014.md"),
        "source_identity": sources,
        "receipt_sha256": {p: sha(p) for p in [effect_path, validation_path, meta_path]},
        "effect_target": {"n0": effect["n0"], "runs_per_grid_point": effect["runs"],
            "chosen": chosen, "g10": g10, "preceding_grid_point": preceding,
            "interpretation": "Risk increment threshold 0.10 is distinct from Delta10=1-g(10)=0.075"},
        "validation": {"host": validation["host"], "runtime": validation["runtime"],
            "rejections_by_block": expected, "trials": sum(r["n"] for r in rows),
            "failed_vectors": sum(r["fit_failures"]["failed_datasets"] for r in rows),
            "gates": [{"block": r["block"], "null_gate": r.get("null_gate"),
                       "power_gate": r.get("power_gate")} for r in rows[:5]]},
        "bank_retained_per_population": dict(retained),
        "arithmetic_fixtures": {"reverse_time_sign": toy, "gap_mapping": gap,
            "qualification": "These confirm index algebra and mapping, not any fitted T statistic"},
        "manual_source_findings": ["Normal prior scale is SD 1.5, hence variance 1.5 squared",
            "T4 uses squared conditional residuals after refitting the mean model without final transitions",
            "Scorer uses squared Mahalanobis distance and complete training vectors; max 40/2000 failures before trial indeterminacy"]}
    pathlib.Path(sys.argv[1]).write_text(json.dumps(report, indent=2) + "\n")
    print("Four frozen sources identical; risk target and 17 validation counts verified; two arithmetic fixtures pass.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main()
