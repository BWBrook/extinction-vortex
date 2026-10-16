# Current state

Updated: 16 October 2026, 12:15 AEDT (Australia/Hobart), by Fable (board participant Claude).

**Stage:** topic selected; first tranche authorised. Barry approved the vortex
study on the basis of the final brief and protocol draft 0.3, with the accepted
repairs. His exact words are in discussion 70, message 1131.
- The production design is not yet frozen.
- No empirical p-values before the validation freeze.

**Compute (Barry, 8 October):** the laptop pilot cap is lifted. Run anything
serious on `deep-server` in tmux.
Fable relayed Barry's offer of Kunanyi capacity (up to 48 x 28-CPU nodes) in
message 1222. The 15–16 October Stage 1a smoke has now run on Kunanyi and
measured throughput. The large pilot awaits execution repairs below; routine
development and bounded verification remain on deep-server.

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
- All 7,900 trials resolved. Fit failures were zero in all gating blocks;
  four failed T vectors occurred in descriptive blocks 14–16 (corrected by
  Astra's independent audit; the original machine summary was already correct).
- The summary reproduces byte for byte on deep-server.
- Under protocol §1 the empirical result can be reported only as *insufficient
  identification*, and `empirical_q1.py` refuses to run.
- No empirical p-value has been computed.

**Astra completed the independent v1 audit, 11 October:**
[findings](notes/astra_validation_v1_audit_20261011.md),
[receipts](analysis/astra/validation_v1_audit/).
- Independently rescored all 7,900 T files; every outcome and p-value bound
  agrees. Verified the archive digest and all 8,339 extracted regular files.
- Checked all 170 chunk configurations and all 9,000 selected low-survival
  population trajectories. No block-specific configuration/scoring defect
  explains V-fail. Reference membership was not retained, and no generation,
  reference-draw or fitting replay was done.
- The post-hoc T1/T2 location shifts give a diagnostic lead, but the radius
  strata do not distinguish residual nuisance dependence from approximation.
- The actual empirical guard refuses this summary before bank access.

**Barry supports developing a separate v2**, in his 11 October Codex chat;
the exact quote and bounded plan are in
[the v2 brief](notes/astra_v2_development_20261011.md). Preserve v1 and its
failure, develop at most two candidate procedures, then preregister/freeze
the selected procedure before fresh validation. V1 outputs are exposed
development evidence for v2, not a reusable untouched validation set.

**Fable accepted the v2 tranche (board reply to 1526).** Fable implements and
executes; Astra critiques. The v1 result note's fit-failure wording is
corrected.
- [Mechanism diagnostic 1](analysis/fable/calibration/v2_dev/NOTE.md) rebuilt
  the v1 null neighbourhoods using the declared code and bank. Its compact
  receipt does not independently establish exact historical identity.
  - At the low-s corner, the library's s is strongly displaced (the true value
    ranks 0.09–0.33 within it).
  - The high-σ block is displaced as much in σ, yet passes.
  - Nuisance non-identification is a working hypothesis. The aggregate ranks
    do not rule out finite-library error or isolate a survival/growth cause.

**Astra reviewed D1 and the next experiments, 11 October:**
[review](notes/astra_v2_diagnostic_review_20261011.md),
[bounded checks](analysis/astra/v2_diagnostic_review/), Correspondence **1533**.
- D1's trend is an endpoint summary; floating-point cancellation can break
  mathematical ties in its ranks. Correct and version the diagnostic output;
  the effect on actual D1 ranks is not yet measured.
- D2 can proceed as a trial-level association diagnostic, not causal
  attribution between survival and growth.
- D3 should use 200 paired outer datasets against both frozen-v1 and oracle
  references, with common C scaling, retained failures and a written budget.
  An oracle improvement would not itself eliminate approximation error.
- Candidate B is a plug-in sketch. Its full estimation/calibration rule must
  be specified; block 17 did not evaluate that procedure. Poor v1 power is
  evidence for caution, not a theorem about all future v2 procedures.

**Fable, 11 October evening.**
- D1's categorical reading is withdrawn and qualified.
- [D1c/D2](analysis/fable/calibration/v2_dev/NOTE.md):
  - Fable reported exact reconstruction from matching rounded distances;
    Astra's subsequent review qualifies membership identity below;
  - integer endpoint ranks address the cancellation defect, but constant-library
    ranks still require the correction below;
  - the association neither supports nor rules out nuisance mixing.
- The [v2 development plan](notes/vortex_v2_dev_plan_20261011.md) fixes the
  paired D3 oracle specification and defines candidates A (C+ with
  demographic-variance summaries) and B (grid-calibrated p over a declared
  Θ_G).
- D3 was launched on deep-server with an estimated 4 h run; completed results
  are recorded below.

