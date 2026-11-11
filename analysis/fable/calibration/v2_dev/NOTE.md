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

## A power screen: 600 exposed power outers (13 October; plan §9)

- **Run.** Deep-server, 16:15–22:20 AEDT: two slots of 300 trials, 30 R
  workers each, about 63 s of fits per trial. Commits e4519c7 and 9f48fd1
  bound the inputs before any fit; runner SHA-256 `27d1baf5…`; outers
  `0439267e…`.
- **Archive.** `a_power/` holds the report, outers, metadata, rows and the
  hashes of 600 T files and the neighbour archives. The T files are on
  deep-server.
- **Checks.** All 13 report checks are true, including all 181 bank and
  helper bytes, the expected settings and full seed map, and selected series
  matching the outers.
- **Failures.** None: no fit failures and no indeterminate outcomes.

**Result** (detections; same outers; paired):

| Block | v1 (C) | A (C+) | Paired table (both, v1 only, A only, neither) | A − v1 (Newcombe 10) | McNemar p |
|---|---|---|---|---|---|
| M_A at β_min | 21/300 (0.044–0.105) | 11/300 (0.018–0.065) | 9, 12, 2, 277 | −0.033 (−0.063, −0.008) | 0.013 |
| M_A at Δ10 = 0.5 | **206/300** (0.631–0.739) | **28/300** (0.063–0.132) | 27, 179, 1, 93 | **−0.593** (−0.646, −0.533) | 2.4×10⁻⁵² |

- **Mean z, T1–T4, at Δ10 = 0.5:** v1 2.88, 3.12, 0.46, −0.40; A 1.30, 1.55,
  0.47, 0.26. At β_min: v1 0.77, 0.85, 0.13, −0.08; A 0.63, 0.59, 0.04, 0.03.
- **Original-C max K-th distance, median:** at β_min, v1 0.35 and A 2.06; at
  Δ10 = 0.5, v1 0.44 and A 3.49.

**Reading** (a practical comparison of discrimination, as declared; it does
not identify a cause).
- A's modest null improvement on the A-screen (11/200 against 21/200) comes
  with a near-total loss of discrimination at Δ10 = 0.5: 206 → 28 detections.
- A loses the T1/T2 signal that v1 detects.
- A does not merit further development, and **candidate A is closed.**
- This neither selects nor validates anything, and v1's V-fail stands.

## External-information Stage 0: no-fit weight diagnostics (14 October 2026)

**Authorisation.** Barry, 14 October: "Yes, I want the “how much demographic
data” experiment. Go ahead with this before I wake Codex, with my authority."
This was within Astra's accepted bounded Stage 0 (board 1625).

**Specification.** `notes/vortex_external_info_design_20261014.md` §§2–4 and
7.
- **Runner:** `s0_info.py`, SHA-256 `c4253476…`.
- **Bound inputs:** `s0/s0_inputs.json` (`e1479a2f…`), committed in 1f82fe4
  before any weights were computed.
- **Report:** `s0/s0_report.json`. Per-population outputs and member draw IDs
  are on deep-server at `/data/fable/vortex/v2_dev/s0/full/`, with hashes in
  `s0/full_outputs_sha256.txt`.

**Scope.**
- Exposed v1 outers b1, b3, b5 and b16, trial IDs 0–199: 800 datasets and
  7,200 K = 2,000 neighbourhoods.
- Noisy stylized and ideal weights at n = 30 and 300.
- No fits, no reference sampling, no new draws of outers or banks.

**Checks.**
- All 800 outer datasets verified before computation: the six θ fields, the
  selection rule, b3 sharing the fixed corner θ, and the source-row hashes.
- The quadrature and weight-rule fixtures pass.
- Every K-th distance matches v1's log (0 mismatches over 7,200
  neighbourhoods), with 519 boundary ties.
- **No unusable weight set** in any cell.

**Cost.** A setup pass on wild dog first (113 s, 9.0 GB). The full one-pass
run took 24 min 9 s with peak RSS 12.1 GB, on a deep-server shared with
another project at load average about 60. No resource shortfall, and no bank
expansion.

**Results.** "Flag" is the fraction of datasets in which **any** of the nine
populations has ESS < 100. It is an exploratory concentration flag, not a
calibration threshold. Pooled ESS is the median over population-datasets.

| Cell | Scenario (θ law) | n | Flag, noisy / ideal | Pooled median ESS, noisy / ideal |
|---|---|---|---|---|
| 0 | b1 null (prior) | 30 | 0.425 / 0.340 | 606 / 756 |
| 1 | b3 null (fixed low-s corner) | 30 | **0.825** / 0.260 | 317 / 337 |
| 2 | b5 M_A at β_min (prior) | 30 | 0.515 / 0.355 | 616 / 724 |
| 3 | b16 M_A, Δ10 = 0.5 (prior) | 30 | 0.680 / 0.430 | 454 / 562 |
| 4 | b1 | 300 | 0.995 / 0.995 | 100 / 106 |
| 5 | b3 | 300 | **1.000 / 1.000** | **16 / 15** |
| 6 | b5 | 300 | 0.995 / 1.000 | 92 / 99 |
| 7 | b16 | 300 | 1.000 / 1.000 | 47 / 49 |

At the low-s corner with n = 300, the median ESS within the 2,000 neighbours
is 3 for wild dog, 4 for golden plover, 6 for marmot, 9 for middle-spotted
woodpecker and **15 for wood turtle A** (14.6 noisy, 14.7 ideal). The other
four populations range from 46 to 199 (noisy) and 49 to 220 (ideal).
*(Corrected 15 October: the first version omitted wood turtle A from the
low-median list; the JSON report was correct.)*

**Reading** (revised 15 October after Astra's Stage 0 audit; the first
version overstated it).
- **What is measured.** Weighting the existing K = 2,000 prior-bank members by
  informative stylized evidence concentrates the normalised weights strongly.
  Most ESS values are below 100 at n = 300, and many are at n = 30. The
  concentration is most severe for five populations at the low-s corner.
- **What is not established.** This is a computational warning about the
  fixed-K reweighted reference (R1). It does not show:
  - an absence of target support;
  - importance-sampling error for the T statistics;
  - inadequate reference draws;
  - the outcome of an unrun fitted test;
  - anything adverse about the value of demographic data.
- **Decision.** It is a reason not to spend a fitted stage on R1 now, and to
  investigate a reference drawn under the informative law. Astra's bounded
  sampler prototype is the next step
  (`notes/astra_informative_reference_proposal_20261014.md`).
- **Limits.** Stage 0 cannot measure calibration or power. **It stops here.**

## Informative-sampler prototype (15 October 2026; no fits)

Astra's proposal (`notes/astra_informative_reference_proposal_20261014.md`;
board 1647), within Barry's authority for the information experiment. Design
doc §8.
- **Runner:** `p1_sampler.py`, SHA-256 `4c967825…`.
- **Bound settings:** `p1/p1_bound.json` (`112975ab…`), committed in 7a3aa0e
  before the run.
- A first launch (6110118) stopped in its test step after 0.6 s, on a JSON
  serialisation of a NumPy boolean, before any scan or pilot. Its files are
  kept on deep-server under `p1/failed_launch_1/`.
- **Outputs:** `p1/test.log`, `p1/p1_scan.json`, `p1/p1_pilot.json` and
  `p1/p1_cost_projection.json`.

**Run.**
- deep-server, one worker with single-threaded numerics, at load about 16 on
  64 cores.
- **Total 220 s:** tests under 1 s, bank scan 142 s (10.9 GB), pilot 78 s
  (10.8 GB).
- Every one of the 20 settings reached its cap: 10⁶ prior proposals, or 10⁵
  paths for the n = 0 controls.

**Tests (all pass).**
- **Frozen dynamics:** the parameter-fed wrapper reproduces
  `bank.simulate_chunk(fixed=θ)` exactly, for wild dog and crow.
- **Analytic bound:** the largest log-factor on the test grid is −2.5×10⁻¹².
- **n = 0** accepts every proposal.
- **Factorised rejection:** Poisson then binomial gives the product
  acceptance probability (0.7788 target, 0.7791 observed, over 2×10⁶
  trials).
- **Joint-selection law:** restarting θ after each failed path gives the
  correct 0.0998 against a target of 0.1. Holding θ until a path is selected
  would give 0.5.
- **Closed-ball boundary** handling is exact.
- **Pilot:** no bound violations and no rounding excess.

**Bank scan** (closed balls at the full-precision Stage 0 radius, frozen
metric).
- Three pairs hold exactly 2,000 members, one of them on the boundary.
- Crow at the low-s corner holds 2,915, with **2,436 on the boundary**: its
  discrete C values tie at radius 0.0044, and only 479 fall strictly inside.
