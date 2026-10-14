# External demographic information: simulation design, revision 2 (draft for review)

Fable, 14 October 2026 (Australia/Hobart).

**Status.** Design only: no run is commissioned and the experiment is
optional. It does not delay the core paper or the Haley case.

**Revision 2** follows Astra's review
(`notes/astra_three_drafts_review_20261014.md`, board 1614) and replaces
revision 1 (commit e614b23). Revision 1's arms are reduced to the eight-cell
first diagnostic, and its errors are corrected:
- the rate labels;
- the selection law;
- the fixed-ESS neighbourhood;
- the seed collision;
- the ideal comparator.

## 1. Question and law

**Question.** In the existing v1 C-conditioned T1–T4 test, suppose the
k-NN reference is reweighted by independent evidence E about two rate
functionals. How do null non-accept rates, detection rates and reference
support change?

**Repeated law: unchanged from v1.**
- θ and the whole path are drawn jointly from prior (b) and M0 (or M_A).
- The result is then kept only if it meets selection S and the cap event A.
- The primary bank was built exactly this way. Its retained members are
  therefore draws from p(θ, N | S, A).
- Likelihood weighting of retained members by L(E | θ) targets
  p(θ, N | S, A, E). No inverse-selection weighting is needed.
- A scheme that held θ fixed until a selected path appeared would be a
  different law. It is not used.

**E is independent of N given θ.** Shared-year or dependent E is deferred. It
would need a joint law, or an explicit misspecification label.

**No guarantee.** The ideal exchangeability argument does not guarantee
fixed-θ calibration or finite-bank calibration. Both are what the experiment
measures.

## 2. Measurement model (stylized)

**Rate functionals.** For each population:
- s̄(θ) = (1 − δ p_c) · E_Z[logit⁻¹(logit s + σZ)], Z ~ N(0, 1);
- f̄(θ) = (1 − δ p_c) · f.

These are the stationary, **unselected** M0 mean annual survival and
recruitment per counted individual. They are census-class marginal rate
functionals, not realized annual field rates.

**Stylized evidence.**
- k ~ Binomial(n, s̄(θ_true));
- r ~ Poisson(n · f̄(θ_true)).

n is an **ideal information index**, not a field sample size: "n marked
animal-years" is an analogy only. Shared annual environment and catastrophes,
which induce extra variance and survival–recruitment dependence in real
studies, are omitted by construction.

**What the likelihood informs.** L(E | θ) depends on σ, p_c and δ as well as
on s and f. It informs two rate functionals, not s and f alone.

**Ideal comparator (I).** The truth-centred version replaces the sampled
(k, r) with their expectations. Its log-weight is

log w_I(θ) = n[s̄₀ log s̄(θ) + (1 − s̄₀) log(1 − s̄(θ))] + n[f̄₀ log f̄(θ) − f̄(θ)],

with s̄₀ = s̄(θ_true) and f̄₀ = f̄(θ_true): the expected binomial and Poisson
log-likelihoods at the true functionals. **Realistic E** uses the sampled
(k, r) in the same likelihood.

## 3. Reference construction (fixed K)

- **Membership.** v1's own K = 2,000 neighbours in the frozen C metric (v1
  mask and MAD), queried with k = K.
- **Draws.** The R_train + R_test reference trajectories are drawn from the
  members with probability proportional to w = L(E | θ) (or w_I). This is
  the only change to `run_chunk`'s reference draw.
- **Not used.** Expanding the neighbourhood to a fixed ESS confounds
  information with C-locality and is a different procedure.

**Stage 0 diagnostics** (no fits), per dataset × population:
- the weight ESS, (Σw)² / Σw², within the K members;
- the largest weight share;
- the original-C K-th distance, unchanged from v1.

**Support rule.**
- A dataset fails support if **any** of its nine populations has ESS < 100.
- Failure rates are reported **by scenario as dataset-level any-of-nine
  failures**, not as pair rates. Even 1% independent pair failures give
  8.65% dataset failures.
- A failed dataset is indeterminate and counted in the fixed denominator, as
  a null failure or a non-detection.

## 4. First diagnostic (eight cells)

**Cells.** Realistic E, unbiased, n ∈ {30, 300}, crossed with four scenarios:

| Scenario | v1 block | Trial IDs |
|---|---|---|
| prior-predictive null | b1 | 0–199 |
| low-s null | b3 | 0–199 |
| M_A at β_min | b5 | 0–199 |
| M_A at Δ10 = 0.5 | b16 | 0–199 |

These are exposed v1 outers, used for development only. Their true θ is
logged, so E can be drawn per outer. Each pairs with its stored v1 outcome.
Stage 0 also reports w_I diagnostics for the same cells; this is cheap and
involves no fits.

**Stage 0 (no fits).**
- All eight cells × 200 outers × 9 populations: weight diagnostics only.
- Cost: one bank pass, about 30 min on deep-server.
- The report is returned to Astra **before any fitted stage is proposed**.

**Stage 1 (fitted; proposed only after Stage 0 review).**
- The same eight cells, 1,600 analyses.
- On kunanyi this is about 40 min of fits on 48 nodes, plus unbenchmarked
  weighting and setup, which Stage 0 will measure.
- Reported per cell:
  - non-accepts or detections, with exact intervals;
  - the paired table against v1, with McNemar and Newcombe method 10;
  - mean z;
  - support failures;
  - fit failures.
- No extension and no retuning.

**Deferred:**
- bias arms;
- the other null corners;
- the baseline-against-decline timing question (the stored outers lack
  annual environment and survivor/recruit histories, and g acts on survival
  odds);
- shared-year dependence;
- the oracle-6 power arm (needs a concrete bounded plan before any cost is put
  to Barry).

## 5. Streams (disjoint and bound)

Every stream comes from NumPy `default_rng` seeded with an integer sequence,
which makes them collision-free by construction.
- **E draws:** `default_rng([20261014, 1, cell, trial, population_index])`.
- **Reference draws:** `default_rng([20261014, 2, cell, trial])`, passed to
  the reference sampler. Populations are drawn in the frozen design order.
- **Coding:** cell = 0–7 (n index × 4 + scenario index); population index =
  frozen design order 0–8.

The full stream table, settings and helper hashes are bound in the inputs file
before Stage 0, as in the A power screen.

## 6. What it can and cannot show

**Can show:** whether stylized rate information at two levels restores
support-limited calibration where v1 failed (b3), and what it costs in
detection (b5, b16), on development outers.

**Cannot show:**
- realistic field-study performance (the measurement model is stylized);
- validity for Haley or caribou;
- anything empirical about the nine populations;
- uniform validity.

A method chosen later would need freezing and prospective validation on fresh
outers.
