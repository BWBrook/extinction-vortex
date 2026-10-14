# Option 3 source-recovery matrix: Maligne, Purcells Central, Banff, Haley Lake

Source-recovery matrix by an AI agent (Claude, delegated by Fable), 13 October 2026, for Astra's review. Public sources only: no contact, sign-up or purchase; no model fitted; no test statistic computed. Sums quoted are descriptive tabulations of source rows. No existing project file was modified. Downloads: `/tmp/claude-1000/-home-bwbrook-papers-project/2114b555-0c74-405f-bb3d-7860a2e979f1/scratchpad/recovery_downloads/<source>/` (hashes in section 7).

Evidence tags: **[P]** primary source read directly; **[D]** downloaded file inspected; **[S]** search/fetch summary only; **[U]** unverified or inferred. Conflicting values sit in separate columns and are not reconciled. "Lamb archive" = Zenodo 10.5281/zenodo.10437005 / Git `f069f1f6` `data/clean/*.csv` (identical files, see 0.1).

## 0. Headline findings

1. **No public deposit found with caribou individual collar histories.** The Zenodo concept record has four versions. The two with files were downloaded and listed with `unzip -l`: v1 `10437006` (52,867,464 B, md5 `5adcd7cf...` matches Zenodo, 306 entries) and v3 `10834654` (134,172,742 B, md5 `be72a591...` verified, 343 entries); v2 `10439543` has no files [D]. Neither ZIP has `data/raw/`, `data/annual_data_updates/` or `jags/output/`. v3's six `data/clean` CSVs and `dataprep.Rmd` are byte-identical (sha256) to the pinned Git files [D]. Individual-level content is limited to `survival.csv` (herd, year, est, sd). `tables/demog.csv` is IPM posterior output (2,025 rows, 41 herds; Maligne 47 rows 1973-2019, Purcells Central 34 rows 1973-2006, Banff 43 rows 1973-2015) and cannot serve as an independent prior [D]. The code reads `data/raw/surv.csv` and agency spreadsheets `data/annual_data_updates/data/*.xlsx` (sheet "Survival": entry/exit dates) [D, `prepupdates.R`, `dataprep.Rmd` l.44, 108], none of which is shipped. Lamb et al. 2024's data statement names only this Zenodo record [S].
2. **Public herd-level census sources exist beyond the Git release and change the census picture** (sections 1-2): the Parks Canada open dataset "Caribou population - Jasper" (group-level aerial records 1988-2017) and BC's public Wildlife Species Inventory (WSI) layers (herd-level late-winter summaries with census class and collar notes; individual telemetry locations).
3. **The Lamb `count` column mixes census classes.** `dataprep.Rmd` l.1010-1030 sets `count` to the minimum-number-known-alive (`MinCount`) when the sightability-corrected survey estimate is below it, and flags `MinUsed=1` [D]. For Purcells Central the BC WSI rows confirm this: archive 1996/1997/2004/2005 values (17/14/6/1) equal BC "MNKA" values, not the observed total counts (13/2/3/0) [D].
4. **Haley Lake**: Bryant (1998) is a **PhD dissertation** (UVic record "Doctor of Philosophy in Biology", 138 PDF pages), not an MSc [D]. The 2018 TRU MSc thesis in this literature is McAdie (captive-program health), not Haley counts. The URL Astra used for Bryant & Page 2005 (`andrew-a-bryant-services.com/...`) now returns a 301 redirect to an unrelated domain; I did not follow it. A Wayback copy was read instead; DOI `10.1139/z05-055` confirmed via CrossRef [D].
5. **Haley-specific individual-based rates exist in the thesis** (annual tagged-animal survival with n for 1987-1996; juvenile survival; Appendix 16 telemetry fates), but they are not independent of the Appendix 7 counts that match Williams ID 15.
6. **Williams ID 27 = Maligne is now well supported** (1998: 68 matches both the archive and the Parks Canada file; 2013-2018 values match Parks Canada text), but the 2006-2012 values differ across all sources (section 1.1).

## 1. Maligne caribou herd (Jasper, Alberta) - priority 1

### 1.1 Census (a)

Survey: Parks Canada annual **fall helicopter survey (late Sept to late Oct, during the rut)**, reported as **minimum counts**; the herd is "too small to use statistical modelling, only minimum counts" [P: Parks Canada caribou report page, 2017-2020 summary; saved `parkscanada_jasper/cariboureport.html`]. Group-level records also include March "recruitment" flights 2007-2013 (6-25 March) [D]. Lamb treats Maligne as a "fall herd" (survival year = Oct to Sep) [D, `dataprep.Rmd` l.207].

Columns are separate sources. PC-CSV = sum of group "Total number of individuals" on the single fall "rut" flight date, from `jasper_np_alpine_caribou_population_1988-2017_data.csv` (Open Government Canada, dataset `8d2849d9-a723-46c1-b94b-ed4a76e78195`, Open Government Licence) [D, my tabulation]. PC-text = Parks Canada web text; PC-chart = approximate (+/-1) values read from the published chart image 2007-2024 [D-figure].

