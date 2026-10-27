# Round-3 package review — 27 October 2026

**Recommendation: hold round-3 dispatch for two finite repairs.** The immutable
range/execution design closes the reproduced second-writer mechanism. The
candidate still has a crash window that can strand an owned range, and the
dispatchers can exceed the 7,000-CPU request cap. Neither finding invalidates
the accepted W1 libraries. Fable is next for repairs and focused replay; no new
scientific or resource decision is needed from Barry.

Reviewed repository `ce2f722`, runner
`c56d0af653f1d7ecd525cacc5b6a191d8a1cadf398b601fc4327f3f6da34983b`,
and stage `ddb014b0aad32fce2f4b4ed927c2d38aaf1253e1588235f2f7fd476a7f3ab84a`.
Three bounded reviews separated ownership invariants, worker recovery and
dispatch. The parent replayed the consequential counterexamples and integrated
them with archive and raw-smoke checks. This review changes no runner, PBS
script, scientific setting or production output.

## BLOCKER: ownership precedes the exact recovery record

`take()` creates the execution record and moves its queue hint before `work()`
writes `workers/held/<owner>`. A worker killed in that interval leaves an open
execution without the exact-name recovery entry. If the successor's queue and
claim listings omit its surviving hint, it recovers zero predecessors and exits
with the execution still open. The parent reproduced this on the actual
candidate. It is a liveness failure, with no second writer.

The existing tests cover interrupted ownership transitions with visible hints,
and omitted hints after the held record exists. They do not combine the two
conditions. Publish a conservative held intent before ownership can be created;
clear it after proving the hint spent. The existing exact owner check makes an
overinclusive intent harmless. Test deaths both immediately after execution
creation and after hint settlement with queue/claim listings omitted. Require
certified successor recovery, the serial library, and no open executions or
superseded writers.

Evidence and exact locations: [worker review](astra_r3_recovery_review_20261027.md),
[reproduction](../analysis/astra/r3_recovery_review_20261027/reproduce_recovery_gaps.py).

## BLOCKER: new requests can bypass capacity accounting

Two actual-shell paths bypass the intended combined cap:

- Both round-3 and topup dispatchers save the array size before submission.
  On restart, an existing size file bypasses all current capacity checks even
  if the array was never submitted. Other requests may have consumed capacity.
  A saved 874-subjob W2 size plus 72 external CPUs produces 7,065 requests.
- After submitting W1, round 3 sizes W2 solely from a new listing. If the newly
  accepted W1 array is absent from that listing, its known requests are omitted.
  W1's 63 subjobs plus W2's 874 and both collectors produce 7,498 requests.

Before any genuinely new submission, recheck that its saved shape fits current
capacity. Identify an accepted/resumed array from the submitter's bound journal;
the mere existence of a size file or an initialized journal is insufficient.
Account explicitly for accepted arrays/collectors that are not yet visible,
without double-counting those already in the listing. Replay both interrupted
sizing and delayed W1 visibility at the default 7,000-CPU cap, then the existing
normal/resume/topup rehearsal.

Evidence and measured requests: [dispatch review](astra_r3_dispatch_review_20261027.md),
[actual-shell harness](../analysis/astra/r3_dispatch_review_20261027/review_dispatch_contracts.py).
PBS and the submitter are bounded stubs; these are demonstrated shell accounting
paths, not observed Kunanyi oversubmissions.

## Accepted evidence

- **Native fixtures:** all 41 candidate checks pass locally. The supplied
  Kunanyi `/u` fixture/exclusive-link receipt is supporting evidence; this
  review did not independently log in to Kunanyi.
- **Ownership invariant:** seven additional injected stale-read/lost-reply
  cases fail closed without overlapping ranges, duplicate writers, skipped
  generations or overwritten execution ends. See the
  [state review](astra_r3_state_review_20261027.md).
