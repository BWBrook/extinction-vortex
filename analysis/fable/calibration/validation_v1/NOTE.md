# Frozen validation run on kunanyi (v1, launched 11 October 2026)

This is the §4.3 validation of the frozen procedure. Astra accepted the freeze
in board message 1450:
- source `52779d01468dac186c19810b59c8295dbedd212f`;
- manifest SHA-256
  `96603037ec05036153f67b649757d067ca193c5e0a8610d3b855ef8f22139429`.

It is synthetic only; the empirical test stays behind the gates.

**Host and staging.**
- TPAC kunanyi, run directory `/u/bwbrook/vortex/run1`.
- Staged from deep-server as one tarball (`vortex_run1.tar`, SHA-256
  `18153af6…`, 11.26 GB, copied at about 100 MB/s). It held:
  - the source at `ede7451`; the 12 manifest-bound run files are identical
    to `52779d0`;
  - the frozen manifest;
  - the stress sets (`b9ec4c2f…`);
  - the primary bank (181 files).
- Wrappers: `analysis/fable/calibration/kunanyi/` (`env.sh`, `setup.pbs`,
  `slot.pbs`, `collect.pbs`, `submit.sh`, `tpac.sh`). These are outside the
  frozen manifest.
- The first setup attempts failed before any validation. Batch jobs did not
  initialise Lmod (`env.sh` now sets it up). nlme 3.1-171 is CRAN's current
  release, not in its archive. The EasyBuild R lacks `lattice`, which nlme
  needs, and it is now installed first. Fixes are in `9536e2d`, `55c136f` and
  the commit carrying this note. Each failure stopped before preflight, and
  `submit.sh` refused to launch without a receipt.

**Preflight receipt** (`preflight_96603037ec050361.json`, node n001,
2026-10-11T13:10:13+11:00):

| Item | Value |
|---|---|
| Manifest digest | `96603037…` |
| Source files checked | 12 |
| Bank files checked | 181 |
| Python | 3.11.7 |
| NumPy | 1.26.4 (pinned) |
| SciPy | 1.11.4 (pinned) |
| R | 4.3.3 (2024-02-29) |
| nlme | 3.1.171 (pinned) |

The empirical Q1 run must use this same recorded runtime, which the guard
enforces, so it also runs on kunanyi.

**Launch** (`submit.sh`, 2026-10-11 about 13:10 AEDT):
- 48 one-node slot jobs (`slot.pbs`; 28 CPUs, 120 GB, 27 R workers each),
  each running `validate.py MANIFEST BASE SLOT 48`. IDs are in
  `run1/slot_jobs.txt`.
- Collector job 817526 runs after every slot (`afterany`). It assembles and
  gates the results, packs `validation_v1.tar.gz` with its SHA-256, and emails
  Barry. It exits nonzero if collection, the summary or packing fails.
- Results follow in this directory after retrieval.
