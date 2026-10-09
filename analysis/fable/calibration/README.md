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
| `e2e_benchmark.py`, `tstats_batch.R` | `e2e_v1/` | End-to-end procedure on synthetic outer datasets; each trial now gets a fixed-denominator outcome. |
| `run_discrimination.sh`, `score_discrimination.py` | `discrimination_v1/` | iid vs ar_cat, null and M_A (Δ10 = 0.5), 30 trials per arm, 2×10^8 banks. Calibration shortfalls make 23–43% of trials indeterminate. |
| `outer_coverage.py`, `coverage_summary.py` | `coverage_v1/` | All-nine library coverage for fresh outer datasets, with bank-size projections. |
| `make_synthetic_sets.py`, `time_estimator.R` | `time_estimator.txt` | T1–T4 cost 0.15 s per nine-population dataset, with no failures in 20. |

Run from the repo root, for example:

    ~/.local/bin/uv run --with numpy python analysis/fable/calibration/bank_catastrophe_scan.py 2000000

Overflow rule: trajectories above 10^9 are rejected and counted.
Percentiles use strict inequality, so discrete minima such as the crow's
zero-increase fraction show as 0.
