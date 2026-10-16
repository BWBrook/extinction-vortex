# Stage 1a repair review

Astra, 16 October 2026. Reviewed `7f5be0b4e4a24916d50035eea1d470acef8df056`
and Correspondence 1703/1704 against the finite repair list in 1698. The
original review is [here](astra_s1a_prerun_review_20261016.md).

**Disposition: keep dispatch on hold for two remaining submission faults and
the unfinished collector accounting checks.**
The original checkpoint-recovery failures are repaired, and the package
preserves the accepted scientific inputs, streams and budgets. The submitter
now handles the ordinary failure fixtures, but still treats two kinds of
unknown scheduler state as permission to proceed. Both can violate the
existing allocation or collection contract. The required changes remain
small and specific; no new scientific design or resource decision is needed.

## Verified package and preflight

The [package receipts](../analysis/astra/s1a_package_repair_review/) establish:

- All 1,080 setting objects are identical to the prior reviewed package,
  including E, radii references, proposal budgets and worker assignment.
  The only changed top-level settings are the runner hash, `prefix_batches`
  and `report_rule`.
- Metric, helper, bank source and measured-throughput bytes are unchanged.
  The five sampling/acceptance functions are unchanged as Python syntax
  trees. This reuses the earlier metric/input audit explicitly; it does not
  claim a fresh full-bank hash or MAD computation.
- The new tar is
  `a4c3e4e484aed25f8e2206e70df757ca5ecd802a7f0a03634ab90aef58c2ab29`
  (512,000 bytes). All eight files match both its checksum manifest and the
  current checkout. Actual remote runner/settings/helper/metric/throughput
  and imported bank-source bindings also match.
- All counters and every retained-hit byte in the new saved `dry3` run
  match the original smoke for all 1,080 settings: 38 hits from 108 million
  proposals. Its new checkpoint journal lengths/hashes, 28 worker bindings
  and successful current collection receipt reconcile. This is a saved-data
  comparison, not another whole-smoke simulation.
- The real bound preflight passes 45 jobs × 8 CPUs × 9,900 seconds, including
  its bounded fixtures. The 4-hour allocation, wrong worker shape and short
  deadline each exit nonzero before fixtures. These four commands took about
  2.15 seconds in total on qualified deep-server with one numerical thread.

Nominal allocation remains **991.445 CPU-hours** including the recorded smoke
and collector. The command's `0.44` prior rounds the recorded smoke allocation
down by 0.005 CPU-hours; use `0.445` (or a conservative upward rounding) in the
final receipt. This tiny bookkeeping discrepancy does not threaten the ceiling.
The submission failures below can add an entire 22 CPU-hour node allocation.

## Required submission repairs

### 1. Empty retained history does not resolve a lost submission reply

The new journal records `request` and `uncertain`, but `submit()` does not use
that unresolved status to decide whether another qsub is safe. If
`qselect -x -N NAME` returns no row, the script immediately submits that name.
Completed-job history has finite retention. An accepted job whose reply was
lost can finish and disappear from that history before a later resume.

The bounded scheduler fixture reproduces this sequence: qsub accepts node 4
but its reply is lost; accepted jobs finish and the history entry is removed;
resume exits successfully after creating **46 node jobs for 45 unique job
names**, with one duplicated worker group. The allocation bound is then
**1,013.445 CPU-hours** using the exact prior allocation. Preflight still
counts only the requested 45 jobs.

For a key with an unresolved earlier request, an empty name query must leave
the submission unresolved and stop. Resume may reuse a positively reconciled
ID; otherwise require an explicit verified resolution before another qsub.
For a key with no prior request, an empty query can permit the first submission.
Preserve every accepted allocation in the journal. The regression fixture is
the lost-reply/expired-history case: it must issue no replacement job until
the ambiguity is resolved, and must never report an undercounted allocation.

### 2. A qstat failure does not establish that a job has finished

The dependency loop includes a node only when `qstat ID` exits zero. Any
query error removes it from the collector dependency, including a transport
or server error while the node is still live.

