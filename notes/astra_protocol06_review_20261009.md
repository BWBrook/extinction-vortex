# Astra review of protocol 0.6

9 October 2026, Hobart. Reviewed `1813bfc`, formal draft `05df1b6`, and
Correspondence 1218/1222. Two bounded read-only reviews checked the mathematics
and implementation; Astra verified the archive arithmetic and recovered the
exact end-to-end source. No new population simulation, empirical test or final
validation was run. The separately running Fable discrimination screen was
inspected read-only and remains Fable's responsibility.

**Disposition: ar_cat is a plausible candidate, with substantial repairs
accepted; correct the development evidence before asking Barry to choose it.**
It is the only tested candidate meeting the stated observed-C draw-budget rule.
That is narrower than evidence that the populations require catastrophes.
The running screen can supply a useful tradeoff once its indeterminate outcomes
and completeness are accounted for. A scientific candidate choice can precede
final validation; it need not await every production check below.

## Accepted changes

- The structural H0 correctly separates direct abundance feedback from
  abundance–environment association. Specify that the environmental **transition
  law excludes N**; this does not imply statistical independence of z and N.
- M_A and beta_min share the null's environmental baseline. Barry's RI-primary
  T1–T4 adoption remains settled.
- The ideal conditional-law argument is separated from finite-bank ABC in
  §2.1. The second-bank comparison is descriptive, and conservative ties and
  unvalidated prior-(a) labels are consistent there.
- All five implemented variants use the same recorded-endpoint selection and
  count/rate caps. Selected parameter vectors, draw identifiers, seeds and
  overflow counts are retained. The Student-t switch is mechanically active.
- Joint hit counts and marginal tie counts are archived; all 45 comparison rows
  have consistent count/rate arithmetic. The estimator now excludes gap-spanning
  changes. The end-to-end benchmark includes calibration and fitting on deep-server.
- E19/E20 is repaired. The final-seed reservation is distinct from the known
  development streams, though remaining old seed text needs removal.

## 1. Preserve failures in the running development screen

**High: affects interpretation now.** The benchmark records a tolerance
shortfall but continues using the nearest K runs outside tolerance and emits a
numeric p-value. In e2e_v1 this occurs in **three of four** synthetic outer
datasets: both ar_cat and one iid. Their zero fit-failure counts are accurate;
they do not mean those datasets passed calibration.

Under the agreed procedure these three trials are indeterminate. They count
against the null gate, and an analogous M_A trial is a nondetection. Keep the
raw p-values as diagnostics, separately from the procedure's outcome. For
test-fit failures, classify from full-precision bounds, not the current `p`
field, which is their lower endpoint. Do not drop difficult trials or calculate
power only among completed/calibrated ones.

The [small failure probes](../analysis/astra/protocol06_checks/probe_failure_branches.py)
reproduce two additional problems without population simulation or R fitting:
an unusable training covariance raises an uncaught error, leaving no final
results JSON; and bare shell `wait` returns success even after failed background
arms. Therefore `DONE` alone does not establish that all 30 records in each arm
exist. Record unresolved trials, checkpoint completed rows, explicitly wait on
each PID, and verify all four arm counts before interpreting the screen.

The existing output remains useful where complete. There is no reason to stop
the bank construction or discard completed rows. I posted the early warning in
1226 so this distinction can accompany Fable's report.

Before production, define and implement the remaining branches: nonfinite
estimates, training failures, straddling test bounds, singular covariance,
fallback starts, and feature flags. The current code silently excludes incomplete
training rows and tries two optimisers without the promised new-start step.
Choose one explicit policy rather than assuming those behaviours match the draft.

## 2. The heavy-tail comparison cannot establish that catastrophes are needed

**High: scientific interpretation.** For standardized Student-t Z with finite
degrees of freedom and sigma > 0,

    E[exp(sigma Z)] = infinity.

The positive polynomial tail cannot offset exponential growth. Thus
`f * exp(sigma * Z - sigma^2/2)` has infinite marginal expectation before the
cap: Gaussian centring does not preserve mean recruitment. The uncapped
transition is still a proper distribution almost surely, but it is not a
finite-mean comparator matched to the Gaussian model. Cap rejection changes
the sampled law further.

Two proportionate ways forward are available. Narrow the conclusion to
feasibility among the exploratory candidates actually implemented, explicitly
retiring this comparison as evidence against continuous heavy tails; or, if
that scientific comparison is retained, use a prespecified finite-exponential-
moment family with the correct normalization (or an explicitly bounded Student-t)
and include **AR plus continuous heavy tails**. Comparing iid-heavy with
AR-plus-catastrophes does not isolate the catastrophe mechanism.

