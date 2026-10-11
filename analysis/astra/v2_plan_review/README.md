# V2 development-plan review receipts

Review target: `29c45c940e6ecca7db0ec94ea992c76e36219a1a`.

- `checks.py` / `checks.json`: reconcile 4,000 D1c rows with the independent
  v1 audit; constant-library rank and tied-neighbour-query fixtures; independent
  Newcombe method 10 transcription checked against two published examples;
  cheap low-s-only Candidate B screen on disjoint exposed power blocks.
- `d3_contract_checks.py` / `d3_contract_checks.json`: bounded mocked D3
  execution/reporting contract fixtures. No study fits or bank loading.

Run the main checks with an existing NumPy/SciPy environment, for example:

```sh
OPENBLAS_NUM_THREADS=1 /home/bwbrook/papers/dsipa-dev/.venv/bin/python analysis/astra/v2_plan_review/checks.py
```

These scripts preserve evidence of the reviewed version, including its defects.
After repairs, use a new review receipt rather than silently changing this one.
The power screen is development evidence, not prospective validation. It makes
no empirical conditional-null calculation and no additional population draws.

Full interpretation: [review memo](../../../notes/astra_v2_plan_review_20261011.md).
