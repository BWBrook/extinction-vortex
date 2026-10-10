# Extinction-vortex selection study (working name)

A joint scientific project led by Barry W. Brook, with Astra (OpenAI, through
Codex) and Fable (Anthropic, through Claude) as advisors, critics, reviewers and
implementers. **Barry selected the extinction-vortex question and authorized
the first execution tranche on 8 October 2026.** The production design is not
frozen and empirical conditional-null tests have not begun.

Setup began on **2 October 2026, Hobart time**. The launch prompt describes the
frontier-model experiment as of September 2026; records use actual activity dates.

## Mandate

Produce novel, useful and defensible science with a light touch of human input.
Barry's attention is scarce. The agents should handle routine work, disagree
productively, and bring him decisions where scientific judgment changes the
direction. Topic selection was the first such decision. Work allocation between
Astra and Fable is by mutual consent.

The selected study asks how much of the observed pattern in extinction-bound
population trajectories can arise under matched outcome selection without
abundance-dependent demographic feedback. The initial slates preserve the wider
ecological and modelling questions considered before selection.

Barry has authorized setup, correspondence, bundled commits and pushes, and the
source/reconstruction/development tranche. His 8 October instruction sends
serious compute to deep-server in tmux; the earlier numerical laptop-pilot cap
does not constrain that authorized remote development. Publication, submission
and changes outside the agreed study remain separate decisions.

## First exchange

The initial procedure, accepted by Fable with amendments, is:

1. Each agent prepares three initial questions before reading the other's slate,
   where practical. This is an attempt to reduce anchoring, not a blinded test.
2. Exchange ideas and challenge the closest prior work, the proposed inference,
   evidence access, feasibility and scientific value. Identify what would make
   each idea worth abandoning. Preserve disagreements that remain consequential.
3. Perform bounded literature and feasibility checks for the strongest options.
4. Give Barry at most three finalists, a recommendation, the strongest objection,
   and a finite first study with a meaningful stop condition.

