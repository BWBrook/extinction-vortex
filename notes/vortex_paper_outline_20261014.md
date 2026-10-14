# Paper outline: core results plus narrowed deep dives

Fable, 14 October 2026 (Australia/Hobart). This is a draft for Astra's review.
It follows Barry's framing of 13 October (STATUS; board 1602) and Astra's
review (`notes/astra_a_power_deep_dive_review_20261014.md` §4).

**Status.** Outline only: no new analysis and no claim beyond the archived
evidence. Section labels keep three tiers of evidence apart:
- **pre-registered** (the frozen v1 validation);
- **development** (exposed, post-validation diagnostics);
- **planned** (not yet specified or run).

## Working title and one-sentence claim

*Can extinction-vortex signatures be read from counts alone? A pre-registered
reanalysis of the Fagan–Holmes populations.*

**Claim, limited to what the record supports.** For the nine Fagan–Holmes
populations, a matched no-feedback reference built from the counts alone did
not give a validated test of vortex signatures:
- it failed pre-registered null calibration at a low-survival nuisance
  setting;
- it had low power at a risk-defined feedback strength;
- in our development screens, the reference's nuisance law, not locality in
  the summary space, drove the failure at that setting.

This is a limitation of the specified inferential procedure. It is **not
evidence for or against feedback** in the empirical populations, whose test
was never run.

## Sections

**1. Introduction.**
- The extinction vortex as a conservation idea.
- Fagan & Holmes (2006): T1–T4 statistics on nine trajectories that ended in
  extinction.
- The inferential question their analysis leaves open: compared with which
  no-feedback process, conditioned the same way?
- Our contribution: a pre-registered, matched, independently audited
  reanalysis; what it can and cannot identify; and what extra information
  would be needed.
- Prior art to cite fairly: Wittmer, Sinclair & McLellan (2005), comparing
  among caribou populations. We claim within-series tests on complete
  extinction trajectories, not a first test of density-dependent decline.

**2. Data and reconstruction** (pre-registered).
- The nine series (Williams et al. 2021 / F&H): sources, census classes and
  windows.
- The source conflicts and unresolved provenance already recorded, including
  intervention histories, stated case by case without blanket "closure"
  claims.
- Reconstruction of T1–T4 with a random-intercept multilevel model with AR(1)
  errors. The historical reconstruction is **not passed** (closest within
  0.0009 of the published values). The study is an exposed reanalysis of the
  reconstructed estimand, not of F&H's exact estimator.

**3. Methods** (pre-registered).
- Null M0 (ar_cat) with exact matched selection S and the cap event A.
- Prior (b).
- Conditional calibration: k-NN on the calibration summaries C, K = 2,000,
  R = 2,000, Ledoit–Wolf covariance, conservative ranks.
- Alternatives: M_A, M_D, M_O and mixtures, with β_min risk-defined
  (Δ10 = 0.075).
- Validation design: four null gates, a power gate and a fit-failure stop,
  with fixed denominators.
- Freeze, independent acceptance and execution on kunanyi.
- Exposure log and deviations.

**4. Results I: pre-registered validation** (v1).
- V-fail: the low-s null gave 148/1,000 rejections, against at most 60
  allowed. The other three null scenarios passed: 46, 41 and 30.
- Power at β_min: 21/300.
- Q2 discrimination profile (blocks 6–16) and the stress check (block 17).
- Fit-failure accounting, the independent audit and the reproducible summary.
- Consequence under protocol §1: the empirical Q1 is reported only as
  *insufficient identification*, and the guard refuses the run.

**5. Results II: why it failed** (development; exposed outcomes; labelled
throughout).
- **D1c/D2.** The libraries' nuisance values were displaced at the corners,
  shown by association only. D2 neither supports nor rules out nuisance
  mixing.
- **D3, paired oracle.** On the same 200 low-s outers, a fixed-θ reference
  gave 7 non-accepts against 34 for the prior reference. Difference −0.135
  (−0.194, −0.080); the T1/T2 shift was removed.
  - This is reference-sensitivity evidence at one corner, with all six
    nuisances fixed.
  - It neither proves the trajectories uninformative nor shows global oracle
    calibration.
- **Candidate A (C+).**
  - A0: displacement unchanged.
  - A-screen: 21 → 11/200 non-accepts.
  - A power: 206 → 28/300 at Δ10 = 0.5.
  - Practical discrimination evidence only, with no causal attribution.
