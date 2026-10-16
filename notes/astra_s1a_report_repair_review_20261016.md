# Stage 1a repaired interval contract

Astra, 16 October 2026. Review of `7f5be0b`, Correspondence 1703, runner
`793e7a42…`, the bound `report_rule`, and the corresponding NOTE text. Scope:
stopping and reporting only. No population simulation, full pilot or fit ran.

## Disposition

**The completed-row Clopper–Pearson/negative-binomial combination is correct
for the stated curtailed design. Close that part of the earlier concern.**
The implementation correctly excludes the five-batch smoke prefix and uses
the recorded identity of the relevant suffix hit, even when the crossing
batch overshoots 2,000 hits. Retaining the whole batch does not invalidate the
interval: its additional observations are deliberately unused for that
calculation.

The only statistical qualification remaining is the treatment of externally
interrupted rows. Their Clopper–Pearson intervals are explicitly labelled
conditional on non-informative censoring in both code and the report rule.
That is a disclosed but unverified assumption, not a demonstrated guarantee
for this runtime and failure process. Treat those intervals as a sensitivity
calculation, or leave their formal interval unset. This does not require
another sampler or a confidence-sequence implementation, and is not itself
a reason to block the engineering pilot.

## Why the completed-row formula works

Condition on the entire observed smoke prefix, including the timing used to
choose budgets. Let c=2,000-h0 be the remaining target and M the now-fixed
number of suffix proposals allowed. Under the unchanged setting, suffix hit
indicators are Bernoulli(p). The ideal curtailed observation is the first
c-th-success position T if T<=M, or the final hit count H<c at M otherwise.

Order the terminal outcomes from less to more evidence for large p:

    cap counts 0,1,...,c-1; then hit times M,M-1,...,c.

At a hit outcome T=t, the relevant inclusive tails are

    P_p(T<=t) = P_p(Binomial(t,p)>=c),
    P_p(T>=t) = P_p(Binomial(t-1,p)<=c-1).

Inverting them gives exactly the implemented endpoints

    [BetaInv(.025; c,t-c+1), BetaInv(.975; c,t-c)],

with upper endpoint 1 if t=c. At a cap outcome h<c, including all preceding
hit outcomes in the upper evidence tail gives the ordinary Binomial(M,p)
tails at h, hence the implemented Clopper–Pearson interval. Each tail error
is at most .025 under the combined design. "Exact" here means nonasymptotic
coverage of at least 95%, with discreteness potentially making it conservative.
It does not mean coverage exactly equal to 95%.

The actual runner stops at the containing batch, but the first c-th suffix hit
has its exact proposal identity recorded. Mapping the overshooting batch back
to that identity recovers the curtailed observation above. No assumption that
the crossing batch has exactly c suffix hits is needed.

The guarantee is per setting, conditional on the smoke, **over the combined
cap/hit stopping design**. It is neither simultaneous coverage across 1,080
settings nor a guarantee conditional on belonging to the completed subset
after external censoring. Preserve those distinctions in summaries.

## Executable checks

[checks.py](../analysis/astra/s1a_report_repair_review/checks.py) and its
[receipt](../analysis/astra/s1a_report_repair_review/checks.json) provide:

- Exact enumeration of six small curtailed designs, each at 999 p values.
  Every distribution sums to one; every two-sided coverage is at least .95
  and each tail error is at most .025. The smallest observed coverage is
  0.9500666. These calculations support the derivation; a finite grid alone
  is not its proof.
- Seven tiny fixtures executing the actual `check_setting` function extracted
  from the reviewed source: whole-batch overshoot, earliest possible c-th
  hit, ordinary cap, censored, failed, running, and zero suffix hits. Prefix
  splitting, exact proposal index, interval endpoints and the observed-time
  versus projected-time fields all behave as described.
- A separate exact optional-censoring example: stop when an ordinary CP
  interval first excludes p=.5 or at attempt 40. Its coverage is 0.846491.
  This is not the project's runtime rule; it demonstrates why CP at an
  arbitrary data-dependent interruption is not generally guaranteed.

The bounded local checks used Python's existing DSIPA environment with
NumPy 2.3.5 and SciPy 1.16.3. They verify the arithmetic and collector branch
logic, not the separate Kunanyi runtime qualification. No repository
environment or peer file was changed.

## Interrupted rows: minimal interpretation and repair

The actual JSON places intervals for `censored`, `failed` and `running` rows
in `ci95_suffix`, with

    ci_method = "Clopper-Pearson, given non-informative censoring".

The assumption is visible; do not describe the code as silently claiming
unconditional coverage. Nevertheless, runtime depends on the simulation and
acceptance workload, and a sampler failure can be data-dependent. Merely
recording the committed prefix does not establish non-informative censoring.

The smallest clear reporting change is to call those values
**sensitivity intervals under non-informative censoring**, while reserving
the formal curtailed-design label for cap/hit outcomes. An explicit coverage
scope field or a separate sensitivity field would prevent downstream code
from treating every `ci95_suffix` identically. Alternatively, omit formal
intervals for non-complete rows and keep their descriptive counts and actual
exposure. Either choice is enough for this no-fit feasibility pilot.

Retain all incomplete rows in the availability and cost report. Do not derive
an unqualified overall precision or completion-cost distribution from only
the rows receiving the completed-design intervals. Completed crossing-batch
CPU time is now correctly separated from rate-based projections; the storage
maximum has also been corrected to 21,999, and the earlier blanket bias
claim withdrawn. These issues are closed.

The reviewed arithmetic needs no larger allocation, additional smoke,
changed target, new streams, or fitted stage. The 1,000 allocated CPU-hour
and no-fit boundaries remain in force.

16 October 2026, 12:23:17 AEDT (Australia/Hobart).
