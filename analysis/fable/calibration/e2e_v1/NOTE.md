# End-to-end development benchmark (v1, 9 October 2026, deep-server)

Run in tmux with `e2e_benchmark.py`, on the 2×10^7-draw banks of
`compare_nulls_v1` (same source commit and host record). Two **synthetic**
outer datasets were drawn from each of the ar_cat and iid nulls. Settings:
R_train = R_test = 2,000; K = 2,000; tolerance 1.0; 16 R workers.

| Component, per outer dataset | Wall time |
|---|---|
| Fresh outer selected trajectories, nine populations | about 7 s |
| Library selection | 0.3 s |
| Writing 4,001 datasets | 1 s |
| T1–T4 fits on 4,001 datasets, 16 workers | 63–69 s |

Peak RSS was about 0.86 GB, and there were no fit failures. One outer dataset
costs about 1,100 core-seconds, or 0.27 core-seconds per T1–T4 dataset on
deep-server. The earlier 0.15 s figure was measured on WSL.

**Production estimate** (replaces the withdrawn 1,170-hour figure):
- 7,000 outer datasets × about 1,100 core-seconds ≈ 2,100 core-hours, about
  36 h on 60 cores;
- plus the banks: about 10× larger than v1; see below;
- plus effect calibration;
- plus a descriptive second bank, applied to the empirical analysis only.

**Finding: the v1 banks are too small for synthetic outer data.** For three
or four populations per synthetic outer dataset, the K-th nearest library run
lay beyond tolerance 1.0; the maximum was 1.97, for the red-cockaded
woodpecker. Under the frozen rule, those datasets would be indeterminate.
Production banks must therefore be sized for the spread of outer calibration
summaries, not only for the observed ones. The next run uses 2×10^8-draw banks.

The p-values computed here (0.92 and 0.24 for ar_cat; 0.89 and 0.66 for iid)
come from synthetic null data. They show that the pipeline runs and nothing
more.
