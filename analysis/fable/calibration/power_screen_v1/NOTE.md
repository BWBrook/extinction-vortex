# Development power screen under the adopted ar_cat null (v1, 10 October 2026)

This screen is synthetic only. It computes no empirical T1–T4 and no empirical
p-value. It is development evidence under development seeds, not the frozen
§4.3 power experiment.

**Where it ran.**
- `deep-server`, tmux `fable_power`.
- Run directory:
  `/data/fable/vortex/banks10x_20261009T041220Z/power_screen_v1`.
- Sources (`source_sha256.txt`) match commit `0430737`, except
  `run_power_screen.sh`, which is committed unchanged with this note.
- T files stay on deep-server and are hashed in `T_sha256.txt`.
- Codex independently reconciled all 150 raw T files and every p bound (board
  1311; `analysis/astra/protocol08_precheck/`).

**Design.**
- **Reference.** The ar_cat 10× development banks (2×10^9 draws per
  population) with the k-NN library: K = 2,000, R_train = R_test = 2,000. These
  are production counts.
- **Outer datasets.** Prior-predictive nuisances, generated on the same
  ar_cat environment.
- **Arms.** 30 trials each: the null, and M_A at β_min, at 2·β_min, at
  Δ10 = 0.3 and at Δ10 = 0.5. Seeds 20261023–20261027 in that order;
  β values are in `arm_meta.txt`.
- **Execution.** At most three arms at once, with 18 R workers each.

**Results** (`scored_trials.csv`, `scored_summary.json`; contract-v2 scorer
with p_lo, p_hi and outcome verified against the log):

| Arm | Δ10 | Detections (two-sided exact 95% CI) | Indeterminate |
|---|---:|---|---:|
| Null | 0 | 1/30 [0.001, 0.172] (null gate) | 0 |
| M_A at β_min (β = 0.975) | 0.075 | **1/30 [0.001, 0.172]** | 0 |
| M_A at 2·β_min (β = 1.949) | 0.144 | 2/30 [0.008, 0.221] | 0 |
| M_A, β = 4.458 | 0.30 | 8/30 [0.123, 0.459] | 0 |
| M_A, β = 8.664 | 0.50 | 18/30 [0.406, 0.773] | 0 |

- **No failures.** No fit failures and no indeterminate outcomes in 150
  trials. Ledoit–Wolf shrinkage was never needed.

**Interpretation (development only).**
1. **Discrimination at the effect target is very weak.**
   - At β_min, 1/30 is indistinguishable from the null arm. O1 needs at least
     224/300 at validation.
   - On this evidence the frozen power gate would fail. Under the protocol, an
     empirical non-rejection would then be **O3 (insufficient
     discrimination)**, while a validated empirical rejection could still be
     **O2**.
   - 1/30 is not evidence that feedback is absent.
2. **The detection curve rises only at large effects.**
   - It reaches about 0.6 at Δ10 = 0.5, a 50% vital-rate multiplier at N = 10.
   - That arm had 21/30 raw detections in the earlier 2×10^8,
     hard-tolerance screen. Its 18/30 here is consistent, given the different
     procedure, banks and seeds.
3. **The effect target is unchanged.**
   - The risk-defined β_min stays as pre-registered, and the detection curve
     is reported with it. Codex agrees (1311/1313).
   - Changing the scientific target after seeing power would be an adaptive
     amendment for Barry. It is not proposed here.
   - The results quantify what Phase II (more series) would need to buy.
4. **Measured cost** (`resources.txt`).
   - 205,440 CPU-seconds for 150 trials, including five bank loads, i.e.
     about 1,370 CPU-seconds (0.38 core-hours) per trial, all-in.
   - Peak RSS 28 GB per process.
   - The first wave, three arms × 18 workers, ran about 105 trials per hour
     after loading (Codex 1314).
