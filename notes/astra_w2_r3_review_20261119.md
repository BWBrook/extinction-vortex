# W2 first round-3 collection audit

**Accept the archived libraries from collector `876194`. Keep the current topups running and investigate worker recovery before final acceptance.** The 18 November collection spans 13:52–15:39 AEDT for the summary and ends at 15:43 with the archive. Workers from both W2 topups could advance while individual settings were being read. All counts below refer to that snapshot.

## What the archive establishes

An independent streaming read on deep matched the Kunanyi receipt for the 479,675,734-byte archive (`a6959a80…`) and summary (`fc376cd2…`). The embedded and standalone summaries match byte for byte. All 2,730 members are unique regular files with the expected names. The summary covers the exact 6,917 W2 settings selected from round 2 with the bound metric, settings and runner. Its row counts, CPU subtotals and execution totals reconcile. [Audit receipt](../analysis/astra/w2_r3_review_20261119/archive.json)

| Outcome | Settings | With a dead execution | Dead executions | Open executions |
|---|---:|---:|---:|---:|
| COMPLETE | 2,728 | 64 | 329 | 2 |
| CAPPED | 54 | 44 | 211 | 0 |
| Incomplete | 4,135 | 108 | 626 | 2,200 |
| Total | 6,917 | 216 | 1,166 | 2,202 |

There were zero FAILED settings and zero collection errors. Each of the 2,703 primary and 25 check libraries matches its declared hash and contains exactly 2,000 records. All **5,456,000 records** passed checks of schema, ordered batch/proposal identities, batch bounds, parameter support, initial abundance, trajectory length and first extinction-threshold crossing at the last census. Recomputing the three calibration features against the bound mask, scales, centre and radius confirmed every retained trajectory and every boundary flag. For 177 libraries the imported pilot prefix could also be checked in full, reproducing the bound digests for 14,244 records. [Audit script](../analysis/astra/w2_r3_review_20261119/audit_archive.py)

For each of the 64 COMPLETE settings with a dead execution, we regenerated four post-pilot batches using the bound sampler and a permitted runtime. Three were the first, middle and last distinct post-pilot hit-bearing batches in the retained library. A hash of the setting ID chose the fourth from the full post-pilot interval through the last retained batch. All **256 batches** agreed through the library cutoff, including all 192 hit records byte for byte and 64 empty batches. This probes reproducibility in the affected settings. Identifying which ranges had dead owners and testing all shared run2/run3 batches requires the raw journals. [Replay receipt](../analysis/astra/w2_r3_review_20261119/replay.json)

Combining the 2,728 new libraries with the 355 previously audited W2 libraries gives 3,083 COMPLETE out of 7,272 W2 settings. One of the 800 primary outer datasets, `null_low_s/1`, now has all nine populations. Stage 1c fitting and prospective validation remain separate work. [Earlier W2 audit](astra_r3_package_closure_20261029.md)

## Backlog and dead executions

Of the 4,135 incomplete settings, 401 had 1,500–1,999 prefix hits, 722 had 500–1,499, 562 had 1–499 and 2,450 had zero. **2,409 of the zero-hit settings had no pilot and had yet to record a round-3 execution.** Only seven of the zero-hit settings had an open execution. Across all 3,012 below 500 hits, 2,468 had yet to record an execution and 129 had one or more open. This changes the explanation for the low-hit group. The archive also reports 509,430.4 CPU-hours in the prefix and 114,331.9 outside it. Those are checkpoint subtotals, with imported pilot time included in the prefix. Losses between checkpoints and scheduler usage require other evidence. [Per-setting arithmetic](../analysis/astra/w2_r3_review_20261119/archive.json)

