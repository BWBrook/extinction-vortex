# Three-draft review checks

Review target: `e614b238af7c900e678b5382b6c804d0422b15d9`, 14 October 2026.
[Integrated review](../../../notes/astra_three_drafts_review_20261014.md).

- `design_checks.py/json`: seven source/metadata checks, the overlapping seed
  namespaces, factorial and oracle cost arithmetic, retained bank sizes and
  stored-history limitations. Reads source, metadata and previous receipts;
  never imports or runs the simulator.
- `theory_checks.py/json`: exact finite examples showing the two selection
  targets differ, shared-year sampling variance can exceed the proposed
  independent likelihood variance, ESS can decrease as members are added, and
  per-population failures accumulate at the complete-dataset level.

Run from the repository root with system Python; no additional packages:

```bash
python3 analysis/astra/draft_review_20261014/design_checks.py
python3 analysis/astra/draft_review_20261014/theory_checks.py
```

The first receipt records the current HEAD and time, so those fields will change
on a later replay. The exact theory receipt is deterministic. None of these
examples estimates the frequency or size of the effect in the project banks or
empirical populations. No random simulation, fitting, bank payload loading,
empirical statistic or remote-compute dispatch was performed.
