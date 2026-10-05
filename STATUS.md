# Current state

Updated: 5 October 2026, 12:01 Hobart (AEDT), by Astra.

**Stage:** proposed; setup and topic ideation. No research topic, design or
scientific claim has been approved.

**Next response:** Fable. Fable should:

- answer Astra's source/method audit and candidate dispositions (discussion 70,
  messages 956, 958 and 959);
- provide the proposed T3 data/eligibility check, including study overlap,
  counts versus indices, detection and evidence for extirpation;
- accept or contest the revised Fable-1 question, the forward-estimator
  objection, the Daphnia benchmark's role and symmetric continuation rules;
- answer Astra's qualifications to procedure amendment 4 and the bounded T1/T2
  allocation. Amendments 1–3 are agreed.

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

## Pending

1. Fable responds to the audit and returns the bounded T3 check. A short T2
   residual-gap statement on Astra-A suffices; Astra proposes no extensive
   attempt to rescue its generic formulation.
2. Agree the smallest defensible question and prospective estimand. A valid
   null leaving a large residual is not an abandonment condition. Data
   insufficiency, duplication or inability to distinguish explanations may be.
   No broad empirical fitting is needed at this stage.
3. After this exchange, Astra drafts the topic decision brief for Barry (at most
   two pages, plus questions only he can answer), and Fable reviews it. Barry may
   choose, redirect or reject. Rename the repo once the topic is clear.

## Correspondence checkpoint for this Astra task

- Project: `project` (active view).
- Discussion: 70; launch message: 826.
- Last full retrieval `next_after`: **959**; exhausted `through`: **959**.
- Explicit acknowledgement: through message **959** in discussion 70.
- Next retrieval: omit `through` to capture new messages, and use `after=959`.

## Correspondence checkpoint for this Fable task

- Project: `project` (active view); discussion 70.
- Read 826–827 in full, then posted 828–832.
- Last full retrieval `next_after`: **827**. Fable's own posts run through 832.
- Explicit acknowledgement: through message **832** in discussion 70.
- Next retrieval: use `after=832` and omit `through`.

## Coordination note

Both agents currently work in the same WSL checkout,
`/home/bwbrook/papers/project`. Commit before handing off, and do not edit the
other agent's files. The Mac mini checkout is canonical. Fable synchronises its
commits there by pushing to a temporary branch and fast-forwarding `main`, after
checking that the Mac working tree is clean. There is no GitHub remote yet.
