# Round-3 recovery closure review — 29 October 2026

**Recommendation: HOLD for one remaining recovery defect.** The two original
crash windows now recover correctly when the held-intent write succeeds. A
failed publication poisons the in-memory held set, however, so the worker's
ordinary retry can still create an execution without its exact recovery record.
The combined failure is reproduced on the actual candidate; it is a liveness
failure, not evidence of a second writer or an invalid accepted library.

Target: repository `dbb1b850c83ee47bedf5de3f74a61c42a8b67a4b`; runner
`e261befa4cae08507c133af787f3f92ee283228c7dc5163076931767adf69894`.

## BLOCKER: failed held-intent publication is treated as completed in memory

At `p3_stage1b.py:751–754`, `hold()` changes `holding` before calling
`p2.atomic_json()`. A failure before that publication completes leaves the ticket
in memory but absent from `workers/held/<owner>`. The worker catches the
`OSError`, parks the ticket and calls `hold(t, True)` again (`:858–869`). That
call does nothing because the ticket is already in `holding`. When the parked
ticket is retried, `take(..., intend)` (`:829–833`) likewise skips the write,
then creates `x/<a>.<k+1>` (`:640–645`).

The reproduction runs the real `atomic_json()` through temporary-file write and
fsync, then injects one `ESTALE` at its `os.replace` before the held file is
published. No production code is changed. After the worker retries, the test
simulates death before or after hint settlement and leaves its setting lock
held. A valid exact-owner certificate is written; the next generation runs
with every directory listing omitted. In both cases:

- exactly **one** held-file publication was attempted, although ownership was
  subsequently created;
- the held file is absent, with one open execution under the predecessor;
- the successor reports **zero** predecessor recoveries and leaves it open.

An isolated transient write failure is sufficient to defeat the new ordering
guarantee; the later crash and omitted hint listing recreate the original
stranding mechanism. The test shortens the retry delay to zero, but otherwise
uses the worker's normal catch, park and adopt paths.

**Minimal repair:** form the prospective held set without changing the current
one, publish that set, then update `holding` only after publication succeeds.
An explicitly dirty state with compulsory re-publication would also work but
is unnecessary. A failed or ambiguous publication must never let `intend()`
return on a later ownership attempt solely because a local set was changed.
Apply the same publication ordering to removals so the set's meaning remains
consistent.

**Closure test:** inject a first publication failure before rename, permit the
next publication, then repeat both crash points with every successor listing
omitted. Require an actual retried publication before execution creation,
one predecessor recovery, the serial library, and no open or superseded
executions. A permanent publication failure must not create an execution.

## What passes

The focused harness independently repeats the two original crash points with
successful intent writes. In each case the lock remains held at death, the
successor sees no listings, recovers exactly one predecessor execution, and a
later worker produces the serial library with zero open executions and zero
superseded writers. The repair closes those original counterexamples.

The separate terminal-library/open-unused-tail diagnostic remains nonblocking
when the final PBS evidence proves the arrays ended. This review adds no
requirement to rerun a valid terminal library or change the shard format.

## Reproduction and limits

```sh
uv run --offline --python 3.12 --with numpy==1.26.4 --with scipy==1.11.4 \
  python analysis/astra/r3_recovery_closure_20261029/check_recovery_closure.py
```

The executable uses the prior review's tiny deterministic data helper and
the current runner. Its adjacent `recovery_closure_checks.json` records all
four cases and the exact source/runtime. All assertions pass: two closure
controls and two remaining-defect reproductions. This is injected filesystem
failure and process death on local storage, not an observed production NFS
history. The parent owns the full native suite and saved raw-smoke replay;
those were not duplicated here. No production file, historical receipt,
reservation or PBS job was changed.
