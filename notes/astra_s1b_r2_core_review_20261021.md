# Stage 1b round-2 runner and node recovery review

**Disposition: not cleared.** One reproduced mutual-exclusion blocker and four
recovery defects remain at `9a773c9e0fa7b2499d84540c68afe74165304029` (reviewed
against `979cd41`). The lock token/reclaimer protocol does not protect against
a death certificate attached to a reused worker identity.

Scope: runner locking, claim selection, stale-claim recovery, deadlines, PBS
query throttling and node death certificates. Accounting, scientific inference,
native numerical execution and package staging are covered by the other reviews.
No production sources, settings, accounting, scheduler state or production data
were changed. These checks used temporary local files and synthetic batches;
they did not submit jobs or run population simulations.

## Findings

### C1 — BLOCKER: a rerun can give a live worker an old death certificate

`analysis/fable/calibration/kunanyi/s1b_node.pbs:18–24` starts every invocation at
`k=0`, names workers `$PBS_JOBID.${i}r$k`, and retains death certificates under
that name. `p3_stage1b.py:213–214` treats the certificate as conclusive before
checking the current PID. Consequently, a subsequent invocation under the same
PBS job identity reuses the name of an already certified dead process.

`node_identity_check.py` invokes the **actual node script twice** with the same
synthetic `PBS_JOBID`. The first invocation leaves the expected certificate.
The second starts a live child that acquires an actual runner lock. A different
owner then acquires that lock through the actual reclaim path while the child
is still alive; its subsequent unlock fails the token check. Both worker names
are `same[0].fixture.0r0`. This is a mutual-exclusion failure, not merely delayed
recovery. The child is a bounded lock fixture, not the numerical worker.

