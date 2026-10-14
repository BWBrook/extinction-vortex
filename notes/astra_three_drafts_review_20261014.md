# Review of the paper outline, external-information design and Haley protocol

Codex (Astra), 14 October 2026. Reviewed clean matching WSL/Mac commit
`e614b238af7c900e678b5382b6c804d0422b15d9` and discussion 70 through 1612.
Three bounded reviewers checked execution/source contracts, the paper outline
and the Haley protocol; this memo integrates their findings and independent
probability checks. Peer drafts remain unchanged.

**Recommendation:** Fable can produce the Haley narrative, source table,
conflict register and figure now, incorporating the finite corrections below.
Existing-results manuscript drafting can proceed with the corrected evidence
labels and claims. The external-information experiment is **design-only and
not ready for implementation or either proposed execution stage**. Repair its
sampling law, reference rule, seeds and cost basis first. It remains optional
work; it must not delay the completed-results paper or Haley deliverables.

This is review and work allocation within Barry's recorded core-paper-plus-
deep-dives direction, not a new empirical-test authorization. No simulation,
model fit, bank load, empirical statistic or external contact was performed.

## 1. Paper and Haley: proceed with amendments during production

The [paper-outline review](astra_paper_outline_review_20261014.md) verifies the
reported v1 results and kunanyi execution against the archived record. Its
essential corrections are:

- Separate **exposed historical reconstruction**, **prospectively frozen
  synthetic validation**, **exposed development diagnostics**, and **optional
  planned work**. The whole reanalysis was not preregistered before exposure;
  the RI primary was chosen after reconstruction fits were inspected. Cite
  the dated freeze if using "preregistered" for its limited validation scope.
- Replace "nuisance law, not locality, drove failure" and "fixed calibration"
  with the observed one-corner reduction from 34/200 to 7/200. D3 changes the
  reference law, bank and neighbourhood geometry. It cannot exclude locality
  effects or prove counts generally uninformative.
- State sample covariance with Ledoit-Wolf **only if condition number exceeds
  10^6**, and `R_train = R_test = 2,000`. Distinguish the null gate from the
  O1 power criterion. Report Q2 as descriptive detection rates of a procedure
  that failed its null requirement, with the comparator scenarios labelled.
- Historical reconstructed slopes can be reported with their exposure label.
  The prohibition concerns new empirical conditional-null tests and feedback
  inference, not the existing reconstruction table. Describe a pooled
  terminal-trajectory procedure, not executed single-series tests or verified
  complete censuses. Keep the already identified primary-text checks for final
  novelty wording; no broad new search is needed to draft verified results.

The [Haley protocol review](astra_haley_protocol_review_20261014.md) supports
direct production of its four deliverables. Fix the reversed fraction notation:
use separate exposed/survivor columns and plot **survivors/exposures**, e.g.
8/13 rather than 13/8, and genuine 0/3 and 0/7 pup persistence. Label transitions
`t -> t+1`. Missing or zero-risk cohorts are gaps, not zero persistence; missing
stage/arrival years stay missing. Show source conflicts at the affected points
and state that uncertainty is unquantified, not absent. Pooled intervals are
context only, never annual Haley error bars. The future quantitative extension
remains uncommissioned and no OLS/AR(1) estimator is selected here.

Recovery-matrix section 8 supersedes its earlier verdicts. Make two small
repairs while using it: the transplant is **not established as a Haley removal**
(unknown donor does not establish non-Haley origin); Maligne ID 378 has blank
**total and composition fields**, while its identifier, date and location exist.

## 2. External-information design: blockers before implementation

### B1. Distinguish stationary marginal rates from a field-observation likelihood

Draft lines 38–56 correctly map the model to unselected stationary M0 means,
but call them realized annual field rates and label the binomial/Poisson arm
"realistic". The generator shares an environmental state and catastrophe across
all animals in a year; its recruitment parameter is per counted individual,
not per breeding record. Neither the joint field likelihood nor its precision
is determined by two marginal means and total animal-years.

For n animals observed in one shared year with random survival probability P,

`Var(K) = n p(1-p) + n(n-1) Var(P)`.

For total recruitment conditional on a shared annual per-capita rate F,

`Var(R) = m E(F) + m^2 Var(F)`.

Survival and recruitment can also be correlated through their common environment;
AR(1) adds dependence across years. Ten animals sharing P = 0.2 or 0.8 have
survivor-count variance 10.6 rather than the Binomial(10, 0.5) variance 2.5.
A corresponding two-state recruitment example has variance 74 rather than 10.
These are exact illustrative calculations, not estimates for the real studies.

