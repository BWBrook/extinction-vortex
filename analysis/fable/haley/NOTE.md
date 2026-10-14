# Haley Lake descriptive deep dive (14 October 2026)

Protocol: [`notes/vortex_haley_deep_dive_protocol_20261014.md`](../../../notes/vortex_haley_deep_dive_protocol_20261014.md).
Astra's review: `notes/astra_haley_protocol_review_20261014.md`, which said to
proceed with production.

| File | Content |
|---|---|
| `haley_source.json` | Transcription of Bryant (1998) Appendices 7, 11 and 12 for Haley Lake, plus the Williams ID 15 series. A source recheck reported by Fable from the PDF (SHA-256 `a263400a…`), made after exposure to Astra's transcription and not blinded; numerical agreement with it is verified. |
| `source_table_annual.csv` | Per year 1981–2000: the Williams total, the Bryant age-summed total, stage counts, tagged pups, immigrants and litters, each with a source note. Missing values are blank, not zero. |
| `source_table_transitions.csv` | Per transition t→t+1: exposed n and survivors s, tagged and count-derived, for non-pups (App. 12) and pups (App. 11) |
| `conflict_register.md` | Value conflicts A1–A7, missing values B1–B6, and the unquantified-uncertainty notes C |
| `make_haley.py` | Builds both tables and the figure. Run with `uv run --with matplotlib python make_haley.py`. |
| `haley_case.png`, `haley_case.pdf` | Four-panel figure: (a) counts, (b) stage composition, (c) tagged persistence s/n, (d) litters and immigrants |

Narrative: [`notes/haley_case_narrative_20261014.md`](../../../notes/haley_case_narrative_20261014.md).

**Corrections incorporated from Astra's review:**
- explicit n and s columns;
- the figure plots s/n, with genuine zeros (0/3, 0/7) shown and gaps where
  n = 0;
- transitions labelled t → t+1;
- missing years left missing;
- conflict flags (‡);
- uncertainty stated as unquantified;
- the transplant is "not established as a Haley removal";
- the count-derived rows are labelled as same-programme summaries.

**Remaining limits:**
- 1981–86 and 1998–2000 unsourced;
- the 1987 conflict;
- no removal ledger;
- detection unknown by year;
- no individual histories.

**Second-round corrections** (Astra's artifact review,
`notes/astra_haley_artifact_review_20261014.md`):
- panel (a) is retitled "Annual totals: Williams and Bryant", and the
  seasonal-maxima convention is scoped to Bryant's 1987–1997 values in a
  footnote;
- the conflicting 1989 yearlings are flagged ‡ in panel (b), and the register
  states which conflicts are annotated;
- the 8/9 label is moved clear of the 1990 pup marker;
- register A3 is reworded so the reason stays unresolved;
- narrative wording:
  - "recorded immigration, including a breeding episode that Bryant attributed
    to immigration";
  - "reproduction was episodic";
  - the pup cohorts are not observed as yearlings the following year, with no
    death asserted;
  - the McQuillan and Franklin accounts' linkage is left unresolved;
- the transcription is described as a source recheck reported after exposure,
  with numerical agreement verified.
