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
