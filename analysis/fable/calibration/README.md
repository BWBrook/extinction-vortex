# Fable calibration development (9 October 2026)

All runs here are synthetic, under prior (b). The only empirical quantities
used are the observed calibration summaries C for the nine deposited series
(exposure row E19). Not computed: T1–T4 null comparisons, p-values and
validation draws.

| Script | Output | Finding |
|---|---|---|
| `bank_benchmark.py` | `bank_benchmark.txt` | Exact-endpoint acceptance is 0.6–1.4% of prior draws. A tolerance of 0.25 is infeasible. |
| `bank_tolerance_scan.py` | `bank_tolerance_scan.txt` | Under plain M0, several series sit in the tails of the selected predictive: red-cockaded woodpecker step variance at the 0.2nd percentile, turtle autocorrelation at the 99.6–99.7th. Banks of 10^8–10^9 draws would be needed. |
| `bank_rho_scan.py` | `bank_rho_scan.txt` | Adding an AR(1) environment improves autocorrelation but not step variance. |
| `bank_catastrophe_scan.py` | `bank_catastrophe_scan.txt` | Adding catastrophes as well (M0\*) puts every series between the 3rd and 97th percentiles. Banks need 2.4×10^6–5.7×10^7 draws at tolerance 1.0. |
| `make_synthetic_sets.py`, `time_estimator.R` | `time_estimator.txt` | T1–T4 cost 0.15 s per nine-population dataset, with no failures in 20. |

Run from the repo root, for example:

    ~/.local/bin/uv run --with numpy python analysis/fable/calibration/bank_catastrophe_scan.py 2000000

Overflow rule: trajectories above 10^9 are rejected and counted.
Percentiles use strict inequality, so discrete minima such as the crow's
zero-increase fraction show as 0.
