# V2 diagnostic review

[Review memo](../../../notes/astra_v2_diagnostic_review_20261011.md).
`checks.py` uses D1's retained summaries and small deterministic arithmetic
fixtures; `checks.json` records findings and limitations. It does not load
the large banks or compute empirical statistics.

From the repository root:

```sh
OPENBLAS_NUM_THREADS=1 /home/bwbrook/papers/dsipa-dev/.venv/bin/python \
  analysis/astra/v2_diagnostic_review/checks.py
```

The numerical fixture demonstrates incorrect treatment of endpoint ties.
The effect on actual D1 trial ranks requires corrected reconstruction and
is not measured here. V1's scoring and gates are unchanged by this diagnostic
review. The hypothetical 10/200 interval is planning arithmetic, not data.
