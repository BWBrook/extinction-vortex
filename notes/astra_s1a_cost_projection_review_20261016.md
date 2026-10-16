# Astra: Stage 1a cost projection review

Reviewed `dc86ef8d56ad9bdc001f08068a269a82b24e4a9f`: the no-fit report,
`p2_report.py`, accepted `report_rule`, `collect_deep.json` and
`s1a_report.json`. This review covers cost arithmetic and statistical
interpretation. Archive integrity, scheduler accounting and the next-stage
design belong to the other reviewers.

**The arithmetic reproduces; the headline uncertainty needs qualification
before it informs a resource commitment.** The 861,632 CPU-hour figure is a
gross plug-in planning projection with four unresolved costs replaced by
one-sided lower limits. Its 749,015–981,136 bootstrap range is conditional
empirical resampling spread, not a calibrated confidence or predictive range
for the full cost. No new sampling, fitting or dispatch is recommended here.

## Verified arithmetic

Independent calculations from the 1,080 saved rows give:

| Inventory component | CPU-hours |
|---|---:|
| n = 0 | 21,340.472570 |
| n = 30 | 117,749.300658 |
| n = 300 | 722,542.225584 |
| Gross total | **861,631.998812** |

The difference from the saved total is floating-point rounding
(`1.2e-10` CPU-hours). For a positive-hit, non-hit-stopped row, the point
projection simplifies correctly to `2000 * cpu_seconds / (3600 * hits)`.
The one hit-stopped row uses observed CPU through its crossing batch. These
are mixed observed and estimated costs, as the report declares.

All complete-nine-population availability counts reproduce: at caps
10/25/50/100/250/500/1,000 hours, n = 30 gives
6/14/23/29/37/40/40 datasets and n = 300 gives
0/2/8/13/19/23/33. Unresolved populations remain unavailable rather than
being silently omitted from their datasets.

Direct binomial-CDF inversion independently reproduces the suffix retention
intervals for the three largest one-hit projections. Their transformed cost
intervals are 331.719–73,000.745, 327.539–72,080.870 and
317.662–69,907.348 CPU-hours for settings 524, 335 and 836 respectively.
The six exposed censored rows have sensitivity intervals and no formal
retention intervals. Setting 576 has zero exposure, no cost estimate and no
interval; excluding it from cost means is explicit, with that control cell's
mean consequently based on nine observed outers.

## Findings, ranked

### MAJOR: the bootstrap range does not quantify full-budget uncertainty

`p2_report.py:103–126` resamples ten fixed cost estimates separately within
each population/scenario/n cell (nine in the no-exposure control cell).
Four zero-hit settings enter as fixed lower-limit substitutes. Replaying the
same algorithm and seed exactly reproduces its quantiles:

| Resampling calculation | 5% | Median | 95% |
|---|---:|---:|---:|
| Published independent cells | 749,015 | 860,011 | 981,136 |
| Pair n values within population/scenario/outer | 747,085 | 861,135 | 990,477 |
| Whole nine-population outer within scenario | 742,522 | 860,672 | 985,423 |

The paired calculations are sensitivity checks, not replacement calibrated
intervals. Pairing matters conceptually because evidence levels share an
outer, but it changes this numerical range only modestly. The principal
limitation is treating the estimated costs and unresolved substitutes as fixed
pseudo-data. Their observed spread can include Monte Carlo noise, but the
bootstrap does not propagate the per-setting retention uncertainty separately,
identify that noise, or represent the unknown upper costs of zero-hit settings
and unobserved expensive outers. It does not establish a 90% full-design
budget range or guarantee that the total is below one million hours.

Two bounded sensitivity calculations show the practical distinction:

- The four zero-hit substitutes contribute **46,759.915** hours to the
  inventory. Replacing only those substitutes by ten times their current
  values gives **1,282,471.238** hours.
- Moving only setting 524 from its point estimate to its own transformed
  upper interval endpoint gives **2,284,681.949** hours.

These are illustrations, not estimates or joint confidence limits. They do
not prove that the total is biased downward or will exceed 861,632 hours.
They show that the narrow bootstrap range cannot be used as budget assurance.