On 5 October, Astra accepted Fable's amendments 1–3: reciprocal novelty checks,
early tests of abandonment conditions, and an eventual decision brief of at most
two pages, with separate questions requiring Barry's judgment. The fourth
amendment concerns prespecification, holdouts and separate core implementations
in the research phase. Astra proposed distinguishing exposed pilot outcomes
from untouched validation data and using separate implementations where they
test consequential components. Agreement between implementations would not
validate shared scientific assumptions. Fable accepted both qualifications on 5 October (message 988). See
discussion 70 and [Astra's first reciprocal review](notes/astra_round1_review_20261005.md).

Assess candidates qualitatively on scientific importance, defensible novelty,
discriminating evidence, feasible execution and value of a null or contrary
result. Do not turn subjective scores into spurious quantitative precision.

Barry's 5 October preference made the vortex proposal the focus for protocol
development. The [working protocol](notes/vortex_protocol.md) combines an
empirical reanalysis with simulation validation and a conditional forward
extension. It remains a draft; Part 2 and the genetic extension are parked.

The [two-page decision brief](notes/vortex_decision_brief_20261005.pdf)
([editable source](notes/vortex_decision_brief.md)) preserves the proposal Barry
approved on 8 October, with his later compute clarification. The
[draft 0.3 review](notes/astra_protocol03_review_20261005.md) records the accepted
repairs needed before production. Fable owns the next formal protocol revision.

## First execution results

Astra froze its [estimator and null sampler](analysis/astra/stage_b/README.md)
before opening Fable's code, then ran 54 declared reconstruction fits on
deep-server. Synthetic likelihood, empirical-Bayes and generator checks passed.
The [post-freeze comparison](analysis/astra/stage_b/comparison_v0/) confirms
matching inputs and likelihood calculations between implementations.
**Stage B has not passed:** no declared candidate reproduces all four published
slopes at their stated precision; scaling and T5 remain unresolved.

The [source audit](notes/astra_source_audit_20261008.md) resolves the crane's
final-count convention and verifies the official winter sequence, identifies
three wild-dog fills absent from the author-distributed data, and records
unresolved census and survival-prior mappings. Raw values are preserved.
Fable has frozen its second M0 implementation and produced protocol 0.6.
[Astra's 0.6 review](notes/astra_protocol06_review_20261009.md) accepts the
structural null definition, descriptive second-bank comparison and improved
provenance. AR plus catastrophes is the only tested candidate satisfying the
then-current bank-budget rule near observed calibration summaries. Barry has
now selected it as the primary development candidate, as recorded below.
Fable's draft 0.7 completes the
[discrimination screen](analysis/fable/calibration/discrimination_v1/NOTE.md)
with calibration failures retained and measures
[outer-dataset coverage](analysis/fable/calibration/coverage_v1/NOTE.md).
- Raw detections were 21/30 versus 29/30 in two matched model-and-test designs;
  both generator and reference changed, so this does not isolate a reference effect.
- The hard tolerance would need about 100× banks to approach the planning
  shortfall target. Astra accepts fixed-K calibration with proposed 10× banks
  for development; larger-bank support remains projected and needs validation.
- The heavy-tail comparator is retired.

Barry [adopted the four-statistic target](notes/vortex_target_amendment_20261009.md)
through Decision Inbox on 9 October: **RI primary, random-intercept-and-slope
mandatory sensitivity, T5/scaling descriptive**. The wide prior (b) is proposed
for primary validation. The [original proposal](notes/vortex_amendment_proposal_20261009.md)
preserves the earlier disagreement. Fable incorporated the decision in draft 0.5
and responded to the 0.6 review in draft 0.7. Astra's
[0.7 review](notes/astra_protocol07_review_20261009.md) supported the primary-null
choice. Barry subsequently [adopted ar_cat as the primary development candidate,
with iid as mandatory sensitivity](notes/vortex_null_amendment_20261009.md),
through the [verified response](docs/decisions/d36e602c-1c18-45fe-83ce-90adda12d313.md)
submitted at 14:51:05 AEDT on 9 October. This selects the candidate for the next
development and validation design; production settings and resources remain
unfrozen. Fable's draft 0.8 sets out the validation design on 10× development
banks.
- [Development β_min](analysis/fable/calibration/dev_design_v1/NOTE.md) is
  Δ10 = 0.075.
- A [power screen](analysis/fable/calibration/power_screen_v1/NOTE.md) found
  1/30 detections at β_min and 18/30 at Δ10 = 0.5. With nine series, a
  non-rejection would therefore most likely be O3 (insufficient
  discrimination).
- [Astra's 0.8 review](notes/astra_protocol08_review_20261010.md) accepts continued
  development.
- Draft 0.9 then adds the M_D and M_O generators with limiting-case tests, the
  stress-check sampling law, and a full execution inventory of about 3,300
  core-hours.
- It also adds a draft [freeze package](notes/vortex_freeze_package_20261010.md).
  The §4.1 development screens and the designated banks are running on
  deep-server.
- [Astra's 0.9 review](notes/astra_protocol09_review_20261010.md) accepts the
  proposed priors and sampling laws. The executable stress sampler, final
  aggregation/gate checks and selected-draw provenance remain to be completed;
  the cost total remains a projection. Fable supplies the completed package next.
Synthetic development continues within existing authority; no empirical p-values
precede the validation freeze.

## How the collaboration will be assessed

Preserve initial proposals, consequential criticisms, changes caused by those
criticisms, rejected ideas, observed human interventions and available model/run
metadata in the board and Git history. Record uncertainty or unavailable metadata
honestly. Participant names do not uniquely identify model versions.

Different providers do not guarantee independent errors. Agreement between the
agents is not empirical validation. Check central claims against sources,
mathematics, controls and reproducible evidence. This one project can document a
collaborative case; it cannot by itself establish the causal benefit of two
models over one or explain differences by their training backgrounds.

## Shared state

- Canonical shared checkout: `/Users/bwbrook/papers/project` on the Mac mini.
- Astra's current WSL checkout: `/home/bwbrook/papers/project`.
- Correspondence section: `project`; launch discussion: **70**.
- No GitHub or publication remote is configured. The agents agreed the proposed
  name `extinction-vortex-selection`; existing paths remain during the active
  handoff, pending a coordinated move.
- [STATUS.md](STATUS.md) records whose response is next and retrieval checkpoints.
- [AGENTS.md](AGENTS.md) records the operating instructions for both agents.
- [Astra's initial slate](notes/astra_initial_slate.md) contains proposals and a
  limited prior-work screen. Fable may prepare its own slate before opening it.
- [Fable's initial slate](notes/fable_initial_slate.md) was drafted before
  opening Astra's. Its simulation checks are in [notes/checks/](notes/checks/).
- [Astra's first reciprocal review](notes/astra_round1_review_20261005.md) records
  the source audit, methodological objections and current candidate dispositions.
- [Fable's round-2 response](notes/fable_round2_response_20261005.md) records the
  corrected vortex specification, the T3 data report ([notes/t3/](notes/t3/)),
  Barry's 5 October input and the proposed pre-registration plan.
- [The working vortex protocol](notes/vortex_protocol.md), draft 0.9, contains
  Fable's proposed formal core, Astra's compilation/exposure/roles sections,
  and the outstanding review disposition. Its [exposure log](notes/vortex_exposure_log.csv) distinguishes
  known outcomes, computational access and reported limits on inspection.
- [The prior-work search record](notes/vortex_prior_work_search_20261005.md)
  preserves actual queries, retrieved identifiers and coverage limits.

- [Pre-approval Q&A](notes/vortex_study_summary_20261008.md) records Barry's final
  questions (novelty, approach, Phase II) and Fable's answers before approval on 8 October.

The referenced Mac folder was not present at the expected path during setup;
Astra established it and synchronized the initial commit with the WSL checkout.
