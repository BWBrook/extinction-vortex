# Astra Stage B v0: reconstruction remains unresolved

Source frozen at `418a5fffcec245821c801840486f7b1c2ee035f0`, before Astra's
first empirical fit and before opening Fable's implementation. The earlier
specification is in `bd4c882`; the residual-subsetting clarification preceded
fitting. Fable's board summary 1139 had already exposed fitted results, so this
is a separate implementation, not a blind reconstruction.

The 54 declared fits ran on deep-server in tmux on 8 October 2026,
06:05:43–06:06:29 UTC (17:05:43–17:06:29 AEDT). The captured batch includes
synthetic tests, 149 growth observations, all optimization attempts, coefficients,
empirical-Bayes scaling effects, full R objects, runtime details and SHA-256
manifests in [results_v0](results_v0/). Exit status was 0. Source and input hashes
were verified again after retrieval. Nothing in this batch computes an empirical
conditional-null p-value or uses final validation draws.

## Reconstruction outcome

The predeclared primary candidate uses random intercepts and slopes with AR(1)
errors. The random-intercept-only candidate is a diagnostic. Below T2 excludes
exactly the final transition (s >= 1); T3/T4 use conditional response residuals,
with the T4 mean model refitted on retained transitions. Every alternative
declared in the specification is retained in `coefficients.csv`.

| Statistic | Published | Primary candidate | RI-only diagnostic | Absolute tolerance |
|---|---:|---:|---:|---:|
| T1 | 0.034 | 0.033684 | 0.033443 | 0.0005 |
| T2 | 0.011 | 0.013081 | 0.011229 | 0.0005 |
| T3 | -0.047 | -0.043176 | -0.047870 | 0.0005 |
| T4 | -0.012 | -0.009066 | -0.011853 | 0.0005 |

Only T1 passes that comparison for the primary candidate; only T2 and T4 pass
for the RI-only diagnostic. Numerical proximity is not exact reproduction.
No declared candidate reproduces the four slopes together at published precision.

The pooled scaling slope is 1.18737 with AR(1) and random intercepts/slopes
(phi = 0.990284), versus the reported 9.1. Removing residual autocorrelation
gives 5.93745. Neither identifies the historical estimator. The period-additive,
period-interaction and separately fitted period curves are diagnostic models,
not accepted implementations of T5. F&H report a period-effect z score and
two plotted curves, not the exact single period coefficient required by the
current protocol label.

All 54 selected fits have optimizer status 0, but 41 have near-singular random
covariance by the recorded diagnostic, two have |phi| > 0.99, and two have a
covariance parameter at its numerical bound. The diagnostic flags overlap.
Some independent-error fits reached different likelihoods from different starts
(largest range about 1.65 log-likelihood units); the best objective is retained,
with every start recorded. Status 0 is not proof of a global maximum or of a
well-identified covariance model.

## Verification and limits

The profiled likelihood agrees with an independently assembled dense Gaussian
calculation. Two synthetic models agree with `nlme` ML in coefficients,
likelihood, conditional residuals and empirical-Bayes effects; log-likelihood
differences were 8.53e-6 (RI) and 3.10e-9 (RI plus slope). Endpoint/indexing tests
cover first census <= 1, endpoint replacement by one and refusal to treat a gap
as one annual transition. The M0 invariant results are also archived here.

Williams counts are used unchanged, with no truncation chosen to recover F&H
numbers. The crane's first census <= 1 is in 2002: its preceding count is two,
which resolves the earlier final-count discrepancy under F&H's endpoint rule.
Original windows, interpolations and some census units remain unresolved. These
gaps, the estimator ambiguity and T5 prevent a production freeze.

## Reproduction

Run from the root of the source commit with R and recommended package `nlme`:

```sh
Rscript analysis/astra/stage_b/test_gaussian_ml.R
Rscript analysis/astra/m0/test_m0.R
Rscript analysis/astra/stage_b/run.R /path/to/new/output
```

For a captured remote batch, put the source commit SHA in `SOURCE_COMMIT` and
invoke `bash analysis/astra/run_stage_b.sh SOURCE_ROOT NEW_ARTIFACT_DIR` in tmux.
The source snapshot used here remains at
`/data/codex/repos/extinction-vortex-selection-astra-20261008`; remote artifacts
are at `/data/codex/artifacts/extinction-vortex-selection-astra-20261008-v0`.
The script refuses to overwrite an existing artifact directory.

## Post-freeze review repairs

A read-only audit after the v0 result freeze found no fatal likelihood or
generator error. It identified a runner guard: a selected fit with nonzero
optimizer status could feed a subsequent variance fit. The current runner
retains such a fit for diagnosis, marks it invalid and skips its descendants.
All 54 archived v0 selections had status zero, so this guard changes none of
their interpretation. The objective sentinel is excluded from the start-range
diagnostic; observation indices and input-mapping assertions were added.
The frozen source and results remain available at their original commits;
these later edits do not overwrite that evidence. The covariance formulas and
empirical model specification are unchanged.

## Comparison after both v0 freezes

The [comparison script](compare_fable_v0.R), frozen at `09f8c6f`, ran on
deep-server after inspecting Fable's code at `f71512c`. Results and hashes are
in [comparison_v0](comparison_v0/); exit status was 0.

All 149 growth and scaling observations match after ordering by population and
year. For 14 shared model fits, Astra's likelihood and profiled fixed effects,
evaluated at Fable's fitted covariance parameters, agree with `nlme` to maximum
absolute differences of 6.25e-13 in log likelihood and 8.08e-14 in coefficients.
This checks the likelihood construction; it does not establish identical
optimization or recover the historical analysis.

Separately optimized RI slopes are very close. Some random-slope models differ:
for example, the scaling slope is 1.18737 in Astra v0 and 1.14468 in the peer
rerun. Both covariance fits are near boundaries. Variance-regression likelihoods
must not be compared as though their responses were identical when their
upstream fitted mean models differ. The comparison CSV retains these differences.

Fable's snapshot has no T4 fit and no M0 sampler to compare. Astra's M0 source
and invariant evidence are ready for that later comparison. Both implementations
share the historical-method uncertainties and current source limitations.
