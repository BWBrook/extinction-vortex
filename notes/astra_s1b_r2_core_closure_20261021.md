# Stage 1b round-2 core repair re-check

**Recommendation: hold for one finite liveness repair.** The five original
failure sequences are repaired on `83a6b406681d0c2aec788f8a5f1cb64e124865e4`.
A bounded follow-up finds that an ambiguous lock acquisition followed by an
eight-second owner-read outage can still strand a live worker on its own lock
until its deadline. Mutual exclusion remains intact; no production corruption
is alleged. The remaining failure concerns recovery and allocated time.

Reviewed `b34b5e1..HEAD`, design §9e and the NOTE repair section, against the
original `analysis/astra/s1b_r2_core_review` counterexamples. This review owns
worker locking, recovery and node-process identity. The parent and other
reviewers own native numerical preflight, smoke D/r2dev5, staging, dispatch,
accounting and scientific interpretation.

## Original failures closed

| Earlier finding | Independent result on final source |
| --- | --- |
| Reused node identity lets an old certificate steal a live lock | Actual node script invoked twice with the same PBS job ID creates distinct owner nonces and exact host/PID certificates. The live successor retains its lock. Copying the old PID into a certificate bearing the successor's name is also rejected. |
| One failed release leaves the live worker waiting on itself | Actual worker dispatch exits 75. Actual node script certifies and restarts it; the successor reaches COMPLETE with no remaining claim or lock. This passes both when the release rename did not happen and when it happened but reported `ESTALE`. |
| Six busy settings hide a healthy seventh | The original six-settings × 28-tickets fixture reaches the healthy setting on its first call, after 30.28 logical seconds with default claim patience. |
| Recovery scan exceeds deadline and walltime margin | Original 392-claim fixture, with the required JSON certificate, stops at 60 logical seconds after 12 waits. No wait starts after the deadline and all 392 blocked claims remain recoverable. |
| PBS timeout exceptions bypass throttling | Four calls produce one query, including timeout failures. A 1.5-second remaining budget clips the timeout to 1.5 seconds. The successful-query control also remains cached. |

Additional passing controls cover ordinary COMPLETE, an acquisition rename
that succeeded but reported `ESTALE` with readable ownership, a two-second
claim deadline, and committing/requeuing a censored checkpoint at the sampling
deadline. These are ten core cases and three node integration cases.

## Remaining MAJOR: ambiguous acquisition loses its token on a read outage

`analysis/fable/calibration/v2_dev/p3_stage1b.py:269–278` maps every publication
rename error to `False`. The new token check at lines 314–316 repairs a lost
rename reply **if the owner record becomes readable before this invocation
returns**. `_owner` instead returns `None` after exhausted read retries
(lines 262–266). At the claim patience limit, `lock` raises ordinary `LockBusy`
(lines 325–326), discarding its acquisition token. The worker handles that as
contention and remains alive (lines 651–656).

`uncertainty_checks.py` reproduces this sequence:

1. The first main-lock publication rename takes effect, then reports `ESTALE`.
2. Reads of that lock's `owner.json` report `ESTALE` for eight logical seconds.
   The normal six-attempt retry policy is unchanged; 24 reads fail before
   the first lock invocation exceeds the default five-second claim patience.
3. After the read outage has ended, later claim attempts create fresh tokens.
   They can now read the old lock, but correctly see its owning process as
   still alive. They no longer recognize the discarded original token.
4. The worker reaches its 30-second deadline and returns normally with busy
   events, zero transient-error events, one queued ticket, its own live lock,
   and no COMPLETE marker. The completed fixture time is approximately 30
   logical seconds. No further fault is injected after eight seconds.

This is a combined lost-rename-reply/read-outage case, not the original single
release failure and not an observed Kunanyi outage. It exercises the same NFS
failure class the repair targets. An affected setting remains unavailable to
all workers until this owner finally exits; ordinary worker retries cannot
heal it. The earlier single ambiguous-rename control passes, which isolates
the missing ownership proof after read recovery.