**Astra reviewed the revised plan and D1c/D2, 11 October:**
[review](notes/astra_v2_plan_review_20261011.md),
[reproducible checks](analysis/astra/v2_plan_review/), Correspondence **1546**.
- Reconciled all 4,000 D1c trial IDs, outcomes and p_hi values with the independent
  v1 audit and checked 36,000 rounded distance comparisons. K+1 truncation can
  change tied membership relative to v1's K query; constant-library midranks
  are defined and must be retained. Refresh D2 after both corrections.
- D3's core pairing/common metric is sound. Reporting, support-stop, restart
  and provenance repairs are required; no partial rejection outcomes were read
  or running jobs changed. Preserve fits and verify which failure branches occurred.
- Candidate A merits bounded development with a heuristic variance rationale
  and measured signal/support costs. Candidate B's rank argument covers a fixed
  finite grid, averaged over calibration-table randomness; empirical C-derived
  grid choice and failure-inclusive validation require explicit qualifications.
- A cheap post-hoc B screen using the stored low-s table reduces beta_min
  detections from 21 to 6/300 and Delta10=.5 from 206 to 98/300. This is
  development evidence for that table, not prospective power validation.

**Fable, 12 October morning.**
- **D3 ran overnight:**
  - frozen prior bank: 34/200 non-accepts;
  - fixed-θ_L oracle: 7/200;
  - McNemar p = 3.5×10⁻⁶; paired difference −0.135 (−0.194, −0.080);
  - the oracle removes the T1/T2 shift.
  - Receipts are verified, and none of Astra's flagged code paths occurred.
- **D1c version 2** corrects the membership query and constant-library
  midranks; D2's interpretation is unchanged (some coefficients change slightly).
- **A0:** C+ leaves the nuisance displacement unchanged and costs C-locality.
- [Plan §7](notes/vortex_v2_dev_plan_20261011.md) proposes invoking the stop
  rule, with three options for Barry:
  1. close and report;
  2. run candidate B (valid on its grid, low power);
  3. use external demographic priors (a target change).
  Fable recommends option 1, with option 3 as the follow-on.

**Astra review, 12 October:**
[completed-result review](notes/astra_v2_results_review_20261012.md),
[reproducers and receipts](analysis/astra/v2_results_review/), Correspondence **1561**.
- Independently rescored all 400 D3 synthetic T files: every outcome/p bound,
  the 34 versus 7 rejections, paired table/interval and z diagnostics reproduce.
  Verified pairing, compact input/source bindings, 404 T/neighbour hashes and
  180 oracle-shard hashes. No new population simulation or fitting.
- D1c2/D2 passes the retained-row audit; A0 features and reported summary
  arithmetic reproduce. Typical original-C distance inflation is about fivefold.
- D3 establishes reference sensitivity at one corner; it does not isolate all
  causes, rule out approximation or validate informative estimated priors. A0
  does not measure A's calibration or power. V-fail/insufficient identification
  remains the declared procedure's outcome, not a theorem about the raw series.
- Recommends one fixed 200-case fitted low-s screen of unchanged A before
  closure, about 5.3% of full A1. This is a proposed bounded assignment within
  the existing two-candidate development scope, not a new freeze or validation.
- D3 retains some inactive reporting/restart defects; fix relevant paths before
  reuse. They do not contradict the independently audited current result.

**Barry's direction, 13 October 2026** (Claude chat, exact): "So, my view is
that we probably need to push forward to Option 3 to make this a study that
moves from "incrementally interesting to a few people" to "more broadly
applicable to conservation biologists". We're in no rush and have the
time/resources to pursue this, provided that the data/case studies exist for
us to leverage. But yes, as the next step, we do the 200-case check now. It's
the obvious next step. Proceed with my full agreement."

**A-screen done** (13 October, 11:06–12:56).
- **Calibration improves modestly.** A rejected 11/200, against v1's 21/200 on
  the same outers. McNemar p = 0.041; difference −0.050 (−0.098, −0.005).
- **The T1/T2 shift largely persists**, and the neighbourhoods are 4.6 times
  wider, so the drop may come from a more diffuse reference. Power is
  untested.
- All checks pass and there were no failed fits in this null-screen comparison.
  [Details](analysis/fable/calibration/v2_dev/NOTE.md).

**Option 3 first-pass scans** (unverified):
[nine populations](notes/option3_evidence_scan_nine_20261013.md) and
[Phase II](notes/option3_phase2_candidates_20261013.md).
- **Nine populations.** Independent survival estimates are mostly
  species-level, with few same-population confidence intervals. Seven
  same-population sources are not yet read.
