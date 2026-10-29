# Round-3 closure review — 29 October 2026

**Hold dispatch for one remaining recovery repair. The capacity blocker is
closed, and final W2, stage identity and recovery selection are accepted.**
Both original crash cases now recover, but a failed held-intent publication
lets the retry create ownership without the recovery record. This is a
reproduced liveness defect, not evidence of a second writer or a bad library.
Fable is next for the finite repair below; Barry need not make another decision.

Reviewed clean matching WSL/mini `dbb1b850c83ee47bedf5de3f74a61c42a8b67a4b`,
runner `e261befa4cae08507c133af787f3f92ee283228c7dc5163076931767adf69894`
and stage `53603d427f7f5313fc5e100649ea186770d712b52601ef935cfc15611872b241`.
This is the response to board 2546 and the [27 October findings](astra_r3_package_review_20261027.md).
No production code or PBS jobs were changed. Three bounded reviewers checked
recovery, capacity, and stage/selection; the parent independently replayed the
consequential worker and capacity cases and audited the archived data.

## Remaining blocker: memory changes before the held record is published

`hold()` adds the ticket to its in-memory set before `atomic_json()` succeeds.
One failed rename leaves the file absent but the ticket present in memory.
The worker catches the error and retries through its normal park/adopt path.
Both the catch-path `hold()` and the next `intend()` skip publication because
the ticket is already in that set. The retry then creates an execution.

The new reproduction injects one `ESTALE` at `os.replace` inside the actual
atomic writer, after temporary-file write/fsync. It then simulates worker
death before or after hint settlement, leaves the setting lock held, writes
the exact death certificate and omits every successor listing. In both cases
there was only one publication attempt, the held file remains absent and the
successor recovers zero executions. Without the write failure, both crash
positions recover one predecessor and finish with the serial library, zero
open executions and zero superseded writers. The parent repeated all four cases.

**Repair:** publish a prospective held set, then update the in-memory set only
after success, for additions and removals. A failed or ambiguous publication
must require publication on retry. Require the first-write-failure test at both
crash positions and a permanent-write-failure control that creates no execution.
Details: [recovery memo](astra_r3_recovery_closure_20261029.md) and
[executable reproduction](../analysis/astra/r3_recovery_closure_20261029/check_recovery_closure.py).

## Capacity, stage and selection closure

The actual submitter, dispatchers and shared capacity helper pass the original
failures with bounded PBS/preflight stubs. Normal and resumed dispatch request
6,994 CPUs, with zero extra submissions on resume. The stale 874-subjob size
is recomputed under changed load. A wholly unlisted accepted W1 array stops
after its one submission; an unlisted collector stops before W2. Both resume
safely once visible. Query failures and a collector retry at 7,000 live CPUs
refuse the next submission. All 16 native submitter fixtures pass on Bash 5.3.9;
the supplied Bash 4.2 receipt was not independently rerun.

The helper assumes PBS lists an array's active subjobs consistently. An injected
parent-only or partial-subjob response defeats that assumption, but no evidence
establishes it as normal Kunanyi behaviour; the primary PBS documentation and
the tested scope are recorded in the [capacity memo](astra_r3_capacity_closure_20261029.md).
This is a bounded qualification, not another dispatch hold. One reporting
correction: a collector-only resume checks capacity after preflight, still
before submission; the early check applies to a new/rejected array.

Two isolated builds of `8be1b4e` reproduce stage `53603d42…`; all ten staged
files match the reviewed checkout. Actual-shell gates reject changed files,
a substituted tar and a self-consistent substituted manifest before install.
The exact final-summary gate selects **6,935 settings: 18 W1 and 6,917 W2**.
Actual `select` reproduces settings digest
`8c46667e4ab9e8a8bd03911eda81f9de072df25f1f40cfbb953c4108965cb3b9`,
with every scientific row unchanged. Wrong digests, mismatched errors and
changed identities fail; FAILED stays eligible. See the
[stage/selection memo](astra_r3_stage_inventory_closure_20261029.md).
The repaired runner will need **new stage and settings digests**; this existing
settings hash must not be carried forward after its runner binding changes.

## Independent archive and smoke evidence

Final W2 archive `c760f0c6…` and summary `beabe2d1…` pass the independent
streaming audit on `deep`: 357 unique regular members, all 355 library digests,
and 710,000 record counts. All 183 previously audited libraries are unchanged;
all 344,000 records in the 172 new libraries pass schema, order, cap, path and
selection checks. The final partition is **355 COMPLETE, 6,901 incomplete and
16 invalid**, with no CAPPED or FAILED rows. Identities, bindings, full inventory
and one-to-one error mapping agree. The 16 invalid rows remain in recovery.

W2 has 353 completed primary and two check libraries. Zero of its 800 primary
outer datasets has all nine populations complete; the maximum is five. These
are availability counts, not fitted validation results. The accepted W1 evidence
is retained without repeating its archive audit.

The incomplete W2 rows record 116,481.9 prefix plus 117,138.4 outside-prefix
CPU-hours, **233,620.3 in total**. This includes the reused pilot and excludes
invalid settings and losing duplicate execution. It is a historical subtotal,
not a forecast or an upper bound on total recovery cost.

All **42 native runner fixtures pass** locally. Independently recollecting a
private copy of the repaired runner's saved smoke reproduces every summary
field except the output tag, and all four libraries match both the saved smoke
and earlier reference. W1 has four COMPLETE and two CAPPED settings; W2 has two
CAPPED settings. Neither wave has open executions, queue hints or claim hints.
This replays archived shards, not the simulator or real NFS failures; it does
not cover the newly reproduced failed-publication path.

## Next response

Fable should return the held-set publication repair, both transient-failure
crash replays, the permanent-failure control, the native suite, and the newly
bound runner/stage/settings hashes. Preserve the capacity, archive and selection
clearances where their source and inputs are unchanged. The current stage stays
held; no new scientific choice, importer or shard format is needed.

Commands, runtime and receipts are in
[the parent evidence directory](../analysis/astra/r3_package_closure_20261029/README.md).
