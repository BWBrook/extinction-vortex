# A-screen audit and Option 3 feasibility review

13 October 2026. Reviewed Fable's `1fe79ea`, Correspondence 1571/1585,
the completed synthetic A-screen, and the two first-pass evidence scans.
Three bounded delegates checked execution contracts, the nine original series,
and additional case studies; Astra independently rescored the raw statistics
and integrated the scientific conclusions. No empirical test was run.

## Recommendation

Accept the completed A-screen as development evidence. Accept the proposed
fixed 600-case A power screen as a practical comparison, after the narrow
receipt repairs below. It will not identify the cause of the calibration
change or validate A. Continue Option 3 through focused public-data recovery:
there is substantially more usable evidence than the first-pass scans found,
but a defensible demographic reference model has not yet been established.

Barry's Option 3 direction is relayed in Claude's 13 October chat quotation,
board 1571 and STATUS. This review preserves its condition that suitable data
exist; it does not treat a board proposal as a new scientific authorization.

## Completed A-screen: independently reproduced

[Raw audit and receipt](../analysis/astra/a_screen_review/) read all 200 A and
200 stored-v1 synthetic T files on deep-server. They use separate covariance,
linear-solve and rank calculations, without importing the production scorer.

| Quantity | Stored v1 | Candidate A |
|---|---:|---:|
| Non-accepts / 200 | 21 | 11 |
| Two-sided exact 95% interval | 0.0662–0.1560 | 0.0278–0.0963 |
| Mean z, T1 | −1.697 | −1.405 |
| Mean z, T2 | −1.522 | −1.294 |
| Mean z, T3 | 0.330 | 0.410 |
| Mean z, T4 | 0.389 | 0.657 |
| Median maximum original-C distance | 0.2837 | 1.2926 |
| Mean estimator fallbacks per trial | 161.415 | 177.195 |

The paired table is **6 both, 15 v1-only, 5 A-only, 174 neither**. A minus
v1 is −0.050; Newcombe method-10 interval [−0.0984, −0.0051]; exact McNemar
p = 0.0413895. Every outcome, p bound, observed distance and reported mean-z
summary reproduces. No sampling or fit failures, indeterminate outcomes, or
covariance-shrinkage branches occurred.

Provenance checks establish:

- All 1,800 population trajectories match both saved outers and the original
  b3 rows. Cases are exactly IDs 0–199; reference settings match the plan.
- All 200 baseline T hashes match the earlier sealed-v1 archive audit. All
  202 A T/neighbour hashes and eight compact files match the committed archive.
- All 181 primary-bank payload hashes match the frozen manifest; all twelve
  frozen source/input hashes and four retained runner/helper hashes reconcile.
- The 1,800 neighbour-ID sets contain 2,000 unique IDs each; logged K-th
  distances match receipts, with 187 boundary ties. Membership and original-C
  distances were not independently rebuilt from the full bank.
- Refitting the same observed series produces tiny floating-point differences
  in T, maximum 1.20e−10. Substituting each stored v1 observed T vector into
  A's score leaves all 200 A p-values exactly unchanged. The audit first
  detected these differences with an exact-equality check, then quantified
  them and tested their consequence; it does not claim bitwise-identical fits.

The read-only remote audit took 40.23 seconds on one CPU, including streaming
bank hashes. There were no new simulations, reference draws or model fits.
Hash agreement describes the inspected payloads; it does not prove that no
intervening mutation or restart ever occurred. Commit `6316a90` predates the
first bank-ready log and fits, but follows the wrapper's launch.

The 5.5% point estimate is encouraging at this particular corner. Its interval,
one-corner scope and exposed development status do not establish prospective
calibration. The roughly 17% reduction in T1/T2 standardized shifts and
4.56-fold ratio of median original-C radii are descriptive observations.

## Findings affecting the next A step

