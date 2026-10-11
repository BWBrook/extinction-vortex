# Freeze-package receipts (v1, 11 October 2026)

These are the receipts behind
[`notes/vortex_freeze_package_20261010.md`](../../../../notes/vortex_freeze_package_20261010.md).
They are synthetic only, plus the C-only library computations (exposure row
E28). No empirical T1–T4 or p-value has been computed.

**Where it ran.**
- `deep-server`, tmux `fable_prodbanks`.
- Run directory: `/data/fable/vortex/production_banks_20261010T081726Z`.
- Banks (28 GB) and libraries stay on deep-server, with hashes here.

| File | Content |
|---|---|
| `banks_run_source_sha256.txt` | Sources of the bank, effect and position run. They match `afe9bca`; the driver matches `a31e5bc`. |
| `bank_{primary,stability,iid}_meta.json` | Shard layout, seeds, draws, selected and overflow counts per shard; NumPy version |
| `bank_{primary,stability,iid}_sha256.txt` | SHA-256 of all 540 shard files |
| `resources.txt` | Run time and CPU: 452,339 CPU-seconds, 2 h 52 min |
| `effect_target_ar_cat.json` | β_min grid and value, pooled library medians, corner parameters and selection rates (primary bank) |
| `corners.json` | The three corner scenarios as frozen fixed-parameter sets |
| `empirical_position_{ar_cat,iid}.json` | K-th-neighbour distances of the observed C (C only) |
| `gen_times.json` | Generation timings for all 13 generator scenarios with the recomputed corners |
| `validation_manifest.json`, `stress_sets.json` | The run definition: 17 blocks × 10 chunks, seeds, trial IDs, roles, the stress parameter sets |
| `package_inputs_sha256.txt` | Current hashes of the frozen manifest (`96603037…`), stress sets (`b9ec4c2f…`), effect JSON, libraries and corners |
| `package_inputs_sha256_pre_repair.txt` | Historical: the pre-repair manifest and stress receipt (`49f65ce`) |
| `preflight_96603037ec050361.json` | deep-server preflight receipt for the frozen manifest |
| `freeze_source_sha256.txt` | Staged freeze source; all 17 files match `49f65ce` |
| `runtime_versions.txt` | Python, NumPy, SciPy, R, nlme and kernel versions |
| `receipt_test_bank.txt`, `receipt_test_validation.txt` | 28/28 and 19/19 on the staged freeze source |
