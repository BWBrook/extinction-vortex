# Astra audit of the informative sampler prototype

15 October 2026. Sampler/report reviewed at `b781db1`; `a7b8ae3` arrived during
review and changes STATUS only. This audit covers the sampling law, code,
bindings, unit checks and completed cap accounting. Parent review owns the
scientific/resource decision. No prototype file was changed.

**Recommendation: accept the completed bounded prototype as development
engineering evidence, with changes required before a longer run.** I found no
failure of the implemented target law in the valid, completed settings. The
checks do not establish statistical calibration, identification, power, or an
accurate cost for every population/outer. The aggregate four hits do not test
the distribution of retained paths. Resource availability is a separate
question; this audit does not declare the construction impractical.

## Law and completed execution

For fixed evidence E and fixed ball B, the pre-selection density after the two
independent acceptance uniforms is proportional to
`pi_b(theta) exp(h(theta)-H_E)`. One path per accepted theta, followed by S/A/B
rejection and then a new prior theta, gives exactly the declared joint target
for the numerical likelihood and finite ball. The Poisson-first ordering does
not alter that density. The noisy settings contain only n, k and r; the true
functionals enter the explicitly labelled ideal settings. The wrapper restores
the original parameter generator in a `finally` block and leaves the frozen
path dynamics intact.

The 20 bound settings all match the Stage 0 outer records, E and full-precision
radii. Current inputs are finite and valid, and all radii are positive.
Completed execution has:

| Quantity | Verified total |
|---|---:|
| Prior parameter proposals | 16,400,000 |
| Paths simulated | 865,652 |
| S/A-selected paths | 17,360 |
| Overflow rejections | 5,714 |
| Closed-ball hits | 4 |
| Hits exactly at the boundary | 3 |
| Expected hits from saved bank forecast at actual proposal counts | 3.012784 |

Each n=0 control stops at 100,000 proposals/paths. Each informative setting
stops at 1,000,000 proposals; every accepted theta was simulated in this run.
There is no path-cap truncation, time-cap termination or recorded bound
violation in the actual output. The cost file's expected-hit denominators
match those actual counts. The shell timeline reports 220 seconds, safely
inside the agreed ceiling. These checks reconcile saved counts and streams;
they do not independently reproduce all 865,652 paths.

## Findings before scaling

### MAJOR for an unattended larger run: enforce the actual dependencies

`p1_sampler.py:121–124` checks the manifest file's hash, the helper's own bytes,
and runtime versions. It does not check that the imported frozen source or
loaded bank bytes match the hashes *inside* that manifest. `metric()` at
127–130 calls `load_bank`, whose metadata/shape/ID checks do not establish byte
identity. Hashing the manifest does not hash its referenced files.

The synthetic guard check demonstrates that replacing the imported generator
leaves `check_binding` satisfied. For this audit, all 12 frozen source files,
the input hash, Stage 0 outputs and bank metadata were freshly reconciled
manually and match. No bank shard was rehashed or rescanned here. Thus this is
a missing enforcement path, not evidence that the completed run used changed
bytes. Before a larger run, verify the required source/bank dependencies,
record a receipt, and bind the exact mask/MAD and source radius to the output.
A changed generator or bank shard must cause a negative test to stop execution.

### MAJOR for a longer run: preserve partial results and enforce the total cap

`run_p1.sh:11–18` puts no timeout around tests or the bank scan. The pilot's
clock is checked between batches (`p1_sampler.py:224–228`), after both metrics
have been loaded, and the only result write is at line 285. A scheduler kill,
exception or interruption before the final write loses all completed setting
counts/samples; a long scan or batch can exceed the advertised global ceiling.
The completed 220-second prototype was unaffected.

Before an enlarged run, checkpoint completed batches atomically and record the
actual settings/round/stream position, counters and stop reason. Use the
scheduler or a wrapper to enforce a real total resource bound, leaving time to
flush a partial result. Test a forced early termination and verify the saved
partial denominators; do not silently turn it into a new stream on resume.

### MINOR in this prototype, required input checks for reuse