| Year | Williams ID 27 [D] | Lamb `count` (sightability; MinUsed) [D] | PC-CSV (flight date; groups) [D] | PC-text / chart |
|---|---|---|---|---|
| 1988 | - | 40 (0.99; 1) | 40 (10-07; 6) | |
| 1993 | - | 41 | 41 (10-08; 12) | |
| 1996 | - | 40 | 40 (10-02; 9) | |
| 1998 | 68 | 68 | 68 (09-30; 15) | 68 [S, 2002-03 report] |
| 2000 | - | 41 | 41 (10-19; 8) | |
| 2001 | - | 12 | 21 (09-28; 5) | |
| 2003 | - | 19 (0.57) | 24 (09-26; 6) | 19 implied [S] |
| 2004 | - | 7 (0.33) | 11 (09-28; 3) | |
| 2005 | - | 8 | 8 (09-21; 2) | |
| 2006 | 11 | 7 (0.5) | 8 (10-11; 3) | |
| 2007 | 7 | 5 | 5 (10-04; 1) | chart ~5 |
| 2008 | 7 | 4 (0.5) | 6 (10-18; 3) | chart ~6 |
| 2009 | 3 | 4 | 4 (10-09; 1) | chart ~4 |
| 2010 | 6 | no row | 6 (10-15; 3) | 6 [S, 2009-13 report]; chart ~6 |
| 2011 | 7 | 6 (0.99; 1) | 6 (10-22; 2) | chart ~6 |
| 2012 | 5 | 6 | 6 (10-04; 1) | chart ~6 |
| 2013 | 5 | 5 | 5 (10-03; 1) | 5 [P]; chart ~5 |
| 2014 | 2 | 2 | 4 (10-28; 2 groups, identical composition 1M+1F) | 2 [P]; chart ~2 |
| 2015 | 3 | 3 | 3 (10-14; 1) | 3 [P] |
| 2016 | 3 | 3 | 3 (10-11; 1) | 3 [P] |
| 2017 | 3 | 3 (0.99; 1) | 3 (10-14; 1) | 3 [P], "October 2017" |
| 2018 | 0 | 0 | file ends 2017 | 0: three flights 2018, two 2019, one 2020 found no caribou, tracks or signs [P] |
| 2019-21 | - | 0, 0, 0 | - | 0 |

Gaps (Lamb archive): 1989-92, 1994-95, 1997, 1999, 2002 (no survey, funding) and 2010. Williams 27 contains 1998 then 2006-2018. Unresolved: why 2001/2003/2004/2008 and 2014 differ between the Parks Canada file and the archive; whether the two 2014 groups are duplicates. COSEWIC 2014 App. 3a/3b lists Maligne "*40" (2 generations) and "*5" (most recent), `*` = minimum count [S].
**Endpoint**: last observation Oct 2017 (scat DNA: collared adult female, her 2015 male calf, 2016 and 2017 female calves = four individuals; three counted on the flight). The collared female was found dead March 2018 "but we observed signs of other live caribou at the site"; first zero count fall 2018 [P: same page]. Astra reports the 2020 annual report keeps "death or movement out of the range" open [S via Astra]; I could not confirm that wording.

### 1.2 Demographic estimates (b)

| Item | Values | Denominator and uncertainty | Type |
|---|---|---|---|
| Adult-female survival, Lamb `survival.csv`, year label Y = Oct(Y-1) to Sep Y [D, inferred from dataprep offsets] | 2002: 1.00 (sd 0.214); 2003: 1.00 (0.128); 2004: 0.714 (0.171); 2005: 0.75 (0.217); 2006: 0.75 (0.217); 2007: 0.667 (0.272) | Kaplan-Meier (`survfit`, 12-month, staggered entry) with Greenwood SE; for est=1 the sd is a constructed bootstrap; herd-years with <=2 animals dropped. n is not in the file. sd values are arithmetically consistent with n = 4, 7-8, 7, 4, 4, 3 [U]. | collar-based, processed |
| Collar numbers (Parks Canada, not at-risk n) | Oct 2001: 4 adult-female GPS (pilot); Oct 2002: 7 GPS in Maligne (+1 VHF kept); Fall 2004: 3 Maligne after redistribution; Aug 2007: 3 (2 GPS, 1 VHF); Aug 2009: 1 VHF; later 2 VHF | counts of collars deployed | [P: saved page `parkscanada_jasper/cariboureport.html`; line numbers 286, 329, 353, 234, 188, 149 of its text extraction] |
| Recruitment, Lamb `recruitment_counts.csv` (calves / non-calf animals, fall OTC, 14 rows) | 1994 10/31; 1997 3/37; 1999 15/53; 2001 6/35; 2002 4/8; 2004 4/15; 2005 1/6; 2006 1/7; 2007 2/5; 2008 0/5; 2009 1/3; 2010 1/3; 2013 1/5; 2014 0/5 | Denominator is non-calf animals (bulls and yearlings included) [D, `dataprep.Rmd` l.650], not cows. Year label = survey year + 1: the rows for 1994/1997/1999/2001 match PC-CSV calves and totals of the preceding fall exactly (10/41, 3/40, 15/68, 6/41), as do 2006, 2008, 2010, 2013, 2014 rows. Rows 2002, 2004, 2005, 2007, 2009 have the same or similar calf numbers but fewer non-calf animals than the PC-CSV group sums (totals 12/19/7/7/4 vs 21/24/11/8/6) [D, my comparison]. | count-derived |
| PC-CSV March flights (calves / total, Maligne) | 2007 1/5; 2008 0/5; 2009 2/4; 2010 1/4; 2011 0/4; 2012 1/6; 2013 1/4 | group-level; age/sex cells often blank (e.g. "Adult - Male" blank in 127 of 525 rows), so sums are incomplete | count-derived |
| Pregnancy/fecundity per breeding female | none for Maligne recovered | | - |
| DeCesare et al. 2011 (Conserv. Biol. 25:365-373, `10.1111/j.1523-1739.2010.01609.x`) | PVA for Banff, Brazeau, Maligne, Tonquin with mean adult-female survival and calves per breeding-age female | Full text closed (Unpaywall); only the abstract was read; values and n not obtained | [S/U] |
| IPM output | Lamb IPM (Maligne 1973-2019) and Parks Canada IPM (Tonquin only) | fitted to the same counts, survival and recruitment | **not independent** |

