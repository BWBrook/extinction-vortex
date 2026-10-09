# Outer-C library coverage (v1, 9 October 2026)

This is Astra's "inexpensive next check" (0.6 review §3, message 1228). It asks
how often fresh synthetic outer datasets find K = 2,000 bank runs within the
tolerance in all nine populations at once. It uses calibration summaries only:
no T1–T4 fitting, no empirical statistic, and observed C only as already
exposed in E20.

**Where it ran.**
- `deep-server`, tmux `fable_cov`.
- Run directory:
  `/data/fable/vortex/compare_nulls_20261009T013137Z/coverage_20261009T031425Z`.
- Sources are hashed in `source_sha256.txt`. Its `coverage_summary.py` entry
  is an earlier version; the tables were regenerated with the version hashed
  in `summary_src_sha256.txt`, which adds the tolerance-3 column and the k-NN
  quantiles.
- Wall time 3 min 49 s; peak RSS 1.2 GB (`resources.txt`).
- A first version, which counted hits by brute force, was too slow at
  0.45 s per row. It was stopped before producing results and replaced by the
  k-d tree version. No output from it was used.

**Design.**
- **Banks.** The 2×10^8-draw banks from `../discrimination_v1/` (iid and
  ar_cat), unchanged.
- **Scenarios.** iid null, iid M_A, ar_cat null and ar_cat M_A, with β = 8.66
  (Δ10 = 0.5). M_A uses the same environment variant as its null.
- **Outer datasets.** 20,000 fresh selected trajectories per population and
  scenario.
  - Seeds 2026101800–2026101835, one per task.
  - Populations are generated independently, so row j across the nine is one
    outer dataset.
- **Success.** A population succeeds when its K-th nearest bank run lies
  within tolerance; this is the e2e shortfall rule.
  - Distances are MAD-scaled within each bank. Columns with zero MAD are
    dropped, matching the e2e `nansum`.
  - Neighbours are found with a k-d tree (`scipy.spatial.cKDTree`).
- **Recorded.** The distance to the 20th, 67th, 200th, 667th, 2,000th and
  20,000th neighbour of the full bank, and the 2,000th neighbour of a 10%
  Bernoulli thinning of the bank, which has its own MAD.

**Projection to larger banks.**
- A bank m times larger is projected to succeed when d_(K/m) ≤ tolerance,
  because expected neighbour counts scale linearly with bank size.
- **Check.** The measured 0.1× thinned bank agrees with the 0.1× projection
  d_(10K):
  - per population, within 0.003;
  - all nine together, 0.0928 vs 0.0928 (iid null) and 0.0809 vs 0.0802
    (ar_cat null).
- Projected rows are planning numbers and ignore the small change in MAD.

Full tables: `coverage_summary.md`; per-task results: `coverage.json`. The
per-task `.npz` files, with outer C and neighbour distances (48 MB), stay on
deep-server and are hashed in `out_sha256.txt`.

**All-nine coverage at tolerance 1.0** (95% CP for measured values):

| Scenario | 0.1× (measured) | 1× = 2×10^8 (measured) | 10× (proj.) | 30× (proj.) | 100× (proj.) |
|---|---:|---:|---:|---:|---:|
| iid null | 0.093 | 0.686 [0.679, 0.692] | 0.956 | 0.984 | 0.995 |
| ar_cat null | 0.081 | 0.671 [0.665, 0.678] | 0.951 | 0.983 | 0.995 |
| iid M_A | 0.029 | 0.566 [0.559, 0.573] | 0.936 | 0.979 | 0.994 |
| ar_cat M_A | 0.027 | 0.549 [0.542, 0.556] | 0.918 | 0.968 | 0.989 |

The screen's shortfall rates (7/30 and 8/30 null; 9/30 and 13/30 M_A) are
consistent with these measured 1× values.

**Findings.**

1. **The hard tolerance consumes the null budget.**
   - Every shortfall counts as a rejection under the null. To keep total
     false alarms well under the 8% ceiling, shortfalls must stay at or below
     about 0.5%.
   - At tolerance 1.0 that needs about 100× banks, i.e. 2×10^10 draws per
     population: roughly 330 core-hours and over 100 GB per null variant.
   - Even then about 0.5% of outer datasets remain short.
   - The tail is long. At 1×, the 99.9th percentile of the largest K-th
     neighbour distance across the nine is 10.8–11.8.
2. **A looser fixed tolerance helps only partly.** With 10× banks, null
   shortfalls fall to:
   - 4.5–4.9% at tolerance 1.0;
   - 0.4–0.5% at 2.0;
   - 0.13–0.17% at 3.0.

   Under M_A they are larger: 1.0% at 2.0 and 0.3% at 3.0 for ar_cat.
3. **Feedback moves C away from the null bank.** Coverage under M_A is lower
   at every bank size, so under a hard tolerance part of the feedback signal
   becomes indeterminate rather than detected.
4. **k-NN library: K nearest runs, no hard tolerance.** This removes the
   shortfall branch altogether. The library's **projected** radius at 10×
   (largest across the nine, ar_cat null) has these quantiles:

   | Quantile | 0.50 | 0.90 | 0.95 | 0.99 | 0.999 |
   |---|---:|---:|---:|---:|---:|
   | Radius | 0.35 | 0.74 | 0.99 | 1.60 | 3.84 |

   For 95% of outer datasets that is at least as tight as the current
   tolerance of 1.0, with a modest looseness in the tail. These are
   projections from the existing bank's 200th-neighbour distances. Their CP
   intervals are conditional on that bank and on the projection, and they
   omit variation in a future bank and its MAD (Astra 1253). Actual radii are
   to be measured in the constructed 10× banks.

   Validation (§4.3) then measures the false-alarm rate of the frozen
   procedure, averaged over its scenarios. Removing the cutoff does not remove
   approximation error in rare C regions; the protocol adds radius-stratified
   diagnostics for that.

This is development evidence under development seeds. The protocol proposal it
supports is in §3.4 (draft 0.7) and awaits Astra's review.
