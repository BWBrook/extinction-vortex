# Astra: external-information Stage 0 audit

Audited revision: `3437fcdcf751bce1a4a0622a9f80d6299b3e734d` (Fable's
board-1642 handoff). Review completed 14 October 2026, Australia/Hobart.

**Disposition:** the saved Stage 0 concentration summaries reproduce. No
observed implementation or aggregation error overturns them. The report needs
one population-list correction and narrower interpretation; the runner needs
binding/completeness guards before reuse. This is a no-fit development
diagnostic, with no calibration, power or empirical validation result.

## Finite findings

1. **P2 — active interpretation overreach.** In
   `analysis/fable/calibration/v2_dev/NOTE.md:363–375`, low ESS becomes “too
   little support” and a future fitted Stage 1 becomes “uninformative”. The
   measurements establish concentrated normalized weights among the existing
   K = 2,000 members. They do not establish absence of target support,
   importance-sampling error, reference-draw adequacy, or the outcome of an
   unrun fitted test. Five populations have small corner medians while the
   other four are appreciably larger; “a handful … per population” also
   overgeneralizes. Report the measured concentration and the reason to
   investigate an informative proposal, preserving the explicit statement
   that calibration and power were not measured. Parent review owns the
   related future-design wording and sampler choice.

2. **P2 — report accepts incomplete or incompatible artifacts; dormant in
   this completed report.** `s0_info.py:191–236` loads and echoes bindings
   without checking input/helper/runtime/source/member compatibility. The
   per-population outputs themselves contain no input or runner hash, so a
   report cannot establish that association merely by hashing today's inputs.
   It does not check population labels or exactly one record for each expected
   outer. Its union of available IDs silently shrinks a denominator when the
   same outer is missing in all populations. A temporary fixture removed
   `null_prior_predictive/199` everywhere and supplied changed helper/runtime
   bindings, wrong population labels and absent member payloads. `report()`
   still succeeded, reporting 199 datasets and 7,191 neighbourhoods. Add
   per-output input/source bindings and require the exact expected unique
   outer/population/key sets, matching member hashes and compatible metadata.
   **Current result:** independent checks below recover all 800 expected
   outers and exactly 200 unique paired datasets in every cell, and all 18
   committed output/member hashes agree. No current denominator error was
   found.

3. **P2 — incomplete run-time source binding; no observed mismatch.**
   `s0_info.py:144–159` checks the manifest digest, this runner, runtime,
   original outer files and population bank shards. It does not check the
   bytes of imported frozen sources or `bank_meta.json`; the shard filter
   excludes the latter. `load_bank` has useful structural metadata checks but
   these do not replace byte binding. Bind/verify the actually imported source
   files and metadata before a later run. **Current result:** all 12 frozen
   source files and `bank_meta.json` freshly match the frozen manifest; pinned
   runtime also matches. These missing guards do not demonstrate that this
   run used wrong bytes.

4. **P2 — active population-list error.** NOTE lines 357–360 omit
   `wood_turtle_A`, whose corner n = 300 median ESS is **14.6159 noisy /
   14.7172 ideal**. The remaining four populations range from **46.4989 to
   198.5349 noisy**, or **49.1831 to 219.9090 ideal**. “Other populations
   range from 46 to 220” is wrong unless wood turtle A is first included in
   the low-median list. The JSON report itself is correct.

5. **P3 — dormant numerical input edges.** At `s0_info.py:64–72`, mixed
   `[0, +inf]` log weights are reported usable with ESS = 1 because the
   infinite member is discarded. Reject positive infinity explicitly. At
   lines 59–61, ideal weights use direct `0 * log(0)` arithmetic: true and
   candidate zero rates can create NaNs where an `xlogy`/`xlog1py` expression
   has a valid limit. Use boundary-safe arithmetic before extending the model
   to exact zero/one rates. These fixtures do not identify a current result
   failure: the specified priors yield interior rates, and all 28,800 saved
   weight sets are finite and usable. No arbitrary uniform fallback occurs.

## Independent evidence

The audit read the nine saved diagnostic JSON files and nine saved member NPZs
on deep-server, processing one member file at a time. The host check found
load approximately 61 and 104 GB available memory; this bounded read and
arithmetic audit took 7.3 seconds. It did not construct a bank/tree or run
population simulations, reference draws or fits.

- **Outer and stream binding:** all 800 input outers match the original v1
  records, six nuisance coordinates, recorded trajectories and logged radii,
  with exactly one original record per expected key. All 1,800 b3
  population/outers match the manifest's fixed corner. The 18 source-row
  files match their bound hashes. All 14,400 saved E draws replay exactly
  under Python 3.12.3 / NumPy 1.26.4 / SciPy 1.11.4. Independent vector
  evaluation of the rate functionals differs by at most `4.44e-16`.
- **Artifacts and membership:** all nine member arrays contain exactly
  `800 × 2000` integer IDs, with no duplicates within a neighbourhood and
  IDs inside the bank's draw range. Their hashes match both the raw records
  and committed checksum file. All **3,600 b1/b3** sorted member digests agree
  with the earlier D1c2 K-neighbour diagnostic, including its tied cases.
  Counts reproduce **7,200 neighbourhoods, 519 boundary ties and zero
  mismatch flags against the rounded v1 radii**.