**Minimal repair:** either label the initial independent binomial/Poisson
experiment a **stylized measurement model for long-run marginal census-class
rates**, with n an ideal information index rather than a required field sample
size, or specify an actual external monitoring design: years, exposures per
year, shared versus independent survival/recruitment observations, environmental
paths and their integrated joint likelihood. Do not infer a field-study
sample-size requirement from the stylized arm. Stage-specific observations
belong to the case-specific model, not an automatic substitution into this
unstructured generator.

The likelihood based on s-bar and f-bar also depends on sigma, p_c and delta.
It informs **two rate functionals**, not exclusively the latent parameters s
and f. The joint prior can remain prior (b); its weighted nuisance marginals
need not remain unchanged. Even exact knowledge of these two means is not the
Oracle-6 limit. Define E separately for each of the nine populations and state
whether an information level is per population or a total study allocation.

### B2. Make the selected joint law unambiguous

Draft lines 16–25 can be read as first drawing theta once, then repeatedly
drawing a path until it satisfies selection. That is different from v1's
prior-predictive bank, which draws theta and a path together and retains the
pair only if the path satisfies S and the cap A.

Let `q(theta) = P_theta(S,A)`. The v1 retained parameter law is proportional
to `pi(theta) q(theta)`. Reweighting that bank by `L(E|theta)` is appropriate
for the joint prior-predictive experiment conditioned on S,A. If theta is
instead held fixed during path rejection, its marginal remains pi; a bank
reweighting for that different target would also need `1/q(theta)` (and a
method for obtaining it). Do not silently change targets.

**Minimal repair:** explicitly preserve v1's draw-pair-then-select law for b1
and the existing fixed-theta laws for the corners. Include S, A, the census
design and exact versus approximate C conditioning in the reference formula.
In the ideal independent-evidence null, the joint density is proportional to

`1{S(N), A(N)} pi(theta) p0(N|theta) L(E|theta)`.

Conditioning on C,E then gives the intended ideal prior-predictive reference.
It does not guarantee pointwise fixed-theta calibration or correctness of a
finite weighted neighbourhood. A two-parameter exact example in the check
receipt gives posterior weights [0.5,0.5] under joint selection versus [0.9,0.1]
under fixed-theta path conditioning. The distinction is substantive.

### B3. Weighted ESS is not an adequate control of C locality

Draft lines 61–86 grow the C neighbourhood until ESS reaches 2,000. Information
levels therefore change both nuisance weights and approximation in C. This is
a new developmental reference rule, not simply the frozen v1 procedure supplied
with external evidence. Large ESS can be obtained from distant trajectories
and does not guarantee a good conditional reference.

ESS is also not monotone with the number of members: ten equal unit weights
have ESS 10; adding a weight of 100 reduces it to 1.209. Specify first crossing,
ties, exhausted banks, log-weight stabilization and all-zero/non-finite weights;
a final-prefix ESS check is not equivalent to a first-crossing rule.

**Recommendation for the first feasibility draft:** hold the original K = 2,000
membership fixed, evaluate likelihood weights and report weight concentration
without T fits. This separates the immediate information/support question from
another neighbourhood redesign. It does not guarantee enough effective support
and does not justify inventing a new ESS cutoff after seeing results. If it
fails, return the measured tradeoff and costed alternatives; do not automatically
expand to 200,000 or launch new banks. Any later expansion needs an explicit
C-distance constraint or a separately labelled algorithm comparison and new
calibration evidence.

The Stage-0 rule currently has an undefined "median" and measures shortfalls
over population pairs, although a single failed population makes the complete
nine-series test fail. Report per-population diagnostics **and the fraction
of outer datasets with any failure, separately for each scenario and level**.
For illustration, independent 1% pair-failure probabilities yield 8.65%
dataset failures; 10% yields 61.26%. Do not pool scenarios to hide a failed
corner, or use a 10%-of-pairs screen as evidence of calibration feasibility.

### B4. The ideal and timing arms lack executable probability definitions

"Same Fisher information" does not specify a unique truth-centred prior or
likelihood on six parameters. One transparent option for the **stylized**
binomial/Poisson benchmark is its expected log-likelihood: use pseudo-counts
`n sbar_true` and `m fbar_true` in the binomial and Poisson log-likelihood,
retaining the common prior and selection convention. This defines an ideal
noise-free comparator (up to theta-independent constants), not observed
external data. State the formula and what comparison it is intended to isolate.
The real-evidence exchangeability argument cannot simply be asserted for it.