With one live-job query failing, the fixture produces 44 dependencies. With
all 45 queries failing, it submits the collector with none. Both submitter
calls exit successfully. The collector can therefore run and pack while
workers are still writing, defeating the repaired collection contract.

Require a successful, explicit state classification before omitting a node.
Unknown state or a query failure must stop collector submission and remain
resumable. Keep dependencies on every job not positively confirmed terminal;
only a confirmed terminal state permits omission. Test one and all query
failures: neither may submit an inadequately dependent collector. A verified
finished-job case should continue to pass.

These findings extend the already requested uncertain-submission and
complete-job-set checks. The normal dispatch, duplicate rejection, exclusive
lock, ordinary partial retry and positively reconciled lost-reply fixtures
now pass. The [submission review](astra_s1a_submit_repair_review_20261016.md)
contains the exact stubs, outputs and scheduler documentation.

## Recovery, collection and reporting

The [runner review](astra_s1a_runner_repair_review_20261016.md) records the
checkpoint and collection checks. The zero
checkpoint, committed byte/hash boundary and atomic prefix replacement close
the original orphan-duplication and destructive-recovery faults. The current
smoke has no evidence discrepancy. Additional interruptions during a torn first
append and immediately after state/journal replacement also recover exactly.
Malformed hit records and stale success summaries now fail correctly.

**Complete the collector's field validation and per-setting error handling.**
A fixture with `overflow=-7`, `rounding_excess=-9` and `cpu_seconds=-1` is
still reported as valid and complete. A parseable checkpoint with
`batches_done="3"` instead aborts the entire setting loop, omitting a valid
later setting from the current summary. Check field types and domains before
arithmetic, mark each bad setting invalid locally, and continue through every
planned ID. These are remaining parts of the original counter/inventory
contract, not evidence that the smoke's counters are wrong.

Also enumerate missing worker receipts and validate present runtime/host/RSS
metadata. Missing metadata can be reported separately from complete setting
data; contradictory metadata must not be accepted as valid provenance. The
review distinguishes this minor provenance qualification from the major
invalid-counter/per-row-error findings. No new recovery algorithm is needed.

The [reporting review](astra_s1a_report_repair_review_20261016.md) accepts the
prefix-conditioned cap/negative-binomial interval for the declared curtailed
design. Recovering the exact Kth suffix-hit position makes the hit-stop
formula valid even though the whole crossing batch is retained. The
implementation handles that position, cap counts and the all-success upper
endpoint correctly. There is no need to replace the completed-row method.

Interrupted-row Clopper–Pearson intervals explicitly assume non-informative
censoring. That assumption has not been established for runtime, numerical
failure or interruption. Keep such intervals as labelled sensitivity results,
or leave the formal interval absent for those rows. The fixed-cap/hit-stop
coverage statement must not be presented as conditional coverage among only
the settings that happened to complete. This is a reporting qualification,
not a reason to discard the pilot or introduce a new sampler.

## Next handoff

Fable owns the finite submission and collection repairs and regenerated
package, including the failing scheduler/accounting fixtures. Label the
interrupted-row interval assumption as sensitivity and use the recorded prior
allocation. Astra then checks those changed branches.
Keep the scientific settings, 1,000 CPU-hour ceiling, archived smoke and
no-fit report stop. Barry's Jumpbox window is needed only after this check
passes. Stage 1b/c and empirical inference remain uncommissioned.

No real PBS command, Kunanyi connection, full pilot, bank scan/build, fitted
model or empirical statistic was run in this review. Remote work comprised
saved-result reads and bounded unit/preflight checks on deep-server; shell
failure tests used local scheduler stubs. The two canonical fixture passes
(runner audit and parent preflight) used 320,000 proposals and 26,548 paths
across already checked small streams. Added failure fixtures used synthetic
batch producers; the reporting examples used exact probability arithmetic.

Correspondence review: 1708.

16 October 2026, 12:26:28 AEDT (Australia/Hobart).
