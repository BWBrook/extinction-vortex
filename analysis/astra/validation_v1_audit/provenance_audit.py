"""Read-only v1 provenance audit, independent of Fable's executable modules.

Runs small stdlib checks locally and over SSH. It reads all 170 chunk metadata
files and the ten block-3 JSONL files; it never opens banks or T CSVs, fits a
model, simulates a population, or writes on the remote host.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo


POPS = {"wild_dog": "14", "marmot": "15", "ms_woodpecker": "6",
        "rc_woodpecker": "20", "golden_plover": "21", "whooping_crane": "10",
        "hawaiian_crow": "4", "wood_turtle_A": "8", "wood_turtle_B": "9"}

REMOTE = r'''
from collections import Counter
from pathlib import Path
import hashlib, json, math
request = json.loads(REQUEST_JSON)
base = Path(request["base"])
man = request["manifest"]
digest = request["digest"]
design = request["design"]
failures = []
hashes = {}
checks = Counter()
def check(name, condition, context=None):
    checks[name] += 1
    if not condition:
        failures.append({"check": name, "context": context})
def read_json(path):
    data = path.read_bytes()
    hashes[str(path.relative_to(base))] = hashlib.sha256(data).hexdigest()
    return json.loads(data)
totals = Counter()
draws_used = Counter()
outcomes = Counter()
by_chunk = []
maximum_recorded = 0
manifest_chunks = []
for scenario in man["scenarios"]:
    for chunk in scenario["chunks"]:
        directory = base / Path(chunk["dir"]).relative_to("validation_v1")
        manifest_chunks.append(str(directory.relative_to(base)))
        expected = {
            "variant": man["variant"], "R_train": man["R"], "R_test": man["R"],
            "K": man["K"], "budget": man["budget"], "bankdir": man["bankdir"],
            "block": scenario["block"], "scenario": scenario["name"],
            "role": scenario["role"], "beta": scenario["beta"], "spec": scenario["spec"],
            "stress": scenario["stress"], "seed": chunk["seed"],
            "trial_ids": chunk["trial_ids"], "dir": chunk["dir"]}
        meta = read_json(directory / "e2e_meta.json")
        check("chunk_manifest_digest", meta.get("manifest_digest") == digest, chunk["dir"])
        check("chunk_all_settings", meta.get("settings") == expected, chunk["dir"])
        check("chunk_top_level_R_train", meta.get("R_train") == man["R"], chunk["dir"])
        check("chunk_primary_reference", expected["variant"] == "ar_cat" and
              expected["bankdir"] == "bank_primary" and expected["R_train"] == 2000 and
              expected["R_test"] == 2000 and expected["K"] == 2000 and
              expected["budget"] == 1000000, chunk["dir"])
        totals["metadata_files"] += 1
        totals["remaining_sets_csv_files"] += len(list(directory.glob("sets_*.csv")))
        if scenario["block"] != 3:
            continue
        check("low_s_generator_settings", scenario["beta"] == 0 and
              scenario["stress"] is False and scenario["role"] == "null" and
              set(scenario["spec"]) == {"fixed"}, chunk["dir"])
        path = directory / "e2e_rows.jsonl"
        data = path.read_bytes()
        hashes[str(path.relative_to(base))] = hashlib.sha256(data).hexdigest()
        rows = [json.loads(line) for line in data.splitlines() if line.strip()]
        check("low_s_trial_ids_order", [row["trial_id"] for row in rows] ==
              list(range(*chunk["trial_ids"])), chunk["dir"])
        check("low_s_outer_positions", [row["outer"] for row in rows] == list(range(len(rows))),
              chunk["dir"])
        cc = Counter()
        for row in rows:
            tid = row["trial_id"]
            selected = row["selected"]
            totals["low_s_trials"] += 1
            cc[row["outcome"]] += 1
            outcomes[row["outcome"]] += 1
            check("low_s_population_set", set(selected) == set(design), tid)
            for name, d in design.items():
                context = [tid, name]
                draw = selected.get(name)
                check("low_s_selected_present", draw is not None, context)
                if draw is None:
                    continue
                totals["low_s_selected_trajectories"] += 1
                check("low_s_parameter_keys", set(draw["params"]) ==
                      set(scenario["spec"]["fixed"][name]), context)
                for key, value in scenario["spec"]["fixed"][name].items():
                    check("low_s_exact_parameter", draw["params"].get(key) == value,
                          [tid, name, key])
                rec = draw["recorded"]
                check("low_s_recorded_length", len(rec) == len(d["years"]), context)
                check("low_s_initial_count", rec[0] == d["initial"], context)
                check("low_s_selected_endpoint", all(v > 1 for v in rec[:-1]) and
                      rec[-1] in (0, 1), context)
                check("low_s_integer_nonnegative_counts", all(isinstance(v, int) and
                      v >= 0 for v in rec), context)
                check("low_s_recorded_counts_within_cap", max(rec) <= 10**9, context)
                check("low_s_no_latent_observation_model", "latent" not in draw, context)
                check("low_s_draw_budget", 0 < draw["draws"] <= man["budget"] and
                      draw["draws"] % 200000 == 0, context)
                maximum_recorded = max(maximum_recorded, max(rec))
                draws_used[draw["draws"]] += 1
        by_chunk.append({"chunk": chunk["c"], "outcomes_as_recorded": dict(cc)})
actual_chunks = sorted(str(p.relative_to(base)) for p in base.glob("b*/c*"))
check("manifest_chunk_inventory", actual_chunks == sorted(manifest_chunks))
print(json.dumps({"remote_base": str(base), "checks": dict(checks), "failures": failures,
                  "totals": dict(totals), "draws_used_batch_totals": dict(draws_used),
                  "low_s_outcomes_as_recorded_not_T_recomputed": dict(outcomes),
                  "low_s_by_chunk": by_chunk, "maximum_low_s_recorded_count": maximum_recorded,
                  "input_sha256": hashes}))
'''


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="deep-server")
    parser.add_argument("--base", default="/data/fable/vortex/kunanyi_run1/extract/validation_v1")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_suffix(".json"))
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[3]
    freeze = repo / "analysis/fable/calibration/freeze_v1"
    manpath = freeze / "validation_manifest.json"
    man = json.loads(manpath.read_text())
    digest = sha(manpath)
    failures = []
    checked = {}

    def check(name, condition):
        checked[name] = bool(condition)
        if not condition:
            failures.append(name)

    check("manifest_frozen_digest", digest ==
          "96603037ec05036153f67b649757d067ca193c5e0a8610d3b855ef8f22139429")
    check("manifest_source_commit", man["code_commit"] == "52779d0")
    check("manifest_primary_bank_inventory", len(man["bank_sha256"]) == 181)
    for path, expected in man["source_sha256"].items():
        check("source_hash:" + path, sha(repo / path) == expected)

    effect = json.loads((freeze / "effect_target_ar_cat.json").read_text())
    check("frozen_effect_hash", sha(freeze / "effect_target_ar_cat.json") == man["effect_sha256"])
    corner = next(c for c in json.loads((freeze / "corners.json").read_text())
                  if c["name"] == "ar_cat_low_s")
    scenario = next(s for s in man["scenarios"] if s["block"] == 3)
    check("low_s_manifest_matches_corner_file", scenario["spec"]["fixed"] == corner["fixed"])
    check("low_s_corner_file_variant_beta", corner["variant"] == man["variant"] and
          corner["beta"] == scenario["beta"] == 0)
    for name, params in scenario["spec"]["fixed"].items():
        check("low_s_corner_matches_effect:" + name, params == effect["corners"]["low_s"][name]["theta"])
        for key, value in params.items():
            quantile = 0 if key == "s" else 1
            check("low_s_frozen_quantile:" + name + ":" + key,
                  value == effect["library_quantiles"][name][key][quantile])

    with (repo / "data/raw/williams2021/population_data.csv").open(newline="") as file:
        raw = {r["ID"]: r for r in csv.DictReader(file)}
    design = {}
    for name, pop_id in POPS.items():
        row = raw[pop_id]
        sequence = sorted((int(y), float(v)) for y, v in row.items()
                          if y.isdigit() and v not in ("", "NULL"))
        first_endpoint = next(i for i, (_, count) in enumerate(sequence) if count <= 1)
        sequence = sequence[:first_endpoint + 1]
        years = [y for y, _ in sequence]
        gaps = [b - a for a, b in zip(years, years[1:])]
        design[name] = {"initial": int(sequence[0][1]), "years": years,
                        "gaps": gaps, "recorded_length": len(years)}
        check("primary_design_no_gaps:" + name, all(gap == 1 for gap in gaps))

    preflight_path = repo / "analysis/fable/calibration/validation_v1" / f"preflight_{digest[:16]}.json"
    preflight = json.loads(preflight_path.read_text())
    check("kunanyi_preflight_digest", preflight["manifest_digest"] == digest)
    check("kunanyi_preflight_counts", preflight["checked_source"] == 12 and
          preflight["checked_bank_shards"] == 181)
    check("kunanyi_preflight_runtime_pins", all(preflight["runtime"].get(k) == v
                                               for k, v in man["runtime_pins"].items()))
    request = {"base": args.base, "manifest": man, "digest": digest, "design": design}
    remote_script = REMOTE.replace("REQUEST_JSON", repr(json.dumps(request)), 1)
    completed = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
                                args.host, "python3", "-"], input=remote_script, text=True,
                               capture_output=True, check=True)
    remote = json.loads(completed.stdout)
    result = {
        "audited_at": datetime.now(ZoneInfo("Australia/Hobart")).isoformat(),
        "scope": "170 chunk metadata files and all 1000 low_s outer selected datasets; no T rescoring or banks",
        "manifest_sha256": digest, "source_commit": man["code_commit"],
        "local_checks": checked, "local_failures": failures, "designs": design,
        "kunanyi_preflight_receipt": preflight, "remote_checks": remote,
        "pass": not failures and not remote["failures"],
        "static_review": [
            "validate.py loads one manifest-bound primary ar_cat bank per slot and supplies the same banks to every chunk.",
            "Block 3 supplies only fixed six-parameter values and beta=0; no block-specific test or reference branch exists.",
            "simulate_chunk replaces prior parameter arrays with the fixed values before transitions; beta=0 leaves the feedback multiplier at one.",
            "Recorded selection requires all preterminal censuses >1 and terminal census <=1, excluding count/rate overflow; primary designs are annual without gaps.",
            "run_chunk uses only each outer trajectory's three C summaries to find its K=2000 nearest bank trajectories, then independently samples with replacement for 2000 training and 2000 test datasets.",
            "The fixed low_s outer parameters are not imposed on references: references remain the frozen prior-mixture bank as declared.",
        ],
        "limitations": [
            "Chunk metadata and preflight receipts bind the declared configuration; they are not retained per-reference draw membership evidence.",
            "sets_*.csv files are deleted by the frozen code, and reference indices/full kNN membership are not retained. This audit cannot independently reconstruct the actual selected reference trajectories without replaying the random stream and banks.",
            "The selected outer record reports the full generated batch total as draws, not the first successful within-batch index; no full outer generator replay was performed.",
            "Recorded counts and static source verify the stated endpoint/cap logic, but unrecorded yearly Poisson rates and overflow histories cannot be checked from selected JSONL records alone.",
            "This audit checks corner values against frozen quantiles, not a new recomputation of those quantiles from large banks.",
            "Outcome counts in this artifact are read from JSONL for provenance only; the separate parent audit independently re-scores T CSVs.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"pass": result["pass"], "local_checks": len(checked),
                      "remote_check_counts": remote["checks"], "totals": remote["totals"],
                      "low_s_outcomes_as_recorded": remote["low_s_outcomes_as_recorded_not_T_recomputed"],
                      "max_recorded": remote["maximum_low_s_recorded_count"],
                      "local_failures": failures, "remote_failures": remote["failures"],
                      "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
