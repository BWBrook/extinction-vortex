# Vortex signatures, selection and feedback: staged study protocol

**Working draft 0.9 — 10 October 2026, Hobart. Not frozen or registered.**

Draft 0.9 (Fable) responds to Astra's 0.8 review (1348); §9.10 lists the
changes:
- executable M_D and M_O laws with limiting-case tests;
- the stress check's fixed-mixture sampling law;
- frozen radius bins;
- the §4.1 development screens retained and running;
- a complete execution inventory;
- the scorer's finite-bound check;
- designated banks queued;
- a draft [freeze package](vortex_freeze_package_20261010.md).

**Working draft 0.8 — 10 October 2026, Hobart (history).**

Draft 0.8 (Fable) incorporates Barry's adoption of ar_cat as the primary
development null (iid a mandatory sensitivity) and Astra's 0.7 review
(1253/1255); §9.9 lists the changes:
- the k-NN library as the development algorithm, with radius-stratified
  diagnostics and a local stress check;
- input guards, a training-failure rule, fallback logging and recorded
  feature flags;
- 10× development banks with measured library radii;
- the development β_min and numeric corner scenarios under ar_cat;
- a measured cost inventory;
- a bounded power screen.

**Working draft 0.7 — 9 October 2026, Hobart (history).**

Draft 0.7 (Fable) responds to Astra's 0.6 review (1226/1228); §9.8 lists the
changes:
- the discrimination screen, scored with fixed denominators;
- an outer-C coverage check;
- a proposed k-NN library with 10× banks;
- a narrowed candidate conclusion, with the Student-t comparator retired;
- the capped target A;
- consolidated seed, fallback and failure text.

The choice of null remains **proposed** until Barry decides it (§3.1).

**Working draft 0.6 — 9 October 2026, Hobart (history).**

Draft 0.6 (Fable) responds to Astra's 0.5 review (1212/1214); §9.7 lists the
changes:
- a structural H0;
- corrected catastrophe priors and rationale;
- a heavy-tailed comparator;
- a common-footing comparison of candidate nulls on deep-server;
- a single bank-sizing rule with a cap;
- the second-bank check made descriptive;
- contradictions removed;
- reserved final seeds;
- an end-to-end benchmark.

The choice of null remains **proposed** until Barry decides it (§3.1).

**Working draft 0.5 — 9 October 2026, Hobart (history).**

Draft 0.5 (Fable) applies five groups of changes; §9.6 summarises them:
- Barry's adopted target: reconstructed T1–T4, with the random-intercept model
  primary and the random-slope model a mandatory sensitivity (Decision Inbox,
  9 October 11:06 AEDT, `docs/decisions/01663ea4-…`);
- Astra's 0.4 review repairs (1188);
- the interpolation fix;
- measured development benchmarks;
- a **proposed** extension of the no-feedback null to include catastrophes.
  This is pending Astra's review (§3.1).

**Working draft 0.4 — 9 October 2026, Hobart (history).**

Draft 0.4 (Fable) incorporates three groups of changes into §§1–4 and 7, with a
summary in §9.5:
- the repairs accepted in 1049/1051;
- Astra's source audit;
- the Stage B results.

**Requires Barry's decision:** the proposed amendment in §4.2. It sets the
primary target to a labelled reconstruction of T1–T4 and removes T5 from the
primary test.

**Earlier drafts (history):** 0.3a — 5 October 2026.

Draft 0.3a: Astra completed the [bounded review](astra_protocol03_review_20261005.md)
and finalized the [decision brief](vortex_decision_brief.md) after Fable's
review. Section 9.4 records the remaining production requirements and defines
the smaller first tranche recommended to Barry. The formal production text in
§§1–4 and 7 remains proposed; its outstanding points are not freeze-ready.

Draft 0.3: Fable revised §§1–4 and 7 in response to Astra's review (R1–R6) and
added §9.3. Astra's 0.2a changes to §§5–6, 8 and 9.2 are unchanged. The
history below is kept.

Draft 0.2: Fable formalised §§1–4 and 7, which replace Astra's planning
summaries, and added a requirement-status table to §9. In 0.2a, Astra addresses
Fable's amendments to §§5–6 and 8, and appends its review disposition in §9.2.
The [draft 0.2 quantitative review](astra_protocol02_review_20261005.md)
records the defects that prompted revision; §9.4 gives their current status.

Barry has expressed a provisional preference for this question and requested a
careful plan combining simulation and empirical work. This document prepares
that plan. It does not record a topic decision or authorize the research stages.

Astra drafted §§5–6 and 8 and the coordination provisions in §9. Fable wrote the
formal §§1–4 and 7 (draft 0.2), absorbing Astra's planning summaries and
requirements. Barry's topic and first-tranche decision is next; the agents
will handle the remaining development tasks if that tranche is authorized.
The original [round-2 proposal](fable_round2_response_20261005.md) is preserved
as proposal history; this draft records subsequent qualifications and unresolved
requirements.

