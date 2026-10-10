# Astra review of protocol 0.9 and the draft freeze package

10 October 2026, Hobart. Reviewed handoff 1359 and immutable commit `f74f4f7`.
The WSL and canonical Mac checkouts were clean and matching at the start.
Fable's running screens and designated-bank jobs were left untouched; no
partial running outcomes were inspected.

**Disposition: accept the proposed scientific specifications for the next
package, with executable completion still required before the freeze.** The
pending numbers alone will not finish the package: the stress sampler and
the complete validation aggregation/gate path are still absent. There is no
new decision for Barry and no reason from this review to interrupt the
current null/feedback screens or designated-bank construction.

## Scientific specifications accepted, with explicit scope

- **M_D.** Accept the proposed Delta ~ Uniform(0, 2) terminal shift and uniform
  annual step time as design distributions for synthetic deterioration
  scenarios. The linear, accelerating and step equations are coherent;
  subtracting m(t) from the stationary AR state shifts the mean without
  feeding the trend back through the AR recurrence. These are specified
  stress distributions, not empirically estimated environmental priors.
  Their selected distributions will differ after S and A. Report that
  distinction when interpreting Q2 rates.
- **Effect scale.** The terminal multiplier on recruitment rate and
  pre-catastrophe survival odds is exp(-sigma * Delta). At Delta = 2 it ranges
  from about .961 at sigma = .02 to .135 at sigma = 1; it is .369 at the
  development pooled median sigma = .498. Thus equal Delta is not a matched
  vital-rate or extinction-risk effect across populations. Q2 describes
  these alternatives; it does not identify a mechanism or make them
  effect-matched competitors to M_A.
- **M_O.** Accept the recorded-count selection rule, absence of a second
  latent-extinction requirement, and the two proposed detection laws. The
  chosen latent start, round(n0/p(n0)), with the first recorded count fixed
  at n0, is an explicit plug-in scenario convention. It is not exact
  conditioning of a latent-abundance model on an initial binomial census.
  Keep that limitation in the specification; no extra latent-initial prior
  is needed for this bounded misspecification experiment.
- **Stress law.** The revision resolves the earlier mixture objection:
  300 intended parameter sets drawn once, retained, and never replaced after
  a timeout. Report unresolved counts and lower/upper conservative rejection
  summaries on the intended denominator, with interval uncertainty. This is
  a descriptive fitted-parameter check, not a fifth null gate or local
  conditional-calibration claim.
- **Radius strata and development screens.** Accept the fixed development
  cut points with ties assigned to the lower bin, independent of validation
  draws. The two 200-dataset screens are explicitly retained; their completed
  results and existing stopping rule remain pending. Beta_min is the minimum
  *risk-defined* effect on the declared grid, not a demonstrated minimum
  detectable effect. Its poor development power remains in the record.
- **Inventory.** The new table covers the previously omitted sensitivities
  and identifies bank reuse and access-dependent work. The approximately
  3,300-core-hour total is a useful planning inventory. The stronger claim
  that total cost equality has now been measured is unsupported (below).

## MAJOR: finish the executable validation contract before freezing

The draft package §6 includes stress block 17, but the code it names does
not implement that law. `e2e_benchmark.py:38` loops until selection succeeds;
its interface only supports fixed parameters, drift and detection. It has no
one-million-attempt cap, no 300-set empirical-library parameter draw, and no
sampling-budget outcome. The scorer likewise has no such outcome.

Implement the accepted stress law with a persisted parameter-set manifest,
stable trial IDs, the exact attempt budget and an unresolved outcome included
in descriptive fixed-denominator reporting. A tiny fixture should force all
attempts to fail and demonstrate termination, preservation of the original
parameter set and intended count, and no replacement. The successful branch
should retain the same reference/estimator procedure as other trials.

The ten-chunk-per-scenario design also needs an executable assembly and gate
step. `run_arms.sh` checks process exit and line count; the scorer emits
per-directory counts. Neither currently assembles ten chunks into the declared
1,000/300-trial scenarios or evaluates the complete scientific gates. Mocked
duplicate-row and all-unresolved launches still print DONE: this establishes
process completion, not passing validation.

One compact run manifest and collector should specify:

- each scenario/chunk, output directory, seed, intended trial IDs and final
  pooled denominator; reject duplicates and retain missing trials;
- the four null bounds, the beta_min power bound and the scope of outcome
  labels; keep the fixed sample sizes and do not introduce optional stopping;
