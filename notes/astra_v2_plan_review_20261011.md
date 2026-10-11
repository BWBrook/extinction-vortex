# Astra review of D1c/D2, paired D3 and the two v2 candidates

11 October 2026, Hobart. Review of Fable's `29c45c9` response and
[development plan](vortex_v2_dev_plan_20261011.md), prompted by Barry's
"Claude has responded." in Codex chat. Fable owns implementation/execution;
Astra owns this critique. Two bounded reviewers examined the candidate
mathematics and D3 contract. Their agreement is not independent validation.

**Recommendation:** finish the paired D3 diagnostic and retain Candidate A
for bounded development, with the specifications below. Candidate B is now
mathematically coherent for a fixed finite grid, but its target needs precise
qualification and its cheap power screen is discouraging. Review that screen
before spending 8,000 new calibration analyses. No method is selected here.
V1 remains failed; no empirical conditional-null statistic was inspected.

## 1. D1c/D2: substantial repairs, two remaining defects

The retained source checks every manifest bank/source hash and records runtime,
neighbour digests and ties. Locally, all **4,000** trial IDs, outcomes and p_hi
values reconcile with Astra's independent v1 audit. All **36,000** reported
population distances match the reported v1 rounded distances; each trial's
maximum also matches the independently audited log maximum. These are useful
checks, not proof of exact historical membership. Astra has not reloaded the
primary bank or the full neighbour-ID archive in this review.

1. **Use a K query for membership.** D1c queries K+1 and truncates; v1 queried
   K. At a boundary tie, these can select different members even in the same
   runtime. On deep-server's Python 3.12.3 / NumPy 1.26.4 / SciPy 1.11.4, an
   eight-identical-point fixture returned `[1,2,0]` for K=3, versus `[1,2,3]`
   for K=4 truncated to three. There are 571, 806, 896 and 914 flagged
   population-neighbourhood ties in b1–b4. Query K separately for membership
   and K+1 solely for the flag; refresh the ranks and D2 together. Distances
   cannot detect membership swaps. The fixture demonstrates the possibility;
   the number and effect of actual changed memberships remain unmeasured.
2. **Retain constant-library midranks.** For `[5,5,5,5]`, observations 4, 5
   and 6 have ranks 0, 0.5 and 1. D1c replaces these valid ranks with NaN;
   `nanmean` then changes the number of populations in D2's summary (for
   example, 370 low-s crow libraries are constant). Flag the constant
   library, retain its rank and use all nine populations. Only a standardised
   residual with zero reference SD is undefined. My prior wording "emit null
   for constant libraries" was too broad and contributed to this ambiguity;
   I explicitly correct it here and in Correspondence 1545.

The integer endpoint calculation resolves the earlier cancellation problem.
The revised nominal and stationary-mean growth labels are appropriate. D2 is
an association diagnostic; after the two repairs it can describe displacement
and rejection together, but cannot identify a survival-specific cause. Preserve
the current outputs as a superseded development version rather than overwrite
their provenance without a record.

## 2. D3: preserve the paired experiment, repair its reporting contract

The source implements the key design: the same 200 saved outers in both arms,
all six nuisance coordinates fixed for the oracle, common original-C mask/MAD,
fixed K/R and a bounded bank extension. All 761 permitted seed values are
distinct. Nonaccept counting and the exact conditional McNemar calculation
match the specification. No live partial rejection outcomes were read or jobs
touched. The metadata-only inspection at 19:54 AEDT found outer generation
still underway, without completed oracle metadata.

Before accepting its report, address these bounded defects in
`analysis/fable/calibration/v2_dev/d3_oracle.py` and `run_d3.sh`:

| Finding | Required repair |
|---|---|
| `newcombe10` uses uncorrected phi, i.e. method 8 | Implement the declared method 10 correction. For `(a,b,c,d)=(100,0,0,100)`, current output is `[0,0]`; method 10 gives `[-0.0097,0.0097]`. This is postprocessing; preserve fits. |
| Bank support failure returns success | Stop before either arm fits if any population remains below 20,000; propagate either arm's failed exit before scoring. |
| Scoring opens T files for sampling failures | Keep these trials in the fixed denominator as unresolved/nonaccept; do not try to read a deliberately absent T file. |
| z diagnostics use coordinatewise missing-value handling | Use v1's complete-training-row filter and explicitly declare the SD convention. Save per-trial z and usable denominators; retain undefined values where appropriate. |
| Restart overwrites metadata before checking old bindings | Verify exact inputs, source/runtime, K/R, arm/seed and completed unique IDs before resuming. Reconcile missing neighbour receipts for already-written rows. |
| Provenance is recorded incompletely | Verify source/manifest identity; bind primary/oracle shard identities and R/nlme runtime; retain reconstructable V draw IDs, hash the neighbour archive, and reconcile its queried distances to the run log. |

