# Option 3 evidence scan: independent demographic estimates for the nine extinction-vortex series

**UNVERIFIED first-pass scan by an AI search agent (Claude, web search and web fetch only), 13 October 2026.**
No one was contacted, nothing was purchased, no other project file was read or changed. Treat every number as a lead
to be checked against the primary source before it enters a prior.

Evidence tags used in the tables:
- **[FT]** text I extracted myself from a downloaded PDF (highest confidence in the transcription).
- **[WF]** a web-fetch tool read a page or full text and returned a summary; numbers are not verbatim, spot-check them.
- **[AB]** abstract or bibliographic record only (publisher page or OpenAlex); full text not read.
- **[SN]** search-engine snippet or secondary page only; unverified. Never rely on these without checking.
"+-" values are reproduced as printed; the abstracts often do not say whether they are SE or SD (stated where known).

Source of the count series (all nine): Williams et al. 2021 (Ecology and Evolution 11:7069-7079, doi 10.1002/ece3.7555) assembled
35 populations from the Living Planet Database plus Fagan & Holmes 2006 (Ecol Lett 9:51-60, doi 10.1111/j.1461-0248.2005.00845.x, read in full). Their per-population table is Table S1 (docx on PMC8207159; Dryad doi 10.5061/dryad.jwstqjq8c, population_data.csv); I could not
open it. The original sources below are those printed in Fagan & Holmes 2006 Table 1 **[FT]**, which lists all nine populations. Fagan & Holmes
monitoring-period lengths differ from our series for three populations (wild dog 20 y vs 1970-1992 = 23; marmot 21 y vs 1981-2000 = 20;
whooping crane 16 y vs 1986-2003 = 18), so the Williams series are probably extended or re-derived; not reconciled here.

---

## 1. African wild dog, Serengeti, Tanzania, 1970-1992

**a) Count source.** Fagan & Holmes 2006 Table 1 cite Ginsberg, Mace & Albon 1995, Proc R Soc B 262:221-228, doi 10.1098/rspb.1995.0199 [AB].
Study-area (Serengeti plains) counts of dogs. Abstract: crash from about 60 to 30 in 1975-76, then about 22 for 16 years, then local extinction;
reductions of at least 40% occurred three times; a Monte Carlo model with parameters matching the fluctuations says chance alone could plausibly
produce the extinction. FH2006: final pre-extinction count 26, smallest size from which an increase occurred 12 (three increases). Companion
analysis of the same population, 1965-1991: Burrows, Hofer & East 1994, Proc R Soc B 256:281-292, doi 10.1098/rspb.1994.0082 [AB]; a secondary
source quotes about 95 dogs in 12 packs in 1970 [WF], which does not match the ~60 in Ginsberg et al.; unreconciled.

**b) Vital rates.**
| Parameter | Estimate | Population / period | Method | Citation | Tag |
|---|---|---|---|---|---|
| Adult annual mortality | 20 +- 6% (n=235) | Selous, Tanzania, 1991-96 | field monitoring, radio-collared | Creel et al. 1997, J Wildl Dis 33:823-832, doi 10.7589/0090-3558-33.4.823 | AB/WF |
| Yearling / pup mortality | 22 +- 10% (n=93) / 31 +- 8% (n=127) | same | same | same | AB/WF |
| Adult annual mortality | 28.8% (95% CI 20.4-38.4; 89.6 dog-yr) | Laikipia-Samburu, Kenya, 2000s | radio-telemetry known fate | Woodroffe 2011, J Mammal 92:305-315, doi 10.1644/10-MAMM-A-157.1 (Results, Mortality) | WF |
| Yearling mortality | 30.9% (9.5-61.1; 11 dog-yr) | same | same | same | WF |
| Pup survival to 6 mo / 12 mo | 86% (161/187) / 71% (65/91), no CI | same | den and pack counts | same (Results) | WF |
| Cohort size leaving den | 7.3 (SD 2.9, range 2-14, n=35 cohorts) | same | pack counts | same (Fecundity) | WF |
| Age at first breeding | 28, 31, 39 months (n=3 alpha females) | same | observation | same | WF |
| lambda (matrix model) | 1.21 (Laikipia); 1.04 quoted for Selous | | | same (Discussion) | WF |
| Post-handling 12-mo survival | 87.6% (106/121), plain proportion, no CI | E Serengeti / Loliondo, 2006-2016 | collar tracking | Jackson et al. 2019, Ecol Evol 9:1110-1118, doi 10.1002/ece3.4798 | WF |
| Adult mortality 0.15 +- 0.03, pup 0.68 +- 0.20, breeding age 3, P(breed) 0.58 | PVA input table, provenance per row not given (model adapted from Ginsberg & Woodroffe 1997) | | | Devenish-Nelson et al. 2013, PLoS One 8:e58060, doi 10.1371/journal.pone.0058060 | WF |
No Serengeti individual-based survival numbers were retrieved. Burrows et al. 1994 report that adult longevity and pack life fell once routine
intervention began, and that survival differed by intervention category [AB]; the numbers are in the full text (not read).

