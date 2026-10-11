# Completed-v1 independent audit

See [audit findings](../../../notes/astra_validation_v1_audit_20261011.md)
and [v2 development brief](../../../notes/astra_v2_development_20261011.md).

- `raw_score.py`: separate scorer; reads the sealed archive and extracted T
  files on deep-server, without production scorer imports or new fitting.
- `raw_score.json.gz`: full receipt, 7,900 trial diagnostics and file hashes.
- `provenance_audit.py` / `.json`: source/manifest/corner and 170-chunk checks,
  including the 9,000 selected low-survival population trajectories.
- `summarise.py` / `summary.json`: compact audit receipt and explicitly
  post-hoc null-block diagnostics. Input hashes connect both audit passes.
- `check_empirical_guard.py` / `empirical_guard.json`: actual completed
  summary refused before empirical execution.

Reproduction from the repository root (remote source paths are fixed in the
read-only scripts):

```sh
ssh deep-server 'env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -' \
  < analysis/astra/validation_v1_audit/raw_score.py \
  > /tmp/project-v1-independent-score.json
python3 analysis/astra/validation_v1_audit/provenance_audit.py
python3 analysis/astra/validation_v1_audit/summarise.py \
  /tmp/project-v1-independent-score.json
OPENBLAS_NUM_THREADS=1 /home/bwbrook/papers/dsipa-dev/.venv/bin/python \
  analysis/astra/validation_v1_audit/check_empirical_guard.py
```

The score pass needs NumPy/SciPy; the provenance and summary scripts use the
standard library. Wall time and dated provenance fields will change on replay.
The compressed original receipt preserves this audit's exact values and hashes.
No result here is an empirical conditional-null test or an independent replay
of population generation, reference selection or model fitting.
