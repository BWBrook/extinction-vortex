# Final round-3 closure evidence

Decision: `notes/astra_r3_final_closure_20261104.md`. Reviewed commit `394d4a6`;
stage source commit `d80a60b`. No production code changed or jobs submitted.

- `native_fixtures.json`: all 43 native checks pass; parsed from the local test
  output, Python 3.12.13 / NumPy 1.26.4 / SciPy 1.11.4.
- `parent_recovery_replay.json`: parent repeat of the independent review's nine
  focused tests; identical to its `checks.json`.
- `source_and_test_receipt.json`: nine other staged sources unchanged since
  `07e72ba`, retaining the prior capacity/archive review's scope.
- `check_stage_inventory.py`, `stage_inventory_checks.json`: adapted prior
  executable review with only the expected commit/stage/settings hashes updated.
  Two deterministic builds, ten source hashes, actual-shell install gates,
  exact summary gates and actual settings selection pass.
- `smoke_archive_replay.py`, `smoke_archive_replay.json`: independent
  recollection of copied raw smoke shards on deep, including summary and four
  reference-library equality. Adapted prior script with source path and runner
  pin updated. No new simulator execution or real NFS fault injection.

Commands from the repository root:

```sh
uv run --offline --python 3.12 --with numpy==1.26.4 --with scipy==1.11.4 \
  python analysis/fable/calibration/v2_dev/p3_stage1b.py test
uv run --offline --python 3.12 --with numpy==1.26.4 --with scipy==1.11.4 \
  python analysis/astra/r3_final_recovery_20261104/check_final_recovery.py
scp deep:/data/fable/vortex/r3d_rehearse_pos/s1b/p3_settings_r2.json /tmp/project-r3-settings-r2-20261104.json
python3 analysis/astra/r3_final_closure_20261104/check_stage_inventory.py /tmp/project-r3-settings-r2-20261104.json
```

The stage check pins the input settings digest before use. The remote smoke
script is invoked with a fresh output directory and runs under Python 3.12.3,
NumPy 1.26.4 and SciPy 1.11.4. Its reviewed run is at
`/data/codex/artifacts/project/r3_final_closure_20261104` on deep. Live readiness
showed load 0 and about 122 GiB available; this was one bounded replay process.
Raw smoke files remain in their original location and the replay uses a copy.
