# Review of the paper outline and recovery-matrix corrections

Astra, 14 October 2026. Reviewed `notes/vortex_paper_outline_20261014.md` and
recovery-matrix §8 at `e614b238af7c900e678b5382b6c804d0422b15d9`, against the
existing protocol, exposure log, freeze, validation summary and independent
audits. No new analysis, source search, fitting or simulation.

**Disposition: proceed with drafting the completed results after the finite
wording corrections below.** The outline has the right core: exposed
reconstruction, failed prospective validation, bounded development comparisons,
and source-grounded case studies. The numerical headline results and kunanyi
execution claim check out. No further general review cycle is needed before
writing. The external-information experiment remains optional planned work,
not a dependency for this draft or a promised calibrated information curve.

## Essential corrections, ranked

### 1. Major — distinguish prospective validation from an exposed reanalysis

The title, introduction and section labels (outline lines 9, 15–16, 39, 46,
57, 69) currently stretch “pre-registered” across the whole study. The record
establishes a dated freeze before fresh **synthetic validation**, after published
outcomes, source values, reconstructed fits and empirical calibration summaries
had been inspected. In particular, the random-intercept primary was selected
after reconstruction results were seen; protocol §4.2 explicitly preserves that
fact. A fixed-procedure validation does not retrospectively validate the adaptive
history used to select it.

Use four evidence categories:

1. **Exposed historical reconstruction and source reconciliation.**
2. **Prospectively frozen v1 synthetic validation**, after documented development.
3. **Exposed post-validation development diagnostics and candidate screens.**
4. **Optional planned work**, without results or execution authority implied.

“Outcome-exposed reanalysis with prospectively frozen simulation validation” is
supported by the record. If “preregistered” is retained, identify the archived
registration/freeze, date and limited scope; avoid a blanket preregistered-study
title. A workable neutral title is *Testing extinction-vortex signatures in
outcome-selected population counts*.

Also narrow the claim-register prohibition on **any empirical effect estimate**
(line 137). Historical reconstructed T1–T4 estimates already exist and belong in
the reconstruction table with their exposure label. The prohibited new claim is
an empirical conditional-null p-value, O-label or feedback inference; it is not
reporting the already exposed reconstruction. The “within 0.0009” summary is
accurate but must retain the ±0.0005 criterion: RI T1 and T3 fail it; T2 and T4
pass; T5 remains unreconstructed.

Evidence: [exposure log](vortex_exposure_log.csv), E01, E13–E16 and E20–E28;
[protocol](vortex_protocol.md), §4.2; [Stage B record](../analysis/astra/stage_b/README.md);
[accepted freeze](astra_protocol10_freeze_20261011.md).

### 2. Major — remove the renewed causal exclusion of locality

The headline says the nuisance law, **not locality**, drove failure (lines
24–25). The synthesis says information **fixed calibration** (97–99), while the
more careful D3 bullets below the headline correctly call it one-corner
reference sensitivity. These are inconsistent. D3 replaced the whole six-parameter
reference law and changed its bank and neighbourhood geometry. Its improvement
despite wider original-C radii does not rule out approximation/locality effects,
isolate survival, prove nonidentifiability or establish calibrated performance
over the nuisance space. The seven of 200 oracle rejections are compatible with
nominal error at this tested corner.

Replace the headline clause with: “At one low-survival corner, replacing the
mixed reference with the generating nuisance values reduced rejections from
34/200 to 7/200.” Call section 5 **Development diagnostics and attempted repairs**.
The synthesis can report a practical discrimination loss for the specified A
and B screens; it cannot generalize to all count-only repairs. Replace “fixed
calibration” with “reduced the excess rejection rate at the tested corner.”

Evidence: [D3 audit](astra_v2_results_review_20261012.md), §2; [A-power review](astra_a_power_deep_dive_review_20261014.md), §§1–2.

### 3. Minor — state the covariance rule and distinct gate roles exactly

“Ledoit–Wolf covariance” (line 61) suggests universal shrinkage. The frozen
procedure uses the sample covariance from an independent training set and
Ledoit–Wolf shrinkage only when its condition number exceeds 10^6. **No v1 trial
required shrinkage.** Write `K = 2,000; R_train = R_test = 2,000`, rather than
one ambiguous R, and retain conservative tail ties and failure bounds.

The null gate is an upper one-sided 98.75% Clopper–Pearson bound ≤ 0.08 for
each of four 1,000-trial scenarios, equivalent to ≤ 60 non-acceptances. The
power criterion is a lower one-sided 95% bound ≥ 0.70, requiring ≥ 224/300;
it governs eligibility for **O1**, rather than being interchangeable with the
V-fail null gate. A failed power gate alone preserves O2/O3 routes. The
fit-stop threshold is **greater than 2%** in a gating block. Here the null
failure overrides all empirical labels and the guard refuses execution.

