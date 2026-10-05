# Vortex signatures, selection and feedback: staged study protocol

**Working draft 0.3 — 5 October 2026, Hobart. Not frozen or registered.**

Draft 0.3: Fable revised §§1–4 and 7 in response to Astra's review (R1–R6) and
added §9.3. Astra's 0.2a changes to §§5–6, 8 and 9.2 are unchanged. The
history below is kept.

Draft 0.2: Fable formalised §§1–4 and 7, which replace Astra's planning
summaries, and added a requirement-status table to §9. In 0.2a, Astra addresses
Fable's amendments to §§5–6 and 8, and appends its review disposition in §9.2.
The formal text in §§1–4, 7 and 9.1 remains Fable's **proposed specification**:
the [quantitative review](astra_protocol02_review_20261005.md) identifies
unresolved model and inference defects. It has not been accepted for a freeze.

Barry has expressed a provisional preference for this question and requested a
careful plan combining simulation and empirical work. This document prepares
that plan. It does not record a topic decision or authorize the research stages.

Astra drafted §§5–6 and 8 and the coordination provisions in §9. Fable wrote the
formal §§1–4 and 7 (draft 0.2), absorbing Astra's planning summaries and
requirements. Fable next responds to Astra's review and the
[decision brief](vortex_decision_brief.md).
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

## 1. Scientific aims and minimum contribution — Fable formal draft 0.3

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
terrestrial sample. Are the observed values of the five published
terminal-trajectory statistics T1–T5 (§2.1) compatible with their conditional
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

## 2. Estimands and comparison populations — Fable formal draft 0.3

### 2.1 Part 1 design, statistics and target

For each population i, the design records:
- the first census N_i,first;
- the census years, including the documented interpolations (one census each
  for the wild dog and the middle spotted woodpecker);
- the extinction rule E (F&H: first census ≤ 1);
- the extinction census year, and hence L_i;
- the published final-step convention, N_0 := 1.

Six of the nine windows already match F&H in length when counted from the
first census to the extinction census
([reconciliation](t3/fh_table1_reconciliation.txt)). The wild dog (20 vs 23
years), marmot (21 vs 20) and crane (16 vs 18) must be settled from the F&H
text before freezing.

The five statistics are those F&H published:

| Statistic | Definition | Published value |
|---|---|---|
| T1 | slope of D_s = ln(N_s/N_{s+1}) on s | +0.034 |
| T2 | T1 excluding the final transition | +0.011 |
| T3 | slope of the squared T1 residuals on s | −0.047 |
| T4 | T3 excluding the final transition | −0.012 |
| T5 | period coefficient (s ≤ 9 vs s ≥ 10) in the regression of s on ln N_s | to be transcribed exactly |

T1–T5 are computed by the Stage B estimator (§4.2).

**Target.** The conditional prior-predictive tail probability

> p_joint = P( D(T^rep) ≥ D(T^obs) | C^rep = C^obs, selection S, M0, prior π ).

- D is the Mahalanobis distance of the vector (T1, …, T5) from its
  reference-distribution mean, using the reference covariance.
- C is the vector of per-population calibration summaries (§3.4).

Properties of this target:
- If the data come from M0's prior predictive and conditioning on C is
  exact, then given C the observed and replicate T are exchangeable, so
  p_joint is uniform.
- The ABC neighbourhood only approximates that conditioning. Validation
  (§4.3) therefore measures the procedure's actual false-alarm rate, under
  draws from the prior and at fixed nuisance values on the boundary.
- This is not Bayarri and Berger's partial posterior predictive p-value, and
  §4.3 is a false-alarm experiment, not simulation-based calibration of
  posterior ranks. The 0.2 labels are withdrawn.
- p_joint depends on the prior, so §3.4 specifies two priors.

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

## 3. Generative models and calibration — Fable formal draft 0.3

### 3.1 Null M0: a valid demographic model

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
- **Expected per-capita growth.** It is E[s_t] + f_i, computed by numerical
  integration, and does not depend on abundance.
- **Invariant tests,** passed before any use:
  - support (survival in (0, 1), counts ≥ 0);
  - the identity E[N_{t+1} | N_t] = N_t(E[s_t] + f_i), checked by simulation
    to within Monte Carlo error;
  - absorption at zero;
  - exact replication of each census schedule and of rule E.
- **Scope.** All nine F&H series are counts of individuals (the crane series
  is a peak winter count). Pair and territory units, and age structure with
  delayed recruitment, are misspecification checks for later work, not
  first-tranche models.

### 3.2 Alternatives and mixtures