The proposal explicitly requires n=0 to have k=r=0, but `log_factors()` at
52–53 and the pilot at 236/251–252 accept any k/r when n is zero. A synthetic
runner fixture with `(n,k,r)=(0,1,1)` simulates paths and reports an ordinary
cap stop. A fixture with `r=NaN` silently rejects every proposal and reports an
ordinary proposal-cap stop with no bound violation. The check must reject
nonfinite or out-of-domain E, enforce integer noisy counts, and require
k=r=0 for n=0. Current saved E passes all those conditions.

`ball()` at 71–74 does not implement the proposal's explicit exact-equality
branch at zero radius. A feature difference of `1e-200` squares to zero and
is accepted at radius zero; exact equality would reject it. This artificial
edge case is not evidence of a problem at the four positive pilot radii.
Implement/test exact equality in the declared retained feature coordinates
when radius is zero, and check feature/mask/scale finiteness.

### MINOR: distinguish simulated exposure when a batch crosses the path cap

At 254–257, proposals/theta acceptances include the entire batch, while only
the prefix that fits the path cap is simulated. In a synthetic four-proposal,
three-path fixture the output correctly records four proposals and three
paths, but a per-proposal joint-hit forecast applied to all four treats the
unsimulated fourth theta as exposed to path selection. The completed pilot
never takes this branch, so its 3.012784 forecast is unaffected. For a larger
pilot, either cap each proposal batch by the remaining path capacity or
record the simulated proposal prefix separately and use the relevant
exposure denominator. Preserve the distinction between accepted theta and
simulated paths.

## Reproduced evidence and limits

Evidence lives in `analysis/astra/p1_sampler_audit/`.

- `qualification.txt`: deep-server was reachable at 11:24 AEDT, load about
  15 on 64 logical CPUs, 110 GiB available memory, 4.1 TiB free under `/data`.
  One worker; OMP/OpenBLAS/MKL/FlexiBLAS threads were fixed to one.
- `canonical_test_replay.log`: the original test command passed and its JSON
  exactly matches Fable's saved log. Elapsed 0.53 s; peak RSS 93,168 KiB.
- `remote_checks.py`, `.json`, `.log`: 1,344 independent full-PMF ratio cases
  (largest discrepancy `9.10e-13`), 200 ideal cases, 18 adaptive-quadrature
  checks (largest absolute error `8.61e-16`), and ordinary closed-boundary /
  adjacent-float tests. All valid-input checks passed.
- The same independent script exactly replays all 1,000 saved theta samples
  from the first bound batch of each setting; these are 1,000,000 parameter
  proposals with no path simulation. Eight heterogeneous-parameter wrapper
  comparisons, spanning both populations and four seeds, give identical
  paths, all parameter fields, selection flags and overflow flags. Each side
  simulated 4,000 unit-test paths. The original canonical test replay adds
  20,000 unit-test path generations; there was no new throughput pilot.
- All 20 Stage 0 E/outer/radius records, the helper and 12 frozen source files,
  the Stage 0 input/output hashes, bank metadata and 2e9 raw-attempt denominator
  were verified. Local and remote bound/scan/pilot JSON hashes match.
- `guard_repros.py`, `.json`, `.log` demonstrate missing fail-closed behavior
  and cap accounting with **stubbed banks and trajectories**, not a population
  pilot. The real prototype files were not modified.
- `local_checks.py`, `.json` verify the source/artifact reconciliation,
  canonical-test equality and forecast denominators. The cost projection file
  is local postprocessing, not a remote pilot artifact.

The independent check script took 2.40 s and 105,472 KiB peak RSS. No full bank
scan, new outer draw, bank build, fitted T model, empirical statistic or HPC
submission ran. The full closed-ball membership counts and saved weighted
bank sums remain Fable's scan results; this audit checked their bindings,
numerical rule and arithmetic, not their independent recomputation. Four
stored paths pass the final-count selection rule; the prototype does not save
matched theta/path identities for those retained hits, which should be added
if later audits need to inspect selected parameter-path pairs directly.

15 October 2026, 11:29 AEDT (Australia/Hobart).
