# Round-2 node implementation review

**Recommendation: hold this node version for one control-flow repair before
using it in a top-up.** The main restart and certification requirements pass,
but an empty scan followed by an unknown scan can bypass both the whole-subjob
idle budget and the launch-cutoff check. At the cutoff it becomes an
unbounded metadata polling loop. No overlapping children, invalid certificate
or unsafe lock reclamation was demonstrated.

Reviewed HEAD `805f0079f5eb8157b351ee31c04a1ab91f3ca3f7`, node implementation
`b17148c`, and the acceptance contract in
`notes/astra_r2_node_plan_review_20261023.md`. The actual node SHA-256 is
`00ed12fb3aa3a8224ea99efa6377755821efb75e46e6786a5a0fdfde34ca8457`.
This is an executable node audit; collection, top-up binding and resource
accounting are covered separately. Existing arrays use their submitted script.

## MAJOR: the empty/recheck branch bypasses every idle-loop limit

In `analysis/fable/calibration/kunanyi/s1b_node.pbs:75–89`, an initial `empty`
result enters a grace pause and a second wave scan. If the second result is
`unknown` or `inflight`, line 82 immediately continues the loop. It skips the
whole-subjob idle check at lines 84–86, the cutoff check at line 88 and the
bounded polling delay at line 89. The outer launch guard is not reached until
this inner loop ends.

`combined_checks.py` runs the actual shell with a deterministic scan sequence:
each first wave check reads both directories empty; each post-grace check
reports a scan failure (`unknown`). Every third `find` fails, while the other
calls use the real local `find`. Two bounded cases expose the distinct limits:

- **Cutoff/deadline:** configure both at ten logical seconds. The only sleep
  is clipped to ten seconds. Thereafter the shell keeps scanning without any
  delay or completion receipt. In the recorded run, 71 of 73 scan attempts
  occurred at the cutoff or later; the harness terminated the still-running
  process group after four real seconds. Only the initial child was launched.
- **Whole-subjob idle budget:** retain the default long allocation/cutoff,
  scale the idle budget to 30 seconds and grace to ten seconds, and leave the
  single slot idle throughout. The shell reaches 190 logical seconds and 59
  scan attempts without retiring. The same four-second harness limit ends it;
  no completion receipt is written.

These are constructed recurring scan-error interleavings, not claims about an
observed Kunanyi event or NFS error frequency. The logical clock and small
budgets expose actual shell control flow without waiting through an allocation.
The issue also applies to a recurring `empty → inflight` observation sequence
by the same source branch; that sequence was not separately run. A real PBS
walltime would ultimately terminate the job, but the wrapper itself does not
honour its intended earlier idle/cutoff limits on this path.

**Minimal repair:** make idle-loop deadline and whole-subjob idle checks
unconditional, including after a grace recheck. Route post-grace `unknown` or
`inflight` through the common bounded waiting path. Do not allow a zero-delay
scan loop once the cutoff has arrived. Preserve the queue-or-claims predicate,
explicit unknown state and exact certificate requirements.

**Acceptance:** the two recorded alternating-scan cases must terminate within
their respective budgets, without harness intervention or a later child
launch. A cutoff-only change is insufficient because it leaves the idle-budget
failure before cutoff. Rerun the existing nine fixture groups and the two
certificate/restart controls below after the repair; no broader simulation
programme is needed.

## Verified improvements

The upstream fixture was copied to the owned audit directory and run against
the unchanged actual node script under Bash `5.2.21(1)-release`. All nine
groups pass. This verifies:

- More than 20 exit-75 children continue, with distinct generations and
  certificates; non-75 failures retain a separate finite count across 75 and
  zero exits.
- Queue-only work refills, claims-only work waits, readable empty state
  retires after a recheck, and other-wave activity does not retain the slot.
- Work appearing between observations is found; persistent scan failure is
  recorded as unknown rather than empty.
- Failed certification stops replacement; an applied-but-failed rename can
  reconcile through exact readback. Node reruns have fresh owner nonces.
- Ordinary pause and certificate-retry cases launch no child after the
  cutoff; every child receives the same absolute deadline.
- Eight idle slots retire after their tested idle budget, while a working
  sibling postpones idle retirement. The replay recorded eight startups and
  58 directory scans for the idle case, and 90 scans with a working sibling.

Two additional combined controls pass:

1. Exit sequence `3, 75, 0, 3, 75, 3` with queued work. Each replacement
   independently checks its predecessor's exact `{owner, host, pid, rc}`
   certificate and confirms that process is gone. Six distinct owners launch;
   the third non-75 failure stops the slot visibly. The zero exit does not
   reset either identity generation or the unexpected-error count.
2. Every certificate rename takes effect but reports failure, and its first
   readback also fails. The wrapper retries, confirms the exact final
   certificate and only then launches the replacement. Both children are
   certified and the node finishes successfully.

The archived Bash `4.2.46(2)-release` nine-group receipt names the same node
digest and reports success. That receipt was inspected, not independently
rerun; no shell was installed for this review.

## Nonblocking qualifications

- The normal idle budget is checked at polling points, so it can overshoot
  nominal `IDLE_MAX_SECS` by a poll interval plus jitter and command time.
  This is a finite scheduling allowance, distinct from the reproduced branch
  that skips the budget indefinitely. Treat 1,800 seconds as nominal unless
  the pause is also clipped to an absolute idle deadline.
- Certificate retries use raw `sleep "$RETRY"` rather than `pause`. They can
  continue beyond the launch cutoff, but defaults bound them to six attempts
  and at most 60 seconds of sleep. The outer guard still prevents replacement
  after cutoff. Given the 600-second launch cutoff and 1,800-second sampling
  margin, this alone does not justify a second hold; documentation saying
  *every* pause is clipped is inaccurate.
- Retirement with an `unknown` activity state is logged explicitly; node
  success is not an assertion that the wave completed. Final collection and
  unresolved-claim accounting remain separate checks.

## Evidence and scope

New artifacts are confined to `analysis/astra/r2_node_review_20261025/`:

- `s1b_node_fixture.py`: unchanged copy of the upstream fixture;
  `s1b_node_fixture_astra_replay.json` and `fixture_replay.log` record the
  independent nine-group replay (25.99 seconds, 18,348 KiB peak RSS).
- `combined_checks.py`, `.json`, `.log`: two failing-limit reproductions and
  two passing combined controls (10.42 seconds, 18,216 KiB peak RSS).

Commands from the repository root:

```bash
FIX_NODE=/home/bwbrook/papers/project/analysis/fable/calibration/kunanyi/s1b_node.pbs FIX_TAG=astra_replay /usr/bin/time -f 'elapsed_s=%e max_rss_kib=%M' python3 analysis/astra/r2_node_review_20261025/s1b_node_fixture.py > analysis/astra/r2_node_review_20261025/fixture_replay.log 2>&1
/usr/bin/time -f 'elapsed_s=%e max_rss_kib=%M' python3 analysis/astra/r2_node_review_20261025/combined_checks.py > analysis/astra/r2_node_review_20261025/combined_checks.log 2>&1
```

The fixture assertions include assertions that the defective cases remain
running until the harness stops them; a zero fixture exit is not production
clearance. All worker processes are synthetic. No PBS operation, population
simulation, production-source modification, prior-evidence change or commit
was made.

Recorded: 2026-10-25 12:06:46 AEDT (Australia/Hobart).