- **Closure violations.** At least five series had documented interventions:
  wild dog, marmot, golden plover, whooping crane and 'alalā.
- **Phase II.** No candidate is rated GOOD. BC/Alberta caribou and Palmer
  Adélie colonies are PARTIAL. A 2005 caribou paper is relevant prior art.

**Astra review, 13 October (Correspondence 1589):**
[combined review](notes/astra_a_screen_option3_review_20261013.md),
[raw/contract receipts](analysis/astra/a_screen_review/),
[nine-series source audit](notes/astra_option3_nine_source_audit_20261013.md),
[additional-case audit](notes/astra_option3_phase2_source_audit_20261013.md).
- All 400 A/v1 raw T files independently rescored; 21 versus 11 non-accepts,
  paired table/interval and diagnostics reproduce. All 181 primary-bank hashes,
  202 A T/neighbour hashes and source/helper bindings reconcile. Tiny observed-T
  refit differences do not change any A p-value. No new simulation or fitting.
- Accept the fixed 600-case b5/b16 power screen after narrow binding/resume
  repairs. This measures practical discrimination; it cannot identify a diffuse
  reference mechanism or validate A. Low-s null and prior-predictive alternative
  reductions are not a matched-nuisance size/power comparison.
- Source recovery is more promising than the first scan: Haley Lake strongly
  matches the marmot series (1987 remains discrepant); original marked-animal
  demographic estimates exist. Crane identity was already verified. Shared
  monitoring does not automatically make individual demographic evidence circular.
- Public caribou inputs include counts, recruitment and processed survival
  summaries. Maligne and Purcells Central are concrete recovery targets, with
  incomplete demographic overlap. Banff matches Williams ID28 exactly, with
  endpoint-year interpretation still open. Palmer supplies public count/chick/
  sighting data, but needs an open breeding-population interpretation.
- The first scan's blanket closure/causal claims are not supported: distinguish
  additions/removals and movement from handling/predator management, and retain
  unknown census inclusion and disappearance mechanisms. No source counts or
  empirical eligibility decisions changed.

**Barry, 13 October 2026** (Claude chat, exact): "I think option 3 in a
narrowed form is still highly useful. The paper can focus on the core results
we've already created, and use the narrowed "deep dives" to explore the
nuances of individual cases more deeply. I think this is the level of depth vs
coverage that the reviewers would be looking for. To me, it then all comes
together as a nicely unified and comprehensive piece of work."

**A power screen done** (13 October, 16:15–22:20).
- Detections on the same outers: β_min 21 → 11/300; **Δ10 = 0.5 206 → 28/300**.
- Paired difference at Δ10 = 0.5: −0.593 (−0.646, −0.533).
- All checks pass and A has no failed fits. Independent rescoring found one
  v1 test-reference fit failure in b16, handled by its recorded bounds without
  an indeterminate outcome. Astra's earlier STATUS placement of this note
  under the null screen was incorrect; the audit receipts were correctly scoped.
- **Candidate A is closed**: its null improvement costs almost all
  discrimination. B stays deferred. The route forward is Barry's narrowed
  option 3.
  [Details](analysis/fable/calibration/v2_dev/NOTE.md).

**Option 3 recovery matrix:**
[notes/option3_recovery_matrix_20261013.md](notes/option3_recovery_matrix_20261013.md).
- Haley Lake: partly usable, with same-colony tagged survival.
- Maligne and Purcells Central: useful source-labelled census and sparse
  demographic evidence; transfer is an optional modelling assumption.
- Banff: a census crosswalk only.
- Suitable individual caribou fate histories were not found in the inspected
  public deposits; the recovered survival files are herd-year aggregates.

**Astra completed A-power and deep-dive review (14 October):**
[integrated findings](notes/astra_a_power_deep_dive_review_20261014.md),
[Haley source review](notes/astra_haley_recovery_review_20261014.md),
[caribou source review](notes/astra_caribou_recovery_review_20261014.md) and
[reproducible receipts](analysis/astra/a_power_review/).
- Independently rescored all 1,200 A/v1 T files; paired results and intervals
  reproduce. All 181 bank files, 602 A T/neighbour entries, five helpers and
  600 sealed-v1 T hashes match; 21 contract checks and nine fixtures pass.
  Supports closure of this A, B deferred, v1 V-fail unchanged.
- D3 fixes all six nuisances and tests null calibration at one corner; it
  does not bound the s/f precision needed for calibration or power. A new
  external-information design needs explicit evidence sampling, nuisance
  scope, reference feasibility and validation rules before execution.
- Haley supports a descriptive deep dive now. Seasonal age-class maxima and
  marked animals seen at different times are not a synchronous census.
  Tagged summaries add information, but conflicting source tables are not a
  reconciled demographic ledger. Define the observation model and a
  case-specific estimand/statistic before any single-colony feedback test.
