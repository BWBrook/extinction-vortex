# §4.1 development screens under the adopted ar_cat null (v1, 10 October 2026)

These screens are synthetic only. They compute no empirical T1–T4 and no
empirical p-value. They are the two 200-dataset development screens required
by protocol §4.1, retained in 0.9 rather than replaced by the 30-per-arm power
screen. They are development evidence, not the frozen §4.3 validation.

**Where it ran.**
- `deep-server`, tmux `fable_screen200`.
- Run directory:
  `/data/fable/vortex/banks10x_20261009T041220Z/dev_screen200_v1`.
- **Sources** (`source_sha256.txt`): `bank.py`, `e2e_benchmark.py` and
  `tstats_batch.R` match `f8546ec`; `run_arms.sh` matches `78a64b0`.
- **Scoring:** scorer contract v2 at `78a64b0` (`score_src_sha256.txt`).
- T files stay on deep-server, hashed in `T_sha256.txt`.

**Design.**
- **Reference.** The ar_cat 10× development banks with the k-NN library;
  K = R_train = R_test = 2,000. These are production counts.
- **Outer datasets.** Prior-predictive nuisances.
- **Arms.** 200 trials each: the null (seed 20261028), and M_A at the
  development β_min, 0.975 (seed 20261029).
- **Execution.** Two concurrent processes with 24 R workers each.
- **Measured cost.** 4 h 02 min of wall time; 511,649 CPU-seconds, i.e.
  1,279 per trial including two setups.

**Results** (`scored_summary.json`, `scored_trials.csv`):

| Arm | Rejections | Two-sided exact 95% CI | Indeterminate | Failed datasets / fitted |
|---|---:|---|---:|---:|
| Null | 5/200 | 0.0082–0.0574 | 0 | 1 / 800,200 |
| M_A at β_min | 5/200 | 0.0082–0.0574 | 0 | 1 / 800,200 |

The two arms are distinct:
- Their seeds differ.
- Their rejections fall on different trials: 26, 51, 65, 106 and 152 under
  the null; 85, 111, 149, 173 and 180 at β_min.
- Their single failed datasets are in different trials: 36 and 74.
- Their mean observed T differ. T1 is 0.0228 against 0.0271, and T2 0.0081
  against 0.0138.

The equal counts are a coincidence.

**§4.1 stop rules.**

| Rule | Result |
|---|---|
| Gross miscalibration (> 30/200 null rejections) | **Not triggered** (5/200) |
| Fit failures > 2% | **Not triggered** (0.0001%) |
| Infeasible bank | **Not triggered** |

nlminb was needed in about 5.3% of fits (170,081 and 167,704 of about
3.2 million per arm).

**Interpretation (development only).**
1. **The null procedure looks conservative rather than liberal** at this
   scale: 2.5%, with an upper 98.75% bound of 0.063 over 200 trials. This is
   not the §4.3 gate, which is 1,000 trials per scenario on the designated
   banks.
2. **At the risk-defined β_min, detection equals the null rate.** That
   confirms the 30-per-arm power screen (1/30). The frozen power gate
   (≥ 224/300) is expected to fail, which would make an empirical
   non-rejection O3.
3. **Library radii.** The largest K-th neighbour distance across the nine
   has a median of 0.36 (null) and 0.33 (β_min), and a 99th percentile of
   1.14 and 1.28. That is consistent with `dev_design_v1`.
