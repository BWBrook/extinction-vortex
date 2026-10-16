# Stage 1c fitted-stage draft (for challenge; not commissioned)

Fable, 16 October 2026. This is the separate fitted-stage draft that review 1657
§4 requires alongside the Stage 1a report
(`notes/vortex_stage1a_report_20261016.md`). It fixes what must be settled
before any fitted execution. It is not a protocol freeze, and it commissions
nothing. Its size depends on the Stage 1b decision, which is still open.

## 1. Question

**Aim.** On exposed development outers, does stylised external rate evidence E
(noisy, n = 30 or 300) restore the support-limited calibration that v1 lacked?
And what does it cost in detection? This is design §6, "can show".
- **Cells:** four scenarios (b1 prior-predictive null, b3 low-s null, b5 M_A
  at β_min, b16 M_A at Δ10 = 0.5) × n ∈ {30, 300}.
- **Comparison:** each cell is compared with a matched n = 0 analysis under
  the same reference construction.

**Out of scope:** empirical inference, field validity, and uniform validity.
Any method chosen from this stage needs its own freeze and prospective
validation on fresh outers.

## 2. Reference-library law

**Library.** For each population-outer-cell, the reference library is the
first K = 2,000 retained (θ, path) pairs, in stream order, from the Stage 1a
sampler law. That law, unchanged:
- θ is drawn from prior (b) and accepted by L(E | θ)/M_E (Poisson, then
  binomial);
- one null path is simulated per accepted θ;
- the pair is retained if it passes S, A and the closed full-precision C-ball
  of its outer (all ties eligible).

**Streams.** Streams are `default_rng([20261015, 2, setting, batch])`, as in
Stage 1a.
- For trials 0–9, the Stage 1a hits are the prefix of the library.
- For further trials, settings and streams are bound before launch.

**The matched baseline is the n = 0 library** of the same population-outer,
built under the same law with E absent. It is shared by the n = 30 and
n = 300 cells. This isolates the effect of the information from the
closed-ball construction; v1's tied K-subset is not reused as if it were the
same reference law (1657 §4).

**The crossing batch is retained in Stage 1b, but the library uses only the
first K pairs.** The surplus is kept for a finite-library check (§3).

## 3. Train/test resampling and finite-library variation

**Resampling** is as in v1 (`e2e_benchmark.py`):
- R_train = R_test = 2,000 datasets per analysis, drawn with replacement from
  the K-member library;
- k-NN on C, with the frozen MAD scaling, the Mahalanobis rule (Ledoit–Wolf
  only above condition number 1e6) and the p_lo/p_hi definitions;
- the v1 scorer, contract v3.

**Finite-library variation (required, 1657 §4).** For a fixed, pre-named
subset of analyses, a second, independent library is drawn from disjoint
batch streams. The between-library spread of p_hi and of accept/detect
decisions is then reported.
- This keeps the claim from relying on 4,000 resamples of 2,000 paths
  behaving like independent paths.

## 4. Inventory

**Primary: noisy E only.**
- At the planned design that is 8 cells × 200 outers = 1,600 analyses
  (14,400 population-outer-cells), plus the matched n = 0 analyses.
- An ideal-E comparator doubles the informative cells. It enters only if the
  Stage 1b budget allows it, and it must be declared beforehand.

**The outer count follows the Stage 1b decision.** The Stage 1a projection
for the full design is about 0.86 × 10⁶ sampling CPU-h, about 84% of it at
n = 300 (report §5).
- **Fixed in advance:** any reduction, whether in outers, n levels or
  scenarios, is fixed beforehand with named trial IDs and denominators.
- **Never selected:** cheaply completing outers are never chosen, and no
  population is dropped from the nine-population statistic.

## 5. Support and failure rules

**Incomplete libraries.**
- A population-outer-cell whose library does not reach K within its declared
  budget is a **support failure**: reported, never silently excluded.
- Its analysis is scored as **not evaluable**. The nine-population dataset it
  belongs to is then incomplete and is counted as such in every
  denominator.
- A zero-hit setting is a support failure with an upper retention bound and
  an unresolved cost.

**Other failures.** Censoring, numerical failure and fit failure are
recorded separately, by cell and population.

**Fit failure.**
- The v1 rule for failed T vectors applies unchanged.
- Fit-failure counts are reported per cell, with no replacement draws.

## 6. Scoring and reporting (per cell)

Following design §4 Stage 1:
- **Results:** non-accepts (nulls) or detections (M_A), with exact intervals.
- **Comparisons:** a paired table against v1 and against the matched n = 0
  baseline, with McNemar and Newcombe method 10; also mean z.
- **Failures:** support failures and fit failures.

**The gates are the v1 analogues, fixed before execution:**
- null non-accepts ≤ 60/1000-equivalent at the cell's size, using exact
  binomial thresholds recomputed for the declared denominators;
- O1-type detection ≥ 224/300-equivalent.

These gates are development criteria. They are not the validation gate of a
frozen method.

**No retuning:** no extension, no retuning, and no post hoc cell selection.

## 7. Open decisions before any fitted execution

1. **Stage 1b scale (Barry).** Full design (~0.86 × 10⁶ CPU-h), n = 30 only
   (~1.4 × 10⁵), or fewer named outers (50 per cell ~2.2 × 10⁵; 25 per cell
   ~1.1 × 10⁵). An alternative is a θ-tilted proposal (Astra's reserve) to cut
   the n = 300 tail.
2. **Library check:** which named subset gets the second, independent library.
3. **Comparator:** whether the ideal-E comparator is included.
4. **Gates:** the exact gate thresholds at the declared denominators.

These are set in a bound settings file and checked by Astra before any
Stage 1b or Stage 1c dispatch.
