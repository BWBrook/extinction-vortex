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

*Revised 12 October after [Astra's plan review](astra_v2_plan_review_20261011.md) §3.*

**Target.** Unchanged in kind: the C+-conditional prior-predictive null under
prior (b), with the frozen simulator, S, A, T1–T4, the RI estimator, the
Mahalanobis rank p and fixed denominators.

**Hypothesis, not derivation.**
- The working hypothesis is that summaries of how the squared log change scales
  with 1/N_t help separate nuisance regimes that C (msq, acf, inc) mixes.
- The motivation is a delta-method heuristic: Var(N_{t+1} | N_t) ≈
  N_t·v_d + N_t²·v_e. It is not exact. Under the AR(1) environment and
  extinction selection, the relevant moments depend on history, not only on
  N_t. Low s alone does not raise v_d either, since v_d contains s(1 − s) + f.
- Neither D2 nor an oracle improvement would prove this mechanism uniquely.

**Added summaries** per population. They use v1's exact transition convention:
d_t = ln(N_{t+1}/N_t) for the non-final transitions that `calib_features`
uses (t = 0..L − 3), with predictor 1/N_t, the starting count of each
transition.
- h_1 = the OLS slope of (d_t − d̄)² on 1/N_t;
- h_2 = its intercept.
- **Constant predictor** (all N_t equal): h_1 = 0, h_2 = the mean of
  (d_t − d̄)², and the series is flagged.
- C+ = (msq, acf, inc, h_1, h_2). It is MAD-scaled on the reference bank,
  zero-MAD columns are dropped as in v1, and K = 2,000.

**Reference.** The frozen primary bank is reused for development; C+ is
recomputed on it. A v2 freeze would declare whether this bank or a new one is
the validation bank.

**Reported, in addition to §5:**
- fit failures and support for all nine populations;
- T3 signal absorbed: per-statistic mean z under M_A (b5, b16) for C+ against
  v1, on the same outer datasets;
- power at β_min and at Δ10 = 0.5.
- Support is measured two ways, because raw 3-D and 5-D radii are not
  comparable:
  - the selected neighbours' distances in the **original C metric** (v1 mask
    and MAD);
  - the per-dimension spread of the neighbours.
- These are development specifications. No change of target, K or validation
  gate follows from the outcomes.

**A0: no-fit pre-screen (proposed first).**
- Rebuild the C+ neighbourhoods for the exposed v1 outers of b1–b4, 1,000
  each, against the primary bank.
- Report, as in D1c, the true-value ranks of s, f, σ and the stationary-mean
  proxy, along with the original-C distances.
- D3 showed that fixed-θ references calibrate this corner. A0 asks whether C+
  moves the library toward the generating nuisance values at the low-s corner,
  without spending fits.
- If A0 shows no material reduction in displacement, A is unlikely to repair
  calibration. The fitted screen (A1) is then reconsidered before it is run.
- Cost: about 30 min on deep-server, with no fits.

**Main risk.**
- h_1 is close in spirit to T3 (variability rising as N falls). Conditioning
  on it can remove T3 signal and change T1/T2 power.
- M_A acts mainly on the mean (g < 1 only for N < 50, strongest at very small
  N), so some T1/T2 signal may remain.
- More dimensions widen the neighbourhoods.

## 4. Candidate B: grid-calibrated p over a declared composite null

*Revised 12 October after Astra's plan review §4.*

**Definition** (unchanged).
- Θ_G has G = 8 points, built by the frozen `effect_target.py` rule from the
  libraries at the observed C (E20): the centre; s, f and σ each at their
  library 10th and 90th percentiles; and ρ with p_c at their 90th.
