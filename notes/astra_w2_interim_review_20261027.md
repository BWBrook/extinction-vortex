# W2 interim results and continuation review

27 October 2026, Astra (board participant Codex). Reviewed `35816f3`, board
2399–2419 (review replies 2421–2422), the bound runner `1e35b94a…`, repaired node `8fe10208…`, and saved
W2-a archive `55448298…`. Review evidence is under
[`analysis/astra/w2_interim_review_20261027/`](../analysis/astra/w2_interim_review_20261027/).

**Recommendation: let the existing W1/W2 topup-b arrays finish, strictly collect
both waves, and hold topup c until the duplicate-ownership defect is repaired.**
The earlier node hold is closed. The duplicate-execution mechanism is now
reproduced, but the particular NFS read that allegedly triggered production
duplication remains a hypothesis. Preserving existing work does not require
another dispatch under the defective runner. Fable owns the next repair and
recovery proposal; no new scientific or resource choice is needed from Barry.

## 1. Accepted evidence

The independent audit ran on deep-server against the immutable saved archive,
with one process and no simulation. It verified:

- archive SHA-256 `55448298029d8bb2d1783f489ed5809dcc88345c84c6e8294c0e23744e9eec96`;
- 185 unique regular members, exactly 183 libraries and the summary/log;
- embedded summary equal to both the remote and committed local summary,
  SHA-256 `9bfe0ca4e2c833bdd2e6c5eeb1e26aecc50e1777e68f7a1aba07bee3e8704a08`;
- every library's declared digest and all 366,000 retained records: exactly
  2,000 per library, unique strictly ordered identities, batch/proposal bounds,
  finite parameter values, path length and selection S, and the K-th-hit batch;
- exact 7,272-row identity coverage and binding to settings `248f9c7d…`, metric
  `2dc57d9f…` and runner `1e35b94a…`.

This establishes consistency of the archived output. It is not raw-journal or
seed-based numerical replay. There is no evidence here that the archived
numerical values are wrong. The collection as a whole remains unsuccessful:
183 COMPLETE, 7,076 incomplete and 13 invalid. A valid archived library does
not certify the current mutable shards for that setting.

The repaired node passes the two previous counterexamples: retirement at the
10-second cutoff and 30-second idle budget, no forced termination and no
post-cutoff scan. Both mixed-restart/certificate controls and all ten current
fixture groups pass on Bash 5.3.9. The saved Bash 4.2 result is Fable's evidence,
not a second runtime replay by this review. The bound scientific runner has
not changed.

The fetched W1 determinism JSON hashes to `73f9cd12…`; its per-setting totals
sum to 1,643,296 identical records across 9,336,542,588 common batches. Coverage
is positive for 1,091 of 4,847 settings; 3,756 have no common committed batches.
This checks the saved comparator receipt, without repeating its raw-journal run.

## 2. MAJOR — omitted claim visibility can create two shard writers

The [mechanism review](astra_w2_duplicate_mechanism_review_20261027.md) injects
one omitted claim in the listing used by the unchanged `plan()` while holding
the real setting lock. The planner republishes the existing range and unchanged
`claim()` admits a second owner. Two concurrent calls to the unchanged shard
engine, with a deterministic one-hit batch stub, then produce identical appended
halves: 318 journal bytes against a 159-byte checkpoint. Strict verification
rejects the excess terminal bytes. The parent independently replayed this
counterexample on the pinned Python/NumPy/SciPy environment.

This is a sufficient failure path, not an observation of the historical NFS
fault. The saved census establishes eight ranges with two claim pathnames
(two W1, six W2); it did not establish that both named owners were alive. Saved
exactly doubled sizes are consistent with the reproduced mechanism, but raw
production halves were not compared. No alternative ordinary interleaving in
the setting-locked claim/recovery/adoption paths was found.

The repair should make each range's state and exact owner authoritative under
the setting lock. Global queue entries can identify candidates; an omitted,
stale or duplicated entry must not authorize a new writer. Claims, completion
and positive-death recovery must condition on the same owner/generation.
Test omitted listings, duplicate/stale hints, competing claimants and every
interruption between the authoritative transition and its queue update. Retain
the current runner as a failing control for the omitted-claim case.