**c) Circularity.** Ginsberg et al. 1995 and Burrows et al. 1994 both fit stochastic models to the same counts: any s, f, or variance taken from their
Monte Carlo parameters is circular. Burrows' pack histories (individual longevity) are in principle independent of the counts but come from the same
monitoring programme (partial circularity). Selous, Laikipia and Jackson numbers are independent.

**d) Environment, disease, interventions.** Immobilisation, radio-collaring and vaccination were applied to the study packs from the mid-1980s; Burrows
et al. 1994 report five packs lost 2-5 months after collar handling (1985-90) and the remaining seven packs lost 5-12 months after the 1990 vaccination
[WF via Jackson 2019]. This is contested: Woodroffe 2001, Oryx 35:234, doi 10.1017/s0030605300031902 [AB] concludes intervention was extremely unlikely to
have caused the extinction. Rabies confirmed in one pack death 1985-90; canine distemper emerged in the ecosystem about 1993-94 (killed ~1/3 of lions)
[WF]. Lions tripled 1966-1998 and spotted hyenas rose 2,200 to 5,500 (Swanson et al. 2014, doi 10.1111/1365-2656.12231 [AB]; Jackson 2019 [WF]).
**Open population:** dogs persisted in Loliondo and Ngorongoro, and the post-2001 recolonisers descended from pre-extinction animals (Marsden et al. 2012,
Conserv Genet, doi 10.1007/s10592-011-0304-z [AB]), so "extinction" in the series is range loss/emigration plus mortality, not death of a closed population.

**e) Verdict: PARTIAL.** Good species-level rates with CIs, but the same-population individual data were not retrieved, and the series is confounded by
intervention, emigration and competitor trends.

---

## 2. Vancouver Island marmot, Canada, 1981-2000

**a) Count source.** FH2006 cite Bryant 1998 (PhD, Univ Victoria, "Metapopulation ecology of Vancouver Island marmots", 125 pp) and marmot.org
[FT]. FH2006 sizes (smallest size with an increase 2; final decline began at 3; final 3) are far below island totals (at least 235 counted in 1984, 300-350
peak, about 70 in 1997-98; COSEWIC 2019 [WF], BC IWMS 2004 [FT]). **So the series is almost certainly a single colony or sub-population, not the island
population; I could not identify which.** Speculative candidate (unverified): Mount Washington, the only surviving colony in the central/northern range in 1998
(marmots.org [WF]).

**b) Vital rates.**
| Parameter | Estimate | Population / period | Method | Citation | Tag |
|---|---|---|---|---|---|
| Pup survival | 61% (1987-93) vs 43% (1994-2003) | Vancouver Island colonies | tag resightings, apparent survival | Bryant 2004, Species at Risk 2004 Conf. extended abstract, p.1 (https://www.arlis.org/docs/vol1/69415913/bryant_edited_final_feb_8.pdf) | FT |
| Adult survival | 78% (1987-93) vs 72% (1994-2003); "current ~74%" | same | same; no CI in the abstract | same | FT |
| Mortality causes (25 carcasses since 1992) | predation 84% (wolf/cougar >=64%, eagle 4%, unknown predators 16%), winter 12%, unknown 4% | radio-telemetry | | same | FT |
| Daily death risk | 0.448% Aug, 0.196% Sep, 0.050% spring to 31 Jul, 0.015% hibernation | same | | same | FT |
| Breeding | about 1/3 of females >=2 y bred; first bred at 4 y (mean 3.6, SD 1.2, n=16); litters 3-4 in alternate years; litter mean 3.4 (SD 1.1, n=58); interval 1.9 y (SD 0.7, n=17); breeding rate unchanged between expansion (1980s-1993) and decline (1994-2003) | same | | Bryant 2004 FT; COSEWIC 2019 (citing Bryant 2005) WF | FT/WF |
| lambda | 1.07 "healthy" vs 0.88 "declining" | whole population, 2010s | Vortex PVA | Jackson et al. 2015 via COSEWIC 2019 | WF |
| Survival of released captive-born marmots: pup 0.500 (95% CI 0.375-0.616), yearling/adult 0.656 | captive-born animals released to the wild, not wild-resident | radio-telemetry, resighting | Aaltonen et al. 2009 | SN (not comparable) |
Other primary refs not read: Bryant 1996, Can J Zool 74:678-687 (reproduction in natural vs logged habitat); Bryant & Janz 1996, Can J Zool 74:667-677;
Bryant & Page 2005, Can J Zool 83:674-682 (timing and causes of mortality) [citations only, via secondary pages].

**c) Circularity.** Resighting survival is independent of counts in principle, but colony counts and mark-resight data come from the same censuses
(COSEWIC: "count and mark-recapture results suggested ... survival declined"); partial. Apparent survival is biased low by emigration.