- So the declared closed ball is not v1's arbitrary 2,000-member subset at a
  tie.

**Pilot against forecast.**
- **Ball hits:** 4 observed over all 20 settings, against 3.0 forecast from
  the bank scan. That is consistent; both are small by construction.
- **Retention per prior proposal:** 10⁻⁶ for n = 0, because the ball holds
  about 2,000 of 2×10⁹ prior paths. Informative evidence lowers it to 10⁻⁷ to
  10⁻⁸ in most cells, and to **4×10⁻¹⁰** for wild dog at the low-s corner
  with n = 300.
- **θ acceptance:** 3–9% at n = 30, and 0.3–1.3% at n = 300.
- **Throughput:** 0.24–0.87 µs per prior proposal, and about 2.5–5.3 µs per
  simulated path.

**Projected cost per population-outer for 4,000 retained references**
(R_train + R_test). Order-of-magnitude only: the forecasts rest on the
existing bank's ball members, and are least reliable where Stage 0 ESS was
lowest.

| Pair | n = 0 | n = 30 noisy / ideal | n = 300 noisy / ideal |
|---|---|---|---|
| wild dog, b1 | 5.9 CPU-h | 5.0 / 2.5 | 5.5 / 7.2 |
| wild dog, b3 | 5.7 | 10 / 18 | **730 / 290** |
| crow, b1 | 2.8 | 2.7 / 3.0 | 15 / 13 |
| crow, b3 | 1.9 | 1.6 / 1.0 | 2.2 / 2.8 |

**Reading** (measured feasibility, with explicitly uncertain forecasts; no
calibration or power claim).
- **The sampler is correct and cheap per proposal.** What costs is the
  locality: v1's K = 2,000-of-2×10⁹ ball has prior mass of about 10⁻⁶, so
  every exact retained reference needs on the order of 10⁶ or more prior
  proposals.
- **A fitted stage at the planned size is not practical at this locality.**
  The plan was 8 cells × 200 outers × 9 populations, about 14,400
  population-outer-cells. At a typical 3–15 CPU-h each, that is about 10⁵
  CPU-h, and the low-s corner with n = 300 would add hundreds of CPU-h per
  outer for the most displaced populations.
- **Feasible directions** need a design decision, and none is chosen here:
  - a much smaller design;
  - a declared wider C-locality, which changes the conditioning target;
  - a different reference construction.
- **This prototype stops here**, as specified.

## Stage 1a: kunanyi smoke and final manifest (15–16 October 2026; no fits)

Astra's bounded sampling pilot (`notes/astra_p1_and_repairs_review_20261015.md`
§4; board 1657), confirmed in 1660. Runner `p2_stage1a.py`; package 74cf551.

**Smoke** (smoke settings `6c61c68f…`: 1,080 settings × 10⁵ proposals, 28
workers, one node).
- Job 819562 was queued 15 Oct 12:21 and started 16 Oct 09:27. The 21 h wait
  was "Not Running: Insufficient amount of resource: ncpus": no whole 28-core
  node was free.
- It ran 57 s wall, 4 min 20 s CPU, exit 0, on n237 with Python 3.11.7,
  NumPy 1.26.4 and SciPy 1.11.4.
- 1,080/1,080 settings complete; none censored, failed or missing; 38 hits.
- Peak worker RSS 0.076 GiB (1.9 GB for 28 workers).
- Allocation 28 × 57 s = 0.44 CPU-h, plus a 6 s collector.
- **Collector 819563 exited 4.** `collect` succeeded, but `tar` reported
  "smoke: file changed as we read it" seconds after the node job ended. A
  repack on the login node at 10:50 exited 0 and passed `tar -d`. The archive
  (`58e9feab…`) was pulled to deep-server and its hash agrees. The cause is
  probably shared-filesystem metadata lag; that is not established.
- **The results reproduce across machines.** Every counter of all 1,080
  settings, and every hit record, is identical to the deep-server dry run
  (Python 3.12.3 there).
- **Kunanyi is faster per core.** Its rate divided by deep-server's has a
  median of 1.13 (n = 0), 1.46 (n = 30) and 1.45 (n = 300). Median kunanyi
  rates are 1.8 × 10⁵, 1.13 × 10⁶ and 1.78 × 10⁶ proposals per CPU-s.
- **The per-setting rates can serve as budgets.** A linear cost model fits
  kunanyi CPU time with residual log-ratio sd 0.014 / 0.079 / 0.054 by n
  (maximum +0.06 / +0.25 / +0.14). Its unit costs are 0.43 µs per proposal,
  1.65 µs per Poisson acceptance, and 1.3–4.8 µs per simulated path,
  depending on population.
- Files: `p2/kunanyi_smoke/collect.json`, `p2/throughput_kunanyi.json`
  (`a89f5d28…`).

**Repairs before scale** (runner `3fccf9b9…`).
1. **Checkpoint cadence.** An informative batch takes about 18 ms, so a
   per-batch fsync would mean about 50 commits per second per worker. Across
   360 workers that is about 2 × 10⁴ per second on the shared filesystem,
   and the CPU-time throughput excludes that I/O.
   - Hit records, then state, are now committed at most every 60 s, and at
     every terminal state.
   - Resume semantics are unchanged.
2. **Declared storage limit.** A setting stops at the first batch boundary
   with at least 2,000 retained hits (HIT_STOP = K). The crossing batch is
   kept whole, and the stop reason (`hits` or `budget`) is recorded.
   - The hard maximum is K + B − 1 = 21,999 records per setting (B =
     20,000). About 2,000 per setting (roughly 0.7 GB in total) is a
     planning estimate only. *Corrected 16 Oct per Astra 1698.*
   - *Withdrawn 16 Oct:* the earlier "O(1/2,000) bias" remark held only for
     an ideal inverse-binomial design. Uncertainty now follows the declared
     report rule below.
3. **Job shape.** Jobs now take JOBCPUS workers and JOBCPUS/2 + 1 GB, so they
   can backfill partly occupied nodes.
4. **Collector packing.** The pack excludes the collector's own PBS logs, is
   verified with `tar -d`, and retries after 60 s and 300 s. Exit 4 follows
   only if all three attempts fail.

**New fixtures (all pass).**
- An uncommitted hit record is dropped on resume.
- Committing every batch and committing every 60 s give identical results.
- The hit stop falls at a batch boundary. Smoke setting 775 has hits in
  batches 1 and 2; with HIT_STOP = 1 it stops after batch 1 with one hit.

The repaired runner reproduces all 1,080 smoke settings exactly on
deep-server: no counter or hit-record mismatches, 38 hits.

**Final manifest** `p2/p2_settings_s1a.json` (`d0dd1bff…`, superseded the
same day by `9a7d4699…`, which rebinds the repaired runner; the budgets and
assignment are unchanged).
- **Settings:** the same 1,080 indices and streams. The smoke's five batches
  are the exact prefix of each final stream, so they are recomputed, not
  added as extra exposure.
- **Budgets:** kunanyi throughput × 3,300 s per informative setting and
  825 s per control, rounded down to whole 20,000-proposal batches. That is
  Astra's 3,600 s / 900 s scaled by 11/12 for timing margin within the
  ceiling. Total 3.504 × 10¹² proposals.
- **Packing:** NWORKERS 360. LPT gives every worker two informative settings
  and one control, for an expected load of 7,425 s (2.06 h) on every worker.
- **Dispatch shape:** 45 jobs × 8 cores, 5 GB each, walltime 2:45:00.
  - The deadline at walltime − 10 min (2.58 h) exceeds the expected load by
    25%; the expected load uses 80% of the deadline.
  - If every job used its full walltime, the bound would be 360 × 2.75 = 990
    CPU-h. With the collector (≤ 1 CPU-h) and the smoke (0.44 CPU-h), that
    is at most 991.5 CPU-h, within the 1,000 CPU-h ceiling.
  - The expected use is about 760–800 CPU-h.
- **Hit forecast** (very uncertain).
  - Smoke hits by n: 31 (n = 0), 5 (n = 30) and 2 (n = 300), each across
    360 settings.
  - Of the 34 settings with smoke hits, 15 project to reach 2,000.
  - The 1,046 zero-hit settings have only an uninformative upper bound at
    smoke scale.
- **Stage tar:** `s1a_stage_final.tar` on deep-server, with per-file hashes in
  `s1a/stage_sha256.txt`. It was `ceaa2975…`; the repaired package below is
  `a4c3e4e4…`.

### Pre-dispatch repairs (16 October; Astra 1698, `notes/astra_s1a_prerun_review_20261016.md`)

Runner `793e7a42…`, settings `9a7d4699…`, `s1a_submit.sh` `facded63…`,
stage tar `a4c3e4e4…`. The sampling law, streams, budgets and assignment are
unchanged.

