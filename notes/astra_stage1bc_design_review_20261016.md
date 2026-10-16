# Stage 1b/1c design review

Astra, 16 October 2026. One bounded review of `dc86ef8`, the Stage 1a report,
Stage 1c fitted draft, development design, earlier sampler reviews and
Correspondence 1751. The separate audits address run provenance and cost
estimation. No sampler, population simulation, fit or dispatch was run here.

**Recommendation:** the full noisy design is scientifically worth considering
on the resources Barry has identified. Keep its named outers, fixed C balls,
matched n=0 baseline and explicit failures. Sharding can preserve the target
exactly. The remaining items are finite design contracts to settle before
sampling or fitting; the projected cost alone is not a veto. Barry's stated
inclination is not yet authorisation for Stage 1b or 1c.

## P1 — Before Stage 1b: bind stable identities, ordered sharding and caps

Fable's first-K-in-global-order rule is sound. For each fixed setting, order
attempts by `(batch, proposal_in_batch)` and retain its first 2,000 accepted
pairs. A library is complete only after every earlier batch range is verified
complete. Faster later shards cannot substitute for an unfinished earlier
range. Cancellation after the crossing range is established does not change
the chosen library; all discarded computation still counts toward the budget.

The implementation contract must preserve the **existing setting IDs and
20,000-proposal batch boundaries**, not merely reuse the seed formula. Naively
changing the existing nested trial loop from 10 to 200 would renumber 1,050 of
the 1,080 pilot settings. For example, seed setting 30 currently denotes wild
dog, low-s trial 0, n=0; the naive larger loop assigns it to prior-predictive
trial 10. Append new IDs or bind an equivalent stable lookup. This is a
pre-implementation requirement, not a defect alleged in Stage 1a.

Pilot reuse is legitimate as a verified stream prefix. Resume each setting
from its last complete, verified batch, preserving all prior accepted-pair
identities exactly once. The no-exposure n=0 setting 576 starts at batch 0.
Reusing these exposed development paths does not make them validation data.
The second-library check needs an explicitly disjoint namespace or ranges
beyond the entire primary proposal cap; "disjoint batches" must remain true
after retries and expansion.

Before dispatch, bind per-setting proposal caps, bounded numbers of shards in
flight, wave ceilings and the campaign's allocated-CPU ceiling. Distinguish
useful attempts from later discarded shards, retries, cancelled allocations,
setup and idle cores. Preserve earlier holes as incomplete work rather than
forming a library from available later hits. A cap shortfall is **failure to
fill K within budget**, not evidence that the mathematical target has zero
support. Both the sampling cap and the execution-failure status remain visible.

The n=0/n=30 wave followed by n=300 is reasonable. A wave checkpoint may
change scheduling within its contract; it must not silently replace the
named design with whichever outers finished or whichever n gave attractive
fits. About 12 days is the arithmetic for 0.86 million CPU-hours at sustained
3,000-core occupancy, not a measured completion guarantee or a reservation
created by the idle-core snapshot.

## P1 — Before Stage 1c: make failures and gate criteria executable

The draft correctly retains incomplete datasets in named denominators. State
their scoring explicitly, as v1's contract v3 does:

- Null scenarios: every outcome other than `accept`, including library
  shortfall, numerical/fit indeterminacy and missing work, is a non-accept.
- Alternatives: only `reject` is a detection; every other outcome is a
  nondetection. Report the reason separately and never replace the outer.

Use all 200 declared IDs for each primary procedural comparison. Report
three-way accept/reject/indeterminate tables as well. Fitted-statistic or
p-value differences require both completed analyses; their complete-pair
denominator must be shown. A procedural binary comparison can include a
failed baseline under the rules above, but then measures the whole procedure,
including availability. The Stage 1a informative-only availability table is
not joint availability with the matched n=0 library; report that too.

The draft's "60/1000-equivalent" and "224/300-equivalent" are not executable
rules. If the original confidence criteria are retained, with four informative
null cells in the family, they give:

| Intended outers per cell | Maximum null non-accepts | Minimum detections |
|---|---:|---:|
| 25 | Cannot pass, even at zero | 22 |
| 50 | Cannot pass, even at zero | 41 |
| 200 | 7 | 152 |

These use the one-sided 98.75% CP upper bound <=0.08 and the one-sided 95%
CP lower bound >=0.70. Bind the family, confidence levels, gating scenarios
and the distinction between beta-min power and descriptive high-effect
detection. Baseline cells need an explicit role rather than being silently
added to a multiple-test family.

