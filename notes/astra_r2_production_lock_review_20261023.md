# Round-2 production lock review

**Continue the bound production run; support a bounded node-only mitigation
for future top-ups.** The current acquisition classifier has a reproduced
operational defect. Nothing in this check establishes an integrity failure
that warrants cancelling the running arrays. Equally, the progress probe does
not establish that every uncertainty exit was false or every interrupted claim
has recovered. The proposed node change has not yet been implemented or tested
by this review.

Target: `461c115c308d301d228eaaa7497aab56ddb38ddd`, including the runner diff
from `d3cda6f`, design §9f, `p3/r2_probe.sh` and the saved 23 October progress
receipt. Runner SHA-256 is
`1e35b94ab3811cc0ddded21aeaa5258120500c9e60f02dd5a6ee0c9c89d50d75`;
the unchanged node script is
`cafc0a4dae6b9490a522dda8991aadae34808d5ec8f3b43a9f41ec17d36193ec`.
The parent owns production binding and aggregate-evidence integration; the
other reviews cover the node proposal and progress arithmetic.

## MAJOR operational defect: known contention is classified as uncertainty

In `analysis/fable/calibration/v2_dev/p3_stage1b.py:269–278`, `_publish` discards
the rename errno and returns `False` for every failure. `lock:316` then sets
`unresolved = True` even for a definite `EEXIST`/`ENOTEMPTY` refusal. If the
foreign holder releases between that refusal and `_owner`'s read, the record
is absent. `_owner:262–266` maps that ordinary absence to `None`, and the wait
limit at lines 329–331 produces `OwnerUncertain`.

The local fixture exercises the **actual** `_publish`, `_owner`, `lock` and
`unlock` functions. It uses temporary files and a logical clock, scheduling a
foreign holder's normal release between a refused publication and the owner
read. There is no NFS error, lost reply, stale read or unreadable-file injection.

| Case | Observed outcome |
| --- | --- |
| Foreign live holder remains readable | `LockBusy`; foreign lock intact |
| Kernel `ENOTEMPTY`; holder releases on the last attempt | `OwnerUncertain` at 5.045 logical seconds; zero successful contender publications; no lock exists at exit |
| Same known refusal represented as `EEXIST` | Same false `OwnerUncertain` |
| Holder releases well before the limit | Contender acquires and releases normally |

For the deadline case there are 46 kernel refusals; the last occurs at 4.995
seconds with default five-second claim patience. The Linux filesystem returned
`ENOTEMPTY` (39). The `EEXIST` (17) variant changes only the reported errno after
that real refusal; it does not claim this filesystem produced both errnos.

This proves a classification defect and provides a sufficient non-NFS cause
of the observed message. It does **not** measure this race's production
frequency. NFS visibility effects may contribute, but are a hypothesis here,
not a demonstrated explanation for all 7,969 recorded exits. Current logging
does not retain the publication errno or observation sequence needed to assign
those exits retrospectively. The saved acquisition-message tally is consistent
with this branch, not a per-event causal audit.

For a later runner, the proposed distinction is sound: only genuinely ambiguous
rename outcomes should create acquisition uncertainty, and that uncertainty
must remain attached to the original acquisition token until reconciled. A
later foreign/absent observation must not silently erase an earlier ambiguous
outcome. This is a future bound-runner change, not a proposed live patch.

## Integrity and recovery: what is supported

In the reproduced false positive the contender owns no lock. Its certificate
therefore has no lock of that attempt to reclaim. The certificate logic checks
owner identity and, for locks, exact host/PID (`certified:209–220`); reclamation
also checks the observed lock generation (`_reclaim:281–299`). The fixture
confirms that a certificate for an ended claimant does not permit breaking a
different live holder's lock.

That protection is conditional evidence about the mechanism. It is not a
whole-run integrity audit. In particular:

- A certificate is **eligibility evidence**, not a recovery receipt.
  `recover_stale:547–568` still needs the setting lock. The fixture leaves a
  certified claim untouched while a foreign holder is live (`0` requeued),
  then requeues it after that holder releases (`1` requeued). Claims can also
  remain behind the documented `LockStale` operator-recovery boundary.
- `OwnerUncertain` bypasses `work`'s final receipt write at lines 671–673.
  Counters aggregated from `workers/*.json` therefore omit interrupted worker
  invocations. Zero `stale_requeued` or `transient_errors` in those receipts
  cannot establish either universal recovery or the absence of NFS failures.
- `r2_probe.sh` reads terminal-marker names and checkpoint counters; it does
  not perform the strict collector's binding, journal, record-identity and
  library-hash validation. Absence of reported FAILED markers is not absence
  of invalid output. The probe also spans several minutes of concurrent work.

The defensible wording is: **no integrity failure was demonstrated by this
probe or the bounded classification replay; interrupted work remains subject
to certificate recovery and strict collection.** The blanket “no correctness
consequence” claim is stronger than the evidence.

## Consequences for the node-only proposal

Removing the arbitrary exit-75 restart cap can preserve available worker slots
without altering the bound runner. Rechecking after an exit 0 can also be
useful: `work:646–652` can exit while other live claims exist and may later plan
new tickets. These are operational mitigations; they do not repair the
classifier or prove that a remaining claim can progress.

The new wrapper should preserve the existing exact reaped-process certificate
and unique restart identity, distinguish exit 75 from unrelated failures,
bound all restarting/polling by the existing worker deadline, and use jitter
or backoff that avoids synchronized metadata churn. A zero-exit continuation
check must be specific to the worker's wave. A persistent exit-75/blocked-claim
case should consume only the authorised time allowance and leave a clear
receipt. These are acceptance cases for the separate node review, not an
additional production-runner edit. More restarts alone are not proof of more
useful completed work.

## Evidence and limits

`analysis/astra/r2_production_lock_review/lock_checks.{py,json,log}` records the
five cases. `helpers.py` reuses the prior bounded audit loader: source functions
are loaded unchanged via AST, and unmocked numerical sampling is forbidden.
The recorded run took 1.78 seconds and 31,120 KiB peak RSS. Command:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 /usr/bin/time -f 'elapsed_s=%e max_rss_kib=%M' python3 analysis/astra/r2_production_lock_review/lock_checks.py > analysis/astra/r2_production_lock_review/lock_checks.log 2>&1
```

The holder release is a deterministic callback between two filesystem
operations, modelling a permitted concurrent interleaving. The clock schedules
the patience boundary; it is not a measured NFS latency result. The certificate
case is a synthetic ended-owner claim, not an audit of live production
certificates. No PBS call, population simulation, production edit or commit was
made. All writes are confined to this memo and its owned audit directory.

Recorded: 2026-10-23 10:57:31 AEDT (Australia/Hobart).