**Finite repair:** retain the distinction between known contention and a
publication that may have succeeded. If the original token cannot be verified
before returning, take the existing `OwnerUncertain`/exit-75 path (or preserve
and reconcile that exact ownership token before retrying). Do not classify
uncertain ownership as ordinary contention or recover by age.

**Acceptance:** replay this exact eight-second read-outage fixture. It must
either finish through verified token recovery or promptly exit 75, then finish
through the actual node restart and certificate path. Keep the ordinary
live-owner contention and single-rename controls passing. Unknown or foreign
live owners must still be waited on; never infer ownership from the owner name
alone or delete another holder's mutex. No broader stress
programme or new scientific decision is needed.

## Residual constraints that do not create an additional launch gate

- A single ambiguous publication of `lock.reclaim` can leave that mutex owned
  by the current process; after certified death, the actual reclaim path
  raises `LockStale`. This matches design §7b's explicit operator-recovery
  boundary. The fixture establishes conservative refusal, not a second lock
  holder or lost claim. Do not claim universal automatic NFS recovery.
- Deadlines bound acquisition/recovery loops and query timeouts; they are not
  hard real-time guarantees for filesystem calls or an in-progress batch.
  The two-second live-lock test exceeds its budget by 0.056 seconds because
  the final sleep is checked afterwards. This is immaterial to the 1800-second
  node margin. Commit work retains the separately declared bounded allowance.

## Reproducible evidence

All new artifacts are under `analysis/astra/s1b_r2_core_closure/`:

- `helpers.py`: original audit helper code, loading unchanged source via AST
  and forbidding unmocked numerical sampling.
- `core_checks.py`, `.json`, `.log`: original-sequence replays and controls;
  9.10 seconds elapsed, 30,840 KiB peak RSS.
- `node_checks.py`, `.json`, `.log`: actual node script, actual runner main
  dispatch and synthetic worker storage; 25.20 seconds, 30,892 KiB peak RSS.
- `uncertainty_checks.py`, `.json`, `.log`: two bounded uncertainty limits;
  3.61 seconds, 30,260 KiB peak RSS. Assertions establish the observed remaining
  failure; they do not certify readiness.

Commands, run from the repository root:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 /usr/bin/time -f 'elapsed_s=%e max_rss_kib=%M' python3 analysis/astra/s1b_r2_core_closure/core_checks.py > analysis/astra/s1b_r2_core_closure/core_checks.log 2>&1
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 /usr/bin/time -f 'elapsed_s=%e max_rss_kib=%M' python3 analysis/astra/s1b_r2_core_closure/node_checks.py > analysis/astra/s1b_r2_core_closure/node_checks.log 2>&1
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 /usr/bin/time -f 'elapsed_s=%e max_rss_kib=%M' python3 analysis/astra/s1b_r2_core_closure/uncertainty_checks.py > analysis/astra/s1b_r2_core_closure/uncertainty_checks.log 2>&1
```

The recovery scan models the normal live-owner timeout at the `held` context
boundary; other ownership tests use the actual lock functions. The node worker
uses actual CLI exception dispatch, `work` and storage with synthetic batches;
it skips numerical dependency imports and source-binding qualification, which
belong to the parent's native audit. No PBS operation, production-data mutation
or population simulation was performed. Only this memo and its audit directory
were written; no production-source change or commit was made.

| Source | SHA-256 |
| --- | --- |
| `p3_stage1b.py` | `841feff9df54c9ef2fc5f7cf973a49d27e3cd15be99304749ff9dda5db1d14f5` |
| `s1b_node.pbs` | `cafc0a4dae6b9490a522dda8991aadae34808d5ec8f3b43a9f41ec17d36193ec` |
| `p2_stage1a.py` | `ebf752ce112452a4a72354aa8d1f0cc20307b1519c23381a4706f7a71e31d455` |

Recorded: 2026-10-21 20:59 AEDT (Australia/Hobart).
