# Stage 1b final launch review

Reviewed `979cd411b1c9ae9ecc32bb2980045a690dfe02b3` in response to Barry's
morning request and Fable's board message 1809. WSL and the canonical Mac mini
were clean at this commit when review began.

**W1 is ready for Fable's ordinary bound preflight and submission.** The
lazy-planning change is accepted, the overnight regression smoke passed,
and Fable reports successful qualification of the exact staged package on
Kunanyi's NFS filesystem. No further code repair, population smoke or
scientific decision is required by this review. Dispatch remains Fable's
responsibility; this review did not submit or reserve production jobs.

## Planner delta

The only executable change since the preceding `ca94676` closure review
delays listing the queue and claimed directories until the first unfinished
range needs reconciliation. It lists each directory at most once per call.
Fresh settings and settings with only finished ranges avoid these listings.

A bounded reviewer compared the actual old and current functions, extracted
unchanged through AST, under the actual setting lock. **All 17 scenarios
produce identical filenames and file bytes after both an initial and a
repeated planning call.** They cover fresh settings, pilot prefixes,
terminal and newly completed/capped settings, failed shards, cancelled and
finished ranges, queued and claimed ranges, three orphan states, and mixed
multiple unfinished ranges. Unrelated settings and waves remain unchanged.

Both production callers hold the setting lock throughout planning. Moving
the listing later within this critical section does not expose a new
same-setting claim transition. The lock and reservation implementations and
all three submission/PBS scripts are unchanged from the closure review.

[Equivalence script](../analysis/astra/s1b_final_delta_review/plan_equivalence.py),
[receipt](../analysis/astra/s1b_final_delta_review/plan_equivalence.json), and
[log](../analysis/astra/s1b_final_delta_review/plan_equivalence.log).

## Saved smoke and package

The parent independently checked the saved `smoke_deep3` run on deep-server:
four COMPLETE and two CAPPED settings, no failures, errors or incomplete
settings, and empty queue and claims. Each complete library has 2,000 records
and is byte-identical to both earlier deep-server smokes. The four saved
serial-recomputation receipts match the actual library hashes.

The completed smoke used the preceding `4886d8e8...` runner. Restoring its
runner and parent-settings bindings reconstructs its exact settings hash.
The current collector, run on an isolated copy with those original bound
settings, reproduces the saved summary exactly. This is not a claim that a
fresh population smoke or fresh serial recomputation ran under the new code.

The current full-settings native preflight passes all **22 synthetic
fixtures**, source bindings and runtime checks on deep-server. Its
audit-only ledger records the correct **199,688 CPU-hours**. All 21,816
setting rows and other settings fields are unchanged: replacing just the
runner binding reconstructs the preceding full-settings hash exactly.
The metric is unchanged; all ten manifest entries and seven staged source
files match, including the local reviewed checkout.

| Artifact | SHA-256 |
|---|---|
| Runner | `00dd369f7eca0e126e47959c2e205a19d155c166a9ca53637059dc03372e5407` |
| Full settings | `86545d6b83dec07e31b84fa97a5fd43b5dc4130170c48e01f92b9f7f0320520a` |
| Smoke settings | `fa477b66d38ac06e234fbe69646159f71ca13fc4a87de13d53f4ebd4be2e1096` |
| Stage tar | `e18bea28684242309897fbf6e6bd7a367a5f108746ce73b2c4ade699d2b3b629` |

[Audit script](../analysis/astra/s1b_final_delta_review/package_and_smoke.py),
[receipt](../analysis/astra/s1b_final_delta_review/package_and_smoke.json), and
[native preflight log](../analysis/astra/s1b_final_delta_review/native_preflight.log).

## Kunanyi and launch handoff

Fable's message 1809 and [committed qualification note](../analysis/fable/calibration/v2_dev/NOTE.md)
record verification of this tar and manifest on Kunanyi, and 22/22 fixtures
with `TMPDIR` on `/u` NFS in 24.8 seconds. These are Fable's on-host results;
Astra did not repeat the Kunanyi probe or inspect the live production ledger.

The long seed is acceptable. Fable measured 653 seconds for all 14,544 W1
settings on deep-server, importing 720 pilot prefixes and producing one
COMPLETE setting, 14,543 planned settings and 14,697 tickets. The measured
NFS file-operation latencies and approximately 16,000 required fsyncs support
an order-of-ten-minute Kunanyi estimate, not a guaranteed duration. Use the
proposed extended dispatch session (`KUNANYI_EXPECT_TIMEOUT=3600`); another
seeding optimization is unnecessary for launch.

Fable next: verify the staged hashes, run the usual preflight with the
production campaign ledger and NFS `TMPDIR`, then seed and submit W1 using
520 jobs, eight CPUs and 48 hours, plus the eight-CPU-hour collector:
`520 * 8 * 48 + 8 = 199,688`, within W1's 200,000-hour ceiling. Preserve the
existing submission journal and evidence-based recovery if interrupted.

Barry's Stage 1b/1c authorization and gate meaning remain settled. Stage 1c
still needs its own executable settings/adapter check before fitting.

17 October 2026, 10:45:55 AEDT (Australia/Hobart).
