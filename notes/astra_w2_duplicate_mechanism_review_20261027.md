# W2 duplicate-shard mechanism review

**Recommendation: allow the already-running W1/W2 topup-b arrays to finish,
then archive and collect them strictly; hold W2 topup c.** The evidence diagnoses
overlapping execution of the same range. The proposed directory-listing
explanation is the strongest code-supported cause, and a focused reproduction
confirms its entire causal chain, but the historical triggering read was not
observed. A repaired runner needs authoritative per-range transitions, not
another directory-listing check.

## MAJOR — planning can republish a claimed range

`plan()` reconciles each unfinished range by building `live` from separate
`os.listdir` results for the global `queue/` and `claimed/` directories
(`p3_stage1b.py`, lines 416–459). If those reads omit the relevant entry, it
creates a new ticket with `open(..., "w")`; another worker can claim that ticket
while the first claim still exists.

The local reproduction uses the exact bound runner
`1e35b94ab3811cc0ddded21aeaa5258120500c9e60f02dd5a6ee0c9c89d50d75`.
It calls unchanged `plan()` through the actual `held()` setting-lock contract
while injecting one omitted `claimed/` listing. The planner republishes the
range, and unchanged `claim()` produces two claim entries for it. Two concurrent
calls to the unchanged shard engine both complete, append the same deterministic
record, and leave a 318-byte journal against a 159-byte checkpoint. The two
journal halves are byte-identical, and the strict verifier rejects the result
with `journal length differs from its checkpoint`. This reproduces the proposed
mechanism without simulating the expensive scientific work.

Run from the repository root:

```bash
uv run --python 3.12 --with numpy==1.26.4 --with scipy==1.11.4 \
  python analysis/astra/w2_duplicate_review_20261027/reproduce_duplicate_path.py
```

The result is saved in
`analysis/astra/w2_duplicate_review_20261027/reproduction_result.json`.

This establishes sufficiency, not the historical trigger. Ordinary
interleaving of the implemented operations does not expose a queue-to-claim
gap: `claim()`, `recover_stale()` and `plan()` make their transitions under the
same setting lock. `adopt()` selects only a claim whose exact owner equals the
current worker. Recovery requires positive process-death evidence before
requeueing. I found no second internal path that republishes an existing range.
Plausible alternatives are an external/manual transition or false death
evidence from PBS; the saved evidence supports neither. “An NFS listing omitted
the claim” should therefore remain a well-supported hypothesis, not an observed
fact.

The saved census proves two claim pathnames for each of eight ranges, not that
both named owners were alive when it ran: it did not test certificates, PIDs or
PBS state. It includes two W1 and six W2 ranges, so the defect is not confined
to W2-a. The journal evidence supplies the stronger temporal inference. A
sequential restart verifies and truncates an uncommitted tail before resuming,
and refuses a terminal checkpoint with extra bytes (`p2_stage1a.py`, lines
270–301). The production size ratios and terminal extra tails are compatible
with overlapping writers, but sizes alone do not establish that the production
journal halves contain identical batches. In particular, s02093 has a COMPLETE
marker but a live journal longer than its terminal checkpoint, consistent with
one worker marking completion while another appended.

## Scientific and data-integrity consequence

The strict collector rejected all 13 settings whose saved journals and
checkpoints disagreed. The separately verified W2-a archive's 183 libraries and
366,000 retained records passed digest, schema, identity order, range and
selection checks. This mechanism review did not replay their raw journals or
numerically regenerate their records. Concurrent duplicate execution could in
principle leave a coherent valid-looking deterministic output and only waste
compute, so these checks establish rejection of malformed manifestations rather
than detecting every duplicated execution.

That protection converts corruption into informative computational missingness.
FAILED or invalid settings must be rerun or recovered under a verified contract.
Any later fit restricted to settings that happened to complete would select on
computational difficulty and violate the declared denominators. The snapshot's
183 COMPLETE rows are not a scientific sample and support no calibration or
empirical inference.

## Required repair contract

The setting directory should hold the authoritative state of every range,
updated under its setting lock. At minimum, the record must bind range, state
(`queued`, `claimed`, terminal), exact owner generation, scientific binding and
transition generation. Global queue entries may remain selection hints, but a
claimant must lock the setting and make a conditional
`queued -> claimed(owner)` transition; stale or duplicated hints do nothing.
Completion must condition on the same owner generation. Recovery may make
`claimed(owner) -> queued` only after positive death evidence for that owner.

The repair must define crash reconciliation for every ordering between the
authoritative transition and creating, renaming or deleting a queue hint. A
second directory-based “does a ticket exist?” test retains the defect. Focused
acceptance cases should:

1. omit a live claim from every global-directory listing and prove planning
   creates no ticket;
2. feed stale and duplicate queue hints to concurrent claimants and prove at
   most one authoritative owner;
3. interrupt each queued/claimed/completed/requeued transition on either side
   of its hint update, then reconcile without duplicate execution or lost work;
4. retain the bound runner as a negative control that fails case 1; and
5. rerun the lock, death-certificate, journal, determinism and strict-collection
   fixtures under Bash 4.2 and the bound Python runtime.

## Preserve valid work without another defective dispatch

Already-running topup b should finish. Cancellation cannot repair affected
shards and would reduce the number of complete libraries obtained from work
already in flight. Its terminal collections must reject every mismatch and
report invalid settings, duplicate claim pathnames and owner-liveness evidence.

Do not submit topup c yet. It would add concurrency and directory churn to a
known-defective runner while duplicate claim pathnames remain in both waves.
Adding a `WAVES` dispatcher option does not alter this risk.

After b finishes, seal the old run and preserve its binding. A one-time import
into the repaired binding is technically preferable to knowingly extending the
defective binding: accept only shards whose complete committed bytes, checkpoint,
range identity, old binding and stream identity all verify; copy only the
committed prefix; record source and destination digests; reject every invalid,
FAILED, ambiguous or multiply owned range; then plan the remainder under the
new state machine. Because the scheduler repair does not change the deterministic
scientific stream, such an importer can preserve valid incomplete prefixes, but
it is a new data-recovery contract and needs independent adversarial review plus
an old-versus-imported byte comparison. If that recovery cannot be made exact,
rerun incomplete/FAILED/invalid settings from batch 0 under the fresh binding.

If the repaired state machine imports old partial shards, independently audit
the importer before dispatch because it crosses the binding boundary and an
error could silently compromise the remaining campaign.
