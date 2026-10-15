# Caribou repairs and nine-series table: follow-up review

Astra, 15 October 2026. Reviewed repair commit `98b771e` at checkout
`b781db17921008724e15f0eca671ea3b767964ef`, against `f2f9ad3` and the two
14 October artifact/table reviews. Scope: caribou repairs and nine-series
table, ledger and rendering only. Sampler and Stage 0 work are outside this review.

**Recommendation: accept for continued manuscript assembly.** The two material
caribou findings are closed, and the readable one-page nine-series deliverable
is complete. Two small editorial items below can be folded into the next
assembly pass; neither requires another analysis or source-recovery round.

## Previous findings and disposition

| Prior finding | Verified repair | Disposition |
|---|---|---|
| Maligne composition rugs one year late | All 14 rows retain `archive_year` and add the correct `survey_calendar_year = archive_year − 1`. All five Purcells winter rows retain the same calendar year. The figure uses the calendar field for composition, keeps archive years for survival, and explains the survival conventions in its footnote. | Closed |
| Archived composition versus Parks group sums | The CSV now calls these summaries from the shared monitoring programme. New A11 retains the nine exact matches and five mismatching survey years, without changing values or treating the Parks sums as reconstructed archive denominators. | Substantively closed; minor prose carry-through below |
| WSI general notes and unknown dates omitted | All detail and general notes match the cached source rows. General notes survive for 1996, 2003, 2005 and 2006, including incomplete coverage, two partial surveys, unknown dates and the historical unit convention. Month/day are separate; 2003/2005 days are blank, with no invented `-00` date. | Closed |
| Narrative/register scope | Panel references are correct; Banff evidence absence and unrecovered risk sets are source-bounded; “still unpublished” is replaced; management is scoped to the represented decline with the later addition identified; 1997 coverage no longer proves no population change. | Closed |
| Build overclaim | NOTE now identifies four generated tables and a manually compiled, source-checked timeline. | Closed |
| Nine-series census and dependence wording | Main table and ledger restrict seasonal age-class maxima to Bryant's 1987–1997 window. The ledger defines IND as observations or summaries with row-specific recoverability. Both use the qualified shared-monitoring statement. | Closed |
| Nine-series table too long for one page | Actual PDF is one landscape A4 page. All nine rows, five columns, caption, dependence note and provenance pointer are present and readable. | Closed |

## Small residual edits

- **MINOR — composition wording carry-through.** The narrative at
  `notes/caribou_case_narrative_20261014.md:81–83` and register at
  `analysis/fable/caribou/conflict_register.md:54–56` still say composition
  comes from “the same surveys as the counts”. Use the corrected CSV's
  “archived composition summaries from the shared monitoring programme”,
  with an A11 pointer where useful. This avoids implying exact survey/denominator
  identity across the five Maligne conflicts and the Purcells MNKA summaries.
  The dependence caution and calf/non-calf distinction should remain.
- **NIT — A11 Markdown row.** The blank line at
  `analysis/fable/caribou/conflict_register.md:26` separates A11 from the table.
  Pandoc parses it as a `LineBlock`, not a table row. Remove that blank line;
  the content itself is correct and retained.

## Verification

[The check script](../analysis/astra/case_repairs_review_20261015/check_repairs.py)
and [receipt](../analysis/astra/case_repairs_review_20261015/receipt.json) record
the inputs, commands, crosswalks, hashes and temporary output locations.

- All eight static source hashes match the manifest. The current cached WSI
  response is `b14dc790…`, with 92 features and **23 Individuals rows**. Its
  declared content fields exactly match the earlier Astra receipt and hash
  `309ac967d022699c26906e48ae9abe34461c63f3fcb85025148ca9059845cc30`.
  These fields include row ID, date fields, method code/name, value, BEST flag
  and both note fields. The new guard accepts changed response-wrapper metadata
  but rejects a changed value, changed general note or missing Individuals row.
  This verifies the declared content contract, not identity of every unused
  GeoJSON property or geometry across the latest download.
- A bounded temporary caribou rebuild produces **four byte-identical CSVs and
  a byte-identical PNG**. The delivered and rebuilt PDFs pass `qpdf --check`
  and produce byte-identical PNG renders at 160 dpi. The Maligne and Banff
  census CSVs are unchanged from `f2f9ad3`; no count reconciliation was silently
  substituted. I visually inspected the repaired PNG and PDF render: the
  shifted Maligne rugs, legends and expanded footnote are readable and uncropped.
- The actual nine-series PDF passes `qpdf --check` and has **one page**,
  841.89 × 595.28 pt. Visual inspection confirms readable text at the declared
  9 pt table setting, with no clipped cells, missing rows or overlapping notes.
  Its extracted Williams IDs are W14, W15, W6, W20, W21, W10, W4, W8 and W9.
  The PDF and Markdown body have identical multisets of **628 normalized
  lexical tokens**; visual inspection checks their placement and grouping.
- The main Markdown is **664 whitespace-delimited words including front matter,
  649 in its body**, versus 3,748 previously. The table's prose is 448 words
  after excluding pipe/separator syntax. The detailed ledger has 3,782 words.
  Its 13 source notes and source list are unchanged from the previous long
  table; the earlier census/dependence corrections are confined to the retained
  table/key. Detailed provenance was moved, not silently discarded or upgraded.

Reproduction:

```text
python3 analysis/astra/case_repairs_review_20261015/check_repairs.py /home/bwbrook/.cache/vortex/caribou_src OUTPUT.json
```

No new external sources were searched. Earlier source adjudications are reused;
this checks their faithful presentation and the specified repairs. The
nine-series PDF was inspected and text-checked, not rebuilt from Markdown.
No peer files, STATUS, source data, scientific settings or empirical results
were edited. Only this review and its check/receipt were written.

15 October 2026, 11:28 AEDT (Australia/Hobart).
