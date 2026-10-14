# Haley Lake recovery review and bounded deep-dive scope

**Recommendation: proceed with a descriptive Haley Lake deep dive, with the
source corrections below. The recovered material is not yet a reconciled input
for a quantitative feedback test.** This is a scientifically useful case because
the source adds age structure, marked-animal persistence, reproduction and
movement to a trajectory that strongly matches Williams ID 15. It also shows
exactly why a declining aggregate series does not identify its demographic
mechanism by itself.

Review scope: the Haley headline, sections 4.1–4.5 and summary row in
[Fable's recovery matrix](option3_recovery_matrix_20261013.md), at repository
commit `20c8574`; read against Barry's narrower-paper direction recorded in
`STATUS.md`. No empirical fitting, test-statistic calculation, simulation,
eligibility change or peer-file edit was performed. The independent-reviewer
workflow was used. This memo and the small
[source transcription](../analysis/astra/a_power_review/haley_source_excerpt.json)
are the only outputs owned by this review.

## Primary-source basis

I downloaded [Bryant's 1998 PhD thesis from UVic](https://dspace.library.uvic.ca/bitstreams/6ef9deb0-12fa-4d2a-a3eb-628159c696fd/download)
again on 14 October. SHA-256 is
`a263400aae0287fad07b61e4d94d165332a4ae90aac7a9c1930a86ffc7358d79`,
matching the matrix and prior audit. Page references below are printed pages;
add 13 for one-based PDF pages. I inspected methods pp. 14–19, sampling and
survival discussion pp. 34–45, reproduction/movement/mortality pp. 47–54,
decline interpretation pp. 74–76, and Appendices 7, 11, 12, 14–16. Numeric
rows in Appendices 7, 11, 12, 14 and 16 were checked against rendered pages.
The 2005 telemetry paper was not independently re-audited in this tranche;
its broader pooled estimate is not required to establish Haley's descriptive
case. Source values below retain inconsistencies rather than repairing them.

## Findings that change the feasibility assessment

### MAJOR — the annual count convention is documented, but is not a fixed-time census

The matrix leaves maximum/last/mean unresolved. Methods p. 14 explicitly
chooses the highest annual count separately for each age class. Counts were
usually made before 1100; pup counts followed emergence around early July.
More importantly, p. 37 explains that intensively studied colonies include all
marked animals observed through the season. Mortality, immigration and
emigration mean those animals need not all have been present simultaneously.
The annual total therefore cannot simply be treated as a single synchronous
post-breeding state. Summing age-class maxima adds another timing issue.

Effort increased after 1992, and the five intensive colonies typically received
more than ten visits annually (p. 34). Across sampled tagged adults, one visit
detected about 44%; repeated visits substantially increased coverage. This is
not a Haley-specific annual detection estimate. Regional correction factors
were applied to habitat totals, expressly not to individual colony-years
(p. 15). The thesis supports good intensive coverage, not a known observation
probability for every Haley year.

Age labels also need explicit mapping. Appendix 7's total adults includes ages
two and older, separately from yearlings and pups. Capture-age terminology
calls two-year-olds subadults and ages three-plus adults (pp. 16–17).
Appendix 12's survival denominator combines adults and yearlings. These are
different aggregations. Older first captures have presumed rather than exact
ages; known-age animals were first caught as pups or yearlings.

**Consequence:** use a source-labelled seasonal abundance series in the deep
dive. Any later state-space or stage-structured model needs a defensible
observation-time mapping; it cannot inherit a fixed census date from the year
label alone.

### MAJOR — individual-based information has been recovered, not complete individual histories

Appendix 12 gives annual tagged risk sets and surviving-animal counts. The
matrix's adult/yearling transcription is correct:

| Transition starts | 1987 | 1988 | 1989 | 1990 | 1991 | 1992 | 1993 | 1994 | 1995 | 1996 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Tagged at risk | 3 | 13 | 12 | 9 | 11 | 10 | 9 | 15 | 10 | 5 |
| Tagged survivors | 3 | 8 | 9 | 8 | 5 | 8 | 4 | 10 | 5 | 4 |

These sum to 97 recorded exposures and 64 survivors. They are not 97 distinct
individuals. The printed mean 0.69 and SD 0.19 summarize ten annual rates;
64/97 is a differently weighted descriptive quantity. The intervals are
1987→1988 through 1996→1997, not ten estimates ending in 1996.

Appendix 11 supplies previously omitted tagged-pup denominators:

| Transition starts | 1990 | 1991 | 1993 | 1994 | 1996 |
|---|---:|---:|---:|---:|---:|
| Tagged pups | 2 | 3 | 6 | 6 | 7 |
| Subsequently observed tagged yearlings | 2 | 0 | 6 | 3 | 0 |

These total 24 recorded exposures and 11 survivors; the published unweighted
annual mean and SD are both 0.50. The all-pup count-derived table has 55 pups
and 30 apparent survivors across seven nonzero cohorts.

These tables preserve additional information about marked animals, but omit
identities, capture/re-observation occasions, exposure timing and censoring.
Appendix 14 supplies first capture and selected lifetime reproductive totals;
it explicitly excludes females still alive at the end of 1997. It is not an
annual breeding-history file. Appendix 16 supplies implant dates, names and
coarse outcomes, not a complete encounter or known-fate exposure file. Its
15 Haley rows cover 11 named animals, including repeated records for Arnold,
Meanie and Tweedledum and the research death Max. They are not 15 independent
animals or uniform full-year observations.

**Consequence:** replace matrix section 4.4's description of recovered
ear-tag/telemetry histories with annual aggregate survival summaries and
partial named-animal summaries. Full histories remain unrecovered.

### MAJOR — the source tables are not a mutually consistent demographic ledger

The matching abundance window remains valuable: Appendix 7's summed stages
equal Williams ID 15 in every year 1988–1997. The 1987 sum is 18 against 28
in Williams and must remain unresolved. The later table match does not resolve
the terminal zero in 2000 or the provenance of every earlier count.

Additional source conflicts were confirmed visually:

| Source entry | Conflicting entry |
|---|---|
| Appendix 11: seven apparent yearling survivors from the 1988 pup cohort | Appendix 7: five total yearlings in 1989 |
| Appendix 12: ten tagged adult survivors from the 1994 risk set | Appendix 7: seven total adults in 1995 |
| Appendix 11: seven tagged pups in 1996 | Appendix 7: two male plus two female tagged pups in 1996 |
| Appendix 7: 59 pups over 1987–1997 | Narrative p. 47: 58 pups over that period |

These may reflect different inclusion rules, revisions or errors; this review
does not identify which. In particular, the second conflict prevents a simple
interpretation of all rows as counts of the same survivors at the same census.
Keep the source tables separately labelled. Do not use arithmetic to silently
choose a preferred value or reconstruct unobserved histories.

Appendix 16 also has 43 numbered records, a summary N of 42, and fate-category
totals of 10 dead, 28 survived and three unknown (41). Its published 28/38
calculation can be reported as such but has not been reconciled to the listed
records. Do not call 42 the verified number of distinct marmots.

**Consequence:** these are stops for a unified fitted demographic ledger,
not stops for an evidence-led descriptive case. A table of provenance and
disagreement is an informative result.

### MAJOR — missing confidence intervals do not require borrowing a pooled interval

The annual numerators and denominators contain sampling information. Under
explicit assumptions, binomial likelihoods or intervals can be constructed
for recorded persistence without transplanting a cross-colony CI. No such
interval was calculated here. Their validity would depend on the meaning of
each denominator, detection, handling of movers and reappearances, and the
dependence induced by repeated animals, family losses and shared years.
The source conflicts above must first be adjudicated or bounded.

The thesis describes tagged survival as minimum persistence because missed
animals, tag loss and permanent emigration can look like deaths (p. 18).
Reappearances occurred in seven of 255 adult-years; the selected pooled CJS
model fixes recapture at one (pp. 43–44). That does not establish perfect
detection for each Haley year. The printed SDs describe variation among
annual rates, not confidence intervals for a mean or process-variance estimates.

The matrix's claim that transfer is needed for CIs is therefore too strong.
Pooled CJS or telemetry estimates could be explicit comparators or inform a
future transfer model, but their intervals cannot be attached to Haley's point
estimate as if estimated locally. The adult/non-pup CJS estimate and the
broader telemetry sample also require separate age and observation mappings.
Table 3's note does provide a relevant study-wide basis of 96 tagged
individuals and 255 adult-years at intensive colonies, plus additional records;
it should not automatically be relabelled the exact Table 2 fitting sample.

### MAJOR — dependence and decline-period sampling need calibrated interpretation

Shared monitoring is not itself circularity. Marked-animal persistence and
stage composition contain information absent from the age-summed Williams
series. However, the count-derived adult ratio is largely a re-expression of
the stage counts, and tagged outcomes overlap those counts and the telemetry
sample. Multiplying all summaries as independent likelihoods would overcount
evidence. A future joint model could represent that overlap; the present
summaries do not yet make such a model ready to run.

Similarly, measuring rates during decline does not demonstrate that abundance
feedback is embedded in them. Those rates may reflect feedback, external
drivers, movement, observation changes, chance or combinations of these.
They are not an external estimate of a counterfactual no-feedback baseline.
This distinction strengthens the deep dive: additional demographic evidence
can constrain explanations without identifying the causal effect of abundance.

## Movement, intervention and reproduction interpretation

The nine tabulated immigrants across ten recorded years establish openness;
the 1974 tagged Haley-to-Bell-Creek movement independently establishes the
possibility of emigration. Nine arrivals over a decade should not be compared
directly with mean annual adult abundance 8.6 as though they had the same
denominator. The thesis cannot estimate emigration rates (p. 19), so the
arrivals are not net movement. Apparent adult survival from consecutive counts
includes net movement; the matrix's wording could otherwise suggest movement
has been removed statistically.

The p. 47 observation that immigration enabled breeding at Haley in 1988
supports a concrete natural-history account of mate availability and rescue.
It does not estimate an abundance-dependent population feedback. Appendix 14
shows concentration of reproduction among a few females, with the survival
selection noted above. Annual litter totals add useful context but are not
automatically fecundity per breeding female or fertility per adult.

The 1996 transplants should not be assigned to Haley. Their source colony is
not identified in the inspected account. Moreover, pp. 50–51 describe four
overwinter deaths at Mount McQuillan, whereas Appendix 16 names Franklin and
lists one transplanted male dying from predation and three females from
hibernation/disease. The link between these records is unresolved; the
matrix's merged Mount McQuillan/Franklin wording should not imply a reconciled
four-animal event. Regional predator removals alter context but are not
movement of Haley marmots.

Max's fatal handling event is documented. Absence of a Haley capture/removal
ledger remains a gap, especially near the end of the Williams series. The
matrix's parenthesis that the 1998 thesis predates captive breeding beginning
in 1997 should be removed: the thesis itself already discusses a female in
Toronto Zoo (p. 48). Neither that statement nor later releases identifies
Haley removals during 1997–2000.

## A useful first deep dive and its stop conditions

The material supports a finite **source-based demographic case study now**:

1. Present the Williams trajectory with the 1988–1997 source match, the
   unreconciled 1987 alternative, and explicit unsourced endpoint years.
   Describe the seasonal count convention and changes in effort.
2. Present annual age composition, litters and observed arrivals for the
   thesis window, alongside the tagged-persistence summaries with their
   denominators. Keep source conflicts visible and distinct from missing
   years. Do not turn these into a fitted population reconstruction.
3. Explain what those observations add: variable juvenile recruitment,
   persistence of marked non-pups, concentrated reproduction, and movement.
   Separate observed disappearance, documented mortality and proposed causes.
4. Show why neither the aggregate decline nor these partial demographic
   summaries alone isolate abundance feedback. Connect that case-level limit
   to the paper's existing methodological results without implying those
   results validated a Haley-specific null test.

This is enough to draft the evidence narrative and its source table. A new
formal feedback test is not required for the case study to be useful.

For a later quantitative extension, the scientific team would first need to
specify the estimand and census timing, reconcile or explicitly bound the
conflicting annual rows, map marked-animal exposures and movement, and state
the observation/dependence assumptions. Complete histories would help, but
their absence is not a universal proof that every defensible aggregate model
is impossible. The standard is a justified model for the recovered evidence,
not merely the existence of a CI. Do not broaden into full-series rate
transfer or source contacts as an automatic consequence of this review.

Stop the descriptive tranche once the source-labelled case narrative, table
and uncertainty register are complete. If the conflicts or ending mechanism
remain unresolved, retain them as limits; do not keep searching indefinitely
or present a forced quantitative reconstruction. The strongest present claim
is that Haley supplies a rich but imperfect demographic explanation of what
an extinction-bound count series can and cannot reveal.

Verification: re-download and SHA-256 comparison; `pdftotext -layout`;
rendered-page inspection; direct source-row transcription; assertions on the
Williams match and reported sums. No fitted rates, empirical test statistics
or new model-based uncertainty estimates were produced.

Check receipt: all ten 1988–1997 Williams matches passed; the 1987 difference
was asserted rather than repaired; adult tagged 97/64, apparent adult 123/83,
tagged juvenile 24/11, apparent juvenile 55/30, pups 59, litters 17 and
immigrants nine matched the transcribed rows. The three cross-table conflicts
involving 1988, 1994 and 1996 were separately asserted as preserved.

Recorded: 14 October 2026, 11:36 AEDT, Australia/Hobart.
