# Astra: Stage 1a runner and collector repair review

Reviewed `7f5be0b4e4a24916d50035eea1d470acef8df056`, runner SHA-256
`793e7a423dc5ad7356f6b871001e1b62b806ad1b0180f5e80d43748cf614966e`.
The parent reviews inputs/preflight, and parallel reviewers cover submission
and interval mathematics. This review does not authorize dispatch.

**Accept the original checkpoint/recovery repairs.** The zero checkpoint,
committed byte count and SHA-256, and atomic prefix replacement resolve the
previously reproduced duplication and destructive-recovery failures. The
collector repairs also reject malformed/duplicated records and replace stale
success summaries correctly. Two finite collection contracts remain incomplete;
repair these before describing the collector as fully validated. Neither is
an observed discrepancy in the saved smoke or a failure of the sampler law.

## Original recovery defects closed

The published tiny suite passes on deep-server, including retained-hit crashes
at four state writes, recovery interruption, short/missing/altered/orphan
journals and terminal-state mismatches. Independent tests add three transitions:

| Injected interruption | State left behind | Outcome on resume |
|---|---|---|
| Halfway through first hit append | Zero checkpoint; 163 uncommitted bytes | Exact reference counters and journal |
| Immediately after first nonzero checkpoint rename | Two committed hits | Exact reference counters and journal |
| Immediately after recovery's journal rename | Verified two-hit prefix | Exact reference counters and journal |

All use identifiable retained hits, not an empty-journal example. The new
runner rejects an orphan journal rather than silently appending to it, and
validates the committed prefix before accepting a terminal checkpoint. No
further change to the recovery algorithm is requested by this audit.

## Remaining collection findings

### MAJOR: incomplete checkpoint schema checks permit invalid summaries or drop later rows

`p2_stage1a.py:561–585` checks required keys and some relationships but not
integer/nonnegative counter types or finite nonnegative timing fields. In a
two-setting fixture built by the actual repaired `run_setting`, changing
`overflow=-7`, `rounding_excess=-9` and `cpu_seconds=-1` leaves both
`collection_ok` and `run_complete` true. The output can consequently contain a
negative CPU cost. This is acceptance of known-invalid accounting, not merely
an optional additional diagnostic.

Changing `batches_done` to the string `"3"` triggers a `TypeError` in the same
validation block. The exception is caught only outside the entire setting
loop (`collect():646–669`), so the current failure summary contains **zero
rows**, including no row for the valid second setting. The stale summary is
correctly replaced and the command fails, but the promised complete setting
inventory is lost.

**Minimal repair:** validate each checkpoint's field types and domains before
arithmetic: nonnegative integer counters, batch bounds, nonnegative integer
journal length, valid digest/status and finite nonnegative timings. Catch
per-setting validation errors locally, emit that setting as invalid and
continue to later settings and worker receipts. Preserve all planned row IDs.
Add the two exact fixtures above; neither requires population simulation.

### MINOR: worker provenance is not fully checked or inventoried

`collect():656–667` validates only present receipts' binding, ID range and
filename. In otherwise valid two-setting fixtures, each of these is accepted
with `collection_ok=true` and `run_complete=true`:

- both worker receipts absent, with no explicit missing-worker IDs;
- a receipt containing only worker ID, worker count and binding;
- a receipt claiming Python/NumPy/SciPy version `0`.

The prior review explicitly requested absent-worker accounting. Data completion
and worker metadata completion can remain separate: a worker can finish its
settings and be interrupted before its final receipt. Valid setting evidence
need not be discarded in that case. However, the summary should enumerate
missing workers and should not treat an out-of-contract runtime receipt as
valid provenance.

**Minimal repair:** compare expected and present worker IDs; report missing
IDs explicitly. Validate present receipts against the writer's schema,
including allowed runtime, nonempty host and finite nonnegative peak RSS.
Distinguish missing provenance from contradictory provenance and from complete
setting data. This is a reporting/integrity repair, not a sampler-law blocker.

An additional fixture confirms that a journal without its checkpoint is
currently reported merely as a missing setting. Flagging that orphan evidence
explicitly would make diagnosis clearer; the runner already rejects it and
the summary does not claim complete execution, so this is optional hardening.

## Verified collector improvements

The independent two-setting fixtures confirm that valid results collect
successfully; malformed JSON checkpoints remain visible as invalid rows while
later rows collect; malformed hit JSON and duplicate proposal IDs cause a
current failure summary; and an old success summary survives none of these
attempts. These are substantial repairs to the original collector. The
remaining type-error case above is narrower than the earlier general failure.

## Evidence, runtime and exposure

Evidence: `analysis/astra/s1a_runner_repair_review/` contains qualification,
canonical-test replay, `repair_checks.py`, its JSON receipts and timed log.
Deep-server qualified at 12:18 AEDT: load 0.04/0.50/0.69, 123 GiB available
RAM and 4.1 TiB free on `/data`. The verified runtime is `/usr/bin/python3`,
Python 3.12.3, NumPy 1.26.4 and SciPy 1.11.4; the suggested
`/data/fable/vortex/venv/bin/python` does not exist. All tests used one worker
with OMP/OpenBLAS/MKL/FlexiBLAS threads set to one.

The canonical suite took 1.33 seconds, peak RSS 87,352 KiB. One pass performs
160,000 real prior proposals and 13,274 paths in the already checked small
streams: three pairs of setting-9999 batches (3 × 3,280 paths) and one pair
for setting 775 (1,718 + 1,716). The parent's separate preflight includes one
more canonical pass, giving 320,000 proposals/26,548 paths across those two
audits. The new independent repair/collector fixtures use synthetic batches
only; they took 10.47 seconds, peak RSS 85,228 KiB.

No full smoke rerun, bank scan/build, new outer dataset, library build, model
fit, empirical test, scheduler command or Kunanyi connection ran. Peer code,
old reviews and STATUS were not edited. All new outputs are audit-owned.

16 October 2026, 12:24:43 AEDT (Australia/Hobart).
