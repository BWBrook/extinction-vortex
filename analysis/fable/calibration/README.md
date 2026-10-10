# Fable calibration development (9 October 2026)

All runs here are synthetic, under prior (b). The only empirical quantities
used are the observed calibration summaries C for the nine deposited series
(exposure row E20). Not computed: empirical T1–T4 null comparisons, empirical
p-values and validation draws. Synthetic-outer T1–T4 are computed in the
end-to-end runs (E23).

| Script | Output | Finding |
|---|---|---|
| `bank_benchmark.py` | `bank_benchmark.txt` | Exact-endpoint acceptance is 0.6–1.4% of prior draws. A tolerance of 0.25 is infeasible. |
| `bank_tolerance_scan.py` | `bank_tolerance_scan.txt` | Under plain M0, several series sit in the tails of the selected predictive: red-cockaded woodpecker step variance at the 0.2nd percentile, turtle autocorrelation at the 99.6–99.7th. Banks of 10^8–10^9 draws would be needed. |
| `bank_rho_scan.py` | `bank_rho_scan.txt` | Adding an AR(1) environment improves autocorrelation but not step variance. |
| `bank_catastrophe_scan.py` | `bank_catastrophe_scan.txt` | Adding catastrophes as well (M0\*) improves marginal coverage. The original "3rd–97th percentile" claim was false (turtle A ACF 97.4); superseded by `compare_nulls_v1/`. |
| `compare_nulls.py` | `compare_nulls_v1/` | Common-footing comparison of five nulls (2×10^7 draws each). Only ar_cat meets the observed-C planning rule for all nine; the Student-t comparator is retired as evidence (infinite-mean recruitment). |
| `e2e_benchmark.py`, `tstats_batch.R` | `e2e_v1/` (hard-tolerance version) | End-to-end procedure on synthetic outer datasets. Current version: k-NN library, fixed-denominator outcome per trial, output contract v2. |
| `run_discrimination.sh` (commit `14f974b`), `score_discrimination.py` (contract v1) | `discrimination_v1/` | iid vs ar_cat, null and M_A (Δ10 = 0.5), 30 trials per arm, 2×10^8 banks. Calibration shortfalls make 23–43% of trials indeterminate. |
| `outer_coverage.py`, `coverage_summary.py` (commit `5ace89e`) | `coverage_v1/` | All-nine hard-tolerance coverage for fresh outer datasets, with bank-size projections. Current versions report k-NN radii for sharded banks and scenario lists. |
| `build_bank.py` | deep-server `banks10x_*` | Sharded 2×10^9-draw development banks (ar_cat, iid); `bank.load_bank` checks the shards. |
| `effect_target.py`, `run_dev_design.sh`, `empirical_position.py` | `dev_design_v1/` | β_min (Δ10 = 0.075) and corner scenarios under ar_cat; measured radii in the 10× banks; empirical position (ar_cat 64th, iid 97th percentile); measured cost. |
| `run_power_screen.sh` (commit `f8546ec`), `score_discrimination.py` (contract v2) | `power_screen_v1/` | ar_cat k-NN at production counts: detections 1/30 (null), 1/30 (β_min), 2/30 (2·β_min), 8/30 (Δ10 = 0.3), 18/30 (Δ10 = 0.5). |
| `test_bank.py`, `time_generators.py` | `alt_check_v1/` | M_D and M_O generators: 28 limiting-case checks; scenario plumbing; generation cost 5–9 CPU-s per dataset, negligible against fitting. |
| `run_arms.sh` | `dev_screen200_v1/` (running) | The §4.1 development screens: 200 under the ar_cat null and 200 at β_min, at production counts. |
| `run_production_banks.sh` | deep-server `production_banks_*` (queued) | Designated primary, stability and iid banks (seed families 8.1, 8.2, 8.3 × 10^12); β_min, corners and empirical position recomputed. |
| `make_manifest.py`, `validate.py`, `run_validation.sh`, `collect_validation.py`, `test_validation.py` | (validation, after freeze) | Executable validation: 17 blocks × 10 chunks; at most three bank-holding slots; pooled gates on full denominators; 19 mocked-fit checks. |
| `empirical_q1.py` | (empirical, after validation) | Guarded Q1 entry point; refuses to run without a passing validation summary for the same manifest; never run. |
| `make_synthetic_sets.py`, `time_estimator.R` | `time_estimator.txt` | T1–T4 cost 0.15 s per nine-population dataset, with no failures in 20. |

Run from the repo root, for example:

    ~/.local/bin/uv run --with numpy python analysis/fable/calibration/bank_catastrophe_scan.py 2000000

Overflow rule: trajectories above 10^9 are rejected and counted.
Percentiles use strict inequality, so discrete minima such as the crow's
zero-increase fraction show as 0.
