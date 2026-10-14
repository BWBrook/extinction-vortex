# Stage 0 and descriptive case package: integrated review

Astra, 14 October 2026. Review of handoffs 1630 and 1642 at
`3437fcdcf751bce1a4a0622a9f80d6299b3e734d`, with three bounded reviewers.
Both checkouts were clean at that revision when this review began.

**Disposition:** accept the corrected core/Haley drafts and the completed
Stage 0 numerical report. Repair two material caribou presentation errors
and shorten the nine-series table. Continue the demographic-information
question through a bounded sampler/throughput prototype, with an explicit
target law and cost limits, before proposing fitted work. No empirical test
or fresh population simulation was run in this review.

## 1. Stage 0 reproduces; its interpretation needs narrowing

The [independent audit](astra_stage0_info_audit_20261014.md) matches all 800
original outers, replays all 14,400 evidence draws under the pinned runtime,
checks the 18 saved raw/member artifacts and independently recomputes every
reported diagnostic. The 7,200 neighbourhoods, 519 ties, zero rounded-radius
mismatch flags and zero unusable weight sets reproduce. All eight cells
have exactly 200 paired outer datasets. The 3,600 comparable b1/b3 member sets
also match the earlier D1c2 receipt. Current frozen-source and bank-metadata
hashes match; the whole bank and individual weights were not independently
recomputed in this audit.

At n=300, any-of-nine ESS<100 flags occur in 199 or 200 of 200 datasets in
every cell. At the low-s corner, medians include wild dog 3.21, marmot 6.31,
middle-spotted woodpecker 8.88, golden plover 4.32 and **wood turtle A 14.62**
for noisy E. The last population was omitted from the prose list. The other
four populations have noisy medians 46.50–198.53; ideal medians differ.

These measurements establish **weight concentration in the finite reference**.
They do not prove absence of mathematical support or that an unrun fitted
stage would be uninformative. The threshold was exploratory. I support not
commissioning the large fitted R1 stage now, while preserving that distinction.
This is a computational warning, not evidence that additional demographic
data have little scientific value.

The saved run is complete, but `report()` can accept missing outers and
incompatible inputs, and `run()` does not verify all imported-source and
bank-metadata bytes. A fixture demonstrates a silently reduced 199-dataset
denominator; independent checks show **no such error in the actual report**.
Add exact expected-key checks and output/input/source/member bindings before
reuse; reject positive-infinite weights and use boundary-safe ideal
log-likelihood arithmetic. Preserve the historical outputs and distinguish
retrospective verification from a pre-run binding. No rerun of the completed
bank diagnostic is required solely to repair these dormant guards.

The full log verifies 24:08.94 elapsed. Its 12,074,316 KiB peak RSS is about
11.52 GiB; the helper's value labelled GB used a different conversion. This
is a reporting-unit correction, not a resource overrun.

## 2. Caribou: two substantive presentation corrections

The [caribou artifact review](astra_caribou_artifact_review_20261014.md)
verifies the nine cached source hashes, 21 Maligne flights, 13 Purcells
crosswalks, 16/16 Banff values, nine survival rows and 19 composition rows.
Four generated CSVs and the PNG reproduce byte-for-byte; the PDFs pass
structural checks and render identically. Source values need no correction.

Before assembly:

1. **Map archive year to survey year.** All 14 Maligne composition rugs use
   the archive's shifted year but are labelled survey year. The archive adds
   one to these autumn observations. Preserve both fields and plot the survey
   year; explain the herd-specific survival-year conventions. Nine of the
   compositions match the corresponding Parks flight exactly, while five do
   not. Keep those source-class differences visible.
2. **Retain WSI general notes.** The new table keeps detail notes but loses
   general notes about incomplete coverage and unknown dates, particularly
   in 1996, 2003 and 2005. Keep both note fields and missing date components;
   constructed `YYYY-MM-00` strings are not valid flight dates.

Also fix the reversed panel references, narrow claims of absent/unpublished
data to the inspected-source boundary, and describe the event timeline as
manually compiled rather than generated. Coverage differences do not prove
no biological population change.

**Correction to my earlier review:** both WSI snapshots contain 92 rows,
including **23 Individuals rows**, with identical properties and geometries.
The prior prose count 25 was my error; the original machine receipt already
held 23. I corrected that sentence with an explicit dated note. The different
response hashes reflect generated feature IDs/timestamps, not lost source
observations.

## 3. Close the core/Haley corrections; finish the one-page table

The [follow-up review](astra_manuscript_tables_followup_review_20261014.md)
accepts core revision 2 and the revised Haley package for continued manuscript
assembly. Prior claim, notation, chronology and figure findings are resolved.
The relevant numerical evidence and source tables are unchanged; no repeat
analysis is needed.

The nine-series synthesis preserves the useful source distinctions, but the
file is 3,748 words and its table alone 1,731. It is not the agreed one-page
artifact. The follow-up memo supplies a concrete nine-row, five-column
replacement with a 606-word table/caption/footnote package. Fable can adapt
that copy, retain the detailed existing source ledger separately, and check
readable one-page pagination. Scope Haley's census method to 1987–1997 and
state that shared monitoring does not justify assuming independent
likelihoods; it does not prove universal conditional dependence either.

## 4. A finite next step for the information experiment

Message 1642 relays Barry's exact instruction from his Claude chat:
"Yes, I want the “how much demographic data” experiment. Go ahead with this
before I wake Codex, with my authority." This review supports continuing that
question, while keeping the completed Stage 0 distinct from any fitted stage.

The [informative-reference proposal](astra_informative_reference_proposal_20261014.md)
recommends screening new prior theta draws with the demographic likelihood
**before** simulating one path and applying S, A and a declared C neighbourhood.
An analytic Binomial/Poisson likelihood bound avoids an unknown posterior
normalizer. Restarting theta after a failed path is essential. This is a
simple auditable comparator before a shared tilted proposal, not a claim of
cheap sampling or sufficient information.

An independent mathematical challenge exposed a limitation of an initially
small pilot: the narrow C ball may yield almost no retained paths under its
caps even when the sampler is correct. The revised assignment therefore
first forecasts hit rates from existing bank mass and then measures
implementation/throughput, without treating predictable zero hits as evidence
of failure. Twenty predeclared target settings use two populations, b1/b3
trial 0, two information levels and both comparators, plus n=0 controls.
The whole prototype, including its bounded existing-bank scan and checks,
is capped at four workers and 30 minutes on a qualified deep-server. The
proposal specifies per-setting draw caps and balanced scheduling.

**Proposed allocation:** Fable implements and returns the checks, measured
costs and explicitly uncertain retention forecasts; Astra audits. Stop there.
No full posterior bank, fitted Stage 1, Kunanyi dispatch, new outer sample or
empirical inference is included. Do not infer a universal sample-size
requirement from two stylized information levels. Even infinite precision
on two rate functionals is not D3's six-parameter oracle.

Fable is next for the bounded caribou/table repairs and a response to the
sampler assignment. Manuscript assembly can proceed independently. No new
Barry decision is needed for these within-scope repairs and prototype;
materially different scientific scope or a larger campaign would return with
an explicit design and measured resource case.

14 October 2026, 16:50:20 AEDT (Australia/Hobart).
