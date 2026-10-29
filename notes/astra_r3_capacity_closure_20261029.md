# Round-3 capacity closure — 29 October 2026

**Recommendation: clear the prior capacity blocker.** At repository `dbb1b85`,
the actual repaired dispatchers, submitter and shared helper close both the
interrupted-size and wholly-unlisted accepted-job paths. No production or PBS
operation was performed. This clears only the capacity component; runner,
archive and stage-identity decisions belong to the other reviews.

The submitter is the enforcement point: before an array request it includes the
array and collector in the required headroom, and immediately before a collector
request it checks that collector's additional CPU. Accepted/resumed jobs are not
requested twice. An unaccepted saved size no longer binds the dispatch plan.

## Verified behavior

The native submitter fixture was run from a private copy: **16/16 passed** under
Bash `5.3.9`. The new harness retains the actual dispatcher, submitter and helper;
it stubs PBS, scientific preflight/seed and summary selection only.

| Case | Observed result |
|---|---|
| Normal W1 = 63, W2 = 811, then resume | 6,994 CPUs; four initial qsubs, zero on resume |
| Saved W2 size 874, no journal; 72 other CPUs | Recomputed to 802 after W1; 6,994 total |
| Accepted W1 array wholly absent from listing | Refused its collector after one qsub; visible rerun ends at 6,994 |
| Accepted W1 collector wholly absent | Refused W2 after two qsubs; visible rerun ends at 6,994 |
| User listing query fails | Nonzero exit, zero qsubs |
| Exact accepted-array query fails | One array accepted; no collector qsub |
| Topup saved size 874, no journal; prior arrays F and 72 other CPUs | Recomputed to 865; 6,993 total |
| Operator-rejected collector resumed with 7,000 CPUs live | Refused the additional CPU; zero new qsubs |

The native suite separately covers a load increase during preflight and an
operator-rejected array on resume. Both refuse the now-over-cap request.
Together these address every genuinely new array/collector entry point in this
delta, including reuse of a bound journal.

One wording qualification: the early preflight capacity check applies to a new
or rejected **array**. A collector-only resume can run preflight before refusing
capacity at the final request gate. The extra collector test observed this
ordering. It creates no new request and is not a cap failure; do not claim every
collector refusal happens before preflight.

## Nonblocking limit: internally incomplete successful listings

`s1b_capacity.sh:12` treats any matching array parent or subjob as evidence that
the accepted array is listed; `live_cpus` then sums only visible subjobs. I
injected successful but inconsistent listings that retained W1's parent while
omitting all, or all but one, of its queued subjobs. The real scripts submitted
7,498 or 7,490 CPUs respectively.

This is **not an observed PBS response or a newly established dispatch blocker**.
PBS documents `qstat -t` as displaying the array object and its non-expired
subjobs. The ordinary all-or-nothing delayed-visibility cases above are fixed.
The injected partial cases specify a stronger fault model than those cases;
the source review and saved receipts do not establish that Kunanyi returns such
an internally incomplete successful response. See the primary
[PBS User Guide, job-array status options](https://2020.help.altair.com/2020.1/PBSProfessional/PBSUserGuide2020.1.1.pdf).

If that stronger fault model becomes relevant, compare the displayed subjob
count with the exact array's `array_state_count` and bound CPU shape, failing
closed on disagreement. Taking known-job visibility and CPU totals from one
listing would also remove the present two-query consistency assumption. Neither
extension is required by the evidence obtained here.

## Reproduction and provenance

Run from the repository root:

```sh
python3 analysis/astra/r3_capacity_closure_20261029/check_capacity_closure.py
```

`capacity_closure_checks.json` contains the complete outputs and exact hashes
for all four reviewed shell files. `native_submit_fixture.json` records the
private-copy native replay. `collector_capacity_resume.json` captures the
additional collector-resume test using the unchanged native fixture's
`scenario()` helper.

Submitter SHA-256:
`ab504d00b583d09e64503cd1d1abe572b62986148ce5a5cfa54a922ca4b8f65c`.
All files created for this review are in the owned memo/evidence paths. Prior
fixtures and receipts were preserved. No scientific simulation, real scheduler
query, allocation, ledger mutation outside temporary fixtures, or remote access
was performed.
