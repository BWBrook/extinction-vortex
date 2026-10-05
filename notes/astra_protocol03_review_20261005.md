# Review of vortex protocol draft 0.3

5 October 2026, Hobart. Astra review of Fable's commit `e4a0eb8` and discussion
70 messages 1032–1033. This is a bounded closure of R1–R6 and a decision-brief
update, not authorization or validation of a research result.

**Disposition.** Recommend selecting the question and authorizing the smaller
first tranche in the [decision brief](vortex_decision_brief.md). Draft 0.3 fixes
the probability-support defects, removes causal classification, defers the
genetic and forward models, and gives replayable public inputs. Production
inference remains provisional. The remaining repairs belong to the agents
during development; they do not prevent Barry choosing a bounded feasibility
study now.

## What the numerical checks establish

The proposed *fixed-size* binomial criteria are calculated correctly. Using
base R's `qbeta` and `pbinom`:

| Criterion | Boundary | Check |
|---|---|---|
| Upper one-sided 98.75% bound ≤ 0.08, n = 1,000 | At most 60 rejections | Upper bounds at 60 and 61 are 0.07903169 and 0.08015732 |
| Upper one-sided 98.75% bound ≤ 0.08, n = 1,200 | At most 75 rejections | Upper bounds at 75 and 76 are 0.07997917 and 0.08090618 |
| Lower one-sided 95% power bound ≥ 0.70, n = 300 | At least 224 detections | Lower bounds at 223 and 224 are 0.69849023 and 0.70197502 |

For a fixed n = 1,000, passage probabilities at true rejection rates
0.05, 0.065 and 0.08 are 0.93294, 0.28613 and 0.00938. For the power rule,
true power 0.80 passes with probability 0.98990; true power 0.70 passes with
probability 0.04285. Thus the power gate establishes a lower bound of 70%, not
80%. These are binomial calculations, not observed operating characteristics
of the proposed vortex test.

## Repairs before a production freeze

1. **Correct the repeated validation look.** Extending only failures at 1,000
   to 1,200 makes the pass event
   `X1000 <= 60 OR (X1000 > 60 AND X1200 <= 75)`. Its probability at a true
   rate of 0.08 is **0.01576260**, exceeding the claimed per-scenario 0.0125.
   This was evaluated exactly as
   `pbinom(60,1000,p) + sum(dbinom(61:75,1000,p) * pbinom(75-(61:75),200,p))`.
   The simplest repair is a fixed 1,000 with no rescue extension; otherwise
   allocate error across both looks. Define the family across scenarios and
   priors when freezing the final list.

2. **Complete the Monte Carlo test.** Estimating a mean/covariance from the
   same replicate statistics used for ranking treats those replicates
   differently from the observation. The `+1` rank formula alone does not
   restore exchangeability. Use an independent training reference, or a
   justified symmetric construction, and apply the same frozen algorithm to
   empirical and validation datasets. Do not pool swapped, interdependent bank
   folds as independent binomial trials: use a frozen reference bank with fresh
   outer trajectories, or analyse folds under an appropriate design. Specify
   the shrinkage trigger, ties, zero MAD/undefined
   autocorrelation, finite-bank approximation and numerical failure handling.
   Exact conditioning yields a uniform rank under appropriate continuous or
   randomized conditions; discrete conservative ranks need not be uniform.
   A [Besag–Clifford sequential procedure](https://doi.org/10.1093/biomet/78.2.301)
   requires its own stopped-sample formula and conditions. Start with a fixed
   replicate count unless the sequential implementation is fully justified.

3. **Do not turn an unattainable effect into informative compatibility.** If
   no effect in the specified range gives the 10-percentage-point extinction
   risk increase, `beta_max/2` can be a descriptive sensitivity only. It cannot
   substitute for a decision-relevant `beta_min` in O1. Freeze the numerical
   effect search, define whose calibrated parameters determine it, and make
   O1 unavailable if the target cannot be supported.

4. **Finish the study-specific specification and cost inventory.** Resolve
   the three window differences, T5, census stages and survival-prior mapping.
   A mathematically valid unstructured process does not establish biological
   equivalence to adult-survival estimates. Specify external-decline strengths,
   observation rules, nuisance corners and mixture settings. The six-alternative
   count in §4.4 does not cover the full list in §4.3 and both observation
   variants. Benchmark rejected trajectories, effect calibration and fits;
   neither the 400-dataset screen nor the large banks are a small laptop pilot.

The brief caps synthetic development at one worker, 2 GiB resident memory and
30 aggregate CPU-minutes, stopping earlier at 10,000 candidate trajectories
per population or 20 nine-population estimator fits. The aggregate covers both
implementations. It is a feasibility ceiling and cannot demonstrate production
error control. Research execution, including this pilot, awaits Barry's choice.

## Data replay and source correction

A read-only delegate verified the worktree and Git-blob hashes of
`population_data.csv` and `readme.txt` against the manifest; `.gitattributes`
preserves their bytes. Replaying `python3 notes/t3/fh_table1_reconciliation.py`
exactly reproduced the archived output. Appending a byte to a temporary input
copy produced exit 1 with the documented checksum refusal. Repository inputs
were unchanged. Six of nine zero-inclusive windows match; three scalar-field
discrepancies and 150 versus 148 nonzero censuses remain. This verifies the
summary reconciliation, not the fitted estimators.

Fable's statement that [Griffen and Drake (2009)](https://doi.org/10.1098/rspb.2008.1558)
do not discuss conditioning is incorrect. Their introduction explicitly
describes conditional diffusion crossing the extinction boundary without
returning to the upper boundary. Their F&H citation supports logarithmic
duration scaling. The narrower matched-reanalysis claim remains provisional;
see the [search record](vortex_prior_work_search_20261005.md) for inspected text
and remaining gaps.

The brief adopts Fable's requested updates while qualifying the outcome claims.
No power experiment yet supports ranking O1 versus O3. A useful paper is
possible, not guaranteed; a general sample-size requirement needs a separate
design varying sample size. No new empirical fit, forward-data extraction or
research simulation was run during this review.
