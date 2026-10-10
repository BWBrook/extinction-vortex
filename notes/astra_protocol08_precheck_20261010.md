# Astra pre-handoff check of the 0.8 development work

10 October 2026, Hobart. This is a bounded early review, not a completed
protocol handoff or freeze approval. At wake, WSL held committed code at
`0430737` (including the `d16fe45` bank builder), plus Fable's uncommitted
draft 0.8 and `dev_design_v1` evidence. The canonical Mac was at `567dd7c`.
Fable's working files and jobs were left untouched. Their inspected hashes
are recorded in
[the working-evidence snapshot](../analysis/astra/protocol08_precheck/working_evidence_sha256.json).

**Main finding: the completed pilot has very low detection at the existing
risk-defined effect target. Keep that result and the target; do not raise the
effect to obtain a favourable power label.** Barry's ar_cat-primary and
RI-primary decisions remain settled. Fable owns the formal handoff and code
repairs; Astra will review the completed validation design.

## 1. Completed synthetic power screen, independently reconciled

The remote screen is complete: five arms of 30 datasets, each with
R_train = R_test = K = 2,000, under the constructed development banks.
The source files match `0430737`; the power driver is uncommitted locally but
matches its remote source hash. I independently recomputed the mean,
covariance, distances and conservative tail counts from all 150 raw T files.
Every file contains exactly 4,001 ordered set IDs, all four statistics are
finite, and failure flags are zero. Both logged p bounds and every outcome
match; fallback totals also reconcile. No covariance required shrinkage.

| Outer scenario | Reject / intended | Two-sided exact 95% interval |
|---|---:|---:|
| ar_cat null | 1 / 30 | 0.00084–0.17217 |
| M_A at beta_min | 1 / 30 | 0.00084–0.17217 |
| M_A at 2 beta_min | 2 / 30 | 0.00818–0.22074 |
| M_A at Delta10 = 0.3 | 8 / 30 | 0.12279–0.45889 |
| M_A at Delta10 = 0.5 | 18 / 30 | 0.40603–0.77344 |

There are no unresolved trials in these five arms. The
[audit receipt](../analysis/astra/protocol08_precheck/power_screen_audit.json)
records the remote root, all 160 output hashes, source hashes, metadata and
reconciliation results. This was read-only analysis of existing synthetic
statistics: no new population simulation, R fits or empirical p-values.

These are development results conditional on the current banks, not the
prespecified validation experiment. They strongly warn against expecting the
70% power gate to pass at beta_min. The null arm is too small to establish the
8% false-alarm ceiling. Similarity of calibration radii C alone would not
demonstrate low power; the fitted-statistic screen now provides direct evidence.

If the frozen power gate fails, a non-rejection of the empirical null must be
O3, insufficient discrimination. A calibrated empirical rejection can still be
O2. Neither outcome is established by this pilot, and low power is not evidence
that feedback is absent. The larger-effect results remain an honest detection
curve; changing the scientific target after inspecting it would be a separate
author amendment, not routine tuning. No new questionnaire is needed merely
to retain the current target and its stated consequences.

## 2. Effect calculation and design interpretation

The inspected effect-target source matches `0430737`, and all eight design-run
source hashes and three bank-build source hashes match their stated commits.
The code applies the existing grid and pooled component-wise library-median
recipe. At N0 = 20 it records null risk 0.42217, risk 0.50952 at Delta10 = .05,
and 0.55255 at Delta10 = .075. The corresponding differences are .08735 and
.13038, selecting beta_min = 0.974519. No effect-grid path overflow is recorded.
I checked the algorithm and arithmetic, not an independent simulation replay.

The parameter recipe is a model-based reference point, not an estimate of a
universal effect across the nine census classes. Describe g(10) = .925 as a
7.5% multiplier reduction in **survival odds and recruitment rate**. It is not
a 7.5% reduction in survival probability. Likewise, s + f = .875 describes
the baseline parameter sum, not an independently established marginal growth
rate under the AR environment, catastrophes and selection.

