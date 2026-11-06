# Stage 1b: full noisy-design sampling package (authorised; executable package under Astra's check)

Fable, 16 October 2026. This responds to Astra's 1755
(`notes/astra_stage1bc_design_review_20261016.md` P1/P2 and the cost review).
It specifies the full 200-outer sampling campaign. Barry authorised it on
16 October 2026 (board 1759, exact): "Decisions: 1 and 2 are both fully
authorised." The implementation is in §7. W1 is dispatched only after Astra's
check of the executable package.

Earlier the same day, Barry had stated his inclination (Claude chat, exact):
"Regarding compute, I'm strongly inclined to authorise the full planned
design."

Numbers come from `p2_inventory.py` → `p2/s1a_main/s1b_inventory.json` and
the corrected Stage 1a report. They are projections, not measured costs.

## 1. Inventory

**Libraries:** 9 populations × 4 scenarios (b1, b3, b5, b16) × trial IDs
0–199 × n ∈ {0, 30, 300}.
- That is **21,600 settings**: 14,400 informative and 7,200 shared n = 0
  controls.
- Each library is K = 2,000 retained pairs, so **43.2 × 10⁶ pairs** in all.

**Unchanged:**
- the sampler law;
- the full-precision closed C-balls with all ties eligible;
- the prior, dynamics, S and A;
- the noisy E draws bound in Stage 0;
- batches of 20,000 proposals.

**Trials 10–199 need their export run once more on deep-server, and E is
already fixed.** E is fixed in `s0/s0_inputs.json`. The metric (mask, MAD,
q, radius, recorded series) is exported once on deep-server for the 6,840
population-outer pairs beyond the pilot's 360 (7,200 in all), with one bank
pass, exactly as `p2_stage1a.py export` did. *Corrected 16 Oct per Astra
1791: the first issue said 1,800.*

## 2. Stable identities and pilot reuse

**Pilot indices are preserved.**
- **Pilot settings:** the 1,080 pilot settings keep their indices (0–1,079).
- **New settings** are appended:
  index = 1,080 + ((pop_i × 4 + scen_i) × 190 + (trial − 10)) × 3 + n_i,
  for trials 10–199, with pop, scenario and n in the frozen orders.
- **Lookup:** the settings file binds an explicit (population, outer, n) →
  index table, and the runner never derives an index from loop position.
  Astra's renumbering example (the naive 10 → 200 loop) cannot arise.

**The per-batch stream is unchanged:** `default_rng([20261015, 2, index,
batch])`.

**Pilot reuse.**
- Each pilot setting resumes from its last verified complete batch. Its
  accepted-pair identities are preserved exactly once, and its first 100,000
  proposals remain the smoke prefix.
- Setting 772 (crow, null_low_s/7, n = 30) is already complete. *Corrected 16 Oct: the first issue named 775.*
- Setting 576 (no exposure) starts at batch 0.

These remain exposed development paths, not validation data.

## 3. Ordered, idempotent sharding

**The work unit is a shard:** a (setting, batch range [a, b)) pair.
- **Determinism:** a shard's output depends only on its setting and batch
  streams, so recomputing a shard reproduces it byte for byte.
- **Recovery:** each shard has the existing atomic recovery contract: zero
  checkpoint, hashed committed journal, verified prefix, atomic replacement.
- **Size:** shards target about 1 worker CPU-h at the setting's measured
  throughput, which keeps walltime and discard small.

**Library assembly** follows Astra's rule.
- Order the attempts by (batch, proposal_in_batch). A library is complete
  only when a contiguous verified prefix of batches 0..m holds at least
  K hits.
- The library is the first K of those hits.
- A hole (an unfinished earlier range) blocks completion, and faster later
  shards cannot substitute for it.
- Once the crossing range is established, later shards for that setting are
  cancelled. Their computation is charged as discarded.

**Execution is pull-based.** Instead of static LPT packing, which the
heavy-tailed costs make impractical, each PBS job (for example 28 cores and
≤ 48 h) runs workers that claim the next shard.
- **Claiming:** a claim is an atomic rename of a shard ticket on the shared
  filesystem.
- **Order:** tickets are ordered by wave, then by setting, then by batch.
- **Stale claims:** these are released only after the owning job has
  terminated, confirmed in PBS, and the shard's journal has been verified.
- **Duplicates** cost compute but cannot change results.
- **Submission:** the journalled, locked, resumable submitter carries over
  unchanged in contract, extended from 45 to the wave's job count.

## 4. Caps, waves and ceilings

**Per-setting cap: a fixed proposal budget equivalent to 2,000 worker
CPU-h,** at the setting's bound rate: its pilot's realised throughput, or the
cell median for trials without a pilot.
- **It is a fixed stopping rule, not a measured-CPU ceiling.** Measured CPU
  at the cap can differ by a few per cent: the 1.5 h smoke caps used 1.53 and
  1.56 h.
- This was the authorised rule (design §4 as authorised). Astra's 1791 asked
  for the wording to be made explicit.
- Allocated-CPU ceilings per wave and per campaign are enforced separately,
  by the reservation ledger (§7).
- The cap bounds the unresolved settings and the single-hit tails, where the
  largest interval reaches about 70,000 h.
- Reaching it is a **failure to fill K within budget**, which Astra calls a
  support failure for scoring. It is not evidence that the target has zero
  support. It stays in every denominator.

| Per-setting cap | Expected gross worker CPU-h | Expected failures to fill (of 21,600) | Datasets with a failure (n = 30; n = 300) |
|---|---|---|---|
| 500 h | 713,854 | 400 | 0; 340 |
| 1,000 h | 812,835 | 60 | 0; 60 |
| **2,000 h** | **861,698** | **0 by point projection** | **0; 0 by point projection** |

These are point projections, and zero plug-in exceedances is not zero expected
failures.
- The four zero-hit pilot settings (242, 512, 536, 833) remain **unresolved**.
  Their expected-cost lower limits, about 560–610 h, are below the cap, but
  their true costs may exceed it.
- Unseen outers will add some failures at any cap.

**The cap of 2,000 h is recommended.** At the point projections it removes
almost nothing. Tighter caps save little and leave n = 300 datasets
incomplete.

**Shards in flight per setting:** at most 28. A 2,000 h setting therefore
needs at least about 71 h of wall-clock.

**Two waves.**
- **W1:** n = 0 and n = 30, all 200 outers: 14,400 settings; 139,090 gross
  worker CPU-h expected.
- **W2:** n = 300: 7,200 settings; 722,608 expected.
- **W1 runs first.** Its full-scale measurements update W2's projection; that
  is reporting, not a design change. The named design is never replaced by
  whichever outers finish.

**Allocated-CPU ceilings.** These include discarded shards, retries,
cancelled allocations, setup and idle cores.
- W1: 200,000.
- W2: 1,000,000.
- **Campaign: 1,200,000.**
- Reaching a ceiling stops further dispatch and returns the measured state to
  Barry. It never redefines the design or completes a library from later
  shards.

## 5. Independent-library check (named and priced)

**Purpose.** This is a second, independent K-member library for a named
subset. It is not the crossing-batch surplus. It estimates numerical
sensitivity to finite libraries on its named cases. It is not a calibration
result or a universal error bound.

**Rule** (pre-fit, from the Stage 1a sampling diagnostics). For each
scenario, take two outers from trials 0–9:
- the **ordinary** outer: the lower median of the n = 300 nine-population
  summed pilot cost;
- the **difficult** outer: the largest resolved one.

All three n levels and all nine populations are included.

