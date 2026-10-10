# Validation freeze package (complete, for Astra's review)

**Status: complete for review, 11 October 2026, Hobart (Fable). Not frozen.**
This collects in one place everything that §4.3 validation and the empirical
test will run on, as Astra's 0.8 and 0.9 reviews (1348, 1368) asked.
- All values come from the designated-bank run
  (`/data/fable/vortex/production_banks_20261010T081726Z`). Its receipts are
  archived in
  [`analysis/fable/calibration/freeze_v1/`](../analysis/fable/calibration/freeze_v1/).
- **The freeze** takes effect when Astra accepts this package and the commit
  carrying it is named as frozen.
- **Validation then starts** only with Barry's go-ahead for the compute,
  per §4.1: about 3,000 core-hours, roughly 75 hours on deep-server.

No empirical conditional-null p-value has been computed or inspected.

## 1. Settled scientific choices (Barry)

- **Target:** reconstructed T1–T4. The random-intercept estimator is primary;
  random intercept and slope is a mandatory sensitivity; T5 and scaling are
  descriptive (`approve_ri_primary`, 9 October).
- **Null:** ar_cat is the primary development null; iid is a mandatory
  sensitivity (`approve_ar_cat_primary`, 9 October).
- **Effect target:** the risk-defined β_min recipe of §3.3, retained.

## 2. Estimator and reference settings

