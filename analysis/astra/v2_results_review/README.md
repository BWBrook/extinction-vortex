# Completed v2 diagnostic review

Reviewed commit: `7b41881c8b73f70b64a915d0957e1ea2f308c114`.

- `d3_raw_audit.py` / `d3_raw_audit.json.gz`: independent rescoring of all 400
  completed synthetic D3 T files on deep-server, paired statistics, compact
  input bindings, 404 T/neighbour hashes and 180 oracle-shard hashes. No fitting,
  simulation or tree reconstruction. One CPU, 6.7 seconds. The saved JSON also
  records local reconciliation against committed copies and the hash list.
- `d3_contract_review.py` / `.json`: local receipt checks and six mocked
  execution/reporting branches. Distinguishes current result acceptance from
  defects that matter only if those paths are reused.
- `d1c2_checks.py` / `.json`: 4,000 retained-row checks and independent D2
  arithmetic, with precision and absent-neighbour-archive limits recorded.
- `a0_checks.py` / `.json`: six deterministic feature fixtures, three invariants
  and retained summary arithmetic. No new C+ bank computation.

Local scripts need an existing NumPy/SciPy environment. For example:

```sh
OPENBLAS_NUM_THREADS=1 /home/bwbrook/papers/dsipa-dev/.venv/bin/python analysis/astra/v2_results_review/d1c2_checks.py
```

The raw D3 audit runs remotely and sends JSON to stdout:

```sh
ssh deep-server 'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -' < analysis/astra/v2_results_review/d3_raw_audit.py > /tmp/project-d3-raw-audit-20261012.json
```

Retained receipts describe the reviewed version; preserve them if peer source
changes. The checks establish numerical consistency and stated provenance,
not prospective calibration, power or the cause of the original failure.

Interpretation and proposed next assignment:
[review memo](../../../notes/astra_v2_results_review_20261012.md).
