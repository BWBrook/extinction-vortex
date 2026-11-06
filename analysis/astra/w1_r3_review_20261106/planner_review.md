# W1 round-3 throughput explanation: bounded source review

Reviewed `0cc1e4a`, board 2907 as supplied to this reviewer, the committed
collection receipt, `p3_stage1b.py::plan()` and `s1b_node.pbs::slot()`.
No production edits, remote calls or new simulations. Parent owns the archive,
summary arithmetic and subjob-count audit. The parent supplied the settings file;
this reviewer independently verified its `fa772829…` SHA-256 and called the
actual `plan()` against empty temporary setting directories, without simulation.

## Supported mechanism and action

The proposed mechanism is consistent with the code. With no pilot or shard
observations, the planner estimates hits per batch from the cell prior and CPU
cost from the bound rate. It computes desired concurrency as the ceiling of
estimated remaining CPU-hours divided by the target wall time, bounded to
1–28 (`p3_stage1b.py:536–576`). If that estimate fits within 24 hours, it creates
one initial range. Completing a low-hit range can greatly increase the estimated
remaining effort, producing additional ranges. The worker normally replans after
finishing a range (`p3_stage1b.py:816`).

An idle slot resets its idle clock while any sibling in its subjob remains busy.
Once all siblings are idle, the subjob can retire after 1,800 seconds even if
other subjobs still have claims in flight (`s1b_node.pbs:77–93`). Thus an array
oversized for its initial runnable ranges can lose much of its capacity before
later fan-out. No code change is needed to resume queued ranges with a topup.
The unchanged idle budget plus sizing from actual initial runnable work is a
reasonable operational response within the reviewed design.

## Corrections and limits

- **The actual initial W1 plan has 32 ranges, not 18.** Sixteen settings without
  a pilot each get one range, but `s00208` gets nine and `s00835` gets seven.
  Both have imported pilot observations. Independent formula evaluation and
  calls to the actual runner `92674ee8…` agree. The no-pilot initial ranges span
  500,140–3,975,536 batches, not the reported 0.7–3.8 million; their estimated
  CPU duration is 2.44–16.76 hours. This still leaves substantial excess capacity
  among 504 slots and supports the broad initial-scarcity explanation.
- From-zero planning does **not universally imply one first range**. It depends
  on the prior, bound rate and planning settings. Here the bound settings confirm
  one range for all sixteen no-pilot W1 cases. Exact initial W2 range counts were
  not computed and cannot be inferred merely from its number of settings.
- The claim that every first range took 14–18 hours, leaving all 18 settings
  serial for 15–18 hours, is contradicted by the receipt. The three displayed
  first-range intervals are about 14.81 h (`s02077`), 17.88 h (`s01669`), and
  **2.88 h (`s14440`)**. The last uses times 1793754747.1085086 and
  1793765111.2876039 in receipt lines 141–142. Early fan-out therefore occurred
  for at least one example substantially before 14 hours.
- “W2 is unaffected” should be restricted to the reported initial capacity
  comparison and queued-work snapshot. These support less severe initial
  scarcity, not a guarantee against later idle retirement or other throughput
  limits. No independent W2 raw-state inspection was performed here.
- “Outside the current prefixes, which will become useful” is too categorical.
  The collector accounts shard CPU outside the current contiguous prefix as
  discarded (`p3_stage1b.py:980–998`). Filling holes can incorporate that work,
  but a K-hit crossing can leave later work unused. The collector also includes
  imported pilot CPU in useful time (`p3_stage1b.py:940–945`), so the sum is not
  automatically PBS CPU consumption for this array.
- No duplicate-execution or stranded-range defect follows from the idle
  mechanism. Conversely, aggregate zero-open/error counts alone do not prove
  that no work ever ran twice. Keep that conclusion at the level supported by
  the parent's archive audit and the still-pending shared-batch comparison.

These are reporting corrections, not evidence requiring cancellation of the
already submitted topup or alteration of the sampler.

## Reproducing the initial plan

Use the reviewed round-3 settings file, SHA-256
`fa7728290d33fb3f0baf30603d731c769de925739815d9a3b4efb77ddb97b9cd`, and runner
`92674ee8aa685b2a20bf5a689a3cbba836b195b8657ba8f79c5da161f315b765`.
Under Python 3.12.13 / NumPy 1.26.4 / SciPy 1.11.4, create a temporary run
directory with `queue/` and `workers/dead/`; for each W1 setting create an empty
`sets/<dir>/`, call `p3.plan(setting, setting_dir, run_dir, settings, owner)`,
and count `p3.ranges(setting, setting_dir)`. No journal or pilot payload is read
by this initial planner calculation. The receipt is `initial_plan.json`; `parent_planning_arithmetic.json` independently
recomputes and confirms all eighteen initial range counts from the bound inputs.
