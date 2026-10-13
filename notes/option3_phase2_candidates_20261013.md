# Phase II candidate case studies: first-pass literature scan

**UNVERIFIED first-pass scan by an AI search agent, 13 October 2026.** Web search and
web fetch only. Nobody was contacted, no dataset was downloaded (repository metadata
pages and journal PDFs were read), and nothing was purchased. Treat every item as a lead,
not as an eligibility decision. This note is not part of the pre-registered protocol.

## Verification legend

- **[P]** read in the primary text or the repository's own metadata page this session.
- **[S]** taken from a search-result summary or a secondary web page; the fetch tool
  summarises pages with a small model, so numbers here can be wrong. Re-check before use.
- **[L]** read from our local copy of the Williams et al. Dryad file
  (`data/raw/williams2021/population_data.csv`).
- **[U]** could not be verified; stated only as a gap.

## Bottom line

- **No candidate meets all three criteria cleanly.** Nothing is rated GOOD. The best are
  PARTIAL: public or tabulated counts plus real individual-based demography, but with a
  caveat on series length, supplementation, or whether "extinction" means local
  abandonment.
- **Strongest leads:** (1) BC/Alberta mountain caribou herds (telemetry adult female survival
  and calf:cow ratios map straight onto s and f); (2) Palmer LTER Adélie penguin colonies
  (public colony-level counts and chick counts, banded-chick survival from a neighbouring
  colony); (3) Barro Colorado Island antbirds (colour-banded, 1960-71, historical but
  small).
- **Most Williams et al. series outside our nine have no identifiable individual-based
  demography** (see the last table). Several are one-driver events (Guam brown tree snake,
  vulture diclofenac, amphibian chytrid) where a vortex test is a poor fit anyway.
- **Prior-art flag:** Wittmer, Sinclair & McLellan (2005, Oecologia) already test accelerated
  decline at low density across 15 caribou subpopulations with radio-collar data [P]. See
  candidate 1; it bears on the novelty statement as well as on Phase II.
- Williams et al. (2021) used 35 populations; our local file has 31 rows because four series
  are confidential [P: readme]. Their Supplementary Table S1 (sources per population) would
  identify the caribou, penguin and shrike series but was not retrievable (PMC download
  returned a loading page).

## Summary table, ranked by feasibility

