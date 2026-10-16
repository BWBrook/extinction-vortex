# Astra: Stage 1a PBS and dispatch review

16 October 2026, 11:51 AEDT (Australia/Hobart). Reviewed source
`e3870d47c132421ee625d53f8297c683dddffdfc`; changes since `36cf1a6`.

**Disposition: the proposed single-dispatch budget passes, but repair submission
recovery and collection integrity before dispatch.** These are narrow execution
repairs; they do not require a new scientific design or orchestration platform.
The independent runner review owns checkpoint recovery defects. No real PBS
command, Kunanyi access, message/email, simulation, fit or production dispatch
was performed in this review.

Evidence: [`audit.py`](../analysis/astra/s1a_pbs_review/audit.py),
[`audit.json`](../analysis/astra/s1a_pbs_review/audit.json), and
[`shellcheck.txt`](../analysis/astra/s1a_pbs_review/shellcheck.txt).
The fixtures execute temporary copies of the actual shell scripts with absolute
qsub/qstat paths replaced by recording stubs. Collector tests execute the actual
`collect()` body extracted by AST with standard-library dependencies; the
simulation module is not imported. PBS directives are comments in these local
Bash fixtures and cannot submit work or send email.

## Findings

### P1: a partial submission followed by retry exceeds the bound and duplicates writers

`s1a_submit.sh:9–19` records all node IDs only after the collector submission.
There is no run lock, duplicate-dispatch guard or per-submission journal.

The fixture makes the fourth qsub fail. Three node jobs have already been
accepted; the script exits 7 and leaves no `node_jobs.txt`. Repeating the same
command accepts another 45 node jobs. The resulting 48 node jobs can allocate
**1,056 CPU-hours before collectors**, exceeding the 1,000-hour ceiling. The
first three jobs and their replacements write the same 24 worker/setting paths.
The replacement collector depends only on the second set of 45 jobs, so it can
start while an original duplicate remains live. This defeats both checkpoint
ownership and the assumption that all writers have stopped before packing.

Repeating a fully successful call also succeeds, accepting 90 node jobs with a
1,980 CPU-hour bound; the second call overwrites the first job-ID files. A
collector-submission failure similarly leaves 45 accepted nodes without a local
job-ID ledger. These are reproduced failure paths, not a claim that Fable has
actually retried or duplicated a run.

Repair with an exclusive run lock and a durable journal of each submission and
its accepted job ID. Refuse an already-submitted run unless an explicit recovery
path reconciles accepted/uncertain submissions. Keep all accepted IDs in the
collector dependency, and count their allocation against the same ceiling.
Persist enough information before each request to reconcile a lost qsub reply;
do not automatically retry an uncertain acceptance. Check the bound settings,
worker count and allocation before the first qsub. The current generic command
also accepts 45 × 8 × 4 hours (1,440 CPU-hours) without rejecting that mismatch.

### P2: collection can package an old success summary after a current failure

`p2_stage1a.py:344–367` aborts on the first malformed checkpoint or binding/count
mismatch, before replacing `collect.json`. `s1a_collect.pbs:13–19` then packs
the output directory anyway.

In the shell fixture, a corrupt current checkpoint plus an old
`collect.json` produces exit 1 **and a correctly hashed archive containing the
old success summary**. The nonzero exit is preserved, which is good, but the
archive is not self-contained evidence of the present collection outcome and
later settings receive no current failure accounting. Missing, failed, running
and censored states are currently counted when their JSON is readable. A
successful collector exit with explicitly labelled incomplete rows is not by
itself an erroneous scientific result; planned censoring should remain allowed.

Write a current summary atomically on every collection attempt. Include
per-setting unreadable/mismatched states, current collection success and run
completion separately. Preserve an earlier summary as historical evidence if
needed, but never leave it at the current-summary path. Pack the current failure
receipt along with salvageable rows, and distinguish expected censoring from
corrupt/missing evidence in the completion report.

### P2: collector verifies line counts, not retained-record validity or worker provenance

At `p2_stage1a.py:355–366`, one line containing `not JSON` is accepted as one
retained hit; collection reports a complete setting and derives a retention
rate. A stale `worker9999.json` with a different binding and `nworkers=99999`
is included without complaint. The collector also does not read or hash its
`metric_path` argument; its output repeats the metric hash from settings even
when the actual supplied metric differs.

