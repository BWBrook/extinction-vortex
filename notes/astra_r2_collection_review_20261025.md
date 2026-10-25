# W1 round-two collection and reconciliation review

Target `805f0079f5eb8157b351ee31c04a1ab91f3ca3f7`. Scope: saved collector
rows, reconciliation/comparison contracts, denominators and accounting.
The parent owns the independent archive and bound-settings audit; this
review does not duplicate it or claim independent raw-journal replay.

**Recommendation: accept the scientific contract for a routine W1 top-up
under the existing run2 binding.** The saved rows reconcile exactly. Retain
the three CAPPED outcomes, resume the 48 incomplete settings and keep the
full denominators. The standalone reconciler has validation limits that
must be distinguished from the separate archive/settings checks; the local
fixtures do not establish corruption in the actual outputs. Node clearance,
live PBS sizing and the independent archive verdict belong to the parent.

## Reproduced collection and selection

The two local summaries reproduce all status counts, error mappings,
incomplete lists and CPU sums. Round two's 4,847 distinct directories equal
round one's 4,846 incomplete plus its one invalid directory, with unchanged
`index`, `pop`, `outer`, `n` and `library` fields. The retained and replayed
sets are disjoint and cover all 14,544 W1 settings.

| W1 outcome | Retained round 1 | Round 2 | Combined |
|---|---:|---:|---:|
| COMPLETE | 9,695 | 4,798 | 14,493 |
| CAPPED | 2 | 1 | 3 |
| Incomplete | — | 48 | 48 |
| FAILED or invalid in final selected rows | 0 | 0 | 0 |

All 48 remaining settings are **primary n = 30**. All 7,200 primary n = 0
libraries and all 144 W1 check libraries are COMPLETE. The previously
invalid s18085 is now COMPLETE; it was not dropped. The new CAPPED row is
**s05404**, marmot, `MA_d10_0.5/121`, n = 30: 628 prefix hits through batch
347,402,198. Its bound proposal cap, rather than measured CPU, determines
that status. The two original cap-affected datasets remain in the union.

Setting counts are not numbers of usable outer datasets. From the combined
primary rows:

| Scenario | All nine populations COMPLETE, n = 0 | All nine COMPLETE, n = 30 | Any CAPPED, n = 30 | Any incomplete, n = 30 |
|---|---:|---:|---:|---:|
| b1: null prior predictive | 200/200 | 187/200 | 0 | 13 |
| b3: low-s null | 200/200 | 186/200 | 1 | 13 |
| b5: MA beta-min | 200/200 | 188/200 | 1 | 11 |
| b16: MA Delta10 = 0.5 | 200/200 | 189/200 | 1 | 10 |

Thus 750 of 800 n = 30 outer datasets currently have all nine libraries;
47 have an incomplete population and three have a CAPPED population. Keep
200 as every scenario/n denominator and keep check libraries separate.
These are library-availability counts, not fitted calibration or power.

## What the reconciliation tool establishes

The ordinary checks work: the bounded fixtures reject a mismatched row
identity, duplicate collection row, missing COMPLETE library and library
digest mismatch. Its scope matches the NOTE's listed count/order/K-th-batch/
path-length checks. Ten temporary cases preserve those controls and the
following limits of using this script alone:

**P2, standalone validation contract.** `p3_w1_reconcile.py:22–28,68–77`
checks each summary against its own settings and compares the round
directory sets. It does not compare all immutable sampling fields across
rounds. A synthetic change to `stream_tag`, `cap_batches`, `E` and the sampler
helper hash is accepted when the second summary matches those altered
settings. It also collapses duplicate settings directories into a dictionary.
For this collection, the independent check should establish full selected-row
equality and the exact reproduced settings SHA `248f9c7d…`; that closes the
actual-input issue without changing the production runner.

**P2, standalone archive contract.** Lines 35–39 silently overwrite duplicate
archive library names and ignore the embedded collection summary. Lines
53–58 validate record count/order and path length but not the collector's
full field-domain and selection contract. Fixtures accept a shadowed
duplicate archive member, a different embedded summary and an otherwise
well-ordered library whose paths fail selection S. These are limitations of
the reconciler, not findings about the actual archive. The parent's separate
audit checks duplicate names, exact embedded-summary bytes and every new
record's schema, parameter domains, identity bounds, path length and S.
Retain that receipt alongside the reconciliation result. The library audit
does not reconstruct all checkpoint histories or independently simulate the
random streams.

