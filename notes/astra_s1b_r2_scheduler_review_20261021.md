# Stage 1b round-2 scheduler and dispatch review

Astra, 21 October 2026. Target `9a773c9e0fa7b2499d84540c68afe74165304029`.
Independent-reviewer skill applied. Scope: round-2 dispatch, submitter,
collector shell, and the runner's select/preflight/reservation interfaces.
Worker recovery and lock ownership are reviewed separately.

**Recommendation: BLOCK the current dispatch wrapper until findings 1–2
are repaired. Fix 3–4 before enabling later top-ups.** These are reproducible
execution/provenance defects, not requests for additional compute permission.
The proposed first arrays fit the stated reservation arithmetic. The current
artefacts' separate native verification does not make a failed verification
command stop this wrapper.

## 1. BLOCKER — stage checksum failure does not stop dispatch

`analysis/fable/calibration/kunanyi/s1b_round2_dispatch.sh:19` uses:

```bash
(cd stage_r2 && sha256sum -c --quiet s1b/stage_sha256.txt) && echo "stage OK"
```

Because the check is the left operand of `&&`, Bash exempts its failure from
`set -e`. Execution continues to installation, selection, ledger release and
submission.

**Reproduction:** the isolated full-wrapper test appends a harmless comment
to the staged runner after making its manifest. `sha256sum` reports a mismatch.
Nevertheless, the wrapper installs the changed bytes, exits **0**, and creates
**four stub PBS jobs**: both arrays and both collectors. Selection rebinds the
new settings to the installed runner, so the later runner-hash check is not a
substitute for verifying the intended stage.

**Minimal fix:** make verification a mandatory command with an explicit
failure branch, then print success separately. A modified staged file or
manifest must exit nonzero before installation, ledger mutation or qsub.
Receipt: `evidence.json.checksum_failure`.

## 2. MAJOR — the summary gate does not establish the input identity

`s1b_round2_dispatch.sh:34–44` checks the **set** of row directory names and
the correspondence between error prefixes and invalid rows. It never checks
the summary's binding against the original settings, row uniqueness and
metadata, or whether every status has declared handling.

The literal embedded gate returned **0** for all of these mutations:

- wrong `binding.settings_sha256`;
- entirely missing `binding`;
- a row status changed from `COMPLETE` to `UNKNOWN`;
- a row's index and population changed while its directory stayed the same;
- a duplicated COMPLETE row.

The unknown-status row is silently omitted from the restart list, despite
having no recognized terminal outcome. A stale summary from different inputs
with the same directory names is likewise admitted. Missing directories,
truncated error lists and an error outside the invalid set are correctly
refused; those useful checks do not cover this identity gap.

**Minimal fix:** verify the complete collected binding against the original
settings file and its metric/runner hashes; require exactly one row per W1
setting with matching `(dir,index,pop,outer,n,library)`; reject unknown or
unhandled statuses and inconsistent status/error accounting. Preserve the
declared restart set of incomplete/invalid W1 plus all W2. The verified current
production counts are a positive fixture, not a replacement for these negative
cases. Receipt: `evidence.json.gate`.

## 3. MAJOR before top-ups — a new label admits a different settings binding

`s1b_submit.sh:38` requires only that the original wave's journal exists.
Lines 44–50 bind the new label's own identity without comparing it to the
already seeded wave.

**Reproduction:** submit one isolated W1 array, then supply a differently
formatted copy of the same settings JSON under a new filename to `topup b`.
Both settings contain identical values but have different SHA-256 hashes.
The top-up exits **0**, performs no seed, and submits another array and
collector against the same output directory. Its original array/collector
can still be live. The runner's later shard-binding rejection cannot recover
the wasted allocation; a top-up must share the seeded run's input binding.
The real `check()` validates source/metric/runtime fields, which a harmless
JSON reformatting preserves; it does not compare the settings-file hash to
the existing run's journal.

**Minimal fix:** before reservation or qsub, compare the new label's settings
SHA and run/wave binding with the original seeded submission. A new round uses
a new output directory and seed; a top-up continues the existing binding.
Apply the same invariant to labelled resumes. Receipt: `evidence.json.topup`.

## 4. MAJOR before overlapping top-up collection — archives can contain the wrong summary

