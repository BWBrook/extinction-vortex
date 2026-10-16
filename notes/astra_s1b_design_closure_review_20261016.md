# Stage 1b/1c design and report closure review

Astra, 16 October 2026. Bounded review of `e11b9b0`, covering the corrected
Stage 1a report, `p2_report.py`, `p2_inventory.py`, the saved inventory,
Stage 1b design and Stage 1c revision 2. Barry's authorization in board 1759
is settled. This review does not reopen the authorized scale, caps or gate
meaning. The separate execution reviews own enforcement, source binding,
scheduler recovery and the cross-machine smoke.

**Disposition:** the earlier scientific design contracts and major reporting
repairs are closed. The cap table still needs a finite qualification: its
zero is a count of plug-in cost exceedances, not an estimate supported by
resolved retention rates for every pilot setting. This does not change the
authorized design or require another scientific decision. No sampling,
population simulation, fitting or remote execution occurred in this review.

## P2 — Keep unresolved settings visible in the cap projection

`p2_inventory.py:26–34` substitutes a lower expected-cost limit for each
zero-hit setting. Lines 44–52 then classify a setting as a failure only when
this substituted value exceeds the cap. Accordingly, the Stage 1b design
§4 table reports **zero expected failures at 2,000 h** and none for these
four settings at 1,000 h. The arithmetic is reproduced, but that label
overstates what the inputs establish.

The four zero-hit settings have these lower limits, in worker CPU-hours at
observed throughput:

| Setting | Population and outer | Lower limit |
|---|---|---:|
| 242 | ms_woodpecker, null_prior_predictive/0 | 608.115 |
| 512 | golden_plover, null_low_s/0 | 586.021 |
| 536 | golden_plover, null_low_s/8 | 587.686 |
| 833 | hawaiian_crow, MA_d10_0.5/7 | 559.465 |

Being below 2,000 h at a **lower limit** does not establish completion within
the cap. All four remain unresolved even before extrapolating to unseen
outers. Under this table's factor-of-20 extrapolation, their uncertain
contribution corresponds to 80 settings and 80 n=300 datasets; it must not
silently become 80 forecast successes. Positive-hit plug-in costs also omit
retention-rate uncertainty, especially the three one-hit estimates.

Relabel the count as **settings whose substituted plug-in cost exceeds the
cap**, show the four unresolved pilot settings separately, and say that
actual failure counts remain unknown. Likewise, `sum(min(point_cost, cap))`
is a planning scenario; it is not generally the expected truncated cost
`E[min(time_to_K, cap)]`. The existing caveats about point projections and
unseen outers are useful but do not describe this treatment of already
observed zero-hit settings. The finite spending and scoring contracts remain
the relevant safeguards; their executable enforcement is reviewed separately.

## P3 — Correct stale counts and authorization wording

- Stage 1b §1 says **1,800** population-outer pairs beyond the pilot. The
  correct increment is **6,840** = 9 populations × 4 scenarios × 190 new
  trials; the full count is 7,200 and the pilot count is 360. Section 7's
  full export count is correct. This is a prose defect, not evidence that
  the export omitted trials.
- Stage 1b's opening still says nothing is implemented or dispatched and
  Barry is merely inclined to authorize. Its later §§7–8 record the build
  and authorization. Stage 1c's title/opening and §7.2 still call it
  uncommissioned and require authorization; Stage 1a's final lines do the
  same. Update these as historical-to-current status corrections. The
  executable Stage 1c settings and adapter check remain unfinished work;
  Barry's authorization is not unfinished.
- The paired-outer bootstrap in `p2_report.py:124–129` omits the no-exposure
  setting 576 from its outer sum, whereas the point inventory uses its
  cell mean. This lowers the resampling population's expected total by
  **67.406 CPU-h**, about 0.0078% of the total. It is immaterial to the
  resource decision. For consistency, impute the same cell mean in that
  sensitivity calculation, or disclose the tiny difference. Its wider
  interpretation as a conditional empirical spread is now correct.

## Closed repairs and verified arithmetic

