# Stage 1b repair review: W1 remains on hold

Reviewed `d801012d2859a69ef076bfa529b4bfba1fbd658a` in response to Barry's
17 October request to check Fable's repairs and W1 launch readiness. WSL and
the canonical Mac mini were clean at that same commit when the review began.
This is a review of the executable changes since `e442f59`, not a new design
decision. Barry's Stage 1b/1c authorisation remains settled.

**Verdict: not ready.** Two repair areas remain: concurrent reclamation of a
dead owner's setting lock, and reservation accounting across retries. These
are reproduced execution failures. They do not reopen the scientific design.

## Verified progress

- All **21,816 setting rows, proposal budgets, streams and pilot prefixes are
  unchanged**. Removing the three new metadata fields and restoring the
  previous runner hash reconstructs the previous full settings hash exactly.
  The full metric hash is also unchanged. This carries forward the preceding
  review's exhaustive checks of the 7,200 outers and 14,400 evidence records.
- The new tar, its ten manifest entries and all seven staged source files
  match the reviewed checkout. The current runner is `2708cb11...`, full
  settings `0fc62239...`, and staged tar `286854e7...`.
- The **19 supplied runner fixtures pass in the native deep-server runtime**.
  The repaired collector reproduces the complete saved deep smoke report
  exactly on an audit-owned copy: four COMPLETE and two CAPPED, no errors or
  incomplete settings. No new population paths were generated for this review.
- Independent fault fixtures confirm that orphan range publication is now
  recovered exactly once, live claims are preserved, aged live owners are not
  displaced, and foreign unlocks are refused. All three previous collector
  counterexamples are rejected, as is negative CPU in a discarded shard on
  its own. A valid early hit-stop plus a later cancelled shard passes.
- The fetched Kunanyi re-smoke archive (`2ed7cc4f...`) and all six members
  match their extracted files. All four libraries match the first Kunanyi
  smoke byte for byte. All four repaired deep-server libraries match the
  first deep-server smoke. Across hosts, all 8,000 retained identities, paths
  and boundary flags agree; the previously recorded single one-ULP theta
  difference remains. This is an observed comparison, not a guarantee for
  other runs or rejected proposals.
- The **eight supplied submitter scenarios pass under Bash 5.2.21 and
  source-built 4.2.46**. Wave isolation is repaired. An ordinary second output
  directory cannot reset reservations, an ambiguous submission retains its
  reservation, and a same-shape retry after seed failure remains idempotent.
- The design now states the fixed **2,000 CPU-hour-equivalent proposal
  budget** explicitly. Measured per-setting CPU may exceed that equivalent;
  actual allocation ceilings are separate. The stopping law is unchanged.
  The four zero-hit pilot settings remain unresolved in the cap projection.

## P1: concurrent dead-owner recovery can steal the replacement lock

`p3_stage1b.py:191-196` reads an owner's death evidence and subsequently
renames the lock pathname. It does not ensure that this pathname still names
the dead owner's lock when reclamation occurs.

A deterministic two-thread replay of the actual `lock()` function shows:

1. A and B both read the same dead owner's record.
2. A reclaims it, acquires a new lock and does not release it.
3. B acts on its earlier observation, renames **A's live lock**, and acquires
   another lock.

Both calls return distinct holder tokens before either releases. The original
same-host PID death check remains active; the hook controls only scheduling.
A's subsequent unlock is correctly refused, but mutual exclusion was already
lost. With queue transitions protected by this lock, this remains a W1
blocker even though the single-reclaimer fixture and normal smoke pass.

Close with reclamation that cannot remove a successor generation, or fail
closed for operator recovery. Merely adding another unprotected token read
does not make check-and-rename atomic. The acceptance test is the exact
two-contender sequence above: at most one acquired holder until its release,
followed by successful acquisition by the other; retain the existing
live-owner, dead-owner and foreign-unlock checks.

## P1: reservation recovery still bypasses the ceiling

Two bounded shell replays use the actual submitter and actual `reserve()` /
`preflight()` implementations, with scheduler commands and scientific
preflight checks stubbed. They expose accounting faults, not actual PBS
allocations or observed overspending.

1. **Existing reservation names do not bind their amount.** Reserve one job
   (392 CPU-hours including the collector), then fail during seeding before
   the submission journal exists. A retry with 521 jobs keeps the same name,
   passes preflight and admits **200,072 CPU-hours** while the ledger still
   charges **392**, despite W1's 200,000 ceiling. The shell permits rewriting
   the run identity before a journal exists; `reserve()` accepts name equality
   without checking the reservation tuple.
2. **Release is permanent for a name, even after re-reservation.** After a
   genuinely rejected submission, an evidenced manual release and journal
   rejection allow a same-name retry. That retry writes a new 199,688-hour
   reservation, but the parser continues excluding the name because an older
   release exists. A fresh-directory submission is then admitted too:
   **399,376 CPU-hours of accepted stub allocations** against W1's 200,000
   ceiling.

The ordinary proposed first submission remains correctly priced at
`520 * 8 * 48 + 8 = 199,688` CPU-hours. These defects concern its recovery
contract. Close them before W1: bind/check the complete reservation identity
as soon as it is recorded, and interpret reserve/release events in order so
that a new reservation is charged. Preserve fail-closed handling of ambiguous
PBS submissions. Tests must cover both reproduced sequences and the passing
same-shape retry.

## Next handoff

Fable owns the two finite repair areas, regression fixtures, refreshed source
bindings and affected smoke evidence; Astra checks that delta before W1.
The approved W1 shape remains 520 eight-core jobs for 48 hours, plus its
collector. No new Barry scale or gate decision is needed. Stage 1c retains
its separate executable settings/adapter check before fitting.

## Evidence and limits

- [Saved-input and smoke audit](../analysis/astra/s1b_repair_review/raw_checks.json),
  [script](../analysis/astra/s1b_repair_review/raw_checks.py), and
  [native fixture log](../analysis/astra/s1b_repair_review/p3_fixtures.log).
- [Scheduler repair review](astra_s1b_scheduler_repair_review_20261017.md) and
  [reproduction evidence](../analysis/astra/s1b_scheduler_repair_review/repair_evidence.json).
- [Core repair review](astra_s1b_core_repair_review_20261017.md) and
  [fault-fixture evidence](../analysis/astra/s1b_core_repair_review/repair_checks.json).

The parent audit took 15.5 seconds on deep-server and read saved artifacts.
The Kunanyi archive contains summaries and libraries, not raw shard journals
or scheduler receipts; this review did not independently query the cluster
ledger or PBS accounting. The two completed smoke reservations (48 of the
60-hour smoke ceiling) and NFS cleanup are Fable's board 1798 evidence.
No bank scan, metric export, new population simulation, fit, PBS dispatch or
email was performed by Astra. The CPU-dispatch explanation for the one-ULP
difference remains unverified.

17 October 2026, 00:36:41 AEDT (Australia/Hobart).
