# Round-2 top-up integration review — 25 October 2026

**The proposed top-ups fit the existing submission, binding and accounting
contracts. No new integration blocker was found.** This accepts the integration
component. **Overall top-up clearance remains held:** the independent node
review reproduced an alternating empty/unknown wave-scan path that bypasses
the node's idle/deadline checks. Repair and recheck that path before installing
the node for new arrays. This review does not claim that installation or
submission has occurred. No new scientific or resource decision is required
from Barry.

Reviewed HEAD: `805f0079f5eb8157b351ee31c04a1ab91f3ca3f7`. The node is now
`00ed12fb3aa3a8224ea99efa6377755821efb75e46e6786a5a0fdfde34ca8457`.
The runner (`1e35b94a…`), submitter (`e8cb24aa…`) and collector shell
(`ab8c1aa2…`) are unchanged from the 23 October review. Full hashes and the
executed checks are in
[`evidence.json`](../analysis/astra/r2_topup_review_20261025/evidence.json).

## Binding and installation

Use the existing **full** `p3_settings_r2.json`, digest
`248f9c7de660dcac19a3e6806fbf97bc512aca9cff42abd54e5fd0f4ee3bbd73`, and
`OUTDIR=run2`. The full file has 12,119 settings, including all 4,847 round-2
W1 settings. Do not generate a 48-row settings subset, rebind the runner or
seed a new directory: the remaining 48 settings already have compatible
shards, tickets and claims in `run2`. Terminal settings are retained in the
collection inventory while workers deal with the remaining queue/claims.

Install only the reviewed node script for future submissions and record its
installed/submitted hash. Its new logic is self-contained: it sources the
existing `env.sh` and invokes the existing bound `p3_stage1b.py`; it requires
no new Python helper or payload. `check()` and `binding()` (runner lines
158–169) bind the scientific sources, metric, runtime and settings, not the
node shell. Preserve those hashes and the existing settings bytes. Existing
PBS submissions retain their submitted node script; no change to those jobs
is needed.

The submitter passes `VBASE`, `SETTINGS`, `OUTDIR`, `WAVE`, `TAG`, `JOBCPUS=8`
and `WALL_SECS=172800` to the node, and requests eight CPUs, 10 GB memory and
48 hours. With node defaults, the worker deadline is 47.5 hours after node
start and the final launch cutoff is 47 h 20 min. The default poll is 300 s
plus up to 30 s jitter; the whole-subjob idle budget is nominally 1,800 s.
These defaults are internal to the node; no extra `qsub -v` entry is needed.
The node review determines whether all branches enforce them correctly.

## Shape, live requests and reservation history

Forty-eight settings at the bound maximum of 28 in-flight shards give an
upper envelope of 1,344 simultaneous W1 shard workers: 168 eight-CPU
subjobs. The proposed 170 subjobs provide 1,360 slots, only 16 above that
envelope. This is a defensible approximate shape, not a claim that all 48
settings will need or obtain 28 shards throughout the tail.

Before the next reservation, append one release of `s1b_22b89261_a` under
the campaign ledger lock, citing terminal W1 array `857922[]` and collector
`857923`. The saved 25 October collection receipt reports both finished and
collector exit 0. Reconcile the current ledger to avoid duplicate release;
retain the original reserve line as history. The release is not a deduction
from measured spending. Keep **all 218,888 CPU-h** of the original W2
reservation active until its whole array and collector end; 191 expired
subjobs do not authorise a partial ledger release.

For a 48-hour W1 top-up, the reservation is
`170 × 8 × 48 + 8 = 65,288 CPU-h`, including its collector. A same-label
resume records no new reservation or PBS submission. A new top-up label
creates its own reservation and journal.

Size W2 from current PBS resource requests across all Barry's jobs, including
held collectors and newly queued top-ups. `max_queued_res` covers queued and
running requests; moving a job from queued to running does not free that
budget ([PBS Reference Guide, server limit attributes](https://help.altair.com/2024.1.0/PBS%20Professional/PBSReferenceGuide2024.1.pdf)).
If the saved 379 running / 191 expired / zero queued W2 snapshot is still
the applicable resource count, and there are no other requests, then adding
170 W1 subjobs leaves room for **325 W2 subjobs**, counting three collectors:
`(379 + 170 + 325) × 8 + 3 = 6,995` CPUs. This is an illustrative calculation,
not a dispatch instruction or a fresh scheduler observation. Use the actual
server accounting immediately before submission.

That example adds 124,808 W2 CPU-h and leaves 408,984 CPU-h reserved in total.
The fixture does not qualify the live ledger: reconcile that ledger and the
bound accounting rules at submission. The scientific per-setting proposal
cap is unchanged. The new idle policy can retain an
entirely idle allocation for its grace period: 170 × 8 CPUs for 30 minutes
would be 680 allocated CPU-h, before polling overshoot. Report that as
allocation time, not useful sampler CPU or a change to the scientific cap.

## Collector provenance and archive preservation

Submit with an unused label such as `topup b`, producing `W1_b` and `W2_b`
in their respective waves. The submitter binds the label into run identity,
PBS variables, logs and journal. The collector writes `collect_W1_b.json`,
`collect_W1_b.log`, `pack_W1_b.txt` and `W1_b.tar.gz` with its checksum. It
does **not** overwrite the original `W1.tar.gz`, whose recorded digest is
`c12e5378589c010f6e4b01d1bbb3cbd19d4d61ca4675aced79269e1e4f0624cc`.
The prior archive should remain preserved under that digest; a manual
recollection with `TAG=W1` would overwrite that snapshot and should use a
distinct tag instead. No archive rescue is needed for the normal labelled
top-up path tested here.

Each collector depends on its own array only. If another array of the same
wave is still running, its result remains a snapshot; a final authoritative
wave collection follows all arrays of that wave. W1 and W2 use separate
settings under the full shared binding, so W2 activity does not prevent a
quiescent W1 collection. The `lib/` directory is shared; archive files and
their hashes preserve the historical snapshot independently of later library
assembly. Archive-content verification belongs to the parent collection review.

## Verification performed

[`check_topup.py`](../analysis/astra/r2_topup_review_20261025/check_topup.py)
ran actual submission and collector shells in temporary directories, with
PBS and scientific worker stubs. It executed the actual reservation functions
but stubbed native preflight validation. The fixture settings are synthetic;
the parent review checks the real archive/settings identity.

- W1 170-job and illustrative W2 325-job top-ups each created one array and
  one collector, with the expected ranges, resources, full settings filename,
  `run2`, wave, tag, deadline input and individual afterany dependency.
- A labelled W1 resume made no additional submission or reservation.
- A replacement subset and a new output directory were refused before PBS;
  the full settings bytes were unchanged, and no seed command ran.
- The ledger retained the original W2 reservation, released only original W1,
  and added the two expected top-up reservations.
- The actual tagged collector shell produced a checksum-valid `W1_b` archive
  and preserved prior W1 archive, checksum, summary, log and pack-list bytes.
  Its scientific collector was stubbed solely to isolate naming/packaging.

The unchanged twelve-case submitter suite was not repeated: these targeted
checks address the proposed shapes and integration. No production source,
settings, archive, ledger or PBS job was modified.

Astra (Codex), 2026-10-25 12:03:33 AEDT (+1100), Australia/Hobart.