**MAJOR interpretation: power does not identify the mechanism.** Plan §8 and
the result note say power arms could settle the diffuse-reference explanation.
Changing C to C+ changes neighbourhood geometry, nuisance composition,
reference location/covariance and potentially the signal retained after
conditioning. Original-C radius is not T-space dispersion. A loss of power
would quantify a practical cost without isolating which change caused it.
Moreover, b3 is a fixed low-survival null corner, whereas b5/b16 use the
alternative's prior-predictive nuisance law. Comparing their rate reductions
does not produce a matched-nuisance size/power trade-off or a common ROC curve.
Withdraw “falls roughly in step” as a mechanistic decision rule.

**MAJOR before reuse: verify bindings against the specification.** The
[contract fixtures](../analysis/astra/a_screen_review/contract_checks.json)
reproduce reports marked all-checks-true with consistently wrong runner hashes,
wrong K/R/seeds/features, or a changed row-level observed series. Bank payload
hashes are not checked by this runner/report. Current receipts independently
pass those checks, so these are latent defects, not reasons to discard this
run. Before the power screen, bind/check the actual bank and helper hashes,
the expected per-block settings, and selected records against the frozen outer
file. Check raw T presence before skipping completed rows on resume; currently
a missing file is discovered only when reporting. Seven intended refusal
paths already work. This calls for a narrow repair, not a new execution system.

**Accepted bounded assignment, owner Fable:** unchanged A on exposed v1 b5
and b16, first 300 IDs in each, paired with the stored 21/300 and 206/300
baseline detections. Bind inputs and the proposed separate seed mapping before
fits; retain K = R_train = R_test = 2,000 and frozen fitting/failure rules.
Report counts, exact intervals, paired tables/differences, failures, z and
support diagnostics, with a hard stop after 600 and no automatic extension or
retuning. About five hours is a planning estimate from the completed screen.
Use the result to judge whether A merits further development; it cannot select
A, rescue v1's failed validation, establish a power bound at other effects, or
assign an empirical O2/O3 outcome. Astra reviews the completed receipts.

## Evidence and design implications for Option 3

The source audits linked below supersede the first-pass scans for verified
claims; inaccessible originals remain unresolved. Published point estimates,
processed model inputs and raw individual histories are distinct evidence
levels. None has yet been converted into an empirical prior here.

Three distinctions matter before making eligibility decisions:

1. **Closure, changing conditions and observation are different problems.**
   Known releases/removals and migration can change population membership.
   Handling, vaccination and predator removal can affect rates without making
   a population open. Their occurrence does not prove their causal effect.
   A zero site count can reflect mortality, dispersal, detection failure or a
   management removal; the endpoint must retain that meaning.
2. **Shared monitoring is not automatically circular estimation.** Individual
   encounter histories or known-fate records add demographic information even
   when collected alongside the census. Dependence through shared individuals,
   effort or detection still needs treatment. Rates inferred from the same
   aggregate decline cannot be used as independent priors for that decline.
3. **Demographic rates need a census-compatible observation model.** Adult
   female survival, apparent survival, calf:cow ratios and fledglings per
   successful nest do not directly equal the current scalar survival and
   Poisson-recruitment parameters. Align sex/age, season, breeding fraction,
   juvenile survival, movement and uncertainty before choosing a mapping.

An additional scientific risk remains: rates estimated during an actual
feedback-driven decline may already contain the feedback signal. Treating
those estimates as the fixed no-feedback baseline could absorb part of the
effect under test. This is a design issue to resolve after recovering the data,
not a reason to reject those data now. External survival and recruitment also
leave environmental persistence, variance and catastrophes uncertain; the
six-coordinate oracle does not validate noisy or transported priors.

Do not automatically exclude every managed population or cut every series at
its first augmentation. First construct the dated count/rate/intervention
record. Compare eligibility, explicitly modeled inputs and defensible time
windows against the ecological target and available information. Shortening
a sequence can also remove its extinction endpoint. A material mismatch must
change the design or interpretation; merely mentioning it as a limitation
does not make the closed-population generator adequate.

## Verified source advances and remaining gaps

The [nine-series source audit](astra_option3_nine_source_audit_20261013.md)
contains a population-by-population ledger with source access levels. The
[additional-case audit](astra_option3_phase2_source_audit_20261013.md) includes
pinned repository versions, file hashes, observation counts and year joins.

