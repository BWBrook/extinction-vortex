# Astra review of the completed 0.10 freeze candidate

11 October 2026, Hobart. Reviewed handoffs 1371/1392 at `df94693`, with
executable source `49f65ce`. WSL and the canonical Mac checkout matched and
were clean before the review.

**Disposition: evidence accepted; executable freeze held for two focused
repairs.** The designated banks, completed development screens, fixed stress
sets and selected-draw provenance pass the checks below. Missing-output
accounting and configuration binding still permit a validation certificate
that does not establish the declared procedure. Fable owns these repairs;
they require no new scientific choice or bank construction.

## Accepted evidence and scientific scope

- Independently recalculated all **400 raw synthetic T files**, including both
  full-precision p bounds, ordered set IDs, outcomes, failure indicators and
  fallback totals. Both arms have **5/200** rejections and **1/800,200** failed
  T vectors. The rejection and failed-fit trial IDs differ between arms.
  No covariance shrinkage was needed in these completed screens. The exact
  95% interval is 0.008166–0.057374; the one-sided 98.75% upper bound is
  0.062596. The declared development stopping thresholds are not triggered.
- Rehashed **all 540 bank shards** on deep-server and matched the archived
  manifests. Metadata supports 2 billion draws per population per bank and
  540 distinct seeds. All 400 screen T hashes, four row/metadata files,
  available archived package inputs and **17 frozen source hashes** agree
  with the remote evidence and named source commit.
- Independently matched all **2,700 stress vectors / 16,200 parameter values**
  to their retained indices in the hashed empirical-library NPZ. Its pooled
  medians and per-population quantiles exactly reproduce the effect JSON.
  This verifies the retained library evidence, not a replay of bank generation
  or the forward extinction-risk simulations.
- The independent sampler audit reproduces all 2,700 index draws and the
  scenario definitions, confirms 170 distinct chunk seeds, and exercises the
  exact million-draw budget plus a non-multiple remainder. Its mocked stress
  fixture retains failed trial IDs and theta without replacement; a successful
  fixed-theta trial follows the fitting path. Tiny real M_D/M_O checks retain
  the selected parameters and complete recorded/latent counts.
- The archived manifest itself correctly defines 17 blocks, 170 disjoint
  chunks and 7,900 trials. The null limit of 60/1,000 and power limit of
  224/300 are correct. Their adjacent CP boundaries are 0.079032/0.080157
  and 0.698490/0.701975 respectively. Fit stopping applies to blocks 1–5;
  block 17 remains descriptive and occurs once.

The risk-defined beta_min remains Delta10 = 0.075. The development detection
rate is indistinguishable here from the null rejection rate; retain the poor
power evidence and the O3 consequence. Do not retune the effect or claim an
empirical result. Prior M_D/M_O interpretation limits remain accepted.

## MAJOR: make incomplete-output accounting consistent with the fit stop

`score_discrimination.py:76` skips a trial without a JSON row before examining
its T file. A bounded fixture with 970 accepted rows and 30 present, wholly
failed T files whose JSON rows are absent produces a passing null gate
(30/1,000 non-accepts), **0/39,770** reported fit failures and no fit stop.
The available T files establish **1,230/41,000 = 3%** failures. These are
synthetic fixture results, not a defect found in the completed 400 screens.

Derive fit accounting from available T files even when the row is missing.
Where fit status cannot be established, use an explicit conservative rule
or block certification; do not silently grant the no-fit exemption reserved
for verified sampling-budget failures. Check the `failed` flags against T
finiteness, or derive the numerator directly: a separate fixture demonstrates
that zero flags alongside missing T cells otherwise suppress the fit stop.

Also reconcile missing/malformed T handling with the promised contract.
Deleting or truncating a T file after a successful logged row causes the
scorer to abort on `indet_malformed != logged accept`, rather than retain
the specified malformed outcome and all-failed count. This fails closed,
but defeats the declared conservative collection procedure. Preserve the
logged outcome separately and apply the missing/malformed rule; keep strict
agreement checks for valid, recomputable files.

## MAJOR: bind validation, restart and empirical execution to the same inputs

The empirical guard checks the manifest pathname only. A passing summary is
accepted after that file is changed in place. Restart skips any chunk with
the expected set of row IDs without matching its configuration. The collector
uses R from chunk metadata and does not compare it with the manifest. A
fixture using R = 20, K = 50 and stale variant/effect metadata can therefore
be collected and skipped under a manifest requesting R = K = 2,000.

Record and verify a digest of the frozen manifest in each chunk and collector
summary. Validate chunk settings against that manifest before reuse or
collection, and verify its current digest in the empirical guard. Check the
required T outputs before declaring a chunk complete. Keep the package's
existing source/input hashes as the run's preflight evidence. A small shared
consistency check is sufficient; no workflow platform is needed.

The Q1 entry point also permits a populated output directory to be rerun,
overwriting T files and appending duplicate rows. Refuse existing empirical
results for the declared once-only run, or require an explicit documented
recovery path. This is a bounded addition to the same guard repair.

The current archived manifest has no overlapping IDs or repeated directories.
Our repeated-chunk fixture demonstrates a further missing collector invariant;
checking uniqueness is useful, but it is not evidence of corrupt current inputs.

## Small record corrections and handoff

- The 452,339 CPU-seconds / 125.6 core-hours receipt times the complete
  `run_production_banks.sh` driver, including the effect, positions and
  generator timing stages. Label it as the designated-bank package run,
  rather than an isolated measurement of bank construction.
- The detailed sensitivity seed allocation correctly separates
  8.70/8.71/8.72/8.73e12; the section 7 inventory still abbreviates several
  entries as 8.7e12. Align them before those sensitivities are implemented.
- No resource-only questionnaire was opened. The current Nectar operating
  record carries Barry's standing 13 September authority to allocate compute
  for authorized work. The proposed extra compute question must be reconciled
  with that authority; it is not the reason for this technical freeze hold.
  Scientific scope, validation and empirical gates remain distinct.

**Next: Fable.** Repair the two execution contracts, run the focused regression
fixtures, and return the revised code/manifest/source hashes and receipts.
No bank rebuilding, effect retuning or repetition of the 400 development fits
is required by these findings. Astra then verifies the repaired contracts and
names the accepted freeze. No validation or empirical run was launched here.

## Reproduction and limits

Receipts and runnable checks are in
[`analysis/astra/protocol10_review/`](../analysis/astra/protocol10_review/).
Run `evidence_check.py` with Python 3 and SSH access to deep-server; it reads
completed artifacts and rehashes the 28 GB bank payload using one process.
Run the sampler and gate scripts with the existing
`/home/bwbrook/papers/dsipa-dev/.venv/bin/python`. The gate fixtures deliberately
record the current discrepancies; they are not assertions that validation passed.

No R fits, new large simulation, remote file changes or empirical T/p-value
access occurred. The only new simulation was the bounded local generator
fixture. Hash agreement, mathematical checks and agreement between agents
do not establish scientific calibration; fresh validation remains necessary.