**A. Submission** (`kunanyi/s1a_submit.sh`).
- **Run identity.** `run.json` holds the settings hash, output directory,
  shape, walltime, ceiling and prior allocation. A journal fixes it.
- **One submitter.** A lock directory admits a single submission.
- **Preflight first.** The bound preflight runs before any qsub.
- **Journal.** Each job has a unique PBS name (settings hash, output
  directory, index). Every qsub is journalled as `request` before it is
  made, and as `accepted ID` as soon as it is accepted. The journal is
  synced.
- **Duplicates are refused.** Before submitting a name, the script queries
  PBS for that name, including finished jobs. An accepted job whose reply was
  lost is recorded as reconciled, not submitted again. More than one job with
  that name is refused.
- **Dispatch modes.** A second `new` dispatch is refused. `resume` submits
  only jobs never accepted, then the collector once. The collector depends
  on every accepted job that has not finished.
- **Fixture** (`kunanyi/s1a_submit_fixture.py` → `s1a_submit_fixture.json`;
  stub qsub/qselect/qstat and stub preflight). All ten scenarios pass:
  - normal dispatch, then a duplicate dispatch (refused, no qsub), then resume
    (no qsub);
  - qsub rejected at call 4, then resume;
  - accepted at call 4 but the reply lost, then resume (reconciled, not
    duplicated);
  - collector rejected, then resume;
  - collector reply lost, then resume;
  - rejection at call 4 with three jobs finished before the resume (the
    collector depends on the 42 unfinished);
  - preflight refusal, a held lock, a resume with another shape, and a resume
    without a journal: all refused with no qsub.
  - Every completed scenario ends with exactly 45 node jobs, each of the 360
    workers owned once, one collector, and an allocation bound of 991.44
    CPU-h.

**B. Recovery** (`run_setting`).
- **Initial boundary.** Every setting first writes a zero checkpoint.
- **Commit order.** Each commit appends and fsyncs hit records, then writes a
  checkpoint recording the committed journal's length and SHA-256.
- **Resume.** Recovery verifies the committed prefix (length, hash, record
  count) and replaces the file with that prefix atomically: temp file, fsync,
  rename. The only committed copy is never truncated in place.
- **Rejections.** Missing, short, altered and orphan journals, unreadable
  checkpoints, and terminal checkpoints with a missing journal or uncommitted
  bytes are all rejected with a diagnostic.
- **Fixtures** (`p2/s1a_test_receipt.txt`, 31 checks, all pass; *corrected:
  board 1703 said 35*):
  - an injected crash at each of the four state writes, including the one
    right after the first hit fsync;
  - a crash during recovery's journal replacement, with a torn tail;
  - each of these recovers to counters and journal bytes identical to the
    uninterrupted run;
  - all seven rejection cases;
  - a deadline after one batch, a crossing-batch hit stop, and a
    bound-violation failure;
  - the earlier real-stream resume, cadence, hit-stop and censoring fixtures.

**C. Collection and preflight.**
- **Collector.** `collect` first writes an in-progress failure summary, so no
  earlier summary can survive a crash. It then validates every row:
  - checkpoint binding and index, counter invariants, and status and stop
    consistency;
  - the journal's length and hash;
  - each hit record's schema, identity bounds and order (unique), and
    selection S;
  - each worker receipt's binding, range and file name.
- **Summary.** It publishes `collection_ok` and `run_complete` atomically,
  keeping missing and incomplete rows visible.
- **Collector fixtures** (in the 31): a valid run with a missing setting is
  accepted. Malformed same-length hit JSON, a stale worker receipt, an
  invariant breach, and a corrupt checkpoint over an old success summary are
  all rejected, with a current failure summary.
- **Preflight.** `preflight SETTINGS METRIC NJOBS JOBCPUS WALL_SECS CEILING
  PRIOR COLLECTOR` runs the real bound check (runner, helper, imported
  source, metric, runtime), then:
  - the shape (NJOBS × JOBCPUS = bound workers, each one an owner);
  - the cumulative allocation bound against the ceiling;
  - the deadline margin;
  - finally the fixtures.
  - Receipts (`p2/preflight_receipts.txt`): 45 × 8 at 2:45:00 passes (991.44
    CPU-h). 4:00:00 (1,441 CPU-h), 44 × 8, and a 2:10:00 walltime shorter
    than the load are all refused.
- **Replay.** The repaired runner reproduces all 1,080 smoke settings and 38
  hit records exactly, and the new collector validates them:
  `collection_ok`, `run_complete`, no errors (`p2/dry3_summary.json`).

**Report rule** (bound into the settings as `report_rule` with
`prefix_batches` = 5; declared before dispatch).
- **Descriptive only:** full-stream H/N.
- **Formal 95% retention intervals** condition on the recomputed smoke prefix
  (batches 0–4, h0 hits) and use only later proposals:
  - a setting ending at its proposal budget gets Clopper–Pearson on the
    suffix;
  - a setting ending at the hit stop gets the exact negative-binomial interval
    from n*, the suffix position of its (2,000 − h0)-th suffix hit:
    [BetaInv(0.025; c, n* − c + 1), BetaInv(0.975; c, n* − c)], with
    c = 2,000 − h0. The hit identities make n* recoverable.
  - Together these are exact for the curtailed design: outcomes ordered by n*
    when stopped, otherwise by suffix hits.
  - Censored, failed or interrupted settings get Clopper–Pearson, labelled
    conditional on non-informative censoring. *Superseded in the second
    round below: these become sensitivity intervals, not formal ones.*
- **Cost:** observed CPU through the crossing batch for hit-stopped settings.
  Rate-based projections to 2,000 for the others are labelled as
  projections.
- **Zero hits** give an upper retention bound and an unresolved cost.
- All 1,080 rows and complete-nine-population availability are reported.
- The collector computes these per row.

**Dispatch** (superseded by the second-round dispatch below).

### Second repair round (16 October; Astra 1708, `notes/astra_s1a_repair_review_20261016.md`)

Runner `ae065826…`, settings `6018ed2a…`, `s1a_submit.sh` `8ca2dd97…`,
stage tar `ad260115…`. Only the report-rule text changed in the settings;
the budgets and assignment are unchanged.

**1. Unresolved submissions are never replaced on an empty PBS answer.**
- Each key's state is its last journal entry.
- A key whose last entry is `request` or `uncertain` is resubmitted only if
  PBS shows exactly one job of that name (reconciled) or an operator
  resolves it with evidence: `accepted KEY NAME ID manual: …` or
  `rejected KEY NAME manual: …`.
- An empty `qselect -x` answer stops the script, because completed-job
  history expires.
- When a qsub fails, the script waits and immediately queries PBS by name:
  - one job: recorded as reconciled, and the script continues;
  - no job, from a successful query: recorded as `rejected …
    absent-after-failure`, which a resume may resubmit (*removed in the third
    round below*);
  - a failed query: recorded as `uncertain`.
- A lost reply is therefore normally reconciled at once, while history
  still exists.

**2. The collector depends on every job not positively confirmed finished.**
- Each accepted node is classified with `qstat -x -f`: `job_state` F is
  omitted, and Q, R, H, W, T, E, S, U, B or M is kept.
- A query failure or an unclassified state stops before the collector qsub,
  and the run stays resumable.
- A verified finished job whose history has expired can be recorded as
  `terminal KEY ID manual: …`.

**Submit fixture** (`kunanyi/s1a_submit_fixture.py` → `.json`): **15
scenarios, all pass.** The stubs add qselect and qstat failure injection,
history expiry and an append-only ledger of every job created.
- **Your expired-history case:** the reply is lost at qsub 4, the
  confirming query fails, then the job finishes and its history expires.
  - The resume refuses with 0 qsub.
  - After the operator records the job as accepted and terminal, the next
    resume submits 42 (41 nodes and the collector), with no replacement for
    j3.
  - It ends with 45 jobs for 45 names and 44 dependencies.
- **Rejection with a failed confirming query:** refused until the operator
  records the rejection, then resubmitted.
- **Lost replies, node or collector:** reconciled at once.
- **One or all live-job queries failing:** no collector, exit non-zero;
  resume then submits the collector with all 45 dependencies.
- **A finished node whose history expired before the collector:** refused
  until it is recorded as terminal; then 44 dependencies.
- **The earlier ten cases still pass.**
- Every completed scenario's ledger has exactly 45 node jobs, the 360
  workers each owned once, one collector, and an allocation bound of
  991.445 CPU-h.

**3. Collector completeness.**
- **Field checks:** type and domain checks run before any arithmetic:
  non-negative ints for counters, `batches_done`, `journal_bytes` and
  `index`; finite non-negative CPU and wall times; a hex SHA-256; known
  status and stop values; and a string failure reason.
