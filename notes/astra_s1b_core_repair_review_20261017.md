# Astra: Stage 1b core repair review

Target: `d801012d2859a69ef076bfa529b4bfba1fbd658a`, including core repair
`d6d1edd`; reviewed against the preceding `e442f59` state.

**Recommendation: retain the W1 hold for one remaining core lock race.** The
earlier orphan-publication and collector counterexamples are repaired. The
new death-based lock correctly preserves an old live owner and checks the
unlock token, but concurrent stale-owner recovery can still steal a live
successor's lock. Scheduler and campaign-ledger findings belong to the separate
review; this memo does not reopen the scientific design or cap contract.

## Remaining blocker: a stale observation can reclaim a successor's lock

In `analysis/fable/calibration/v2_dev/p3_stage1b.py:191–196`, a contender reads
`lock/owner.json`, establishes that this owner is dead, then renames whatever
directory currently occupies `lock`. The rename does not bind reclamation to
the observed ownership generation. Its destination uses the **contender's**
token, so two contenders can each rename a different generation successfully.

The reproducible fixture uses two actual threads calling the real `lock()`
function. The only concurrency hook controls when each thread returns from
`owner_dead`; that function still uses the actual same-host PID-death check.
The starting owner has a verified nonexistent PID. The observed sequence is:

1. A and B both read the dead ownership generation.
2. A removes that dead generation and acquires a new lock with A's live PID.
3. A retains its acquisition; no unlock occurs.
4. B acts on its earlier dead-owner observation, renames A's live lock, and
   acquires another lock.

Both acquisition calls return distinct tokens without any intervening release.
The retained `lock.broken.*` directories contain both the genuinely dead owner
and live owner A. A's subsequent `unlock()` correctly raises an ownership
error, but it cannot undo the overlapping critical sections. Because planning
and queue transitions rely on this lock, the repaired orphan reconciliation
can again run concurrently after a worker death. This is a recovery-path
failure under a permissible worker interleaving, not evidence that the saved
smoke suffered corruption.

**Finite repair:** make reclamation atomic with respect to the observed
ownership generation. A generation-keyed, retained reclaim tombstone or an
equivalent serialization mechanism can ensure that only one contender removes
that dead generation and later contenders cannot rename a successor. Merely
reading the token again before the rename leaves another check/use race.

**Acceptance:** retain the existing old-live-owner and foreign-unlock checks;
add the exact two-contender dead-owner interleaving. A must retain the lock
until it releases it, B must wait, and B must then acquire normally. Exercise
this with the production filesystem semantics used for the queue. No sampler,
proposal-budget or scientific-design change is required.

## Repairs accepted

The saved replay contains eight bounded cases. Its assertions deliberately
confirm the remaining race as well as the repaired behaviors; an all-passing
test log therefore does **not** mean W1 is ready.

| Replayed condition | Current behavior |
|---|---|
| Interruption after range marker, before queue ticket | Retry restores one ticket; a second retry adds none; replanning with its live claim preserves that claim and creates no duplicate ticket. |
| Live lock aged well beyond the former threshold | Contender waits and leaves the live token intact. |
| Unlock with another token | Refused; current owner remains intact. |
| Two short budget-complete shards hidden inside larger declared ranges | Collection fails with `complete by budget without covering its range`; no library is produced. |
| Malformed later shard after a valid first-K prefix | Collection fails on the later shard's binding instead of silently discarding it. |
| Hit records outside their committed batch range | Collection fails with the precise committed-range diagnostic. |
| Negative CPU accounting in an otherwise valid later shard | Collection fails the checkpoint type/domain check. |
| Valid early hit stop and a valid cancelled later shard | Collection succeeds and assembles exactly K records. |

The two live-lock checks share one case, and the two-contender failure is the
eighth case. All invalid collector cases retain an explicit invalid setting
row and error. These results close the earlier targeted planner and collector
findings; the remaining lock race is the narrower unresolved part of the
ownership requirement.

## Evidence and limits

Evidence is under `analysis/astra/s1b_core_repair_review/`:
`check_repairs.py`, `repair_checks.json`, and `repair_checks.log`.

- p3 SHA-256: `2708cb1134b201e9a18d36706c46cdf6ca2949d71ff9eff1ceca6804e7d1df95`.
- p2 SHA-256: `ebf752ce112452a4a72354aa8d1f0cc20307b1519c23381a4706f7a71e31d455`.
- Local command: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 /usr/bin/time -f 'elapsed_s=%e max_rss_kib=%M' python3 analysis/astra/s1b_core_repair_review/check_repairs.py`.
- Observed runtime: **0.84 seconds**, peak RSS **41,120 KiB**.

The harness loads the actual p3 module with the same narrow local p2 shim used
for the earlier audit: unmodified AST-extracted storage and `run_setting`
functions; an unmocked scientific sampler call raises immediately. Every
batch is synthetic. This establishes local control-flow and filesystem-race
evidence, not numerical-runtime qualification or a Kunanyi filesystem test.
The parent's native suite, source bindings and saved-smoke recollection are
separate evidence. This reviewer made no new real proposals or population
paths, bank reads, SSH/PBS calls, source implementation edits or commits.

17 October 2026, 00:36:16 AEDT (Australia/Hobart).