`s1b_collect.pbs:15–16` makes the JSON and archive names tag-specific but keeps
`collect_<WAVE>.log` and `pack_<WAVE>.txt` shared. The runner writes that shared
pack list at `p3_stage1b.py:754–758`. Top-up submission does not require earlier
collectors to be terminal, and each collector depends only on its own array.

**Deterministic reproduction:** run the actual collector shell for tags
`W1_b` and `W1_c` with tiny collection stubs. Pause B after writing its pack
list; let C replace the shared list; then let both pack. Both shells exit
**0**, both tar verification steps succeed, and both checksum files exist.
Yet **`W1_b.tar.gz` contains `collect_W1_c.json`, not `collect_W1_b.json`**.
The shared log is also overwritten. A checksum certifies these wrong archive
bytes just as successfully as the intended bytes.

**Minimal fix:** give each collection its own log and pack list, derived from
its output/tag. Either require the previous array and collector to be terminal
before a top-up or serialize the complete collection-and-pack transaction for
a wave; separately retain the existing rule that final collection must use a
quiescent wave. The first W1/W2 arrays use different wave names, so this race
does **not** block their simultaneous initial submission once 1–2 are fixed.
Receipt: `evidence.json.collector_race`.

## 5. MINOR — wrapper recovery needs an explicit per-wave resume path

After W1's array and collector are accepted, inject rejection of W2's array.
The wrapper exits nonzero. Re-running it makes no duplicate qsub calls, but
stops at W1's existing journal before recovering W2 (`s1b_round2_dispatch.sh:55–57`).
This is safely refusing a duplicate, not double-spending or corrupting output.

Recovery can use the existing helper directly, preserving the recorded shape:

```bash
bash src/analysis/fable/calibration/kunanyi/s1b_submit.sh "$VB" p3_settings_r2.json run2 W2 570 8 48:00:00 resume
```

If the previous qsub outcome is unresolved, first reconcile it with PBS/accounting
and record the evidenced accepted/rejected journal entry as the helper requires.
If W2 never acquired a journal, its direct call uses `new` instead. Document
this recovery or make the wrapper choose new/resume per wave after verifying
unchanged identities. Do not replace a failed resume with a fresh output
directory or label. The release section also needs cleanup on interruption so
its campaign lock cannot be stranded. Receipt: `evidence.json.dispatch`.

## Verified accounting and evidence limits

| Reservation | CPU-hours |
|---|---:|
| W1: 300 × 8 × 48, plus 8-hour single-core collector | 115,208 |
| W2: 570 × 8 × 48, plus its collector | 218,888 |
| Combined new reservation | 334,096 |

The requested resources total **6,962 CPU slots** including collectors and
872 subjobs/collectors, plus array-parent records if counted. This is compatible
with the stated 7,000 CPU-resource and 4,000 job limits. I do not interpret
the diagnostic's `max_run=3000` as a verified CPU-concurrency limit; the parent
is checking its PBS job-count semantics and the resulting time forecast.

Release of the old reservation is preceded by positive finished-state queries
for both the old array and collector. The ledger replays releases/reservations
chronologically; the first active identity remains bound, and unresolved
submissions remain charged. Treat summing historical reserve lines as reserved
allocation history, **not measured total CPU spending**: reservations precede
seed and qsub, and can include unsuccessful preparation. Barry has already
removed total-resource ceilings; no new authorization question follows.

All **11 supplied submitter fixtures pass under Bash 5.2.21** in temporary
copies. The old local Bash 4.2.46 binary is absent at its recorded path; I did
not rebuild it or claim a new 4.2 replay. Current dispatch/source rehearsal and
native 27-fixture verification are covered by the parent's independent checks.

Reproduce this audit with:

```bash
python3 analysis/astra/s1b_r2_scheduler_review/check_scheduler.py
```

The [harness](../analysis/astra/s1b_r2_scheduler_review/check_scheduler.py) and
[receipt](../analysis/astra/s1b_r2_scheduler_review/evidence.json) preserve exact
source hashes, gate results, stub scheduler requests, reservation lines and
archive contents. Native source/runtime validation and scientific self-tests
are stubbed in the shell interface cases; actual select, reservation and
preflight bodies are extracted from the reviewed source. Seeding and
collection payloads are stubs. No live PBS command, remote compute, production
ledger change, simulation, fitted analysis, email or peer-file edit occurred.

Only this memo and the owned audit directory were written. The parent
integrates the independent reviews; Fable owns the implementation repairs.

21 October 2026, 15:12:05 AEDT (Australia/Hobart).