The reconciler keeps every library's uncompressed bytes in `libs`; it is not
a streaming archive validator. This is a memory/placement limitation, not a
scientific gate. Only tiny temporary archives were used locally here.

## Accounting and evidence qualifications

Round two's collector accounts for **49,492.955 useful + 17,974.070
outside-prefix = 67,467.025 CPU-hours**, including imported pilot CPU in
the useful total. Of the outside-prefix amount, **17,701.224 hours (98.48%)**
belong to the 48 incomplete settings; only **272.846 hours** belong to
COMPLETE settings. For incomplete settings, the field named `discarded`
means outside the currently usable contiguous prefix. Valid committed work
there can be reused when the missing earlier ranges finish. It is not
automatically lost CPU. Do not double-count imported pilot CPU when adding
accounted costs across rounds, or equate these totals with PBS allocation
or all CPU consumed by interrupted workers.

**P3 reporting.** The local collector establishes `incomplete`, not the
precise stop/requeue history of each of the 48 settings. The NOTE's statement
that all their shards were censored at the 48-hour limit and requeued needs
the raw checkpoint/claim evidence. Likewise `queue_left = 12,130` and
`claims_left = 3,237` count both waves in the shared run directory; they are
not W1-only remaining-work counts. Neither qualification prevents ordinary
recovery under the existing bound runner.

The saved Kunanyi receipt reports comparator exit 0 for 4,847 requested
settings: **1,643,296 byte-identical records across 9,336,542,588 shared
committed batches**, zero unmatched records and zero recorded problems.
The current comparator rejects duplicate requested settings, within-shard
duplicate identities, inconsistent cross-shard records and bad committed
journal hashes. This is meaningful evidence on the common non-pilot work
under two operational runners. It is not a comparison of every round-two
record, nor proof of positive common coverage for all 4,847 settings: exit
0 requires aggregate positive coverage. The per-setting JSON remains at
`/u/bwbrook/vortex/run1/s1b/probe/w1r2_determinism.json`; preserve it at the
next normal transfer, with its hash, to report positive/zero coverage and
settings excluded by either round's stopping point. No expensive replay is
needed to retrieve that existing receipt.

## Safe top-up contract

Use the existing **`p3_settings_r2.json` SHA
`248f9c7de660dcac19a3e6806fbf97bc512aca9cff42abd54e5fd0f4ee3bbd73`** and
`OUTDIR=run2`, with W1 top-up mode and a new submission tag. Do not create a
new settings file containing only 48 rows: its changed digest would break
the binding of their existing shards and defeat the intended continuation.
The current submitter explicitly requires the seeded settings filename and
digest for top-ups. It does not reseed. The existing runner can ignore
terminal settings and recover remaining work while preserving absolute
proposal caps. CAPPED rows are terminal outcomes to retain, not refill
targets. A later W1 collection replaces the earlier run2 snapshot; do not
count its already COMPLETE libraries again.

Archive location for the independent audit:
`/data/fable/vortex/v2_dev/p3/w1_r2/W1.tar.gz`, 824,755,048 bytes, SHA
`c12e5378589c010f6e4b01d1bbb3cbd19d4d61ca4675aced79269e1e4f0624cc`.
The local/expected embedded summary SHA is
`3cd158028c58477c1652aa727dcbec19450a2a507f016926b83b48774fd92fb5`.

## Reproduction and scope

```bash
PYTHONDONTWRITEBYTECODE=1 python3 analysis/astra/r2_collection_review_20261025/collection_checks.py
```

The JSON receipt records source/input hashes, exact saved-row arithmetic,
dataset availability and ten synthetic contract cases. Assertions verify
both rejected mutations and accepted counterexamples; they are not ten
claims of complete validation. No production archive, raw journal or remote
host was accessed in this delegate's work. No production edits, PBS actions,
simulations, fits or commits were made. Only this memo and
`analysis/astra/r2_collection_review_20261025/` were written.

25 October 2026, 12:02:04 AEDT (Australia/Hobart).
