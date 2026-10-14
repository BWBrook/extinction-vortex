# Core methods and results: draft manuscript text

Fable, 14 October 2026 (Australia/Hobart).

**Revision 2.** Incorporates Astra's core review
(`notes/astra_core_manuscript_review_20261014.md`) and outline review
(`notes/astra_paper_outline_review_20261014.md`). Where they differ, it
supersedes `vortex_paper_outline_20261014.md`. Every number is taken from an
archived summary or audit, cited in brackets.

The Introduction and Discussion remain skeletons. The novelty wording waits on
a narrow primary-text check of the prior-art passages.

**Working title.** *Testing extinction-vortex signatures in outcome-selected
population counts*

**Evidence categories**, used as section labels:

| Label | Evidence |
|---|---|
| [R] | exposed historical reconstruction and source reconciliation |
| [V] | the prospectively frozen v1 synthetic validation, after documented development |
| [D] | exposed post-validation development diagnostics and candidate screens |
| [P] | optional planned work; no results, no execution authority implied |

---

## Abstract (draft)

Fagan and Holmes (2006) reported extinction-vortex signatures in nine
populations whose counts ended at one or none. Their four terminal-trajectory
statistics (T1–T4) describe how decline and variability change as the
terminal count approaches.

We reconstructed these statistics, then asked whether a matched-outcome
reference, built from simulated counts selected by the same terminal rule and
conditioned on calibration summaries of the counts, can test them against a
specified population process without abundance-dependent feedback.

In a synthetic validation frozen before any of its trials was run, the
procedure:
- met its null-calibration criterion under the prior predictive and at two
  fixed nuisance settings;
- failed it at a low-survival setting, with 148 non-acceptances in 1,000
  against at most 60;
- detected feedback of the risk-defined strength in 21 of 300 datasets.

Under the protocol, the empirical test was therefore not run. The procedure's
result is reported as insufficient identification.

Development diagnostics followed the validation. In paired datasets at the
low-survival setting, replacing the reference's prior-mixed nuisance values
with the generating values reduced rejections from 34 to 7 of 200. A fixed
screen of one count-only repair (augmented calibration summaries) reduced
excess rejection, but lost most detection of strong feedback. A post-hoc
rescoring of a second repair also lost detection.

A source-matched case study (Haley Lake marmots) shows what age structure,
marked-animal persistence, reproduction and movement add to a count series,
and what they leave unresolved.

**The specified count-based procedure did not support empirical feedback
inference.** The reference sensitivity and case evidence motivate testing
procedures that use additional demographic information. These results do not
show that feedback is present or absent in these populations.

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

Each series runs to its first recorded count ≤ 1. That is the operational
terminal event, not proof of biological extinction.

**Census classes.** These differ, and the series are not verified complete
censuses. Source matches, interventions and conflicts are given per series in
the nine-series evidence table, without a blanket closure claim.

**Exposure chronology** [exposure log E01, E13–E16, E20–E30]. Exposure
accumulated in phases:
1. The published outcomes were known before initial drafting.
2. Reconstruction fits preceded the choice of the random-intercept estimator
   as primary (protocol §4.2).
3. The empirical calibration summaries and development outputs preceded the
   choice of the null and reference design.
4. The final procedure was frozen before the fresh v1 validation trials were
   run.

The analysis is therefore an **outcome-exposed reanalysis with a prospectively
frozen synthetic validation**.

**Time indexing.** Let T be the calendar year of the terminal count and
N_s = N(T − s), so s counts years remaining. Each annual log change is
attached to its *later* census:
D_s = ln[N(T − s) / N(T − s − 1)] = ln(N_s / N_{s+1}).
The final transition has s = 0.
- The endpoint count is replaced by 1 for the log-growth calculation only; no
  source count is altered.
- Calendar gaps are excluded from the log-change regressions, not annualised.
  The AR(1) term keeps the integer s positions, and the generator still
  propagates annually through unrecorded years. The deposited primary windows
  contain no such gaps, but the rule defines the procedure and its fill
  sensitivities.

**Statistics.**
- **T1:** the slope of D on s. For example, counts 20 → 10 → 1 give
  D_1 = −0.693 and D_0 = −2.303. A more severe terminal decline therefore
  shows as a **positive** slope on years remaining.
- **T2:** the mean model refitted on exactly the non-final transitions
  (s ≥ 1).
- **T3:** the slope on s of the squared level-1 conditional response
  residuals from the T1 model. A more negative T3 means larger squared
  residuals nearer s = 0.
- **T4:** the mean model refitted on s ≥ 1, its own squared conditional
  residuals then regressed on s.

All four come from a random-intercept multilevel model with AR(1) errors,
fitted by marginal ML across the nine series. They are **pooled
terminal-trajectory statistics, not single-population tests**.