- block 17's single execution point: it appears in the validation table and
  again alongside the empirical run. Reconcile its descriptive, non-gating
  status with the phrase "any scenario" in the fit-failure stop rule; keep
  sampling-budget failures distinct from estimator failures;
- the >2% failure numerator and denominator, including observed, training and
  test datasets. The current R `failed` field means a dataset with any missing
  T1–T4 statistic, not four separately counted fit attempts. Define the
  scenario calculation and missing-output treatment before observing final
  validation, then test the threshold;
- at most three simultaneous bank-holding e2e processes on deep-server unless
  another capacity check supports more. The generic launcher starts every
  supplied tuple; ten processes at approximately 28 GB each exceed the host's
  documented memory. The pilot supports the three-process configuration;
- exact empirical analysis IDs and sensitivity-bank substreams. The primary,
  stability and iid families are distinct and correct, but three sensitivity
  designs reuse the 8.7e12 family while the builder restarts task numbering
  on every invocation. Allocate disjoint offsets or declare intentional
  paired streams explicitly.

Record the final executable revision, configuration/input/bank hashes and
runtime versions in the package. Label future empirical/sensitivity entry
points by their actual implementation status; the current synthetic-only
e2e program does not execute the complete §7 inventory. Filling pending bank
numbers does not by itself freeze a runnable procedure.

## MAJOR: retain the selected alternative-draw evidence promised by the protocol

`bank.simulate_chunk` returns M_D shift and step time and, for M_O, latent
counts. `fresh_selected` discards the M_D parameters, and the outer-trial
writer retains only M_O's latent endpoint. This does not change the tested
selected-path distribution, but it falls short of §3.2's statement that the
shift, step time and latent counts are kept per draw.

Persist the selected outer parameters and the agreed latent/recorded evidence,
or narrow the storage contract explicitly while preserving enough evidence
to audit the claimed alternative and selection. In particular, retain
selected Delta/tau so the prior proposal can be distinguished from the
distribution remaining after endpoint selection. This is small per-outer
metadata, not a request to retain all rejected simulations.

## MINOR: keep the cost claim calibrated to what was timed

`alt_check_v1/gen_times.json` measures only fresh outer generation: 13 scenarios,
20 datasets each, 5.00–9.19 CPU-seconds per nine-population dataset. This is
under .671% of the prior 1,370-second end-to-end benchmark. It verifies that
outer generation is cheap. It does not establish total costs within 1% across
scenarios, as `alt_check_v1/NOTE.md:59` claims: scenario C changes the libraries
and hence the 4,001 datasets to be fitted. Their optimizer/fallback cost can
change. The three R=20, K=50, two-trial smoke arms are plumbing checks.

Keep the total as a projection with unmeasured scenario-dependent fitting
costs. Full-path spot timings can refine it if needed; another exhaustive
benchmark is not required merely to retain a provisional resource estimate.
Also parameterize `time_generators.py` from the recomputed beta_min: its
current constant remains the development value even when the bank driver
has recomputed the final effect target. This affects those timings, not bank
generation or the separately saved effect calculation.

## Checks completed and next handoff

The [generator audit](../analysis/astra/protocol09_review/generator_audit.json)
records eleven grouped checks in 2.9 seconds: exact null/M_A parity against
`fb28d8a` across 36 configurations with 2,000 draws each; all 28 existing
limiting checks at reduced 5,000-draw size; deterministic drift/AR/gap and
observation-stream checks; and actual v1/v2 scorer runs retaining three
successive trials and rejecting a NaN in the second trial. Early latent
stopping does not corrupt the selected M_O law: an earlier latent count <=1
implies an earlier recorded count <=1 and exclusion.

The [run-contract audit](../analysis/astra/protocol09_review/run_contract_audit.json)
records shell syntax, mocked child-failure/incomplete-output checks, source
hashes, 540 unique designated-bank task seeds and 170 unique proposed
validation seeds for chunk indices 0–9. Both audits use immutable source
copies. Reproduce with the corresponding `.py` files using
`/home/bwbrook/papers/dsipa-dev/.venv/bin/python`; no packages were installed.

**Next: Fable.** Complete the running evidence archive, retain its full failure
denominators, add the missing executable steps and selected-draw provenance,
qualify the cost claim, and return the completed freeze package. Astra then
checks the completed receipts and final procedure. These are agent-owned
completion tasks within the existing scope. No empirical p-values, R fits,
new large runs or changes to live jobs occurred in this review; only bounded
local synthetic and mocked checks were run.
