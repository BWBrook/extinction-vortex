# Informative-reference prototype: design challenge and next no-fit tranche

Astra, 15 October 2026. Independent bounded design review of the p1 proposal,
reports and Correspondence 1654–1655. This is not a sampler implementation
audit, a new simulation, or a fitted-stage specification.

## Recommendation

Accept the direction in 1655: measure the unchanged evidence-rejection
sampler on Kunanyi with the declared C balls before changing the sampling
method or locality. Barry's statement, quoted in 1655 from his Claude chat,
is: "The 100K CPU hours is quite feasible on `kunanyi`!" This removes the
reason to treat the current cost projection as a resource veto. It does not
make the projection representative or settle the eventual statistical design.

The next assignment should be a bounded sampling pilot near the lower end of
Fable's proposed budget, followed by a report and stop. A density-known tilted
proposal remains a legitimate reserve option. It need not be implemented
before this direct pilot, and widening the C balls has no present justification.

## What the cost evidence establishes

The p1 settings cover four deliberately selected population–outer pairs, all
at trial 0 in two null scenarios. Their twenty information settings are not
twenty independent outer examples. The forecasts demonstrate a serious
cost issue for some settings under this sampler. They do not estimate a
"typical" cost across nine populations, four scenarios and 200 outers.

The aggregate four observed ball hits versus about three forecast hits is
compatible with the forecast, but cannot validate its rarest cells or its
population-wide extrapolation. In particular, the extreme wild-dog forecast
is informed by the same thin weighted bank support diagnosed at Stage 0.

The further extrapolation in 1655 from wild dog to the four other populations
with low Stage 0 ESS is a scenario for planning, not a measured estimate.
ESS describes normalized weight concentration. Multiplying every likelihood
acceptance weight by a constant preserves ESS while changing total acceptance
mass and projected cost by that constant. Similar ESS therefore does not
imply similar retention, even before differences in path time and C geometry.
Neither the original approximately 100,000 CPU-hour figure nor the later
0.2–1 million range is a supported confidence interval for the full design.

The parent review separately checks the arithmetic, reference-count change,
comparator totals and timing denominators. These accounting repairs do not
remove the missing representativeness evidence.

## A theta proposal can affect the C-ball bottleneck

The statement in 1654 that theta tilting cannot reduce the C-ball bottleneck
is too strong. Write

    a(theta) = P_m0(S, A, C in B | theta).

Drawing theta from q and then one unchanged path gives a ball-hit probability
of integral q(theta) a(theta) dtheta. This can differ substantially from its
value under the prior or the evidence-only posterior. As a simple mathematical
counterexample, two parameter states with prior probabilities (0.999, 0.001)
and event probabilities (1e-9, 1e-3) have prior event probability approximately
1e-6. A proposal assigning each state probability 0.5 raises event probability
to approximately 5e-4. This is an illustration, not a project simulation.

The target is still proportional to

    pi_b(theta) L(E|theta) m0(N|theta) 1{S,A,C in B}

if retained trajectories receive weights pi_b(theta)L(E|theta)/q(theta),
with a density-known q positive wherever the target is positive. A defensive
prior component can preserve this support. Any mixture proportions must be
defined before selection and its full mixture density evaluated; selected
component quotas do not supply that density automatically.

More hits alone are not a success criterion: a poor q can create concentrated
weights and worsen accuracy per CPU hour. Tilting cannot remove trajectory
randomness at fixed theta, and an evidence-only tilt may leave most of the
rare C-event problem intact. The present pilot does not establish how much
of that problem is caused by parameter mismatch versus path randomness.
The valid claim is narrower: the particular prior-proposal rejection sampler
has the reported low joint acceptance. Its prior-proposal bound is not a
bound for all target-preserving proposals.

If a q probe later becomes warranted, keep it small: one explicit proposal
family, fixed balls, fresh paths, correct weights, and independently scored
holdout predictions. Fitting q and judging it on the same few high-weight
bank members cannot establish improved target coverage. Regression adjustment
or widening the ball changes the approximation or conditioning and needs its
own scientific specification; neither is a necessary consequence of p1.

## Smallest useful Kunanyi tranche

Fable's proposed coverage is sensible: all nine populations, the four named
scenarios, noisy evidence at n=30 and 300, and ten exposed outers per scenario.
Bind IDs 0–9 in each scenario before the run and use the same IDs across
the two n values. This is a simple declared batch, not selection by cheap
settings or favourable outcomes. Record that trial 0 was already used in the
targeted p1 pilot; these are exposed development outers throughout. There are
720 informative settings.

