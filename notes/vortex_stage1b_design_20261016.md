# Stage 1b: full noisy-design sampling package (for Astra's check and Barry's decision)

Fable, 16 October 2026. This responds to Astra's 1755
(`notes/astra_stage1bc_design_review_20261016.md` P1/P2 and the cost review).
It specifies, as a design, the full 200-outer sampling campaign that Barry is
inclined to authorise. Nothing is implemented or dispatched yet.

**Barry, 16 October 2026** (Claude chat, exact; an inclination, not yet an
authorisation): "Regarding compute, I'm strongly inclined to authorise the
full planned design."

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
q, radius, recorded series) is exported once on deep-server for the 1,800
population-outer pairs beyond the pilot's 360, with one bank pass, exactly as
`p2_stage1a.py export` did.

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

**Per-setting cap: 2,000 worker CPU-h,** converted to a proposal cap at the
setting's pilot throughput (the median for unseen trials in the same cell).
- The cap bounds the unresolved settings and the single-hit tails, where the
  largest interval reaches about 70,000 h.
- Reaching it is a **failure to fill K within budget**, which Astra calls a
  support failure for scoring. It is not evidence that the target has zero
  support. It stays in every denominator.

| Per-setting cap | Expected gross worker CPU-h | Expected failures to fill (of 21,600) | Datasets with a failure (n = 30; n = 300) |
|---|---|---|---|
| 500 h | 713,854 | 400 | 0; 340 |
| 1,000 h | 812,835 | 60 | 0; 60 |
| **2,000 h** | **861,698** | **0** | **0; 0** |

These are point projections. Unseen outers will add some failures at any cap.

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

## 8. Decisions (Barry, 16 October 2026; board 1759)

"Decisions: 1 and 2 are both fully authorised."
1. **Stage 1b sampling is authorised:** W1 then W2, within allocated ceilings
   of 200,000 / 1,000,000 / 1,200,000 CPU-h, with a 2,000 CPU-h per-setting
   cap.
2. **Stage 1c fitting is authorised,** with the gate meaning of
   `notes/vortex_stage1c_fitted_draft_20261016.md` §6.

Each executable package is still checked by Astra before dispatch.
