# V2 diagnostic 1 and next-experiment review

Astra — 11 October 2026, Australia/Hobart. Reviewed `a60b266` and Fable's
Correspondence message 1530. Fable implements/executes; Astra critiques.

**Recommendation: continue development with changes.** D1 documents a
substantial nuisance displacement at the failed corner. It does not isolate
the cause of v1's failure. D2 can proceed as an association diagnostic after
the corrections below. Revise the oracle contrast before launching it, and
specify candidate B before treating it as a calibration procedure. No new
Barry decision is needed for these bounded development repairs.

V1 remains V-fail, with its frozen settings and all results retained. No v2
method is selected or frozen, and no empirical test is enabled by this review.

## Findings

### MAJOR — D1 does not rule out approximation error or establish a survival mechanism

[D1 NOTE lines 31–45](../analysis/fable/calibration/v2_dev/NOTE.md) interpret
average ranks as libraries centred on truth, infer sensitivity to s rather
than sigma, and exclude finite-library error. The retained JSON supports
the reported rank ranges, not those stronger conclusions.

A mean rank near 0.5 can average over large opposing errors; it does not say
that each trial's library is centred on its generating value or that its
conditional distribution is correct. At the fixed corners, the nuisance
displacement is compatible with incomplete identification by C. Comparing
one displaced sigma corner that passes with one displaced survival corner
that fails cannot identify a causal direction or establish insensitivity to
sigma. Nor does it measure what would happen under smaller neighbourhoods,
independent banks or exact conditioning. Residual nuisance dependence and
finite-library error can coexist.

**Repair:** retain the displacement finding; label nuisance mixing as a
hypothesis. Replace the categorical cause in D1's note, STATUS and E31's
interpretation, preserving the original record in Git. Report trial-level
distributions rather than treating aggregate mean ranks as local matching.

### MAJOR — The trend diagnostic has a numerical tie defect and measures an endpoint summary

The implemented mean non-final log change telescopes:

\[
\bar d=\{\log(N_{L-2})-\log(N_0)\}/(L-2),
\]

where the recorded vector has length L and the terminal count is indexed
L-1. Within each population, N0 and L are fixed. Thus the statistic is a
monotone function of the **penultimate count**, not a measure of temporal
path shape. Agreement would not establish that the series “decline alike”.

There is also a reproducible defect in `knn_nuisance.py:19–20,33–34`:
summing floating-point log differences can give unequal values for exact
endpoint ties, and `<`/`==` then misrank them. In a deterministic 343-path
fixture with identical initial/penultimate counts and lengths, the actual
D1 function produces three values differing by about 1e-16. One path's
reported midrank is **0.0321 instead of 0.5**, although every path is tied.
This is a numerical counterexample, not a measurement of affected D1 trials.
The retained aggregates cannot establish that impact. Standardising a tiny
roundoff spread can also produce meaningless z-scores.

**Repair:** calculate this endpoint quantity directly; for ranks, compare
integer penultimate counts within population and apply half-ties. Detect a
structurally constant library explicitly. Emit `null` with valid/undefined
counts and reasons, rather than NaN or a silent omission. D1 contains 12 NaNs
and fails strict JSON parsing. Preserve the original D1 output and write a
corrected version with the actual changes in ranks documented. A small
same-endpoint/different-path fixture is sufficient regression coverage.

### MAJOR — D3 needs a paired contrast and a limited interpretation

Scoring 200 new outers only against an oracle bank and comparing their rate
with 148/1,000 changes the outer sample as well as the reference. Use **the
same 200 outer datasets against both references**, preserving S, A, K =
2,000, R_train = R_test = 2,000, estimator, scoring and failure accounting.
Generate and bind the outer dataset file once; give the two reference arms
separate declared random streams. Keep the frozen v1 C feature mask and MAD
scaling in both arms so changes to the distance metric are not another
intervention. Report distances and C displacement in that common metric.

An oracle improvement would show that changing the reference's nuisance law
helps at this corner. It would not isolate survival: the whole nuisance
vector is fixed and bank density/geometry changes too. Finite-K error remains
possible. A failure would likewise leave approximation, support and other
implementation explanations open. It is a diagnostic, not an empirical
method or v2 validation.

**Finite execution specification:** 200 paired fresh low-survival outers;
the frozen prior bank versus the proposed fixed-theta bank; record both
outcomes/p-bounds, signed T residuals, discordant rejection pairs, paired
rate difference and its uncertainty. Keep every intended trial and failure.
Specify draw budgets, required selected-bank counts, support diagnostics and
the stop rule before simulation; 10^8 raw draws alone does not guarantee
2,000 retained paths for each population. Retain input hashes, runtime and
neighbour identifiers. Use the proposed disjoint development seed domain
with explicit bank/outer/reference substreams and bounded index ranges.

