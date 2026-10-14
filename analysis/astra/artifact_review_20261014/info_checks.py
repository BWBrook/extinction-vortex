"""Revision-2 external-information design: deterministic execution fixtures.

Run with OPENBLAS_NUM_THREADS=1 /home/bwbrook/papers/dsipa-dev/.venv/bin/python
analysis/astra/artifact_review_20261014/info_checks.py. No production bank loads,
queries, population simulations, fits, E draws or remote execution. Local RNG
initial states, a tiny geometric fixture and numerical integrals are inspected.
The numerical helpers below are audit examples, not a production implementation.
"""
import ast
from datetime import datetime
import hashlib
import json
from pathlib import Path
import platform
import subprocess
from zoneinfo import ZoneInfo

import numpy as np
import scipy
from scipy.integrate import quad
from scipy.special import expit, xlog1py, xlogy
from scipy.spatial import cKDTree
from scipy.stats import binom, poisson

ROOT = Path(__file__).resolve().parents[3]
CAL = ROOT / "analysis/fable/calibration"
DRAFT = ROOT / "notes/vortex_external_info_design_20261014.md"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normal_logistic(logodds, sigma, nodes=40):
    x, w = np.polynomial.hermite_e.hermegauss(nodes)
    return float(np.dot(w / w.sum(), expit(logodds + sigma * x)))


def logweight(n, k, r, sbar, fbar):
    """Theta-dependent terms only; k/r may be expected pseudo-counts."""
    return xlogy(k, sbar) + xlog1py(n - k, -np.asarray(sbar)) + xlogy(r, fbar) - n * np.asarray(fbar)


def normalise(logw):
    logw = np.asarray(logw, float)
    if np.isnan(logw).any() or np.isposinf(logw).any() or not np.isfinite(logw).any():
        raise ValueError("unusable logweights")
    w = np.exp(logw - np.max(logw)); total = float(w.sum())
    return w / total, total * total / float(np.dot(w, w)), float(w.max() / total)


def numerical_checks():
    errors, refinement_errors = [], []
    for logodds in [-30., -12., -5., -1., 0., 1., 5., 12., 30.]:
        for sigma in [0., .02, .25, .5, 1.]:
            gh40 = normal_logistic(logodds, sigma)
            gh80 = normal_logistic(logodds, sigma, 80)
            exact, bound = quad(lambda z: expit(logodds + sigma * z) * np.exp(-z*z/2) / np.sqrt(2*np.pi),
                                -np.inf, np.inf, epsabs=1e-13, epsrel=1e-12)
            errors.append(abs(gh40 - exact)); refinement_errors.append(abs(gh40 - gh80))
    assert max(errors) < 1e-10 and max(refinement_errors) < 1e-10
    sbar = np.array([.05, .25, .65, .95]); fbar = np.array([.02, .2, .6, 1.7])
    likelihood_errors = []
    for n, k, r in [(30, 0, 0), (30, 30, 1), (300, 213, 117)]:
        ours = normalise(logweight(n, k, r, sbar, fbar))[0]
        full = normalise(binom.logpmf(k, n, sbar) + poisson.logpmf(r, n * fbar))[0]
        likelihood_errors.append(float(np.max(np.abs(ours - full))))
    assert max(likelihood_errors) < 1e-12
    n, s0, f0 = 300, .7, .3
    ideal_a = logweight(n, n*s0, n*f0, sbar, fbar)
    ideal_b = n*(s0*np.log(sbar) + (1-s0)*np.log1p(-sbar)) + n*(f0*np.log(fbar) - fbar)
    assert np.allclose(ideal_a, ideal_b, rtol=0, atol=1e-12)
    stable, ess, share = normalise([-1000000., -1000001., -1000002.])
    assert np.allclose(stable, normalise([0., -1., -2.])[0])
    assert np.exp(np.array([-1000000., -1000001., -1000002.])).sum() == 0
    invalid = []
    for values in [[-np.inf, -np.inf], [0., np.nan], [0., np.inf]]:
        try:
            normalise(values)
        except ValueError:
            invalid.append(True)
        else:
            invalid.append(False)
    assert all(invalid)
    endpoint = logweight(30, 0, 0, np.array([0., 1.]), np.array([0., 0.]))
    assert endpoint[0] == 0 and np.isneginf(endpoint[1])
    zero_evidence = normalise(logweight(0, 0, 0, np.linspace(.001, .999, 2000), np.linspace(.01, 2, 2000)))
    threshold = normalise(np.r_[np.zeros(100), np.full(1900, -np.inf)])
    assert zero_evidence[1] == 2000 and threshold[1] == 100
    return {
        "GH40_vs_adaptive_quad_cases": len(errors), "GH40_max_absolute_error": max(errors),
        "GH40_vs_GH80_max_absolute_difference": max(refinement_errors),
        "scope": "Deterministic grid spans sigma0..1 and logit(s)-30..30; this does not certify every possible input or a future implementation.",
        "normalized_loglikelihood_vs_full_pmf_max_error": max(likelihood_errors),
        "ideal_expression_matches_expected_pseudocounts": True,
        "underflow_fixture": {"raw_weight_sum": 0., "stable_weights": stable.tolist(), "ESS": ess, "max_share": share},
        "all_minus_inf_nan_and_plus_inf_refused": invalid,
        "zero_times_log_zero_boundary_handled": True,
        "n0_returns_uniform_K2000_ESS": zero_evidence[1],
        "ESS_exact100_fixture_passes_strict_less_than100_flag": threshold[1] == 100,
        "proposed_numerical_contract": "Fix the quadrature rule; stabilize in log space; use xlogy/log1p equivalents at boundaries; allow -inf zero weights only when some finite weight exists; report unusable weights instead of uniform fallback."
    }


