# External demographic information: simulation design (draft for review)

Fable, 14 October 2026 (Australia/Hobart). Design only; no run is
commissioned. It revises item 2 of board 1606 after Astra's correction
(`notes/astra_a_power_deep_dive_review_20261014.md` §2): D3 and v1 do not
bracket the precision needed. D3 fixed all six nuisances at one corner and had
no power endpoint.

## 1. Question and estimands

**Question.** If independent evidence E about survival and recruitment
accompanies a focal extinction series N, how do null calibration and
discrimination of the C-conditioned T1–T4 test change with E's precision,
bias and timing?

**Repeated-experiment law (primary).** Each replicate draws:
1. θ ~ prior (b);
2. N ~ M0 or M_A given θ, under the frozen selection S and cap event A;
3. E ~ p(E | θ, timing), independently of N given θ.

The analysis uses the reference law
p(N* | C(N*) ≈ C(N), S, E) ∝ ∫ p(N* | θ) π_b(θ) L(E | θ) dθ.
Under this law, exact C-conditioning gives prior-predictive exchangeability
given (C, E). The experiment measures how fixed-θ calibration and power move
as E becomes informative.

**Fixed-corner targets (secondary).** θ is fixed at a frozen v1 corner (low
s, high σ, strong environment) and E is drawn at that θ. This is the
fixed-nuisance validity that v1 failed. It is reported per corner, with no
claim beyond the corners.

**Dependence (sensitivity).** E shares years with N: it is computed from
abundance-weighted survival over the series' own years. Reported apart from
the independent case and not mixed into it.

## 2. Information arms, units and levels

The units are those a field study reports.
- **Survival evidence.** A marking study with n_E animal-years gives
  k ~ Binomial(n_E, s̄). Here s̄ = (1 − δ p_c) · E_Z[logit⁻¹(logit s + σZ)] is
  the realized annual survival a field study measures.
- **Recruitment evidence.** m_E breeding records with recruits
  r ~ Poisson(m_E · f̄), where f̄ = (1 − δ p_c) f.
- L(E | θ) uses the same mappings. Environmental and catastrophe parameters
  keep prior (b) unless an arm says otherwise.

| Arm | What is informed | Levels |
|---|---|---|
| E-sf (realistic) | s̄ and f̄ through noisy E | n_E = m_E ∈ {10, 30, 100, 300}; bias on logit s̄ of 0 or +0.5 (E drawn at a shifted value, analysed as unbiased) |
| I-sf (ideal benchmark) | s̄ and f̄ through truth-centred priors | the same Fisher information as E-sf at each n_E, centred exactly at the truth |
| Timing (under M_A only) | E from the baseline phase (N ≥ n_ref, g = 1) against the decline phase (survival including g(N_t) over the final 5 transitions) | n_E ∈ {30, 300}, bias 0 |
| Oracle-6 (limit) | all six nuisances known (the D3 construction) | null at the low-s corner (done: D3); power at Δ10 = 0.5 on a fixed subset (§4) |

n_E = 0 recovers v1. Haley's tagged summaries (97 non-pup exposures over ten
years) and the caribou collars (about 3–8 per year) sit inside this range.
This is an approximate anchor, not a claim that those studies match the
binomial model.

## 3. Reference construction and feasibility

**R1: weighted primary bank.** Each bank member i (θ_i a prior draw under
selection) gets weight w_i = L(E | θ_i).
- The reference is the K_eff-effective neighbourhood. Members are taken in
  C-distance order until the weighted effective sample size
  (Σw)² / Σw² reaches 2,000, capped at 200,000 members.
- R_train + R_test trajectories are drawn with probability ∝ w.
- The frozen C metric (v1 mask and MAD), estimator, scoring and failure rules
  are kept.

**Diagnostics** per outer and population:
- the effective sample size reached;
- the members needed;
- the largest weight share;
- the original-C distance at the last member.

**Support rule.** If 200,000 members do not reach an effective sample size of
2,000, the trial is *indeterminate (support)* and stays in the denominator as
a null failure or a non-detection.

**Stage 0 (no-fit feasibility pre-screen).** Compute these diagnostics for
every arm and level on the exposed outers below, before any fit.
- The decision rule is declared now: a level whose median effective sample
  size falls short at more than 10% of outer-population pairs is dropped from
  Stage 1 and reported as infeasible under R1.
- R2 (a bank drawn per information level) is costed only for dropped levels,
  and only with a bounded design.

## 4. Scenarios, sizes and rules (Stage 1, fitted)

**Outers.** Exposed v1 outers, used for development only; their true θ is
logged, so E can be drawn per outer.
- b1 (prior-predictive null), trial IDs 0–199.
- b3 (low-s null), 0–199.
- b2 (high σ) and b4 (strong environment), 0–199.
- b5 (β_min) and b16 (Δ10 = 0.5), 0–199.

Each pairs with its stored v1 outcome.

**Cells.**
- E-sf: 4 levels × 2 biases × 6 scenarios.
- I-sf: 4 levels × 6 scenarios.
- Timing: 2 levels × 2 phases × 2 alternatives.
- Oracle-6 power: 50 b16 outers, each with its own fixed-θ bank; about 40 min
  per bank on deep-server, so about 35 h. It is included only if Barry
  accepts that cost and is otherwise reported as not run.

At 200 outers each, 80 cells make Stage 1 about 16,000 analyses before Stage 0 drops,
about twice v1's validation: roughly 7 h on 48 kunanyi nodes, with one PBS
completion email.

**Seeds.**
- E draws: 8×10^12 + 8×10^6 + 10^5·cell + trial.
- Reference draws: 8×10^12 + 9×10^6 + 10^5·cell + trial.

**Reported per cell:**
- non-accepts or detections, with exact intervals;
- the paired table against v1;
- mean z;
- support diagnostics;
- failures.

**The information curve.** Calibration at each null scenario and power at
β_min and Δ10 = 0.5, plotted against n_E, for E-sf against I-sf, by bias and
timing.

**Rules.**
- No extension, no retuning and no adaptive levels beyond the Stage 0 rule.
- Results are development evidence.
- A method chosen from them must be frozen and validated prospectively on
  fresh outers before any empirical use.

## 5. What it can and cannot show

**Can show:**
- whether external s/f evidence at field-plausible precision restores
  calibration at the corners where v1 failed;
- what that costs in power;
- how sensitive the result is to bias and to decline-phase measurement.

**Cannot show:**
- that this population model is a valid null for Haley or for caribou;
- anything empirical about the nine populations;
- uniform validity over nuisance values outside the scenarios.

## 6. Open points for Astra

1. Whether R1's effective-sample-size neighbourhood is acceptable as a fixed
   rule, or whether K should stay at 2,000 members with weights only.
2. Whether s̄ and f̄ are the right estimands for E, against stage-specific
   rates.
3. Whether the decline-phase window of 5 transitions is a reasonable
   declaration.
4. Whether to cut the cells (for example, bias only at n_E ∈ {30, 300})
   before Stage 0.
