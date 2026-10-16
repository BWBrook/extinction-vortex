# Astra: Stage 1b Python execution review

Target: `e11b9b0171463c4b10e1dbce87b67e0949931db7`.
Reviewed `p3_stage1b.py`, its Stage 1a runner delta, and the Stage 1b design
and implementation notes. Source hashes:

- p3: `5cf875b26214bb07eac3f4b299b3ab80e89f6d08fa6f66e39e1003201203b342`.
- p2: `ebf752ce112452a4a72354aa8d1f0cc20307b1519c23381a4706f7a71e31d455`.

**Recommendation: HOLD W1 for the finite execution repairs below.** Stable
stream identities and the positive synthetic library checks pass, but a
planner interruption can strand work permanently, and the collector can
certify malformed shard coverage as a complete first-K library. The per-setting
cap also needs an explicit, accurate contract: it currently bounds proposals
at a nominal CPU conversion, not measured CPU consumption.

The malformed-state examples are injected fixtures, **not observed defects in
the saved smoke libraries**. The parent independently verifies the actual
package, inputs and saved smoke artifacts. Scheduler/wave/ceiling integration
and scientific design arithmetic are reviewed separately.

## 1. BLOCKER: planner publication is not recoverable; lock ownership can be lost

**Source:** `p3_stage1b.py:211–260`, especially range creation at 258 followed
by ticket creation at 259; `lock()`/`unlock()` at 143–159.

The planner creates a range marker before its queue ticket. A process killed
between those writes leaves a range with no checkpoint, queued ticket or
claim. On retry, the marker counts as in-flight work, advances the planning
cursor, and can consume every available slot; no code restores its ticket.

**Reproduction:** inject `KeyboardInterrupt` immediately before opening the
first queue ticket. The durable state is range `[0,5)`, empty queue. A normal
second `plan()` call leaves exactly the same state: `claim()` returns `None`,
and the setting is neither complete, capped nor failed. Releasing the old lock
does not recover the missing work. The hole permanently prevents completion.

There is a related ownership flaw. A lock is stolen solely because its
directory mtime exceeds 600 seconds. In a bounded fixture, owner A holds a
lock whose timestamp is aged to 601 seconds, owner B acquires a replacement,
then A's `unlock()` removes B's lock. Both acquisitions returned the same path;
unlock has no ownership token. This models a live owner paused or blocked for
longer than the age threshold. It does not establish that ordinary planning
takes ten minutes, but demonstrates that the lock ceases to provide mutual
exclusion under that permitted timing.

**Finite repair:** make range/ticket publication a recoverable transaction.
On recovery, reconcile each declared range with its queued/claimed/completed
state under an ownership-safe protocol; republish an unfinished orphan exactly
once without duplicating a live claim. A range marker alone must not count as
recoverable in-flight work. Do not infer owner death from elapsed time alone;
use verified ownership/death or a correct lease, and require the acquiring
owner's token when unlocking.

**Acceptance tests:** kill after range creation but before ticket publication,
then retry twice and obtain one usable ticket and the reference library.
Exercise a live owner older than the stale threshold and an old owner's late
unlock; neither may remove another owner's lock or create concurrent planners.

## 2. BLOCKER: the collector does not establish the promised verified first-K prefix

**Source:** `prefix():172–190`, `collect():397–429`, especially advancing
`end=b_` at 189 and the limited checks at 407–420.

The prefix calculation trusts a checkpoint's `complete` label and advances to
the range marker's end even when the checkpoint contains fewer completed
batches. The collector checks prefix binding and journal hash/count, but not
range coverage, committed proposal counts or record identities within the
committed range. It validates even less for shards outside the chosen prefix.

Three small fixtures reproduce distinct consequences:

| Fixture | Current result |
|---|---|
| Range markers `[0,10)` and `[10,20)`, each backed by a valid one-batch checkpoint with 2 and 3 hits, K = 5 | `COMPLETE`, `collection_ok=true`; library batches `[0,0,10,10,10]`, skipping uncomputed batches 1–9 |
| Range `[0,1)` with five journal records claiming batch 9,999 and an internally matching hash/count | `COMPLETE`, `collection_ok=true`, prefix end 1, Kth hit batch 9,999 |
| Valid completed prefix plus a later checkpoint with wrong binding, incomplete schema and `cpu_seconds=-3600` | `COMPLETE`, `collection_ok=true`, `discarded_cpu_h=-1`, no errors |

The first two fixtures violate the required stream-order/coverage guarantee.
They do not show that the current valid producer normally emits such states;
they show that the collector accepts internally hash-consistent but
out-of-contract metadata. A hash binds bytes to a checkpoint, not their
meaning. In the third case the later shard is excluded from the library but
still contributes invalid accounting, contradicting the claim that every
shard is validated.

