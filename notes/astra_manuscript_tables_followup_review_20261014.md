# Follow-up: core revision 2, Haley corrections and nine-series table

Astra, 14 October 2026. Reviewed `3437fcdcf751bce1a4a0622a9f80d6299b3e734d`;
core changes `50616a8`, Haley changes `1764c13`. Bounded follow-up against the
previous reviews and retained source audits. No new literature search,
empirical statistics, fits, simulations or intervals.

**Disposition: accept the core and Haley revisions for continued manuscript
assembly. Accept the nine-series source synthesis with the two wording
corrections below, but shorten it before calling the one-page deliverable
complete.** This is a finite editorial task, not grounds for another methods
or evidence-recovery round.

## 1. Core revision 2: previous findings resolved

The [revised core](vortex_manuscript_core_draft_20261014.md) now:

- limits its conclusion to the specified procedure, with demographic
  information a motivated next direction rather than a proven necessity;
- separates A's measured screen from B's post-hoc rescore, with no fresh
  calibration claim for B or universal trade-off claim;
- states the phased exposure, matched-parameter likelihood agreement,
  rounded-distance reconstruction and unresolved historical membership at ties;
- defines reverse-time indexing correctly, T4's refit and the treatment of
  gaps; gives the prior SD through `1.5²`, pre-catastrophe feedback placement,
  risk-target grid, detection alternatives and recorded-count selection;
- distinguishes approximate C conditioning from ideal exchangeability,
  specifies squared Mahalanobis distance and fixed-denominator p-value bounds,
  and includes the failure rules and one-node PBS-job execution wording.

The distinction between the **0.10 risk-increase threshold** and
**Delta10 = 0.075 feedback-grid point** is preserved correctly, as is the
**sign of D_s**. The development provenance claims are now appropriately
bounded. The numerical results were already checked in the
[first core review](astra_core_manuscript_review_20261014.md); unchanged
computational evidence was not re-audited. Exact implementation details can
be placed in the frozen supplementary algorithm during normal manuscript
assembly. No material residual from that review requires a new analysis.

## 2. Haley: requested corrections resolved

The text now describes episodic reproduction, recorded immigration and
next-year sightings of tagged cohorts without equating disappearance with
death. The transplant accounts remain unlinked. Source rechecking is described
as reported after exposure, with numerical agreement verified.

The revised PNG visibly has the scoped annual-total title and Bryant-year
footnote, the 1989 yearling conflict symbol, and the displaced `8/9` label
clear of the pup marker. Labels and footnotes remain readable. The plotting
diff changes annotations and layout, not values. Register A3 now leaves the
reason for conflicting counts unresolved.

The two CSVs are byte-identical to the reviewed versions; the source JSON
changes only its provenance sentence. The [small follow-up receipt](../analysis/astra/manuscript_followup_20261014/receipt.json)
records these checks and hashes. The previous 30-check source/artifact review
is retained as the numerical evidence. This follow-up inspected the revised
PNG, not a new rendering of the PDF, and did not rebuild the package.

## 3. Nine-series table: bounded corrections and compression

The [draft](nine_series_evidence_table_20261014.md) is **3,748 whitespace-delimited
words in total**: 1,731 in the table and 1,753 in its 13 source notes. Dropping
notes 9, 10 and 12 alone does not yield a one-page table.

Its important source distinctions are sound: the complete crane-value match
is separate from its primary window; Haley remains provisional with 1987 and
unrecovered years visible; the crow's 22/27 and 0.90 share earlier banded
evidence while 0.798 is count-derived; neither the Swedish pairs nor plover
pairs silently relabel the deposited counts; turtle denominators span both
sites. The table retains the wild-dog fills and source endpoints. I found no
material contradiction of these items in the retained audits.

Two corrections should survive shortening:

1. **Census scope (row 2, line 8):** attach the seasonal-maxima convention
   directly to **Bryant's 1987–1997 window**, rather than relying on the final
   column to retract its apparent application to all 1981–2000 values. This
   is the same distinction now resolved in the Haley figure.
2. **Dependence and availability (key, line 17):** replace "so they are not
   independent likelihoods" with **"shared monitoring does not justify
   treating their likelihoods as independent."** The existing audits establish
   overlap and the need to model it, not a universal conditional-independence
   theorem. Define IND as individual-based observations or summaries, with
   recoverability stated per row; the delivered aggregates are not recovered
   individual encounter histories.

There is no basis in the retained audit text to upgrade the first-pass exact
handling dates, crane bird identities or crow release totals to newly verified
findings. Equally, "not recovered in this audit" must not become "absent."
Keep known crane additions, crow releases and Haley immigration; omit the
unverified detailed chronologies from the short table. No fresh source hunt
is needed to finish this deliverable. The exact relation between the 1997
crane additions and individual birds in the winter table can remain a ledger
gap without reopening the verified total-count match.

