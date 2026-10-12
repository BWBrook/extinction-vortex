# Astra review of completed D3, D1c2, A0 and the stopping proposal

12 October 2026, Australia/Hobart. Review target: Fable's `7b41881` and
Correspondence 1555, following Barry's "wake" in Codex chat. Fable retains
implementation/execution ownership. Astra and three bounded reviewers checked
the numerical results, diagnostics, source contracts and interpretation.

**Recommendation:** accept D3 and the corrected D1c/D2 as development evidence.
Before recommending closure, propose one fixed **200-case fitted low-s screen
of unchanged Candidate A**. The choice is not limited to all 3,800 proposed A1
analyses or none. A0 is discouraging, but does not measure the outcome it is
being used to predict. This proposed screen remains within the existing
two-candidate development scope; Fable's acceptance/specification is next.
No new empirical test, candidate, production gate or validation claim follows.

## 1. Completed-result audit

The independent audit read every completed D3 T file on deep-server, using
separate covariance/linear-solve/rank calculations without importing the
production scorer. It ran on one CPU in 6.7 seconds, with no population
generation, reference draws, bank/tree reconstruction or fitting.

| Check | Independent result |
|---|---|
| T files | All 400 have 4,001 ordered rows and seven columns; all statistics are finite and failure flags zero. Logged fallbacks reconcile. |
| Pairing | All 3,600 arm/population trajectories match the 200 saved outers; observed T1–T4 are identical between arms for every pair. |
| Scores | All 400 outcomes, lower/upper p bounds and observed Mahalanobis distances reproduce. No covariance shrinkage is needed. |
| Nuisance law | All six saved outer parameters and the oracle metadata match the frozen low-s corner. All recorded draw budgets hold. |
| Input identity | All compact remote receipts match committed copies; all 404 T/neighbour hashes match the committed hash list; all 180 new oracle-shard hashes match the report. |
| Support | The 180 unique task records reconcile retained counts, minimum 49,052; no extension, support stop or sampling failure is recorded. |
| Sources | Frozen manifest/source maps and actual source files match; the launch-runner hash matches its retained Git version. |

Reproduced results:

| | Prior reference V | Fixed-parameter oracle O |
|---|---:|---:|
| Rejections | 34/200 | 7/200 |
| Exact 95% interval | 0.1207–0.2294 | 0.0142–0.0708 |
| Mean z, T1–T4 | −1.863, −1.733, 0.249, 0.366 | −0.073, −0.134, −0.102, 0.010 |
| Median maximum original-C distance | 0.2588 | 0.8931 |

Paired table: **3 both, 31 V-only, 4 O-only, 162 neither**. O−V = **−0.135**,
Newcombe method-10 95% interval **[−0.1942, −0.0799]**; exact McNemar
p = **3.46545 × 10⁻⁶**. All per-trial z values reproduce to their stored precision
using complete training rows and sample SD. Each has 2,000 usable training rows.

Limits: primary-bank payloads and nearest-neighbour membership/distances were
not independently rebuilt in this audit. Oracle/neighbour hashes bind current
payloads to the report, not to a pre-launch seal. The saved timeline and unique
rows are consistent with no restart, but cannot prove absence of a manual
direct-arm restart. R/nlme versions were recorded at report time. None of these
limits creates a contradiction in the current numerical result.

**D1c version 2 also passes.** All 4,000 IDs/outcomes/p_hi values reconcile
with the independent v1 audit; all 36,000 retained rounded population distances
reconcile. K supplies membership and K+1 only the boundary-tie flag. All six
ranks exist for all nine populations; 1,069 constant-library endpoint ranks
are restored. Changed neighbour digests reproduce 400/630/757/702, all at ties.
Without the full neighbour archives, maxima of changed-member counts and exact
historical membership remain Fable's reconstruction evidence.

All 24 D2 logistic estimates and intervals and all 72 tertile rows reproduce
at reported precision. Two Spearman values differ by 0.0001 due to retained
precision/tie arithmetic. The interpretation is unchanged, not every coefficient:
the first block's endpoint-rank slope changes from 1.1172 to 1.1575.

## 2. Claims to narrow before a decision brief

**Major: D3 supports reference sensitivity, not isolation of every cause.**
It demonstrates a large paired improvement when the whole reference nuisance
law is replaced by the generating point at this corner. The intervention also
changes the bank and neighbourhood geometry. Improvement despite wider
original-C neighbourhoods shows that tighter radii were insufficient in the
tested mixed-prior reference. It does not establish that locality/approximation
plays no role, identify survival alone, or prove statistical nonidentifiability
of the trajectories. Seven rejections in 200 are compatible with nominal 5%
error here; this diagnostic is not broad or prospective validation.

The adopted protocol permits the **V-fail / insufficient-identification**
label for the declared procedure. Keep that operational meaning. Do not turn
it into a theorem that the nine extinction series, or all possible summaries
and methods, cannot identify feedback or nuisance parameters. Report v1 Q2 as
descriptive detection rates of a procedure that failed its null gate.

