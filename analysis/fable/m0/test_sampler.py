"""Invariant tests for Fable's generators (protocol draft 0.3 §3.1). Run from repo root:
    ~/.local/bin/uv run --with numpy python analysis/fable/m0/test_sampler.py
Each check prints PASS/FAIL; the script exits non-zero on any failure."""
import sys
import numpy as np
sys.path.insert(0, "analysis/fable/m0")
from sampler import Generator, mean_survival, step, simulate, select_exact, interpolate, expit

rng = np.random.default_rng(20261009)
fails = 0


def check(name, ok, detail=""):
    global fails
    fails += not ok
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


# 1. Quadrature against Monte Carlo
z = rng.standard_normal(2_000_000)
for s, sig in [(0.3, 0.8), (0.9, 0.5), (0.97, 1.0)]:
    mc = expit(np.log(s / (1 - s)) + sig * z).mean()
    check(f"mean survival quadrature s={s} sigma={sig}", abs(mc - mean_survival(s, sig)) < 1e-3,
          f"quad {mean_survival(s, sig):.5f} mc {mc:.5f}")

# 2. Conditional-mean identity under M0, at several abundances (abundance independence)
gen = Generator(s=0.75, f=0.2, sigma=0.4)
lam = gen.expected_growth()
for n0 in (2, 10, 60, 400):
    n = np.full(400_000, n0, dtype=np.int64)
    nxt = step(n, gen, 0, rng)
    se = nxt.std() / np.sqrt(len(nxt))
    check(f"M0 E[N'|N={n0}] = N*lambda", abs(nxt.mean() - n0 * lam) < 4 * se,
          f"mean {nxt.mean():.4f} target {n0 * lam:.4f} se {se:.4f}")

# 3. Support and absorption
n = np.zeros(10_000, dtype=np.int64)
check("zero is absorbing", np.all(step(n, gen, 0, rng) == 0))
rec = simulate(30, list(range(1990, 2010)), gen, rng, 5000)
check("counts are non-negative integers", np.all(rec >= 0) and np.all(rec == np.floor(rec)))
absorbed = (rec[:, :-1] == 0) & (rec[:, 1:] > 0)
check("no recovery after zero", not absorbed.any())

# 4. M_A: identical to M0 at n >= 50; reduced expected growth at small n
ga = Generator(s=0.75, f=0.2, sigma=0.4, beta=8.66)        # Delta10 = 1 - g(10) = 0.5
n = np.full(400_000, 80, dtype=np.int64)
r0 = step(n, gen, 0, np.random.default_rng(1)); ra = step(n, ga, 0, np.random.default_rng(1))
check("M_A equals M0 above N_ref (same seed)", np.array_equal(r0, ra))
n = np.full(400_000, 10, dtype=np.int64)
m_a = step(n, ga, 0, rng).mean() / 10
check("M_A lowers expected growth at n=10", m_a < 0.85 * lam, f"M_A {m_a:.3f} vs M0 {lam:.3f}")
check("M_A multiplier in (0,1]", 0 < ga.g(np.array([1.0]))[0] <= 1 and ga.g(np.array([60.0]))[0] == 1)

# 5. M_D shifts the environment downward and lowers expected growth over time
gd = Generator(s=0.75, f=0.2, sigma=0.4, decline="linear", d=0.05)
n = np.full(400_000, 100, dtype=np.int64)
check("M_D growth at t=10 below t=0", step(n, gd, 10, rng).mean() < step(n, gd, 0, rng).mean())

# 6. M_O detection: recorded <= true and mean ratio as specified
go = Generator(s=0.75, f=0.2, sigma=0.4, detect="uniform")
rec_o = simulate(200, [0, 1], go, np.random.default_rng(5), 200_000)
rec_e = simulate(200, [0, 1], gen, np.random.default_rng(5), 200_000)
check("M_O uniform detection mean ratio about 0.9",
      abs(rec_o[:, 1].mean() / rec_e[:, 1].mean() - 0.9) < 0.01,
      f"{rec_o[:, 1].mean() / rec_e[:, 1].mean():.4f}")

# 7. Missing-year propagation: recorded mean after a 3-year gap equals N0 * lambda^3
rec = simulate(100, [0, 3], gen, rng, 400_000)
se = rec[:, 1].std() / np.sqrt(rec.shape[0])
check("3-year gap propagates three annual steps", abs(rec[:, 1].mean() - 100 * lam ** 3) < 4 * se,
      f"mean {rec[:, 1].mean():.3f} target {100 * lam ** 3:.3f}")

# 8. Exact selection
years = list(range(1970, 1993))
gdec = Generator(s=0.6, f=0.25, sigma=0.5)
rec = simulate(77, years, gdec, rng, 200_000)
keep = select_exact(rec, len(years) - 1)
sel = rec[keep]
ok = keep.sum() > 0 and np.all(sel[:, -1] <= 1) and np.all(sel[:, :-1] > 1)
check("selection keeps only first <=1 at the extinction census", ok, f"accepted {keep.sum()} of {len(keep)}")

# 9. Interpolation replicates a linear fill between neighbours
r = np.array([[10.0, 99.0, 30.0]])
check("interpolation", np.allclose(interpolate(r, [2000, 2001, 2002], [2001]), [[10, 20, 30]]))
r2 = np.array([[77.0, 999.0, 999.0, 43.0]])                 # adjacent gaps (Astra's 1188 case)
check("adjacent-gap joint interpolation",
      np.allclose(interpolate(r2, [1970, 1971, 1972, 1973], [1971, 1972]), [[77, 77 - 34 / 3, 77 - 68 / 3, 43]]))

# 10. Reproducibility
a = simulate(50, list(range(10)), gen, np.random.default_rng(7), 100)
b = simulate(50, list(range(10)), gen, np.random.default_rng(7), 100)
check("seeded reproducibility", np.array_equal(a, b))

print("FAILURES:", fails)
sys.exit(1 if fails else 0)