**d) Environment, catastrophes, interventions.** Strong catastrophe signal: "much of the decline was due to distinct episodes of high mortality at particular
colonies" (Bryant 2000, cited in BC IWMS 2004 [FT]); colony survival rates are spatially correlated and single-year predation spikes occurred (marmots.org
[WF]). Predator-prey shift (deer down, cougar/wolf indices up), possible disease hypothesis, logging-created clearcut colonies that persist 5-19 y (median ~10;
sinks) [FT/WF]. **Interventions inside the series window:** captive breeding began 1997; 55 of 63 animals removed from the wild for captivity were taken
1997-2004 [WF], so removals overlap 1997-2000. Releases began 2003 (after the series). Metapopulation dispersal means the colony was not closed.

**e) Verdict: PARTIAL.** Same-region, same-era survival and fecundity exist, but as point estimates without uncertainty in what I could read; may become
GOOD if Bryant 1998 or Bryant & Page 2005 give CIs. Colony identity and the metapopulation structure are the main obstacles.

---

## 3. Middle spotted woodpecker, Sweden, 1967-1982

**a) Count source.** Pettersson 1985, Biol Conserv 32:335-353, doi 10.1016/0006-3207(85)90022-9 (no abstract in OpenAlex; full text not read). FH2006: min size
5, final decline from 7, final 7, one census interpolated [FT]. Last Swedish pairs disappeared 1982 (Nilsson et al. 1992, Ornis Svecica 2:13-21, doi
10.34080/os.v2.22398 [FT]; another source says 1983 [SN]). Province, pair counts and census method not retrieved. Companion: Pettersson 1985, Ecography
8 (doi 10.1111/j.1600-0587.1985.tb01152.x) [AB]: oak-area size and isolation were the best predictors; about 75 ha of oak gave a 50% chance of regular occurrence;
suggests extinction debt or range-edge habitat.

**b) Vital rates (all from Spain; no same-population data found).**
| Parameter | Estimate | Population | Method | Citation | Tag |
|---|---|---|---|---|---|
| Adult annual survival | 0.786 +- 0.074 | Cantabrian Mts, Spain, 2000s | radio-tagged and ringed birds | Robles et al. 2007, Ecography 30:685-694, doi 10.1111/j.2007.0906-7590.05179.x | AB |
| Post-fledging (first 3 wk) / first-year survival | 0.359 +- 0.077 / 0.255 +- 0.044 | same | same | same | AB |
| Nest success; nestling survival | 59/72 (81.9%); 70/94 (74.4%) | same, 2000-05 | nest monitoring | Robles et al. 2008, Auk 125:131-139, doi 10.1525/auk.2008.125.1.131 | WF |
| Clutch; fledglings per successful nest | 5.1; 3.1 | same | same | same | WF |
| Pairing success of territorial males | 83.3% (190/228); annual 77.1-97.4% | same | territory surveys | same | WF |
| Adult survival 0.67 (resighting) | not known | resighting | Michalek & Winkler 2001, as tabulated in Pasinelli 2006, Ann Zool Fenn 43:96-111 | SN (unverified) |
Age at first breeding was not retrieved. Whether "+-" is SE or SD is not stated in the abstract.

**c) Circularity.** None (different country and decade).
**d) Environment, interventions.** Loss and fragmentation of old oak woodland at the species' range edge; no catastrophe, harvest, or management intervention
found in the sources I could read. Robles 2007 found no fragmentation effect on survival, which suggests habitat area acts through pairing/recruitment rather than s.
**e) Verdict: PARTIAL.** Species-level, other country, SE/SD ambiguity; plausible prior for s of about 0.8 and nest-stage fecundity.