| Scenario | Ordinary | Difficult | Projected worker CPU-h |
|---|---|---|---|
| null_prior_predictive | 7 (179) | 4 (492) | 671 |
| null_low_s | 6 (1,915) | 4 (3,490) | 5,405 |
| MA_betamin | 6 (321) | 8 (1,511) | 1,832 |
| MA_d10_0.5 | 6 (843) | 1 (3,072) | 3,915 |

**Total:** 8 outers × 27 = **216 libraries, about 11,800 worker CPU-h**, and
24 paired fitted analyses.

**Its streams use a disjoint namespace:** `default_rng([20261015, 3, index,
batch])`. Tag 3 is never used by the primary campaign, which keeps the check
disjoint after any retry or expansion.

**These names are fixed now, before any fitted output.** Their failures are
counted, and the analysis uses no library selection.

## 6. Fitting, storage, wall-clock and total

**Fitting.**
- 1,600 informative analyses, plus 800 n = 0 baseline analyses, plus 24
  check analyses: 2,424 analyses.
- At about 0.5 worker CPU-h each (v1 and D3 measured 0.34–0.48), that is
  about **1,200 worker CPU-h**.
- Fitting is a separate Stage 1c decision (draft revised alongside).

**Storage.** About 315 bytes per retained pair, so about **13.6 GB** of
primary libraries.
- Add the crossing surplus, shard checkpoints and the check libraries.
- Check the /u quota before dispatch, and use a project or scratch area if
  needed.

**Wall-clock.** About 12 days at a sustained 3,000 cores. This is
arithmetic, not a completion guarantee or a reservation.

**Expected total (worker CPU-h).**

| Component | Worker CPU-h |
|---|---|
| Sampling | 861,698 (additional 860,964 after the pilot credit) |
| Library check | 11,823 |
| Fitting | 1,212 |
| **Total** | **≈ 874,700** |

Allocation overhead (idle cores in jobs, setup, discarded shards) plausibly
adds about 5–10%, so about 0.92–0.96 × 10⁶ allocated. The enforceable ceiling
is 1.2 × 10⁶ allocated.

**Uncertainty.** The expected figures are point projections. Their
resampling spread (746k–984k for sampling) is not a calibrated range. The
caps and ceilings, not the projections, are what bound spending.

## 7. Implementation (authorised 16 October; board 1759)

**Built and tested on deep-server;** Astra checks it before any dispatch.
Code: `v2_dev/p3_stage1b.py`; `kunanyi/s1b_node.pbs`, `s1b_collect.pbs`,
`s1b_submit.sh` and `s1b_submit_fixture.py`.

1. **Metric export.** Done (`p3/p3_metric.json`, `2dc57d9f…`): 7,200 outers
   and 14,400 E records.
   - All 360 pilot pairs and 720 pilot E records are identical to Stage 1a's.
   - It took one bank pass of 6 min 20 s.
2. **Settings.**
   - `p3/p3_settings.json` holds 21,600 primary plus 216 check settings,
     with stable IDs and the pilot prefix bound per setting.
   - Each setting also binds its rate, its cap (proposals) and a cell-prior
     hit rate.
   - The planner parameters are bound in the settings too.
3. **Runner.** The audited Stage 1a `run_setting` gains a batch offset, a
   file name and a cancellation hook, with the defaults unchanged; its 34
   fixtures still pass. The check streams use tag 3.
   - **Shards** are planned adaptively, as successors created under a
     per-setting lock (a range marker, then a ticket).
   - **Claims** are atomic renames. A stale claim is requeued only when PBS
     reports its job as finished.
   - **The prefix** has hole blocking. When a COMPLETE marker appears, any
     running shard is cancelled at its next commit.
   - **Failures:** a refused recovery or an unexpected error marks the
     setting FAILED; it does not kill the worker.
4. **Collector.** It validates every shard's binding, journal and records,
   assembles each library from the verified prefix, accounts for useful and
   discarded CPU, and writes the pack list.
5. **Waves.** Each wave is one PBS job array plus an afterany collector that
   emails Barry. The submitter is derived from the audited Stage 1a
   journal/reconciliation contract, with keys a and c.
6. **Fixtures.**
   - **p3 synthetic** (all pass):
     - the library is byte-identical across serial and parallel plans and
       claim orders;
     - a zero-rate setting is capped;
     - stale claims are requeued only for finished jobs;
     - a killed worker's claim is recovered and resumed identically;
     - nothing is claimed after the deadline;
     - tampered journals and altered pilot prefixes are rejected;
     - a refused recovery fails the setting, not the worker.
   - **Submitter:** 7 scenarios, passing under bash 5.2 and 4.2.46.
7. **Planner simulation** on the 1,079 pilot settings, with unlimited
   workers: worst-case CPU overhead 6.8% over serial. A typical setting needs
   one range (mean 2.5, maximum 56), about 55k ranges in the campaign.
8. **Smokes.** A deep-server end-to-end smoke on a 6-setting subset
   (`p3_settings_smoke.json`, reduced cap) runs first. Then the same subset
   on kunanyi, where the libraries must match deep-server byte for byte
   although the machine-dependent shard plans differ. Then W1.

### 7a. Repairs after Astra 1791 (16 October, evening)

1. **Owner-safe locks.** A lock is a directory holding `owner.json`
   (owner, host, pid, token), published by an atomic rename.
   - It is broken only on positive evidence that its owner has ended:
     the same host with the pid gone, or the owner's PBS job at
     `job_state = F`. Age is never evidence.
   - `unlock` requires the acquiring token, so a late unlock cannot free a
     successor's lock.
2. **Recoverable publication.**
   - Every queue transition holds the setting lock: claim, censored requeue,
     stale requeue, ticket release, and every plan.
   - `plan()` reconciles each unfinished range so that it has exactly one
     queued ticket or live claim, and republishes an orphan once. A range
     marker alone is never counted as recoverable in-flight work.
3. **Strict prefix and collector certification.**
   - A completed non-crossing range advances the prefix only when it
     committed every batch of its range.
   - The collector validates every declared range before using it for the
     library or the accounting: ranges tile from the pilot end; and each
     shard's binding, first batch, status, stop, field types and domains,
     exact proposal count, counter invariants, journal length, hash and
     count, record schema, identity bounds within its committed batches,
     global order and selection S are checked.
   - It also checks marker consistency in both directions (COMPLETE against
     the crossing, CAPPED against the cap), and lists incomplete settings.
4. **Cap rule wording** (§4): a fixed 2,000 h-equivalent proposal budget,
   not a measured-CPU ceiling.
5. **Waves.** Workers, claims and stale recovery are restricted to their own
   wave.
6. **Campaign account.**
   - Ceilings are bound in the settings (W1 200k, W2 1.0M, campaign 1.2M).
     The submitter holds a campaign-wide lock and its preflight writes a
     reservation to `$VBASE/s1b/reservations.tsv`: array cores × walltime +
     8 h for the collector, once per array name.
   - A fresh output directory therefore cannot reset spending history.
   - An unresolved submission keeps its reservation; only an explicit
     `release NAME manual: <evidence>` line frees it.
   - The operator-supplied PRIOR and CEILING arguments are removed.
