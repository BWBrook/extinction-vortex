# Stage 1a sampling pilot: no-fit report

Fable, 16 October 2026. This reports the bounded kunanyi pilot specified in
Astra's review 1657 §4, under the report rule bound into the settings
(`report_rule`). No fits, p-values or empirical T1–T4 tests. These are
exposed development outers (b1/b3/b5/b16, trial IDs 0–9), not validation.
- Script: `analysis/fable/calibration/v2_dev/p2_report.py`.
- Outputs: `analysis/fable/calibration/v2_dev/p2/s1a_main/` (`s1a_report.json`,
  `collect_deep.json`, `s1a_tables.md`).

## 1. Execution

- **Dispatch:** 16 October, about 16:31 AEDT, after Astra's clearance in 1735.
  45 × 8-core jobs (820683–820728) and collector 820729. Every node job
  exited 0, and the collector exited 0.
- **Archive:** `main.tar.gz` (`3e18e5b8…`, 29 MB). It was verified on
  deep-server and re-collected there independently, with rows identical to
  kunanyi's collection.
  - `collection_ok`: true; `provenance_complete`: true (360/360 worker
    receipts, 21 hosts, peak RSS 0.085 GiB).
  - `run_complete`: false, because 7 settings were censored (§2).
- **Exposure:** 3.491e+12 proposals (99.6% of the planned
  3.504e+12), 1.221e+11 simulated paths and
  2.08e+09 S/A-selected paths. 322,736 retained hits,
  9,097 of them on a ball boundary.
- **Cost:** 733.9 worker CPU-h.
  - Allocated node time is about 767 CPU-h: 8 × the slowest
    worker per job, excluding setup. PBS accounting is still to be read.
  - With the smoke (0.445) and the collector (0.07), the total is about 770
    CPU-h, within the 1,000 CPU-h ceiling.
- **Budget accuracy:** realised throughput divided by the smoke estimate had a
  median of 0.997 (range 0.875–1.163).
  Job busy times were 2.05–2.58 h against an expected 2.06 h.

## 2. Completion

| n | Hit stop (K reached) | Budget | Censored |
|---|---|---|---|
| 0 | 0 | 359 | 1 |
| 30 | 1 | 354 | 5 |
| 300 | 0 | 359 | 1 |

- **Only one setting reached K = 2,000:** setting 772 (crow, null_low_s/7,
  n = 30). *Corrected 16 Oct: the first issue said null_low_s/8, which is
  setting 775 and ended at its budget with 1,722 hits.*
  All other completed settings ended at their proposal budget with fewer than
  2,000 hits, and the seven censored settings stopped at the wall deadline.
  Their times to K are projections (§3).
- **Censored (7):** all on workers 0–15, the two jobs that started first and
  ran to their deadline at walltime − 10 min. Their exposure is retained.
  - Settings: 547 (golden_plover, MA_betamin/2, n = 30, 467 hits), 576 (golden_plover, MA_d10_0.5/2, n = 0, 0 hits), 893 (wood_turtle_A, null_low_s/7, n = 300, 7 hits), 931 (wood_turtle_A, MA_d10_0.5/0, n = 30, 297 hits), 985 (wood_turtle_B, null_prior_predictive/8, n = 30, 130 hits), 994 (wood_turtle_B, null_low_s/1, n = 30, 14 hits), 1078 (wood_turtle_B, MA_d10_0.5/9, n = 30, 1036 hits).
  - Setting 576 was censored before any proposal. It is a no-exposure failure
    and is excluded from cost means.
- **Zero hits with exposure (4, all n = 300):** 242 (ms_woodpecker, null_prior_predictive/0: ≥ 608 CPU-h); 512 (golden_plover, null_low_s/0: ≥ 586 CPU-h); 536 (golden_plover, null_low_s/8: ≥ 588 CPU-h); 833 (hawaiian_crow, MA_d10_0.5/7: ≥ 559 CPU-h).
  These are approximate one-sided expected-cost lower limits from the exact
  suffix retention bound, not minimum run times. The costs are unresolved.
  *Corrected 16 Oct per Astra 1755; the first issue used 3/N.*

## 3. Retention and time to 2,000 (no fits)

**Report rule.**
- Full-stream hits/proposals is descriptive.
- Intervals come from the post-prefix suffix: Clopper–Pearson for a setting
  ending at its budget, and the exact negative-binomial interval for the one
  hit-stopped setting.
- Censored rows carry sensitivity intervals only.
- Time to K is the projected **expected** worker CPU cost at observed
  throughput: observed for 1 setting, projected for 1,068, projected with
  sensitivity-only intervals for 6 censored, and unresolved for 4 zero-hit.
- Intervals are suffix retention intervals transformed at observed
  throughput. They bound expected cost; they do not predict a future run's
  time and exclude throughput variation.
- Settings with only 1–3 hits have very wide intervals; see the most
  expensive settings below.

