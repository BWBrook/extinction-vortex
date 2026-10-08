# Astra review of protocol 0.4

9 October 2026, Hobart. Reviewed `902bc15` (protocol changes in `c2c8d1d`),
discussion 70 messages 1180–1181, and Fable's independently frozen M0 code.
An additional read-only mathematical review checked the calibration argument.
This is development review, not production validation.

**Disposition: continue development; revise before freezing.** The independent
training reference, fresh outer validation trajectories, fixed 1,000 null
trials, and refusal to substitute an unattainable effect for informative
compatibility are sound repairs. I support a clearly labelled four-statistic
reconstruction and descriptive treatment of T5. I do not endorse §4.2 as written:
proximity to published coefficients does not identify the historical estimator,
and applying the same estimator to both datasets does not by itself validate a
test. The [proposed amendment](vortex_amendment_proposal_20261009.md) separates
the scientific decision from the agents' remaining implementation work.

## 1. Freeze the procedure that will actually be tested

**Production blocker.** Sections 3.4 and 4.4 specify different algorithms:
10,000 training and test datasets for the empirical analysis, but 1,000 of each
for validation. Training size changes the estimated distance; test size changes
Monte Carlo decisions. Validation of one does not automatically validate the
other. Select a common pair of counts from the benchmark, then use it throughout
final validation and empirical analysis. A smaller pilot may diagnose feasibility
but cannot certify the larger final procedure.

The second-bank rule also enlarges the bank after seeing a change in empirical
p-values. That is incompatible with validation conditional on one frozen bank.
Finish bank sizing in development and freeze its construction and any second-bank
check before validation. A later failed stability check must produce a documented
indeterminate result or require validation of an explicitly amended procedure;
it cannot silently trigger more computation until the result stabilizes.

The cost inventory still contains 1,200 null trials and six alternative scenarios.
Replace these with the final scenario list and include both training and test
fits, unsuccessful trajectory draws, effect calibration, and mandatory sensitivity
work. No new numerical production estimate is supplied by this review.

## 2. State what calibration can establish

**Production blocker for the current validity language.** Independent training
and test sets repair the earlier in-sample/out-of-sample distance asymmetry. An
exact rank argument additionally needs the observation and test draws to have
the same conditional distribution. A fresh observation follows the population
law; draws resampled from a finite library follow its empirical law. Matching
calibration summaries exactly would not itself remove that finite-bank difference.

Describe the implemented algorithm as an approximate finite-bank ABC procedure.
Its operating characteristics must be measured on fresh outer datasets using the
frozen procedure. Such validation is conditional on the frozen bank(s), design
and scenario distributions. It does not establish uniform control across all
nuisance values, calibration summaries, census units or observational processes.
The four-scenario confidence rule bounds rejection rates against an **8% ceiling**;
it does not prove exact 5% size.

The displayed `>=` rank formula and "ties broken uniformly" also need one
executable definition. Keeping all ties in the upper tail is a simple conservative
choice in the ideal exchangeable experiment. This does not make the finite-bank
implementation exact.

## 3. Keep failures inside the fixed denominators

**Production blocker.** Reporting a failure rate below 2% does not specify what
happens to those trials in the null and power gates. Retain all 1,000 null and
300 power trials. For the conservative gates, unresolved outer outcomes count as
rejections for the null upper bound and nondetections for the power lower bound.
Do not discard or replace difficult datasets. Freeze fallback optimization and
calibration-failure handling before validation.

For failed test replicates, retain most/least-extreme p-value bounds. If empirical
bounds straddle 0.05, no O1/O2 label is available. Failure to construct the training
distance requires a dataset-level indeterminate outcome, not deletion of whichever
replicates caused it. The fixed-denominator rules and >2% stop rule serve different
purposes and both need implementation.

## 4. Prior (b) is a reasonable development primary

The source audit has not established census-class-matched independent survival
estimates for every population. Using the stated wide prior (b) avoids inventing
those anchors. Call it **the prior proposed for primary validation**, not already
validated. Retain its actual specification; "wide" is not evidence of robustness.

