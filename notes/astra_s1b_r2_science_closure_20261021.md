# Stage 1b round-two scientific and comparison-contract closure

Target `83a6b406681d0c2aec788f8a5f1cb64e124865e4`; bounded recheck of
`p3_r2_determinism.py`, design §9 and the cost-reporting corrections since
`b34b5e1`. Only this memo and `analysis/astra/s1b_r2_science_closure/` were
written. No production code, data, settings or ledger were changed.

**Verdict: no scientific or reporting issue in this scope blocks the restart.**
The sparse comparison repair removes the production-scale memory failure,
and the revised design now states the material limitations of the cost
diagnosis. Two comparison-input checks remain necessary before treating the
standalone comparator as sufficient evidence for the full production
comparison. They do not require a change to the bound sampling runner or a
new production launch gate. Concurrency, dispatch and final-package clearance
remain with the parallel reviews.

## Repaired behavior

The local receipt records **20 synthetic cases**, each with asserted exit
code and relevant counts. Assertions include the remaining counterexamples;
this is not a claim that all 20 cases demonstrate correct validation.

- Sparse interval intersections count shared batches correctly across gaps
  and half-open boundaries, while excluding hits outside shared coverage.
- A **381,823,099-batch interval with one hit** uses only **17,104 traced
  peak bytes** inside the comparator call and finishes in about 3 ms. This
  verifies the former scale failure without constructing a large dataset.
- A missing requested directory, wrong journal digest, short committed
  prefix, out-of-range record, malformed JSON and missing identity field all
  exit **1** with a recorded problem.
- Different identities exit **1**; matching identities with different bytes
  exit **2**. Identical records with positive coverage exit **0**.
- No shared batches exits **1**. Shared batches with zero hits correctly
  count as positive coverage. An uncommitted journal suffix is excluded.

Positive coverage is aggregate. A setting with no new shard checkpoints can
appear with zero coverage alongside a positive setting and yield exit 0.
The per-setting receipt exposes this; it is appropriate for shared-pilot-only
settings, provided the scientific report states how many settings actually
replayed non-pilot batches.

## Remaining comparison-only issues

**P2 — duplicate identities can conceal a difference.** At comparator lines
29 and 62, dictionaries overwrite earlier records with the same
`(batch, proposal_in_batch)`. In a valid-hash fixture, run A contains two
committed records at the same identity, first with `theta.s = 0.4` and then
`0.5`; run B contains only the `0.5` record. The comparator exits **0** and
reports one identical record. The same problem occurs across overlapping
shard checkpoints. Matching a journal's checksum establishes byte integrity,
not valid identity multiplicity. Reject repeated identities within and across
shards, and reject inconsistent overlapping checkpoint coverage, before
using this comparator on production outputs. Alternatively, run the existing
strict journal audit first and retain its receipt.

**P3 — duplicate requested directories inflate totals.** Supplying the same
directory twice yields two settings and twice the batches/records in
`total`, although `settings` contains one entry. Require a unique directory
list or reject duplicates. This is another small diagnostic change.

These fixtures do not show corruption in the smoke or production data. The
parent independently rechecked smoke D with the earlier strict sparse audit,
including counts, ordering, unique identities and nonoverlapping ranges:
174,302 shared batches, 2,310 identical records and five settings with
positive non-pilot coverage; s00772 is shared pilot only. The parent also
verified the final source/stage bindings. That separate validation addresses
the comparator's remaining gaps for the actual launch evidence.

The comparator itself does not validate settings, stream tags, indices,
metrics or sampling-helper hashes; it compares the named journals. Those
bindings must come from the setting/source audit. A synthetic changed
settings payload leaves its result unchanged, as its current interface
implies. Require equality of immutable sampling fields and helpers across
rounds, while allowing the explicitly changed operational runner binding.

## Cost-language closure

`p3_w1_costs.py` and the saved cost, W1 collector and pilot collector JSON
are byte-identical to `b34b5e1`; their SHA-256 values are in the receipt.
The previous independent recomputation therefore remains applicable, and no
archive or cost reanalysis was repeated.

Design §9a now identifies the **4,251 completed settings out of 6,840**, the
proration used for the 1.19 ratio, and the **1.247 recorded-CPU ratio**. It
excludes unresolved/capped/invalid settings from full-cell inference, names
the 4,846-row scope of the 92k-hour restart heuristic and its omitted invalid
setting, labels the W2 range a planning scenario, and separates incomplete
outside-prefix work from a causal estimate of defect damage. §9d also
separates reservation history, allocated resources, PBS CPU and checkpoint
CPU. These corrections close the consequential interpretation issues.

Minor reporting cleanup remains:

- `NOTE.md:1055–1058` still repeats the earlier unqualified heavy-tail claim
  and says the 92k-hour estimate prices all 4,847 open settings. Update this
  summary to match the revised design.
- The design table's `Actual / projected` heading (line 391) remains loose:
  its numerator is estimated crossing cost plus outside-prefix discard.
  Lines 410–412 infer a typical setting's cost from reported median
  throughput and hit-rate ratios. Those separate medians do not establish
  the median cost ratio. Prefer “throughput and hit-rate medians are near
  projection among completed settings; unresolved costs remain unknown.”

These wording issues do not change the selected settings, caps, sampling law
or launch readiness.

## Reproduction

```bash
PYTHONDONTWRITEBYTECODE=1 python3 analysis/astra/s1b_r2_science_closure/closure_checks.py
```

Receipt: `analysis/astra/s1b_r2_science_closure/closure_checks.json`.
Comparator SHA-256:
`bf8809ccca10a4840885325d096638893871e1f584fcfd60f5e984e7e36b3561`.
The script uses temporary local journals and unchanged-input byte checks.
No remote reads, population simulations, reference sampling, fits, PBS
operations or production mutations were performed for this closure review.

21 October 2026, 20:56:32 AEDT (Australia/Hobart).
