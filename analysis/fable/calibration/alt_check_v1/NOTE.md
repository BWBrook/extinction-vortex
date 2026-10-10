# M_D and M_O generators: limiting cases, plumbing and generation cost (v1, 10 October 2026)

Synthetic only. These generators implement the executable laws in protocol §3.2
(draft 0.9). The run used commit `afe9bca`, with hashes in `source_sha256.txt`,
on `deep-server`. The scorer fix from `a31e5bc` is hashed in
`scorer_fixed_sha256.txt`.

## 1. Limiting cases (`test_bank.py`; `test_bank.txt`)

28 checks pass locally and on deep-server:
- **Zero deterioration.** Δ = 0 for the linear, accelerating and step forms
  reproduces ar_cat exactly, with the same seed: identical trajectories and
  selection masks for three populations.
- **Mixtures.** β = 0 in M_A + M_D reproduces the M_D component exactly, for
  all three forms.
- **Perfect detection.** p ≡ 1 reproduces ar_cat exactly, and recorded counts
  equal latent counts.
- **M_O properties:**
  - recorded counts never exceed latent counts;
  - the first recorded count is n0, and the latent start is round(n0/p(n0));
  - selection uses the recorded counts only;
  - some selected recorded extinctions are latently extant: 159 of 401 for
    the golden plover under low-n detection.
- **Shift forms.** The shift offsets match d·t, d·t²/span and the step form
  exactly. Shift and step-time provenance are recorded and in range.
- **Null unchanged.** A separate one-off regression (not kept as a test)
  confirmed that the new simulator matches the committed `f8546ec` version
  exactly for the null and M_A: same trajectories and selection masks for the
  turtles and crow, under iid, ar_cat and M_A.

## 2. End-to-end plumbing (`smoke_summary.json`)

- **Setup.** A 3×10^6-draw toy bank, R = 20, K = 50, 2 outer datasets per
  arm.
- **Arms.** M_A + M_D (step) at β_min; M_O low-n; the low-survival corner.
- **Result.** Every arm completed 2/2. The M_O rows record latent endpoints.
- **Scorer guards:**
  - A logged non-finite p_hi is rejected.
  - This smoke test caught a variable-shadowing bug in the finite-bound check
    (`afe9bca`): trials after the first were scored as missing. It is fixed
    in `a31e5bc`.
  - After the fix, all arms score 2/2, the power screen re-scores to
    1/1/2/8/18 of 30 with no missing trials, and the discrimination_v1 v1
    summary is reproduced exactly.

## 3. Generation cost (`gen_times.json`)

CPU-seconds to generate one nine-population outer dataset. Each figure is the
mean of 20 datasets, seed family 20261030.

| Scenario | CPU-s | Scenario | CPU-s |
|---|---:|---|---:|
| null | 6.9 | M_O low-n | 9.1 |
| M_A at β_min | 7.3 | M_O uniform | 9.2 |
| M_D linear / accelerating / step | 6.8 / 6.9 / 6.9 | high-σ corner | 7.2 |
| M_A + M_D linear / accelerating / step | 7.1 / 7.3 / 7.2 | low-s corner | 5.0 |
| | | strong-environment corner | 7.8 |

- **What this measures.** Only outer-dataset generation, which is cheap:
  under 0.7% of the 1,370 CPU-seconds per analysed dataset.
- **What it does not establish** (Astra 0.9 review). It does not show that
  total cost is equal across scenarios to within 1%. A scenario's C changes
  its reference libraries, and with them the optimiser and fallback cost of
  fitting the 4,001 datasets.
- **The §4.4 figure of about 3,300 core-hours therefore stays a projection.**
  Scenario-dependent fitting cost is unmeasured.
- The smoke arms in §2 are plumbing checks, not timings.
- **The corners here** come from the development bank; they are recomputed on
  the primary bank.
- **Latent-extant recorded extinctions** (out of 180 trajectories): 80 under
  low-n detection and 49 under uniform detection.