Add one n=0 control per population–outer, shared across the two n values:
360 controls. These need not receive the same pilot budget as the rarer
informative settings. Use a total ceiling of 1,000 allocated CPU hours including
setup and idle allocation: at most one worker-hour per informative setting and one quarter
worker-hour per n=0 control give 810 worker-hours, leaving 190 for qualification,
setup and allocation overhead. These are ceilings for a concrete manifest,
not throughput promises; host qualification should establish fixed proposal/
batch budgets that fit them. Reduce all budgets proportionally if measured
packing overhead requires that to respect the total allocation cap. Do not launch an open-ended run or automatically
use the upper 10,000-hour suggestion.

A compact package should bind the exact metric mask, MAD, radii, outer designs,
evidence, source and runtime without making every worker load the 10 GB bank.
Measure the actual node memory, process packing and throughput before the large
array. Checkpoint complete batches atomically, make retry accounting explicit,
and distinguish an interrupted setting from a completed zero-hit result.

Use the unchanged full-precision closed balls, frozen metric and evidence
values. Fixed attempt budgets are preferable for the primary rate estimates,
with hard time and memory guards. Keep complete batches and actual attempted
denominators if a guard interrupts a setting. Every scheduled setting must
produce a status record, including zero hits, crashes and incomplete work.
Do not require 2,000 hits to report a pilot setting and do not stop the whole
pilot merely because an easy setting obtains that many.

Report, by population, scenario and information level:

- raw proposals, evidence acceptance, path attempts, S/A retention, closed-ball
  and boundary counts, elapsed/CPU time, memory and all failure states;
- ball-yield rates with sampling intervals, and projected time to a declared
  reference size only where the data support it; zero hits give a bound or an
  unresolved cost, not a finite point estimate;
- the distribution of costs across the ten outers, preserving the paired
  populations rather than pooling every accepted path into one rate;
- projected complete-nine-library coverage under candidate fixed budgets,
  along with uncertainty and the number of outers on which it rests.

The stop condition is completion of this fixed manifest or exhaustion of its
resource ceiling, followed by the report. It is not an ESS threshold, a count
of successful outers, or permission to run fits. If the low-rate settings have
too few hits to distinguish relevant budgets, say so. The next choice can then
be a targeted additional sampling tranche, the reserved q experiment, or a
smaller declared future design. Failed or expensive settings must stay visible.

## Reference size, baseline and later decisions

Using 2,000 independent accepted trajectories as a finite library, then
sampling 4,000 reference datasets with replacement, is a coherent candidate
design. It is different from obtaining 4,000 fresh accepted paths. It also
does not reproduce v1 exactly: the new closed ball includes all tied boundary
members, whereas v1 selected an arbitrary K-member subset when ties occurred.
The crow example makes this distinction material. Library size is a numerical
design choice whose adequacy is still untested, not a demonstrated minimum.
Any later calibration must include the common finite-library error created by
resampling train and test references from the same library.

The future fitted experiment needs an n=0 reference built by the same
closed-ball/library/resampling construction. Historical v1 outcomes remain a
useful exposed comparison, but cannot by themselves isolate the effect of
demographic evidence from the changed finite reference and tie treatment.
The no-fit controls above start measuring this baseline without commissioning
its fitted analysis. Keeping a fixed independent reserve where affordable
would allow a later library-size comparison without relaunching every sampler;
it is optional preparation, not a new requirement for this pilot.

The original eight-cell fitted proposal is noisy only: 1,600 outer analyses
and 14,400 population settings. That count is correct for its stated scope.
The noisy-only pilot does not establish costs for adding the ideal comparator
mentioned in 1655. Before a larger sampler or any fits, explicitly declare
which comparators are included, their outer counts, K, training/test resampling, support/failure rules and
budget. A reduced outer count for expensive cells is permissible as a future
declared design with changed precision. It must use a selection independent
of individual completion or fit outcomes; retaining only affordable completed
outers would alter the evaluated law. In particular, an underpowered fixed-
corner null check cannot be converted into a pass by relaxing its criterion.

No new Barry decision is needed merely to price the unchanged target on the
resource he has identified. A materially larger commitment, a changed
scientific target, wider locality, or a changed inferential claim should be
brought back as a concrete decision. The fitted stage still requires its own
agreed specification; neither this note nor the sampler pilot commissions it.

15 October 2026, 11:29:14 AEDT (Australia/Hobart).
