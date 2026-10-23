# Stage 1b round-2 interim review

**Continue the existing arrays. Accept the node-only mitigation in principle;
review its executable change and focused tests before the first W2 top-up.**
The current node script is unchanged, so this is a review of the proposal,
not clearance of an implementation. The false-uncertainty mechanism is
reproduced. No integrity failure was demonstrated, but the probe cannot
support the unconditional assurance that all interrupted work has recovered
or that every current library is valid.

Barry requested this check on 23 October after Claude's progress report and
board message 2235. Both WSL and canonical Mac mini were at clean commit
`461c115c308d301d228eaaa7497aab56ddb38ddd` when review began. Reviewed runner:
`1e35b94ab3811cc0ddded21aeaa5258120500c9e60f02dd5a6ee0c9c89d50d75`;
unchanged node script:
`cafc0a4dae6b9490a522dda8991aadae34808d5ec8f3b43a9f41ec17d36193ec`.

## What the interim evidence establishes

The saved 10:27–10:32 AEDT probe supports 4,676 COMPLETE markers among
4,847 W1 replay settings (96.47%): all 2,055 n = 0 settings and 2,621 n = 30
settings, with 171 n = 30 settings still open. W2 has 7,272 open settings.
The readable shard checkpoints account for approximately 53.3k W1 CPU-hours
and 18.4k W2 CPU-hours. These are progress observations, pending strict
collection; they are not scientific validation or measured final costs.

The earlier log census records 7,969 nonzero worker exits, all code 75.
The later message tally identifies acquisition uncertainty. These are
concurrent scans, not one atomic census: the saved category counts total
7,971 and hourly counts 7,973. The exact equality between 8,980 certificates
minus 1,011 exit records and 7,969 logged exits is a useful cross-check, not
a per-owner recovery audit.

## Reproduced defect and limits of the safety claim

The [lock review](astra_r2_production_lock_review_20261023.md) uses the
unchanged production functions with temporary files and a logical clock.
A foreign holder releases normally between a refused publication and the
contender's owner read at the five-second patience limit. The actual Linux
rename returns `ENOTEMPTY`; the contender has never published successfully,
yet exits with `OwnerUncertain` after 5.045 logical seconds. An equivalent
`EEXIST` refusal reproduces the same result. Readable-live-owner and early
release controls behave correctly. The parent independently repeated all
five classification/recovery cases; evidence is under
`analysis/astra/r2_interim_review/parent_lock_replay.{json,log}`.

Thus ordinary contention is sufficient; NFS caching is not needed for this
counterexample. The production logs lack the errno/observation history to
prove that every recorded exit was the same false positive. The reproduced
case is fail-closed and leaves no contender lock. This supports continuing
the bound run, not cancelling or rebinding its output.

A death certificate establishes that its exact worker ended. Recovery still
requires acquiring the setting lock and processing the abandoned claim.
The fixture preserves a foreign live lock and leaves a certified claim
unrecovered until that holder releases. Moreover, an acquisition failure
during commit can occur while the worker already owns a claim. The statement
that each interrupted worker holds nothing is therefore too broad.
Exit-75 processes bypass the normal final worker receipt, so zero counters
in those receipts do not cover all interrupted work. The probe inventories
markers and checkpoint counters; it does not perform the collector's
binding, range, journal, identity or library checks.

Use: **no integrity failure was observed; recovery and strict collection
remain to be verified.** A future runner should distinguish definite
contention from ambiguous rename outcomes and retain the original token's
uncertainty until reconciled. Keep the current runner bound for round 2.

## Node-only mitigation: accepted direction, implementation still pending

The runner's `check()` and `binding()` bind the metric, runner, scientific
helpers/imports, settings and allowed runtime. They do not bind
`s1b_node.pbs`. Changing only the wrapper for future arrays can therefore
preserve existing shard compatibility. Record the exact submitted node
script hash for each array; existing PBS jobs retain their submitted copy.

The [node review](astra_r2_node_plan_review_20261023.md) sets the focused
acceptance cases. The implementation should:

1. Allow exit-75 retries while useful time remains, with jitter/backoff and
   no fixed retry count. Preserve bounded handling and visible failure for
   unrelated nonzero exits.
2. Certify the exact reaped child successfully before continuing. Keep a
   unique invocation nonce and a new attempt identity for every launch,
   including restarts following exit 0.
