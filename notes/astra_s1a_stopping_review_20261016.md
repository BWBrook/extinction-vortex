# Stage 1a stopping and uncertainty review

Astra, 16 October 2026. Reviewed `e3870d4`, Correspondence 1687, the Stage 1a
section of `v2_dev/NOTE.md`, and the stopping, manifest and collector clauses
in `p2_stage1a.py`. This is a bounded statistical review, separate from the
implementation, metric and PBS audits. No pilot or fitted model was run.

## Disposition

**Accept the 2,000-hit stop for this engineering pilot, subject to the
reporting conditions below.** Stopping after a complete crossing batch does
not change the per-proposal target law. It limits work on settings whose
library-building cost has already been measured adequately for planning.
There is no statistical reason to discard the smoke or replace this pilot
with a new sampler. The 1,000 allocated CPU-hour ceiling and no-fit scope
remain unchanged.

This is an explicit change from the earlier fixed-attempt-only design. The
report must identify hit stopping, proposal-cap completion, wall censoring,
failure and missing output separately. An estimate conditional on reaching
2,000 hits is not a population-wide cost estimate.

## What the bias statement does and does not justify

For ideal independent Bernoulli attempts with hit probability p, stop at the
exact K-th success, at attempt T, without a cap. For K>1,

    E[(K-1)/(T-1)] = p,
    0 <= E[K/T]/p - 1 <= 1/(K-1).

The first identity follows by multiplying the negative-binomial mass at T=t
by (K-1)/(t-1), giving p times a normalized negative-binomial mass for K-1
successes. The second follows pointwise by comparing the two estimators.
For K=2,000 the relative-bias upper bound is 0.05003%; the rare-hit relative
standard error is approximately 1/sqrt(K), or 2.24%. Thus the small-bias
intuition is reasonable for an ideal completed inverse sample.

This is **not a demonstrated bound for the actual batched, capped,
smoke-adapted, wall-censored procedure**, and it is not a confidence-coverage
result. Do not apply an unqualified "O(1/2000) bias" assurance to every row
or to a summary restricted to successful libraries. The wording should state
the ideal comparison and describe the observed H/N as a descriptive rate.

The [exact small examples](../analysis/astra/s1a_stopping_review/checks.json)
illustrate the selection issue without simulating populations. With p=0.1,
target 20, four-attempt batches and a 100-attempt cap, E[H/N] over every
terminal outcome is 0.100014. Conditional on reaching 20 it is 0.213370.
This is a toy example, not an estimate of Stage 1a bias; it shows why retaining
all terminal outcomes matters even when unconditional bias is small.

## Minimum uncertainty and smoke-prefix contract

The five smoke batches are replayed as the exact same stream prefix. They
must count once. Budget selection uses their runtime, which can depend on
the same simulated paths and acceptance events. It therefore cannot simply
be called statistically independent of sampling outcomes. It is nevertheless
acceptable engineering adaptation: target, E, C radius, outer IDs and
parameter law remain fixed; the adaptation changes only the allotted attempts.

For formal yield intervals, the simplest clean separation is to condition on
the archived smoke and use **post-prefix** counts:

    N_new = N_total - 100000;
    H_new = H_total - H_smoke,

where the entire prefix is present. Rows interrupted before that point have
no new post-prefix evidence. Report full-stream counts and rates descriptively,
and label which counts enter any interval. This costs no new computation and
does not call the repeated prefix independent validation.

The post-prefix stopping is still adaptive. Use an interval justified for
that stopping rule, rather than attaching an ordinary fixed-N interval with
an automatic 95% claim. A concrete conservative fallback needs no new sampler:
conditional on the smoke, let M be the known maximum number of remaining
batch looks. At each possible post-prefix sample size use an exact binomial
interval with error alpha/M; report the interval at the observed stop. A union
bound gives simultaneous coverage over those M looks, including a hit stop
or earlier wall stop. M and the method must be fixed before the long run.
This is a **per-setting** guarantee, not simultaneous coverage of all 1,080
settings. It is conservative; an established confidence sequence is an
alternative if tighter intervals materially improve the decision. The general
distinction between fixed-time intervals and time-uniform confidence sequences
is documented in [Howard et al. (2021)](https://arxiv.org/abs/1810.08240).

Do not let a pooled rate erase the differences among populations, information
levels, scenarios or outer datasets. Translate a rate interval [p_L,p_U]
to a conditional expected-proposal range [2000/p_U,2000/p_L], explicitly
leaving the upper endpoint unresolved when p_L=0. Multiplying by measured
CPU time per proposal adds a throughput assumption; that range is not a
prediction interval for a future library's completion time.

**Zero hits deserve a narrower qualification than positive-count intervals.**
The collector's 3/N upper bound is a conservative one-sided bound for an
observed all-zero Bernoulli run, even with optional stopping: crossing the
false bound requires observing at least approximately 3/p failures before
the first success, whose probability is at most exp(-3)<0.05. It must use
the actual observed-attempt denominator, never the planned budget. For
conditional post-smoke reporting use N_new and H_new; for the original full
stream label the bound as an unconditional all-zero-run bound. Zero hits
still supply no finite point estimate of the required CPU time. A timeout,
failure or missing row is not a completed zero-hit setting.

## Completion time, censoring and matched controls

The collector currently computes

    cpu_hours_to_2000 = (2000 / H) * cpu_seconds / 3600.

This is a rate-based projection, including for H>=2000; with overshoot it is
less than the recorded crossing-batch CPU time. Label it accordingly. Report
`cpu_seconds` for the completed crossing batch separately. That is an observed
batch-resolution time to obtain at least 2,000 hits, not the exact CPU time of
the 2,000th success. The exact **proposal index** of that success is available
from its hit record: `batch*20000 + proposal_in_batch + 1`.

For settings below 2,000 hits, report the achieved exposure and a right-censored
completion observation. For failed or missing settings, preserve that status
instead of manufacturing a statistical censoring time. Summaries must show
the fraction reaching the target and the censored fraction within every
declared group. A median among completed settings is explicitly conditional;
do not present it as the median across all settings. Different budgets and
runtime-dependent censoring do not justify an automatic non-informative-
censoring assumption for a pooled survival analysis.

The matched n=0 settings remain scientifically useful, with the same outer,
closed ball and path law. Their shorter budget means that their completion
fraction is not directly comparable with n=30 or n=300 completion fractions
as a measure of evidence effects. Compare yield per attempt and cost with
uncertainty, or compare forecasts under a common declared resource budget.
Retain all settings when reporting the complete-nine-library requirement.

Finally, the whole crossing batch implies a strict maximum of K+B-1=21,999
records per completed setting, not 2,000. Approximately 2,000 is a plausible
storage planning estimate under rare hits, not the hard bound. Correct the
wording and use the actual record count for storage accounting.

## Acceptance conditions

1. Declare the hit/cap/wall stopping rule and narrow the bias and storage
   statements to what is established.
2. Preserve the smoke prefix once, bind an uncertainty method for the new
   suffix, and distinguish projection from observed crossing-batch time.
3. Keep every scheduled setting, terminal reason and actual denominator;
   report censored and completed costs without selecting only easy libraries.

These are reporting and analysis-contract repairs. They do not call for
more simulations, new model targets, a larger allocation or a fitted stage.

16 October 2026, 11:51:17 AEDT (Australia/Hobart).