- Caribou census classes and time labels remain distinct. Maligne's 2014
  groups differ in location; duplication is unresolved. Banff primary text
  confirms April 2009 deaths and earlier management, but not the archive's
  2008 label. Missing CIs do not force rate transfer; decline-period sampling
  does not prove feedback. Preserve source disagreements.

**Fable, 14 October.** Three drafts for Astra's review:
- [paper outline](notes/vortex_paper_outline_20261014.md);
- [external-information design](notes/vortex_external_info_design_20261014.md),
  design only;
- [Haley Lake descriptive protocol](notes/vortex_haley_deep_dive_protocol_20261014.md).

The recovery-matrix corrections are appended as matrix §8.

**Astra review of the three drafts (14 October, message 1614):**
[integrated review](notes/astra_three_drafts_review_20261014.md),
[paper-outline review](notes/astra_paper_outline_review_20261014.md),
[Haley protocol review](notes/astra_haley_protocol_review_20261014.md), and
[deterministic source/probability checks](analysis/astra/draft_review_20261014/).
- Proceed to the four Haley descriptive deliverables with corrected
  survivors/exposures notation, transition labels, missing-versus-zero rules
  and uncertainty wording. No further general protocol round is needed.
- Existing-results writing can proceed with four evidence categories: exposed
  reconstruction, prospectively frozen synthetic validation, exposed development,
  and optional planned work. Remove the claim that D3 excludes locality effects;
  keep Q2 descriptive after V-fail and the covariance/gate rules exact.
- The external-information study remains optional, design-only and not ready
  for implementation or either proposed execution stage. Repair its external
  observation likelihood, selection law, reference rule and overlapping seeds;
  measure the revised resource needs before any run. Seven source checks and
  exact examples reproduce the review's logical/arithmetic findings.
- Suggested first diagnostic design: unbiased information levels 30 and 300,
  b1/b3/b5/b16, fixed-K weight diagnostics without fitting; defer the larger
  factorial, timing/dependence and oracle-power arms. This is a proposal for
  the revised specification, not an execution instruction or validation.

**Fable, 14 October afternoon** (after Astra 1614):
- **Haley Lake descriptive deep dive** produced:
  [narrative](notes/haley_case_narrative_20261014.md);
  [tables, conflict register and figure](analysis/fable/haley/NOTE.md).
  The transcription was re-extracted from the PDF, and every value agrees with
  Astra's.
- [Core methods and results draft](notes/vortex_manuscript_core_draft_20261014.md),
  with the corrected claims and four evidence categories.
- External-information design cut to
  [revision 2](notes/vortex_external_info_design_20261014.md): eight cells, a
  Stage 0 no-fit diagnostic first, optional.

**Barry, 14 October 2026** (Claude chat, exact): "Yes, agreed, I think the
second caribou case study would round it off nicely, without bloat. Propose
caribou and the nine-series table to Codex."
- Proposed in board 1623: a descriptive caribou case (Banff, Maligne,
  Purcells Central) and a one-page evidence table for the nine F&H series.
- Descriptive only, from the pinned public sources and existing audits.

**Astra reviewed the completed drafts and accepted the next tranche (14 October,
message 1625):**
[integrated review](notes/astra_completed_drafts_caribou_review_20261014.md),
[Haley artifact review](notes/astra_haley_artifact_review_20261014.md),
[core manuscript review](notes/astra_core_manuscript_review_20261014.md) and
[reproducible checks](analysis/astra/artifact_review_20261014/).
- All 30 Haley source/artifact checks pass, including rebuilt tables/PNG and
  identical PDF rendering. Finish bounded wording and annotation corrections;
  no source values or empirical inference changed.
- All 17 v1 validation totals and the effect/bank receipts reconcile. Correct
  the manuscript's definitions, chronology and evidence limits. The 0.10 risk
  threshold and Delta10=0.075 describe different quantities and both stand.
- Accept Fable's six descriptive caribou deliverables and one-page nine-series
  evidence table, with source classes, denominators, endpoint conflicts and
  data dependence explicit. Fable implements; Astra reviews. No broader search,
  author contact, new interval or fitted case analysis is included.
- Revision 2 supports an optional bounded external-information Stage 0 within
  the standing development scope, after input/runtime/member-ID binding and
  tiny numerical checks. Exactly eight cells x 200 exposed outers x nine
  populations, with noisy and ideal weight diagnostics; no fitting or new bank.
  ESS<100 is an exploratory concentration flag, not a validated calibration
  gate. Measure setup/time/memory, report support/cost and stop. Stage 1 remains
  uncommissioned; this optional work must not delay manuscript production.

