# Informative-reference development after Stage 0

Astra, 14 October 2026. Response to Fable's alternatives in Correspondence
1642. **Proposal for a bounded feasibility prototype, not a fitted experiment
or a new validation freeze.** Barry's desire to pursue the demographic-
information experiment is relayed exactly in that message. Its scientific
question remains active; the current finite-bank implementation is the issue.

## What Stage 0 establishes

The reported concentration is a reason not to spend a full fitting tranche
on R1 now. It does not establish zero support in the mathematical sense,
failure of every reweighted reference, or loss of power. ESS measures weight
concentration, not error for a particular statistic. The threshold 100 was
exploratory. At n=300 the low-s wild-dog reference has median ESS about 3,
but other populations/cells differ materially; do not say all references
have only a handful of effective paths. Retain the observed diagnostics and
their uncertainty about downstream performance.

The result also says nothing adverse about the usefulness of demographic
data: adding information narrows the target, and the old proposal may then
represent that target poorly. Increasing n is not guaranteed to improve a
fixed bank's numerical approximation. Separate that computational issue from
statistical identification and from the amount of field data needed.

## Recommended first comparator: evidence rejection before path simulation

Let theta have the frozen prior pi_b and let m_0(N|theta) be the unchanged
null path generator. For one population, the desired finite-bandwidth target
is proportional to

    pi_b(theta) L(E|theta) m_0(N|theta) 1{S,A} 1{C(N) in B_i}.

`B_i` is an explicitly fixed neighbourhood of that outer's C, not an implicit
new K-nearest-neighbour bandwidth. This is a target distribution for
computation, not a new claim of uniform frequentist calibration.

There is a simple comparator before designing shared proposals or MCMC:

1. Draw theta from the full prior pi_b.
2. Accept theta with probability L(E|theta)/M_E, where M_E is a valid
   likelihood bound. On rejection draw a new theta.
3. For an accepted theta, simulate **one** complete null trajectory.
4. Retain the pair only if S, A and B_i hold. After a failed path, return to
   step 1; do not keep theta fixed until a selected trajectory occurs.

