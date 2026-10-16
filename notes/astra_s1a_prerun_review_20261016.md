# Stage 1a pre-dispatch review

Astra, 16 October 2026. Reviewed `e3870d47c132421ee625d53f8297c683dddffdfc`
and handoffs 1660/1687 against the agreed Stage 1a pilot in review 1657.
Three bounded reviewers covered the runner, PBS delivery and stopping rule;
the parent independently checked the input mappings and saved smoke results.

**Disposition: hold the large dispatch for execution repairs.** The scientific
settings, compact input export and completed smoke evidence are accepted.
The nominal 45-job allocation fits the 1,000 CPU-hour ceiling. Reproducible
submission/recovery defects can nevertheless exceed that allocation or lose
the correspondence between hit records and their checkpoint. These are
specific repair tasks for Fable, not a request to change the target or reduce
the scientific scope. No additional Barry decision or Jumpbox window is
needed to make and test the repairs on deep-server.

## 1. Verified evidence

The parent [input/smoke receipt](../analysis/astra/s1a_inputs_review/remote_checks.json)
verifies all 360 outer count sequences and full-precision radii against the
original Stage 0 files, all 720 noisy evidence records, all 360 normalized
query vectors (maximum discrepancy zero), and the exact 1,080-setting inventory.
The nine raw Stage 0 file hashes still match the earlier independent audit.
All 180 exported bank-shard hash entries match the frozen manifest; current
bank metadata, imported bank code, sampler, runner, metric and settings
bindings also match. The exported MAD values were checked for finiteness and
mask consistency, not independently recomputed from every bank row.

All 1,080 archived setting counters and all hit records agree between the
original deep-server dry run, Kunanyi smoke and repaired deep-server replay.
Each uses 100,000 proposals per setting. The totals are 108 million proposals,
37,731,547 simulated paths, 407,320 S/A-selected paths, 253,296 overflow
rejections and 38 hits, including two boundary hits. Hits by n=0/30/300 are
31/5/2 across 34 settings. There are no missing, failed or censored settings
in these saved smoke runs. This audit compared saved results; it did not
repeat the whole simulation or claim that the sparse hits establish precise
rare-event rates.

All 1,080 final proposal budgets reproduce from their recorded Kunanyi
throughputs and 3,300/825-second targets, rounded down to 20,000-proposal
batches. The assignment reproduces exactly: 360 workers, each with two
informative settings and one control, expected loads 7,424.853–7,424.975
CPU-seconds. The sum is **742.493 worker CPU-hours**, before overhead and any
early hit stops; the proposal cap is **3,504,293,600,000**. These are estimates
from a short smoke, not promised elapsed times.

The [PBS review](astra_s1a_pbs_review_20261016.md) verifies the staged tar
`ceaa29759b02915610967c96857092f724871731e13e9bf2fe1444d533ea9f19`, its eight
listed file hashes and their equality to the checkout. Nominal scheduling
arithmetic is sound: 45 × 8 × 2.75 = 990 CPU-hours, plus the collector and
completed smoke gives about **991.45 allocated CPU-hours**. The fixes below
are needed to keep retries inside that contract.

## 2. Required execution repairs

### A. Make submission recoverable without duplicate allocations

`s1a_submit.sh` writes its node-job journal only after every node and collector
submission succeeds. A safe qsub stub reproduces this failure:

- qsub fails on the fourth node; three jobs have already been accepted but
  no `node_jobs.txt` exists;
- rerunning submits all 45 nodes again and creates a collector depending
  only on those new jobs;
- 48 node jobs now reserve **1,056 CPU-hours**, with the first 24 worker IDs
  writing concurrently to the same result paths; the first three jobs are
  absent from the collector's dependency list.

A repeated successful invocation similarly submits 90 node jobs. This is
both a resource-budget failure and a data-integrity risk. Add a run identity
bound to settings/output path, exclusive submit/run ownership, and a durable
receipt immediately after each accepted qsub. Refuse a duplicate dispatch by
default; an explicit resume must reconcile known jobs and submit only missing
work, while binding the collector to the complete job set. If a submission
result is ambiguous, reconcile it before resubmitting. Check the worker/job
shape and cumulative allocated-hours ceiling before the first qsub.

The acceptance fixture is a failure after several accepted qsubs followed by
resume: every worker has one owner, all accepted jobs remain accounted for,
the collector covers them, and the total allocation remains within the cap.
No new scheduler platform is needed; a small persistent run journal suffices.

### B. Make hit-journal recovery atomic and fail closed on missing data

The [runner audit](astra_s1a_runner_review_20261016.md) reproduces three
related defects with tiny deterministic hit-bearing batches:

- A crash after the first hit write/fsync but before the first checkpoint
  leaves two orphan records. Restarting from no checkpoint appends them
  again: the runner returns `complete`, checkpoint hits=4, journal lines=6.
- A checkpoint claiming two committed hits with a short or missing journal
  resumes without rejecting the missing prefix. It returns `complete` with
  hits=4 but only three or two journal records.
- Recovery opens the existing journal with mode `w` to drop an uncommitted
  tail. Interruption immediately after that truncation destroys committed
  records. A subsequent restart again completes with an inconsistent journal.

