# Core methods and results: draft manuscript text

Fable, 14 October 2026 (Australia/Hobart). This is a draft for Astra's review.
It incorporates Astra's outline review
(`notes/astra_paper_outline_review_20261014.md`) and supersedes the wording of
`vortex_paper_outline_20261014.md` where they differ.

Every number below is taken from an archived summary or audit; sources are in
brackets. Introduction and Discussion remain bullet skeletons, because the
novelty wording waits on the narrow primary-text check Astra flagged.

**Working title.** *Testing extinction-vortex signatures in outcome-selected
population counts*

**Evidence categories**, used as section labels throughout:
- **[R]** exposed historical reconstruction and source reconciliation;
- **[V]** the prospectively frozen v1 synthetic validation, after documented
  development;
- **[D]** exposed post-validation development diagnostics and candidate
  screens;
- **[P]** optional planned work. No results exist for [P], and no execution
  authority is implied.

---

## Abstract (draft)

Fagan and Holmes (2006) reported extinction-vortex signatures in nine
populations monitored to extinction. Their four terminal-trajectory statistics
(T1–T4) describe accelerating decline and rising variability as extinction
approaches.

We reconstructed these statistics and asked whether a matched-outcome
reference built from the counts alone can test them against a specified
no-feedback population process. The reference is conditioned on the same
selection to extinction and on calibration summaries of the counts.

In a synthetic validation frozen before it was run, the procedure:
- met its null-calibration criterion under the prior predictive and at two
  fixed nuisance settings;
- failed it at a low-survival setting, with 148 rejections in 1,000 against at
  most 60 allowed;
- detected abundance-dependent feedback of risk-relevant strength in 21 of 300
  datasets.

Under the protocol, the empirical test was therefore not run, and the result
is reported as insufficient identification for this procedure.

In development diagnostics after validation, replacing the reference's
prior-mixed nuisance values with the generating values reduced rejections at
the low-survival setting from 34 to 7 of 200 paired datasets. Two specified
count-only repairs reduced excess rejection only with large losses of
detection.

A source-matched case study (Haley Lake marmots) shows what age structure,
marked-animal persistence, reproduction and movement add, and what they still
cannot identify.

These results do not show that feedback is present or absent in these
populations. They show that a declining count series needs demographic
information beyond the counts before these statistics can support that
inference.

---

## 2. Data and reconstruction [R]

**Series.** The nine terrestrial series of Fagan and Holmes (2006), taken from
the Williams et al. (2021) compilation:
- African wild dog (Tanzania);
- Vancouver Island marmot;
- middle-spotted woodpecker (Sweden);
- red-cockaded woodpecker (USA);
- European golden plover (Scotland);
- whooping crane (Rocky Mountain flock, peak winter counts);
- Hawaiian crow;
- two wood turtle populations (Connecticut).

Each series runs to the first count ≤ 1.

**Census classes.** Census classes, windows and source conflicts are recorded
per series. They are not verified complete censuses: several series carry
documented management or movement histories, given case by case in the
supplement without a blanket closure claim.

**Exposure.** Before any design decision, we had inspected the published
statistics, source values, our reconstructed fits and the empirical
calibration summaries of the counts [exposure log E01, E13–E16, E20–E28]. The
analysis is therefore an **outcome-exposed reanalysis**. The random-intercept
estimator was chosen as primary after reconstruction results were seen
(protocol §4.2).

**Statistics.**
- D_s = ln(N_s / N_{s+1}), with s the years before extinction and the endpoint
  count replaced by 1 for the log only.
- T1: the slope of D on s.
- T2: T1 refitted without the final transition.
- T3: the slope on s of the squared conditional residuals of the T1 model.
- T4: T3 without the final transition.

All four are estimated by a random-intercept multilevel model with AR(1)
errors, fitted by marginal ML across the nine series. They are **pooled
terminal-trajectory statistics, not single-population tests.**

**Reconstruction status: not passed.** Two independent implementations agree
to 10⁻¹² in likelihood, but do not reproduce every published value within the
±0.0005 criterion [protocol §4.2]. T5 and the scaling model were not
reconstructed.

| Statistic | Published | Reconstructed (random intercept) | Within ±0.0005 |
|---|---:|---:|---|
| T1 | 0.034 | 0.03344 | no |
| T2 | 0.011 | 0.01123 | yes |
| T3 | −0.047 | −0.04787 | no |
| T4 | −0.012 | −0.01185 | yes |

## 3. Methods [V]

**No-feedback process M0 (ar_cat).** For each population:
- Annual survival is logit⁻¹(logit s + σz_t) and recruitment per individual
  is f·exp(σz_t − σ²/2), both multiplied by (1 − δ) in a catastrophe year
  (probability p_c).
- z_t is a stationary AR(1) process (coefficient ρ, unit variance).
- N_{t+1} = Binomial(N_t, survival) + Poisson(N_t · recruitment).
- The first count is fixed at the observed one.