- p_raw is v1's p_hi from the unchanged v1 procedure.
- For each θ_g, R_cal = 1,000 complete v1 analyses of fresh selected datasets
  give F_g(x) = (1 + #{p* ≤ x}) / (R_cal + 1).
- p_B = max(p_raw, max_g F_g(p_raw)).

**Claims, narrowed.**
1. **Validity at grid points only.** At each θ_g, the inclusive Monte Carlo
   rank gives P(F_g(p_raw) ≤ α) ≤ α. That probability averages over the
   random calibration table, so it is not exact 5% control for one frozen
   1,000-row table. The maximum needs no Bonferroni factor for validity at an
   included point (Dufour 2006).
2. **The grid is not data-independent.** It is fixed before any fresh
   simulation but derived from the exposed empirical C. So the theorem does
   not validate the original data-adaptive construction, or the continuum
   structural null outside Θ_G. Candidate selection has to settle what the
   empirical target is; that is not changed here.
3. **Nesting only.** Including p_raw makes B's rejection region a subset of
   v1's. It gives no new prior-predictive guarantee: v1's 46/1,000 met only the
   8% criterion.
4. **Failures.** An unresolved *analysed* dataset stays indeterminate and
   counts as a null failure in validation. Setting an unresolved *calibration*
   p* to 0 is a separate conservative rule for building F_g. The rank theorem
   does not control the failure-inclusive rate.

**Astra's cheap screen, and my response.**
- She took the v1 low-s table alone (F_L from the 1,000 audited b3 p values)
  and applied the wrapper max(p_raw, F_L(p_raw)) to the disjoint stored power
  blocks. Detections out of 300 fell:
  - β_min: 21 → 6;
  - 2β_min: 25 → 8;
  - Δ10 = 0.3: 118 → 35;
  - Δ10 = 0.5: 206 → 98.
- Any full B that keeps this table can only reject a subset of these.
- With D3's result (§7), this changes what B can offer. B would buy
  grid-point validity, but it would leave a test that has almost no power at
  β_min and about one-third power at Δ10 = 0.5. That is enough to make an O2
  label valid only for strong feedback.
- **Proposal:** defer B's 8,000-analysis calibration and keep B, fully
  defined, as the measured fallback.
  - A0, and A1 if A0 warrants it, go first.
  - If A fails, the stop rule returns the method, scope and sample-size choice
    to Barry with A's evidence, B's screened power and the cost of a full B.

## 5. Shared development evaluation

*Revised 12 October after Astra's plan review §5.*

**One set of outer datasets serves both candidates.** Each candidate gets its
own reference stream, and B its own calibration stream.
- **Exposed v1 outers** (development evidence only): trial IDs 0–299 of b1
  (prior predictive), b2 (high σ), b3 (low s), b4 (strong environment), b5
  (β_min) and b16 (Δ10 = 0.5). These already have paired v1 outcomes.
- **Fresh outers**, 200 at each of five Θ_G points: the centre, low f, high f,
  low σ and high s. They are generated once and their SHA-256 is bound.
  - Seeds: 8×10^12 + 5×10^6 + 10^4·g + i.
  - Each fresh set is scored with v1 (descriptive v1 calibration at points v1
    never tested) and with each candidate run.
- **Reference streams:** 8×10^12 + 6×10^6 + 10^5·arm + trial index.
- **Calibration tables** for any later B are drawn from a disjoint stream,
  8×10^12 + 7×10^6 + …, and never from these evaluation outers.

**Cost of A1.**
- A1 is 1,800 + 1,000 analyses, plus 1,000 v1 analyses on the fresh points:
  about 3,800 in all, roughly half of a v1-sized kunanyi run.
- That is about 2 h on 48 nodes, with one completion email.

**Reported:**
- null rejection at each point, with exact intervals and the paired McNemar
  against v1;
- power at β_min and Δ10 = 0.5;
- per-statistic mean z;
- original-C distances and 5-D radii;
- fit failures;
- measured cost.

**Stop rule.** Astra's: no third candidate and no gate loosening. If neither
candidate is credibly calibrated with useful discrimination at feasible cost,
the method, scope and sample-size choice goes back to Barry with the evidence.

## 6. Power wording (corrected)

21/300 measures v1. It is not an information bound for nine populations. A
procedure with a different C or reference law need not have nested rejection
regions, so its power has to be measured. O3 remains the planning expectation.

## 7. Results of D3 and A0, and the stop rule (12 October)

Details and receipts are in
[v2_dev/NOTE.md](../analysis/fable/calibration/v2_dev/NOTE.md).

**D3.**
- On the same 200 low-s outers, the frozen prior bank gave 34 non-accepts and
  the fixed-θ_L oracle gave 7.
- Paired table: 3, 31, 4, 162. McNemar p = 3.5×10⁻⁶. The difference is −0.135,
  with a Newcombe method-10 interval of (−0.194, −0.080).
- The oracle also removes the T1/T2 shift. Its neighbourhoods are 3–4 times
  wider in the original C metric.
- Within the declared limits, the reference's nuisance law drives the v1 low-s
  failure at this corner; C-locality does not.

**A0.**
- C+ leaves the nuisance displacement unchanged at every corner: low-s s
  ranks 0.09–0.33 → 0.10–0.32, proxy 0.004–0.15 → 0.004–0.15.
- It makes neighbours about 4 times farther away in the original C metric.
- So candidate A as specified does not address the mechanism D3 isolates, and
  A1 is not worth its roughly 3,800 analyses.

**Candidate B.**
- B is coherent but buys validity on its grid at a large cost in power.
- Astra's cheap screen, on v1's low-s table alone: β_min 6/300, Δ10 = 0.5
  98/300. A full B can only reject a subset when it keeps that table.

**Proposed: invoke the stop rule.** No third candidate, and no modified C+
chosen against these outcomes. The method, scope and sample-size choice goes
back to Barry, after Astra's critique, with three options:

1. **Close v2 development and report.** Report the v1 V-fail and the
   mechanism evidence (D1c/D2, D3, A0): under no feedback, the null
   distribution of the Fagan–Holmes statistics depends on nuisance values
   that the extinction series' calibration summaries do not identify. Report
   the v1 discrimination profile (Q2) descriptively. The empirical test stays
   unrun, and is reported as insufficient identification.
2. **Run candidate B.** About 8,000 calibration analyses, then a fresh v2
   validation, giving a valid test on the declared grid. It would detect
   little: by the screen, at most about 2% at β_min and about 33% at
   Δ10 = 0.5. The likely empirical label is O3, or O2 only under strong
   feedback.
3. **Change the target: external demographic information.**
   - Use species-specific survival and fecundity estimates from independent
     demographic studies as informative nuisance priors. D3 shows that a
     reference with the right nuisance values calibrates.
   - This needs a literature extraction for the nine populations, possibly
     Phase II, and a new pre-registered protocol and validation.
   - It is a change to Barry's adopted target.

My recommendation, for Astra to challenge: option 1 now, with option 3 as the
substantive follow-on if Barry wants an empirical vortex test. Option 2 costs
more than its expected information is worth.

## 8. Fixed 200-case fitted screen of candidate A (A-screen; bound 13 October before any fit)

**Direction.** Barry, in Claude chat on 13 October 2026: "But yes, as the next
step, we do the 200-case check now. It's the obvious next step. Proceed with
my full agreement." This follows Astra's proposal (board 1561;
`notes/astra_v2_results_review_20261012.md` §3), which is adopted unchanged.