| # | Candidate | Count series (end) | Independent demography | Supplemented? | Data access | Verdict |
|---|---|---|---|---|---|---|
| 1 | Mountain caribou herds, BC/Alberta (Banff, Maligne, Purcells, others) | Late-winter aerial censuses; Banff to 2009, others to about 2018; periodic, not always annual | Radio-collar adult female survival with SE, pregnancy rate, calves per 100 cows [P] | Some herds: transplants, maternity pens, wolf control [S/U] | Paper tables [P]; government herd reports [S]; Williams IDs 27, 28 [L] | PARTIAL (best) |
| 2 | Adélie penguin colonies, Palmer LTER (Litchfield Is., Torgersen sub-colonies) | Colony counts 1991-2017 [P], earlier counts from 1974-75 [S]; Litchfield to 0 in 2006/07 | Colony chick counts per pair 1992-2018 [P]; flipper-band survival, Humble Is. only [P] | No | Public ERDDAP/EDI [P] | PARTIAL |
| 3 | Ocellated antbird and barred woodcreeper, Barro Colorado Is., Panama | 1960-71 pair densities; near-extinct by early 1971 | Colour-banded adult mortality and nest losses, same study [S] | No | Paper tables [U: full text not read] | PARTIAL |
| 4 | Bay checkerspot, Jasper Ridge (patches C and H), California | Adult male mark-recapture estimates 1960-98; zeros 1988/1996, extinction 1991/1998 [P] | Not in the cited paper; larval/oviposition studies [U] | No [U] | Unpublished, no repository [P] | PARTIAL (access) |
| 5 | Florida grasshopper sparrow subpopulations (Avon Park, Kissimmee, Three Lakes) | Singing-male counts; Kissimmee functionally extirpated [S] | Banding survival 0.598 (adult males, 1989-92) [P]; fecundity not measured [P] | Captive releases from 2019 [S] | Reports [S]; no dataset found | PARTIAL (weak) |
| 6 | Large blue butterfly, Britain | Colony counts to 1979 extinction [S]; counts not retrieved | Egg and larval survival measured by J. Thomas [S] | None before 1979 | Not retrieved | PARTIAL/POOR |
| 7 | Northern spotted owl, British Columbia | Site occupancy 1992-2002 [S]; one wild female left in 2023 [S] | BC recovery documents [S]; mostly US demography | Captive-bred releases [S] | Reports | POOR |
| 8 | Heath hen, Martha's Vineyard | Annual census 1916-32, numbers disputed [S/P] | Sex ratio, fire, predation; no individual-based estimates found | Reserve, predator control, 1898 prairie chicken release [P] | Gross 1928 monograph, not retrieved | POOR |
| 9 | Dusky seaside sparrow, Florida | Singing-male counts about 1968-80 [S]; sources conflict | Not found | Last males captured 1979-80 [S] | Scanned PDFs, not read | POOR |
| 10 | Guam forest birds (6 species in Williams) | Road-survey densities 1976-98 [L] | Nest-protection studies for crows [S]; none for others found | Nest protection, Rota translocation [S] | In Williams file [L] | POOR |
| 11 | White-rumped vulture, India (probably Keoladeo) | Active nests 1985-99, 6 obs [L] | Not identified for this colony | No | In Williams file [L] | POOR |
| 12 | Lesser grey shrike, Spain (sub-population) | 13 obs 1989-2002 [L] | Breeding success not found | Captive releases in Lleida [S] | In Williams file [L] | POOR |
| 13 | 'Akikiki, Kauai | Irregular range-wide surveys 1968-73, 2012, 2018 [S] | Nest success 0.77, 20 nests, 2012-13 [S] | Captive breeding since 2015 [S] | Not retrieved | POOR |
| 14 | Po'ouli, Maui | Irregular densities and sightings 1975-2004 [S] | 2 nests in 1986 [S] | Capture attempts 2002-04 [S] | Not retrieved | POOR |
| 15 | Wyoming toad, Mortenson Lake | Counts from 1987; wild breeders taken to captivity 1989 [S] | Mark-recapture 1990-91 [S] | Captive breeding, releases [S] | Not retrieved | POOR |
| 16 | Mountain yellow-legged frog, Sierra Nevada | 13-year Bd epizootic series [S] | Not a vortex case; disease-driven | No | PMC article [S] | POOR |
| 17 | Glanville fritillary patches, Aland | Thousands of patch extinctions, nest counts [S] | Individual-level work exists [U] | No | Dryad has other Aland sets [S] | POOR |
| 18 | Bighorn sheep herds (Berger 1990) | 122 herds, up to 70 years, summary sizes [S] | Not individual-based | Some translocations [S] | Paper only | POOR |

## Notes per candidate

### 1. Mountain caribou herds, British Columbia and Alberta: PARTIAL (best)

- **Series.** Williams has two Canadian caribou series [L]: ID 27 (1998-2018, 14 obs, 68
  falling to 3 and then 0) and ID 28 (1986-2008, 16 obs, 29 falling to 5 and then 0), both
  "Full population count". The data file does not name the herds. Banff (extirpated April
  2009 by an avalanche) and Maligne, Jasper (considered extirpated, no sign since 2018) fit
  the endpoints [S]; Purcells South (last animals penned in 2018) and South Selkirk are also
  possible [S]. **Identities are my guess; do not use until Table S1 or the LPD record
  confirms.**
- **Counts (primary).** Wittmer et al. 2005, Table 2 [P]: late-winter census estimates, first
  and last year only, e.g. Purcells-South 63 (1995) to 14 (2002); Purcells-Central 15 to 5;
  George Mountain 20 (1992) to 3 (2002); Monashee-South 10 (1994) to 4 (2002). Two census
  points per herd in that paper; annual herd series would have to come from BC Ministry
  or Parks Canada reports [U].
- **Independent demography [P].** Wittmer et al. 2005 CJZ: more than 380 collared caribou,
  adult female annual survival by subpopulation (Table 5, e.g. Purcells-South 0.55 +/- 0.10),
  calves per census (Table 4), causes of mortality. Wittmer et al. 2007 JAE: survival of
  10 populations ranged 0.67-0.93. Wittmer, Sinclair & McLellan 2005 Oecologia: 349
  radio-collared animals, 15 subpopulations, pregnancy rate 92.4 +/- 2.24 percent, rates of
  increase printed as "0.1871 to 0.0496" (a minus sign is probably lost in the text), smaller
  subpopulations declining faster. DeCesare et al. 2011 (Banff/Jasper PVA) used mean adult female survival and calves
  per breeding-age female as fecundity [S].
