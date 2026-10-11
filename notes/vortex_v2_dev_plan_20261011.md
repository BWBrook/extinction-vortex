# V2 development plan: D3 oracle specification and two candidate procedures

Fable, 11 October 2026 (Australia/Hobart). This plan follows
[Astra's v2 brief](astra_v2_development_20261011.md) and her
[diagnostic review](astra_v2_diagnostic_review_20261011.md).

**Status.** This is a development specification. It is not a freeze and not a
selected method. V1 stays failed and reportable, and no empirical test is
enabled. Everything below uses development seeds or exposed v1 outputs.

## 1. D1 correction and D2

- D1's categorical reading is withdrawn. The original note and output stay in
  Git, with a qualification appended in
  [v2_dev/NOTE.md](../analysis/fable/calibration/v2_dev/NOTE.md).
- The repair (D1c) and the association diagnostic (D2) are in
  `v2_dev/knn_nuisance_c.py`.
  - It compares integer penultimate counts with half ties, and gives null for
    a constant library.
  - It checks the manifest, all 181 bank hashes and the source hashes, and
    records the runtime.
  - Per trial and population it records the K-th distance against v1's
    rounded value, flags boundary ties and keeps a digest of the neighbour
    draw IDs. The full IDs are kept in an npz file on deep-server.
  - D2 uses one summary per trial: the mean over the nine populations of
    rank − 0.5. It reports rejection by tertile with exact intervals, a
    univariate logistic slope per SD, Spearman correlations with p and
    between the summaries, and the summaries' distributions.
- s + f is labelled a **nominal** growth proxy. A second proxy is the
  stationary mean multiplier (1 − δ p_c)(E logit⁻¹(logit s + σZ) + f).
  Neither is the growth rate of the selected process.

## 2. D3: paired oracle contrast at the low-s corner (fixed before simulation)

**Question.** At the frozen low-s corner θ_L (`freeze_v1/corners.json`),
does replacing the prior-bank reference with a fixed-θ_L reference change the
rejection rate on the same outer datasets?

**Outer datasets.**
- 200 fresh datasets at θ_L, generated once with `fresh_selected` under the
  frozen S and A and a budget of 10^6 draws per population.
- Stream: seed 8×10^12 + 3×10^6 + 0, one generator in trial order.
- They are written once to `d3_outers.json`, and its SHA-256 is bound into
  both arms.
- A budget failure is kept as `indet_sampling` in both arms, never replaced.

**Arm V (frozen v1 reference).**
- The frozen primary bank, with its frozen C feature mask and MAD scaling;
  K = 2,000.
- R_train = R_test = 2,000, the frozen RI fits (`tstats_batch.R`), and v1's
  scoring and failure rules.
- Each trial is run through the frozen `run_chunk` with `observed=` its outer
  dataset. Reference stream: seed 8×10^12 + 3×10^6 + 10^4·1 + i, for trial
  i < 200.

**Arm O (oracle reference).**
- A fixed-θ_L bank: per population, 20 shards of 10^8 draws at θ_L with the
  frozen simulator, S and A, with `rho`, `p_c` and `delta` fixed too.
- Shard seed: 8×10^12 + 3×10^6 + 3×10^4 + 100·(population index) + shard.
- Neighbours are found in the **v1 primary bank's metric**: the same feature
  mask and MAD, applied to the oracle bank's C.
- K, R, fits, scoring and failure accounting are as in arm V. Reference
  stream: seed 8×10^12 + 3×10^6 + 10^4·2 + i.

**Support requirement and stop rule** (selection rates at θ_L run from
2.35×10^-5 for wild dog to 1.4×10^-2):
- Each population needs at least 20,000 retained paths (10·K).
- After 2×10^9 draws, wild dog would expect about 47,000 and golden plover
  about 85,000.
- If any population falls short, extend it once to 4×10^9 draws. If it still
  falls short, D3 stops before any fit and the shortfall is reported.

**Recorded per trial and arm.**
- Outcome, p_lo and p_hi, the fit-failure counts, and the signed standardised
  T residuals z_k = (T_obs,k − mean_train,k)/sd_train,k.
- K-th distances in the common metric, boundary ties, and the neighbour draw
  IDs (npz, hashed).

Also recorded: input and source hashes, runtime, and the arm V check that its
K-th distances match the run's logged values.

**Report.**
- Rejections in each arm, with exact 95% intervals; unresolved trials count
  as rejections, as in v1.
- The discordant pairs b = (V reject, O accept) and c = (V accept, O reject).
- An exact conditional McNemar test and the paired difference (c − b)/200
  with a Newcombe hybrid-score 95% interval.
- Mean z_k by arm, and the distributions of K-th distance in each arm.

n = 200 is fixed, with no extension after results.

**Interpretation, declared now** (Astra's wording):
- A drop in arm O shows that changing the reference's nuisance law helps at
  this corner. It does not isolate survival (the whole nuisance vector is
  fixed and the bank geometry changes), does not define a usable empirical
  method, and does not exclude finite-K error.
- No drop leaves approximation, support and implementation explanations open.
- For scale: 10/200 has an exact 95% interval of 0.024–0.090.

**Cost.**
- 400 reference analyses. v1 measured 45 s of fits per analysis with 27
  workers on kunanyi.
- On deep-server the two arms run at the same time, 30 R workers each, at
  roughly 45–60 s per analysis: about 3 h.
- The oracle bank is 1.8×10^10 draws at the production rate of about
  8.4 µs per draw: about 40 min on 60 processes.
- Generating the outers takes about 20 min.
- No PBS job is needed.

**Smoke test.** The full path ran end to end on deep-server with 2 outers,
K = 50, R = 20 and a 4×10^6-draw oracle bank (`D3_SMOKE=1`). It is not a
result.

## 3. Candidate A: demographic-variance-augmented conditioning (C+)

**Target.** Unchanged in kind: the C+-conditional prior-predictive null under
prior (b), with the frozen simulator, S, A, T1–T4, the RI estimator, the
Mahalanobis rank p and fixed denominators.

**Rationale.**
- Given N_t, the variance of the next count is N_t·v_d + N_t²·v_e, so the
  squared log change scales roughly as v_d/(λ²N_t) + v_e/λ².
- C (msq, acf, inc) mixes the demographic term v_d (from s(1−s) + f) with the
  environmental term v_e. A low-s, high-turnover population has a larger
  1/N coefficient.
- D1c/D2 and D3 test whether that is the direction that moves the T1/T2 null.

**Added summaries**, per population, over the non-final transitions used by C
(so the terminal transition is excluded, as in C):
- h_1 = the OLS slope of (d_t − d̄)² on 1/N_t;
- h_2 = its intercept;
- here d_t = ln(N_{t+1}/N_t).

A series whose 1/N_t values are all equal gives h_1 = 0 and is flagged, like
v1's constant-changes flag. C+ = (msq, acf, inc, h_1, h_2), MAD-scaled on the
reference bank, zero-MAD columns dropped as in v1, and K = 2,000.

**Reference.** The frozen primary bank is reused for development; C+ is
recomputed on it. A v2 freeze would declare whether this bank or a new one is
the validation bank.

**Main risk.**
- h_1 is close in spirit to T3 (variability rising as N falls). Conditioning
  on it can remove T3 signal and change T1/T2 power.
- M_A acts mainly on the mean (g < 1 only for N < 50, strongest at very small
  N), so some T1/T2 signal may remain. Development power is measured; it is
  not assumed.
- More dimensions also widen the neighbourhoods; radii are reported.

## 4. Candidate B: grid-calibrated p over a declared composite null

**Target.** Level-α validity at each nuisance vector in a declared finite set
Θ_G. Validity is **marginal over selected datasets at fixed θ**, not
conditional on C. There is no claim for θ outside Θ_G; off-grid points are a
descriptive challenge only.

**Θ_G**, declared before any development outcome. It is built by the frozen
`effect_target.py` rule: per population, library medians at the observed C,
which were already exposed in E20.
- G = 8: the centre (all medians); s at the library 10th and 90th
  percentiles; f at the 10th and 90th; σ at the 10th and 90th; and ρ with p_c
  at their 90th.
- The 10th-percentile s, 90th-percentile σ and strong-environment points are
  the frozen v1 corners. The others follow the same rule.

**Raw statistic.** p_raw is v1's p_hi from the frozen v1 procedure, unchanged:
C, k-NN on the primary bank, references, fits and conservative rank.

**Calibration (single level, not nested).**
- For each θ_g, R_cal = 1,000 fresh selected datasets. Each is analysed by the
  complete v1 procedure, giving p*.
- F_g(x) = (1 + #{p* ≤ x}) / (R_cal + 1).
- Unresolved calibration trials count as p* = 0, which is conservative.

**Calibrated p.**
- p_B = max(p_raw, max_g F_g(p_raw)).
- p_raw itself is calibrated under the prior predictive, so including it covers
  the prior-predictive member.

Θ_G is fixed and data-independent once declared. A simulated dataset's
analysis therefore repeats everything that p_raw's procedure estimates, and
there is no per-dataset re-estimation of θ to nest.

**Plug-in alternative, dropped.** Centring a reference on the library median
would keep the D1 displacement (wild dog: true s 0.20, library median 0.58),
so it is dropped as a candidate.

**Cost.** 8,000 analyses, about the size of v1's validation: about 3.5 h on
48 kunanyi nodes with one PBS completion email. A v2 validation then needs
fresh outers.

**Main risk.**
- p_B is conservative; at the low-s point, F_g(0.05) ≈ 0.15. Power at β_min
  will likely fall below v1's 21/300.
- Validity covers only Θ_G.

## 5. Shared development evaluation (for A and B; after D1c, D2 and D3)

**Development outers**, declared now:
- 300 from each of v1 b1, b3, b5 and b16 (trial IDs 0–299 of each block);
- 200 fresh at each of the four new Θ_G points (low/high f, low σ, high s);
- seeds 8×10^12 + 10^6·d + c with d = 5 for A and d = 6 for B.

Exposed v1 outers count as development evidence only.

**Reported for each candidate:**
- null rejection at each point, with exact intervals;
- power at β_min and Δ10 = 0.5 (b5, b16);
- radii;
- fit failures;
- measured cost.

**Stop rule.** Astra's: no third candidate and no gate loosening. If neither
candidate is credibly calibrated with useful discrimination at feasible cost,
the method, scope and sample-size choice goes back to Barry with the evidence.

## 6. Power wording (corrected)

21/300 measures v1. It is not an information bound for nine populations. A
procedure with a different C or reference law need not have nested rejection
regions, so its power has to be measured. O3 remains the planning expectation.
