# Astra: source audit of the canonical nine

13 October 2026. Reviewed `notes/option3_evidence_scan_nine_20261013.md` at
`1fe79ea`, after README, AGENTS, STATUS and the existing 8 October source audit.
Bounded source review only: no empirical fitting, eligibility changes, author
contact or purchase. This memo owns no changes to the scanned note or protocol.

**Recommendation: retain the scan as a discovery ledger, with major corrections
before using its verdicts or constructing priors.** The strongest new leads are
Haley Lake marmots and the original banded-crow histories. The evidence does not
support blanket exclusions of managed populations or blanket claims that their
extinctions were non-stochastic.

## Major findings

1. **Population identity was recoverable further than the scan reports.** The
   existing crane reconciliation was overlooked. The marmot sequence strongly
   maps to Haley Lake, with one newly exposed discrepancy; see below. Kerloch
   and Tall Timbers are independently named in Holmes et al.'s source ledger.
2. **Shared field programmes are not automatically count-derived circularity.**
   Individual encounter histories, nest outcomes and telemetry add information
   absent from annual totals. They can nevertheless share individuals, years,
   observation error and environmental effects with those totals. Separate
   information does not justify treating the two likelihoods as independent.
   Conversely, a demographic parameter inferred only from the same annual
   decline cannot be presented as independent prior evidence.
3. **The scan conflates demographic closure with management and causation.**
   Predator removal changes an external influence on vital rates; collaring
   changes handling exposure. Neither alone adds or removes members of the
   focal population. Counted releases, permanent removals, immigration and
   emigration require their own evidence. Habitat or disease evidence also does
   not establish that demographic stochasticity or abundance feedback was absent.
