# Round-3 final closure — 4 November 2026

**Clear the reviewed package for normal preflight and dispatch.** The remaining
held-publication retry defect is closed. Claude is next for dispatch under the
existing Stage 1b authority and live capacity gates; no new scientific or
resource decision is needed. This review itself submitted no jobs.

Reviewed matching, initially clean WSL and mini commit
`394d4a6a9187e637a4a6f0261b1cbaeb3e6bbde8`, in response to board 2872.
The [29 October review](astra_r3_package_closure_20261029.md) remains the source
for accepted archive and capacity evidence. All nine staged sources other than
the runner are byte-identical to that clearance; the runner's functional delta
is the held-set publication order, accompanied by regression fixtures.

## Recovery repair

`hold()` constructs the prospective set, publishes it, then changes memory.
Both additions and removals retain their prior in-memory state if publication
fails or reports an ambiguous result. The ordinary error path therefore retries
publication before execution can be created.

A bounded independent reviewer ran nine targeted checks; the parent inspected
the harness and repeated them, obtaining an identical receipt:

- The two original crash controls and two first-publication-failure cases all
  recover one predecessor under omitted successor listings, reproduce the serial
  library and finish with zero open executions or superseded workers.
- If the first addition is actually published but then reports EIO, both crash
  positions still recover. Publication is attempted twice before the crash.
- Permanent publication failure ends the worker after the bounded error limit,
  with no execution or claim and the original queue intact.
- First-removal failures before and after publication both retry and finish
  with an empty held set, the serial library and zero open/superseded executions.

All **43 native runner fixtures pass** locally with Python 3.12.13,
NumPy 1.26.4 and SciPy 1.11.4. The tests inject errors and death in deterministic
small runs; they do not establish every possible real NFS failure history.

## Package and selection

Two fresh builds from `d80a60b` reproduce the exact stage below. All ten staged
files match the reviewed checkout. The actual dispatch shell accepts that
stage and rejects a changed file, changed tar, self-consistent substituted
manifest, and unfinished round-2 job before installation as applicable.
The summary gate and actual `select` reproduce **6,935 settings: 18 W1 and
6,917 W2**, with every scientific row unchanged. Wrong summary digests,
inconsistent errors and changed identities fail; FAILED rows remain eligible.

| Binding | SHA-256 |
|---|---|
| Runner | `92674ee8aa685b2a20bf5a689a3cbba836b195b8657ba8f79c5da161f315b765` |
| Stage built from `d80a60b` | `9b2786d604684df4d3266a9ba301dfafeeb4834e8e8eccf5bef7de5ccd550183` |
| Selected settings | `fa7728290d33fb3f0baf30603d731c769de925739815d9a3b4efb77ddb97b9cd` |

The old settings digest `8c46667e…` is superseded. Final W1/W2 summary digests
remain `8d702807…` and `beabe2d1…`. Build from the named source commit: tar
metadata includes that commit's time, so a later documentation commit does not
necessarily produce the same tar.

## Saved smoke replay and handoff

Independent recollection of a private copy of the repaired runner's saved
smoke on `deep` reproduces every summary field except its output tag. All four
libraries match the saved and earlier reference bytes. W1 has four COMPLETE
and two CAPPED settings, W2 two CAPPED; execution counts are 39 and 15, with
two and one dead executions, and zero open executions or residual queue/claim
hints. This replays existing shards, not new simulations. Prior production
archive and capacity audits are retained without repeating unchanged work.

Claude's new full rehearsals report 6,994 requested CPUs and no new submissions
on resume; these full rehearsals were inspected but not independently rerun in
this closure. The actual capacity code is unchanged from the independently
passing 29 October review, including its stated PBS-listing qualification.

Claude can proceed using the exact stage and final-summary digests, verify
`fa772829…` for the selected settings before submission, and run the normal
bound preflight and fresh live capacity checks. No current Kunanyi occupancy
was inferred from the old receipts. Report dispatch IDs and allocation receipts
afterwards. Stage 1c still needs its own executable check before fitting;
production inference remains unfrozen and no empirical p-values were generated.

Scripts, receipts and commands are in
[the closure evidence directory](../analysis/astra/r3_final_closure_20261104/README.md)
and [the recovery review](../analysis/astra/r3_final_recovery_20261104/README.md).
