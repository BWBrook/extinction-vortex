# Project (working name)

A joint scientific project led by Barry W. Brook, with Astra (OpenAI, through
Codex) and Fable (Anthropic, through Claude) as advisors, critics, reviewers and
implementers. **The research topic has not been selected.**

Setup began on **2 October 2026, Hobart time**. The launch prompt describes the
frontier-model experiment as of September 2026; records use actual activity dates.

## Mandate

Produce novel, useful and defensible science with a light touch of human input.
Barry's attention is scarce. The agents should handle routine work, disagree
productively, and bring him decisions where scientific judgment changes the
direction. Topic selection is the first such decision. Work allocation between
Astra and Fable is by mutual consent.

The project may draw on ecology, conservation, extinction, global change or
related modelling. Barry's [UTAS profile](https://discover.utas.edu.au/Barry.Brook)
provides background on his population ecology, conservation and computational
research. This is a starting point for ideas, not a restriction to one method or
a requirement that the scientific topic concern AI.

Barry has authorized repository setup, ideation, correspondence, and commits and
pushes when appropriate, preferably as coherent bundles. A research programme
will follow his topic decision. Publication, submission, substantial resource
commitments and changes outside the agreed scope remain separate decisions.

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

Barry's 5 October preference makes the vortex proposal the current focus for
protocol development. The [working protocol](notes/vortex_protocol.md) combines
an empirical reanalysis with simulation validation and a conditional forward
extension. It is a draft, not a frozen registration. The immediate endpoint is
an integrated protocol and concise topic decision brief; research execution
follows that decision.

The [two-page decision brief](notes/vortex_decision_brief_20261005.pdf)
([editable source](notes/vortex_decision_brief.md)) is finalized after Fable's
review. Astra recommends selecting the question and authorizing source checks,
reconstruction and a capped local feasibility pilot. The
[draft 0.3 review](notes/astra_protocol03_review_20261005.md) records the remaining
inference and validation work before a production freeze. Barry's decision is
next; no research tranche is authorized by the brief.

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
- No GitHub or publication remote is configured at setup. The temporary folder
  name can change after topic selection.
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
- [The working vortex protocol](notes/vortex_protocol.md), draft 0.3a, contains
  Fable's proposed formal core, Astra's compilation/exposure/roles sections,
  and the outstanding review disposition. Its [exposure log](notes/vortex_exposure_log.csv) distinguishes
  known outcomes, computational access and reported limits on inspection.
- [The prior-work search record](notes/vortex_prior_work_search_20261005.md)
  preserves actual queries, retrieved identifiers and coverage limits.

- [Pre-approval Q&A](notes/vortex_study_summary_20261008.md) records Barry's final
  questions (novelty, approach, Phase II) and Fable's answers before approval on 8 October.

The referenced Mac folder was not present at the expected path during setup;
Astra established it and synchronized the initial commit with the WSL checkout.