**Projected expected worker CPU-hours to K = 2,000 per setting** (median [IQR], largest resolved point estimate; resolved settings of 40, with unresolved zero-hit or no-exposure settings counted)

| Population | n = 0 | n = 30 | n = 300 |
|---|---|---|---|
| wild_dog | 3.8 [3.7–4.1], 4.9 | 4.8 [2.0–14.6], 85.7 | 14.8 [5.5–153], 926 |
| marmot | 3.2 [3.2–3.4], 3.8 | 3.8 [2.8–11.0], 301 | 27.4 [10.0–92.9], 914 |
| ms_woodpecker | 2.6 [2.5–2.7], 3.1 | 4.6 [2.6–23.0], 166 | 32.8 [12.9–131], 1,825 (1 unresolved) |
| rc_woodpecker | 2.5 [2.3–2.6], 2.9 | 4.3 [2.6–7.9], 149 | 18.8 [10.1–36.1], 368 |
| golden_plover | 3.4 [3.1–3.6], 3.9 (1 unresolved) | 4.3 [2.0–12.1], 139 | 17.2 [5.4–111], 1,848 (2 unresolved) |
| whooping_crane | 2.8 [2.6–2.9], 3.3 | 3.3 [2.0–7.5], 78.7 | 19.2 [7.8–41.0], 270 |
| hawaiian_crow | 1.9 [1.8–2.0], 2.2 | 3.2 [1.5–7.9], 166 | 21.7 [5.7–68.5], 1,770 (1 unresolved) |
| wood_turtle_A | 3.1 [3.0–3.3], 3.7 | 3.9 [2.7–15.4], 363 | 36.1 [11.3–77.4], 945 |
| wood_turtle_B | 3.2 [2.9–3.5], 3.8 | 3.2 [2.3–8.6], 51.1 | 16.8 [6.9–35.4], 360 |

By scenario (resolved settings of 90; unresolved counted):

| Scenario | n = 0 | n = 30 | n = 300 |
|---|---|---|---|
| null_prior_predictive | 3.0 [2.6–3.4], 4.3 | 2.9 [1.8–4.8], 139 | 7.2 [4.3–16.7], 125 (1 unresolved) |
| null_low_s | 3.0 [2.6–3.4], 4.8 | 5.5 [3.2–17.7], 301 | 67.8 [20.6–244], 1,848 (2 unresolved) |
| MA_betamin | 3.0 [2.6–3.5], 4.9 | 3.1 [2.3–8.4], 363 | 15.6 [5.3–31.0], 945 |
| MA_d10_0.5 | 3.0 [2.5–3.4], 4.1 (1 unresolved) | 4.6 [2.6–17.8], 361 | 32.8 [15.4–74.5], 1,825 (1 unresolved) |

**Most expensive settings** (projected expected CPU-h to K; interval: suffix retention interval transformed at observed throughput, for expected cost, not a run-time prediction)

| Setting | Population | Outer | n | Hits | CPU-h | 95% interval | Kind |
|---|---|---|---|---|---|---|---|
| 524 | golden_plover | null_low_s/4 | 300 | 1 | 1,848 | 332–73,001 | projected |
| 335 | ms_woodpecker | MA_d10_0.5/1 | 300 | 1 | 1,825 | 328–72,081 | projected |
| 836 | hawaiian_crow | MA_d10_0.5/8 | 300 | 1 | 1,770 | 318–69,907 | projected |
| 905 | wood_turtle_A | MA_betamin/1 | 300 | 2 | 945 | 262–7,800 | projected |
| 38 | wild_dog | null_low_s/2 | 300 | 2 | 926 | 256–7,644 | projected |
| 155 | marmot | null_low_s/1 | 300 | 2 | 914 | 253–7,549 | projected |
| 515 | golden_plover | null_low_s/1 | 300 | 2 | 897 | 248–7,405 | projected |
| 53 | wild_dog | null_low_s/7 | 300 | 2 | 891 | 247–7,356 | projected |
| 50 | wild_dog | null_low_s/6 | 300 | 2 | 841 | 233–6,941 | projected |
| 341 | ms_woodpecker | MA_d10_0.5/3 | 300 | 3 | 618 | 211–2,997 | projected |

**Stage 1b inventory by cell** (12 largest; mean of 10 pilot outers x 200)

