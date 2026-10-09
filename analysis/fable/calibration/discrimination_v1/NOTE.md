# Development discrimination screen (v1, 9 October 2026)

This screen is synthetic only. It computes no empirical T1–T4 and no empirical
p-value, and it is development evidence, not validation.

**Where it ran.**
- `deep-server`, tmux `fable_disc`.
- Run directory:
  `/data/fable/vortex/compare_nulls_20261009T013137Z/disc_20261009T014241Z`.
- Source commit `14f974b`. All 12 hashes in `source_sha256.txt` match that
  commit.

**Design.**
- **Banks.** 2×10^8 prior-(b) draws per population, for iid and for ar_cat.
  - Seeds 20261014100–20261014117.
  - 1,304 s wall time on 18 processes.
  - Each population keeps 1.3–3.0×10^6 selected runs.
  - Hashes are in `banks2e8_sha256.txt`.
- **Arms.** Four arms of 30 outer datasets each.
  - Each outer dataset is fresh: generated either under the null (seed
    20261016) or under M_A with β = 8.66, i.e. Δ10 = 0.5 (seed 20261017).
  - M_A always uses the same environment variant as the null it is tested
    against.
  - The reference is always that variant's no-feedback bank.
- **Settings.** K = 2,000; tolerance 1.0; R_train = R_test = 1,000
  (development; production uses 2,000); 14 R workers per arm.
- **Completeness.** All four arms completed all 30 trials, checked by row and
  file count.
  - At this commit, `e2e_benchmark.py` emitted a numeric p even after a
    calibration shortfall.
  - The driver used a bare `wait`, so its `DONE` message does not establish
    completeness on its own.
  - Both defects are repaired after this run (Astra 1226/1228).

**Scoring.**
- `score_discrimination.py` recomputes D and both p bounds at full precision
  from the archived `T_k.csv` files.
- The recomputed lower bound equals the logged p in all 120 trials.
- Each trial is classified under the protocol's fixed-denominator rules:
  - a calibration shortfall, observed-fit failure, unusable covariance or
    straddling bounds makes the trial indeterminate;
  - every non-accept counts against the null gate;
  - only a reject counts as a detection.
- Outputs: per-trial rows in `scored_trials.csv`, totals in
  `scored_summary.json`, and scorer hashes in `score_src_sha256.txt`.
- `T_sha256.txt` hashes the T files, which stay on deep-server.

| Arm | Accept | Reject | Indeterminate (calibration) | Other indeterminate or missing | Procedure (95% CP) | Raw p < 0.05, diagnostic only |
|---|---:|---:|---:|---:|---|---:|
| iid, null | 23 | 0 | 7 | 0 | null-gate count 7/30 = 0.23 [0.10, 0.42] | 0/30 |
| ar_cat, null | 21 | 1 | 8 | 0 | null-gate count 9/30 = 0.30 [0.15, 0.49] | 1/30 |
| iid, M_A Δ10 = 0.5 | 1 | 20 | 9 | 0 | detections 20/30 = 0.67 [0.47, 0.83] | 29/30 = 0.97 [0.83, 1.00] |
| ar_cat, M_A Δ10 = 0.5 | 3 | 14 | 13 | 0 | detections 14/30 = 0.47 [0.28, 0.66] | 21/30 = 0.70 [0.51, 0.85] |

**Failures and shortfalls.**
- **Fits.** 120 × 2,001 = 240,120 datasets were fitted (observed, training and
  test), with four nlme fits each.
  - None failed after the fallback.
  - Ledoit–Wolf shrinkage was never triggered.
- **Shortfall populations.** Each entry counts trials in which that population
  fell short; one trial can involve several populations.
  - iid null: Hawaiian crow 4; middle spotted woodpecker, whooping
    crane and turtles A and B 1 each.
  - ar_cat null: wild dog 3, marmot 2; whooping crane, golden plover and
    turtle A 1 each.
  - iid M_A: wild dog 4; golden plover, red-cockaded woodpecker and turtle A
    2 each; marmot 1.
  - ar_cat M_A: turtle A 6, middle spotted woodpecker 5, red-cockaded
    woodpecker 3, marmot 2; wild dog, whooping crane and Hawaiian crow 1 each.

**Mean synthetic T_obs, for orientation only.**

| Arm | T1 | T2 | T3 | T4 |
|---|---:|---:|---:|---:|
| iid null | 0.015 | 0.002 | −0.012 | −0.006 |
| iid M_A | 0.039 | 0.026 | −0.009 | −0.003 |
| ar_cat null | 0.021 | 0.007 | −0.012 | −0.005 |
| ar_cat M_A | 0.046 | 0.032 | −0.012 | −0.007 |

These are prior-predictive outer datasets, not conditioned on the observed C,
and they were not compared with any empirical statistic.

**Interpretation (development only).**

1. **2×10^8 banks are not viable for the procedure.**
   - Calibration shortfalls alone make 23–43% of trials indeterminate. Under
     the null that alone breaks the 8% ceiling, whichever null is correct.
   - The binding constraint is coverage of fresh outer C values, not the test
     statistic. This is quantified in `../coverage_v1/`.
2. **The trade-off for Barry** (raw p, ignoring shortfalls, diagnostic only).
   - Under the null, raw p fell below 0.05 in 0/30 and 1/30 trials: no sign
     of excess false alarms, but little information at n = 30.
   - Under M_A at Δ10 = 0.5, raw p fell below 0.05 in 29/30 trials against the
     iid null and 21/30 against the ar_cat null.
   - An AR environment with catastrophes reproduces part of what Allee
     feedback does to the T statistics, so the richer null costs detection.
     This is the expected direction; its size is now measured at one
     development effect.
3. **Feedback also shifts C away from the null bank.**
   - Shortfalls are more frequent under M_A (9 and 13 trials) than under the
     null (7 and 8).
   - Most M_A shortfall trials had raw p < 0.05: 9 of 9 for iid, 7 of 13 for
     ar_cat.
   - Under the hard-tolerance rule, part of the feedback signal therefore
     becomes indeterminate rather than detected. Larger banks reduce this.
4. **Δ10 = 0.5 is a development effect, not β_min.** Nothing here bears on
   the O1 power gate.
5. **Seeds.** Both variants' null arms share seed 20261016, and both M_A arms
   share 20261017. They are different processes, so the shared streams do not
   make the arms identical, but the arms are not independent RNG streams.