### 1.3 Interventions, movements (c)

- Lamb `treatments.csv`: applied=0 for all six recovery-action types (wolf/moose reduction, sterilization, pen, feed, transplant) for 1988-2023 (NA before 1988) [D]. This table omits access management.
- Parks Canada: delayed access in all caribou habitat since 2014; Maligne-Brazeau range closed 1 Nov-28 Feb; Phase I action plan 2005-07 (dynamic speed limits, lithium chloride trials on the Maligne Lake road and Hwy 93, track-set routes); wolves collared (Signal, Medicine, Maligne/Brazeau packs) but no Maligne-specific wolf control reported; conservation breeding proposed 2020-22 for the Tonquin/Brazeau herds, no captive Maligne animals [P/S: `cariboureport.html`; `breeding_strategy.pdf` pp. 7-8].
- Immigration/emigration: no collared caribou moved Maligne-Tonquin or to Banff (1988-91: 29 caribou-years; 2001-05: 29 caribou-years); genetics show some historic exchange (parent-offspring links, 2009-13 report); over >10 years of DNA monitoring only rare male movement and no female movement detected (2014-16 report) [P: `cariboureport.html` l.300-301 and summaries].

### 1.4 Individual histories (d)

No Maligne collar or fate file found: not in Zenodo; Movebank Data Repository search for "caribou" returned 6 records, none Jasper/Banff/Purcells (the "Mountain caribou in British Columbia" record, `10.5441/001/1.p5bn656k`, is South Peace *northern* herds) [D, DSpace API]; Dryad/Zenodo API searches found no Maligne item [D]. The Parks Canada dataset is group-level, not individual. "Caribou scat - Jasper" (`2f5d1704-...`) covers 2016 only, columns undocumented, not downloaded [S]. Parks Canada states full progress reports are "available upon request"; not requested.

### 1.5 Feasibility (e)

A census-compatible baseline is available now for the **count trajectory** (annual fall minimum counts 1988-2017 with survey dates; group-level age/sex partly classified), but it is a minimum count of all classes, not female-only. Source-specific **survival** exists only for 2002-2007 from about 3-8 collars per year, with no raw histories and no usable CI, ending 5-11 years before disappearance (counts 19 to 5); **recruitment** is calves per non-calf animal in 14 fall surveys, not per breeding female. Per-capita fecundity, adult-female sex ratio and post-2007 survival must be transferred (Tonquin/other Jasper herds; DeCesare 2011 values if obtained). All Maligne rates were measured during the decline (counts 41 to 5, 2000-2008), so any density feedback is already embedded; Parks Canada attributes the decline to altered predator-prey dynamics (external driver), which a closed no-feedback null cannot absorb. Final loss is unclassified (death vs movement). **Verdict: census usable; rates need transfer.**

## 2. Purcells Central caribou herd (BC) - priority 2

### 2.1 Census (a)

Survey: BC late-winter helicopter total counts (March; May 1998; April 2002, 2004, 2006) with tracks; mark-resight sightability: WSI notes cite average SCF 1.23 (=1/0.813, Kinley 2004), Hatter Table 1 lists PC scf 0.86, Wittmer used 0.87 pooled; all kept separate [P: Hatter 2006 report pp. 1-3; D: BC WSI]. Sources: **WSI** = BC public layer `WHSE_WILDLIFE_INVENTORY.SPI_SURVEY_SUMMARIES_SV` (WFS, `POPULATION_UNIT_NAME='Purcell Central'`, 92 rows, none secured) [D]; **Hatter** = Hatter 2006 (BC MoE draft, "Mountain Caribou 2006 Survey Results", Appendix 1 = counts plus tracks, Appendix 2 = estimates) [D]; OTC = observed total count, MNKA = minimum number known alive, MC = SCF-adjusted estimate.

| Year | WSI OTC | WSI MNKA / MC / official | Hatter App 1 / App 2 | Lamb `count` (MinUsed) | Other |
|---|---|---|---|---|---|
| 1994 | 15 | MNKA 18 (obs + 3 from tracks) | 15 / 18 | 15 (0) | |
| 1995 | 15 (3 of 3 collars seen) | MC 18 | 15 / 18 | 15 (0) | Wittmer 2005 T2: 15 (JHE 15; 3/3 collars) |
| 1996 | 13 (3 of 3) | MNKA 17 (obs + 4 tracks) | 13 / 17 | 17 (1) | |
| 1997 | 2 (0 of 2 collars seen; both located later) | MNKA 14 (obs + 12 caribou seen "north of the study area" before/after survey) | 2 / 14 | 14 (1) | |
| 1998 | 5 (3 of 3) | MC 6 | 5 / 6 | 5 (0) | |
| 2000 | 5 | MC 6 | 5 / 6 | 5 (0) | |
| 2002 | 5 | MC 6 | 5 / 6 | 5 (0) | Wittmer T2: 5 (JHE 6; 0/0 collars) |
| 2003 | 6 | MC 7 (row note cites "SCF-adjusted estimate (10)") | 6 / 10 | 6 (0) | |
| 2004 | 3 | MNKA 6 (obs + 3 tracks: 1 calf, 1 cow, 1 other adult) | 3 / 6 | 6 (1) | |
| 2005 | 0 | MNKA 1 (+1 from tracks) | 0 / 1 | 1 (1) | COSEWIC 2014 App 4b: 0 (2005) |
| 2006 | 0 | official 0 | 0 / 0 | 0 | BC Oct 2021 table: "Extirpated in 2006" |
| 2007 | 0 | official 0 (Kinley 2007) | - | 0 | |
| 2009 | 0 | official 0 (DeGroot 2009) | - | 0 | |

