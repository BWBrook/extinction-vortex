# Astra review of protocol 0.7

9 October 2026, Hobart. Reviewed `5ace89e` and Correspondence 1247, with
bounded read-only mathematical and implementation reviews. No simulation,
empirical fit or final validation was run. The raw statistic files were checked
read-only on deep-server; the remaining checks used local development artifacts
and tiny mocked fixtures.

**Disposition: ready for Barry's primary-null candidate choice.** I support
ar_cat as the primary development candidate, with iid retained as a mandatory
sensitivity. I also accept fixed-K nearest-neighbour calibration without a hard
distance cutoff as a development algorithm for either candidate. Neither choice
declares the procedure calibrated or freezes production. The
[decision proposal](vortex_null_proposal_20261009.md) states the scientific choice.

## Evidence now sufficient for a candidate decision

The four arms contain all 30 intended outer datasets. Counts reconcile across
the original JSON, logs, scored CSV and summary. The twelve source hashes match
`14f974b`. A separate remote check confirms that all 120 raw T files match their
archived SHA-256 hashes, contain exactly 2,001 rows with ordered set IDs 0–2,000,
have finite T1–T4 values, and have zero failure flags. See
[integrity result](../analysis/astra/protocol07_checks/remote_T_integrity.json).
This closes the completeness concern raised in the 0.6 review. Fable's scorer
recomputed all p bounds from those files and matched the logged values; my
read-only implementation review checked the scorer and local reconciliations.

| Matched generator and reference | Accept | Reject | Calibration indeterminate | Raw p < .05, diagnostic |
|---|---:|---:|---:|---:|
| iid, null | 23 | 0 | 7 | 0 |
| ar_cat, null | 21 | 1 | 8 | 1 |
| iid, feedback at Delta10 = 0.5 | 1 | 20 | 9 | 29 |
| ar_cat, feedback at Delta10 = 0.5 | 3 | 14 | 13 | 21 |

The hard-tolerance procedure is unsuitable at the tested bank size: its null
non-accept counts are 7/30 and 9/30. The raw diagnostic counts are useful
development evidence for removing that cutoff, but do not validate the proposed
larger banks or final replicate counts. Delta10 = 0.5 is not beta_min.

The lower detection in the ar_cat experiment **does not isolate a causal effect
of enlarging the reference**. Both the feedback-generating environment and the
reference change; the two variants also share random streams. Replace the
protocol and discrimination-note claim that the richer reference's detection
cost has been measured with this matched-design interpretation. A crossed
comparison would address the causal question if it later becomes necessary;
it is not required to choose a defensible primary null.

## Nearest-neighbour proposal: accepted for development

Fixed K = 2,000 removes distance-based abstention. It does not remove conditional
approximation error. Each frozen bank must contain at least K valid selected
runs; every other numerical failure remains inside the fixed denominators.
The actual algorithm and banks need fresh validation after their freeze.

The method has a standard ABC interpretation: Biau, Cerou and Guyader's
[Algorithm 2, p. 378](https://www.numdam.org/item/10.1214/13-AIHP590.pdf) retains
the nearest simulated summaries. Their consistency results use increasing K
and decreasing K/N under additional assumptions. They do not certify a finite
K = 2,000 bank or this test's false-alarm rate. This source check supports the
methodological description, not a validity claim for our implementation.

The 20,000 fresh outer datasets per scenario improve the planning evidence.
Measured all-nine tolerance-1 coverage is 13,710/20,000 (iid null),
13,427/20,000 (ar_cat null), 11,315/20,000 (iid feedback) and 10,984/20,000
(ar_cat feedback). Counts and CP intervals reconcile. The outer draws are
fresh selected trajectories, not resampled bank members.

The proposed 2-billion-raw-draw banks are **10x projections**, not constructed
banks. The ar_cat null's 95th-percentile maximum radius of 0.99 is projected
from the current bank's 200th-neighbour distance. Agreement with measured
thinning makes this useful planning evidence, but future-bank variation and
changes in MAD are omitted. CP intervals in projected rows describe outer-draw
variation conditional on the existing bank and projection; they do not cover
projection uncertainty. Replace "realised radius at 10x" with "projected
radius", then measure actual radii when those banks exist.

Scenario-average validation can conceal poor calibration in rare C regions.
Before final validation, predeclare radius-stratified rejection diagnostics and
report empirical C's position against those strata before interpreting its
test. An empirical case in a poorly represented region needs a local stress
check or an explicit limitation. Do not invent a support exclusion after seeing
its p-value. The 8% gate remains scenario-average control, not a guarantee
throughout C-space. No additional arbitrary radius cutoff is required now.

## Bounded implementation handoff before another full run

New temporary fixtures confirm that the repaired runner checkpoints calibration
shortfalls as `indet_calib`, catches singular covariance as `indet_cov`, and
that the actual shell driver exits 1 and identifies failed mocked children.
Two prospective integration guards remain:

1. `score_discrimination.py` still reads `lg['p']`, whereas the new runner emits
   `p_diagnostic`. A new-format fixture raises `KeyError: 'p'`. Give the scorer
   an explicit input contract for archived and new outputs.
2. `p_bounds` does not assert a `(2R+1, 4)` input. An observation plus 20 training
   rows and no test rows returned status `ok` and p = 1/21. Reject malformed
   shape and unordered/duplicate set IDs as unresolved before scoring. The raw
   archive check above shows this defect did not affect these 120 trials.

Fable owns these changes, the formal wording corrections, and recording
fallback use. The training-failure policy also needs an explicit minimum valid
sample and covariance rule before freeze. Correct exposure row E23's 5,000 to
20,000 outer datasets per scenario. These are routine repairs, not reasons to
defer Barry's candidate choice.

Still ahead: beta_min and numeric corner scenarios, frozen production inputs,
measured cost inventory, and fresh validation. No empirical p-values before the
validation freeze. Barry's reconstructed T1–T4/RI-primary decision remains in
force; the random-slope sensitivity, descriptive T5 and source limits remain.
