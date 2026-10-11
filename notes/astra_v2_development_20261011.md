# V2 development and prospective-freeze brief

Astra — 11 October 2026, Australia/Hobart. **Development proposal, not a
frozen replacement method.** Read with the
[completed v1 audit](astra_validation_v1_audit_20261011.md).

## Barry's direction and retained result

Barry said in the Codex chat on 11 October 2026:

> Back to you. Note: to me, the proposal to pre-register a revised v2 procedure with its own freeze and validation, still reporting v1’s failure, seems right.

This supports developing a separate v2 and prospectively specifying it before
new validation. V1 remains the frozen procedure tested on 11 October, with
V-fail (low-survival null: 148/1,000) and failed power at beta_min (21/300).
All v1 outputs are now exposed development evidence for v2. New version numbers
or a new analysis script cannot make those simulations untouched again.

The project's preregistration convention is a dated, committed pre-analysis
protocol and freeze. This brief neither makes that freeze nor claims an
external public registration. A consequential change to the scientific target
returns to Barry with a concrete recommendation; routine diagnostic work
continues under the existing development authority.

## Next bounded tranche

**Proposed owner: Fable**, retaining implementation/execution ownership;
**critic: Astra**. Fable's acceptance or revision of this assignment is next.
Output: one mechanism-diagnostic memo, at most two specified candidate
procedures, measured cost and a recommendation. Keep the structural null,
T1–T4 target, primary RI estimator and mandatory sensitivities, beta_min,
fixed denominators, and complete failure accounting as the baseline.

1. **Diagnose the existing outputs first.** Start with the audited T1/T2
   location shifts. Examine selected outer C, each population's matching
   displacement and library nuisance distribution, selection draw totals and
   terminal/penultimate counts. Compare low-survival and prior-predictive
   trials in overlapping C regions. If actual reference membership is needed,
   label a replay as reconstructed evidence and verify its T/input provenance;
   those indices were not retained in v1. No new large run is needed to begin.
2. **Use a small diagnostic experiment only if it can distinguish mechanisms.**
   Before generating outcomes, fix an outcome-independent subset and budget
   for modest K changes and an existing independent bank. A true fixed-theta
   reference at the low-survival values could test the simulator/scorer
   explanation, preserving S and A. It is an oracle diagnostic: theta is not
   known empirically, and dropping C matching would change the conditional
   target. Neither oracle success nor a larger bank alone defines a usable v2.
3. **Compare no more than two candidates.** Judge calibration, retained
   discrimination and measured computational cost together. Include nearby
   nuisance combinations during development so a repair does not merely
   fit the failed corner. Any split/reuse of v1 outcomes is development only.

| Candidate direction | Required claim and evidence | Main risk |
|---|---|---|
| Better nuisance-sensitive summaries and neighbourhoods | Retain the conditional prior-predictive target; specify the new C/matching rule and challenge it at fixed nuisance settings as well as under the prior. | Additional conditioning can remove feedback signal, increase dimensionality and raise cost; more accurate nuisance estimation does not ensure calibrated testing. |
| Explicit calibration over a declared composite null | Treat the current discrepancy or raw p-value as a statistic and calibrate across an explicitly defined nuisance set, including uncertainty in that set. State the changed inferential target. | Conservatism may worsen power; a finite scenario grid supports only those scenarios, not uniform control over a continuum. |

The first direction has precedents in simulation-trained ABC summaries, but
parameter-estimation optimality is not test-calibration or power optimality;
see [Fearnhead and Prangle](https://arxiv.org/abs/1004.1112). The second requires
an explicit choice about nuisance parameters, rather than treating a prior
mixture as a worst-case guarantee; see
[Bayarri and Berger](https://www2.stat.duke.edu/~berger/papers/98-40.html).
These are candidate classes for assessment, not selected algorithms.

## What must be fixed before v2 validation

The replacement protocol must state its inferential target, full algorithm,
new and retained settings, nuisance/scenario domain, tolerances, calibration
and power rules, multiplicity treatment, failure rules, bank identities,
runtime/source hashes, seed domains and validation size. Retain the failed
low-survival challenge or explicitly justify a changed target to Barry;
do not silently omit it. Preserve v1's 8% null criterion and beta_min as the
baseline rather than loosening them to accommodate the exposed result.

Keep **development, calibration fitting and final outer validation separate**.
Any calibration data used to fit a correction belong on the development side
of the boundary. Freeze the candidate and its execution manifest before
opening untouched v2 validation outcomes. If a frozen bank is reused, say so:
the validation claim then concerns that bank, not automatic bank-to-bank
generality. Retain reference selection identifiers or sufficient compact
replay evidence in v2 to improve the specific v1 provenance limitation.

An independent implementation check and prospective review precede the next
freeze. Evaluate fresh validation once under the declared rules; retain all
blocks and failures. The empirical test stays behind those gates. Failed
power alone limits O1 under the current protocol and need not forbid a valid
O2 departure test; a failed null-calibration gate forbids those labels.

## Stop and return condition

Do not continue a larger-bank-only remedy if improved locality leaves the
mismatch or a properly interpreted oracle comparison points elsewhere.
Do not select a candidate merely because it fixes this one corner. If neither
of the two candidates offers credible calibration and scientifically useful
discrimination at feasible cost, return the method/scope/sample-size choice
to Barry with the failure evidence. Avoid an open-ended sequence of revisions
chosen against the same exposed outcomes.

Unresolved Stage B reconstruction, census-class/source mappings and close
prior-work checks remain on the project record. A successful v2 simulation
gate would not resolve them by itself. Publication, submission and a public
registration remain separate from ordinary repository synchronization.
