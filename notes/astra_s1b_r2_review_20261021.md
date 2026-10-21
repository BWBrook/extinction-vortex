# Stage 1b round-2 review

Reviewed `9a773c9e0fa7b2499d84540c68afe74165304029`, following Barry's wake
and Claude's message 2133. WSL and the canonical Mac mini were clean at that
commit. The review covers the executable recovery package, saved round-1
results, round-2 selection, and the cost and accounting interpretation.
Three bounded reviewers examined worker recovery, scheduling, and science;
the parent independently checked the staged sources and saved outputs.

**Hold this executable package for a focused repair. The scientific restart
strategy is acceptable and the saved terminal libraries can be retained.**
The new fault tests reproduce theft of a live lock after a node rerun,
live-owner lock stalls, starvation of healthy tickets, and dispatch despite
a failed stage checksum. These defects are
not contradicted by the passing smoke and native fixtures: they exercise
failure sequences those checks did not cover.

## What is accepted

- Preserve round 1's 9,695 COMPLETE libraries and two CAPPED outcomes under
  their original binding. Restart the 4,847 incomplete/invalid settings under
  the repaired runner, using the same absolute batches, stream identities,
  scientific inputs and fixed proposal caps. This replays the same finite
  experiment; it does not grant each setting a fresh scientific proposal
  budget in addition to its earlier batches.
- Report a binding for each library and assemble an exact disjoint partition
  of the original inventory. Keep all 200 outer datasets per cell in the
  denominator, including unresolved or capped constituents. Do not fit only
  the convenient completed subset.
- W2 can run alongside W1 recovery. Barry's existing authorization covers
  finishing the work; no further resource decision is needed. Release a
  reservation only on evidence that its jobs have ended, preserving the
  complete historical ledger.
- The proposed shapes reserve 115,208 and 218,888 CPU-hours, respectively,
  including the collectors: 334,096 in flight. They request 6,962 CPUs in
  total, including the collectors, against the recorded 7,000-CPU limit.

## Repairs before the next dispatch

**1. Reused worker names make old death certificates apply to live processes.**
The actual node script starts slot names again at `<PBS_JOBID>.<slot>r0`
on a new invocation. The fixture invokes it twice with the same PBS job ID:
the first invocation leaves a certificate, and the second acquires a lock
under the same owner name with a new, live PID. `owner_dead()` accepts the old
certificate and a competing owner steals the live lock. Both node wrappers
exit successfully. Bind every worker name/certificate to a unique node
invocation as well as the slot/restart number; retain a separately parseable
PBS job identity. Death evidence must refer to the exact process incarnation.

**2. A transient unlock error can strand a lock owned by the surviving worker.**
The actual-source fixture injects one `ESTALE` at the unlock rename after a
claim. The worker catches it as recoverable, adopts its claim, completes the
shard checkpoint, then repeatedly waits on its own still-held lock. At its
deadline it returns success with no COMPLETE marker and the claim retained.
The parent shell therefore does not restart it during the allocation.
Make uncertain acquisition/release ownership an explicit recovery case:
complete a token-safe release, or terminate the affected owner so its reaped
death can be certified. Merely parking the claim cannot solve a live
self-lock. Retain generation-safe mutual exclusion.

**3. Busy settings can still hide healthy work indefinitely.**
Six busy settings with 28 tickets each ahead of one healthy setting cause
repeated `claim()` calls to return `LockBusy` without ever trying the healthy
ticket. Three scans of a 32-ticket head exhaust the fixed loop, and the set
of busy settings is forgotten on the next call. Continue past all excluded
settings or preserve scan progress, while honoring an absolute deadline.

**4. The worker deadline does not bound complete recovery operations.**
`recover_stale()` can perform a five-second lock wait for every eligible
claim without consulting the deadline. A logical-clock fixture with 392
such claims starts 380 waits after a 60-second worker deadline and runs for
1,960 seconds, beyond that deadline plus the 30-minute margin. Propagate an
absolute deadline through claim, recovery, lock and PBS work, clipping waits
and query timeouts. Also cache unsuccessful PBS attempts: four consecutive
60-second query timeouts currently bypass the advertised 300-second throttle.

**5. The staged-source check fails open, and the restart summary is insufficiently bound.**
The checksum command is on the left of `&&`, where shell `set -e` does not
stop the wrapper. An exact-wrapper fixture changes the staged runner after
hashing it: the checksum reports failure, yet the wrapper installs it,
rebinds settings, and submits both arrays and collectors to the stub PBS.
Make checksum failure terminate explicitly before installation.

The summary gate separately accepts a wrong or absent binding, duplicate
terminal rows, wrong row identities, and an unknown status. Verify the
original settings/metric/runner binding, unique full inventory, immutable
row identities, allowed statuses and coherent error mapping before selecting
the restart set. The actual saved summary passes these stronger checks in
the parent's audit; the defect is in the executable gate.

The [core review](astra_s1b_r2_core_review_20261021.md) and
[scheduler review](astra_s1b_r2_scheduler_review_20261021.md) give exact source
locations, fault boundaries, controls, and reproduction commands.

## Before later top-ups and full-scale comparison

- Bind a top-up to the original wave's seeded settings digest and run
  identity. A different digest currently passes top-up admission, skips
  seeding, and sends workers to checkpoints with another binding.
- Protect collection across top-ups. Although JSON and archive names use
  TAG, the log and pack list still use WAVE. In the controlled concurrent
  collector fixture, both collectors succeed and write checksums, but
  `W1_b.tar.gz` contains `collect_W1_c.json`. Use isolated pack/log paths
  and ensure collection has a defined quiescent or snapshot contract.
