# Haley artifact review

**Recommendation: accept the descriptive case study with the small corrections
below.** It meets the finite descriptive scope. No numerical reconstruction,
new source hunt or additional inference is needed. There is no numerical or
workflow blocker; apply these corrections during final assembly and rebuild
the figure once.

Reviewed at `ec72dd0330b6acd440aa85d2507c28e465ed2020`:
`analysis/fable/haley/` and
[the case narrative](haley_case_narrative_20261014.md), against the already
primary-source-verified
[Astra transcription](../analysis/astra/a_power_review/haley_source_excerpt.json).
The [QA script](../analysis/astra/artifact_review_20261014/haley_checks.py) and
[30-check receipt](../analysis/astra/artifact_review_20261014/haley_checks.json)
record the checks and input hashes. Only this memo and those QA files were
created. No peer artifact was edited.

## Findings, ranked by consequence

**MINOR — narrow the biological wording to the observations.** Narrative
lines 72–74 describe “dependence on arrivals”. Nine recorded immigrants and
one reported immigration-enabled breeding episode establish movement and a
specific breeding opportunity; they do not establish general demographic
dependence on immigration. Replace this with **“recorded immigration,
including a breeding episode that Bryant attributed to immigration.”**
“Reproduction/pup production was episodic” is also more precise
than deriving recruitment from litter counts (lines 39–42).

At lines 52–53, say **“none of the tagged pups in the 1991 and 1996 cohorts
was observed as a yearling in the following year”**, retaining 0/3 and 0/7.
This avoids assigning the disappearance to the cohort's starting calendar
year or asserting death. At lines 65–66, keep the McQuillan/Franklin accounts'
linkage unresolved, rather than describing one established transplant in two
accounts. Their donor colony remains unknown and no Haley removal is coded.

**MINOR — scope the census-method label to the verified source window.**
`make_haley.py:66` labels the entire 1981–2000 panel as summed seasonal
age-class maxima. That method is documented for Bryant's record, not verified
for the Williams-only years. Use **“Annual totals: Williams and Bryant”**
for panel (a), and explain in its caption that Bryant's 1987–1997 values are
sums of seasonal age-class maxima with the marked-animal accumulation caveat.
Original census conventions remain unrecovered for 1981–1986 and 1998–2000.
The shading and two 1987 totals themselves are correct.

I inspected both the committed PNG and a 180-dpi rendering of the committed
PDF. The plots are readable, with intact footnote and legends. One small
local collision remains: the `8/9` annotation for the transition beginning
1990 touches the green `2/2` pup marker. Move that annotation clear while
rebuilding; no change to plotting values or layout design is needed.

**MINOR — make conflict annotations and unresolved causes exact.** Register
line 14 promises that every conflict touching a plotted value is marked ‡.
Only the two tagged-persistence conflicts carry that symbol; A1 has a separate
1987 annotation. In A2 the seven apparent survivors are not plotted, but the
conflicting **five yearlings in 1989 are plotted in panel (b)**. Add a small
A2/‡ reference to that stage segment and identify it in the register, or
explicitly state which conflicts the figure annotates and name the unflagged
1989 counterpart. Do not say A2 is wholly unplotted.

Register A3's assertion that the rows do not count the same animals at the
same census is stronger than the evidence. Replace it with **“these entries
cannot jointly be read as consistent counts of the same survivors at one
census; the reason is unresolved.”** A transcription error, revision or
different inclusion rule has not been distinguished.

**Evidence limitation — agreement does not establish extraction independence.**
The JSON and accompanying notes report Fable's re-extraction from the PDF.
The delivered values agree with Astra's earlier source-checked extraction,
and the full PDF hash matches the actual cached primary source. That is
verified. The files alone do not establish the process used for a fresh
extraction, and Fable produced them after exposure to Astra's review and
transcription. Describe this as **a reported source recheck after exposure,
with numerical agreement verified**; do not present it as blinded extraction
or as independent biological evidence. No repeat extraction is required to
finish this descriptive artifact.

## Verified results and stopping point

- All 20 Williams ID 15 annual values were independently read from the raw
  CSV; species identity and both endpoints agree. All ten 1988–1997 Bryant
  matches reproduce. The 1987 18-versus-28 discrepancy is retained.
- Every transcribed annual and transition array agrees with the source
  receipt. Tagged totals are 97/64 and 24/11 in exposure/survivor order;
  count-derived totals are 123/83 and 55/30. The CSVs keep separate `n` and
  `s` columns; the figure correctly plots `s/n`.
- **Eight of eleven years have litters**, with zeros in 1989, 1992 and 1995.
  Totals of 17 litters, 59 pups and nine recorded immigrants are correct.
  The source-text value 58 remains in the conflict register.
- All 15 persistence points have correct transition years and values.
  Genuine 0/3 and 0/7 points remain visible; zero-risk cohorts are gaps.
  Missing stage years are blank, and 1987 immigration remains unavailable.
  No intervals, fitted rates, empirical test statistics or imputed values
  were introduced. The preserved source conflicts are unchanged.
- A rebuild in a temporary directory produced **byte-identical CSVs and
  PNG**. The rebuilt and committed PDFs produce identical raster images;
  the committed PDF passes `qpdf --check`. Matplotlib 3.11.2 matches the
  committed PDF's producer version. All 30 source/artifact checks passed.

The case's observation, inference and future-model boundaries are otherwise
appropriate. Complete the bounded text/annotation corrections, regenerate
the figure and perform a targeted visual check. The unresolved source
conflicts and terminal mechanism remain limitations, not reasons to reopen
the protocol or begin a fitted analysis.

Recorded: 14 October 2026, 15:07 AEDT, Australia/Hobart.
