# Held-publication repair: focused closure evidence

Reviewed source `394d4a6`, runner SHA-256
`92674ee8aa685b2a20bf5a689a3cbba836b195b8657ba8f79c5da161f315b765`.

**The reproduced held-publication retry defect is closed.** `hold()` constructs
its prospective set, publishes it, then changes memory. The add path in `take()`
calls `intend()` before execution creation. An exception therefore leaves memory
requiring a publication retry before a new execution can be created. An ambiguous
successful publication is harmlessly repeated. Removal follows the same ordering;
its failure retains a conservative in-memory ticket for an already-ended
execution, and a later successful removal reconciles the record.

`check_final_recovery.py` reuses the prior independent synthetic worker harness
and calls the real runner and atomic writer. `checks.json` records nine passing
checks:

- Four previous cases: no write failure or one failed rename, each followed by
  death before or after hint settlement. All recover one predecessor with every
  successor listing omitted, and finish with the serial library and zero open
  executions or superseded workers. Failed additions require two publication
  attempts before death; no-failure controls require one.
- Two ambiguous additions: the write and rename succeed, then the caller receives
  `EIO`. Both death positions still require two publications and recover exactly
  as above.
- Permanent addition failure: six publication attempts across three iterations,
  no execution or claim created, original queue unchanged.
- First removal failure before or after publication: both retry, finish with an
  empty held set, reproduce the serial library, and leave zero open executions
  or superseded workers.

Run from the repository root:

```sh
uv run --offline --python 3.12 --with numpy==1.26.4 --with scipy==1.11.4 \
  python analysis/astra/r3_final_recovery_20261104/check_final_recovery.py \
  > analysis/astra/r3_final_recovery_20261104/checks.json \
  2> analysis/astra/r3_final_recovery_20261104/checks.log
```

Runtime: Python 3.12.13, NumPy 1.26.4, SciPy 1.11.4. This is a bounded replay with
tiny deterministic batches and injected exceptions/death, not actual NFS/PBS
failure testing or scientific validation. The native suite and package bindings
are separate parent-review obligations. No production code changed.
