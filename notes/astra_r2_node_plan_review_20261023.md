# Round-2 node refill plan review — 23 October 2026

**Recommendation: accept the direction, with the requirements below.** This is
a review of the proposal in design §9f (board 2235 as relayed by the parent),
not approval of an executable: no node repair exists at reviewed HEAD
`461c115c308d301d228eaaa7497aab56ddb38ddd`. The current node SHA-256 is
`cafc0a4dae6b9490a522dda8991aadae34808d5ec8f3b43a9f41ec17d36193ec`; the bound
runner is `1e35b94ab3811cc0ddded21aeaa5258120500c9e60f02dd5a6ee0c9c89d50d75`.
Leave existing arrays and the bound runner unchanged. The node-only repair and
focused verification can proceed within the existing authority; this creates
no new decision for Barry. Review that actual repair before its first top-up.

## Required execution contract

1. **Refill exit 75 while useful allocation time remains; retain a separate
   finite budget for other failures.** Removing the current shared 20-exit cap
   addresses the observed retirement of slots. It must not turn unexpected
   errors into unlimited retries. Owner generation and unexpected-error count
   are different counters: an intervening exit 75 must not conceal repeated
   other errors or permit owner reuse.

2. **The activity predicate is this wave's queued tickets OR claims, with an
   explicit unknown/error result.** Both shared directories contain both waves;
   match the exact `WAVE_` prefix. Claims alone are insufficient: `run_ticket`
   moves a censored claim back into `queue` (runner lines 627–635), and planning
   publishes successors before removing the old claim. A slot can observe the
   old claim gone after new work became available. Do not treat failed, missing
   or unreadable directory scans as empty; retry with bounded delay and report
   persistent failure. After a pause, recheck both before retiring. These are
   capacity observations, not an authoritative assertion of wave completion.
   A grace recheck reduces transient observations without claiming an atomic
   snapshot of two NFS directories.

3. **Bound idle residence and polling.** Retaining idle slots while sibling
   slots still use the same allocation can recover capacity cheaply. Retaining
   every completely idle subjob merely because one remote wave claim remains
   can hold almost the entire array for the tail. For 300 × 8 CPUs, 48 hours
   of such waiting would allocate 115,200 CPU-h. Therefore use a finite,
   documented idle grace for a completely idle subjob, or otherwise demonstrate
   the chosen idle budget. Avoid full worker startups and directory/PBS scans
   independently in every idle slot on a short cycle. A nominal ten-second
   pause across 4,560 slots permits 456 retries per second before startup cost.
   A lightweight, rate-limited wave check with jitter and a measured startup
   count is sufficient; a scheduler framework is unnecessary. The old §9d
   claim that over-provisioning costs only minutes cannot simply carry over
   to the proposed global-claims waiting policy.

4. **Publish and confirm the death certificate before a replacement.** Keep
   `wait` before certification and the exact `{owner, host, pid, rc}` contents.
   A write/rename failure needs bounded retry and a diagnostic/nonzero exit if
   publication cannot be established. An ambiguous rename can be reconciled by
   reading the exact final certificate. Do not silently refill indefinitely
   after failed publication: the runner cannot reclaim a remote claim from an
   uncertified owner while its PBS subjob still runs. The current node ignores
   this failure (lines 28–30); the isolated test below reproduces it.

5. **A distinct owner for every child, including successful idle refills.** The
   existing per-node nonce plus a monotonically increasing per-slot generation
   is adequate if every launch advances the generation and a node rerun draws
   a fresh nonce. A separate random nonce on every refill is not necessary.
   Reusing the exit-0 owner's name is unsafe because claim recovery trusts a
   certificate matching that owner name without checking a PID. Certify only
   a child actually reaped; never overlap old and replacement children in one
   slot.

6. **One allocation deadline, checked before every launch and after every
   pause/probe/certificate retry.** Preserve `T0 + WALL_SECS - margin` for all
   children and the existing commit/cleanup allowance. Refilling must never
   reset it. Clip waits to remaining time and retain an explicit latest-launch
   cutoff. The current wrapper checks only before its ten-second sleep, so it
   can launch a child after that sleep crosses the deadline; this is a wrapper
   startup issue, not evidence that the bound worker computes past its deadline.

## Focused acceptance cases for the future diff

| Case | Required observation |
| --- | --- |
| More than 20 consecutive exit-75 children, then productive success | Replacement continues within time; every owner is distinct and has the correct prior certificate; no extra simultaneous child per slot. |
| Repeated non-75 errors interspersed with 75 and 0 | The declared finite unexpected-error policy still ends with a visible failure; generation numbers never reset. |
| Exit 0; queue-only, claims-only, neither, or only the other wave's files | Same-wave queued work refills; claims-only waits under the idle budget; readable empty wave retires; other-wave activity does not retain it. |
| Last claim requeued or successors published between idle observations | Queued work is detected on the post-pause check; no claims-only false-idle decision. |
| Wave scan raises ESTALE/EIO or cannot read a directory | Classified as unknown, retried within bounds, and never logged as wave complete. |
| Certificate write/rename fails; rename applied but reports failure | No silent replacement without verified publication; exact final certificate reconciles the applied case; persistent failure is visible. |
| Same PBS job rerun; repeated exit-0 refills; recycled child PID | Owner identities remain distinct; an earlier certificate never certifies the new child. |
| Deadline already passed, crossed in sleep, or reached during a scan/certificate retry | No subsequent child launch; all children receive the same original absolute deadline. |
| Many idle slots, one remote long claim, no queue | Whole-subjob idle budget is respected; retry/startup/metadata rates are recorded and remain bounded. |
| Labelled top-up submitted with stub PBS | Existing settings-digest binding, distinct TAG/journal, reservation accounting and afterany collector dependency remain intact; no change to runner, metric, settings or shard streams. |

## Executed baseline and resource boundary

[`check_current_node.py`](../analysis/astra/r2_node_plan_review/check_current_node.py)
ran the actual current Bash wrapper with one slot and isolated worker, clock,
sleep and certificate-rename stubs. Its
[`current_node_evidence.json`](../analysis/astra/r2_node_plan_review/current_node_evidence.json)
records six cases: both 75 and non-75 stop after 20 launches; exit 0 immediately
retires despite a same-wave claim; failed certificate renames permit a second
child and an overall success with no certificates; and the wrapper launches
after an elapsed or sleep-crossed deadline. These establish the current
baseline and discriminate the proposed repair; they do not test nonexistent
replacement code or exercise scientific computation. No PBS or remote mutation
was performed.

The recorded 7,000-CPU request limit includes queued and running requests.
Starting the already queued W2 subjobs therefore frees no request capacity.
If all 570 original W2 subjobs and their collector remain, and W1 plus its
collector have ended, at most 304 additional eight-CPU subjobs plus their new
one-CPU collector fit in 7,000 CPUs (assuming no other requests). A 300-subjob
top-up would bring that total to 6,962. This is arithmetic from the recorded
policy, not a live scheduler check: use current PBS state and all user requests
before submission. W1 email alone does not establish released capacity or a
valid final collection. Reconcile terminal jobs and the reservation ledger;
each top-up collector remains a snapshot if another array of its wave runs.

Astra (Codex), 2026-10-23 10:56:45 AEDT (+1100), Australia/Hobart.
