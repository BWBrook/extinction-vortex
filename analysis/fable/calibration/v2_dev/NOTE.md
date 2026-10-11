# V2 development: mechanism diagnostic 1 (11 October 2026)

This is development evidence for v2, computed on the exposed v1 outputs. No new
outcomes were generated; the work is part of tranche 1 of
[Codex's v2 brief](../../../../notes/astra_v2_development_20261011.md).

**What it measures.** `knn_nuisance.py` rebuilds each null trial's K = 2,000
neighbourhood exactly. The neighbourhood is deterministic given:
- the logged recorded series;
- the frozen primary bank;
- the cKDTree query.

Only v1's R draws from the neighbourhood were random. For each population, the
script then compares the outer dataset with its library on two things:
- the true nuisance values (s, f, σ) against the library's;
- the outer mean non-final log change against the library's. This trend is not
  a C feature.

It ran on deep-server in about 25 minutes. Output: `knn_nuisance.json`.

**Mean rank of the true value within its library** (range over the nine
populations; 0.5 means the library is centred on the truth):

| Null block | s | σ | f | trend | Rejections |
|---|---|---|---|---|---|
| prior predictive | 0.49–0.51 | 0.49–0.51 | 0.48–0.52 | 0.48–0.52 | 46 |
| high σ | 0.60–0.80 | **0.77–0.92** | 0.32–0.39 | 0.48–0.52 | 41 (pass) |
| low s | **0.09–0.33** | 0.28–0.59 | 0.26–0.50 | 0.46–0.50 | 148 (fail) |
| strong environment | 0.39–0.68 | 0.34–0.62 | 0.39–0.60 | 0.47–0.51 | 30 |

**Reading.**
- Under the prior, the library is centred on the truth for every nuisance, as
  C-conditioning predicts.
- At fixed corners it is not. C does not pin down the nuisances, so the
  library pulls them toward the prior. In the low-s block the library's
  median s is 0.53–0.76, against true values of 0.16–0.69.
- The trend matches in every block, so the outer and library series decline
  alike.
- **Nuisance displacement alone does not cause failure.** The high-σ block is
  displaced as much in σ and still passes. The low-s block fails. So T1–T4
  appear sensitive to the survival/growth direction (s, and so λ = s + f) and
  not to σ, given C.
- This mechanism lives in the spread of the nuisances given C, which a larger
  bank or a smaller K only samples more finely. It is not finite-library
  approximation error.
- Not yet shown:
  - whether it is s specifically or the growth/turnover structure that matters
    (Codex's caution);
  - whether trials with more displacement reject more often within the low-s
    block.

**Limits.**
- Trend z is undefined (NaN) for the Hawaiian crow, where some libraries have
  constant changes; the ranks are unaffected.
- This is post hoc and exploratory. It sets no criterion.

## Qualification after Astra's review (board 1533), and the corrected D1c/D2

**Withdrawn readings.** The "Reading" bullets above are superseded; the
original text and `knn_nuisance.json` stay as the record.
- Mean ranks near 0.5 do not show that each library is centred on its truth.
- One passing σ corner against one failing s corner does not isolate s, or
  insensitivity to σ.
- D1 does not exclude finite-library error.
- "Trend" telescopes to the penultimate count, so it is an endpoint summary,
  not path shape. Its float ranks could also mis-handle exact ties.
- Nuisance mixing given C remains a **hypothesis**.

**D1c/D2** (`knn_nuisance_c.py`; `d1c_summary.json`; per-trial
`d1c_trials.jsonl.gz`; neighbour IDs on deep-server at
`/data/fable/vortex/v2_dev/d1c_neighbours.npz`, SHA-256 `cd51656d…`):
- **Bindings verified** before any query:
  - manifest `96603037…`;
  - all 181 bank files and all 12 source files against the manifest.
  - Runtime: Python 3.12.3, NumPy 1.26.4, SciPy 1.11.4 (the pinned
    versions).
- **Reconstruction.** All 36,000 recomputed K-th distances equal v1's rounded
  records exactly, and N0 matches everywhere.
  - Boundary ties are common: 571, 806, 896 and 914 per 9,000
    population-trials in b1–b4.
  - So membership at the K-th boundary rests on cKDTree's tie order. That
    order matches v1 under the same SciPy and data, but this receipt cannot
    verify it independently.
- **Endpoint ranks** (integer penultimate counts, half ties):
  - In the low-s block the population medians are 0.35–0.45: the outer
    penultimate count sits slightly below its library's.
  - Hawaiian crow has 370 constant libraries there, given as null.
- **Growth proxies.** At low s, the true stationary mean multiplier ranks at
  0.001–0.24 (q10–q90 over trials and populations) within its library. The
  library medians are 0.80–0.95, against true values of 0.48–0.70.
  - Every low-s trial is displaced almost to the floor, with a trial summary
    of −0.47 to −0.45.
  - So a within-block association for this proxy has no leverage.
- **D2 association** (one summary per trial; logistic slope per SD, with 95%
  interval):

  | Summary | prior predictive | high σ | low s | strong environment |
  |---|---|---|---|---|
  | s rank | −0.05 (−0.34, 0.25) | −0.29 (−0.59, 0.01) | 0.21 (0.04, 0.39) | −0.07 (−0.43, 0.29) |
  | mean-multiplier rank | −0.10 (−0.39, 0.20) | 0.49 (0.17, 0.80) | −0.01 (−0.19, 0.16) | 0.00 (−0.36, 0.37) |
  | σ rank | 0.37 (0.07, 0.67) | 0.54 (0.17, 0.90) | −0.24 (−0.41, −0.07) | −0.10 (−0.47, 0.26) |
  | endpoint (penultimate) rank | 1.12 (0.80, 1.43) | 1.32 (0.97, 1.67) | 0.33 (0.16, 0.51) | 0.79 (0.42, 1.16) |

- **Reading** (association only):
  - In every block, rejections concentrate where the outer's penultimate count
    is high relative to its library. That is a property of the v1 test, which
    is calibrated overall under the prior.
  - Within the low-s block there is no dose–response on s displacement: the
    association is weak and the wrong sign for that hypothesis. The
    mean-multiplier proxy cannot be assessed.
  - The summaries are correlated: s with f ρ = −0.87, s with σ −0.40.
  - D2 therefore neither supports nor rules out the nuisance-mixing
    hypothesis. The paired oracle D3 is the discriminating check.