- **Interventions to flag.** Purcells: 19 caribou moved in 2012, 12 had died by the time of
  a 2012 BC quarterly report [S]; 2018 capture of the last South Purcell and South Selkirk
  animals into a maternity pen [S]. Wolf management and other measures in Alberta and BC
  [S/U]. Any herd series must be cut at the first augmentation.
- **Fit to our null.** Female-only matrix with s (adult female survival) and f (calves per
  female) is exactly how these herds are modelled. Predation by wolves is an external driver,
  so a vortex test would need the external-deterioration alternative.
- **Citations.**
  - Wittmer HU, McLellan BN, Seip DR, et al. 2005. Can J Zool 83:407-418.
    doi:10.1139/Z05-034 [P]
  - Wittmer HU, McLellan BN, Serrouya R, Apps CD. 2007. J Anim Ecol 76:568-579.
    doi:10.1111/j.1365-2656.2007.01220.x [P]
  - Wittmer HU, Sinclair ARE, McLellan BN. 2005. Oecologia 144:257-267.
    doi:10.1007/s00442-005-0055-y [P: DOI from the PDF; volume/pages from search]
  - Hebblewhite M, Whittington J, Bradley M, et al. 2007. Rangifer 27(4).
    doi:10.7557/2.27.4.322 [P]
  - Hebblewhite M, White CA, Musiani M. 2010. Conserv Biol 24:341-344, "Revisiting
    extinction in national parks: mountain caribou in Banff" [S; DOI not retrieved]
  - DeCesare NJ et al. 2011. Conserv Biol 25:365-373 [S; DOI not retrieved]
  - Lamb CT et al. 2024. Ecol Appl 34. doi:10.1002/eap.2965 [S; data availability not
    checked]
- **Next step.** Identify which LPD records ID 27 and 28 are, then pull herd census and
  telemetry tables from the above and BC government reports.

### 2. Adélie penguin colonies, Palmer LTER: PARTIAL

- **Series.** Williams ID 25 [L]: Antarctica, "Estimate", breeding pairs, 1979-2007, 26 obs,
  564 falling to 0. It may be Litchfield Island (unverified guess). The Palmer census
  dataset covers islands CHR, COR, HUM, LIT, TOR, 1991-11-03 to 2017-11-24, breeding pairs
  0-517 per colony [P]. Litchfield went extinct in 2007 per a Fraser and Patterson-Fraser
  poster (five rookeries 15,202 pairs in 1974 to 2,511 in 2011/12) [P]; a BirdLife
  factsheet is reported to give about 1000 pairs in the early 1970s and nests vacated by
  2006/07 [S]. Cimino et al. 2025 report that only 5 of 23 historic Torgersen
  sub-colonies remain active, using counts 1975-2022 [P], which implies many sub-colony
  series ending at zero.
- **Independent demography [P].** Colony-specific chick production 1992-2018 (pairs and
  chicks per colony). Flipper-band resightings: about 1000 crèche-age chicks banded each
  year 1991-1998 on Humble Island, resighted to 2005/06. Survival is therefore from a
  neighbouring colony, not Litchfield.
- **Interventions.** None, and tourism showed no effect on Torgersen breeding success [S].
- **Caveat.** Local colony "extinction" is abandonment and emigration in a long-lived seabird
  with a skua-predation hypothesis for small colonies [P: poster]; this is not closed
  demographic extinction, so a vortex null with fixed s and f may not apply.
- **Data and citations.** Public under the LTER data access policy.
  - Census: doi:10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e [P]
  - Chick production: doi:10.6073/pasta/9bf4588c02d6caa12a68133134ed4489 [P]
  - Band resightings: doi:10.6073/pasta/afcab7754e2c2a96fadcd587a3a55faf [P]
  - Cimino MA, Larsen GD, Johnston DW, Groff DV. 2025. Landscape Ecol 40(4).
    doi:10.1007/s10980-025-02088-y [P]
  - Poster: asm2012.lternet.edu, "Adélie penguin colony size and local population
    extinction: predation-induced tipping point" [P]

### 3. Barro Colorado Island antbirds: PARTIAL

- **Series.** Willis (1974) tracked colour-banded ant-following birds 1960-71. Ocellated
  antbird fell from about 1.5 pairs/km2 to one female in early 1971; barred woodcreeper
  from two pairs to local extinction; ground-cuckoo gone before 1960 [P: abstract via AGRIS].
