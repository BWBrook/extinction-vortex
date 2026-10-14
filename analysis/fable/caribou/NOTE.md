# Caribou descriptive deep dive (14 October 2026)

Accepted by Astra in board 1625, with Barry's decision of 14 October quoted in
board 1623. The evidence base is
`notes/astra_caribou_recovery_review_20261014.md` and
`notes/option3_recovery_matrix_20261013.md` §8.

| File | Content |
|---|---|
| `caribou_sources.json` | URLs, byte counts and SHA-256 of the pinned public snapshots, with Astra's hashes where she recorded them. Lamb files are pinned to Git `f069f1f6` only. The live WSI file hash differs from Astra's snapshot, but its 23 Individuals rows are identical to her receipt. The snapshots are kept outside the repository. |
| `make_caribou.py` | Builds every table and the figure from the snapshots, refusing to run if a snapshot hash differs. Run with `uv run --with matplotlib python make_caribou.py SOURCE_DIR`. |
| `maligne_census.csv` | By year: Parks Canada fall flight dates, group records, sum of recorded totals and blank-total IDs, alongside the Lamb archive count and Williams ID 27 |
| `purcells_central_census.csv` | By year: WSI OTC, MNKA and MC (with BEST flags, detail IDs and notes) and the Lamb archive count |
| `banff_census.csv` | Williams ID 28 against the Lamb archive (16/16 match), with the 2008/2009 note |
| `demographic_evidence.csv` | Herd-year survival (est, sd) and calves per classified non-calf, each with a provenance note |
| `events_timeline.csv` | Dated, sourced events and interventions, with evidence tags and coding |
| `conflict_register.md` | Value conflicts A1–A10, missing evidence B1–B6, and interpretation limits C |
| `caribou_case.png`, `caribou_case.pdf` | Three-panel small multiples: counts by source class, rugs for survival and composition years, and Banff event lines |

Narrative: [`notes/caribou_case_narrative_20261014.md`](../../../notes/caribou_case_narrative_20261014.md).

**Verification.**
- The Maligne fall sums equal those in Astra's receipt: 2001 = 21,
  2003 = 24, 2004 = 11, 2008 = 6, 2014 = 4.
- Banff crosswalk: 16/16.
- WSI Individuals rows match Astra's receipt.
- The figure was inspected after rebuilding.
- Every count is a tabulation of source rows. Nothing is deduplicated,
  imputed or fitted.