**Fable, 14 October late afternoon** (after Astra 1625):
- **Haley:** second-round corrections done, and the figure rebuilt.
- **Core draft:** [revision 2](notes/vortex_manuscript_core_draft_20261014.md)
  carries Astra's exact definitions and the narrowed claims.
- **Caribou descriptive case** produced:
  [narrative](notes/caribou_case_narrative_20261014.md);
  [tables, register, timeline, figure and pinned sources](analysis/fable/caribou/NOTE.md).
- **[Nine-series evidence table](notes/nine_series_evidence_table_20261014.md)**
  drafted from the audited records. It is dense; notes 9, 10 and 12 can be cut.
- Stage 0 was unstarted at that artifact handoff; its later completion is below.

**External-information Stage 0 done** (14 October, under Barry's authority;
no fits). [Report](analysis/fable/calibration/v2_dev/NOTE.md).
- **Scope:** 800 exposed outers and 7,200 K = 2,000 neighbourhoods. The
  completed diagnostics reproduce, with no unusable weights. 24:08.94 elapsed,
  peak 11.52 GiB from the raw resource log.
- **Result:** the fixed-K weighted prior-bank reference (R1) shows substantial
  weight concentration at the stronger information level.
  - Any-of-nine ESS < 100 flags: 26–83% of datasets at n = 30, and about
    100% at n = 300.
  - At the low-s corner with n = 300, noisy median ESS is 3–9 in four
    populations and 14.62 in wood turtle A; the other four range from 46.50
    to 198.53. The ideal comparator differs.
- **Consequence:** do not commission a full fitted R1 stage now. ESS is an
  exploratory concentration diagnostic, not proof of absent mathematical
  support, calibration failure or low power. **Stage 0 stops here.**

**Astra reviewed Stage 0 and the case package (14 October, message 1647):**
[integrated review](notes/astra_stage0_case_package_review_20261014.md),
[Stage 0 audit](notes/astra_stage0_info_audit_20261014.md),
[caribou artifact review](notes/astra_caribou_artifact_review_20261014.md), and
[manuscript/table follow-up](notes/astra_manuscript_tables_followup_review_20261014.md).
- Stage 0 saved results reproduce: all 800 original outers, 14,400 E draws,
  18 raw/member hashes and all reported aggregates. Binding/completeness guards
  need repairs before reuse, with no observed error in the current report.
- Core revision 2 and Haley corrections are accepted for manuscript assembly.
- Caribou count values and rebuilt artifacts reproduce. Correct the one-year
  Maligne composition-survey shift and restore WSI general survey/date notes;
  finish the bounded narrative/cross-reference repairs. Astra's earlier WSI
  prose count 25 was corrected to 23; the machine receipt was already right.
- The nine-series table has a supplied 606-word replacement candidate; shorten
  and render it as a readable page while retaining the existing detailed ledger.
- [Informative-reference proposal](notes/astra_informative_reference_proposal_20261014.md):
  evidence rejection of fresh prior theta, then one path and S/A/C selection.
  A bounded mathematical audit supports the law/envelope and identified a
  likely zero-hit limitation of tiny pilots. Forecast bank mass first, then
  measure implementation/throughput; do not interpret predictable zero hits as
  failure. Proposed 20-setting pilot: at most four workers and 30 minutes total
  on qualified deep-server, no fits/full banks/new outers. Fable implements by
  agreement; Astra audits the returned report. Stage 1 remains uncommissioned.

**Fable, 15 October.**
- **Repairs after Astra 1647** (98b771e):
  - caribou survey-year alignment, WSI notes and a content check;
  - a [one-page nine-series table](notes/nine_series_evidence_table_20261014.md),
    render-checked, with a detailed ledger;
  - Stage 0 prose corrected and runner guards added;
  - design doc consolidated.
- **Informative-sampler prototype done** (no fits; 220 s).
  [Report](analysis/fable/calibration/v2_dev/NOTE.md).
  - The sampler is verified: all tests pass, and 4 hits were observed against
    3.0 forecast.
  - Exact references at v1's C-locality cost about 3–15 CPU-h per
    population-outer, and hundreds at the low-s corner with n = 300.
  - **A fitted stage at the planned size is impractical at this locality,
    and a design decision is needed.**

**Barry, 15 October 2026** (Claude chat, exact): "The 100K CPU hours is quite
feasible on `kunanyi`!"
- Fable's corrected projection (board 1655): 2,000 retained paths are needed
  per population-outer, not 4,000. But the low-s, n = 300 corner likely
  dominates, so the full eight-cell design is about 0.2–1 × 10⁶ CPU-h
  (uncertain).
- Proposed staged plan: a measured kunanyi sampling pilot (1a), then a
  budgeted full sampling run (1b), then fits under a frozen specification
  (1c).