Validate each retained record's JSON/schema and batch/proposal identifier,
unique ordered identity and committed-prefix bounds. Check setting identity,
counter consistency and input binding; validate expected worker IDs, bindings
and assignment. Record absent workers explicitly. Run the appropriate actual
input/source checks before interpreting or packaging a current complete result.
The independent runner audit supplies the crash-recovery cases that can create
short, orphaned or inconsistent journals even without a manual file edit.

### P2: the documented preflight does not perform its claimed runtime check

The dispatch recipe in `v2_dev/NOTE.md:558` says `p2_stage1a.py test` also checks
the runtime. `test(metric_path)` at lines 291–341 does not call `check()` or
compare `allowed_runtimes`; it accepts no settings file. Its fixtures are
useful but do not validate the final settings/source/runtime binding. Workers
do call `check()` after allocation.

Add a light settings-and-metric preflight that calls the existing binding
checks before submitting jobs, and correct the recipe. The stage archive is a
patch to the existing runtime root: it omits `bank.py` and `env.sh`. Verify the
actual existing `bank.py` and environment on the destination rather than
treating the patch archive alone as a self-contained runtime. No new runtime
installation or cluster smoke is implied by this recommendation.

## Verified arithmetic and shell behavior

- 1,080 settings; 360 unique workers numbered 0–359; three settings per worker,
  exactly one n=0 control and two informative settings. Total proposal ceiling:
  **3,504,293,600,000**.
- Recomputed throughput-derived load: **742.4933 CPU-hours**, with worker loads
  from 7,424.8531 to 7,424.9752 seconds. This is a model based on the smoke's
  CPU rates, not measured elapsed time for the large pilot. The stated 760–800
  CPU-hour expected use adds unmeasured overhead/margin.
- One 45-job dispatch × 8 cores × 2.75 hours gives **990 allocated CPU-hours**.
  Adding one collector at its one-hour limit, smoke allocation 28 × 57 seconds
  and its six-second collector gives **991.445 CPU-hours**. There are 8.555
  hours left below 1,000, insufficient for one additional full 22 CPU-hour node
  job. These bounds depend on enforcing one dispatch and accounting for retry
  allocations.
- The node shell launches eight workers for job 44: IDs 352–359, each told
  NWORKERS=360. One stubbed worker failure produces node exit 1 after all PIDs
  are waited. The deadline is start + 9,300 seconds for the proposed walltime,
  leaving ten minutes for final checkpoint/exit; scheduler walltime supplies
  the allocation bound.
- The collector's real tar command excludes its live `collect.out` and
  `collect.err`, passes `tar -d` on a quiescent fixture and emits a matching
  SHA-256. Source provides up to three packing attempts with 60/300-second
  delays. Shared-filesystem lag and live concurrent-directory writes were not
  recreated; this test does not establish why the original smoke packing failed.
- `bash -n` passes for all three scripts. ShellCheck reports SC2207 for the
  unquoted qsub command substitution and SC1091 because the sourced runtime is
  external to the invocation. The material submission issues above are
  established independently of those lint diagnostics.

## Stage archive receipt

The only remote action was a qualified, read-only deep-server check and copying
the 491,520-byte stage archive for local inspection. Host identity was
`deep-server`, Linux, user `bwbrook`. No Kunanyi connection was needed.

Source:
`/data/fable/vortex/v2_dev/p2/s1a_stage_final.tar`.

SHA-256:
`ceaa29759b02915610967c96857092f724871731e13e9bf2fe1444d533ea9f19`.

All eight entries in `s1a/stage_sha256.txt` match archive bytes and this
checkout's bytes: metric, settings, throughput, three PBS/submit scripts,
`p1_sampler.py`, and `p2_stage1a.py`. The ninth regular archive file is the
checksum manifest itself. No full bank is included. A repaired source package
will need fresh settings/source hashes and a fresh archive receipt.

Fable owns the narrow repairs and executable handoff; Astra then verifies the
changed contracts. No additional user decision follows from these execution
findings alone.