Units: animals, all classes (adults, calves; sex partly classified). Endpoint: first OTC zero March 2005 with one animal inferred from tracks; first official zero April 2006 (a count, not an observed final death); no fate record for the last animals. WSI row notes are truncated at 255 characters by the service. Hatter's 1997 "2" is the true OTC (0 of 2 collars seen), not a typo. COSEWIC 2014 (extirpated 2005), Hatter (extirpated, 2006 analysis), BC 2021 (2006) and the archive (first zero 2006) differ on the endpoint year because they use OTC, MNKA, and official-estimate zeros differently.

### 2.2 Demographic estimates (b)

| Item | Values | Denominator and uncertainty | Type |
|---|---|---|---|
| Collared sample | Wittmer et al. 2005, Can. J. Zool. 83:407-418, Table 1: Purcells-Central 03/94-02/99, 9 collared (5 F, 4 M), 405 radiolocations (324 F, 81 M), 15.47 animal-years (11.24 F, 4.23 M), F mean 2.25 +/- 1.93 y/individual | counts of animals and years | [P, `wittmer2005_cjz.pdf`] |
| Adult-female survival | **Not reported by Wittmer** (Table 5 requires >=4 collars/yr; Purcells-Central absent). Lamb `survival.csv` 1994: 1.00 (sd 0.269); 1995: 1.00 (0.274); 1996: 0.667 (0.272) | KM/Greenwood, label Y = Apr Y to Mar Y+1 [D, inferred]; sd consistent with n=3 [U]; WSI: "3 of 3 collared caribou observed" 1995, 1996, 1998 and "0 of 2" in 1997 | collar-based, processed |
| Pregnancy | Wittmer Table 3: 1994 1.00 (3/3); 1997 0.67 (2/3); mean 0.84 +/- 0.17 | 6 females | individual-based (serum progesterone) |
| Calves | Wittmer Table 4 (% calves, late-winter, 1995-2002): 0.00, 7.69, 0.00, 0.00, 0.00, 0.00 (1995, 1996, 1997, 1998, 2000, 2002), mean 1.28 +/- 1.28 | percent of animals counted | count-derived |
| Calves (Lamb `recruitment_counts.csv`, 5 rows) | 1994 2/13 (OTC); 1996 1/12 (OTC); 1997 1/13 (MNKA); 2003 1/5 (OTC); 2004 1/5 (MNKA) | non-calf denominators; conflicts with Wittmer 1997 (0.00) because MNKA counts animals seen outside the survey | count-derived |
| WSI composition | e.g. 1994 Ad F 10, Ad M 1, unclassified 2, Juv 2; 1995 Ad F 8, Ad M 4, unclassified 3; 1996 Ad F 10, Ad M 2, Juv 1; 1998 Ad F 2, Ad M 3; 2000 Ad F 1, Ad M 3, yearling 1; 2002 Ad F 2, Ad M 3 | same flights as the census | count-derived |
| IPM | Lamb `demog.csv` (1973-2006); Wittmer lambda 0.88 (1995-2002, from census) | uses the same counts | **not independent** |

### 2.3 Interventions, movements (c)

- BC Oct 2021 herd table (`bc_caribou_herds_population_estimates.pdf`): Purcell Central 0, 2006, observed total count, "Extirpated in 2006"; the management-actions column is empty [D]. Lamb `treatments.csv`: no applied actions 1991-2023 (NA before 1991) [D].
- COSEWIC 2014 Table 5 lists Purcells Central "Augmented 2012" ("9 caribou in March 2012; all transplanted caribou died or left the area and died"; footnote 9: Purcells Central "considered part of Purcells South range in COSEWIC (2002)") [S]. Lamb `transplants.csv` records the 2012 release under **Purcell South** (16 adult F + 3 adult M) [D]. Both post-date the zero, so no effect on the 1994-2006 series, but unit identity differs across sources.
- Boundary/identity notes in WSI: 1996 one of five track points (Old Tom Mtn) lies in Purcells South range; 1997 MNKA includes 12 animals seen north of the study area [D].
- Immigration/emigration: no quantitative exchange rate recovered; Wittmer describes isolated subpopulations [S/U].

### 2.4 Individual histories (d)

BC WFS layer `SPI_TELEMETRY_OBS_NONSENS_SP` is public (738,209 features overall; caribou `M-RATA` 144,768): project "1987-1999 - Caribou - Telemetry - Purcell Mountains" (16,049 records dated <=2006 under project names containing "Purcell"; fields ANIMAL_ID, SEX, MARK_METHOD, RADIO_FREQUENCY, OBSERVATION_DATE, NOTE; ATS/Lotek GIS collar and VHF "Telemetry data" notes). I retrieved 10,000 of the 16,049 and found **no entry/exit/outcome fields**: the only note matching DEAD/dead/ortality in the whole Purcell caribou project is one "ANIMAL DEAD" (animal 4, 1996-06-26). Herd (Central vs South) is not a field. So location histories are public, fate histories are not [D]. `SPI_SURVEY_OBS_NONSENS_SP` holds 10,541 caribou survey points [D, hit count only].

### 2.5 Feasibility (e)

The census is the best-documented of the four: 11 late-winter surveys 1994-2006 with OTC/MNKA/MC classes, collar sightings and age/sex composition, plus an endpoint survey series. Source-specific survival rests on about 3 collared animals per year over 1994-1996 with no CI (and Wittmer excluded the herd), so adult survival must be **transferred** from Purcells South (Wittmer Table 5: multi-year mean 0.55 +/- 0.10; annual 0.29 +/- 0.17 [1993-94], 0.67 +/- 0.19, 0.75 +/- 0.22, 0.50 +/- 0.25 [1997-98]; column header shows "(13)", whose meaning the caption does not define) or other BC herds, with its own decline-phase bias. Calf data are 5-6 surveys of 2-15 animals (0-20 percent). Every rate was measured while counts fell 15 to 5 (lambda 0.88), so measured rates may already embody the feedback under test. The herd is also the smallest series (peak 15-18), so annual per-capita rates have very large sampling variance. **Verdict: census usable now; rates need transfer.**