The revised catastrophe prior is transparently exploratory. The conversion of
a per-generation occurrence rate to an annual upper range does not estimate a
prior over vital-rate multipliers for these nine census classes. Retain that
limit. More flexible nulls can be reasonable candidates without claiming that
the observed trajectories identify their mechanisms.

## 3. Observed-C feasibility does not establish outer-dataset coverage

**High before validation.** Re-evaluating the declared rule
`3 * draws_for_K2000_upper <= 1e9` gives:

| Candidate | Populations within the cap | Largest required bank, raw draws |
|---|---:|---:|
| iid | 7/9 | 21.85 billion |
| AR | 7/9 | 1.314 billion |
| catastrophes | 7/9 | 3.310 billion |
| AR + catastrophes | 9/9 | 337.0 million |
| Student-t iid | 7/9 | 15.68 billion |

The archive's AR-feasible and catastrophe-borderline descriptions do not follow
its own rule. AR fails for wild dog and turtle B; catastrophe-only fails for
both turtles. These are planning calculations around **observed C**, not achieved
production-bank sizes or evidence of biological adequacy.

The four end-to-end trials already show that those local calculations do not
guarantee coverage of fresh outer C values. Increasing every bank tenfold is a
candidate remedy, not an established one. The inexpensive next check is to
generate fresh outer trajectories, calculate only C, and measure whether **all
nine** populations obtain K neighbours within tolerance. Run that check under
the intended null scenarios before expensive T1–T4 fitting. Calibration failures
consume the same null-gate budget as statistical rejections.

The claimed exact CP confidence statement also needs qualification: MAD is
estimated from the same bank whose hits are counted, so the hit events are not
independent Bernoulli trials against a separately fixed region. Freeze scaling
from an independent pilot if an exact binomial interpretation is required;
otherwise call these planning bounds approximate and measure achieved coverage.

## 4. State the capped target and finish one executable specification

The common implementation conditions on an extra event A: neither counts nor
Poisson rates exceed the cap before the recorded endpoint. Overall overflow
rates of 0–3.3% do not bound the excluded share among extinction-selected paths
or near particular C values. Either state the target as conditional on S and A,
or assess distortion through a bounded cap comparison focused on the selected
law. Keep bank and outer-draw treatment identical. This is particularly relevant
to comparisons involving heavy tails.

Before the final freeze, remove the remaining competing instructions rather
than adding another overriding paragraph:

- §3.4 still retains the old 200,000-selected/100-million-draw requirement beside
  the new local-hit/billion-draw rule.
- The test-reference paragraph still infers exchangeability from independence
  of training; §2.1's correct finite-bank qualification must govern it.
- Label the abundance-independent mean/invariant explicitly as the unselected,
  fixed-parameter **plain Gaussian iid** case.
- Reconcile the old development/final seed ranges with the new reservation.
  Include the running screen's actual seeds in the development ledger.
- Freeze numeric null scenarios for the added environmental parameters and the
  risk-defined beta_min. The current Delta10=0.5 screen is useful development
  evidence, not the eventual beta_min power experiment.

## 5. Provenance recovered; runtime remains a planning estimate

The manifest named an e2e Python file absent from the stated Git commit. I found
the exact source in the original deep-server run directory, verified its SHA-256,
and archived it [with reconstruction instructions](../analysis/astra/protocol06_checks/README.md).
It was an uncommitted addition to the named source tree; it is now recoverable.
This closes the provenance gap without treating the results as corrupted.

The revised benchmark is materially better. Its approximately 1,100 core-seconds
is inferred from fitting wall time multiplied by sixteen workers; the resource
archive records wall time and peak RSS, not aggregate CPU time. Roughly 2,100
core-hours is therefore a planning estimate for the tested path. Include bank
construction, effect calibration, descriptive sensitivities and final throughput
when committing production resources. The screen's failure policy and outer-C
coverage must be resolved before interpreting this as a production forecast.

Fable relayed Barry's offer of Kunanyi capacity (48 x 28 CPUs) in message 1222.
That is a useful later resource option. Simple division by 1,344 is an idealized
runtime calculation, not a measured PBS completion forecast. No cluster job was
submitted or resource change made in this review.

## Next handoff

Fable owns the running screen and formal implementation. Next output: a complete
four-arm report with calibration/fit/other indeterminates retained, a narrow
candidate-comparison conclusion, and the inexpensive outer-C coverage check.
The archived failure probes provide concrete acceptance checks for repairs.
Astra reviews that package and can then prepare one Decision Inbox question on
the primary candidate, with the observed discrimination tradeoff and remaining
validation limits. Formal validation follows the scientific choice and freeze;
uniquely identifying a catastrophe mechanism is not a prerequisite for choosing
an explicitly model-dependent primary null. No new author question is opened
before the running evidence is available.

9 October 2026, 13:07 AEDT (Australia/Hobart).
