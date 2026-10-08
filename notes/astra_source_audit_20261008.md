# Astra source audit: first execution tranche

8 October 2026. The first tranche is authorized; the production design is not
frozen. This audit preserves deposited values and separates verified mappings
from unresolved source interpretation. It does not assign survival priors or
decide which populations to exclude.

## Findings that change the next step

1. The crane's deposited sequence matches the official Rocky Mountain flock
   table when each winter is labelled by its ending year. Applying F&H's
   first-census-at-or-below-one rule gives a preceding count of two, resolving
   that earlier table discrepancy. The 16-versus-17-census window remains open.
2. The MARSS author-distributed wild-dog series has missing counts in 1971,
   1972 and 1978, where Williams supplies 66, 54 and 24. All 19 shared,
   nonmissing values match. F&H report one interpolation, without naming its
   year. Starting in 1973 would give their 20-year window with just the 1978
   gap, but this is a hypothesis, not recovered provenance.
3. The assertion that all nine are complete, all-individual censuses is too
   strong. Original-study descriptions do not yet establish every deposited
   row's unit, age class, observation process, closure or intervention history.
   In particular, a source narrative in pairs does not prove the deposited
   woodpecker row is in pairs; marking animals does not prove an annual turtle
   value is a count of captures. No conversion is justified yet.
4. The crow plan's 79.8% survival estimate is calculated from the same decline
   trajectory. It cannot serve as an independent literature prior for that
   trajectory. The earlier 81% estimate is only a candidate lead until its
   underlying data, age class and temporal overlap are checked.
5. T5 has no exact single coefficient to transcribe from the inspected F&H
   text. Its z score and separately plotted curves do not uniquely specify
   the fitted contrast, covariance structure or test convention.

## Input and census ledger

The pinned Williams input is unchanged:
`data/raw/williams2021/population_data.csv`, SHA-256
`fce2d8a232460b56f5566c41c03038a3f99ca978e0620a49867e5016a34df168`.
Williams metadata calls these individual/full-population counts, except that
the crane unit is a peak winter count. Those are source labels, not our
independent validation. Each row below is a local population or study series,
not necessarily a species-wide extinction.