**Outer datasets.**
- The exposed v1 b3 (`null_low_s`) trials with IDs 0–199, from chunks c00 and
  c01: a fixed budgeted subset, kept whole and not chosen by outcome.
- Their recorded series and stored v1 results are extracted once to
  `a_outers.json`. Its SHA-256 and the hashes of the source row files are bound
  into every run.
- The v1 baseline on these trials is already exposed: 21/200 non-accepts.

**Procedure.**
- Candidate A exactly as in §3:
  - C+ = (msq, acf, inc, h₁, h₂), MAD-scaled on the frozen primary bank, with
    zero-MAD columns dropped;
  - K = 2,000; R_train = R_test = 2,000;
  - the frozen RI fits, scoring and failure rules.
- It runs through v1's frozen `run_chunk(observed=…)`. The only substitution
  is the calibration-feature function, which is replaced by C+. Neighbours are
  found with a k = K query, as v1 does.
- Reference stream: seed 8×10^12 + 6×10^6 + 10^5·1 + trial ID (plan §5,
  arm 1).

**Recorded per trial.**
- Outcome, p bounds, the fit and failure counts, and T1–T4 z on v1's
  complete-row rule.
- Neighbour draw IDs and boundary-tie flags.
- The C+ K-th distance, checked against the run's log.
- The selected neighbours' maximum distance in the original C metric.

**Report** (`a_screen.py report`, which exits non-zero on any failed binding or
missing receipt):
- A and v1 non-accepts with exact intervals;
- the paired table, exact McNemar and a Newcombe method-10 interval;
- retained failures;
- mean z per statistic for both arms (v1's from its stored T files);
- original-C support for both arms;
- the measured resource cost.

**Fixed in advance.**
- n = 200. There is no extension and no change to the summaries, scaling, K,
  cases or rules after results.
- This is a null-only screen, so it supports no power claim.

**Reading, as Astra proposed.**
- This is development triage.
- Little or inconclusive improvement strengthens the case for returning the
  method choice to Barry.
- A clear improvement warrants considering the broader §5 evaluation. It
  neither selects nor validates A.

**Cost.** About 1.5 h of fits on deep-server, from D3's measured 3 h 10 min
for 400 analyses at 2 × 30 R workers. Here two slot processes of 100 trials
each run with 30 workers apiece. Building the C+ bank takes about 15 min.
