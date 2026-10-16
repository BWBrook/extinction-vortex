# Astra Stage 1b scheduler repair review

17 October 2026, 00:34 AEDT (Australia/Hobart). Target:
`d801012d2859a69ef076bfa529b4bfba1fbd658a`, changes since `e442f59`.

**Recommendation: hold W1 until two narrow reservation-ledger defects are
fixed.** The proposed first W1 allocation remains correctly calculated at
199,688 CPU-h. Wave isolation is repaired, and a straightforward second output
directory is now refused. However, ordinary recovery paths can still accept
allocations beyond the approved W1 ceiling. These are executable accounting
failures, not objections to the scientific sampling design.

Scope: `s1b_submit.sh`, its fixtures, `s1b_node.pbs`, and the campaign ledger and
wave interfaces in `p3_stage1b.py`. The parent/core reviews cover scientific
bindings, saved smoke data, queue recovery and collector integrity. This check
ran no PBS/SSH/network commands, population simulations, fits or email.

## P1 / MAJOR — A released job name permanently hides its future reservations

`analysis/fable/calibration/v2_dev/p3_stage1b.py:590-601` accumulates all release
names in a set and excludes every reserve record bearing any released name.
It does not replay the ledger chronologically. A new reservation with that
same name is therefore forgotten on the next preflight, even if it precedes
an accepted scheduler job.

The shell reproduction uses a legitimate rejected submission, not an operator
releasing accepted work:

1. Request the planned 520-job W1 array; the qsub stub explicitly rejects it.
   The journal marks it uncertain and the ledger reserves 199,688 CPU-h.
2. After the stub accounting verifies that no job was accepted, append the
   documented release entry and an operator `rejected` journal entry. Resume
   the same run. Its array and collector are accepted and another reservation
   for the same name is appended.
3. Submit the same W1 shape in a fresh output directory. It also succeeds:
   the earlier release hides the accepted retry's new reservation.

Allocations accepted by the PBS stub total **399,376 CPU-h**, despite the
200,000 W1 ceiling. Run exit codes: `[1, 0, 0]`. Each successful preflight
reports only 199,688 reserved. This demonstrates a budget-guard failure; no
real allocation or expenditure occurred.

Minimal repair: replay reserve/release records in order into the current active
reservation state. A release should remove only the reservation active at that
point; a subsequent reserve must become active again. Test this exact rejected,
released, same-name retry, fresh-directory sequence; its final submission must
be refused before qsub. The existing release fixture uses a different new name
and consequently misses this case.

## P1 / MAJOR — Pre-journal retries can change shape without changing the reservation

`p3_stage1b.py:600-601` treats matching name alone as an idempotent reservation
and returns without checking the requested CPU amount or wave.
`kunanyi/s1b_submit.sh:34-45` derives that name from settings hash and directory,
excluding shape; lines 36-39 permit `run.json` replacement while no submission
journal exists. Preflight reserves before seeding at lines 43-51, so a seed
failure leaves precisely this state.

Reproduction:

1. Request one 8-core, 48-hour job: preflight records **392 CPU-h**, including
   the collector. The seed stub exits 7; no qsub call or journal exists.
2. Retry the same directory and settings with **521 jobs**. The same name is
   found in the ledger, so preflight returns `recorded:false` and
   `wave_reserved:392`, while reporting `reservation_cpu_h:200072`.
3. The actual submitter sends the array and collector to the accepting PBS
   stub: **200,072 CPU-h**, exceeding 200,000. Run exit codes: `[1, 0]`.

Minimal repair: require an existing active reservation to match the complete
immutable reservation tuple, including campaign, wave and CPU amount; otherwise
refuse. Bind the run identity from the first reservation, not only from the
first submission journal. A same-shape seed retry should remain idempotent;
a changed-shape retry should fail before qsub or undergo an explicit,
accounted replacement that rechecks both ceilings.

## Verified repairs and operational qualifications

- All **8 supplied scheduler fixtures pass under Bash 5.2.21 and 4.2.46**.
  All three shell scripts pass Bash syntax checks. Tests run in temporary
  copies, so Fable's checked-in fixture receipts were not overwritten.
- The repaired node script passes WAVE. With mixed W1/W2 tickets and stale
  claims, the actual claim/recovery functions select and requeue only W2;
  the W1 ticket and stale claim remain untouched. Setting-lock internals were
  replaced by a no-op context only for this isolated interface test.
- An immediate second output-directory submission is refused after the first
  199,688-hour reservation. A same-shape seed failure/retry records only one
  reservation and accepts one array/collector. An accepted-but-lost reply whose
  history expires retains its reservation and blocks both automatic retry and
  a fresh directory.
- The campaign-wide lock covers preflight, seed and submission; ambiguous
  requests retain reservations. Stale lock cleanup still requires the stated
  operator check that no submitter remains alive.
- The earlier minor fixture issue remains at `s1b_submit_fixture.py:64`:
  `<= CEIL + 8` permits eight extra hours although line 53 already includes the
  collector. Production arithmetic includes it correctly; this is not an
  independent launch blocker.
- Reservation totals are conservative upper bounds, not measured scheduler CPU
  usage. No live scheduler requeue policy or accounting state was inspected.

## Reproduction and evidence

Run:

```sh
python3 analysis/astra/s1b_scheduler_repair_review/check_repairs.py
```

The durable output is
`analysis/astra/s1b_scheduler_repair_review/repair_evidence.json`, with source
hashes, supplied fixture receipts, commands' exit codes, preflight reports and
ledger contents at each step. The local harness executes the real submitter
and the actual `reserve`/`preflight` bodies extracted from the reviewed source.
Source/runtime binding checks and sampler self-tests are stubbed to isolate
the scheduler/accounting contract; no scientific computation is involved.

No Fable implementation, project STATUS, exposure log or board state was edited.