7. **Fixtures.**
   - **p3: 19, all pass.** They add:
     - an interrupted publication republished once, reaching the reference
       library;
     - an aged live lock owner not displaced, and a successor acquiring
       after release;
     - a late unlock unable to free a successor, and a dead owner's lock
       recovered;
     - stale claims requeued only within the wave, and the wave filter;
     - the collector rejecting an uncovered range ("complete by budget
       without covering its range"), an identity outside its committed
       batches, and a bad discarded shard (wrong binding, negative CPU);
     - the campaign account: same name, a fresh directory, the ceiling,
       release.
   - **Submitter: 8 scenarios** under bash 5.2 and 4.2.46, including a
     concurrent submission refused by the campaign lock.

### 7b. Repairs after Astra 1800 (17 October)

1. **Generation-safe lock reclamation.**
   - An ended lock generation is broken only through `_reclaim`, which takes
     the `lock.reclaim` mutex, itself published by an atomic rename, so there
     is one reclaimer at a time.
   - Under that mutex the reclaimer re-reads the lock's current token, and
     breaks the lock only if that token is the observed dead generation and
     its owner is positively ended.
   - A reclaim mutex whose own owner has ended fails closed (`LockStale`).
     That setting waits for operator recovery; claim, recovery and the
     post-shard step skip it and report it, while other settings proceed.
   - **Fixture:** Codex's two-contender interleaving. Both contenders observe
     the same ended generation, and one acts only after the other has
     acquired. The result is one holder, then the successor. The same
     harness (`p3/race_check.py`) gives two concurrent holders on the
     previous code (d801012) in 3/3 runs and one on the repaired code in 3/3.
   - Two more fixtures: a stale observation cannot remove a successor, and a
     dead reclaimer fails closed.
2. **Chronological, identity-bound ledger.**
   - The ledger is replayed in order. A `release` deactivates a name, and a
     later `reserve` of that name is active again.
   - Each reservation binds wave, CPU-h and identity (settings sha, output
     directory, shape) at its first active line. The same identity is
     idempotent; any difference is refused.
   - Array names now include the shape, so a re-shaped retry is a new name and
     the old reservation stays charged until released with evidence.
   - **Fixture:** Codex's retry paths.
     - A same-name reservation with another shape is refused.
     - A fresh directory beyond the ceiling is refused.
     - After a release, a same-name retry is charged again, and a
       fresh-directory array is then refused.
3. **Fixtures:** p3 22/22; submitter 8/8 under bash 5.2 and 4.2.46.

## 8. Decisions (Barry, 16 October 2026; board 1759)

"Decisions: 1 and 2 are both fully authorised."
1. **Stage 1b sampling is authorised:** W1 then W2, within allocated ceilings
   of 200,000 / 1,000,000 / 1,200,000 CPU-h, with a 2,000 CPU-h per-setting
   cap.
2. **Stage 1c fitting is authorised,** with the gate meaning of
   `notes/vortex_stage1c_fitted_draft_20261016.md` §6.

Each executable package is still checked by Astra before dispatch.

## 9. Round 2 (21 October 2026)

### 9a. W1 round 1: outcome and diagnosis

Array 821088[] (520 × 8 cores × 48 h) ended at about 11:25 on 21 October with
its 199,688 CPU-h reservation spent. Sources: probe `p3/w1_progress_20261021.txt`;
diagnosis `p3/w1_diag_20261021.txt`; board 2119.

**Collector 821089** ran 11:24–12:48 and exited 1, which means a finished
summary with an error, not a crash.
- **Statuses:** 9,695 COMPLETE, 2 CAPPED, 0 FAILED, 4,846 incomplete and
  1 invalid.
- **The invalid setting is s18085:** "verified K-hit prefix without a COMPLETE
  marker". Its crossing shard finished, but no worker survived to plan it;
  its last two claims belonged to dead workers.
- **Archive:** `W1.tar.gz` (`bb604f1c…`, 1.75 GB) holds the summary, the log
  and the 9,695 libraries. It was verified on deep-server
  (`/data/fable/vortex/v2_dev/p3/w1_r1/`).
- **CPU:** 151,638 useful and 26,666 discarded (pilot CPU included in useful).

**Cost diagnosis** (`p3_w1_costs.py`, `p3/w1_r1_costs.json`):

| Group (completed settings) | Estimated crossing cost + discards / projected | Median throughput ratio | Median hit-rate ratio |
|---|---|---|---|
| Pilot outers (trials 0–9), n = 0 | 0.97 | 0.98 | 1.00 |
| Pilot outers (trials 0–9), n = 30 | 0.97 | 1.00 | 0.45 |
| Unseen outers, n = 0 | 0.98 | 0.99 | 1.00 |
| **Unseen outers, n = 30** | **1.19** | **1.01** | **1.05** |

The hit-rate ratio is against the cell's pooled prior, which is weighted by
proposals, so a typical pilot outer sits below it.

- **Kunanyi's throughput and the pilot outers were projected correctly.**
- **The scope of the 1.19 ratio** (corrected after Codex 2142). It covers the
  4,251 unseen n = 30 primary settings that completed, out of 6,840. It is an
  estimated cost to the K-th-hit batch, prorated from each prefix's average
  CPU per batch.
  - The same settings' recorded useful and discarded CPU is 1.247× their
    projection.
  - The ratio excludes unresolved, capped and invalid settings, so it
    establishes neither the full cell means nor the cost of the unresolved tail.
  - Among completed settings, the throughput and hit-rate medians are near
    projection; unresolved costs remain unknown. The two medians, taken
    separately, do not establish the median cost ratio.
- **Discards:** 6,638 CPU-h (6%) on COMPLETE n = 30 settings is the planned
  parallel overshoot. The 20,029 CPU-h outside incomplete n = 30 settings'
  usable prefixes includes the defect's damage (for example, s07690 has 29
  ranges with the first blocked while 28 finished). It is not a causal estimate
  of that damage: later committed work can also wait behind an ordinarily
  unfinished earlier range.
- **Restart estimate:** about 92k CPU-h for the 4,846 incomplete rows (cell
  means of realised costs, or 1.25× round-1 spend where larger). The invalid
  s18085 is not included. This is a planning heuristic.
- **W2 planning scenario** (722,608 expected): with a similar unseen-outer
  excess and the planned overshoot, roughly 0.9–1.1M worker CPU-h. This is a
  scenario, not a forecast; the unresolved tail is not priced.
- **Wall time** is conditional on the running CPUs the scheduler grants. W1
  peaked at 2,624; queued CPUs are capped at 7,000 (§9d).

**Settings** (14,544 in W1): 9,695 COMPLETE, 2 CAPPED, 0 FAILED, 4,847 open
(including s18085).

**Cost:** 177,940 worker CPU-h from the shard checkpoints (178,304 per the
collector), against 139,090 expected for the whole of W1.

**A defect that wasted allocation** (none of it reached the science; no shard
or setting failed):
- **NFS stale handles:** 97 workers died of `OSError: Stale file handle`, and 6
  died of `Directory not empty` when removing a released lock, caused by a
  silly-renamed `.nfs` file. These errors arose in bookkeeping outside
  `run_setting`'s handler: reading a checkpoint or `owner.json` that another
  client had just replaced.
- **Locks left by crashed workers:** a worker that crashed holding a setting
  lock left it held. Without positive death evidence, workers on other hosts
  could prove the owner dead only once its PBS job finished, up to 48 h later.
- **Unbounded waits:** every worker that picked one of that setting's tickets
  waited without limit, past its own deadline. The waits were the likely cause
  of the 75 walltime kills (`Exit_status 271`). About 424 workers left no exit
  record: about 103 had crashed and the rest were stuck until killed.
- **PBS load:** each stuck worker queried PBS (`qstat -x -f`) on every 0.05–0.15 s
  poll. That is the likely cause of a single history query taking about 10 min
  on 18 October.
