# Round-3 stage and inventory closure — 29 October 2026

**Clear the assigned stage-identity and selection contracts.** No blocker was
found in these components at `dbb1b850c83ee47bedf5de3f74a61c42a8b67a4b`.
This does not clear worker recovery or capacity accounting, which have separate
reviews.

## Stage identity

Two isolated builds from commit `8be1b4e` produced exactly:

```text
53603d427f7f5313fc5e100649ea186770d712b52601ef935cfc15611872b241
```

The tar's manifest has SHA-256
`ccc056511cbb7b49afbd2cb4d6ad173b39419d289309dc731cd716b907f7c8c9`.
All ten manifest entries match their archived bytes and the current review
checkout, including runner `e261befa4cae08507c133af787f3f92ee283228c7dc5163076931767adf69894`
and the new capacity helper.

The actual dispatcher requires the external `STAGE_SHA`, checks the tar digest,
compares the extracted manifest with the tar's own manifest, then checks every
file. Focused local execution gave:

| Case | Result |
|---|---|
| Correct stage; all eight old jobs F | Verification and installation passed; deliberately stopped at environment loading |
| Changed runner, unchanged manifest | Refused before installation and before any PBS query |
| Changed tar bytes | Refused before installation and before any PBS query |
| Changed runner and matching rewritten extracted manifest | Refused before installation and before any PBS query |
| Correct stage; first old job unfinished | Refused before installation |

The positive case deliberately exits 77 from a stub `env.sh` after reaching
`== round-3 settings`. That tests stage verification and installation without
starting preflight, seeding, submissions or simulation. The four negative cases
leave the installed sentinel runner unchanged. PBS queries are local stubs.

This closes the previous procedural identity qualification. Continue supplying
the independently recorded stage digest at launch; an internal manifest alone
does not identify a reviewed artifact.

## Final summaries and recovery selection

The exact embedded Python gate was executed against the final W1/W2 summaries
and the bound round-2 settings file
`248f9c7de660dcac19a3e6806fbf97bc512aca9cff42abd54e5fd0f4ee3bbd73`.
It confirms complete, unique wave inventories; matching identities and bindings;
status/count consistency; and one-to-one invalid/error mapping.

| Wave | COMPLETE | CAPPED | Incomplete | Invalid | Selected |
|---|---:|---:|---:|---:|---:|
| W1 | 4,820 | 9 | 15 | 3 | 18 |
| W2 | 355 | 0 | 6,901 | 16 | 6,917 |

The **6,935** selected rows are exactly those classified incomplete, invalid or
FAILED. A synthetic conversion of one incomplete W2 row to FAILED, with its
counts updated consistently, remains selected. Separate wrong-digest,
invalid/error-mismatch and changed-identity cases are refused before selection
files are written.

Running the actual candidate's `select` command yields:

```text
8c46667e4ab9e8a8bd03911eda81f9de072df25f1f40cfbb953c4108965cb3b9
```

Every selected setting row is unchanged and stays in source order. The only
changed top-level fields are `settings`, `runner_sha256`,
`derived_from_sha256` and the explanatory `stage` label. This verifies the
predicted binding and scientific-field preservation, not the quality of the
underlying libraries or any fitted inference.

## Transport and evidence limits

The `tpac.sh` delta now invokes the existing Nectar SSH/SCP helpers from WSL
with the `kunanyi` alias, consistent with the 29 October access guidance. Its
helper arguments match the current implementation and `bash -n` passes. No
credential file was opened, no live authentication was attempted, and no
network route was changed.

Reproduction from the repository root:

```sh
python3 analysis/astra/r3_stage_inventory_closure_20261029/check_stage_inventory.py \
  /path/to/bound/p3_settings_r2.json
```

The harness checks the settings digest before use. Its captured receipt is
`analysis/astra/r3_stage_inventory_closure_20261029/stage_inventory_checks.json`.
It preserves production source and old receipts. It does not repeat the parent
archive audit, native runner fixtures, raw-smoke replay or capacity review.
