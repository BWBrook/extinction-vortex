# Validation freeze package (draft for Astra's review)

**Status: draft, 10 October 2026, Hobart (Fable). Not frozen.** This collects in
one place everything that §4.3 validation and the empirical test will run on,
as Astra's 0.8 review (1348) asked. Values marked *pending* come from the
designated-bank run, which is queued on deep-server
(`run_production_banks.sh`). They are filled in by the next handoff.

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
| Code | the commit carrying this package (`bank.py`, `e2e_benchmark.py`, `tstats_batch.R`, `score_discrimination.py` contract v3, `make_manifest.py`, `validate.py`, `collect_validation.py`, `run_validation.sh`, `empirical_q1.py`); runtime: Python 3 with NumPy 1.26.4 and SciPy 1.11.4, R with nlme, on deep-server |

## 3. Designated banks

All are 2 × 10^9 prior-(b) draws per population, in 20 shards of 10^8, built
with `build_bank.py` from source staged at `afe9bca`. `bank.py` and
`build_bank.py` are unchanged in `a31e5bc`.

| Bank | Variant | Seed family | Use | Hashes |
|---|---|---|---|---|
| Primary | ar_cat | 8.1 × 10^12 + task | validation, empirical Q1, all reused sensitivities | *pending* |
| Stability | ar_cat | 8.2 × 10^12 + task | descriptive second-bank comparison | *pending* |
| iid | iid | 8.3 × 10^12 + task | plain-M0 mandatory sensitivity | *pending* |

## 4. Recomputed on the primary bank

These use the fixed recipes; the development values are in brackets.

- **β_min:** *pending* [β = 0.975, Δ10 = 0.075].
- **Corners:** *pending* [development values in `dev_design_v1/scenarios.json`].
- **Empirical K-th-neighbour position:** *pending* [ar_cat 0.433, bin 4; iid
  1.073].

## 5. Radius strata (frozen)

- **Bins:** (0, 0.2050], (0.2050, 0.2956], (0.2956, 0.4049], (0.4049, 0.5613],
  (0.5613, ∞). A tie goes to the lower bin.
- **Source:** 20,000 C-only ar_cat null prior-predictive outer datasets against
  the 10× development bank (§3.4 step 3).

## 6. Validation run definition and streams

**Executable.**
- `make_manifest.py` writes the manifest and the stress parameter sets. The
  sets are drawn once, with seed 9 × 10^12 + 17 × 10^6 + 999.
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

- Astra's review of the completed package. The M_D and M_O specifications
  were accepted in the 0.9 review, with the stated scope limits.
- The *pending* values above.
- **§4.1 screens, done** (`dev_screen200_v1/`): 5/200 null rejections, 5/200
  at β_min, 1 of 800,200 datasets failed per arm. No stop rule was
  triggered.
- Unresolved limits, kept visible: source and census-unit conflicts; the F&H
  windows for the wild dog, marmot and crane; whether the ledger supports
  prior (a); access to the Williams archived code and to *Daphnia*.