| Model | Specification | Parameter values |
|---|---|---|
| M_A (feedback in expected growth) | the recruitment rate *and* the survival odds multiplied by g(n) = exp(−β(1/n − 1/N_ref)) for n < N_ref = 50; g = 1 otherwise | β ∈ {β_min, 2·β_min}. Because β ≥ 0 and n ≥ 1, g lies in (0, 1]. Effect sizes are set on the β scale, so doubling never gives an invalid multiplier. Report Δ10 = 1 − g(10) for interpretation. |
| M_D (external deterioration) | the mean of z_t shifted downward, which lowers survival and recruitment together | linear, −d·t; accelerating, −d·t²/L_i; a single step of size k at a uniformly random time. d and k are calibrated like the other nuisances. |
| M_O (observation change) | C_t ~ Binomial(N_t, p(N_t)) | p(n) = 1 − 0.3·exp(−n/10); plus uniform binomial census error with p = 0.9 |
| M_A + M_D | feedback combined with each deterioration form | for discriminability only |
| M_G (genetic) | **deferred** | see below |

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
  g(10) = 0.1, use β_max/2 and report that no decision-relevant effect is
  definable at these parameters.
- **Computation.** 10^5 runs per grid value, done once at Stage C before
  validation.

### 3.4 Conditional calibration algorithm

1. **Bank.** For each population, draw parameters from the prior π and simulate
   M0 from N_i,first with the observed schedule. Keep the runs that satisfy S
   exactly: rule E is met first at the observed extinction census.
   - Target: at least 2 × 10^5 kept runs per population, within a budget of
     J_max = 10^8 draws.
   - A population that cannot reach the target fails calibration, and the
     outcome becomes indeterminate.
2. **Calibration summaries C_i.** Three summaries, standardised by their median
   absolute deviation (MAD) within the bank:
   - the mean squared one-step log change, excluding the final transition;
   - the lag-1 autocorrelation of one-step log changes;
   - the fraction of increasing transitions.

   They are not independent of T, which is why the target is defined
   conditionally (§2.1).
3. **Library.** The K = 2,000 bank runs nearest to c_obs,i, each from a
   distinct parameter draw. The K-th distance must be ≤ 0.25 standardised
   units; otherwise enlarge the bank, or record a calibration failure.
