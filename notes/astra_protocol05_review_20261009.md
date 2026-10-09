# Astra review of protocol 0.5

9 October 2026, Hobart. Reviewed `9e597d9` (formal changes in `5c2d1f2`)
and discussion 70 message 1206. Two bounded read-only delegates checked the
mathematics and benchmark evidence; Astra integrated their findings, checked
primary-source abstracts and reproduced the deterministic arithmetic below.
This is development review, not production validation or an empirical test.

**Disposition: repair and compare before freezing.** Barry's RI-primary T1–T4
decision is correctly carried forward. The adjacent-gap repair passes all 20
sampler checks on replay. Matching training/test counts, fixed banks and keeping
failures inside fixed denominators are useful repairs. The proposed M0* is a
credible development model, but its primary promotion is a scientific change,
not a computational substitution. Keep M0 as the existing baseline and M0* as a
candidate until a bounded comparison makes that choice reviewable. No further
decision is requested from Barry at this checkpoint.

## 1. Define no feedback with the correct conditioning

**High: scientific target.** At fixed parameters theta and n > 0, before
endpoint/cap selection, the M0* transition satisfies

    E[N_next / N | N=n, z, B, theta]
      = (1 - delta B) [logistic(logit(s) + sigma z)
                       + f exp(sigma z - sigma^2/2)].

Here B is the current catastrophe indicator. This expression has no direct
abundance dependence. But with persistent environmental variation, N contains
information about z. Consequently

    E[N_next / N | N=n, theta]
      = (1 - p_c delta) E[m(z) | N=n, theta]

generally depends on n. The fixed-theta qualifier also matters: mixing parameter
sets can induce abundance associations even with independent annual environments.
Thus §3.1's existing abundance-independent conditional-mean invariant cannot be
carried into M0* unchanged. This association is not itself causal feedback.

The appropriate proposed H0 is structural: abundance does not enter per-capita
vital rates or the exogenous environmental/catastrophe transition laws. State
this distinction, test the conditional transition identity, and show the expected
association under persistent environments in a bounded synthetic check. Carry
the adopted baseline through M_A, beta_min, and the validation scenarios; the
old nuisance corners do not explore the new rho, p_c and delta dimensions.

The complete law also needs to state stationary initial z, catastrophe timing,
independence, and severity fixed per parameter draw rather than per event. These
are implemented choices in the scan, not yet a complete formal specification.
Rejecting any path above 10^9 adds conditioning on its maximum abundance. Record
that conditioning explicitly and assess its influence; calling it an overflow
guard does not show it is negligible. The plain-M0 scan currently lacks this cap.

## 2. Separate mechanistic justification from improved calibration fit

**High: primary-null choice.** The exposure to C is honestly recorded. Better
marginal coverage after this exposure does not establish the enlarged model's
biological adequacy, joint calibration support, or discrimination from feedback.
The primary tolerance also changes from 0.25 to 1.0. Compare models at common
tolerances and under the same cap before attributing feasibility improvements
to mechanisms. The existing scans supply some of that evidence, but not the
catastrophe-only control or common-cap comparisons.

The source rationale needs narrowing:

- [Lande (1993), publisher abstract](https://www.journals.uchicago.edu/doi/10.1086/285580)
  analyses extinction risk under demographic and environmental stochasticity
  and random catastrophes. It supports considering these mechanisms, not these
  particular priors or the claim that only genetic processes can create feedback.
  M_A itself is a non-genetic demographic feedback counterexample.
- [Reed et al. (2003), publisher abstract](https://zslpublications.onlinelibrary.wiley.com/doi/10.1017/S1367943003003147)
  defines die-offs by an observed annual abundance decrease of at least 50%,
  estimates approximately 14% occurrence per generation, and reports decreasing
  frequency with severity. It does not calibrate an annual Uniform(0, 0.15)
  probability or Uniform(0.5, 0.99) vital-rate multiplier. A multiplier on
  survival/recruitment is also not identical to an observed abundance decrease.
  Its continuous-tail interpretation is relevant contrary evidence for treating
  catastrophes as a separately identified mechanism.

These are abstract-level checks, not full-paper validation of a catastrophe
prior. Treat the proposed priors as exploratory until justified or explicitly
framed as sensitivity ranges. A terminal crash in an extinction-selected sample
does not by itself identify its cause.

The all-summaries-between-3rd-and-97th-percentiles statement is numerically false:
turtle A autocorrelation is 97.4. More consequentially, the archived rounded
joint-support results imply only 109 wild-dog, 70 turtle-A and 85 turtle-B hits
among two million raw draws at tolerance 1.0. These show sampled support; they
do not supply the eventual K=2,000 libraries. Report counts, Monte Carlo
uncertainty, and both strict/non-strict CDFs for tied summaries such as the crow.

## 3. The second-bank guard confounds bank differences with Monte Carlo noise

**High: production blocker.** Let K1 and K2 be independent Binomial(2000, p)
counts from two ideal test references with the same true tail probability.
The proposed plus-one estimates differ by more than 0.01 exactly when
abs(K1 - K2) >= 21. The exact probabilities are:

| True tail probability p | Probability of triggering the guard |
|---:|---:|
| 0.05 | 0.136820609 |
| 0.25 | 0.454108536 |
| 0.50 | 0.516817392 |

These are conditional thought experiments, not empirical vortex p-values or an
estimated overall null rejection rate. They omit training-distance uncertainty
and real bank differences. Nevertheless, a guard that frequently marks identical
ideal references indeterminate is unsuitable without Monte Carlo calibration,
especially when all indeterminates count as rejections in the null gate.

Reproducible calculation: [script](../analysis/astra/protocol05_checks/check_arithmetic.R)
and [output](../analysis/astra/protocol05_checks/arithmetic.txt). First measure the
guard's behaviour on synthetic references with known equality. Then either make
the bank comparison descriptive, or specify a Monte Carlo-aware decision rule
and include its complete operation in every relevant outer validation trial.
Do not choose its threshold from empirical p-values. Both banks, training/test
fits and any coupling must be specified and costed if the comparison changes
empirical labels. This review does not adopt a replacement rule.

## 4. Reconcile bank targets and retain the information needed downstream

**High: production blocker.** Applying J_i = 3 times the archived requirement
at tolerance 1.0 yields:

| Population | Raw draws (millions) | Expected selected runs | Conflict |
|---|---:|---:|---|
| Wild dog | 110.10 | 712,127 | exceeds 100-million cap |
| Turtle A | 171.30 | 1,380,421 | exceeds cap |
| Turtle B | 141.30 | 1,234,538 | exceeds cap |
| Golden plover | 11.01 | 120,493 | below 200,000 target |
| Crane | 7.20 | 68,940 | below target |
| Crow | 7.41 | 110,150 | below target |

These are deterministic expectations using rounded scan requirements and exact
acceptance counts, not achieved production-bank sizes. Freeze a rule that
jointly addresses retained size, K-neighbour availability, estimation uncertainty
and the cap. Report infeasibility if those requirements cannot jointly be met.

The catastrophe scan returns trajectories only. It discards parameter vectors,
draw identifiers and overflow counts, although the latter are tracked internally.
The archived outputs therefore cannot supply calibrated parameter medians for
beta_min. Preserve these fields, per-population accepted counts and full failure
accounting in the development implementation. Do not infer parameter medians
from trajectory summaries.

Freeze the actual features and metric: the current code excludes the final
transition from all three summaries, uses mean squared changes (not variance),
a full-series demeaned lag-one autocovariance divided by total squared deviations,
and Euclidean distance scaled by raw MAD. It does not record the undefined-ACF
flag. Zero-MAD handling differs across scripts. All primary deposited schedules
are annual and gap-free; the generic features/timing code still needs the stated
gap-exclusion rule before use for missing-year sensitivities.

## 5. Treat the runtime as a preliminary fitting subtotal

**Moderate: feasibility evidence.** The 0.15-second result times four primary
fits on 20 randomly endpoint-selected M0* datasets. Those datasets were not
calibrated to observed C. The calculation 7,000 x 4,000 x 0.15 / 3,600 = 1,166.7
core-hours is correct for that fitting subtotal. Dividing by 60 gives 19.44
ideal wall-hours, not a measured deep-server completion forecast.

The archive does not identify the timing host, R/nlme version, thread settings
or fixture hash, and omits full per-dataset diagnostics. Simulation throughput
was measured for plain M0; the AR/catastrophe scans have no archived timing.
The claim that all other work adds under 2% is unsupported. A second complete
bank-based analysis could approximately double fitting work, depending on the
specified guard. Library selection, distances, fallback fits, data movement and
parallel overhead also need inclusion.

Run a small end-to-end benchmark on deep-server in tmux with source/fixture
hashes and component timings, including calibrated and difficult datasets.
Count nonfinite estimates and convergence diagnostics explicitly. Zero incomplete
rows in 20 trials has a one-sided exact 95% upper failure bound of 13.91%; this
benchmark cannot establish a failure rate below 2%.

## 6. Remove competing executable instructions before a freeze

The finite-bank caveat does not repair all earlier assertions. Independence of
training and test sets does not make a fresh observation exchangeable with
draws from an empirical library. Applying the same estimator does not by itself
validate a test. Remove those exact-validity promises. Also reconcile random
versus conservative ties, prior-(a) outcome labels versus unvalidated sensitivity,
and the retained 1,000-replicate paragraph versus the new 2,000 counts.

The development scan uses seed 20261012, outside the stated 1–999 development
range and within the proposed final range (>=10^6). Numeric ranges alone no longer
establish separation. Record used seeds/streams and reserve disjoint final ones.
The exposure log has two E19 identifiers; retain the earlier row as E19, rename
the later Fable calibration row E20 and update its references. This review is E21.

## Bounded handoff

Fable retains ownership of the formal protocol and calibration implementation.
Proposed next output: a corrected development comparison of M0, AR-only,
catastrophe-only and both, with common nuisance settings, caps and tolerances;
explicit joint support and uncertainty; a repaired bank diagnostic; complete
model/effect definitions; and a small component benchmark. Reuse archived
evidence where comparable. Add bounded synthetic discrimination where needed
to expose the cost of a more flexible null; this is development, not the final
power gate. Stop before production validation and empirical p-values.

Astra will review that package against these findings. If M0* remains the
recommendation, bring Barry one concrete primary-null choice through Decision
Inbox, including the structural H0, prior rationale and discrimination tradeoff.
The existing RI-primary adoption remains in force. The next response is Fable's.

9 October 2026, 11:47 AEDT (Australia/Hobart).
