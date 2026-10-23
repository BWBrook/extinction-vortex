# Round-two interim progress and accounting review

Reviewed `461c115c308d301d228eaaa7497aab56ddb38ddd`, the saved 23 October
10:27–10:32 AEDT probe, `r2_probe.sh`, design §9f, NOTE and STATUS.

**Verdict: substantial W1 progress is supported, but several assurances and
cost attributions exceed this live probe's evidence. Correct the report;
these reporting limitations alone are not a reason to stop current
production.** The separate lock and node-script reviews determine the
operational implications and suitability of the proposed mitigation. This
review does not establish that production journals are valid or corrupted.

## Supported figures and their scope

| Quantity | Saved result | Interpretation |
|---|---:|---|
| W1 replay COMPLETE markers | 4,676 / 4,847 (96.47%) | 2,055 n = 0 and 2,621 n = 30; marker inventory, pending collection |
| W1 replay open | 171 | All n = 30; 2,621 / 2,792 n = 30 replay settings have COMPLETE markers |
| W1 readable shard CPU | approximately 53,311 h | Sum of separately rounded 4,543 and 48,768 h; imported pilot CPU excluded |
| W2 COMPLETE markers | 0 / 7,272 | All open; rounded raw-hit median and p90 both 0.00 |
| W2 readable shard CPU | approximately 18,390 h | Same checkpoint accounting scope |
| W1 PBS summary | 53,389 cput-h / 63,184 allocated CPU-h | 84.50%; difference 9,795 h |
| W2 PBS summary | 18,459 cput-h / 19,084 allocated CPU-h | 96.73%; difference 625 h |
| Running subjobs | W1 291; W2 186 | 3,816 allocated cores, not measured simultaneously busy worker cores |
| Logged nonzero exits | 7,969, all code 75 | W1 6,587; W2 1,382 |
| Near-cap slot tally | 82 with at least 19 exits; maximum 20 | Exact number reaching 20 is not reported |

Ratios reproduce the **saved rounded PBS summary**; raw subjob records were
not independently validated here. The probe AWK counts the parent array's
`B=1` record and sums resource fields without filtering to subjobs. Parent
resource fields might therefore matter, but there is no evidence in the
saved summary that they actually double-counted usage. A later accounting
receipt should retain the raw records and use subjob IDs and actual `ncpus`.

The independently rounded checkpoint group totals sum to 71,701 h, versus
71,700 h printed for the unrounded total. That one-hour difference is
compatible with ordinary rounding.

## Corrections needed

**P1 reporting — remove “no invalid settings” and unconditional “no
correctness consequence.”** The probe assigns only COMPLETE, CAPPED, FAILED
or open, using file presence (`r2_probe.sh:21–29`). It never validates marker
contents, checkpoint bindings, journals, declared ranges, counter invariants
or library construction. Unreadable checkpoint JSON is silently skipped.
Thus “no FAILED markers observed” is supported; “no invalid settings” is not.
The real collector computes `invalid` after those checks. A six-case local
fixture confirms that the probe reports COMPLETE for a bare marker with no
checkpoints and even a simultaneous FAILED marker, and reports unreadable or
missing settings as open with zero work.

The logs identify the uncertainty exit path, not whether each acquisition
was certainly refused or took effect. The diagnosis of contention-induced
false positives is plausible and is being checked by the core review; the
aggregate count does not establish that all 7,969 exits were false positives.
Likewise, an intended certificate/recovery path and passing earlier smokes
do not prove every live claim recovered or every current library is valid.
Use “no FAILED markers or transient-error messages were observed in this
probe; collection and journal verification remain pending.” The worker JSON
counters cover processes reaching the normal end of `work()`; exit-75
processes bypass that write, and still-running workers have no exit record.
Zero counters are consequently not a census of all worker activity.

**P2 reporting — label 76% as raw hit-count progress, not prefix completion
or remaining time.** The probe adds pilot hits and every readable shard's
`hits`, then clips the sum at 2,000. It does not require contiguous committed
ranges. An exact-function fixture gives **76%** from 1,520 hits in a later
shard while the actual `prefix()` has **zero hits** because an earlier range
is still running. This is a demonstration of the metric's meaning, not a
finding that the real 171 settings have such gaps. W2's 0.00 quantiles are
rounded raw hit counts across all settings, including unstarted settings;
they do not establish zero hits or poor sampling throughput. The planner
prioritises larger estimated work, so early completions are not a random
sample of W2. The probe does not save started-setting coverage.