| Item | Frozen value |
|---|---|
| Estimator | `tstats_batch.R`: nlme `lme`, random intercept, `corAR1(form = ~ s \| pop)`, ML; optim then nlminb, no further restarts; gaps never annualised; endpoint set to 1 for log growth |
| Calibration summaries | mean squared non-final log change; lag-1 ACF (0 if constant, flagged); fraction of increases; MAD-scaled within the bank; zero-MAD features dropped and flagged |
| Library | k-NN, K = 2,000, no distance cutoff; bank ≥ K valid runs (code-enforced) |
| Replicates | R_train = R_test = 2,000; Ledoit–Wolf if cond > 10^6; p = (1 + #{D_test ≥ D_obs}) / (R_test + 1) |
| Outcomes | reject / accept / indeterminate (`indet_sampling` (no selected draw within 10^6 for some population; no fits; never replaced), `indet_malformed`, `indet_obsfit`, `indet_train` (> 2% of training fits failed), `indet_cov`, `indet_straddle`); fixed denominators |
| Fit-failure accounting | numerator: datasets with any missing T1–T4 among the 2R + 1 per fitted trial (a missing or malformed T file counts all); sampling failures excluded and reported separately |
| Provenance per trial | selected draw per population: parameters (including M_D shift and step time), recorded counts, latent counts under M_O; K-th distances; flags; fallback count |
| Selection and cap | exact matched selection S on recorded counts; cap event A (counts and Poisson rates ≤ 10^9) |
| Prior | (b): logit s ~ N(0, 1.5²); log f ~ U(log 0.01, log 2); σ ~ U(0.02, 1); ρ ~ U(0, 0.9); p_c ~ U(0, 0.05); δ ~ U(0.5, 0.95) |
| Code | commit `49f65ce` (`bank.py`, `e2e_benchmark.py`, `tstats_batch.R`, `score_discrimination.py` contract v3, `make_manifest.py`, `validate.py`, `collect_validation.py`, `run_validation.sh`, `empirical_q1.py`); all 17 staged source hashes match it (`freeze_v1/freeze_source_sha256.txt`) |
| Runtime | deep-server, Linux 6.8.0; Python 3.12.3, NumPy 1.26.4, SciPy 1.11.4; R 4.6.1, nlme 3.1.171 (`freeze_v1/runtime_versions.txt`) |
| Receipts | `test_bank.py` 28/28 and `test_validation.py` 19/19 on the staged freeze source (`freeze_v1/receipt_*.txt`) |

## 3. Designated banks

All are 2 × 10^9 prior-(b) draws per population, in 20 shards of 10^8, built
with `build_bank.py` from source staged at `afe9bca`.
- `bank.py`, `build_bank.py`, `effect_target.py` and `empirical_position.py`
  are byte-identical in `49f65ce`.
- `run_production_banks.sh` is committed unchanged in `a31e5bc`.
- **Measured cost:** 452,339 CPU-seconds (125.6 core-hours) for the three
  banks; 2 h 52 min of wall time on 56 processes.

| Bank | Variant | Seed family (task 0–179) | Selected runs per population | Overflow (max) | Size | Use | Shard hashes |
|---|---|---|---|---:|---:|---|---|
| Primary | ar_cat | 8,100,000,000,000 + task | 13.46–29.90 million | 2.80% | 11 GB | validation, empirical Q1, all reused sensitivities | `freeze_v1/bank_primary_sha256.txt` |
| Stability | ar_cat | 8,200,000,000,000 + task | 13.46–29.91 million | 2.80% | 11 GB | descriptive second-bank comparison | `freeze_v1/bank_stability_sha256.txt` |
| iid | iid | 8,300,000,000,000 + task | 12.77–28.44 million | 2.83% | 6.2 GB | plain-M0 mandatory sensitivity | `freeze_v1/bank_iid_sha256.txt` |

Per-shard seeds, draw counts, selected counts and overflow are in
`freeze_v1/bank_*_meta.json`. `bank.load_bank` checks these when it loads a
bank.

## 4. Recomputed on the primary bank

These use the fixed recipes (`freeze_v1/effect_target_ar_cat.json`). The
development values are in brackets.
- **β_min = 0.974519, i.e. Δ10 = 0.075** [unchanged].
  - The pooled library medians are s 0.732, f 0.146, σ 0.498, ρ 0.469,
    p_c 0.0277, δ 0.753.
  - P(count ≤ 1 within 10 years from N = 20) rises from 0.414 under the null
    to 0.550 under M_A, an increase of +0.136 [+0.130].
  - This is the minimum *risk-defined* effect, not a demonstrated minimum
    detectable effect.
- **Corners** (`freeze_v1/corners.json`; per-population fixed parameters):
  - high σ, low s and strong environment, each by the fixed quantile recipe;
  - selection rates are 2.35 × 10^-5 to 0.067, the lowest being the wild dog
    under low s; all are feasible.
- **Empirical K-th-neighbour position** (C only;
  `freeze_v1/empirical_position_*.json`):
  - ar_cat largest 0.429 (turtle B), in **bin 4** (0.4049–0.5613) [0.433];
  - iid largest 1.067 (turtle B; turtle A 0.905), above the top cut point
    [1.073].
- **Generation timings** (`freeze_v1/gen_times.json`): 4.9–9.1 CPU-seconds
  per dataset. This run used the development β_min, which equals the
  recomputed value. It times generation only.

## 5. Radius strata (frozen)

- **Bins:** (0, 0.2050], (0.2050, 0.2956], (0.2956, 0.4049], (0.4049, 0.5613],
  (0.5613, ∞). A tie goes to the lower bin.
- **Source:** 20,000 C-only ar_cat null prior-predictive outer datasets against
  the 10× development bank (§3.4 step 3).

## 6. Validation run definition and streams

**Executable.**
- **The manifest** is `freeze_v1/validation_manifest.json`. It has 17 blocks,
  170 chunks and 7,900 trials, with output root
  `/data/fable/vortex/validation_v1`, the primary bank, β_min = 0.974519 and
  `code_commit` `49f65ce`.
- **The stress sets** are `freeze_v1/stress_sets.json`: 300 × 9 retained
  library indices and parameters.
- Both were written by `make_manifest.py` from the recomputed effect JSON and
  libraries. The stress sets were drawn once, with seed 9 × 10^12 +
  17 × 10^6 + 999. Input hashes are in
  `freeze_v1/package_inputs_sha256.txt`.
- `run_validation.sh MANIFEST 3 OUT` runs `validate.py` in three slots, the
  most the host's memory allows at about 28 GB each, then runs
  `collect_validation.py`.
- Each chunk directory holds its manifest entry, its rows and its T files.
- `DONE` means the processes and the collector completed. The scientific
  result is in the collector's JSON.

**Streams and records.**
- **Seed:** 9 × 10^12 + 10^6·b + c, for block b and chunk c: 170 distinct
  streams.
- **Recorded:** every trial's row, including indeterminate and sampling
  failures, all on the intended denominators.

| b | Scenario | Trials | Chunks |
|---:|---|---:|---:|
| 1 | Null, prior-predictive | 1,000 | 10 × 100 |
| 2–4 | Null corners: high σ, low s, strong environment | 3 × 1,000 | 10 × 100 each |
| 5–6 | M_A at β_min and 2·β_min | 2 × 300 | 10 × 30 each |
| 7–9 | M_D linear, accelerating, step (Δ ~ U(0, 2); step time ~ U) | 3 × 300 | 10 × 30 each |
| 10–11 | M_O low-n and uniform | 2 × 300 | 10 × 30 each |
| 12–14 | M_A (β_min) + M_D, each form | 3 × 300 | 10 × 30 each |
| 15–16 | Detection curve: M_A at Δ10 = 0.3 and 0.5 | 2 × 300 | 10 × 30 each |
| 17 | Fitted-parameter predictive stress check: its single execution point. Parameter sets are drawn once; budget failures are `indet_sampling`, not replaced | 300 | 10 × 30 |

**Gates and labels:**
- **Null scenarios:** pass if the upper 98.75% CP bound on the rejection rate
  is ≤ 0.08, i.e. at most 60 rejections in 1,000, with unresolved trials
  counted as rejections.
- **Power at β_min:** the O1 label needs ≥ 224/300. Development evidence
  (1/30) indicates it will fail, which makes a non-rejection O3.
- **Stop rule:** a fit-failure rate above 2% in any gating block (1–5) stops
  validation. Descriptive blocks report their rate. Sampling failures are
  counted separately.
- **Descriptive only:** blocks 6–17.
- **Cost:** about 3,006 core-hours; roughly 75 hours on deep-server (§4.4).

## 7. After validation (empirical, once)

- **Q1:** `empirical_q1.py MANIFEST SUMMARY OUT 1` on the primary bank.
  - It refuses to run unless the collector's summary for this manifest shows
    no V-fail and no fit stop.
  - Before its p-value is read, the empirical radius position is reported
    against the frozen bins.
- **Then the §7 inventory**, with analysis IDs a = 1–22 and replicate streams
  9.5 × 10^12 + a.
- **Not yet implemented** (each implemented and frozen before its own run;
  reported unvalidated): the per-statistic p_k; the sensitivity generators
  and designs; the RI+slope replicate fitting; LOPO assembly.

## 8. Still open before freezing

- Astra's review of this completed package. The M_D and M_O specifications
  were accepted in the 0.9 review, with the stated scope limits.
- Barry's go-ahead for the validation compute (§4.1).
- **§4.1 screens, done** (`dev_screen200_v1/`): 5/200 null rejections, 5/200
  at β_min, 1 of 800,200 datasets failed per arm. No stop rule was
  triggered.
- Unresolved limits, kept visible: source and census-unit conflicts; the F&H
  windows for the wild dog, marmot and crane; whether the ledger supports
  prior (a); access to the Williams archived code and to *Daphnia*.