**Prior (b):**
- logit s ~ N(0, 1.5);
- log f ~ U(log 0.01, log 2);
- σ ~ U(0.02, 1);
- ρ ~ U(0, 0.9);
- p_c ~ U(0, 0.05);
- δ ~ U(0.5, 0.95).

**Selection S.** All interior recorded counts > 1 and the final count ≤ 1,
matching each series' design; these are the populations we can only observe
because they went extinct. The cap event A requires counts and Poisson rates
≤ 10⁹; overflowed runs are excluded and counted. θ and the path are drawn
jointly and then selected.

**Conditional reference.**
- **Bank.** Per population, 2×10⁹ prior draws (20 shards); 13–30 million
  selected paths.
- **Calibration summaries C.** The mean square, lag-1 autocorrelation and
  fraction of increases of the non-final log changes, MAD-scaled.
- **Library.** For an outer dataset, each population's K = 2,000 nearest bank
  paths in C.
- **Reference datasets.** R_train = R_test = 2,000, each drawing one library
  path per population.
- **Statistic.** T1–T4 are fitted to the outer dataset and to every reference
  dataset. D is the Mahalanobis distance of the observed T from the training
  mean, using the training sample covariance. Ledoit–Wolf shrinkage applies
  only when the condition number exceeds 10⁶; no v1 trial required it.