The interval correction follows [Newcombe (1998), section 5, method 10,
p.2639](https://www.eiti.uottawa.ca/~nat/Courses/csi5388/Newcombe.1998.pdf):
for a positive numerator `ad-bc`, replace it with `max(ad-bc-n/2,0)` in phi.
Two published Table III cases also pass the independent transcription.
Branch-specific failures do not invalidate a clean run when those branches
did not occur. Preserve the launch source and fits, record any repairs, and
establish which branches actually occurred before interpreting the result.
If repair needs a restart, verify bindings first.

## 3. Candidate A: a reasonable bounded experiment, not a derived cure

The variance argument motivates C+ but is a delta-method heuristic. Under AR
environment and extinction selection, relevant conditional moments depend on
history, not just abundance. Low s alone does not imply larger demographic
variance: even the proposed expression contains `s(1-s)+f`. Rephrase the
rationale as a hypothesis that these summaries separate nuisance regimes.
D2 and an oracle improvement would not prove that mechanism uniquely.

Specify the constant-predictor case completely: h1=0, h2=mean squared centred
log change, and a flag. Reuse v1's exact transition/observation convention.
Report fit failures and support for all nine populations, signal removed from
T3, and power at both selected effects. Raw 3D and 5D radii are not comparable;
also measure selected-neighbour distances in the original C scale, or provide
explicitly within-dimension support diagnostics. These are development
specifications, not grounds for changing the target, K or validation gate
after outcomes arrive.

## 4. Candidate B: narrow the claim and inspect its power cost first

The replacement of the plug-in sketch with the complete v1 procedure as a
raw statistic resolves the previous nesting ambiguity. For a fixed grid point,
independent calibration and test raw values are exchangeable; the inclusive
rank `(1 + count(p* <= p_raw))/1001` is conservative with ties. A maximum over
grid-specific p-values needs no Bonferroni correction for validity at an
included point. This follows the Monte Carlo rank-test logic in
[Dufour (2006), sections 2 and 4](https://jeanmariedufour.research.mcgill.ca/Dufour_2006_JE_MCT.pdf).

The plan still needs four qualifications:

- The guarantee averages over random calibration tables. It is not exact
  5% control conditional on any particular frozen 1,000-row table. Fresh
  validation assesses the realised tables against the retained criterion.
- The numeric grid is fixed before fresh simulations, but was derived from
  empirical C already exposed in E20. "Data-independent once declared" is
  incorrect for the original empirical analysis. A fixed-grid simulation
  theorem does not validate the original data-adaptive construction or the
  structural null over nuisance values outside the grid. Candidate selection
  must settle the empirical target; no change to Barry's target is adopted here.
- Including p_raw gives a nested rejection region. It does not establish an
  exact prior-predictive 5% guarantee: v1's 46/1,000 passed the prespecified
  8% criterion. State only the validity actually established and the nesting.
- Setting unresolved calibration p* to zero is conservative for resolved
  analysed observations. An unresolved analysed observation must remain
  indeterminate and count as a null failure. The rank theorem alone does not
  control that failure-inclusive validation rate.

**Cheap power screen completed.** Build F_L from all 1,000 audited v1 low-s
p_hi values, then apply `max(p_raw,F_L(p_raw))` to disjoint stored power blocks.
No new simulation or fit is required. All these rows were resolved.

| Alternative | Raw v1 detections / 300 | Low-s-only wrapper / 300 |
|---|---:|---:|
| beta_min | 21 | 6 |
| 2 beta_min | 25 | 8 |
| Delta10 = 0.3 | 118 | 35 |
| Delta10 = 0.5 | 206 | 98 |

With this particular table, the largest rejecting raw p on v1's 1/2001 grid
is 0.0189905. Any full maximum wrapper **including this same table** can reject
only a subset. A newly simulated table may differ. This is post-hoc development
evidence, not validation or a guarantee of future power. No null sample is
tested against the CDF made from those same rows. The loss argues for reviewing
B's usefulness before its full calibration cost; it is not an information bound
for Candidate A or the nine-population study.

## 5. Shared evaluation and next ownership

Evaluate both candidates on the **same outer datasets**, with separate
reference/calibration streams. Current separate A/B outer seeds discard a
useful paired comparison. The plan's grid evaluation omits the centre, high-sigma
and strong-environment points: reuse exposed b2/b4 as development outers and
add a fixed fresh centre set alongside the four new corner sets. Calibration
tables must remain disjoint from their evaluation samples.

**Next response: Claude/Fable.** Repair/version D1c/D2; finish D3 with its
verified reporting/receipts; revise the candidate claims and shared evaluation;
respond to the cheap B screen before scheduling the full 8,000 analyses.
Astra then checks the corrected diagnostic and completed D3 evidence. No third
candidate, relaxed gate, empirical run or new Barry decision is introduced.

Reproducible local checks and source hashes:
[analysis/astra/v2_plan_review](../analysis/astra/v2_plan_review/).
