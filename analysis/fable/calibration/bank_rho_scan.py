"""Development scan: does an AR(1) environment (rho ~ U(0, 0.9), stationary unit-variance
z_t) in the no-feedback null bring the observed calibration summaries inside the selected
prior predictive? Otherwise identical to bank_tolerance_scan.py (prior (b), exact selection)."""
import sys
import numpy as np
CAP = 10 ** 9       # development rule: trajectories exceeding 1e9 are rejected and counted
sys.path.insert(0, "analysis/fable/calibration")
from bank_benchmark import designs, calib_features


def bank_rho(design, draws, rng, rho_max=0.9):
    years = design["years"]; L = len(years); n0 = int(design["counts"][0])
    s = 1 / (1 + np.exp(-rng.normal(0, 1.5, draws)))
    f = np.exp(rng.uniform(np.log(0.01), np.log(2.0), draws))
    sig = rng.uniform(0.02, 1.0, draws)
    rho = rng.uniform(0.0, rho_max, draws)
    lgs = np.log(s / (1 - s))
    n = np.full(draws, n0, dtype=np.int64); z = rng.standard_normal(draws)
    rec = np.empty((draws, L)); rec[:, 0] = n0
    alive = np.ones(draws, bool); overflow = np.zeros(draws, bool)
    for j in range(1, L):
        for _ in range(years[j] - years[j - 1]):
            z = rho * z + np.sqrt(1 - rho ** 2) * rng.standard_normal(draws)
            idx = np.flatnonzero(alive)
            st = 1 / (1 + np.exp(-(lgs[idx] + sig[idx] * z[idx])))
            ft = f[idx] * np.exp(sig[idx] * z[idx] - sig[idx] ** 2 / 2)
            n[idx] = rng.binomial(n[idx], st) + rng.poisson(n[idx] * ft)
            big = n > CAP                     # overflow guard: reject, count, and stop simulating
            overflow |= big; alive &= ~big; n[big] = 0
        rec[:, j] = n
        if j < L - 1:
            alive &= n > 1
    keep = alive & (rec[:, -1] <= 1) & ~overflow
    return rec[keep], overflow.mean()


if __name__ == "__main__":
    draws = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000
    rng = np.random.default_rng(20261011)
    print(f"prior (b) + rho ~ U(0, 0.9); draws per population: {draws}")
    print("population        accepted  overflow  pct(msq) pct(ac) pct(inc)  q@0.5   J(K=2000)  q@1.0   J(K=2000)")
    for name, d in designs().items():
        rec, ovf = bank_rho(d, draws, rng)
        c = calib_features(rec); cobs = calib_features(d["counts"][None, :])[0]
        pct = [(c[:, k] < cobs[k]).mean() * 100 for k in range(3)]
        mad = np.median(np.abs(c - np.median(c, axis=0)), axis=0)
        dist = np.sqrt((((c - cobs) / mad) ** 2).sum(axis=1))
        a = len(rec) / draws
        cells = []
        for t in (0.5, 1.0):
            q = (dist <= t).mean()
            cells.append(f"{q:.4f}  {2000 / (a * q) if q > 0 else float('inf'):9.3g}")
        print(f"{name:16s} {len(rec):8d}  {ovf:.4f}   {pct[0]:6.1f}  {pct[1]:6.1f}  {pct[2]:6.1f}   " + "  ".join(cells))
