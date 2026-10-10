# Development design run on 10× banks (v1, 9–10 October 2026)

This run is synthetic only. It computes no empirical T1–T4 and no empirical
p-value. Observed calibration summaries C are used only as already exposed
in E20, to build the libraries at the observed C. It is development evidence
under development seeds, not validation. It follows Barry's adoption of ar_cat
as the primary development null, with iid as a mandatory sensitivity
(`docs/decisions/d36e602c…`).

**Where it ran.**
- `deep-server`, tmux sessions `fable_bank10x` and then `fable_design`.
- Run directory: `/data/fable/vortex/banks10x_20261009T041220Z`.
- **Banks:** source commit `d16fe45`, hashes in `banks_source_sha256.txt`.
- **Design run:** source commit `0430737`, hashes in `source_sha256.txt`.
- All source hashes match their commits.
- Bank files (17 GB) and the coverage and T files stay on deep-server. They
  are hashed in `banks_sha256.txt`, `coverage_sha256.txt` and
  `other_sha256.txt`.

## 1. Banks (`build_bank.py`)

- **Size and seeds.** For each of ar_cat and iid: 9 populations × 20 shards ×
  10^8 prior-(b) draws, i.e. 2×10^9 per population. Seeds 20261019000–
  20261019359. NumPy 1.26.4.
- **Selected runs.** 13.5–29.9 million per population (ar_cat) and 12.8–28.4
  million (iid). Per-shard counts are in `bank_meta.json`.
- **Overflow.** At most 2.8% of draws (the wild dog).
- **Measured cost** (`build_resources.txt`): 278,916 CPU-seconds, i.e. 77.5
  core-hours for both variants. Wall time 2 h 00 min on 40 processes.

## 2. Library radii in the constructed banks (`coverage_summary.md`)

- **Outer datasets.** 20,000 fresh selected datasets per prior-predictive
  scenario and 2,000 per fixed-parameter corner. Task seeds 2026102100–
  2026102117.
- **Radius.** The largest K-th neighbour distance across the nine (K = 2,000),
  measured in the banks as built, i.e. at 10×.

| Scenario | q0.50 | q0.90 | q0.95 | q0.99 | q0.999 |
|---|---:|---:|---:|---:|---:|
| ar_cat null, prior-predictive | 0.35 | 0.73 | 0.99 | 1.58 | 3.92 |
| ar_cat M_A at β_min | 0.34 | 0.74 | 1.00 | 1.61 | 4.37 |
| ar_cat M_A at Δ10 = 0.5 | 0.44 | 0.89 | 1.12 | 1.89 | 5.03 |
| ar_cat high σ corner | 0.36 | 0.57 | 0.66 | 1.00 | 1.50 |
| ar_cat low survival corner | 0.27 | 0.52 | 0.57 | 0.79 | 1.15 |
| ar_cat strong environment corner | 0.30 | 0.55 | 0.63 | 0.91 | 1.10 |
| iid null, prior-predictive | 0.34 | 0.72 | 0.95 | 1.45 | 3.49 |

- **The projection held.** The 0.7 projection from the 2×10^8 bank was
  0.35 / 0.99 / 1.60 / 3.84 at q0.50 / q0.95 / q0.99 / q0.999. The measured
  values are 0.35 / 0.99 / 1.58 / 3.92.
- **Thinned-bank check.** The 10% thinned bank against its projection
  d_(10K) agrees to within 0.01 at every reported quantile.
- **Corners are better represented** than the prior-predictive scenario,
  because they sit at library-median parameters.

## 3. Effect target β_min (§3.3) and corners (§4.3) under ar_cat

Output: `effect_target_ar_cat.json`. Seed 20261020; 10^5 paths per grid value.

- **Library parameters.** Each population's library at its observed C has
  2,000 nearest runs. The component-wise medians pooled across the nine are:

  | s | f | σ | ρ | p_c | δ |
  |---:|---:|---:|---:|---:|---:|
  | 0.734 | 0.141 | 0.498 | 0.472 | 0.028 | 0.750 |

  The baseline parameter sum s + f is 0.875. That is not a measured marginal
  growth rate, which also depends on σ, ρ and the catastrophes.
- **Baseline risk.** Under the null from N = 20, P(count ≤ 1 within 10 years)
  is 0.422, below 0.85, so N0 = 20.
- **The grid.** Increase in that probability under M_A:

  | Δ10 | 0.025 | 0.050 | **0.075** | 0.10 | 0.20 | 0.30 | 0.50 |
  |---|---:|---:|---:|---:|---:|---:|---:|
  | Increase | +0.042 | +0.087 | **+0.130** | +0.174 | +0.330 | +0.437 | +0.545 |

  The increase saturates near +0.58.
