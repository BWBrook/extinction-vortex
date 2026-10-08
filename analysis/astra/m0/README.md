# Astra M0 v0

Separate base-R implementation of protocol 0.3, section 3.1, frozen before
opening Fable's sampler. The shared demographic specification was already known.
This is an implementation check, not a validation of the null for the nine
empirical series.

`m0_step()` samples binomial survivors and Poisson recruits with a shared
standard-normal annual environment. `rho = 0.5` gives the declared two-factor
sensitivity. `simulate_m0()` propagates every calendar year and returns both
the annual path and scheduled censuses. Selection uses the first **recorded**+census at or below one. There is no interpolation, calibration, rejection bank,
population cap, feedback term or empirical tail-probability calculation here.
Numerical overflow is an error, not an extinction or a truncated trajectory.

Run from the repository root:

```sh
Rscript analysis/astra/m0/test_m0.R
```

The tests cover parameter/count support, absorption, expected growth, scheduled
observations, missing calendar years and endpoint selection. Six fixed-seed
Monte Carlo comparisons use 30,000 one-step draws each and a five-MCSE bound;
their values are development diagnostics, not production validation draws.

The model's survival parameter applies to its census class. An adult-survival
estimate is not automatically appropriate for an all-age or breeding census.
No empirical survival priors are assigned. Resolving source units, age structure,
observation and immigration is necessary before claiming empirical applicability.
