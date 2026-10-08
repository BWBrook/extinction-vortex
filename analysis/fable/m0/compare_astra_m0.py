# Same configurations with Fable's sampler (run from repo root).
import sys
import numpy as np
sys.path.insert(0, "analysis/fable/m0")
from sampler import Generator, step, simulate, select_exact
rng = np.random.default_rng(20261009)
for s, f, sig in [(0.75, 0.20, 0.4), (0.60, 0.25, 0.5), (0.95, 0.03, 0.3)]:
    for n0 in (3, 10, 60):
        x = step(np.full(200000, n0, dtype=np.int64), Generator(s, f, sig), 0, rng)
        print(f"onestep s={s:.2f} f={f:.2f} sigma={sig:.1f} N={n0} mean={x.mean():.4f} var={x.var(ddof=1):.4f}")
rec = simulate(77, list(range(1970, 1993)), Generator(0.60, 0.25, 0.5), rng, 200000)
acc = select_exact(rec, 22)
print(f"selection acceptance={acc.mean():.5f} (n={acc.sum()})")
print("mean recorded count at s=1..5 among accepted:", " ".join(f"{v:.3f}" for v in rec[acc][:, [21, 20, 19, 18, 17]].mean(axis=0)))