**Astra review, 15 October** ([integrated review](notes/astra_p1_and_repairs_review_20261015.md);
board 1657; exposure E46).
- Accepts the repaired caribou package and readable one-page table. Two minor
  prose/table-formatting edits can accompany manuscript assembly.
- Accepts the completed informative sampler as development evidence:
  likelihood/wrapper/stream checks pass, all 20 settings meet their caps,
  and all cost rows reproduce. Four hits against 3.012784 forecast do not
  validate rare-cell rates, power or the whole-study cost projection.
- The resource-impracticality conclusion above is superseded by Barry's
  clarification and this review. The K=2,000 finite-library correction is
  accepted as a candidate design; its adequacy still needs calibration.
  Low ESS does not establish equal costs across populations. The 0.2–1 million
  CPU-hour range remains a planning scenario, not a measured full inventory.
- Supports Fable's fixed-radius Kunanyi Stage 1a route. Proposed first ceiling:
  **1,000 allocated CPU-hours**, including overhead, for 720 noisy settings
  (all nine populations, four scenarios, n=30/300, outer IDs 0–9) plus 360
  shorter matched n=0 controls. A cluster smoke fixes the packing and
  attempt/time budgets before dispatch. This is a no-fit sampling pilot.
- Before scaling, enforce actual source/metric bindings, checkpoint partial
  results with deterministic resume, enforce hard total budgets, reject invalid
  inputs, handle zero-radius equality and truncated-batch exposure correctly.
  Stage 0's report also needs its recorded runner hash checked before reuse.
- **Next response: Fable.** Confirm the bounded refinement and prepare the
  repaired executable/manifest for Astra's check before large dispatch.
  Return the no-fit report before any Stage 1b campaign or Stage 1c fits.
  No new Barry questionnaire is needed for this in-scope preparation.

**Fable, 15–16 October: Stage 1a package, kunanyi smoke and final manifest**
(board 1660/1687;
[NOTE](analysis/fable/calibration/v2_dev/NOTE.md), Stage 1a section; exposure E47).
- **Smoke (one 28-core node, 10⁵ proposals per setting):** 1,080/1,080
  complete, 38 hits, every counter and hit record identical to the deep-server
  dry run. Peak RSS 0.076 GiB per worker; 0.44 allocated CPU-h.
  - The node job waited 21 h for a whole free node.
  - Its collector exited 4 on a transient `tar` "file changed"; a verified
    repack followed.
- **Repairs before scale:**
  - checkpoints at most every 60 s (per-batch fsync would be about 2 × 10⁴
    commits per second at scale);
  - a declared stop at 2,000 hits per setting;
  - 8-core jobs that can backfill partly occupied nodes;
  - a verified, retried collector pack.
  - All fixtures pass, and the smoke reproduces exactly.
- **Final manifest** `p2/p2_settings_s1a.json` (`d0dd1bff…`): budgets are
  kunanyi throughput × 3,300 s per informative setting and × 825 s per
  control. 360 workers each carry 2.06 h; 45 jobs × 8 cores at walltime 2:45.
  - Worst-case allocation is ≤ 991.5 CPU-h including the smoke; about
    760–800 CPU-h is expected.
- **Next response: Astra.** Check the law, guards and budget before dispatch.
  Barry then opens one Jumpbox window for the push, test and submit.

**Astra review, 16 October** ([integrated review](notes/astra_s1a_prerun_review_20261016.md);
board 1698; exposure E48).
- **Hold large dispatch for execution repairs.** All 1,080 saved smoke settings
  and 38 hit records reconcile across the three runs. Input/metric bindings,
  exact budgets and worker assignments pass. Nominal allocation is 991.445
  CPU-hours including smoke and collector; 742.493 worker CPU-hours is the
  throughput-based estimate before overhead.
- A reproduced partial-submission/retry failure accepts 48 jobs, allocating
  1,056 CPU-hours and duplicating 24 worker owners. The submitter needs an
  exclusive run identity, durable per-submission receipts, reconciliation and
  an enforced cumulative allocation limit.
- Hit-bearing failure fixtures reproduce orphan duplicates and loss of
  committed records during checkpoint recovery. Require an initial recovery
  boundary, validated committed prefixes and atomic tail removal; reject
  short/missing/corrupt journals, including terminal checkpoints.
- Collection needs current atomic success/failure receipts, hit-record and
  worker validation, and explicit incomplete outcomes. The documented test
  does not check the final settings/runtime binding; add the real preflight.
- Accept the 2,000-hit stop for this no-fit pilot with whole crossing batches,
  every terminal outcome retained, a stopping-valid uncertainty contract and
  separate observed time/projections. The reused smoke prefix counts once.
  The ideal inverse-binomial bias statement is not a general coverage result.
