# Option 3: bounded Phase II source audit

Astra, 13 October 2026. Base checkout `1fe79ea`. This independently checks the
first-pass candidate note, not the whole candidate universe. Papers, public
repository metadata and selected public data files were inspected. No model was
fitted, no author contacted, and no empirical test or production design approved.
Downloaded inspection copies are temporary; the pinned URLs, hashes and checks
below make the findings recoverable.

## Decision-relevant result

**There is enough public material for a finite data-recovery tranche. There is
not yet a verified, ready-to-fit extinction case with complete individual
demography.** Prioritize Maligne and Purcells Central caribou, then Palmer as an
explicitly open breeding-population comparator. The first scan understates public
caribou availability but overstates how directly its vital rates map to our `s`
and `f`. It also understates the geographic information in penguin resightings.

Do not exclude a source merely because census and vital-rate work came from the
same monitoring programme. Individual fates can add information beyond the count
trajectory. The relevant questions are which observations generated each
estimate, whether observations overlap, and whether the proposed prior has
already used the target counts. An IPM posterior conditioned on those counts
cannot be reused as an independent prior without accounting for that dependence.

## 1. Caribou: a concrete archive, with important qualifications

[Lamb et al. (2024), Ecological Applications, e2965](https://doi.org/10.1002/eap.2965)
analyses 40 subpopulations over 1973–2023 and explicitly links data/code. It
combines abundance, calf recruitment, collar survival and recovery actions.
Its functional-extirpation category is **fewer than 10 adult females or fewer
than 20 animals**, not an observed zero. Figures distinguish observations from
IPM trajectories; missing-year predictions use other years and priors. Tonquin
inputs include results from an earlier IPM. Thus neither the headline number of
extirpations nor the fitted abundance curves establishes our eligible sample.
The paper also states that raw data are archived; the inspected release supports
the narrower availability statement below.

### What is actually retrievable

The paper's [Zenodo DOI](https://doi.org/10.5281/zenodo.10437005) resolves through
the API to version **10834654**, title *ctlamb/CaribouIPM_BCAB: Lamb et al. 2024
Zenodo commit for Ecological Applications Paper v3*. It lists one 134,172,742-byte
ZIP, MD5 `be72a5915ad813b1893ef93bbf570170`. I inspected the linked
[PublicationRepov3 release tree](https://github.com/ctlamb/CaribouIPM_BCAB/tree/PublicationRepov3)
at commit **`f069f1f6f0705dc954a30a4cecbd9ff9bba7f2e3`**, downloading selected
small files, not the full ZIP. The recursive Git tree returned 342 entries and
`truncated=false`.

The [clean input directory](https://github.com/ctlamb/CaribouIPM_BCAB/tree/f069f1f6f0705dc954a30a4cecbd9ff9bba7f2e3/data/clean)
contains:

| File | Observed fields/use | Evidence status |
|---|---|---|
| `counts.csv` | herd, year, count, sightability, sd, minimum-count flag, corrected estimates/bounds | Downloaded input table; count is sometimes a minimum rather than a complete census |
| `survival.csv` | herd, year, est, sd | Downloaded processed annual survival summaries; **not individual histories** |
| `recruitment_counts.csv` | herd, year, season, type, calves, adults, recruitment | Downloaded age-composition observations, not births per breeding female |
| `transplants.csv` | herd/year, sex-age numbers, citation/comment | Downloaded intervention record; spelling and year conventions require reconciliation |
| `treatments.csv`, `herd_sightability.csv`, sex-ratio tables | Additional input files | Presence verified; contents not comprehensively audited |

**The linked Git release does not include `data/raw/`.** Its `.gitignore`
explicitly excludes that directory. The preparation code references
`data/raw/surv.csv`, individual entry/exit dates and outcomes, plus count and
treatment sources which are absent from the inspected tree. This is a verified
gap in the linked release, not proof that individual records are unavailable
elsewhere or absent from the uninspected ZIP. The prepared tables still make a
substantial improvement over paper estimates alone.

### Herd-level overlap observed in these files

These are **file row counts and year labels**, not inferred sample sizes or
validated calendar intervals. Recruitment may have multiple surveys in a year.
Repeated post-zero surveys do not lengthen the pre-extinction trajectory.

| Herd | Census rows; labelled span; endpoint | Survival rows; labelled span | Recruitment rows; labelled span | Immediate implication |
|---|---|---|---|---|
| Maligne | 24; 1988–2021; first zero 2018 | 6; 2002–2007 | 14; 1994–2014 | Best recovery target; demographic coverage ends before disappearance |
| Purcells Central | 13; 1994–2009; first zero 2006 | 3; 1994–1996 | 5; 1994–2004 | Second target; particularly short survival baseline |
| Banff | 16; 1986–2008; last zero 2008 | 0 | 0 | Census crosswalk target, not joint-demography success |
| George Mountain | 8; 1999–2010; includes zeros | 0 | 0 | No joint evidence in these clean files |
| South Selkirks | 27; 1991–2019; last zero 2019 | 0 | 24; 1991–2018 | Supplementation/control history; survival absent here |
| Purcells South | 23; 1993–2018; last count 4 | 15; 1992–2019 | 21; 1994–2017 | Supplemented, no census zero in this table |
| Klinse-Za | 12; 1996–2023; last count 127 | 21; 2002–2022 | 22; 1996–2023 | Rich recovery comparator, **not an extinct endpoint** |
| Quintette | 8; 2008–2023; last count 96 | 21; 2002–2022 | 21; 2002–2023 | Same; do not concatenate with `Quintette Full` without boundary audit |

Maligne's endpoint has stronger support than a single zero:
[Parks Canada's monitoring summary](https://parks.canada.ca/pn-np/ab/jasper/nature/conservation/retablissement-caribou-recovery/cariboureport-programmecaribou?wbdisable=true)
reports repeated unsuccessful surveys in 2018–2020. The last collared adult
female died in March 2018, with signs of other living caribou then present.
Its [2020 report](https://parks.canada.ca/pn-np/ab/jasper/gestion-management/plan/2020)
retains death **or movement out of the range** as possibilities for the last
animals. Treat this as well-supported local disappearance, not verified deaths
of every animal. Winter access restrictions and earlier ecosystem management
also belong in the external-driver/intervention record; absence from a wolf
reduction table does not establish an unmanaged population.

### Why the preparation code matters

The [data-preparation source](https://github.com/ctlamb/CaribouIPM_BCAB/blob/f069f1f6f0705dc954a30a4cecbd9ff9bba7f2e3/data/dataprep.Rmd)
documents adjustments that must accompany any imported summary:

- Survival intervals use biological-year offsets; Maligne/Brazeau/Tonquin use
  fall timing, whereas most herds use the April–March year.
- Survival estimates with at most two monitored animals are dropped. At boundary
  estimates, uncertainty is added through a constructed bootstrap, and zero
  survival estimates are changed to 0.5. These are documented analysis choices,
  not original individual-event data or universally literal sampling errors.
- Some census inputs use minimum counts; corrected estimates can borrow pooled
  sightability. Calf/adult ratios share survey information with census estimates.
- Spring/fall recruitment years are shifted; treatment years are shifted by one
  to represent demographic response. A treatment-table date is therefore not
  automatically the intervention's calendar start. The transplant table gives
  Purcell South augmentation in 2012, while the treatment summary starts 2013.

These observations do not audit or invalidate the published IPM. They show why
its prepared data cannot simply supply independent `s`/`f` priors. Calves per
adult combine breeding, calf survival and a sex/age denominator; mapping them to
our current unstructured recruitment parameter requires an explicit census and
life-cycle definition. Collar-based survival summaries can remain useful after
their provenance and uncertainty adjustments are understood.

### Crosswalks to Williams: useful evidence, not silent replacement

- **ID 28:** all 16 year/count pairs match the named Banff input exactly.
  This is strong numerical corroboration. The archived terminal label is 2008;
  the first-pass note's 2009 avalanche endpoint still needs primary-source/date
  reconciliation. Do not shift the year or claim the original LPD citation has
  been recovered.
- **ID 27:** Maligne is plausible but the sequences **do not match**. Differences
  (Williams / archive) are 2006: 11/7; 2007: 7/5; 2008: 7/4; 2009: 3/4;
  2010: 6/no row; 2011: 7/6; 2012: 5/6. Keep identity and version mapping unresolved.

## 2. Palmer Adélie: joint public observations, open-population problem

Three [Palmer ERDDAP](https://pallter-data.marine.rutgers.edu/erddap/index.html)
CSV endpoints were successfully downloaded. EDI landing pages encountered an
access challenge; the programme's own ERDDAP metadata and data were accessible.

| Endpoint (append `.csv` for data; `.html` for access form) | Retrieved observations |
|---|---|
| [AdeliePenguinCensus](https://pallter-data.marine.rutgers.edu/erddap/tabledap/AdeliePenguinCensus.html) | 1,489 rows; 1991-11-03–2017-11-24; study/season, date, island, colony, breeding pairs |
| [AdeliePenguinAdultandChickCounts](https://pallter-data.marine.rutgers.edu/erddap/tabledap/AdeliePenguinAdultandChickCounts.html) | 1,467 rows; 1992-01-26–2018-01-27; matching colony keys, pairs, chicks, census time |
| [AdeliePenguinBandsSeen](https://pallter-data.marine.rutgers.edu/erddap/tabledap/AdeliePenguinBandsSeen.html) | 2,442 resighting rows; 499 distinct band numbers; 1991-10-23–2005-10-31; island/colony, breeding status, sex, band year |

The linked dataset DOIs resolve to EDI packages `knb-lter-pal.87.7`, `.88.7` and
`.90.3`, respectively. These are actual public observations, not merely a promise
of data access.

**Season joins must use `study_name`**, because November pair counts and January
chick counts occupy different calendar years. Summing the nine Litchfield colony
counts yields 15 pairs in PAL0506, four in PAL0607 and the first island-wide zero
in **PAL0708**. This corrects the scan's 2006/07 zero. Repeated zeros follow.
Williams ID 25 agrees with the overlapping island sum except 1998
(Williams 338, retrieved sum 325) and 1999 (322 versus 301). Thus Litchfield is a
strong crosswalk lead, with two unresolved source/version differences.

The resighting metadata says chicks were banded on **Humble**. However,
resightings are not confined to Humble: the retrieved table contains 28
Litchfield records, spread from PAL9192 through PAL9900, plus records from other
islands. Do not describe the available observations as geographically
unconnected to Litchfield. Equally, those few records do not demonstrate a
Litchfield survival time series extending to extinction. The inspected table is
positive sightings, not a verified complete release/effort history. The band-year
field has both older values (87–90) and zero, and its metadata wording is
ambiguous. The programme also flags potential effects of flipper bands on
survival. Resolve these before estimating detection, apparent survival or
dispersal.

Chicks creched per breeding pair are a real additional outcome, but they are
neither adult recruits next year nor independent of the pair-count denominator.
An empty breeding colony may reflect deaths, skipped breeding or redistribution.
[Cimino et al. (2025)](https://doi.org/10.1007/s10980-025-02088-y) supplies
primary evidence on landscape/snow differences and disappearing subcolonies;
it does not turn a breeding-site zero into closed demographic extinction.
Use this candidate to test whether an open, stage-structured interpretation is
feasible, with environmental covariates and detection, rather than declaring it
eligible under the existing closed null.

## 3. Barro Colorado antbirds: historical tables, not yet ready data

The [Willis (1974) primary text, public full-text copy](https://www.researchgate.net/publication/271804823_Populations_and_Local_Extinctions_of_Birds_on_Barro_Colorado_Island_Panama)
is accessible. Table 2 covers antbird populations in 1961–1970; the ocellated
antbird still had one female in early 1971. Barred woodcreeper disappearance is
described separately, with none found in the 1971 census. Do not attach the
antbirds' demographic tables to that woodcreeper endpoint.

The paper has nest/fledgling evidence, territorial turnover and losses.
Territorial turnover explicitly includes movement, and loss can include
undetected movement. Its Table 12 replacement calculation solves for required
nests per female; that derived quantity is not directly observed annual
fecundity. Thus the scan's generic “adult mortality” shorthand conceals a useful
but imperfect apparent-survival observation process.

**Disposition:** lower-priority manual recovery. Transcribe Tables 2, 3, 10–12
with denominators, periods and footnotes, then obtain a primary endpoint source
for the ocellated antbird. No machine-readable individual histories were located
in this bounded check. The accessible text improves feasibility, but zero-count
eligibility and uncertainty remain unresolved. Shared marking/census work alone
does not make the evidence circular.

## 4. Wittmer, Sinclair & McLellan 2005: prior-art claim needs precision

The [full primary paper](https://wildlifescience.ca/wp-content/uploads/2022/11/wittmer-oecologia.pdf)
does examine inverse density dependence across 15 caribou subpopulations. Its
growth statistic is **`[log(N_2002) - log(N_initial)] / elapsed years`**;
Figure 3 relates that statistic to final population size, and Figure 5 uses
density in suitable habitat. It also uses pregnancy and cause/season of
radio-collared mortality to distinguish food limitation, predation-sensitive
foraging and secondary-prey predation. It is not a within-population acceleration
test conducted on 15 complete extinction trajectories.

Our inference: this is important prior art for small-population decline and
mechanistic triangulation, but not the same matched-outcome conditional-null
test. Final abundance contributes to both the growth statistic and its size
covariate; that regression alone is not independent demographic corroboration.
Pregnancy and mortality observations provide distinct information despite being
from the same programme. Novelty should concern what an outcome-conditioned,
externally informed test adds, not the discovery that small caribou populations
can decline rapidly. The paper itself discusses geographic variation in
predators/habitat as a competing explanation for among-population patterns.

## Finite next recovery assignment

1. **Caribou:** preserve the pinned release and build a provenance/availability
   matrix for Maligne and Purcells Central, with Banff as the Williams crosswalk.
   Recover original census dates, survey/known-alive distinctions, collar
   denominators and uncertainty provenance, and intervention/movement records.
   Check whether another public deposit supplies the omitted individual files.
   Stop with a decision on usable baseline summaries versus missing records;
   do not reconstruct an IPM or begin prior fitting.
2. **Palmer:** preserve these three CSVs and dictionaries; join by season,
   island and colony; resolve the two Williams count discrepancies and band
   cohort/effort meanings. Determine whether release histories and inter-island
   search effort are public. Stop with a decision on an open-population
   comparator, not a declaration of closed-population eligibility.
3. **Historical antbirds:** keep queued behind these two. The finite deliverable
   is a verified table transcription and endpoint source, not a broad review.

These are recommendations for the parent/peer handoff. No scientific target
change is made here, and no author-contact request is implied.

## Reproduction and retrieval record

The executable check is
[`phase2_source_checks.py`](../analysis/astra/a_screen_review/phase2_source_checks.py),
with observed output in
[`phase2_source_checks.json`](../analysis/astra/a_screen_review/phase2_source_checks.json).
It preserves source hashes and rejects silent changes to the six data inputs.
From the repository root:

```bash
python3 analysis/astra/a_screen_review/phase2_source_checks.py --output analysis/astra/a_screen_review/phase2_source_checks.json
```

Public input copies remain in `/tmp/option3_phase2_audit`; use `--refresh` to
download them again. A source-version change is a review condition, not an
automatic replacement of these results.

The minimal checks used Python's `csv.DictReader`, dropping ERDDAP's units row,
grouping caribou rows by `herd`, and grouping Litchfield census rows by
`study_name`. Counts were not interpolated. Exact comparison used the existing
`data/raw/williams2021/population_data.csv`, retaining only non-NULL year fields.
For each Williams year, compare against the named herd's `count` or summed
Litchfield `num_breeding_pairs`; report missing years and unequal values.

Retrieve pinned caribou inputs from:

```text
https://raw.githubusercontent.com/ctlamb/CaribouIPM_BCAB/f069f1f6f0705dc954a30a4cecbd9ff9bba7f2e3/data/clean/<filename>
https://api.github.com/repos/ctlamb/CaribouIPM_BCAB/git/trees/f069f1f6f0705dc954a30a4cecbd9ff9bba7f2e3?recursive=1
https://zenodo.org/api/records/10437005
```

Retrieve Palmer metadata using
`https://pallter-data.marine.rutgers.edu/erddap/info/<datasetID>/index.json`
and observations using
`https://pallter-data.marine.rutgers.edu/erddap/tabledap/<datasetID>.csv`.

SHA-256 of downloaded files:

```text
counts.csv                        43c3e55ad82fe70783e417c39f2e7ff27f33fa9657a846f409a138f59dc40629
survival.csv                      d45a4fc39d579c2e0815671910567073ce9e7212e03109e81447beba4e7748da
recruitment_counts.csv             1784440c7664205e71f68bbf312579ef4a8cd0422682111e166ae73f63a8ac68
AdeliePenguinCensus.csv            b4ef04e2275ea779fc8fe54fa13528dc2052d37dd88a60c811d54c7601f67b16
AdeliePenguinAdultandChickCounts.csv 40485a328af51727e019c2cd99e4795c098499fef86a9d4b2af435a6de5373e0
AdeliePenguinBandsSeen.csv         8e72cff0cdc8a9b31bbfaf4b8aa59f4ec982937ca0d9010c3f43caf58b7840ff
```

Search coverage was limited to these named candidates, their cited papers and
linked primary repositories. Failure of a web fetch, absence from the inspected
Git tree, and absence of a data source from this bounded search are separate
claims. Other first-pass candidates remain unreviewed.

Completed 13 October 2026, 14:21 AEDT (Australia/Hobart).
