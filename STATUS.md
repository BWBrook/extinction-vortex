# Current state

Updated: 2 October 2026, 17:05 Hobart (AEST), by Fable.

**Stage:** proposed; setup and topic ideation. No research topic, design or
scientific claim has been approved.

**Next response:** Astra. Astra should:

- accept or amend Fable's four procedure amendments and the T1–T3 allocation
  (discussion 70, messages 828 and 829);
- answer the critiques of slate items A–C (830–832);
- run T1, if agreed.

No decision is requested from Barry yet.

## Completed by Astra

- Verified Correspondence API v2 under the Astra identity and read the interface
  and recovery guidance. No existing active project section matched this repo.
- Created section `project` and launch discussion 70, beginning with message 826.
- Recorded the mandate and proposed exchange procedure; drafted three candidate
  questions with a limited primary-source screen and explicit abandonment tests.
- Prepared the shared Mac mini checkout and matching WSL foundation.

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

1. Astra responds to the amendments, the allocation and the critiques, and may
   critique Fable's slate. Proposed bounded checks, pending mutual consent:
   - T1 (Astra): adversarial novelty search on Fable-1.
   - T2 (Fable): triviality check on Astra-A.
   - T3 (Fable): data feasibility for Fable-1.
2. Run the agreed checks, kill tests first.
3. Astra drafts the topic decision brief for Barry (at most two pages, plus a
   list of questions only he can answer), and Fable reviews it. Barry may
   choose, redirect or reject. Rename the repo once the topic is clear.

## Correspondence checkpoint for this Astra task

- Project: `project` (active view).
- Discussion: 70; launch message: 826.
- Last full retrieval `next_after`: **826**; exhausted `through`: **826**.
- Explicit acknowledgement: through message **826** in discussion 70.
- Next retrieval: omit `through` to capture new messages, and use `after=826`.
  Setup receipts posted later by Astra may also appear; this is intentional.

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
