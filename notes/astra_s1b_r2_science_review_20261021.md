# Stage 1b round-two scientific and data-contract review

Target: `9a773c9e0fa7b2499d84540c68afe74165304029`, design §9, the
round-one collector/cost receipts, `p3_w1_costs.py`,
`p3_r2_determinism.py`, and smoke B. Independent-reviewer scope; no production
code, settings, libraries, ledger or source records were changed.

**Recommendation: approve the split-binding restart contract with reporting
changes.** Preserving terminal round-one outcomes and replaying every open
setting under the new operational runner does not change the sampling law or
proposal cap, provided the immutable setting fields and sampling helpers
remain equal. There is no scientific reason to rerun the completed libraries
or reopen a compute-authority decision. This recommendation concerns the
scientific contract; the separate concurrency and dispatch reviews determine
whether the implementation safely executes it.

## Ranked findings

**MAJOR, before using the production comparison — the determinism diagnostic
does not scale and is not a completeness validator.**
`p3_r2_determinism.py:18,32–36` builds sets containing every committed batch
number, intersects them, then visits every shared batch, including empty ones.
The open setting `s01669` already has **381,823,099** contiguous committed
batches. On this Python, its integer objects alone need **10.69 GB** for one
set, excluding the hash table, the other run and the intersection. The smoke
does not exercise this scale. Use merged interval intersections plus sparse
hit records; no production-size memory experiment is needed to establish the
problem. This limits the proposed diagnostic, not the validity of restarting.

The same script silently skips missing requested settings, collapses duplicate
hit identities into dictionaries, and does not check journal hashes or short
reads. The tiny fixture in the receipts asks for two settings, supplies one,
duplicates a hit in one run and deliberately supplies wrong checkpoint
hashes: the diagnostic still reports one identical line and zero differences.
Treat it as an intersection diagnostic over **already verified** journals.
Report requested/present settings, batches committed in either/both runs,
unmatched records and non-pilot coverage. Reject malformed journals and
duplicate identities before comparison. A round-two run stopped at K may
legitimately not replay old overshoot batches; account for those explicitly
rather than requiring unnecessary simulation.

**MAJOR reporting correction, not a launch blocker — 1.19 is neither a
full-cell cost factor nor recorded total spending.** The n = 30 unseen-primary
summary uses **4,251 of 6,840 settings**, selected by completion. It omits the
2,589 others. Hardware throughput in that subset is close to projection; this
does not establish that all ten-outer pilot cell means underestimate their
population means or identify the full unseen tail. Queue order, interrupted
prefixes, different cells' coverage and expensive unfinished settings all
matter. Only **67 of 72** W1 population/scenario/n cells have a completed cost
value for the restart heuristic.

Moreover, `p3_w1_costs.py:43–46` prorates the entire prefix's CPU to the Kth-hit
batch using average CPU per batch. Its “actual” is an **estimated crossing
cost plus outside-prefix discard**. For the same 4,251 settings:

| Quantity | CPU-h or ratio |
|---|---:|
| Matched pilot projection | 87,435.622 |
| Estimated crossing cost plus discard | 104,343.518 |
| Ratio currently reported | 1.19338 |
| Recorded checkpoint CPU, same completed subset | 109,005.006 |
| Recorded checkpoint CPU / matched projection | 1.24669 |
| CPU removed by within-prefix proration | 4,661.488 |

There are 598 completed prefixes extending past their Kth-hit batch. Their
unrecorded per-batch CPU history prevents an exact retrospective crossing-time
measurement. Retain both quantities with accurate labels. The proposed
**0.9–1.1 million W2 worker CPU-h** is a planning scenario obtained by extending
a conditional n = 30 factor to n = 300, not a measured W2 result or predictive
interval. Report W2's early costs and completion coverage before refining it;
unresolved and capped settings remain visible. The scheduler review addresses
the available parallelism and wall-clock forecast separately.

**MINOR — the restart estimate prices 4,846, not 4,847 settings.**
`p3_w1_costs.py:64–71` includes only `status == "incomplete"`, omitting invalid
`s18085`. The published **91,952.539 CPU-h** therefore does not price every
setting selected for restart. Applying the same completed-cell-mean rule to
the omitted setting adds 34.575 CPU-h, yielding **91,987.114 CPU-h**; this is
only an arithmetic correction to the heuristic, not a new validated forecast.
The invalid collector row also omits its actual CPU, so obtain that from its
verified checkpoints for full accounting. Completed-cell means and
`max(mean, 1.25 × old spend)` are useful planning rules but do not supply a
calibrated remaining-work interval. Imported pilot prefixes are reused, so
their CPU should remain a separate historic contribution.

There is also a small unmatched numerator/denominator case in the n = 0 pilot
ratio: `s00576` contributes **3.334 CPU-h** to “actual” but no projection,
because its pilot had no exposure. Matching both sums changes that ratio from
0.96720 to 0.96267; both round to approximately 0.96–0.97. Exclude it from both
sums or state the explicit substitute projection.

## What the saved evidence establishes

Standard-library recomputation reproduces every published cost statistic and
the collector's status arithmetic. The ledger's reservations, PBS allocation
or usage, and checkpoint CPU answer different questions; none should be
silently substituted for another. In particular, cumulative reserve lines are
**reserved allocation**, not measured spending, and can include reservations
released before work ran.

