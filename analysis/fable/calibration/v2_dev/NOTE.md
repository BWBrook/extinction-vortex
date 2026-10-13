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

## D1c version 2 (12 October; after Astra 1544–1546)

Two repairs, in `knn_nuisance_c.py` version 2:
- membership now comes from a separate k = K query, which is the query v1
  made; the k = K + 1 query only flags ties;
- constant libraries keep their midranks and are flagged separately.

Outputs: `d1c2_summary.json`, `d1c2_trials.jsonl.gz`, and neighbour IDs on
deep-server (`d1c2_neighbours.npz`, `f988a607…`). Version 1's outputs above
are kept as superseded.

**Membership.** Compared with version 1's truncated K + 1 query, these numbers
of the 9,000 population sets per block differ:

| Block | Sets that differ | Most members changed (of 2,000) | Differing sets without a tie flag |
|---|---|---|---|
| b1 | 400 | 10 | 0 |
| b2 | 630 | 27 | 0 |
| b3 | 757 | 30 | 0 |
| b4 | 702 | 16 | 0 |

Every changed set carries the boundary-tie flag. The K-th distances still
match v1's records exactly.

**D2 after both repairs.** The slopes are essentially unchanged; the
penultimate-rank summary now averages all nine populations. Penultimate rank
(logistic slope per SD, 95% interval):
- b1: 1.16 (0.84, 1.48);
- b2: 1.33;
- b3: 0.33 (0.16, 0.51);
- b4: 0.79.

The s, mean-multiplier and σ rows agree with version 1 to within 0.001. The
reading stands: association only, neither supporting nor ruling out nuisance
mixing.

## D3: paired oracle contrast (run 11 October 19:48–23:51; verified report 12 October)

Specification: plan §2. Launch source `d3_oracle.py` (SHA-256 `675bd8f2…`).
Verified report (`d3/d3_report.json`): the same source with Astra's repairs
applied after the run. Archived receipts are in `d3/`:
- outers;
- the oracle metadata;
- both arms' metadata and rows;
- per-trial z values;
- hashes of all 400 T files and of the neighbour archives (deep-server
  `/data/fable/vortex/v2_dev/d3/`).

**Branches Astra flagged** (none occurred):
- no sampling failures;
- no support stop or extension (wild dog retained the fewest paths, 49,052);
- 200 unique, complete trials per arm, with no restart;
- no fit failures.

**Receipts.**
- Manifest, outers, oracle-metadata and source bindings all hold.
- All 181 primary-bank files match the manifest.
- 1,800 neighbour sets per arm were reconciled from their stored IDs: every
  recomputed K-th distance equals the logged value. 186 sets in arm V and 206
  in arm O carry the tie flag.
- Runtime: Python 3.12.3, NumPy 1.26.4, SciPy 1.11.4. R 4.6.1 and nlme
  3.1.171 were recorded at report time.

**Result** (200 paired low-s outers):

| | Arm V (frozen prior bank) | Arm O (fixed-θ_L oracle) |
|---|---|---|
| Non-accepts | **34** (0.121–0.229) | **7** (0.014–0.071) |
| Mean z, T1–T4 (SD) | −1.86 (0.85), −1.73 (0.90), 0.25 (0.78), 0.37 (0.81) | −0.07 (0.96), −0.13 (0.99), −0.10 (0.97), 0.01 (1.05) |
| Max K-th distance, original-C metric (q10/50/90) | 0.18 / 0.26 / 0.51 | 0.66 / 0.89 / 1.41 |

- Paired table (both, V only, O only, neither): 3, 31, 4, 162.
- Exact McNemar p = 3.5×10⁻⁶.
- Paired difference O − V = −0.135, with a Newcombe method-10 interval of
  (−0.194, −0.080).
- The score in `score_launch_superseded.json` used the uncorrected φ (method
  8), giving (−0.194, −0.081).

**Interpretation, as declared in plan §2.**
- Replacing the reference's nuisance law with the generating one removes the
  excess at this corner. It also removes the T1/T2 location shift, and the
  standard deviations of z return to about 1.
- It does not isolate survival, because all six nuisance values were fixed.
- It does not define a usable empirical method, since θ is unknown.
- It does not exclude finite-K error in general.
- Descriptively, though, the oracle's neighbourhoods were 3–4 times **wider**
  in the original C metric and still calibrated. Tight C-locality around a
  prior-mixed nuisance law did not.

