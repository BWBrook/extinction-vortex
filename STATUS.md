# Current state

Updated: 5 October 2026, 13:25 Hobart (AEDT), by Astra.

**Stage:** proposed; vortex protocol preparation. The research design is not
frozen and research execution has not been authorized.

**Barry, 5 October, in chat to both agents:** a provisional preference for the vortex
idea, together with a request for a careful, PRISMA-style pre-registered plan.
His exact words are quoted in discussion 70, message 990, and in
[Fable's round-2 response](notes/fable_round2_response_20261005.md) §1. This is
not a topic selection.

**Next response:** Fable. Fable should:

- formalize §§1–4 and 7 of [the working protocol](notes/vortex_protocol.md),
  resolving its listed estimand, calibration and validation specifications;
- review Astra's §§5–6 and 8 and the [exposure log](notes/vortex_exposure_log.csv);
- answer the proposed metadata-before-power stage order and the qualification
  of preliminary inventory labels, reconstruction and outcome exposure.

The draft handoff and remaining methodological specifications are in discussion
70, messages 994 and 999.

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
  fallback, Astra-C reserve; park Astra-A/B and Fable-3. Fable's round-2 reply
  accepts the earlier methodological objections and continuation rules.
- Read and acknowledged 988–990, accepted the section allocation, and drafted
  the protocol's compilation, exposure and roles sections, with planning
  summaries for Fable's formal sections. No stage is frozen.
- Checked the inventory and GPDD counting mechanics with a read-only delegate,
  and obtained a methodological review of the corrected specification. The
  inventory labels are provisional; no archived script demonstrates exact
  Fagan–Holmes reconstruction. GPDD follow-up counts are observations, not years.
- Verified the Williams Dryad API's CC0 licence declaration and consulted the
  official PRISMA-P, PRISMA-S and PRISMA-EcoEvo guidance. No new empirical fit
  or forward-outcome extraction was run.
- Posted 994 (allocation and stage-order response) and 999 (concrete draft,
  methodological specifications and handoff). Checked local document links,
  exposure-log structure and protocol coherence.

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

1. Fable integrates its formal sections into the existing working protocol and
   reviews Astra's sections. Resolve the finite specification list in §9.
2. Astra reviews the integrated protocol and drafts the two-page brief. Barry
   can then select, redirect or reject the concrete study. Full LPD access and
   a founder-size module remain optional; the public-data core does not depend
   on those decisions.
3. Proposed stage order, once the study is authorized:
   - freeze the search/eligibility specification and audit metadata/structure;
   - reconstruct the published empirical analyses, recording discrepancies;
   - freeze and run calibrated Part 1 simulations and observed comparisons;
   - validate the Part 2 estimator at the audited sampling structure;
   - only if its prespecified gate passes, release additional post-entry
     responses for the frozen forward analysis.

The empirical Part 1 comparison plus simulation is the minimum contribution;
Part 2 is conditional. A failed gate does not become evidence of absent feedback.

## Correspondence checkpoint for this Astra task

- Project: `project` (active view).
- Discussion: 70; launch message: 826.
- Last full retrieval `next_after`: **999**; exhausted `through`: **999**.
- Explicit acknowledgement: through message **999** in discussion 70.
- Next retrieval: omit `through` to capture new messages, and use `after=999`.

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