Replacing a hypothetical shortened-window corner with the added environmental
dimensions is reasonable for the fixed nine schedules. The listed numeric
corners provide concrete development cases; final settings remain unfrozen.
Their selection probabilities and fitting costs should accompany the final
allocation rather than assuming the four prior-predictive benchmark trials
represent every corner.

The measured radii in constructed banks are an improvement over projections.
However, the empirical maximum-radius percentile (64th under ar_cat) supports
the narrower statement that its largest radius is typical of the simulated
distribution. It does not establish local conditional calibration or density
throughout the nine-population C configuration.

The proposed 300-dataset stress check draws parameters from empirical
libraries, then generates fresh data. Specify the endpoint-selection rule and
whether parameters are retained or redrawn on rejected trajectories: those
produce different parameter mixtures. Also record the resulting C distances.
Without conditioning or concentrating those datasets near empirical C, this
is a fitted-parameter predictive stress check, not direct validation of the
conditional law at empirical C. Keep its descriptive status and interpret
its support accordingly; no extra p-value-driven gate is proposed.

## 3. Committed code: prior repairs accepted, three narrow gaps remain

A bounded read-only delegate tested immutable `git show` copies with tiny
fixtures; no real population simulation or R fitting was used.

- The scorer now distinguishes v1/v2 fields. Missing test rows and duplicate
  set IDs are rejected. The >2% training-failure rule, covariance failure
  outcome, fixed-K minimum bank size and fallback counts behave as specified.
- **Parse and absent-file failures:** a ragged T CSV still raises ValueError
  outside outcome handling; an arm with metadata but no first checkpoint
  raises FileNotFoundError. Classify those as malformed/missing and retain the
  intended denominator, including an entirely absent arm using the declared
  run configuration. Do not substitute a completed-trial denominator.
- **Shard integrity:** the loader checks sequence, seed and raw-draw count but
  accepts repeated global draw IDs and inconsistent trajectory/parameter row
  counts. Check selected count, all field lengths, and strictly increasing
  in-range IDs within each shard before constructing libraries. The builder
  produces globally ordered IDs, so these checks need no speculative format.
- **Upper-bound reconciliation:** the v2 scorer promises to check both logged
  bounds but checks only p_lo and outcome. An altered p_hi passed the fixture.
  Compare it too. The independent screen audit above verified both bounds.

These are prospective integrity repairs; they do not show that current banks
are corrupt or that the completed power results are affected. I did not read
all 17 GB of bank payloads or independently replay the coverage arrays.

## 4. Cost and handoff

The archive measures 77.5 core-hours for both development bank variants and
5,112.69 CPU-seconds for the four-dataset benchmark including setup. The quoted
1,154 CPU-seconds per dataset subtracts 495.1 **wall** seconds of bank loading
from the CPU total before dividing by four. Label that an amortised estimate
using a roughly single-core setup assumption, or measure setup CPU separately.
The unadjusted four-dataset mean is 1,278 CPU-seconds (0.355 core-hours).

The approximately 2,420-core-hour inventory is useful planning but is not yet
complete: it omits the separately promised independent primary reference bank
and empirical/sensitivity/stability fits. M_D and M_O remain unimplemented and
their costs assumed. Include those small or uncertain components explicitly
and preserve the difference between measured cost and projected elapsed time.
The completed power screen provides a closer scheduling comparison: its first
wave ran three arms with 18 R workers each. After subtracting each arm's bank
load, the slowest arm took 3,086.8 seconds for 30 trials. Approximately 90
trials per 3,087 seconds is 105 trials/hour, suggesting **about 70 hours for
7,300 trials** before bank construction and other overheads, rather than 45.
This remains a small-pilot extrapolation, not a guaranteed duration, but uses
the proposed concurrent configuration instead of dividing by nominal cores.
This is not a request for a new compute-permission gate; existing resource
authority applies within the authorised scientific work.

Next response: Fable supplies the completed protocol/results handoff, repairs
the three guards, and resolves the stress-check and cost specifications before
the final validation freeze. No production validation or empirical testing is
approved by this precheck.
