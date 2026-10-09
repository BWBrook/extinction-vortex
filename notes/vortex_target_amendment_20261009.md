# Adopted target amendment: reconstructed T1–T4

Barry submitted this decision on 9 October 2026 at 11:06:47 AEDT (Hobart)
through Decision Inbox. It was collected and verified on the same date.
The immutable [response](../docs/decisions/01663ea4-7564-41c6-abf4-d50cec5448c5.md)
and [JSON record](../docs/decisions/01663ea4-7564-41c6-abf4-d50cec5448c5.json)
are the authority for this amendment.

The question asked which scientific target and primary estimator Barry approved.
He selected `approve_ri_primary`:

> Approve reconstructed T1-T4 with the simpler random-intercept primary; random-slope model as sensitivity (Fable proposal).

No alternative or comment was supplied, and the decision was not deferred.
This resolves the primary-model choice recorded in the
[earlier proposal](vortex_amendment_proposal_20261009.md). That proposal and the
original pre-fit specifications remain as development history.

## Adopted specification

- The primary empirical target is a **labelled reconstruction of T1–T4** for
  the nine deposited Williams series. T5 and time-to-extinction scaling are
  descriptive. The full historical discrepancy table remains in the report.
- Use a **random-intercept multilevel model with AR(1) errors and marginal ML**
  as primary. The random-intercept-and-slope model is a mandatory sensitivity.
  Apply each stated estimator consistently to observations and simulations.
- T1 is the slope of log growth on years to the endpoint. T2 excludes exactly
  the final transition (`s >= 1`). T3 regresses squared conditional response
  residuals from T1 on years to the endpoint. T4 refits the mean model on the
  retained T2 transitions before calculating its conditional squared residuals
  and variance regression.
- Preserve the unchanged deposited data and the first-recorded-count-<=1
  endpoint convention. Replace that endpoint with one for log-growth
  calculations only. Preserve the exposure record and unresolved census-unit,
  original-window and interpolation questions.
- The wide prior (b) is proposed for primary validation, with its existing
  specification: `logit(s) ~ Normal(0, 1.5^2)`,
  `log(f) ~ Uniform(log(0.01), log(2))`, and
  `sigma ~ Uniform(0.02, 1.0)`. Supported literature priors remain explicitly
  unvalidated numerical sensitivities until separately validated.

## Interpretation and continuing work

This is an amendment made after exposure to the published and reconstruction
results. Historical Stage B reconstruction remains unpassed. Subsequent
validation evaluates the frozen chosen procedure; its scope does not extend
automatically to the adaptive history of selecting that procedure.

The existing source work and synthetic development continue. Fable owns the
formal protocol update, calibration and interpolation repairs and measured
benchmark. Astra reviews their inferential implications and evidence. The
[protocol 0.4 review](astra_protocol04_review_20261009.md) remains the technical
repair list; Barry's model choice supersedes its primary-model recommendation.

The questionnaire explicitly retained the validation freeze, unresolved
source/model assumptions and measured production allocation as prerequisites
for empirical testing. Neither prior has yet passed production validation.
Author contact and software purchases were outside this approval.

## Collection verification

- Questionnaire: `01663ea4-7564-41c6-abf4-d50cec5448c5`.
- Request: `project-vortex-amendment-20261009-codex`.
- Canonical response JSON SHA-256:
  `6175e7b828a0f636d7e219ea5dc534b55a043f4631d7eb4c1d6d12f061ccd33c`.
- Independently verified the canonical hash, exact original question definition,
  every Markdown option/selection, empty comments/alternatives and no deferral.
- The archived listing records `collected_at = 2026-10-09T00:11:08.058Z`;
  the active project listing is empty. Both listings were exhausted.
