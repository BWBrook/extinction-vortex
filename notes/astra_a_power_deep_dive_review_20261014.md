# Completed A-power screen and narrowed deep-dive review

Codex (Astra), 14 October 2026. Reviewed common WSL/Mac commit
`20c85745f417c093b22743a304d0521c962cd986` and discussion 70 through message 1606.
Barry's core-paper-plus-narrowed-deep-dives direction is recorded in STATUS
from Claude's 13 October chat relay; this review does not enlarge that authority.

**Disposition:** accept closure of candidate A and retain B's deferral. Support
Fable's proposed core-paper outline, a specification for the external-information
experiment, and a Haley protocol draft, with the amendments below. These are
writing and design tasks. No new simulation, empirical test or author contact
is commissioned by this review. Fable's response and drafts are next; Astra
reviews them before execution is considered.

## 1. Completed A comparison: result accepted, scope retained

Independent rescoring of 600 A and 600 paired v1 raw T files reproduces every
outcome and p bound, all reported marginal residual means and distance summaries,
the paired tables, exact binomial intervals, exact McNemar tests and Newcombe
method-10 intervals. K = R_train = R_test = 2,000; the two blocks each use 300
already exposed outers.

| Effect | v1 rejects | A rejects | A minus v1, paired 95% interval |
|---|---:|---:|---:|
| beta_min | 21/300 | 11/300 | -0.0333 [-0.0627, -0.0083] |
| Delta10 = 0.5 | 206/300 | 28/300 | -0.5933 [-0.6459, -0.5326] |

Paired tables (both, v1 only, A only, neither) are `[9,12,2,277]` and
`[27,179,1,93]`. Exact paired p-values are 0.012939453125 and
2.3621602174e-52. At the larger effect, mean T1/T2 standardized residuals
fall from 2.875/3.116 to 1.300/1.548 and the median maximum original-C
neighbourhood radius rises from 0.4360 to 3.4893. These describe the changed
reference and practical loss of discrimination; they do not identify its cause.

The modest one-corner null improvement does not repair v1's failed validation
gate, and A has not passed its own prospective calibration. Closing this
specified five-feature candidate is justified. The result does not establish
that every informative reference or alternative conditioning statistic must
lose discrimination. Retain the original risk-defined effect and the failed
corner; no third retrospective candidate follows from this review.

Reproducible receipts are in [the audit directory](../analysis/astra/a_power_review/).
The source-contract review checks all 600 IDs, 5,400 selected population series,
source bindings and seeds; 21 receipt checks and nine focused fixtures pass.
All 181 primary-bank files, 602 A T/neighbour manifest entries, nine compact
files and five helpers match. All 600 baseline T files match the earlier sealed
v1 audit. Observed paired T values differ by at most 1.56e-9; substituting the
baseline observed vector leaves every A p bound unchanged.
The fixed runner/helper binding and missing-T resume guards work. The raw audit
uses independently written covariance/rank calculations rather than importing
the production scorer. It performs no new simulation, T-model fitting or
nearest-neighbour reconstruction. Baseline incomplete fits are handled by
complete training rows and fixed-denominator worst-case test p bounds.
A has no failed fits; the stronger-effect v1 block has one test-reference
fit failure, handled by its recorded p bounds without an indeterminate outcome.
Present-payload hashes cannot prove absence of intermediate
mutation or restart.

## 2. External-information experiment: revise the question before implementation

Message 1606 says D3 and v1 "bracket" the precision of independent survival
and fecundity information needed for calibration and power. They do not.
D3 fixed **all six** nuisance parameters, including environmental variation,
autocorrelation and catastrophe parameters, at one low-survival corner and
tested null calibration. It supplied neither an s/f-only precision experiment
nor an oracle power endpoint. These are contrasting reference-information
experiments that motivate a new question; they provide no numerical precision
bound and no demonstrated monotonic relation between width and performance.

The draft should define:

1. The estimand and repeated-experiment law for external evidence E and focal
   counts N. A prior deliberately centred at the true parameter is an ideal
   information benchmark. Realistic external estimates need repeated noisy E,
   their bias law, and a declared relationship to N. If E is fixed instead,
   identify the conditional target and validate it as such.
2. Which of the six nuisances receive information. Include a separate s/f-only
   intervention if that is the scientific question; distinguish the residual
   uncertainty in environmental and catastrophe parameters. Choose and state
   the scale and units for precision and bias rather than equating arbitrary
   prior width with study sample size.
3. Null calibration and alternative discrimination, evaluated under the same
   evidence-generation and conditioning procedure. Prespecify effects, sample
   counts, failure handling and decision rules before viewing outputs. Keep
   exposed development and future prospective validation separate.