- **Candidate B (grid-calibrated p).** The cheap screen, specific to its table
  and sample, gave β_min 21 → 6/300 and Δ10 = 0.5 206 → 98/300. Deferred.
- **Synthesis.** The two obvious count-only repairs trade calibration against
  discrimination. What fixed calibration in D3 was information about the
  nuisance values.

**6. Results III: how much external demographic information is needed**
(planned). See `vortex_external_info_design_20261014.md`. It reports
calibration and power against the declared information levels for:
- s/f-only information;
- an ideal truth-centred benchmark;
- noisy and biased external evidence;
- baseline-phase versus decline-phase evidence.

**7. Case studies** (narrowed deep dives; planned).
- **Haley Lake marmots.** A source-grounded descriptive case
  (`vortex_haley_deep_dive_protocol_20261014.md`): what age structure,
  marked-animal persistence, litters and movement add, and what they cannot
  identify.
- **Maligne and Purcells Central caribou,** after the census-class and
  time-label crosswalk. Author contact is Barry's decision.
- Any formal single-case feedback test is conditional on its own statistic,
  observation model and prospective validation. The nine-population
  random-intercept estimator is not a one-colony procedure.

**8. Discussion.**
- What count-only vortex diagnostics can and cannot show.
- Implications for conservation assessment: count trajectories need
  demographic context.
- Limitations:
  - a single model class for the null;
  - source conflicts;
  - exposure;
  - the unpassed reconstruction;
  - development evidence that is not validation;
  - unresolved case-level ledgers.

## Claim register (wording rules)

| Allowed | Not allowed |
|---|---|
| "the specified procedure failed its pre-registered null gate" | "the vortex is absent" or "the data show no feedback" |
| "insufficient identification" (protocol §1 label for the failed procedure) | any empirical p-value, O-label or effect estimate for the nine populations |
| "at the low-s corner, replacing the reference's nuisance law removed the excess" | "survival alone causes the failure"; "the counts cannot identify s" as a theorem |
| "A's null improvement came with a large discrimination loss in our screens" | "A works by dilution" (not tested causally) |
| "no suitable individual fate histories were found in the sources inspected" | "the data do not exist" |
| "rates measured during decline may contain feedback" | "decline-phase rates are a no-feedback baseline" |

## Figures and tables (draft list)

1. The nine trajectories, with source-labelled windows.
2. v1 validation gates and the Q2 profile, as a forest of rejection rates with
   exact intervals.
3. D3 paired outcomes and the T1–T4 z shift, prior reference against oracle.
4. Calibration against discrimination for v1, A and the B screen: null
   non-accept rate against power.
5. The information curve from §6 (when run).
6. The Haley case panel: series, stage composition, tagged persistence with
   denominators, and arrivals.

**Supplement.** Protocol and freeze package, exposure log, audits, all
receipts and the source-recovery matrices.

## Decisions for Barry (none needed now)

- Author contact: F&H/Hedeker for the historical estimator; caribou collar
  histories.
- Whether the secondary Williams analysis (Q3) is in scope.
- Target journal and length. The structure above suits a full article with a
  substantial supplement.

---

**Revision note (14 October, after Astra's outline review).**
[`vortex_manuscript_core_draft_20261014.md`](vortex_manuscript_core_draft_20261014.md)
supersedes this outline's wording on the following:
- **Four evidence categories:** exposed reconstruction [R], frozen synthetic
  validation [V], exposed development [D], optional planned work [P].
- **Title and framing:** "outcome-exposed reanalysis with prospectively frozen
  simulation validation", not a blanket "pre-registered".
- **D3:** reported as 34/200 → 7/200 at one corner, with no
  "nuisance law, not locality" claim.
- **Covariance:** sample covariance, with shrinkage only above condition
  number 10⁶.
- **Gates:** the null gate is kept separate from the O1 power criterion, and
  Q2 is descriptive after V-fail.
- **Reconstruction:** the reconstructed slopes are reportable, with the
  ±0.0005 criterion stated.
- **Novelty:** narrowed to "a matched-outcome test of reconstructed pooled
  terminal-trajectory statistics", with the wider prior-art pointers flagged
  for a primary-text check.
