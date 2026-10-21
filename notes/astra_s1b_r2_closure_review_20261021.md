# Stage 1b round-2 repair review

Reviewed `83a6b406681d0c2aec788f8a5f1cb64e124865e4`, following Barry's request
to check Claude's repairs before launch and Claude's handoff 2149. WSL and the
canonical Mac mini were clean and identical at the start. Three bounded
reviewers checked core recovery, scheduling and comparison/reporting; the
parent verified the package, native preflight and saved smoke, and replayed
the remaining fault.

**Hold for one remaining recovery repair. The original reported failure
cases now pass, and the dispatch, top-up and scientific restart contracts
are accepted.** A combined ambiguous lock publication and brief owner-read
outage still strands a live worker's own lock. This is a liveness failure;
no unsafe second holder or corrupted scientific output was observed.

## One repair before dispatch

**MAJOR — uncertain acquisition can outlive the acquisition token.**
In `p3_stage1b.py:271–328`, `_publish()` returns `False` after a rename error,
including an error reported after the rename took effect. `lock()` correctly
recognizes its own token if it can read the owner record. If those reads
remain unavailable beyond its five-second claim patience, however, it raises
`LockBusy`. Its local token is discarded. Later calls create another token
and treat the original lock, still owned by the same live process, as a
foreign live lock.

The bounded fixture injects exactly one rename that takes effect and then
reports `ESTALE`, followed by an eight-second logical outage reading that
lock's owner record. Ordinary reads recover. With a 30-second worker budget,
the worker nevertheless waits until the deadline, returns normally, and
leaves one queued ticket, no COMPLETE marker, and its own lock in place.
The parent replay reproduces this outcome. The shorter single-rename case
passes; this finding specifically requires the combined uncertainty and read
outage. It is a synthetic NFS fault sequence, not a claim that this precise
sequence has already occurred on Kunanyi.

At production walltimes, this can keep a setting blocked for the remainder
of its owner's allocation after the filesystem has recovered. Its normal
exit certificate eventually permits recovery; it does not restore the lost
allocation time. Other healthy settings can now proceed, thanks to the busy
queue repair.

Resolve uncertain acquisition before returning control as ordinary lock
contention: retain and reconcile the exact acquisition token, or terminate
through `OwnerUncertain` so the existing node certificate/restart path can
recover. Continue to respect known foreign live owners and generation-safe
mutual exclusion. Do not recover by deleting a lock merely because its owner
name matches.

Required regression: the exact eight-second read-outage fixture must end in
safe recovery and completion, rather than a normal deadline exit with the
worker's own lock. Retain the existing actual-node exit-75/certificate/restart
checks and successor-lock protections.

The [core closure review](astra_s1b_r2_core_closure_20261021.md) gives source
locations and all controls. Reproduce the remaining case with:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 analysis/astra/s1b_r2_core_closure/uncertainty_checks.py
```

[Parent replay receipt](../analysis/astra/s1b_r2_closure_review/uncertainty_parent_replay.json)
records the second execution without changing the production source.

## Repairs independently closed

- Unique invocation nonces and exact host/PID certificates prevent the
  demonstrated stale-certificate theft of a live lock. Actual-node checks
  exercise repeated PBS identities.
- Uncertain release, both before a rename takes effect and after an applied
  rename reports failure, exits 75 through the actual entry point. The node
  certifies and restarts the process; another worker recovers and completes.
- Six busy settings with 28 tickets each no longer hide the seventh healthy
  setting. Recovery scans honor the deadline; failed PBS queries are cached.
- A damaged stage stops before installation, ledger writes or submission.
  All 21 malformed-summary variants are refused. The exact gate also accepts
  the actual archived summary and selects the correct restart inventory.
- Interrupted dispatch resumes without duplicate accepted jobs or reservation
  releases. Changed existing round-2 settings are preserved and refused.
  Top-ups reject changed filenames or bytes and accept a correctly bound run.
- Concurrent collectors archive their own tagged summaries and logs. The
  final collection must still follow completion of every array in that wave;
  earlier collections are snapshots.

The [scheduler closure review](astra_s1b_r2_scheduler_closure_20261021.md)
contains the actual-shell/PBS-stub receipts, including all 12 supplied
submission checks rerun under Bash 5.2. Earlier Bash 4.2 receipts remain
historical evidence, not a new execution claim.

## Exact-package and saved-smoke evidence

- Runner: `841feff9df54c9ef2fc5f7cf973a49d27e3cd15be99304749ff9dda5db1d14f5`.
- Stage tar: `3eafd94d5b48f7b49409674f2d1cb1006bb4971c1b14a1ae526e6ec1f1eaaa8f`.
  All eight staged sources match both this checkout and the smoke D source
  tree (`r2dev5`).
- Actual selection: **4,847 W1 plus 7,272 W2 settings**, all original row
  fields unchanged. Selected settings SHA-256:
  `fa403f91585d5fcae63e81d0024899a50b78f61b680bfa7b28c3f656d8e14814`.
- Native preflight on deep-server passes **all 35 fixtures**, with a
  115,208 CPU-hour reservation written only to an isolated audit ledger.
  No production reservation or PBS action occurred.
- Recollection of an isolated smoke D copy exactly reproduces both saved
  summaries: W1 four COMPLETE and two CAPPED; W2 two CAPPED; no pending claims
  or collection errors. All four libraries match `smoke_deep3` byte for byte.
- The final comparator replay exactly reproduces its saved receipt. A
  separate strict sparse audit checks journal hashes, record counts, order,
  unique identities and nonoverlapping coverage: **174,302 shared batches
  and 2,310 identical records**, with positive non-pilot coverage in five
  settings. The fourth COMPLETE library, s00772, is shared pilot input only.
- Saved smoke fault records contain five injected kills, 26 valid death
  certificates, three node-invocation nonces, three successful node wrappers
  and the reclaimed foreign-host ghost lock.

[Parent scripts and receipts](../analysis/astra/s1b_r2_closure_review/) preserve
these checks. They audit saved outputs; no fresh population simulation or
serial numerical recomputation was performed. No live Kunanyi filesystem
qualification was performed in this review. The earlier full round-1 archive
audit remains applicable; its inputs were not changed by these repairs.

## Follow-ups that do not block launch

The sparse comparator now handles production-scale batch intervals and
rejects missing inputs, bad hashes and reported differences. It still
silently overwrites duplicate hit identities and double-counts repeated
requested directories. Reject these inputs, or run the existing strict
journal audit before the full production comparison. These are standalone
comparison changes and do not require altering the bound sampling runner.
The strict smoke audit above excludes these defects in the actual evidence.

The revised design closes the consequential cost-interpretation issues.
Some older NOTE shorthand and median-cost wording still need alignment with
that design. The [science closure review](astra_s1b_r2_science_closure_20261021.md)
preserves the 20-case diagnostic audit and precise editorial corrections.

Fable next: make the narrow uncertain-acquisition repair, return its passing
regression and updated bound package/preflight receipts. Keep the closed
scheduler and scientific findings closed; no redesign, proposal-cap change,
new resource decision or broad review restart is requested. After closure,
perform the ordinary exact-stage checks and preflight on Kunanyi, then
proceed with the already authorised W1 recovery and first W2 array. Stage 1c
retains its executable settings/adapter check before fitting.

21 October 2026, 20:59:55 AEDT (Australia/Hobart).
