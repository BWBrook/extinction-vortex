# W2 first-array collection: integrity and accounting review

**Scope.** Read-only review of commit `35816f3`, the saved W2 collection summary
`analysis/fable/calibration/v2_dev/p3/w2_a_collect_W2.json`, its collection
receipt, and the bound runner/collector `p3_stage1b.py` (`1e35b94a…`). I checked
the collection and recovery code, recomputed the saved counts and CPU fields,
and ran four synthetic journal cases against the actual `verified()` function.
I did not inspect the live run directory, reproduce the duplicate-claim
mechanism, or regenerate numerical streams. The local audit is in
`analysis/astra/w2_collection_review_20261027/`.

## Recommendation

**APPROVE WITH CHANGES.** The observed malformed shards fail closed, and the
183 archived libraries are structurally usable as an interim snapshot. Keep
the current W1/W2 top-up-b arrays running, then perform strict end-of-wave
collections for both waves. Do not call the W2 collection successful or use its
current availability for scientific inference. Hold further top-ups while the
duplicate-ownership mechanism and repaired state model are reviewed. Replace
the categorical "integrity holds" claim with the narrower evidence below.
Before Stage 1c, perform an authoritative post-array collection and exact
across-round reconciliation under a repaired runner.

## Evidence boundary — duplicate record identities are excluded

The collector validates every declared shard before using any of them
(`p3_stage1b.py:746-768`). A terminal shard must have exactly the checkpointed
journal length (`:712-717`), and records must have unique, strictly increasing
identities within the committed batch range (`:677-695`). The global prefix is
also strictly ordered (`:769-790`). These checks reject the observed doubled
journals and prevent two copies of the same `(batch, proposal_in_batch)` from
being assembled.

The synthetic cases on the bound runner confirm the boundary:

- a terminal journal containing a second uncommitted copy is rejected for
  excess length;
- a journal whose checkpoint commits both copies is rejected for duplicate or
  decreasing identities;
- a nonterminal journal may contain an extra duplicate tail, but `verified()`
  returns only the checkpointed prefix. Such a shard is not part of the useful
  prefix, because `prefix()` admits only `complete` shards (`:375-395`), and
  normal recovery replaces the file with the committed prefix
  (`p2_stage1a.py:247-267, 279-301`).

This establishes that **repeated record identities were excluded from the
saved libraries**. There is no evidence that any archived record has the wrong
numerical value. The collector checks schema, ordering, bounds and selection S;
it does not regenerate a batch from its seed. A deliberately fabricated,
self-consistent checkpoint and structurally valid journal passes `verified()`,
which demonstrates only the boundary of the collection proof. It is not a
reachable counterexample from the observed concurrency fault. Under the bound
same-code, same-runtime execution, two workers on one range should emit the
same bytes.

Recommended wording: "All 13 observed mismatches were rejected. The 183 saved
libraries contain 2,000 unique, ordered identities and passed binding, digest,
schema, range, selection and K-th-hit checks. No numerical stream regeneration
was performed." This preserves the meaningful guarantee without turning
structural validation into a numerical replay claim.

## MAJOR — the CPU totals omit all work in the 13 invalid settings

The saved arithmetic is internally exact: 143,903.7256 useful CPU-h and
98,520.2635 outside-prefix CPU-h. Of the latter, 72,689.0202 h (73.78%) is
attached to settings currently marked incomplete and is **potentially** reusable
if later shards close every preceding hole and pass verification. The remaining
accounted outside-prefix work is 25,831.2433 h in COMPLETE libraries and is not
part of their first-K scientific output.

Those figures are lower bounds on execution, not campaign cost. `attempt()`
reduces any invalid setting to identity plus `status="invalid"`
(`p3_stage1b.py:799-815`), discarding its useful/discarded CPU fields. The
summary sums missing fields as zero (`:816-821`). It also cannot count duplicate
workers whose checkpoint lost a race. Thus none of the CPU in 12 invalid primary
settings and one invalid check setting, nor duplicated execution hidden behind
one surviving checkpoint, appears in either total. Change "98.5k outside-prefix
CPU-h" to "98.5k accounted outside-prefix CPU-h among valid rows; invalid and
duplicate execution is unmeasured."

