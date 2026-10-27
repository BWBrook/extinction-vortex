# W2 interim review evidence

Reviewed source: `35816f3`; no production changes. The consolidated memo is
`notes/astra_w2_interim_review_20261027.md`.

- `archive_audit.py`: one read-only process on deep-server, using the preserved
  inputs named in the script. Run with
  `python3 archive_audit.py /data/codex/artifacts/project/w2_interim_review_20261027`.
  `archive_audit.json` and `.log` are the returned receipts. All 366,000 archived
  records were inspected; no raw shard or numerical sampler replay.
- `replay_node.py`: from the repository root, run
  `python3 analysis/astra/w2_interim_review_20261027/replay_node.py`.
  This reuses the prior fixture against the current shell and asserts both
  previous failures are closed; certificate/restart assertions remain enabled.
  Output: `node_checks.json` and `.log`.
- `s1b_node_fixture.json` and `node_fixture.log`: current ten-group fixture
  replay on Bash 5.3.9, with only its output directory redirected to this
  directory. Production fixture/script bytes were unchanged. Reproduce by
  loading `analysis/fable/calibration/kunanyi/s1b_node_fixture.py` with
  `importlib.util`, setting the loaded module's `HERE` to this directory, and
  calling `main()`; its `NODE` remains the original production script.
- `dispatch_check.py`: actual dispatcher with recording submitter and bounded
  PBS stubs. Run with `python3 analysis/astra/w2_interim_review_20261027/dispatch_check.py`.
  Finished default reference fails before submission; live explicit reference
  proceeds. No live PBS or reservation tests.
- `determinism_receipt_check.json`: local digest and arithmetic check of
  `analysis/fable/calibration/v2_dev/p3/w1r2_determinism.json`; per-setting sums,
  positive/zero coverage and no-record coverage counted independently.
- `parent_collection_replay.json` and `parent_duplicate_replay.json`: parent
  replays of the adjacent `w2_collection_review_20261027/audit_w2_snapshot.py`
  and `w2_duplicate_review_20261027/reproduce_duplicate_path.py`. Both used
  `uv run --offline --python 3.12 --with numpy==1.26.4 --with scipy==1.11.4 python`.
  The first exactly matches the reviewer receipt; the second again produces
  two claims and a doubled journal with identical halves.

Saved production probes are dated observations from Claude. This review did
not log into Kunanyi, interrogate current owners, or change any live run.
