"""Independent check: do no-feedback nulls reproduce Fagan & Holmes (2006) regressions?

F&H: s = years to extinction, N_0 = 1. D_s = ln(N_s / N_{s+1}).
Reported pooled-style fits: D ~ s: -0.50 + 0.034 s (all steps), -0.22 + 0.011 s (excl. s = 0).
Squared residuals ~ s: 0.66 - 0.047 s (all), 0.22 - 0.012 s (excl. s = 0).
Selection: monitored 12-21 y until <= 1 individual.
"""
import numpy as np

rng = np.random.default_rng(7)


def fits(paths):
    out = {}
    for label, drop0 in (("all", False), ("excl_final", True)):
        S, D = [], []
        for p in paths:
            lx = np.log(p[::-1])            # lx[s] = ln N_s, lx[0] = ln 1
            s = np.arange(len(p) - 1)
            d = lx[s] - lx[s + 1]
            if drop0:
                s, d = s[1:], d[1:]
            S.append(s), D.append(d)
        S, D = np.concatenate(S), np.concatenate(D)
        X = np.column_stack([np.ones_like(S, dtype=float), S])
        b = np.linalg.lstsq(X, D, rcond=None)[0]
        r2 = (D - X @ b) ** 2
        v = np.linalg.lstsq(X, r2, rcond=None)[0]
        out[label] = (b, v)
    return out


def select(N, tmin=12, tmax=21):
    hit = N <= 1
    first = np.where(hit.any(1), hit.argmax(1), -1)
    keep = np.where((first >= tmin) & (first <= tmax))[0]
    paths = []
    for i in keep:
        p = N[i, : first[i] + 1].astype(float)
        p[-1] = 1.0
        if np.all(p[:-1] > 1):
            paths.append(p)
    return paths


def branching(mu, sig, n=300_000, tmax=21, lo=10, hi=200):
    N = np.zeros((n, tmax + 1), dtype=np.int64)
    N[:, 0] = np.round(np.exp(rng.uniform(np.log(lo), np.log(hi), n)))
    for t in range(tmax):
        N[:, t + 1] = rng.poisson(N[:, t] * np.exp(mu + sig * rng.standard_normal(n)))
    return select(N)


def lognormal_walk(mu, sig, n=300_000, tmax=21, lo=10, hi=200):
    x = np.zeros((n, tmax + 1))
    x[:, 0] = rng.uniform(np.log(lo), np.log(hi), n)
    for t in range(tmax):
        x[:, t + 1] = x[:, t] + mu + sig * rng.standard_normal(n)
    return select(np.exp(x))


print("F&H 2006 reference: D~s  all -0.50 +0.034s | excl -0.22 +0.011s ; resid^2~s  all 0.66 -0.047s | excl 0.22 -0.012s")
for name, fn in (("branching (Poisson demog + env)", branching), ("log-normal walk (env only)", lognormal_walk)):
    for mu in (-0.2, -0.1, 0.0):
        for sig in (0.2, 0.4):
            paths = fn(mu, sig)
            if len(paths) < 200:
                print(f"{name:32s} mu={mu:+.1f} sig={sig}: only {len(paths)} paths")
                continue
            f = fits(paths)
            (ba, va), (be, ve) = f["all"], f["excl_final"]
            print(f"{name:32s} mu={mu:+.1f} sig={sig}: n={len(paths):6d} | D~s all {ba[0]:+.2f} {ba[1]:+.3f}s | excl {be[0]:+.2f} {be[1]:+.3f}s"
                  f" | r2~s all {va[0]:.2f} {va[1]:+.3f}s | excl {ve[0]:.2f} {ve[1]:+.3f}s")
