# Astra's review of vortex protocol 0.2

5 October 2026, Hobart. Reviewed baseline: `24945ff5fd14101a8fca0c3ba056668e987a2d94`.
This records Astra's assessment, pending Fable's response. It does not freeze the
protocol or authorize research execution.

**Recommendation:** retain the question, but revise the quantitative specification
before freezing it. The first defensible execution tranche is source/metadata
verification, reconstruction of the published analysis, and a small synthetic
development pilot. Production Stage C and the forward extension need further
specification and an end-to-end benchmark. The [decision brief](vortex_decision_brief.md)
sets out that bounded recommendation for Barry.

The draft makes several essential commitments: a population-matched comparison,
the same processing and estimator for real and simulated data, an explicit
insufficient-identification outcome, recorded exposure, and a conditional Part 2.
Those commitments survive this review. Numerical detail has exposed several
problems that the proposed validation cannot simply be assumed to cure.

## Changes required before the Part 1 analysis freeze

### R1. Make the null a valid probability model

Sections 3.1 and 3.4 imply recruitment `f = lambda - s`, but draw lambda and
survival independently. For example, lambda = 0.5 and s = 0.9 give a negative
Poisson rate. The survival interval can also exceed one. These are admissible
draws under the written priors, not rare numerical failures.

Parameterize bounded survival and non-negative recruitment directly, or specify
a justified joint constrained distribution. Define the census life stage,
transition interval, propagation across missing years, and environmental
covariance between survival and recruitment. Adult survival alone does not
identify demographic variance for all-age, pair or territory counts. Verify
support, moments and absorbing-state behaviour before fitting anything.

### R2. Repair or defer the genetic alternative

Section 3.2's recurrence gives `F_next = 2.5` when F = 0, N = 2 and Ne/N = 0.1.
The terminal trajectories therefore enter a region where the approximation is
not a valid inbreeding process. Its annual time step, initial F = 0 and use of
an adult Ne/N ratio also need biological justification.

