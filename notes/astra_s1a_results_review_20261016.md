# Astra: completed Stage 1a review and next-stage handoff

Reviewed `dc86ef8d56ad9bdc001f08068a269a82b24e4a9f`, the saved Kunanyi
archive, the no-fit report and Stage 1c draft, and Correspondence 1738–1752.
Two bounded reviewers separately checked cost arithmetic and the Stage 1b/1c
design. This is an exposed development audit, not a validation result.

**Recommendation: accept the pilot's provenance and numerical accounting;
revise the cost interpretation and complete the next-stage contracts.** The
861,632 gross worker CPU-hour projection reproduces. Its reported bootstrap
range is not a calibrated resource allowance. Keep the full noisy 200-outer
design as the principal option Barry favours; the cost alone is not a veto.
Stage 1b sampling and Stage 1c fitting remain uncommissioned.

## 1. Verified pilot evidence

The [raw audit](../analysis/astra/s1a_results_review/raw_audit.json) records
the executed checks and hashes; its adjacent script reads saved files and
reruns the accepted collector into an Astra-owned directory on deep-server.

- All **2,975 regular archive members** match the extracted files byte for
  byte. The archive SHA-256 is
  `3e18e5b880f346ed683e63e15e2b46f167b71a0a2dab72885ff0afdb3d132df0`.
- The cluster collection, saved deep-server collection and fresh Astra
  collection are identical. All **1,080 settings and 360 workers** have the
  expected identities and bindings. There are no invalid, missing or failed
  rows, and no uncommitted hit-journal tails.
- **1,073 settings completed their stopping rule; seven are censored**:
  547, 576, 893, 931, 985, 994 and 1078. Setting 576 has no exposure. A completed
  proposal budget does not imply a completed K-member library: only one
  setting reached K=2,000; no complete nine-population dataset did so.
- Totals reproduce: **3,490,909,420,000 proposals; 122,054,077,782 paths;
  322,736 retained hits; 733.873484 worker CPU-hours**. The first five batches
  of all 1,079 exposed settings preserve the prior smoke's 38 hits byte for
  byte. The no-exposure setting has no prefix to reuse.
- The submission journal has exactly 45 node-job acceptances and one
  collector acceptance, with matching unique job IDs. All 45 worker-summary
  logs report zero failures. The archived preflight binds **991.445 allocated
  CPU-hours**, within the authorised 1,000-hour ceiling.

The report's roughly 770 allocated hours is an estimate. The saved worker
wall times give **767.159 hours** for eight times each node's slowest worker,
excluding setup and the collector. I did not read authoritative PBS
`resources_used.walltime` records; the all-PBS-exits-zero statement remains
attributed to Fable. No new Kunanyi connection or scheduler command was needed.
This accounting limit does not invalidate the accepted dispatch ceiling.

## 2. MAJOR: qualify the cost uncertainty before a resource decision

The [cost review](astra_s1a_cost_projection_review_20261016.md) independently
reproduces the full projection and its 749,015–981,136 bootstrap quantiles.
The algorithm in `p2_report.py:103–126` resamples fixed estimated costs, with
four zero-hit costs fixed at lower-limit substitutes. That spread does not
calibrate uncertainty from poorly estimated rates, unseen expensive outers
or future throughput. Paired outer resampling changes the numbers modestly;
it does not cure the missing uncertainty.

Retain **861,632 gross worker CPU-hours** as the stated plug-in planning
projection, with **84% at n=300**. Label the bootstrap as conditional empirical
resampling spread, not a 90% budget range. The report already says the total
is not an upper bound; carry that limitation into every summary and decision
option. Do not claim a million-hour ceiling will complete the design.

Finite accompanying repairs: label transformed retention intervals as
intervals for projected expected cost at fixed measured throughput; distinguish
censored sensitivities and approximate zero-hit lower limits; show resolved
denominators and unresolved counts in scenario tables; distinguish gross
from additional work and scheduler allocation; correct the statement that
everything except the hit-stopped setting exhausted its proposal budget.
The detailed memo supplies numerical checks and finite edits. Its cost
sensitivities are illustrations, not replacement forecasts or joint bounds.

## 3. MAJOR: settle the execution and fitted-stage contracts

The [design review](astra_stage1bc_design_review_20261016.md) sets out the
bounded requirements. These are prospective contracts, not defects alleged
in an unimplemented Stage 1b.

1. **Preserve stream identities and global order.** Retain pilot setting IDs
   and 20,000-proposal batch boundaries; append new IDs or bind a stable map.
   Merely extending the existing trial loop to 200 renumbers 1,050 pilot
   settings. A first-K library may close only after all earlier batch ranges
   are verified complete. Bind disjoint second-library streams, caps, bounded
   concurrent shards, wave ceilings and the total allocation ceiling. Charge
   discarded later shards and retries to that ceiling.
2. **Make failure scoring explicit.** Under the v1 procedural rule, library
   shortfalls and indeterminacy count as null non-accepts and alternative
   nondetections, with reasons retained. A capped failure to fill K is not
   proof of zero mathematical support. Preserve all named denominators and
   report joint availability with n=0; complete-pair statistic comparisons
   need their own disclosed denominator.
3. **Specify the gate's purpose before fitting.** If retaining the original
   one-sided 98.75% CP upper limit <=0.08 for four informative null cells and
   the 95% lower limit >=0.70 for power, N=200 requires **at most seven null
   non-accepts and at least 152 detections**. A true 5% null non-accept rate
   passes that per-cell criterion only **21.3%** of the time, versus 93.3% for
   the old 60/1,000 rule. Nonpass can mean inadequate precision to establish
   the bound. N=25 or 50 cannot pass this null criterion even with zero
   non-accepts. Agree the family, gating scenarios and intended interpretation;
   do not silently rescale counts, relax criteria or add outers after results.

The full primary inventory is **21,600 population libraries and 2,400 fitted
analyses**, including 800 shared n=0 analyses. Price the named independent
library check, fitting, discarded shards and allocation overhead separately.
The crossing-batch surplus is not an independent second K-member library.
Consume the first-K fixed-ball references directly; the draft's k-NN clause
must not cause fresh neighbourhood selection or MAD scaling. Preserve
independent train/test resampling streams and conditional finite-library
interpretation. Replace the assumption that information will “restore”
calibration with the neutral question of how it changes non-acceptance,
detection and computational availability.

## 4. Next owner and stop

**Fable next:** correct the report and bring back a concrete full-design
Stage 1b package: stable stream map, capped waves and complete inventory,
with a named/priced second-library check. Resolve the Stage 1c gate purpose
and scoring plan before fitted execution. About 12 days at sustained 3,000
cores is conditional arithmetic, not a resource reservation. Barry's stated
inclination supports preparing this option; it is not yet launch authority.

This review does not choose new caps, change the scientific target, reopen
v1's failed validation or commission fitting. The audit used 11.03 seconds
and about 88 MiB peak child RSS on deep-server plus small local arithmetic.
No new population paths, bank build/scan, fitted statistic or empirical test
was run. Source and peer implementation files were not edited. Exposure E56
records access to saved development outcomes and these arithmetic checks.

16 October 2026, 20:31:56 AEDT (Australia/Hobart).