## MINOR — two saved interpretations exceed their evidence

The receipt's 13-setting recheck shows eight `FAILED` markers, four settings
with no terminal marker, and one `COMPLETE` marker. The design note and board
message say nine settings had `FAILED` markers. Use 8/4/1 unless a later live
probe, clearly dated, establishes a change.

Likewise, a journal file exactly twice the checkpointed byte length is strong
evidence of concurrent duplicate appends, but file sizes alone do not show that
the two byte blocks are identical or that "the same batches were written
twice." That conclusion needs a raw-byte half comparison. The duplicate claim
names and repeated 2× lengths support the mechanism without this stronger
claim.

## Scientific denominator and recovery contract

The saved row inventory preserves the fixed design: 7,200 primary settings =
9 populations × 4 scenarios × 200 outer datasets, plus 72 check settings =
9 × 4 × 2. The interim availability is nonrepresentative: only 182 primary and
one check library are COMPLETE; no outer dataset has all nine primary
population libraries, and the maximum is five. This pattern can reflect
scheduling, progress and setting-specific rates; the snapshot does not identify
their relative contributions. Complete-case inference would therefore be
invalid. The scientific denominator remains 200 per population-scenario cell,
with outcome status retained; the 72 checks remain separate.

The later-round contract should be executable:

1. Wait until every array using the old W2 binding has ended, then collect once
   authoritatively. A saved snapshot while workers run is evidence about that
   instant, not the round result (`p3_stage1b.py:724-728`).
2. The conservative cleared fallback is to select **exactly** every `invalid`,
   `FAILED`, or still-`incomplete` setting from that collection. Preserve every
   scientific setting field and stream identity; change only the
   runner/settings binding and run directory. Start those settings at batch 0.
   Treat `COMPLETE` and `CAPPED` as old-round terminal outcomes, subject to
   archive verification. A possible lower-cost alternative is an exact,
   one-time audited import of verified partial shards into the fresh binding.
   That would need an explicit source/target manifest, byte digests, coverage
   proof and import receipt; it is not implemented or cleared, and in-place
   rebinding remains unacceptable.
3. Reconcile old and recovery rounds against the full 7,272-row inventory:
   exact bindings and row identities; no duplicate rows or archive member names;
   one error per invalid row; recovery settings exactly equal the old-round
   nonterminal/invalid complement; disjoint terminal sets; and union of terminal
   plus remaining rows exactly equal the inventory. Verify every COMPLETE
   library's digest, 2,000 unique ordered records, path length, selection S and
   K-th batch.
4. Compare clean old/new journals byte-for-byte over common committed coverage
   wherever the old journal remains verifiable. Invalid old journals cannot
   support that comparison. For their recovered outputs, retain the limitation
   or add targeted seed-based serial regeneration before fitting.
5. Apply the same final-collection/recovery rule to still-active W1 top-up work,
   because the census found two W1 range names duplicated as well as six W2
   names. The census establishes duplicate claim names, not that both owners
   were alive. It does not retroactively overturn the already audited W1 archive.

This recovery makes missingness an execution state rather than a changed
scientific sample and prevents the interim availability pattern from defining
the fitted dataset.

## Verification

Executed with Python 3.12, NumPy 1.26.4 and SciPy 1.11.4:

```text
uv run --offline --python 3.12 --with numpy==1.26.4 --with scipy==1.11.4 \
  python analysis/astra/w2_collection_review_20261027/audit_w2_snapshot.py
```

The audit asserts all saved counts and totals, exact 200/2 cell inventories,
one-to-one invalid/error directories, and the four journal guard cases. Results
are in `audit_w2_snapshot.json`.

## Residual risk

The observed archive can support continuation planning, not validation or
empirical inference. The material unresolved issue is duplicate ownership while
the shared run remains writable: further execution can waste CPU, append beyond
checkpoints and create additional invalid settings. Finish the already-running
arrays, collect both waves strictly, and require the repaired state model plus
an exact recovery/reconciliation contract before another top-up.
