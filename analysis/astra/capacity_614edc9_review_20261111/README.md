# Dispatcher query-status review of 614edc9

**The subsequent concrete dispatcher repair passes all three affected gates.**
Original `614edc9` has the query-status regression below. The repaired working
tree captures `qstat` with an explicit failure branch before grepping, and
closes it on both tested Bash versions.

The helper's three changed tests avoid the SIGPIPE failure while preserving the
explicit `out=$(qstat ...) && grep ...` success requirement. `ref_live()` also
already captures qstat with an explicit failure return before testing output.

Three checks in original `614edc9` do not preserve that requirement:

- `s1b_round3_dispatch.sh:42`, before installing the runner;
- `s1b_round3_dispatch.sh:104`, before releasing old reservations;
- `s1b_topup_dispatch.sh:28`, before releasing named reservations.

In that commit each runs `grep -q ... <<< "$(qstat ...)"`. The command substitution's
nonzero exit status is lost: grep's status governs the test. A failed query
that emits a partial `job_state = F` answer passes. The former pipeline with
`pipefail` refused it.

`check_dispatch_query_status.py` executes the actual topup prefix
through its ledger-release loop, the exact round-3 reservation-release block,
and the actual round-3 prefix through its preinstallation completion loop.
All data and scheduler responses are in temporary directories. Results under Bash 5.3.9 and 4.2.46 are identical:

| Reply | Old | 614edc9 | Repaired working tree |
|---|---|---|---|
| Short F reply, qstat exit 0 | passes | passes | passes |
| F output, qstat exit 2 | refuses | **passes** | refuses |
| F plus 3,000 padding lines, qstat exit 0 | refuses (SIGPIPE) | passes | passes |

For the failed query, the candidate topup prefix actually appends a release
record to its temporary ledger; the old prefix does not. The candidate
round-3 prefix passes all eight completion tests before the install boundary;
the old prefix stops at the first one. These are 54 script runs across the two
shells, three gate paths, three reply cases and three source variants.

The finite repair is to capture the query with its status before grepping:

```bash
out=$("$PBS/qstat" -x -f "$j") && grep -q 'job_state = F' <<< "$out" || { ...; exit 1; }
```

The concrete repair was made by a peer in the shared worktree during review;
this reviewer neither made nor reverted those changes. The updated harness
reads and hashes those actual files, tests all three gates, and verifies that
the hashes remain unchanged throughout. Tested SHA-256:

- `s1b_round3_dispatch.sh`:
  `545c9d37d19a1499c85c9e9e6737ad1e4cdf430de42f666bba68c868c364648f`
- `s1b_topup_dispatch.sh`:
  `7dead4f34805a03894d94dca1054371f72cfb9f0a1355e73566cfd4c74195e83`

No production code was edited by this reviewer. Preserve the existing failure
messages and retain failed-with-matching-output regression coverage.

For urgent recovery, direct `s1b_submit.sh ... resume b` sources the helper,
retains the accepted array and run identity, verifies the array state with an
explicit successful qstat assignment, and can submit only the missing collector.
Use the original settings, output directory, W2, 854 x 8 shape and 48-hour
walltime so its bound run identity matches; require the existing journal to
show the accepted array and no unresolved collector request. This path does
not require installing or invoking either modified dispatcher. A new full-stage
bundle would need new stage identity because these scripts are staged sources;
rerunning the original stage installer would reinstall its old helper.

Run:

```sh
python3 analysis/astra/capacity_614edc9_review_20261111/check_dispatch_query_status.py
```

`dispatch_query_status.json` records the results. This is injected shell-level
failure testing, not evidence that PBS emitted such a partial failed answer in
production. Parent owns helper/native submitter verification, final scope of
clearance and integration. No live jobs, reservations, PBS queries or production
files were changed by this review.