- **Lost completion lines:** `jobs.log` received concurrent appends over NFS
  and lost lines (442 of 520 subjobs recorded).
- **Memory was not a factor:** peak use was under 1 GB per 8-core subjob,
  against 10 GB requested.

### 9b. Repairs

Runner `ee5e8cd6…` (fixtures 27/27):
- **NFS reads:** listings and JSON reads retry `ESTALE`. A released lock's
  directory is removed with `ignore_errors`.
- **No crash on transient errors:** an `OSError` that outlives its retries
  ends only the iteration. The claim stays with the worker, which resumes it
  from its checkpoint after `PARK_SECS`. Thirty consecutive errors end the
  worker. A transient `OSError` inside `run_setting` (`ESTALE`/`EIO`) no
  longer fails the setting.
- **Bounded lock waits:** a claim passes over a setting whose lock stays busy
  for 5 s. A commit waits at most 600 s (and never past the deadline), then
  parks the claim.
- **Death certificates:** `s1b_node.pbs` writes
  `workers/dead/<owner>` for every worker process it reaps. Any worker accepts
  the certificate as positive evidence, so it breaks that owner's locks and
  requeues its claims without waiting for PBS. Claims are recovered every
  `RECOVER_SECS` (600 s), as well as when the queue is empty.
- **PBS throttle:** PBS is consulted about a lock owner only after the same
  lock generation has been seen for `PBS_SUSPECT_SECS` (300 s). Each job is
  then queried at most once per interval, and a finished answer is final.
- **Node script:**
  - the deadline is taken from the job start, before Lmod, with a 30 min
    margin;
  - a slot restarts a failed worker under a new owner name (`<job>.<slot>r<k>`),
    up to 20 times while time remains;
  - completion is recorded in one `done.<index>` file per subjob.
- **`select` subcommand:** a round's settings are the listed dirs of the bound
  settings, all other fields unchanged, rebound to the new runner.

### 9c. Round-2 design

- **A new binding, so round 2 never resumes round-1 shards.** The binding
  (settings, metric and runner hashes) is checked on resume and by the
  collector.
- **Round-1 settings that are final keep their libraries:** COMPLETE and
  CAPPED, collected under binding `86545d6b…`/`00dd369f…`.
- **The open round-1 W1 settings, incomplete and invalid, restart from batch 0,** or from their bound
  pilot prefix. This is in `run2`, under settings `p3_settings_r2.json` (open W1
  dirs plus all W2 dirs).
- **Restarting is chosen over a cross-binding resume** because it needs no
  compatibility logic. Streams are fixed per (stream tag, index, batch), so the
  re-run reproduces round 1's hit records batch by batch. Comparing the two is
  a determinism check that comes free with the restart.
- **The final W1 library set** is round 1's terminal settings plus round 2's.
  Each library is reported with its binding.
- **W2 is dispatched alongside W1 round 2,** in the same run directory, with
  waves filtered.

### 9d. Ceilings and the ledger (Barry, 21 October 2026, Claude chat; board 2123)

> "As to finishing W1 and W2: authorised to use whatever compute you need.
> Those caps were just guesses, they're not a straight jacket and I'm replete
> with allocated compute. It's not a constraint: do what you need to do to get
> all the work completed! Break the glass ceiling :)"

- **The allocated-CPU ceilings of §4 and §8 no longer limit total spending.**
- They remain bound in the settings (hash-bound, so unchanged). The ledger now
  enforces them as **bounds on in-flight reservations**:
  - each finished array gets a `release` line citing its PBS accounting;
  - reserve lines are reserved-budget history, not spending.
- **Spending is reported as four separate measures:**
  - reservation history;
  - accepted PBS allocation (subjobs × CPUs × walltime used);
  - PBS CPU usage;
  - the checkpoint-accounted useful and discarded CPU.
- **The per-setting 2,000 h proposal cap is unchanged.** It is a stopping rule,
  CAPPED is a reported outcome, and changing it would change the design.

**Shapes.** kunanyi's per-user limits (`qmgr`, 21 October) are:
- `max_run = 3000` running **jobs** (not CPUs; corrected after Codex 2142);
- `max_queued_res.ncpus = 7000` CPUs, which counts queued and running
  requests;
- `max_queued = 4000` jobs.

Round 2 therefore opens with:
- W1 r2: 300 × 8 × 48 h;
- W2 a: 570 × 8 × 48 h;
- 6,960 CPUs plus two collectors in all.

Later W2 arrays follow as earlier ones finish, each reserved and released the
same way. Over-provisioning costs only minutes, because a worker exits when
the queue is empty.

### 9e. Repairs after Codex 2142 (21 October 2026)

Runner `841feff9…`; stage tar `3eafd94d…`. Each of Codex's reproduced failures
is now a passing regression.

1. **Exact death certificates.**
   - Owner names are `<PBS job>.<slot>r<restart>n<nonce>`, with the nonce drawn
     per node invocation, so a rerun under the same PBS job never reuses a name.
     The PBS job identity stays parseable before the last dot.
   - `s1b_node.pbs` starts each worker in the background, waits for its pid,
     and certifies `{owner, host, pid, rc}` by atomic rename.
   - A certificate breaks a lock only if it names the lock owner's host and pid.
     For a claim, the unique owner name suffices.
2. **Uncertain ownership.**
   - If `unlock` cannot read its owner record, or its releasing rename fails,
     it raises `OwnerUncertain`. That is a `BaseException`, outside every worker
     handler. The process exits 75, and its node script certifies it and
     restarts the slot, so other workers break the lock through the
     certificate. A retried rename could have removed a successor's lock.
   - A publication whose rename reported failure but took effect is recognised
     by its token in `lock()`.
   - **Uncertain acquisition (after Codex 2156).** Each failed publication stays
     unresolved until the lock's token is read: our own token means acquired, a
     foreign one means contention. If the wait ends while the last publication
     is unresolved (the owner record unreadable past the read retries and the
     patience), `lock()` raises `OwnerUncertain`, not `LockBusy`, so a lock
     this process may hold is never forgotten. The process exits 75, is
     certified, and its lock is broken once reads recover. Known foreign live
     owners are still waited for (`LockBusy`). The fail-closed boundary of an
     ambiguous reclaim-mutex publication is unchanged.
3. **Busy settings cannot hide healthy work.** `claim()` keeps passing over busy
   settings, with all their tickets, until it claims a ticket, has found every
   setting with tickets busy (`LockBusy`), or reaches the deadline.
4. **Absolute deadlines.**
   - The worker's deadline bounds `claim`, `recover_stale` (it stops scanning),
     every lock wait and every PBS query (timeout clipped; none within 1 s of
     the deadline).
   - Commit-time lock waits end no later than deadline + `LOCK_PATIENCE`.
   - A failed or timed-out PBS query is cached for `PBS_SUSPECT_SECS` like any
     other answer.
5. **Dispatch.**
   - A stage checksum failure stops before installation.
   - The gate checks the round-1 summary's exact digest (`2aa92fb0…`); its
     binding to the round-1 settings, metric and runner; the unique W1
     inventory with unchanged row identities; known statuses (COMPLETE exactly
     when a library exists) with consistent counts and incomplete list; and
     errors one-to-one with the invalid rows.
   - Every step is repeatable:
     - an existing `p3_settings_r2.json` must be identical;
     - the release is written once;
     - each wave is submitted new, or resumed if it has a journal.