**Reconstruction status: not passed.** Two separate implementations agree at
matching covariance parameters: the maximum log-likelihood difference over 32
comparisons is 6.25×10⁻¹³. Separately optimised fits can differ. The
implementations were not blinded, since one reviewer had seen the other's
fitted summaries. Neither reproduces every published value within the ±0.0005
criterion [protocol §4.2; Stage B record]. T5 and the scaling model were not
reconstructed. This is source and estimand reconstruction, not replication of
the historical estimator.

| Statistic | Published | Reconstructed (random intercept) | Within ±0.0005 |
|---|---:|---:|---|
| T1 | 0.034 | 0.03344 | no |
| T2 | 0.011 | 0.01123 | yes |
| T3 | −0.047 | −0.04787 | no |
| T4 | −0.012 | −0.01185 | yes |

## 3. Methods [V]

### No-feedback process M0 (ar_cat)

For each population, with B_t a catastrophe indicator (probability p_c) and
z_t a stationary Gaussian AR(1) environment with coefficient ρ and unit
variance:
- annual survival: S_t = (1 − δB_t) · logit⁻¹(logit s + σz_t);
- per-capita recruitment rate: F_t = (1 − δB_t) · f · exp(σz_t − σ²/2);
- N_{t+1} = Binomial(N_t, S_t) + Poisson(N_t F_t), with the first count
  fixed at the observed one and zero absorbing.

The structural null excludes direct abundance effects given the environment.
It does not make abundance and an autocorrelated environment statistically
independent.

### Prior (b)

Independent design priors before selection; they are not recovered
demographic estimates:
- logit s ~ Normal(0, 1.5²);
- log f ~ U(log 0.01, log 2);
- σ ~ U(0.02, 1);
- ρ ~ U(0, 0.9);
- p_c ~ U(0, 0.05);
- δ ~ U(0.5, 0.95).

### Selection

- **Terminal rule (S).** A simulated path is included under the same recorded
  terminal rule as the retrospective sample: all interior recorded counts
  > 1, and the final count ≤ 1, on each series' census years.
- **Cap event (A).** Counts and Poisson rates must stay ≤ 10⁹. Overflowed
  paths are excluded and counted.
- θ and the path are drawn jointly, then selected.

### Conditional reference

- **Bank.** Per population, 2×10⁹ prior draws (20 shards); 13.46–29.90
  million selected paths.
- **Calibration summaries C.** The mean square, lag-1 autocorrelation and
  fraction of increases of the non-final log changes, MAD-scaled on the bank.
  Zero-MAD columns are dropped.
- **Library.** For an outer dataset, each population's K = 2,000 nearest bank
  paths in C. This finite-bank k-NN reference *approximates* conditioning on
  C. Exact exchangeability holds only for the ideal selected prior-predictive
  law with exact conditioning. The pass criteria do not imply exact 5% size,
  or uniform control over the nuisance space.
- **Reference datasets.** R_train = R_test = 2,000. Each draws one library
  path per population.

### Test statistic and outcome

- **Fitting.** T1–T4 are fitted to the outer dataset and to every reference
  dataset. A *failed vector* is any dataset with a missing T1–T4; it is not
  counted as four separate fits.
- **Statistic.** Q = (T − μ)ᵀ Σ⁻¹ (T − μ), the squared Mahalanobis distance
  from the training mean μ.
  - Σ is the training sample covariance. Up to 40 failed training vectors
    (2%) are omitted from it; more than 40 makes the trial indeterminate.
  - Ledoit–Wolf shrinkage applies only when the condition number exceeds
    10⁶. No v1 trial required it.
- **p-value bounds.**
  - p_lo = (1 + e) / (R_test + 1) and p_hi = (1 + e + m) / (R_test + 1).
  - e counts valid test vectors with Q ≥ Q_obs; m counts failed test vectors.
  - The denominator stays 2,001.
- **Outcome.**
  - Reject if p_hi < 0.05; accept if p_lo ≥ 0.05; otherwise indeterminate
    (straddle).
  - Also indeterminate: a failed observed vector, malformed output, an
    unusable covariance, more than 40 failed training vectors, or an exhausted
    outer sampling budget.

### Alternatives (frozen; supplementary table)

**M_A (feedback).** g(N) = exp(−β(1/N − 1/50)) for 0 < N < 50, and g = 1
for N ≥ 50. g multiplies the *pre-catastrophe* survival odds and the
recruitment rate, giving S_t = (1 − δB_t) · logit⁻¹(logit s + σz_t + log g(N_t)).
- Effect size is indexed by Δ10 = 1 − g(10), the reduction in the multiplier
  at abundance 10. It is *not* a probability difference.