| F&H / Williams | What the audit supports | What remains unresolved before using M0 biologically |
|---|---|---|
| FH01 / W14, wild dog | Serengeti study population; 1970–1991 author-distributed counts agree wherever observed. Williams adds three filled values and a 1992 zero. [MARSS pinned data](https://raw.githubusercontent.com/atsa-es/MARSS/bf06ca8e4d2bbeb0655cfcb9a8562ae7963d3d53/data/wilddogs.rda); original study [Ginsberg et al. 1995](https://doi.org/10.1098/rspb.1995.0199). | Original F&H start year, fill rule and endpoint provenance; age/season/closure. No transferable numeric survival prior verified. |
| FH02 / W15, marmot | Bryant's work combined marked animals, telemetry and population counts; it warns that count-based survival confounds survivors with immigrants. [Bryant thesis abstract](https://dspace.library.uvic.ca/items/aaf4e5e1-58c9-4b89-b9c3-40c1e6ec2c8d). | Exact colony and mapping of the 1981–2000 sequence, which extends past the 1998 thesis; age class, effort correction and 21-versus-20-census window. No prior assigned. |
| FH03 / W6, middle spotted woodpecker | The original abstract describes 15–20 pairs and a 1967–1974 census followed by decline during 1975–1983. [Pettersson 1985 abstract](https://www.sciencedirect.com/science/article/abs/pii/0006320785900229). | Unit conflict/unresolved: Williams says individuals. The original figure/table was not obtained, so the row is **not** relabelled as pairs. Interpolated year and 1982/1983 endpoint convention unresolved. No prior assigned. |
| FH04 / W20, red-cockaded woodpecker | The AOU report describes about 40 adult birds at Tall Timbers in 1970 and disappearance by 1981, citing Baker 1983. Cooperatively breeding groups also contain helpers. [Ligon et al. 1986, pp. 849–850](https://www.srs.fs.usda.gov/pubs/ja/1986/ja_1986_ligon_001.pdf). | Baker's original two-page account and exact annual row remain untraced; adult versus seasonal all-age census, group composition and closure. Do not convert the counts to breeding pairs. No prior assigned. |
| FH05 / W21, golden plover | Original citation identifies the northeast Scotland decline. The accessible abstract describes return rates and winter losses that may include mortality or emigration. [Parr 1992](https://doi.org/10.2307/3676443); [abstract access](https://eurekamag.com/research/007/881/007881115.php). | Original table/census timing and exact row transformation were not inspected. Breeding-population scope is supported at abstract level, but age/season and closure need the original methods. Apparent return is not direct survival. No numeric prior assigned. |
| FH06 / W10, whooping crane | All 18 Williams counts match the Rocky Mountain adult-plus-young totals, winters 1985–86 through 2002–03, using the ending year. [USFWS recovery plan, Table 1, p. 13](https://ecos.fws.gov/docs/recovery_plan/070604_v4.pdf). | Experimental flock/intervention history must enter model assessment. First <=1 is winter 2001–02; preceding total is two. Exact F&H 16-census window remains open. No prior assigned. |
| FH07 / W4, Hawaiian crow | Wild South Kona/McCandless individuals: the 1992–2003 figure matches the deposited trajectory. Separate releases did not establish a breeding population; species persisted in captivity. [USFWS 2009, pp. I-14–I-15 and I-19–I-21](https://ecos.fws.gov/docs/recovery_plan/090417.pdf). | Confirm the treatment of released birds in the original F&H record and census availability. The reported 79.8% survival uses the same decline and is excluded as an independent prior. Earlier banded-bird estimate requires provenance review. |
| FH08 / W8, wood turtle A | One of two biologically separate populations in the same protected watershed and mark–recapture study. [Garber and Burger 1995 abstract](https://scholarship.libraries.rutgers.edu/esploro/outputs/journalArticle/A-20Yr-Study-Documenting-the-Relationship/991031665380704646). | Annual statistic not traced: marking alone does not distinguish unique observations, minimum known alive or estimated abundance. Age/sex coverage and detection/closure unresolved. No prior assigned. |
| FH09 / W9, wood turtle B | The other population in that shared study; both experienced the recreation-opening exposure and synchronous declines. [Same primary abstract](https://scholarship.libraries.rutgers.edu/esploro/outputs/journalArticle/A-20Yr-Study-Documenting-the-Relationship/991031665380704646). | Same observation gaps as A, plus the 53-versus-44 minimum-size-before-increase discrepancy. Shared process/error dependence is plausible, not estimated. Record a common study cluster and plan a sensitivity; do not assert independence or dependence from reproductive isolation alone. |

The first threshold census gives 149 pre-endpoint/scaling observations and
149 annual growth transitions in the current data. Six of nine zero-inclusive
windows match the published duration; wild dog, marmot and crane remain
different. F&H's printed nine monitoring durations sum to 155; subtracting one
terminal census per series gives 146, whereas their text reports 148 nonzero
censuses. This arithmetic is another reason to recover the exact inputs rather
than infer a unique window from the table alone.

The crow never increases in the deposited trajectory. Its Table 1 entry of 12
has the paper's no-increase footnote; treating it as an observed increase is
incorrect. The turtle-B smallest pre-increase count remains 44 in Williams
versus 53 in F&H. These facts do not justify changing any source value.

## Small, reproducible source comparisons

The [transcription/comparison script](../analysis/astra/source_audit/check_sources.R)
checks the pinned MARSS bytes and a manually transcribed official crane table,
writing [wild-dog differences](../analysis/astra/source_audit/results/wilddog_comparison.csv)
and the [crane check](../analysis/astra/source_audit/results/crane_comparison.csv).
The crane table was checked visually against the downloaded PDF. The crow
figure was also visually checked; that comparison is not claimed as an
independent digitization with quantified extraction error.

Primary PDFs were inspected in temporary local storage, not redistributed in
the repository. Retrieval was 8 October 2026:

| Source | Locator | SHA-256 of inspected bytes |
|---|---|---|
| Fagan and Holmes 2006 | [Author PDF](https://faculty.washington.edu/eeholmes/Files/FaganHolmes2006.pdf), pp. 53–58 | `4b63e6e92d9780c6431af58fa145f89a95e4e626882ee9c1c63db5997a4f7d9d` |
| MARSS wilddogs.rda | [Pinned revision bf06ca8e](https://raw.githubusercontent.com/atsa-es/MARSS/bf06ca8e4d2bbeb0655cfcb9a8562ae7963d3d53/data/wilddogs.rda) | `cb6e06203eb7bcaa98a1d0bb2c1fd1aaae29690481809f5d1b8d269da32aaf87` |
| USFWS crane plan 2006 | [Official PDF](https://ecos.fws.gov/docs/recovery_plan/070604_v4.pdf), Table 1 | `48460931790624c911e2a8f559fbab55c61be9639f0c4cdb17ae2632be8d3256` |
| USFWS crow plan 2009 | [Official PDF](https://ecos.fws.gov/docs/recovery_plan/090417.pdf), Figure 2 | `fd9cdc40b2bd28a662d9c7884616b2783cb2b1955fb9f3329a34cb84edfbda31` |

No author was contacted, access agreement entered, source count replaced or
new forward-cohort outcome opened. Some original articles remain inaccessible
in this bounded pass. The source-audit delegates initially overstated two unit
claims; direct adjudication reduced both to unresolved mappings. Those stronger
claims are not adopted here.

## Estimator and protocol handoff

The [Astra reconstruction record](../analysis/astra/stage_b/README.md) gives the
54 predeclared fits and checks. The four slope targets are printed to three
decimals, so a difference of 0.0005 is the comparison tolerance; a nearby value
outside that interval does not pass. Neither a successful optimizer status nor
agreement between agents establishes the historical estimator.

F&H describe marginal ML, AR(1) errors and population empirical-Bayes slopes.
They do not fully identify the random-effects covariance used in every model,
the residual convention, or T4's refit-versus-subset operation. Their Method 3
and Figure 4 give early and late curves and z = 2.3; there is no single printed
period coefficient matching protocol T5. Keep it unresolved rather than invent
a transcription or substitute an interaction statistic silently.

Requested work for Fable's protocol 0.4:

- Replace the unconditional all-individual/full-count assertion with this
  provisional ledger. Keep census unit, age class, observation, closure,
  intervention and shared-study cluster as separate fields.
- Leave literature survival centres unassigned until the source and census
  class match; exclude same-trajectory fitted survival as an independent prior.
- Record Stage B as not passed. Resolve the historical estimator/T5 and
  original-input question before an empirical discrepancy test.
- Retain the agreed independent reference construction, fixed-n validation and
  unattainable-effect repair. Synthetic calibration development can proceed,
  but it does not establish empirical model adequacy.

Any decision to replace a failed historical reconstruction with a newly defined
estimator changes the scientific claim. It needs an explicit design amendment,
with the source uncertainty and changed target visible to Barry.
