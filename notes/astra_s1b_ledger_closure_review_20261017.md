# Astra Stage 1b ledger closure

17 October 2026, 00:50 AEDT (Australia/Hobart). Reviewed source
`ca94676a0a06cf895637fb25d5dd291f5f65cd50`, changes since `ced47a8`.

**Both reservation retry findings are closed. No ledger-related W1 launch
blocker remains within this focused review.** The first W1 reservation is
still 199,688 CPU-h. This conclusion is limited to the two ledger defects and
their submission/recovery contracts; the parent review integrates lock,
source-binding and smoke evidence before deciding overall readiness.

## Repairs verified

`analysis/fable/calibration/v2_dev/p3_stage1b.py:629-660` now replays ledger
entries chronologically. Releasing a name removes its current reservation;
reserving that name again makes it active again. A request reusing an active
name must match its wave, CPU amount and identity. `preflight` binds settings
SHA-256, output directory, job count, cores and walltime in the identity
(`:663-674`). The submitter also includes job count, cores and walltime in its
array-name hash (`kunanyi/s1b_submit.sh:34-35`).

The actual shell and extracted actual ledger/preflight bodies reproduce the
following outcomes:

| Case | Exit codes | Allocation accepted by PBS stub | Result |
|---|---|---:|---|
| One-job reservation (392 h), seed failure, then 521-job retry | 1, 1 | 0 h | Enlarged request refused before qsub |
| Explicit qsub rejection, evidenced release/rejection, same-name resume, then fresh directory | 1, 0, 1 | 199,688 h | Retried reservation remains charged; second allocation refused |
| Normal submission, duplicate new request, resume | 0, 1, 0 | 199,688 h | One array and collector |
| Same-shape seed failure then retry | 1, 0 | 199,688 h | One reservation, one accepted array and collector |
| Normal submission then fresh directory | 0, 1 | 199,688 h | Cumulative ceiling retained |
| Accepted array with lost reply and expired history, resume, fresh directory | 1, 1, 1 | 199,680 h | Unresolved array stays charged; no collector or replacement submitted |

The final ambiguous case reserves the full 199,688 h, including the collector,
although the stub accepts only the array. This is the intended conservative
accounting. No real allocations or expenditure occurred in any case.

Direct calls to the actual reservation function additionally verify that the
same active name refuses a changed CPU amount, wave, or identity; an identical
request remains idempotent with one ledger line. All eight supplied scheduler
fixtures pass under Bash 5.2.21 and 4.2.46. The three shell scripts pass syntax
checks. There are eleven passing aggregate acceptance checks in the new
evidence file.

## Evidence and scope

Run `python3 analysis/astra/s1b_ledger_closure_review/check_closure.py`.
The script writes `analysis/astra/s1b_ledger_closure_review/closure_evidence.json`
with source hashes, fixture receipts, ledger entries and each preflight trace;
it exits nonzero if an acceptance check fails. The two preceding failure
sequences are preserved in the new harness, adapted only to the current
preflight signature and added `ledger_active` function.

PBS commands and seeding are stubs. Scientific source/runtime binding checks
and the runner's self-tests are disabled in this interface harness; settings
file SHA-256 is computed normally for its identity. The parent runs the native
runner tests separately. Temporary fixture copies prevent overwriting Fable's
receipts. No PBS dispatch, remote activity, population simulation or fitting
was performed, and no implementation or project state was changed.

Reservations from failed preparation remain conservative charges until an
operator releases them on evidence; that is the documented contract. This
review does not verify the live campaign ledger or scheduler accounting, and
does not reopen the earlier minor fixture tolerance issue or other unrelated
scope.
