# Caribou artifact review, 14 October 2026

Astra review of `analysis/fable/caribou/` and the case narrative delivered in
`1476781`, at checkout `3437fcd`. This checks the accepted descriptive tranche
against the pinned source files, the earlier recovery review and matrix §8.
No peer artifact or source row was changed, and no model or interval was fitted.

**Finding:** the count crosswalks and four generated tables reproduce correctly.
The case supports its descriptive purpose after two bounded corrections: align
Maligne composition to survey years, and retain the WSI coverage/date notes.
The broader conclusion about limits on identifying abundance feedback does not
depend on changing any count. No further source search is needed for these fixes.

## Actionable findings

1. **P2 — Maligne composition is plotted one calendar year late.**
   `make_caribou.py:116–120,132–136` copies the archive's `year` directly and calls
   the rug “composition survey year”. The pinned `dataprep.Rmd:848–853` explicitly
   adds one to fall and spring survey years before writing
   `recruitment_counts.csv`. All 14 Maligne rows are fall observations: archive
   1999, 15 calves / 53 non-calves, corresponds to the 30 September 1998 flight;
   the final archive 2014 row, 0/5, corresponds to the 3 October 2013 flight.
   The current figure therefore misaligns composition with the count trajectory.
   Keep the original archive year, add a separately named survey-calendar year,
   and plot that field when using the current rug label. The five Purcells winter
   composition rows need no year shift. Explain the survival year convention
   alongside this: Maligne Y represents approximately October Y−1 to September
   Y, whereas Purcells Central Y represents April Y to March Y+1 under the
   documented preprocessing offsets. Do not silently relabel the original data.

   A source-class qualification belongs with this correction. Nine of the 14
   Maligne archive compositions match the preceding Parks flight composition
   exactly; five do not (survey years 2001, 2003, 2004, 2006, 2008). For example,
   archive 2009 is 1/3, while the 2008 Parks flight has 2 calves and 4 non-calves.
   The receipt records every crosswalk. Describe these as archived composition
   summaries from the shared monitoring programme, retaining their OTC/MNKA
   classes, rather than implying every numerator and denominator is reconstructed
   from the displayed Parks group sum. Purcells 1997 and 2004 use MNKA composition,
   including the associated off-survey/track evidence.

2. **P2 — The WSI table drops material survey qualifications.**
   `make_caribou.py:83–96` keeps only `SUMMARY_DETAIL_NOTE`. The omitted
   `SUMMARY_GENERAL_NOTE` records incomplete coverage in 1996; two partial
   surveys, limited areas and an unknown survey date in 2003; an incomplete survey
   and unknown date in 2005; and the pre-2006 South Purcells unit convention in
   2006. The last point survives in the timeline, but the others are absent from
   the new crosswalk. Retain both source-note fields, with their WSI IDs, and
   carry the 2003/2005 date uncertainty explicitly. `2003-03-00` and `2005-03-00`
   are placeholders constructed by the script, not valid dates: keep the supplied
   year/month fields and missing day, plus the source's stronger date-unknown
   qualification. Do not infer a precise flight date. The figure's annual count
   values can remain as shown. Avoid calling every observation a late-winter
   flight; the pinned 1998 date is 1 May.

3. **P3 — Narrow the narrative shorthand and correct two cross-references.**
   In `caribou_case_narrative_20261014.md`, Purcells is panel **b**, Maligne panel
   **a** (lines 33 and 42 are reversed). “Banff has neither” should read “the
   inspected archive contains no Banff survival or composition rows”; annual risk
   sets were not recovered in the inspected sources, rather than demonstrated
   universally non-public. Replace the concluding inference “still unpublished”
   with “not recovered in the inspected public sources” unless a specific
   publication-status source is cited. Qualify the management introduction as
   the **documented actions during the represented decline**; the 2012 transplant
   was an addition, falls after the zero, and retains unresolved historical unit
   identity. In register A5 and the 1997 timeline row, say the low OTC does not
   itself establish a population drop; the coverage evidence does not prove that
   no population change occurred. These are wording corrections to preserve the
   stronger qualifications already present elsewhere in the package.

