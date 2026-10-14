"""Deterministic source/seed/resource audit of the external-information draft.

No generator calls, bank payload loads, fits or empirical statistics. Run with
python3 analysis/astra/draft_review_20261014/design_checks.py. Only the sibling
JSON receipt is written. Probability-law and Stage-0-rule reviews are separate.
"""
import ast
from collections import defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
CAL = ROOT / "analysis/fable/calibration"
DRAFT = ROOT / "notes/vortex_external_info_design_20261014.md"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def function(path, name):
    tree = ast.parse(path.read_text())
    return next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)


def assignment(node, name):
    matches = [n for n in ast.walk(node) if isinstance(n, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)]
    return [{"line": n.lineno, "expression": ast.unparse(n.value)} for n in matches]


def main():
    manifest = json.loads((CAL / "freeze_v1/validation_manifest.json").read_text())
    primary_path = CAL / "freeze_v1/bank_primary_meta.json"
    primary = json.loads(primary_path.read_text())
    retained = defaultdict(int)
    for t in primary["tasks"]:
        retained[t["population"]] += t["selected"]
    sim = function(CAL / "bank.py", "simulate_chunk")
    fresh = function(CAL / "e2e_benchmark.py", "fresh_selected")
    build = function(CAL / "build_bank.py", "task")
    chunk = function(CAL / "e2e_benchmark.py", "run_chunk")
    ret = next(n for n in sim.body if isinstance(n, ast.Return))
    out_assign = next(n for n in ast.walk(fresh) if isinstance(n, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == "out" for t in n.targets))
    saved_outer_fields = [k.value for k in out_assign.value.keys]
    bank_save = next(n for n in ast.walk(build) if isinstance(n, ast.Call)
                     and isinstance(n.func, ast.Attribute) and n.func.attr == "savez_compressed")
    bank_save_fields = [k.arg for k in bank_save.keywords]
    checks = {
        "bank_source_matches_frozen_manifest": sha(CAL / "bank.py") == manifest["source_sha256"]["analysis/fable/calibration/bank.py"],
        "fitter_source_matches_frozen_manifest": sha(CAL / "e2e_benchmark.py") == manifest["source_sha256"]["analysis/fable/calibration/e2e_benchmark.py"],
        "primary_metadata_matches_frozen_bank_manifest": sha(primary_path) == manifest["bank_sha256"]["bank_meta.json"],
        "all_primary_population_banks_exceed_200000_records": min(retained.values()) >= 200000,
        "saved_outer_fields_are_counts_theta_drawcount": saved_outer_fields == ["recorded", "draws", "params"],
        "simulator_returns_no_annual_rate_history": ast.unparse(ret.value) == "(rec, p, overflow, selected)",
        "bank_save_has_no_explicit_environment_survival_recruit_fields": set(bank_save_fields) == {"rec", "draw_id", "seed", "draws", "overflow", None},
    }
    assert all(checks.values()), checks
    source = {
        "generator_assignments": {name: assignment(sim, name) for name in ("z", "mult", "g", "logit", "st", "ft", "lam", "selected")},
        "saved_outer_fields": saved_outer_fields,
        "saved_bank_named_fields": [k for k in bank_save_fields if k is not None],
        "saved_bank_extra_fields": "PARAM_NAMES: s,f,sigma,rho,p_c,delta,nu; these are draw parameters, not annual histories",
        "simulator_return": ast.unparse(ret.value),
        "existing_reference_sampling": assignment(chunk, "traj"),
        "interpretation": [
            "Annual survival probability is catastrophe_multiplier * logistic(logit(s)+sigma*z+log(g)); g multiplies survival odds.",
            "Annual recruits have Poisson mean N * catastrophe_multiplier * g * f * exp(sigma*z-sigma^2/2); f is per counted individual.",
            "z and catastrophe multiplier are shared among individuals within a trajectory-year; z follows stationary-marginal AR(1).",
            "Draft sbar and fbar match stationary unconditional M0 mean probabilities/rates, not realised finite-year field rates.",
            "Fresh prior-predictive sampling redraws theta for every candidate and retains first selected candidate; it does not hold one prior theta fixed until selection.",
            "Selection checks recorded intermediate census counts >1, final count <=1 and no overflow. The process runs annual steps between censuses.",
            "Stored census counts and theta do not determine realised z, catastrophe occurrence or the survivor/recruit decomposition. Matched latent-history replay would require new generator execution."
        ],
    }
    evidence_seed = lambda c, i: 8 * 10**12 + 8 * 10**6 + 10**5 * c + i
    reference_seed = lambda c, i: 8 * 10**12 + 9 * 10**6 + 10**5 * c + i
    e = {evidence_seed(c, i) for c in range(80) for i in range(200)}
    r = {reference_seed(c, i) for c in range(80) for i in range(200)}
    overlaps = e & r
    assert len(overlaps) == 14000
    seed_audit = {
        "identity": "E(cell+10,trial) == Reference(cell,trial)",
        "example": {"evidence_cell": 10, "reference_cell": 0, "trial": 0,
                    "both_seed": evidence_seed(10, 0)},
        "within_each_family_unique": len(e) == len(r) == 16000,
        "cross_family_overlap_if_both_families_defined_for_all_cells_0_to_79": len(overlaps),
        "overlap_cell_pairs": 70,
        "qualification": "Actual used collision count depends on the unspecified cell enumeration and which cells draw E; I-sf may draw no E. The namespace collision itself is exact.",
        "population_stream_contract": "No population coordinate or fixed population iteration/spawn convention is declared; this must be defined before execution."
    }
    cells = {"E_sf": 4 * 2 * 6, "I_sf": 4 * 6, "Timing": 2 * 2 * 2}
    n_cells = sum(cells.values()); analyses = n_cells * 200; R = manifest["R"]
    timeline = {}
    for line in (CAL / "v2_dev/d3/timeline.txt").read_text().splitlines():
        label, *stamp = line.split()
        if label in ("outers", "bank"):
            timeline[label] = datetime.fromisoformat(stamp[0])
    observed_d3_bank_seconds = (timeline["bank"] - timeline["outers"]).total_seconds()
    arithmetic = {
        "cells": cells, "total_cells": n_cells, "analyses": analyses,
        "fitted_T_vectors_if_all_cells_run_at_frozen_R": analyses * (2 * R + 1),
        "v1_validation_analyses": sum(s["n_trials"] for s in manifest["scenarios"]),
        "ratio_to_v1": analyses / sum(s["n_trials"] for s in manifest["scenarios"]),
        "oracle_power_additional_analyses": 50,
        "analyses_with_oracle": analyses + 50,
        "oracle_50_times_40min_hours": 50 * 40 / 60,
        "observed_D3_bank_seconds": observed_d3_bank_seconds,
        "oracle_fixed_draw_projection": {"population_banks": 50 * len(retained), "shard_files": 50 * len(retained) * 20,
                                           "initial_generator_draws": 50 * len(retained) * 20 * 10**8},
        "R1_worst_case_weight_evaluations": analyses * len(retained) * 200000,
        "unique_outer_population_queries_if_reused_across_cells": 6 * 200 * len(retained),
        "full_top200000_cache_distance_index_bytes_at_8_bytes_each": 6 * 200 * len(retained) * 200000 * 16,
        "cost_interpretation": "80 cells and 16000 analyses are arithmetically correct; seven hours is an unmeasured old-run scaling, omitting new weighting/large-neighbour setup. Oracle 35h rounds 33h20m bank generation and excludes 50 extra fitted analyses; support/extension costs vary with each theta."
    }
    assert cells == {"E_sf": 48, "I_sf": 24, "Timing": 8} and analyses == 16000
    result = {
        "scope": "Source and deterministic arithmetic only; no bank payloads, simulation, fitting, dispatch or empirical statistics",
        "time_hobart": datetime.now(ZoneInfo("Australia/Hobart")).isoformat(),
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "draft_sha256": sha(DRAFT), "checks": checks, "source_contract": source,
        "seed_audit": seed_audit, "arithmetic": arithmetic,
        "primary_bank_retained_by_population": dict(retained), "primary_bank_retained_total": sum(retained.values()),
        "remaining_feasibility_limit": "Record counts suffice for the 200000 cap in every population, but weighted ESS/support cannot be certified without the proposed separate pre-screen. Existing run_chunk samples uniformly from fixed K; weighted variable-size libraries require a new declared sampler."
    }
    path = Path(__file__).with_suffix(".json"); path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(path), "source_checks": len(checks), "cells": n_cells,
                      "analyses": analyses, "potential_namespace_seed_collisions": len(overlaps)}))


if __name__ == "__main__":
    main()
