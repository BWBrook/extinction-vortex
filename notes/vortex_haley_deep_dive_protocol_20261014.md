# Haley Lake deep dive: descriptive protocol (draft for review)

Fable, 14 October 2026 (Australia/Hobart). It follows Astra's Haley source
review (`notes/astra_haley_recovery_review_20261014.md`) and recovery matrix
§4, as corrected below. This is a descriptive case study. **It is not a
feedback test**: no empirical T1–T4, p-value or fitted demographic
reconstruction.

## 1. Aim

Show what a source-grounded demographic record adds to an extinction-bound
count series, and what it still cannot identify. The case is Williams ID 15,
the Vancouver Island marmot at Haley Lake. The case links to the paper's
methodological result (counts alone do not pin down nuisance demography)
without implying that those results validate a Haley-specific null test.

## 2. Sources and identity

**Primary source.** Bryant (1998), PhD dissertation, University of Victoria.
- Retrieved PDF SHA-256 `a263400a…`.
- Printed pages are cited; add 13 for the PDF page.
- Methods pp. 14–19; sampling and survival pp. 34–45; reproduction, movement
  and mortality pp. 47–54; decline pp. 74–76; Appendices 7, 11, 12, 14 and 16.

**Secondary.** Bryant & Page (2005) for the pooled telemetry context, as a
comparator only. The original URL now redirects, so the archived copy must be
cited.

**Identity.** Appendix 7's age-summed annual totals equal Williams ID 15 in
every year 1988–1997.
- 1987 is 18 in Bryant against 28 in Williams. **Unresolved**, shown both
  ways.
- 1981–86 and 1998–2000, including the terminal zero, have **no recovered
  source**. They are shown as Williams-only values.

## 3. Deliverables

**1. Case narrative**, about 1–1.5 manuscript pages.

**2. Source table**, every value carrying its source location:
- the seasonal abundance series, as **age-class seasonal maxima**. Counts were
  mostly before 11:00; pups were counted after emergence in early July.
  Intensively studied colonies include all marked animals seen through the
  season, so this is not a simultaneous census (pp. 14 and 37).
- annual stage composition: pups, yearlings, and adults aged 2 and over
  (Appendix 7). Capture-age terms (subadult = 2, adult = 3 and over) are
  mapped explicitly.
- litters and pups. Appendix 7 gives 59 pups; the narrative on p. 47 gives 58.
  Both are shown.
- observed arrivals: 9 immigrants over the recorded years, plus the 1974
  Haley-to-Bell-Creek movement as evidence that emigration is possible.
- tagged persistence with denominators, given as explicit exposed n and
  survivors s and plotted as s/n (corrected 14 October; the first draft wrote
  n/s):
  - non-pups (Appendix 12), s/n for transitions starting 1987–1996: 3/3,
    8/13, 9/12, 8/9, 5/11, 8/10, 4/9, 10/15, 5/10 and 4/5. Total 64 survivors
    from 97 exposures.
  - tagged pups (Appendix 11), s/n for transitions starting 1990, 1991, 1993,
    1994 and 1996: 2/2, 0/3, 6/6, 3/6 and 0/7. Total 11 from 24.
  - The thesis calls these minimum persistence (p. 18), and they are not
    independent animals.
- count-derived apparent survival (83 survivors from 123 non-pup exposures;
  30 from 55 pup exposures), labelled as summaries from the same count
  programme, not independent evidence, and not algebraically reconciled in
  every row.
- named-animal records (Appendix 16; 15 Haley rows covering 11 named animals)
  and selected lifetime reproduction (Appendix 14, excluding females alive at
  the end of 1997), described as partial records.

**3. Conflict and uncertainty register**, each conflict kept as found and
never repaired by arithmetic:
- 1987: 18 against 28.
- Appendix 11's 7 apparent yearlings from the 1988 pups, against Appendix 7's
  5 yearlings in 1989.
- Appendix 12's 10 tagged adult survivors from 1994, against Appendix 7's 7
  adults in 1995.
- Appendix 11's 7 tagged pups in 1996, against Appendix 7's 2 + 2.
- 59 pups against 58.
- Appendix 16's 43 records, against N = 42 and the fate totals of 41.
- The 1996 transplant: the McQuillan and Franklin accounts differ, and the
  donor colony is unknown, so it is **not coded as a Haley removal**.
- The capture and removal ledger for 1997–2000 is missing.
- Effort changes after 1992.
- The observation probability is not known for each year. One visit detected
  about 44% of tagged adults across colonies; regional correction factors
  were not applied to individual colony-years (p. 15).

**4. One figure:**
- the Williams series, with the Bryant-matched window shaded and 1987 shown
  both ways;
- stage composition below it;
- tagged persistence, drawn as counts over exposures (no intervals) and
  marked as minimum persistence;
- arrivals as event ticks.

## 4. Interpretation rules

- **Separate observed from proposed.** Keep observed disappearance,
  documented mortality (for example Max's handling death) and proposed causes
  (predation, mate limitation, habitat) apart.
- **Immigration and breeding.** The p. 47 observation that immigration
  enabled breeding in 1988 is a natural-history account of mate availability.
  It is not an estimate of abundance-dependent feedback.
- **Decline-period rates.** Measured during the decline, they may reflect
  feedback, external drivers, movement, observation changes or chance. They
  are not a no-feedback baseline.
- **Uncertainty.** No intervals are constructed now. The annual numerators
  and denominators could support binomial intervals under stated
  assumptions, but only after the conflicts are bounded. Pooled CJS (0.623,
  0.565–0.678) or telemetry intervals appear as cross-colony comparators,
  never attached to Haley.
- **No 97 independent trials.** Repeated exposures are not pooled as
  independent Bernoulli trials.

## 5. Stop conditions

Stop when the narrative, source table, conflict register and figure are
complete. Unresolved conflicts and the missing endpoint years remain stated
limits. There is no open-ended source search and no author contact (that is
Barry's decision). No quantitative reconstruction is forced.

## 6. Future quantitative extension (not commissioned)

A formal Haley feedback analysis would first need:
1. A case-specific estimand and statistic. The nine-population
   random-intercept T1–T4 estimator does not identify its between-population
   random effect from one colony. A case-specific statistic must be defined
   and justified; none is selected by this protocol.
2. A mapping from seasonal age-class maxima to the generator's census state,
   including observation error and effort.
3. Reconciled or explicitly bounded annual rows.
4. A model of movement: arrivals, unknown emigration and the transplant
   question.
5. Dependence assumptions linking tagged persistence, stage counts and
   telemetry. They are not independent likelihoods.
6. Its own calibration and prospective validation, with power measured rather
   than assumed.

Complete individual histories would help but are not strictly required.