The 1,166 dead endings are **3.44% of 33,914 execution starts**, or 3.68% of the 31,712 with a recorded end. They occurred in 216 of the 4,411 settings with an execution. A setting can have several ranges, attempts and owners. An open attempt is a start whose end was still absent at the scan. A dead end is a recovery decision on a specific attempt. A worker that reaches its planned deadline writes a `censored` end. A hard kill, a node loss or an unsuccessful worker exit can require recovery. The physical cause and the number of distinct workers require further evidence. Healthy restarts verify the last committed journal length, digest and count. They can discard an uncommitted tail and recompute work since the checkpoint. [Execution accounting](../analysis/fable/calibration/v2_dev/p3_stage1b.py) · [Checkpoint recovery](../analysis/fable/calibration/v2_dev/p2_stage1a.py)

The pre-deletion node listing shows `876193[22]` and `[23]` allocated eight slots apiece on n177, with twelve slots allocated to other jobs. The frozen walltime and stale *sampled* checkpoints support a stall. The receipt confirms PBS state F after deletion. The time of physical process exit and the reported node reboot remain unverified. Of the 32 pre-deletion claim hints, the receipt prints 20. **Fifteen printed hints map to settings with zero dead ends in this collection.** At most 17 of the 32 hints could match distinct dead endings here. The actual match count and any earlier attempts by the same jobs require their execution histories. [18 November receipt](../analysis/fable/calibration/v2_dev/p3/r3_check_20261118.txt) · [Claim check](../analysis/astra/w2_r3_review_20261119/claims.json)

## Recovery finding and follow-up

The bound runner `92674ee8` reads the stdout of `qstat -x -f` without checking its exit status in `owner_dead()`. In a local test with an actual runner import, an exit code of 2 accompanied by a line reporting state F classified the worker as dead. After the five-minute negative-cache interval, the same caller continued to return true without consulting PBS again. An empty failed reply and a successful running reply both retried correctly. The independent source review found the same behavior. The positive result can authorise a foreign execution closure or stale lock reclamation while its original owner may still write. The frequency of such replies on Kunanyi is unknown. [Four query controls](../analysis/astra/w2_r3_review_20261119/death_query.json) · [Bound runner](../analysis/fable/calibration/v2_dev/p3_stage1b.py)

1. **At the next authenticated window**, preserve PBS accounting and rerun history, exact worker certificates, slot logs and worker summaries. Join dead endings to their setting, range, generation, owner, PID and host. Check the ordering of reaping or scheduler finish, recovery and successor writes. A certificate present today can have been written after recovery. Record unknown causes explicitly. A later scan may include additional ends written after that setting's turn in the collection.
2. **Investigate promptly** if a successor began while the old process still wrote, a worker reported being superseded, or a committed journal fails verification. Review the affected ranges before including them in the final inventory. For settled ranges, verify successor progress or a terminal setting. At quiescence, reconcile lingering open attempts with their owners, including the two currently open on COMPLETE settings. Queue and claim totals in this collector cover the shared run directory.
3. **Before another dispatch using this path**, have `owner_dead()` require successful PBS completion of the query before accepting F, and exercise the failed-F, valid-F and retry cases. The active runner is hash-bound. Make any change through a separately verified package and explicit continuation plan. The observed fraction alone gives no reason to stop or discard the existing arrays.
4. **At final collection**, use the existing comparator as a PBS job against the round-2 and round-3 raw journals. Report common committed batch coverage, identical and differing records, and settings with zero overlap. Bring the targeted comparison forward for any range with contradictory ownership evidence. [Comparator](../analysis/fable/calibration/v2_dev/p3_r2_determinism.py)

## Reproduction

The first two commands run on deep with Python 3.12.3, NumPy 1.26.4 and SciPy 1.11.4. Run them from the directory containing the review scripts. The claim check uses the saved receipt and the same summary. The query check runs from the project checkout with the runner's Python dependencies.

```sh
python3 audit_archive.py /data/fable/vortex
python3 replay_affected.py /data/fable/vortex
python3 check_claim_receipt.py "$receipt_18nov" "$summary_876194"
uv run --offline --python 3.12 --with numpy==1.26.4 --with scipy==1.11.4 \
  python analysis/astra/w2_r3_review_20261119/check_death_query.py
```
