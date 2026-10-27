# Round-3 package review evidence

Target: repository ce2f722; runner c56d0af6. The main decision is in
`notes/astra_r3_package_review_20261027.md`.

- `native_fixture_receipt.json`, `native_fixtures.json` and captured logs:
  all 41 native checks passed on the review machine.
- `archive_delta_audit.py/json/log`: read-only streaming audit on deep-server
  of the final W1 archive. Every member, digest and record count was checked;
  only the 22 new libraries were reparsed because the other 4,798 match the
  previously audited hashes.
- `smoke_archive_replay.py/json/log`: recollect a private copy of the saved
  adversarial smoke on deep-server, requiring identical summary fields except
  tag and four identical libraries. Use a fresh output directory on replay.
- `recovery_accounting.json`: W1 availability, proposed allocation arithmetic,
  and historical W2-a incomplete-row CPU accounting. This is not a forecast.
- `parent_replays.json` and captured replay outputs: the parent independently
  reran the bounded worker and shell counterexamples after reviewing their
  source. These do not contact PBS or modify production files.

Native fixture command (repository root):

```sh
uv run --offline --python 3.12 --with numpy==1.26.4 --with scipy==1.11.4 \
  python analysis/fable/calibration/v2_dev/p3_stage1b.py test
```

The archive script requires the existing deep-server data paths recorded in
its source and takes one output-directory argument. It uses Python's standard
library. The smoke script uses the saved source/runtime under
`/data/fable/vortex/r3dev2`, NumPy 1.26.4 and SciPy 1.11.4, also taking a new
output-directory argument. Review outputs are under
`/data/codex/artifacts/project/r3_package_review_20261027`; original data remain
under `/data/fable/vortex`.

The three component harnesses and receipts live in adjacent
`r3_state_review_20261027`, `r3_recovery_review_20261027` and
`r3_dispatch_review_20261027` directories. Their memos state the injected faults
and the observations those faults establish. Native tests and archived-data
replays do not establish real NFS failure histories or scientific validity.