4. **Reference distribution.**
   - Build R = 10,000 replicate datasets, each taking one library run per
     population independently, and apply the Stage B estimator.
   - Estimate the covariance from the replicates, with Ledoit–Wolf shrinkage
     if it is ill-conditioned.
   - p_joint = (1 + #{D^rep ≥ D^obs}) / (R + 1).
   - Monte Carlo stability: repeat with a fresh seed and an independent bank
     half. A change of more than 0.01 triggers a larger R or bank.
5. **Priors.**

   | Prior | Survival | Recruitment, environment |
   |---|---|---|
   | (a) literature-anchored | logit s_i ~ N(logit s_lit, 0.5²), with s_lit from the §5.4 ledger | log f_i ~ U(log 0.01, log 2); σ_i ~ U(0.02, 1.0) |
   | (b) wide | logit s_i ~ N(0, 1.5²) | as (a) |

   Report both priors. If they lead to different outcome labels, report
   *prior-sensitive*.

## 4. Stages, outputs and decision rules — Fable formal draft 0.3

### 4.1 First tranche (to be authorised by Barry, if selected)

This is Astra's proposed tranche, with concrete exit criteria:
1. **Source and metadata audit.**
   - Settle the three F&H windows, the endpoint evidence and the units.
   - Transcribe T5.
   - Build the survival ledger.
   - Close the named prior-work gaps (final Nabutanyi–Wittmann text; Drake &
     Griffen 2009 methods).
2. **Stage B reconstruction.**
   - Both agents implement the F&H estimator independently from §2.1.
   - Pass: T1–T5 reproduced at published precision, which for T1–T4 means
     |Δ| ≤ 0.0005 (three decimals).
   - If that fails: a labelled *reconstructed estimand* with a discrepancy
     table. Never adjust dates, endpoints or values to obtain agreement.
3. **Development pilot** (synthetic only, within the laptop limits).
   - Implement M0, M_A, M_D and M_O and pass the §3.1 invariant tests.
   - Measure, per population, the acceptance rate of the exact selection S,
     simulation throughput, estimator fit time and failure rate, and memory.
   - Run one 200-dataset development screen under M0 and one at β_min.
   - Report a measured production estimate.
   - Stop before production if: a bank is infeasible; fits fail in more than
     2% of datasets; or the screen shows gross miscalibration (more than 30 of
     200 rejections).

Production validation (§4.3) and the empirical test follow only with a
measured cost estimate and Barry's allocation.

### 4.2 Stage B criterion

As in item 2 of §4.1. The 0.2 tolerance of 0.005 is withdrawn as too loose:
it is about half of the published T2 slope.

### 4.3 Production validation (on frozen code, before the empirical p-values)

- **Independence.** The synthetic "observed" datasets never come from the
  library used to test them. Each population's bank is split into halves; the
  observed data come from one half and the library from the other, and the
  halves are then swapped. Boundary scenarios draw fresh trajectories at fixed
  parameter values.
- **Type I error.** Four M0 scenarios:
  - prior-predictive;
  - three nuisance corners: high σ; low survival; short L, using the shortest
    observed window.

  Each gets 1,000 datasets. It passes if the one-sided upper 98.75%
  Clopper–Pearson bound on its rejection rate is ≤ 0.08 (Bonferroni across the
  four), which means at most 60 rejections in 1,000.
  - A true 5% test passes with probability 0.93; a true 6.5% test with 0.29; a
    true 8% test with about 0.01.
  - If a scenario fails at 1,000, extend it once to 1,200 (pass if ≤ 75). If it
    still fails, or the budget is exhausted, the result is V-fail.
- **Power.** 300 datasets under M_A at β_min (prior-predictive nuisances). The
  O1 label requires a lower one-sided 95% Clopper–Pearson bound ≥ 0.70, which
  means at least 224 detections in 300. True power of 0.80 passes with
  probability 0.99; true power of 0.70 with 0.04.
- **Discriminability.** 300 datasets each for M_A at 2·β_min, the three M_D
  forms, M_O, and the M_A + M_D mixtures. Detection rates are reported with
  exact intervals. These are descriptive only and are not a gate.
- **Failed fits.** Refit with an alternative optimiser and new starting values.
  A failure rate above 2% in any scenario stops validation pending a
  documented estimator revision. Report p-value bounds that treat failures as
  most and least extreme.
- **Development vs validation seeds.** Seeds 1–999 are for development. Final
  validation uses seeds ≥ 10^6, run once on frozen code.

### 4.4 Compute

The 220-core-hour figure is withdrawn: it omitted simulation and selection
costs.
- **Main term.** Production cost is dominated by estimator fits:
  - validation: 4 null scenarios × up to 1,200 datasets, plus 6 alternative
    scenarios × 300 datasets, each with R_v replicate fits;
  - the empirical test: 2 × 10^4 fits.
- **Banks.** These are one-off costs, set by the acceptance rates.
- **Benchmark.** The pilot measures fit time t_fit and acceptance rates, and
  sets R_v (between 1,000 and 2,000).
- **Sequential p-values.** Validation p-values use Besag–Clifford sequential
  Monte Carlo tests (Besag & Clifford 1991, doi:10.2307/2337256). Each test
  stops at 20 exceedances or at R_v replicates. This keeps the tests valid
  while cutting fits for the many clearly non-significant datasets.
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
matches 24 of 27 scalar fields, not the fitted statistics; its Williams spans
end at the last nonzero census. Replay requires the manifest-matching source
CSV and verification of its hash. Existing CSVs do not demonstrate exact
reproduction of the fitted statistics.

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

## 7. Analysis and reporting plan — Fable formal draft 0.3

**Prespecified vs exploratory analyses.**

| Analysis | Status |
|---|---|
| Q1: p_joint on T1–T5 under priors (a) and (b), with the validation results and outcome labels of §1 | Prespecified, **primary** |
| Q2: discriminability rates (§4.3) | Prespecified, **primary** |
| Each p_k (Holm-adjusted across the five) | Prespecified, secondary |
| Williams statistics on complete-count series confirmed by the audit (Q3) | Prespecified, secondary |
| Sensitivity: exact endpoint vs the study's inclusion window; rule E (≤ 1 vs 0); separate environmental factors; leave-one-population-out across all nine; runs of identical counts treated as missing except the first, where provenance is uncertain | Prespecified, reported regardless of result |
| *Daphnia* (if the data are obtained): the Q1 pipeline applied to the deteriorating replicates. A departure is a diagnostic to investigate with the controls, not proof of error, since the known food reduction does not rule out concurrent feedback. | Prespecified diagnostic, conditional on access |
| Part 2; M_G; the founder-size module; the 2016 LPD subset; anything not listed here | Exploratory, or parked until a dated amendment |

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

Fable's formal draft and Astra's review/brief are now recorded. Fable is next to
respond to the quantitative objections and review the brief. This is a dependency
order, not a promise of elapsed runtime before the data and models are settled.

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
