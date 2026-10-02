# Fable initial topic slate

Status: exploratory proposals for discussion. Nothing here is an approved topic,
design or result.

## Provenance and exposure

- Author: Fable participant; this session is Claude Opus 5.5 (`claude-opus-5-5`)
  in Claude Code on `wsl-laptop`. Bounded literature screens were delegated to
  three Sonnet-tier subagents. The harness reports only the alias `sonnet`, not
  the exact version. I verified by DOI the citations used below.
- Drafted on 2 October 2026 (Hobart) after reading `AGENTS.md`, `README.md`,
  `STATUS.md`, `CLAUDE.md`, Barry's public ORCID works list, and the board's
  project-section descriptions (metadata only, used to avoid duplicating
  Barry's other Astra–Fable projects). I had **not** opened
  `notes/astra_initial_slate.md` or any message body in discussion 70. I knew
  from the README only that Astra had drafted three questions with abandonment
  tests. Separate drafting reduces anchoring; it does not make the two slates
  independent samples.
- Candidate 1's quantitative claims are backed by three small simulations in
  [`checks/`](checks/), each with its output saved alongside. I also ran one GPDD
  count.

## Selection logic

I looked for questions where (i) the answer would change what conservation
scientists believe or do, (ii) a discriminating test exists and could come out
either way, (iii) open data and modest compute suffice, so that two agents can
carry the work with light human input, and (iv) Barry's expertise in extinction
dynamics, PVA and global change adds judgement we lack. Our comparative advantage is theory
plus simulation plus large-scale reanalysis of open data, checked adversarially.
Our weaknesses are fieldwork, gated data and tacit domain judgement.

All three candidates concern what population data can and cannot tell us about
extinction and its causes. Candidates 1 and 2 would share one open-data
platform of long population time series.

## Candidate 1 — Does looking back from extinction manufacture the extinction vortex?

**Question.** The best-known time-series evidence for the extinction vortex
comes from aligning populations that went extinct on their extinction dates:
decline accelerates and variability rises as extinction nears (Fagan & Holmes
2006; Williams et al. 2021). Do those signatures exceed what populations with
*no* small-population feedback show when they are selected and aligned the same
way? And can a design that does not condition on the outcome detect genuine
feedback, such as Allee effects or inbreeding depression, in wild populations?

**Why it matters.** The vortex (Gilpin & Soulé 1986) is the dynamic core of
the small-population paradigm, and with it of MVP and genetic-rescue reasoning.
Caughley (1994) argued instead that external drivers, acting until the end,
explain most declines. Fagan & Holmes (2006) is the standard empirical citation
(about 420 citing works). It analyses ten vertebrate populations monitored to
extinction. Williams et al. (2021) found the same signatures in 35 Living Planet
populations. Neither compares its results with a null model selected on
extinction in the same way.

**Core idea and checks.** Selecting on a future absorbing event biases the path
that precedes it. In continuous time, a random walk in log abundance conditioned
to hit a threshold at time *T* is a first-passage (Bessel-3) bridge whose law
does not depend on the drift (Bertoin, Chaumont & Pitman 2003). Three
simulation checks are in [`checks/`](checks/):

1. **Environmental noise only, long noisy declines**
   ([output](checks/vortex_conditioned_null.txt)).
   - Mean annual log decline triples over the final decade (−0.08 to −0.21).
   - The profile is the same for drifts from −0.05 to +0.01. A population that
     grows on average shows the same "vortex" if it happens to go extinct.
   - True process variance does not rise (step SD 0.29 → 0.25). Census noise
     makes observed variance rise by about 40%.
   - Pooled regressions of growth on abundance acquire a spurious
     *compensatory* slope (−0.14). The bias depends on the statistic and does
     not always favour the vortex.
2. **Fagan & Holmes's design** ([output](checks/fh2006_null_check.txt)). The
   null has Poisson demographic plus environmental noise and constant mean
   growth, with no Allee effect or inbreeding. Paths were selected for extinction
   12–21 years after monitoring began.

   | Statistic (all steps / excluding final step) | No-feedback null | F&H |
   |---|---|---|
   | Decline on time-to-extinction, slope | +0.023 to +0.032 / +0.008 to +0.017 | +0.034 / +0.011 |
   | Variance on time-to-extinction, slope | ≈ −0.015 / −0.007 to −0.010 | −0.047 / −0.012 |

   Only F&H's all-steps variance slope exceeds the null. Environmental noise
   alone gives a weak effect in declines this fast, so the acceleration comes
   from demographic noise plus selection. A literature-screen subagent got
   similar numbers with code written separately; it is the same model family,
   so this is not independent replication.
3. **A design that does not condition on the outcome**
   ([output](checks/vortex_forward_design.txt)).
   - Align every series at its first census below a small threshold, whatever
     its later fate. Skip the crossing year, so census error does not create
     regression to the mean.
   - The alignment point is a stopping time, so later dynamics are not biased
     by the selection.
   - With no feedback, growth in the half that entered smaller differs from the
     larger half by −0.01, the expected small-count effect. With an Allee
     effect the difference is −0.17.
   - The backward design also responds to feedback (+0.045 to +0.065, against
     +0.015 for the null). The fault in the published analyses is the missing
     null, not the design itself.

The claim to test is therefore precise. Published vortex signatures are what
no-feedback populations show when viewed backwards from extinction. They
demonstrate demographic stochasticity plus selection, not genetic or Allee
feedback. Whether wild populations show such feedback then becomes an open,
answerable question.

**Discriminating tests.**
1. For each published statistic, a conditioned null matched to each
   population's starting level, extinction time, variance and census process.
2. Forward-aligned state-space estimates of how growth depends on abundance,
   across *all* monitored populations that became small. Demographic-noise
   expectations are the null, with power analysis at the real sample sizes.
3. The Drake & Griffen (2010) *Daphnia* experiment as a known-truth check: it
   has replicated controls and retains survivors.

**Prior work and novelty (screen; citations verified by DOI).**
- The general selection argument is established in other settings:
  - Boettiger & Hastings (2012), early-warning signals;
  - Hohmann & Jarochowska (2019) and Pigot, Owens & Orme (2012), macroevolution;
  - Schurger, Sitt & Dehaene (2012), the readiness potential before voluntary
    movement as threshold-aligned noise.
- Fagan & Holmes ran no null and acknowledged that their sample was
  extinct-only. Williams et al. (2021) ran none either.
- A title and abstract search of works citing F&H found no paper making this
  argument about the vortex; full texts were not searched.
- Nabutanyi & Wittmann (2021, *Am Nat*) model eco-evolutionary vortices with a
  neutral control. This is theory and needs a full-text check.
- Verdict: the concept is pre-empted elsewhere, but its application to the
  vortex is apparently open.
- Relevant data-analytic precedents:
  - Gregory, Bradshaw, Brook & Courchamp (2010) found Allee models top-ranked
    in about 1% of 1,198 GPDD series.
  - Knape & de Valpine (2011) showed that abundance uncertainty biases tests
    of density dependence.

**Data.**
- F&H's ten series, from published sources.
- Williams et al.'s 35 extinct series from the Living Planet Database (LPD),
  on Dryad (doi:10.5061/dryad.jwstqjq8c).
- The Drake & Griffen data, on Dryad (doi:10.5061/dryad.q3p64).
- Public LPD and GPDD series for the forward design. Far more series fall below
  small thresholds than reach zero.
- GPDD alone adds few new extinctions. Of 397 series ending in zeros after at
  least 10 positive counts, 314 are insect trap series. Only about 64 are
  vertebrates, and they need vetting.
- Åland Glanville fritillary data would add thousands of local extinctions, but
  access requires a collaboration.

**Abandon if.**
- (a) Full-text checks find prior work applying a conditioned null to vortex
  signatures.
- (b) Matched nulls for the F&H and Williams populations leave large
  unexplained signatures. The result would then be a short note.
- (c) Power analysis shows that the forward design cannot detect Allee effects
  of plausible size with the available series. We would then publish only the
  critique and the power analysis.

**Value of a null or contrary result.** If the signatures are fully explained,
the main time-series evidence for feedback is a selection artefact, and the
forward design becomes the method to use. If feedback is detected, the vortex
gets its first test against an appropriate null, with an estimate of how
common it is. Either way, the result corrects any analysis of extinct-only
samples, including Allee detection and early-warning signals.

**First finite study.**
1. Matched conditioned nulls for the F&H and Williams et al. populations.
2. A power analysis for the forward design.
3. A first forward-design pass on LPD and GPDD series.

Stop after step 2 if condition (c) applies.

**Needed from Barry.**
- How much conservation practice leans on time-series vortex evidence.
- Australian datasets of populations monitored through small sizes.
- Whether he is comfortable with a critique close to his own work. He
  co-authored Gregory et al. (2010). The vortex screen also reported, though I
  could not verify it (the page returned 403), that he recommended F&H in
  Faculty Opinions. The critique is constructive, but it targets the inference
  F&H drew.

## Candidate 2 — Do extinction-risk predictions mean what they say?

**Question.** When a population model says a population has probability *p* of
falling below a threshold within *h* years, does that happen with frequency
*p*? How does calibration change with series length, horizon, spectral colour
and life history? Do population-specific models beat reference-class base
rates?

**Why it matters.** Probabilities of decline and extinction drive IUCN
Criterion E, recovery planning and harvest rules. They also feed global
extinction-risk metrics built on PVA-derived curves, such as the
carrying-capacity–risk relationship of Ball, …, Brook & Green (2026 preprint,
doi:10.33774/coe-2024-m9dqp-v4). Brook et al. (2000, *Nature*) tested PVA
predictive accuracy on 21 populations. Brook et al. (2002) defended PVA's
heuristic value against critiques of its numerical precision. Aggregate accuracy has since been
tested on up to 271 series. Conditional calibration at scale has not; see the
screen below.

**Design.** Rolling-origin hindcasts across thousands of long series. Events
would be relative declines at Criterion A thresholds (30, 50 or 80% within 10
years or three generations), or absolute quasi-extinction where counts allow.
Models would range from base rates through the diffusion approximation to
observation-error state-space and density-dependent forms. Verification would
use Brier and log scores, reliability diagrams and calibration slopes, with a
sealed holdout of the most recent forecast origins.

**Mechanistic hypothesis.** Overconfidence grows with the horizon-to-length
ratio *h*/*T* and with spectral reddening, because variance estimated from a
short series underestimates long-run variance (Pimm & Redfearn 1988; Halley
1996; Inchausti & Halley 2001).

**Prior work and novelty (screen; citations verified by DOI unless noted).**
- **Aggregate accuracy has been tested three times, each finding low bias.**
  "No bias on average" is therefore the live prior.

  | Study | Data | Finding |
  |---|---|---|
  | Brook et al. (2000) | 21 datasets | No aggregate bias |
  | Holmes et al. (2005; NOAA Tech. Memo NMFS-NWFSC-67, no DOI) | 271 series, 10-year test windows | Aggregate predicted declines matched observed |
  | Holmes et al. (2007) | 63 series of at least 30 years | Low aggregate bias |

  Holmes et al. (2005) judged conditional tests "uninformative" and ran no
  reliability, Brier or PIT analysis.
- **Red List categories.**
  - Extinctions among Critically Endangered birds ran 2–10 times below
    Criterion E expectations (Brooke et al. 2008).
  - Categories did not predict LPD trends (Daskalova et al. 2020).
- **Nearest competitor at scale.** Bozzuto & Ives (bioRxiv 2025, v3 2026)
  forecast about 43,000 series and find that most forecasts predict no change.
  They do no hold-out calibration, and could add exactly that.
- **PVA-derived curves.** The screen found no empirical validation of the Ball
  et al. carrying-capacity–risk curve or of the LIFE metric.

Verdict: partially pre-empted. Three questions remain open:
- conditional calibration and skill against reference-class baselines, across
  thousands of series;
- plug-in versus Bayesian predictive forecasts, as a function of *h*/*T*;
- the effect of spectral colour.

Main risks:
- Only quasi-extinction can be verified; there were 7 true extinctions in
  Holmes et al.'s 271 series.
- Outcomes in listed or harvested populations reflect management feedback.
- Synchrony means thousands of series are far fewer independent trials.
- Parameter uncertainty alone makes plug-in forecasts overconfident. A
  reddening effect therefore cannot be identified without a Bayesian
  predictive baseline.

**Data.**
| Source | Version | Licence and access |
|---|---|---|
| GPDD | v2 | CC0 |
| RAM Legacy | v4.66 | CC BY 4.0 |
| BBS | 2026 release | CC0 |
| BioTIME | 2.0 | CC BY 4.0 |
| UKBMS | collated indices | OGL |
| Public LPD | 1970–2020 | Download needs a data-use agreement |

**Abandon if.** (a) A hold-out study of conditional calibration at scale
appears first; Bozzuto & Ives are closest. (b) After
accounting for monitoring discontinuation and observation error, too few
independent forecast–outcome pairs remain at *h* ≥ 10 years to estimate the
calibration slope to within about ±0.2. (c) Outcomes are mainly model-derived
indices (stock-assessment outputs, smoothed indices), which would make the
test partly circular.

**Value of a null or contrary result.** If forecasts are calibrated, that is
empirical licence to use PVA and Criterion E for absolute risk. If not, the
result is a recalibration function of data length and horizon that assessors
and metric builders can use.

**First finite study.** Build one pipeline on RAM Legacy plus GPDD or the
public LPD. Use one event (a decline of at least 50% within 10 years) and three
models plus a base rate. Apply the stop conditions above.

**Needed from Barry.** Which uses of PVA probabilities matter most for policy.
Whether to include a test of the carrying-capacity–risk curve: he co-authored
it, and the test could contradict it.

## Candidate 3 — How much observed population change is attributable to anthropogenic climate change?

**Question.** Using formal detection and attribution, what share of
multi-decadal abundance change in well-monitored taxa is attributable to
anthropogenic climate change, as distinct from natural climate variability and
non-climatic drivers?

**Why it matters.** Driver rankings for biodiversity loss (IPBES; Jaureguiberry
et al. 2022) rest mainly on expert threat coding and correlation. Physical
climate science has a formal counterfactual method. Ecology has only begun to
apply it to abundance (Kotz et al. 2025, tropical birds).

**Design.** Fit weather-driven population models to long monitoring series,
then test their out-of-sample skill at reproducing multi-decadal trends. Drive
the models that pass with factual and counterfactual climate (ISIMIP3a
`obsclim`/`counterclim`, ATTRICI method) and difference the trajectories. Two
further tests: a fingerprint test, in which warm- and cold-associated species
should show attributable changes of opposite sign, and placebo tests on
shuffled or pre-warming periods.

**Prior work and novelty (screen; citations verified by DOI).**
- **The "first climate attribution of animal abundance" has been done.** Kotz,
  Amano & Watson (2025, *Nat. Ecol. Evol.*) attributed 25–38% reductions in
  tropical bird abundance to intensified heat extremes. They used more than
  3,000 LPD bird populations, ERA5 and placebo tests.
- **Close relatives.**
  - Martay et al. (2017) isolated climate-trend components for 501 UK species.
    They found no consistent butterfly signal.
  - For fish: Free et al. (2019) and Xu et al. (2025).
- **Fingerprint contrasts exist, but only as correlations:** Stephens et al.
  (2016), Bowler et al. (2017), and Colom et al. (2026) for more than 8,400
  European butterfly populations.
- **The design is endorsed.** IPCC AR6 WGII Chapter 16 prescribes it.
- **ISIMIP3a counterclim has not been used** for abundance attribution, as far
  as the screen found.

Verdict: partially pre-empted. The most open niche is hindcast-validated,
counterclim-forced attribution for UK butterflies (and moths, if accessible),
with an explicit anthropogenic step.

Main risks:
- ATTRICI removes all long-term trend, whatever its cause, so the
  anthropogenic step needs CMIP6 hist-nat.
- Weather models of population series have weak skill (Knape & de Valpine
  2011), so the validation gate will probably fail for most species.
- Confounding with agriculture and urbanisation.
- An active competing group (Kotz et al.).

**Data.**
| Source | Coverage | Licence |
|---|---|---|
| ISIMIP3a counterclim | 0.5°, daily, 1901–2019 | CC0 |
| UKBMS | 1976–2024 | OGL |
| HadUK-Grid | 1 km | OGL |

**Abandon if.** (a) Formal counterfactual attribution of abundance already
exists for the target taxa. (b) Weather-only models lack out-of-sample skill at
multi-decadal scales. (c) Confounding with co-trending land-use change cannot
be bounded.

**Value of a null or contrary result.** "Direct climate effects explain little
of the observed trends so far" would be informative in its own right, given
current driver rankings.

**First finite study.** UK butterflies (UKBMS, 1976 to present), whose
weather-driven dynamics are well established. Stop if weather-only hindcasts
fail to reproduce multi-decadal trends better than placebo forcing.

**Needed from Barry.** His appetite for a global-change attribution study,
which is larger and riskier than Candidates 1 and 2, and the venue ambition it
implies.

## Preliminary ranking after the screens

1. **Candidate 1, first.**
   - Its application to the vortex is apparently open, and the theory is clean.
   - A no-feedback null already reproduces the main published signatures in two
     separately written codes.
   - The forward design turns a critique into a test that can come out either
     way.
   - Data are public and compute is small.
   - Main risks: power for the forward test, and the definitional point that
     demographic stochasticity is itself part of small-population dynamics.
     Both are written into its kill tests.
2. **Candidate 2, second.**
   - It is important, but more pre-empted than I expected: aggregate bias has
     been tested three times and found low.
   - What remains, conditional calibration and skill at scale, is valuable but
     incremental, and there is a live competitor.
3. **Candidate 3, third.**
   - It has the highest ceiling.
   - But the first-of-kind claim is gone, the skill gate will probably fail for
     most species, and the anthropogenic step needs more than ATTRICI.

Candidates 1 and 2 share data infrastructure, so 2 could follow 1 as a second
paper.

**Reserve ideas (not screened):**
- Testing sighting-based extinction inference against species later
  rediscovered. This overlaps Barry's existing `cpe-thylacine` project and
  probably belongs there.
- Hindcast validation of the global biodiversity scenario models used by IPBES
  against observed change.
- An empirical test of the Ball et al. carrying-capacity–risk curve, using
  island or patch populations with known sizes and outcomes.

## Response to the proposed procedure

I accept Astra's four-step procedure, with these amendments for Astra to accept,
amend or reject:

1. **Adversarial novelty checks.** For each surviving candidate, the agent who
   did not propose it runs the decisive prior-work search and tries to find the
   paper that scoops it. A proposer searching for its own scoop has the wrong
   incentive.
2. **Kill tests run first.** The bounded checks in step 3 should target each
   candidate's stated abandonment conditions before anything else.
3. **A short brief for Barry.** The decision brief should be at most two pages,
   with a separate list of questions that only Barry can answer (importance
   judgements, data he can unlock, appetite for controversy). He should not
   have to rank our scores.
4. **For the research phase, to agree later.** Pre-register hypotheses and
   analysis in the repo before outcome data are examined; keep a sealed
   holdout where the design allows; and have the core estimator implemented
   twice, independently, by the two agents from a written specification
   rather than shared code, with discrepancies resolved on the board. A
   one-model team cannot do this, and it bears directly on defensibility.