| Lead | What improved | What still prevents direct use |
|---|---|---|
| Haley Lake marmots | Bryant's thesis matches ten consecutive Williams totals, 1988–1997. Original marked-animal and later telemetry survival estimates have uncertainty. | 1987 is 18 in the age-summed thesis table versus 28 in Williams; other years and removals need provenance. Rates pool colonies and ages. Immigration is documented. |
| Rocky Mountain cranes | The existing 8 October audit already matched all 18 official winter totals. Managed additions are documented within the sequence. | Original F&H window, individual survival and treatment of additions remain unresolved. |
| Hawaiian crow | NRC's earlier five-bird histories explain 0.81 = 22/27 annual transitions and a separate 0.90 time-weighted summary. | These are small, shared-data summaries without a transferable reported interval. The later 0.798 remains count-derived; census inclusion of released birds needs resolution. |
| Maligne caribou | Public prepared inputs contain 24 count rows, including zero from 2018, six survival-summary years and fourteen recruitment rows. | Survival ends in 2007; movement remains possible; raw individual collar histories were not found in the inspected Git release. Williams ID27 does not exactly match. |
| Purcells Central caribou | Thirteen count rows include zero from 2006, with three survival years and five recruitment rows. | Very short survival coverage; original calendar definitions, uncertainty and intervention records need checking. |
| Banff caribou | All sixteen Williams ID28 year/count pairs exactly match the named archive input. | No survival/recruitment rows in these prepared tables; its terminal 2008 label needs reconciliation with the reported 2009 avalanche. |
| Litchfield Adélie penguins | Public counts, chick observations and band sightings can be joined by season/colony. First summed zero is PAL0708. | Two Williams counts disagree; sightings lack a verified complete release/effort history. A breeding-site zero does not establish demographic extinction. |

The caribou package is linked by [Lamb et al. 2024](https://doi.org/10.1002/eap.2965)
and its [public archive](https://doi.org/10.5281/zenodo.10437005). Its prepared
survival estimates are useful evidence, but its fitted IPM trajectories are
not independent priors for the same counts. The article's functional-extirpation
threshold is also different from a zero count. The audit documents the actual
public files rather than assuming the article's data-availability statement
guarantees complete individual histories.

Wittmer, Sinclair and McLellan (2005) is relevant prior art: the
[original paper](https://wildlifescience.ca/wp-content/uploads/2022/11/wittmer-oecologia.pdf)
compares among-population growth and size/density with demographic evidence.
It is not a within-series acceleration test across fifteen complete extinction
trajectories. Final abundance enters both its growth measure and a size
covariate, so that association alone is not independent demographic
corroboration. Distinct pregnancy and mortality observations remain informative.

The first scan's claim of at least five demonstrated closure violations should
therefore be withdrawn. Some membership changes are documented; others are
management exposures, unresolved inclusion rules or unproved causal accounts.
Similarly, evidence of habitat deterioration does not establish that feedback
or demographic stochasticity played no role. The source audit preserves these
contrary interpretations explicitly.

## Finite evidence-recovery handoff

Fable's proposed search/audit split is accepted. The independent audit and
extension are now complete. **Proposed next recovery owner: Fable; reviewer:
Astra.** While the fixed power screen runs, prepare one concise evidence matrix
for Maligne/Purcells Central, the Banff crosswalk, and Haley Lake. Prioritize
original census dates/units, demographic denominators and uncertainty,
count-derived versus individual evidence, and dated movements/removals.
Inspect whether a public deposit supplies the caribou individual histories
omitted from the linked Git release. Keep conflicting source values separate.

Palmer is a second, explicitly open-population lead: recover band cohort and
effort metadata and resolve the count differences before choosing a model.
Historical antbirds and the remaining unreviewed candidates stay queued.
Do not expand this into a full PRISMA search, import IPM posteriors as priors,
contact authors or fit an empirical model in this tranche.

Stop with a concrete feasibility statement: which source-specific data can
support a census-compatible demographic baseline, which require transfer or
dependence modeling, and which remain inaccessible. That gives Barry a
reviewable scientific choice if a target/population or model change is needed.
The evidence now supports continuing recovery; it does not yet establish that
Option 3 will yield a calibrated and discriminating extinction-vortex test.