Evidence: [protocol](vortex_protocol.md), §§1, 3.4 and 4.3;
[executable scoring rule](../analysis/fable/calibration/e2e_benchmark.py);
[validation audit](astra_validation_v1_audit_20261011.md).

### 4. Major — describe Q2 and the comparison figure as descriptive evidence

Keep the complete Q2 profile, labelled **detection rates of a procedure that
failed its null-calibration requirement**. A high detection rate under a strong
alternative does not repair V-fail or identify the mechanism. In Figure 4,
label the low-s null scenario separately from prior-predictive alternative
nuisances: this is not a matched-nuisance size/power frontier. B's cheap screen
remains specific to its exposed calibration table and samples; it is not a
validated competing procedure. The outline already states that limitation and
should retain it in the figure caption. Add A's β_min result, 21 → 11/300,
alongside its stronger-effect loss if both effects are discussed.

### 5. Major — narrow the novelty claim and preserve the source-check gate

“Within-series tests on complete extinction trajectories” (lines 43–44) can
imply executed single-population tests and verified complete counts. The current
estimator pools nine series, empirical Q1 was never run, and the census ledger
does not establish complete counts for every source. Describe the contribution
as a **matched-outcome test of reconstructed pooled terminal-trajectory
statistics, with measured calibration and discrimination limits**.

Wittmer et al. is relevant prior art, but not the only comparison. Existing
project records already identify Boettiger–Hastings on outcome-selection bias,
Hefley et al. on external deterioration versus density dependence, and
Griffen–Drake/Lande on conditioned terminal decline. They also record that
Fagan–Holmes acknowledged extinct-only selection. Do not imply they overlooked
that restriction. Define the focal “no-feedback” contrast as absence of the
specified abundance-dependent feedback in expected growth, not absence of every
process called an extinction vortex.

These are **existing literature-audit pointers**, not newly checked primary
texts. Before final novelty wording, verify the precise supporting passages and
resolve explicitly flagged abstract/preprint-only coverage. That narrow
source-check gate remains open; it does not block drafting the verified methods
and results or justify another broad novelty search now. Evidence:
[initial source review](astra_round1_review_20261005.md), §3;
[protocol corrections](vortex_protocol.md), §§9.3–9.4;
[Wittmer audit](astra_option3_phase2_source_audit_20261013.md), §4.

## Verified results and execution

The machine-readable [v1 summary](../analysis/fable/calibration/validation_v1/validation_summary.json)
agrees with the prior independent raw audit:

| Result | Verified value |
|---|---|
| Null blocks 1–4 | 46, 41, **148**, 30 rejections per 1,000; only low-s fails |
| β_min | 21/300; lower one-sided 95% bound 0.04738; O1 criterion fails |
| Descriptive blocks 6–14 | 25, 16, 26, 17, 15, 17, 42, 40, 28 per 300 |
| Stronger effects Δ10 = 0.3 / 0.5 | 118/300 / 206/300 |
| Fitted-parameter stress block 17 | 11/300; no unresolved trials; descriptive only |
| Failures | Zero in gating blocks; four failed T vectors overall, in blocks 14–16; all 7,900 trials resolve |
| Validation host | `n001.kunanyi`; Python 3.11.7, R 4.3.3, nlme 3.1.171 |

Thus the outline's kunanyi attribution is correct. Deep-server built/staged
inputs and hosted later independent rescoring/development; the freeze's
deep-server preflight was not the completed validation runtime. D3's paired
−0.135 interval and the A/B counts in the outline match the existing audit
records. “Insufficient identification” is the protocol's disposition of this
failed procedure, not a general theorem about information in the counts.

## Recovery-matrix §8

Accept the addendum as superseding the identified original statements. It
preserves census classes, uncertainty provenance, qualified public availability,
shared-monitoring information and unresolved Banff chronology. Two small wording
repairs remain:

- Donor colony unknown means the 1996 transplant is **not established as a
  Haley removal**; replace the categorical “It is not a Haley removal.”
- Maligne ID 378 has a blank **total and all composition fields**, while its
  date, location and identifier exist; replace “entirely blank record.”

Use §8 and the linked source audits when drafting, rather than copying the
superseded verdicts from earlier matrix sections. Neither repair requires new
data or another review loop. Parent reviews the external-information design;
the separate Haley reviewer covers its descriptive protocol.

14 October 2026, 14:32 AEDT (Australia/Hobart).