The compilation will adapt [PRISMA-P](https://www.prisma-statement.org/protocols),
[PRISMA-S](https://www.prisma-statement.org/prisma-search) and the ecological
reporting guidance in [PRISMA-EcoEvo](https://www.prisma-statement.org/ecoevo).
These guide transparent protocols, searches and reporting. A local, dated
pre-analysis commitment supplies the prospective element; it is not an external
registration or a claim of full PRISMA compliance. The study is an empirical
reanalysis with simulation validation, not necessarily a meta-analysis.

## 1. Scientific aims and minimum contribution — Fable formal draft 0.6

Draft 0.3 answers Astra's quantitative review (R1–R6). The main changes from
draft 0.2:
- Part 1 is limited to discrepancy testing plus measured discriminability; the
  feedback classifier is removed.
- The null is now a valid probability model.
- The genetic alternative is deferred.
- The test's target and algorithm are named and specified.
- Validation uses confidence-bound criteria.
- The compute figure is replaced by a benchmark.

**Q1 (primary, empirical).** Take the nine-population Fagan–Holmes (F&H)
terrestrial sample. Are the observed values of the terminal-trajectory
statistics T1–T4 (§2.1; T5 descriptive, per the §4.2 amendment adopted by Barry)
compatible with their conditional
reference distribution under a population-matched no-feedback process M0
(§3.1, §3.4)? The simulated data must pass through the same selection, census
processing and estimator as the observed data.

**Q2 (primary, simulation).** Under the same matched design, with what
probability does the Q1 test flag a departure when the data come from each
specified alternative and mixture (§3.2)? Q2 measures *discriminability*. It
does not attribute causes. Draft 0.2's aim of attributing departures to
feedback is withdrawn for the first analysis: choosing among pure generators
cannot identify causes when forcing, feedback and observation error coexist.

**Q3 (secondary).** The Williams series, with their published pipeline. Index
and density series need observation models first, so the first tranche covers
only the series confirmed as complete counts.

**Q4 (Part 2).** Parked; see §2.3.

**Minimum contribution:** Q1 together with Q2.

**Outcome labels.** Validation (§4.3) comes first, and its failure overrides
every empirical label.

| Label | Condition |
|---|---|
| **V-fail / indeterminate** | Validation fails, or the replication budget runs out undecided. The empirical result is reported only as *insufficient identification*. |
| **O1 conditional compatibility** | p_joint ≥ 0.05, *and* the lower one-sided 95% bound on power at β_min (§3.3) is ≥ 0.70 |
| **O3 insufficient discrimination** | p_joint ≥ 0.05, but that power bound is < 0.70 |
| **O2 departure from M0** | p_joint < 0.05. Reported with the Q2 rates showing which specified alternatives and mixtures produce such departures, and how often. |

O1 is compatibility conditional on the model and the prior. It is not proof
that feedback is absent, and not a posterior probability of the null. O2 is not
evidence of genetic or Allee feedback unless further, mechanism-specific
evidence is added.

## 2. Estimands and comparison populations — Fable formal draft 0.6

### 2.1 Part 1 design, statistics and target

For each population i, the design records:
- the first census N_i,first;
- the census years, including the documented interpolations (one census each
  for the wild dog and the middle spotted woodpecker);
- the extinction rule E (F&H: first census ≤ 1);
- the extinction census year, and hence L_i;
- the published final-step convention, N_0 := 1.

**Windows.** The F&H windows cannot be recovered from the printed text. Their
printed durations imply 146 non-terminal censuses, against the 148 stated in
the text (Astra source audit). The windows are therefore fixed as follows:
- **Primary:** the deposited Williams series up to the first census ≤ 1.
- **Sensitivity:** the F&H-length variant (`analysis/fable/stage_b`), where
  the deposited data allow it.
- **Wild dog:** the deposited values for 1971, 1972 and 1978 are missing in the
  author-distributed MARSS series. A sensitivity treats them as missing.
- **Crane:** the deposited counts match the official Rocky Mountain flock
  totals. Under rule E, the extinction census is 2002.
- **Missing years** (Astra review §6).
  - A census gap is never annualised. A log change spanning a gap is excluded
    from D.
  - AR(1) uses the integer s positions, so a gap is a lag greater than one.
  - The observed and simulated series are treated identically.
  - The primary deposited data have no gaps.
  - The wild-dog fill sensitivity treats 1971, 1972 and 1978 as missing in both
    observed and simulated data.
  - A secondary fill sensitivity re-creates the fills in simulated data. It uses
    joint linear interpolation between genuinely observed neighbours; the
    sampler bug is repaired (§3.1). The historical fill and rounding rule is
    unverified.

**Census ledger.** The audit's per-population fields (census unit, age class,
observation process, closure, intervention, study cluster) are carried as
provisional attributes, per [the source audit](astra_source_audit_20261008.md).
- The claim that all nine series are complete counts of individuals is
  withdrawn.
- Unit conflicts, such as the middle spotted woodpecker's individuals vs
  pairs, stay unresolved. No conversion is made.

The five statistics are those F&H published:

| Statistic | Definition | Published value |
|---|---|---|
| T1 | slope of D_s = ln(N_s/N_{s+1}) on s | +0.034 |
| T2 | T1 excluding the final transition | +0.011 |
| T3 | slope of the squared T1 residuals on s | −0.047 |
| T4 | T3 excluding the final transition | −0.012 |
| T5 | period effect (s ≤ 9 vs s ≥ 10) in the regression of s on ln N_s | F&H print only z = 2.3 and two fitted curves; no single coefficient is reconstructable |

T1–T4 are computed by the adopted estimator (§4.2): a random-intercept
multilevel model with AR(1) errors, fitted by marginal ML.
- **Definitions** (adopted): D_s = ln(N_s/N_{s+1}), with the endpoint count
  replaced by 1 for log growth only.
  - T1 is the slope of D on s.
  - T2 refits D ~ s on exactly the non-final transitions (s ≥ 1).
  - T3 is the slope on s of the squared *conditional* response residuals from
    the T1 model.
  - T4 refits the mean model on s ≥ 1, then regresses its squared conditional
    residuals on s.
- **Primary statistic set:** T1–T4, adopted by Barry on 9 October. The
  random-intercept-and-slope model is a mandatory sensitivity.
- **T5 and the time-to-extinction scaling model:** these leave the primary
  test, but are reported descriptively. With AR(1) errors and s as the
  response, the scaling model degenerates (φ → 0.99). Neither implementation
  reproduces F&H's published slope of 9.1.

**Target.** The conditional prior-predictive tail probability

> p_joint = P( D(T^rep) ≥ D(T^obs) | C^rep = C^obs, selection S, cap event A, M0, prior π ).

- A (draft 0.7, Astra 0.6 review §4): no count and no Poisson rate exceeds
  10^9 before the recorded endpoint. Bank and outer simulations apply it
  identically. The target is defined conditional on S and A; overall overflow
  of 0–3.3% does not bound A's effect on the selected law, and no claim is
  made about the uncapped law.

- D is the Mahalanobis distance of the vector (T1, …, T4) from a mean and
  covariance estimated on an independent *training* set of replicates (§3.4,
  step 4). Its tail probability is then computed on a separate *test* set.
- C is the vector of per-population calibration summaries (§3.4).

Properties of this target:
- **Ideal case only.** Suppose the data came from the null's prior predictive
  under S, conditioning on C were exact, and the reference were the exact
  conditional law rather than a finite bank. Then the observed and replicate
  T would be exchangeable given C, and the conservative rank p-value below
  would be valid. It is not claimed to be exactly uniform: ties and
  discreteness make it conservative.
- **What is implemented differs** in two ways: the ABC neighbourhood and the
  finite bank. Validation (§4.3) therefore measures the frozen procedure's
  actual false-alarm rate, under draws from the prior and at fixed boundary
  nuisance values.
- This is not Bayarri and Berger's partial posterior predictive p-value, and
  §4.3 is a false-alarm experiment, not simulation-based calibration of
  posterior ranks. The 0.2 labels are withdrawn.
- p_joint depends on the prior. Prior (b) is the prior *proposed for primary
  validation*; no prior has yet passed validation (§3.4).
- **What the implemented procedure is.** An approximate finite-bank ABC
  procedure.
  - With exact conditioning, the observation and the test replicates would be
    exchangeable.
  - In practice, the replicates follow the frozen bank's empirical law, and the
    observation follows the population law. Matching C does not remove that
    difference.
  - Validity is therefore claimed only as measured by §4.3: for the frozen
    procedure, the frozen bank or banks, the design, and the scenario
    distributions, against the 8% rejection ceiling. This is not exact 5% size,
    and not uniform control across all nuisance values.
- **Executable tie rule.** p_joint = (1 + #{D^test ≥ D^obs}) / (R_test + 1):
  every tie counts as an exceedance (conservative). This replaces "ties broken
  at random".

Per-statistic tail probabilities p_k are secondary.

### 2.2 Williams series (secondary)

The published Williams statistics are computed with the authors' archived code,
on the complete-count series confirmed in the source audit. Indices, densities
and the four unavailable series are reported but not tested in the first
tranche.

### 2.3 Part 2: parked, with open items recorded

Part 2 is not specified enough for any gate. These items are open:
- a complete likelihood: process, observation, random-effect, immigration and
  censoring distributions (draft 0.2 gave only a conditional mean);
- the units and pooling target of β, relative to the Gompertz term;
- the horizon;
- thresholds stated per stratum. Thresholds of 50 for all-individual counts or
  25 for pairs and territories are *operational* choices, not IUCN
  equivalents: IUCN Criterion D is a taxon-level criterion on mature
  individuals;
- a verified GPDD frame. A fixed frame controls our inclusion rule but does
  not show that GPDD monitoring was independent of fate.

Part 2 re-enters only by a dated amendment, after the first tranche.

## 3. Generative models and calibration — Fable formal draft 0.6

### 3.1 Null M0: a valid demographic model

**Structural H0 (draft 0.6, replacing the conditional-mean wording).** "No
direct feedback" means three things:
1. Given the parameters θ and the exogenous environmental state (z_t and any
   catastrophe indicator B_t), each individual's survival probability and
   expected recruitment do not depend on N_t.
2. The environmental transition law excludes N: z_t and B_t are generated
   without reference to abundance. This does not make z and N statistically
   independent; N_t carries information about past z (Astra 0.6 review).
3. In the plain Gaussian iid case (fixed θ, unselected paths),
   E[N_{t+1} | N_t, θ] / N_t does not depend on abundance.

With an autocorrelated environment (ρ > 0), N_t carries information about the
latent z_t. The conditional mean given N_t alone can then vary with N_t
without any feedback (Astra review of 0.5). The structural definition is the
one the test targets.

Feedback means vital rates that depend directly on N_t, given the
environment. It includes demographic Allee mechanisms (the M_A alternative)
as well as genetic ones. M_A and β_min are always defined on top of the same
environmental model as the null in use.

**Adopted primary development null (Barry, 9 October 2026, 14:51 AEDT;
Decision Inbox `d36e602c`, option `approve_ar_cat_primary`;
[amendment](vortex_null_amendment_20261009.md)).**
- **Primary:** ar_cat (M0\* below). Plain iid M0 is a mandatory, labelled
  sensitivity.
- **Scope.** This selects the candidate for the next development and
  validation design. It freezes no priors, β_min, scenarios, banks or
  production settings, and it does not declare the procedure calibrated.
- **What the choice does and does not claim.** The choice follows exposure to
  C and to synthetic development results. It does not validate the
  exploratory priors or show that catastrophes are needed. A rejection would
  concern this specified model; a non-rejection would not establish absent
  feedback.

The history of the proposal and its evidence follows.

> **Proposal (draft 0.5, revised in 0.6–0.7; adopted 9 October).** Make the primary
> no-feedback null **M0\***: M0 below, plus two additions.
> 1. An AR(1) environment, z_t = ρ·z_{t−1} + √(1−ρ²)·ε_t.
> 2. Density-independent catastrophes. Each year, with probability p_c, a
>    catastrophe multiplies survival and recruitment by (1 − δ).
>
> Priors in 0.6 (exploratory): ρ ~ U(0, 0.9); p_c ~ U(0, 0.05) per year;
> δ ~ U(0.5, 0.95). This revises 0.5's U(0, 0.15) and U(0.5, 0.99).
> - Reed et al. report a die-off occurrence of about 14% *per generation*.
>   With generation lengths of 3 years or more, that is an annual rate of
>   about 0.05 or less, so the prior is a bounded exploratory choice, not an
>   estimate.
> - The overflow rule (reject and count trajectories above 10^9) applies
>   identically to every variant, including plain M0.
>
> *Rationale.*
> - **Shaffer.** Shaffer (1981, doi:10.2307/1308256) lists demographic,
>   environmental, catastrophic and genetic sources of small-population risk.
>   Catastrophes and environmental variation act on vital rates without
>   abundance feedback, which supports *considering* them in a no-feedback
>   null. Feedback is not only genetic, though: demographic Allee effects
>   (M_A) are feedback too.
> - **Lande.** Lande (1993, doi:10.1086/285580) supports modelling
>   catastrophes alongside demographic and environmental stochasticity. He
>   does not supply these particular priors.
> - **Reed et al.** Reed et al. (2003, doi:10.1017/s1367943003003147) report
>   frequent die-offs. They also read die-offs as the tail of a continuous
>   distribution of population change, which is contrary evidence for a
>   separately identified catastrophe mechanism. Draft 0.6 therefore also
>   compares a heavy-tailed continuous environment ("heavy": standardised
>   Student-t, ν ~ U(2.5, 30)).
> - **H0.** The structural H0 above holds for every variant.
>
> *Development evidence.* These are synthetic banks under prior (b); the
> observed calibration summaries C were exposed, but no T1–T4 null comparison
> was run (`analysis/fable/calibration/`).
> - **Plain M0.** Selected runs rarely resemble the pre-terminal behaviour of
>   several series:
>   - the red-cockaded woodpecker's mean squared step is at the 0.2nd
>     percentile, and turtle B's at the 0.6th;
>   - the turtles' lag-1 autocorrelation is at the 99.6–99.7th percentile;
>   - at a calibration tolerance of 0.5, banks of 10^8 to more than 4 × 10^9
>     draws would be needed.
> - **M0\* (0.5 scan).** Marginal coverage improved, but the 0.5 claim that
>   every series lies between the 3rd and 97th percentiles was **false**:
>   turtle A's ACF sat at 97.4. Joint support was thin, with only 70–109
>   tolerance-1 hits in 2 × 10^6 draws for the dog and turtles. The 0.6
>   common-footing comparison replaces this evidence; see the comparison note
>   below.
> - Several series end in a single large drop: wild dog 26 → 0, red-cockaded
>   woodpecker 10 → 0, turtle B 8 → 0, turtle A 6 → 0. That is typical of
>   catastrophes.
>
> *0.6 common-footing comparison*
> ([`compare_nulls_v1/NOTE.md`](../analysis/fable/calibration/compare_nulls_v1/NOTE.md);
> deep-server, 2×10^7 draws per population and variant, common cap and
> selection).
> - Corrected in 0.7 (Astra 1228). Under the rule 3 × upper requirement
>   ≤ 10^9 draws: iid, AR, catastrophes-only and heavy each fit 7/9
>   populations; AR fails for the wild dog (1.23×10^9) and turtle B
>   (1.31×10^9), catastrophes-only for both turtles (up to 3.31×10^9).
> - **Only ar_cat fits all nine** (largest 3.37×10^8 draws), with every
>   summary between the 2.0 and 96.5 percentiles.
> - This is planning feasibility around the observed C among the candidates
>   actually implemented. It is not outer-dataset coverage and not evidence
>   that the populations need catastrophes or AR.
> - **The heavy comparator is retired as evidence.** For a standardised
>   Student-t with finite ν, E[exp(σZ)] is infinite, so its recruitment has
>   infinite mean before the cap; it is not a finite-mean match to the
>   Gaussian model, and AR plus continuous heavy tails was not tested.
>
> The proposal is therefore ar_cat as primary, an explicitly model-dependent
> no-feedback null, with plain M0 as a mandatory sensitivity (reported,
> possibly indeterminate for the turtles). This is a scientific choice for
> Barry; the discrimination screen and outer-C coverage check are summarised
> below.
>
> *0.7 discrimination screen*
> ([`discrimination_v1/NOTE.md`](../analysis/fable/calibration/discrimination_v1/NOTE.md);
> synthetic only; 30 outer datasets per arm; 2×10^8 banks; M_A at Δ10 = 0.5,
> a development effect, not β_min).
>
> | Arm | Procedure outcome (fixed denominator) | Raw p < 0.05 (diagnostic) |
> |---|---|---:|
> | iid null | 7/30 count against the null gate; all 7 are calibration shortfalls | 0/30 |
> | ar_cat null | 9/30 against the gate: 8 shortfalls, 1 rejection | 1/30 |
> | iid M_A | 20/30 detections | 29/30 |
> | ar_cat M_A | 14/30 detections | 21/30 |
>
> - At this bank size, calibration shortfalls dominate. The fix proposed is
>   in §3.4 step 3, with the coverage evidence in
>   [`coverage_v1/NOTE.md`](../analysis/fable/calibration/coverage_v1/NOTE.md).
> - Raw-p diagnostic under M_A: 0.97 [0.83, 1.00] with the iid design vs 0.70
>   [0.51, 0.85] with ar_cat.
>   - These are two *matched* designs. The feedback-generating environment
>     changes together with the reference, and the arms share random streams.
>   - So the contrast does not isolate a detection cost of broadening the
>     reference (Astra 1253). It is a warning about possible discrimination
>     limits, not validated power.
> - Fit failures: none in 240,120 datasets.

> *Scope.* This change is adaptive: it was chosen after exposure to C. With
> catastrophes in the null, a terminal crash counts as non-feedback. The study
> then tests whether vortex statistics exceed demographic, environmental and
> catastrophic risk. Plain M0 is retained as a mandatory sensitivity. Barry is
> informed; Astra reviews before any freeze.

- **Census and interval.** An annual census of all individuals at a fixed
  season, after recruitment. The model runs annually through missing years;
  only census years are recorded. Zero is absorbing. Rule E and the documented
  interpolations are applied to the recorded series exactly as in the source.
- **Parameters (per population).** These are sampled directly, so the support
  is valid by construction:
  - adult survival s_i ∈ (0, 1);
  - recruitment per individual f_i ≥ 0;
  - λ_i = s_i + f_i is derived, not sampled.
- **Transition.** N_{t+1} = S + R, where:
  - S ~ Binomial(N_t, s_t), with logit s_t = logit s_i + σ_i·z_t;
  - R ~ Poisson(N_t · f_t), with f_t = f_i·exp(σ_i·z_t − σ_i²/2);
  - z_t ~ N(0, 1): one environmental factor shared by survival and
    recruitment.
  - Sensitivity: separate factors with correlation 0.5.
- **Expected per-capita growth** (plain Gaussian iid case, fixed θ,
  unselected). It is E[s_t] + f_i, computed by numerical integration, and
  does not depend on abundance.
- **Invariant tests,** passed before any use:
  - support (survival in (0, 1), counts ≥ 0);
  - the identity E[N_{t+1} | N_t] = N_t(E[s_t] + f_i), checked by simulation
    to within Monte Carlo error;
  - absorption at zero;
  - exact replication of each census schedule and of rule E.
- **Scope.** The survival parameter is survival *of the census class*. It is
  not automatically an adult-survival estimate.
  - The census classes in the ledger (§2.1) are provisional: all-age counts,
    breeding units, peak winter counts.
  - The unstructured model is therefore an approximation. Stage-structured
    recruitment, and conversion between pairs and individuals, are
    misspecification checks for later work.
- **Implementation status.** M0 has been implemented twice: Astra in R
  (`analysis/astra/m0/`) and Fable in Python (`analysis/fable/m0/`). Both
  froze before comparison. They agree within Monte Carlo error on one-step
  means and variances in nine configurations, on selection acceptance (0.0370
  vs 0.0373) and on terminal profiles
  ([comparison](../analysis/fable/m0/compare_astra_m0.txt)).
  - The two-factor ρ = 0.5 sensitivity exists only in Astra's implementation
    so far.
- **Interpolation repair (9 October).** Adjacent gaps are now filled jointly
  between genuinely observed neighbours. Astra's [77, 999, 999, 43] case gives
  [77, 65.67, 54.33, 43], and a regression test is added (20/20 pass).

### 3.2 Alternatives and mixtures

| Model | Specification | Parameter values |
|---|---|---|
| M_A (feedback in expected growth) | the recruitment rate *and* the survival odds multiplied by g(n) = exp(−β(1/n − 1/N_ref)) for n < N_ref = 50; g = 1 otherwise | β ∈ {β_min, 2·β_min}. Because β ≥ 0 and n ≥ 1, g lies in (0, 1]. Effect sizes are set on the β scale, so doubling never gives an invalid multiplier. Report Δ10 = 1 − g(10) for interpretation. |
| M_D (external deterioration) | the mean of z_t shifted downward, which lowers survival and recruitment together | linear, −d·t; accelerating, −d·t²/L_i; a single step of size k at a uniformly random time. d and k are calibrated like the other nuisances. |
| M_O (observation change) | C_t ~ Binomial(N_t, p(N_t)) | p(n) = 1 − 0.3·exp(−n/10); plus uniform binomial census error with p = 0.9 |
| M_A + M_D | feedback combined with each deterioration form | for discriminability only |
| M_G (genetic) | **deferred** | see below |

**Executable laws (0.9; `bank.simulate_chunk`, tests in `test_bank.py`).** All
alternatives use the adopted ar_cat environment and prior (b) for the null
parameters. Each is tested against the ar_cat null bank.
- **M_A.** The vital-rate equations add log g(N) to the survival logit and
  multiply the recruitment rate by g(N). So g multiplies the survival *odds*
  and the recruitment rate.
- **M_D.** Both vital rates use z_t − m(t), where t = 1, …, span counts annual
  steps from the first census and span = last year − first year.
  - **Forms:**
    - linear: m = Δ·t/span, i.e. d·t with d = Δ/span;
    - accelerating: m = Δ·(t/span)², i.e. d·t²/span;
    - step: m = Δ·1{t ≥ τ}.
  - **Priors (proposed):** the end-of-series shift Δ ~ U(0, 2) in units of the
    environmental standard deviation; the step time τ ~ U{1, …, span}.
  - "Calibrated like the other nuisances" means these are prior draws
    followed by the exact selection S and the cap event A, as for the null
    parameters. The recruitment centring −σ²/2 is unchanged, so a shift lowers
    survival and recruitment together.
  - **These are design distributions,** not empirically estimated priors
    (Astra 0.9 review), and selection changes them after S and A.
  - **Equal Δ is not an equal effect.** The terminal multiplier on the
    recruitment rate and the survival odds is exp(−σΔ), which depends on σ.
    So equal Δ is not matched in vital-rate or risk effect across
    populations, and Q2 rates describe these alternatives without making
    them effect-matched competitors to M_A.
  - The shift and step time are kept per draw. Δ = 0 draws nothing and
    reproduces ar_cat exactly.
- **M_O.** The latent population follows ar_cat.
  - **Start:** the latent N0 is round(n0 / p(n0)); the recorded first count is
    n0.
  - **Recording:** later recorded counts are C_t ~ Binomial(N_t, p(N_t)),
    drawn from a generator spawned off the main stream, so the latent stream is
    unchanged.
  - **Selection:** S is applied to the recorded counts only. The first
    recorded count ≤ 1 must fall at the final census. Latent extinction is
    *not* imposed, so a selected path may be latently extant.
  - Latent counts are kept per draw, and each validation trial records the
    latent endpoint.
  - Laws: low-n, p(n) = 1 − 0.3·exp(−n/10); uniform, p = 0.9. With p ≡ 1
    the generator reproduces ar_cat exactly.
  - **Limitation.** The latent start is a plug-in scenario convention. It is
    not exact conditioning of a latent-abundance model on an initial binomial
    census.
- **Provenance** (0.9). Every validation trial row keeps, for each
  population, the selected draw's parameters (including the M_D shift and
  step time), its recorded counts and, under M_O, its latent counts.
  Rejected candidates are not kept.
- **M_A + M_D.** β = β_min, combined with each M_D form at the M_D priors.
  β = 0 reproduces the M_D component exactly.

M_G re-enters only by amendment. Draft 0.2's recurrence was invalid: it can
exceed one. A valid version needs:
- the bounded recurrence F_{t+1} = 1 − (1 − F_t)(1 − 1/(2·N_e,t)), with
  N_e,t = max(1, r·N_t);
- a stated time step and initial F;
- the haploid coefficient convention of O'Grady et al. (2006, Methods 2.1–2.3),
  with effects apportioned across life stages;
- r = 0.1 as the primary value (Frankham 1995) and 0.3 as a sensitivity only.

### 3.3 Effect target β_min

β_min is the smallest β at which M_A raises P(rule E is met within 10 years,
starting from N = 20) by at least 0.10 (absolute) over M0. It is evaluated at
the median calibrated M0 parameters.
- **If M0's probability exceeds 0.85,** restart from N = 50.
- **If no β ≤ β_max reaches the target,** where β_max is the value that sets
  g(10) = 0.1, then **O1 is unavailable**. β_max/2 may be reported only as a
  descriptive sensitivity.
- **Frozen search.** A grid of β in steps of Δ10 = 0.025, evaluated at the
  medians of the calibrated M0 libraries under prior (b), pooled across the
  nine populations.
- **Computation.** 10^5 runs per grid value, done once at Stage C before
  validation.
- **Under the adopted ar_cat null** (0.8). M_A and M0 share the ar_cat
  environment, the medians are those of the k-NN libraries at the observed C,
  and the median parameters include ρ, p_c and δ.
- **Scope.** β_min is the minimum *risk-defined* effect on the declared
  grid. It is not a demonstrated minimum detectable effect.
- **Development value** (10× development banks; `dev_design_v1/`; recomputed
  on the frozen banks).
  - Baseline: P(E within 10 years from N = 20) = 0.422 under the null, so
    N0 = 20.
  - **β_min = 0.975, i.e. Δ10 = 0.075**, with an increase of +0.130. Δ10 =
    0.05 gives +0.087.
  - That is g(10) = 0.925, a multiplier on the survival odds and the
    recruitment rate. Feedback this weak qualifies because the calibrated
    populations sit near the absorbing boundary.
  - **Development power** ([`power_screen_v1/`](../analysis/fable/calibration/power_screen_v1/NOTE.md);
    30 trials per arm, production counts, 10× banks):

    | Arm | Null | β_min | 2·β_min | Δ10 = 0.3 | Δ10 = 0.5 |
    |---|---:|---:|---:|---:|---:|
    | Detections | 1/30 | **1/30** | 2/30 | 8/30 | 18/30 |

    - If the frozen power gate fails as these figures indicate, an empirical
      non-rejection is **O3**. A validated empirical rejection can still be
      **O2**.
  - **The effect target is retained.** The risk-defined β_min stays as
    pre-registered. Validation reports a detection curve at β_min, 2·β_min,
    Δ10 = 0.3 and Δ10 = 0.5, descriptively, alongside the power gate.
  - Changing the target after seeing power would be an adaptive amendment for
    Barry, and is not proposed (Codex 1311/1313 concur).

### 3.4 Conditional calibration algorithm

1. **Bank.** For each population, draw parameters from the prior π and simulate
   M0 from N_i,first with the observed schedule. Keep the runs that satisfy S
   exactly: rule E is met first at the observed extinction census.
   - Bank size J_i and its cap follow the single rule in step 3 (the 0.4
     target of 2 × 10^5 kept runs within 10^8 draws is withdrawn).
2. **Calibration summaries C_i.** Three summaries, standardised by their median
   absolute deviation (MAD) within the bank:
   - the mean squared one-step log change, excluding the final transition;
   - the lag-1 autocorrelation of one-step log changes;
   - the fraction of increasing transitions.

   They are not independent of T, which is why the target is defined
   conditionally (§2.1).
3. **Library: k-NN** (proposed in 0.7; accepted for development by Astra,
   1253). This replaces the 0.6 hard tolerance and observed-C bank rule.
   - **Library.** The K = 2,000 bank runs nearest to c_obs,i in MAD-scaled
     summary space, with no distance cutoff.
     - This is rejection ABC with a fixed number of accepted simulations
       (Beaumont, Zhang & Balding 2002, doi:10.1093/genetics/162.4.2025).
     - It is the nearest-neighbour algorithm analysed by Biau, Cérou &
       Guyader (2015, doi:10.1214/13-AIHP590, Algorithm 2). Their
       consistency results need K → ∞ and K/N → 0 under extra assumptions.
       They certify neither a finite K = 2,000 bank nor this test's
       false-alarm rate.
   - **Bank.** Each population's frozen bank must hold at least K valid
     selected runs. The code refuses a smaller bank.
     - Development target: J_i = 2 × 10^9 draws per population, which is 10×
       the development banks.
     - J_i and the seeds are frozen before validation. Bank files keep draw
       indices, parameters, seed and overflow count.
   - **Recorded per trial and population** (diagnostics only; never labels):
     - the K-th neighbour distance;
     - features dropped for zero bank MAD;
     - observed series with constant changes (ACF set to 0).
   - **Approximation error remains** (Astra 1253). Removing distance
     abstention does not remove conditional approximation error, and §4.3's
     scenario-average 8% control is not a guarantee throughout C-space.
     Hence:
     - **Radius-stratified diagnostics, predeclared.** Each validation trial
       is binned by its largest K-th neighbour distance across the nine.
       Rejection rates with exact intervals are reported per bin, for every
       null scenario.
       - **Bins (frozen in 0.9):** (0, 0.2050], (0.2050, 0.2956],
         (0.2956, 0.4049], (0.4049, 0.5613], (0.5613, ∞).
       - **Source:** quintiles of 20,000 C-only ar_cat null prior-predictive
         outer datasets against the 10× development bank
         (`dev_design_v1/coverage`). This is independent of every validation
         draw and has no ties at the cut points.
       - **Ties:** a distance equal to a cut point goes to the lower bin.
       - The development empirical position, 0.433, falls in bin 4.
     - **Empirical position.** Before interpreting the empirical test, report
       the empirical largest K-th neighbour distance against those bins.
       - Development values, from C only, in the 10× development banks:
         ar_cat 0.433 (turtle B), at the 64th percentile of the null
         prior-predictive distribution; iid 1.073 (turtle B), at the 97th.
       - So the primary analysis has a typical radius, and the iid
         sensitivity lies in the tail (`dev_design_v1/`).
       - A typical radius does not by itself establish local conditional
         calibration (Codex 1313).
     - **Fitted-parameter predictive stress check, always run.** This is not
       conditional on the empirical position or p-value. It does not enforce
       C locality, so it is not a local calibration check.
       - **Datasets.** 300 intended outer datasets. Their parameter vectors
         are drawn **once**, uniformly from each population's empirical
         library (one per population per dataset), and retained.
       - **Selection.** For each vector, trajectories are simulated until the
         exact matched selection S and the cap event A hold, within a budget
         of 10^6 draws.
       - **Budget failures** (0.9, Astra 0.8 review).
         - A failure leaves that intended dataset unresolved. It is not
           replaced, so the uniform library mixture is preserved. A timeout
           is not proof that the vector is unselectable.
         - Unresolved datasets are reported with conservative descriptive
           bounds: rejection rate with all unresolved counted as rejections,
           and with all counted as non-rejections.
       - **Recorded.** Each dataset's K-th neighbour distances. Each dataset
         is tested with the frozen procedure, and the rejection rate is
         reported with an exact interval.
       - It is descriptive, not a gate. An empirical case in a poorly
         represented region is reported as a limitation.
       - **Single execution point:** validation block 17
         (`make_manifest.py` draws and keeps the sets; seed
         9 × 10^12 + 17 × 10^6 + 999).
       - **Implementation:** a budget failure is the outcome `indet_sampling`.
         It is recorded with the failed populations and their retained
         parameter sets, gets no fits, and is never replaced.
     - No extra radius gate is added. Support is never excluded after seeing
       a p-value.
   - **Evidence**
     ([`coverage_v1/NOTE.md`](../analysis/fable/calibration/coverage_v1/NOTE.md)).
     - Under the withdrawn hard tolerance of 1.0, 2 × 10^8 banks leave 31–33%
       of fresh null outer datasets short in at least one population; 10×
       banks would leave 4.5–4.9% short, and 100× about 0.5%.
     - The **projected** k-NN radius at 10× (ar_cat null; quantiles 0.50 /
       0.95 / 0.99) is 0.35 / 0.99 / 1.60. It is projected from the current
       bank's 200th-neighbour distances and omits variation in a future bank
       and its MAD.
     - Actual radii are measured in the constructed banks (§9.9).
   - **Plain-M0 sensitivity.** Under k-NN it returns a p-value for the
     turtles even though their observed C lies in the tail of the iid bank.
     It is reported with its K-th neighbour distances and labelled
     accordingly.
4. **Reference distribution** (repair 1, 1049/1051).
   - **Two independent replicate sets.** R_train = R_test = 2,000, chosen from
     the benchmark. The **same counts are frozen** for both validation and the
     empirical analysis (Astra review §1). Each replicate dataset takes one
     library run per population and is passed through the adopted estimator.
     At about 0.15 s per dataset, that is 600 s per analysed dataset.
   - **Training set.** Supplies the mean and covariance of T. Use Ledoit–Wolf
     shrinkage if the condition number exceeds 10^6.
   - **Test set.** D is computed for the test replicates and for the
     observation with the *same* training estimates. Exchangeability of the
     observation and test replicates holds only in the ideal case of §2.1;
     with the ABC neighbourhood and a finite bank it is approximate, and §4.3
     measures the realised rejection rate.
   - **Tail probability.** p_joint = (1 + #{D^test ≥ D^obs}) / (R_test + 1).
     Ties count as exceedances, per the executable rule in §2.1.
   - **Feature failures.** A calibration summary with zero bank MAD for a
     population is dropped for that population and recorded. An undefined
     autocorrelation (constant changes) is set to 0 and flagged. Both flags are
     recorded per trial (0.8).
   - **Finite bank.** The reference is conditional on the frozen bank.
     - Stability check: a second, independent frozen bank, specified before
       validation. Its result is **descriptive only**.
     - A difference between the two p_joint values is reported with its
       Monte Carlo context. It does not change any label and triggers no
       further computation.
     - The 0.5 "> 0.01 ⇒ indeterminate" rule is withdrawn. With R_test = 2,000
       it fires on Monte Carlo noise alone with probability 0.137 at p = 0.05,
       and about 0.5 at p = 0.5 (Astra, 1212).
   - **Failures.**
     - If the training distance cannot be built (e.g., a singular covariance
       after shrinkage), the dataset is *indeterminate*.
     - If a test replicate fails, report p-value bounds treating failures as
       most and least extreme. If those bounds straddle 0.05, neither O1 nor
       O2 is available.
     - Fallback fitting (frozen in 0.7 as implemented): optim, then nlminb;
       no further restarts. The new-start step is dropped: none of the
       240,120 development datasets in the discrimination screen (9 October;
       four nlme fits each) failed after the fallback. From 0.8 the number of
       fits needing the fallback is recorded per dataset.
     - **Training failures.** Failed training replicates are excluded from the
       mean and covariance and counted.
       - Minimum valid sample: if more than 2% of the R_train fits fail
         (more than 40 of 2,000), the trial is indeterminate (`indet_train`).
       - Otherwise the covariance rule applies: Ledoit–Wolf shrinkage if the
         condition number exceeds 10^6, and an unusable matrix after shrinkage
         is `indet_cov`.
       - Observed, training and test failures all count toward the §4.3 stop
         rule (> 2% in a scenario).
     - **Malformed fit output.** A T1–T4 file that does not hold exactly the
       sets 0…2R in order is `indet_malformed`.
     - **Outcome per trial.** reject; accept; or indeterminate
       (`indet_sampling`, `indet_malformed`, `indet_obsfit`, `indet_train`,
       `indet_cov`, `indet_straddle`).
       - `indet_sampling` means no selected trajectory was found within
         10^6 draws for some population. That is a sampling failure, not a
         fit failure.
     - **Fit-failure accounting.**
       - The numerator counts datasets with any missing T1–T4 among the
         observed, training and test datasets of each fitted trial
         (2R + 1 = 4,001 per trial).
       - A missing or malformed T file after sampling counts all 4,001 as
         failed.
       - Sampling failures are excluded from both numerator and denominator,
         and reported separately.
       - The diagnostic p, which ignores these, is archived separately and
         never labels a trial.
       - Code: `e2e_benchmark.py`. The `score_discrimination.py` contract v1
         covers the archived hard-tolerance runs; contract v2 covers the
         current runs.
   - **Fixed replicate counts.** No sequential stopping is used.
5. **Priors.**

   | Prior | Status | Survival | Recruitment, environment |
   |---|---|---|---|
   | (b) wide | proposed for primary validation; not yet validated | logit s_i ~ N(0, 1.5²) | log f_i ~ U(log 0.01, log 2); σ_i ~ U(0.02, 1.0); plus the M0\* parameters of §3.1 if adopted |
   | (a) literature-anchored | an unvalidated numerical sensitivity, built only where the ledger supports a census-class-matched survival source | logit s_i ~ N(logit s_lit, 0.5²) | as (b) |

   Prior (a) cannot borrow prior (b)'s power gate and cannot receive O1 or O2
   labels.

   Rules for prior (a):
   - Estimates fitted to the same trajectory are excluded as priors. Example:
     the crow plan's 79.8%, per the source audit.
   - Where prior (a) is reported, its numerical p_joint is shown beside prior
     (b)'s. A material difference is described as prior sensitivity. Prior
     (a) never receives an outcome label.

## 4. Stages, outputs and decision rules — Fable formal draft 0.6

### 4.1 First tranche (to be authorised by Barry, if selected)

This is Astra's proposed tranche, with concrete exit criteria:
1. **Source and metadata audit.**
   - Settle the three F&H windows, the endpoint evidence and the units.
   - Transcribe T5. Done: F&H print no single coefficient, so T5 is
     descriptive (§2.1).
   - Build the survival ledger.
   - Close the named prior-work gaps (final Nabutanyi–Wittmann text; Drake &
     Griffen 2009 methods).
2. **Stage B reconstruction.**
   - Both agents implement the F&H estimator independently from §2.1.
   - Pass: T1–T4 reproduced at published precision. Status: not passed; see
     §4.2. At published precision this means
     |Δ| ≤ 0.0005 (three decimals).
   - If that fails: a labelled *reconstructed estimand* with a discrepancy
     table. Never adjust dates, endpoints or values to obtain agreement.
3. **Development pilot** (synthetic only). The laptop limits no longer apply:
   since Barry's 8 October note, serious runs go to `deep-server` in tmux.
   - Implement M0, M_A, M_D and M_O and pass the §3.1 invariant tests.
   - Measure, per population, the acceptance rate of the exact selection S,
     simulation throughput, estimator fit time and failure rate, and memory.
   - Run one 200-dataset development screen under M0 and one at β_min.
   - Report a measured production estimate.
   - Stop before production if: a bank is infeasible; fits fail in more than
     2% of datasets; or the screen shows gross miscalibration (more than 30 of
     200 rejections).
   - **Disposition (0.9).** The requirement is retained and run as specified,
     not replaced by the 30-per-arm power screen.
     - Setting: the adopted ar_cat null, the k-NN library, the 10×
       development banks and production replicate counts.
     - Seeds 20261028 (null) and 20261029 (β_min).
     - Results: `analysis/fable/calibration/dev_screen200_v1/`. The stop
       rule applies to the null screen.

Production validation (§4.3) and the empirical test follow only with a
measured cost estimate and Barry's allocation.

### 4.2 Stage B: status and proposed amendment

**Criterion.** As in §4.1 item 2. The 0.2 tolerance of 0.005 was withdrawn as
too loose; it is about half of the published T2 slope.

**Status: not passed.** Two implementations, frozen independently, share all
149 inputs. Their likelihoods agree to 10^-12 at matching covariance
parameters.

| Statistic | Published | Random intercept only (closest) | Random intercept and slope |
|---|---:|---:|---:|
| T1 | 0.034 | 0.03344 | 0.03368 |
| T2 | 0.011 | 0.01123 | 0.01308 |
| T3 | −0.047 | −0.04787 | −0.04318 |
| T4 | −0.012 | −0.01185 | −0.00907 |

- With a random intercept only, T2 and T4 are within ±0.0005 of the published
  values; T1 misses by 0.0006 and T3 by 0.0009.
- The scaling model and T5 are not reproduced.
- Sources: `analysis/astra/stage_b/README.md` and `analysis/fable/stage_b/`.

**Bounded check of the historical estimator (Fable and Astra, 9 October).**
MIXREG was not recovered in our bounded search. The interface developer's
2017 page still describes free distribution, and SuperMix is its commercial
successor (Astra review §7). A licence alone would not recover F&H's input
windows, settings or residual convention, and those input files are
unpublished. Identifying the historical
estimator exactly therefore needs one of:
1. contact with the authors (Holmes, Fagan) or with Hedeker;
2. a SuperMix licence.

Both are Barry's decisions.

**Adopted amendment (Barry, 9 October 2026, 11:06 AEDT;
`docs/decisions/01663ea4-7564-41c6-abf4-d50cec5448c5.md`).**
- Barry chose `approve_ri_primary`: reconstructed T1–T4; random-intercept
  primary; random-slope sensitivity.
- Astra had recommended the random-slope model as primary; that view is
  preserved as development history.

The proposal text follows, corrected where noted.
- **Primary target.** A labelled *reconstructed estimand*: T1–T4 computed by
  the documented reconstruction (random-intercept multilevel regression, AR(1)
  errors, marginal ML) on the deposited data. Random intercept plus slope is a
  sensitivity. Random intercept only is pre-specified as primary because it
  reproduces the published T1–T4 most closely.
  - *Correction:* the choice was made after the reconstruction results were
    inspected, but before any conditional-null p-value or final validation.
  - Fixed-procedure validation does not validate the adaptive history of
    choosing the procedure.
- **T5.** Removed from the primary test.
- **Validity.** The test applies the same estimator to the observed and the
  simulated data, so the inference stays valid for the reconstructed
  statistics.
- **What changes.** The scientific claim becomes "F&H's vortex statistics, as
  reconstructed", not the exact published numbers. The full discrepancy table
  is reported alongside: random intercept, at most 0.0009; random intercept
  and slope, at most 0.0038.
- **Optional, in parallel.** If Barry wishes, he could contact the authors for
  the original inputs. If those were recovered and identified the historical
  estimator, the target would revert to it by dated amendment.

### 4.3 Production validation (on frozen code, before the empirical p-values)

- **Independence** (repair 1). Each population has one frozen reference bank.
  Synthetic "observed" datasets are *fresh* trajectories:
  - drawn from the prior and then selected, for the prior-predictive scenario;
  - drawn at fixed parameter values, for the boundary scenarios.

  They never come from the bank. Folds are not swapped or pooled.
- **Type I error.** Four scenarios under the adopted null (ar_cat):
  - prior-predictive;
  - three fixed-parameter nuisance corners (numeric values proposed in 0.8,
    pending Astra's review). Each population is fixed at the component-wise
    medians of its library at the observed C, except:
    - **high σ:** σ at that library's 90th percentile;
    - **low survival:** s at its 10th percentile;
    - **strong environment:** ρ and p_c at their 90th percentiles.
  - **Strong environment replaces "short L".** The nine designs are fixed in
    this study, so a shortened-window scenario would validate a design that
    is never analysed. The strong-environment corner probes the nuisance
    dimensions that ar_cat adds instead.
  - Values and selection rates: `analysis/fable/calibration/dev_design_v1/`
    (§9.9). They are frozen with the banks.

  Each gets 1,000 datasets. It passes if the one-sided upper 98.75%
  Clopper–Pearson bound on its rejection rate is ≤ 0.08 (Bonferroni across the
  four), which means at most 60 rejections in 1,000.
  - A true 5% test passes with probability 0.93; a true 6.5% test with 0.29; a
    true 8% test with about 0.01.
  - **Fixed n = 1,000, with no extension** (repair 2). A scenario with more
    than 60 rejections means V-fail. The family is the four null scenarios
    under the primary prior (b).
- **Power.** 300 datasets under M_A at β_min (prior-predictive nuisances). The
  O1 label requires a lower one-sided 95% Clopper–Pearson bound ≥ 0.70, which
  means at least 224 detections in 300. True power of 0.80 passes with
  probability 0.99; true power of 0.70 with 0.04.
- **Discriminability.** 300 datasets each for M_A at 2·β_min, the three M_D
  forms, M_O, and the M_A + M_D mixtures. Detection rates are reported with
  exact intervals. These are descriptive only and are not a gate.
- **Failures inside fixed denominators** (Astra review §3). All 1,000 null
  trials and all 300 power trials are retained.
  - An unresolved outer trial counts as a **rejection** for the null upper
    bound, and as a **nondetection** for the power lower bound. Unresolved
    means any indeterminate outcome in §3.4 step 4: malformed output,
    observed-fit failure, training failures above 2%, unusable covariance,
    or straddling bounds.
  - Difficult datasets are never dropped or replaced.
  - Separately, a fit-failure rate above 2% stops validation, pending a
    documented estimator revision. This applies in any *gating* scenario:
    the four null scenarios and the power scenario. Descriptive blocks
    (alternatives, detection curve, stress) report their rate.
- **Radius strata and the fitted-parameter predictive stress check** (§3.4
  step 3). Rejection rates per radius quintile are predeclared for every null
  scenario. The stress check (300 datasets) runs once, as validation block 17.
  Both are descriptive.
- **Executable contract** (0.9; freeze package §6).
  - `make_manifest.py` writes 17 blocks × 10 chunks: seeds 9 × 10^12 +
    10^6·b + c, contiguous trial IDs, one directory per chunk.
  - `validate.py` runs the chunks; `run_validation.sh` caps concurrency at
    three bank-holding processes. A chunk that is already complete is
    skipped; a partial chunk stops its slot for a manual decision.
  - `collect_validation.py` pools the chunks on the full intended
    denominators. It retains missing trials and refuses duplicates and rows
    outside a chunk.
  - It evaluates the four null gates (≤ 60 of 1,000), the power gate
    (≥ 224 of 300) and the fit stop, and reports the descriptive rates and
    the stress bounds.
  - Tested in `test_validation.py` with mocked fits, plus a real-R run of the
    launcher on a toy manifest.
- **Detection curve** (§3.3). M_A at Δ10 = 0.3 and 0.5 is added to the
  alternatives, 300 datasets each and descriptive, adding about 230
  core-hours.
- **Scope of validation.** Validation covers the frozen procedure, bank,
  design and scenario distributions, against the 8% ceiling. It does not
  certify secondary or sensitivity tests, the iid sensitivity, or prior (a).
- **Development vs validation seeds.** Development streams are listed in
  §4.4. Final validation uses seeds 9 × 10^12 + i, run once on frozen code.

### 4.4 Compute

The 220-core-hour figure is withdrawn: it omitted simulation and selection
costs.
- **Measured benchmark (9 October).** Measured with
  `analysis/fable/calibration/time_estimator.txt` and the bank scans:
  - T1–T4 cost 0.15 s per nine-population dataset (four nlme fits), with no
    failures in 20 synthetic datasets;
  - bank simulation runs at about 4 × 10^5 prior draws per second per core;
  - `deep-server` has 64 cores and 125 GB of RAM.
- **Measured inventory (0.8; 10× banks, k-NN library, R_train = R_test =
  K = 2,000)**
  ([`dev_design_v1/NOTE.md`](../analysis/fable/calibration/dev_design_v1/NOTE.md)).
  - **Per trial:** 1,370 CPU-seconds (0.38 core-hours), all-in. This is
    measured process CPU time over the 150-trial power screen, including five
    setups. The 4-trial cost run's derived 1,154 CPU-seconds per trial assumed
    single-core setup.
  - **Memory:** 28 GB resident per process, which holds the banks.
  - **Banks:** 77.5 core-hours measured for 2 × 10^9 draws per population for
    ar_cat and iid together; 17 GB on disk.

  | Component | Datasets | Core-hours |
  |---|---:|---:|
  | Null scenarios (4 × 1,000) | 4,000 | 1,522 |
  | Alternatives (10 × 300): M_A at β_min and 2·β_min; M_D linear, accelerating and step; M_O low-n and uniform; M_A + M_D in each M_D form | 3,000 | 1,142 |
  | Detection curve: M_A at Δ10 = 0.3 and 0.5 (2 × 300; proposed in 0.8) | 600 | 228 |
  | Fitted-parameter predictive stress check (§3.4) | 300 | 114 |
  | Empirical analyses and sensitivity banks (itemised in the §7 execution inventory) | about 25 | about 155–165 |
  | Banks: production ar_cat, second ar_cat stability bank, iid sensitivity bank | — | about 120 |
  | **Total** | about 7,925 | **about 3,300** |

  - **Wall time on deep-server.** The power screen's observed throughput was
    about 105 trials per hour (three concurrent processes × 18 workers), so
    roughly 75 hours plus banks. This is a small-pilot projection. Kunanyi is a
    later option and needs Barry to open a TPAC Jumpbox.
  - **Not yet measured:** the corners, and the M_D and M_O generators, which
    are not yet implemented. Their cost is assumed equal to M_A's.
  - Mandatory sensitivities run on empirical data only and are reported
    unvalidated.
- **Earlier estimates withdrawn:**
  - the 220 core-hour figure;
  - the 0.5 subtotal of 1,170 core-hours;
  - the 0.6 inferred estimate of 2,100 core-hours, which used worker count ×
    wall time;
  - the 0.8 cost-run figure of 2,420 core-hours, which used a derived
    per-trial cost.
- **Replicate counts.** The 0.4 "R_v" lines are superseded. Every
  validation and empirical dataset uses the same frozen R_train = R_test =
  2,000.
- **No sequential p-values.** The Besag–Clifford proposal is withdrawn
  (repair 1).
- **Seeds.** Development seeds used so far:
  - 20261002–20261027;
  - 20261014000–20261014044 (comparison banks);
  - 20261014100–20261014117 (2 × 10^8 discrimination banks);
  - 2026101800–2026101835 (outer-C coverage, v1);
  - 20261019000–20261019359 (10× bank shards);
  - 2026102100–2026102117 (radius coverage, 10× banks).

  The discrimination arms reused 20261016 (null) and 20261017 (M_A) for both
  variants. The 0.8 runs used 20261020 (effect target), 20261022 (cost run)
  and 20261023–20261027 (power-screen arms). Final validation seeds are reserved at 9 × 10^12 + i,
  disjoint from all of these.
- **Compute (Barry, 8 October).** Serious runs go to `deep-server` in tmux.
  The laptop cap no longer applies.
- **If the published estimator is too slow,** the pilot evaluates a
  decomposable surrogate (pooled GLS with fixed AR(1)). An amendment then
  states which estimator defines T for the test. The published estimator
  remains the reconstruction target.
- **Where it runs.** Production runs on `deep-server` under AGENTS.md, after
  the measured estimate.

## 5. Data compilation and source appraisal — Astra draft

### 5.1 Two distinct evidence sets

**Published reanalysis set.** Start with the named Fagan–Holmes populations and
the Williams source mapping, retaining both study identifiers and a stable
population identifier. This is a closed case reconstruction, not a systematic
sample of extinctions. The [T3 inventory](t3/vortex_series_inventory.csv) is a
lead ledger. Its 36 rows, 13 complete-count labels and 10 supported-extirpation
labels are provisional classifications; the report explicitly says primary
extirpation records were not checked. The nine-series overlap is recorded, but
window/endpoint discrepancies and the reported 150-versus-148 nonzero censuses
remain unresolved. The archived [Table 1 reconciliation](t3/fh_table1_reconciliation.txt)
matches 24 of 27 scalar fields, not the fitted statistics. It now reports both
last-nonzero and zero-census window conventions: six of nine window lengths
match under the latter convention. The CC0 source is archived in
`data/raw/williams2021/`; the replay checks its hash. Wild dog, marmot and
crane windows still differ. Existing CSVs do not demonstrate exact reproduction
of the fitted statistics.

The [Williams Dryad deposit](https://doi.org/10.5061/dryad.jwstqjq8c) is public;
Astra checked the repository API's CC0 licence declaration on 5 October 2026
(version 2, version ID 111752). The eventual source manifest must retain the
downloaded files, dates, versions and hashes. The current 31-public/4-confidential
mapping needs verification against source files. Unavailable raw series remain
explicitly unavailable; do not substitute invented values to reconstruct 35.

**Forward sampling frame.** Enumerate the GPDD census metadata from one fixed
version first, including nonentrants. The primary discovery route must not
select populations because they subsequently declined, recovered or went extinct.
Exclude supplementary bibliographic discoveries and any additional database
from the primary GPDD estimate; retain them as labelled secondary ascertainment
strata. This fixes our discovery rule without assuming the database itself is
free of monitoring or reporting bias. Full LPD access is optional and outside the
public-data core; accepting its agreement or contacting providers requires
Barry's decision. Verify the licence/version of any open LPD subset separately.

### 5.2 Search specification

Freeze the date cutoff, database versions and translated executable queries
before the planned compilation. Cover records available through that cutoff,
without a lower publication-year limit. Search OpenAlex and Crossref, named data
repositories and one backward/forward citation pass from the seed studies and
eligible compilations. A second citation pass is justified only for newly found
compilations and must be logged. Record inaccessible records rather than
silently excluding them. No language exclusion is proposed; translation or
access limits must be reported. No author contact is assumed authorized.

Use separate search families:

| Purpose | Draft query concepts / seed |
|---|---|
| Competing explanations and prior work | `"extinction vortex"`; `"extinction" AND ("conditioning" OR "selection bias" OR "first passage" OR "null model")`; exact titles and citation links for Fagan–Holmes, Williams, Boettiger–Hastings, Dennis, Nabutanyi–Wittmann, Hefley, and both Griffen/Drake 2009 passage-time/final-decline papers |
| Outcome-neutral discovery of monitoring data | `("population" OR "abundance") AND ("census" OR "monitoring") AND ("time series" OR "long term" OR "annual counts")`; GPDD source citations and references in eligible monitoring compilations |

These are logical query templates, not claims that both APIs accept identical
Boolean syntax. Archive each provider's actual query, filters, retrieval date,
pagination/completeness status and returned identifiers. Verify translation
against known seed records before freezing the executable search. Neither a
search-engine ranking nor a citation count establishes search completeness.

The [5 October orientation-search record](vortex_prior_work_search_20261005.md)
provides executed query URLs and retrieved identifiers, with explicit coverage
limits. These queries inform the search specification; they are not a completed
systematic compilation or a retroactive search freeze.

Deduplicate publications by DOI/identifier and then metadata; deduplicate
datasets by population, spatial boundary, census definition, period and source
lineage. Retain overlapping versions as linked records. Do not count a reused
population as independent evidence. Report separate flows for publications,
datasets/populations and threshold entrants, since these are different units.

### 5.3 Eligibility and screening

Both agents independently record include/exclude/uncertain decisions and source
locations before opening the other's decisions. Preserve their initial decisions,
resolve discrepancies against the source, and retain unresolved cases as uncertain.
Report agreement and disagreement counts; a confidence score or model agreement
does not establish eligibility. The existing T3 inventory has already been seen
and cannot be retrospectively labelled independently screened.

For the forward primary frame, include entrants and nonentrants satisfying:

- a defined wild population or local population with a sufficiently stable area
  and census target, and a source-supported observation protocol;
- absolute abundance in a defined biological unit, with evidence for completeness
  or enough detection information for the specified observation model. A database
  label alone is insufficient. Keep individuals, breeding units and estimates
  separate until their model/threshold interpretation is justified;
- observation dates and units that permit the chosen transition interval, plus
  the prespecified initial-history information. Missing years remain missing; multiple
  visits and changes in survey design must be identified;

Within that frame, define threshold-entry reporting strata using history
available at entry, retaining direct entry to zero in the joint fate/abundance
analysis. An observed crossing is not an inclusion requirement. Series already
below the threshold when monitoring begins form an initial-small group with
unknown earlier entry history, not invented observed crossings.

Eligibility must not require a minimum number of later positive counts,
survival to the horizon, recovery, a verified extinction or complete follow-up.
Administrative opportunity to observe an H-year horizon can be defined from
calendar dates fixed independently of outcome. Actual early monitoring cessation
remains in the cohort with censoring and its documented or unknown reason.

Indices, densities without known sampled area/effort, inferred model outputs,
undefined population boundaries and incompatible units remain separate from the
primary count cohort. Preserve the reason for exclusion or secondary use rather
than silently converting proxies into individuals. Translocation/release studies
are a separate candidate module: manager-set release size is not automatically
exogenous, because allocation may depend on species, site quality and perceived
risk. That module needs its own assignment model and novelty assessment.

### 5.4 Extraction, provenance and bias appraisal

Use one compact population ledger, linked to immutable source files. Record:

| Field group | Minimum contents |
|---|---|
| Identity and access | Stable population/source IDs, taxon, spatial boundary, source citation/page, licence/version, file hash, duplicate/overlap links |
| Observation design | Biological unit/stage, census/estimate/index, effort/area, evidence for detection, observation dates and season, interval, missingness and design changes; source and assumptions for any unit conversion |
| Demographic inputs | Source/page for survival estimates, population and life stage measured, time interval and census timing, uncertainty, and concordance with the counted unit; generation length if used |
| Entry and monitoring | Observed history used for entry, entry date/unit, available administrative horizon, monitoring-end date and whether its reason is known |
| Provenance and endpoints | Reported interpolation/rounding/carry-forward, original versus processed values, source evidence for local extirpation, non-detection, captivity or recolonization |
| Ascertainment and covariates | Why the population was monitored/reported, measured external drivers, interventions, population dependence and source-level clustering |
| Review | Each initial eligibility decision and evidence, adjudication, reason for exclusion/secondary use, exposure status |

Appraise endpoint validity, detection, interpolation, sampling-frame selection,
informative cessation and external-driver confounding separately; do not reduce
them to a single quality score. Repeated identical plover counts alone neither
establish interpolation nor quantify variance distortion. Preserve them as
recorded while seeking their provenance. Use source-supported observation
processes and prespecified sensitivity bounds where facts remain uncertain.

The GPDD pilot's 65/59/52, 44/37/27 and 39/33/20 totals are threshold/follow-up
**observation counts**, not verified calendar-year cohorts. At threshold 50,
the reported 37 with at least five later observations include only 12 labelled
All Individuals; the rest include pairs, territories, nests and other units.
These are planning summaries, not the final eligible sample or a rationale for
choosing whichever threshold supplies most apparent power.

## 6. Exposure, freezes and deviations — Astra draft

The [exposure log](vortex_exposure_log.csv) records known access and its evidence.
Distinguish files accessed computationally, values displayed to an agent, published
outcomes already known, and fitted analyses. Include delegates: withholding their
raw output from the parent does not make their role unexposed.

Part 1 is an openly outcome-exposed reanalysis. A freeze can precede its new
tests, but cannot make its published results unknown. The GPDD pilot read real
abundance vectors to determine entry and later observation counts; an earlier
pilot also summarized terminal-zero frequencies. The open LPD subset's terminal
zero total has been reported. Individual forward trajectories may remain
unexamined by the analysts, but a blanket claim that these databases' outcomes
have never been inspected would be incorrect. Record the narrower claim and its
verification limits.

Use three small, staged records:

1. **Search/design freeze:** commit the agreed search, eligibility, structural
   extraction fields, exposure record and Part 1 reconstruction specification.
   Record unresolved specifications explicitly; a document containing unresolved
   decisive choices is not frozen for that analysis.
2. **Analysis/validation freeze:** after the metadata audit and documented pilots,
   commit estimators, parameter sources, candidate models, numerical gates,
   multiplicity rules and final simulation design before the decisive validation
   and new empirical tests. Further Part 1 adaptation remains exposed work.
3. **Forward release record:** if the gate passes without tuning to forward
   responses, record its result and the exact pre-existing analysis commit before
   releasing additional post-entry response data to the fit. If the cohort changes
   materially, repeat or amend the structural gate before looking at those responses.

Each record names the commit, source hashes, outcome exposure, next permitted
analysis and both agents' review status in a dated Board message. Use a new
commit for amendments; never rewrite the old freeze or backdate it. Record what
changed, why, what had been seen and which later results it affects. The Board
timestamp and Git history support a local audit trail; they do not provide an
external registry's guarantees.

During forward metadata compilation, the permitted displays are source/unit
information, observation dates and gaps, pre-entry values needed for eligibility,
administrative follow-up opportunity, and monitoring-end reason categories.
Source-reported extinction, non-detection or recolonization evidence may also be
needed to appraise censoring. Such information reveals fate: record the affected
population and exposed information before using it in the simulation design.
This is outcome-restricted compilation, not fully outcome-blind compilation.

The Stage D design uses audited observation structure and prespecified synthetic
parameter ranges, not fitted forward effects or growth/variance estimates from
new response values. Entry counts are abundance-derived and remain logged as
exposed information. Record overlap with the archived October terminal-zero
screen, including unrecoverable prior delegate access. Any proposal to use GPDD
responses for Part 1 nuisance checks requires an explicit exposure amendment;
it is not covered by the metadata permission.

New post-entry abundance trajectories, growth summaries, fitted feedback effects
and derived responses remain outside analyst context until release. Titles and
abstracts can also reveal fate incidentally; log that exposure. If prior endpoint
knowledge cannot be isolated from cohort/design choices, report a prespecified
analysis of partly exposed existing data, not validation on wholly unseen
outcomes. An independent extractor may mechanically split files, but its access
and summaries must also be logged. A checksum shows file identity, not that
nobody inspected its contents.

## 7. Analysis and reporting plan — Fable formal draft 0.6

**Prespecified vs exploratory analyses.**

| Analysis | Status |
|---|---|
| Q1: p_joint on T1–T4 (the reconstructed estimand, §4.2) under prior (b), with the validation results and outcome labels of §1 | Prespecified, **primary**; target adopted by Barry on 9 October |
| Prior (a), where the ledger supports it | Prespecified secondary; unvalidated |
| T5 and the scaling model: published F&H curves set beside our diagnostic fits | Descriptive only |
| Q2: discriminability rates (§4.3) | Prespecified, **primary** |
| Each p_k (Holm-adjusted across the four) | Prespecified, secondary |
| Williams statistics on complete-count series confirmed by the audit (Q3) | Prespecified, secondary |
| Sensitivity: exact endpoint vs the study's inclusion window; rule E (≤ 1 vs 0); separate environmental factors; leave-one-population-out across all nine; turtles A and B left out together (shared study cluster); the crane excluded (experimental flock with intervention history); the wild dog's three deposited fills treated as missing; random intercept plus slope estimator; F&H-length windows; runs of identical counts treated as missing except the first, where provenance is uncertain | Prespecified, reported regardless of result |
| *Daphnia* (if the data are obtained): the Q1 pipeline applied to the deteriorating replicates. A departure is a diagnostic to investigate with the controls, not proof of error, since the known food reduction does not rule out concurrent feedback. | Prespecified diagnostic, conditional on access |
| Plain M0 (no catastrophes, ρ = 0), if M0\* is adopted | Mandatory sensitivity; reported unvalidated |
| Random-intercept-and-slope estimator (Barry's decision) | Mandatory sensitivity; reported unvalidated |
| Per-population calibration adequacy: the percentile of c_obs within the selected prior predictive, for each summary | Prespecified diagnostic, reported for all nine |
| Part 2; M_G; the founder-size module; the 2016 LPD subset; anything not listed here | Exploratory, or parked until a dated amendment |

**Execution inventory (0.9; Astra 0.8 review).**

This links every promised analysis to its generator and reference, outer
count, seed family and cost.
- **Cost basis.** 0.38 core-hours per analysed dataset at R_train = R_test =
  K = 2,000, measured all-in. One 2 × 10^9-draw bank costs about 4.3
  core-hours per population.
- **Seed families** (proposed; frozen with the banks):
  - 8.1 × 10^12 + task: the primary ar_cat bank;
  - 8.2 × 10^12 + task: the stability ar_cat bank;
  - 8.3 × 10^12 + task: the iid bank;
  - 8.4 × 10^12 (rule E = 0), 8.5 (inclusion window), 8.6 (separate
    factors), 8.70 (F&H-length windows), 8.71 (wild-dog fills missing), 8.72
    (fills re-created), 8.73 (identical-count runs), 8.8 (prior (a)), each
    + task. These families are disjoint;
  - 9 × 10^12 + 10^6·b + c: validation, for scenario block b and process
    chunk c;
  - 9.5 × 10^12 + a: the replicate streams of empirical analysis a, where
    a is: 1 Q1; 2 stability; 3 iid; 4 RI+slope; 5–13 LOPO in design order;
    14 turtles together; 15 rule E = 0; 16 inclusion window; 17 separate
    factors; 18 F&H windows; 19 fills missing; 20 fills re-created;
    21 identical runs; 22 prior (a).
- **Implementation status (0.9).**
  - **Implemented and tested:** validation (all 17 blocks) and the Q1
    entry point (`empirical_q1.py`). That entry point shares the validated
    code path, refuses to run without a passing validation summary for the
    same manifest, and has never been run.
  - **Not implemented:**
    - the per-statistic p_k (Holm);
    - the sensitivity generators and designs (rule E = 0, inclusion window,
      separate factors, windows, fills, identical runs, prior (a));
    - the RI+slope replicate fitting;
    - the LOPO dataset assembly.

    Each is implemented and frozen after validation and before its own run.
    Each is reported as an unvalidated sensitivity.

| Analysis (§) | Generator / reference | Bank | Datasets | Seeds | Core-hours |
|---|---|---|---:|---|---:|
| Validation, null scenarios: prior-predictive, high σ, low s, strong environment (§4.3) | ar_cat | primary (reused) | 4 × 1,000 | 9e12 blocks | 1,522 |
| Validation, alternatives: M_A at β_min and 2·β_min; M_D × 3; M_O × 2; M_A + M_D × 3 (§4.3) | §3.2 laws vs the ar_cat reference | primary (reused) | 10 × 300 | 9e12 blocks | 1,142 |
| Detection curve: M_A at Δ10 = 0.3 and 0.5 (§3.3) | M_A vs ar_cat | primary (reused) | 2 × 300 | 9e12 blocks | 228 |
| Fitted-parameter predictive stress check (§3.4) | ar_cat at library parameters | primary (reused) | 300 | 9e12 block | 114 |
| **Q1 empirical test**, with the p_k (Holm) from the same run | ar_cat | primary | 1 | 9.5e12 | 0.4 |
| Second-bank stability (descriptive) | ar_cat | stability (new) | 1 | 8.2e12 / 9.5e12 | 39 + 0.4 |
| Plain-M0 mandatory sensitivity | iid | iid (new) | 1 | 8.3e12 / 9.5e12 | 39 + 0.4 |
| Random intercept + slope mandatory sensitivity | ar_cat; replicates refitted with that estimator | primary (reused) | 1 | 9.5e12 | about 1 (projected) |
| Leave one population out (9), turtles together (1); crane exclusion = LOPO crane | ar_cat on 8 or 7 populations | primary (reused) | 10 | 9.5e12 | 4 |
| Rule E = 0 (first census of 0) | ar_cat, selection changed | new, 9 populations | 1 | 8.4e12 / 9.5e12 | 39 + 0.4 |
| Inclusion window instead of exact endpoint | ar_cat, selection changed | new, 9 populations | 1 | 8.5e12 / 9.5e12 | 39 + 0.4 |
| Separate environmental factors (correlation 0.5) | ar_cat, two factors | new, 9 populations | 1 | 8.6e12 / 9.5e12 | 39 + 0.4 |
| F&H-length windows (wild dog, marmot, crane; where the data allow) | ar_cat, design changed | new, 3 populations; others reused | 1 | 8.7e12 / 9.5e12 | 13 + 0.4 |
| Wild-dog fills as missing; fills re-created in simulation | ar_cat, wild-dog design changed | new, wild dog only, × 2 | 2 | 8.7e12 / 9.5e12 | 9 + 0.8 |
| Identical-count runs as missing except the first, where provenance is uncertain (currently the golden plover) | ar_cat, recorded-census mask | new, affected populations | 1 | 8.7e12 / 9.5e12 | 4–17 + 0.4 |
| Prior (a), where the ledger supports it | ar_cat with the literature survival prior | new, supported populations | 1 | 8.8e12 / 9.5e12 | ≤ 39 + 0.4; **ledger-dependent** |
| Per-population calibration adequacy (percentiles of c_obs) | ar_cat | primary (reused) | — | — | negligible |
| Williams statistics on complete-count series (Q3, §2.2) | authors' code; no simulated reference | — | 31 series | — | negligible; **needs the archived code** |
| *Daphnia* diagnostic | Q1 pipeline | new | — | — | **access-dependent** |
| Production banks | primary ar_cat | new | — | 8.1e12 | 39 |

**Totals.**
- Validation: about 3,006 core-hours.
- Empirical analyses (about 9 core-hours) and sensitivity banks (143–156):
  about 155–165.
- The primary, stability and iid banks: about 117.

**Overall: about 3,300 core-hours**, excluding the conditional items. The
sensitivity banks dominate the empirical side. All empirical analyses run
only after the validation freeze.

**Data handling.**
- Missing years stay missing.
- Documented interpolations are replicated in every generator.
- Values are analysed as recorded, unless the source documents a correction.
- After Stage B, no exclusion is made except by a dated amendment that states
  what had been seen.

**Reporting.**
- Published and reconstructed values appear side by side.
- Departures are described only relative to the specified generators.
- Validation results and exposure status are reported with every empirical
  result.
- Release all code, manifests and seeds.

## 8. Responsibilities and separate implementation — Astra draft

| Owner | Output and evidence standard | Stop / handoff |
|---|---|---|
| Fable | Formal §§1–4 and 7; corrected model/inference specification; review Astra's decision brief | Respond to R1–R6 in the quantitative review; no empirical fitting implied |
| Astra | §§5–6 and 8, source/exposure corrections; quantitative review and decision brief | Integrate substantive replies; preserve any unresolved scientific disagreement |
| Both agents | Separately recorded screening decisions; source adjudication; critical code comparisons | Escalate only unresolved choices that change the scientific target or require Barry's access/authority |
| Barry | Scientific direction and final scope; optional access agreements, major extensions and external commitments | One coherent study decision rather than approval of routine stages |

After the study is authorized, both agents separately implement the Fagan–Holmes
estimator and M0 conditional sampler from a common mathematical specification
and synthetic fixtures. Fable leads the calibration implementation and Astra
reviews it; Astra leads a forward likelihood only if the extension is justified,
with Fable reviewing. Confirm the remaining ownership before coding. Freeze each
implementation before inspecting the other's code; document prior shared code
exposure. Compare limiting cases, generated moments, likelihoods and inference
at declared tolerances. Different random-number libraries need not produce
identical draws. Preserve discrepancies and their resolution. Agreement supports
implementation consistency; analytic checks and synthetic calibration address
different questions, and none substitutes for empirical identification.

## 9. Immediate completion requirements and operating scope

Before the confirmatory Part 1 comparison or forward analysis can be frozen,
the integrated protocol needs:

1. Exact study-specific reconstruction/selection algorithms and resolution of the
   Fagan–Holmes window/endpoint discrepancies; a feasible public Williams subset.
2. A justified calibration strategy and joint nuisance sensitivities, rather than
   assumed drift invariance or uncontaminated preterminal variance.
3. The entrant target, units, threshold/horizon, ascertainment treatment, zero
   transitions and explicit limits on mechanism identification.
4. Numerical validation and decision criteria set before final validation results,
   plus a compact table distinguishing prespecified from exploratory analyses.
5. Executable search strings, source/exposure manifests and source-supported
   eligibility assessments; resolution of the outstanding close-prior-work check.

Fable's formal revision and brief review, and Astra's response, are recorded.
Barry's topic and bounded-tranche decision is next. This is a dependency order,
not a promise of elapsed runtime before the data and models are settled.

Current authorization covers this protocol, bounded source checks, correspondence
and ordinary Git synchronization. The research programme awaits Barry's direction
on the concrete plan. No new access agreement, provider contact, publication or
submission is included. The public-data core should not depend on optional LPD
access or a translocation module. Small pilots must fit the WSL resource limit;
before larger execution, estimate cost from a small benchmark and consult the
existing compute-resource instructions. No heavy compute belongs on this laptop.

### 9.1 Requirement status after draft 0.2 (Fable)

| §9 item | Status in draft 0.2 | Still open |
|---|---|---|
| 1. Reconstruction and selection algorithms; F&H windows and endpoints; feasible Williams subset | Selection rules fixed in §3.4 (exact matched design primary; inclusion windows as sensitivity). Stage B criterion in §4.2. Table 1 reconciliation archived (24 of 27 match; 3 discrepancies listed). Williams subset is the 31 public series (§2.2). | The exact F&H windows for wild dog, marmot and crane; the turtle B discrepancy; transcription of T5. All are Stage B work. |
| 2. Calibration strategy and joint nuisance sensitivities | ABC under the same selection as the data, with calibration features kept separate from the tested statistics (§3.4). Drift, σ and demographic variance are calibrated jointly; the drift-invariance claim is withdrawn. Calibration validity is tested by simulation-based calibration (§4.3). | Species adult-survival table (sources) before the validation freeze |
| 3. Entrant target, units, threshold, horizon, ascertainment, zero transitions, limits on mechanism | Risk-set likelihood over the whole frame; IUCN-anchored N* by unit stratum; zero transitions and immigration specified; Wooldridge initial conditions; limits on mechanism stated in §1 (§2.3) | The frame audit (Stage A) |
| 4. Numerical validation and decision criteria; table of prespecified vs exploratory analyses | δ_min rule (§3.3); Stage C and D criteria, Monte Carlo sizes, failed-fit handling, development vs validation seeds (§4.3–4.4); prespecified/exploratory table (§7) | Astra's review of the thresholds |
| 5. Search strings, manifests, eligibility; close-prior-work check | Source manifest started ([source_manifest.csv](t3/source_manifest.csv)); exposure log extended (E09, E10) | Executable searches (Astra, §5.2); the remaining close-prior-work census (T1) |

### 9.2 Astra review disposition (draft 0.2a)

The [detailed review](astra_protocol02_review_20261005.md) takes precedence over
any reading of §9.1 as mutual acceptance. Items 2–4 remain open: M0 and M_G need
valid probability support; the conditional test and classifier need a defined
target and algorithm; validation needs uncertainty-aware decision rules; and
Part 2 still needs units and a complete likelihood. Item 1 has an archived
summary-table comparison but no fitted-statistic reconstruction. Item 5 now has
executed orientation queries, new close prior work and explicit coverage gaps.

Astra accepts Fable's four amendments with the qualifications incorporated in
§§5–6 and 8. The [decision brief](vortex_decision_brief.md) recommends a bounded
source/reconstruction/development-pilot tranche if Barry selects the study.
The 220-core-hour figure is an unbenchmarked fitting subtotal, not an agreed
production allocation. This disposition does not authorize any research stage.

### 9.3 Fable response to the review (draft 0.3)

All six requirements are accepted and addressed in the revised §§1–4 and 7.
Astra's novelty narrowing and the Part 2 objections are accepted, and the
qualified amendments in §§5–6 and 8 stand.

| Review item | Draft 0.3 change |
|---|---|
| R1. Valid null | Survival in (0, 1) and recruitment ≥ 0 are sampled directly, with λ derived. The census stage, interval, propagation through missing years, environmental covariance and invariant tests are specified (§3.1). |
| R2. Genetic alternative | M_G is deferred until a bounded recurrence and the coefficient convention are specified. A valid phenomenological M_A is defined on the β scale, so its multiplier lies in (0, 1]. β_min has a stated endpoint and an unattainable-case rule (§3.2–3.3). |
| R3. Inferential target | The target is the conditional prior-predictive p-value given C and S; the 0.2 labels are withdrawn. The bank, standardisation, tolerance, K, distinct-draw rule, tail formula, covariance, Monte Carlo stability check and two priors are specified (§2.1, §3.4). Cross-fitted independence is in §4.3. |
| R4. Validation criteria | Confidence-bound criteria with pass probabilities, a Bonferroni correction across four null scenarios, a maximum budget, V-fail precedence, and power bounds (§1, §4.3). Discrimination results are descriptive only. |
| R5. Classifier | Removed. The first analysis is limited to discrepancy testing plus discriminability, mixtures included (§1). *Daphnia* becomes a diagnostic (§7). |
| R6. Reconstruction and compute | Stage B is judged at published precision. The reconciliation now verifies its input hash against the stored CC0 source (`data/raw/williams2021/`) and reports both window conventions: 6 of 9 F&H windows match when counted to the extinction census; the wild dog, marmot and crane remain. The 220-core-hour figure is replaced by a benchmark plan, a cost formula and sequential p-values (§4.4). |

**Verified this round.** Griffen & Drake (2009), read on PMC, cite F&H only for
the logarithmic scaling of decline duration. They do not discuss vortex
signatures or conditioning. The narrower novelty claim, a matched
reconstruction with measured discrimination limits, therefore still stands
provisionally.

*Fable correction (5 October, message 1051):* the statement above that Griffen &
Drake do not discuss conditioning is wrong. Their introduction explicitly
describes the conditional diffusion of a final decline, following Lande et al.
(2003). It came from a fetch tool's summary, not the primary text. See §9.4.

### 9.4 Astra disposition after draft 0.3

The model-support repairs, narrower discrepancy question, deferred genetic and
forward analyses, improved validation framework and byte-preserved input make
a bounded feasibility tranche defensible. They do not make production ready.
The [draft 0.3 review](astra_protocol03_review_20261005.md) records the evidence
and the remaining agent tasks:

1. Make the discrepancy reference and Monte Carlo ranks valid; define ties,
   finite-bank approximation and any sequential stopping formula explicitly.
2. Use a fixed validation size or adjust confidence bounds for both looks.
   The unadjusted 1,000-to-1,200 extension does not preserve §4.3's guarantee.
3. Make O1 unavailable when the stated effect target is unattainable. A
   fallback effect can support descriptive sensitivity only.
4. Finish the matched windows, survival/census-unit mapping, comparator
   parameter ranges and complete scenario/cost inventory before freezing.

**First tranche recommended to Barry.** Source/metadata checks, independent
published-estimator reconstruction and a genuinely small synthetic feasibility
pilot. For the pilot: one worker, at most 2 GiB resident memory and 30 aggregate
CPU-minutes; stop earlier at 10,000 candidate trajectories per population or
20 complete nine-population estimator fits. Counts and CPU budget include the
separate implementations together. These caps do not promise successful
calibration. The 400-dataset screen in §4.1, the large banks in §3.4 and the
effect-grid production in §3.3 are outside this first tranche. Report measured
acceptance, failures, memory and extrapolated cost before proposing larger
runs. No empirical p-values, remote production or new access agreements are
included.

**Source correction to §9.3.** Griffen and Drake (2009), introduction, explicitly
describe a conditional diffusion process for final decline. They cite F&H for
logarithmic duration scaling; the assertion that they do not discuss
conditioning is incorrect. The candidate novelty remains the specific matched
reanalysis and its measured limits, subject to the bounded search's open gaps.
See the [source record](vortex_prior_work_search_20261005.md).

Astra adopts Fable's requested updates for draft 0.3, realistic outcomes and
resources, with that literature correction. Neither the most likely outcome,
a publishable paper, nor a general sample-size requirement has been established.
The brief is ready for Barry's scientific choice; this disposition authorizes
no research stage.

### 9.5 Fable draft 0.4 (9 October): what changed

**Accepted repairs (1049/1051).**
- An independent training/test reference for D, and a frozen bank with fresh
  outer trajectories (§3.4, §4.3).
- Fixed n = 1,000 validation, with no extension (§4.3).
- O1 unavailable when β_min is unattainable; a frozen effect search (§3.3).
- Besag–Clifford sequential p-values withdrawn.

**Astra source audit (1160).**
- Census ledger fields kept separate; the "all complete individual counts"
  claim withdrawn (§2.1, §3.1).
- Same-trajectory survival excluded as a prior; prior (a) secondary and
  unvalidated (§3.4).
- Shared-cluster sensitivity for the two turtles, crane-intervention
  sensitivity, and wild-dog fill sensitivity (§7).

**Stage B (1159; Fable's 1139).**
- Recorded as not passed.
- MIXREG is not publicly available.
- Proposed amendment for Barry: the reconstructed T1–T4 become the primary
  target and T5 becomes descriptive (§4.2).

**M0.**
- Two independent implementations, frozen and then compared; they agree
  within Monte Carlo error (§3.1).

**Still open.**
- Barry's decision on §4.2.
- Survival-source mapping for prior (a).
- The census-unit conflicts.
- Comparator parameter ranges for M_D and M_O.
- The full scenario and cost inventory after the pilot benchmark.
- Synthetic calibration development, which is Fable's next task.

### 9.6 Fable draft 0.5 (9 October): what changed

- **Barry's adopted target.** Recorded in §2.1 and §4.2, with corrected timing
  wording and the full discrepancy table.
- **Astra's 0.4 repairs.**
  - One frozen procedure, R_train = R_test = 2,000, for both validation and
    the empirical analysis.
  - Banks sized and frozen in development, with no enlargement triggered by
    p-values.
  - Failures kept inside fixed denominators, and indeterminate outcomes.
  - Finite-bank ABC scope stated, against the 8% ceiling.
  - An executable tie rule.
  - Prior (b) is now "proposed for primary validation"; prior (a) is an
    unvalidated sensitivity.
  - Missing-year handling.
  - Software wording: "not recovered in our bounded search".
- **Interpolation.** The adjacent-gap fix is in, with a test.
- **Benchmarks.** Measured bank and estimator costs give a production
  inventory of about 1,170 core-hours, about 20 h on `deep-server`.
- **Proposed null extension M0\*** (catastrophes plus AR(1) environment). This
  needs Astra's review, and its adaptive origin is recorded. Barry is informed
  in chat.

**Still open:**
- the M0\* decision;
- the final β_min computation;
- the census-unit conflicts and prior (a) sources;
- freezing the J_i bank sizes;
- the second-bank specification;
- the validation freeze itself.

### 9.7 Fable draft 0.6 (9 October): what changed

Responses to Astra's 0.5 review (1212/1214):
- **Structural H0.** Defined as no direct feedback, given the environment.
  The conditional-mean wording is retired, and feedback explicitly includes
  Allee mechanisms.
- **Catastrophes.** Priors corrected to p_c ~ U(0, 0.05) and
  δ ~ U(0.5, 0.95), with a per-generation derivation; the rationale is
  narrowed; a heavy-tailed comparator is added.
- **Common-footing comparison** of five nulls (iid, ar, cat, ar_cat, heavy):
  same cap and selection, with provenance. Only ar_cat is feasible for all
  nine.
- **Bank-sizing rule.** Lower Clopper–Pearson bound of at least 3K within
  tolerance, capped at 10^9 draws, with provenance kept.
- **Second bank.** Now descriptive only; the 0.01 rule is withdrawn.
- **Contradictions removed:** the R_v lines, the tie rule, labels for prior
  (a), and the exact-uniformity claim.
- **Seeds.** Final validation seeds reserved at 9×10^12 + i.
- **E19/E20.** My exposure row renumbered to E20.
- **End-to-end benchmark.** About 2,100 core-hours, and banks must be about
  10× larger.

**Open:**
- the bounded discrimination check, running on deep-server;
- Barry's decision on the primary null;
- β_min under the chosen null;
- the final scenario and cost inventory with production bank sizes;
- the census-unit conflicts.

### 9.8 Fable draft 0.7 (9 October): what changed

Responses to Astra's 0.6 review (1226/1228):
- **Discrimination screen, completed and scored** (`discrimination_v1/`).
  - All 4 × 30 trials completed.
  - Each trial is classified with fixed denominators, from recomputed
    full-precision bounds. The recomputation matches the logged p in all 120.
  - Shortfalls count against the null gate and as nondetections.
  - Raw p is kept as a diagnostic only.
- **Outer-C coverage** (`coverage_v1/`), with 20,000 fresh outer datasets per
  scenario.
  - The hard tolerance needs about 100× banks.
  - Proposal: a k-NN library with 10× banks (§3.4 step 3; pending Astra).
- **Candidate conclusion narrowed** (§3.1, `compare_nulls_v1/NOTE.md`).
  - The comparison table is corrected: AR and catastrophes-only each fit 7/9.
  - Ar_cat is the only implemented candidate meeting the observed-C
    planning rule.
  - This is not evidence that catastrophes or AR are needed.
  - The Student-t comparator is retired: its recruitment has infinite mean
    before the cap.
- **H0 wording.** The environmental transition law excludes N, which is not
  statistical independence. The abundance-independent mean is now labelled
  as the plain Gaussian iid, fixed-θ, unselected case.
- **Capped target.** The target conditions on S and on the cap event A
  (§2.1).
- **Consolidation.**
  - The 2×10^5 / 10^8 bank target is removed.
  - Test-set exchangeability is deferred to §2.1.
  - Development seeds are listed and the old seed ranges removed.
  - Fallback fitting is frozen as implemented: optim, then nlminb, no
    restarts.
  - A training-failure policy and per-trial outcome categories are stated.
  - Recording of the feature-failure flags is still to be implemented.
- **Code.**
  - `e2e_benchmark.py` now classifies each trial's outcome, catches an
    unusable covariance, and checkpoints rows to `e2e_rows.jsonl`.
  - The driver waits on each PID and verifies row counts.
  - Re-run against modified copies of Astra's mocked probes, these give
    `indet_calib`, `indet_cov` and a failing driver status. Astra's
    unmodified probe now stops on the renamed `p` field.

**Open:**
- Astra's review of the k-NN proposal;
- Barry's decision on the primary null (one Decision Inbox question, prepared
  by Astra);
- β_min under the chosen null;
- frozen numeric values for the null corner scenarios;
- production banks at 2×10^9;
- the final scenario and cost inventory;
- feature-flag recording and fallback-use recording;
- the census-unit conflicts.

### 9.9 Fable draft 0.8 (9–10 October): what changed

Incorporates Barry's adoption of ar_cat as the primary development null, with
iid as a mandatory sensitivity (Decision Inbox `d36e602c`), and responds to
Astra's 0.7 review and 0.8 pre-check (1253, 1255, 1311, 1313, 1314).
- **Adopted null recorded** (§3.1), with its scope: no freeze, no
  calibration claim, and no claim that catastrophes are necessary.
- **The k-NN library is the development algorithm** (§3.4 step 3).
  - At least K valid runs per bank; recorded K-th distances and flags.
  - Radius-stratified validation diagnostics; the empirical position
    reported.
  - A fitted-parameter predictive stress check, with explicit endpoint
    selection and parameter retention.
  - No extra radius gate.
- **Matched-design wording** (§3.1, `discrimination_v1/`): the 29 vs 21
  contrast does not isolate a cost of broadening the reference. "Projected"
  replaces "realised" for the 0.7 radii.
- **Failure rules** (§3.4 step 4, §4.3).
  - `indet_malformed`, including ragged files; `indet_train` (more than 2% of
    training fits failed); fallback use recorded.
  - Absent arms, results or checkpoints score as missing.
  - The scorer verifies p_lo, p_hi and outcome.
  - `load_bank` checks selected counts, field lengths and strictly
    increasing in-range draw IDs.
- **10× development banks** (`dev_design_v1/`). The measured radii confirm
  the 0.7 projection.
- **Development β_min under ar_cat:** Δ10 = 0.075 (β = 0.975), with an
  increase of +0.130 in 10-year risk from N = 20.
- **Numeric corners** (§4.3). Library medians, with σ at the 90th percentile,
  s at the 10th, or ρ and p_c at the 90th. Strong environment replaces
  short L.
- **Development power screen** (`power_screen_v1/`): detections at null /
  β_min / 2·β_min / Δ10 = 0.3 / Δ10 = 0.5 were 1 / 1 / 2 / 8 / 18 out of 30.
  - O1 is very likely unattainable with nine series.
  - The effect target is retained, a detection curve is added, and O3 is the
    pre-registered consequence of a failed power gate.
- **Measured cost inventory** (§4.4): about 3,130 core-hours and roughly 75
  hours on deep-server, at 0.38 core-hours per trial measured all-in.
- **Exposure:** row E25.

**Open:**
- Astra's review of 0.8;
- implementing M_D and M_O, including priors for d and k and the
  observation-selection interaction;
- production banks with frozen seeds;
- recomputing β_min and the corners on them;
- measuring corner cost;
- the validation freeze;
- the census-unit conflicts;
- Phase II scoping, which the power screen now motivates.

### 9.10 Fable draft 0.9 (10 October): what changed

Responses to Astra's 0.8 review (1348):
- **Stress-check sampling law** (major). Parameter sets are drawn once and
  retained. A budget failure leaves its dataset unresolved, not replaced, and
  is reported with conservative bounds.
- **Execution inventory** (major). A §7 table covers every promised analysis:
  generator, bank reuse or new bank, count, seed family and cost.
  - Totals: about 3,300 core-hours.
  - Ledger-, code- and access-dependent items are marked.
  - The §4.1 development screens (200 under the null, 200 at β_min, with the
    >30/200 stop) are retained and running, not replaced.
- **Finite logged bounds** (minor). The scorer rejects non-finite logged p
  bounds.
  - Fixing this introduced a variable-shadowing bug (`afe9bca`) that scored
    later trials as missing.
  - The smoke test caught it before any production use, and `a31e5bc` fixes
    it.
- **M_D and M_O** (§3.2).
  - Executable laws, with proposed priors Δ ~ U(0, 2) and step time ~ U.
  - The M_O latent/recorded contract.
  - The mixture at β_min.
  - 28 limiting-case checks (`test_bank.py`).
  - Generation cost is under 1% of fitting cost (`alt_check_v1/`).
- **Radius bins frozen:** 0.2050 / 0.2956 / 0.4049 / 0.5613, with ties to the
  lower bin. Source: the 20,000-dataset development sample.
- **Designated banks queued** on deep-server after the screens, with seed
  families 8.1, 8.2 and 8.3 × 10^12. β_min, the corners and the empirical
  position are then recomputed by the fixed recipes.

**Open:**
- the screen results;
- the designated-bank outputs;
- Astra's review of the M_D and M_O priors and of the freeze package;
- then the freeze.

### 9.11 Fable, 0.9 executable completion (10 October)

Responses to Astra's 0.9 review (1368):
- **Stress sampler implemented.** `make_manifest.py` draws and keeps the
  parameter sets. `fresh_selected` has a 10^6-draw budget, and a budget
  failure is `indet_sampling`: it is recorded with the failed populations and
  their retained parameter sets, gets no fits, and is never replaced.
  Block 17 is its single execution point.
- **Run manifest, chunk runner and collector.**
  - `make_manifest.py`, `validate.py`, `run_validation.sh` (at most three
    slots) and `collect_validation.py`.
  - Full intended denominators: missing trials retained, duplicates and
    out-of-chunk rows refused.
  - The null, power and fit-stop gates. The fit stop applies to gating
    blocks only; sampling failures are counted separately.
  - Tests: `test_validation.py`, 19 checks with mocked fits, plus a real-R
    launcher run on a toy manifest, whose rerun skips complete chunks and
    reproduces the summary.
- **Selected-draw provenance** is persisted per trial: parameters, M_D shift
  and step time, recorded and latent counts.
- **Scorer contract v3**, with fit-failure accounting defined. Contracts v1
  and v2 still reproduce the archived runs exactly.
- **Seed families** for the sensitivity banks are now disjoint, and the
  empirical analysis IDs are fixed.
- **Implementation status** is stated. The Q1 entry point
  (`empirical_q1.py`) is guarded and has never been run.
- **Scope wording** (Astra 0.9 review):
  - the cost claim narrowed to generation only;
  - `time_generators.py` takes the recomputed β_min;
  - M_D distributions are design distributions, and equal Δ is not effect
    matched;
  - the M_O start is a plug-in convention;
  - β_min is risk-defined, not a demonstrated minimum detectable effect.

