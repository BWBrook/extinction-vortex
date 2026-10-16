# Stage 1c fitted-stage draft, revision 2 (for challenge; not commissioned)

Fable, 16 October 2026. Revision 2 incorporates Astra's 1755
(`notes/astra_stage1bc_design_review_20261016.md` P1/P2). It fixes what must
be settled before any fitted execution. It is not a protocol freeze, and it
commissions nothing. The sampling it needs is
`notes/vortex_stage1b_design_20261016.md`.

## 1. Question (neutral)

**Aim.** On exposed development outers, how does stylised external rate
evidence E (noisy, n = 30 or 300) change null non-acceptance, detection and
computational availability, relative to a matched n = 0 analysis under the
same reference construction?
- **Cells:** four scenarios (b1 prior-predictive null, b3 low-s null, b5 M_A
  at β_min, b16 M_A at Δ10 = 0.5) × n ∈ {30, 300}.

**What it does not claim** (revision 1's wording "restore the calibration v1
lacked" is withdrawn):
- that v1's failure was caused solely by finite-bank support;
- that exact informative sampling guarantees fixed-θ calibration, at the
  low-s corner especially;
- anything about real marked-animal years, a minimum field sample size,
  empirical inference or uniform validity.

E informs two stylised marginal rate functionals. The two n levels are
prebound noisy draws, not necessarily nested observations from one study.
Any method chosen later needs its own freeze and prospective validation on
fresh outers.

## 2. Libraries and loading

**Library.** Each population-outer-cell uses the first K = 2,000 retained
pairs from Stage 1b, in global stream order, from its verified complete
prefix.

**The matched baseline** is the n = 0 library of the same population-outer.
It is shared by the n = 30 and n = 300 cells, with one baseline analysis per
outer and scenario. The pairing is kept in every comparison and every
uncertainty calculation.

**Stage 1c consumes these libraries as they are.** It does not recompute MAD,
select a new neighbourhood, or reselect nearest pairs: the fixed closed ball
was already enforced in Stage 1b.

**Reused v1 components:**
- T fitting;
- the training mean and covariance;
- the Mahalanobis rule (Ledoit–Wolf only above condition number 1e6);
- tie handling;
- the p_lo/p_hi bounds;
- the scorer, contract v3.

**A small deterministic check** of the library-loading adapter precedes any
fitting.

## 3. Resampling

**Per analysis:** R_train = R_test = 2,000 index draws with replacement from
the K-member library.
- Draws come from bound streams, as sequential segments of one fixed stream.
- Training and testing use independent draws, and the training matrix is
  never reused as the test matrix.
- These are independent draws **conditional on the finite library**, not
  4,000 fresh paths from the target. More resamples do not remove that
  approximation.
- Any later prospective validation must include the same finite-library
  construction.

**Independent-library check.**
- **The cases** are the named subset in the Stage 1b design §5: 8 outers ×
  3 n, 24 paired analyses, 216 extra libraries from stream namespace 3.
- **What it reports:** paired p_hi differences and decision changes, with the
  fit and resampling rules held fixed.
- **What it can show:** numerical sensitivity on those named cases only. It
  is not calibration evidence or a universal finite-library bound.
- **Its library is separate from the crossing-batch surplus.**
- **A material change** in the substantive conclusion calls for an explicit
  follow-up decision. There is no automatic retuning or bank expansion.
- **One library is never preferred** over the other.

## 4. Inventory

**Primary analyses:**
- 1,600 informative (8 cells × 200 declared outers);
- 800 n = 0 baselines (4 scenarios × 200);
- **2,400 in all,** plus 24 check analyses.
- Without caching, each analysis needs 4,001 T-vector evaluations: about
  9.6 × 10⁶ evaluations.

**Cost:** about 1,200 worker CPU-h (0.5 per analysis).

**Every primary comparison uses all 200 declared IDs.** No outer is ever
replaced or dropped.

## 5. Outcome coding (as contract v3)

**Null scenarios (b1, b3).** Every outcome other than `accept` counts as a
non-accept. That includes a library shortfall (failure to fill K within the
cap), numerical or fit indeterminacy, and missing work.

**Alternatives (b5, b16).** Only `reject` is a detection. Every other outcome
is a nondetection.

**Reasons** (shortfall, indeterminacy, missing) are reported separately, by
cell and population.

**Tables:**
- three-way accept/reject/indeterminate tables are reported alongside the
  binary coding;
- differences in fitted statistics or p-values use only complete pairs, with
  the complete-pair denominator shown;
- procedural binary comparisons include failed baselines under the rules
  above, so they measure the whole procedure, availability included;
- **joint** availability (the informative library and its matched n = 0
  library both complete) is reported, not only informative availability.

## 6. Gates: family, levels and meaning (resolved for challenge)

**Family.** The family is the four informative null cells: b1 and b3, each at
n = 30 and 300.
- Each gets a **one-sided 98.75% Clopper–Pearson upper bound ≤ 0.08**: at most
  7 non-accepts of 200.
- **Power:** the b5 (β_min) cells at n = 30 and 300 need a **one-sided 95%
  CP lower bound ≥ 0.70**: at least 152 detections of 200.
- **Outside the gated family:**
  - b16 (Δ10 = 0.5) is descriptive high-effect detection;
  - the n = 0 baselines are comparators, reported with the same intervals.

**Meaning.** These are **development adequacy criteria**. They are not the
validation gate of a frozen method. At 200 outers they are stringent. The
probability that a cell passes:

| True null non-accept rate | 0.01 | 0.02 | 0.03 | 0.04 | 0.05 | 0.06 |
|---|---|---|---|---|---|---|
| P(≤ 7 of 200) | 0.999 | 0.951 | 0.746 | 0.450 | 0.213 | 0.083 |

| True power | 0.75 | 0.80 | 0.85 |
|---|---|---|---|
| P(≥ 152 of 200) | 0.408 | 0.931 | 1.000 |

**The primary result is estimation.**
- Each cell's non-accept or detection rate, with exact intervals.
- Paired differences against the n = 0 baseline, with McNemar and Newcombe
  method 10, and against v1 where defined.
- A **non-pass** means adequacy was not established at this precision; it
  does not by itself establish miscalibration.
- **No automatic enlargement:** neither the outer count nor the criteria
  change after fitted results are seen.
- Matching v1's original 60/1000 operating characteristic would need about
  1,000 outers per cell, about 5 × the sampling. That is not proposed.

## 7. Open before fitting

1. **Stage 1b completion** within its caps and ceilings.
2. **Barry's authorisation** of Stage 1c, separately from Stage 1b.
3. **Astra's agreement** to the gate meaning in §6, which is bound in the
   Stage 1c settings before any fit.
4. **The adapter check and the bound streams,** in a Stage 1c settings file
   checked by Astra.
