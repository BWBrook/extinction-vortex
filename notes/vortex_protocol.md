# Vortex signatures, selection and feedback: staged study protocol

**Working draft 0.1 — 5 October 2026, Hobart. Not frozen or registered.**

Barry has expressed a provisional preference for this question and requested a
careful plan combining simulation and empirical work. This document prepares
that plan. It does not record a topic decision or authorize the research stages.

Astra drafted §§5–6 and 8, the coordination provisions in §9, and the planning
summaries in §§1–4 and 7. Fable owns the formal specification of §§1–4 and 7 and
will review Astra's sections; Astra will then review the integrated protocol.
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

## 1. Scientific aims and minimum contribution — Fable to formalize

**Primary question:** do published terminal-trajectory summaries distinguish
feedback in expected per-capita growth from demographic/environmental
stochasticity under outcome selection, observation processes and external
deterioration?

The minimum empirical contribution is a reproducible reconstruction of the
Fagan–Holmes terrestrial analysis and a population-matched comparison of its
observed statistics with calibrated simulated distributions. The corresponding
simulation experiment must show which candidate processes those statistics can
distinguish. A generic stochastic-path demonstration alone does not meet this
objective. Novelty remains a question for the final prior-work check, not an
assumption secured by preregistration.

**Conditional extension:** estimate abundance dependence among a defined cohort
entering small-population states, if available data and synthetic validation
support identification. This extension is not necessary merely to give the
project an empirical component. Neither component identifies genetic versus
other biological causes without additional mechanism-specific evidence.

Retain three conclusions: compatibility with the specified null; departure that
needs explanation; and insufficient identification or precision. A large
residual is not a reason to abandon the question. Failure of a forward gate
does not strengthen the claim that feedback is absent.

## 2. Estimands and comparison populations — Fable to formalize

| Component | Proposed target | Boundary to preserve |
|---|---|---|
| Part 1 primary | The original nine-population Fagan–Holmes terrestrial summaries, including the specified final-step treatment | Conditional inference for the published sample, not general extinction probabilities |
| Part 1 secondary | The accessible Williams populations, with their actual preprocessing and sampling units | The nine Fagan–Holmes populations overlap this sample; it is not an independent replication. Four of 35 Williams series are reported unavailable as raw public data. An accessible-subset refit is not reproduction of the full 35-series result. |
| Part 2 extension | Arithmetic expected per-capita growth at latent abundance `n > 0`, and joint extinction/abundance transitions, among eligible entrants | Retain direct transitions from above the threshold to observed zero; model their fate rather than silently requiring survival. Do not define a per-capita ratio at `n = 0`. |

For Part 2, specify the population/area boundary, census unit, entry threshold,
pre-entry history requirement, calendar follow-up horizon and treatment of
immigration/recolonization. A threshold in individuals is not interchangeable
with the same numerical threshold in pairs, nests or territories. The target
is the monitored sampling frame, not prevalence of feedback among all species.

The likelihood must address ascertainment into the entrant cohort and the
distribution of latent population effects. Including entrants' entire observed
histories does not automatically make an unconditioned random-effects model
valid. Define either an adequate full monitored risk set or explicit conditioning
on entry/history; test the chosen approach in synthetic recovery.

## 3. Generative models and calibration — Fable to formalize

The proposed baseline has abundance-independent expected per-capita recruitment
with demographic and environmental variation. Its environmental multiplier must
be centred consistently with the arithmetic mean being claimed. Arithmetic-scale
modelling avoids a log-transformation artefact under that specified transition
model; it does not remove ascertainment, observation error or extinction risk.

Before freezing, specify:

- study-specific endpoints and ascertainment: exact first-passage conditioning
  versus selection within a monitoring window, initial states, missing years,
  interior/recovering zeros, extinction at one versus zero, and terminal-value
  substitution;
- joint nuisance calibration for drift, process variance, observation error and
  serial dependence, including parameter uncertainty and sensitivity to
  misspecification;
- which observations inform calibration and which diagnostic features are
  tested, with the full estimation/selection procedure repeated in validation;
- a small, justified alternative set covering low-abundance feedback, external
  deterioration and observation change, with relevant departures from the fitted
  forms. A linear time trend is a candidate model, not proof that deterioration
  has been separated from abundance effects.

Exact Brownian first-passage drift invariance is not a licence to assume weak
drift dependence in a discrete demographic model selected within a window.
Similarly, re-estimating preterminal variance in a bootstrap propagates the
specified estimator's variation but does not establish that the selected
preterminal segment identifies environmental variance. These require validation.

## 4. Stages, outputs and decision rules — Fable to quantify

| Stage | Concrete output | Condition for proceeding |
|---|---|---|
| A. Protocol and metadata | Search/eligibility rules, audited source map, exposed-data record, units and observation schedules | Resolve the specifications required below; preserve outcome exposure honestly |
| B. Published-data reconstruction | Original-versus-reconstructed statistics and a discrepancy table, with scripts and input hashes | Reproduce the estimators or define a justified, explicitly labelled reconstruction. Do not silently alter dates, endpoints or observations to obtain agreement. |
| C. Part 1 calibrated comparison | Observed statistics against population-matched null distributions, plus false-attribution/power results across candidate processes | Validation supports the comparison's stated interpretation; report all three scientific outcomes from §1 |
| D. Part 2 identification gate | Synthetic recovery at the audited sampling structure, including censored and immediate-zero entrants | Meet numerical error-control, precision and power criteria fixed before the decisive simulations; otherwise stop the empirical extension |
| E. Forward analysis, conditional | The prespecified estimate, uncertainty and sensitivity results for the frozen cohort | Open additional post-entry responses only after the gate and analysis freeze |