6. **Before later topups:**
   - a topup must use the wave's seeded settings file and digest (from
     `submit_<WAVE>/run.json`);
   - collectors use `collect_<TAG>.{json,log}` and `pack_<TAG>.txt`, so two
     collectors of one wave share no files.
   - **Collection contract:** a collection taken while another array of the
     wave may run is a snapshot. After one `RETRY_SECS` (30 s) pause, the
     settings that failed validation are re-read once; the pause is taken once
     per collection, so a wave-wide failure still yields a summary within the
     walltime. Only a collection taken after every array of the wave has ended
     is authoritative.
7. **Determinism check, now sparse.**
   - Committed coverage is held as intervals, and only the records inside the
     other run's coverage are compared, by identity and then by bytes.
   - Journals are verified against their checkpoints, and every listed setting
     must exist in both runs.
   - Exit codes: 0 when identical with positive coverage; 1 for an identity
     difference, a missing setting or no coverage; 2 for byte-only differences.

### 9f. Round 2 in production: false-positive acquisition uncertainty (23 October 2026)

Probe at 36 h (`p3/r2_progress_20261023.txt`).

**Progress**
- W1 r2: 4,676 of 4,847 COMPLETE markers, or 96.47% (all 2,055 n = 0; 2,621
  n = 30), with 171 heavy n = 30 settings open. Their median progress of 0.76
  sums all shard hits, not the verified contiguous prefix. 53.3k worker CPU-h
  so far, which does not establish the final cost against the ~92k heuristic.
- W2: all 7,272 open, with the heaviest started first; 18.4k CPU-h.
- No FAILED marker and no transient-error lines. Invalid settings and journal
  or library validity were not tested; the strict collection decides those.