- **Demography.** Same study: high adult mortality in the ocellated antbird and possibly
  higher nest losses than in the stable spotted antbird [P: abstract]. A search summary
  quotes about 30 percent adult mortality versus 15-17 percent, and nest losses 96 versus
  91 percent [S: not confirmed against the paper]. Willis found no clear cause.
- **Caveats.** Pairs per km2, not individual counts; the number of annual points is
  unknown; the endpoint (final disappearance) may fall after the paper. The island was a
  forest fragment isolated since the early 20th century. Later reassessments of BCI
  extinctions exist but I did not search them [U].
- **Citation.** Willis EO. 1974. Ecol Monogr 44(2):153-169. doi:10.2307/1942309 [P: AGRIS
  record]. Full text not read.

### 4. Bay checkerspot, Jasper Ridge: PARTIAL (data access is the blocker)

- **Series [P].** McLaughlin, Hellmann, Boggs & Ehrlich 2002 (PNAS 99:6070-6074,
  doi:10.1073/pnas.052131199): patches C (9.8 ha) and H (2.55 ha), adult male estimates from
  daily mark-recapture 1960-98 (incomplete 1964-68), populations fluctuated over four
  orders of magnitude. Figure 1 gives extinction in 1991 (C) and 1998 (H); the model uses
  data to the first zero (1988 and 1996). A secondary page says 1989 and 1997 [S], so the
  dates need checking.
- **Demography.** The paper reports no survival or fecundity rates. The Stanford group's
  mark-recapture and host-plant work likely contain them [U].
- **Access.** Data cited as unpublished; no repository [P]. Obtaining them means asking the
  Ehrlich/Stanford group, which is Barry's call and was not attempted.

### 5. Florida grasshopper sparrow: PARTIAL (weak)

- **Demography [P].** Delany, Moore & Progulske, Proc SE Assoc Fish Wildl Agencies
  47:366-369 (year not printed in the PDF text): 48 colour-banded adult males 1989-92,
  annual survival 0.598, mean life expectancy 2.95 years, and 5.4 young per pair needed for
  stability; the paper says fecundity data are lacking.
- **Counts [S].** Avon Park about 130 singing males in 1999 to 13 (2003) or 10 (2004);
  278 males at seven subpopulations in 2004; 75 males on three public properties in 2012;
  Kissimmee Prairie Preserve functionally extirpated.
- **Interventions [S].** Captive breeding from 2015, releases from 2019 (Avon Park from
  2021), 1,000th captive-bred bird released July 2024. No subpopulation count reached zero
  before releases except possibly Kissimmee. No annual dataset found.

### 6. Large blue butterfly, Britain: PARTIAL/POOR

- Extinct nationally in 1979 after decline from the mid-1800s, steeper after 1950 [S].
  Jeremy Thomas lived with the last colony and measured egg laying, egg survival and
  caterpillar numbers [S: a quotation]. Science paper: Thomas JA, Simcox DJ, Clarke RT.
  2009. Science 325:80-83, doi:10.1126/science.1175726 [S: from the NERC record].
- I did not retrieve the 1950s-79 colony counts or the larval survival tables. The colony
  count series is probably adult counts at a handful of sites, with ant-host habitat change
  (an external driver) as the cause.

### 7. Northern spotted owl, British Columbia: POOR

- Occupancy surveys at 40 sites fell 49 percent 1992-2001 and 35 percent more by 2002;
  under 33 potential pairs in 2002; extirpation predicted 2007-12 [S: recovery strategy].
  By 2023 one wild female remained after two released captive-born males died [S].
- Series is site occupancy and does not reach zero in the sources found; captive-bred
  releases; barred owl competition. Demographic rates cited are mostly from US studies [S].

### 8. Heath hen: POOR

- Counts are inconsistent across accounts: about 77 counted in 1907, about 300 in 1910,
  roughly 800 to 2,000 in 1916, a peak over 400 in 1920, last broods 1925, one bird 1928,
  last seen March 1932 [P: Bird Observer 2015 summary of Gross 1928; its own text notes the
  conflict]. Gross AO. 1928. Mem Boston Soc Nat Hist 6(4) (page range given inconsistently
  in sources) and Gross AO. 1929. The Heath Hen census for 1929. Wilson Bull 41(2) [P: title
  page only]. Neither table was read.
