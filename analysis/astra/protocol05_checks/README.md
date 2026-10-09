# Protocol 0.5 deterministic review checks

Reviewed snapshot: `9e597d9d0b86bdca580bcc1d142f2533237e4c36`.
These calculations use archived development summaries and exact binomial laws;
they do not compute empirical vortex p-values or run population simulations.

From the repository root:

```sh
Rscript analysis/astra/protocol05_checks/check_arithmetic.R
```

[Archived output](arithmetic.txt) records R 4.6.1, the second-bank Monte Carlo
counterexample, the zero-of-twenty failure bound, conflicting bank-size targets,
and the fitting-cost subtotal. Joint hit counts are recovered only when both
rounded archive fields uniquely identify the same integer; `NA` means they do
not uniquely identify it.

The parent review also replayed
`~/.local/bin/uv run --with numpy python analysis/fable/m0/test_sampler.py`:
20 passes, zero failures, including the repaired adjacent-gap interpolation.
That is a sampler regression check, not validation of M0* or the empirical test.

Interpretation and primary-source checks are in
[Astra's review](../../../notes/astra_protocol05_review_20261009.md).
