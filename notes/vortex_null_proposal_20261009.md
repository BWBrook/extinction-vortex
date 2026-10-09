# Primary-null choice for the vortex study

9 October 2026. Proposal after Astra's review of draft 0.7 (`5ace89e`).
Barry's choice is pending; this note does not promote a primary model.

**Recommendation: make the no-feedback AR(1)-plus-catastrophe model (`ar_cat`)
the primary development candidate, retaining iid Gaussian environmental noise
as a mandatory sensitivity.** Both models exclude direct abundance feedback
from survival and recruitment; ar_cat allows environmental persistence and
occasional external shocks. Its environmental transition law does not depend
on abundance, although environment and abundance can be statistically associated.

The scientific reason is to ask whether terminal signatures exceed a more
plausible range of external population fluctuations before attributing anything
to feedback. Rejection still concerns this specified model and its priors;
it would not identify feedback or prove that other no-feedback models fail.
Non-rejection would not establish that feedback is absent.

The iid option keeps a simpler, narrower primary reference, with ar_cat as the
mandatory sensitivity. It makes the primary question about independent
environmental noise, so a primary rejection is easier to explain through
omitted temporal persistence or shocks. Neither option settles the biological
mechanism or removes model dependence.

## What the development evidence says

- Among the implemented candidates, ar_cat alone met the earlier bank-budget
  rule near the observed calibration summaries. This is computational
  feasibility, not evidence that catastrophes are biologically necessary.
  The Student-t comparator has been retired.
- In 30 feedback trials per design at Delta10 = 0.5, raw diagnostic p < .05
  occurred in 29/30 iid trials and 21/30 ar_cat trials. These are different
  matched generator-and-reference designs sharing random streams. Their
  difference does not isolate the effect of making the reference more flexible,
  and these proportions are not validated power.
- Under the tested hard distance cutoff, only 20/30 and 14/30 feedback trials
  were detections; 9/30 and 13/30 were calibration-indeterminate. The null
  non-accept counts were 7/30 and 9/30. This version fails the intended gate.
- We propose keeping the nearest 2,000 simulations without that hard cutoff,
  using banks with 2 billion raw draws per population. The larger-bank radius
  estimates are projections. Removing abstention does not ensure calibration;
  the actual frozen implementation needs new validation and radius diagnostics.

The model, priors and calibration proposal follow exposure to observed C and
synthetic development results. This remains an adaptive reanalysis. ar_cat's
catastrophe priors are exploratory; they are not estimated for these nine
populations. The [review](astra_protocol07_review_20261009.md) gives the checks,
qualifications and remaining implementation repairs.

## What an answer changes

An approval selects the primary model for the next development and validation
design, with the other model mandatory as a labelled sensitivity. It preserves
Barry's reconstructed T1–T4 target, RI primary estimator and random-slope
sensitivity. It does not freeze the priors, beta_min, corner scenarios, banks,
resource allocation or production algorithm; those still need a concrete final
design. It does not authorize empirical p-values before validation.

Fable would incorporate the selected model and routine repairs; Astra would
review the resulting validation design and measured costs. Existing synthetic
development authority continues. Neither agent will turn this choice into a
claim that the scientific or validation gates have passed.