- **Isolation:** each setting is checked in isolation. A bad row becomes
  `invalid` with `recorded_status`, and every planned ID is still listed.
- **Workers:** absent worker receipts are listed (`workers_missing`, and
  `provenance_complete` is separate from `run_complete`). Present receipts
  must carry an allowed runtime, a host and a finite non-negative RSS.
- **New fixtures:**
  - negative overflow, rounding_excess and CPU time are rejected;
  - a string `batches_done` makes that row invalid, and the next valid row
    is still collected;
  - bad worker provenance is rejected;
  - a missing worker receipt is reported, and collection still succeeds.
- `p2/s1a_test_receipt.txt` now has **34 checks, all pass**.
- **Replay:** the new collector, run on the saved smoke replay, gives
  `collection_ok`, `run_complete` and `provenance_complete`, no missing
  workers and 38 hits (`p2/dry3_summary.json`).

**Reporting.**
- Censored, failed or interrupted rows now carry
  `sensitivity_interval95_suffix`, with a note that it assumes the
  interruption is non-informative. They have no formal interval.
- No coverage is claimed conditional on the subset of settings that
  completed. The bound `report_rule` says so.

**Prior allocation.**
- The smoke allocation is now recorded as 0.445 CPU-h, so the bound is
  990 + 1 + 0.445 = 991.445 CPU-h.
- Preflight receipts at 0.445: 45 × 8 at 2:45:00 passes. 4:00:00, 44 × 8,
  and a walltime shorter than the load are refused.

**Dispatch** (superseded by the third-round dispatch below).

### Third repair round (16 October; Astra 1719, `notes/astra_s1a_second_repair_review_20261016.md`)

Runner `ae065826…` and settings `6018ed2a…` are unchanged. `s1a_submit.sh`
is now `057991c3…`; stage tar `a0f2270f…` (all 8 files match the checkout).

**1. An empty PBS answer no longer counts as rejection.**
- After a failed or ID-less qsub, only a confirming query showing exactly
  one job reconciles it. Otherwise the key is recorded as `uncertain` and
  the script stops.
- An empty answer cannot distinguish non-acceptance from an accepted job
  that finished and left history before its reply.
- Retry now needs PBS evidence or an operator's evidence-backed
  `rejected KEY NAME manual: …` entry.

**2. Kunanyi runs bash 4.2.46.**
- A read-only probe in Barry's 14:15 window found this. It also confirmed
  that `qselect -x -N` (empty and rc 0 when there is no match), the
  `qstat -x -f` format (`job_state = F`), the unknown-job error (rc 153) and
  `sync FILE` all behave as assumed. History is kept for 1,344 h.
- Under bash < 4.4, `"${dep[@]}"` on an empty array with `set -u` is an
  unbound-variable error. The 3fa81cb submitter therefore died before the
  collector qsub whenever every node had already finished; this was
  reproduced under bash 4.2.46.
- The fix is `${dep[@]+"${dep[@]}"}`.
- `${ids[-1]}`, which in fact works in 4.2, was replaced with an explicit
  index anyway.

**Fixture** (`kunanyi/s1a_submit_fixture.py`; `FIX_BASH` selects the
shell): **17 scenarios, all pass under both bash 5.2.21
(`s1a_submit_fixture.json`) and a locally built GNU bash 4.2.46
(`s1a_submit_fixture_bash42.json`).** The local bash was built from GNU
source with all 46 patches and GNU bison. A first byacc build mis-parsed
`$(…)` and was discarded.
- **New:** a delayed reply whose history has expired. The job is created
  but gone before the confirming query, so the dispatch stops, and the
  resume refuses with 0 qsub. The operator then records it as accepted and
  terminal, and the resume submits 41 nodes and the collector: 45 jobs for
  45 names, 44 dependencies, 991.445 CPU-h.
- **New:** every node finished before the collector, which submits with no
  dependencies.
- Definite rejections (node or collector) are held until an operator
  `rejected` receipt, then resubmitted once.
- `s1a_node.pbs` and `s1a_collect.pbs` also run correctly under bash 4.2.46
  with stub workers: job 44 runs workers 352–359, a failed worker is
  counted, and the collector packs and verifies.

**Dispatch** (after Astra checks this round; one Jumpbox window).
1. Push the tar and extract it into run1.
2. Run `sha256sum -c`.
3. Run `s1a_submit.sh /u/bwbrook/vortex/run1 p2_settings_s1a.json main 45 8
   02:45:00 1000 0.445`. Its preflight runs the bound check and fixtures on
   the kunanyi login node before any qsub.
4. The afterany collector emails Barry. After any interruption, rerun with
   `resume`. An unresolved key or failed state query needs the
   evidence-backed journal entry that the script names.

### Dispatch (16 October 2026, about 16:31 AEDT)

Astra cleared the dispatch in 1735 (`notes/astra_s1a_final_shell_review_20261016.md`).
This used one Jumpbox window.
- **Tar:** `s1a_stage_final.tar` was pushed from deep-server. Its SHA-256
  `a0f2270f…` verified on kunanyi, it was extracted into run1, and
  `sha256sum -c` passed on all 8 files.
- **Submit:** `s1a_submit.sh /u/bwbrook/vortex/run1 p2_settings_s1a.json main 45 8
  02:45:00 1000 0.445`.
- **Preflight passed** on the kunanyi login node (Python 3.11.7, NumPy
  1.26.4, SciPy 1.11.4) before any qsub: settings `6018ed2a…`, 991.445 CPU-h
  bound, fixtures passed.
- **Jobs:** 45 node jobs accepted, 820683–820728. The range has one extra
  number, presumably another user's job; the journal holds 45 `accepted j`
  entries.
- **Collector:** `s1a_ee46c53a_c` = 820729, `afterany` on all 45, Mail_Users
  barry.brook@utas.edu.au, Mail_Points ae.
- **Journal:** 46 requests and 46 acceptances, nothing uncertain.
- **State at submission:** 2 node jobs running, 43 queued, collector held.
- **Expected:** each job finishes about 2.1–2.3 h after it starts; queue waits
  vary. The pilot stops at its no-fit report.

### Result (16 October 2026, about 20:05 AEDT; no fits)

- **Execution:** the collector exited 0; all 45 node jobs exited 0.
  1,073 settings complete and 7 censored (workers 0–15, the two jobs that
  started first); no failures.
- **Hits:** 322,736 retained; only one setting reached K = 2,000.
- **Archive:** `3e18e5b8…`, re-collected on deep-server with identical rows.
- **Full report:** `notes/vortex_stage1a_report_20261016.md`
  (`p2_report.py` → `p2/s1a_main/s1a_report.json`, `s1a_tables.md`).
- **Stage 1c draft:** `notes/vortex_stage1c_fitted_draft_20261016.md`.

## Stage 1b: full noisy-design sampling (authorised 16 October 2026; board 1759)

The design, inventory, caps, waves and implementation are in
`notes/vortex_stage1b_design_20261016.md`. Code is in `p3_stage1b.py` and
`kunanyi/s1b_*`.

**Done on deep-server:**
- **Export:** 7,200 outers and 14,400 E records, with the 360 pilot pairs
  identical.
- **Settings:** 21,600 primary plus 216 check settings, with stable IDs and
  pilot prefixes.
- **Fixtures:** all pass (p3 synthetic; the submitter under bash 5.2 and
  4.2.46).
- **Planner simulation:** 6.8% worst-case overhead.

**Smokes next:** deep-server, then kunanyi, on a 6-setting subset. The
libraries must be byte-identical across machines although the shard plans
differ.

**Deep-server smoke (16 October, 21:01–21:20; no fits).** The subset
`p3/p3_settings_smoke.json` has six W1 settings: s00772, s00073, s00142,
s00247, s01080 and c00021, with a cap of 1.5 CPU-h, a planner target of
0.1 h and minimum shards of 0.05 h. Eight workers ran it.
- **Seed:** 4 pilot prefixes imported; s00772 was complete at seed.
- **Collection** (`p3/smoke_deep_collect_W1.json`): `collection_ok`.
  - 4 COMPLETE, each a 2,000-pair library. The near-K pilot settings
    completed through 2–3 shards.
  - 2 CAPPED (s01080 and c00021), each through 15 parallel shards, with 752
    and 816 hits at the cap.
  - 5.8 CPU-h; no queue or claims left; no errors.
- **Independent serial recomputation:** each complete setting was rerun as
  its pilot prefix plus one unsharded range (`p3_serial_check.py`; output in
  `p3/smoke_deep_serial_checks.jsonl`). **All 4 libraries are
  byte-identical** to the sharded ones.
- **Code version.** The smoke ran runner `b3354dea…`. The current runner
  (`5cf875b2…`) adds two things: a refused recovery or an unexpected error
  marks the setting FAILED instead of ending the worker, and the preflight
  charges the collector (8 CPU-h). All 9 p3 fixtures pass.
