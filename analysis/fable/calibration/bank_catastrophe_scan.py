"""Development scan: no-feedback null with demographic noise, AR(1) environment and
density-independent catastrophes (Shaffer 1981's non-genetic sources). Each year a
catastrophe occurs with probability p_c ~ U(0, 0.15); it multiplies survival and
recruitment by (1 - delta), delta ~ U(0.5, 0.99). Expected per-capita growth remains
independent of abundance. Prior (b) otherwise; exact selection; overflow guard 1e9."""
import sys
import numpy as np
sys.path.insert(0, "analysis/fable/calibration")
from bank_benchmark import designs, calib_features
CAP = 10 ** 9


def bank_cat(design, draws, rng):
    years = design["years"]; L = len(years); n0 = int(design["counts"][0])
    s = 1 / (1 + np.exp(-rng.normal(0, 1.5, draws)))
    f = np.exp(rng.uniform(np.log(0.01), np.log(2.0), draws))
    sig = rng.uniform(0.02, 1.0, draws); rho = rng.uniform(0.0, 0.9, draws)
    pc = rng.uniform(0.0, 0.15, draws); dl = rng.uniform(0.5, 0.99, draws)
    lgs = np.log(s / (1 - s))
    n = np.full(draws, n0, dtype=np.int64); z = rng.standard_normal(draws)
    rec = np.empty((draws, L)); rec[:, 0] = n0
    alive = np.ones(draws, bool); overflow = np.zeros(draws, bool)
    for j in range(1, L):
        for _ in range(years[j] - years[j - 1]):
            z = rho * z + np.sqrt(1 - rho ** 2) * rng.standard_normal(draws)
            cat = rng.random(draws) < pc
            mult = np.where(cat, 1 - dl, 1.0)
            idx = np.flatnonzero(alive)
            st = mult[idx] / (1 + np.exp(-(lgs[idx] + sig[idx] * z[idx])))
            ft = mult[idx] * f[idx] * np.exp(sig[idx] * z[idx] - sig[idx] ** 2 / 2)
            n[idx] = rng.binomial(n[idx], st) + rng.poisson(n[idx] * ft)
            big = n > CAP; overflow |= big; alive &= ~big; n[big] = 0
        rec[:, j] = n
        if j < L - 1:
            alive &= n > 1
    keep = alive & (rec[:, -1] <= 1) & ~overflow
    return rec[keep]


if __name__ == "__main__":
    draws = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000
    rng = np.random.default_rng(20261012)
    print(f"prior (b) + rho ~ U(0,0.9) + catastrophes (p_c ~ U(0,0.15), delta ~ U(0.5,0.99)); draws: {draws}")
    print("population        accepted  pct(msq) pct(ac) pct(inc)  q@0.5   J(K=2000)  q@1.0   J(K=2000)")
    for name, d in designs().items():
        rec = bank_cat(d, draws, rng)
        c = calib_features(rec); cobs = calib_features(d["counts"][None, :])[0]
        pct = [(c[:, k] < cobs[k]).mean() * 100 for k in range(3)]
        mad = np.median(np.abs(c - np.median(c, axis=0)), axis=0)
        dist = np.sqrt((((c - cobs) / mad) ** 2).sum(axis=1))
        a = len(rec) / draws
        cells = [f"{(dist <= t).mean():.4f}  {2000 / (a * (dist <= t).mean()) if (dist <= t).any() else float('inf'):9.3g}" for t in (0.5, 1.0)]
        print(f"{name:16s} {len(rec):8d}  {pct[0]:6.1f}  {pct[1]:6.1f}  {pct[2]:6.1f}   " + "  ".join(cells))
