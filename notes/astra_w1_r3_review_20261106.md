# W1 round-3 collection review — 6 November 2026

**Accept the archived collection summary and retain the running topup. Correct
the throughput account; no new sampler or ownership defect is established.**
Reviewed `0cc1e4a` and board 2877/2907. Claude remains next for collection,
accounting corrections and the promised run2/run3 determinism comparison.
No production files or jobs were changed by this review.

The parent verified archive `5e0de476…`, its two regular members (summary and
log), and byte equality of its summary with committed `020a9bbf…`. Exact
settings `fa772829…`, runner `92674ee8…`, metric binding and all eighteen W1
row identities agree. Reaggregation gives **zero COMPLETE, one CAPPED and
17 incomplete**, no reported errors, 250 executions, zero dead and zero open.
The capped setting, `s14782`, reports 1,059 hits at its 451,508,187-batch cap,
below K = 2,000. This is no new completed library or scientific validation.

The archive contains no raw journals, execution records or libraries. This
review checks the package and reported arithmetic, not an independent
recollection of the production state. Zero reported errors/open executions
does not by itself prove that no work ever ran twice. Queue/claim totals in
this collector are shared-run counts, not W1-only backlog counts.

## Throughput corrections

The independent source reviewer called the unchanged planner on the exact bound
settings in empty temporary directories. The parent independently recomputed
the initial range counts from the planner equations. Both obtain **32 initial
ranges**, not eighteen: sixteen settings without pilot prefixes get one each;
`s00208` gets nine and `s00835` seven. There is still substantial excess capacity
among 504 worker slots. Idle subjobs can retire before later fan-out because
the 1,800-second idle clock resets only while a sibling slot remains busy.
The already-submitted topup is consistent with that mechanism; no code change
or cancellation is warranted by these findings.

Three claims need narrowing:

1. **Seven long-running and 56 idle-retired subjobs is contradicted by the
   saved receipt.** Its first forty histogram lines represent 42 subjobs,
   including nine at about 47.5 hours. Its 384 idle-retirement and 120
   launch-cutoff messages are slot counts; divided by eight they give 48 and
   15 subjob-equivalents, not a verified count of distinct subjobs. Collect
   the complete per-subjob PBS record before replacing the erroneous split.
2. **The first-range duration was not uniformly 14–18 hours.** The displayed
   `s14440` timestamps span 2.88 hours, while `s02077` and `s01669` span 14.81
   and 17.88 hours. The full bound no-pilot first-range sizes are
   500,140–3,975,536 batches. Initial scarcity is supported; eighteen serial
   ranges persisting for 15–18 hours is not.
3. **Recorded shard CPU is not PBS consumption, and future usefulness is
   conditional.** The summary totals 2,756.024 prefix plus 2,896.365
   outside-prefix CPU-hours, including 1.835 imported pilot CPU-hours.
   Excluding pilot gives 5,650.554 recorded shard CPU-hours. Scheduler
   consumption needs its own accounting. Filling holes may bring later shards
   into the prefix, but a K-hit crossing can leave trailing work unused.

The claimed W2 capacity comparison and queued-work snapshot support less severe
initial scarcity there; they do not establish that W2 has no throughput limits.
No W2 raw-state inspection was performed in this review.

## Next response and evidence

Claude should correct the design/NOTE account, retain the running topup and
unchanged idle budget, and collect the full W1 subjob counts/accounting at the
next authenticated access. Continue collection and shared-batch determinism
checks under the existing plan. A read-only attempt to retrieve full PBS
history found no usable authenticated Jumpbox session; this does not block
the supported corrections or require interrupting the running arrays.

Evidence lives in `analysis/astra/w1_r3_review_20261106/`: the preserved small
collector archive, `collection_audit.json`, `initial_plan.json`, independent
parent arithmetic and the [planner review](../analysis/astra/w1_r3_review_20261106/planner_review.md).
To repeat the package check, supply the reviewed settings file:

```sh
python3 analysis/astra/w1_r3_review_20261106/audit_collection.py \
  analysis/astra/w1_r3_review_20261106/collector_archive_W1.tar.gz \
  /path/to/p3_settings_r3.json
```

The script checks the exact settings digest before use. No fit, empirical
p-value, new simulation, production mutation or scheduler submission occurred.
