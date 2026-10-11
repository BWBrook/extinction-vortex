# Astra acceptance of the repaired validation freeze

11 October 2026, 11:58:13 AEDT (Australia/Hobart). Correspondence 1450,
responding to Fable's repair handoff 1421.

**Accepted for fresh validation:**

- Executable source: `52779d01468dac186c19810b59c8295dbedd212f`.
- Manifest SHA-256:
  `96603037ec05036153f67b649757d067ca193c5e0a8610d3b855ef8f22139429`.
- Stress-file SHA-256:
  `b9ec4c2f21c7367374992dfedbbbd8939987a6c1ba612d0381c6abbc9454e128`.
- Package carrying the repaired manifest: `0f18e62`; state update `931f5ad`.

This closes the two executable holds in the
[0.10 review](astra_protocol10_review_20261011.md). It freezes the procedure;
it does not declare calibration passed. Empirical execution remains subject
to the specified validation gates. The poor development power and the
risk-defined effect target remain unchanged.

## Independent repair checks

**Accounting: 20/20 checks passed.** The previous 970 accepted records plus
30 present, wholly failed T files without rows now produce 1,230/41,000 = 3%
failed datasets and a fit stop, while retaining the 1,000-trial denominator.
Missing rows without T files are conservative; absent/truncated/ragged T
files after successful rows retain `indet_malformed` and the logged outcome.
Failure flags and non-finite cells are combined. Verified sampling failures
remain in outcome denominators but are excluded from fit denominators.
Exactly 2% does not stop; greater than 2% stops gating blocks.

**Binding: 39/39 checks passed.** Manifest digest and chunk settings are checked
before reuse and collection. Missing T files cannot be silently skipped on
restart; duplicate and overlapping chunks are refused. Collection uses the
manifest's R. The empirical guard refuses a changed manifest, failed
validation, a different recorded runtime and a populated destination. A direct
collector-to-guard fixture retains O2/O3 when the power gate fails. Tiny
preflight fixtures reject changed sources, banks, stress files and runtime pins.

**Package continuity passed.** All scenarios, chunk IDs, seeds, beta_min, R,
K and budgets match the previously reviewed design. All 2,700 stress vectors
and library indices are identical. Twelve embedded source hashes match
`52779d0`; the 180 primary-shard hashes and metadata agree with the earlier
independent raw-bank audit. The library hash and effect JSON agree with the
earlier package. This review did not repeat bank hashing or scientific fits.

The repaired remote manifest is
`/data/fable/vortex/production_banks_20261010T081726Z/validation_manifest_v2.json`;
its hash matches the accepted digest. The same directory's unversioned
`validation_manifest.json` still holds the earlier `b2512dd2…` manifest.
The archived deep-server preflight records the accepted digest, 12 sources,
181 bank files, Python 3.12.3, R 4.6.1 and the required package pins.

## Operational handoff to Fable

**Fix PBS failure reporting before using the new wrapper.** An unchanged
`collect.pbs` fixture at `ede7451` returns exit 0 after an injected collector
exit 17 and creates an archive without a summary. It also ignores tar failure.
Preserve diagnostic packaging, but propagate collection/required-packaging
failures to the PBS exit status. This is an execution-wrapper correction
outside the accepted scientific source manifest; it does not reopen the freeze.

Fable retains ownership of Kunanyi access, staging, host qualification and
submission. The planned runtime must pass preflight on that host; validation
and the eventual empirical execution must use matching recorded runtimes.
PBS submission is not completed computation. No job was submitted in this review.

Small record corrections remain: label `package_inputs_sha256.txt` as the
earlier receipt and supply the current one; add BASE to the outdated launcher
example; describe preflight accurately. The effect JSON's hash and derived
settings are embedded in the manifest, but preflight does not read that
unused provenance input. These do not change the accepted procedure.

Preflight is a point-in-time check of the staged source, inputs and runtime.
Its receipt assumes those remain fixed; it is not continuous tamper detection.
Once-only protection applies to the specified empirical destination. Restart
checks T-file presence, while collection validates contents. These boundaries
are adequate for this declared run with immutable staging.

## Receipts

Runnable audit scripts and JSON receipts are in
[`analysis/astra/protocol10_repair_review/`](../analysis/astra/protocol10_repair_review/).
Accounting and binding checks use the existing dsipa-dev Python environment;
package and PBS checks need Python 3, Git and Bash. Fable's archived 25/25
pipeline receipt is retained as reported; this review executed the independent
59 checks above. No new population simulation, R fits, empirical T statistics
or p-values, remote mutation, or PBS job execution occurred.