- Document or implement wrapper resume. If W1 submits and W2 is rejected,
  rerunning the outer wrapper stops at W1's existing journal before reaching
  W2. This is a safe refusal, not duplicate submission; the existing
  per-wave resume path can be used with the appropriate PBS evidence.
- Make the determinism comparison sparse. It currently materializes Python
  sets containing every committed batch ID. Open setting s01669 already has
  381,823,099 prefix batches: integer objects alone exceed 10.6 GB for one
  set, before hash tables, the second run, and intersection. Intersect batch
  intervals and compare sparse hit identities instead. Require the expected
  setting set and positive comparison coverage, and fail on differences.

## Results and cost interpretation

The 1.19 ratio is a diagnostic of the **4,251 completed unseen n = 30 primary
settings**, out of 6,840. It excludes unresolved/capped/invalid settings and
uses estimated cost through the Kth-hit batch, prorated from a whole-prefix
average. Their recorded useful plus discarded CPU divided by the same
projection is about 1.247. Neither quantity establishes the full-cell mean
or the cost distribution of the unresolved settings.

The approximately 92,000-hour restart estimate prices 4,846 incomplete rows
and omits the invalid s18085, despite the text referring to all 4,847 restart
settings. Treat it and the 0.9–1.1-million-hour W2 range as planning
heuristics; correct the scope and retain the unresolved tail. No change to
the fixed proposal cap follows from these cost diagnostics.
Likewise, the 20,029 hours outside incomplete settings' usable prefixes are
not by themselves a causal estimate of crash damage; some later committed
work can be blocked by ordinarily unfinished earlier ranges.

Reservation sums are budget history, not measured spending: reservations
can precede a failed submission, and released names can be reserved again.
Report reservation history, accepted PBS allocation, PBS CPU usage, and
checkpoint-accounted useful/discarded CPU separately. The collector's
178,304 accounted CPU-hours exclude the invalid row's unreported cost; the
earlier checkpoint probe and collector also differ in scope and time.

The recorded `max_run = 3000` limits **running jobs**, not CPUs;
`max_run_res.ncpus` is the resource-limit form. The recorded
`max_queued_res.ncpus = 7000` covers queued and running requests. Thus the
two-week forecast is conditional on its assumed 2,600–3,000 running CPUs,
not a demonstrated scheduler ceiling. See the official
[PBS Professional reference guide](https://help.altair.com/2024.1.0/PBS%20Professional/PBSReferenceGuide2024.1.pdf).

The [science review](astra_s1b_r2_science_review_20261021.md) preserves the
per-cell dataset availability, cost calculations, and comparison-tool checks.
The sampler law and fixed scientific fields need no redesign for this repair.

## Independently verified evidence

- **Full saved archive:** SHA-256
  `bb604f1cc10317b8ea279af471208985c1b3bf464d729b4d284d0418a6538779`;
  9,697 members. All 9,695 libraries match their collector digests and each
  contains 2,000 records: 19,390,000 records in total. Archived and separately
  saved summaries are byte-identical. This validates archive consistency,
  not an independent recomputation of those population paths.
- **Saved summary:** unique full W1 inventory and row identities match the
  original bound settings; 9,695 COMPLETE, two CAPPED, 4,846 incomplete and
  one invalid. Its single diagnostic is the missing COMPLETE marker on
  s18085's verified K-hit prefix.
- **Actual `select`:** 4,847 W1 and 7,272 W2 settings, all original row fields
  identical; only declared round metadata and runner binding change.
  Selected settings hash:
  `fde6c18bdc6a5ddd352b6147cec3f9b99e653e2346dc47dc2ed11b9edaad81d0`.
- **Native preflight on deep-server:** all 27 synthetic fixtures and the
  source/runtime checks pass; 115,208 CPU-hours recorded in an audit-only
  ledger. No production reservation or PBS action occurred.
- **Fault smoke B:** current collector on an isolated copy reproduces both
  saved wave summaries exactly. All four completed libraries match the
  earlier `smoke_deep3` byte for byte. An independent sparse comparison of
  verified journals reproduces 174,302 shared batches and 2,310 identical
  records, with positive non-pilot coverage in five settings. The fourth
  completed library, s00772, is shared pilot input only. The smoke is useful evidence, with
  no new population or serial-recomputation run by Astra.
- **Stage:** tar `b49d00f0b6ffab9bbb3926311477edc65f91005560c68e95a36dfb6c9e632765`
  and all eight source hashes match the checkout. Seven sources match the
  smoke tree; the dispatch wrapper, unused by that smoke, matches both
  actual rehearsal trees. The earlier wrapper in the smoke tree is recorded
  explicitly rather than described as an exact full-package match.

[Parent audit scripts and receipts](../analysis/astra/s1b_r2_review/) include
the streamed archive audit, package/selection audit, native preflight log,
copied recollection logs, and dispatch-source comparison. No live Kunanyi
filesystem qualification was performed in this review. Historical Bash 4.2
receipts are retained separately from the new Bash 5.2 replay.

Fable next: repair the concrete recovery and dispatch failures, incorporate
the top-up protections and reporting corrections, and return one coherent
package with the fault reproductions turned into passing regressions. Preserve
the round-1 archive and scientific settings. Stage 1c retains its executable
settings/adapter check before fitting; no scientific or compute decision is
being sent back to Barry.

21 October 2026, 15:13:26 AEDT (Australia/Hobart).
