# Round-3 authoritative-state invariant review — 27 October 2026

## Decision

**No blocker in the assigned ownership-safety scope.** At runner
`c56d0af653f1d7ecd525cacc5b6a191d8a1cadf398b601fc4327f3f6da34983b`, a stale exact read can delay a setting, but I
found no path by which it admits a second writer, skips an execution generation, overwrites an execution end, or creates
overlapping ranges.

The reason is structural: every range start and execution generation has one immutable pathname, and the transition
that can authorise new work is an exclusive hard-link create at that pathname. A stale negative therefore collides with
the existing record and fails closed. Clear the state-invariant component without changing the protocol.

I found one **MINOR evidence-scope defect**, not an ownership failure: the collector's off-chain-record check depends on
directory-listing completeness. The design should say that the collector rejects *visible* off-chain records; absence
of off-chain records follows from the construction invariant rather than from this listing check.

## Invariant and evidence

| Property or fault | Mechanism and observed result |
|---|---|
| Complete immutable create | `create()` writes and `fsync`s a temporary JSON record, then hard-links it to the permanent path (`p3_stage1b.py:383–398`). |
| Lost link reply, token visible | Injected `os.link()` success followed by `FileExistsError`; token readback reconciled it as success and exactly one complete record remained. |
| Lost link reply plus stale token readback | The link existed but injected `rec()` returned `None`; `create()` returned false. The permanent record remained and the caller could not acquire duplicate authority. |
| Non-overlapping range chain | `ranges()` follows exact `r/<a>` records from the pilot end (`:409–420`); `plan()` extends only the observed end and stops when exclusive create collides (`:512–576`). |
| Stale range head | Hid the first record of a two-range chain from `plan()`. Its same-path create collided; both records were unchanged and no overlapping range appeared. |
| One live execution per range | `execution()` walks exact `x/<a>.<k>` names (`:423–432`); `take()` creates only the next exact generation and converts collision to `Behind` (`:610–643`). |
| Stale execution 0 | Hid a live `x/<a>.0` from `take()`. Result: `Behind`; execution 0 remained the only start. |
| Stale latest execution | Hid live execution 1 after execution 0 had ended dead. Result: `Behind`; execution 2 was not created. |
| Stale immutable end | Hid a complete execution-0 end while its owner had a death certificate. Result: `Behind`; the completion was not overwritten and execution 1 was not created. |
| Lost reply during `take()` | Injected success then `EEXIST` for the new execution start. Token reconciliation returned execution 0 and left one start record. |
| Queue/claim omissions | Queue and claim files are discovery hints only. All contenders must resolve the same authoritative `r/` and `x/` paths under the setting lock. |

The focused harness is
`analysis/astra/r3_state_review_20261027/adversarial_state_checks.py`; its compact receipt is
`analysis/astra/r3_state_review_20261027/adversarial_state_checks.json`. It ran with:

```text
uv run --offline --python 3.12 --with numpy==1.26.4 --with scipy==1.11.4 \
  python analysis/astra/r3_state_review_20261027/adversarial_state_checks.py
```

Exit code was 0 and all seven safety expectations held. These are local POSIX fault injections against the exact runner
hash above, not an NFS server-conformance test.

The existing negative control is discriminating. Bound runner
`1e35b94ab3811cc0ddded21aeaa5258120500c9e60f02dd5a6ee0c9c89d50d75` treats directory listings as authoritative; an
omitted entry republishes a live range, owner B claims beside owner A, and the two workers produce a 318-byte journal
against a 159-byte checkpoint. The candidate ownership control creates one execution record and admits no second owner,
including when every listing is omitted
(`analysis/fable/calibration/v2_dev/p3/r3_ownership_control.json`).

## MINOR: off-chain collector check is conditional

At `p3_stage1b.py:938–953`, the collector lists `r/` and `x/`, walks the exact chains, then rejects listed entries not
reached by those walks. An off-chain record omitted from the listing is absent from both compared sets and is therefore
not rejected.

The focused reproduction created `r/000000010` without `r/000000000`, injected empty directory listings, and ran the
actual collector. It returned `collection_ok=true`, reported one incomplete setting and `ranges=0`, while the off-chain
record still existed. Thus the statement in `notes/vortex_stage1b_design_20261016.md:859–863` that the collector
cross-checks that no record lies off-chain is too strong.

This is not a reproduced normal construction path: current writers can create only the exact observed chain end, and
the exclusive create prevents two records at the same start. The least disruptive remedy is to describe the collector
as rejecting *visible* off-chain records. If an independent absence proof is required, it needs a quiescent server-side
inventory or a separately committed manifest; repeated client listings do not eliminate an adversarial omission.

## Scope limits

- Reviewed: authoritative `r/` range chain, immutable numbered `x/` starts and ends, lost hard-link reply handling,
  stale exact reads, and `plan()`/`take()` safety.
- Assumed: same-destination hard-link creation is exclusive and permanent records are not replaced or removed. The
  package records that `/u` is NFS 4.1 and a second `os.link` reports `EEXIST`
  (`notes/vortex_stage1b_design_20261016.md:922–923`).
- Not reviewed here: long-worker lifecycle and predecessor recovery, lock reclamation, dispatch, scientific sampling,
  library-content validity, or whether an already-issued filesystem RPC from a dead process can land after a successor
  starts.
- No production file was changed. The parent is running the broad native fixture baseline separately; this review did
  not duplicate it.
