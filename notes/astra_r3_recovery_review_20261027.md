# Round-3 worker-recovery review

**Target:** repository `ce2f722`; runner
`c56d0af653f1d7ecd525cacc5b6a191d8a1cadf398b601fc4327f3f6da34983b`;
node wrapper `8fe102080e1433ef880f0d1f30f8ef5cd127881c46cde0ae44bf38a40e5729c6`.

**Recommendation: BLOCK round-3 dispatch.** The immutable per-setting execution
chain prevents a second logical writer in the cases reviewed, but the new exact
same-slot recovery index is not durable before ownership is created. A worker can
die after creating its execution and moving its hint but before publishing
`workers/held/<owner>`. If the successor's queue and claim listings omit that
hint, neither recovery path knows the exact range and the execution remains open.
This combines two separately tested conditions that the 41 fixtures do not
combine. Separately, the collector can consistently report a terminal library
and an unresolved execution record as `collection_ok: true`; that is not a
scientific-integrity failure once PBS proves every process ended, but final
recovery closure should test it explicitly.

## Scientific and computational target

The target output is the first 2,000 retained pairs for each setting in global
`(batch, proposal_in_batch)` order, under the frozen deterministic stream and
fixed proposal cap. Recovery is therefore scientifically adequate only if it
(1) never admits concurrent execution of one range, (2) eventually resolves
every required range after a certified worker death, and (3) makes an
authoritative collection prove both the ordered library and reconciled execution
state. Queue and claim entries are discovery hints observed through potentially
incomplete NFS directory listings. Immutable `r/` and `x/` records are the
authoritative ownership state; PBS/node certificates are the observation that a
process has ended; shard checkpoint and journal files are mutable products shared
by successive executions.

The review concerns availability, library integrity and execution/accounting
provenance. It does not validate the population model, statistical estimand,
empirical inference or production throughput.

## Findings

### BLOCKER — an uncovered pre-held crash window can strand a range

`take()` creates `x/<a>.<k>` and then settles the hint
(`p3_stage1b.py:639-643`). Only after `claim()` returns does `work()` publish the
ticket in `workers/held/<owner>` (`:830-840`). A process death anywhere in this
interval leaves an authoritative open execution and a claim hint, but no exact
per-owner recovery entry. `recover_predecessors()` can read only tickets in the
held file (`:752-768`); `recover_stale()` depends on listing `claimed/`
(`:682-706`).

The focused reproduction kills the predecessor immediately after the hint move,
publishes its exact death certificate, omits only the successor's queue and claim
listings, and starts the next generation in the same node slot. Observed result:

- the execution is open before and after the successor;
- `workers/held/<predecessor>` does not exist;
- `predecessor_recovered = 0`;
- the claim hint remains on disk but was not discovered.

The node wrapper does not supply an independent repair. After a zero-exit worker
sees only claims, it polls rather than launching another worker and retires after
the idle bound (`s1b_node.pbs:77-94`). This is the same liveness class as the
stranded range under runner `928265bd`, now shifted into a shorter transition.
No second writer was observed or implied: the failure is a required range left
under a certified-dead owner.

The existing transition fixture kills before/after `settle()` but recovers with
visible hints (`p3_stage1b.py:1591-1662`). The listing-omission successor fixture
kills mid-shard, after the held record exists (`:1663-1687`). Neither covers the
combined condition.

**Minimal repair.** Durably record a conservative held intent before creating an
execution, under the setting lock. The claim path should add the selected ticket
to the per-owner record before `take()` can create `x/<a>.<k>`, and clear it when
`take()` proves the ticket spent. An overinclusive held intent is safe because
successor recovery already checks the exact setting record and acts only when
the execution owner equals the predecessor. Preserve the current claim-hint scan
as a fallback.

**Required test.** Repeat both crash points—after execution creation before hint
settlement, and after settlement before `claim()` returns—with every queue and
claim listing omitted. The exact same-slot successor must end the predecessor's
execution and replan; a later worker must reproduce the serial library with zero
open executions and zero superseded writers.

### MINOR — final collection does not distinguish consistency from execution-record closure

The collector counts open executions (`p3_stage1b.py:943-951`) but does not make
them invalid. `collection_ok` depends only on caught errors (`:1003-1025`). A
realistic two-range fixture starts the later range under worker B, lets worker A
complete the earlier range and create `COMPLETE`, then collects after B is gone
without an end record. The collector produced:

```text
terminal = COMPLETE
library_records = 25
later_execution_still_open = true
summary_open_executions = 1
collection_ok = true
```

This does not falsify the assembled library: the open range follows the range
that supplied the K-hit prefix. It leaves resource accounting and
recovery-record closure unresolved. Because the final
collector runs only after every PBS array is `F`, an open record is not evidence
of an actual live writer. The current round-3 dispatch gate consumes historical
round-2 summaries, not future output from `c56d0af6`; it is not the final
acceptance gate for this runner.

**Minimal repair.** Preserve snapshot `collection_ok` semantics, but separate
structural consistency from authoritative recovery closure. Before final
collection, close open executions whose exact owners have death certificates and
replan nonterminal settings; alternatively require a summary field such as
`recovery_complete = (open_executions == 0)` at the final acceptance gate and
resolve every reported row. Do not discard or rerun an otherwise verified
terminal library merely because an after-prefix execution end record is missing.
`claims_left` is only diagnostic because it itself uses a directory listing.

**Required test.** Retain the two-range terminal/open fixture and require the
final recovery step to close the certified-dead execution, or require the final
acceptance gate to report unresolved recovery rather than scientific invalidity.
Also check a normal terminal row with all execution records ended.

## Delayed post-mortem writes

The death certificate proves that the process was reaped; it does not, by
itself, bind mutable shard files to an execution generation. Successive
executions reuse `sh<a>.json` and `sh<a>_hits.jsonl`
(`p3_stage1b.py:784-787`). `run_setting()` appends and fsyncs journal data before
atomically replacing the checkpoint (`p2_stage1a.py:270-313`). A hypothetical
NFS write or rename initiated by the predecessor but observed after the successor
begins is therefore outside the process-level single-writer proof.

Two deterministic delayed-write simulations were fail-closed:

- an extra post-terminal journal record was rejected as `journal length differs
  from its checkpoint`;
- a coherent older zero checkpoint/journal pair under an extant `COMPLETE`
  marker was rejected as `COMPLETE marker without a verified K-hit prefix`.

Together with deterministic batch streams, this supports a fail-closed outcome:
the tested mutations caused loss of acceptance, not silent corruption of the
K-prefix. This was not a real NFS post-reap reproduction, so it neither proves
nor disproves that the filesystem can deliver the hypothesised delayed operation.
There is no discriminating failure that justifies making execution-generation
checkpoint binding or unique per-execution shard files a dispatch condition.
Those become serious alternatives only if a targeted delayed-write fixture makes
the current collector silently accept a wrong prefix or accounting state.

## Evidence and limits

Reproduction:

```bash
~/.local/bin/uv run --offline --python 3.12 \
  --with numpy==1.26.4 --with scipy==1.11.4 \
  python analysis/astra/r3_recovery_review_20261027/reproduce_recovery_gaps.py
```

The script and captured JSON are in
`analysis/astra/r3_recovery_review_20261027/`. It uses the actual candidate
worker, collector and checkpoint code with tiny deterministic batch and listing
stubs. The full 41-fixture baseline and saved smoke/archive replay were assigned
to the parent review and were not duplicated here. I made no production, PBS,
board or source-runner changes.

The ownership design is materially stronger than the round-2 runner: immutable
execution records and exact death evidence address the observed second-writer
defect. The review found no path by which the tested listing omissions admit a
second logical writer. The package is nevertheless not end-to-end complete until
the held intent precedes ownership creation. Explicitly closing or gating
unresolved execution records is a provenance improvement, not a second
scientific-integrity blocker.

## Decision and residual risk

Repair the pre-held transition before dispatch, add the combined transition test,
then rerun the native fixture suite and the short omission smoke. If those pass
with zero unresolved executions, zero claims and byte-identical libraries, this
review would approve the recovery package. The supported claim should remain “no
second live process writer, with strict fail-closed collection”; do not broaden
it to a claim about NFS operations after process death without a discriminating
test.

A Sol Max audit is not justified for this bounded recovery decision. The blocker
and its minimal fix are directly testable, the terminal/open case does not alter
the verified library, and both delayed-write mutations tested here fail closed.