- **Aggregation:** all per-population ESS/share quantiles, pooled ESS
  quantiles, radius quantiles, unusable counts and any-of-nine fractions
  reproduce exactly at the report's rounding. There are **zero unusable
  sets**, and every cell has exactly 200 datasets.
- **Numerical implementation:** AST-isolated production functions pass their
  self-tests. Three independent finite noisy-weight fixtures differ in
  ESS/share by at most `2.22e-16`; the ideal log-weight expression agrees
  with expected-count arithmetic within `5.68e-14`. The previous 45-case
  quadrature receipt is reused, not rerun: maximum GH40 versus adaptive
  quadrature error `7.77e-16` over its stated deterministic grid.
- **Provenance and cost:** local and remote inputs/report/runner/manifest
  agree. The runner and inputs equal their pre-weight commit `1f82fe4`
  versions. Fresh source and bank-metadata checks pass. The saved full log
  records **24:08.94 elapsed**, exit status 0 and maximum RSS 12,074,316 KiB.
  The helper's “GB” field divides KiB by 1e6; the log value is about 11.52
  GiB or 12.36 decimal GB, so “12.1 GB” is approximate labeling, not an
  indication of a resource overrun. Whole-bank functional evaluation is
  broader than member-only evaluation but the observed time is within this
  bounded diagnostic's budget.

| Cell | Block | n | Any-of-nine ESS < 100, noisy / ideal | Pooled median ESS, noisy / ideal |
|---|---|---:|---|---|
| 0 | b1 | 30 | 0.425 / 0.340 | 605.5037 / 756.3833 |
| 1 | b3 | 30 | 0.825 / 0.260 | 317.4203 / 337.0434 |
| 2 | b5 | 30 | 0.515 / 0.355 | 615.7043 / 723.8308 |
| 3 | b16 | 30 | 0.680 / 0.430 | 453.8499 / 562.0633 |
| 4 | b1 | 300 | 0.995 / 0.995 | 100.2074 / 106.2390 |
| 5 | b3 | 300 | 1.000 / 1.000 | 15.6403 / 14.6090 |
| 6 | b5 | 300 | 0.995 / 1.000 | 92.1434 / 99.1829 |
| 7 | b16 | 300 | 1.000 / 1.000 | 46.7450 / 49.0997 |

| Population, b3 n = 300 | Median ESS noisy | Median ESS ideal |
|---|---:|---:|
| Wild dog | 3.2108 | 3.2218 |
| Marmot | 6.3119 | 6.1060 |
| Middle-spotted woodpecker | 8.8792 | 8.7931 |
| Red-cockaded woodpecker | 47.8850 | 51.6542 |
| Golden plover | 4.3164 | 3.6923 |
| Whooping crane | 79.0093 | 83.7699 |
| Hawaiian crow | 198.5349 | 219.9090 |
| Wood turtle A | 14.6159 | 14.7172 |
| Wood turtle B | 46.4989 | 49.1831 |

## Receipts, reproduction and limits

Receipts and audit source are in `analysis/astra/stage0_info_review/`:
`remote_audit.py`, `remote_audit.json`, `local_checks.py`, and
`local_checks.json`. The JSON receipts include full raw/member/source hashes,
all per-population quantiles, runtime and scope. Principal bindings:

- Manifest: `96603037ec05036153f67b649757d067ca193c5e0a8610d3b855ef8f22139429`.
- Runner: `c42534764dff7f587d845e599c5a196ee16e2a32dbf83f1d1bbf968c920710d5`.
- Inputs: `e1479a2f2a96ad5321fe89b25b30df8b21a69792e7ba4907f9a95714343b0126`.

From the repository root, with the same remote paths available:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 deep-server 'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -' < analysis/astra/stage0_info_review/remote_audit.py > analysis/astra/stage0_info_review/remote_audit.json
OPENBLAS_NUM_THREADS=1 /home/bwbrook/papers/dsipa-dev/.venv/bin/python analysis/astra/stage0_info_review/local_checks.py
```

The audit independently recomputes summaries from the saved diagnostics; it
does **not** recompute all individual ESS values from bank parameters or
rebuild neighbourhoods. It freshly hashes the metadata and frozen source,
but does **not** rehash the 180 full bank shards; the runner checks those
shards, and that assertion is source evidence rather than a fresh independent
bank-byte check. The b5/b16 member IDs have no prior comparable member receipt
in this review; their shape, uniqueness, range, stored checksums and logged
radii are checked, without a new tree query. Rounded radius equality alone
would not establish tied membership. Local numerical fixtures use NumPy 2.3.5
/ SciPy 1.16.3; the full saved-E replay and artifact audit used the pinned
remote versions. A matching present-day source cannot retrospectively prove
an unrecorded execution environment; the launch command and hashes provide
supporting evidence with the binding gap described above.

No peer artifact was edited and no extension beyond Stage 0 was run.

14 October 2026, 16:45:32 AEDT (Australia/Hobart).
