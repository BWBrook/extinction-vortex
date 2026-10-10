# Astra review of protocol 0.8

10 October 2026, Hobart. Reviewed Fable's handoff 1326 and commit `f8546ec`.
The WSL and canonical Mac checkouts were clean and identical at the start.
This completes the [pre-handoff review](astra_protocol08_precheck_20261010.md).

**Disposition: accept the revised design for continued development, with the
remaining specifications below settled before a validation freeze.** The
risk-defined effect target remains unchanged. Barry's primary-null and
primary-estimator decisions need no further question. This review is not a
production freeze or an empirical inference.

## Accepted changes and verified evidence

- **Effect target and interpretation.** Retain the existing effect recipe and
  its development value, beta_min = 0.974519 (Delta10 = .075). The five-arm
  screen remains 1, 1, 2, 8 and 18 detections out of 30. A failed frozen power
  gate makes a non-rejection O3; it does not prevent O2 after a calibrated
  rejection, and does not establish absent feedback. The two larger-effect
  descriptive arms are a useful detection curve, not replacement power gates.
- **Corners.** Accept high sigma, low survival and strong environment as the
  three development corners. Replacing short L is appropriate because the
  nine schedules are fixed. These are selected stress scenarios, not a claim
  of uniform validity over nuisance parameters. Recompute their numerical
  values using the fixed recipe on the designated primary bank and measure
  their actual generation/fitting costs before freezing.
- **Radius diagnostics.** Accept the narrower typical-radius interpretation,
  predeclared radius strata, and an always-run descriptive fitted-parameter
  check. None establishes calibration conditional on the empirical C. Record
  numerical bin boundaries, their source and the tie rule before validation;
  an independent C-only development sample can supply these boundaries.
- **Input guards.** Tiny fixtures on immutable source copies verify ragged-T
  handling, absent arms/checkpoints with intended denominators, finite p_hi
  mismatch detection, and the shard count/length/index/width checks. Valid v1
  fixture behavior is retained. A narrow non-finite reconciliation gap remains
  below. These fixtures do not establish that every real bank is intact.
- **Archive identity.** All 150 T-file manifest entries and the ten archived
  arm metadata/checkpoint files match the earlier independent raw-statistic
  audit. The five outcome summaries reconcile. Raw T files were not fetched
  or fitted again in this review.
- **Cost.** The archived 204,149.03 user plus 1,290.53 system CPU seconds give
  1,369.597 seconds per trial, or 0.380444 core-hours. The stated inventory
  sums to 3,130.50 core-hours using the two small placeholders. The roughly
  75-hour extrapolation for 7,900 trials uses the measured concurrent pilot
  throughput and excludes bank construction. Corner and M_D/M_O costs remain
  unmeasured; the empirical sensitivity inventory also needs completion below.

## Remaining findings

### MAJOR: define the stress check's finite-budget sampling law

Protocol lines 608–613 draw a parameter uniformly from an empirical library,
retain it for up to one million trajectory attempts, then replace it after a
timeout. That is fully specified as an algorithm, but the *completed* parameter
mixture is no longer uniform over that library. If p(theta) is the probability
of S and A, its weight is proportional to

`q_M(theta) = 1 - (1 - p(theta))^M`, with `M = 10^6`.

For illustrative p values of 10^-5, 10^-6 and 10^-7, these weights are
0.99995, 0.63212 and 0.09516. These are analytic examples, not measured library
frequencies. The actual size of this effect is unknown. Failure to sample
within the budget does not establish that a parameter is unselectable.

**Preferred repair:** draw the 300 intended parameter-vector sets once, retain
them, and record a sampling-budget failure if any population times out. Do
not replace that outer dataset; report unresolved counts and conservative
descriptive bounds. This preserves the intended mixture and the project's
fixed-denominator convention. Alternatively, explicitly define and label the
retry-weighted mixture and report its rejection/timeout diagnostics. Settle
this before implementing the stress sampler; it creates no extra empirical
p-value gate and does not affect the completed power screen.

### MAJOR: reconcile the remaining execution scope before calling the cost complete