- Demography is population-level: sex ratio skew after the 1916 fire, goshawks, blackhead
  disease, cold wet breeding seasons [P: Bird Observer]. No survival or nest-success
  estimates found. Managed (1907 reservation, predator control, 1898 prairie chicken
  release, failed captive breeding) [P: Bird Observer].

### 9. Dusky seaside sparrow: POOR

- A secondary table lists St Johns singing males 143 (1970), 110 (1972), 54 (1973), 37
  (1974), 47 (1975), 11 (1976), 12 (1977), 9 (1978); another source gives 28 and 24 for
  1977-78 [S: the two disagree]. Last female seen 1975; six males in 1979 [S]. The
  Baker (SEAFWA) and Delany (Florida Field Nat 9:64-67) PDFs are scanned images and were
  not read. The endpoint is capture of the last males, and the late population was
  all male, which breaks any s/f null.

### 10. Guam forest birds: POOR

- Williams has six Guam series on one road-survey source [L]: Mariana crow (1976-98, 23
  obs), white-throated ground-dove (1976-87), Micronesian myzomela (1976-85), Mariana
  fruit-dove (1976-86), rufous fantail (1976-85), Micronesian kingfisher (1976-89), all in
  individuals per 100 km. They share one driver (brown tree snake predation, [S]) and one
  island, so they are not independent replicates.
- Crow nest protection results: no chicks fledged from unprotected nests since 1987 [S].
  Savidge 1987 and Wiles et al. are the usual sources; I did not verify their citations.
  The Rota crow population is a separate, still-extant series.

### 11. White-rumped vulture, India: POOR for a vortex test

- Williams ID 11 [L]: active nests, 6 obs: 244 (1985), 353 (1987), 150 (1996), 25 (1997),
  20 (1998), 0 (1999). A BNHS document says the Keoladeo colony fell about 97 percent from
  1985-86 to 1996-97 and was extinct by 2003 [S]; a 2003 collapse paper documents the
  national decline (Biol Conserv 109:381; authors not confirmed) [S]. Identification with
  Keoladeo is an inference; the zero year does not match.
- Cause is diclofenac poisoning (an external, adult-mortality driver) [S].

### 12. Lesser grey shrike, Spain: POOR

- Williams ID 13 [L]: 12 (1989) to 0 (2002), 13 obs. Spain had 24 pairs in 2002 and 2004 and
  0 in 2018 [S], so ID 13 is a sub-population (Girona? Lleida?), unverified. Girona census
  from 1989, about 60 percent decline 1990-2000 (Giralt & Valera 2002, cited via a Spanish
  government document) [S]. Lleida: magpie nest predation and captive-bred releases [S].
  No breeding-success figures found.

### 13-18. Short notes

- **'Akikiki (13).** Range-wide estimates 6,832 (1968-73), 468 (2012), 454 (2018; Paxton et
  al. 2020), functionally extinct in the wild, fewer than 5 in 2024 [S]. Nest success 0.77
  from 20 nests, 2012-13 (Hammond et al. 2015, Condor 117, doi:10.1650/CONDOR-14-75.1) [S].
  Surveys are not annual and captive breeding began in 2015.
- **Po'ouli (14).** Density 76 birds/km2 (1975) to 8 (1985) in a 50 ha plot; 5-7 birds known
  in 1995, 3 by mid-1997; last seen 2003-04 [S]. Not an annual series.
- **Wyoming toad (15).** Decline 1975-78, wild group found at Mortenson Lake 1987, Corn and
  Withers mark-recapture 1990-91 showed decline, 10 toads taken into captivity 1989 [S].
  Counts and captive management make it a poor fit.
- **Mountain yellow-legged frog (16).** Vredenburg et al. 2010, PNAS 107:9689-9694 [S]: 13-year
  series in three Sierra basins, Bd epizootics drive extinction in a few years. Exogenous
  disease, too fast for a vortex.
- **Glanville fritillary (17).** Presence/absence of 4,415 patches over 22 years and a
  10-fold collapse after the 2018 drought [S]. Counts are larval nests, rescue effect is
  strong, and the Dryad record found (doi:10.5061/dryad.d461s) is a dispersal dataset [S].
- **Bighorn (18).** Berger 1990, Conserv Biol 4:91-98 [S: abstract]: 122 populations, all under
  50 animals extinct within 50 years. Herd sizes and persistence, not annual counts or
  individual demography; Singer et al. 2001 dispute the size effect [S].