## A0: C+ pre-screen (12 October; plan §3; `a0_cplus.py` → `a0_cplus.json`)

No fits. For each of the 1,000 exposed outers in b1–b4, the script built
neighbourhoods in C+ = C + (h₁, h₂) on the primary bank and compared them with
v1's C neighbourhoods. All 181 bank hashes were verified; no series had a
constant predictor and no column was dropped.

| Block | True-value rank of s, C → C+ | Stationary-mean proxy rank, C → C+ | Median max distance in original C, C → C+ |
|---|---|---|---|
| prior predictive | 0.49–0.51 → 0.49–0.51 | 0.49–0.51 → 0.49–0.52 | 0.05–0.11 → 0.34–0.46 |
| high σ | 0.60–0.80 → 0.61–0.79 | 0.31–0.58 → 0.31–0.58 | 0.03–0.25 → 0.18–1.18 |
| **low s** | **0.09–0.33 → 0.10–0.32** | **0.004–0.15 → 0.004–0.15** | 0.03–0.18 → 0.13–0.88 |
| strong environment | 0.39–0.68 → 0.39–0.65 | 0.40–0.65 → 0.39–0.64 | 0.03–0.18 → 0.14–0.84 |

**Reading.**
- C+ does not move the library toward the generating nuisance values at the
  low-s corner, or at any other.
- It costs C-locality: neighbours are about 4 times farther away in the
  original C metric.
- Within v1's C neighbourhoods, h₁ varies over about 21 MAD units (wild dog,
  low s). Conditioning on it therefore spends neighbours on a noisy dimension
  that carries little nuisance information.
- By plan §3's rule, the fitted screen A1 is not worth running as specified.

## A-screen: fixed 200-case fitted screen of candidate A (13 October; plan §8)

- **Run.** Deep-server, 11:06–12:56 AEDT: two slots of 100 trials, 30 R
  workers each, about 48.6 s of fits per trial. Commit 6316a90 bound the
  inputs before any fit.
- **Archive.** `a_screen/` holds the report, outers, metadata, rows and the
  hashes of all 200 T files and the neighbour archives. The T files themselves
  are on deep-server at `/data/fable/vortex/v2_dev/a_screen/`.
- **Report checks, all true:**
  - every trial appears exactly once;
  - slot bindings are identical;
  - manifest digest and outers SHA-256;
  - source-row and source hashes;
  - neighbour receipts are complete;
  - every C+ K-th distance matches the log.
- **Failures.** None: no sampling or fit failures and no indeterminate
  outcomes. Estimator fallbacks average 177 per trial, against 161 for v1 on
  the same trials.

**Result.** Same 200 exposed low-s outers (v1 b3 trial IDs 0–199):

| | v1 (C) | Candidate A (C+) |
|---|---|---|
| Non-accepts | 21 (0.066–0.156) | **11** (0.028–0.096) |
| Mean z, T1–T4 | −1.70, −1.52, 0.33, 0.39 | −1.41, −1.29, 0.41, 0.66 |
| Max K-th distance, original-C metric (q10/50/90) | 0.17 / 0.28 / 0.52 | 0.78 / 1.29 / 2.60 |

- Paired table (both, v1 only, A only, neither): 6, 15, 5, 174.
- Exact McNemar p = 0.041.
- A − v1 = −0.050, with a Newcombe method-10 interval of (−0.098, −0.005).
- 187 of 1,800 C+ population sets carry the boundary-tie flag.

**Reading (development triage, as declared).**
- A lowers the non-accept rate on these trials. The paired interval excludes
  zero, but only just.
- The improvement does not come with removal of the T1/T2 location shift: it
  shrinks by about 17%, and the T4 shift grows. D3's oracle removed it
  entirely.
- A's neighbourhoods are about 4.6 times wider in the original C metric. So
  part or all of the drop may come from a broader, more diffuse reference
  rather than from a corrected nuisance law. That route would also cost power.
- This null-only screen cannot show which explanation holds.
- Under §8, this is enough improvement to warrant considering the §5 broader
  evaluation, whose power arms are what would settle it. It neither selects
  nor validates A.