- Stage 0 runner-hash guard and the minor caribou/table repairs are verified
  and closed. No full pilot, bank build/scan, fit or Kunanyi submission ran in
  this audit; only saved-result reads and bounded unit/failure checks.
- **Next response: Fable.** Repair and rebind the finite package, then Astra
  checks the changed contracts before dispatch. No new Barry decision or
  Jumpbox window is needed for these repairs. Stage 1b/c remain uncommissioned.

**Fable, 16 October: Stage 1a pre-dispatch repairs** (board reply to 1698;
[NOTE](analysis/fable/calibration/v2_dev/NOTE.md), "Pre-dispatch repairs";
exposure E49). Runner `793e7a42…`, settings `9a7d4699…` (same budgets and
assignment), stage tar `a4c3e4e4…`.
- **Submission:** run identity, a lock, preflight before any qsub, a synced
  per-job request/accepted journal, and PBS-name reconciliation including
  finished jobs. A second dispatch is refused; `resume` submits only missing
  jobs and the collector once. The stub-scheduler fixture passes ten
  scenarios. Each completed one has 45 jobs, 360 single-owner workers, one
  collector and ≤ 991.44 CPU-h.
- **Recovery:** a zero checkpoint; checkpoints carry the committed journal's
  length and SHA-256; verified prefix and atomic replacement; missing, short,
  altered, orphan and terminal-inconsistent journals are rejected. Crashes at
  every state write and during recovery are recovered identically.
- **Collection:** a current atomic summary (`collection_ok` / `run_complete`)
  with full row, record and worker validation.
- **Preflight:** a real bound preflight runs shape, ceiling, deadline and
  fixture checks; it passes 45 × 8 at 2:45:00 and refuses the three negative
  shapes.
- **Report rule** bound into the settings: prefix-conditioned exact intervals
  (Clopper–Pearson at the budget; negative binomial at the hit stop). Storage
  maximum corrected to 21,999 records per setting; the bias remark is
  withdrawn.
- 35/35 runner fixtures pass, and the smoke replays exactly under the new
  collector.
- **Next response: Astra.** Check the repaired contracts. Barry's Jumpbox
  window is needed only after that check passes.

## Completed by Astra

- 16 October, reviewed Stage 1a at `e3870d4` with three bounded reviewers.
  Verified saved smoke/input/budget evidence, reproduced submission and
  checkpoint-recovery failures, and returned the finite repair list in 1698.
  Accepted the hit-stop refinement with reporting conditions; preserved the
  1,000-hour cap and no-fit scope. Evidence and limitations are in E48.
- 15 October, reviewed the repaired artifacts and informative sampler at
  `b781db1`, incorporating the resource clarification in `a7b8ae3` and 1655.
  Replayed bounded numerical/stream/wrapper checks, all cost arithmetic and
  Stage 0 guard fixtures; rebuilt caribou outputs and checked table rendering.
  Proposed the concrete fixed-radius Kunanyi pilot in 1657. Small synthetic
  unit fixtures ran, but no full pilot, bank scan, fit or empirical statistic.
- 14 October late afternoon, audited Stage 0 raw outputs and input/stream
  bindings, the caribou descriptive package, and core/Haley/table revisions at
  `3437fcd`. Prepared a finite informative-reference proposal with independent
  mathematical challenge and 1,544 deterministic likelihood-envelope cases.
  Corrected the earlier WSI prose row count. No new population simulation,
  reference draw, model fitting or empirical statistic was performed.
- 14 October, reviewed completed Haley artifacts, core manuscript and revised
  external-information design at `ec72dd0`, with three bounded reviewers.
  Verified the figure rebuild, frozen source/results, rate integration, seed
  enumeration and numerical fixtures. Accepted the caribou/table tranche and
  optional bounded no-fit diagnostic with execution checks. No bank loading,
  population simulation, reference sampling, model fit or empirical statistic.
- 14 October afternoon, reviewed the paper outline, external-information design
  and Haley protocol at `e614b23`, with three bounded reviewers. Checked source,
  seed and cost contracts and exact selection/variance/ESS examples. Supported
  direct descriptive/manuscript production with amendments; returned concrete
  design repairs before external-information implementation or execution.
- 14 October, independently audited the 600-case A-power comparison, including
  all paired raw T files and source/bank bindings. Audited the recovery matrix
  against primary Haley and caribou sources. Supported A closure and bounded
  writing/design drafts, with calibrated source and causal claims. No new
  simulation, T-model fit, empirical statistic or external contact.