| Population | Scenario | n | Mean CPU-h | Max CPU-h | CPU-h for 200 outers | Unresolved |
|---|---|---|---|---|---|---|
| golden_plover | null_low_s | 300 | 568 | 1,848 | 113,664 | 2 |
| wild_dog | null_low_s | 300 | 505 | 926 | 101,013 | 0 |
| ms_woodpecker | MA_d10_0.5 | 300 | 338 | 1,825 | 67,557 | 0 |
| marmot | null_low_s | 300 | 319 | 914 | 63,738 | 0 |
| hawaiian_crow | MA_d10_0.5 | 300 | 285 | 1,770 | 57,065 | 1 |
| ms_woodpecker | null_low_s | 300 | 171 | 355 | 34,234 | 0 |
| wood_turtle_A | MA_betamin | 300 | 130 | 945 | 26,040 | 0 |
| wood_turtle_A | null_low_s | 300 | 114 | 229 | 22,797 | 0 |
| wood_turtle_B | null_low_s | 300 | 109 | 360 | 21,800 | 0 |
| hawaiian_crow | MA_betamin | 300 | 108 | 584 | 21,693 | 0 |
| wild_dog | MA_d10_0.5 | 300 | 106 | 608 | 21,247 | 0 |
| marmot | MA_d10_0.5 | 300 | 96.4 | 363 | 19,273 | 0 |

**Reading.**
- **The n = 0 controls are cheap and uniform:** about 1–5 CPU-h each.
- **Informative evidence makes reference sampling heavy-tailed,** most of all
  at n = 300 and in the null_low_s and MA_d10_0.5 scenarios.
  - The median n = 300 setting needs about 20 CPU-h; the upper decile needs
    about 250 or more.
  - The three most expensive projections are about 1,800 CPU-h, each from a
    single hit, with intervals of about 300 to 70,000 CPU-h.
- **The tails are outer-specific,** not population-uniform, so a few named
  outers dominate the total.

## 4. Complete-nine-population availability

A dataset is one (scenario, trial, n) combination, and it needs libraries for
all nine populations.
- **At the pilot budget,** no dataset is complete for either n.
- **Projected,** counting the datasets whose slowest population needs at most
  the cap (of 40):

| Cap per population (CPU-h) | 10 | 25 | 50 | 100 | 250 | 500 | 1000 |
|---|---|---|---|---|---|---|---|
| n = 30 | 6 | 14 | 23 | 29 | 37 | 40 | 40 |
| n = 300 | 0 | 2 | 8 | 13 | 19 | 23 | 33 |

- At n = 300, 4 datasets also contain an
  unresolved (zero-hit) population.
- A dataset's cost is the sum over its nine populations; the per-dataset sums
  are in `s1a_report.json`.

## 5. Stage 1b sampling inventory (projection)

**Planned noisy design:** 9 populations × 4 scenarios × n ∈ {30, 300} × 200
outers (14,400 population-outer-cells), plus 7,200 n = 0 controls: 21,600
libraries at K = 2,000.
- **Method:** each cell's mean over its 10 pilot outers, × 200, in gross
  worker CPU-hours to K. Zero-hit settings enter at their lower limits, so
  this is not an upper bound.

| Part | Projected gross worker CPU-h |
|---|---|
| n = 0 controls | 21,340 |
| n = 30 | 117,749 |
| n = 300 | 722,608 |
| **Total** | **861,698** |

- **Additional work:** subtracting the pilot's 734 spent worker CPU-h gives
  860,964 additional. Allocated node-hours are larger; see the Stage 1b design.
- **Uncertainty (corrected 16 Oct per Astra 1755).** Resampling the 10 pilot
  outers per cell gives 749,078–981,232 (5–95%). Resampling whole nine-population
  outers within each scenario gives 746,020–984,217.
  - Both are **conditional empirical resampling spreads of plug-in costs,
    with zero-hit costs fixed at their lower limits**, not calibrated budget
    ranges.
  - They exclude per-setting retention uncertainty, the unknown upper costs of
    zero-hit settings, unseen expensive outers, and future throughput.
  - Astra's two illustrations show what this means:
    - zero-hit costs × 10 gives about 1.28 × 10⁶;
    - setting 524 at its interval's upper end gives about 2.28 × 10⁶,
      uncapped.
  - A defensible upper allowance needs enforceable caps (Stage 1b design),
    not more bootstrap repetitions.
- **The point projection is about 8.6 times the "100K CPU hours"** Barry
  described on 15 October. Its n = 300 part is 84%.
- **Five low-s or d10 n = 300 cells** (golden plover, wild dog, marmot, crow
  and woodpecker) account for 403,037.
- **Bounded alternatives:**
  - n = 30 plus controls: 139,090;
  - 50 outers per cell: 215,424;
  - 25 per cell: 107,712;
  - Astra's θ-tilted reserve.
- **Barry's 16 October inclination is the full design.** The concrete package
  (stable IDs, ordered sharding, caps, waves, inventory and the priced
  library check) is `notes/vortex_stage1b_design_20261016.md`.
- **Any outer reduction must be declared before launch,** with named IDs and
  fixed denominators. Cheaply completing outers must not be selected, and no
  failed population may be omitted (1657 §4).

## 6. Stop

The pilot stops here, as specified.
- A separate fitted-stage (Stage 1c) draft is in
  `notes/vortex_stage1c_fitted_draft_20261016.md`.
- Stage 1b and Stage 1c remain uncommissioned. Their scale is a resource and
  design decision for Barry, after Astra's audit of this report.
