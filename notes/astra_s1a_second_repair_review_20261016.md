# Stage 1a second repair review

Astra, 16 October 2026; Correspondence review 1719. Reviewed
`3fa81cb58b262684722332c35d2d3e3b48fe408a` and Correspondence 1714 against the
remaining findings in 1708. Two bounded
reviewers checked submission and collection; the parent checked the package,
saved smoke and bound preflight.

**One submission branch still needs repair before dispatch.** The previous
collector and dependency findings are closed. The new branch that classifies
an empty query after a failed qsub as a definite rejection still permits a
duplicate allocation. Removing that automatic inference is sufficient; the
existing unresolved-state and verified-operator paths provide the remedy.

## Remaining dispatch finding

At `s1a_submit.sh:66`, a failed/no-ID qsub followed by a successful empty
name query writes `rejected ... absent-after-failure`. Resume may then submit
the same job again. A delayed or failed reply can arrive after an accepted
job has completed and left retained history. Waiting ten seconds after the
reply does not establish how long ago acceptance occurred or guarantee that
the history remains available.

The [submission fixture](../analysis/astra/s1a_submit_second_repair_review/audit.json)
accepts the fourth node, retains it in the allocation ledger, and removes its
completed history before returning the failed reply. The empty confirmation
is therefore a correct query result, not an injected query error. Resume
exits zero with **46 node jobs for 45 names, one collector and an allocation
bound of 1,013.445 CPU-hours**. This is a simulated scheduler lifecycle; no
claim is made that this event occurred on Kunanyi.

**Exact remedy:** delete the `n == 0` automatic-rejection branch and let it
reach the existing `uncertain` entry and stop. Keep positive one-job
reconciliation. A later `rejected` entry requires affirmative evidence of
non-acceptance; the existing operator receipt is sufficient. Update the
definite-rejection fixtures to supply that evidence before retry, and add the
delayed-reply/history-expiry fixture. It must make no replacement submission
while the outcome remains unknown. This needs no new service or Barry decision.

The [submission memo](astra_s1a_submit_second_repair_review_20261016.md) closes
the other branches: all 15 supplied scenarios pass, prior unresolved requests
now stop on absent history, unknown/query-error job states prevent collector
submission, and all ten supported live states retain their dependencies.

## Repairs accepted

The [collector review](astra_s1a_collector_second_repair_review_20261016.md)
closes the negative-field, per-setting exception and worker-provenance
findings. Its 34 canonical and 24 targeted checks pass. Missing worker
metadata is now explicit and separate from data completion; contradictory
metadata fails. Interrupted rows carry labelled sensitivity intervals and
no formal interval. The completed cap/hit formulas remain unchanged.

Two minor diagnostic limitations remain in malformed/incomplete fixtures:
a rejected checkpoint index can replace the planned row ID, and excessive
batch counts in running/failed states can pass as incomplete. Neither
produces a complete-run or formal-interval claim in those fixtures. They are
recorded for later diagnostic cleanup and do not add a dispatch gate or reopen
the accepted recovery algorithm.

The [package receipts](../analysis/astra/s1a_second_package_review/checks.json)
verify all 1,080 setting objects unchanged. Only the runner hash and report
text changed in settings. Metric, helper, imported bank source and throughput
bytes are unchanged, as are the sampling, recovery and preflight functions.
The staged tar
`ad260115a5dd0a9ad5fdb96639801942c6dc3debadbf643b90ea0ac404508897`
(522,240 bytes) matches all eight listed checkout files.

The existing smoke was recollected with the new validator, not rerun under
the new runner. Its original settings/runner bindings are preserved. All
1,080 saved counters and hit journals still match the original smoke: 38 hits
from 108 million proposals. Collection and provenance are complete with no
missing workers. The real preflight passes the planned shape at **991.445
CPU-hours**, including the corrected 0.445 prior allocation, and refuses the
three documented budget/shape/deadline violations.

## Next handoff and limits

Fable is next for the single submission-branch change, its focused fixture and
updated stage checksum. If only the submitter changes, no scientific settings,
runner rebind, population simulation or full smoke rerun is needed. Astra then
checks that finite change. Barry's Jumpbox window is needed after the check
passes; no new scientific or resource decision is pending.

The two canonical fixture passes (collector audit and parent preflight) used
320,000 proposals and 26,548 paths from already checked small streams. New
collector cases used synthetic batches; submission tests used scheduler stubs.
No full pilot, bank scan/build, model fit, empirical test, Kunanyi connection
or actual PBS action occurred. Live scheduler compatibility remains a dispatch
check. The 1,000 CPU-hour ceiling and no-fit stop remain unchanged; Stage 1b/c
are uncommissioned.

16 October 2026, 14:11:40 AEDT (Australia/Hobart).
