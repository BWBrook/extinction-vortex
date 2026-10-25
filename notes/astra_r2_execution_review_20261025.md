# Round-2 collection and node implementation review

**Hold the new node wrapper for one control-flow repair before either top-up.**
The W1 collection and same-binding continuation strategy are supported; the
submission, archive naming and reservation integration pass. The new wrapper
can bypass both idle and deadline limits after a grace recheck. Existing
arrays retain their submitted script and need no intervention from this
finding. Fable is next for the narrow repair and its focused checks; no new
scientific or resource decision is needed from Barry.

Barry requested these interim checks on 25 October. Reviewed clean WSL and
canonical Mac mini HEAD `805f0079f5eb8157b351ee31c04a1ab91f3ca3f7`, including
node implementation `b17148c` and board messages 2242, 2389 and 2390. The
node hash is `00ed12fb3aa3a8224ea99efa6377755821efb75e46e6786a5a0fdfde34ca8457`;
the production runner remains
`1e35b94ab3811cc0ddded21aeaa5258120500c9e60f02dd5a6ee0c9c89d50d75`.

## MAJOR: one branch bypasses both idle limits

In `analysis/fable/calibration/kunanyi/s1b_node.pbs:78–82`, an initial empty
wave scan causes a grace pause and a second scan. If the second result is
unknown or in flight, `continue` bypasses the whole-subjob idle check and
allocation cutoff below it. Repeating that permitted observation sequence
keeps a wholly idle allocation alive; once the cutoff clips pauses to zero,
the loop repeatedly scans the shared directories without sleeping.

The [node review](astra_r2_node_review_20261025.md) reproduces both limits
with the actual shell and bounded worker/clock/scan stubs. I independently
repeated all four combined cases:

- With cutoff and worker deadline at ten logical seconds, the wrapper made
  94 further scan attempts at or after that cutoff. It never completed and
  needed the harness's four-second process-group termination.
- With the ordinary long allocation, a 30-second idle budget and ten-second
  grace, the wholly idle slot reached 290 logical seconds without retiring.
  It again required harness termination.
- Mixed unexpected/75/zero exits preserved the finite unexpected-error
  budget and unique owners. Each replacement verified its predecessor's
  exact certificate and absence; no child overlap occurred.
- Applied-but-reported-failed certificate renames combined with an initial
  readback failure recovered safely before replacement.

The scan counts vary with the bounded real-time harness. These are
constructed recurring scan-error sequences, not observed production events
or estimates of NFS failure frequency. The outer guard prevents a later
worker launch; the defect is that the inner idle loop never reaches it.
PBS walltime would ultimately end the job, after the wrapper's intended
limits had failed. No data corruption or unsafe second lock holder was
demonstrated.

Make the allocation-cutoff and whole-subjob idle checks unconditional on
every idle-loop path, including after a grace recheck. Process post-grace
unknown/in-flight state through the common bounded waiting path. A cutoff-only
repair would leave the earlier idle-budget failure. Acceptance is termination
within both budgets without harness intervention, retaining the nine existing
fixture groups and the two combined certificate/restart controls. The nine
groups independently pass under Bash 5.2; the supplied Bash 4.2 receipt was
inspected, not rerun. No broad scientific rerun is needed for this repair.

## W1 collection and provenance

The [collection review](astra_r2_collection_review_20261025.md) reconciles the
saved identities, outcomes and full denominator:

| Outcome | Retained round 1 | Round 2 | Combined W1 |
| --- | ---: | ---: | ---: |
| COMPLETE | 9,695 | 4,798 | 14,493 |
| CAPPED | 2 | 1 | 3 |
| Incomplete | — | 48 | 48 |

All 48 remaining settings are primary n = 30. The formerly invalid s18085
is now COMPLETE. The new capped marmot setting s05404 has 628 prefix hits
at its fixed proposal cap; it remains a terminal outcome. The final selected
rows contain no FAILED or invalid status. These are library outcomes, not
validation results or fitted tests; retain all 200 outer datasets per
scenario/n and keep the independent-check libraries separate.

The independent streaming archive audit passed on deep-server in 399 seconds:

- The 824,755,048-byte archive has SHA-256 `c12e5378…`, 4,800 unique members,
  exactly 4,798 libraries, and an embedded summary byte-identical to the
  fetched summary (`3cd15802…`). Every library matches its declared digest.
- All **9,596,000 new library records** satisfy the 2,000-record count,
  strict identity ordering and bounds, exact field/parameter schema, finite
  parameter values, metric path length, selection S and K-th-hit batch.