**Finite repair:** validate every declared shard before using it for either
prefix construction or cost accounting. At minimum check:

- bound setting, first batch and declared range; integer/nonnegative counters;
  finite nonnegative CPU/wall time; known status and stop/failure fields;
- `0 <= batches_done <= range_length`, exact proposal count for those batches,
  counter invariants and the checkpoint/journal length/hash/count contract;
- full range coverage before advancing beyond a non-crossing complete shard;
  a short terminal range is permissible only where a valid first-K crossing
  has already been established within its actual committed batches;
- each hit's integer batch/proposal coordinates within those committed
  batches, monotone unique identities, finite parameter values and valid path
  schema/selection constraints;
- equivalent binding, schema, journal and accounting checks for discarded or
  incomplete shards, even when their records do not enter the library.

Invalid evidence must fail collection while retaining every setting's row and
an explicit invalid count. Keep incomplete-but-valid shards distinct from
corrupt shards; their committed accounting should remain visible. The three
exact counterexamples above should fail with current diagnostics, while valid
early hit stops, cancelled later shards and hole blocking should continue to
work. This can reuse the Stage 1a validation principles; no sampler redesign is
needed.

## 3. MAJOR: a 2,000-hour-equivalent proposal cap is not a measured CPU cap

**Source:** settings conversion at `p3_stage1b.py:88–98`; planner stop at
223–225; worker range budget at 349–354. The planner estimates CPU per batch
for sizing work, but does not stop on cumulative measured CPU hours.

This distinction is already visible in saved smoke results, not just injected
faults. With a bound nominal cap of 1.5 CPU-hours:

| Kunanyi smoke setting | Status | Worker CPU-hours | Excess over nominal |
|---|---|---:|---:|
| s01080 | CAPPED | 1.531901 | 2.13% |
| c00021 | CAPPED | 1.560466 | 4.03% |

Both settings have no imported pilot cost and zero discarded cost. A synthetic
clock fixture makes the distinction exact: two batches budgeted at one CPU-hour
each run at two hours each, consume four measured hours, and then become CAPPED
under a declared two-hour cap. No real CPU-intensive work is performed in that
fixture. This is not evidence of a campaign-ceiling breach; aggregate allocated
ceilings are a separate scheduler contract.

The design expressly says the 2,000-hour cap is converted to a proposal cap,
while the decision and later wording can be read as a hard CPU limit. These
must not be silently treated as equivalent.

**Finite resolution:** state and bind which cap Barry authorised. If it is the
fixed proposal cap corresponding to 2,000 hours at the pilot throughput, name
it that way and disclose that actual setting cost can exceed 2,000 hours. If a
hard measured CPU cap is required, enforce a shared cumulative budget across
pilot credit, completed/partial/in-flight work and retries, with declared
reservation/overrun semantics and cancellation before exceeding that contract.
The existing proposal cap alone is insufficient. This resolution is additional
to the unambiguous planner and collector blockers above.

## Passing checks, evidence and limits

Independent enumeration verifies all 21,600 primary IDs occur exactly once,
with the original 1,080 pilot IDs preserved. Source review confirms tag 2
remains the Stage 1a default and primary namespace; check libraries use tag 3.
The batch offset is applied to the sampler's actual batch ID, and the p2
recovery binding checks the offset. The published all-synthetic p3 suite's
nine checks pass, including varied shard plans/claim orders, killed-worker
recovery, refusal of altered journals/pilot prefixes and failure isolation.

Local Python lacks SciPy and pandas. For the bounded fault tests,
`check_core.py` loads the actual p3 module with a narrow p2 shim containing
verbatim AST-extracted `sha`, `atomic_json`, `journal_prefix`, `replace_bytes`
and `run_setting` functions. Unmocked `one_batch` raises an assertion. This
checks the real storage/coordination code without claiming numerical-runtime
qualification. The parent separately reports that all nine native fixtures
pass on qualified deep-server with the actual bound source/runtime.

Evidence: `analysis/astra/s1b_python_review/check_core.py`,
`core_checks.json`, `core_checks.log` and `published_synthetic_suite.log`.
The local command used Python 3.12.3 and single numerical-thread settings;
it took **1.38 seconds**, peak RSS **45,424 KiB**. All fixture path counters
are artificial. **No new real proposals or population paths**, bank reads,
fits, SSH, PBS commands, source implementation changes, commits or board posts
were made by this reviewer. The existing saved smoke collection was read only.

16 October 2026, 22:35:25 AEDT (Australia/Hobart).
