# Astra: Stage 1a submission repair review

16 October 2026, 12:21 AEDT (Australia/Hobart).
Source: `7f5be0b4e4a24916d50035eea1d470acef8df056`.
Submitter SHA-256:
`facded63e025906cffad131277844b7ca3981cbc122a7547a2ba79acfea11ed4`.

**Hold dispatch for two small recovery/dependency repairs.** The new lock,
identity, durable accepted-ID journal, ordinary resume and preflight integration
address the original common failure paths. All ten supplied stub scenarios
reproduce successfully. Two additional scheduler-error scenarios still defeat
the proposed resource and collection guarantees.

Scope: `kunanyi/s1a_submit.sh`, its stub fixture, and the called preflight's
shape/allocation logic. Runner, collector contents, input/archive bindings and
statistical intervals are owned by the other reviewers. No remote connection,
PBS command, email or simulation was performed. The primary scheduler
documentation was consulted; Kunanyi's current job-history settings were not
queried.

Reproducible evidence: [`audit.py`](../analysis/astra/s1a_submit_repair_review/audit.py),
[`audit.json`](../analysis/astra/s1a_submit_repair_review/audit.json), and
[`baseline_replay.json`](../analysis/astra/s1a_submit_repair_review/baseline_replay.json).
The original fixture and submitter were copied to a temporary directory before
baseline execution so the peer's checked-in receipt was not rewritten. Extra
fixtures use the production shell and the same isolated stub harness with
explicit additional scheduler behaviors.

## Remains open

### P1: an empty history query still converts uncertain acceptance into another allocation

At `s1a_submit.sh:39–47`, no matching `qselect -x -N` result causes another qsub,
even when the journal already records a request/uncertain outcome for that key.
The previous uncertain state is never tested before resubmitting.

The fixture accepts job 4 but loses its qsub reply. The four accepted jobs then
finish and their scheduler history expires. On `resume`, the first three IDs
are recovered from the durable journal; job 4 has no accepted ID and is absent
from history, so it is submitted again. Resume exits zero with **46 accepted
node jobs, 45 unique names, and a 1,013.44 CPU-hour allocation bound**. Preflight
still checks only the nominal 45-node plan. The duplicate has an earlier
completed owner in this fixture; concurrent writers are not claimed here.

The history condition is supported by PBS's documented contract: finished/moved
jobs can be queried only while their history remains retained, for a duration
set by the administrator. The `-x` option includes retained history; it does not
establish that an absent job was never accepted.
[PBS Professional User Guide, section 10.1.1.3](https://help.altair.com/2024.1.0/PBS%20Professional/PBSUserGuide2024.1.pdf#page=187)

The same fixture at the collector submission produces two accepted collectors
after its lost reply and expired history. Its 992.44-hour bound remains below
1,000, but the claimed collector-once behavior is false in that case.

**Minimal repair:** distinguish never-requested from requested-but-unresolved
keys. For a prior request without a verified acceptance or authoritative
non-acceptance receipt, an empty query must leave it unresolved and stop before
another qsub. A found job can still reconcile automatically. Routine manual
reconciliation by the executing agent can use scheduler/accounting evidence;
this need not ask Barry or create a new service. Any truly authorized replacement
must count the prior accepted allocation against the same ceiling.

### P1: any qstat error removes a potentially live worker from the collector dependency

At `s1a_submit.sh:64`, only qstat exit zero adds a dependency. Every nonzero
exit is treated as if the job had finished, with stderr discarded. The code
never inspects an explicit terminal state.

With 45 live queued jobs, the fixture makes qstat fail with a server-connection
error for one ID. The script exits zero and submits the collector with only
44 dependencies. With the same error on all status queries, it exits zero and
submits the collector with **no dependencies**. The collector can therefore
start, summarize and pack while workers are still queued/running. Its later
completion would not establish a complete or stable result archive.

PBS documents a nonzero qstat status as inability to process an operand,
not as a terminal-job receipt. It provides `-x` and explicit job-state fields
for finished/history jobs.
[OpenPBS qstat manual](https://github.com/openpbs/openpbs/blob/master/doc/man1/qstat.1B)

**Minimal repair:** use successful status retrieval and explicit terminal-state
evidence to omit a dependency. Retain dependencies for confirmed live jobs;
stop collector submission on transport/query failure, unknown status or
unresolved missing history. Preserve the error and leave the accepted node IDs
available for safe resume. A previously recorded, verified terminal receipt can
resolve a job after history expiry. The existing afterany collector is adequate
once this classification is reliable.

## Closed or verified within this scope

- The original duplicate `new` call is refused. A completed dispatch followed
  by `resume` submits no extra jobs.
- A held/stale lock refuses dispatch and remains in place. The message requires
  checking that no submitter runs before removal. This conservative behavior is
  appropriate; automatic stale-lock deletion is not requested.
- A fourth-qsub rejection resumes correctly in the supplied stub; an accepted
  fourth job with lost reply reconciles correctly while it remains queryable.
- A rejected collector resumes once; an accepted collector with lost reply is
  reused while it remains queryable. Completed known node IDs are retained in
  the ledger and not resubmitted.
- Shape changes on resume and resume without a journal are refused.
- A qselect error fails closed before dispatch. The added recovery fixture
  also confirms that a qselect error after an uncertain fourth submission makes
  no extra qsub calls. The unsafe case above is a successful empty query.
- Preflight is now called before any qsub and the actual function calls
  `check(settings, metric)` before calculating shape/allocation. Isolated
  arithmetic checks accept 45 × 8 × 9,900 seconds and reject four-hour jobs,
  44 × 8 workers, and a 2:10 walltime shorter than the expected load plus margin.
  This subreview stubs `check()`/`test()` and does not claim a second actual
  runtime-binding verification; the parent is replaying the real preflight.
- The command's prior-cost input 0.44 plus collector cap 1 yields the reported
  **991.44 CPU-hours** for one accepted 45-node dispatch. The earlier audit's
  unrounded smoke-plus-collector figure yields 991.445; both are below 1,000.
  These calculations do not cover a hidden duplicate allocation.
- `bash -n` passes. ShellCheck's only diagnostic is SC1090 for the intentionally
  configurable sourced environment; no shell syntax finding remains.

No additional design decision or compute ceiling is proposed. Fable owns the
two bounded repairs; Astra can close this submission review by replaying the
expired-history and status-error fixtures after those repairs.