The 7,900 synthetic-dataset arithmetic is correct. The approximately five
empirical datasets in §4.4 (line 893) do not cover the sensitivity list in §7
(line 1154): nine leave-one-population-out runs alone exceed it. Other promised
checks include the joint turtle exclusion, crane exclusion, alternate rule E,
separate environmental factors, missing-fill and window treatments. Some can
reuse banks; others change the generator, selection or observation mapping and
need their own reference construction. This is a scope/inventory gap, not a
claim that the total must be much larger.

Also, §4.1 (lines 734–738) still specifies two 200-dataset development screens
and a >30/200 gross-miscalibration stop. The new screen has 30 datasets per
arm and does not satisfy that stated requirement. Explicitly retain and run
the development screen, or propose a dated replacement and its justification
before the freeze. Do not silently mark it complete or reinterpret development
data as the fixed production experiment.

**Repair:** one compact execution table linking each currently promised
analysis to its generator, bank reuse/new bank, outer count, seed family,
estimator and measured/projected cost. Mark genuinely access-dependent items
as such. Changes to agreed scientific scope need explicit disposition; do not
drop sensitivities merely to preserve the headline cost. Existing compute
authority covers routine allocation within the authorized work; this is not
a request for another resource-permission gate.

### MINOR: NaN bypasses logged-bound reconciliation

In `score_discrimination.py` lines 86–89, `abs(recomputed - logged) > 1e-12`
is false if the logged value is NaN. A tiny v2 fixture with a finite recomputed
p_hi and a logged NaN exits successfully. The output bounds and classification
are still recomputed correctly; the defect is false reconciliation success.
The earlier audit independently checked both finite bounds of every actual
power-screen trial, so this finding does not invalidate those results.

Require finite numeric logged bounds before comparing them, or use a comparison
that rejects NaN. Preserve a tiny non-finite-bound fixture alongside the finite
mismatch check. No general validator framework is needed.

## Next bounded tranche

Fable retains implementation and formal-protocol ownership; Astra reviews the
next handoff. Before building the final run definition:

1. Propose the M_D d/k distributions and precise AR drift/step law, plus M_O's
   latent initial count, detection and recorded-endpoint selection contract.
   M_O must select on its recorded counts if it is intended to mimic the
   observed selection; do not accidentally impose both recorded and latent
   extinction. Preserve the latent/recorded distinction in the output.
2. Implement and check limiting cases: zero deterioration recovers ar_cat;
   beta = 0 in a mixture recovers its M_D component; detection p = 1 recovers
   the corresponding latent-count generator. Preserve source/input hashes and
   count sampling/fit failures. Resolve the stress and scorer findings above.
3. Complete the execution inventory, development-screen disposition and corner
   timings. Then freeze bank-generation settings/seeds, build the designated
   banks, and recompute beta_min/corners by the existing fixed recipes. Freeze
   those outputs, exact estimator/reference settings and validation streams
   together before validation; inspect no empirical conditional-null p-value
   beforehand.

Stop at a reviewable freeze package with the unresolved source/census limits
visible. No new question for Barry is needed for this continuation. Any proposal
to alter the effect target or expand Phase II remains a separate scientific
decision.

## Verification and limits

- `python3 analysis/astra/protocol08_review/evidence_check.py` reconciles the
  archive, counts, cost arithmetic and analytic retry-cap examples; its
  [receipt](../analysis/astra/protocol08_review/evidence_check.json) records hashes.
- `/home/bwbrook/papers/dsipa-dev/.venv/bin/python analysis/astra/protocol08_review/guard_audit.py`
  runs the tiny fixtures against immutable `f8546ec` source. Its
  [receipt](../analysis/astra/protocol08_review/guard_audit.json) records source
  hashes and Python/NumPy/SciPy versions. No packages were installed.
- No new population simulation, R fitting, bank construction or empirical
  testing occurred. The 17 GB of bank payloads and the coverage arrays were
  not independently replayed. Guard fixtures verify the listed failure modes;
  they are not an end-to-end validation of the scientific procedure.
