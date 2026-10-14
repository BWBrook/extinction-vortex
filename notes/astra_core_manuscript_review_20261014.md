# Review of the core methods/results manuscript

Astra, 14 October 2026. Target: `vortex_manuscript_core_draft_20261014.md` at
`ec72dd0330b6acd440aa85d2507c28e465ed2020`. Applied the independent-reviewer
skill. Reviewed frozen definitions, executable code and retained audits; no
new empirical statistics, fits, population simulations or literature search.

**Recommendation: APPROVE WITH CHANGES for continued drafting.** The reported
results reproduce the existing evidence, and the four evidence categories are
an improvement. Correct the claims and definitions below before treating the
methods/results as verified manuscript text. These are finite manuscript
repairs, not grounds for another experimental or general protocol round.

The apparent **0.10 versus Δ10 = 0.075 discrepancy is not a changed target**;
the two numbers describe different quantities. The **D_s equation has the
correct sign** under reverse-time count indexing. Neither should be “fixed”
by changing the frozen analysis.

## MAJOR — the abstract still claims demographic data are necessary

Lines 59–62 move from failure of this procedure to a general necessity claim
about declining count series. The study has neither ruled out all count-based
procedures nor shown that additional demographic information is sufficient.
D3 fixes six true nuisance values at one corner; it does not identify the
information realistically needed. Keep the conclusion procedural: **the
specified count-based procedure did not support empirical feedback inference;
the reference sensitivity and case evidence motivate testing additional
demographic information.**

Likewise, lines 51–53 and the development summary should distinguish the
measured A comparison from B's post-hoc rescore using the same low-s empirical
calibration table. B has no fresh null-calibration result. Its lost detections
are real, but it is not a second independently demonstrated calibration repair.
Avoid “only with” as a claim of an inevitable trade-off. Evidence:
[A-power audit](astra_a_power_deep_dive_review_20261014.md), §§1–2;
[B screen audit](astra_v2_plan_review_20261011.md), §3.

## MAJOR — restore the limits of chronology and reconstruction evidence

Three claims overstate their records:

- **“Before any design decision” (86–88):** exposure accumulated in phases.
  Published outcomes were known before initial drafting; reconstruction fits
  preceded selection of the RI primary; empirical C and development outputs
  preceded selection of the null/reference design; the final procedure was
  then frozen before fresh v1 validation. Replace the blanket chronology with
  that sequence. “Before any trial” (169–170) should specify **fresh v1
  validation trial**, since development trials had already run.
- **Likelihood agreement to 10⁻¹² (105–106):** the agreement is at **matching
  covariance parameters**, not a claim that independently optimized fits have
  identical likelihoods. The 32-row comparison receipt records a maximum
  matched-parameter log-likelihood difference of 6.25×10⁻¹³; some separately
  optimized models differ. Also say “separate implementations”: Astra had
  seen Fable's fitted summaries before implementing its own estimator.
- **“Each was specified and bound before its fits” and “neighbourhoods
  exactly” (225–229):** remove these blanket claims. D1/D2 were post-hoc;
  some screens do no new fitting; D3's audit does not have a pre-launch seal
  for all payloads and its runtime was recorded at report time. D1c2 restored
  the original k=K query and reproduced **rounded logged K-th distances**,
  but v1 did not retain historical neighbour IDs. Tied boundary membership
  was demonstrably query-sensitive. Distances alone do not establish exact
  historical membership.

Use: “Development diagnostics and fixed candidate screens were audited with
the provenance limits recorded in the supplement. Reconstructed neighbourhoods
matched v1's logged distances; historical membership at ties was not directly
verified.” Evidence: [exposure log](vortex_exposure_log.csv), E01, E13–E16,
E20–E30; [Stage B comparison](../analysis/astra/stage_b/README.md), final
section; [D3/D1c2 audit](astra_v2_results_review_20261012.md), §1.

## MAJOR — make the statistical methods reproduce the frozen procedure

### Time, sign, residuals and gaps (93–103)

Define calendar endpoint T, `N_s = N(T−s)`, and attach each annual log change
to its **later census**. Then

`D_s = log[N(T−s) / N(T−s−1)] = log(N_s / N_{s+1})`.

The final transition has s=0. Counts 20→10→1 give D_1=−0.693 and D_0=−2.303:
the more severe terminal decline is consistent with a **positive** slope on
years remaining. Keep the equation's sign. Explain that more negative T3/T4
represent larger squared residuals nearer s=0.

T4 is not simply T3 after deleting a row. The code **refits the mean model on
s≥1**, squares that model's level-1 conditional response residuals, and fits
their slope on s. Add this explicit definition. Calendar gaps are excluded
from log-change regressions rather than annualised; AR(1) retains the integer
s positions, and the generator propagates annually through unrecorded years.
The deposited primary windows have no such gaps; this rule still defines the
procedure and its fill sensitivities. Endpoint replacement by one applies to
the log-growth calculation, not a correction to the source count.

Evidence: frozen [tstats_batch.R](../analysis/fable/calibration/tstats_batch.R),
lines 22–34; protocol §§2.1 and 3.4. Two hand-specified arithmetic fixtures in
the receipt verify the indexing and gap mapping without fitting anything.

### Priors, feedback and risk target (119–167)

- **Prior:** the code draws a normal with **SD 1.5**. Under mean–variance
  notation write `logit(s) ~ Normal(0, 1.5²)`, as protocol §3.4 already does.
  The five other stated ranges match the frozen code. State the prior draws
  are independent before selection, with Gaussian stationary AR(1) innovations.
  These are design priors, not recovered demographic estimates.