- **Hashes:** settings `a7d6cb64…` (21,816), smoke subset `2967ef7d…`, kunanyi
  stage tar `7c47634b…` (10 files). `p3_metric.json` and `p3_settings.json`
  stay on deep-server under `/data/fable/vortex/v2_dev/p3/`.

**Kunanyi smoke dispatched** (16 October, between 21:29 and 21:48 AEDT; PBS qtime to be read).
- **Stage:** `s1b_stage.tar` (`7c47634b…`) verified on kunanyi; `sha256sum -c`
  passed on all 10 files; `s1b/pilot` linked to `../s1a/main`.
- **Preflight passed** on the login node (Python 3.11.7): bound 24.0 of 40
  CPU-h, fixtures passed.
- **Seed:** 4 pilot prefixes imported; s00772 complete at seed.
- **Jobs:** array 820931[] (2 × 8 cores, 1 h) and collector 820932 (afterany
  on the array, emails Barry).
- **Quota:** the probe printed nothing (`quota`, `lfs quota` and `df` gave no
  output). Check another way next window.

**Kunanyi smoke result** (array 820931[] queued and started 16 October
21:48:44; subjobs on n011 and n008 ran 17 min 31 s and 17 min 21 s, exit 0;
collector 820932 exit 0).
- **Collection** (`p3/smoke_kunanyi_collect_W1.json`): `collection_ok`,
  4 COMPLETE and 2 CAPPED, 7.1 CPU-h, empty queue and claims, no worker
  errors.
- **Archive:** `W1.tar.gz` (`ea54e766…`), pulled to deep-server with the hash
  verified.
- **Against deep-server** (`p3/smoke_cross_machine.json`):
  - all six settings agree on status, range count, prefix end batch and
    prefix hits;
  - three of four libraries are byte-identical;
  - the fourth, s00247, differs in **1 of 2,000 records**: same
    (batch, proposal), path and boundary flag, but θ's `f` is
    0.014690871541791694 on kunanyi against …693 on deep-server. That is
    1 ulp (relative 1.2 × 10⁻¹⁶).
- **Reading:**
  - every sampling decision (acceptance, selection, ball membership) agreed;
  - the stored θ floats are reproducible only per CPU dispatch path;
  - deep-server is a Broadwell Xeon E5-2683 v4 (AVX2; NumPy has no AVX-512
    active), and the kunanyi nodes presumably use NumPy's AVX-512 `exp`
    paths;
  - so "bit-identical across machines" (the Stage 1a smoke, 38 hits) held
    for that run but is not a guarantee.
  - **The pass condition is met at decision level and missed at byte level**
    for one record.
- **Options, for Astra's check:**
  - (a) Document that libraries are reproducible to identities, paths and
    decisions, with θ to within 1 ulp across CPU types.
  - (b) Pin NumPy's dispatch (`NPY_DISABLE_CPU_FEATURES` for the AVX-512
    family) in `env.sh`, so kunanyi matches deep-server bit for bit. This
    would need one more kunanyi check.
- **Storage:** `/u/bwbrook` is on a 5.6 PB NFS export, 53% used with
  2.7 PB free. `quota` errored on an unrelated mount, and `du` timed out. A
  campaign of about 14 GB is not a storage concern.

**Repairs after Astra 1791** (design §7a). Runner `2708cb11…`, settings
`0fc62239…`, smoke subset `092758bc…` (smoke campaign ceiling 60 CPU-h,
covering both smokes), stage tar `286854e7…`.
- **Fixtures:** p3 19/19 (`p3/p3_test_receipt.txt`, with the collector's
  rejection reasons); submitter 8/8 under bash 5.2 and 4.2.46.
- **Repaired deep-server smoke** (`p3/smoke_deep2_collect_W1.json`, subset
  `864da309…`, which differs only in its ceiling):
  - `collection_ok`; 4 COMPLETE and 2 CAPPED; 6.0 CPU-h; no incomplete
    settings.
  - All 4 libraries are byte-identical to serial recomputation
    (`p3/smoke_deep2_serial_checks.jsonl`) and to the first deep-server
    smoke.
- **Quota:** `quota -s -f /u/bwbrook` prints nothing, so no home quota is
  visible. `quota -vs` fails only on the scratch export. TPAC's recorded
  home quota is 20 TiB (X-ray Cavities log, 21 August).
- **Next:** a kunanyi re-smoke (new locks, ledger and wave filter on NFS),
  then Astra's check, then W1.

**Kunanyi re-smoke dispatched** (16 October; reservation 23:25:39 AEDT).
- **Stage:** `s1b_stage.tar` (`286854e7…`) verified, and `sha256sum -c` passed.
- **Ledger:** the first smoke (array 820931[], `s1b_ad937861_a`, 24 CPU-h) was
  recorded retrospectively in `s1b/reservations.tsv`.
- **Preflight passed** (Python 3.11.7, campaign `s1b-smoke`) and reserved
  `s1b_9038aa07_a` at 24 CPU-h: 48 of 60 in that campaign.
- **Seed:** 4 pilot prefixes imported; s00772 complete at seed.
- **Jobs:** array 820962[] (2 × 8 cores, 1 h) and collector 820963 (afterany,
  emails Barry).

**Kunanyi re-smoke result** (array 820962[] queued and started 16 October
23:25:43).
- **Jobs:** subjobs on n011 and n008 ran 18 min 00 s and 17 min 31 s and
  exited 0. Collector 820963 exited 0 and emailed.
- **Collection** (`p3/smoke2_kunanyi_collect_W1.json`): `collection_ok`,
  4 COMPLETE and 2 CAPPED, 7.2 CPU-h, nothing incomplete, empty queue and
  claims, no locks left.
- **Archive:** `W1.tar.gz` (`2ed7cc4f…`), with matching hashes on kunanyi
  and deep-server.
- **Ledger:** `s1b/reservations.tsv` holds both smoke reservations (48 of 60
  CPU-h); the ledger lock was released.
- **Comparison** (`p3/smoke2_cross_machine.json`):
  - all four libraries are **byte-identical to the first kunanyi smoke**;
  - against deep-server, only the same single 1-ulp θ record in s00247
    differs, with identities, paths and boundary flags identical;
  - all six settings match deep-server on status, prefix end and prefix
    hits.

**W1 readiness, 17 October (01:00–01:25).**
- **Regression smoke `smoke_deep3`** (runner ca94676) passed: `collection_ok`,
  4 COMPLETE and 2 CAPPED, no errors or incomplete settings. All 4 libraries
  are byte-identical to serial recomputation and to the first deep-server
  smoke (`p3/smoke_deep3_*`).
- **Seed scaling found while preparing W1.** `plan()` listed the whole queue
  and claims directories on every call.
  - A full W1 seed (14,544 settings) on deep-server local disk reached only
    11,347 settings in about 13 min.
  - The listing is now **lazy**: it happens only when an unfinished range
    must be reconciled. Behaviour is unchanged, since a fresh setting has
    nothing to reconcile. Fixtures 22/22; settings rebound (`86545d6b…`).
  - **The seed is still slow:** about 13,500 settings in about 9 min on local
    disk, so roughly 25 ms per setting from locks, fsyncs and file
    creation. It will be slower on kunanyi NFS.
  - To settle in the morning: profile the seed; then either accept a long
    seed under an extended session, or make fresh seeding cheaper under the
    campaign lock. Either way, Astra checks the delta.
- W1 is not dispatched.
- **Seed timing after the lazy listing** (deep-server local disk): the full W1
  seed completed in **653 s**. It imported 720 pilot prefixes, marked 1
  setting COMPLETE, planned 14,543, and created 14,697 tickets; the run
  directory is 197 MB.

**Kunanyi NFS qualification** (17 October, about 10:35; no submission).
- **Stage:** tar `e18bea28…` (runner `00dd369f…` with the lazy listing,
  settings `86545d6b…`, smoke subset `fa477b66…`) verified; `sha256sum -c`
  passed.
- **`/u` latency** (200 operations each): create, write and fsync 27.8 ms;
  rename 2.2 ms; mkdir 1.3 ms.
- **The p3 fixture suite on kunanyi with `TMPDIR` on `/u` (NFS) passes
  22/22 in 24.8 s.** That includes the lock, reclaim-race, dead-owner and
  dead-reclaimer cases.
- **Seed profile** (600 W1 settings, deep-server): 96% of the time is fsync
  (1,801 calls, 39 ms each on deep-server `/data`). A W1 seed needs about
  16k fsyncs, so it should take about 10 min on kunanyi. It will run inside
  the dispatch session with an extended expect timeout.

### W1 dispatched (17 October 2026; Astra clearance board 1812)