---

## 4. Red-cockaded woodpecker, 1968-1981: Tall Timbers Research Station, Leon County, northwest Florida

**a) Count source and identification.** FH2006 cite Baker 1983, "Decline and extirpation of a population of Red-cockaded Woodpeckers in northwest Florida", pp. 44-45
in Wood (ed.) Red-cockaded Woodpecker Symposium II, Florida Game and Fresh Water Fish Commission, Tallahassee [FT]. I could not obtain Baker 1983, but Cox & McCormick 2016
(J Field Ornithol 2016, doi 10.1111/jofo.12165, read in full [FT]) state that RCWs occurred on Tall Timbers Research Station from at least the early 1940s;
**11 potential breeding groups in 1970; population declined and disappeared in 1981.** Population identified with reasonable confidence (Tall Timbers); count table
itself not seen. FH2006 values: min 16, final decline from 19, final 10 individuals.
Baker's causes (via Cox & McCormick p.2): (1) inbreeding/isolation (nearest group >5 km away; natal dispersal usually <3 km); (2) hardwood midstory encroachment, partly through
fire-exclusion research plots (one group possibly lost after fire was excluded from a 10-ha plot from 1967); (3) declining quality of ageing loblolly/shortleaf cavity trees.

**b) Vital rates (species-level; Sandhills NC and others).**
| Parameter | Estimate | Population | Method | Citation | Tag |
|---|---|---|---|---|---|
| Annual survival: breeding males 76%, helper males 80%, breeding females 69% | NC Sandhills, 6 y, ~500 marked | banding/resighting | Walters, Doerr & Carter 1988, Ethology 78:275-305, doi 10.1111/j.1439-0310.1988.tb00239.x | AB (via snippet) |
| Adult survival about 75% M / 70% F (Sandhills), 80/75 (coastal NC), 86/80 (Florida panhandle) | rangewide summary, source not cited on page | | FWS species page (https://fws.gov/species/red-cockaded-woodpecker-dryobates-borealis) | WF |
| First-year mortality 68% F, 57% M; peak breeding age 4-8; clutch 2-4 (population means 2.9-3.5); successful nests fledge 1-4 | same FWS page (no primary cited) | | | WF |
| Female annual mortality 24% non-dispersing, 59% dispersing | Sandhills | | Daniels 1997 (Virginia Tech thesis) | AB |
| 1.9 fledglings per successful nest; 9-25% of groups did not nest | Sandhills | nest monitoring | LaBranche & Walters 1994, Wilson Bull 106:258-271 | SN |
| Helpers do not change variance in breeder survival | Sandhills | | Reed & Walters 1996, Auk 113:608-616, doi 10.2307/4088981 | AB |
| Tropical storm Fay 2008: adult females 50% survived vs 100% of adult males; no young of the year survived | **Tall Timbers, 2006-2015 reintroduction (same site, later era)** | census | Cox & McCormick 2016, p.7 | FT |
| Catastrophe vulnerability judged low because helpers buffer variance in mortality and reproduction | individual-based PVA | | Walters, Crowder & Priddy 2002, Ecol Appl 12:249-260, doi 10.1890/1051-0761(2002)012[0249:pvafrc]2.0.co;2 | AB |

**c) Circularity.** None found. No independent demographic study of the 1968-81 Tall Timbers birds was found beyond Baker's note.
**d) Environment, interventions.** Fire exclusion and hardwood encroachment (an exogenous, slow driver, not a stochastic one); isolation; no translocation or supplementation in
the period (the first RCW reintroduction was in 1998 per Cox & McCormick). Tropical storms are a recurrent catastrophe class for the species (Hooper & McAdie 1995, cited in Cox & McCormick [FT]).
**e) Verdict: PARTIAL.** The best-studied species of the nine (breeder survival 0.69-0.86, with strong cooperative-breeding structure that the null model lacks), but
rates are from other populations; the Tall Timbers series was driven by habitat degradation and isolation, not by demographic stochasticity.

---

## 5. European golden plover, Scotland, 1973-1990