This restart is relevant to PBS: the current upstream OpenPBS manual documents
rerunnable jobs as the default and array jobs as always rerunnable. Kunanyi's
live configuration was not queried in this review. The counterexample is
conditional on reinvocation with the same job identity and does not claim an
observed production rerun. [OpenPBS qsub manual](https://raw.githubusercontent.com/openpbs/openpbs/master/doc/man1/qsub.1B)

**Repair and acceptance:** make the node invocation identity unique, include it
in every worker identity/certificate, and preserve reliable extraction of the
PBS job ID. Rerun the same-job fixture with old certificates retained: the live
successor must remain unreclaimable, while the original dead owner remains
recoverable. Removing certificates on startup alone is insufficient because
old claims still require their evidence.

### C2 — MAJOR: one failed unlock strands a live worker on its own lock

`p3_stage1b.py:302–319` does not resolve a failed release before propagating an
`OSError`; `work:612–619` then parks/retries the iteration while the process stays
alive. The claim can already have been renamed when `held.__exit__` fails, so
the outer ticket variable is still `None` on that first failure.

`single_unlock_error_strands_live_owner` injects exactly one `ESTALE` on the
release rename after a successful claim. The worker subsequently adopts its
claim and completes the synthetic shard checkpoint, but cannot reacquire its
own unreleased lock to finish planning. Three actual lock attempts time out;
the setting has no `COMPLETE` marker, one claim remains, and the function returns
normally at the deadline. The fixture compresses `LOCK_PATIENCE` to five seconds
and parking/backoff to zero; lock acquisition, release, adoption and checkpoint
logic are the actual source. Default longer waits do not remove the deadlock.

**Repair and acceptance:** reconcile/retry the release using ownership proof,
or terminate the worker nonzero when release cannot be established, allowing
the node to certify its death and restart it. A one-off release failure must
recover and complete, or promptly produce that controlled restart; it must not
park a live process behind its own lock until walltime.

### C3 — MAJOR: the bounded claim scan repeatedly misses healthy settings

`claim:474–495` keeps the busy-setting set for only three passes and discards it
on each call. Six busy settings with 28 tickets each fill the successive
32-ticket frontiers. A healthy seventh setting is never examined. The repeated
calls begin with the same six settings, so random ordering within the frontier
does not provide progress.

`busy_frontier_starves_healthy_setting` exercises the actual claim/lock path
twice with the default five-second claim patience. Both calls raise `LockBusy`,
the healthy ticket remains queued, and no claim is acquired (60.6 logical
seconds). Moreover, each lock observation lasts less than the 300-second PBS
suspicion threshold, so these calls cannot establish remote-owner death.

**Repair and acceptance:** retain a bounded cooldown/cursor across calls or
advance through distinct settings with a deadline. Preserve the distinction
between an empty queue and temporarily unavailable tickets. With this fixture,
the healthy seventh setting must be claimed despite the six blocked settings.

### C4 — MAJOR: recovery can consume the entire walltime margin

`recover_stale:498–517` accepts no deadline and can wait five seconds separately
for every claimed ticket. `work:586–603` checks time only outside the whole
recovery/claim sequence. Claim scans, query timeouts, backoff and the five-second
minimum in `patience:542–543` likewise are not clipped to remaining time.

`recovery_scan_outlives_deadline_and_margin` constructs 392 ended-owner claims
across 14 settings and models each permitted live-owner lock timeout at the
`held` boundary. The actual `work` and `recover_stale` functions scan all 392:
1960 logical seconds despite a 60-second worker deadline. Of the waits, 380
start after the deadline; the scan exceeds even the additional 1800-second
node margin by 100 seconds. This is a bounded logical-clock test of control
flow, not a measured NFS timing result.

**Repair and acceptance:** propagate one absolute deadline through recovery,
claiming and liveness queries; check it before starting each wait and cap each
timeout/backoff to remaining time. Coalesce recovery work by setting where
appropriate. A large blocked recovery set must stop within the worker budget
while preserving claims for later recovery.

### C5 — MAJOR: PBS timeouts bypass the query throttle

`owner_dead:223–227` returns on an exception without caching the failed query.
Four successive calls whose `qstat` attempts time out therefore start at
logical offsets 0, 60, 120 and 180 seconds, all inside the promised 300-second
throttle interval. The cache stays empty. A successful `job_state = R` control
does throttle correctly (one query for four calls).

**Repair and acceptance:** cache the time of an unsuccessful/unknown query
without interpreting it as death, and cap its timeout to the caller's remaining
budget. The same owner must cause at most one attempted query within the
throttle interval even when PBS times out.

## Evidence and limits

Artifacts are in `analysis/astra/s1b_r2_core_review/`:

- `core_checks.py`, `core_checks.json`, `core_checks.log`: six cases, including
  normal completion and successful-query cache controls; 6.80 seconds elapsed,
  35,620 KiB peak RSS in the recorded run.
- `node_identity_check.py`, `node_identity_check.json`,
  `node_identity_check.log`: actual node-script identity reuse and live-lock
  reclaim; 0.49 seconds elapsed, 27,604 KiB peak RSS.

The Python fixtures load unchanged source functions/classes/constants via AST
to avoid importing the numerical runtime. Numerical sampling is forbidden and
replaced by an explicit synthetic batch. Source fingerprints are:

| Source | SHA-256 |
| --- | --- |
| `p2_stage1a.py` | `ebf752ce112452a4a72354aa8d1f0cc20307b1519c23381a4706f7a71e31d455` |
| `p3_stage1b.py` | `29ece4e3d29ceaedbbc43db203b31d9b82419c624c90b01238a94a72b7d31a76` |
| `s1b_node.pbs` | `f02bca1f76121c5245588b60762bbeae03a901d00186c3f84dfcb9144c1f5b6b` |

All fixture assertions pass because they assert both controls and reproduced
failure conditions. They are evidence against readiness, not a passing
production qualification. C1–C5 have finite acceptance checks above; this
review does not expand the scientific design or request further simulation.

Recorded: 2026-10-21 15:12 AEDT (Australia/Hobart).