- **β_min** is the first point on the declared Δ10 grid (steps of 0.025) that
  gives an estimated increase of **at least 0.10** in the probability of
  reaching a count ≤ 1 within ten years, from N0 = 20, at the pooled
  component-wise library medians. Each grid point uses 100,000 draws.
  - At Δ10 = 0.075 (g(10) = 0.925; β_min = 0.974519) the baseline is
    0.41431, under M_A it is 0.55012, and the difference is 0.13581.
  - The preceding point, Δ10 = 0.05, gives +0.08932.
  - β_min is a grid point, not an exact continuous minimum or a minimum
    detectable effect.

**M_D (environmental deterioration).** z_t − m(t) enters both vital rates.
- m(t) is linear, accelerating (quadratic) or a step.
- The end-of-series shift is Δ ~ U(0, 2), and the step year is uniform over
  the annual steps.

**M_O (abundance-dependent detection).** Recorded counts are
Binomial(N, p(N)), with p(N) = 1 − 0.3·exp(−N/10) ("low-n") or p = 0.9
("uniform").
- The latent start is round(n0 / p(n0)), and the recorded start stays n0.
- Selection applies to the *recorded* counts and does not require latent
  extinction.

**Mixtures** use β_min. The scenarios are not matched in risk or vital-rate
effect.

### Validation design

Frozen on 11 October 2026 (source `52779d0`; manifest `96603037…`). An
independent reviewer accepted it before any fresh v1 validation trial was run.

| Block | Role | n | Criterion |
|---|---|---:|---|
| 1–4: prior-predictive null; fixed corners high σ, low s, strong environment | null gates | 1,000 each | upper one-sided 98.75% Clopper–Pearson bound ≤ 0.08 (≤ 60 non-accepts; Bonferroni over four). Any failure is **V-fail**, which overrides every empirical label. |
| 5: M_A at β_min | O1 power criterion | 300 | lower one-sided 95% bound ≥ 0.70 (≥ 224 detections). It governs O1 eligibility only; failing it alone leaves O2/O3 open. |
| 6–16: alternatives and mixtures; 17: fitted-parameter stress check | descriptive | 300 each | exact 95% intervals |

**Failure accounting.**
- Unresolved outer trials count as non-accepts for the null gates and as
  non-detections for the O1 criterion.
- Sampling-budget failures stay in those outcome denominators, but not in the
  fit-failure denominator.
- **Fit stop:** more than 2% failed vectors in any gating block.

**Execution.** 48 one-node PBS slot jobs on TPAC kunanyi, 11 October 2026.
- Host preflight on `n001.kunanyi`: Python 3.11.7, NumPy 1.26.4, SciPy
  1.11.4, R 4.3.3, nlme 3.1.171.
- The summary was rescored independently, and the collector re-run on a second
  host reproduced it byte for byte.

## 4. Results I: validation [V]

**Null gates.** 46, 41, **148** and 30 non-accepts per 1,000 for the
prior-predictive, high-σ, **low-s** and strong-environment scenarios. Only
low-s fails, with an upper bound of 0.175 against 0.08. **The result is
V-fail.**

**O1 power criterion.** 21/300 at β_min, with a lower bound of 0.047 against
0.70. It fails.

**Failures.** No vector failed in any gating block. Four failed T vectors
occurred overall, all in descriptive blocks 14–16. All 7,900 trials resolved.

**Consequence.** The null failure overrides every empirical label. The
pre-specified guard refused the empirical run, and the protocol reports this
procedure's result as **insufficient identification**. That is a disposition
of the failed procedure, not a general theorem about the information in the
counts.

**Q2 profile** (blocks 6–17). These are detection rates of a procedure that
failed its null-calibration requirement. They are descriptive only and do not
repair V-fail.

| Scenario | Detections / 300 |
|---|---:|
| M_A at 2β_min | 25 |
| M_D: linear / accelerating / step | 16 / 26 / 17 |
| M_O: low-n detection / uniform detection | 15 / 17 |
| M_A + M_D: linear / accelerating / step | 42 / 40 / 28 |
| M_A, Δ10 = 0.3 | 118 |
| M_A, Δ10 = 0.5 | 206 |
| Fitted-parameter stress check (block 17) | 11; no unresolved trials |

**Radius strata** (predeclared; descriptive). The low-s excess is not confined
to the widest-radius bin: 33/250, 43/318, 40/241, 18/133 and 14/58. Maximum
radius is a coarse diagnostic and does not exclude approximation error.

## 5. Results II: development diagnostics and attempted repairs [D]

These analyses followed the validation outcome and use exposed outputs or
development seeds; none is validation. The diagnostics and fixed candidate
screens were audited, with the provenance limits recorded in the supplement:
- some were post hoc (D1/D2);
- some involved no new fitting;
- D3's runtime record was made at report time.