3. Check the time cutoff before every launch, including after any delay.
   Persistent uncertainty must end within the existing allocation deadline.
4. On exit 0, check both queued tickets and in-flight claims for this wave.
   A claim can become a successor ticket between observations, so a
   claims-only test can abandon available work. Ignore other-wave activity;
   distinguish unreadable state from an empty wave.
5. Avoid frequent full-directory scans by every idle slot. Bound the time an
   entirely idle subjob remains allocated because of remote claims; otherwise
   the refill policy can retain thousands of idle cores for the tail. Use
   jittered waiting and retain an intelligible final reason for stopping.

Exercise more than 20 exit-75 attempts, ordinary/non-75 failures, certificate
publication failure, deadline crossing during a delay, exit-0 refill after
successor creation, other-wave-only state and true wave exhaustion. Reuse
the established node harness and confirm the production Bash surface.
Six isolated tests of the actual current wrapper establish the baseline,
including ignored certificate-publication failure and launches after the
deadline. Those use worker/clock/filesystem stubs; neither failure was
observed in the production probe. These are implementation checks for
Fable's forthcoming diff, not a new
resource or scientific decision for Barry. Restarting more processes alone
does not establish a throughput benefit or resolve a permanently blocked
claim.

## Reporting corrections

The [progress review](astra_r2_progress_review_20261023.md) reproduces the
arithmetic and six small exact-probe cases. Material corrections are:

- **82 slots are near or at the cap:** the tally selects at least 19
  nonzero exits, with maximum 20. It does not give the number that reached
  20 and stopped.
- **76% is median raw hit-count progress:** all readable shard hits plus
  the pilot, clipped at K. It is not verified contiguous-prefix completion
  or a forecast of remaining time. A synthetic gap case produces 76% raw
  progress with zero usable prefix hits.
- **No FAILED markers were reported; invalidity was not tested.** A bare
  COMPLETE marker can pass this progress inventory without valid journals.
- **Efficiency ratios reproduce the saved summary:** 84.50% for W1 and
  96.73% for W2. Raw PBS records were not available for independent checking.
  The probe's accounting parser does not exclude parent-array resource
  fields; retain the raw subjob records at the next ordinary collection.
- **The 9,795-hour W1 allocation/CPU gap is not a causal breakdown.** At
  15–20 seconds per event, 6,587 W1 restarts imply only 27–37 slot-hours
  of direct delay; capped-slot idle time and lost/repeated work need their
  own evidence. The current receipts do not measure which cause dominates.
  Likewise, 53.3k hours spent so far cannot establish final savings against
  the approximate 92k planning heuristic.

## Next ordinary collection and handoff

The collector email marks a scheduling dependency finishing, not proof that
all W1 settings completed successfully. Fetch its archive and reconcile all
4,847 replay identities and statuses with the settings and strict collector
output. Verify journal/library hashes and retain COMPLETE, CAPPED, incomplete
and invalid outcomes explicitly. Do not infer all-complete from
`collection_ok`: that field reports absence of collection errors and permits
incomplete settings. Queue/claim totals in the collector are global, so
ongoing W2 activity must not be mistaken for residual W1 work.

Check actual queued and running requests before sizing a top-up. Starting
already queued W2 jobs does not release capacity under the recorded
7,000-CPU request cap. With the original 570 W2 subjobs and collector still
present, a 300-subjob top-up and its collector request 6,962 CPUs in total
after W1 and its collector finish, assuming no other requests. Reconcile
completed allocations against the reservation ledger.

Run the round-to-round comparison over the prescribed W1 set after strict
journal validation. The standalone comparator now rejects within-shard
duplicate identities and repeated requested settings, but it is not a
replacement for the collector's binding/range checks. Report actual common
batch/record coverage and pilot-only cases, not just its exit code. Preserve
the original 9,695 COMPLETE and two CAPPED outcomes and the full campaign
denominators. No Stage 1c fitting clearance follows from this interim check.

Fable is next for the node diff, focused fixtures and normal collection/
determinism receipts; Codex can check the concrete wrapper before the first
extra W2 array. Existing production may continue. No new population
simulation, fitting, PBS command or production-source edit was made in this
review. A narrow attempt to read the already-saved PBS files could not
authenticate through the jumpbox; no access changes or new probe followed.

Review posted in discussion 70, message 2239.

Recorded: 23 October 2026, 11:00:37 AEDT (Australia/Hobart).
