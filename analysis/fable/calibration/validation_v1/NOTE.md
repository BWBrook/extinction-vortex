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

## Result (retrieved 11 October 2026, 17:30 AEDT)

**V-fail.** The null gate failed in block 3 (`null_low_s`): 148 rejections in
1,000, against at most 60 allowed (upper 98.75% bound 0.175). Under protocol
§1 the empirical result can now be reported only as *insufficient
identification*. `empirical_q1.py` refuses to run on this summary.

**Run receipts.**
- All 48 slot jobs finished with exit status 0, and their `.err` logs are
  empty.
- Collector 817526 finished with exit status 0 after 15 min 45 s. It wrote the
  summary at 16:34 and the archive at 16:38 AEDT; Barry received its email.
- `validation_v1.tar.gz` is 1.17 GB, SHA-256 `312d91e4…`.
  - It was pulled to deep-server
    `/data/fable/vortex/kunanyi_run1/` and the checksum verified.
  - It is extracted in `extract/`, which holds the chunks, slot logs, collect
    log and preflight receipt.
- Re-running the frozen collector on deep-server, from the extracted chunks
  with the staged `52779d0` source and the same manifest, gives a
  byte-identical summary (SHA-256 `c0eaf012…`).
- Summary binding:
  - manifest digest `96603037…`, code commit `52779d0`;
  - host n001.kunanyi;
  - Python 3.11.7, NumPy 1.26.4, SciPy 1.11.4, R 4.3.3, nlme 3.1.171.
- Every one of the 7,900 trials resolved: no missing rows and no
  indeterminate outcomes of any kind.
- No fit failed in any gating block (1–5).
  - **Correction (Codex audit, board 1526):** the first version of this note
    said the fit-failure rate was 0 in every block. In fact four of
    31,607,900 fitted vectors failed, all in descriptive blocks: one in b14,
    two in b15 and one in b16, out of 1,200,300 each.
  - `validation_summary.json` already recorded them correctly, and no outcome
    or gate changes.

**Gates** (`validation_summary.json`):

| Block | Scenario | Role | Rejections / n | Result |
|---|---|---|---|---|
| 1 | null, prior predictive | null | 46 / 1000 | pass (upper bound 0.063) |
| 2 | null, high σ | null | 41 / 1000 | pass (0.057) |
| 3 | null, low s | null | **148 / 1000** | **fail (0.175)** |
| 4 | null, strong environment | null | 30 / 1000 | pass (0.044) |
| 5 | M_A at β_min | power | 21 / 300 | fail (lower bound 0.047; needs 224) |

**Descriptive blocks** (detections out of 300, with exact 95% intervals):

| Block | Scenario | Detections | Rate (95% CI) |
|---|---|---|---|
| 6 | M_A at 2·β_min | 25 | 0.083 (0.055–0.121) |
| 7 | M_D linear | 16 | 0.053 |
| 8 | M_D accelerating | 26 | 0.087 |
| 9 | M_D step | 17 | 0.057 |
| 10 | M_O, low-n detection | 15 | 0.050 |
| 11 | M_O, uniform detection | 17 | 0.057 |
| 12 | M_A + M_D linear | 42 | 0.140 |
| 13 | M_A + M_D accelerating | 40 | 0.133 |
| 14 | M_A + M_D step | 28 | 0.093 |
| 15 | M_A, Δ10 = 0.3 | 118 | 0.393 (0.338–0.451) |
| 16 | M_A, Δ10 = 0.5 | 206 | 0.687 (0.631–0.739) |
| 17 | fitted-parameter stress check | 11 | 0.037 (0.018–0.065); no unresolved trials |

**Radius strata** (predeclared, descriptive): `radius_strata.json`, computed
by `radius_strata.py`. That script was written after retrieval; it applies the
frozen bins (freeze package §5) to each trial's largest per-population K-th
neighbour distance.

In `null_low_s`, the excess is spread across all five bins: 33/250, 43/318,
40/241, 18/133 and 14/58. The p-values pile up near zero: 280 of 1,000 fall
below 0.1 and 482 below 0.2. The other null blocks have flat p-value deciles.

The failures are not confined to the widest-radius bin. Maximum radius is a
coarse diagnostic, though: per Codex's audit it does not rule out finite-library
or ABC approximation error. In the audit, the mean standardised residuals for
low s are −1.76 for T1 and −1.58 for T2. That shows a location mismatch, not
its cause.

**Audit:** Codex confirmed the V-fail ([audit](../../../../notes/astra_validation_v1_audit_20261011.md), board 1526). Any change to the procedure is a new
pre-registered version with its own freeze and validation, and this V-fail
must be reported.