The [collection review](astra_w2_collection_review_20261027.md) confirms that
terminal excess bytes and committed duplicate identities are rejected;
nonterminal extra bytes stay outside the verified checkpoint prefix. Those
guards explain the 13 invalid rows. Coherent duplicate execution can also leave
valid deterministic output while wasting CPU, so neither the invalid count nor
the duplicate-claim census measures total duplication.

## 3. Preserve work; do not expand the defective run

I agree with keeping the existing b arrays, preserving their binding and
collecting their work. I disagree with adding topup c under the same runner
while the demonstrated defect is unresolved. Available capacity alone does
not justify adding writers and directory traffic.

After every array of each wave ends, retain a dated terminal PBS/worker receipt
and strictly collect that wave. Include W1 in this check: its previously audited
archives remain accepted, but the active W1 topup also appears in the duplicate
claim census. Preserve the old run and all invalid evidence.

For a fresh repaired run, account for **all final incomplete, FAILED and invalid
settings**, not just the 13 invalid rows in this snapshot. Preserve scientific
settings, streams, proposal caps and denominators. A batch-zero rerun is the
conservative recovery route. A one-time exact import of verified partial shards
could preserve substantial work, but it is not implemented or cleared here:
it needs old-binding verification, committed-prefix and range checks, exact
source/destination byte identity, owner ambiguity rejection and independently
tested fresh ownership state. Do not relabel an old run's binding in place.
If that import cannot meet the contract, use the batch-zero route.

Reconcile immutable old and recovered results against the original inventory,
with unique setting rows and archive members, unchanged scientific identities,
verified COMPLETE libraries and explicit remaining failure/cap outcomes. Keep
primary and check libraries separate. Do not treat old FAILED rows as final
scientific exclusions when constructing the recovery inventory.

The W2 snapshot contains 7,200 primary settings and 72 checks. Only 182 primary
libraries are complete; zero of 800 outer datasets has all nine populations
(the maximum is five). These are library-availability results. They do not
support fitted validation or empirical inference; the fixed 200-trial scenario
denominators remain unchanged.

## 4. Reporting and dispatch corrections

The summary accounts for 143,903.73 useful and 98,520.26 outside-prefix CPU-h
**among valid rows**. Invalid rows omit CPU fields, and one surviving checkpoint
cannot count all losing duplicate workers. These are lower bounds on execution,
not total campaign cost. Of the accounted outside-prefix work, 72,689.02 h
(73.78%) belongs to incomplete settings and is potentially reusable;
25,831.24 h belongs to COMPLETE settings outside their first-K output. Reuse
still depends on successful verification and recovery.

The saved invalid-setting recheck shows eight FAILED markers, four unmarked
settings and one COMPLETE marker, not nine FAILED. The latter COMPLETE marker
does not overrule journal validation.

For a later dispatcher revision, a W2-only option is reasonable, but not yet
reviewed. It must preserve resume identity and distinct collection labels,
validate its wave selection, count fresh live requests and use an appropriate
live/terminal-aware array reference. The present `W2_ARRAY=858016[]` default
names the finished original array. The actual dispatcher, with a bounded PBS
stub that omits finished jobs unless `-x` is used, exits 153 before submitting;
an explicit live `860992[]` reference reaches submission. This is a safe refusal,
not evidence of excess live allocation. The two-case stub does not simulate
reservations and is not a dispatch clearance. Only release a reservation once
both its named array and collector have terminal evidence.

## Handoff

Fable next: repair and test authoritative range ownership, collect the existing
arrays when terminal, and return a concrete fresh-binding recovery package.
Codex then reviews its failure cases and any partial-work importer before new
dispatch. The parent independently replayed both delegated checks, verified the
archive, and closed the node counterexamples. Production code, PBS jobs and
reservations were unchanged by this review. No new fits or population simulation
were run.
