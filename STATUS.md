# Current state

Updated: 11 October 2026, 17:45 Hobart (AEDT), by Fable (board participant Claude).

**Stage:** topic selected; first tranche authorised. Barry approved the vortex
study on the basis of the final brief and protocol draft 0.3, with the accepted
repairs. His exact words are in discussion 70, message 1131.
- The production design is not yet frozen.
- No empirical p-values before the validation freeze.

**Compute (Barry, 8 October):** the laptop pilot cap is lifted. Run anything
serious on `deep-server` in tmux.
Fable relayed Barry's offer of Kunanyi capacity (up to 48 x 28-CPU nodes) in
message 1222. This is a later resource option; this project has not submitted a
PBS job or measured throughput there. Development remains on deep-server.

**Phase II (Barry's suggestion, not yet a commitment):** a PRISMA-style search
(protocol §5) for post-2006 series monitored to extinction, to enlarge the
sample beyond the canonical nine. Its target size should come from the Phase I
discriminability results.

**Scientific target adopted by Barry, 9 October, 11:06:47 AEDT.**
- [Verified Decision Inbox response](docs/decisions/01663ea4-7564-41c6-abf4-d50cec5448c5.md):
  **reconstructed T1–T4, simpler random-intercept primary, random-slope model as
  mandatory sensitivity** (`approve_ri_primary`). No comments, alternatives or
  deferral. The primary-model disagreement is resolved by Barry's choice.
- [The adopted amendment](notes/vortex_target_amendment_20261009.md) records
  T5/scaling as descriptive, prior (b) proposed for primary validation, and the
  retained validation/source/production limits. Historical reconstruction
  remains unpassed; the analysis is an exposed reanalysis.

**Primary-null development candidate adopted by Barry, 9 October, 14:51:05 AEDT.**
- [Verified response](docs/decisions/d36e602c-1c18-45fe-83ce-90adda12d313.md):
  **ar_cat primary development candidate; iid mandatory sensitivity**
  (`approve_ar_cat_primary`). No comments, alternatives or deferral.
- [Adopted null amendment](notes/vortex_null_amendment_20261009.md) records the
  scope. This selects the model for the next development and validation design;
  it does not freeze production or pass validation. Beta_min, numeric scenarios,
  final settings and measured resources remain to be settled.

**Protocol draft 0.5 (Fable, `5c2d1f2`; board message 1206).**
- Applies Barry's adopted target and several of Astra's 0.4 repairs; competing
  executable instructions remain, as detailed in the latest review.
- Fixes adjacent-gap interpolation; Astra replayed all 20 sampler checks.
- Adds a preliminary benchmark: 0.15 s per T1–T4 dataset; about 1,170
  core-hours is a one-bank fitting subtotal. Full costs and deep-server
  throughput have not been established by this benchmark archive.
- **Proposes** a no-feedback null with AR(1) environment and catastrophes
  (M0\*). Several calibration summaries have improved marginal coverage,
  but joint support, model justification and discrimination need comparison.
  The all-summaries-between-3rd-and-97th claim is false (turtle A: 97.4).
  This model choice follows exposure to C and remains adaptive.

**Astra review of 0.5:** [full findings](notes/astra_protocol05_review_20261009.md)
and [reproducible arithmetic](analysis/astra/protocol05_checks/).
- M0\* can have no direct abundance feedback while violating the stated
  abundance-independent conditional mean. Formal H0 and downstream experiments
  need revision before any promotion.
- With two equal ideal references and 2,000 independent test draws each, the
  >0.01 stability rule triggers with probability 13.7% at true tail probability
  0.05 and 51.7% at 0.5. These are analytical examples, not empirical p-values.
- The proposed J_i rule exceeds the raw-draw cap for three populations and
  misses the retained-bank target for three others.
- M0 remains the existing baseline; M0\* is a development candidate. A primary
  promotion requires Barry's scientific choice after a reviewable comparison.
  No new questionnaire is open at this checkpoint.

**Protocol draft 0.6 (Fable, `05df1b6`; board message 1218).** Responds to
Astra's 0.5 review.
- Structural H0 and exploratory catastrophe priors; a Student-t comparator.
- The second-bank check is descriptive; final seeds are reserved and Fable's
  exposure row is now E20. Some older competing instructions remain.
- **Five-null comparison** (deep-server): only AR + catastrophes (ar_cat)
  satisfies the new bank-budget rule near observed C for all nine. This does
  not establish coverage of fresh outer C or necessity of catastrophes.
- **End-to-end benchmark:** approximately 1,100 worker-seconds per outer dataset,
  inferred from sixteen workers times fitting wall time, giving a roughly
  2,100-core-hour planning estimate. A tenfold bank increase is a proposed remedy
  for calibration shortfalls, not an established coverage guarantee.

**Astra review of 0.6:** [findings](notes/astra_protocol06_review_20261009.md)
and [reproducible checks/source recovery](analysis/astra/protocol06_checks/).
- Accepts the structural H0, descriptive second-bank rule and provenance repairs.
- Three of four archived synthetic benchmark trials are indeterminate under
  the calibration rule despite numeric diagnostic p-values. The running screen
  must retain these failures and check all arm counts before interpretation.
- Tiny mocked fixtures reproduce unhandled singular covariance and a driver
  that can report completion after background failures.
- The unbounded Student-t exponential recruitment has infinite marginal mean;
  the Gaussian centring is not appropriate. The current comparison does not
  test AR plus continuous heavy tails or show that catastrophes are necessary.
- Exact benchmark source was recovered from deep-server and its archived hash
  verified. No empirical test or new population simulation was run by Astra.

**Protocol draft 0.7 (Fable), responding to the 0.6 review.**
- **Discrimination screen complete** ([note](analysis/fable/calibration/discrimination_v1/NOTE.md)).
  All 4 × 30 synthetic trials ran and were scored with fixed denominators.
  - With 2×10^8 banks, calibration shortfalls make 23–43% of trials
    indeterminate, which breaks the null gate for either null.
  - Raw-p diagnostic under M_A at Δ10 = 0.5: 29/30 detections against the
    iid null and 21/30 against ar_cat. Null arms: 0/30 and 1/30.
  - No fit failures in 240,120 datasets.
- **Outer-C coverage** ([note](analysis/fable/calibration/coverage_v1/NOTE.md)),
  20,000 fresh outer datasets per scenario.
  - At tolerance 1.0, all-nine coverage is 0.67–0.69 under the nulls at 1×.
    About 100× banks would be needed to hold shortfalls near 0.5%.
  - Proposal (§3.4; Astra review below): a k-NN library with 2×10^9-draw banks
    and no distance-shortfall branch. Its projected maximum radius at 10×
    is ≤ 0.99 for 95% of ar_cat null datasets; larger banks are not yet built.
- **Corrections.** The candidate conclusion is narrowed: ar_cat is the only
  implemented candidate meeting the observed-C rule, which is not evidence
  that catastrophes are needed. The Student-t comparator is retired. The
  capped target A, the H0 wording and the seed and failure text are
  consolidated.
- **Code.** The e2e outcome classification, covariance catch and row
  checkpointing are repaired; the driver now waits on each PID.

**Astra review of 0.7:** [findings](notes/astra_protocol07_review_20261009.md).
- Accepts ar_cat and fixed-K nearest-neighbour calibration as development
  candidates, with iid mandatory sensitivity. Barry subsequently adopted the
  primary-null choice above; no production or validation freeze is implied.
- All 120 raw remote statistic files match their archived hashes and contain
  exactly 2,001 ordered, finite rows with zero failure flags. The four-arm
  summaries reconcile. Tiny fixtures confirm the three previous repairs.
- The 29/30 versus 21/30 raw detection difference compares matched generator
  and reference designs, both of which change; it does not isolate the effect
  of broadening the reference. Tenfold-bank radii remain projections.
- Before another full run, fix the scorer's new-output field mismatch and
  reject incomplete/unordered statistic inputs. Before freeze, record fallback
  use and the minimum training sample/covariance policy, and predeclare
  radius-stratified validation diagnostics. Scenario-average control is not
  uniform control throughout C-space.

**Astra pre-handoff review, 10 October:**
[bounded findings](notes/astra_protocol08_precheck_20261010.md) and
[independent power audit](analysis/astra/protocol08_precheck/power_screen_audit.json).
- At that pre-handoff inspection, committed calibration code was at `0430737`,
  including sharded-bank builder `d16fe45`. Fable's draft 0.8, exposure-log edits
  and development-design archive were uncommitted in WSL. They were
  inspected read-only and their hashes recorded, not adopted or frozen.
- Completed remote pilot: five arms ×30 trials, R_train = R_test = K = 2,000.
  Independently recomputed all 150 synthetic T files: complete ordered rows,
  finite statistics, zero failures; both bounds/outcomes/fallback totals match.
- Rejections: null 1/30; beta_min 1/30; 2 beta_min 2/30; Delta10 .3 8/30;
  Delta10 .5 18/30. At beta_min the two-sided exact 95% interval is
  0.00084–0.17217. This warns of low discrimination at the risk-defined effect;
  it is development evidence, not validation or evidence of absent feedback.
- The earlier output-contract and row-shape repairs pass. Three narrow guards
  remain: malformed/absent-file classification; shard field-length, selected-
  count and draw-ID integrity; and checking the logged upper p bound.
- The effect recipe yields beta_min .974519 (Delta10 .075) in this development
  bank. Retain the risk target and its consequences; changing it after power
  inspection would need an explicit scientific amendment.
- The draft's radius interpretation and proposed predictive stress check need
  qualification. Complete the cost inventory; measured concurrent pilot
  throughput suggests roughly 70 hours for 7,300 trials before banks/overheads,
  rather than the nominal-core projection of 45 hours. Both are planning figures.

**Protocol draft 0.8 (Fable): validation design and measured costs.**
- **Adopted null recorded.** The k-NN library is the development algorithm,
  with radius-stratified diagnostics and a fitted-parameter predictive stress
  check (selection and parameter-retention rules stated).
- **Repairs.** All of the 1253 and 1313 repairs are made: ragged, absent and
  missing inputs; bank-shard integrity; p_hi verification; the
  training-failure rule; fallback logging.
- **Results.**
  - 10× development banks: [dev_design_v1](analysis/fable/calibration/dev_design_v1/NOTE.md).
  - Measured radii match the projection; the empirical radius is typical
    (64th percentile) under ar_cat and in the tail (97th) under iid.
  - Development β_min is Δ10 = 0.075.
  - Numeric corners are proposed; strong environment replaces short L.
- **Power screen**: [power_screen_v1](analysis/fable/calibration/power_screen_v1/NOTE.md).
  - Detections were 1/30 at β_min, 8/30 at Δ10 = 0.3 and 18/30 at 0.5.
  - The effect target is retained; O3 is the likely outcome and a detection
    curve is added.
- **Measured cost.** About 3,130 core-hours: 0.38 core-hours per trial,
  measured all-in over 150 trials. Roughly 75 hours on deep-server.
- **Still to do.** The M_D and M_O generators are not yet implemented.

**Astra review of 0.8 (`f8546ec`, handoff 1326):**
[review and next tranche](notes/astra_protocol08_review_20261010.md),
[archive/cost checks](analysis/astra/protocol08_review/evidence_check.json) and
[guard fixtures](analysis/astra/protocol08_review/guard_audit.json).
- Accept continued development with the risk-defined effect target retained,
  the three numeric-corner recipes, the larger-effect detection curve and
  descriptive radius diagnostics. No validation freeze is implied.
- All 150 T-manifest entries and ten archived metadata/checkpoint files match
  the earlier independent raw-statistic audit; outcomes and 3,130-core-hour
  arithmetic reconcile. No new simulations, R fits or empirical p-values.
- The requested guards pass tiny fixtures. A logged NaN still bypasses the
  bound-reconciliation check; this does not alter the recomputed outcome.
- Before freeze: settle finite-budget parameter replacement in the predictive
  stress check; reconcile the full section 7 sensitivity inventory and the
  still-stated two 200-dataset development screens; implement/specify M_D/M_O
  and measure the remaining costs. Production-bank generation and subsequent
  beta_min/corner recomputation remain preparation, not validation.

**Protocol draft 0.9 (Fable).** Responds to 1348.
- **Done:**
  - executable M_D and M_O with priors and 28 limiting-case checks
    ([alt_check_v1](analysis/fable/calibration/alt_check_v1/NOTE.md));
  - the fixed-mixture stress-check law;
  - the §7 execution inventory, about 3,300 core-hours;
  - the finite-bound scorer check, plus a fix for a shadowing bug it
    introduced, which the smoke test caught;
  - frozen radius bins;
  - a draft [freeze package](notes/vortex_freeze_package_20261010.md).
- **Running on deep-server:**
  - tmux `fable_screen200`: the §4.1 screens, 200 under the null and 200 at
    β_min. Run directory
    `/data/fable/vortex/banks10x_20261009T041220Z/dev_screen200_v1`.
  - Then tmux `fable_prodbanks`: the designated primary, stability and iid
    banks, followed by β_min, the corners and the empirical position on the
    primary bank. Run directory `/data/fable/vortex/production_banks_*`.

**Astra review of 0.9 (`f74f4f7`, handoff 1359):**
[review](notes/astra_protocol09_review_20261010.md),
[generator checks](analysis/astra/protocol09_review/generator_audit.json) and
[run-contract checks](analysis/astra/protocol09_review/run_contract_audit.json).
- Accept the proposed M_D design distributions, explicit M_O starting-count
  convention and recorded selection, fixed-mixture stress law, radius bins,
  retained development screens and expanded execution inventory.
- Bounded checks preserve exact null/M_A behavior across 36 configurations,
  verify the alternative limiting cases and multirow scorer/NaN repairs.
- Pending numbers alone do not complete the freeze: implement the stress
  sampler and fixed-budget unresolved branch; final chunk assembly, gate and
  failure accounting; explicit concurrency/stream mapping; and the promised
  selected M_D/M_O evidence. Qualify the equal-cost claim and pass recomputed
  beta_min to the timing script. The total remains a planning projection.
- No partial running outcomes inspected, no R fits or new large jobs, and no
  changes to the running screens/banks. Only bounded local synthetic/mocked
  checks. The current jobs can continue within their existing scope.

**Fable, 0.9 executable completion (§9.11).**
- **Implemented and tested:**
  - the stress sampler, with a fixed budget and unresolved sampling outcome;
  - the run manifest, the three-slot chunk runner and the gate-checking
    collector;
  - per-trial provenance of the selected draw;
  - scorer contract v3 with fit-failure accounting;
  - disjoint sensitivity seed families;
  - the guarded Q1 entry point, never run.
- **Tests:** 19 mocked-fit checks, plus a real-R launcher run on a toy
  manifest.

**Draft 0.10 (Fable): freeze candidate, 11 October.**
- **§4.1 screens** ([dev_screen200_v1](analysis/fable/calibration/dev_screen200_v1/NOTE.md)):
  5/200 null rejections, 5/200 at β_min, 1 of 800,200 datasets failed per arm.
  No stop rule triggered.
- **Designated banks:** primary ar_cat, stability ar_cat and iid, each 2e9
  draws per population; 125.6 core-hours measured; shard hashes recorded.
- **Recomputed on the primary bank:** β_min unchanged at Δ10 = 0.075; the
  corners; the empirical position (ar_cat 0.429, bin 4).
- **Final manifest and stress sets** at code commit `49f65ce`. Receipts and
  runtime versions are in
  [freeze_v1](analysis/fable/calibration/freeze_v1/NOTE.md).
- The [freeze package](notes/vortex_freeze_package_20261010.md) is complete
  for review.

**Astra review of 0.10 (`df94693`, handoffs 1371/1392):**
[full review](notes/astra_protocol10_review_20261011.md).
- Independently recomputed all 400 screen T files and p bounds; verified
  5/200 rejections and 1/800,200 failed vectors per arm.
- Rehashed all 540 designated-bank shards; matched the source/package
  receipts and all 2,700 stress vectors to the retained library indices.
- Sampler, provenance, manifest counts and numerical gate limits pass.
- Freeze held for two executable repairs: missing-output fit accounting and
  binding chunk/restart/summary/empirical execution to the frozen configuration.
  The completed screens and current archived manifest were not found corrupt.

**Fable, 0.10 review repairs (§9.13), 11 October.**
- **Fit accounting** comes from the T files themselves; unknown fit status and
  missing or malformed outputs count conservatively.
- **Binding.** The manifest is host-independent and embeds the source, bank
  and stress hashes and the runtime pins. Preflight runs per host. Chunks,
  the summary and the empirical guard are all bound to the manifest digest
  `96603037…` and to the code at `52779d0`.
- **Tests:** 25/25 pipeline and 28/28 generator; the deep-server preflight
  passed.
- **Allocation wording** is reconciled with Barry's standing authority; no
  resource question is proposed.

**Astra accepted the validation freeze, 11 October, 11:58:13 AEDT:**
[acceptance and checks](notes/astra_protocol10_freeze_20261011.md), board 1450.
- Source `52779d01468dac186c19810b59c8295dbedd212f` and manifest SHA-256
  `96603037ec05036153f67b649757d067ca193c5e0a8610d3b855ef8f22139429`.
- Both 0.10 holds are resolved: 20 accounting and 39 binding checks pass.
  All scientific settings, chunk seeds and 2,700 stress vectors are unchanged.
- This freezes the procedure; validation has not yet passed or begun.

**Frozen validation ran on kunanyi, 11 October, 13:10–16:39 AEDT: V-fail.**
[Record and results](analysis/fable/calibration/validation_v1/NOTE.md).
- Block 3 (`null_low_s`) gave 148 rejections in 1,000, against at most 60
  allowed. The other three null blocks passed: 46, 41 and 30.
- Power at β_min was 21 of 300, against at least 224 required.
- All 7,900 trials resolved. The fit-failure rate was 0 in every block.
- The summary reproduces byte for byte on deep-server.
- Under protocol §1 the empirical result can be reported only as *insufficient
  identification*, and `empirical_q1.py` refuses to run.
- No empirical p-value has been computed.

**Next response: Codex.** Independent audit of the retrieved outputs:
- the tarball is on deep-server at `/data/fable/vortex/kunanyi_run1/`,
  SHA-256 `312d91e4…`.

Then Barry decides how to proceed. Any revised procedure would be a new
pre-registered version, with its own freeze and validation, and this V-fail
must be reported.

## Completed by Astra

- 11 October, accepted the repaired scientific freeze in message 1450 after
  59 independent contract checks and package identity checks. Separately
  reproduced a PBS collector wrapper that masks process failure and returned
  that operational repair to Fable before launch. Receipts are in
  `analysis/astra/protocol10_repair_review/`.

- 11 October, reviewed the complete 0.10 candidate at `df94693`.
  Accepted the archived evidence and implemented stress sampler; returned
  reproducible incomplete-output and stale-configuration counterexamples.
  Saved the audit scripts and receipts under `analysis/astra/protocol10_review/`.

- Reviewed the 0.9 specifications and draft freeze package on 10 October at
  `f74f4f7`, in parallel with Fable's running compute. Accepted the scientific
  specifications and identified the remaining executable completion work in
  message 1368.
- Reviewed Fable's formal 0.8 handoff on 10 October at `f8546ec`, with a bounded
  independent guard audit and archive/cost reconciliation. Accepted continued
  development and returned the finite pre-freeze handoff above in message 1348.
- On 10 October, inspected committed code and Fable's unfinished 0.8 evidence,
  independently reconciled the completed remote power screen, and posted
  findings in 1309/1311/1313/1314. No new simulation, R fits or empirical test;
  no peer working files or jobs changed. Preserved the poor-power result.
- Collected and independently verified Barry's primary-null response, archived
  the form, preserved immutable response files at `07c233e`, and relayed the
  exact choice in 1255. Updated the adopted amendment and active project record.
- Reviewed 0.7 at `5ace89e`, acknowledged 1247 and posted the development
  acceptance and implementation handoff in 1253. Verified all raw statistic
  hashes/shapes read-only; no simulation or empirical fit. Created the single
  primary-null questionnaire with an explicit candidate-selection scope.
- Reviewed 0.6 at `1813bfc`, acknowledged 1218/1222 and posted the early warning
  and full repair handoff in 1226/1228. Archived deterministic feasibility
  arithmetic and tiny mocked failure probes, and recovered the exact uncommitted
  e2e_v1 source by its existing SHA-256. The live screen was inspected read-only;
  no jobs were changed or additional population simulations dispatched.
- On 9 October, reviewed draft 0.5 and benchmark evidence at `9e597d9`, with
  bounded read-only mathematical and implementation audits. Replayed 20 sampler
  checks and archived exact second-bank/bank-size arithmetic. Posted findings
  and the proposed bounded development handoff in 1212 and 1214. No new empirical
  fits, conditional-null p-values or production validation were run.
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
- Created the Decision Inbox questionnaire at Barry's request, then collected
  his submitted `approve_ri_primary` decision. Independently verified the hash,
  complete answer rendering and archived/active status; committed the immutable
  response on the canonical Mac and synchronized it into WSL. Recorded the
  adopted amendment and relayed the exact decision in message 1203.

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

- 9 October, draft 0.7.
  - Completed and scored the four-arm discrimination screen.
  - Ran the outer-C coverage check, archived in `discrimination_v1/` and
    `coverage_v1/`.
  - Proposed a k-NN library with 10× banks.
  - Corrected and narrowed the null comparison, and retired the Student-t
    comparator.
  - Stated the capped target, and consolidated the H0, seed, fallback and
    failure text.
  - Repaired e2e failure handling and the driver.
  - Added exposure row E23. Read 1226–1228.

- 10 October, draft 0.8.
  - Built 10× ar_cat and iid development banks (77.5 core-hours) and measured
    library radii.
  - Computed the development β_min, the corners and the empirical position.
  - Ran a 150-trial power screen at production counts.
  - Repaired the scorer, input and bank guards from 1313.
  - Wrote the protocol's design, stress-check and cost sections.
  - Exposure row E25. Read 1309–1314.

- 11 October, 0.10 review repairs.
  - Repaired fit accounting.
  - Made the manifest host-independent and bound it by digest, with
    preflight and runtime pins.
  - Regenerated the manifest; wrote receipts. Read 1408–1413.
- 11 October, draft 0.10.
  - Archived the §4.1 screens and the designated banks.
  - Recomputed β_min, the corners and the empirical position.
  - Wrote the final manifest and stress sets, recorded receipts and runtime
    versions, and completed the freeze package. Exposure row E28.
- 10 October, 0.9 executable completion.
  - Implemented the stress sampler, the manifest, the chunk runner, the
    collector and the gates, with provenance kept per trial and the scorer
    at contract v3.
  - Added the guarded Q1 entry point; qualified the cost and scope wording.
  - Read 1366–1368.
- 10 October, draft 0.9.
  - Implemented M_D and M_O with limiting-case tests.
  - Repaired the stress law and the scorer (including the shadowing fix).
  - Wrote the execution inventory, froze the radius bins and drafted the
    freeze package.
  - Launched the §4.1 screens and queued the designated banks.
  - Read 1339–1348.

## Pending

1. Fable completes the PBS failure-status repair and host qualification/staging
   for the accepted validation freeze. Source `52779d0` and manifest `96603037…`
   are accepted. The low-power evidence is retained, and the effect is not
   retuned to obtain O1.
2. Retain the unresolved historical input/estimator and census-class questions.
   Do not infer software unavailability from failed retrieval or silently change
   raw values, interpolation or annual-increment definitions. Stage B remains
   unpassed, even if a reconstructed target is adopted.
3. Develop synthetic calibration, record acceptance rates and component costs,
   and retain all failed feasibility checks. Serious work runs on deep-server
   in tmux. The 220-core-hour proposal remains withdrawn; production resources
   follow a measured design. Empirical tests follow the specified validation
   freeze (now accepted) and its still-pending validation gates.
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
- Last full retrieval `next_after`: **1450**; exhausted `through`: **1450**.
- Explicit acknowledgement: through actual message **1450** in discussion 70.
- Next retrieval: omit `through` to capture new messages, and use `after=1450`.

## Decision Inbox checkpoint

**Primary-null question (collected and archived):**
`d36e602c-1c18-45fe-83ce-90adda12d313`.
- Request `project-vortex-primary-null-20261009-codex`; submitted
  `2026-10-09T03:51:05.102Z`; collected `2026-10-09T03:55:15.285Z`.
- [Definition](docs/decisions/requests/vortex-primary-null-20261009.json) and
  [creation receipt](docs/decisions/requests/vortex-primary-null-20261009.receipt.json)
  preserve the original request and returned URL; the receipt's open status is
  historical.
- [Response JSON](docs/decisions/d36e602c-1c18-45fe-83ce-90adda12d313.json) and
  [Markdown](docs/decisions/d36e602c-1c18-45fe-83ce-90adda12d313.md) are immutable,
  committed first on the canonical Mac at `07c233e`, then fast-forwarded to WSL.
- Independently verified canonical SHA-256
  `047051b91c4955b788decdb6d32131222e3366389f87e2b25df84bb656bffc86`, equality to
  the original definition, full Markdown question/context/options/selection,
  and empty comments/alternatives with no deferral. Archived listing includes
  collection time; the active project listing is empty with no further pages.
- Decision: `approve_ar_cat_primary`, relayed in Correspondence 1255 and
  adopted above. No questionnaire remains open in this project. No polling.

**Earlier target question (completed):**

- Questionnaire: `01663ea4-7564-41c6-abf4-d50cec5448c5`; **collected and archived**.
  Submitted `2026-10-09T00:06:47.788Z`; collected `2026-10-09T00:11:08.058Z`.
- Request: `project-vortex-amendment-20261009-codex`; project `project` is bound
  to the canonical Mac repo `/Users/bwbrook/papers/project`.
- [Question definition](docs/decisions/requests/vortex-target-20261009.json) and
  [creation receipt](docs/decisions/requests/vortex-target-20261009.receipt.json)
  preserve the exact request and returned URL. Correspondence message 1195
  records creation; its open status is historical.
- [Response JSON](docs/decisions/01663ea4-7564-41c6-abf4-d50cec5448c5.json) and
  [Markdown](docs/decisions/01663ea4-7564-41c6-abf4-d50cec5448c5.md) are immutable
  submitted records, committed first on the canonical Mac as `d613e6c` and
  fast-forwarded into WSL.
- Independently verified canonical SHA-256
  `6175e7b828a0f636d7e219ea5dc534b55a043f4631d7eb4c1d6d12f061ccd33c`, equality to
  the original question definition, all Markdown selections and empty
  comments/alternatives, and absence of deferral. Archived listing includes the
  form with collection time; the active project listing was empty at that
  collection checkpoint, with no further pages.
- Decision: `approve_ri_primary`, as recorded above and relayed in Correspondence
  message 1203. No polling or automatic
  wakeup. A changed decision requires a new questionnaire/request ID.

## Correspondence checkpoint for this Fable task

- Project: `project` (active view); discussion 70. The board identity is now
  "Claude"; Astra's appears as "Codex".
- Read through 1413 in full. Fable's latest posts: 1392 and the 0.10 repairs.
- Last full retrieval `next_after`: **1419**.
- Explicit acknowledgement: through message **1368** in discussion 70.
- Next retrieval: use `after=1419` and omit `through`.

## Coordination note

Both agents currently work in the same WSL checkout,
`/home/bwbrook/papers/project`. Commit before handing off, and do not edit the
other agent's files. The Mac mini checkout is canonical. Fable synchronises its
commits there by pushing to a temporary branch and fast-forwarding `main`, after
checking that the Mac working tree is clean. There is no GitHub remote yet.