This is **400 reference analyses**, approximately twice the quoted fitting
subtotal before bank construction, assuming the same measured per-analysis
cost. Fable should record the actual estimate and capacity before launch.
No production freeze or new approval process is implied by this development
specification. For scale, even a hypothetical 10/200 rejection count has an
exact 95% interval of 0.024–0.090; it would not certify v1's null gate.

### MAJOR — Candidate B is a plug-in sketch, not yet composite-null calibration

A bank centred on a library-median estimate does not automatically account
for nuisance-estimation uncertainty or control error over a nuisance region.
D1 itself shows why this matters: low-survival wild-dog truth is about 0.20,
but its average library median is about 0.58. Concentrating a reference near
that estimate may preserve the mismatch. Specify the centring distribution,
bandwidth/dispersion, joint versus marginal nuisance treatment and target.

“Optional outer calibration” must become a defined part of the candidate
before evaluation. If it calibrates the full data-dependent plug-in procedure,
each simulated dataset's analysis must repeat C calculation, nuisance
estimation, reference construction and raw scoring. Generating simulations
at an original fitted value is distinct from fixing that value during every
simulated dataset's analysis. The latter evaluates a different procedure.
State whether calibration is marginal under selection or also conditional
on C, and measure the resulting nested computation cost.

Block 17's 11/300 is not validation of this candidate. Its parameter vectors
were drawn from the empirical libraries; selected outer data were then
tested against the unchanged prior bank. There was no per-outer refitting
and centre-specific reference. This is confirmed in `make_manifest.py:67–74`
and `e2e_benchmark.py:165,184–188`.

**Repair:** keep the existing second candidate class, but provide a complete
estimation-and-calibration rule and its supported nuisance-domain claim.
If only a plug-in reference is proposed, call it that and test its failures;
do not imply worst-case validity from the name. Plug-in, predictive and
conditional p-values are distinct approaches to a composite null; see
[Bayarri and Berger](https://www2.stat.duke.edu/~berger/papers/98-40.html).

## D2, candidate A and power wording

D2 may proceed on exposed outputs as **association**, not “attribution
between s and lambda”. In b3 each population's true s and f are fixed;
variation in displacement is generated by the data-selected library. Both
the displacement and rejection depend on that construction. Use declared
trial-level summaries or account for the shared outcome when examining nine
population rows; they are not nine independent rejection events. Preserve
collinearity, distributions and uncertainty. Candidate A still needs a
specified nuisance-sensitive summary and a development power check; D1's
endpoint-trend match does not nominate or validate such a summary.

Label s + f a **nominal growth proxy**. In `ar_cat`, the actual conditional
mean multiplier under the null is

\[
(1-\delta B_t)\left[\operatorname{logit}^{-1}
\{\operatorname{logit}(s)+\sigma z_t\}
+f\exp(\sigma z_t-\sigma^2/2)\right],
\]

and selection alters the environmental histories represented in the sample.
The nominal sum is not the selected process's actual growth rate.

The poor v1 power makes O3 a sensible planning expectation. It does not prove
that nine populations impose a 21/300 power ceiling or that any revised
procedure can at best yield O2/O3. A correction that only shrinks the old
rejection region cannot improve power on the same datasets; changed C or
reference laws need not produce nested rejection regions. Keep O1 unlikely
as a forecast, then measure candidate power at the retained beta_min.

## Evidence quality and handoff

The bounded [checks and receipt](../analysis/astra/v2_diagnostic_review/)
reproduce all reported rank ranges, match 81 stored corner means to the frozen
values, verify the bank/e2e source hashes, demonstrate the trend defect and
identify the 12 undefined fields. Two bounded reviewers separately checked
the source alignment and the D2/D3/plug-in logic. No banks were reloaded,
population simulations generated or models fitted in this review. The tiny
arithmetic fixtures use NumPy 2.3.5/SciPy 1.16.3, not the frozen runtime; they
demonstrate the numerical defect rather than quantifying its historical size.

Static code agrees on shard ordering, parameter alignment, C features and
MAD scaling. However, D1's result records no input hashes, runtime, trial IDs,
neighbour IDs, distances or boundary ties; it does not verify its manifest
or bank hashes. Thus no wrong-neighbour bug is demonstrated, but **exact
historical reconstruction is not independently established by this receipt**.
The [SciPy 1.11.4 query contract](https://docs.scipy.org/doc/scipy-1.11.4/reference/generated/scipy.spatial.cKDTree.query.html)
defines nearest-neighbour queries, not the provenance of this run. During
the next bank pass, retain compact per-trial evidence, compare Kth distances
with the rounded v1 records, and flag ties/precision limits. No second full
bank run is requested solely to repair the receipt.

**Fable's next output:** corrected D1 arithmetic/wording and D2 association
diagnostic, plus the paired D3 specification and complete two-candidate
definitions. Keep v1 unchanged and reportable. Carry out D3 only after its
written paired design, budgets and failure rules are fixed; this is ordinary
development preparation within the accepted tranche.
