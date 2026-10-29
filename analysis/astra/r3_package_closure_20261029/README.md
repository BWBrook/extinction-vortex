# Round-3 closure evidence — 29 October 2026

Target `dbb1b85`, runner `e261befa`; decision in
`notes/astra_r3_package_closure_20261029.md`.

- `native_fixture_receipt.json`, parsed output and logs: 42 native runner
  checks pass locally on Python 3.12.13 with NumPy 1.26.4/SciPy 1.11.4.
- `parent_recovery_replay.json`: independent repeat of the component's four
  worker cases. Both original crash controls pass; both first-publication-failure
  cases strand the predecessor. The failure is injected at the actual atomic
  writer's rename, followed by simulated death and omitted successor listings.
- `parent_capacity_replay.json`: independent repeat of the actual dispatcher,
  submitter and capacity helper with bounded PBS/preflight stubs. The component
  directory retains detailed logs and native submitter results.
- `audit_final_w2.py`, `final_w2_archive_audit.json/log`: streaming audit of the
  final archive on `deep`. Every library is hash/count checked; only the 172 new
  libraries are reparsed because all 183 old libraries match audited hashes.
- `smoke_archive_replay.py`, `smoke_archive_replay.json/log`: recollection of a
  private copy of the saved `r3dev3` smoke on `deep`. Both summaries match except
  tag; all four libraries match the saved and earlier reference files.

Native suite:

```sh
uv run --offline --python 3.12 --with numpy==1.26.4 --with scipy==1.11.4 \
  python analysis/fable/calibration/v2_dev/p3_stage1b.py test
```

Parent recovery replay uses the same environment to run
`analysis/astra/r3_recovery_closure_20261029/check_recovery_closure.py`.
Capacity replay uses Python 3 to run
`analysis/astra/r3_capacity_closure_20261029/check_capacity_closure.py`.

Both data scripts take an output-directory argument and use the read-only data
paths recorded in their source. They ran as single processes at nice 10 under
`/data/codex/artifacts/project/r3_package_closure_20261029`; the smoke script
requires a fresh output directory. `deep` had 122 GiB available and load below
one when selected. Python there was 3.12.3, NumPy 1.26.4, SciPy 1.11.4.
No scheduler, production run, scientific fit or new simulation was invoked.

The raw-data archive remains on its original host. Source and compact review
evidence are synchronized with the canonical `mini` checkout. Access used the
current `mini` and `deep` aliases, following Nectar's 29 October guidance.