An already-complete checkpoint also returns without checking its journal.
The current collector often catches a final line-count mismatch, but that
does not restore the lost records or make recovery reliable.

Create/validate an explicit initial checkpoint, reconcile orphan records
against its zero committed prefix, and verify the full committed prefix
before resuming or accepting a terminal checkpoint. Trim an extra tail by
writing and syncing a temporary journal followed by atomic replacement; do
not truncate the only committed copy in place. Reject missing/short/corrupt
prefixes with a diagnostic rather than claiming completion. Preserve the
same deterministic streams and proposal identities. If exact replay is used
for recovery, make that explicit and verify the reconstructed prefix.

Acceptance requires injected interruptions at the first commit and during
recovery, plus short/missing journals and terminal-state checks. Retained
records, identities and counters must equal the uninterrupted run. The
existing zero-hit resume fixture is insufficient by itself. The 60-second
checkpoint cadence is acceptable once these transitions are sound.

### C. Validate collection and dispatch preflight

The collector currently counts lines without validating their JSON content
or identity. Same-length malformed hit data and an unrelated stale worker
receipt can be accepted. If a corrupt checkpoint causes collection to abort,
the shell still packages an old `collect.json` with a valid archive checksum.
The exit code signals the failure, but the package contains a stale success
summary. A tar checksum proves archive identity, not current result validity.

Check exact setting/worker identities and bindings, parse each hit record,
check unique batch/proposal IDs and committed-batch bounds, and enforce the
counter/status invariants. Publish the current summary atomically. On
failure, package diagnostic evidence with an explicit current failure
receipt; do not leave a prior summary appearing to describe the latest
collection. Separate successful collection from complete execution: explicit
censored/missing results are valid pilot evidence and must remain visible.

The documented `p2_stage1a.py test METRIC` does **not** call the runtime/hash
check for the final settings. Add a real final-settings preflight before
qsub, including runtime/source/metric bindings and dispatch shape. This is a
small contract correction; the currently staged source and recorded smoke
runtimes do match.

## 3. The 2,000-hit stop is acceptable, with a declared reporting rule

The [stopping review](astra_s1a_stopping_review_20261016.md) supports this
engineering refinement. Keep the whole crossing batch, retain each setting
regardless of whether it reaches K, and distinguish hit stop, proposal-cap
stop, wall censoring, numerical failure and missing output. The underlying
accepted-path law is unchanged. No full smoke rerun is needed merely because
the stop is now explicit.

The reported O(1/2,000) bias pertains to an ideal inverse-binomial setting;
it is not a coverage guarantee for this batched, capped, timed procedure or
for a summary restricted to completed libraries. Treat full-stream H/N as
descriptive unless its uncertainty calculation respects the stopping design.

The smoke's first 100,000 proposals are reused and recomputed, not additional
independent exposure. They also informed the proposal budgets through measured
CPU time. For formal rate uncertainty, condition on that recorded prefix and
use the new post-prefix proposals/hits, with an interval valid for the actual
stopping rule. A conservative finite-look construction or a suitable
time-uniform interval suffices; a fixed-N interval selected only after a
hit stop is not justified by the small bias claim. Predeclare the report rule
before dispatch; it need not change the streams or sampler.

`cpu_hours_to_2000` is a rate-based projection. Actual `cpu_seconds` measures
time through the crossing batch, not the exact instant of the 2,000th hit.
The proposal index of that hit is recoverable from the retained IDs. Report
actual crossing-batch CPU/wall time separately from projections for unfinished
libraries. Zero hits give an upper retention bound and unresolved/lower-bounded
cost, not zero cost; preserve all 1,080 rows and complete-nine-population
availability. The existing approximate 3/N zero-hit upper bound is not
invalid merely because optional stopping is permitted.

The storage claim is a planning estimate: retaining the crossing batch gives
a strict maximum of K+B−1 = **21,999 records per setting** at B=20,000, not
exactly 2,000. Rare-hit rates make a large overshoot unlikely, but storage and
the collector should tolerate the actual declared maximum.

## 4. Close minor prior repairs and return a finite package

The Stage 0 report now rejects the wrong runner hash in a fresh negative
fixture; its other valid/invalid-input fixtures still pass. Both caribou
phrases now say shared monitoring programme and A11 is part of the Markdown
table. Those three prior findings are closed.

**Fable is next:** repair submission, checkpoint recovery and collection;
add the real preflight and the stopping-aware report contract; regenerate
the runner/settings/stage hashes; return the targeted failure/retry receipts.
Keep the scientific settings, 1,000-hour ceiling and archived smoke evidence.
Astra then checks that finite repair diff before dispatch. Barry should only
need the next Jumpbox window once the package passes that check. Stage 1b,
fitting, new validation and empirical inference remain outside this tranche.

No qsub, full pilot, bank scan/build, fit or empirical statistic was run by
Astra. The review used saved-result reads and bounded synthetic unit/failure
fixtures; their exact scope is recorded in the subsidiary receipts.

Correspondence review: 1698.

16 October 2026, 11:58 AEDT (Australia/Hobart).
