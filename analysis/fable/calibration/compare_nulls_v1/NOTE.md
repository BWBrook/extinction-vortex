# Common-footing comparison of candidate no-feedback nulls (v1, 9 October 2026)

Run on `deep-server` in tmux:
- source commit in `SOURCE_COMMIT`;
- file hashes in `source_sha256.txt`;
- host details in `host.txt`;
- wall time and memory in `resources.txt`.

Bank files (`.npz`, 432 MB) stay on deep-server under
`/data/fable/vortex/compare_nulls_20261009T013137Z/out`. Each keeps the selected
trajectories, draw indices, parameters, seed and overflow count.

**Design.** Five variants × nine populations × 2×10^7 draws from prior (b),
all on the same footing:
- the same exact matched selection;
- the same overflow cap (10^9, applied to both counts and Poisson rates);
- the same three calibration summaries;
- the same tolerance (standardised distance 1.0).

The variants are those defined in `bank.py`: iid, ar, cat, ar_cat and heavy.

**What the table reports** (`comparison.csv`):
- mid-rank percentiles of the observed summaries, with ties counted half;
- joint tolerance hits;
- exact 95% Clopper–Pearson intervals;
- the draws needed for K = 2,000, at the point estimate and at the
  conservative bound;
- under the 0.6 rule, 3 × `draws_for_K2000_upper` must stay within the
  10^9 cap.

**Findings.**

| Variant | Result | Most demanding population |
|---|---|---|
| iid | **Infeasible** for both turtles. ACF at the 99.6–99.7th percentile; red-cockaded woodpecker msq at the 0.2nd percentile. | Turtle B: 3 × 7.3×10^9 |
| heavy | Indistinguishable from iid, so continuous heavy tails do not help. | Turtle B: 3 × 5.2×10^9 |
| ar | Fixes the turtles' ACF (95–96th percentile) but not the woodpecker's msq (0.2nd). Feasible, but woodpecker msq stays extreme. | Turtle B: 3 × 4.4×10^8 |
| cat | Helps the woodpecker's msq (1.8th percentile) but not the turtles' ACF (99.7th). Borderline: turtle B needs 3 × 1.1×10^9. | Turtle B: 3 × 1.1×10^9 |
| **ar_cat** | **Feasible for all nine.** Every percentile lies between 2.0 and 96.5. | Turtle B: 3 × 1.1×10^8 |

Overflow rates are 0–3.3% under every variant; the wild dog is the highest,
because it starts at 77.

**Interpretation, development only.**
- The turtle series need an autocorrelated environment.
- The woodpecker and turtle step variances, together with the terminal drops,
  need catastrophes.
- Neither feature is feedback. All five variants satisfy the structural H0
  in protocol §3.1.
- These comparisons used the observed calibration summaries (exposure row E20)
  but no T1–T4 null comparison.
- Choosing a primary null from them is an adaptive, exposed decision. It is
  for Barry, after the bounded discrimination check.