## 3. Banff caribou herd: crosswalk to Williams ID 28 - priority 3

| Year | 1986 | 1989 | 1992 | 1994 | 1995 | 1996 | 1999 | 2000 | 2001 | 2002 | 2003 | 2004 | 2005 | 2006 | 2007 | 2008 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Williams ID 28 [D] | 29 | 22 | 24 | 19 | 17 | 8 | 3 | 5 | 4 | 2 | 4 | 5 | 6 | 5 | 5 | 0 |
| Lamb Banff `count` [D] | 29 | 22 | 24 | 19 | 17 | 8 | 3 | 5 | 4 | 2 | 4 | 5 | 6 | 5 | 5 | 0 |

16 of 16 pairs equal (compared row by row from the local Williams CSV and the pinned `counts.csv`). All Banff archive rows have `MinUsed=0` and no sightability, i.e. raw survey counts. Independent corroboration: COSEWIC 2014 App. 3a gives Banff 1986 *29 and 1996 *8 (`*` = minimum count), "most recent" **2009: 0**; footnote 15.1: "Data based on annual maximum counts and telemetry studies" [S].

**Terminal-year adjudication: unresolved.** Evidence: Parks Canada states "The last 5 Banff caribou died in a 2009 avalanche" [P: `population.html`]; COSEWIC 2014 text "confirmed extirpated in 2009 ... last five individuals ... killed by an avalanche" citing Hebblewhite et al. [S]; press places it April 2009, Molar Creek area [S]. The archive/Williams zero is labelled **2008**, 2007 = 5. Candidate readings, none verified: (i) year label = winter-season start, so 2008 = the 2008-09 season with 0 as the post-avalanche state (then 5 animals were alive until April 2009 and the "5" is the 2007-08 count); (ii) a 2008 survey recorded zero while five animals survived (detection/coverage); (iii) label error. Needed: Hebblewhite, White & Musiani 2010 (Conserv. Biol. 24:341-344, `10.1111/j.1523-1739.2009.01343.x`, closed access) or the Banff survey reports with dates. Do not shift the year or claim the original LPD citation until then.

Demography/interventions (b, c): Lamb archive has **0** Banff survival rows and **0** recruitment rows [D]; DeCesare 2011 used Banff mean adult-female survival and calves per breeding-age female (values not obtained) [S]. `treatments.csv`: applied=0 for 1986-2023 [D]; no dated translocation or predator management found before 2009. The end event is a single catastrophe killing the last five animals, so it is not an endpoint produced by demographic stochasticity alone. Isolation from Jasper stated in a 2004 Parks Canada report [S, via search summary; not verified]. Individual histories: none public found.

Feasibility (e): census crosswalk only (annual maximum counts plus telemetry; no sightability); no source-specific rates; rates must be transferred from Jasper/BC herds. The 1986-2007 decline from 29 to 5 supplies the same decline-phase caveat. **Verdict: census usable (terminal year unresolved); rates missing, need transfer.**

## 4. Haley Lake Vancouver Island marmot colony - priority 4

