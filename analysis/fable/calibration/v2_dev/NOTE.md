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
- **Fixtures** (`p2/s1a_test_receipt.txt`, 35 checks, all pass):
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
- **Collector fixtures** (in the 35): a valid run with a missing setting is
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
    conditional on non-informative censoring.
- **Cost:** observed CPU through the crossing batch for hit-stopped settings.
  Rate-based projections to 2,000 for the others are labelled as
  projections.
- **Zero hits** give an upper retention bound and an unresolved cost.
- All 1,080 rows and complete-nine-population availability are reported.
- The collector computes these per row.

**Dispatch** (after Astra checks this repair; one Jumpbox window).
1. Push the tar and extract it into run1.
2. Run `sha256sum -c`.
3. Run `s1a_submit.sh /u/bwbrook/vortex/run1 p2_settings_s1a.json main 45 8
   02:45:00 1000 0.44`. Its preflight runs the bound check and fixtures on
   the kunanyi login node before any qsub.
4. The afterany collector emails Barry. After any interruption, rerun with
   `resume`.