- **Feedback:** state g(N)=1 for N≥50 and zero is absorbing. In the combined
  catastrophe model, g multiplies the **pre-catastrophe survival odds**;
  catastrophe multiplies the resulting survival probability and recruitment
  rate. The exact survival expression is
  `(1−δB_t) expit[logit(s)+σz_t+log g(N_t)]`. This avoids accidentally applying
  g to the odds of an already catastrophe-adjusted probability. The structural
  null excludes direct abundance effects given environment; it does not make
  abundance and an autocorrelated environment statistically independent.
- **Effect:** define `Δ10 = 1−g(10)`, a multiplier reduction at abundance ten,
  **not** a ten-year probability difference. β_min is the first point on the
  declared Δ10 grid (steps 0.025) with an estimated **at least 0.10 absolute
  increase** in reaching count≤1 within ten years from N0=20, at pooled
  component-wise library medians. With 100,000 draws per grid point, the
  frozen receipt gives baseline 0.41431, M_A 0.55012, difference **0.13581**,
  β_min=0.974519268 and Δ10=0.075 (g(10)=0.925). The preceding Δ10=0.05 point
  gives +0.08932. Thus retain both 0.10 and 0.075, but add their definitions,
  “at least,” N0 and the grid qualifier. It is not an exact continuous
  minimum or a minimum detectable effect.
- **Other alternatives:** the current M_D/M_O names alone cannot reproduce
  the Q2 rows. Add, or explicitly reference a frozen supplementary table of,
  the three M_D shift functions with Δ~U(0,2), step time uniform over annual
  steps, and the two detection laws `p(N)=1−0.3 exp(−N/10)` and `p=0.9`.
  Under M_O, the latent start is the specified plug-in `round(n0/p(n0))`,
  the recorded start remains n0, and selection concerns **recorded** counts;
  it does not require latent extinction. Mixtures use β_min. These scenarios
  are not matched in risk or vital-rate effect.

Evidence: frozen [bank.py](../analysis/fable/calibration/bank.py), lines
68–77 and 104–169; [effect-target code](../analysis/fable/calibration/effect_target.py),
lines 60–74; [frozen effect receipt](../analysis/fable/calibration/freeze_v1/effect_target_ar_cat.json);
protocol §§3.1–3.3.

### Conditioning, distance and failures (135–179)

Replace “populations we can only observe because they went extinct” with
**series included in this retrospective sample under the recorded terminal
rule**. Selection into the analysis is not the ability to observe a
population, and a recorded count≤1 is the operational event, not proof of
biological extinction. The finite-bank k-NN reference **approximates** C
conditioning. Exact exchangeability applies only to the ideal selected
prior-predictive law with exact conditioning; the pass criteria do not imply
exact 5% size or uniform nuisance control.

The scorer uses **squared Mahalanobis distance**,
`Q=(T−μ)'Σ⁻¹(T−μ)`. Calling it unsquared distance leaves tail ranks unchanged
but misdescribes the stored quantity. Use a separate symbol from log growth.
Write the bounds explicitly as `(1+e)/(R_test+1)` and
`(1+e+m)/(R_test+1)`, where e counts exceedances among valid test vectors and
m counts failed test vectors. R_test stays fixed at the intended 2,000,
giving denominator 2,001; it is not reduced to the number of valid test vectors.

Add the other indeterminate cases (failed observed vector, malformed output,
unusable covariance and exhausted sampling budget); ≤40 failed training
vectors are omitted from covariance estimation, >40 makes the trial
indeterminate. A failed vector means any missing T1–T4, not each of its four
model fits counted separately. Unresolved outer trials count as non-accepts
for null gates and nondetections for the O1 power criterion. Sampling-budget
failures remain in those outcome denominators but not the fit-failure
denominator. The fit stop is **>2%** in a gating block. Give the supplementary
algorithm these details if main-text brevity requires it.

Evidence: frozen [scorer](../analysis/fable/calibration/e2e_benchmark.py),
`fresh_selected`, `p_bounds` and `outcome`; protocol §§2.1, 3.4 and 4.3;
[accounting acceptance](astra_protocol10_freeze_20261011.md).

## MINOR — execution wording and verified numbers

“48 nodes” should be **48 one-node PBS slot jobs**, the documented execution
unit; the retained note does not establish 48 distinct physical hosts. Kunanyi
and the listed preflight versions are correct.

The reconstruction table, all 17 validation totals, 7,900 trials, four failed
vectors, 13.46–29.90 million selected paths per primary-bank population and
the risk-target receipt reproduce. D3, A and B values match their prior audit
reports. Their numerical results need no amendment. Preserve the current
qualifications on D3, Q2, protocol-only “insufficient identification,” and the
unrun empirical test. The optional external experiment and final primary-text
novelty check remain separate from completing this core draft.

## Verification and limits

[core_checks.py](../analysis/astra/artifact_review_20261014/core_checks.py)
produces [core_checks.json](../analysis/astra/artifact_review_20261014/core_checks.json).
It verifies that four reviewed implementation files are byte-identical to
frozen `52779d0`, checks all 17 validation totals and gate/failure summaries,
reconciles the effect target and bank metadata, and performs two pure
arithmetic mapping examples. Run from the repository root:

`python3 analysis/astra/artifact_review_20261014/core_checks.py OUTPUT.json`

This checks manuscript statements against existing evidence. It does not
repeat the prior raw-T audits, reconstruct historical neighbour membership,
replay generators, reopen empirical inference or audit the new Haley artifacts.
Only this memo and its two small receipts were written.

14 October 2026, 15:08:24 AEDT (Australia/Hobart).