**Nuisance displacement (association only).** Reconstructed neighbourhoods
matched v1's logged (rounded) K-th distances. Historical membership at tied
boundaries was not directly verified, and it was demonstrably sensitive to the
query.
- At the low-s corner, the generating survival ranked low within its library:
  population means of 0.09–0.33, against about 0.5 under the prior
  predictive.
- The trial-level association between displacement and rejection was weak,
  and in the wrong direction for a dose–response reading.
- This neither supports nor rules out nuisance mixing as the mechanism.

**Paired oracle reference (D3).** 200 fresh low-s datasets, each scored two
ways:

| Reference | Non-accepts / 200 |
|---|---:|
| frozen prior bank | 34 |
| fixed bank at the generating values of all six nuisances | 7 |

- Paired table (both, prior only, oracle only, neither): 3, 31, 4, 162.
  McNemar p = 3.5×10⁻⁶.
- Difference −0.135, with a Newcombe hybrid-score interval of (−0.194,
  −0.080).
- The oracle removed the T1/T2 location shift: mean standardised residuals
  −1.86 and −1.73 under the prior reference, −0.07 and −0.13 under the
  oracle.

At one low-survival corner, replacing the mixed reference with the generating
nuisance values reduced rejections from 34/200 to 7/200. The oracle changes
the whole nuisance law, and also the bank and neighbourhood geometry: its
median maximum K-th distance in the original C metric was 0.89, against 0.26.
The result:
- does not isolate survival;
- does not exclude locality or approximation effects;
- does not establish calibration across the nuisance space;
- is not usable empirically, since the generating values are unknown.

**Candidate A: summaries targeting demographic variance** (measured,
fixed-screen comparisons). C was augmented with the slope and intercept of
squared log change on 1/N.
- **No-fit pre-screen.** Nuisance displacement was unchanged. Neighbourhoods
  were about 5 times wider in the original C metric.
- **Fixed 200-case low-s screen.** 11/200 non-accepts against 21/200 for v1 on
  the same datasets. Difference −0.050 (−0.098, −0.005); McNemar p = 0.041.
  The T1/T2 shift largely persisted.
- **Fixed 600-case power screen.** Detections fell at β_min (21 → 11/300) and,
  sharply, at Δ10 = 0.5 (206 → 28/300; difference −0.593, −0.646 to −0.533).
- This is practical discrimination evidence for the specified A, with no
  causal attribution. **A was closed.**

**Candidate B: grid-calibrated p** (post-hoc rescore only). This is not a
fresh calibration result.
- The same exposed v1 low-s table (1,000 p-values) was used as a calibration
  CDF for the stored power blocks.
- Detections fell from 21 to 6/300 at β_min and from 206 to 98/300 at
  Δ10 = 0.5. Any full B that keeps that table can reject only a subset.
- B has no fresh null-calibration result and is not a second demonstrated
  repair. **B was deferred.**

**Summary.**
- For the specified candidate A, a measured reduction in excess rejection came
  with a large loss of detection. B's post-hoc rescore also lost detection.
- At the tested corner, generating-value nuisance information reduced the
  excess rejection rate.
- We do not generalise these results to every possible count-based method, and
  we do not claim the trade-off is inevitable.

---

## Remaining sections (skeleton)

**1. Introduction.**
- The vortex concept, and Fagan and Holmes (2006), who acknowledged their
  extinct-only selection.
- The open question: a matched no-feedback reference.
- **Contribution:** a matched-outcome test of reconstructed pooled
  terminal-trajectory statistics, with measured limits on calibration and
  discrimination.
- **The no-feedback contrast** is the absence of the specified
  abundance-dependent feedback in expected growth, not the absence of every
  process called a vortex.
- **Prior art.** Boettiger and Hastings; Hefley et al.; Griffen and Drake and
  Lande; Wittmer et al. 2005. *These are literature-audit pointers; verify the
  primary passages before the final wording.*

**6. [P] External demographic information.** An optional design (revision 2),
with a bounded no-fit Stage 0. It appears here only if run and reviewed.

**7. Case studies** (descriptive):
- Haley Lake, `haley_case_narrative_20261014.md`;
- caribou: Banff, Maligne and Purcells Central (in preparation);
- the nine-series evidence table (in preparation).

**8. Discussion.**
- What these statistics can and cannot show from counts alone under the
  specified procedure.
- Which demographic information could be tested next.
- Implications for diagnosing vortex dynamics in conservation assessments.
- **Limitations:**
  - a single null model class;
  - phased exposure;
  - the unpassed reconstruction;
  - development is not validation;
  - source conflicts;
  - incomplete case ledgers.