**Finite repair:** retain the verified point calculation, label the bootstrap
as *conditional empirical resampling spread of plug-in costs, with zero-hit
costs fixed at their lower limits*, and explicitly state that it excludes a
calibrated allowance for unresolved rates, unseen outers and future throughput.
Use paired outer resampling if presenting this sensitivity as resampling
outers. Replace the report's “7.5–10 times” cost range with the point estimate
of about 8.6 times 100,000 hours plus the stated uncertainty limitation.
Obtaining a defensible upper resource allowance is a separate design/resource
decision; it is not achieved by increasing bootstrap repetitions.

### MINOR: transformed retention intervals concern mean cost, not realised runtime

`cost()` maps a retention interval through `K * measured_CPU_per_proposal / p`.
This is an interval for projected **expected** CPU cost conditional on treating
measured CPU per proposal as fixed. It is not a predictive interval for the
actual stopping time of a future run and does not include throughput variation.
For a hit-stopped row, the equal lower/upper values merely record an observed
cost; they are not an uncertainty interval for replicating that setting.

The zero-hit “time to K ≥ …” wording likewise denotes an approximate
one-sided confidence lower limit on expected cost under that fixed-throughput
assumption, not a hard minimum runtime. The report uses `3/N` from the full
stream. Exact one-sided 95% suffix bounds give **608.115, 586.021, 587.686 and
559.465** hours (settings 242, 512, 536, 833), about **0.14%** above the
reported substitutes. This is numerically immaterial but makes the conditioning
and approximation explicit.

**Finite repair:** label the table “projected expected CPU-hours to K” and its
intervals as transformed retention intervals at observed throughput; retain
the sensitivity qualification for censored rows. Mark zero-hit limits as
approximate one-sided expected-cost limits, or use the exact suffix expression
`-expm1(log(0.05) / suffix_proposals)` for their retention upper bound.

### MINOR: the scenario maximum silently excludes unresolved settings

The n = 300 `null_prior_predictive` scenario table shows a maximum of
**125.069** CPU-hours among **89** resolved estimates. Its omitted setting
242 alone has an expected-cost lower-limit substitute of **607.262** hours.
Unlike the population table, the scenario table gives no unresolved count.
The apparent scenario maximum is therefore misleading without an exclusion
label, although the unresolved row is disclosed elsewhere.

**Finite repair:** show the resolved denominator and unresolved count in both
tables; call this the largest resolved point estimate, not the scenario's
maximum cost. Preserve unresolved cells and their limits separately.

### MINOR: gross inventory is not additional Stage 1b compute

`pilot_hits_counted` is recorded but never used to reduce `cpu_h_total`.
The 861,631.999 hours describe the gross total-to-K projection. Under a simple
matching accounting convention, subtracting the **733.873** worker CPU-hours
already spent gives **860,898.125** additional projected worker hours. This
small difference does not affect the scientific or resource-scale conclusion,
and it is not an allocated-node-hour estimate.

**Finite repair:** identify the headline as gross worker CPU-hours and report
pilot credit separately if describing remaining work. Keep the scheduler's
allocation accounting distinct. Also change “Everything else ended at its
proposal budget” to “All other completed settings …”, retaining the seven
censored rows.

## Evidence and limits

New evidence: `analysis/astra/s1a_cost_projection_review/check_costs.py`,
`cost_checks.json` and `cost_checks.log`. The independent script does not
import the sampler or reporting implementation. It records source hashes,
per-component totals, exact bootstrap replay, two small paired-resampling
sensitivities, direct binomial inversions, zero-hit limits, availability counts
and the gross/additional accounting distinction.

Executed locally with Python 3.12.3 and NumPy 1.26.4; numerical thread limits
were all one. The final run took **0.29 seconds**, peak RSS **40,100 KiB**.
An initial path-resolution error was corrected before the successful runs;
two successful arithmetic passes each took less than one second. No SciPy
installation, remote execution, population simulation, bank scan, model fit,
new extrapolation model or scheduler command occurred. Peer code, STATUS and
exposure records were not edited. This review does not authorize Stage 1b/1c.

16 October 2026, 20:28:15 AEDT (Australia/Hobart).