[O'Grady et al. (2006)](https://doi.org/10.1016/j.biocon.2006.05.016), Methods
2.1–2.3, distinguish the haploid coefficient in the exponential from reported
diploid lethal equivalents, and distribute effects across life stages. The
draft labels B as diploid but puts it directly into `exp(-B*F)`. It cannot claim
that this annual, whole-growth multiplier implements that paper's model.
[Frankham (1995)](https://doi.org/10.1017/S0016672300034455) supports a
comprehensive mean Ne/adult-N ratio near 0.10–0.11; 0.3 should be identified as
a sensitivity choice, not an equally supported estimate for every census unit.

The smallest pilot can use one valid phenomenological feedback alternative.
Add M_G only after specifying a bounded process, time scale and coefficient
convention. The draft's delta_min is defined for M_A, so an M_G power statement
“at delta_min” currently has no meaning. Define a common risk contrast or
separate model-specific effect targets; define the endpoint and the case where
the proposed ten-percentage-point increase is unattainable. Keep Delta below
one; doubling delta_min must not create an invalid multiplier.

### R3. Choose the inferential target before choosing its algorithm

Keeping calibration summaries C different from tested summaries T does not make
them independent. Reusing accepted trajectories in §3.4 could approximate a
conditional reference distribution `p(T | C, selection)`. That is a coherent
possible target, but is different from drawing new trajectories from fitted
parameters for posterior prediction.

[Bayarri and Berger (2000)](https://doi.org/10.1080/01621459.2000.10474309),
equations 8–9, define a particular partial posterior that removes T's likelihood
contribution. The draft does not implement that construction. Likewise,
[Talts et al. (2018)](https://arxiv.org/abs/1804.06788), §4, validate posterior
computation using parameter ranks; a repeated false-alarm experiment is a
different useful check. Correct the labels and specify the actual procedure.

Required details are the conditioning event, summary standardization, tolerance,
minimum accepted/effective sample size, tail calculation, covariance estimation
and failure rule. Validation datasets must be independent of their reference
libraries, or use an explicit cross-fitting construction. Include nuisance-space
boundary cases as well as posterior-weighted averages. Retaining every survivor
when very few simulations meet the endpoint does not establish adequate accuracy.

### R4. Separate an exploratory calibration screen from a validation gate

Four to sixteen rejections in 200 is the central binomial acceptance range under
an exactly 5% error rate. It does not establish that the rate is acceptably close
to 5%: a procedure whose true rate is 8% still passes this count criterion about
57% of the time. At 10/200, the exact 95% interval is 2.4–9.0%; at 160/200,
power's interval is 73.8–85.3%; at 20/200, misattribution's interval is 6.2–15.0%.
The KS screen does not turn these into assurances of the stated rates.

Use 200 runs, if convenient, as a development screen. For final validation,
specify acceptable error margins and confidence-bound criteria, accounting for
the number of scenarios, with a maximum replication budget and an indeterminate
outcome. Validation failure must take precedence over every empirical outcome.
A non-rejection plus design power is still conditional compatibility, not proof
of absent feedback or a posterior probability of the null.

### R5. Complete the classifier or limit Part 1 to discrepancy testing

The 0.8 classification threshold in §4.3 lacks model priors, scenario weights,
external-deterioration parameter ranges, library construction and probability
calibration. A choice among five pure generators does not identify a biological
cause when forcing, feedback and observation error can coexist. Specify these
items and include mixtures, or report only departure and model-specific
discriminability. This simpler first analysis would still address Q1–Q2's
central question, with any reduction of the attribution aim stated openly.

The *Daphnia* food treatment establishes an external cause, not the absence of
every concurrent feedback. A feedback classification there is a diagnostic to
investigate with controls and assumptions, not automatically a proven error.

### R6. Finish reconstruction and price the complete computation

The archived Table 1 check is a useful correction: 24 of 27 **scalar fields**
(increase/start/final, across nine populations) agree. It does not reproduce
T1–T5. Williams's reported spans end at the last nonzero census, whereas the
F&H windows use their own extinction endpoint. The 150-versus-148 comparison
also needs matched windows and definitions. The script accepts any supplied CSV
and does not check its hash; the manifest-matching input is absent from this
checkout. A replay needs that input and verification of its recorded hash.

Stage B should compare at published precision and explain discrepancies. An
absolute tolerance of 0.005 is large relative to a published slope of 0.011;
it cannot by itself establish reconstruction. Transcribe T5 and settle each
analysis window before the analysis freeze. If exact reconstruction is
impossible, label the new estimand and the limits of comparison explicitly.

The stated 220 core-hours covers roughly four million fits at an assumed
0.2 seconds each. The same formula entails 1.8 billion simulated trajectories
for a single reference generator, before other libraries, selection rejection,
ABC distances and additional estimator fits. It is not yet a production cost
estimate. Benchmark the full pipeline, acceptance rate, memory and I/O using a
small synthetic design. No heavy computation was run for this review.

## Part 2 and the four amendments

1. **Accept a fixed GPDD primary frame.** Keep bibliographic additions secondary.
   This controls our discovery rule; it does not prove that GPDD monitoring or
   inclusion was independent of population fate. The claim that every literature
   series is necessarily outcome-selected is too strong.
2. **Accept survival-source and census-season fields**, adding the counted life
   stage, interval and any documented unit conversion. Parameter uncertainty
   remains a modelling issue, not something an extra citation resolves.
3. **Accept a structural identification pilot**, with explicit exposure limits.
   Threshold-entry counts are abundance-derived, and prior endpoint aggregates
   reveal outcomes. Record that exposure and frame overlap. Do not estimate
   nuisance parameters from new forward responses under the guise of metadata;
   §3.4's proposed GPDD sigma check would need its own exposure decision.
4. **Accept separate F&H estimators and M0 samplers after authorization and a
   shared mathematical specification.** Fable leads the conditional-calibration
   implementation, Astra reviews; Astra leads a forward likelihood only if that
   extension is justified. Freeze separate implementations before comparison and
   disclose existing shared-code exposure.

Part 2 itself remains incomplete. A conditional mean plus a citation to an
initial-conditions method is not a full likelihood. Process, observation,
random-effect, immigration and censoring distributions are missing. Beta is
an incremental low-abundance shape beyond the existing Gompertz term; its units
and pooling target need specification. The horizon remains open.

[IUCN Categories and Criteria v3.1](https://portals.iucn.org/library/sites/library/files/documents/RL-2001-001-2nd.pdf),
pp. 10 and 18, use mature individuals and a taxon-level criterion. Applying 50
to all-individual counts, or 25 indiscriminately to pairs and territories,
requires additional assumptions. Use a justified stratum-specific threshold or
call these operational thresholds. Do not claim IUCN equivalence. Similarly,
Williams's indices and densities need observation models before an integer-count
generator can supply their reference distributions. Neither issue must delay
the nine-series reconstruction.

## Prior-work update and limits

The earlier [bounded source audit](astra_round1_review_20261005.md) already
identified Dennis, Boettiger–Hastings and Hefley as limiting broad novelty.
This pass adds two particularly close leads:

- [Griffen and Drake (2009)](https://doi.org/10.1098/rspb.2008.1558) analyse
  conditioned final declines, extend Lande et al.'s scaling theory, and test it
  using laboratory populations. The introduction, methods and discussion were
  inspected in the author-posted text. This precedes any proposed claim that
  conditioning or stochastic final-decline patterns are newly discovered here.
- [Drake and Griffen (2009)](https://doi.org/10.1111/j.1461-0248.2009.01325.x)
  test equal passage-time predictions for population increases and declines.
  The primary abstract was inspected; its full methods remain a close-prior-work
  task. A later [35-population experiment](https://doi.org/10.1111/ele.70178)
  concerns habitat-size/extinction-time scaling, not the proposed matched
  F&H/Williams estimator comparison.

The potential contribution is narrower: reconstruct the published summaries,
quantify their compatibility with explicitly conditioned processes, and measure
their ability to distinguish specified alternatives at the observed design.
No directly equivalent matched reanalysis was identified in the records examined;
that is a bounded search result, not a demonstrated absence from the literature.

The [search record](vortex_prior_work_search_20261005.md) supplies actual query
URLs, retrieval counts, returned identifiers and inspection limits. Final
Nabutanyi–Wittmann text remains unavailable in this check; the earlier audit used
its accessible preprint and final abstract. The new passage-time lead, literature
coverage and source-level frame validation remain Stage A work. Do not rename
this orientation search a completed systematic review.

## Verification and next owner

Astra inspected the protocol, code and sources, and checked the binomial
calculations in base R. A separately tasked methodological auditor
(`sol_max_auditor`, configured GPT-5.6-sol, max effort) checked the formal model,
decision rules and workload; a read-only scout checked the reconciliation and
retrieval metadata. These checks did not fit empirical models or reopen GPDD
trajectories. Agreement is not empirical validation.

**Fable is next:** respond to R1–R6 with a compact corrected specification and
review the decision brief. Leave Part 2's unresolved model explicitly open.
Astra will integrate any substantive disagreement before presenting a joint
execution recommendation. Barry need not choose ABC details, thresholds or an
unsupported compute allocation on the agents' behalf.
