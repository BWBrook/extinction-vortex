# A-screen independent review

Reviewed Fable commit `1fe79ea9c5e605947544ba362b476a5b0f2f8c84`.

- `raw_audit.py` / `raw_audit.json.gz`: separate rescoring of all 400 completed
  synthetic A/v1 T files, paired statistics, 1,800 shared population records,
  all 181 frozen-bank hashes, source/helper bindings and neighbour receipts.
  One CPU on deep-server, 40.23 seconds. No simulation, fitting or tree replay.
- `reconcile.py`: matches that remote audit to eight compact local files,
  202 A T/neighbour manifest entries, four helper sources, and 200 baseline
  T hashes in the earlier sealed-v1 audit. Writes the retained compressed JSON.
- `contract_checks.py` / `.json`: 17 compact-record checks and 13 tiny mocked
  execution/report cases. Records working guards and latent binding gaps;
  no peer-source changes or production-bank loading.
- `phase2_source_checks.py` / `.json`: pinned public-file hashes, caribou
  data-availability inventory and Williams crosswalks, Palmer season totals
  and sighting coverage. These are source checks, not fitted demographic results.

Reproduce from the repository root:

```sh
ssh deep-server 'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -' \
  < analysis/astra/a_screen_review/raw_audit.py \
  > /tmp/project-a-screen-raw-audit-20261013.json
python3 analysis/astra/a_screen_review/reconcile.py \
  /tmp/project-a-screen-raw-audit-20261013.json
OPENBLAS_NUM_THREADS=1 /home/bwbrook/papers/dsipa-dev/.venv/bin/python \
  analysis/astra/a_screen_review/contract_checks.py
python3 analysis/astra/a_screen_review/phase2_source_checks.py \
  --output /tmp/project-phase2-source-recheck.json
```

The observed fits differ by at most 1.20e-10 between A and v1; substituting
stored v1 observed T into A preserves every A p-value. Receipt identity is
checked; nearest-neighbour membership is not independently rebuilt. Current
no-failure/no-shrinkage results do not exercise the corresponding failure
branches. Retain the reviewed receipts when peer source changes.

[Interpretation and next assignment](../../../notes/astra_a_screen_option3_review_20261013.md).
