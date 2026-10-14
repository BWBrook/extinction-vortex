# Completed A-power and source-recovery review

Review of `20c85745f417c093b22743a304d0521c962cd986`, 14 October 2026.
The [review memo](../../../notes/astra_a_power_deep_dive_review_20261014.md)
states interpretation, next drafts and limits. No new simulation, fitting or
empirical test was run.

- `raw_audit.py`: read-only single-CPU remote audit of 1,200 raw T files;
  independent covariance/rank calculations, paired intervals and source hashes.
- `raw_audit.json.gz`: compressed receipt, including all per-trial outcomes,
  p bounds and T/source/bank hashes, plus local reconciliation.
- `reconcile.py`: binds the remote result to nine local compact files,
  602 A T/neighbour manifest entries, five helpers and 600 baseline T hashes
  from the sealed v1 audit.
- `contract_checks.py/json`: 21 compact receipt checks and nine mocked fixtures,
  covering seven refusal paths plus successful complete-resume and report paths.
- `haley_source_excerpt.json`: source-labelled descriptive transcription and
  retained contradictions; [source memo](../../../notes/astra_haley_recovery_review_20261014.md).
- `caribou_source_checks.py/json`: public CSV/WFS/version checks with source URLs
  and hashes; [source memo](../../../notes/astra_caribou_recovery_review_20261014.md).

Raw audit command, from the repository root (deep-server has NumPy/SciPy):

```bash
ssh deep-server 'env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 nice -n 10 python3 -' \
  < analysis/astra/a_power_review/raw_audit.py \
  > /tmp/project-a-power-raw-audit-20261014.json
python3 analysis/astra/a_power_review/reconcile.py \
  /tmp/project-a-power-raw-audit-20261014.json
```

The executed audit took 89 seconds. Both arms reproduce 21 versus 11 detections
at beta_min and 206 versus 28 at Delta10 = 0.5. One v1 test-reference fit failed;
fixed-denominator bounds reproduce its determinate outcome. A has no failed
fits. Every covariance is below the frozen shrinkage threshold; this script
asserts that scope rather than claiming to exercise a shrinkage branch.
All 181 frozen bank hashes match. Maximum paired observed-T drift is 1.56e-9;
substituting stored v1 observations leaves every A p bound unchanged.

The contract fixture command is in its module header. Source tabulation replay:

```bash
python3 analysis/astra/a_power_review/caribou_source_checks.py \
  /tmp/astra_caribou_20261014 /tmp/caribou_source_checks_replay.json
```

For a new machine, retrieve the six URLs in the caribou receipt's manifest to
the specified filenames first. Source downloads remain outside Git.
Nearest-neighbour selection and original-C distances were checked against saved
receipts, not rebuilt independently. Hashes describe the inspected payloads,
not uninterrupted historical immutability. Source disagreements remain
unadjudicated; primary-paper reading is distinct from automated tabulation.