**a) Count source.** Parr 1992, "The decline to extinction of a population of Golden Plover in North-East Scotland", Ornis Scand 23:152-158, doi 10.2307/3676443 (no abstract
available) [AB]. FH2006: min 85, final decline from 112, final 7. Study area **probably Kerloch Moor, NE Scotland** (inference: Parr 1993, Bird Study 40:223-231,
doi 10.1080/00063659309477187, describes a declining golden plover population there during predator removal [AB]); not verified. Earlier marked-bird study: Parr 1980, Ornis Scand 11:179-189,
doi 10.2307/3676122: six years, NE Scotland, winter losses, return timing, egg predation; "production appeared sufficient to keep the population stable" [AB]. Its survival numbers were
not retrievable.

**b) Vital rates.**
| Parameter | Estimate | Population | Method | Citation | Tag |
|---|---|---|---|---|---|
| Adult annual survival | 0.73 ("all adults"); no CI or method on page | Britain, ringing-based (presumed) | not stated | BTO BirdFacts (https://www.bto.org/learn/about-birds/birdfacts/golden-plover) | WF |
| Clutch | 3.94 +- 0.28 (range 2-4); breeds typically at 1 y | Britain | | same | WF |
| Nest fate on the study moor | no golden plover chicks hatched at Kerloch 1986-89; foxes took all nests 1987-89 (n=8 nests in control years) | Kerloch | nest monitoring | Parr 1993 [AB]; detail from [SN] | AB/SN |
| Productivity driven by cranefly (Tipulidae) abundance, linked to August temperature | Peak District, England | long-term monitoring | Pearce-Higgins et al. 2010, Global Change Biol 16:12-23, doi 10.1111/j.1365-2486.2009.01883.x (no values retrieved) | AB |
No chick survival or fledging rate per pair was retrieved. A Pacific golden plover survival study (Oahu) turned up but is a different species and is not used.

**c) Circularity.** Parr's marked-bird work is individual-based and independent in principle, but numbers were not obtained; BTO 0.73 is independent of the Scottish counts.
**d) Environment, interventions.** **Predator removal (crows, gulls) on the study moor in 1986-89 falls inside the series**, and fox predation rose; winter weather and spring return
timing affect the population (Parr 1980 [AB]); possible plantation-edge avoidance (Stroud et al. 1990, Bird Study 37:177-186, doi 10.1080/00063659009477055 [AB]) not linked to this moor.
**e) Verdict: PARTIAL (low confidence).** Same-population individual data exist (Parr 1980) but I could not read them; the only number is a secondary species-level 0.73.

---

## 6. Whooping crane, USA, 1986-2003 (peak winter counts)

**a) Count source and identification.** FH2006 cite T. Stehn, USFWS, personal communication; no published series [FT]. FH2006: 16 y, min 3, final decline from 6, final 2.
**Identification as the Rocky Mountain (Grays Lake) cross-fostered flock is consistent but not directly verified:** it is the only flock I found whose counts end in zero within 1986-2003 (the Florida non-migratory flock only began in 1993);
peak 33 in 1985; the last bird was presumed dead in spring 2002 (High Country News 25 Nov 2002, https://www.hcn.org/issues/239/13567/ [WF]; Stehn is quoted and was part of the project);
winter counts were at Bosque del Apache NWR, New Mexico. FH2006's 16 y vs our 1986-2003 suggests the Williams series was extended with zeros.

**b) Vital rates.** I found **no numerical survival, fecundity or variance estimates for the Rocky Mountain flock.** What exists is qualitative:
| Item | Finding | Citation | Tag |
|---|---|---|---|
| Pairing and recruitment | birds imprinted on sandhills, did not pair or breed; flock never self-sustaining | Horwich 2001, Proc 8th N Am Crane Workshop; HCN 2002 | AB/WF |
| Fledged-bird mortality | power-line collisions 39.0% of known deaths; 76% of fledged-bird mortality during migration | Brown et al. 1987; Drewien et al. 1989, both via a secondary summary | SN |
| Necropsy causes, n=24 RMP birds | predation and collisions leading causes | Hartup et al. 2010, Proc 11th N Am Crane Workshop | AB |
| Sex bias | females apparently suffer higher early mortality (an observation, not a rate) | USFWS release 1981 | SN |
| Species-level, reintroduced eastern flock | 1-yr survival 81% overall (85.1% ultralight-led, 65.7% direct release); years 1-3 84% | Urbanek et al. 2016, Proc N Am Crane Workshop 13:42 | AB |
No adult survival with uncertainty for the wild Aransas-Wood Buffalo flock was retrieved either (a USGS chapter gives about 4% population growth for decades [SN]).

