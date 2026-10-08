# Astra Stage B reconstruction specification

8 October 2026. Development specification before Astra's first fit. The code
will be frozen before opening Fable's implementation. Board message 1139 has
already exposed Fable's variant descriptions and fitted results, so this is
separate implementation, not result-blind reconstruction. This record fixes
the initial diagnostic set; it is not a production analysis freeze.

## Input and endpoint

Use the hash-verified Williams `population_data.csv`, IDs 14, 15, 6, 20, 21,
10, 4, 8 and 9, without changing recorded values. Retain each series from its
first nonmissing count through its first census at or below one. Record both
calendar years and observation indices. For the final growth transition set
the endpoint count to one, as stated by Fagan and Holmes (2006), p. 53. Positive
censuses strictly before the extinction endpoint enter the scaling regressions.
Do not silently extend or truncate a series to match the Table 1 duration.
Any newly recovered original source is a separately versioned input.

Growth is log(N_next/N_current), indexed by time remaining at the next census:
the final transition has s = 0. Declared exclusion diagnostics retain s >= 1
(exclude exactly the final transition) and s >= 2 (the literal printed cutoff).
Missing calendar steps must not be treated as annual growth; preserve the
schedule and reject an unsupported interpolation. Known but unidentified source
interpolations remain provenance gaps even where the deposited row is complete.

## Estimator

Implement the Gaussian marginal maximum-likelihood model directly, without
calling Fable's code or using its fitted parameters. For population i:

`y_i ~ Normal(X_i b, Z_i G Z_i' + sigma^2 R_i)`;
`R_i[j,k] = phi^abs(year_j - year_k)`.

Profile b and sigma^2 from the likelihood using Cholesky solves. Parameterize
G/sigma^2 by a positive semidefinite Cholesky factor and phi in (-1,1).
Use deterministic multiple starts; retain warnings and boundary solutions.
The primary reconstruction candidate has a random intercept and slope, as
needed for the paper's population-specific empirical-Bayes scaling slopes.
Random-intercept-only and independent residual errors are declared diagnostics,
not substitutes chosen for their proximity to published numbers. F&H do not
fully specify which random-effects structure was used for every analysis.

T1 regresses growth on s. T2 repeats after excluding the final transition;
the s >= 2 alternative is reported separately. T3 regresses squared response
residuals from T1 on s; T4 applies the same construction to T2. Since the paper
does not state whether residuals include empirical-Bayes random effects, report
both conditional and population-mean residuals explicitly. Do not use normalized
or Pearson residuals without a source-supported amendment.

For the scaling analysis, regress s on log(N). Report the population slope
and empirical-Bayes slopes against the published rounded values. For Method 3,
fit both a period main effect and a period-by-log(N) interaction, and fit the
two period subsets separately as a diagnostic. Define early = s >= 10 and
late = s <= 9. Report all coefficients and conditional Wald z statistics;
none is yet accepted as T5. The paper reports z = 2.3 and separate plotted
curves but no single period coefficient matching the present protocol label.

## Verification and stop

Check the likelihood on tiny deterministic examples against direct dense
Gaussian calculations and a maintained mixed-model implementation on synthetic
data. Check endpoint, year indexing, residual and empirical-Bayes calculations.
Use local work only for light checks. Run a larger reconstruction batch on
deep-server in tmux with source/input hashes, exit status and captured results.

Archive every declared fit, including failure/boundary diagnostics. Judge the
four published three-decimal slopes against 0.0005 tolerance, without accepting
one variant as the historical estimator merely because it is closer. A failed
reconstruction or unresolved T5 is an informative Stage B outcome and keeps
the production test unfrozen. Freeze source and results before code comparison.

Primary source: [Fagan and Holmes 2006](https://doi.org/10.1111/j.1461-0248.2005.00845.x),
pp. 53–58. Author PDF inspected from
[Holmes's university page](https://faculty.washington.edu/eeholmes/Files/FaganHolmes2006.pdf);
SHA-256 `4b63e6e92d9780c6431af58fa145f89a95e4e626882ee9c1c63db5997a4f7d9d`.
