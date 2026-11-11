# Capacity-helper and collector-only resume review

Main finding: `notes/astra_capacity_helper_review_20261111.md`, board 3236.

- `native_submit_checks.json`: unchanged 17-check submitter suite replayed in
  temporary source copies under Bash 5.3.9 and 4.2.46. Both pass. The old helper
  also passes the original 3,000-line case on the current kernel, recording the
  buffering dependence rather than treating that negative control as universal.
- `check_collector_resume.py`, `collector_resume_checks.json`: start with the
  old helper and a 30,000-line padded listing; the actual submitter accepts an
  array but refuses its collector. Replace only the helper, resume, and require
  one collector for the existing array plus an idempotent further resume.
  Repeat with capacity full, hidden array and failed exact-query controls.
  Four scenarios on each of the two shells pass.
- `parent_dispatch_query_status.json`: parent repeat of the independent
  reviewer's actual dispatcher-gate matrix, including old/candidate/committed
  repaired code at all three gates and short/large/failed matching query replies.

Reproduce from the repository root:

```sh
python3 analysis/astra/capacity_helper_review_20261111/check_collector_resume.py
python3 analysis/astra/capacity_614edc9_review_20261111/check_dispatch_query_status.py
```

The native suite command is `python3 s1b_submit_fixture.py` from a temporary
copy of the kunanyi scripts; `FIX_BASH` selects the older shell. Copies avoid
overwriting committed native fixture receipts. No PBS, heavy compute,
production edits or scientific fits occur.