**c) Circularity.** Any survival "estimate" from the flock's own counts would be circular; none found.
**d) Interventions (open population; severe).** Cross-fostering of whooping crane eggs under sandhills 1975-1988/89 (about 288-289 eggs [SN]); predator control at Grays Lake 1976/77-89 (633 predators
removed 1976-84; Drewien et al. 1985 [AB]); a captive-reared female released 1981 [SN]; guide-bird trials in 1993-94 (3 wild adults held, 5 isolation-reared chicks; Drewien et al. 1997, Proc 7th
N Am Crane Workshop pp. 86-95 [AB]); ultralight-led migration trials from 1996-97 and an ultralight-raised female joining the flock in 1999 (HCN 2002 [WF]). Also drought, power lines.
After 1989 the series is an ageing cohort with essentially no recruitment plus occasional additions, which is the opposite of the null model's f.
**e) Verdict: POOR.** Qualitative only, no usable independent rates, and the series is dominated by management.

---

## 7. Hawaiian crow ('alala), 1992-2003 (wild population)

**a) Count source.** FH2006 cite USFWS 2003 Draft Revised Recovery Plan (68 FR 71128-71129) [FT]. The final plan (USFWS 2009, Revised Recovery Plan for the 'Alala,
https://ecos.fws.gov/docs/recovery_plan/090417.pdf, Part I pp. I-6, I-14 to I-15) [FT]: McCandless Ranch/South Kona population **12 birds in 1992 (including one juvenile; Engbring 1992), two in 2002**,
last pair not found after June 2002, presumed extirpated 2003. FH2006: 12 y, min 12 (never increased), final 2.

**b) Vital rates.**
| Parameter | Estimate | Population / period | Method | Citation | Tag |
|---|---|---|---|---|---|
| Annual survival | **79.8%** (log y = 405.1 - 0.202x, r2 = 0.95; "fits a 20.2% mortality rate") | wild, 1992-2002 | **regression of the count series; birds were not radio-tracked and carcasses were not recovered** | USFWS 2009, p. I-14, Fig. 2 | FT, **CIRCULAR** |
| Annual survival | 81% "modeled estimate from banded birds" | same site, pre-1992 | banding model, no CI given | NRC 1992 (The Scientific Bases for the Preservation of the Hawaiian Crow), quoted in USFWS 2009 p. I-14 | FT (secondhand) |
| Reproduction | only one wild juvenile known 1992-2003 (Kalahiki pair, 1992; last seen 1997) | same | monitoring | USFWS 2009 p. I-15 | FT |
| Age at first breeding; clutch | ~2 y females, 2-3 y males; 2-5 eggs (usually 3), one brood of 1-2 chicks | species | | USFWS 2009 p. I-8, citing Banko et al. 2002 (Birds of North America 648) | FT |
| Released juveniles: mortality about 40%/yr, "approximately double that of wild adults" | 27 captive-reared birds, 1993-98 | radio-tracking | USFWS 2009 p. I-19 | FT |
| Hatching from removed eggs | 17 eggs removed 1993-94, 13 hatched, 12 reared | | Kuehler et al. 1995, Oryx 29:261-266, doi 10.1017/s0030605300021256 | AB |

**c) Circularity: the headline 79.8% is circular (derived from the same counts).** The 81% banded-bird figure is independent but earlier and unquantified.
**d) Environment, disease, interventions.** **Egg removal from wild nests (1993-94) and releases of 27 captive-reared juveniles into the same area (1993-98)**; whether released birds are in
our "wild" counts is not stated. Wild adults were struck/harassed by the Hawaiian hawk ('Io; released-bird deaths: 7 'Io, 3 toxoplasmosis, 2 other infections, 1 mammal, 8 unknown); fatal toxoplasmosis
(Work et al. 2000); drought and poor fruit production during the releases; probable illicit shooting into the 1980s-90s; malaria/pox not a mortality source in released birds [FT, pp. I-11 to I-21].
**e) Verdict: PARTIAL.** Same-site banded-bird survival (0.81) exists but without uncertainty; fecundity is effectively zero, so s is not separately informative beyond the circular count decay.

---

## 8 and 9. North American wood turtle, Connecticut, 1974-1992 (populations A and B)