## Williams et al. (2021) series outside our nine [L]

IDs, years and units are from the local CSV. "No demography found" means nothing was found
in this scan, not that none exists. Series ID 8 and 9 (wood turtles) and the other eight of
our nine are excluded.

| ID | Population | Country | Years (obs) | Type | Assessment |
|---|---|---|---|---|---|
| 1 | Buff-rumped thornbill | Australia | 1996-2005 (10) | Mean birds per survey | POOR; survey index, not searched |
| 5 | Mariana crow | Guam | 1976-98 (23) | Density per 100 km | POOR; see 10 |
| 7 | White-throated ground-dove | Guam | 1976-87 (12) | Density | POOR; see 10 |
| 16 | Micronesian myzomela | Guam | 1976-85 (10) | Density | POOR; see 10 |
| 24 | Mariana fruit-dove | Guam | 1976-86 (11) | Density | POOR; see 10 |
| 29 | Rufous fantail | Guam | 1976-85 (10) | Density | POOR; see 10 |
| 33 | Micronesian kingfisher | Guam | 1976-89 (14) | Density | POOR; see 10 |
| 11 | White-rumped vulture | India | 1985-99 (6) | Active nests | POOR; see 11 |
| 12 | Griffon vulture | Croatia | 1985-98 (8) | Breeding pairs | POOR; 7 pairs to 0, not searched further |
| 13 | Lesser grey shrike | Spain | 1989-2002 (13) | Breeding pairs | POOR; see 12 |
| 18 | Western ground parrot | Australia | 1996-2008 (13) | Calls per visit | POOR; fox/cat predation and fire [S], calling index |
| 19 | Great cormorant | South Africa | 1984-2004 (21) | Breeding pairs | Not searched |
| 22 | Pacific golden plover | Australia | 1974-2001 (25) | Summer max count | POOR; non-breeding count |
| 23 | King brown snake | Australia | 1998-2007 (9) | Encounters per hour | POOR; under 10 obs, effort index |
| 25 | Adélie penguin | Antarctica | 1979-2007 (26) | Breeding pairs | PARTIAL; see 2 |
| 27, 28 | Caribou | Canada | 1998-2018 (14); 1986-2008 (16) | Full count | PARTIAL; see 1 |
| 30 | Roseate tern | UK | 1992-2004 (13) | Breeding pairs | Not searched; colony is open (dispersal) [U] |
| 31 | Ostrich | Niger | 1986-99 (6) | Estimate | POOR; 6 obs |
| 32 | Common starling | Finland | 1962-83 (22) | Nests | Not searched |
| 34 | Arctic ground squirrel | Canada | 1990-2011 (22) | Density per ha | Not searched; may be a trapping-grid absence rather than extinction [U] |
| 35 | Northern lapwing | Slovenia | 1988-97 (10) | Pairs | Not searched |

## Demography-rich datasets without an extinction endpoint (do not qualify)

- House sparrow metapopulation, 11 Helgeland islands, 1994-2022, CMR, pedigree and nestling
  production; CC0; Frank et al., Dryad doi:10.5061/dryad.rr4xgxdnq (article
  doi:10.1002/ecy.70356). The page reports no island extinction [P].
- Great Lakes piping plover integrated model data, 1993-2016, Dryad doi:10.5061/dryad.j2906
  [P]. No extinction.

## Searched without finding a usable case

- Mauritius and Pacific island birds beyond Guam and Hawaii, small-mammal island
  populations, reptile populations followed to extirpation, and COMADRE entries flagged as
  extinct. Searches returned only persisting populations or methods papers [S]. Dryad and
  Zenodo keyword searches returned no dataset combining counts to zero with individual-based
  demography.
- Not searched this session: California condor, black-footed ferret (Meeteetse) and Japanese
  crested ibis, which would end by capture, and Bachman's sparrow or other sparrow
  sub-populations beyond Florida.

## Suggested next tranche (for Barry's decision)

1. Resolve Williams IDs 25, 27, 28 (and 13, 30) against the LPD records or Table S1, then
   build herd-level caribou series and the Litchfield/Torgersen colony series from public data.
2. Read Willis 1974 and Wittmer et al. 2005 Oecologia in full; decide whether the latter
   changes the novelty claim.
3. Decide whether to request the Jasper Ridge data. No contact was made.
