"""Backward (extinction-aligned) versus forward (smallness-aligned) designs.

True dynamics: N[t+1] ~ Poisson(N[t] * exp(mu + sig * e) * N[t] / (N[t] + A)),
with A = 0 (no feedback; demographic plus environmental noise only) or A > 0
(component Allee effect, i.e., genuine small-population feedback). Censuses
C[t] ~ Binomial(N[t], p) add sampling error.

Backward design: keep series that go extinct within 12-21 years; regress
log growth on years-to-extinction s (as in Fagan & Holmes 2006).
Forward design: align every series at the first census below C* = 30,
whatever its later fate; estimate mean log growth over the next 5 years,
skipping the crossing year to avoid regression to the mean from census
error. Census 0 is treated as extinction and the series stops there.

Run: uv run --with numpy python vortex_forward_design.py
"""
import numpy as np

rng = np.random.default_rng(20261003)
N_SERIES, YEARS, P_DETECT, C_STAR = 200_000, 40, 0.8, 30


def simulate(mu, sig, allee):
    n = np.round(np.exp(rng.uniform(np.log(60), np.log(400), N_SERIES))).astype(np.int64)
    N = np.zeros((N_SERIES, YEARS + 1), np.int64)
    N[:, 0] = n
    for t in range(YEARS):
        lam = N[:, t] * np.exp(mu + sig * rng.standard_normal(N_SERIES))
        if allee > 0:
            lam = lam * N[:, t] / (N[:, t] + allee)
        N[:, t + 1] = rng.poisson(lam)
    return N, rng.binomial(N, P_DETECT)


def backward_slope(C):
    ext = C == 0
    first = np.where(ext.any(1), ext.argmax(1), -1)
    S, D = [], []
    for i in np.where((first >= 12) & (first <= 21))[0]:
        c = C[i, : first[i] + 1].astype(float)
        c[-1] = 1.0
        if np.any(c[:-1] < 1):
            continue
        lx = np.log(c[::-1])
        s = np.arange(1, len(c) - 1)                 # exclude the final step
        S.append(s), D.append(lx[s] - lx[s + 1])
    n_series = len(S)
    S, D = np.concatenate(S), np.concatenate(D)
    return np.polyfit(S, D, 1)[0], n_series


def forward_growth(C):
    below = (C < C_STAR) & (C > 0)
    first = np.where(below.any(1), below.argmax(1), -1)
    ok = np.where((first >= 1) & (first <= YEARS - 7))[0]
    g, start = [], []
    for i in ok:
        c = C[i, first[i] + 1 : first[i] + 7].astype(float)     # skip crossing year
        if np.any(c == 0):
            c = c[: np.argmax(c == 0)]                           # stop at extinction
        if c.size >= 2:
            g.append(np.mean(np.diff(np.log(c))))
            start.append(c[0])
    g, start = np.array(g), np.array(start)
    lo = start < np.median(start)
    return g.mean(), g[lo].mean(), g[~lo].mean(), g.size


print(f"series={N_SERIES}, detection p={P_DETECT}, forward threshold C*={C_STAR}")
for mu, sig in ((-0.05, 0.25), (0.0, 0.25)):
    for allee in (0, 10, 25):
        N, C = simulate(mu, sig, allee)
        b, nb = backward_slope(C)
        fm, flo, fhi, nf = forward_growth(C)
        print(f"mu={mu:+.2f} sig={sig} Allee A={allee:2d}: backward D~s slope (excl. final) {b:+.3f} (n={nb}) | "
              f"forward mean log growth {fm:+.3f} (n={nf}); smaller-start half {flo:+.3f} vs larger {fhi:+.3f}")