4. **Several causal summaries are stronger than their sources.** The original
   Swedish woodpecker abstract reports little habitat-area change in 1941–1978,
   winter-loss associations and low reproduction, proposing inbreeding as an
   explanation. It does not establish habitat loss as the cause. The AOU report
   describes annual burning at Tall Timbers and explicitly cautions that local
   decline need not be attributable to habitat alteration. The turtle abstract
   associates declines with public access but does not identify the fate of
   disappearing turtles. Preserve these distinctions.
   [Pettersson 1985](https://www.sciencedirect.com/science/article/abs/pii/0006320785900229),
   [Ligon et al. 1986, pp. 849–850](https://www.srs.fs.usda.gov/pubs/ja/1986/ja_1986_ligon_001.pdf),
   [Garber & Burger 1995 abstract](https://scholarship.libraries.rutgers.edu/esploro/outputs/journalArticle/A-20Yr-Study-Documenting-the-Relationship/991031665380704646).

## Canonical identity, access and limits

`W` denotes the local Williams CSV ID, not a new population identifier.
**PDF** means relevant full-text pages inspected; **HTML** means full article
or chapter text accessed; **AB** means primary abstract only; **ledger** means a
compilation's metadata rather than the underlying field methods. Access claims
refer to this audit. All nine deposited windows and metadata were read directly
from `data/raw/williams2021/population_data.csv`.

| F&H / W; deposited window | Identity and source access | Demographic evidence and dependence | Closure, interventions and unresolved limits |
|---|---|---|---|
| 1 / W14; 1970–1992 | Serengeti plains study population. [Holmes et al. 2005, Table A-1, p. 28](https://eeholmes.github.io/publications/Holmesetal2005.pdf), PDF ledger, identifies adults + yearlings. [Jackson et al. 2019](https://onlinelibrary.wiley.com/doi/full/10.1002/ece3.4798), HTML. | Original Burrows individual histories remain a lead; no historical same-area survival estimate newly recovered. Jackson's 106/121 surviving 12 months concerns 2006–2016 handled dogs, including 67 translocated animals; it is not a historical unmanipulated survival estimate. | Persistence outside the historical study area and later connectivity are supported; the proportion of the historical disappearance due to emigration is not established. Handling alone does not prove opening or cause of disappearance. Retain the prior audit's three Williams fills and historical start/endpoint gaps. |
| 2 / W15; 1981–2000 | **Strong provisional Haley Lake natural-colony mapping**, not Mount Washington. [Bryant 1998, Appendix 7, printed p. 110 / PDF page 123](https://dspace.library.uvic.ca/bitstreams/6ef9deb0-12fa-4d2a-a3eb-628159c696fd/download), PDF visually checked. | Ten consecutive age-summed totals match; one earlier value does not. Individual histories and census-derived survival are distinguished within the thesis. Same study does not make both forms circular. Quantitative leads below. | Appendix 7 records immigrants at Haley: direct evidence against strict colony closure. Island-wide captive removals cannot be assigned to this row without a colony/year ledger. Entire 1981–2000 sequence and final removal history remain unverified. |
| 3 / W6; 1967–1982 | Southern Sweden; [Pettersson 1985](https://www.sciencedirect.com/science/article/abs/pii/0006320785900229), AB; [Holmes Table A-1](https://eeholmes.github.io/publications/Holmesetal2005.pdf), PDF ledger, labels adults. | The original study discusses reproduction, so “no same-population data found” should mean no quantitative rates recovered. Spanish estimates remain transfer evidence requiring age/method matching. | No focal additions/removals established here. Habitat-loss-only explanation is unsupported. Original annual table, observation process and 1982/1983 endpoint discrepancy remain open. The abstract's pairs are not authority to halve or relabel Williams counts. |
| 4 / W20; 1968–1981 | Tall Timbers, Florida. [Holmes Table A-1](https://eeholmes.github.io/publications/Holmesetal2005.pdf), PDF ledger, labels adults; [Ligon et al. 1986](https://www.srs.fs.usda.gov/pubs/ja/1986/ja_1986_ligon_001.pdf), PDF text, corroborates approximately 40 adults in 1970 and disappearance by 1981. | No original-period individual survival series newly obtained; NC/other Florida rates remain transfer evidence. Baker 1983 original account remains unexamined. | Isolation is supported context, not proof of zero dispersal. Annual burning and the report's causal caution prevent a simple fire-exclusion explanation for the full series. No focal addition/removal demonstrated here; census season and group composition remain open. |
| 5 / W21; 1973–1990 | **Kerloch, NE Scotland**, explicitly named in [Holmes Table A-1](https://eeholmes.github.io/publications/Holmesetal2005.pdf). [Parr 1993](https://www.tandfonline.com/doi/pdf/10.1080/00063659309477187), downloaded PDF, methods and Tables 3–4 inspected. | Adults were individually recognized and breeding outcomes observed; this supports a distinct individual-data lead. Parr 1980/1992 rates and return histories remain unrecovered. BTO 0.73 is not newly verified as an independent estimate here. | Crows/gulls were removed in 1986–1989; no plover immigration/removal follows from that fact. No young hatched in those experimental years. Table 3 counts pairs and is not the Williams all-individual sequence; exact conversion and census definition remain open. |
| 6 / W10; 1986–2003 | **Rocky Mountain experimental flock**, official winters 1985–86 to 2002–03 labelled by ending year. [CWS/USFWS 2007 plan, Table 1, p. 13](https://ecos.fws.gov/docs/recovery_plan/070604_v4.pdf), PDF; all 18 adult+young sums agree. | No independent numerical survival parameter recovered for this flock. Cross-fostered birds failed to establish normal conspecific reproduction; a no-recruitment interpretation must distinguish natural reproduction from managed additions. | Additions are documented, including the 1997 ultralight birds; the deposited rise 3→6 is not pure ageing-cohort decay. Predator control alone is a different issue. First count ≤1 is winter 2001–02, preceding count 2; F&H's 16-census window remains unresolved. |
| 7 / W4; 1992–2003 | Wild South Kona/McCandless remnant. [USFWS 2009, I-14–I-15, I-19–I-21](https://ecos.fws.gov/docs/recovery_plan/090417.pdf), PDF, distinguishes wild remnant and released birds. | **0.798 is count-derived, not independent.** Original [NRC 1992, pp. 31–35](https://www.nationalacademies.org/read/2023/chapter/4), HTML, supplies earlier banded-adult evidence; details below. | Egg collection and releases occurred, but inclusion of released birds in the exact F&H/Williams count definition remains a mapping question. One known wild juvenile and unlocated disappearances do not establish a deterministic closed survival process. |
| 8 / W8; 1974–1992 | Connecticut turtle A, one of two isolated study populations. [Garber & Burger 1995](https://scholarship.libraries.rutgers.edu/esploro/outputs/journalArticle/A-20Yr-Study-Documenting-the-Relationship/991031665380704646), AB; [Holmes Table A-1](https://eeholmes.github.io/publications/Holmesetal2005.pdf), ledger, total population, maximum 51. | A mark–recapture programme followed 133 turtles across both sites; a survival analysis of their histories would not automatically equal the annual totals. No such estimate was obtained here. | Public-access association is supported; actual collection/removal of each missing animal is not established by the abstract. Observation estimator, exact A-site mapping and detection remain unknown. |
| 9 / W9; 1974–1992 | Connecticut turtle B, other population in the same study; same access. Holmes ledger maximum 58 matches W9. | Shared programme/exposure warrants a study cluster; reproductive isolation does not establish statistical independence. No same-population vital-rate estimate recovered. | Same causal limits as A. Preserve the previously documented W9 minimum-before-increase discrepancy (44 versus F&H 53); no source value changed. |

## Reproducible Haley comparison and strongest new rate leads

The following are manual transcriptions from Bryant's Appendix 7, checked
against the rendered page, then summed and compared to W15 with Python `csv`:

```text
Year       1987 1988 1989 1990 1991 1992 1993 1994 1995 1996 1997
Adults       12   14   12   12    8    7    9    5    7    5    4
Yearlings     4    1    5    0    3    6    0   10    3    0    0
Young         2   12    0    3    9    0   12   10    0    7    4
Sum          18   27   17   15   20   13   21   25   10   12    8
Williams     28   27   17   15   20   13   21   25   10   12    8
```

This is strong identification evidence, not complete source reconciliation.
Do not correct 1987 automatically. **Bryant Table 2, p. 44**, also reports pooled
adult apparent survival **0.623 (95% limits 0.565–0.678)** under fixed resighting
probability, and **0.629 (0.570–0.683)** with estimated resighting. These are
pooled marked-animal results, not a Haley-only independent prior.

[Bryant & Page 2005, pp. 675–678](https://andrew-a-bryant-services.com/wp-content/uploads/2014/05/bryant-and-page-2005.pdf)
was read through the full-text web extraction. It supplies **known-fate survival
0.74 (95% CI 0.65–0.81)**, or **0.76 (0.68–0.83)** for the seasonal model,
using 1992–2004 telemetry from 15 colonies including Haley. There were 166
marmot–site–year records; the sample mixes ages and sites. Eight animals vanished
with their signals; censoring them can bias survival upward, and the authors'
alternative coding reduced the constant estimate to 0.72. These are substantially
better qualified leads than the scan's unbounded conference-summary values,
but the pooled scope and overlap must remain visible.

[NRC 1992, Box Table 2 and accompanying text](https://www.nationalacademies.org/read/2023/chapter/4)
resolves the crow lead: **0.81 = 22/27** survived annual transitions from **five
banded McCandless adults**, described as a minimum. A separate time-weighted
calculation gives **0.90**, based on two of five surviving nine years. These are
small, earlier individual-history summaries, not the 1992–2003 decline fit;
there is no reported confidence interval to transfer directly. Treat 0.81 and
0.90 as alternative summaries of shared evidence, not two independent studies.

The later recovery plan's **0.798 = 1 − 0.202** corresponds to its reported
log-count slope, not a separate survival experiment. If that slope is a natural
log rate, the discrete multiplier would instead be `exp(-0.202) ≈ 0.817`.
This arithmetic distinction does not rescue independence or validate either
number as survival. No new regression was fitted.

## Provenance and stopping point

The local Dryad CSV and readme were already available. CSV SHA-256 remains
`fce2d8a232460b56f5566c41c03038a3f99ca978e0620a49867e5016a34df168`.
The readme labels these raw abundance data; it does not validate every field
method. [Dryad's live landing page](https://datadryad.org/dataset/doi:10.5061/dryad.jwstqjq8c)
was checked. Williams' full XML identifies the supplement
`ECE3-11-7069-s001.docx`, but Table S1 was **not obtained**: no local DOCX found,
PMC returned a download challenge, Europe PMC supplement requests timed out,
and the attempted Wiley supplement path returned 404. These access outcomes
do not establish that the supplement is unavailable through other normal routes.

Verification used direct CSV reads; downloaded PDF text extraction; visual
checking of the Haley, CJS and official crane tables; an asserted 18/18
crane-total comparison; and primary
abstract/full-text browsing. Source files and page renders are temporary under
`/tmp/option3-nine-audit/`; no copyrighted PDFs were added to the repository.
Stable retrieval hashes: Bryant thesis
`a263400aae0287fad07b61e4d94d165332a4ae90aac7a9c1930a86ffc7358d79`;
crane plan `48460931790624c911e2a8f559fbab55c61be9639f0c4cdb17ae2632be8d3256`;
crow plan `fd9cdc40b2bd28a662d9c7884616b2783cb2b1955fb9f3329a34cb84edfbda31`.

The useful next data tranche is finite: recover Haley's full count/removal
ledger and resolve 1987; recover Parr's original return/breeding histories and
count transformation; inspect the crow band histories and census/release
definition. Turtle and Baker originals remain access/provenance gaps. These
are evidence-recovery tasks, not permission to redesign production or exclude
series. The parent integrates this audit; no external response was requested.

Recorded: 13 October 2026, 14:25 AEDT, Australia/Hobart.