A rough feasibility simulation can precede compilation. The decisive gate cannot
be described as using realised sample structure until that structure has been
audited. Metadata extraction therefore precedes it. Post-entry response extraction
and model fitting remain later activities.

Fable must supply, with reasons, the smallest scientifically meaningful effect,
false-attribution criterion, required precision/power, Monte Carlo precision,
parameter grid, missingness/censoring scenarios and treatment of convergence
failures. Do not select these to make an observed power curve pass. Separate
development seeds/scenarios from the final validation set, and specify what
that separation does and does not test. Failure to distinguish deterioration
from feedback is a failed identification gate even if the fitted Allee model
recovers its own generating parameter.

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
still need an archived reconciliation. Existing CSVs do not demonstrate exact
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
Treat supplementary bibliographic discoveries and any additional database as
separate ascertainment strata. Full LPD access is optional and outside the
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
| Competing explanations and prior work | `"extinction vortex"`; `"extinction" AND ("conditioning" OR "selection bias" OR "first passage" OR "null model")`; exact titles and citation links for Fagan–Holmes, Williams, Boettiger–Hastings, Dennis, Nabutanyi–Wittmann and Hefley |
| Outcome-neutral discovery of monitoring data | `("population" OR "abundance") AND ("census" OR "monitoring") AND ("time series" OR "long term" OR "annual counts")`; GPDD source citations and references in eligible monitoring compilations |

These are logical query templates, not claims that both APIs accept identical
Boolean syntax. Archive each provider's actual query, filters, retrieval date,
pagination/completeness status and returned identifiers. Verify translation
against known seed records before freezing the executable search. Neither a
search-engine ranking nor a citation count establishes search completeness.

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

For the forward primary cohort require:

- a defined wild population or local population with a sufficiently stable area
  and census target, and a source-supported observation protocol;
- absolute abundance in a defined biological unit, with evidence for completeness
  or enough detection information for the specified observation model. A database
  label alone is insufficient. Keep individuals, breeding units and estimates
  separate until their model/threshold interpretation is justified;
- observation dates and units that permit the chosen transition interval, plus
  the prespecified pre-entry information. Missing years remain missing; multiple
  visits and changes in survey design must be identified;
- a threshold crossing defined from history available at entry, retaining direct
  entry to zero in the joint fate/abundance analysis. Series already below the
  threshold when observation begins form a left-truncated group, not invented
  observed crossings.

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
| Observation design | Biological unit/stage, census/estimate/index, effort/area, evidence for detection, observation dates, missingness and design changes |
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

New post-entry abundance trajectories, growth summaries, fitted feedback effects
and derived responses remain outside analyst context until release. Titles and
abstracts can also reveal fate incidentally; log that exposure. If prior endpoint
knowledge cannot be isolated from cohort/design choices, report a prespecified
analysis of partly exposed existing data, not validation on wholly unseen
outcomes. An independent extractor may mechanically split files, but its access
and summaries must also be logged. A checksum shows file identity, not that
nobody inspected its contents.

## 7. Analysis and reporting plan — Fable to formalize

Specify the primary statistic or joint decision rule, secondary summaries,
multiplicity, uncertainty, sensitivity grid, calibration targets, failed fits,
missing observations and permissible exclusions. Retain the published processing
as one explicitly labelled target even if a corrected estimator is also studied.
Do not silently replace it and call the replacement a reproduction.

The primary empirical result should be an observed-versus-simulated comparison
with uncertainty, accompanied by the estimator's validated discrimination limits.
Describe departures from a null as departures from that model; they are not
automatically genetic or Allee evidence. Report inaccessible populations, overlap,
selection and detection limitations alongside the result. Daphnia is an already
known external-treatment benchmark, not an untouched positive feedback control.

## 8. Responsibilities and separate implementation — Astra draft

| Owner | Output and evidence standard | Stop / handoff |
|---|---|---|
| Fable | Formal §§1–4 and 7; source-supported model ranges and quantitative gate; review §§5–6 and 8 | Return an integrated draft resolving the items in §9; no empirical fitting implied |
| Astra | §§5–6 and 8, source/exposure corrections; review Fable's formal specification and evidence | Prepare Barry's concise decision brief after reciprocal review |
| Both agents | Separately recorded screening decisions; source adjudication; critical code comparisons | Escalate only unresolved choices that change the scientific target or require Barry's access/authority |
| Barry | Scientific direction and final scope; optional access agreements, major extensions and external commitments | One coherent study decision rather than approval of routine stages |

After the study is authorized, use a common written mathematical specification
and synthetic fixtures for the consequential components: conditional simulation
and the empirical-summary estimator, and the forward likelihood if it survives
its gate. Agree implementer/reviewer ownership before coding. Freeze each
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

Fable is next to integrate its sections and answer these specifications. Astra
then reviews once and prepares the decision brief. This is a dependency order,
not a promise of elapsed runtime before the data and models are settled.

Current authorization covers this protocol, bounded source checks, correspondence
and ordinary Git synchronization. The research programme awaits Barry's direction
on the concrete plan. No new access agreement, provider contact, publication or
submission is included. The public-data core should not depend on optional LPD
access or a translocation module. Small pilots must fit the WSL resource limit;
before larger execution, estimate cost from a small benchmark and consult the
existing compute-resource instructions. No heavy compute belongs on this laptop.