**Finding: 7,969 worker exits with `OwnerUncertain`** (exit 75; 6,587 in W1,
1,382 in W2), every one from the acquisition rule of §9e item 2.
- They are concentrated on a few hot settings: s15403 alone has 1,975.
- 82 slots had 19 or 20 restarts (the tally selected ≥ 19; the maximum was 20,
  which is the node script's cap). Those at 20 have stopped.
- **Cause.** The rule marks *every* failed publication unresolved, including
  plain contention (`EEXIST`/`ENOTEMPTY`, where the server refused because the
  lock exists). On a hot lock, the owner record is often absent or unreadable
  for a moment between holders. When the 5 s claim patience ends in such a
  moment, the worker exits instead of passing the setting over, restarts, and
  claims the same hot setting again.
- **No integrity failure observed** (corrected after Codex 2239). Recovery and
  the strict collection remain to be verified.
  - In a false positive this process holds no lock.
  - An acquisition failure during a commit leaves an owned claim. The
    certificate permits its recovery but is not a recovery receipt: a claim
    waits while a foreign live lock holds its setting.
  - Exit-75 processes write no final worker record.
- **Cost.** The direct restart delay is about 27–37 slot-hours in W1 (6,587 ×
  15–20 s). Capped-slot idleness, lost in-flight work and the attribution of
  W1's 9.8k CPU-h allocated-versus-used gap (84.5%) between this and the W1
  tail are not measured. PBS ratios come from the saved aggregate only.
- **The runner cannot change during round 2.** Its hash is in every run2
  shard's binding. The correct rule, for any later runner: only an ambiguous
  rename failure (an errno other than `EEXIST`/`ENOTEMPTY`) leaves acquisition
  unresolved, and it stays unresolved for the whole call unless this call's own
  token is read. Reading a foreign or absent record is not trusted to resolve it,
  because NFS can serve a stale entry.

**Mitigation within the binding, for W2 topup arrays** (the node script is not
bound; submitted arrays keep PBS's stored copy):
- restart a worker that exits 75 without a restart cap, while time remains,
  with a short jittered delay;
- restart a worker that exits 0 after a pause, but only while the wave still
  has claims in flight, since a finishing shard can plan successor tickets. A
  subjob whose wave has nothing left in flight still ends.

This goes to Codex for a check before the first W2 topup.

**Node script for topups (`00ed12fb…`; Codex 2239 requirements).** The submitted
arrays keep PBS's stored copy (`cafc0a4d…`); the runner `1e35b94a…` and the
settings are unchanged.
- **Owners.** Every launch advances the slot's generation, so the owner is
  `<job>.<slot>r<g>n<nonce>`, with the nonce drawn per invocation. Exit 0
  refills get new names too.
- **Certificates.** Each child is waited for, certified with `{owner, host, pid,
  rc}` and read back before any replacement, with up to `CERT_TRIES` attempts.
  An applied-but-failed rename reconciles by the read-back. A persistent
  failure stops the slot with a diagnostic (exit 3).
- **Exit 75** relaunches with no cap while time remains.
- **Other non-zero exits** relaunch until `MAX_FAIL` (20) such exits, then the
  slot stops with that status. The generation is never reset.
- **Exit 0.** Same-wave queued tickets (`WAVE_*` in `queue`) refill at once.
  - With only claims in flight, or an unreadable state (a scan error is
    "unknown", never "empty"), the slot polls every `POLL_SECS` (300) plus
    jitter.
  - The slot retires once the whole subjob has been idle for `IDLE_MAX_SECS`
    (1,800). The idle clock restarts while any sibling slot holds a worker,
    since those cores are held anyway.
  - Queue and claims reading empty, twice across a grace pause, retire the
    slot.
- **Deadline.** One absolute deadline is passed to every child. There is no
  launch after `LAUNCH_CUTOFF_SECS` (600) before it, checked before every
  launch, and every pause is clipped to the cutoff.
- **Polling cost.** A 1,800 s idle budget at a 300 s poll gives at most about 7
  two-`find` checks per idle slot, with no Python start while idle.

**Evidence**
- `kunanyi/s1b_node_fixture*.json`: 9/9 under bash 5.2 and 4.2.46, using a
  logical clock and stubs for `python`, `date`, `sleep`, `mv` and `find`.
  The cases follow Codex's acceptance table:
  - 25 × exit 75, then success;
  - non-75 failures interspersed with 75 and 0;
  - queue-only, claims-only, empty and other-wave states;
  - work published between observations;
  - transient and persistent scan errors;
  - certificate failure and applied-then-failed rename;
  - a same-job rerun with refills;
  - a deadline passed, crossed in a pause, or crossed in a certificate retry;
  - eight idle slots, with and without a busy sibling, in real time.
- Codex's `check_current_node.py`, with a clock-advancing `sleep`
  (`p3/codex_node_baseline_on_00ed12fb.*`):
  - endless exit 75: 380 certified refills, each seeing its predecessor's
    certificate;
  - non-75: stops at 20;
  - exit 0 with claims: one launch, then bounded retirement;
  - certificate refusal: one launch, then the slot stops;
  - deadline crossed during a pause, or passed at start: no further launch.
- Submitter fixtures are unchanged at 12/12.

**Idle-loop repair after Codex 2391/2393 (node `8fe10208…`).**
- **The bug.** In `00ed12fb…`, a post-grace reading other than "empty" (unknown
  or in flight) skipped the idle-budget and cutoff checks. Alternating empty and
  unknown readings could poll past the idle budget and, at the cutoff (pauses
  clipped to zero), scan without pause.
- **The repair.** Every idle pass now:
  - first checks the launch cutoff, then the whole-subjob idle budget;
  - then makes one reading;
  - then ends in one pause: the grace pause after a first "empty", or a poll
    pause clipped to the remaining idle budget.
  - Retirement on "empty" needs two consecutive empty readings. Pauses of at
    least 1 s are enforced.
- **Evidence:**
  - node fixtures 10/10 under bash 5.2 (twice) and 4.2.46. The new case fails
    every third scan:
    - long before the cutoff the slot retires at the 30 s idle budget after 3
      scans;
    - at a 10 s cutoff it retires after 2 scans.
  - On `00ed12fb…` the same two cases ran to the 60 s harness timeout, with
    1,431 and 1,525 scans and no retirement.
  - Codex's `combined_checks.py` on `8fe10208…`
    (`p3/codex_node_combined_on_8fe10208.*`, the two bug assertions recorded
    rather than asserted):
    - past-deadline case: retires at 10 s, 2 scans, 0 at or after the cutoff,
      no forced termination, done receipt written;
    - idle-budget case: retires at 30 s after 3 scans;
    - the mixed-restart and ambiguous-certificate controls pass as assertions.

**Topup dispatch** (`kunanyi/s1b_topup_dispatch.sh`).
1. Verify the pushed node script's digest and install it.
2. Release W1 round 2's reservation once, after PBS shows its array and
   collector F.
3. Size from live requests: the CPUs of every queued, running and held job and
   subjob, with array parents excluded. Sizing is refused if the total falls
   below the running W2 array's own count × 8.
4. Submit the W1 topup (`W1_JOBS`, default 170, for the 48 remaining
   settings), then a W2 topup sized to the room left under 7,000 CPUs. Each
   topup's size is recorded on first submission, so a rerun resumes the same
   submissions.

The original W2 reservation stays until its array and collector finish.
Rehearsed with stub PBS (`p3/rehearsal_topup_*`).

**Accounting correction (Codex 2393).** 17,701 of W1 round 2's 17,974
outside-prefix CPU-h belong to the 48 incomplete settings and are potentially
reusable by the W1 topup under the same binding. The accounted total of 67,467
CPU-h includes 190 imported pilot hours.


### 9g. Duplicate shard execution in W2 (27 October 2026)

**W2 collector 858017** (the first array, 858016[], F) ran 26 October 20:02–20:31
and exited 1 (`p3/w2_a_collection_20261027.txt`).
- **Statuses:** 183 COMPLETE, 7,076 incomplete and 13 invalid. Archive `55448298…`
  (35 MB, 183 libraries) verified on deep-server.
- **This collection is a snapshot**, taken while W2 topup b's 381 subjobs ran.
  Its errors are nonetheless persistent: a read-only re-check of the 13 settings,
  using the runner's own `verified()`, fails again 18 hours later.
- **The failures:** eight "journal differs from its checkpoint" and five
  "journal length differs from its checkpoint".
  - Several journals are **exactly twice** their committed length (for example
    9,346 → 18,692 bytes; 1,007 → 2,014; 6,419 → 12,838): the same batches were
    written twice.
  - Completed shards carry extra appended bytes.
  - Nine of the settings already have FAILED markers, written when the runner
    refused to resume a mismatched journal.
- **Duplicate claims are live:** a census of `claimed/` filtered by setting and
  range finds 8 ranges with two claims each (2 W1, 6 W2) among 3,084 claims,
  and one range both queued and claimed. My first re-check over-counted claims
  because it matched range bounds without the setting.

**Interpretation: shards of one range have been run concurrently by two workers.**
- **The likely path is orphan republication.** `plan()` decides that an
  unfinished range has no live ticket or claim from directory listings of the
  shared `queue` and `claimed` directories. An NFS directory read of a large
  directory under concurrent renames can omit entries. A claimed range then
  looks orphaned, is republished, and is claimed by a second worker.
- This is a hypothesis consistent with the evidence, not yet reproduced.

**Integrity holds.**
- Every affected shard is rejected: by the collector's strict checks (committed
  prefix digest, exact length for terminal shards, strictly increasing
  identities) or by the runner's own refused recovery.
- Duplicated records cannot enter a library.
- The W1 libraries passed strict reconciliation, and W1 round 2 had no such
  errors.

**Cost.** Duplicated CPU, and affected settings ending FAILED or invalid. W2's
collection shows 98.5k outside-prefix CPU-h against 143.9k useful; most of that
belongs to incomplete settings and stays reusable. The duplication share is not
yet measured.

**Decision: continue W2 under its binding.**
- Restarting W2 under a repaired runner would discard its committed work.
- FAILED and invalid settings rerun from batch 0 in a later round under a
  repaired runner, as W1's did in round 2.
- **Repair for that runner:** never infer "no live ticket or claim" from a
  directory listing. Record each range's ticket and claim state in the
  setting's own directory, under the setting lock, and plan from that record.

### 9h. Round 3: authoritative range ownership (27 October 2026)

**Codex's review (board 2420–2423).** Review notes:
`notes/astra_w2_interim_review_20261027.md`, `notes/astra_w2_duplicate_mechanism_review_20261027.md` and
`notes/astra_w2_collection_review_20261027.md`.
- Codex reproduced the 9g path on the bound runner 1e35b94a. With the setting lock held, one omitted `claimed/` entry
  makes `plan()` republish a live range. `claim()` then admits a second owner, and two shard engines write
  byte-identical journal halves (318 bytes against a 159-byte checkpoint), which strict verification rejects.
- This shows the path is sufficient, not that this NFS read happened in production.
- **Recommendation:** let the running topup-b arrays finish; collect both waves strictly once all their arrays have
  ended; hold topup c until the runner is repaired; recover every final incomplete, FAILED and invalid setting under a
  fresh binding.

**The repair (runner `928265bd…`).** Ownership is decided only by each setting's own records:

| Record | Meaning |
|---|---|
| `r/<a>` | declares range [a, b), with b and the range's queue priority |
| `x/<a>.<k>` | names the owner of the range's k-th execution |
| `x/<a>.<k>.end` | its outcome: complete, censored, cancelled, failed, discarded or dead |

- **How records are written:** each record is created exclusively, by hard-linking a fully written temporary into
  place. A lost NFS reply is resolved by reading back a token. No record is ever replaced or removed.
- **Invariant:** execution k + 1 is created only after `x/<a>.<k>.end` exists with outcome censored or dead. Because
  each start record is created exclusively, a range has at most one live execution.
- **The range chain:** ranges form a chain from the pilot prefix (`r/<a>` → `r/<b>` → …), extended only at its end.
  No two ranges can share a start, and none can overlap another.
- **Reads use exact names, never a directory listing.** Records are never removed, so a cached positive is always
  true. A stale negative (a record not yet visible here) can only:
  - delay work, or
  - lead to an exclusive create that fails (`Behind`), after which the setting is passed over and retried.
- **Queue and claim entries are hints.**
  - `take()` resolves a hint against the records under the setting lock. It returns the execution this worker now
    owns, or spends the hint: a range live under another owner becomes that owner's claim hint, and a finished range
    or terminal setting drops it.
  - `plan()` consults no listing.
  - Recovery reads claim hints to find dead owners. With positive death evidence it ends that owner's execution as
    dead, replans the setting (republishing every runnable range's hint) and removes the hint.
- **Crash windows.** Every transition is ordered so that whatever survives a crash, a queue hint or a claim hint,
  leads a later worker to reconcile the setting. Fixture case 3 enumerates the eight windows.
- **A second hazard removed.** The bound runner's `ranges()` also lists the setting's own `ranges/` directory. If that
  listing omits an entry, planning recreates an existing range: it fails on the exclusive create, or, if the omitted
  range was the last and the new size differs, two overlapping ranges share a start. The ownership control (below) hit
  the first outcome. The chain removes this dependence too.
- **Unchanged:** the death evidence (an exact-owner certificate or PBS job_state F for executions; host and pid as
  well for locks), the lock protocol, the shard engine (`p2_stage1a.run_setting`), streams, caps and the library rule.
- **The collector** now:
  - walks the chain and the execution records;
  - requires every execution before the last to have ended censored or dead;
  - cross-checks, after a listing taken before the walks, that no range or execution record lies off the chain;
  - reports executions, dead executions and open executions for each setting and in total.

**Recovery: rerun every affected setting from batch 0.**
- **Scope:** every setting that round 2's final collections leave incomplete, invalid or FAILED, in both waves. Each
  reruns from its bound pilot prefix under `p3_settings_r3.json`, made by `select` from `p3_settings_r2.json`.
  Scientific fields, streams and caps are unchanged; denominators stay complete; FAILED is not treated as a final
  scientific exclusion.
- **No import of partial shards.**
  - Barry lifted the compute ceilings on 21 October (9d).
  - An importer would be a new data path across bindings, needing its own adversarial review.
  - Batch-zero reruns regenerate the old committed prefixes deterministically, so `p3_r2_determinism.py` can compare
    run2 against run3 and extend the 9c determinism coverage.
  - **The cost:** W2-a's 72.7k reusable outside-prefix CPU-h plus topup b's incomplete work, roughly a day at the
    7,000-CPU queued cap.
- **Old runs stay sealed:** `run` and `run2` are never modified, and their archives are kept. The final library set
  carries one binding per library across rounds 1–3.

**Dispatch.**
1. **Precondition:** every round-2 array and collector is F, and both final summaries (`run2/collect_W1_b.json`,
   `run2/collect_W2_b.json`) are fetched and verified.
2. **`s1b_round3_dispatch.sh`:**
   1. verify the stage checksums;
   2. require PBS to show round 2 finished, and only then install;
   3. gate both summaries: exact digest, binding, inventory, identities, counts, and errors one-to-one with invalid
      rows;
   4. run `select`;
   5. release the three round-2 reservations with PBS evidence;
   6. submit W1 round 3 (one subjob per 8 of its settings' 28 in-flight ranges, at most 170) and W2 round 3 (the CPUs
      left under the cap), each resumable.
3. **Later W2 arrays** go through `s1b_topup_dispatch.sh`. It now takes:
   - an explicit `WAVES` list, so a W2-only topup;
   - a required array reference `REF`, read with `qstat -x`, so a finished reference counts zero live subjobs instead
     of failing;
   - the releases as parameters.

   The node-install step is gone: round 3 installs everything.

**Successor recovery (runner `c56d0af6…`, commit 451e50e).**
- **The gap:** the first adversarial smoke (runner 928265bd, 30% listing omission) left one W2 range under a killed
  owner. Its successor's single recovery pass missed the claim hint, and the node idles on in-flight work without
  relaunching. This was a liveness gap, with no second writer.
- **The fix:** a worker keeps the hints of ranges it may own in `workers/held/<owner>`. A relaunched worker derives its
  slot predecessors' exact names (`<job>.<slot>r<g>n<nonce>`, g below its own), and the node certifies each before the
  next launch. At start, the worker ends as dead any execution a certified predecessor still owns, then replans. No
  listing is involved.

**Evidence (27 October 2026).** Receipts are in `analysis/fable/calibration/v2_dev/p3/`.

*Fixtures.* 41/41 pass on Python 3.12.13 and 3.11.13 locally, 3.12.3 on deep-server (six concurrent runs, all
passing) and **3.11.7 on kunanyi `/u`** (`r3_kunanyi_fixtures_20261027.txt`, from a scratch extract of stage
`ddb014b0`). The new cases:

| Case | Result |
|---|---|
| Every directory listing omitted | no hint for a live range; a forged duplicate hint admits no second writer |
| Eight concurrent claimant processes, half unable to see execution records | one execution record; only its owner given the range |
| A worker ended at each of eight transitions, with its lock left held | each reconciles to the serial library, with no superseded writer |
| A successor recovering its predecessor with every listing omitted | recovered |

On `/u`, `os.link` is exclusive (a second link reports EEXIST). The mount is NFS 4.1, `hard`, with default lookup
caching.

*Ownership control* (`p3_ownership_control.py`, `r3_ownership_control.json`):
- The bound runner 1e35b94a, with the global listings omitted, republishes a live range at priority 0, and owner B
  claims it beside owner A.
- Codex's reproduction on it doubles the journal (318 bytes against a 159-byte checkpoint).
- The candidate admits nobody, whether the global listings or every listing is omitted.

*Adversarial smokes* (deep-server; `smoke_r3.sh`, `smoke_omit.py`). Each worker's `queue/` and `claimed/` listings
drop every entry with probability 0.3. A random worker is killed with `kill -9` every 3 minutes for 30 minutes, and a
foreign-host ghost lock is certified at 15 minutes:

| Runner | Collections | Libraries vs `smoke_deep3` | Shards | Other |
|---|---|---|---|---|
| bound 1e35b94a (control) | both fail: 4 settings invalid ("journal length differs from its checkpoint") | — | 73 | 3 discarded tickets; reproduces the production defect |
| 928265bd | both pass | 4 identical | 44 | one W2 range stranded (above); 5 executions ended dead; 0 superseded |
| **c56d0af6** | **both pass** | **4 identical; W2 2 CAPPED, as the reference** | 47 | 0 open executions, 0 claims left, 0 superseded; 3 executions ended dead, 1 by its successor; determinism exit 0 |

The control's determinism comparison also passes, because duplicate execution writes byte-identical records. Only the
strict length and digest checks expose it, as Codex noted.

*Dispatch rehearsals* (stub PBS, `rehearsal_round3.sh`, on the real round-2 W1 and W2-a summaries):
- **Positive:** the gate gives 48 W1 and 7,089 W2 settings, 7,137 in all. The three reservations are released with
  PBS evidence. W1 round 3 is sized 168 × 8 and W2 706 × 8, bringing live requests to 6,994. A rerun resumes without a
  qsub.
- **Topup:** with W1 finished, a W2-only topup b is released and sized at 168 × 8, and its rerun resumes.
- **Negatives:** a tampered stage stops before install. An unfinished round-2 job stops before install. A wrong digest,
  or errors not one-to-one with the invalid rows, stops before the settings, ledger and PBS.

**W1 round 2 is final** (collector 860990 F, exit 1; `w1_r2b_collection_20261027.txt`). The archive `849cd0ba…` is
verified: 4,822 unique members, all 4,820 library digests match, and the embedded summary is identical.

| COMPLETE | CAPPED | FAILED | incomplete | invalid |
|---|---|---|---|---|
| 4,820 | 9 | 0 | 15 | 3 |

The invalid settings are s02311, s10624 and s14782, all journal mismatches of the duplicate-execution kind. No W1
claims remain. W1's round-3 inventory is therefore 15 + 3 = 18 settings.

**Repairs after Codex's round-3 review (board 2425–2427; `notes/astra_r3_package_review_20261027.md`; 29 October).**
Codex accepted the immutable range/execution design, the batch-zero recovery and the final W1 archive, and held
dispatch for two blockers.

1. **A crash before the held record (liveness).** `take()` created the execution and settled the hint before `work()`
   wrote `workers/held/<owner>`. A death in between, with the successor's listings omitted, left the execution open.
   - **Fix (runner `e261befa…`):** `take()` calls `intend(t)` under the setting lock just before the exclusive create,
     so the held record names t before the worker can own it. An intent left by an exclusive create that failed is
     harmless, because successor recovery acts only on executions whose owner is exactly the predecessor.
   - **Fixtures 42/42:** both crash points, with the lock left held and every listing omitted for the successor, give
     1 predecessor recovery, the serial library, 0 open executions and 0 superseded.
   - Codex's `reproduce_recovery_gaps.py`, run on `e261befa` from a scratch copy, reports `gap_reproduced: false`
     (`p3/codex_recovery_gaps_on_e261befa.json`).
2. **Capacity accounting.** A saved size could bypass the cap check on restart, and W2 was sized from a listing that
   might not yet show the just-accepted W1 jobs. The fixes:
   - **`kunanyi/s1b_capacity.sh`:** live CPUs, and accepted jobs in a run's journals that the live listing omits and
     PBS does not show finished. Operator `terminal` records count as finished.
   - **`s1b_submit.sh`:** any new array or collector request must fit under `CAP_CPUS` (7,000) with live requests, and
     no accepted job of the run may be unlisted. This is checked before preflight (so a refusal leaves no reservation)
     and again just before `request`, under the campaign lock. Submitter fixtures 16/16 under bash 5.3.9 and 4.2.46,
     including capacity refused before preflight, load rising during preflight, an unlisted accepted array refusing a
     topup, and a rejected array rechecked on resume.
   - **Dispatchers:** a saved size binds only once its submission journal exists, and is recomputed until then. Before
     sizing a wave, `wait_listed` waits for every accepted job of the run to be listed or finished, then fails closed.
3. **Stage identity (Codex's non-blocking point).** `s1b_round3_dispatch.sh` now requires `STAGE_SHA`, checks the
   extracted manifest byte for byte against the tar's own, then checks every file.

**Final round-2 inventories.**

| Wave | Collector | COMPLETE | CAPPED | FAILED | incomplete | invalid | Archive | Summary |
|---|---|---|---|---|---|---|---|---|
| W1 | 860990 | 4,820 | 9 | 0 | 15 | 3 | `849cd0ba` | `8d702807` |
| W2 | 860993 | 355 | 0 | 0 | 6,901 | 16 | `c760f0c6` | `beabe2d1` |

- Both are verified on deep-server: W2 has 357 unique members, all 355 library digests match, and the embedded summary
  is identical (`p3/w2_r2b_collection_20261029.txt`).
- **Round 3 reruns 18 W1 and 6,917 W2 settings, 6,935 in all.**
- **Corrected cost of batch-zero recovery** (Codex 2426): W2-a's incomplete rows held 96,293.8 CPU-h inside their
  verified prefixes and 72,689.0 outside, 168,982.8 in all. The final W2 incomplete rows hold 116,481.9 inside
  (including pilot CPU, which is reused) and 117,138.4 outside. The rerun therefore forfeits up to about 234k CPU-h,
  roughly 1.4 days at the cap. Invalid settings and losing duplicate executions are not counted. This is a historical
  bound, not a round-3 forecast.

**Closure evidence (29 October; stage `53603d42…`, commit 8be1b4e).** The stage is deterministic: two builds give the
same digest.
- **Fixtures:** 42/42 on Python 3.12.13 and 3.11.13 locally and in three concurrent deep-server runs (3.12.3).
- **Adversarial smoke** (runner e261befa; 30% omission of queue and claim entries, kill -9 every 3 minutes, ghost
  lock): both collections pass, 4 libraries identical to `smoke_deep3`, W2 2 CAPPED, 0 open executions, 0 claims
  left, 0 superseded, 3 predecessor recoveries, determinism exit 0 (`p3/smoke_r3c_*`).
- **Rehearsals** on the final summaries (`p3/rehearsal_round3_20261029.txt`):
  - **positive:** live requests 0, then W1 63 × 8, then 505, then W2 811 × 8, giving **6,994 CPUs**; a rerun resumes
    with no qsub;
  - **topup:** with W1 F, a W2-only topup b is released and sized at 63 × 8, giving 6,994; its rerun resumes;
  - **stale size:** a saved 874 with no journal and 72 CPUs of other load is resized to 802 × 8, giving 6,994;
  - **W1 array unlisted:** the submitter refuses even W1's collector (1 qsub), and a rerun once listed completes at
    6,994;
  - **W1 collector unlisted:** the dispatcher's wait fails closed before W2 (2 qsubs), and a rerun completes at 6,994;
  - **refusals:** a tampered file, a substituted tar, a self-consistent substituted manifest and an unfinished round-2
    job each stop before install; a wrong digest and errors not matching the invalid rows stop before the settings,
    ledger and PBS; a bad `REF` refuses with no qsub.
- **Prediction for production:** `p3_settings_r3.json` will be `8c46667e…`, since `select` over the same inputs is
  deterministic. That gives a check at dispatch.

**Held-publication repair and closure evidence (29 October; runner `92674ee8…`, stage `9b2786d6…`, commit d80a60b).**
Codex's closure review (board 2550) found that `hold()` updated the in-memory held set before the held file was
published, so a failed publication was not retried and a later crash could leave a range owned with no held record.
`hold()` now writes the prospective set and updates memory only after the write succeeds; the OSError path retries
the same publication before any execution can be created.
- **Fixtures:** 43/43 locally (3.12, 3.11) and in three concurrent deep-server runs (3.12.3), adding a first-publication
  failure at both crash points and a permanent publication failure that creates no execution and leaves the hint
  queued (`p3/r3_deep_fixtures_20261029.txt`). Codex's `check_recovery_closure.py` on 92674ee8 does not reproduce the
  gap in any of its four cases (`p3/codex_recovery_closure_on_92674ee8.json`).
- **Adversarial smoke** (runner 92674ee8; same faults as above): both collections pass, 4 libraries identical to
  `smoke_deep3`, 0 open executions, 0 claims left, 0 superseded, 2 predecessor recoveries, determinism exit 0 with
  2,310 records identical (`p3/smoke_r3d_*`).
- **Rehearsals** on stage 9b2786d6 (`p3/rehearsal_round3_20261029b.txt`): positive W1 63 × 8 and W2 811 × 8 at 6,994
  CPUs, resume with no qsub, W2 topup 63 × 8 at 6,994; a substituted manifest stops before install.
- **Production check:** `p3_settings_r3.json` must be `fa772829…` (the old `8c46667e…` was bound to runner e261befa).

**W1 round-3 collection and idle retirement (6 November).** Collector 876186: collection ok, 1 CAPPED, 17 incomplete,
0 errors, 0 dead and 0 open executions (archive `5e0de476…`, summary `020a9bbf…`). Only about 5,650 of 24,200 reserved
CPU-h were used: 7 of 63 subjobs ran 47.5 h and 56 retired after the node script's 30-minute idle budget. Cause, from the
setting records (`p3/w1_r3_collection_20261106.txt`): 16 of the 18 W1 settings carry no bound pilot, so round 3 replans
them from batch 0 under the cell prior, which predicts K hits within the first range. Each setting therefore starts as
one range of 0.7–3.8 M batches (14–18 h on one core) and fans out to about 28 ranges only after that range completes.
For those 15–18 hours W1 has 18 runnable ranges for 504 slots; the surplus subjobs saw only claims in flight and
retired well before the fan-out. This is the planner and idle budget behaving as specified: no range was stranded or
run twice. The cost is wall time, not correctness. W2 is unaffected, since its 6,917 first ranges exceed its 6,488 slots
and its fan-out keeps 11,165 hints queued. The remedy is a topup after fan-out, sent at once: W1_b `876850[]` (60 × 8,
collector 876851), with 333 W1 hints queued. Lesson: size a from-zero rerun array to its first ranges, then top up after
the fan-out, rather than raising the idle budget.