The corrected Stage 1a report, JSON inventory and Markdown tables reproduce
identically from the saved collection. Independent calculations agree with:

| Component | Count or projected worker CPU-h |
|---|---:|
| Primary libraries | 21,600 |
| Primary retained pairs | 43,200,000 |
| Primary sampling, gross | 861,697.823 |
| Pilot worker credit | 733.873 |
| Primary sampling, additional | 860,963.950 |
| Independent check libraries | 216 |
| Independent check sampling | 11,822.774 |
| Primary plus check W1 sampling | 140,531.953 |
| Primary plus check W2 sampling | 732,988.645 |
| Primary plus check fitted analyses | 2,424 |
| Fitting at 0.5 h per analysis | 1,212 |
| Gross sampling plus fitting | 874,732.598 |

The design's rounded 874,700 total is correct. Its separate primary-wave
subtotals exclude the independently listed library check; adding that check
gives the wave totals above. This is not an omitted total cost. The stated
315.339 bytes per retained record gives 13.623 GB of primary libraries;
surplus, duplicated journals, checkpoints and other storage remain additional.

The following earlier concerns are substantively resolved:

- Expected-cost intervals are distinguished from predictive run-time
  intervals. Zero-hit lower limits now use the exact suffix retention bound.
  Resolved/unresolved denominators appear in both summary tables; gross and
  additional cost are distinguished; the bootstrap's limited meaning and
  the approximately 8.6-fold increase over 100,000 h are explicit.
- The actual hit-stopped setting is **772**, crow null_low_s/7 at n=30.
  Setting 775 has 1,722 hits and stopped at its budget. The corrected report
  and design now name the right setting.
- The design binds stable pilot IDs, first-K global stream order, verified
  complete prefixes and a disjoint second-library namespace. Implementation
  compliance remains the separate execution review's responsibility.
- Stage 1c consumes the fixed-ball libraries without new neighbourhood
  selection. It preserves the shared matched n=0 baseline, independent
  training/testing index draws conditional on each library, and the finite
  library limitation.
- Null non-acceptance and alternative detection follow contract v3 with all
  200 declared IDs retained. Missing work and cap failures remain in binary
  denominators; fitted comparisons show complete-pair denominators and
  joint availability.
- The gate family and interpretation are explicit and authorized. Exact
  calculation gives the stated **at most 7/200** null non-accepts and
  **at least 152/200** beta-min detections. The boundary upper bounds are
  0.076451 at 7 and 0.083161 at 8; lower bounds are 0.699812 at 151 and
  0.705100 at 152. The probability tables also reproduce. These are stringent
  development adequacy criteria, with estimation primary, not prospective
  validation or an automatic trigger to enlarge the design.

## Independent-library subset: accepted, with its stated narrow meaning

The lower-median and largest-resolved selection rule reproduces all eight
named outers and their prices. All eight selected n=300 nine-population
costs are resolved plug-in estimates. Selection used sampling diagnostics
before fitted outcomes, is fixed by name, includes all populations and all
three n levels, and counts subsequent failures. The 216 extra libraries and
24 repeat analyses correctly price this check.

The phrase **largest resolved** matters. For prior-predictive n=300, the
chosen difficult outer is trial 4 with a nine-population cost of 401.560 h.
The omitted unresolved trial 0 has a plug-in lower-limit sum of 789.149 h;
its one zero-hit population alone has a 608.115 h lower limit, exceeding the
entire selected outer. Thus this is not a check covering every sampling
tail, and sampling cost is not itself a bound on fitted sensitivity. The
draft already restricts its claim to numerical sensitivity on the named
cases. Preserve that restriction; there is no reason here to replace the
authorized cases or enlarge the diagnostic.

The [arithmetic receipt](../analysis/astra/s1b_design_closure_review/checks.json)
and [script](../analysis/astra/s1b_design_closure_review/checks.py) retain input
hashes, independent counts/costs/gates, the subset rankings and report-only
replay checks. Only this note and the owned arithmetic directory were written.

16 October 2026, 22:31:31 AEDT (Australia/Hobart).
