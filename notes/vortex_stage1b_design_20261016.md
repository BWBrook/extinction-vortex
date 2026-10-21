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

| Group | Actual / projected | Median throughput ratio | Median hit-rate ratio |
|---|---|---|---|
| Pilot outers (trials 0–9), n = 0 | 0.97 | 0.98 | 1.00 |
| Pilot outers (trials 0–9), n = 30 | 0.97 | 1.00 | 0.45 |
| Unseen outers, n = 0 | 0.98 | 0.99 | 1.00 |
| **Unseen outers, n = 30** | **1.19** | **1.01** | **1.05** |

The hit-rate ratio is against the cell's pooled prior, which is weighted by
proposals, so a typical pilot outer sits below it.

- **Kunanyi's throughput and the pilot outers were projected correctly.**
- **The excess is in the tail of unseen n = 30 outers.** Each cell's 10 pilot
  outers underestimate the cell mean of a heavy-tailed cost. The median setting
  is on projection; the costly unseen outers lie in the tail.
- **Discards:** 6,638 CPU-h (6%) on COMPLETE n = 30 settings is the planned
  parallel overshoot. The 20,029 CPU-h on incomplete n = 30 settings is the
  defect's damage: for example, s07690 has 29 ranges with the first blocked
  while 28 finished.
- **Restarting the 4,847 open settings** is estimated at about 92k CPU-h
  (cell means of realised costs, or 1.25× round-1 spend where larger).
- **W2 projection** (722,608 expected): with the same unseen-outer factor of
  1.2–1.35 and the planned overshoot, roughly 0.9–1.1M worker CPU-h. That is
  about two weeks at 2,600–3,000 cores.

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
  - total spending is the sum of reserve lines, reported separately.
- **The per-setting 2,000 h proposal cap is unchanged.** It is a stopping rule,
  CAPPED is a reported outcome, and changing it would change the design.

**Shapes.** kunanyi limits a user to 3,000 running CPUs, 7,000 queued CPUs
(`max_queued_res.ncpus`) and 4,000 queued jobs. Round 2 therefore opens with:
- W1 r2: 300 × 8 × 48 h;
- W2 a: 570 × 8 × 48 h;
- 6,960 CPUs plus two collectors in all.

Later W2 arrays follow as earlier ones finish, each reserved and released the
same way. Over-provisioning costs only minutes, because a worker exits when
the queue is empty.
