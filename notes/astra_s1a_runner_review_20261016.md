# Astra review of the Stage 1a runner

16 October 2026. Reviewed `p2_stage1a.py` at `e3870d4`, including the changes
from the original `74cf551` package. The scientific design, exported metrics,
whole-smoke reconciliation, PBS allocation and collector implementation are
covered by the parent and parallel reviews. This note covers the sampler,
runtime/source guards, batch accounting and crash recovery.

**Do not dispatch this runner unchanged.** The valid-input sampling law and
ordinary execution checks pass, but two reproducible journal-recovery defects
can duplicate or destroy retained records while returning `complete`. These
are failures of the promised recovery contract, not observed discrepancies in
the completed smoke or evidence against the sampling target.

## Findings

### MAJOR: the first checkpoint has no recovery boundary

`p2_stage1a.py:241–248` appends and fsyncs hit records before atomically writing
the state. This ordering can recover from an interrupted later checkpoint,
because a prior state gives the committed prefix. It cannot recover safely
from an interrupted **first** checkpoint: when the state file is absent,
lines 236–238 initialize zero counts but leave any existing hit journal intact.

Fault injection after the first journal fsync and before the first state write
left two journal records and no state. Resuming recomputed the first batch,
appended its records again, then finished with:

- `status=complete`, `batches_done=2`, `proposals=20`, `hits=4`;
- **six journal records**, with both batch-0 proposal identities duplicated.

The fixture forces an immediate checkpoint to keep the test bounded. The
production 60-second interval changes when the same commit sequence occurs,
not its failure behavior. A crash during the first terminal commit has the
same issue. The collector's line-count check will reject the mismatch, so
this is not a silent accepted result, but the resumed run is not complete and
recoverable as claimed.

**Repair:** establish a bound zero-exposure checkpoint before any hit append,
and explicitly handle an orphan journal when no state exists. Never append to
such a file as if it were empty. Add a retained-hit fault test that interrupts
each first-commit boundary and compares the recovered records, identities and
counts with an uninterrupted run.

### MAJOR: recovery can destroy committed records and accepts a short journal

Lines 232–235 open the existing journal with mode `w` and rewrite the prefix
counted by the checkpoint. The open truncates the file before those committed
records are restored. An interruption during recovery therefore destroys
already committed data. Moreover, a short or missing journal is not rejected:
`lines[:S["hits"]]` silently returns whatever exists, then the runner starts at
the checkpoint's next batch and never regenerates the missing prefix.

With a checkpoint declaring two committed hits from batch 0:

| Recovery input | Returned state after batch 1 | Actual journal |
|---|---|---:|
| One of the two committed lines missing | complete, hits=4 | 3 lines |
| Entire journal missing | complete, hits=4 | 2 lines |
| Kill immediately after recovery opens journal with `w` | complete, hits=4 on the next resume | 2 lines |

Lines 230–231 also return an existing `complete` or `failed` checkpoint before
checking its journal; deleting a completed fixture's journal still returns
`complete` with four hits and zero records. The collector catches the count
mismatch later, but recovery itself has already misclassified the state.

**Repair:** record and validate a committed journal boundary before resuming
or returning a terminal state. Reject a short/missing committed prefix. Drop
only the uncommitted tail without rewriting the committed prefix in place;
for example, validate a committed byte offset and truncate a read/write file
at that offset, or atomically replace a fully written temporary prefix. Keep
the state and journal binding/record identities consistent. Test interruption
during recovery as well as interruption during forward computation.

The positive control matters: an existing checkpoint with a longer,
uncommitted tail *does* recover correctly when recovery is uninterrupted.
Its four final records and four-hit state agree. The failures above identify
specific missing branches, not a wholesale rejection of the checkpoint scheme.

## Verified behavior

- The actual runner, imported `bank.py` and imported `p1_sampler.py` paths and
  hashes match the bound settings and this checkout. `check()` passes the
  current package and rejects a changed metric file and an unlisted runtime.
  The source-binding repair is effective in this execution environment.
- The sampler retains the previously audited law: independent Poisson and
  binomial rejection uniforms, every accepted theta simulated exactly once,
  then S/A and the fixed exported ball. No path-cap truncation remains.
- A separate reconstruction of real setting 775, batches 0 and 1, matches
  theta acceptance (1,718 and 1,716), path/selection/overflow counts and the
  retained theta/path/proposal identity. The batches contain zero and one
  hits respectively. This is an 80,000-proposal check including the reference
  reconstruction, not a rerun of the 1,080-setting pilot.
- The original runner suite passes. Its main resume fixture has **zero
  retained hits**, so its passing result does not exercise a committed hit
  prefix. The new synthetic fixtures deliberately supply identifiable hits.
- Additional NaN/infinite/negative-evidence fixtures are rejected. The
  zero-radius rule rejects an unequal coordinate even when squaring the
  difference would underflow; the previous prototype defect is repaired.
- A deadline reached after one synthetic batch flushes its two pending hits
  and records exactly ten proposals as `censored`. An already-expired
  deadline is covered by the original zero-exposure fixture. The runner stops
  starting batches at the deadline; PBS supplies the external hard limit.
- With a synthetic hit stop of three and two hits per batch, the runner stops
  after two complete batches with four hits and 20 proposals, recording
  `stop=hits`. It keeps the whole crossing batch as declared.
- An injected bound violation produces a `failed` checkpoint with zero
  completed exposure. No failure is recast as successful zero yield in this
  tested branch.

## Evidence and scope

Evidence is under `analysis/astra/s1a_runner_review/`:

- `qualification.txt`: deep-server on 16 October at 11:47 AEDT; load near
  zero on 64 logical CPUs, 123 GiB available memory and 4.1 TiB free on `/data`.
- `canonical_test_replay.log`: all original fixtures pass, 0.40 seconds wall,
  60,928 KiB peak RSS.
- `runner_fault_checks.py`, `fault_checks.json`, `fault_checks.log`: exact
  fixture code and before/after state/record identities, plus the successful
  numerical and accounting checks. Elapsed 1.81 seconds; 68,496 KiB peak RSS.
- `actual_bindings.json`: actual imported module paths, hashes, runtime and
  settings/metric digests; the local source hashes were also reconciled.

All checks used one worker and numerical-library threads fixed to one on
deep-server. Fault cases replace only the batch producer in memory and write
only audit-owned scratch directories. They leave the real sampler files and
saved results untouched. No full bank read, outer generation, library build,
full pilot, fit, empirical test or Kunanyi launch was performed. Source and
test scripts were not changed. The journal repairs and a fresh targeted
crash-recovery replay are needed before this review can support dispatch.

16 October 2026, 11:53 AEDT (Australia/Hobart).
