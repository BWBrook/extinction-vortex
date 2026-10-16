# Stage 1b lock and ledger closure

Reviewed `ca94676a0a06cf895637fb25d5dd291f5f65cd50` in response to Barry's
17 October request. WSL and the canonical Mac mini were clean at this commit
when the review began.

**The lock and reservation blockers are closed. The repaired executable is
cleared for W1, subject to the already-running regression smoke completing
cleanly and the usual verification of this exact package on Kunanyi.** The
smoke had eight active workers, empty worker logs and no completion report
at the [00:53:19 AEDT check](../analysis/astra/s1b_closure_review/smoke_snapshot.json). That is pending
evidence, not a failed test or another requested code repair. No further
scientific decision or additional code-review round is needed if it passes
the checks below without changing the package.

## Lock recovery

The independent replay uses the same deterministic, event-controlled
interleaving against old and new lock functions, real threads and filesystem
operations, and the actual same-host PID-death check:

| Source | Result |
|---|---|
| Previous `ced47a8` / runner `2708cb11...` | Two simultaneous holders; the first holder's unlock fails. |
| Current `ca94676` / runner `4886d8e8...` | One holder; the stale contender cannot reclaim it; after release the successor acquires and releases normally. |

The new reclaim mutex serializes reclamation and protects the generation
re-check. A dead reclaimer raises `LockStale` and preserves both owner files.
The queue fixture keeps the stalled setting's ticket and serves a healthy
setting; stale recovery preserves the stalled claim and reports the condition.
An evidence-preserving operator recovery in a quiescent fixture restores
normal acquisition. This is an explicit incomplete/operator-needed state,
not permission to remove locks on age alone.

Six bounded cases pass. See the [lock closure memo](astra_s1b_lock_closure_review_20261017.md)
and [evidence](../analysis/astra/s1b_lock_closure_review/lock_closure_checks.json).

## Reservation ledger

Both exact preceding failure sequences now fail safely in the real submitter
with the actual ledger/preflight functions and a stub scheduler:

- Reserve 392 CPU-hours, fail seeding before the journal, then retry with
  521 jobs: the enlarged request is refused before qsub; **zero allocation**
  is accepted by the stub.
- Reject an array, release it on evidence, resume under the same name, then
  request a fresh-directory array: the retry stays charged and the second
  array is refused. **One 199,688-hour reservation** remains active.

Same-name changes to CPU amount, wave or identity are refused. Identical
retries remain idempotent; ambiguous submissions retain their reservation.
The previous shape-change defect cannot reuse the old amount because shape
now participates in the array name, and prior reservations remain charged.
Chronological ledger replay reactivates a name when it is reserved again.
All eleven aggregate closure checks pass, and the eight supplied scheduler
scenarios pass under Bash 5.2.21 and source-built 4.2.46.

See the [ledger closure memo](astra_s1b_ledger_closure_review_20261017.md) and
[evidence](../analysis/astra/s1b_ledger_closure_review/closure_evidence.json).
No actual PBS allocation or expenditure occurred in these tests.

## Native package verification

The parent ran the **actual full-settings preflight on deep-server**, including
the native 22-case synthetic suite and all source/runtime binding checks.
It passed and recorded **199,688 CPU-hours** for the proposed
`520 * 8 * 48 + 8` shape in an audit-owned ledger. It did not touch the
production ledger or submit jobs.

All 21,816 setting rows and other settings fields are unchanged: restoring
only the previous runner hash reconstructs the previous settings SHA-256
exactly. The full metric and sampling dependencies are unchanged. All ten
manifest entries and all seven staged source files match the reviewed source.

| Artifact | SHA-256 |
|---|---|
| Runner | `4886d8e89abb09b5acbcb803e5d16e3d198d6a5c3cdad9e67327c9876931930b` |
| Full settings | `f811b7a82d57a311dd653cf55e9814fa774737d4344627b286a3b0a84f0368d3` |
| Smoke settings | `3c89151b764ce8b6b90b71d47242be6b5d9ccdc913f8c231b53cbf3755c16c5a` |
| Stage tar | `b4b1bfc16f104bd7eda48ce669421c86035b7b381cfd917988d2c015e01a894c` |
| Submitter | `2a982cf96023bc9169d72d2ba8264a7babcb230b1ae0f28ee5b9d906b20b1b46` |

[Package receipt](../analysis/astra/s1b_closure_review/package_check.json),
[native log](../analysis/astra/s1b_closure_review/native_preflight.log),
and [reproduction script](../analysis/astra/s1b_closure_review/package_check.py).
The native audit took 15.7 seconds. No new population paths were generated.

## Launch handoff

Fable owns completion of the existing `smoke_deep3` run and dispatch. Before
launch, record a clean collection with the expected four COMPLETE and two
CAPPED settings, no errors or incomplete settings, and all four complete
libraries byte-identical to the earlier deep-server smoke. Investigate a
mismatch; do not treat a still-running test as a pass.

Then verify the exact tar and manifest on Kunanyi and run the ordinary bound
preflight with the production campaign ledger. The proposed W1 allocation
remains 199,688 CPU-hours under the 200,000 ceiling. The current package's
preflight includes the new recovery fixtures; run its temporary lock fixtures
on the campaign filesystem when qualifying the NFS behavior. This does not
require another population smoke or a new scientific decision.

This review has not checked the live Kunanyi stage or production ledger.
Earlier completed smoke evidence remains as recorded in the preceding review;
it is not relabelled as a completed run of this newer package. The fixed
proposal-equivalent cap and the Stage 1c gate meaning are unchanged. Stage 1c
still has its separate executable settings/adapter check before fitting.

17 October 2026, 00:52:04 AEDT (Australia/Hobart).
