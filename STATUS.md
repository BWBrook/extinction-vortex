# Current state

Updated: 9 October 2026, 10:17 Hobart (AEDT), by Astra (board participant Codex).

**Stage:** topic selected; first tranche authorised. Barry approved the vortex
study on the basis of the final brief and protocol draft 0.3, with the accepted
repairs. His exact words are in discussion 70, message 1131.
- The production design is not yet frozen.
- No empirical p-values before the validation freeze.

**Compute (Barry, 8 October):** the laptop pilot cap is lifted. Run anything
serious on `deep-server` in tmux.

**Phase II (Barry's suggestion, not yet a commitment):** a PRISMA-style search
(protocol §5) for post-2006 series monitored to extinction, to enlarge the
sample beyond the canonical nine. Its target size should come from the Phase I
discriminability results.

**Scientific decision next: Barry.**
- [Astra's amendment proposal](notes/vortex_amendment_proposal_20261009.md)
  recommends reconstructed T1–T4 with T5 descriptive and prior (b) proposed for
  primary validation. This narrows the eventual empirical target; it does not
  turn the failed historical reconstruction into a pass.
- One disagreement is preserved: Fable proposed RI as primary because its
  observed estimates were closest; Astra recommends retaining the recorded
  pre-fit random-slope candidate, with RI as a mandatory sensitivity. Neither
  choice identifies the historical estimator or makes the analysis blind.

**Fable next:** respond to [Astra's 0.4 review](notes/astra_protocol04_review_20261009.md),
repair the formal calibration specifications and adjacent-gap interpolation,
and continue synthetic development on `deep-server`. Freeze the same full
procedure for validation and empirical use. No primary prior has yet passed
production validation.

**Fable's M0 (8–9 October):** frozen at `ebcd0d2` before reading Astra's
sampler. It agrees with Astra's within Monte Carlo error (board message 1180;
`analysis/fable/m0/`). Astra reran all 19 invariant checks successfully and
found a separate adjacent-gap interpolation defect; the completed M0 comparison
did not use interpolation. Historical MIXREG was not recovered in the bounded
search; current evidence does not establish universal unavailability or that a
licence would recover the historical inputs/settings.

**Astra execution bundle (8 October):** source freeze `418a5ff`, result freeze
`e1afca1`, both preceding Fable-code inspection. All 54 declared fits ran on
deep-server; synthetic likelihood/EB and M0 invariant checks passed. The
post-freeze comparison matches all 149 input observations and Gaussian
likelihoods at matching covariance parameters to 6.3e-13. **Stage B has not
passed:** no candidate recovers all four rounded slopes, and scaling/T5 remain
unresolved. See [reconstruction](analysis/astra/stage_b/README.md) and
[source audit](notes/astra_source_audit_20261008.md).

**Stage B v0 (Fable), frozen 8 October:** see `analysis/fable/stage_b/` and
board message 1139. Astra should freeze its own independent implementation
before opening those files.

Astra accepted the 1131 allocation and proposed name `extinction-vortex-selection`
in 1144; existing paths remain during the active handoff. The Q&A behind the approval (novelty, approach,
Phase II) is recorded in
[notes/vortex_study_summary_20261008.md](notes/vortex_study_summary_20261008.md)
(board message 1132).

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
  inventory labels are provisional; the later archived Table 1 check does not
  demonstrate fitted-statistic reconstruction. GPDD follow-up counts are
  observations, not years.
- Verified the Williams Dryad API's CC0 licence declaration and consulted the
  official PRISMA-P, PRISMA-S and PRISMA-EcoEvo guidance. No new empirical fit
  or forward-outcome extraction was run.
- Posted 994 (allocation and stage-order response) and 999 (concrete draft,
  methodological specifications and handoff). Checked local document links,
  exposure-log structure and protocol coherence.
- Reviewed draft 0.2, board 1001, the reconciliation script/output and source
  manifest. A separate mathematical audit identified invalid model support,
  unresolved calibration/classification targets, weak validation gates and an
  incomplete cost estimate. The review gives bounded repairs, not empirical
  findings about feedback.
- Accepted Fable's four procedural amendments with unit, ascertainment and
  exposure qualifications in §§5–6 and 8. Formal §§1–4, 7 and Fable's §9.1 are
  preserved as proposed text; §9.2 records the unresolved review findings.
- Extended the bounded prior-work check, adding the Griffen/Drake 2009
  final-decline and passage-time papers. Archived executed query URLs and 938
  returned metadata records in the [search record](notes/vortex_prior_work_search_20261005.md)
  and [identifier ledger](notes/vortex_prior_work_records_20261005.csv).
  Retrieval is not systematic screening; novelty remains provisional.
- Prepared and visually checked the two-page decision brief. Its recommendation
  is a source/reconstruction/development-pilot tranche if Barry selects the study;
  it does not endorse a 220-core-hour production allocation.
- Posted 1027 (quantitative objections) and 1028 (brief, amendments and handoff),
  read the contiguous updates and acknowledged through 1028. No new empirical
  fit, GPDD trajectory extraction or heavy computation was run.
- Reviewed draft 0.3 and messages 1032–1033. Verified the fixed-sample
  validation arithmetic and identified the unadjusted optional-look issue.
  Recorded remaining Monte Carlo-reference, effect-target and scenario/unit
  specifications as development tasks before production, with a bounded
  independent methodological check.
- A read-only delegate verified raw worktree/Git-blob hashes, exact replay of
  the archived reconciliation, and checksum refusal on a changed temporary
  input. Six zero-inclusive window lengths match; fitted statistics remain
  unreconstructed. Exposure row E12 records the access.
- Corrected the claim that Griffen–Drake 2009 omit conditioning against their
  primary introduction. Qualified publication, outcome-probability and general
  sample-size promises. Finalized the two-page brief with explicit pilot caps;
  no research simulation or empirical fit was run in this review.
- Posted 1049 (review closure and source correction) and 1050 (final brief and
  capped first-tranche proposal); read and acknowledged through 1050.
- On 8 October, caught up through the approval and Fable's first reconstruction,
  accepted the allocation in 1144, and recorded the pre-fit specification and
  prior exposure to Fable's reported numbers. The separate implementation was
  not result-blind.
- Implemented profiled Gaussian marginal ML and the unstructured M0 sampler;
  froze code, ran 54 declared fits on deep-server in tmux, froze all results,
  then opened Fable's code. Source/input hashes and exit status were retained.
  A read-only audit found no fatal mathematical defect; a nonconvergence guard
  and provenance assertions were added after the freeze and tested.
- Compared 14 common models: shared inputs match and likelihood/GLS calculations
  agree at matching covariance parameters. Independently optimized results can
  differ near covariance boundaries. No historical-estimator equivalence or
  empirical feedback conclusion is claimed.
- Verified the primary crane table and wild-dog data, audited all nine census
  mappings, and excluded the same-trajectory crow survival estimate as an
  independent prior. Original windows, some annual-statistic definitions and
  literature-prior centres remain unresolved. Exposure rows E14–E17 record the
  access. No forward GPDD outcomes or empirical conditional-null p-values were
  generated.
- Posted 1159 (frozen reconstruction, comparison and M0 handoff) and 1160
  (source findings and protocol amendments). Read the contiguous updates and
  acknowledged through 1160. Execution bundle `ca6be86` was synchronized to the
  clean canonical Mac checkout before posting; Fable's response is next.
- On 9 October, read 1180–1181 and protocol 0.4. Reviewed the finite-bank
  calibration argument with a read-only mathematical delegate; identified
  mismatched validation/empirical replicate counts, post-result bank enlargement
  and undefined failure contributions to the fixed-denominator gates.
- Inspected Fable's frozen M0 and comparison code; all 19 invariant tests passed
  on replay. A targeted consecutive-interpolation check failed and is recorded
  for Fable's repair. No new empirical fits or conditional-null tests were run.
- Prepared the four-statistic amendment and recommended keeping the pre-fit
  primary candidate rather than selecting a diagnostic for closer observed
  agreement. Prior exposure and the unresolved difference with Fable are explicit.
- Committed the review/proposal as `a14af6d`, synchronized clean WSL and Mac
  checkouts, and posted 1188 (review) and 1189 (amendment recommendation).
  Read the contiguous updates and acknowledged through actual message 1189.

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
- Protocol draft 0.2 (5 October): read 994 and 999. Formalised protocol §§1–4
  and 7: questions and outcome rules, Part 1 and Part 2 estimands, generative
  models, ABC calibration under matched selection, δ_min, Stage B–D criteria,
  compute estimate, and a table of prespecified vs exploratory analyses. Added
  a requirement-status table (§9.1).
  - Archived the F&H Table 1 reconciliation
    ([notes/t3/fh_table1_reconciliation.txt](notes/t3/fh_table1_reconciliation.txt)):
    24 of 27 values match, with 3 discrepancies; 150 vs 148 censuses. This
    corrects the round-2 claim that the values reproduced exactly.
  - Added a [source manifest](notes/t3/source_manifest.csv), exposure rows E09
    and E10, and an archive of the 2 October GPDD terminal-zero screen.
  - Posted 1001: integration summary, resolution of 999's five
    specifications, and review of §§5–6 and 8 with four amendments.
- Draft 0.3 (5 October): read 1027 and 1028, Astra's quantitative review and
  the brief. Accepted R1–R6 and revised §§1–4 and 7:
  - valid M0 (survival and recruitment sampled directly) and a β-scale M_A;
    M_G deferred;
  - a named conditional prior-predictive test with a proposed ABC
    algorithm, cross-fitted validation and two priors;
  - Clopper–Pearson validation criteria, with V-fail taking precedence;
  - discrepancy-only Part 1, with the classifier removed;
  - Stage B judged at published precision; the compute figure replaced by a
    benchmark plan with sequential p-values;
  - Part 2 parked with its open items listed.
  - Stored the Williams CC0 input in `data/raw/williams2021/`. The
    reconciliation now checks the input hash and reports both window
    conventions: 6 of 9 F&H windows match.
  - Reported that Griffen & Drake 2009 cite F&H for log-scaling; Astra's
    subsequent correction distinguishes this from their explicit discussion
    of conditioning (protocol §9.4).
  - Posted 1032 (R1–R6) and 1033 (brief review, four suggested edits).
- Final review (5 October): read 1049–1050, Astra's draft 0.3 review and the
  final brief. Confirmed Astra's source correction against the Griffen & Drake
  full text: Fable's claim that they do not discuss conditioning was wrong.
  Accepted the three production repairs (independent reference construction,
  fixed n = 1,000 validation, O1 unavailable for an unattainable effect target).
  Endorsed the brief as written. Posted 1051 and added a correction note to
  protocol §9.3.

## Pending

1. Barry considers the four-statistic target amendment. Fable responds to
   Astra's estimator-choice recommendation and repairs the formal 0.4 text;
   the review records which statements are not yet supported by validation.
2. Retain the unresolved historical input/estimator and census-class questions.
   Do not infer software unavailability from failed retrieval or silently change
   raw values, interpolation or annual-increment definitions. Stage B remains
   unpassed, even if a reconstructed target is adopted.
3. Develop synthetic calibration, record acceptance rates and component costs,
   and retain all failed feasibility checks. Serious work runs on deep-server
   in tmux. The 220-core-hour proposal remains withdrawn; production resources
   follow a measured design. Empirical tests follow the specified validation
   freeze, which has not occurred.
4. Complete the named close-prior-work checks and the frozen Stage A search.
   Final Nabutanyi–Wittmann text and Drake–Griffen 2009 passage-time methods
   remain unverified; the orientation search is not a completed systematic
   review. Phase II's additional-series search is a suggestion, not a commitment.
5. Part 2, genetic extensions and new forward-response access remain parked.

The empirical Part 1 comparison plus simulation is the minimum contribution;
Part 2 is conditional. A failed gate does not become evidence of absent feedback.

## Correspondence checkpoint for this Astra task

- Project: `project` (active view).
- Discussion: 70; launch message: 826.
- Last full retrieval `next_after`: **1189**; exhausted `through`: **1189**.
- Explicit acknowledgement: through actual message **1189** in discussion 70.
- Next retrieval: omit `through` to capture new messages, and use `after=1189`.

## Correspondence checkpoint for this Fable task

- Project: `project` (active view); discussion 70. The board identity is now
  "Claude" (it was "Fable"); Astra's appears as "Codex".
- Read through 1160 in full. Fable's posts: 828–832, 988–990, 1001, 1032–1033,
  1051, 1131–1132, 1139–1140, 1180–1181.
- Last full retrieval `next_after`: **1179**.
- Explicit acknowledgement: through message **1181** in discussion 70.
- Next retrieval: use `after=1181` and omit `through`.

## Coordination note

Both agents currently work in the same WSL checkout,
`/home/bwbrook/papers/project`. Commit before handing off, and do not edit the
other agent's files. The Mac mini checkout is canonical. Fable synchronises its
commits there by pushing to a temporary branch and fast-forwarding `main`, after
checking that the Mac working tree is clean. There is no GitHub remote yet.
