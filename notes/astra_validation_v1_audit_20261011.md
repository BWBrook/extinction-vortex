# Independent audit of frozen validation v1

Astra — 11 October 2026, Australia/Hobart. Completed synthetic validation;
no empirical conditional-null test.

**V-fail is confirmed.** Independently recomputing the scores from all 7,900
T files reproduces every reported outcome and p-value bound. The failed
low-survival block has 148 rejections out of 1,000. The audit found no
block-specific configuration or scoring defect that explains the failure.
This is a failure of the declared validation requirement; it does not identify
feedback, or its absence, in the empirical populations.

## Evidence and independence

- Frozen source: `52779d01468dac186c19810b59c8295dbedd212f`.
- Manifest SHA-256:
  `96603037ec05036153f67b649757d067ca193c5e0a8610d3b855ef8f22139429`.
- Retrieved archive SHA-256:
  `312d91e4f52b9e973a313f2242752ac013e35c827ef9d6a21a25c240f3a507f1`.
- Summary SHA-256:
  `c0eaf012ded16d79b82f894c76f13bd281a287660ef01581abe6d7a9949d1154`.

[Raw scoring code](../analysis/astra/validation_v1_audit/raw_score.py) imports
no production scoring modules. It independently estimates covariance, solves
the Mahalanobis distances, counts conservative tail ranks and applies the
frozen gates. All observed/training/test row positions and shapes match;
all p-value bounds agree within 1e-12. The compressed archive checksum and
the contents of **all 8,339 extracted regular files** match. Per-file hashes,
all trial scores and signed residuals are retained in
[the compressed audit receipt](../analysis/astra/validation_v1_audit/raw_score.json.gz).
The score pass ran on deep-server in 35.3 seconds with four bounded CPU
workers; it fitted no models and generated no new trajectories.

The separate [provenance audit](../analysis/astra/validation_v1_audit/provenance_audit.json)
checks all 170 chunk metadata files and all 9,000 selected population
trajectories in the 1,000 low-survival trials. They agree with the frozen
parameters, census designs, endpoint selection and budgets. All 12 bound
source hashes match. Its 180 remote input hashes also match the verified
archive. The low-survival block changes the outer nuisance values only:
references retain the same primary `ar_cat` bank and K = R_train = R_test =
2,000 used by the other blocks. That is the declared design, not an accidental
switch to a different reference.

The audit is informed by Fable's reported results; independent code is not
blinded reasoning or independent simulation. Reference indices and temporary
input `sets_*.csv` files were not retained. Actual reference membership cannot
be checked from the archive alone without replaying the banks and random
streams. The audit does not refit models, replay generators or verify
unrecorded yearly Poisson-rate/cap histories.

## Confirmed gates and a reporting correction

| Scenario | Rejections / intended n | Relevant exact bound | Frozen decision |
|---|---:|---:|---|
| Prior-predictive null | 46 / 1,000 | upper 98.75%: 0.06312 | pass |
| High-sigma null | 41 / 1,000 | upper 98.75%: 0.05736 | pass |
| Low-survival null | **148 / 1,000** | **upper 98.75%: 0.17498** | **fail** |
| Strong-environment null | 30 / 1,000 | upper 98.75%: 0.04446 | pass |
| M_A at beta_min | 21 / 300 | lower one-sided 95%: 0.04738 | power fails |

The null rule allows at most 60 non-acceptances per 1,000; the power rule
requires at least 224 rejections per 300. All 7,900 trials resolve. There are
no discrepancies between nonfinite statistic vectors and failure flags, and
no trial requires covariance shrinkage. All 17 rejection totals match the
committed summary: 46, 41, 148, 30, 21, 25, 16, 26, 17, 15, 17, 42, 40, 28,
118, 206 and 11.

**Correction to the initial narrative:** fit failures are zero in all gating
blocks, but not in every block. There are four failed T vectors among
31,607,900 intended dataset vectors: one in block 14, two in block 15 and
one in block 16. Each of those descriptive blocks has denominator 1,200,300.
The machine-readable summary already records these correctly. This correction
does not alter any outcome or gate. Successful estimator fallbacks are logged
separately and are not synonymous with failed fits.

The actual empirical guard, called with the frozen manifest and completed
summary, refuses the result before preflight or bank access; see
[receipt](../analysis/astra/validation_v1_audit/empirical_guard.json).
V-fail overrides the O1/O2/O3 branches. Protocol §1's available wording is
*insufficient identification*; there is no empirical non-rejection to report.

## What the failure suggests, and what remains open

The predeclared radius strata reproduce as 33/250, 43/318, 40/241, 18/133
and 14/58 in the low-survival block. These calculations use stored
four-decimal distances, so membership very close to a boundary is subject
to that precision. Failures occur across the radius range; this does **not**
exclude local approximation error. A maximum radius loses information about
directional mismatch, local density and the nine separate neighbourhoods.

A post-hoc diagnostic from the existing T files is more specific. For each
trial define z_k = (T_observed,k - mean_train,k) / sd_train,k. Its mean across
the 1,000 trials is:

| Null block | T1 | T2 | T3 | T4 |
|---|---:|---:|---:|---:|
| Prior predictive | 0.003 | 0.023 | 0.036 | 0.018 |
| High sigma | -0.054 | -0.040 | 0.217 | 0.232 |
| Low survival | **-1.761** | **-1.580** | 0.293 | 0.346 |
| Strong environment | 0.081 | 0.192 | 0.173 | -0.011 |

The low-survival mismatch includes a marked location shift in T1 and T2.
These marginal residuals are correlated; their means neither partition the
joint statistic nor identify the biological or computational cause. They are
development diagnostics, not new validation criteria or grounds to drop a
statistic. Full block summaries are in
[summary.json](../analysis/astra/validation_v1_audit/summary.json).

Exact C-conditioning would provide exchangeability under the selected
**prior-predictive** law, as protocol §2.1 states. It need not control error
at each fixed nuisance vector. Thus the prior-predictive pass and fixed-corner
failure can coexist without a software defect. This distinction concerns the
chosen nuisance treatment in a composite null; see
[Bayarri and Berger's author-hosted account](https://www2.stat.duke.edu/~berger/papers/98-40.html).
The present evidence does not separate that mechanism from finite-library
approximation or an untested generator/estimator issue. Lowering survival with
recruitment unchanged also changes expected growth and demographic variance;
the corner is not an isolated survival effect.

**Disposition:** preserve v1 and its failure; proceed with the bounded
[v2 development and prospective-freeze brief](astra_v2_development_20261011.md).
No empirical execution follows this audit.
