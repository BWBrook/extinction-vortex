---
title: "Vortex signatures: proposed first study"
subtitle: "Decision brief for Barry W. Brook"
date: "5 October 2026 · Astra recommendation, pending Fable review"
fontsize: 11pt
papersize: a4
geometry: margin=20mm
colorlinks: true
---

**Recommendation.** Keep the vortex question as the leading candidate. Start,
if selected, with a bounded reconstruction and method-development phase. The
quantitative protocol needs repair before an empirical test or production
simulation campaign can be frozen. This brief proposes scope; it does not record
your authorization.

**Scientific question.** Do the terminal trajectories reported by Fagan and
Holmes (2006), and subsequently Williams et al. (2021), distinguish feedback
that reduces expected growth at small abundance from stochastic paths selected
because they ended in extinction, external deterioration and observation error?

The minimum study combines a real-data reconstruction with simulation tests of
what those summaries can distinguish. A forward GPDD analysis is an optional
extension. A valid result could show conditional compatibility, a departure
needing explanation, or insufficient discrimination. None alone establishes
the absence or presence of genetic feedback in wild populations.

**What could be new.** The matched reanalysis and its measured discrimination
limits. Conditioning and stochastic final-decline patterns are established:
[Griffen and Drake (2009)](https://doi.org/10.1098/rspb.2008.1558) combine theory,
simulation and laboratory data; [Boettiger and Hastings (2012)](https://doi.org/10.1098/rspb.2012.2085)
show selection effects in early-warning signals; [Hefley et al. (2016)](https://doi.org/10.1111/ele.12671)
show that environmental deterioration can confound inference about density
dependence. No directly equivalent matched reanalysis was identified in our
bounded checks. Novelty remains provisional, with specific close-prior-work
and access gaps recorded.

**What the data presently support.** The public Williams deposit contains
versions of the nine Fagan–Holmes terrestrial series. The archived reconciliation
matches 24 of 27 summary-table fields, with 150 versus 148 nonzero censuses;
it has not reproduced the fitted statistics. Windows, endpoint conventions and
one turtle discrepancy remain unresolved. Williams's accessible subset is
reported as 31 of 35 series; mixed census types need separate observation
models. The inventory's 13 complete-count and 10 supported-extirpation labels
remain provisional. No final eligible forward-cohort size is established.

**Why draft 0.2 needs another methodological pass.** Its priors permit negative
recruitment, its genetic recurrence can exceed the valid inbreeding range, and
its conditional test and classifier are not yet fully specified. The proposed
4–16 false alarms in 200 simulations is a useful screening calculation, not
evidence that the error rate is close enough to 5%. We should resolve these
issues ourselves before asking you to commit substantial compute.

\newpage

**Proposed first tranche and stopping points**

| Work | Deliverable and stop condition |
|---|---|
| Source and metadata audit | Verify the public inputs, windows, census units, endpoint evidence and closest prior work. Stop or narrow the claim if the required observations cannot be supported. |
| Published-analysis reconstruction | Independently implement the Fagan–Holmes estimator and compare with published precision. Preserve discrepancies; label a reconstructed estimand if exact reproduction is impossible. |
| Small synthetic development pilot | Implement a valid null, one feedback alternative and an external-decline comparator; specify conditioning and independent calibration. Test probability-model invariants, acceptance, estimator stability and total runtime. Stop before production if these fail. |

The eventual public-data core remains reconstruction **plus** calibrated
simulation and empirical comparison. Before production, the agents would freeze
the corrected model, effect targets, confidence-bound validation criteria,
exposure record, code and measured resource estimate. Failed validation means
insufficient identification. Scientific redirection returns to you; routine
implementation remains with the agents.

**Resources.** The quoted 220 core-hours counts assumed fitting time but omits
major simulation and selection costs; it is not a defensible allocation yet.
Benchmark within the laptop limits, then size larger runs for `deep-server`
under the existing compute policy. No production run has been launched.

**Optional work.** Keep the Living Planet Database agreement, provider contact,
translocation module and *Daphnia* data acquisition outside this first tranche.
None is needed to establish an empirical core. Part 2 first needs a verified
frame, defensible units and a complete likelihood. IUCN's threshold concerns
mature individuals; a simple 50-individual/25-territory conversion is not yet
justified. Known *Daphnia* treatments can test sensitivity to external forcing,
but do not establish that every other feedback is absent.

**Division of work.** Fable next repairs the formal specification and reviews
this brief. Astra maintains the source/exposure record and reviews the revised
inference. Once authorized, both separately implement the critical estimator
and null sampler from one agreed specification. Your role is to choose the
scientific direction and scope. The critique's target is what terminal abundance
summaries identify; it need not challenge the broader evidence for genetic or
Allee effects, including work you co-authored.

**Decision to bring back after Fable's review:** whether to select this question
and authorize the bounded first tranche above. No access agreement, browser
download or production-compute commitment is needed for that choice.

Supporting records: [working protocol](vortex_protocol.md),
[Astra's detailed review](astra_protocol02_review_20261005.md), and
[prior-work search record](vortex_prior_work_search_20261005.md).
