# Round-3 dispatch and binding review

**Recommendation: HOLD dispatch until one capacity-contract repair covers both
failure paths below.** The scientific selection and final W1 inventory are
correct, and the ordinary positive/resume/error gates are useful evidence. The
current scripts can still submit above the declared 7,000-CPU live-request cap.
I found no stage-byte mismatch; external stage identity is a launch-procedure
check, not a second dispatch blocker.

## BLOCKER — interrupted sizing can be submitted after capacity changes

Both dispatchers write the chosen job count before calling the submitter. The
exact failure precondition is an interruption after that write but before the
matching submit journal exists, followed by an increase in live load. On the
rerun, the size file bypasses `requested()` and every cap check. At the real
cap, the actual round-3 script accepted a saved 874-subjob W2 size after live
load rose from zero to 72 CPUs: eventual requests would be 72 + 874 × 8 + one
collector = 7,065. `s1b_topup_dispatch.sh` accepted the same case. The submit
journal was absent in both reproductions, so these were genuinely new/topup
calls, not no-op resumes of an already accepted array.

Reproduction:

```bash
python3 analysis/astra/r3_dispatch_review_20261027/review_dispatch_contracts.py
```

Treat a saved size as identity only, never as a capacity reservation. Immediately
before any invocation that can issue a new array qsub, recompute the live total
and refuse unless that exact bound size fits. This includes a journal whose
latest array entry is operator-rejected, because `resume` may then issue a new
qsub; an already accepted array must not be counted as new. The least disruptive
implementation is a just-in-time check under the submitter's existing campaign
lock, before it writes `request a`. Add round-3 and topup tests that interrupt
after the size write, increase external live load, rerun, and require no qsub.

## BLOCKER — W2 sizing assumes the accepted W1 jobs are immediately listed

Round 3 submits W1, then derives W2 capacity from a fresh `qstat -t -u` listing.
It does not independently include the W1 array and collector just accepted by
the submitter. The exact failure precondition is successful W1 qsub followed by
a user listing that has not yet exposed those IDs. With the actual final W1
count, W1 accepted 63 × 8 plus a collector; the injected listing omitted it,
W2 accepted 874 × 8 plus a collector, and eventual demand was 7,498. The
existing rehearsal stub exposes accepted jobs immediately, so it does not test
this boundary.

Before sizing W2, either require the accepted W1 array and collector IDs to be
visible in the live listing or add any absent live demand from their bound
journal/run shape. Failing closed until PBS reconciles is simpler and sufficient.
A focused test should delay W1 visibility and require no W2 qsub. The same
principle applies to a topup reference: a finished reference provides no lower
bound, and a live reference covers only itself, so it cannot repair a stale
saved size.

## Non-blocking launch check — bind the extracted stage to the receipt

`sha256sum -c stage_sha256.txt` proves internal consistency only. The manifest
is supplied by the same extracted stage, and no expected tar or manifest digest
is required by `s1b_round3_dispatch.sh`. The harness therefore installed a
deliberately marked, self-consistent substitute stage. This establishes where
identity must be supplied; it is not evidence that the reviewed stage differs.

The reviewed build is reproducible: rebuilding commit `451e50e` produced
`ddb014b0aad32fce2f4b4ed927c2d38aaf1253e1588235f2f7fd476a7f3ab84a`
again. Verify that tar digest before extraction and record it with the two final
summary digests. That trusted construction/transfer receipt closes this point
without changing the dispatcher; requiring an expected manifest digest there
would be useful hardening.

## Accepted contracts

The final W1 summary `8d702807…` is exactly bound to round-2 settings
`248f9c7d…`, metric `2dc57d9f…` and runner `1e35b94a…`. Its 4,847 rows are
unique and identity-equal to the settings: 4,820 COMPLETE, nine CAPPED,
15 incomplete and three invalid. The recovery selection is exactly the latter
18 rows; COMPLETE and CAPPED are excluded. The same rule explicitly includes
FAILED rows when present. No scientific row is altered by selection; the new
settings metadata changes the runner binding and records derivation.

The summary gate checks the supplied digest, binding, complete wave inventory,
row identity, status counts, incomplete list and one-to-one invalid/error
mapping. The new topup wave validation, required reference, terminal-aware PBS
query, distinct labels and submitter identity checks are sound apart from the
capacity cases above. One-time ledger releases require terminal evidence for
each named array and collector. An interruption after a release is resumable.

The existing rehearsal demonstrates the normal path, resumption without a
second qsub, W2-only topup and five refusal paths. It uses the earlier 48-row W1
summary; the separate exact audit above establishes the final 18-row W1
selection. Final W2 remains correctly gated on its future independently
verified digest.

## Evidence and limits

Evidence is in `analysis/astra/r3_dispatch_review_20261027/`. The shell harness
uses the actual dispatch scripts with bounded PBS and submitter stubs; it does
not run PBS, alter a ledger, or test the scientific runner. The W1 audit ran
read-only on deep-server against the full settings and final summary. I did not
repeat the core 41 fixtures, ownership smokes, W1 archive audit, or real
submitter/preflight suite owned by the other reviews.

No Sol Max audit is justified for these deterministic shell defects. Repair the
two capacity checks, run the focused failure cases plus the existing
positive/resume rehearsal, and return the exact stage and summary digests for
clearance.