- Every one of the 12,119 selected settings equals its original scientific
  row. Independent reconstruction of the complete settings JSON reproduces
  `248f9c7de660dcac19a3e6806fbf97bc512aca9cff42abd54e5fd0f4ee3bbd73`
  exactly, including unchanged helpers, caps and stream definitions.
- The full retained round-1 archive digest still matches our previous audit.
  Its 9,695 libraries were not parsed again by this parent audit. Both
  summaries and their terminal/remaining partition reconcile to 14,544 W1
  settings; the new CAPPED row reaches its unchanged proposal cap.

The receipt is `analysis/astra/r2_execution_review_20261025/archive_audit.json`.
This verifies the archived outputs and bindings, not an independent replay
of all shard checkpoints or the numerical sampling law.

The standalone reconciliation script is narrower than the combined audit:
it does not check every cross-round scientific field, reject duplicate tar
names, compare the embedded summary, or enforce the full record schema and
selection contract. Ten bounded cases establish those limits and its passing
negative controls. They are not findings of corruption in the actual files.
Keep the independent input/archive receipt beside its reconciliation receipt;
the script need not be changed to resume this already checked run.

The saved Kunanyi comparison reports **1,643,296 byte-identical records over
9,336,542,588 common committed batches**, with zero mismatches or recorded
problems across 4,847 requested settings. Its source is unchanged and the
sparse comparison contract was reviewed. This review did not rerun the raw
journal comparison: its per-setting output remains on Kunanyi. Fetch and hash
`s1b/probe/w1r2_determinism.json` in the next ordinary transfer so positive
and zero-coverage settings can be reported. Aggregate success does not prove
positive common coverage for every setting or compare every new record.

The collector's 67,467.025 accounted CPU-hours comprise 49,492.955 useful
and 17,974.070 outside-prefix hours, including imported pilot CPU. Of the
outside-prefix amount, 17,701.224 hours belong to the incomplete settings;
valid committed ranges there remain reusable when earlier gaps finish.
The field name `discarded` must not be interpreted as irrecoverably lost
work. Imported pilot CPU contributes 190.015 hours to this round's useful
total; avoid double-counting it across rounds. The saved
summary alone does not establish each incomplete shard's precise censoring
and requeue history; queue/claim totals include both waves.

## Top-up integration is ready once the wrapper is repaired

The [integration review](astra_r2_topup_review_20261025.md) exercised the
actual submission/collector shells and reservation functions with isolated
PBS and scientific-preflight stubs. Labelled W1/W2 top-ups, idempotent resume,
wrong-subset/new-directory refusal, reservations and preservation of the
existing W1 archive pass. There was no production submission.

Use the existing full `p3_settings_r2.json` digest `248f9c7d…`, `run2` and
distinct top-up labels. Do not select a new 48-row file or reseed. Terminal
settings remain in the inventory while workers resume remaining work under
the same binding and fixed caps. A label such as `b` gives distinct `W1_b`
and `W2_b` receipts and archives, preserving the current W1 snapshot.

The proposed 170 × 8 W1 shape supplies 1,360 slots against a maximum of
48 × 28 = 1,344 concurrent shard workers. Its reservation is 65,288 CPU-h
including the collector. Release the completed original W1 reservation once,
using terminal array/collector evidence; retain the original W2 reservation
until its whole array and collector finish. A new W1 collection is a later
snapshot of run2, not an additional disjoint set of libraries to add again.

Size W2 using actual queued and running requests, held collectors and other
jobs immediately before submission. At the saved 379-running-W2 snapshot,
170 W1 and 325 W2 top-up subjobs plus three collectors would total 6,995 CPUs;
that is illustrative arithmetic, not a live allocation instruction. Each
collector depends on its own array, so overlapping same-wave collections
remain snapshots until the wave is quiescent. No Stage 1c executable or
fitting clearance is supplied by this review.

## Evidence and handoff

Evidence is in `analysis/astra/r2_execution_review_20261025/` and the three
linked review directories. The parent node replay retains its exact fixture
source hash separately. The new wrapper finding was posted as board message
2391; the consolidated review is message 2393, replying to the collection message.

Production sources, settings, ledgers and jobs were not changed. Work comprised
bounded local fixtures and read-only archive/input verification in one
low-priority process on deep-server. No population simulation, numerical
stream replay, fitted statistic or PBS action was run. Fable owns the node
repair and ordinary continuation after that finite implementation check.

Recorded: 25 October 2026, 12:11:06 AEDT (Australia/Hobart).
