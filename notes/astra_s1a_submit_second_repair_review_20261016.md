# Astra: second Stage 1a submission repair review

16 October 2026, 14:06 AEDT (Australia/Hobart).
Source: `3fa81cb58b262684722332c35d2d3e3b48fe408a`;
comparison with reviewed `2404fda`.
Submitter SHA-256:
`8ca2dd97250b294c884c209fdbac2bbc2419503e51a965de303e1cdff8f85a0d`.

**One narrow submission ambiguity remains.** The qstat dependency repair is
accepted, and an earlier `request`/`uncertain` entry now prevents resubmission
when its history is absent. The new post-failure confirmation branch nevertheless
labels an empty query as a rejection, without evidence that the job was never
accepted. Remove that automatic rejection before dispatch.

Scope is the changed submitter and fixture only. Parent and peer reviews own
the package, preflight bindings and collection. No actual scheduler command,
remote connection, email or simulation was performed. The 15 supplied scenarios
were independently replayed from temporary copies; all pass. Evidence is in
[`baseline_replay.json`](../analysis/astra/s1a_submit_second_repair_review/baseline_replay.json),
with additional checks in
[`audit.py`](../analysis/astra/s1a_submit_second_repair_review/audit.py) and
[`audit.json`](../analysis/astra/s1a_submit_second_repair_review/audit.json).

## P1 remaining: absent-after-failure does not prove non-acceptance

At `s1a_submit.sh:61–68`, a failed/no-ID qsub waits ten seconds and queries by
name. Line 66 writes `rejected ... absent-after-failure` when that query succeeds
with no result. Resume is then allowed to submit the same key again.

A submission reply can fail or remain delayed while an accepted job completes
and leaves retained history. Waiting ten seconds **after the qsub returns**
does not bound the time since acceptance or establish the server's retention
window. No retained-history guarantee or response-time bound is checked here.
The same primary PBS reference used in the first repair review says historical
jobs are available only while the administrator's retention period still holds.
[PBS Professional User Guide, section 10.1.1.3](https://help.altair.com/2024.1.0/PBS%20Professional/PBSUserGuide2024.1.pdf#page=187)

The added stub accepts the fourth node job, preserves it in the append-only
allocation ledger, and removes its completed history before returning the lost
reply. This models elapsed server time; no wait or live cluster behavior is
claimed. The successful empty confirmation is therefore not a simulated query
error or an inconsistent query result: that historical record is genuinely no
longer available.

Observed fixture result: the first invocation records `rejected j3 ...
absent-after-failure` despite four accepted node jobs. Resume exits zero after
creating **46 node jobs plus one collector**, with only 45 unique node names and
an allocation bound of **1,013.445 CPU-hours**. All 45 currently live jobs are
included in the collector dependency; the uncounted earlier completed job is
what breaks the cumulative bound. This is the remaining original resource
finding through the newly introduced confirmation branch.

**Minimal exact remedy:** delete the `n == 0` automatic-rejection branch at
line 66 and let it reach the existing `uncertain` record/stop at line 68. Keep
the one-match reconciliation path. Permit a later `rejected` receipt only when
there is affirmative non-acceptance evidence, rather than another absence
query. The existing verified-operator receipt path is sufficient; this does not
require a new tool, service or Barry decision. Update the definite-rejection
fixtures to provide that receipt before retrying, and include the new delayed
reply/history-expiry case.

## Closed within this scope

- Prior `request`/`uncertain` plus empty query now stops. The supplied history-
  expiry scenario creates no replacement until verified accepted/terminal
  receipts are supplied.
- qstat now uses `-x -f`, omits only explicit F or an ID-matching terminal
  receipt, and stops before collector submission on query failure. One-failure
  and all-failure scenarios resume with one collector and all 45 dependencies.
- Additional successful-but-unclassifiable qstat output stops with 45 node
  jobs and zero collectors. Cycling the 45 job queries through all supported
  live states Q/R/H/W/T/E/S/U/B/M retains all 45 dependencies.
- Expired history for a known accepted node stops until a verified terminal
  receipt is supplied. The recovery then retains 44 live dependencies.
- Locking, fixed run identity, ordinary duplicate refusal, already-accepted
  collector reuse and supplied preflight-refusal scenarios continue to pass.
- The supplied single-dispatch arithmetic now retains the unrounded prior
  allocation: **991.445 CPU-hours**. `bash -n` passes.

This disposition leaves only the absent-after-failure inference open in the
submission contract. Other reviewers' scopes are not reopened here.