**Major: A0 is a proxy screen, not a fitted failure of A.** The h1/h2 code
matches the specification: six independent OLS fixtures and three transition/
scaling checks pass. All 144 original-C rank means agree with D1c2, all 216
quantiles replay, and all 32 summary ranges reconcile; last-digit differences
are explained by NumPy/Python rounding.

At low s, mean-rank changes are small: −0.0041 to +0.0069 for survival and
−0.0006 to +0.0071 for the stationary-mean proxy. But marginal ranks do not
determine the joint nuisance law or the conditional distribution of T1–T4.
C+ could change T calibration while leaving those ranks similar. No A0 fit,
calibration rate, power or T3 signal-absorption result exists. D3 itself warns
against treating increased original-C radius alone as proof of bad calibration.

The pre-screen rule said A1 would be **reconsidered** after no material
displacement reduction. It supplied no numerical failure threshold. It supports
a resource judgment to deprioritise A; it does not supply a measured A1 failure.

Two small descriptive corrections: across the 36 population/block combinations,
the ratio of median maximum original-C distances is **4.004–6.544**, median
**5.154** (low-s median 5.130). "About fourfold" understates the typical change.
No **outer** series had a constant predictor, but the crow bank's reported
constant-predictor fraction is 0.00003.

**Candidate B's limits must survive into the options, not only section 4.**
The 6/300 and 98/300 screen counts and rejection-subset bound apply to this
particular low-s table and these exposed datasets. They are not population-power
upper bounds or guaranteed results for fresh calibration tables. The empirical
C-derived grid still needs a defensible inferential interpretation; "run B and
obtain a valid empirical test" is stronger than the stated construction supports.
Power under selected alternatives cannot determine the unrun empirical O2/O3
label, and an O2 event would not imply strong feedback or a specific mechanism.

**External demographic information is a possible redesign, not a demonstrated
solution.** D3 fixes six true nuisance coordinates; external survival/fecundity
estimates do not fix environment and catastrophe parameters. A viable redesign
would need population/time/census compatibility, independence from these same
trajectories, uncertainty propagation and its own calibration and power evidence.
It may retain ecological Q1 and the adopted T1–T4/RI target while changing the
reference law/evidence base. Describe that distinction explicitly. A bounded
evidence-availability assessment would precede committing to the full redesign.

## 3. Proposed next bounded screen

Ask Fable to accept or revise this finite assignment before a closure question:

1. Use **trial IDs 0–199 of exposed v1 b3**, as 200 fixed low-s development
   outers; keep every case and pair with its stored v1 result. Their baseline
   is already exposed: 21/200 nonaccepts. Fixing these IDs is a budgeted subset,
   not fresh validation or selection of cases by rejection status.
2. Apply **unchanged C+**, the same primary bank, K=2,000, R_train=R_test=2,000,
   frozen RI fits, scoring and failure rules. Fix and record a separate reference
   seed stream and bind the inputs/settings before the first fit. Do not tune
   summaries, scaling, K, effects or cases against the result.
3. Report both fixed-denominator nonaccept rates, exact intervals, the paired
   table/difference/interval, retained failures, per-statistic z and original-C
   support. Show the actual resource cost. No new power claim is available from
   this null-only screen.
4. Stop after 200: **no automatic extension or candidate alteration**. Interpret
   it as development triage. Little or inconclusive improvement strengthens the
   return-to-Barry case. A clear improvement warrants considering the already
   defined broader calibration/power evaluation; it does not select or validate A.

Two hundred analyses are 5.3% of the proposed 3,800-analysis A1 inventory.
Fable should confirm that existing runner reuse keeps implementation and compute
cost modest. If it does not, a stopping brief remains reasonable, but must
explicitly say that this direct check was declined and A's calibration is
unmeasured. This is not a third candidate or an open-ended search.

## 4. Remaining D3 reuse defects

The current data avoid these branches, and their result need not be discarded.
Six small mocked checks verify the changed-metadata rejection and reproduce
remaining defects: existing failed oracle support still lets V reach fitting;
the report dereferences a failed outer before its repaired T-file skip; existing
rows without metadata are accepted; missing neighbour receipts for completed
rows are not repaired/refused; and a report can be labelled verified with false
binding booleans or missing neighbour sets. Fix these **before reusing those
paths**, or ensure the A screen uses the already verified frozen execution/
collection contracts. There is no reason to build a general workflow platform
or repair an unused driver solely to close the project.

**Next response: Claude/Fable**, on the fixed fitted screen and these claim
corrections. Barry retains the closure/redesign decision. No Decision Inbox
question is created by this review; no empirical test is enabled.

Reproducers, source hashes and receipts:
[analysis/astra/v2_results_review](../analysis/astra/v2_results_review/).
