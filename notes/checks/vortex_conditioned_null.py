"""Conditioned-on-extinction null for 'extinction vortex' signatures.

Log abundance x follows a Gaussian random walk with constant drift mu and SD
sigma: no density dependence, Allee effect, demographic stochasticity or
inbreeding. Paths are absorbed at x = 0 (quasi-extinction threshold N_q).
Extinct paths are aligned on first-passage time tau, as in retrospective
vortex analyses. Continuous-time theory: given tau = T the path is a Bessel-3
bridge whose law does not depend on mu; near T the mean distance above the
threshold is about 1.596 * sigma * sqrt(T - t).

Run: uv run --with numpy python vortex_conditioned_null.py
"""
import numpy as np

rng = np.random.default_rng(20261002)
SIGMA = 0.3
X0 = 3.0                 # start 3 log units (10 sigma) above threshold
TMAX = 400
NPATH = 100_000
NQ = 5.0                 # threshold abundance for the Poisson-count variant


def simulate(mu):
    x = np.full(NPATH, X0)
    alive = np.ones(NPATH, bool)
    tau = np.full(NPATH, -1)
    hist = np.empty((TMAX + 1, NPATH))
    hist[0] = x
    for t in range(1, TMAX + 1):
        x = x + (mu + SIGMA * rng.standard_normal(NPATH)) * alive
        hit = alive & (x <= 0)
        tau[hit] = t
        alive &= ~hit
        hist[t] = x
    return hist, tau


def aligned(hist, idx, end, kmax):
    """Rows k = 0..kmax: state at end - k for each selected path."""
    return np.stack([hist[end - k, idx] for k in range(kmax + 1)])


print(f"sigma={SIGMA}; start {X0} log units above threshold; {NPATH} paths; horizon {TMAX}")
for mu in (-0.05, -0.02, 0.0, 0.01):
    hist, tau = simulate(mu)
    ext = np.where(tau > 12)[0]
    lev = aligned(hist, ext, tau[ext], 11)          # lev[k] = x at tau - k
    steps = lev[:-1] - lev[1:]                       # steps[k] = x(tau-k) - x(tau-k-1)
    k = np.arange(1, 11)
    print(f"\nmu={mu:+.2f}: extinct={ext.size}, median tau={np.median(tau[tau > 0]):.0f}")
    print("  years before extinction k: " + " ".join(f"{v:6d}" for v in k))
    print("  mean x(tau-k):             " + " ".join(f"{v:6.3f}" for v in lev[1:11].mean(1)))
    print("  1.596*sigma*sqrt(k):       " + " ".join(f"{1.596 * SIGMA * np.sqrt(v):6.3f}" for v in k))
    print("  mean step into tau-k:      " + " ".join(f"{v:6.3f}" for v in steps[1:11].mean(1)))
    print("  SD of step into tau-k:     " + " ".join(f"{v:6.3f}" for v in steps[1:11].std(1)))
    late, early = steps[1:6], steps[6:11]
    print(f"  P(final-5 mean step < preceding-5) = {np.mean(late.mean(0) < early.mean(0)):.3f}; "
          f"P(final-5 var > preceding-5 var) = {np.mean(late.var(0, ddof=1) > early.var(0, ddof=1)):.3f}")

    # Spurious Allee effect: pooled regression of next step on current level
    # in the final 10 pre-extinction years, versus a matched window in survivors.
    x_now, x_next = lev[2:12].ravel(), lev[1:11].ravel()
    slope_ext = np.polyfit(x_now, x_next - x_now, 1)[0]
    surv = np.where(tau < 0)[0]
    if surv.size > 1000:
        win = aligned(hist, surv, np.full(surv.size, 200), 10)
        s_now, s_next = win[1:].ravel(), win[:-1].ravel()
        slope_surv = np.polyfit(s_now, s_next - s_now, 1)[0]
        print(f"  growth-on-level slope: extinct final decade {slope_ext:+.3f}; survivors {slope_surv:+.3f}")
    else:
        print(f"  growth-on-level slope: extinct final decade {slope_ext:+.3f}")

    # Poisson census of true abundance N = NQ * exp(x): sampling noise alone
    # raises the variance of observed log growth as the population shrinks.
    counts = rng.poisson(NQ * np.exp(lev[1:12]))
    obs_steps = np.diff(np.log(counts[::-1] + 0.5), axis=0)[::-1]   # obs_steps[j] = step into tau-(j+1)
    vl, ve = obs_steps[0:5].var(0, ddof=1), obs_steps[5:10].var(0, ddof=1)
    print(f"  Poisson counts (N_q={NQ:g}): mean var observed step final-5 {vl.mean():.3f} vs preceding-5 "
          f"{ve.mean():.3f}; P(var up) = {np.mean(vl > ve):.3f}")
