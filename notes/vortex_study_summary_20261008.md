# Vortex study: pre-approval Q&A with Barry

8 October 2026, Hobart. Fable's answers in chat to Barry's final sanity-check
questions before he approved the study. Barry's questions are quoted verbatim;
the answers are reproduced as given. The approval itself is relayed verbatim in
discussion 70, message 1131.

Sources:
- [protocol draft 0.3](vortex_protocol.md), with the repairs accepted in board
  messages 1049 and 1051;
- the [decision brief](vortex_decision_brief.md).

The numbers in A2(vi) come from exploratory, unmatched simulations
([`checks/fh2006_null_check.txt`](checks/fh2006_null_check.txt)). They are a
prior, not a result.

## Q1. "What is the novelty of the proposal?"

The novelty is an audit of the evidence, not a new theory.

**Not new:**
- the theory that a decline conditioned on ending in extinction looks like a
  final collapse (Lande et al. 2003; Griffen & Drake 2009);
- the general warning that selecting on the outcome biases the summaries
  (Boettiger & Hastings 2012, for early-warning signals);
- the point that environmental deterioration is easily mistaken for density
  dependence (Hefley et al. 2016).

**New, as far as our bounded search shows:** a population-matched test of the
empirical evidence the field actually cites for the vortex. That evidence is
the five statistics of Fagan & Holmes (2006), cited about 420 times, plus the
Williams et al. (2021) series. The test simulates populations with no
small-population feedback, then runs them through the same selection on
extinction, the same census processing and the same estimator. It asks two
things:
1. Do the published signatures depart from what selection alone produces?
2. How often would those statistics detect true feedback, external
   deterioration or observation error at the actual nine-population design?
   That is, what can this evidence distinguish at all?

**Why it matters:** the theory has been available for 20 years, but nobody
appears to have confronted the standard vortex evidence with it. Either result
changes how that evidence should be cited, and the method transfers to any
analysis of extinct-only samples.

**Caveats:**
- The novelty is narrow and methodological. The likely venue is a methods or
  comment paper.
- It is still provisional. The search was bounded, and two close papers remain
  unchecked in full text: the final version of Nabutanyi & Wittmann (2021),
  and the methods of Drake & Griffen (2009) on passage times.

## Q2. "What is the essence of the approach?"

Barry asked for the answer under eight headings. The approach is both
simulation and real data: the real time series are tested against matched
simulations, and simulations with a known truth measure what that test can
detect.

**i) Problem.** The extinction vortex says small populations spiral down
through positive feedback such as Allee effects or inbreeding. It underpins
minimum-viable-population and genetic-rescue thinking. Its main time-series
evidence (Fagan & Holmes 2006; Williams et al. 2021) lines up extinct
populations on their extinction date and finds decline accelerating and
variability rising at the end. Looking backwards from extinction, though,
produces such patterns even without feedback, through selection plus
demographic noise.

**ii) Gap.** The relevant theory exists (Lande et al. 2003; Griffen & Drake
2009), but nobody has tested the published vortex statistics against a null
that reproduces their selection, census handling and estimator. Nor has anyone
measured what those statistics can distinguish.

**iii) Question.**
- H0: the five published statistics for Fagan & Holmes's nine populations are
  what populations without feedback would produce, when selected and analysed
  the same way. "Without feedback" means expected growth does not depend on
  abundance; there is still demographic and environmental noise.
- Secondary: how often would the test flag a departure if the truth were
  Allee feedback, external decline, observation error, or a mixture?

**iv) Data.**
- The nine Fagan & Holmes series, public (CC0) via Williams et al.
- Fagan & Holmes's published estimates.
- Williams et al.'s complete-count series, as a secondary check.
- Literature survival rates, for calibration.
- Nothing new from the field. The forward GPDD analysis is parked.

**v) Core approach.**
1. Rebuild Fagan & Holmes's estimator on the real data, reproducing their
   published slopes to three decimals.
2. For each real population, simulate many no-feedback trajectories matched to
   it: same starting size, census years, interpolations, extinction year and
   extinction rule. Calibrate the noise on features that are not being tested.
3. Run nine-population simulated datasets through the same estimator to get a
   reference distribution, then locate the observed statistics in it.
4. Run the whole pipeline on synthetic data with a known truth, to measure
   false-alarm and detection rates.

**vi) Null expectation.** Accelerating terminal decline is expected even with no
feedback. Our unmatched pilot reproduced Fagan & Holmes's acceleration slope
(+0.023 to +0.032, against their +0.034). The likely open question is the
variance slope that includes the final step (−0.047 published, against about
−0.015 under the null). That is a prior, not a result.

**vii) Pre-registered success criteria.** Validation comes first, and its
failure overrides everything.
- **False alarms:** four no-feedback scenarios, 1,000 synthetic datasets each.
  Each passes only if it has 60 or fewer false alarms, i.e. the error rate is
  demonstrably at most 8%.
- **Power:** the smallest meaningful feedback is the one that raises 10-year
  extinction risk from N=20 by at least 10 percentage points. The test must
  detect it in at least 224 of 300 datasets, i.e. power demonstrably at least
  70%.
- **Verdicts:**
  - p < 0.05 means a departure from the null, not proof of feedback.
  - p ≥ 0.05 with that power means conditional compatibility.
  - p ≥ 0.05 without that power means insufficient discrimination.
  - If no meaningful effect is attainable, no compatibility claim is made.

**viii) Other.**
- It cannot say which mechanism caused a departure.
- Nine populations may well give insufficient power, and that is a legitimate
  result.
- Astra and Fable each code the estimator and null independently, and keep a
  log of who has seen which data.
- The first tranche is capped (laptop, 30 CPU-minutes) and produces no
  empirical p-values. The likely output is a short methods paper.

*Superseded on 8 October:* Barry later lifted the compute cap in favour of
`deep-server` via tmux (message 1131).

## Q3. Phase II

Barry: "I suppose a follow-up (phase II) step might be to search for new
(post-2006) time-series that we could leverage to this purpose, to increase the
sample size beyond the canonical 9?"

Yes, Phase II makes sense, with some caveats:
- **It fits the design.** Any new series will also have been selected because
  the population went extinct. The matched null reproduces that selection, so
  a larger extinct-only sample is still a valid sample. The PRISMA search
  protocol (§5) already covers how we'd find them.
- **The supply is thin.** Williams et al. (2021) found only 35
  extinct-population series, including Fagan & Holmes's, and only 13 of those
  were complete counts. The likeliest new sources are published case studies
  of populations declining to extinction, failed reintroductions and island
  populations. The full Living Planet Database would also help, but its data
  agreement is Barry's call.
- **Size the target first.** Phase I's detection-rate results will tell us how
  many populations are needed before compiling. That way Phase II has a
  concrete target rather than "as many as possible".
- **Lab experiments are a bonus.** Replicated microcosm extinctions, like the
  *Daphnia* experiments, could add large samples where the cause of decline is
  known.
