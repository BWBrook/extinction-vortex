# Haley descriptive protocol review

**Recommendation: proceed to the four finite descriptive deliverables.**
Fable can incorporate the amendments below while producing the narrative,
source table, conflict register and figure. Another protocol-review round is
not needed. No empirical test, fitted reconstruction, new interval or future
quantitative extension is endorsed by this recommendation.

Reviewed at `e614b238af7c900e678b5382b6c804d0422b15d9`:
[Haley protocol](vortex_haley_deep_dive_protocol_20261014.md), plus the Haley
and cross-cutting corrections in
[recovery-matrix section 8](option3_recovery_matrix_20261013.md). The evidence
standard is the completed [primary-source review](astra_haley_recovery_review_20261014.md)
and [transcription receipt](../analysis/astra/a_power_review/haley_source_excerpt.json).
No new source search, empirical statistic, fitting or simulation was performed.
This memo is the only file edited in this review.

## Essential amendments during production

**1. Correct numerator/denominator notation (protocol lines 52–61).**
The proposed fractions are currently exposures/survivors, whereas the figure
promises survivors/exposures. Values such as `13/8` and `3/0` are not
persistence proportions. Prefer separate columns `exposed n` and `observed
survivors s`, then label plotted proportions explicitly `s/n`:

- Non-pups, transitions beginning 1987–1996: **3/3, 8/13, 9/12, 8/9,
  5/11, 8/10, 4/9, 10/15, 5/10, 4/5**.
- Tagged pups, transitions beginning 1990, 1991, 1993, 1994 and 1996:
  **2/2, 0/3, 6/6, 3/6, 0/7**.
- Count-derived totals are **83 survivors from 123 non-pup exposures** and
  **30 from 55 pup exposures**, rather than apparent-survival fractions
  `123/83` and `55/30`.

Preserve the tagged totals as 97 exposures with 64 survivors and 24 with 11.
Neither a pooled ratio nor an unweighted mean of annual proportions should
replace the other; no pooled estimate is needed for this figure. Each plotted
point should identify the transition `t → t+1` or use an axis explicitly
labelled transition-start year. The Appendix 12 denominator combines
yearlings and older animals; the subsequent survivors are in the age-two-plus
adult class. Pup persistence refers to pups becoming observed yearlings.

**2. Specify missing-versus-zero display rules (protocol lines 84–90).**
These are simple implementation rules, not reasons to delay production:

- Plot genuine zero tagged persistence when `n > 0, s = 0`, including
  `0/3` in 1991 and `0/7` in 1996. A zero tagged risk set has no persistence
  proportion; display a gap, not zero. Do not connect lines across unavailable
  cohorts or manufacture denominators.
- Stage composition outside 1987–1997 is unavailable. Williams-only totals
  do not supply stage values; do not fill missing stages with zeros or
  extrapolate proportions. Show 1987's two source totals distinctly and
  shade only the verified 1988–1997 matching window.
- The 1987 immigrant entry is blank, not zero. Arrival ticks represent years
  with recorded arrivals, not exact event dates. Preserve annual multiplicity
  in the source table or annotations; absence of a tick in an unrecorded year
  does not establish no immigration.
- Keep conflict flags visible beside the affected observations. State that
  uncertainty is not quantified in this descriptive plot; absent intervals
  do not imply exact persistence or perfect detection. Cross-colony CJS or
  telemetry intervals belong in separately labelled context, not as bands
  around Haley's annual points.

The count-derived rows should be labelled as summaries from the same count
programme, with the documented inconsistencies. Calling them re-expressions
of the stage counts must not imply that every row reconciles algebraically.

**3. Preserve unknown transplant origin (matrix lines 250–251).**
Replace “It is not a Haley removal” with **“It is not established as a Haley
removal and is not coded as one; the donor colony remains unknown.”** The
protocol already uses the correct coding language. Unknown origin is not
evidence that Haley was not the donor. The McQuillan and Franklin narratives
must remain separate accounts with unresolved linkage.

## Accepted scope and interpretation

The revised census and age mappings are adequate for the descriptive work:
seasonal age-class maxima, the within-season marked-animal accumulation
caveat, pups/yearlings/age-two-plus adults, and the separate capture-age
terminology. The history-granularity correction is also right: annual
aggregate persistence and partial named-animal records, not a recovered
encounter-history dataset. The identified source conflicts, changing effort,
unresolved endpoint provenance and missing removal ledger are retained.

The proposed narrative can state what the additional observations reveal
about age composition, recorded persistence, reproductive concentration and
movement. It should not convert disappearance to death, classify the final
zero as a documented mortality event, or infer feedback or its absence.
The observation about immigration enabling breeding remains a specific
natural-history account, not an estimated density effect.

Connect the case to the limitations demonstrated by the investigated
count-based procedures. Do not turn their failed calibration or weak power
into a theorem that every count-based method or population is unidentified.
The present case has informative extra evidence and unresolved mechanisms;
both belong in the manuscript.

Section 6 is appropriately labelled **not commissioned**. Its census mapping,
row reconciliation, movement, dependence and prospective validation requirements
are reasonable. For clarity, omit the OLS/AR(1) example or label it explicitly
as an unselected possibility: no statistic or single-series estimator is
chosen by approving the descriptive tranche. Full histories may help without
being a universal prerequisite for every future aggregate model.

Finish when the four source-labelled deliverables are complete and visually
checked. Reuse the existing transcription and preserved conflicts; source
searches, modelling and a further protocol negotiation are not completion
criteria. Return the finished artifacts with a compact record of incorporated
corrections and remaining source limits.

Recorded: 14 October 2026, 14:29 AEDT, Australia/Hobart.