Sources: Bryant 1998, PhD dissertation, Univ. of Victoria, "Metapopulation ecology of Vancouver Island marmots", 138 pp [D: `Bryant_AndrewAlbert_PhD_1998.pdf`, sha256 `a263400a...` as Astra's]; Bryant & Page 2005, Can. J. Zool. 83:674-682 [D: Wayback copy]; McAdie 2018 MSc (TRU) [D].

### 4.1 Census (a)

Colony naming: Appendix 7 "Haley Lake (natural)"; Table/App. 18-19 call the sites "Haley Bowl", "Bell Creek", "Vaughan Road (clearcut, 1 km west)", all separate rows [D]. Counts were made 21 April-7 October 1972-1997; the five intensively studied colonies were counted >10 times per year, with more effort after 1992 (thesis Part 2, p. 34; Appendix 6 p. 109). Class: age-summed marmots seen: adults (tagged plus untagged, >=2 y), yearlings, young-of-the-year; the annual statistic (maximum? last? mean?) is not stated in the pages read [U].

| Year | 1987 | 1988 | 1989 | 1990 | 1991 | 1992 | 1993 | 1994 | 1995 | 1996 | 1997 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Adults (App 7) | 12 | 14 | 12 | 12 | 8 | 7 | 9 | 5 | 7 | 5 | 4 |
| Yearlings | 4 | 1 | 5 | 0 | 3 | 6 | 0 | 10 | 3 | 0 | 0 |
| Young-of-year | 2 | 12 | 0 | 3 | 9 | 0 | 12 | 10 | 0 | 7 | 4 |
| Sum | 18 | 27 | 17 | 15 | 20 | 13 | 21 | 25 | 10 | 12 | 8 |
| Williams ID 15 [D] | 28 | 27 | 17 | 15 | 20 | 13 | 21 | 25 | 10 | 12 | 8 |

Source: Appendix 7, printed p. 110 (PDF p. 123), checked against the page image [D]; reproduces Astra's transcription. Conflicts kept: **1987 = 18 (thesis) vs 28 (Williams)**; Williams 1981-86 = 33, 28, 24, 24, 14, 23 and 1998-2000 = 2, 3, 0 have no table source in the thesis (the thesis has a colony-count figure and says in 1998 the natural colony "currently contains only two adults", p. 54) [U]. Endpoint: Williams 0 in 2000; no source for the last count or last survivors. Haley Lake later received captive-born marmots (first pair released 2004; >30 in 2010 per Marmot Recovery Foundation) [S], after the series.

### 4.2 Demographic estimates (b)

| Item | Values | Denominator, uncertainty, type |
|---|---|---|
| Haley tagged-animal annual survival (adults + yearlings), App 12 p. 117, transitions 1987-1996 | 1.00, 0.62, 0.75, 0.89, 0.45, 0.80, 0.44, 0.67, 0.50, 0.80; mean 0.69, SD 0.19 (n=10 years) | tagged at risk 3, 13, 12, 9, 11, 10, 9, 15, 10, 5 (sum 97); survivors 3, 8, 9, 8, 5, 8, 4, 10, 5, 4 (sum 64); no CI; individual-based (ear tags), same fieldwork as the counts |
| Haley apparent adult survival from counts, App 12 | 0.88, 0.80, 0.71, 0.67, 0.64, 0.69, 0.56, 0.47, 0.50, 0.80; mean 0.67, SD 0.13 | adults + yearlings at risk 123 (sum), apparent survivors 83; "net of immigration/emigration" (thesis Table 4 note); **count-derived, same data as Williams** |
| Haley juvenile apparent survival, App 11 p. 116 | 0.50, 0.58, -, 1.00, 0.67, -, 0.83, 0.30, -, 0.00 (n=7 years; mean 0.55, SD 0.33); tagged juvenile survival 1.00, 0.00, 1.00, 0.50, 0.00 (n=5; mean 0.50, SD 0.50) | young-of-year 2, 12, 0, 3, 9, 0, 12, 10, 0, 7 (sum 55); survivors 30 |
| Haley count-derived summaries, thesis pp. 74-76 | median annual survival 0.69 (n=26 years), six years with >50% loss; 3 of 4 years since 1994 "high mortality events", fourth 0.50; "18 of 21 juveniles produced during a four-year period" died; excluding the last four years median 0.71, R0=0.94, lambda=0.985 | count-derived; explicitly decline-phase |
| Pooled CJS adult survival, Table 2 p. 44 (all intensively studied colonies, not Haley-only) | pooled 0.629 (0.570-0.683) with recapture 0.933 (0.867-0.968), AIC 429.7; **pooled, recapture fixed at 1.0 0.623 (0.565-0.678), AIC 398.7**; male 0.545 (0.451-0.656), female 0.684 (0.609-0.751) | animals/animal-years not tabulated (one text figure: 7 reappearances in 255 adult-years); OCR printed 0.476 for the male upper bound in the unfixed block |
| Telemetry, thesis Appendix 16 p. 121 | 42 transmittered marmots 1992-98; 15 Haley implants 1992-94; pooled gross annual survival 28/38 = 74% excluding unknown fates and one research death (Haley male "Max", hyperthermia, Aug 1992) | pooled across colonies |
| Telemetry, Bryant & Page 2005 | 106 surgeries, 78 individuals 1992-2004 (42 F, 36 M), 15 colonies (9 natural incl. Haley bowl, 6 clearcut); 166 marmot-site-year records; 29 known-fate deaths; known-fate S = 0.74 (0.65-0.81); seasonal model 0.76 (0.68-0.83); male 0.74 (0.62-0.84), female 0.79 (0.67-0.87); recoding two 4-year-old vanished records as deaths gives 0.72; 8 animals vanished with their signal | pooled; one recovered transmitter at Haley Lake (1994, 5-year-old male, wolf; Table A1); 1992-94 animals overlap the thesis telemetry |
| Reproduction | Haley: 12 reproductive-age females produced 58 pups 1987-97, three of them 30 pups (p. 47); Haley litters per year 1, 4, 0, 1, 3, 0, 3, 2, 0, 2, 1 (sum 17, App 7); pooled litter size 3.28 (SD 0.85, n=43), interval 2.0 y; individual lifetime reproduction in App 14 | individual-based for tagged females |

Not independent: the count-derived rows and Williams ID 15 are the same observations; telemetry and ear-tag survival share animals and observers with the counts but add information the totals lack.

### 4.3 Interventions, movements (c)

- Immigration: App 7 Haley "Immigrants" sums to 9 over ten recorded years (mean 0.9, SD 1.1); thesis p. 47 records reproduction possible only after immigration (Haley, 1988); all 39 immigrants at the studied colonies were young adults. Emigration: one tagged/known Haley emigrant (adult male, Haley to Bell Creek, 0.9 km, 1974, Heard 1977; App 15) [D]. Metapopulation, not closed.
- 1996 experimental transplant of four marmots to "Mount McQuillan/Franklin" (App 16 rows 34-37; pp. 50-51); all died; **source colony not stated** in the pages read [D/U].
- Predator removal is regional (e.g. 24 wolves and 11 cougars in 1985, p. 30, App 5), not colony-specific; it does not add or remove focal marmots. Research handling: one fatality (1992). Captive breeding began 1997 (thesis predates it); 63 wild marmots were captured for the captive programme by Dec 2017 (61 by 2016) [D: McAdie]; a first-pass claim that 55 of 63 were taken 1997-2004 is unverified [U]. **No colony-by-year capture ledger found**, so removals from Haley in 1997-2000 cannot be dated.

### 4.4 Individual histories (d-equivalent)

Thesis appendices give ear-tag/telemetry histories at the page level (App 12, 14, 16); no machine-readable individual file was found. Bryant & Page 2005 Table A1 lists transmitter recoveries only.

### 4.5 Feasibility (e)

The Haley colony offers the most complete **stage-structured** public record: yearly adults/yearlings/young 1987-1997, annual tagged-animal survival with n, juvenile apparent survival, litter counts and immigrant counts. Dependence is the main limit: every Haley rate comes from the colony's own decline (adult apparent survival fell to 0.47-0.50 in 1994-95 as young survival collapsed), so any abundance feedback is already in the rates, and immigration (9 animals against mean 8.6 adults) breaks closure. Pooled CIs (CJS 0.623, 0.565-0.678; known-fate 0.74, 0.65-0.81) are cross-colony and mix ages. Transfer is needed for CIs, for 1981-86, 1987 and 1998-2000 counts (no table source), and for removal history. **Verdict: partly usable now (1988-1997 stage-structured, non-independent, non-closed); the rest needs transfer or is missing.**

## 5. Palmer LTER Adelie colonies (Litchfield/Torgersen) - brief

- ERDDAP files re-downloaded; sha256 equal to Astra's [D]. Metadata for `AdeliePenguinBandsSeen` (DOI `10.6073/pasta/afcab7754e2c2a96fadcd587a3a55faf`): "Annually between 1991 and 1998, a subsample of 1000 Adelie penguin creche-age chicks were flipper-banded on **Humble Island** ... resighting ... through 2006 when the last banded bird was observed"; banding ended because flipper bands may affect survival [D, `_info.json`]. So the cohort size (about 1,000 per year, 8 cohorts) is documented, but the band "year" field comment reads "year of measurement in GMT" (ambiguous), no search-effort or release-by-island table exists in the three ERDDAP datasets, and the file holds positive sightings only (2,442 rows; 28 Litchfield records per Astra [S]) [U for effort].
- Count discrepancies not resolved: Litchfield nine-colony sums are 325 (PAL9899, 1998-12-10) and 301 (PAL9900, 1999-11-17) against Williams ID 25 values 338 and 322 [D]; all other overlapping years match exactly. The January adult-and-chick file gives sums of `num_breeding_pairs` 248 (PAL9899) and 409 (PAL9900), which reproduce neither pair of values [D]. PAL9798 in that file carries both 1997-01-29 and 1998-01-29 dates (date anomaly). First zero PAL0708 (2007-11-20) matches Williams 2007 = 0 [D].
- Verdict: open-population comparator with documented cohort size but missing effort and unresolved counts; not usable as a closed baseline.

## 6. Final summary table

| Target | Census source and class | Individual-based rate evidence (n, uncertainty) | Count-derived / IPM evidence | Interventions and movement | Verdict |
|---|---|---|---|---|---|
| Maligne | Parks Canada fall helicopter minimum counts 1988-2017 (group-level open CSV; archive mixes OTC/MinCount; Williams 27 differs 2006-12) | AF survival 2002-2007 from about 3-8 collars, KM, no CI, n not shipped; no raw histories | calves per non-calf animal, 14 fall surveys; Lamb IPM posteriors (not independent); DeCesare 2011 values not obtained | no recovery actions recorded; access limits since 2014; no collared movement to other herds; rare male DNA movement; last animals dead or moved | **Census usable now; rates need transfer** |
| Purcells Central | BC late-winter total counts 1994-2006 (OTC, MNKA, MC; WSI public) plus zeros 2007, 2009 | 9 collared (5 F) 1994-99 [Wittmer T1]; survival not published (n about 3 per year); pregnancy 5/6 | % calves 0-16, 5-6 surveys; Lamb IPM; lambda 0.88 | none recorded; 2012 augmentation post-dates the zero and is attributed to Purcells South; boundary/identity notes | **Census usable now; rates need transfer** |
| Banff | Annual maximum counts plus telemetry, 16 pairs identical in Williams 28 and Lamb; 2008 zero vs April 2009 avalanche unresolved | none | none in archive; DeCesare 2011 PVA inputs not obtained | none recorded; end by avalanche (last 5) | **Census crosswalk only; rates missing; terminal year unresolved** |
| Haley Lake | Bryant 1998 App 7 age-summed colony counts 1987-1997 (10 of 11 years match Williams 15; 1987 18 vs 28; 1981-86, 1998-2000 unsourced) | tagged survival 10 transitions (n 3-15/yr, no CI); pooled CJS 0.623 (0.565-0.678); telemetry 0.74 (0.65-0.81), pooled | apparent adult survival 0.47-0.88 and juvenile survival from the same counts | immigrants 9; 1996 transplant (source unknown); no capture ledger; later releases after 2004 | **Partly usable now (non-closed, non-independent); gaps need transfer** |

Individual caribou histories: **not publicly available** (Zenodo v1 and v3, Dryad, Zenodo, Movebank, BC Data Catalogue, Open Government Canada checked). Public substitutes are herd-level (BC WSI, Parks Canada) or location-only (BC telemetry layer).

## 7. Manifest, reproduction and gaps

Hashes (sha256): Zenodo v3 ZIP `e0a42318bf59cddc50c0da5036a60820b2062ea7a402b9d4c32c603210bf2039`; v1 ZIP `6ca854ce57d43c3f7c5e4992abe2ae2b3195ab52578d4270c6e1a1b93ec6ac9f`; Git `counts.csv` `43c3e55a...`, `survival.csv` `d45a4fc3...`, `recruitment_counts.csv` `1784440c...` (as Astra); Bryant thesis `a263400a...`; Bryant & Page Wayback PDF `ad1c851b3c4398cca0a1a1cb20408ecf0a5ef820d1ba4d3a9676a8d53eb9c862`; Wittmer 2005 `3cc0494d...`; Hatter 2006 `2f84b336...`; BC 2021 herd table `229f22c9...`; Parks Canada CSV `623bb71d011721c7dc59254d7eb1cf6c849d92bae0579d2b7671f350afc43c83`; McAdie thesis `e9ef9c9d...`; DeMars Dryad CSV `99c03a9b...`.
Retrieval: Parks Canada CSV via `open.canada.ca/data/dataset/8d2849d9-a723-46c1-b94b-ed4a76e78195/resource/f9a392dc-aa09-41bd-ae74-c8de9ed5d42b/download/jasper_np_alpine_caribou_population_1988-2017_data.csv` (redirects to a signed blob URL; direct `curl` against open.canada.ca was rejected by its WAF). BC WSI via `https://openmaps.gov.bc.ca/geo/pub/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=pub:WHSE_WILDLIFE_INVENTORY.SPI_SURVEY_SUMMARIES_SV&outputFormat=application/json&CQL_FILTER=SPECIES_CODE='M-RATA' AND POPULATION_UNIT_NAME LIKE 'Purcell%'`. Bryant thesis via `dspace.library.uvic.ca/bitstream/handle/1828/8706/Bryant_AndrewAlbert_PhD_1998.pdf` (the `/bitstreams/<uuid>/download` URL returned 502). Bryant & Page: `web.archive.org/web/2022if_/https://andrew-a-bryant-services.com/wp-content/uploads/2014/05/bryant-and-page-2005.pdf`.
Other repositories checked: Dryad DeMars et al. 2021 (`10.5061/dryad.stqjq2c3g`, 21 AB/BC/NWT populations 1994-2015, herd-year S, nS, calves, cows) contains **no** Maligne, Purcells Central or Banff rows [D]; Zenodo 4432963 (Williams et al.) has individual `*_fate.csv`/`*_capture.csv` for one other herd ("RRPC") only [S]. Alberta Open Data returned 403 and the Open Canada CKAN API was blocked, so those two were checked only through the search page [U].
Not obtained: Hebblewhite et al. 2010 and DeCesare et al. 2011 (closed); Parks Canada progress reports (on request); Banff survey record with dates; Haley 1981-86 and 1998-2000 table source and the 1987 value; colony-by-year capture ledger; Bryant (1998) text for the 1996 transplant source; Kinley survey reports; Lamb Appendix S1.
Highest-value next tranche: (1) tabulate the Parks Canada CSV by flight and reconcile it with the archive for Maligne; (2) obtain Hebblewhite 2010 for the Banff terminal year; (3) pull the remaining WSI Purcell telemetry records (6,049 not fetched) to count collar-monitoring spans per animal; (4) settle Haley 1987 and 1998-2000.

## 8. Corrections after Astra's audit (Fable, 14 October 2026)

Astra's [Haley](astra_haley_recovery_review_20261014.md) and
[caribou](astra_caribou_recovery_review_20261014.md) reviews supersede the
following claims in this matrix. They are recorded here rather than edited in
place.

### Verdicts

- "Census usable now; rates need transfer" for Maligne and Purcells Central
  is replaced. The public sources support descriptive crosswalks and
  explicitly conditional sensitivity illustrations now. They do not yet
  support an observation-resolved, source-specific feedback test. Rate
  transfer is one optional modelling choice, not a prerequisite.

### Haley Lake

- **Count convention.** The annual totals are age-class seasonal maxima
  (p. 14). At intensive colonies they include all marked animals seen through
  the season (p. 37), so they are not a simultaneous census.
- **Tagged data.** Section 4.4's "recovered ear-tag/telemetry histories"
  should read: annual aggregate tagged-persistence summaries (Appendix 12:
  97 exposures and 64 survivors, non-pups; Appendix 11: 24 exposures and 11
  survivors, tagged pups) and partial named-animal summaries (Appendices 14
  and 16). Full histories were not recovered.
- **Conflicts kept unresolved:**
  - 1988 pups against 1989 yearlings;
  - 1994 tagged survivors against 1995 adults;
  - 1996 tagged pups;
  - 59 pups against 58;
  - Appendix 16's 43, 42 and 41.
- **Uncertainty.** Missing confidence intervals do not compel borrowing a
  pooled interval, and repeated exposures are not independent animals.
- **Transplant.** The 1996 transplant is not established as a Haley removal
  and is not coded as one; the donor colony remains unknown. Unknown origin is
  not evidence that Haley was not the donor. The McQuillan and Franklin
  accounts stay separate, with their linkage unresolved. *(Wording corrected
  14 October after Astra's protocol review.)*
- **Captive breeding.** The parenthesis about the thesis predating captive
  breeding is withdrawn; p. 48 already mentions a female at Toronto Zoo.

### Caribou

- **Zenodo.** Four records; three carry files, with two distinct ZIP
  checksums (`10833932` and `10834654` share one; `10439543` has none).
- **Individual histories.** Individual fate histories were *not found in the
  sources inspected*; this is not a universal claim of unavailability.
  `survival.csv` is herd-year aggregate evidence. The processed `sd` values
  are uncertainty information with stated provenance, not recovered binomial
  denominators.
- **Maligne 2014.** Groups 423 and 424 have different locations, so they are
  not exact duplicates. The 2010 record ID 378 has blank total and composition fields; its date,
  location and ID are present. *(Wording corrected 14 October.)* Blank
  composition fields elsewhere do not by themselves show incomplete
  classification.
- **Purcells Central.** The OTC, MNKA and MC classes stay distinct. 1997
  OTC = 2 is a real observed count.
- **Banff.** The primary paper (Hebblewhite et al.) is openly readable. It
  documents the April 2009 avalanche and recovery management around 2002.
  The archive's 2008 terminal label remains unresolved.

### Cross-cutting

- **Decline-phase rates.** Rates measured during decline may contain feedback
  but do not demonstrate it.
- **Shared monitoring.** Marked outcomes and composition add information
  despite shared monitoring; they need a joint or conditional model.
- **External drivers.** Predator–prey and other external drivers are not
  excluded by closure. They can make a particular implemented null
  inadequate.