**a) Count source (verified).** Garber & Burger 1995, Ecol Appl 5:1151-1162, doi 10.2307/2269362 [AB, Rutgers record]. Two allopatric populations in a ~1,000-ha protected watershed,
New Haven County, south-central Connecticut, separated for ~100 y by a 1.5-km man-made pond; mark-recapture 1974-1993 (133 turtles, 1,176 observations). Populations were stable while public access
was denied and **both declined by 100% within about 10 years of the area opening to hiking and fishing**; mean age rose and adult females fell, but recruitment failure alone did not explain the loss.
FH2006: A: min 29, final decline from 31, final 6; B: 53, 58, 8. Which of A/B is which in our data is not known. Full text not read (JSTOR failed); I do not know whether the counts are raw captures
or abundance estimates.

**b) Vital rates (species-level only; none retrievable for the Connecticut populations).**
| Parameter | Estimate | Population | Method | Citation | Tag |
|---|---|---|---|---|---|
| Adult annual survival | 0.970 +- 0.016 SD (IPM); CJS 0.964, 90% interval 0.933-0.997; telemetry 0.983 (3 deaths/178 turtle-yr) | Michigan, 1998-2015 | CMR + telemetry | Schneider et al. 2018, J Herpetol 52(2), doi 10.1670/17-063 | WF |
| Annual recruitment to age 15 | 0.058 +- 0.019 SD; mean age at first capture 14.7 +- 5.2 SD; maturity 14-18 y | Michigan | IPM | same | WF |
| Apparent annual survival | 91.2% (95% CI 83.9-95.4); F 94.9% (81.6-97.8), M 92.8% (77.6-97.4), subadults 82.7% (68.6-91.3); yearly range 80.3-97.5% | central Maine, 5 y | CMR | Chatfield et al. 2023, Chelonian Conserv Biol 22:58-67, doi 10.2744/CCB-1548.1 (Results p.62) | WF |
| Nest survival 8% (2/24); PVA lambda 0.93 (0.91-0.95) | same | | | same | WF |
| Adult survival ~96% (lower bound 92%) | northern New Hampshire, 2007-2020 | closed-population loglinear | Hillman & Jones 2022, Can Field-Nat 136, doi 10.22621/cfn.v136i2.2783 | AB |
| Age at maturity 11-22 y; clutch 1-20 (mean 8-12), one clutch/yr with skipping; embryo mortality 20-80%; no quantitative hatchling/juvenile survival | Canada | review | COSEWIC wood turtle status report, ch. 6 (https://www.canada.ca/en/environment-climate-change/services/species-risk-public-registry/cosewic-assessments-status-reports/wood-turtle/chapter-6.html) | WF |
| Adult survival range 0.76-0.97 across N American freshwater turtles | | | Shine & Iverson 1995, via Schneider 2018 | WF |
| Removing 3 adults/yr from 100 leads to extirpation in ~50 y | | PVA | Compton 1999 (thesis), via secondary | SN |
| 50% adult decline in 7 y, Quebec | | | Daigle & Jutras 2005, J Herpetol 39:130-132, doi 10.1670/0022-1511(2005)039[0130:QEODIA]2.0.CO;2 | AB |
Also: Moore et al. 2025 (Endang Species Res 58:147-158, doi 10.3354/esr01440) expert elicitation: predators dominate hatchling/juvenile loss, roads dominate adult loss [AB]; Chatfield 2023 quotes it
as Moore et al. 2022 (adult 90.8%, juveniles 6-12 y 82.4%, lambda 0.912, nest survival 31%) [WF]; the dates do not match, check.

**c) Circularity.** The only same-population data are Garber & Burger's own mark-recapture, which is the count series (fully circular).
**d) Environment, harvest, interventions.** Human recreation (hiking, fishing) and probable collection or disturbance drove the loss; no active management; a long-lived species that matures at ~14-18 y,
so a 19-year series covers about one generation and the observed losses were rapid adult removal (an exogenous, step-like mortality source).
**e) Verdict: PARTIAL for species-level s and f with CIs; same-population independent data: none (POOR).** Species-level adult survival (0.91-0.97) is much higher than the low-s regime
where our calibration fails, and the process that ended these populations (human removal) is not in the null model.

---

## Summary table