4. A feasible reference construction. Reweighting a finite primary bank needs
   support, weight concentration and effective-sample-size diagnostics under
   endpoint and C selection; nominal bank size does not establish adequacy.
   A new bank requires measured costs and a bounded design before launch.

The experiment can support a methodological section without pretending that
its simple population model is already a valid Haley or caribou null.

## 3. Deep dives: usable descriptive evidence, unresolved test specification

The recovery matrix improves feasibility. Several categorical conclusions
should be narrowed before they enter the paper or determine priors:

- **Rates measured during decline may contain feedback.** Measurement during
  decline alone does not prove that feedback is present or quantify it. Do not
  impose the null by removing an inconvenient period, or treat a decline-phase
  estimate as an independently known no-feedback baseline.
- **Same field programme does not mean no additional information.** Marked
  survival and age composition add information absent from total abundance,
  even when their observations overlap. They need a joint or conditional
  observation model. Feeding a posterior fitted to these counts back as an
  independent prior would reuse information.
- **Missing individual records or published confidence limits does not force
  transfer.** Available aggregate estimates and uncertainty can support an
  explicit approximation or a sensitivity analysis, subject to adequacy checks.
  A transferred rate is another assumption to assess, not a verified remedy.
- **An external predator-prey driver is not logically excluded by closure or
  absence of direct abundance feedback.** It can violate the implemented
  stationary null or its environmental law. Specify that mismatch and the
  relevant alternative rather than claiming that any closed no-feedback null
  cannot represent it.
- **Availability is search-bounded.** Say that no suitable individual fate
  histories were found in the inspected deposits. The Lamb survival CSV is
  herd-year aggregate evidence; public BC locations are not complete fate
  histories. Neither supports a universal claim of non-public availability.

The [Haley source review](astra_haley_recovery_review_20261014.md) resolves the
count convention: seasonal maxima by age class, with all marked animals seen
through the season included at intensive colonies. These need not be a
simultaneous census. It verifies 97 non-pup tagged exposures/64 survivors and
24 pup exposures/11 survivors, but also documents conflicts between survival
and abundance tables and between tabular and narrative totals. The records
are not yet a consistent demographic ledger. Keep those conflicts visible;
do not repair them from arithmetic alone.

Haley is the first protocol candidate. Its tagged survival, stage composition,
litters and movements support a useful source-grounded descriptive deep dive.
The first draft must settle colony identity, census timing/aggregation, ages,
sex structure, immigration, observation error and the target window. Keep
1987's 18-versus-28 conflict and the unsourced endpoint years visible. The
1996 transplant has no verified Haley source colony; do not code it as a
Haley removal. Do not pool repeated marked-animal exposures as 97 independent
Bernoulli trials merely to obtain a narrow interval.

The existing nine-population random-intercept T1-T4 procedure is not a ready-made
one-colony test: a single population does not identify the same between-population
random effect. Define the case-specific statistic/estimand and map the observation
process into the generator before considering calibration. A descriptive case
study is already useful while a formal feedback test remains conditional on
that specification and prospective validation. Reduced power in one case is
a concern to measure, not a foregone result.

The [caribou source review](astra_caribou_recovery_review_20261014.md) reproduces
all 21 Maligne fall sums and the critical Purcells Central census-class
crosswalk. Maligne's two 2014 groups have different locations, so they are
not exact duplicate records. An entirely blank 2010 row remains unresolved;
all numeric rut and recruitment records reconcile age/sex sums to totals.
Blank fields alone therefore do not establish missing classified animals.
The Banff primary paper is accessible and documents the April 2009 avalanche
and recovery management around 2002, but not the reason for the archived
2008 terminal label. Zero entries for the archive's six treatment categories
do not establish absence of all management.

Caribou can follow after the census-class and time-label crosswalk is explicit.
Preserve observed counts, minimum known alive and adjusted estimates as distinct
source fields. Retain Banff's 2008 archived zero versus the documented April
2009 deaths, and Maligne's 2014 duplicate-looking groups, as unresolved source
questions. Neither licenses a silent year shift or deletion. Author contact
remains Barry's decision.

## 4. Paper outline and next response

Support the core-results outline in 1606: the exposed reconstruction, v1 V-fail,
paired oracle/reference evidence, completed A and B development screens, and
the Q2 discrimination profile. Present failed calibration as a limitation of
the specified inferential procedure, not evidence for or against empirical
vortex feedback. Keep prospective validation claims distinct from development
and from the historical reconstruction, which remains unpassed.

Fable next: correct the recovery-matrix claims, provide the paper outline,
external-information design and Haley descriptive/model protocol. Astra next:
review those finite drafts. No empirical run or additional compute is started
by the present audit.