**P2 reporting — 82 slots “at the cap and stopped” is not the saved count.**
The command at receipt line 38 explicitly selects `>=19`, while the node
script stops after its twentieth nonzero exit or the time cutoff. State
“82 slots had at least 19 logged exits; the maximum was 20.” Exact cap
exhaustion needs the per-slot histories, grouped by job/slot/invocation and
their final status. The zero failed-slot count comes from only nine finished
W1 subjobs and no finished W2 subjobs; it says nothing about failed slots in
the still-running subjobs.

**P2 reporting — the claimed restart cost and dominant tail attribution are
not measured.** At the stated 15–20 seconds per event, W1's 6,587 events cost
only **27.4–36.6 slot-hours**; all 7,969 cost **33.2–44.3 slot-hours**. These
are illustrative elapsed slot times, not measured CPU consumption. Hundreds
to 2,000 hours would require separate cap-idle durations, lost computation,
waiting or other costs. The 9,795-hour allocated-minus-cput difference cannot
apportion those causes or establish that most comes from the W1 tail. The
tail mechanism is credible, but quantitative attribution needs per-slot exit
times and parent-subjob end times, or sampled active-worker counts. CPU
consumed by restarts or replay also need not appear in that allocation gap.

The roughly 53.3k checkpoint hours are **spending so far**, including
readable work outside the usable prefix, excluding historic pilot CPU,
uncommitted lost work and process overhead. They cannot validate savings
against the roughly 92k full-restart heuristic while 171 costly settings
remain open. That heuristic prices 4,846 rows and omits the original invalid
s18085; its input basis also differs. Keep both amounts labelled and wait for
resolved outcomes before evaluating forecast accuracy. The per-setting cap
remains an absolute proposal-count budget, not a measured-CPU stopping rule.

## Snapshot and denominator discipline

The checkpoint scan alone took 133 seconds, inside a 261-second probe, with
another tally running concurrently. Its later message categories sum to
7,971 and hour bins to 7,973, versus the earlier 7,969 exits. These small
differences are consistent with ongoing activity; do not force them into a
single exact snapshot. The equality `8,980 certificates - 1,011 worker exit
records = 7,969` is a useful aggregate cross-check, not an identity audit.

Keep the replay denominator distinct from the full campaign. Combining the
9,695 retained W1 COMPLETE outcomes with 4,676 new markers gives **14,371
candidate completions**, with **two retained CAPPED outcomes** and **171
open settings**, across 14,544 W1 settings. The new markers still need
validation. The full union remains 21,816 settings including W2. Primary and
independent-check libraries must remain separate; settings are not outer
datasets. This probe has no population/scenario/library breakdown and cannot
establish the number of datasets with all nine populations available for
Stage 1c. Preserve all 200 outer datasets per scenario/n, including failures.

## Next useful receipts

1. At the next ordinary collection, retain per-setting identities, immutable
   bindings, terminal status, verified contiguous-prefix hits, useful and
   outside-prefix CPU, and exact errors. A collection with other arrays of
   the same wave running is a snapshot; final authority requires quiescence.
   Verify libraries and the round-to-round comparison, preserving the old
   COMPLETE/CAPPED outcomes and the full denominator.
2. For any further lightweight progress probe, save timestamp bounds,
   settings/source hashes, per-row or grouped checkpoint-read failures,
   missing directories, started-setting coverage and marker conflicts.
   Label all-shard hits separately from verified prefix hits. It need not
   reconstruct every library during production.
3. Retain raw PBS subjob records and per-slot exit histories when available.
   Separate allocated time, CPU use, checkpoint work and idle slot exposure;
   count exactly 20 exits separately from 19 and do not infer causal losses
   by subtracting aggregate counters.

No new broad audit or heavy live scan is needed merely to correct the report.

## Reproduction and scope

```bash
PYTHONDONTWRITEBYTECODE=1 python3 analysis/astra/r2_progress_review/progress_checks.py
```

`progress_checks.json` records source hashes, saved-text arithmetic and six
small synthetic cases running the exact extracted probe function. The gap
case also runs the exact extracted `prefix()` on its temporary ranges.
This review made no remote reads, production writes, PBS actions, population
simulations, fits or commits. The parent owns the independent core/node
reviews and integration. Only this memo and
`analysis/astra/r2_progress_review/` were written.

23 October 2026, 10:56:05 AEDT (Australia/Hobart).
