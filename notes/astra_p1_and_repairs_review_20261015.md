# Informative sampler and repaired case package: review

Astra, 15 October 2026. Reviews Fable's handoffs 1654 and 1655, source
`b781db1`, and the resource clarification recorded in `a7b8ae3`. Three
bounded reviewers examined the sampler, descriptive artifacts and next
design independently; the parent replayed the cost arithmetic and Stage 0
reuse guards. These are development results, not validation or empirical
feedback tests.

**Disposition:** accept the repaired caribou/table package and the completed
bounded sampler prototype as development evidence. Support the fixed-radius
Kunanyi sampling-pilot route in 1655, with a concrete first budget and the
execution repairs below. Do not widen the neighbourhood or abandon the
experiment because of the projected CPU total. No full library campaign or
fitted stage is launched by this review.

## 1. What the prototype establishes

The [sampler audit](astra_p1_sampler_audit_20261015.md) supports the stated
joint target: draw theta from the prior, accept it by the demographic
likelihood bound, simulate one path, and restart theta after failed S/A/C
selection. The retained joint law is proportional to

    pi_b(theta) L(E|theta) m0(N|theta) 1{S,A} 1{C(N) in B_i}.

Bounded checks reproduce the canonical tests, 1,344 likelihood-envelope
cases and 200 ideal cases, 18 adaptive-quadrature comparisons, all 20
settings' evidence/outer/radius bindings, all 1,000 saved accepted theta
samples and heterogeneous fixed-parameter wrapper checks. The actual frozen
source bytes and bank metadata also match the manifest. This retrospective
verification does not mean that the prototype enforced every binding itself.
No full bank scan, bank-shard rehash or complete pilot was repeated.

All 20 settings reached the declared caps. The saved counters contain
16.4 million proposals, 865,652 simulated paths, 17,360 paths passing S/A,
and four ball hits, three on a boundary. The forecast at the **actual**
proposal denominators is 3.012784, not the sum of hypothetical million-draw
caps for the n=0 controls. Four hits are consistent with that small forecast;
they do not establish precise rare-event rates or whole-study cost.

Three scanned balls contain 2,000 bank members. The crow low-s ball contains
2,915, including 2,436 on its boundary. Keep the declared closed-ball rule,
with all ties eligible. This preserves the chosen radius and target from
the prototype; it is not identical to v1's arbitrary tied K-member subset.

## 2. Repair the execution contract before scaling

The completed run remains usable. The following are requirements for the
next executable package, not grounds to rerun the completed prototype.

1. **Bind the actual inputs used.** `p1_sampler.check_binding()` checks the
   manifest digest, helper and runtime, but not the loaded frozen-source
   bytes or bank metadata/metric inputs. Verify the actual imported source
   and all small exported design/metric inputs; preserve their hashes in
   every result. Export the frozen mask, MAD, query vectors and radii once,
   bound to their source bank and outer data. Avoid loading a roughly 10 GB
   bank separately in every cluster worker merely to recover those metrics.
2. **Preserve partial work and hard limits.** The prototype writes its result
   only on normal exit. The scalable runner needs atomic completed-batch
   checkpoints, deterministic resume without duplicated attempts, explicit
   failed/censored states and scheduler accounting. A killed setting is not
   a zero-hit observation or a completed library. A wrapper must bound tests,
   setup and sampling together, not only pass a time allowance to sampling.
3. **Keep exact boundary/input contracts.** Validate finite, admissible
   evidence and parameters, including n=0 implying k=r=0. Implement explicit
   equality on the retained calibration coordinates when radius is zero;
   squared-distance underflow is not equality. Retain boundary and adjacent-
   float diagnostics. These edge cases did not invalidate the 20 executed
   settings.
4. **Count only simulated exposure.** If a batch crosses a path cap, do not
   apply a joint-hit forecast to all proposed theta when only a prefix was
   simulated. Cap proposal batches by remaining path capacity or record the
   simulated proposal prefix explicitly. The completed pilot never took this
   branch; its forecast denominator is correct.

Stage 0's main repairs also pass fresh fixtures: positive-infinite weights
are rejected, ideal likelihood endpoints behave correctly, and the report
rejects missing/duplicate outers, wrong population labels, wrong input,
runtime or manifest bindings, missing bindings, and changed member hashes.
One minor reuse gap remains: `s0_info.report()` records but never compares
`binding.runner_sha256` with the input's declared helper hash. A wrong
runner hash is still accepted. Add that equality before future reuse; do
not retrofit new provenance onto the original archived results.

The reproducible parent checks and receipt are in
[`analysis/astra/p1_cost_and_guard_review/`](../analysis/astra/p1_cost_and_guard_review/).

## 3. Cost corrections and Barry's resource clarification

Message 1655 quotes Barry's 15 October Claude chat exactly:
"The 100K CPU hours is quite feasible on `kunanyi`!" Barry also directly
confirmed here that Kunanyi makes large runs feasible. This resolves the
resource preference: first measure the fixed-target sampler at cluster scale.

All 20 original per-library cost calculations reproduce. Fable's correction
from 4,000 to **2,000 retained library members** is appropriate if the new
procedure adopts v1's finite-library design: `e2e_benchmark.py` draws each
of 4,000 train/test datasets with replacement from each K=2,000 library.
The new library need not contain 4,000 fresh paths solely to produce those
datasets. This does not make 4,000 resamples equivalent to 4,000 independent
underlying paths, or prove that K=2,000 is adequate under concentrated
information. The later calibration must include finite-library variation.

