# Astra: Stage 1b executable-package review

Reviewed `e11b9b0171463c4b10e1dbce87b67e0949931db7` and Correspondence
1756–1786. Barry's authorisation in 1759 covers Stage 1b and the Stage 1c
gate meaning; those decisions are settled. Three bounded reviewers examined
the Python runner, scheduler and revised design/report. Astra separately
checked the saved inputs, staged sources and both smoke outputs.

**Recommendation: hold W1 for finite execution repairs.** Accept the revised
scientific design and major reporting corrections. The observed one-ULP
cross-machine difference is not, by itself, a reason to block the experiment.
The launch blockers are recovery and validation defects reproduced with tiny
synthetic fixtures. The stated CPU cap also needs a consistent, tested
contract. This is the agreed executable check, not a new request to authorise
the study or its resource scale. Fable owns the repairs and dispatch.

## 1. Closed findings and independently verified evidence

The [design/report review](astra_s1b_design_closure_review_20261016.md) closes
the earlier gate, failure-scoring, matched-baseline and finite-library
contracts. Stage 1c keeps all 200 IDs; uses the first-K fixed-ball references
without reselection; distinguishes conditional index resampling from new
paths; and uses the authorised 7/200 and 152/200 development criteria with
estimation primary. The named second-library subset and its limited purpose
are accepted. Fitting still needs its separate executable settings and adapter
check before it runs.

The [saved-input audit](../analysis/astra/s1b_package_review/raw_checks.json)
verifies:

- All **21,600 primary and 216 check settings**, their stable indices, E,
  pilot prefixes, rate-derived proposal budgets and disjoint stream tags.
  W1 has 14,544 settings including checks; W2 has 7,272.
- All **7,200 recorded outers, scaled C coordinates and radii**, and **14,400
  evidence records**, against saved Stage 0. The 360 pilot metric entries and
  720 pilot E records are unchanged. There are **6,840**, not 1,800, new
  population-outer pairs. Previously checked bank-file bindings are unchanged;
  no bank rescan was needed.
- The staged tar's 11 regular members, its ten-file checksum list, current
  source bindings and all six members of the fetched Kunanyi smoke archive.
- Deep-server's six-setting collection reproduces exactly under the current
  collector, on an audit-owned copy. The old settings were reconstructed by
  the documented runner/derived-hash changes and matched their saved SHA-256
  exactly. All nine supplied synthetic Python fixtures pass in the actual
  deep-server runtime. The seven supplied submission fixtures and shell
  syntax/failure-propagation checks also pass in the bounded scheduler review.

The corrected primary sampling projection is **861,697.823 gross worker
CPU-hours**; primary plus check sampling and fitting is **874,732.598**.
The proposed first W1 reservation is correctly **199,688 allocated CPU-hours**,
including its collector, within 200,000. These positive checks do not cover
the adverse cases below.

## 2. BLOCKER: repair interrupted planning and lock ownership before W1

The [Python review](astra_s1b_python_review_20261016.md) reproduces a crash
after a durable range marker is written but before its queue ticket exists.
Re-entering `plan()` leaves the range permanently unqueued: no claim, no
terminal status and no way for normal workers to complete that prefix.
Idempotence requires reconciliation of range markers, queued/claimed tickets
and committed checkpoints, including this two-write interruption.

Separately, a live lock aged 601 seconds is taken over solely on age. The
old owner's later `unlock()` removes the replacement owner's lock because
both use the same pathname. Bind locks to an owner/token, prove that owner
has ended before recovery, and allow only that owner to release its lock.
An elapsed-time test alone is not sufficient on a distributed filesystem.

The finite regression cases are a crash between the two writes, an aged live
owner, a genuinely dead owner, and a delayed unlock after replacement. Keep
the first-K order and the approved scientific inputs unchanged.

## 3. BLOCKER: validate complete shard coverage and every charged shard

The collector's successful smoke does not establish its rejection contract.
Three constructed malformed-state cases return `collection_ok=True`:

- Range markers `[0,10)` and `[10,20)` each backed by only one completed
  batch yield a supposedly complete first-K library at batches
  **[0,0,10,10,10]**, skipping batches 1–9.
- A `[0,1)` range whose hashed records claim batch **9999** is accepted.
- A later, non-prefix shard with the wrong binding and **negative CPU time**
  is not validated; it contributes **−1 hour** to discarded accounting.

These are synthetic counterexamples, not corruption observed in either
saved smoke. They show that a matching journal hash and ordered identities
are insufficient. Validate each range's binding, checkpoint schema, finite
nonnegative counters, proposal/batch consistency, stop reason and hit-identity
bounds. A non-crossing completed range must cover its full interval before
the prefix advances. Apply the integrity checks to discarded/cancelled shards
as well as useful ones, and preserve their charged cost. The detailed review
provides exact source locations and reproducible cases.