| Round-one quantity | Recomputed value |
|---|---:|
| COMPLETE | 9,695 |
| CAPPED | 2 |
| Incomplete | 4,846 |
| Invalid | 1 (`s18085`) |
| Useful checkpoint CPU-h, including pilot | 151,637.592 |
| Outside-prefix checkpoint CPU-h | 26,666.489 |
| Total represented in collector rows | 178,304.080 |
| Included historic pilot CPU-h | 408.823 |
| Represented non-pilot CPU-h | 177,895.258 |

The invalid row has no cost fields. These totals are **accounted committed
work**, not complete CPU consumption: uncommitted work lost to killed workers,
bookkeeping, setup and idle allocation are separate. The earlier checkpoint
probe's 177,940 CPU-h is a different snapshot/accounting scope; retain its
timestamp instead of treating it as the same total.

The saved per-setting data reproduce 6,637.693 CPU-h outside the final prefix
on COMPLETE n = 30 settings and 20,028.513 CPU-h outside the currently usable
prefix on incomplete n = 30 settings. Calling all the latter defect-caused
damage is stronger than the collector alone supports: an open setting can
have valid committed later work blocked behind an earlier gap. Under the
chosen restart that old work is not reused, but its attribution to crashes
versus ordinary unfinished parallel work requires the run history. The saved
crash and blocked-range evidence supports the diagnosis without making the
collector category a causal estimate.

The independent smoke audit validates checkpoint journal hashes, lengths,
unique ordered identities and ranges before a sparse comparison. It
reproduces **174,302 shared batches and 2,310 byte-identical hit lines**, with
zero changed or unmatched lines. Five settings have positive non-pilot
comparison coverage. Four completed libraries match the earlier smoke byte
for byte, each with 2,000 records; **s00772 is shared pilot only**, so it is not
a fourth independently regenerated library. This is evidence for the tested
operational change, not a comparison of every production stream or of n = 300.
The sampling helpers have no diff between `d1549ac` and the reviewed HEAD.

## The final aggregation contract

The saved inventory has a disjoint, exhaustive partition:

| Component | Settings |
|---|---:|
| W1 primary / check | 14,400 / 144 |
| Retained round-one terminal outcomes | 9,697 |
| W1 settings to replay | 4,847 |
| All W2 primary / check | 7,200 / 72 |
| Round-two selected settings | 12,119 |
| Full campaign union | 21,816 |

The two retained CAPPED outcomes are `s06583` (middle-spotted woodpecker,
b3/134, n = 30, 326 hits) and `s14092` (whooping crane, b5/167, n = 30,
703 hits). Each verified prefix ends exactly at its own bound cap. CAPPED is
an outcome to preserve, not a completed library. Replaying other settings
from the same absolute batch indices redoes work but does not grant new
proposal streams or enlarge their fixed proposal budget. CPU spent on the
old attempt is not subtracted from the replay's proposal cap; doing that
would prematurely truncate the intended deterministic sequence.

For final reporting, use exactly one row per original setting directory and
its full identity `(population, outer, n, library, stream_tag, index)`, with
terminal status, round, settings/metric/runner binding and library hash where
a library exists. Require the retained and replayed subsets to be disjoint
and their union to equal the original inventory. Do not deduplicate by index
alone: primary and independent-check libraries share indices and have
different stream tags. Check libraries are not additional outer replicates.
This is an ordinary aggregation check, not a new approval step.

The current round-one dataset availability shows why setting counts alone
are insufficient:

| Scenario | All nine n = 0 complete, /200 | All nine n = 30 complete, /200 | Both sets complete, /200 |
|---|---:|---:|---:|
| b1 | 0 | 0 | 0 |
| b3 | 0 | 1 | 0 |
| b5 | 0 | 0 | 0 |
| b16 | 0 | 36 | 0 |

Every final scenario/n denominator remains **200**, with failures to fill and
later fit failures retained. Keep the two current cap-affected datasets
(b3/134 and b5/167) even when other populations finish. No fitted calibration
or power conclusion follows from these partial library counts.

## Reproduction and scope

Owned receipts and sources are under
`analysis/astra/s1b_r2_science_review/`:

```bash
python3 analysis/astra/s1b_r2_science_review/cost_coverage_checks.py
ssh -o BatchMode=yes -o ConnectTimeout=10 deep-server 'python3 -' < analysis/astra/s1b_r2_science_review/smoke_sparse_audit.py > analysis/astra/s1b_r2_science_review/smoke_sparse_audit.json
PYTHONDONTWRITEBYTECODE=1 python3 analysis/astra/s1b_r2_science_review/determinism_contract_fixture.py
```

The first script reads the committed collector, pilot and cost receipts and
the original small settings JSON on deep-server, verifying their SHA binding.
The second reads only the named smoke journals and libraries. The third uses
temporary synthetic JSON files. The production archive audit, actual
round-two `select` execution, native runner fixtures, concurrency and dispatch
checks belong to the parallel reviews and are not duplicated here. No
production-sized batch set, population simulation, reference sampling or fit
was run.

21 October 2026, 15:11:12 AEDT (Australia/Hobart).
