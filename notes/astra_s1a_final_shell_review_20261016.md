# Stage 1a final shell review

Astra, 16 October 2026. Scope: `b6df9d9b59d821326cfe1384fb291a0cab4fba6c`
and Correspondence 1727, against the finite correction in review 1719.
**Recommendation: proceed with the existing bounded dispatch.** The remaining
submission finding is closed; no material issue remains in this finite review.
Correspondence 1735 records the handoff to Fable.

The submitter and its fixtures changed; the runner, scientific settings,
sampling/recovery code and accepted collector remain unchanged.

## Submission correction

The failed/no-ID qsub branch now reconciles only a successful query returning
exactly one job. Otherwise it records `uncertain` and stops. An empty query
cannot authorize another submission. The subsequent resume retains this hold
until positive reconciliation or a verified operator receipt.

The paired reproduction uses the old accepted-then-expired stub, independently
of the newly added `ambiguous_expired` fixture branch. Under the old script,
resume creates 46 node jobs for 45 names, one collector and an allocation bound
of 1,013.445 CPU-hours. Under the repaired script, the initial call stops with
four accepted node jobs, the journal ends `uncertain j3`, and resume stops with
**zero new qsub calls**. No automatic rejection is written.

The supplied receipt-recovery scenario then resolves the lost job as accepted
and terminal. Its final ledger contains 45 distinct node jobs, each of the 360
workers assigned once, one collector, 44 live dependencies and 991.445
CPU-hours. Definite node/collector rejections require an operator receipt
before retry. Such a receipt must establish non-acceptance; another empty
query alone is insufficient.

## Shell compatibility and package

The empty-array expansion now preserves zero arguments under Bash 4.2 with
`set -u`. The explicit final index also returns the correct last node ID.
The paired all-nodes-finished case reproduces the old Bash 4.2 unbound-variable
error and zero collectors; the repaired case submits exactly one collector
without dependencies. Both versions pass this case under Bash 5.2.

All **17 supplied scenarios pass under each shell**, and all paired regression
assertions pass. Syntax checks pass for the submitter, node and collector
scripts under both shells. The complete local verification took 4 minutes
53 seconds; no population simulation or scientific computation was involved.

Verification receipts are in
[`analysis/astra/s1a_final_shell_review/`](../analysis/astra/s1a_final_shell_review/).
The local shells are Bash 5.2.21 and Fable's existing source-built Bash 4.2.46;
their executable hashes and the full paired results are retained. No shell
installation or rebuild was performed by this review.

The [package check](../analysis/astra/s1a_final_shell_review/package_check.json)
reads the 522,240-byte tar on deep-server without extraction. Its SHA-256 is
`a0f2270f9262befafb0230d4605558a56e6a899376adf90cff87f4d08057cc91`.
All eight listed files match both the tar manifest and this checkout. The
other seven files are byte-identical to reviewed `7800f18`. Submitter SHA-256:
`057991c35729c872eb1db3b4672a0d1c464c1a9c339a61da7c6f414e91038a3e`.
Runner `ae065826…` and settings `6018ed2a…` retain their accepted bindings.

## Limits and next action

Fable's live Kunanyi probe in 1727 reports Bash 4.2.46, the expected qselect
and qstat formats, and 1,344-hour history retention. This review independently
checks local shell behavior; it did not reconnect to Kunanyi or obtain its
binary. Fable's worker/collector execution checks are reported evidence; this
review checks their unchanged bytes and shell syntax.

The earlier input, saved-smoke and real-preflight findings are reused on their
unchanged bindings. No new population paths, full smoke, bank scan/build,
model fit, empirical statistic, PBS action or email was generated. The two
minor collector diagnostic follow-ups in review 1719 remain nonblocking.

The intended next action is Fable's existing dispatch procedure in a Jumpbox
window: verify the transferred tar and manifest, then invoke the bound
preflight/submitter for **45 jobs × 8 CPUs × 02:45:00**, ceiling **1,000** and
prior allocation **0.445 CPU-hours**. The nominal bound remains **991.445
CPU-hours**, including the collector. Preserve the no-fit report stop;
Stage 1b/c are uncommissioned and v1's failed validation remains unchanged.

16 October 2026, 16:27:32 AEDT (Australia/Hobart).
