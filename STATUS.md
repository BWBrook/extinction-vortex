# Current state

Updated: 5 October 2026, 13:00 Hobart (AEDT), by Fable.

**Stage:** proposed; setup and topic ideation. No research topic, design or
scientific claim has been approved.

**Barry, 5 October, in chat to Fable:** a provisional preference for the vortex
idea, together with a request for a careful, PRISMA-style pre-registered plan.
His exact words are quoted in discussion 70, message 990, and in
[Fable's round-2 response](notes/fable_round2_response_20261005.md) §1. This is
not a topic selection.

**Next response:** Astra. Astra should accept or contest:

- the corrected Fable-1 question and minimal specification (988);
- the T3 data and eligibility report and the T2 statement (989);
- the pre-registration plan, section allocation and stage order (990).

No decision is requested from Barry yet.

## Completed by Astra

- Verified Correspondence API v2 under the Astra identity and read the interface
  and recovery guidance. No existing active project section matched this repo.
- Created section `project` and launch discussion 70, beginning with message 826.
- Recorded the mandate and proposed exchange procedure; drafted three candidate
  questions with a limited primary-source screen and explicit abandonment tests.
- Prepared the shared Mac mini checkout and matching WSL foundation.
- Read Fable's slate, messages 827–832, code and saved exploratory outputs.
- Completed an initial bounded T1 source audit and a code/method review,
  recorded in [the first reciprocal review](notes/astra_round1_review_20261005.md).
  The final Nabutanyi–Wittmann full text and a systematic citation census remain
  unchecked; novelty is provisional.
- Posted procedural/allocation response 956, methodological objections 958,
  and portfolio response 959. Preserved both original slates and Fable's checks.
- Provisional disposition: revised Fable-1 first, Fable-2 an independent
  fallback, Astra-C reserve; park Astra-A/B and Fable-3. Fable has not yet
  responded to this revised assessment.

## Completed by Fable

- Verified API v2 and the Fable identity. Read the board interface and recovery
  docs on the Mac mini.
- Wrote [notes/fable_initial_slate.md](notes/fable_initial_slate.md) before
  opening Astra's slate or any discussion-70 body; committed as `d417fe9`.
  - Its three candidates: the extinction-vortex conditioning artefact,
    calibration of extinction-risk forecasts, and climate attribution of
    abundance.
  - Each has a bounded prior-work screen (citations verified by DOI),
    abandonment tests and a first finite study.
  - Supporting simulations and outputs are in [notes/checks/](notes/checks/).
- Posted the slate and procedure response (828), a review of Astra's slate (829)
  and findings on A, B and C (830–832).
- Fable's preliminary ranking: Fable-1 (vortex) first. Fable-2 could follow it
  as a second paper on the same data. Astra-C is the strongest of Astra's three.
- Round 2 (5 October): read 956–959 in full and Astra's review. Accepted all
  four objections, the symmetric continuation rules and both qualifications to
  amendment 4. Set out a corrected Part 1/Part 2 specification with staged
  gates, completed T3 and a short T2, and proposed a PRISMA-style
  pre-registration with a section allocation.
  - Recorded in [notes/fable_round2_response_20261005.md](notes/fable_round2_response_20261005.md),
    with the T3 inventory and GPDD script in [notes/t3/](notes/t3/).
  - Posted 988 (audit response and specification), 989 (T3 and T2) and 990
    (Barry's input and plan).
  - `notes/checks/vortex_forward_design.py` is withdrawn as evidence: it is
    outcome-selected. It stays as a superseded pilot.

## Pending

1. Astra responds to 988–990.
2. If agreed, draft `notes/vortex_protocol.md`. Proposed split: Fable writes
   §§1–4 and 7 (aims, estimands, generative models, simulation validation and
   gates, analysis plan). Astra writes §§5–6 and 8 (PRISMA compilation,
   exposure log and sealing, roles and independent implementation). Each
   reviews the other's sections.
3. Astra drafts the two-page brief summarising the protocol, the fallbacks
   (Fable-2, Astra-C) and the questions only Barry can answer (LPD data
   agreement, his comfort with a critique near his own work, importance, the
   founder-size module). Fable reviews it. Barry then selects, redirects or
   rejects; rename the repo once the topic is clear.
4. Proposed stage order, once a topic is authorised:
   - reproduce the published numbers;
   - run the Part 1 matched nulls and confusion matrix;
   - run the Part 2 synthetic identifiability and power gate;
   - only if the gate passes, run the PRISMA compilation and a sealed forward
     analysis.

## Correspondence checkpoint for this Astra task

- Project: `project` (active view).
- Discussion: 70; launch message: 826.
- Last full retrieval `next_after`: **959**; exhausted `through`: **959**.
- Explicit acknowledgement: through message **959** in discussion 70.
- Next retrieval: omit `through` to capture new messages, and use `after=959`.

## Correspondence checkpoint for this Fable task

- Project: `project` (active view); discussion 70.
- Read 826–827, posted 828–832; read 956–959, posted 988–990.
- Last full retrieval `next_after`: **987**, a global boundary with no project
  messages between 959 and 987. Fable's own posts run through 990.
- Explicit acknowledgement: through message **990** in discussion 70.
- Next retrieval: use `after=990` and omit `through`.

## Coordination note

Both agents currently work in the same WSL checkout,
`/home/bwbrook/papers/project`. Commit before handing off, and do not edit the
other agent's files. The Mac mini checkout is canonical. Fable synchronises its
commits there by pushing to a temporary branch and fast-forwarding `main`, after
checking that the Mac working tree is clean. There is no GitHub remote yet.
