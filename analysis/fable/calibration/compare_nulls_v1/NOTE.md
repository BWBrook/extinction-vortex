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

**Findings** (corrected 9 October after Astra's re-evaluation, 1228; the
first version misapplied the rule to AR and catastrophes and quoted
3 × the upper requirement loosely). Rule: 3 × `draws_for_K2000_upper` ≤ 10^9.

| Variant | Within the cap | Largest requirement (3 × upper), raw draws | Notes |
|---|---:|---|---|
| iid | 7/9 | turtle B 2.19×10^10; turtle A 5.48×10^9 | Turtles' ACF at the 99.6–99.7th percentile; red-cockaded woodpecker msq at the 0.2nd. |
| ar | 7/9 | turtle B 1.31×10^9; wild dog 1.23×10^9 | Turtles' ACF fixed (95–96th); woodpecker msq still at the 0.2nd. |
| cat | 7/9 | turtle B 3.31×10^9; turtle A 2.57×10^9 | Woodpecker msq improved (1.8th); turtles' ACF not (99.7th). |
| **ar_cat** | **9/9** | 3.37×10^8 | Every percentile between 2.0 and 96.5. |
| heavy | 7/9 | turtle B 1.57×10^10; turtle A 5.70×10^9 | **Retired as evidence** (below). |

Overflow rates are 0–3.3% under every variant; the wild dog is the highest,
because it starts at 77.

**Heavy comparator retired.** For a standardised Student-t Z with finite ν and
σ > 0, E[exp(σZ)] is infinite, so `f·exp(σZ − σ²/2)` has infinite mean
recruitment before the cap; the Gaussian centring does not normalise it, and
the cap then changes the sampled law (Astra 1228). The comparison is not a
finite-mean match to the Gaussian model, and it is not evidence against
continuous heavy tails. AR plus continuous heavy tails was not tested.

**Interpretation, development only.**
- Among the five exploratory candidates actually implemented, only ar_cat
  meets the observed-C planning rule. This is planning feasibility around the
  observed summaries, not outer-dataset coverage (see `../discrimination_v1/`)
  and not evidence that the populations require catastrophes or an AR
  environment: AR plus a finite-mean continuous heavy tail is untested, and
  the priors are exploratory.
- Neither feature is feedback. All five variants satisfy the structural H0
  in protocol §3.1.
- These comparisons used the observed calibration summaries (exposure row E20)
  but no T1–T4 null comparison.
- Choosing a primary null from them is an adaptive, exposed decision. It is
  for Barry, after the bounded discrimination check.
