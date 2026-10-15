# Caribou case: conflict and uncertainty register

Descriptive deep dive covering Banff, Maligne and Purcells Central. Accepted in
board 1625; the evidence base is Astra's caribou recovery review and matrix §8.

**Rules.**
- Values are kept as found: no source row is deduplicated, corrected or
  imputed.
- "Unresolved" means the pinned sources do not settle it.
- Snapshots and hashes are in `caribou_sources.json`.

## A. Value conflicts

| # | Entry | Conflicting entry | Status |
|---|---|---|---|
| A1 | Maligne, Parks Canada fall group sums: 2001 = 21, 2003 = 24, 2004 = 11, 2006 = 8, 2008 = 6, 2014 = 4 | Lamb archive count: 12, 19, 7, 7, 4, 2 | Unresolved. The archive mixes count classes (Astra review); its minimum-count construction is not reconstructed here. |
| A2 | Maligne, Williams ID 27: 2006–2012 = 11, 7, 7, 3, 6, 7, 5 | Lamb archive (7, 5, 4, 4, –, 6, 6) and Parks Canada sums (8, 5, 6, 4, 6, 6, 6) | Unresolved. The Williams series agrees with the archive in 1998 and 2013–2018. ID 27's identification as Maligne is plausible, not exact. |
| A3 | Maligne 2014: group records 423 and 424 (28 October), each one adult male and one adult female | — | Different locations (Maligne Pass; north of Maligne Pass), so not exact duplicates. Repeated sighting and distinct groups remain alternatives. Sum 4 kept beside the archive's 2. |
| A4 | Maligne 2010: record 378 (15 October, Evelyn Creek) has blank total and composition fields; its date, location and ID are present | — | Unresolved. The 2010 sum of 6 comes from the two populated records and is not called three quantified groups. The archive has no 2010 count. |
| A5 | Purcells Central, WSI 1997: OTC = 2 | MNKA = 14 (12 animals seen north of the study area before or after the survey; both collars found after the flight); archive = 14 | Both are real source values. The low OTC does not itself establish a population drop; the coverage evidence does not prove that no change occurred. |
| A6 | Purcells Central, archive count column | WSI classes: the archive uses MNKA in 1996, 1997, 2004 and 2005, and OTC elsewhere | The classes are kept separate. Merging them changes the estimand. |
| A7 | Purcells Central, WSI 2003: MC = 7 | WSI note mentioning 10 | Unresolved. |
| A8 | Purcells Central: OTC and MC both flagged BEST in 1998, 2000, 2002 and 2003 | — | The flag alone does not pick one annual value. |
| A9 | Banff: archive and Williams terminal zero labelled 2008 (2007 = 5) | Hebblewhite et al. 2010 and Parks Canada: the last five animals died in the April 2009 avalanche | Unresolved: a season-label convention, a detection gap or a label error. No year shift is applied. |
| A10 | Purcells Central 2012 augmentation: COSEWIC (9 caribou, "Augmented 2012") | Lamb `transplants.csv`: release recorded under Purcells South (16 adult F + 3 adult M) | Unit identity differs. The release post-dates the zero and is not coded within the series. |
| A11 | Maligne archived composition (`recruitment_counts.csv`, survey years after the +1 archive shift is undone) | Same-year Parks Canada flight composition: 9 of 14 match exactly; 5 differ (survey years 2001, 2003, 2004, 2006, 2008) | Archived composition summaries from the shared monitoring programme, with their OTC/MNKA classes kept. Not reconstructed from the displayed Parks group sums (Astra caribou artifact review). |

## B. Missing or unrecovered evidence (missing is not zero)

| # | Gap |
|---|---|
| B1 | **No individual collar fate histories** were found in the sources inspected: both distinct Zenodo ZIPs, Dryad, Movebank, the BC Data Catalogue and Open Canada. `survival.csv` is a herd-year aggregate. This is a search-bounded statement, not a claim that the data do not exist. |
| B2 | Annual collar risk sets and censoring behind `survival.csv`; the published collar totals (for example 9 collared in Purcells Central, 1994–99) are not annual risk sets |
| B3 | Banff: no survival or composition rows in the archive |
| B4 | Maligne: survival only for 2002–2007, with demographic coverage ending before the disappearance; Parks Canada counts end in 2017 (archive zeros 2018–2021) |
| B5 | Purcells Central: survival only for 1994–1996 |
| B6 | Access-restricted sources not consulted: Parks Canada progress reports (on request) and DeCesare 2011 |

## C. Unquantified uncertainty and interpretation limits

- **What the counts are.**
  - Maligne: fall helicopter minimum counts, summed by flight.
  - Purcells Central: helicopter counts (mostly March–April; 1 May in 1998;
    day unrecorded in 2003 and 2005), with tracks, in three WSI classes
    (OTC, MNKA, MC). The general notes flag incomplete coverage in 1996, 2003
    and 2005.
  - Banff: annual maximum counts plus telemetry.
  - Detection and coverage vary by year and are not modelled here.
- **Survival.** `survival.csv` values are KM estimates at month 12 with
  staggered entry. Boundary values (est = 1) carry a constructed resampling
  `sd`. This is uncertainty information with stated provenance, not a
  binomial denominator or a recovered CI (`dataprep.Rmd`).
- **Composition.** Calves per classified non-calf (`recruitment_counts.csv`)
  come from the shared monitoring programme with the counts and exclude unclassified animals.
  This is not automatically calf:cow, and counting the same total twice as
  independent evidence would be wrong.
- **IPM outputs.** Lamb's IPM posteriors reuse the counts and rates and are
  not independent priors.
- **Management.** Archive treatment zeros do not establish an unmanaged
  population. Documented actions such as elk reduction and access closures
  change the environment rather than adding or removing focal caribou.
- **Decline-period rates** may reflect feedback, environmental change,
  sampling or combinations of these. They do not identify a feedback-free
  baseline.