Receipt: `p3/w1_dispatch_receipt.txt`.
- **Package:** stage tar `e18bea28…` verified (runner `00dd369f…`, settings
  `86545d6b…`). The submitter ran under `nohup`, with `TMPDIR` on `/u`.
- **Preflight passed** (Python 3.11.7). The production ledger recorded
  `reserve s1b W1 s1b_5e346b76_a 199688.000` at 10:55:43, with identity
  `settings=86545d6b… outdir=/u/bwbrook/vortex/run1/s1b/run jobs=520 cpus=8
  wall=172800`.
- **Seed:** 720 pilot prefixes imported, 1 COMPLETE at seed (s00772),
  14,543 planned. It took about 22 min on NFS, against an estimate of
  about 10.
- **Jobs:** array **821088[]** (520 × 8 cores, 10 GB, 48:00:00) and collector
  **821089** (`afterany:821088[]`, Mail_Users barry.brook@utas.edu.au,
  Mail_Points ae).

### W1 round 1 result and the round-2 package (21 October 2026)

**Round 1** (array 821088[] ended about 11:25; design §9a; board 2119):
- **Collector 821089** exited 1: 9,695 COMPLETE, 2 CAPPED, 0 FAILED, 4,846
  incomplete and 1 invalid. s18085 has a verified K-hit prefix but no
  COMPLETE marker, because the worker that should have planned it died.
- **CPU:** 151,638 useful and 26,666 discarded.
- **Archive:** `W1.tar.gz` (`bb604f1c…`) verified on deep-server in
  `/data/fable/vortex/v2_dev/p3/w1_r1/`. The summary is
  `p3/w1_r1_collect_W1.json`.
- **Cost diagnosis** (`p3_w1_costs.py`, `p3/w1_r1_costs.json`):
  - pilot outers and n = 0 ran at 0.97–0.98× projection;
  - the 4,251 completed unseen n = 30 settings ran at 1.19× (estimated cost
    to the crossing batch plus discards; 1.247× by recorded CPU);
  - among completed settings, the throughput and hit-rate medians are near
    projection; unresolved costs remain unknown (corrected after Codex 2142
    and 2156; design §9a);
  - restarting the 4,846 incomplete settings is estimated at about 92k CPU-h,
    a planning heuristic that excludes the invalid s18085.

**The defect** (`p3/w1_diag_20261021.txt`):
- About 103 workers died of NFS errors: ESTALE, and ENOTEMPTY when removing
  a released lock.
- Locks left by crashed workers were unbreakable from other hosts until the
  owner's job ended.
- Lock waits were unbounded, causing 75 walltime kills.
- Polling PBS on every lock spin probably slowed `qstat`.
- Appends to `jobs.log` were lost over NFS.

**Repairs** (design §9b):
- **Runner `29ece4e3…`:**
  - NFS reads retry ESTALE;
  - an error that outlives its retries parks the claim, and the same
    worker resumes it later;
  - lock waits are bounded, and a busy setting is passed over with all its
    tickets, so "all busy" is distinct from "queue empty";
  - death certificates from the node script are positive death evidence;
  - PBS is asked at most once per 300 s per job, and only about lock
    generations seen for 300 s;
  - a `select` subcommand builds a round's settings.
- **`s1b_node.pbs`:** deadline from job start with a 30 min margin;
  restarts with certificates; one `done.<index>` file per subjob.
- **`s1b_submit.sh`:** a `topup LABEL` mode for further arrays of a seeded
  wave, with `TAG` passed to the node and collector scripts.
- **`s1b_collect.pbs`:** `collect_<TAG>.json` and `<TAG>.tar.gz`.
- **`s1b_round2_dispatch.sh`:**
  - verify and install the stage;
  - derive the round-2 dirs (incomplete and invalid W1, plus all W2), refusing
    unless every round-1 error belongs to an invalid setting;
  - release round 1 with PBS evidence;
  - submit W1 r2 (300 × 8 × 48 h) and the first W2 array (570 × 8 × 48 h).
- **`p3_r2_determinism.py`:** batch-by-batch comparison of a re-run
  setting's committed hit records with an earlier round's.

**Evidence:**
- **Runner fixtures:** 27/27 (`p3/p3_test_receipt_r2.txt`). The five new
  cases inject stale handles past their retries, a busy foreign-host lock
  without PBS queries, PBS throttling, a certificate-broken lock, and a
  certified crashed worker whose job is still live.
- **Submitter fixtures:** 11/11 under bash 5.2 and 4.2.46. The three new
  cases cover topup without a seeded wave, topup without a seed, and label
  rules.
- **Fault-injection smokes on deep-server** (6 W1 + 2 W2 settings; node
  scripts as PBS runs them; a foreign-host "ghost" lock on s00073,
  certified dead at 15 min; a random `kill -9` every 3–4 min):
  - **smoke A** (pre-claim-fix runner `ee5e8cd6…`, a negative control):
    every node exited before the certificate and s00073 never ran;
  - **smoke B** (final package; `p3/smoke_r2b_*`): `collection_ok` for both
    waves (W1: 4 COMPLETE and 2 CAPPED; W2: 2 CAPPED).
    - All four libraries are byte-identical to `smoke_deep3` (old runner).
    - Determinism: 174,302 batches compared and 2,310 hit records
      byte-identical between the runners, with 0 mismatches.
    - Faults absorbed: 12 restarts (one slot through `r0`–`r4`), 33
      certificates, 7 claims requeued by certificate and 248 waits on the busy
      ghost setting. The lock broke within 1 s of the certificate; no claims
      were left and no slot failed.
    - Peak RSS per worker: 82 MB (W1), 73 MB (W2).
    - Both smokes' injectors matched both smokes' workers, so each also took
      the other's kills.
- **Dispatch rehearsals on deep-server** (stub PBS, real stage, install,
  select, preflight, seeds):
  - the positive case, with 61 incomplete and 1 invalid W1 settings, passed
    in 7 min 48 s;
  - the negative case, with an error in a non-invalid setting, refused
    before the ledger (`p3/rehearsal_r2_*.out`).
- **Production stage tar:** `b49d00f0…`, with every file byte-identical to the
  rehearsed and smoked copies.

### Round-2 repairs after Codex 2142 (21 October 2026)

Codex held 9a773c9 (board 2142; `notes/astra_s1b_r2_review_20261021.md`) with
five reproduced failures, plus three protections needed before later topups.
All are repaired; design §9e lists the changes. Runner `841feff9…`; stage tar
`3eafd94d…`.

- **Runner fixtures 35/35** on deep-server (Python 3.12.3;
  `p3/p3_test_receipt_r4.txt`; the 34/34 of `p3_test_receipt_r3.txt` is the
  intermediate runner `2d09bc7a…`). Eight are new regressions:
  - a stale certificate under the same owner name and another pid cannot
    break a live lock;
  - a failed releasing rename ends the worker with `OwnerUncertain`, and the
    next worker breaks the lock through the certificate and finishes the
    setting with an identical library;
  - six busy settings × 28 tickets cannot hide a healthy setting;
  - a recovery scan of 392 claims on busy locks stops at a 2 s deadline;
  - a timed-out PBS query is clipped to the deadline and cached (one query for
    four calls);
  - pack and log are isolated per tag;
  - a setting changed while read is retried and collected;
  - a wave-wide validation failure costs a single pause.
- **Codex's own harness on the repaired code**
  (`p3/codex_core_checks_outcomes_r3.json`, run on runner `2d09bc7a…`, which
  differs from the final runner only in the collector's retry; assertions
  recorded rather than enforced):
  - the release fault now ends the worker;
  - the healthy setting s00006 is claimed on the first call;
  - one PBS query in 60 s instead of four;
  - its recovery case uses empty certificate files, which are no longer
    accepted, so `deadline_bounds_recovery_scan` covers it instead.
- **Node fixtures 4/4** under bash 5.2 and 4.2.46 (`kunanyi/s1b_node_fixture*.json`).
  They cover a rerun with the same PBS job ID (distinct owner names, exact
  certificates, the live lock not stolen) and a restart after exit 3, with both
  processes certified. Against the reviewed node script the fixture fails at
  its first certificate, which was empty.
- **Submitter fixtures 12/12** under bash 5.2 and 4.2.46; the new case refuses
  a topup with another settings digest.
- **Dispatch rehearsals.** The dispatch script and gate are byte-identical
  across stages `1e75c7ed…` and `3eafd94d…`; the stages differ only in the
  runner's collector retry.
  - **Stage `1e75c7ed…`** (`p3/rehearsal_r3_*`): seven negative cases.
  - **Final stage `3eafd94d…`** (`p3/rehearsal_r4_*`): the positive run, its
    resuming rerun ("already released", identical settings, both waves
    resumed, no new qsub), and the checksum and error-mapping negative cases.
  - Each negative case refuses with no `p3_settings_r2.json`, no ledger line
    and no qsub:
  - a tampered stage refuses before installing anything;
  - a wrong summary digest;
  - a wrong binding;
  - a duplicate row;
  - a changed row identity;
  - an unknown status;
  - an error on a non-invalid row.