## 4. MAJOR contract mismatch: nominal proposal cost versus measured CPU cap

The implementation converts 2,000 hours at a pilot rate into `cap_batches`.
It does not enforce 2,000 measured worker CPU-hours. This is visible in real
smoke evidence: with `cap_cpu_h=1.5`, the two new capped settings consumed
**1.531901** and **1.560466** CPU-hours, respectively. A synthetic slow-rate
fixture likewise consumes four measured hours under a two-hour nominal cap.

The design already mentions conversion to a proposal budget; consequently
this is an ambiguity in the stated contract, not evidence of an unauthorised
dispatch. Make the distinction explicit in the repaired package. If the
promised ceiling is measured CPU, enforce it across concurrent shards,
discarded work and retries, with a declared bound on in-flight work. If the
intended stopping rule is the fixed proposal limit, call it a **2,000-hour-
equivalent proposal budget at pilot throughput** and do not advertise it as
a hard per-setting CPU ceiling. Resolve that wording/implementation match
without silently changing the stopping rule. The separate wave and campaign
allocation ceilings must still be enforced.

## 5. MAJOR before rollover or further reservations: wave and budget accounting

The [scheduler review](astra_s1b_scheduler_review_20261016.md) verifies the
first W1 arithmetic and inherited ambiguous-submission handling, but reproduces
two campaign-level gaps:

- Workers receive no wave filter, so a W2 worker can claim residual W1 work
  from the shared queue. Bind wave identity through claiming and recovery,
  and report unfinished W1 settings explicitly at the handoff.
- Allocation history is supplied by the operator as `PRIOR` and scoped to
  the run directory. Starting another W1 directory with zero prior admits a
  second 199,688-hour reservation. This does not invalidate the first command;
  it means cumulative ceilings are not established for a restart/top-up.
  Use a verified campaign account, with a locked reservation record or an
  explicit operator-maintained ledger checked by the launcher. Unresolved
  submissions must retain their reservation. A new output directory must
  not reset spending history.

These need resolution before W2 or a further reservation. They can be repaired
with the runner now; they do not require a new workflow platform.

## 6. Cross-machine smoke: accept the observation, restrict the claim

Independent comparison confirms three byte-identical libraries and exactly
one differing field among 8,000 retained records. In s00247, record 1882
(zero-based), batch 250274, proposal 16958, `f` is
`0.014690871541791693` on deep-server and `0.014690871541791694` on Kunanyi:
one ULP. All retained identities, recorded paths and boundary flags match,
as do the six reported statuses, prefix endpoints and hit counts.

I favour **documenting this observed numerical agreement**. Withdraw the
general byte-identity claim and preserve each run's actual library bytes,
hashes, source/runtime and node provenance. The smoke does not prove a
universal one-ULP bound, identity of all rejected-proposal decisions, or exact
equality on future CPU types. The suggested AVX-512 explanation is unverified;
do not present it as established. Pinning a dispatch path now would require
new evidence and would not retroactively change the reused pilot prefixes.
Nothing in this one observed difference establishes a substantive change
to the scientific results; no fitted results have yet been produced here.

## 7. Finite reporting repairs, owner and stop

Keep the four zero-hit pilot settings unresolved in the cap table. Its “zero
expected failures” at 2,000 hours counts lower-limit substitutions as successes;
report plug-in exceedances and unresolved counts instead. Correct 1,800 to
6,840 new pairs and stale “uncommissioned” wording. The paired bootstrap's
67.406-hour omission is immaterial but can be made consistent with the point
inventory. Tighten the scheduler fixture's `CEIL+8` assertion to `CEIL`.
Filesystem free space does not establish a per-user quota; complete the stated
quota check or document the applicable absence of a quota at dispatch.

**Fable next:** finite recovery/collector repairs, explicit cap contract and
wave/cumulative-accounting corrections; preserve all authorised settings and
gates. Rebind the executable package, rerun the affected adverse cases and
the bounded smoke, and return it for Astra's check before W1. Barry's Stage
1b/1c authorisation remains in force; no repeat resource decision is requested.

This review ran no new population simulation, bank scan/export, fit, empirical
test, live PBS command or email. The saved-input/smoke audit and native synthetic
suite took 7.20 seconds on qualified deep-server. Kunanyi's fetched archive
contains libraries and the summary/log, not raw shard journals or PBS receipts;
the collector replay was therefore independently performed for deep-server
only. The adverse-case reproductions are bounded local synthetic tests.
Exposure E59 records these limits.

16 October 2026, 22:37:25 AEDT (Australia/Hobart).
