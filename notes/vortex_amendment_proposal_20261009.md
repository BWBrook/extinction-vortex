# Proposed four-statistic reconstruction amendment

9 October 2026, Hobart. Astra's recommendation after reviewing protocol 0.4.

**Historical proposal.** Barry subsequently approved the reconstructed T1–T4
target with **RI primary and the random-slope model as sensitivity**. See the
[adopted amendment](vortex_target_amendment_20261009.md) and immutable response.
The original recommendation below is preserved; production remains unfrozen.

**Original proposal, before Barry's decision:** Fable
proposed RI as primary; this version recommends retaining Astra's pre-fit
random-slope candidate. That difference was unresolved when this was written.

**Decision proposed.** Continue toward a conditional-null analysis of four
explicitly reconstructed terminal-trajectory statistics in the deposited nine
series. Report T5 and the time-to-extinction scaling fits descriptively. Use the
wide prior (b) for primary development and eventual validation; literature priors
remain numerical sensitivities until independently supported and validated.

Exact Fagan–Holmes reproduction has not succeeded. The approved first tranche
already allowed reporting a labelled reconstruction. This amendment additionally
narrows the eventual primary statistic set and fixes its interpretation; it does
not declare the historical reconstruction passed.

## Concrete target

- **Data:** the unchanged Williams deposit, IDs 14, 15, 6, 20, 21, 10, 4, 8 and 9,
  from the first deposited census through the first recorded count <=1. Preserve
  the original endpoint in the data; replace it by one only for log-growth
  calculations. Preserve and disclose the known filled counts and unresolved
  census-unit mappings.
- **Primary estimator:** the random-intercept-and-slope AR(1) marginal-ML candidate
  declared in Astra's pre-fit specification (`bd4c882`), using calendar-year lags.
  RI-only is a mandatory sensitivity. Neither is represented as the identified
  historical estimator. Retaining the original candidate avoids promoting a
  diagnostic simply because its fitted values are closer to the printed results.
- **T1:** the slope of log growth on years to the endpoint, including the final
  transition. **T2:** repeat after excluding exactly that transition (`s >= 1`).
  **T3:** the slope of squared conditional response residuals from T1 on years
  to the endpoint. **T4:** the equivalent variance regression after refitting
  the mean model on T2's retained transitions. Use the same covariance structure
  throughout. Freeze numerical fitting and failure rules before validation.
- **T5/scaling:** report the published curves and all declared reconstruction
  diagnostics, with their unresolved estimator identity; omit these from the
  primary joint test. Do not interpret their omission as a negative result.

| Statistic | F&H printed | Proposed primary | RI sensitivity |
|---|---:|---:|---:|
| T1 | 0.034 | 0.033684 | 0.033443 |
| T2 | 0.011 | 0.013081 | 0.011229 |
| T3 | -0.047 | -0.043176 | -0.047870 |
| T4 | -0.012 | -0.009066 | -0.011853 |

These are the already frozen development results, not new tests. The table and
its discrepancies remain in the report regardless of the empirical null result.

## What the eventual result could claim

The question becomes whether these reconstructed decline and variability
summaries depart from a specified no-feedback model under matched selection.
It cannot establish that the exact published F&H estimates have been explained,
or identify the biological cause of a departure. Biological interpretation also
depends on the unresolved observation and census-class mappings.

This is an exposed reanalysis: published outcomes and reconstruction results were
already known. Subsequent validation evaluates the frozen procedure, not a fully
blinded analysis or the adaptive history of choosing it. Agreement across the
primary and sensitivity estimators is informative; it is not a correction for
selection or multiplicity. Any validated labels must state that scope.

Prior (b) keeps `logit(s) ~ Normal(0, 1.5^2)`, `log(f) ~ Uniform(log(0.01),
log(2))`, and `sigma ~ Uniform(0.02, 1.0)`. It is proposed for validation, not
already validated. No same-trajectory survival estimate supplies an independent
prior. Unsupported literature priors receive no validated outcome labels.

## What continues and what remains gated

Synthetic calibration development and measured cost benchmarks can continue
under the existing authority. Fable will repair the
[reviewed specifications](astra_protocol04_review_20261009.md): identical final
procedures for validation and observation, frozen bank rules, conservative
failure handling, executable ties, exact scenario definitions and an attainable
effect target. The adjacent-gap interpolation defect must be repaired before
that operation is used.

No empirical p-values follow from approving this amendment alone. The validation
freeze, source/model assumptions and measured production allocation remain to
be settled. Author contact is optional and separate; buying software is not a
substitute for recovering historical inputs. If original inputs/settings are
later recovered, preserve this analysis and document any replacement before
running dependent tests.

**Recommendation:** adopt this narrowed target and interpretation, while the
agents complete development and return the measured production proposal. If
exact historical reproduction is essential to the paper's purpose, retain that
gate instead and pursue the missing original inputs before an empirical test.
