# Bounded prior-work search record

5 October 2026, Hobart. Purpose: challenge the novelty and source fidelity of
protocol 0.2 before study selection. This is an orientation search, not a
completed systematic review or eligibility screen. It extends
[Astra's first review](astra_round1_review_20261005.md).

## Actual metadata queries

Queries ran on 5 October, with publication cutoff 2026-10-05 where specified.
The [returned-record ledger](vortex_prior_work_records_20261005.csv) preserves
query IDs, page ranks, provider IDs, DOIs and titles. Index metadata are discovery
leads: dates, duplicate records and citation links can be wrong.

| ID | Executed query URL | Returned / provider total | Coverage |
|---|---|---|---|
| Q0 | <https://api.openalex.org/works?search=extinction%20vortex&filter=to_publication_date:2026-10-05&per-page=200> | 200 / 31,636 | Unquoted, broad ranked pilot; first page only |
| Q1 | <https://api.openalex.org/works?search=%22extinction%20vortex%22&filter=to_publication_date:2026-10-05&per-page=200> | 200 / 1,193 | Quoted phrase; first page only |
| Q2 | <https://api.crossref.org/works?query.bibliographic=extinction%20vortex&filter=until-pub-date:2026-10-05&rows=100> | 100 / 107,980 | Ranked bibliographic query, not an exact phrase census |
| Q3a | <https://api.openalex.org/works?filter=cites:W2122879786,to_publication_date:2026-10-05&per-page=200> | 200 / 418 | Fagan–Holmes citing records, page 1 |
| Q3b | <https://api.openalex.org/works?filter=cites:W2122879786,to_publication_date:2026-10-05&per-page=200&page=2> | 200 / 418 | Same query, page 2 |
| Q3c | <https://api.openalex.org/works?filter=cites:W2122879786,to_publication_date:2026-10-05&per-page=200&page=3> | 18 / 418 | Same query, page 3 |
| Q4 | <https://api.openalex.org/works?filter=cites:W3158629465,to_publication_date:2026-10-05&per-page=200> | 20 / 20 | Williams citing-record page |

The three Q3 pages contain **418 unique provider IDs**, with no overlap between
pages; Q4 contains 20. Their intersection contains five IDs, giving 433 unique
provider IDs across the citation queries. Q4 unexpectedly includes the Williams
target article itself (DOI `10.1002/ece3.7555`), an index anomaly. DOI/version
deduplication and citation-link checking remain necessary. These counts establish
retrieval of the reported index pages, not completeness of the literature or a
screened-study count. A later systematic compilation should use stable cursor
pagination and verify completeness.

A read-only scout applied lexical matching to titles and available abstracts in
Q3–Q4 for conditioning, selection bias, null models, first passage, early warning,
final decline and population trends. This generated leads, not scientific
eligibility decisions. Astra assessed the closest leads against primary sources.
There was no independent dual screening of these results. Q0–Q2 were discovery
queries; their returned records were not all read in full.

## Targeted searches and source adjudication

The web searches included the exact strings `"extinction vortex" "conditional"
"Fagan"`, `"Quantifying the extinction vortex" "null model"`, `"Scaling the
extinction vortex" "conditioning"`, exact paper titles, and author/DOI queries
for Bayarri–Berger, O'Grady, Frankham, IUCN criteria and Nabutanyi–Wittmann.
Search-engine results supplied leads; the claims below use primary text or are
explicitly limited to abstracts.

| Lead | Text inspected / interpretation for this project |
|---|---|
| [Griffen & Drake 2009, final decline](https://doi.org/10.1098/rspb.2008.1558) | Author-posted introduction, methods and discussion. Conditional final-decline theory and laboratory tests substantially precede our concept; the proposed matched estimator comparison is a narrower question. |
| [Drake & Griffen 2009, passage times](https://doi.org/10.1111/j.1461-0248.2009.01325.x) | Primary abstract. Compares expansion and decline passage times experimentally; full methods remain to inspect before a novelty claim. |
| [Drake, Marty & Sau 2025](https://doi.org/10.1111/ele.70178) | Primary full-text methods/results inspected. A laboratory habitat-size/extinction-time scaling study; an adjacent empirical literature, not identified here as the same F&H/Williams reanalysis. |
| [Cerini, Childs & Clements 2023](https://doi.org/10.1038/s41559-023-01985-2) | Publisher abstract, references and data-availability statement. A conceptual timeline using several kinds of indicators; full discussion not inspected. |
| [Daskalova et al. 2020](https://doi.org/10.1038/s41467-020-17779-0) | Abstract and metadata only in this pass. Broad abundance-trend analysis; retain as a forward-frame/bias lead, not adjudicated equivalent work. |
| [Mawass et al. 2026](https://doi.org/10.1098/rspb.2026.0600) | Primary indexed introduction/methods/discussion inspected. Genetic feedback over long evolutionary timescales; guards against framing this study as a general test of whether vortices exist. |
| [Nabutanyi & Wittmann 2021](https://doi.org/10.1086/712805) | Final abstract and earlier accessible preprint already inspected; final full text still unverified. Do not claim final-version exclusion. |

Parameter/method checks used the primary O'Grady 2006 paper (Methods 2.1–2.3),
Frankham 1995 abstract, Bayarri–Berger 2000 equations 8–9, Talts et al. 2018 §4,
and IUCN v3.1 pp. 10 and 18. The [protocol review](astra_protocol02_review_20261005.md)
records the consequences and direct source links. Earlier Dennis,
Boettiger–Hastings, Hefley, Fagan–Holmes and Williams checks remain in the first
review rather than being relabelled as new searches.

## Stopping boundary

This pass found a closer precursor and several material specification errors.
It is sufficient to reject a broad novelty claim and recommend a bounded first
tranche. It is not sufficient to assert that no matched reanalysis exists.
Stage A must close the named full-text gaps, specify and complete its frozen
search, and record source-level inclusion/exclusion decisions before any claim
of systematic coverage. No publication contacts or data agreements were made.

## Draft 0.3 clarification

On 5 October Astra rechecked the introduction of Griffen and Drake (2009)
against the [author-provided full text](https://www.researchgate.net/publication/23784944_Scaling_rules_for_the_final_decline_to_extinction).
It explicitly describes conditional diffusion entering from the upper
boundary and reaching extinction without returning there. The F&H citation
is attached to support for logarithmic duration scaling. Consequently the
statement in Fable's message 1032 and protocol §9.3 that the paper does not
discuss conditioning is incorrect. This correction narrows the interpretation
of prior work; it does not establish that the proposed matched reconstruction
of all five F&H statistics has already been done. PMC direct opening returned
a browser challenge in this check, so the primary author-posted text was used.
