# Astra Stage 1b scheduler review

16 October 2026, 22:30 AEDT (Australia/Hobart). Source reviewed:
`e11b9b0171463c4b10e1dbce87b67e0949931db7`.

## Recommendation and scope

The proposed first W1 reservation is correctly bounded at **199,688 CPU-h**
(`520 × 8 × 48 + 8`). The submission journal retains the accepted Stage 1a
fail-closed recovery behaviour in the seven supplied fixtures. I found no
additional launch blocker in that particular shell invocation. **The campaign
rollover needs changes:** workers do not respect wave boundaries, and the
ceiling check is per invocation with operator-supplied prior expenditure,
rather than an enforceable cumulative campaign account. The parent review
separately assesses runner correctness and per-setting CPU caps.

Reviewed `s1b_submit.sh`, `s1b_node.pbs`, `s1b_collect.pbs`, and
`s1b_submit_fixture.py`, against their Stage 1a equivalents. Relevant Python
interfaces were read to resolve scheduler behaviour. No PBS/SSH commands,
remote activity, population simulations, fits, or email were performed.

## Findings

### MAJOR — W2 workers can consume unfinished W1 tickets

`analysis/fable/calibration/kunanyi/s1b_node.pbs:14-15` omits WAVE from the
worker invocation. `p3_stage1b.py:292-305` claims any queue ticket, and
`:329-342` has no wave restriction. Both waves share the same run directory.
W1's collector can legitimately leave unfinished tickets after its allocated
walltime; `collect` reports incompleteness without requiring an empty queue.

The bounded reproduction placed one unfinished W1 ticket in the shared queue
and invoked the actual `claim` function with a W2 worker identity. The W2
worker claimed it. Thus W2's reservation may continue W1 work, spending more
than the W1 allocation ceiling permits and reducing resources for the named
W2 design. This is conditional on residual W1 work; the completed six-setting
smoke had none and does not test that transition.

Minimal repair: pass the bound wave into `work`/`claim`, filter ticket claims
and stale-claim recovery by that wave, and make the W1-to-W2 handoff explicitly
account for unresolved W1 settings. Test a mixed queue with incomplete W1 and
W2 tickets; a W2 worker must consume only W2. This must be fixed before W2,
and is convenient to fix before freezing W1's executable package.

### MAJOR — Cumulative ceilings depend on an unverified operator prior

`s1b_submit.sh:24,30-41` scopes its lock and journal to OUTDIR/WAVE and accepts
CEIL/PRIOR directly from the command line. `p3_stage1b.py:454-461` merely adds
that prior to the current reservation and compares with that supplied ceiling.
Neither reads a campaign-wide reservation/expenditure record, binds the
200,000/1,000,000 ceilings, or proves the prior includes retries and cancelled
allocations.

The reproducible stub example invokes the real submitter twice, with identical
settings, W1 shape and ceiling, but OUTDIR `run` then `run_retry` and PRIOR=0
both times. Both return success and create an array and collector; each reports
199,688 CPU-h, for a combined reservation of **399,376 CPU-h**. The actual
Python preflight arithmetic is executed; source checks and its synthetic
sampler fixtures are stubbed because this test concerns submission accounting.

This is not a claim that the stated first W1 command overspends, or that an
operator intentionally bypassing a guard must be prevented. It means the
package currently cannot establish its advertised cumulative ceiling when a
failed campaign is restarted or topped up under a fresh directory. An accurate
external ledger and operator prior would enforce the policy, but that evidence
is not part of the executable preflight.

Minimal repair: use one campaign-level locked reservation ledger, binding the
settings identity and approved per-wave/campaign ceilings and reserving the
full allocation before qsub; unresolved requests must retain their reservation.
A simpler explicit operator-managed ledger is acceptable if the launcher
requires and verifies it rather than silently accepting an independent zero
prior. Test a second output-directory request against the same campaign,
including expired ambiguous submissions and failed/cancelled allocations.

### MINOR — The fixture permits an eight-hour ceiling excess

`s1b_submit_fixture.py:62` tests `allocated_cpu_hours_bound <= CEIL + 8`, although
the collector's eight hours are already included at line 51. Production
preflight correctly compares the total with CEIL. Tighten this assertion to
`<= CEIL` and add an exact-boundary fixture. This does not change the proposed
199,688 CPU-h result.

## Executed evidence and limits

Run `python3 analysis/astra/s1b_scheduler_review/check_scheduler.py`.
The script creates temporary stubs/copies only and writes
`analysis/astra/s1b_scheduler_review/scheduler_evidence.json`.

- Bash syntax passes for all three scripts; all seven supplied submission
  fixtures pass on local Bash 5.2. I did not rerun Bash 4.2 locally.
- The two failing stub workers produce node exit 2. A failing collector Python
  process preserves exit 3 despite successful packing. Failed tar packing
  produces exit 4. Successful tiny packing creates its checksum and exits 0.
- The wave-isolation and fresh-directory accounting examples reproduce as
  described. They run no scientific calculation.
- The supplied scheduler stubs use ordinary job IDs and do not model every PBS
  array semantic. The saved Kunanyi smoke is separate evidence of actual array
  and afterany operation; no live scheduler state was queried here.
- No scheduler automatic-requeue policy, per-user storage quota, campaign
  accounting export, or live allocated CPU usage was verified in this review.

Root integrates these findings with the core-runner, saved-output and scientific
design checks. No peer implementation, STATUS, exposure log or board state was
changed by this delegate.