Literature prior (a), where supportable, may be an explicitly unvalidated numerical
sensitivity. It cannot borrow prior (b)'s power gate or receive validated O1/O2
labels. A material change can be described as prior sensitivity without implying
that the second procedure passed validation. Joint-test validation likewise does
not certify every secondary or sensitivity test.

## 5. Keep the estimator amendment honest

The proposed RI promotion follows inspection of the observed T1–T4 values.
"Before any test outcome is known" should therefore say "after reconstruction
results were inspected, before conditional-null p-values or final validation."
The original Astra specification explicitly retained its RI diagnostic without
promoting it for proximity to the published numbers.

My recommendation is to retain that specification's random-intercept-and-slope
AR(1) candidate as the primary reconstruction, with RI as a mandatory sensitivity.
This avoids a new closest-match promotion. It is not a claim of full blindness:
the prior exposure to Fable's reported reconstruction was already recorded in E14.
Fixed-procedure validation does not validate the historical or adaptive process
by which the analysis was chosen. If the agents instead propose RI as primary,
they must state that exposed change and its inferential scope explicitly.

Whichever target Barry adopts, specify the residuals and cutoff, not merely
"multilevel AR(1)": T2 excludes exactly the final transition (`s >= 1`); T3 uses
squared conditional response residuals; T4 refits the mean model on the retained
transitions before computing those residuals. The alternate residual and cutoff
diagnostics remain archived. Stage B remains unpassed.

The current claim that all displayed discrepancies are <=0.002 is true for the RI
column, not the random-slope column (its largest difference is about 0.00382).
Report the full table, whichever model is primary.

## 6. M0 comparison and an interpolation defect

I inspected Fable's sampler and both comparison scripts. The shared M0 transition,
annual gap propagation and first-recorded-census selection agree with Astra's
specification. Re-running `python3 analysis/fable/m0/test_sampler.py` in WSL on
9 October passed all 19 checks, including the mean identity and support tests.
The small checks used existing NumPy 1.26.4. I inspected the archived nine-setting
R/Python comparison; I did not rerun it or produce new empirical fits.

The single-gap interpolation test misses an adjacent-gap defect. Reproduction:

```python
interpolate(np.array([[77., 999., 999., 43.]]),
            [1970, 1971, 1972, 1973], [1971, 1972])
# observed: [[77., 538., 290.5, 43.]]
# joint interpolation between the two observed endpoints:
#           [[77., 65.6666667, 54.3333333, 43.]]
```

The loop uses another value scheduled for replacement as a neighbour. The wild-dog
gap includes adjacent 1971–1972 values, so any sensitivity recreating those fills
must interpolate from genuinely observed neighbours jointly. Their historical
rounding/reconstruction method remains unverified; this example does not establish
that Williams used that method. Missing-year processing must also define which
annual increments are retained; neither silently treating a multi-year change as
annual nor an undocumented fill is acceptable. Astra's current reader deliberately
rejects such gaps. Fable owns this sampler repair. The completed M0 comparison used
no interpolation, so the defect does not overturn that comparison.

## 7. Historical software: report retrieval limits

A bounded primary-source check does not support "MIXREG is no longer publicly
distributed" as an established fact. Its interface developer's
[Mixed-Up page](https://www.dsi-software.com/mixedup.html), last updated in 2017,
still describes free distribution and links to the old UIC site. That link and
Hedeker's current site were inaccessible in this check; no executable was recovered.
The [University of Chicago centre](https://www.healthstats.org/) confirms that
SuperMix combines the four programs and advertises a free student edition.
These pages establish historical availability and a successor, not an accessible
original package or equivalence to the F&H setup.

Use "not recovered in our bounded search." A licence alone would not recover
the historical input windows, settings or residual convention. No purchase or
author contact is needed for current synthetic development, and neither was made.
The source and census ambiguities remain open.

## Handoff

Fable owns formal protocol and calibration repairs; the existing synthetic
development authorization continues. Astra has supplied the amendment proposal
and bounded review, without editing Fable's formal text or code. Barry's decision
concerns the narrowed scientific target, not the numerical housekeeping above.
No empirical conditional-null p-values, final validation or new data search were
run in this review.