There is an important precision consequence: at 200 outers, a true null
non-accept probability of 0.05 passes the <=7 criterion with probability
0.2133, versus 0.9329 under the original 60/1000 rule. Retaining the confidence
standard therefore gives a stringent development adequacy criterion. A
nonpass can mean insufficient precision to establish the bound, not proven
miscalibration. Do not automatically increase the outer count or relax the
criterion after seeing fitted results. Agree its intended interpretation
before fits. The smaller 25/50 options remain possible estimation exercises,
but cannot promise a pass under this unchanged null criterion.

## P2 — Before budgeting the full campaign: complete the inventory

The report correctly includes primary n=0 sampling. The complete primary
inventory is 14,400 informative population libraries plus 7,200 shared n=0
libraries: **21,600 libraries and 43.2 million retained pairs** at K=2,000.
For fitting this means 1,600 informative analyses **plus 800 baseline
analyses**, or 2,400 primary analyses. Without justified caching, 4,001 T-vector
evaluations each imply 9,602,400 evaluations, before the independent-library
check. A bare "1,600 fits" subtotal omits the baseline.

The 0.86-million sampling projection is not a complete execution allowance.
Add the named independent-library subset, its fitting repetitions, fitted
primary analyses, sampling overshoot/discarded shards, retries and allocated
idle time. State gross versus additional work after credited pilot prefixes;
do not count reused paths or already-spent allocation twice. About 10 GB of
hit records is a planning estimate for useful retained material, not a hard
bound on shard/checkpoint/surplus storage. The resource decision should show
the expected case and enforceable ceilings separately. Cost-estimation
uncertainty is addressed by the independent cost review.

## P2 — Before fitting: resolve finite-library and resampling details

The matched n=0 reference is the right baseline. Sharing its one analysis
across n=30 and 300 avoids duplicate baseline work; retain that pairing in
comparisons and uncertainty calculations.

Clarify the draft's "k-NN on C" clause. Stage 1b already enforces the fixed
closed ball. Stage 1c should consume the first K accepted pairs from that
target, not recompute MAD, find a new neighbourhood or reselect the nearest
pairs. The reused v1 components are the declared T fitting, training
mean/covariance, Mahalanobis rule, tie handling, p bounds and scorer; their
library-loading adapter needs a small deterministic check.

The 4,000 resamples are independent index draws **conditional on the finite
libraries**, not 4,000 fresh paths from the ideal target. Bind the resampling streams and use independent index draws for training
and testing; sequential segments of a fixed stream are sufficient. Never
reuse the training matrix as the test matrix. The prospective validation of any later method must include this
finite-library construction. More resamples do not remove its approximation
error.

The second independent library is a useful diagnostic, not a proof that
K=2,000 is adequate. Name its subset before any fitted outcomes. A bounded
candidate is two outers per scenario at all three n levels: 24 repeated
analyses and 216 extra population libraries. Include an ordinary and a
difficult case selected from pre-fit sampling diagnostics, then preserve
those names and count any failure; do not choose only cases that complete
cheaply. Price that concrete subset before approval. Hold the fit and
resampling rules fixed and report paired p_hi differences and decision
changes. Do not select whichever library gives the preferred conclusion.

The crossing-batch surplus is not this dedicated second K-member library;
the draft should separate those two statements. One paired library check
estimates numerical sensitivity on its named cases, not calibration or a
universal finite-library error bound. A material change of the substantive
conclusion under the named check calls for an explicit follow-up decision,
not automatic retuning or bank expansion.

## P2 — Preserve the scientific interpretation

Replace "restore the support-limited calibration that v1 lacked" with a
neutral test of how information changes null non-acceptance, detection and
computational availability. The earlier evidence did not establish that v1's
failure was caused solely by finite-bank support. Exact informative sampling
does not guarantee fixed-theta calibration, especially at the low-s corner.

The experiment informs two stylised marginal-rate functionals. It does not
identify all nuisance parameters, translate n into real marked-animal years,
or establish a minimum field sample size. Two information levels can compare
performance or bracket a change. Their prebound noisy evidence draws must
remain unchanged; they are not necessarily nested observations from one
field study. The current limitations on empirical inference, uniform validity
and fresh validation in the draft are appropriate.

## Finite next decision

Bring Barry a corrected full noisy-design inventory with capped waves and a
priced independent-library check. Keep 200 named outers per scenario as the
main option he favours; do not substitute a cheaper design solely because
the calculation is large. His decision should distinguish Stage 1b sampling
from Stage 1c fitting. Freeze the latter's failure coding, exact gate meaning,
resampling and comparison plan before any fitted outputs are inspected.

The [arithmetic receipt](../analysis/astra/stage1bc_design_review/checks.json)
checks the naive stream-renumbering example, inventory and gate consequences.
It contains no population simulation. Only this note and its small arithmetic
files were written in this review.

16 October 2026, 20:31:17 AEDT (Australia/Hobart).