- 13 October, independently audited all A-screen raw results and bank/source
  bindings; corrected the power-screen interpretation; audited/extended both
  Option 3 scans with primary sources and public-data checks. Accepted a fixed
  600-case practical screen after narrow repairs and proposed finite data recovery.
- 12 October, audited D3 raw outputs and corrected diagnostics, reconciled A0,
  and challenged the stopping proposal. Proposed a fixed 200-case fitted A
  screen before closure, retaining all prior empirical/validation boundaries.

- 11 October evening, reviewed the revised v2 plan, reconciled D1c rows,
  reproduced membership/rank/interval counterexamples and a cheap Candidate B
  power screen. Returned bounded D3 reporting/restart repairs. No bank reload,
  new population simulation, model fitting or empirical-statistic access.

- 11 October, reviewed v2 diagnostic 1 and Fable's D2/D3/candidate proposals.
  Verified aggregate ranges and corner means; reproduced an endpoint-tie
  arithmetic defect; returned a paired oracle design and plug-in-calibration
  qualifications. No bank reload, new population simulations or model fits.

- 11 October, independently audited the completed v1 archive, reproduced all
  gates, verified low-survival provenance and checked the empirical refusal.
  Recorded Barry's v2 direction, a bounded development brief and exposure E30.
  Findings and reproducible receipts are linked above.

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

- 16 October, Stage 1a pre-dispatch repairs per 1698: journalled, resumable
  submission with fixture; atomic journal recovery; validating collector;
  bound preflight; report rule. Exposure row E49.
- 16 October, Stage 1a: kunanyi smoke (1,080/1,080, cross-machine identical);
  checkpoint-cadence, hit-stop, job-shape and collector repairs with new
  fixtures; budgeted final manifest and stage tar. Exposure row E47.

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

1. Astra checks Fable's Stage 1a pre-dispatch repairs (runner `793e7a42…`,
   settings `9a7d4699…`, `s1a_submit.sh` `facded63…`, stage tar
   `a4c3e4e4…`) per review 1698. Then, in one Jumpbox window, Fable pushes the
   tar and runs `s1a_submit.sh … main 45 8 02:45:00 1000 0.44`; the preflight
   runs first and the collector emails Barry. The pilot stops at its no-fit
   report; full-library Stage 1b and fitted Stage 1c remain uncommissioned.
   Core/Haley, material caribou and one-page table findings are closed.
   Stage 0 and the bounded sampler prototype are complete and audited.
   D3, D1c2, A-screen and A-power have been audited; A is closed and B remains
   deferred. The original two-candidate route meets its stop rule. Any new
   inferential procedure needs a separate prospective protocol/freeze before
   untouched validation. Retain the failed corner and low-power result; do
   not retune beta_min to obtain O1 or silently loosen the null gate.
2. Retain the unresolved historical input/estimator and census-class questions.
   Do not infer software unavailability from failed retrieval or silently change
   raw values, interpolation or annual-increment definitions. Stage B remains
   unpassed, even if a reconstructed target is adopted.
3. Retain failed feasibility checks and measure any revised design's costs.
   Serious work follows the standing remote-compute authority and measured
   resource selection; the 220-core-hour proposal remains withdrawn. Empirical
   tests remain blocked by v1's failed null gate. They would require a separately
   frozen v2 procedure that passes its prospective validation rules.
4. Complete the named close-prior-work checks and the frozen Stage A search.
   Final Nabutanyi–Wittmann text and Drake–Griffen 2009 passage-time methods
   remain unverified; the orientation search is not a completed systematic
   review. Phase II's additional-series search is a suggestion, not a commitment.
5. Part 2, genetic extensions and new forward-response access remain parked.

The current paper route is the core reconstruction/methodological results plus
narrowed descriptive deep dives, following Barry's 13 October direction.
Formal empirical feedback tests remain conditional on an adequate new design
and prospective validation. A failed gate is not evidence of absent feedback.

## Correspondence checkpoint for this Astra task

- Project: `project` (active view).
- Discussion: 70; launch message: 826.
- Last full retrieval `next_after`: **1698**; exhausted `through`: **1698**.
- Explicit acknowledgement: through actual message **1698** in discussion 70.
- Next retrieval: omit `through` to capture new messages, and use `after=1698`.

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
- Read through 1700 in full and acknowledged through **1700**. Fable's latest
  posts: 1687 and the repair post replying to 1698.
- Next retrieval: use `after=1700` on discussion 70.

## Coordination note

Both agents currently work in the same WSL checkout,
`/home/bwbrook/papers/project`. Commit before handing off, and do not edit the
other agent's files. The Mac mini checkout is canonical. Fable synchronises its
commits there by pushing to a temporary branch and fast-forwarding `main`, after
checking that the Mac working tree is clean. There is no GitHub remote yet.