| Population | Best survival source | Best fecundity source | Circularity flag | Interventions / non-null processes in series | Verdict |
|---|---|---|---|---|---|
| 1 Wild dog (Serengeti) | Woodroffe 2011 adult mortality 28.8% (20.4-38.4), Laikipia; Creel 1997 Selous 20 +- 6% | Woodroffe 2011 cohort 7.3 (SD 2.9); Serengeti individual data (Burrows 1994) not read | Monte Carlo fits in Ginsberg 1995/Burrows 1994 use the same counts | collaring, immobilisation, vaccination 1985-91 (contested); emigration; rabies/CDV; lions, hyenas | PARTIAL |
| 2 VI marmot (colony?) | Bryant 2004: adults 78% to 72%, pups 61% to 43%, no CI | Bryant 2004; COSEWIC 2019: litter 3.4 (SD 1.1), ~1/3 of females breed, alternate years | partial (same census programme) | episodic colony die-offs; predation; wild removals 1997-2000; dispersal | PARTIAL |
| 3 Middle spotted woodpecker | Robles 2007 (Spain) adult 0.786 +- 0.074 | Robles 2008 (Spain) 3.1 fledglings per successful nest, nest success 81.9% | none | habitat loss and isolation only | PARTIAL |
| 4 Red-cockaded woodpecker (Tall Timbers) | Walters 1988 breeders 0.69-0.80 (NC); FWS 0.80-0.86 (FL, unsourced) | LaBranche & Walters 1994 1.9 per successful nest (snippet) | none | fire exclusion, hardwood midstory, isolation; no management until 1998 | PARTIAL |
| 5 Golden plover (Kerloch?) | BTO 0.73 (unsourced); Parr 1980 not read | clutch 3.94; productivity not retrieved | none found | predator removal 1986-89; fox predation; winter weather | PARTIAL (low confidence) |
| 6 Whooping crane (Rocky Mt flock) | none | none (essentially no recruitment) | any count-derived s is circular | cross-fostering to 1988/89, predator control, captive-reared and ultralight additions to 1999 | POOR |
| 7 Hawaiian crow ('alala) | NRC 1992 banded 0.81 (no CI); 0.798 is count-derived | ~0: one wild juvenile 1992-2003; age 2, 3 eggs | **0.798 circular** | egg removal 1993-94; 27 captive releases 1993-98; 'Io; toxoplasmosis; shooting | PARTIAL |
| 8, 9 Wood turtle A, B (Connecticut) | Schneider 2018 0.970 +- 0.016 SD; Chatfield 2023 0.912 (0.839-0.954) | Schneider 2018 recruitment 0.058; Chatfield nest survival 8% | same-population data = the counts | public access opened (collection/disturbance); no management | PARTIAL (species-level); same-pop POOR |

## Cross-cutting caveats

1. **Survival values cluster at 0.7-0.8 for six of the seven vertebrate species** (wild dog 0.71-0.80, marmot 0.72-0.78, middle spotted woodpecker 0.79, red-cockaded woodpecker 0.69-0.86, golden plover 0.73, 'alala 0.80-0.81); wood turtle is 0.91-0.97. Independent priors exist exactly in the low-s region, but with ambiguous +- conventions and no same-population CIs.
2. **Closed-population violations** are documented for at least five series (wild dog, marmot, golden plover, whooping crane, 'alala) and the wood turtle loss was driven by exogenous human removal. Two series are sub-populations of a larger metapopulation (marmot colony, Tall Timbers RCW), and the wild dogs emigrated. These are not demographic-stochasticity extinctions.
3. **Two series are nearly deterministic decays** (whooping crane, 'alala: f approximately 0), so s is identified by the counts alone and any "independent" s from them is circular.
4. **Same-population individual-based data probably exist but were not accessible:** Burrows et al. 1994 (wild dog), Bryant 1998 PhD (marmot), Parr 1980 (plover), Pettersson 1985 (woodpecker), NRC 1992 (alala), Garber & Burger 1995 full text (turtle), Baker 1983 (RCW).
5. Tools: all web numbers came from fetch-tool summarisers unless tagged FT; spot-check before use. I did not read Williams et al. Table S1 or the Dryad population_data.csv, which would confirm exact sources and units for every series.

## Highest-value next tranche

Obtain full texts of Burrows et al. 1994, Bryant 1998 / Bryant & Page 2005, Parr 1980 and 1992, Pettersson 1985, Baker 1983, NRC 1992 and Garber & Burger 1995 (interlibrary loan or institutional access); check Table S1 and the Dryad CSV against these sources; then decide which series can carry informative priors (candidates: marmot, plover, 'alala banded-bird survival) and which are better treated as open or managed systems and excluded from the closed-null calibration (whooping crane, wood turtle, wild dog).