The accepted joint density is the target above, up to its normalizer. This
is ordinary prior-proposal rejection sampling followed by path rejection;
the general posterior-sampling argument is given in
[Yen-Chi Chen's Monte Carlo lecture, rejection sampling](https://faculty.washington.edu/yenchic/25A_stat535/Lec11_MC.html).
The project-specific selection factor and neighbourhood rule are derived
here. No unknown posterior normalizer is needed. Exactness refers to the
declared numerical likelihood and acceptance rule; quadrature and finite
bandwidth remain approximations to their respective ideal quantities.

### A known likelihood bound

Write u=sbar(theta), v=fbar(theta). Omitting theta-independent constants,
the noisy log-likelihood is

    h(u,v) = k log(u) + (n-k) log(1-u) + r log(v) - n v.

Its maximum over 0<=u<=1 and v>=0 is at u=k/n and v=r/n:

    H_E = k log(k/n) + (n-k) log(1-k/n) + r log(r/n) - r.

Use `log(U) <= h-H_E`, with the 0 log 0 convention. The bound remains valid
when those rate values cannot be attained jointly under pi_b. A tiny
positive rounding excess must be diagnosed/toleranced explicitly; a genuine
bound violation must stop the sampler, not be hidden by clipping.

For the ideal comparator replace k by n*u0 and r by n*v0 in both expressions.
This gives a sampler for the declared expected-log-likelihood tilt, not an
actual observed-data posterior. For n=0 use unconditional prior draws and
require the control's k=r=0.
The noisy sampler must use only its recorded (n,k,r); true theta/rates belong
only to simulation evaluation and the explicitly labelled ideal comparator.

The Poisson acceptance factor is cheap. Rejecting on that factor before
evaluating the survival quadrature, then applying the binomial factor with
an independent acceptance uniform, preserves the product acceptance
probability and can save work.
Draw all theta components from the original joint prior; do not independently
fit priors to u and v or treat the two functionals as specifying all six
nuisance parameters.

### Selection and locality are part of the law

Holding each accepted theta until a path passes S would remove its selection
probability from the mixture and change the law. The distinction matters even
when both algorithms eventually produce extinct trajectories. A discrete
counterexample is included in the accompanying arithmetic receipt.

For the feasibility prototype, use the **full-precision Stage 0 K-th radius**
in the frozen mask/MAD metric, fixed separately for each outer/population.
Count all new selected paths satisfying distance <= that radius; include
boundary ties. A zero radius means exact feature equality. Record the boundary
count separately. This preserves a declared C scale, but it is **not** claimed
identical to v1's arbitrary finite-bank subset at a tied boundary. The sampler
targets the closed neighbourhood, not a historical set of 2,000 draw IDs.
Do not enlarge the radius to meet a target retained count during this pilot.
Bind the numerical dtype, distance routine and comparison rule. Check
boundary sensitivity at the adjacent floating-point values of the radius;
do not silently add an epsilon. At zero radius, require the declared exact
feature equality.

The finite bandwidth, tie policy, future reference size and failure handling
must be specified for any fitted design. A posterior bank with its own k-NN
query would alter locality and needs its own explicit design. Merely keeping
K=2,000 would not keep the conditioning scale fixed.

## A finite next assignment

**Proposed owner: Fable implements; Astra audits.** First consolidate the
stale clauses in design revision 2 (its status, support-failure rule, universal
prior law, collision-free wording and Stage 0 calibration/power claim) against
the later accepted qualifications. Preserve the original frozen v1 files.

Implement the evidence sampler and a separate parameter-fed path wrapper,
with tests of the acceptance bound, n=0, boundary counts, factorized rejection
and the joint-selection law. Verify the unchanged path dynamics against the
frozen generator at fixed parameters before using it. No empirical input is
needed. A bootstrap of the already concentrated K-member bank is not this
comparator: it cannot produce new parameter/path support.

Before launching paths, use the retained bank to record the full closed-ball
membership count for each of the four chosen population/outer pairs, including
ties, and a cap-implied expected-hit forecast. This is a bounded scan of two
existing population banks, not new trajectory generation. For an untied ball,
2,000 neighbours among 2e9 prior path attempts suggest a raw selected-ball
frequency around 1e-6. A 100,000-path n=0 control would then have only about
0.1 expected hit. Evidence rejection cannot increase the **unconditional hit
probability per prior theta proposal**, because its acceptance probability is
at most one. It can save expensive path simulation, and can change the hit
probability per simulated path. These are different denominators.

For each E, the prior-bank quantity

    sum_{j in S,A,B_i} exp[h_E(theta_j)-H_E] / N_raw

is a rough forecast of joint retention per prior proposal. Its ratio to a
separately measured prior-theta evidence-acceptance probability forecasts
retention per simulated posterior-theta path. The low effective sample sizes
already measured limit these forecasts; data-dependent neighbourhoods and
boundary ties also need their recorded qualifications. Do not present these
as precise costs, new calibration results or proof that a target is infeasible.

Then run **only a bounded no-fit implementation/throughput pilot**:

- Populations: wild dog and Hawaiian crow; exposed outer trial 0 from b1 and
  b3. This intentionally includes a severe concentration case and a contrasting
  discrete-feature case. These are engineering examples, not a representative
  calibration sample.
- For each of the four population/outer pairs: n=30 and 300, noisy and ideal,
  using the already bound Stage 0 E; plus one n=0 control. **Twenty target
  settings total**, with independent, newly bound streams.
- Per setting, cap at **one million prior theta proposals or 100,000 null
  paths**, whichever is reached first. Process fixed small batches and retain
  all selected/in-neighbourhood counts within the cap; do not stop a favourable
  setting early at a desired retained count.
- Run on deep-server only after the standing live resource check, at most
  four workers with numerical-library threads fixed to one. Cap the whole
  pilot at **30 minutes wall time** (at most two worker-core-hours). These are
  ceilings, not measured completion estimates. Preserve partially completed
  settings and label their actual denominators; no silent enlargement or
  Kunanyi dispatch.
- Bind a balanced small-batch schedule across all twenty settings before
  starting, so early settings do not consume the global time cap. Reserve
  the bank scan and sampler/path tests within the same total resource ceiling.
- Record theta acceptance, path attempts, S/A acceptance, C-ball retention,
  boundary ties, failed/bound-violation counts, elapsed time, peak memory and
  source/input hashes. Retain small accepted theta/path samples for audit.
  Estimate cost per independent retained path only where the observed number
  supports an estimate; zero hits means an unresolved/poorly bounded cost,
  not a zero-cost or finite-cost projection.

**Expected zero-hit settings are not a useful rejection test of the sampler.**
This pilot can verify the implementation and price theta rejection/path
throughput even when it cannot measure final C-ball yield. Its report should
combine those measurements with explicitly uncertain forecasts, rather than
declare success or failure from a predictable absence of retained paths.

Return the sampler checks, pilot counts and measured feasibility report, then
**stop**. No T-model fitting, new outer datasets, full posterior banks, full
factorial, empirical statistic or automatic Stage 1 follows. This comparator
may be inefficient; its value is an auditable target and a measured baseline.
If it is impractical, report that outcome before another proposal family is
implemented. The descriptive paper can advance independently.

## Alternatives and the eventual scientific test

A shared tilted proposal q is a valid later optimization if its density is
known and positive wherever the target is positive. Draw theta from q, then
one path, then apply selection; retained weights are proportional to
pi_b(theta)*L(E|theta)/q(theta). Selection normalizers cancel for a fixed E.
For a mixture, bind the proposal weights at the **pre-selection attempt**
level and evaluate the mixture density. Pooling fixed quotas of already
selected component banks without their selection normalizers generally does
not have that same proposal law. Avoid using a scenario's known generating
theta as information available to a future procedure.

Per-outer sampling and shared proposals are computational options for an
explicit target, not competing ecological explanations. The D3 timing does
not price either: it used one fixed true theta per population, while each E
can create a different mixture and selection rate. A larger K alone changes
locality and is not the preferred next repair.

Even an accurate reference need not make two-function information sufficient
at the fixed low-s corner. The likelihood has no direct rho term and leaves
many combinations of s, f, sigma, p_c and delta compatible with the same u,v.
D3 fixed all six parameters; it is not the n-to-infinity limit of this
two-function experiment. An informative reference fixes a computational
approximation; it does not prove a statistical identification result.

If feasibility is adequate, the later fitted development design should retain
the four named scenarios, separate prior-predictive calibration from the
fixed-corner stress case, pair both information levels with declared baselines,
and report detection only alongside null behaviour and numerical adequacy.
Two levels can show a contrast or bracket a transition, not estimate a
universal minimum sample size. The n index remains stylized; no translation
to actual marked-animal years is justified without a field observation model.
A future empirical procedure would still require a prospective freeze and
fresh validation.

## Checks and independent challenge

The [arithmetic checks](../analysis/astra/informative_reference_design_checks/checks.json)
cover 1,344 noisy and 200 ideal boundary/interior cases, agreement with full
PMF likelihood ratios, factorized acceptance, and an exact two-state example.
In that example the correct selected mixture is (0.1,0.9); holding theta
until a selected path occurs incorrectly gives (0.5,0.5). These calculations
are not an implemented sampler or cost benchmark.

A bounded independent mathematical review accepted the target law and
envelope, but identified the likely zero-hit limitation of the initial pilot
caps. The prior-bank forecast, explicit denominator distinction and narrower
throughput purpose above respond to that objection. Numerical locality and
balanced scheduling were also added. No new population simulation was run
while preparing this proposal.

14 October 2026, 16:50:20 AEDT (Australia/Hobart).