- **p-value bounds.** p_lo = (1 + #{D_test ≥ D_obs}) / (R + 1). p_hi also
  counts failed test fits as exceedances.
- **Outcome.** Reject if p_hi < 0.05; accept if p_lo ≥ 0.05; otherwise
  indeterminate. A trial is also indeterminate if more than 2% of its training
  fits fail.

**Alternatives.**
- **M_A (feedback).** g(N) = exp(−β(1/N − 1/50)) for N < 50 multiplies the
  survival odds and the recruitment rate. β_min is risk-defined: the smallest
  feedback raising 10-year extinction probability by 0.10 at the pooled
  library medians (Δ10 = 0.075; β_min = 0.9745).
- **M_D.** Environmental deterioration: linear, accelerating or step.
- **M_O.** Abundance-dependent detection.
- Mixtures of M_A and M_D.

**Validation design.** Frozen on 11 October 2026 (source `52779d0`, manifest
`96603037…`) and accepted by an independent reviewer before any trial was run.

| Block | Role | n | Criterion |
|---|---|---:|---|
| 1–4: prior-predictive null; fixed corners high σ, low s, strong environment | null gates | 1,000 each | upper one-sided 98.75% Clopper–Pearson bound ≤ 0.08 (≤ 60 non-accepts; Bonferroni over four); any failure is **V-fail**, overriding every empirical label |
| 5: M_A at β_min | O1 power criterion | 300 | lower one-sided 95% bound ≥ 0.70 (≥ 224 detections); governs O1 eligibility only |
| 6–16: alternatives and mixtures; 17: fitted-parameter stress check | descriptive | 300 each | exact 95% intervals |

Fit stop: more than 2% failed fits in any gating block. Denominators are fixed
throughout; unresolved trials count against the procedure.

**Execution.** TPAC kunanyi, 48 nodes, 11 October 2026.
- Host preflight on `n001.kunanyi`: Python 3.11.7, NumPy 1.26.4, SciPy
  1.11.4, R 4.3.3, nlme 3.1.171.
- The summary was rescored independently, and the collector re-run on a second
  host reproduced it byte for byte.

## 4. Results I: validation [V]

**Null gates.** 46, 41, **148** and 30 non-accepts per 1,000 for the
prior-predictive, high-σ, **low-s** and strong-environment scenarios. Only the
low-s scenario fails: upper bound 0.175 against 0.08. **The result is
V-fail.**

**O1 power criterion.** 21/300 detections at β_min, lower bound 0.047 against
0.70. It fails.

**Failures.** No fit failed in any gating block. Four failed T vectors occurred
overall, all in descriptive blocks 14–16. All 7,900 trials resolved.

**Consequence.** Under the protocol, V-fail overrides every empirical label.
The empirical test was not run, and its result is reported as **insufficient
identification for this procedure**. The pre-specified guard refused
execution.

**Q2 profile** (blocks 6–17; detection rates of a procedure that failed its
null-calibration requirement; descriptive only):

| Scenario | Detections / 300 |
|---|---:|
| M_A at 2β_min | 25 |
| M_D: linear / accelerating / step | 16 / 26 / 17 |
| M_O: low-n detection / uniform detection | 15 / 17 |
| M_A + M_D: linear / accelerating / step | 42 / 40 / 28 |
| M_A, Δ10 = 0.3 | 118 |
| M_A, Δ10 = 0.5 | 206 |
| Fitted-parameter stress check (block 17) | 11; no unresolved trials |

**Radius strata** (predeclared, descriptive). The low-s excess is not confined
to the widest-radius bin (33/250, 43/318, 40/241, 18/133, 14/58). Maximum
radius is a coarse diagnostic and does not exclude approximation error.

## 5. Results II: development diagnostics and attempted repairs [D]

These analyses came after the validation outcome and use exposed outputs or
development seeds. None is validation. Each was specified and bound before its
fits, and each was independently audited.

**Nuisance displacement (association only).** We reconstructed the v1
neighbourhoods exactly; all K-th distances match v1's records. At the low-s
corner, the generating survival ranked low within its library: population
means of 0.09–0.33, against about 0.5 under the prior predictive. Trial-level
association between displacement and rejection was weak and in the wrong
direction for a dose–response reading. This neither supports nor rules out
nuisance mixing as the mechanism.

**Paired oracle reference (D3).** On 200 fresh low-s datasets, each scored two
ways:

| Reference | Non-accepts / 200 |
|---|---:|
| frozen prior bank | 34 |
| fixed bank at the generating values of all six nuisances | 7 |

- Paired table (both, prior only, oracle only, neither): 3, 31, 4, 162.
  McNemar p = 3.5×10⁻⁶.
- Difference −0.135, with a Newcombe hybrid-score interval of (−0.194,
  −0.080).
- The oracle reference also removed the T1/T2 location shift: mean
  standardised residuals −1.86 and −1.73 under the prior reference, −0.07 and
  −0.13 under the oracle.

**Interpretation.** At one low-survival corner, replacing the mixed reference
with the generating nuisance values reduced rejections from 34/200 to 7/200.
The oracle changes the whole nuisance law and also the bank and neighbourhood
geometry. Its neighbourhoods were wider in the original C metric (median
maximum K-th distance 0.89 against 0.26). The result:
- does not isolate survival;
- does not exclude locality or approximation effects;
- does not establish calibration across the nuisance space;
- is not a usable empirical method, since the generating values are unknown.

**Candidate A: summaries targeting demographic variance.** C was augmented
with the slope and intercept of squared log change on 1/N.
- **No-fit pre-screen.** Nuisance displacement was unchanged. Neighbourhoods
  were about 5 times wider in the original C metric.
- **Fixed 200-case low-s screen.** 11/200 non-accepts against 21/200 for v1 on
  the same datasets. Difference −0.050 (−0.098, −0.005); McNemar p = 0.041.
  The T1/T2 shift largely persisted.
- **Fixed 600-case power screen.** Detections fell at β_min (21 → 11/300) and,
  sharply, at Δ10 = 0.5 (206 → 28/300; difference −0.593, −0.646 to −0.533).
- This is practical discrimination evidence for the specified A, with no
  causal attribution. **A was closed.**

**Candidate B: grid-calibrated p over a declared composite null.** A screen
calibrated v1's p against v1's own 1,000 low-s values and applied the result
to the stored power blocks.
- Detections fell from 21 to 6/300 at β_min and from 206 to 98/300 at
  Δ10 = 0.5.
- These counts are specific to that table and sample; B is not a validated
  procedure.
- **B was deferred.**

**Summary.** For the two specified count-only repairs, reducing the excess
rejection rate came with substantial losses in detection. At the tested
corner, information about the nuisance values reduced the excess rejection
rate. We do not generalise these results to every possible count-based
method.

---

## Remaining sections (skeleton)

**1. Introduction.**
- The vortex concept, and Fagan and Holmes (2006), who acknowledged their
  extinct-only selection.
- The open question: a matched no-feedback reference.
- Our contribution: a matched-outcome test of reconstructed pooled
  terminal-trajectory statistics, with measured limits on calibration and
  discrimination.
- **The no-feedback contrast** is the absence of the specified
  abundance-dependent feedback in expected growth, not the absence of every
  process called a vortex.
- **Prior art.** Boettiger and Hastings (outcome-selection bias); Hefley et
  al. (external deterioration against density dependence); Griffen and Drake
  and Lande (conditioned terminal decline); Wittmer et al. 2005 (caribou,
  across populations). *These are pointers from the project's literature
  audit; check the primary passages before the final wording.*

**6. [P] External demographic information.** An optional design (revision 2,
`vortex_external_info_design_20261014.md`). Included only if run and reviewed.

**7. Case study: Haley Lake** (descriptive). See
`haley_case_narrative_20261014.md`. Caribou may follow after the census-class
and time-label crosswalk.

**8. Discussion.**
- What these statistics can and cannot show from counts alone.
- What demographic information would be needed.
- Implications for diagnosing vortex dynamics in conservation assessments.
- **Limitations:**
  - a single null model class;
  - exposure;
  - the unpassed reconstruction;
  - development is not validation;
  - source conflicts;
  - incomplete case ledgers.