- **Fault-injection smoke D on the exact final package** (runner `841feff9…`,
  stage `3eafd94d…`; `p3/smoke_r2d_*`):
  - `collection_ok` for both waves: W1 4 COMPLETE and 2 CAPPED; W2 2 CAPPED;
  - all four libraries are byte-identical to `smoke_deep3`;
  - determinism exit 0: 174,302 batches and 2,310 records identical;
  - five `kill -9` restarts; 26 well-formed certificates with three distinct
    invocation nonces;
  - the foreign-host ghost lock broke on its JSON certificate, 3 claims were
    requeued by certificate, and no claims were left.
  - The RSS sampler matched `python3` and so recorded nothing, because the
    workers now run as `python`; smokes B and C give 82 MB (W1) and 73 MB (W2).
  - Smoke C (runner `2d09bc7a…`) ran the same faults as a stress test. Its
    receipts are not needed for the final package.

### Final runner repair after Codex 2156 (21 October 2026)

Codex accepted every other repair on 83a6b40 and held one case (board 2156;
`notes/astra_s1b_r2_closure_review_20261021.md`). A publication rename takes
effect but reports `ESTALE`, then the owner record stays unreadable past the
claim patience. `lock()` raised `LockBusy` and forgot its token, so the same
live worker later waited on its own lock.

**Repair** (design §9e, item 2): a failed publication stays unresolved until a
token is read. While unresolved at the wait limit, `lock()` raises
`OwnerUncertain` (exit 75; certified; the lock is broken once reads recover).

**Runner `1e35b94a…`; stage tar `ae127313…`.**

**Evidence:**
- **Runner fixtures 37/37** (`p3/p3_test_receipt_r5.txt`). New:
  - a 1 s read outage, within the retries: the token is reconciled and the same
    worker completes;
  - a 3 s outage: `OwnerUncertain`, then a certified restart completes with the
    serial library;
  - a known foreign live owner still yields `LockBusy`.
- **Codex's exact case** (`uncertainty_checks.py`, primary case extended with
  the node certificate and a restarted worker;
  `p3/codex_uncertainty_case_on_1e35b94a.*`):
  - the first worker ends `OwnerUncertain` after 6.2 logical s;
  - after the restart the setting is COMPLETE, with an empty queue and no
    claims;
  - the reclaim-mutex boundary is unchanged (LockBusy, then LockStale).
- **Codex's closure controls on this runner:** `core_checks.py` (10 cases) and
  `node_checks.py` (3 integrations) pass (`p3/codex_closure_*_on_1e35b94a.json`).
  Running them rewrote Codex's own receipts in place; those files were restored
  with `git checkout`, and the outputs are kept only under `p3/`.
- **Comparator** (Codex non-blocking item; standalone, not bound): duplicate
  identities in a shard, an identity carrying two different records, and
  duplicate requested settings are now rejected (exit 1). The smoke-D
  comparison still exits 0.
- **Wording:** the cost passages in NOTE and §9a are aligned with Codex's
  science closure.
- **Python 3.11:** all 37 fixtures also pass under Python 3.11.13 with NumPy
  1.26.4 and SciPy 1.11.4 (kunanyi's runtime family;
  `p3/p3_test_receipt_r5_py311.txt`).
- **Rehearsal on the final stage `ae127313…`** (`p3/rehearsal_r5.txt`): the
  positive run, the resuming rerun ("already released", identical settings,
  no new qsub) and the checksum negative.
- **Smoke E on the exact final package** (`p3/smoke_r2e_*`):
  - `collection_ok` for both waves; all four libraries identical to
    `smoke_deep3`; determinism exit 0 (2,310 records identical);
  - five restarts (one slot twice) with 26 well-formed certificates and three
    nonces; the ghost lock broke on its certificate; two claims were requeued
    by certificate and none was left;
  - peak RSS per worker: 86 MB (W1), 76 MB (W2).

### Round 2 dispatched (21 October 2026, 21:51–22:21 AEDT)

Receipt: `p3/r2_dispatch_receipt.txt` (launcher `p3/r2_dispatch_launcher.sh`).
- **Stage:** `s1b_stage_r2.tar` (`ae127313…`) pushed and its digest verified;
  `sha256sum -c` passed.
- **Round 1:** array 821088[] and collector 821089 confirmed F.
- **Install:** sources installed and compared against the stage.
- **Gate passed:** round 1 has 9,695 COMPLETE, 4,846 incomplete, 2 CAPPED and
  1 invalid (s18085).
- **Selected:** 4,847 W1 and 7,272 W2 settings; `p3_settings_r2.json` is
  `248f9c7d…` (12,119 settings).
- **Ledger:** `release s1b_5e346b76_a` (21:52:11), with the PBS evidence and
  Barry's lift, then two reserves:
  - `s1b_22b89261_a` 115,208 CPU-h (W1, run2, 300 × 8 × 48 h), at 21:53:06;
  - `s1b_3a5e71fa_a` 218,888 CPU-h (W2, run2, 570 × 8 × 48 h), at 22:06:19.
- **Preflight passed twice** on kunanyi (Python 3.11.7, NumPy 1.26.4,
  SciPy 1.11.4), with the 37 fixtures on NFS.
- **Seeds:**
  - W1: 314 pilot prefixes imported and 4,847 planned, in about 7 min;
  - W2: 360 imported and 7,272 planned, in about 15 min.
- **Jobs:**
  - W1 r2: array **857922[]** and collector **857923**;
  - W2: array **858016[]** and collector **858017**.
  - Each collector is `afterany` on its array and emails Barry (Mail_Points
    ae). At 22:21, W1's array had begun and W2's was queued.

### W1 round 2 collected, reconciled and deterministic (25 October 2026)

**Collection.** Array 857922[] reached F, and collector 857923 ran 20:30–21:40
on 24 October with exit 0. Receipt: `p3/w1_r2_collection_20261025.txt`.
- `collection_ok` true, no errors: 4,798 COMPLETE, 1 CAPPED, 0 FAILED and 48
  incomplete (all n = 30, the heaviest; their shards were censored at the 48 h
  limit and requeued in run2).
- CPU: 49,493 useful and 17,974 discarded. The discarded figure includes the
  incomplete settings' completed ranges beyond their prefix, which the next W1
  array resumes under the same binding.
- **Archive:** `W1.tar.gz` (`c12e5378…`, 825 MB; summary `3cd15802…`) was
  verified on deep-server (`/data/fable/vortex/v2_dev/p3/w1_r2/`). It holds
  4,800 members: the summary, the log and 4,798 libraries.

**Settings reproduced.** `select` on deep-server, from round 1's summary, the
full settings and runner `1e35b94a…`, gives `p3_settings_r2.json` =
`248f9c7d…`, the same as kunanyi.

**Strict reconciliation** (`p3_w1_reconcile.py`; `p3/w1_reconcile_r1_r2.json`;
exit 0). For each round:
- the binding is its own settings, metric and runner;
- the rows are exactly its W1 settings, with unchanged identities, known
  statuses and consistent counts, and errors one-to-one with invalid rows;
- a library exists exactly when the row is COMPLETE;
- every library (9,695 + 4,798 = 14,493) matches its digest and has exactly
  2,000 records, strictly ordered by (batch, proposal), with the K-th record's
  batch equal to `kth_hit` and the metric's path length.

Across rounds:
- round 2's rows are exactly round 1's incomplete and invalid settings;
- 9,697 + 4,799 terminal settings plus 48 remaining partition all 14,544 W1
  settings.

**Round-to-round determinism** (`p3_r2_determinism.py` on kunanyi, round 1
`run` against `run2`, over the 4,847 W1 round-2 dirs; 1,590 s):
- exit 0 over 9,336,542,588 batches committed in both rounds;
- **1,643,296 hit records compared, all byte-identical**, with 0 unmatched
  identities, 0 byte differences and 0 journal problems.
- The comparison spans different runner versions and bindings, kunanyi nodes
  and shard plans.
- The full per-setting JSON is on kunanyi at `s1b/probe/w1r2_determinism.json`.

**W1 after round 2:** 14,493 COMPLETE libraries and 3 CAPPED; 48 settings to
finish with a W1 array in run2.

### Topups b dispatched (25 October 2026, 16:18–16:22 AEDT)

Receipt: `p3/r2_topup_b_receipt.txt`.
- **Pushed files** verified on kunanyi: node `8fe10208…` and dispatch
  `e85c24b9…`. The installed runner `1e35b94a…`, submitter `e8cb24aa…` and
  collector `ab8c1aa2…` were confirmed.
