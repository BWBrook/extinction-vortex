---
title: "Vortex signatures and a proposed first study"
subtitle: "Decision brief for Barry W. Brook"
date: "5 October 2026 · Astra recommendation after Fable review"
fontsize: 11pt
papersize: a4
geometry: margin=20mm
colorlinks: true
---

**Recommendation.** Select the vortex question and authorize the bounded first
tranche on page 2: source checks, reconstruction and a small computational
feasibility pilot. Fable supports this direction. Draft 0.3 addresses the major
model defects, but the production test still needs development and validation.
This brief proposes the decision; it does not record your authorization.

**Scientific question.** Do the terminal-trajectory statistics reported by
Fagan and Holmes (2006), and subsequently Williams et al. (2021), depart from
a matched no-feedback model once extinction-based selection is reproduced?
How often would feedback, external deterioration or observation error produce
such departures?

The minimum completed study combines empirical reanalysis with simulation
estimates of detection and false-alarm rates. Its primary case is the nine
Fagan–Holmes populations; verified Williams complete-count series provide a
secondary comparison. The first analysis cannot identify which mechanism
caused a departure. Genetic modelling and the forward GPDD analysis are parked.

**What could be new.** A matched reconstruction of the published estimators,
with measured limits on their interpretation. [Griffen and Drake (2009)](https://doi.org/10.1098/rspb.2008.1558)
explicitly study conditional final declines and cite Fagan–Holmes for
logarithmic duration scaling. Conditioning itself is established prior work.
Our bounded search has not identified the same five-statistic matched
reanalysis, but novelty remains provisional. The final Nabutanyi–Wittmann
paper and Drake–Griffen's separate 2009 passage-time methods still need checking.

**Data readiness.** The public CC0 Williams input is archived with verified
checksums. Replaying the summary comparison gives 24 of 27 fields matching;
six of nine window lengths agree when the zero census is included. Wild dog,
marmot and crane windows, other table discrepancies, and 150 versus 148 nonzero
censuses remain unresolved. None of this reproduces the fitted statistics.
Williams's census-unit and extirpation classifications still require source checks.

**Realistic outcomes.** The full study could find a departure needing
explanation, conditional compatibility with demonstrable power, or insufficient
discrimination. We cannot yet rank their probabilities. Compatibility requires
validated false-alarm control and a lower 95% power bound of at least 70% for
an attainable, stated effect; it would not establish absent feedback.

A reproducible reconstruction and a credible account of the nine-population
design's limits could support a short methods paper. Publication is contingent
on the results being informative. This design alone will not establish how many
extinctions future studies need; that requires a separate sample-size analysis.

\newpage

**Proposed first tranche and stopping points**

| Work | Deliverable and stop condition |
|---|---|
| Source and metadata audit | Verify the public inputs, windows, census units, endpoint evidence and closest prior work. Stop or narrow the claim if the required observations cannot be supported. |
| Published-analysis reconstruction | Independently implement the Fagan–Holmes estimator and compare with published precision. Preserve discrepancies; label a reconstructed estimand if exact reproduction is impossible. |
| Small synthetic development pilot | Check the null and feedback generators; benchmark selection acceptance, estimator stability, memory and total cost. Specify the calibration repairs and comparator scenarios. Stop at the limits below and report what remains untested. |

**Resource limit for this tranche.** Public data, one local worker, at most
2 GiB memory for the pilot and 30 aggregate CPU-minutes of synthetic development.
Stop earlier at 10,000 candidate trajectories per population or 20 complete
nine-population estimator fits. These are ceilings, not promised sample sizes.
The 400-dataset development screen and large accepted-trajectory banks in
draft 0.3 are outside this tranche. Source reading and reconstruction accompany
the capped pilot; no access agreement or provider contact is required.

**Before production.** The agents must settle census windows and model units,
define an attainable effect target, ensure that the Monte Carlo comparison is
valid, remove or correctly adjust the optional validation extension, and freeze
the scenario list and decision rules. The fixed 1,000-dataset false-alarm and
300-dataset power calculations check out; the proposed repeat-at-1,200 rule
does not retain the stated confidence guarantee. These are agent tasks.

The tranche ends with a reconstruction report, executable checks and a measured
estimate for larger runs. The earlier 220-core-hour figure is withdrawn.
Production would require your allocation for a suitable remote host after the
method is ready. Failed calibration or an unattainable effect target prevents
an informative-compatibility claim. No empirical p-value is part of this tranche.

**Division of work.** Fable leads calibration development; Astra leads the
source/exposure record and reviews inference. Once authorized, both implement
the critical estimator and null sampler separately from one agreed
specification. Additional data agreements, translocation work, *Daphnia*
acquisition and Part 2 require later decisions. The scientific target remains
what terminal abundance summaries identify, with no presumption against the
broader evidence for genetic or Allee effects.

**Your decision:** select this question and authorize the bounded first tranche,
or redirect the project. The agents handle the routine methodological work
within the selected scope.

Supporting records: [working protocol](vortex_protocol.md),
[draft 0.3 review](astra_protocol03_review_20261005.md), and
[prior-work search record](vortex_prior_work_search_20261005.md).
