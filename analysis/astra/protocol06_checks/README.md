# Protocol 0.6 review evidence

Reviewed snapshot: `1813bfc`. This directory contains bounded audit evidence,
not new population simulations, empirical tests or final validation.

```sh
python3 analysis/astra/protocol06_checks/check_evidence.py
```

[Output](evidence.txt) independently evaluates the declared bank-size rule for
all 45 archived rows and classifies the four synthetic e2e_v1 trials under the
declared tolerance rule. Three trials have calibration shortfalls despite
numeric diagnostic p-values. Fit failures and calibration failures are distinct.

The small [failure-branch probe](probe_failure_branches.py) mocks the population
sampler and R fitting. Its [output](probe_failure_branches.txt) records current
failure behaviour; it does not certify the full pipeline.

## Recovered source

The exact e2e_v1 Python source was present on deep-server at
`/data/fable/vortex/compare_nulls_20261009T013137Z/src/analysis/fable/calibration/e2e_benchmark.py`.
It was copied read-only on 9 October 2026 and is preserved byte-for-byte under
[`recovered_e2e_v1/e2e_benchmark.py`](recovered_e2e_v1/e2e_benchmark.py).
Its SHA-256 is
`dc6e72fd21be9fb2065ded874669e5a18e56f88e31f7c6ba706449891f8e371d`,
matching the existing `compare_nulls_v1/source_sha256.txt` manifest.

The named source commit `04c90b5` contains the bank/comparison implementation,
but not the two end-to-end files added to the remote source tree. Reconstructing
the benchmark therefore requires that commit plus this recovered Python file
and the manifest-matching `tstats_batch.R` from commit `05df1b6` (SHA-256
`36f0336ebe06a0aacea10816c9380d26c8a76513d7391a5d9c3337502f2cff5d`).
This closes source recovery; it does not retroactively make the run commit-only.
The recovered file is an evidence snapshot, not the production entry point.

Interpretation and handoff: [Astra's review](../../../notes/astra_protocol06_review_20261009.md).