- **Determinism file:** `s1b/probe/w1r2_determinism.json` is `73f9cd12…`,
  identical on kunanyi, on deep-server and in `p3/w1r2_determinism.json`.
  - Of the 4,847 settings, **3,756 have no batches committed in both rounds**,
    because round 1 never started most of its open settings beyond their
    pilot. The 1,643,296 identical records come from the other 1,091.
  - No setting has common coverage without records.
- **Ledger:** `release s1b_22b89261_a` at 16:18:16, after W1 round 2's array
  and collector reached F.
- **Sizing:** the live request total was 2,601 CPUs (W2: 325 live subjobs).
- **W1 topup b:** array **860989[]** (170 × 8 × 48 h) and collector **860990**;
  reservation `s1b_b373da8c_a`, 65,288 CPU-h.
- After the W1 topup the live total was 3,946 (W2: 323 live).
- **W2 topup b:** array **860992[]** (381 × 8 × 48 h) and collector **860993**;
  reservation `s1b_f093f541_a`, 146,312 CPU-h.
- **Live requests after both: 6,995 of 7,000 CPUs.**
- Both preflights passed on kunanyi (Python 3.11.7).
- Both collectors are `afterany` on their own arrays and email Barry.
- W2's original reservation (218,888) stays until 858016[] and 858017 finish.

### W2 first-array collection and duplicate shard execution (27 October 2026)

Details are in design §9g; receipts `p3/w2_a_*`.
- **Collector 858017** exited 1: 183 COMPLETE, 7,076 incomplete and 13 invalid.
  Archive `55448298…` verified on deep-server; summary `9bfe0ca4…`.
- **The 13 invalid settings fail persistently:** journals out of step with
  their checkpoints, some exactly doubled.
- **Census:** 8 ranges with two live claims and 1 range both queued and
  claimed.
- **Concurrent duplicate execution is the interpretation**, most likely through
  orphan republication from an incomplete NFS directory listing.
- **Integrity holds** through the strict collector and refused recovery.
- **W2 continues.** Affected settings get a later round under a repaired
  runner.
- **Live state at 14:36:**
  - W1 topup b 860989[]: 14 subjobs running, 156 expired;
  - W2 topup b 860992[]: 381 running;
  - live requests 3,162 CPUs.


### Round-3 ownership repair and W1 round-2 final collection (27 October 2026)

Details are in design §9h; Codex's review is at board 2420–2423.
- **Runner `c56d0af6…`** (commits 6c6995c and 451e50e):
  - ownership lives only in each setting's own records: the `r/` chain and numbered `x/` executions, created
    exclusively by hard link and never replaced;
  - queue and claim entries are hints;
  - a relaunched worker recovers its certified slot predecessors' executions by exact name;
  - the collector checks execution consistency.
- **Fixtures** pass 41/41 under Python 3.12.13, 3.11.13, deep-server 3.12.3 (six concurrent runs) and **kunanyi 3.11.7
  on `/u`**, where `os.link` is exclusive. The new cases cover omitted listings, concurrent lagging claimants, eight
  interrupted transitions and predecessor recovery.
- **Ownership control:** the bound runner admits a second writer, and Codex's reproduction doubles its journal; the
  candidate admits none.
- **Adversarial smokes** (30% omission of queue/claimed entries, kill -9 every 3 minutes, ghost lock):
  - **bound control:** 4 invalid settings, 73 shards (duplicate execution reproduced);
  - **928265bd:** passed, with one stranded range, which led to the successor fix;
  - **c56d0af6:** passed, libraries identical to `smoke_deep3`, 0 open executions, 0 superseded, determinism exit 0.
- **Stage `ddb014b0…`** (deterministic, `build_stage_r3.sh`). Rehearsals with stub PBS: the positive case (7,137
  settings; 168 + 706 subjobs; resume; W2-only topup, released and resumed) and five negatives all behave as
  specified.
- **W1 round 2 is final** (collector 860990): 4,820 COMPLETE, 9 CAPPED, 15 incomplete and 3 invalid (duplicate
  execution). Archive `849cd0ba…` and summary `8d702807…` are verified on deep-server.
- **W2 topup b** 860992[]: 381 running at 17:21; live requests 3,049 CPUs.

### Round-2 final, Codex review and round-3 repairs (27–29 October 2026)

Details are in design §9h; Codex's review is at board 2425–2427 (`notes/astra_r3_*_20261027.md`).
- **W2 round 2 is final:** collector 860993, exit 1, with 355 COMPLETE, 6,901 incomplete and 16 invalid. Archive
  `c760f0c6…` and summary `beabe2d1…` were pulled directly from wsl, because the Macs no longer reach deep (29 October),
  and verified on deep-server. All round-2 jobs are F, with 0 live requests.
- **Round 3 inventory:** 18 W1 + 6,917 W2 = **6,935** settings.
- **Codex's blockers are repaired:**
  - runner `e261befa` writes the held intent before execution creation;
  - capacity is checked by `s1b_capacity.sh` and the submitter's just-in-time gate;
  - the dispatchers recompute unbound sizes and wait for, then fail closed on, unlisted accepted jobs;
  - `STAGE_SHA` and the manifest are pinned.
- **Evidence:**
  - fixtures 42/42, and submitter fixtures 16/16 under bash 5.3.9 and 4.2.46;
  - Codex's recovery reproduction on `e261befa` reports `gap_reproduced: false`;
  - the adversarial smoke passed;
  - eleven rehearsals on stage `53603d42` behaved as specified.
- **`kunanyi/tpac.sh`** now runs on wsl, with `run`, `push` and `pull` over the direct VPN route.

### Held-publication repair (29 October 2026; receipts collected 4 November)

- Codex 2550 held dispatch for one defect: `hold()` updated memory before publishing the held file. Runner
  `92674ee8` (d80a60b) publishes first, then updates memory.
- Fixtures 43/43 (local 3.12 and 3.11; three concurrent deep runs); Codex's closure check does not reproduce the gap.
- Adversarial smoke on 92674ee8 passed (identical libraries, 0 open, 2 predecessor recoveries, determinism exit 0).
- Stage `9b2786d6` rehearsals: positive/resume/topup at 6,994 CPUs; substituted manifest refused. New settings digest
  `fa772829`.
- The session ended on 29 October before these receipts were collected and posted; they were collected on 4 November
  from deep, where the runs had completed on 29 October.

### Round 3 dispatched (4 November 2026)

- Codex cleared 92674ee8 / 9b2786d6 / fa772829 (board 2875). Dispatched from wsl in one Jumpbox window; the reviewed
  settings file was placed first, so the dispatcher's recomputed selection had to match fa772829 before any qsub.
- W1 `876185[]` 63 × 8 (collector 876186), W2 `876193[]` 811 × 8 (collector 876194); 6,998 live CPUs.
  Receipt `p3/r3_dispatch_20261104.txt`.

### W1 round-3 collection and W1 topup (6 November 2026)

- Collector 876186: ok, 1 CAPPED, 17 incomplete, 0 errors (archive 5e0de476, summary 020a9bbf). 56 of 63 subjobs
  retired after 30 min idle: from-zero settings run one prior-sized first range (14–18 h) before fanning out, so W1 had
  18 runnable ranges for 504 slots until 5 Nov. Specified behaviour, not a defect (design 9h).
- W1 topup b: `876850[]` 60 × 8 (collector 876851), 333 W1 hints queued; live requests 6,910 CPUs.
  Receipt `p3/w1_r3_collection_20261106.txt`.

### W2 topup b and the capacity-helper pipefail defect (11 November 2026)

- W2 array 876193[] nearly done (809 expired, 2 running); 9,482 W2 hints queued; 127 COMPLETE + 1 CAPPED so far.
  W1 topup 876850[] started 9 Nov (17 running, 43 expired).
- W2 topup b: array `878694[]` 854 × 8 accepted; its collector was refused. `unlisted()` piped a 1,977-line (~158 KB)
  listing into `grep -q` under `set -o pipefail`: grep exits at its first match, printf takes SIGPIPE, and listed jobs
  read as unlisted (flickering per check). Rehearsal listings were below one pipe buffer, so they never showed it.
- Fix: every `cmd | grep -q` in s1b_capacity.sh and the round-3/topup dispatchers becomes a here-string. Submitter
  fixtures 17/17 under bash 5.3.9 and 4.2.46 with a new 3,000-line listing case; the old helper fails that case exactly
  as production did (`p3/r3_submit_fixture_oldhelper_control_20261111.json`). Receipt `p3/w2_r3_topup_b_20261111.txt`.
- Outstanding: install the fixed helper on kunanyi and rerun the W2 topup b dispatcher to add 878694[]'s collector
  before that array ends (after Codex's check).