- **β_min is at Δ10 = 0.075 (β = 0.975).**
  - That is g(10) = 0.925, with g(5) = 0.84 and g(2) = 0.63.
  - g multiplies the survival *odds* and the recruitment *rate*. It does not
    multiply survival probability.
  - Feedback this small raises extinction risk by more than 0.10 because the
    calibrated populations are already declining close to the absorbing
    boundary.
- **Corners.** Each population is fixed at its library medians, with σ at
  the library 90th percentile, s at the 10th, or ρ and p_c at the 90th.
  - Numeric values: `scenarios.json`.
  - Selection rates at those fixed values are 1.25×10^-5 to 0.068. The
    lowest are the wild dog and golden plover under low survival, which cost
    about 10^5 draws per selected trajectory. All corners are feasible.

## 3b. Empirical position (C only)

Script: `empirical_position.py`, hashed in `position_src_sha256.txt`. Outputs:
`empirical_position_{ar_cat,iid}.json`.

The empirical position is the largest K-th neighbour distance of the
observed C across the nine. Each value is compared with the null
prior-predictive outer datasets from §2.

| Bank | Largest (population) | Share of null outer datasets at or below |
|---|---|---:|
| ar_cat | 0.433 (turtle B) | 0.639 |
| iid | 1.073 (turtle B; turtle A 0.913) | 0.969 |

- **Under the primary null** the observed series' largest radius is typical,
  near the 64th percentile. A typical radius does not by itself establish
  local conditional calibration (Codex 1313).
- **Under the iid sensitivity** the turtles are in the tail, near the 97th
  percentile. That sensitivity is reported with its distances (§3.4).
- **Exposure.** These positions use only the already-exposed C.

## 4. Measured cost at production counts

**Cost run** (`e2e_cost_*`): ar_cat null, prior-predictive; 4 datasets; 32 R
workers; seed 20261022.
- **Measured:** 5,112.7 CPU-seconds in total, including setup. Setup (bank
  loading and tree building) took 495 s of wall time.
- **Per dataset:** about 1,154 CPU-seconds, *derived* by subtracting that
  setup on the assumption that it ran on a single core (Codex 1313).
- Wall time about 58 s per dataset; peak RSS 28 GB, because the banks are held
  in memory.
- All four trials were accepted, with no fit failures. nlminb was needed in
  35–299 of 16,004 fits per dataset.

**Power screen** (`../power_screen_v1/`): 150 trials and five setups.
- **Measured:** 205,440 CPU-seconds, i.e. **1,370 CPU-seconds (0.38
  core-hours) per trial, all-in**. This is the basis for the inventory below.
- **Throughput:** about 105 trials per hour after loading, with three
  concurrent processes × 18 workers (Codex 1314).

**Validation inventory** (§4.3, plus the §3.4 stress check), at 0.38
core-hours per trial:

| Component | Datasets | Core-hours |
|---|---:|---:|
| Null scenarios (4 × 1,000) | 4,000 | 1,522 |
| Alternatives incl. power at β_min (10 × 300) | 3,000 | 1,142 |
| Detection curve: M_A at Δ10 = 0.3 and 0.5 (2 × 300; proposed) | 600 | 228 |
| Fitted-parameter predictive stress check | 300 | 114 |
| Empirical primary, RI+slope and iid sensitivities, second-bank stability | about 5 | about 5 |
| Banks: production ar_cat, second ar_cat stability bank, iid sensitivity bank | — | about 120 |
| **Total** | about 7,905 | **about 3,130** |

- **Wall time.** Roughly 75 hours on deep-server at the observed 105 trials
  per hour, plus about 3 hours for banks. This is a small-pilot projection.
- **Not yet measured:**
  - the corners, whose low-selection populations cost more per trajectory;
  - the M_D and M_O generators, which are not yet implemented and whose cost
    is assumed equal.

## 5. Implications

- **O1 at β_min is very likely unattainable with nine series.**
  - At β_min, g(10) = 0.925, and the library radii are indistinguishable from
    the null's, so C barely moves.
  - The power screen (`../power_screen_v1/`) gives 1/30 detections at
    β_min.
- **The risk-defined effect target is a scientific choice.** It answers "a
  feedback that raises 10-year extinction risk from N = 20 by 0.10". Under
  ar_cat at the calibrated parameters, that feedback is small. Reporting O3
  (insufficient discrimination) at β_min, together with a detectable-effect
  curve, is the honest pre-registered consequence.
- **Changing the effect target after seeing power** would be an adaptive
  amendment, and it is for Barry to decide.
