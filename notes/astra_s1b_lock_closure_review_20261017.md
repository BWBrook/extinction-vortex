# Astra: Stage 1b lock closure review

Target: `ca94676a0a06cf895637fb25d5dd291f5f65cd50`; finite delta from
`ced47a8`, covering the dead-owner reclamation race and the declared
dead-reclaimer behavior only.

**The prior lock blocker is closed. No launch blocker remains in this review's
scope.** The repaired code serializes reclamation, checks the observed token
under that mutex, and refuses automatic recovery of a dead reclaimer. Overall
W1 readiness also depends on the separately reviewed ledger, staging, input
bindings and native checks.

## Direct old/current replay

The independent fixture loads the actual lock and queue functions unchanged
from their source ASTs. It runs two real threads with event-controlled timing,
actual filesystem operations and the real same-host PID-death test. Both
contenders observe the same dead generation; B acts only after A has acquired.
No elapsed-time sleep is used to decide when B may act on that stale evidence.

| Source | Observed sequence and result |
|---|---|
| `ced47a8` | A acquires; B removes A's live lock and acquires; two simultaneous holders; A's unlock raises an ownership error. |
| `ca94676` | A acquires; B's stale reclamation is refused while A holds; A releases; B then acquires and releases normally; one holder throughout, no errors. |

The relevant repair is `p3_stage1b.py:198–216`: `_reclaim()` acquires the
separate `lock.reclaim` mutex, rereads the current lock token, and renames the
lock only when that token still equals the observed dead generation and its
owner is positively ended. Every automatic reclamation passes through this
serialization point. Its mutex is not itself automatically stolen, so the
previous race is not merely moved to another automatically reclaimed lock.

Fable's `p3/race_check.py` and its saved old/new receipt were read before this
replay. The independent harness replaces the fixture's sleep-based ordering
with explicit thread events and verifies the successful successor acquisition.

## Dead reclaimer: accepted operational limitation

When both the setting-lock owner and the reclaim-mutex owner are positively
ended, `lock()` raises `LockStale`. The two owner files remain byte-identical.
The following actual-function checks also pass:

- `claim()` logs the operator-needed state, retains the stalled ticket and
  successfully claims a second, healthy setting.
- `recover_stale()` logs the stalled setting and retains its finished-job
  claim; it does not silently requeue or remove it.
- In a quiescent fixture, moving the dead reclaim mutex to an evidence
  directory preserves its bytes. A normal subsequent acquisition then
  reclaims the positively dead setting lock and releases successfully.

This is a declared fail-closed state requiring operator recovery, not a
remaining mutual-exclusion defect or an automatically completed setting.
Recovery must establish owner death and stop contenders before changing the
reclaim mutex; the test had no active contenders during that operation.
No live campaign files or locks were altered. Source inspection also confirms
the normal post-shard `LockStale` handler preserves the claim and records
`lock_stale`; that branch was not separately executed in this bounded replay.

## Evidence and limits

Evidence: `analysis/astra/s1b_lock_closure_review/check_lock_closure.py`,
`lock_closure_checks.json` and `lock_closure_checks.log`.

- Old p3 SHA-256: `2708cb1134b201e9a18d36706c46cdf6ca2949d71ff9eff1ceca6804e7d1df95`.
- Current p3 SHA-256: `4886d8e89abb09b5acbcb803e5d16e3d198d6a5c3cdad9e67327c9876931930b`.
- Six cases passed; **0.41 seconds**, peak RSS **32,700 KiB**.
- Command: `/usr/bin/time -f 'elapsed_s=%e max_rss_kib=%M' python3 analysis/astra/s1b_lock_closure_review/check_lock_closure.py`.

This is a local WSL control-flow and filesystem replay, not a Kunanyi
filesystem test or numerical-runtime qualification. The finished-PBS fixture
uses a local executable returning a canned record; no scheduler is contacted.
No sampler or numerical modules were imported, and no proposals, population
paths, remote commands, peer-source changes or commits were made.

17 October 2026, 00:51:13 AEDT (Australia/Hobart).
