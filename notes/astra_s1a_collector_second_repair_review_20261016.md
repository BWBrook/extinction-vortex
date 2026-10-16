# Astra: Stage 1a second collector repair review

Reviewed `3fa81cb58b262684722332c35d2d3e3b48fe408a` against `2404fda`.
Runner SHA-256:
`ae065826ed9d6399217d1c3220e1ed4dfbe5f92b0a3cdd88ad3e50af1d96fd5d`.

**Accept the repairs to the previously reproduced collector failures.** No
material collector blocker remains in this focused review. Two minor reporting
and validation gaps remain below; neither warrants reopening the recovery
audit or holding otherwise valid pilot execution. This is a review
recommendation, not dispatch authority. The parent owns the input/preflight
and saved-smoke checks; the submission reviewer owns PBS handling.

## Closed findings and verified reporting

The canonical tiny suite passes all **34 checks**. Independently, 24 synthetic
collector fixtures support 24 passing assertions, including the original
counterexamples and the new reporting branches:

| Contract | Independent result |
|---|---|
| Negative overflow, rounding count and CPU time | Row invalid; collection fails; valid second row retained |
| String `batches_done` | Row invalid; planned IDs `[0, 1]` retained; later row complete |
| Unexpected per-setting exception | Isolated to that row; later setting and worker receipts still processed |
| Counter boolean, negative wall time, nonfinite CPU, invalid digest/status/stop/failure type | Rejected with current failure summary |
| Both worker receipts missing | `workers_missing=[0,1]`, `provenance_complete=false`; valid setting completion retained |
| Missing worker metadata, runtime `0`, empty host, negative/nonfinite RSS | Rejected; affected worker included in missing valid-provenance inventory |
| Running, failed and censored rows with a committed suffix | Sensitivity interval and explicit non-informative-censoring assumption; no formal interval fields |
| Complete budget and hit-stop rows | Expected Clopper–Pearson and negative-binomial formal interval fields respectively |
| Stale success summary | Replaced in every fixture |

The report rule now explicitly disclaims coverage conditional on the subset
of settings that completed. This review verifies the labels and code branches;
the earlier interval mathematics review remains the basis for the formula.

Function-level syntax-tree comparison finds changes only in `test`,
`check_setting` and `collect`. The recovery and sampler functions are unchanged.
The previous recovery findings stay closed; they were not independently
reaudited beyond the required canonical-suite replay.

## Minor follow-ups, not dispatch blockers

### MINOR: invalid checkpoint identity can replace its planned row ID

At `p2_stage1a.py:590`, copying the checkpoint into the row overwrites `index`
before the mismatch is diagnosed. In the two-setting fixture, changing only
checkpoint 0's index to 1 correctly causes a collection failure, but the
resulting row IDs are `[1,1]`, not `[0,1]`. The error text still identifies
setting 0 and its row is invalid; no incorrect result is accepted as complete.
The claim that every planned ID remains listed is therefore slightly too broad.

Preserve the planned identity fields as authoritative row keys and, when useful,
store conflicting values separately as recorded checkpoint identity. The same
provenance treatment would improve early schema failures: their
`recorded_status` is currently `invalid`, not the checkpoint's original
`complete`, because the early return at line 589 replaces it before collection.
These are diagnostic fidelity issues; the invalid input already fails closed.

### MINOR: batch upper bound is not checked for running or failed states

The new type check enforces nonnegative integer `batches_done`. The upper bound
is enforced for complete and censored states, but not globally
(`p2_stage1a.py:594–609`). Starting from a valid three-batch checkpoint and
setting `batches_done=4`, removing `stop`, and using `running` or `failed`
(with a string failure reason) yields `collection_ok=true`. The proposal
consistency check uses `min(nb * B, proposal_budget)`, so it cannot detect this.

Both rows remain incomplete, have only sensitivity intervals, and keep
`run_complete=false`; they do not create a false completion or formal coverage
claim. A global `batches_done <= st['batches']` check would close this small
corrupt-input gap. No broader schema redesign or new simulation is needed.

## Evidence and compute exposure

New evidence is in `analysis/astra/s1a_collector_second_repair_review/`:
`canonical_test_replay.log`, `collector_checks.py`, `collector_checks.json`,
`collector_checks.log`, `source_comparison.json` and `qualification.txt`.
The JSON preserves every fixture's status, errors, row IDs and first row,
including the two minor findings rather than hiding them behind the passing
assertion count.

Deep-server qualified at 14:03 AEDT: load 0.04/0.02/0.00, 123 GiB available
RAM and 4.1 TiB free on `/data`. Tests used `/usr/bin/python3` (3.12.3),
NumPy 1.26.4 and SciPy 1.11.4, with OMP/OpenBLAS/MKL/FlexiBLAS threads all set
to one, from `/data/fable/vortex/kunanyi_stage/run1/src`.

The canonical replay took **1.47 seconds**, peak RSS **87,428 KiB**. Its real
streams and call pattern are unchanged: **160,000 prior proposals and 13,274
population paths** for this pass. The parent's separate preflight adds another
canonical pass, to be accounted for in the combined exposure record. The
independent collector fixtures use synthetic batches only; they took **21.16
seconds**, peak RSS **84,380 KiB**, and add no population paths.

Canonical command on deep-server:

```sh
cd /data/fable/vortex/kunanyi_stage/run1/src
env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 FLEXIBLAS_NUM_THREADS=1 \
  /usr/bin/time -f 'elapsed_s=%e maxrss_kib=%M' /usr/bin/python3 \
  /data/fable/vortex/v2_dev/p2_stage1a.py test \
  /data/fable/vortex/v2_dev/p2/p2_metric.json
```

The synthetic script was copied to
`/data/codex/artifacts/project/s1a_collector_second_repair_review/collector_checks.py`
and invoked with the same runtime/thread limits and an audit-owned output
directory. Replaying it requires a new empty output directory.

No full smoke, pilot, bank build, new outer dataset, fit, empirical test or
scheduler command ran. Peer code, prior reviews and STATUS were not edited;
all new outputs are audit-owned and uncommitted.

16 October 2026, 14:08:11 AEDT (Australia/Hobart).
