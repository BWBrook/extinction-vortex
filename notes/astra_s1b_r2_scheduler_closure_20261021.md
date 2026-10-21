# Stage 1b round-2 scheduler repair closure

Reviewed by Astra (Codex), 21 October 2026, against
`83a6b406681d0c2aec788f8a5f1cb64e124865e4`. This is the scheduler and dispatch
closure component of the independent review; the parent review covers the
native preflight, stage identity and scientific smoke evidence, and a separate
review covers locks, workers and recovery.

**Verdict: the previous scheduler/dispatch findings are closed. No remaining
launch-blocking scheduler defect was found in this scoped check.**

The executable evidence is
[`check_scheduler.py`](../analysis/astra/s1b_r2_scheduler_closure/check_scheduler.py),
with the full results in
[`evidence.json`](../analysis/astra/s1b_r2_scheduler_closure/evidence.json).
Run `python3 analysis/astra/s1b_r2_scheduler_closure/check_scheduler.py` from the
checkout to reproduce it. The harness reuses the previous review's isolated PBS
stubs and directory builder, and executes the current literal shell scripts and
Python function bodies. It stubs native scientific checks and seeding. It does
not contact PBS, run remote computation or modify production files.

| Earlier finding | Independent closure evidence |
| --- | --- |
| Failed stage checksum allowed installation and four PBS submissions | Changed staged runner bytes after manifest creation. The actual wrapper returned 1, installed no changed runner, made zero `qsub` calls and left the ledger unchanged. |
| Summary gate admitted wrong bindings, identities, unknown states and duplicate rows | One valid summary selected exactly the incomplete and invalid W1 rows plus all W2 rows. All 21 malformed variants returned nonzero and wrote no selection file: wrong digest/wave, missing or wrong settings/metric/runner binding, wrong row index/population/outer/n/library, duplicate/missing rows, inconsistent library presence, counts, incomplete list, error list or collection flag. |
| Wrapper could not continue after W1 dispatch succeeded and W2 failed | Forced W2's array `qsub` to reject. The first run made three `qsub` calls, an unresolved retry made zero, a retry after an evidence-labelled rejection entry made two, and a completed rerun made zero. Exactly two arrays and two collectors existed. The round-1 reservation was released once; each new wave reservation was recorded once. The unresolved request still requires operator evidence, as intended by the submission journal contract. |
| Existing round-2 settings could be overwritten during a rerun | Supplied different existing bytes. The wrapper refused before any ledger change or `qsub` and preserved those bytes. |
| Top-up could join a seeded wave with other settings | A valid top-up created one array and collector; its resume created none. Both a changed filename with identical bytes and changed bytes at the original filename were refused before `qsub`. |
| Concurrent same-wave collectors shared log/pack paths and archived the other summary | Forced `W1_b` and `W1_c` to finish both actual `collect()` calls before either shell archived. Each actual collector shell returned 0, archived its own `collect_TAG.json` and `collect_TAG.log`, retained its own summary tag, and passed its SHA-256 check. |

The supplied submission fixture independently reran under Bash 5.2 with all
12 checks passing, including ambiguous scheduler replies, expired history,
failed collector queries, campaign-lock contention, and the added top-up
digest refusal. This closure run does not add a fresh Bash 4.2 execution claim.

The concurrent collector test uses an empty scientific inventory to isolate
the repaired summary/log/pack naming and shell archive path. Libraries remain
shared under `lib/`; the source's broader phrase that collectors “share no
files” should therefore be read as referring to their collection artefacts.
The implemented and documented operational rule remains necessary: a
collection made while another array of the wave runs is a snapshot; only a
collection taken after every array has ended is authoritative. This test does
not promote a running-wave snapshot to a final collection.

Source SHA-256 prefixes recorded in the evidence: runner `841feff9df54`, dispatch
`7108d21c9146`, submitter `e8cb24aa7472`, collector shell `ab8c1aa2afa4`.

Closed: 2026-10-21 20:57:13 AEDT (+1100), Australia/Hobart.