Timing and same-year evidence need a different joint model. If E depends on
the focal path or its environment, replace the independence factorization
with `p0(N,E|theta)`; using `L(E|theta)` unchanged would be an intentionally
misspecified analysis and must be labelled that way. The stored exposed
outers retain census counts and parameters, not the full annual environmental,
catastrophe, survivor or recruit histories. Their realized own-year vital rates
cannot be recovered arithmetically from those fields. Five annual transitions
and five recorded-census transitions also differ where census years are missing.
In M_A, g multiplies survival **odds**, not survival probability, and multiplies
recruitment rate; a decline-phase definition must apply both correctly.

**Recommendation:** defer timing and shared-year arms from the first tranche.
Their present uncertainty is the observation law and recoverable history, not
whether five is the best window length. They can be specified separately later
without blocking the simpler independent-evidence experiment.

### B5. Seeds collide; resource estimates are not an execution plan

The declared formulas satisfy `seed_E(cell+10, trial) = seed_reference(cell, trial)`.
Disjoint streams require a tuple-based or explicitly nonoverlapping allocation
covering arm, level, bias, scenario, trial, population and train/test role.
Prespecify any deliberate coupling between levels/arms separately from unintended
reuse, bind the enumeration, and verify all active streams before implementation.

The main factorial is 80 x 200 = 16,000 analyses; the 50 Oracle-6 power analyses
are additional, as are their per-outer banks. The stated 50 x 40 minutes is
33 h 20 min before fits/overheads, not a measured end-to-end cost. A per-level
bank also cannot generally be drawn once without specifying how it accommodates
different realized E across outers. The seven-hour Kunanyi estimate does not
yet measure weighted lookup, memory, concurrency, bank strategy or the revised
likelihood cost. Reuse existing cluster evidence only with a clearly stated
scaling model and its limits. Do not seek approval for the oracle cost before
preparing a concrete bounded design.

The source/metadata audit verifies 13.46–29.90 million retained records per
population: nominal availability of 200,000 members is not the problem, while
their weighted ESS is unknown. Exhausting the proposed cap across the full
factorial would require up to 28.8 billion candidate-weight evaluations.
Neighbour ordering can be shared, but that optimization and its memory costs
must be specified rather than omitted from the estimate. The existing sampler
draws uniformly from fixed K; weighted variable-size sampling requires a declared
new implementation. These are planning bounds, not measured runtime predictions.

## 3. Answers to the four open questions and next ownership

| Fable's question | Recommended next draft |
|---|---|
| Grow the neighbourhood to fixed ESS, or retain fixed K? | Retain fixed K for the first no-fit weight/support diagnosis; expansion would be a separate algorithm requiring its own comparison. |
| s-bar/f-bar versus stage-specific rates? | Use explicitly defined marginal census-class rate functionals for the synthetic study, with either a stylized information model or a justified monitoring likelihood. Stage-specific inference belongs to the later case model. |
| Five-transition decline window? | Defer; first specify annual timing, latent histories, dependence and the feedback mapping. |
| Cut cells? | Yes. First draft an unbiased two-level independent-evidence feasibility check at n = 30 and 300 for b1, b3, b5 and b16; treat this as a proposed eight-cell diagnostic, not an authorized run or adequate validation. Defer bias, timing, oracle-power and the full factorial until feasibility and cost justify them. |

**Fable next:** produce the four Haley deliverables with the inline corrections;
start drafting the verified core methods/results with the corrected labels;
return a smaller external-information specification addressing B1–B5. No further
protocol round is needed for the descriptive or existing-results writing. Astra
reviews the resulting artifacts and the revised experiment before any execution
decision. Barry need not adjudicate routine notation or missing algorithm
definitions; contact, publication and consequential new resource choices retain
their existing boundaries.

## Verification and limits

[Exact probability checks](../analysis/astra/draft_review_20261014/theory_checks.py)
and [their receipt](../analysis/astra/draft_review_20261014/theory_checks.json)
reproduce the selection, shared-year variance, ESS and any-of-nine examples
without random generation or project-data fitting. They show logical failure
modes, not their frequency or size in these populations. The
[source/seed/cost checks](../analysis/astra/draft_review_20261014/design_checks.py)
and [receipt](../analysis/astra/draft_review_20261014/design_checks.json) contain
seven source checks and exact planning arithmetic. Existing archived results were
checked against their receipts; no raw-bank or validation rerun was needed.

One project-record correction accompanies this review: Astra's previous STATUS
edit placed the single v1 test-reference failure note under the **A null screen**.
It belongs under **A power**. The audit receipt and previous review memo already
assign that failure correctly to baseline b16. The present STATUS repair moves
the note; no result or source data changes.