4. **P3 — State the build boundary accurately.** `NOTE.md:11` says the script
   builds every table. A clean temporary build produces four CSVs and the two
   figure formats; `events_timeline.csv` is a manually compiled, source-checked
   input artifact and is not generated. Correct the documentation; no new build
   machinery is needed.

## Verified facts and retained conflicts

- All nine cached inputs match Fable's recorded SHA-256 and byte counts. **Both
  WSI snapshots contain 92 features and 23 Individuals rows.** All properties
  and geometries are identical, including notes, methods, values and BEST flags.
  Only generated GeoJSON feature IDs and the response timestamp differ. My
  earlier recovery review's “25” was a prose error; its machine receipt already
  contains 23. There are no two missing Individuals rows.
- All **21 Maligne fall flights** reproduce their dates, group-record counts,
  recorded totals and missing-total IDs. The six differences from the Lamb
  archive are 2001 (21/12), 2003 (24/19), 2004 (11/7), 2006 (8/7), 2008 (6/4)
  and 2014 (4/2). Archive 2010 remains absent. ID 378 has blank total/composition
  with date and location present. IDs 423/424 have identical composition but
  different locations; no deduplication is justified. Williams ID 27 remains a
  plausible Maligne attribution with unresolved numerical differences.
- All **13 Purcells annual rows** preserve OTC/MNKA/MC values, BEST flags and
  detail IDs. Archive `MinUsed=1` identifies the four MNKA substitutions in 1996,
  1997, 2004 and 2005; other archive values match OTC. The 2003 MC seven versus
  note ten, multiple BEST values, 2005 OTC zero/MNKA one and 2006 OTC zero all
  remain unresolved or distinguished as appropriate. None establishes a last
  individual death. The historical geographic-unit caution remains necessary.
- **Banff matches 16/16** between Williams ID 28 and the Lamb archive. The 2008
  zero versus April 2009 final avalanche conflict remains visible. The earlier
  direct primary-paper reading supports the avalanche and c. 2002 management
  context; this audit did not re-read that paper or the management pages.
- All **nine survival rows and 19 composition rows** reproduce their archive
  values. Six survival estimates are Maligne 2002–2007; three are Purcells
  1994–1996; Banff has none in these files. Displayed `sd` values round to three
  decimals. They are processed KM/boundary uncertainty, not recovered binomial
  risk sets or confidence intervals. The published nine Purcells collars are
  monitoring totals, not annual KM denominators. Classified non-calves are not
  cows. Shared monitoring and count-reusing IPM outputs remain dependent evidence.
- The six treatment categories contain zeros for Banff 1986–2023, Maligne
  1988–2023 and Purcells Central 1991–2023; earlier rows are **NA**, not zeros.
  The recorded 2012 transplant is under `Purcell South`, 16 adult females and
  three adult males. The separate COSEWIC attribution of nine under Purcells
  Central is preserved as a source/unit conflict, not reconciled by assumption.

## Rebuild and evidence boundary

[The check script](../analysis/astra/caribou_artifact_review/check_caribou.py)
and [receipt](../analysis/astra/caribou_artifact_review/receipt.json) document the
independent tabulations, input hashes and temporary build. All four generated
CSVs and the PNG are byte-identical to the delivered versions using cached
Matplotlib 3.11.2. Both PDFs pass `qpdf --check`; their bytes differ, but PNG
renders at the same resolution are byte-identical. I visually inspected the
rebuilt PNG and PDF render: panels, legends and annotations are legible and
uncropped. The incorrect Maligne rug timing is semantic, not a rendering defect.

Run the check with the two pinned source directories and an output JSON path:

```text
python3 analysis/astra/caribou_artifact_review/check_caribou.py FABLE_SOURCE_DIR ASTRA_SOURCE_DIR OUTPUT.json
```

The receipt records the current local caches and temporary render location.
Pinned snapshots remain outside Git; a future changing WSI download may fail the
intentional hash check. This review reuses explicitly attributed prior source
readings and searches; it does not verify absence of other public records, recover
individual histories, resolve biological identities, or establish a feedback
mechanism. A successful rebuild establishes artifact reproducibility only.

14 October 2026, 16:43 AEDT (Australia/Hobart).