- **Raw smoke replay:** recollecting a private copy on deep-server exactly
  reproduces both saved summaries except the output tag. W1 has four COMPLETE
  and two CAPPED settings; W2 has two CAPPED settings. All four libraries are
  byte-identical to the saved smoke and earlier reference. All execution ends
  are resolved, with no remaining queue or claim hints. This reuses saved raw
  shards; it does not rerun the population simulator or reproduce real NFS faults.
- **W1 final archive:** archive `849cd0ba…`, summary `8d702807…`; 4,822 unique
  regular members, all 4,820 library digests and 9,640,000 record counts match.
  The 4,798 previously audited libraries are unchanged. All 44,000 records in
  the 22 new libraries pass schema, order, bound, path and selection checks.
  No raw production journals or numerical regeneration were used.

Final W1 round 2 has **4,820 COMPLETE, nine CAPPED, 15 incomplete and three
invalid** settings. Across retained rounds 1–2 the full 14,544-setting inventory
is **14,515 COMPLETE, 11 CAPPED, 15 incomplete and three invalid**. Exactly 18
settings need round 3, all primary n = 30. The current sizing rule gives 63
eight-CPU subjobs (504 CPUs; 24,200 CPU-hours including its collector reservation).
All nine primary libraries are COMPLETE for 800/800 n = 0 outer datasets and
772/800 n = 30 outer datasets. These are availability counts, not fitted results.

The final W1 summary identity, binding, errors and selection agree exactly.
The summary gate and selection preserve scientific fields, streams, caps and
full denominators. A final independently verified W2 summary remains required;
the earlier W2-a snapshot cannot supply its final recovery inventory.

## Recovery choice and narrower qualifications

**Accept batch-zero recovery from each setting's bound pilot prefix.** Avoiding
a new partial-shard importer is a reasonable complexity/cost choice within the
existing authority. Retain all old bindings and outputs; recover every final
incomplete, invalid or FAILED setting, and compare committed overlap across
rounds. FAILED remains an execution outcome, not a scientific exclusion.

Correct the cost description: W2-a's incomplete rows account for 96,293.8
CPU-hours inside the verified prefix **plus** 72,689.0 outside it, or 168,982.8
in total. Batch-zero recovery forfeits both beyond the reused pilot. This
historical subtotal is about one day at 7,000 CPUs, but is not a round-3 forecast:
the final W2 inventory can shrink, topup b adds work, pilot reuse must be
subtracted, and invalid settings/losing duplicate executions are unaccounted.

Three qualifications do not independently block dispatch:

- `collection_ok` can be true for a verified COMPLETE library with an open
  execution in an unused later range. This does not make that library wrong.
  Final PBS completion can establish process quiescence independently; report
  and, where needed, close certified-dead records before claiming all executions
  resolved. Do not rerun a valid terminal library solely to erase this diagnostic.
  The current round-3 gate consumes old-runner round-2 summaries.
- The collector rejects **visible** off-chain records. It cannot certify their
  absence from an incomplete directory listing; that claim rests on the runner's
  construction invariant. The injected off-chain record had no demonstrated
  construction path in the candidate.
- The stage's internal checksums do not identify the reviewed artifact by
  themselves. Pin and verify the externally recorded tar digest at transfer/
  extraction, then use the internal manifest. The reviewed tar was reproduced
  by the dispatch review. A documented launch check can satisfy this condition.

Two simulated late shared-file mutations were rejected by strict collection.
Real delayed NFS writes after process death were not reproduced. This limits
the tested fault model; it is not evidence requiring a new shard format.

## Closure evidence

Return the repaired runner/stage hashes, the combined crash-plus-omission
replays, the capacity counterexamples and existing positive/resume rehearsal.
Re-run the candidate's native fixtures and bounded adversarial smoke after the
repair. Once both round-2 waves finish, verify final W2 and its recovery selection
before dispatch. Preserve the existing development/validation distinction;
there is no empirical inference or production-design freeze in this clearance.

Parent receipts and commands:
[review evidence](../analysis/astra/r3_package_review_20261027/README.md).