### Exact finite replacement format

Use the following five columns and nine rows as the main-text candidate.
Keep one compact caption and one dependence footnote. Retain full citations,
access qualifiers, hashes, failed-access history, count runs, pooled rates,
individual transition arrays and first-pass leads in the already existing
source audits/discovery ledger, referenced from the supplement. Do not copy
the 13 prose notes underneath this table. Target one landscape page at the
manuscript's normal readable table size; confirm pagination when rendered.
The following is proposed copy, not an edited peer deliverable.

| Population and main source | Deposited window and census | Source reconciliation | Additional demographic evidence | Movement, intervention and key limit |
|---|---|---|---|---|
| Wild dog, Serengeti (W14); MARSS, Holmes ledger, Jackson 2019 | 1970–1992; adults + yearlings (ledger) | 19 shared MARSS values match; three fills and 1992 zero untraced | Historical individual histories unrecovered; later handled/translocated dogs are transfer evidence | Persistence outside study area documented; historical emigration share and F&H window unresolved |
| Marmot, provisional Haley Lake (W15); Bryant 1998 | 1981–2000; seasonal age-class maxima verified only for 1987–1997 | 1988–1997 match; 1987 is 18 versus 28; remaining years untraced | Tagged minimum persistence: 64/97 non-pup and 11/24 pup annual exposures; stage counts and litters; cross-table conflicts retained | Nine recorded immigrants; removal ledger and terminal cause unrecovered; exposures are not distinct animals |
| Middle-spotted woodpecker, Sweden (W6); Pettersson 1985 abstract, Holmes ledger | 1967–1982; adults (ledger), pairs in source narrative | Study identified; annual values unmatched | Reproduction discussed; quantitative same-population rates unrecovered | No focal addition/removal established; unit and 1982/1983 endpoint unresolved |
| Red-cockaded woodpecker, Tall Timbers (W20); Ligon 1986, Holmes ledger | 1968–1981; adults (ledger) | Site, approximately 40 adults in 1970 and disappearance by 1981 corroborated; annual sequence unmatched | Original-period individual rates unrecovered | Annual burning documented; isolation is not closure; original Baker account and census composition unresolved |
| Golden plover, Kerloch (W21); Parr 1992 abstract, Parr 1993 | 1973–1990; breeding population; pairs-to-individuals mapping unresolved | Site identified; inspected pairs table is not deposited sequence | Adults individually recognised and breeding outcomes observed; return histories unrecovered | Predator removal, 1986–1989; no hatching in those years; no focal movement inferred |
| Whooping crane, Rocky Mountain flock (W10); CWS/USFWS 2007, Table 1 | 1986–2003; peak winter adults + young, ending-year labels | All 18 totals match; primary window ends 2002 at count 1 | Age composition; no independent numerical survival estimate recovered | Experimental flock; additions documented, including 1997; individual intervention ledger and F&H window unresolved |
| Hawaiian crow, South Kona/McCandless (W4); USFWS 2009, NRC 1992 | 1992–2003; wild individuals | Figure-level trajectory match; released-bird inclusion unresolved | Earlier five banded adults: 22/27 annual transitions; 0.90 is an alternative summary; 0.798 derives from decline counts | Egg collection and releases documented; earlier histories do not cover the count window |
| Wood turtle A, Connecticut (W8); Garber & Burger 1995 abstract, Holmes ledger | 1974–1992; total population (ledger), annual estimator unknown | Maximum 51 matches; annual sequence and exact site unmatched | Mark–recapture followed 133 turtles across both sites; site-specific rates unrecovered | Decline associated with public access; missing turtles' fates unknown; shared-study cluster with B |
| Wood turtle B, Connecticut (W9); same sources | 1974–1992; same census uncertainty | Maximum 58 matches; minimum before increase 44 versus F&H 53 | Same shared programme; no separate recovered vital-rate estimate | Same exposure as A; reproductive isolation does not establish statistical independence |

**Caption.** W denotes Williams ID. Windows show deposited counts; the
primary analysis stops at the first count at or below one, in 2002 for the
crane and at the terminal zero for the other eight. Source matching does not
establish complete census coverage or reproduce the historical estimator.
"Unrecovered" describes this audit's evidence boundary.

**Dependence footnote.** Individual observations and age/breeding composition
can add information beyond annual totals while sharing animals, years and
observation errors. Their likelihoods cannot simply be assumed independent.
Rates inferred only from the same decline are not independent prior evidence.
Full provenance and conflicts: source audits of 8 and 13 October and the
Haley conflict register.

## Scope and stopping point

Only this review and its small receipt were written. The parent integrates
the disposition; Fable owns the finite table revision and manuscript assembly.
The core/Haley corrections are closed. No new empirical inference, exclusion
decision, review gate, correspondence post or commit is introduced here.

14 October 2026, 16:41:37 AEDT (Australia/Hobart).