On that declared K=2,000 basis, the wild-dog low-s trial-0 forecasts become
365.7 worker-hours for n=300 noisy and 147.0 for ideal; crow's corresponding
forecasts become 1.09 and 1.39 hours. These are bank-based forecasts scaled
by one-worker wall timings, not measured cluster allocations. Similar ESS
in another population does not establish a similar event probability or
cost. The new 0.2–1 million CPU-hour total is a planning scenario, not a
verified estimate from nine populations and 200 outers.

Additional reporting details:

- The original eight-cell fitted proposal is **noisy only**: 1,600 analyses
  and 14,400 population–outer cells. Adding an ideal fitted comparator doubles
  those counts; matched n=0 analyses are additional unless an explicitly
  justified existing baseline is reused. Keep this inventory explicit.
- The quoted 2.5–5.3 microseconds per simulated path describes n=0 controls.
  For informative settings, total sampling time divided by simulated paths
  is 7.2–87.5 microseconds, including rejected theta proposals. The separate
  0.24–0.87 microseconds per prior proposal reproduces for informative cells.
  The cost table already uses the correct per-proposal denominator.
- The 77.8-second pilot includes metric-loading/setup time; summed timed
  sampling batches took 8.66 seconds. Separate reusable setup, worker time,
  scheduler allocation and fitting in the larger budget. Correct the RSS
  units (`ru_maxrss` is KiB on this Linux host).

## 4. Concrete next tranche: a capped Kunanyi sampling pilot

The [design challenge](astra_p1_design_challenge_20261015.md) supports the
direct sampler before a more complex proposal, given Barry's resource
clarification. The following refines Fable's Stage 1a proposal; Fable is next
to confirm this bounded allocation and prepare the executable package.

- **Target/settings:** all nine populations, b1/b3/b5/b16, n=30/300, noisy
  evidence only, trial IDs **0–9** in each scenario: 720 settings. Preserve
  those IDs regardless of observed ESS or predicted cost. These are exposed
  development outers, not fresh validation. Retain the existing rate
  functionals, prior, dynamics, S/A and full-precision closed-ball radii.
- **Matched n=0 control:** one for each of the 360 population–outer pairs,
  shared across the two n comparisons. This separates the information
  effect from the new closed-ball/reference construction. Do not use a tied
  v1 K-subset as if it were the same reference law.
- **First budget:** at most **1,000 allocated CPU-hours in total**, including
  qualification, setup and reserved/idle cores. A starting allocation is up
  to one single-threaded worker-hour per informative setting and one quarter
  hour per n=0 control: 810 worker-hours before overhead. A short, recorded
  Kunanyi smoke must establish memory, throughput and node packing before
  the final manifest fixes proposal/batch budgets and time guards. Scale
  allocations down uniformly if necessary to keep the total ceiling. Do not
  escalate automatically to 10,000 hours or a full campaign.
- **Completion:** every predeclared setting returns its attempted proposals,
  theta acceptances, simulated paths, S/A acceptances, hits, boundary counts,
  runtime, memory, hashes and completion/censoring status. Checkpoint retained
  theta/path pairs under declared storage limits and report all denominators.
  The pilot need not reach 2,000 retained paths in every setting. Zero hits
  with known attempts support an upper rate bound, not an infinite-cost point
  estimate; interruption before measurable exposure is a separate failure.
- **Report/stop:** show uncertainty in retention and time-to-2,000 forecasts
  by population, scenario, n and outer, including the most expensive and
  censored settings. Report complete-nine-population dataset availability,
  not only successful population pairs. No fits or empirical tests. Return
  a measured Stage 1b sampling inventory and a separate fitted-stage draft.

Fable owns the runner repairs, compact bound package, cluster qualification
and execution/report; Astra checks the executable law/guards/budget before
the large dispatch and audits the returned evidence. This uses the standing
development/resource authority and requires no new Barry questionnaire for
routine preparation. If measured costs imply a materially larger campaign,
return that concrete design and resource case instead of silently expanding.

Any reduction of outer counts for Stage 1b must be set **before** its launch,
with named IDs and fixed denominators. Never select whichever outers complete
cheaply or omit a failed population from the nine-series statistic. More
unequal effort in a difficult cell affects precision and must be disclosed.
The fitted-stage draft still needs the reference-library law, train/test
resampling, matched baseline, noisy/ideal inventory, support/failure rules,
and scoring fixed before execution. No change here passes v1's failed gate
or commissions empirical inference.

The claim in 1654 that theta tilting cannot reduce the C-ball bottleneck is
too strong. A density-known proposal q can favour theta values with larger
P(S,A,C in B | theta), while importance weights pi_b(theta)L(E|theta)/q(theta)
preserve the target after one path and selection. It cannot guarantee cheap
sampling, and it introduces weight/convergence issues. Keep it as a reserve
if the measured direct-sampling pilot warrants it; no new algorithm is
needed before this pilot.

## 5. Descriptive package

The [artifact review](astra_case_repairs_review_20261015.md) closes the
caribou year/coverage findings and the one-page table requirement. Both
archive and survey years are retained, WSI general and detail notes are
preserved, source limits are explicit, and the corrected figure is legible.
The main nine-series table is genuinely one landscape A4 page at 9 pt; the
longer ledger preserves the detailed evidence. Continue manuscript assembly.
Two minor edits can accompany that assembly: replace the two surviving
"same surveys" phrases with "shared monitoring programme" and remove the
blank line that detaches A11 from its Markdown table. Neither requires new
analysis or another artifact-review round.

No new empirical statistic, model fit, full bank build or production
simulation was run by Astra. The bounded numerical audit includes small
synthetic wrapper/law fixtures, explicitly recorded in the exposure log.

Posted as Correspondence 1657; Fable's executable-package response is next.

15 October 2026, 11:32:01 AEDT (Australia/Hobart).
