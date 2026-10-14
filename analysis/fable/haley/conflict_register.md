# Haley Lake: conflict and uncertainty register

Descriptive deep dive (`notes/vortex_haley_deep_dive_protocol_20261014.md`).

**Source.** Bryant 1998 (PDF SHA-256 `a263400a…`; printed pages). The
transcription in `haley_source.json` is a source recheck reported by Fable
(`pdftotext -layout`, Appendices 7, 11 and 12), made after exposure to Astra's
transcription. Agreement in every value with
`analysis/astra/a_power_review/haley_source_excerpt.json` is verified. The
recheck was not blinded.

**Rules.**
- Every entry is kept as found: none is repaired, reconciled or resolved by
  arithmetic.
- "Unresolved" means the inspected sources do not settle it.
- The figure flags with ‡ the plotted values involved in A2, A3 and A4: the
  1989 yearlings in panel (b), the 1994 non-pup transition and the 1996 pup
  transition in panel (c). A1 is annotated directly in panel (a). A5 and A6
  are not plotted.

## A. Value conflicts between sources or tables

| # | Entry | Conflicting entry | Where it shows | Status |
|---|---|---|---|---|
| A1 | Appendix 7 (p. 110): age-summed total for 1987 = 18 | Williams ID 15: 1987 = 28 | Figure (a); annual table | Unresolved. Both shown. 1988–1997 match exactly. |
| A2 | Appendix 11 (p. 116): 7 apparent survivors from the 1988 pup count | Appendix 7: 5 yearlings in 1989 | Transition table (count-derived; not plotted); the conflicting 1989 yearlings **are plotted** in figure (b) ‡ | Unresolved; reason not established. |
| A3 | Appendix 12 (p. 117): 10 surviving tagged adults from the 1994 tagged risk set of 15 | Appendix 7: 7 total adults in 1995 | Figure (c) ‡; transition table | Unresolved. These entries cannot jointly be read as consistent counts of the same survivors at one census; the reason (transcription, revision or a different inclusion rule) has not been distinguished. |
| A4 | Appendix 11: 7 tagged pups in 1996 (0 observed as tagged yearlings) | Appendix 7: 2 tagged male + 2 tagged female pups in 1996 | Figure (c) ‡; transition and annual tables | Unresolved. |
| A5 | Appendix 7: 59 pups over 1987–1997 | Narrative p. 47: 58 pups | Annual table total | Unresolved. Both reported. |
| A6 | Appendix 16: 43 numbered records | Summary N = 42; fate categories sum to 41 (10 dead, 28 survived, 3 unknown); published 28/38 | Narrative only | Unresolved. 42 is not the verified number of distinct marmots. The 15 Haley rows cover 11 named animals, with repeated records. |
| A7 | 1996 transplant: Mount McQuillan account (pp. 50–51; four overwinter deaths) | Appendix 16: Franklin, one transplanted male killed by predation and three females lost to hibernation or disease | Narrative only | Linkage unresolved. Donor colony unknown. **Not established as a Haley removal and not coded as one**; unknown origin is not evidence that Haley was not the donor. |

## B. Missing or unsourced values (missing is not zero)

| # | Gap | Display rule |
|---|---|---|
| B1 | Williams 1981–1986 and 1998–2000, including the terminal 0 in 2000, have no recovered source | "Williams only" label; no stage values; the final zero is not a documented mortality event |
| B2 | Stage composition outside 1987–1997 | Not shown; no zeros filled and no extrapolated proportions |
| B3 | 1987 immigrants: blank in Appendix 7 | "n/a" in figure (d); blank in the table |
| B4 | Tagged pup risk set zero (1987–89, 1992, 1995) | Gap in figure (c), not 0 persistence. Genuine zeros (0/3 in 1991, 0/7 in 1996) are plotted. |
| B5 | Capture and removal ledger for Haley, especially 1997–2000 | None recovered; no removals coded |
| B6 | Emigration rate | Not estimable from the thesis (p. 19). The 1974 Haley-to-Bell-Creek tagged movement shows emigration is possible. |

## C. Unquantified uncertainty and interpretation limits

- **Census.** Counts are age-class seasonal maxima (p. 14), mostly before
  11:00, with pups counted after emergence in early July. Intensive colonies
  include all marked animals seen through the season (p. 37). So annual totals
  are not a simultaneous census, and summing age-class maxima adds a further
  timing issue.
- **Effort and detection.**
  - More than ten visits a year at intensive colonies, with effort increasing
    after 1992 (p. 34).
  - Across tagged adults, one visit detected about 44%; this is not a
    Haley-specific annual detection probability.
  - Regional correction factors were not applied to individual colony-years
    (p. 15).
- **Tagged persistence** is minimum persistence (p. 18): missed animals, tag
  loss and permanent emigration look like deaths.
  - Reappearances occurred in 7 of 255 adult-years in the study-wide data.
  - The pooled CJS model fixes recapture at 1. That does not establish perfect
    detection for each Haley year.
- **Exposures are not animals.** The 97 non-pup exposures (64 survivors) and
  24 pup exposures (11 survivors) are recorded exposures, not independent
  animals. The printed means (0.69, SD 0.19; 0.50, SD 0.50) summarise the
  annual rates; the SDs describe variation among years, not confidence
  intervals.
- **No intervals.** None are constructed here. Cross-colony CJS (0.623,
  0.565–0.678) or telemetry intervals are context only, never attached to
  Haley.
- **Denominators.** Appendix 12's denominator combines yearlings and adults
  at t; its survivors are adults aged 2+ at t+1. Pup persistence is pups
  becoming observed yearlings.
- **Count-derived rows** (83 survivors from 123 non-pup exposures; 30 from 55
  pup exposures) are summaries from the same count programme. They are not
  independent evidence, and they do not reconcile algebraically in every row
  (A2, A3).
