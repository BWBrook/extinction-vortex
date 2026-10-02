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

## Proposed first exchange

This procedure is Astra's proposal pending Fable's response:

1. Each agent prepares three initial questions before reading the other's slate,
   where practical. This is an attempt to reduce anchoring, not a blinded test.
2. Exchange ideas and challenge the closest prior work, the proposed inference,
   evidence access, feasibility and scientific value. Identify what would make
   each idea worth abandoning. Preserve disagreements that remain consequential.
3. Perform bounded literature and feasibility checks for the strongest options.
4. Give Barry at most three finalists, a recommendation, the strongest objection,
   and a finite first study with a meaningful stop condition.

Assess candidates qualitatively on scientific importance, defensible novelty,
discriminating evidence, feasible execution and value of a null or contrary
result. Do not turn subjective scores into spurious quantitative precision.

The immediate endpoint is a topic decision brief. No substantive analysis or
production compute is required to complete the setup and initial ideation.

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

The referenced Mac folder was not present at the expected path during setup;
Astra established it and synchronized the initial commit with the WSL checkout.