def stream_checks(populations):
    entropies, states = set(), set(); e_count = r_count = 0; duplicate_states = 0
    bit_generators = set()
    for cell in range(8):
        for trial in range(200):
            for entropy in [(20261014, 1, cell, trial, p) for p in range(9)] + [(20261014, 2, cell, trial)]:
                e_count += entropy[1] == 1; r_count += entropy[1] == 2
                assert entropy not in entropies; entropies.add(entropy)
                rng = np.random.default_rng(entropy)
                state = json.dumps(rng.bit_generator.state, sort_keys=True)
                duplicate_states += state in states; states.add(state)
                bit_generators.add(type(rng.bit_generator).__name__)
    assert (e_count, r_count, duplicate_states) == (14400, 1600, 0)
    return {"E_streams": e_count, "reference_streams_reserved_for_Stage1": r_count,
            "entropy_tuples_unique": True, "duplicate_initial_states_in_enumeration": duplicate_states,
            "bit_generators_in_local_runtime": sorted(bit_generators),
            "frozen_population_order": populations,
            "cell_map": [{"cell": ni*4+si, "n": n, "block": b} for ni, n in enumerate([30, 300]) for si, b in enumerate([1, 3, 5, 16])],
            "qualification": "Finite enumeration found no duplicate states in this installed runtime; SeedSequence does not mathematically guarantee collision-free/nonoverlapping streams. Pin NumPy/BitGenerator and bind ordering plus k-then-r draw convention."}


def source_checks():
    man = json.loads((CAL / "freeze_v1/validation_manifest.json").read_text())
    assert sha(CAL / "bank.py") == man["source_sha256"]["analysis/fable/calibration/bank.py"]
    assert sha(CAL / "e2e_benchmark.py") == man["source_sha256"]["analysis/fable/calibration/e2e_benchmark.py"]
    tree = ast.parse((CAL / "bank.py").read_text())
    pops = next(n.value for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "POPS" for t in n.targets))
    populations = list(ast.literal_eval(pops))
    fresh = next(n for n in ast.parse((CAL / "e2e_benchmark.py").read_text()).body if isinstance(n, ast.FunctionDef) and n.name == "fresh_selected")
    saved = next(n.value for n in ast.walk(fresh) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "out" for t in n.targets))
    saved_fields = [k.value for k in saved.keys]
    assert saved_fields == ["recorded", "draws", "params"]
    ap = json.loads((CAL / "v2_dev/a_power/a_power_outers.json").read_text())
    assert all(set(o) == {"dir", "recorded", "v1"} for o in ap["outers"].values())
    # Tiny geometrical fixture only; do not query production banks.
    ties = cKDTree(np.zeros((8, 2)))
    direct = ties.query([0., 0.], k=3)[1].tolist()
    truncated = ties.query([0., 0.], k=4)[1][:3].tolist()
    assert set(direct) != set(truncated)
    primary = json.loads((CAL / "freeze_v1/bank_primary_meta.json").read_text())
    retained = sum(t["selected"] for t in primary["tasks"])
    result = {
        "frozen_bank_and_fitter_sources_match": True,
        "original_v1_outer_schema": saved_fields,
        "A_power_compact_outers_lack_theta": True,
        "truth_source_contract": "Extract six-coordinate theta from original v1 selected[population].params, bind source row hashes and IDs. A compact observed-mode rerun is not a source of true theta; it stores params={}.",
        "current_availability_limit": "Source schema verified locally; no new read of all remote original row payloads in this review.",
        "tie_fixture": {"direct_K3_members": direct, "truncated_K4_members": truncated,
                        "membership_differs_despite_equal_distances": True},
        "membership_contract": "Use k=K (not truncated K+1), identical bank/shard row order, mask/MAD and pinned runtime; bind actual draw IDs. A matching rounded Kth distance does not certify membership at ties.",
        "Stage0_arithmetic": {"cells": 8, "outer_population_pairs_per_weight_type": 8*200*9,
                              "noisy_weight_evaluations": 8*200*9*2000,
                              "ideal_weight_evaluations": 8*200*9*2000,
                              "distinct_outer_population_neighbour_sets": 4*200*9,
                              "member_occurrences_if_shared_across_levels_and_weight_types": 4*200*9*2000,
                              "primary_retained_members": retained,
                              "GH40_evaluations_for_occurrences_if_reused": 4*200*9*2000*40,
                              "GH40_evaluations_if_needlessly_applied_to_all_bank_members": retained*40},
        "resource_limit": "Thirty minutes is a planning estimate, not a measured bound; preserve one-pass/per-population processing and record elapsed time/peak memory. Stage0 measures support diagnostics only, with no fitted classification or Stage1 permission.",
        "ESS100_interpretation": "Declared concentration flag for exploratory diagnostics; not a demonstrated validity threshold. Report continuous ESS/max-weight share and any-of-nine fractions by scenario and n for both noisy and ideal weights."
    }
    return populations, result


def main():
    populations, source = source_checks()
    result = {"scope": "Rev2 numerical/seed/source fixtures only; no bank payload/query, E sampling, fits or remote compute",
              "time_hobart": datetime.now(ZoneInfo("Australia/Hobart")).isoformat(),
              "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "draft_sha256": sha(DRAFT),
              "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
              "numerical_fixtures": numerical_checks(), "stream_fixtures": stream_checks(populations), "source_and_feasibility": source}
    path = Path(__file__).with_suffix(".json"); path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(path), "quadrature_cases": result["numerical_fixtures"]["GH40_vs_adaptive_quad_cases"],
                      "initial_states_checked": 16000, "duplicate_initial_states": result["stream_fixtures"]["duplicate_initial_states_in_enumeration"]}))


if __name__ == "__main__":
    main()
