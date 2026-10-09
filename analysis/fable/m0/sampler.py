"""Fable's independent implementation of the protocol draft 0.3 generators (§3.1-3.2).

Written without reading Astra's sampler (analysis/astra/m0/), from the protocol text.

Annual post-recruitment census of all individuals. Each year t -> t+1:
    z_t ~ N(-m_t, 1)                      one environmental factor; m_t > 0 only under M_D
    logit s_t = logit s + sigma * z_t + log g(N_t)
    f_t       = f * exp(sigma * z_t - sigma^2 / 2) * g(N_t)
    N_{t+1}   = Binomial(N_t, s_t) + Poisson(N_t * f_t)
with g = 1 under M0 and g(n) = exp(-beta * (1/n - 1/N_ref)) for 0 < n < N_ref under M_A
(applied to recruitment and to the survival odds). Zero is absorbing. Under M0 the
expected per-capita growth E[s_t] + f does not depend on abundance.

The process runs annually through unrecorded years; only scheduled census years are
recorded. Observation: exact counts (M0, M_A, M_D) or binomial detection (M_O).
Selection S (exact matched endpoint): the first recorded census with count <= 1 is the
observed extinction census, and no earlier recorded census is <= 1.
"""
from dataclasses import dataclass
import numpy as np

N_REF = 50.0
_GH_X, _GH_W = np.polynomial.hermite_e.hermegauss(80)    # probabilists' Hermite nodes
_GH_W = _GH_W / _GH_W.sum()


def expit(x):
    return 1.0 / (1.0 + np.exp(-x))


def mean_survival(s, sigma):
    """E[expit(logit s + sigma z)], z ~ N(0,1), by Gauss-Hermite quadrature."""
    return float(np.sum(_GH_W * expit(np.log(s / (1 - s)) + sigma * _GH_X)))


@dataclass
class Generator:
    s: float                    # median adult survival, in (0, 1)
    f: float                    # recruitment per individual, >= 0
    sigma: float                # environmental scale, >= 0
    beta: float = 0.0           # M_A feedback strength (beta >= 0); 0 gives M0
    decline: str = "none"       # M_D form: none | linear | accelerating | step
    d: float = 0.0              # M_D rate (linear/accelerating) or step size k
    t_step: float = np.inf      # M_D step time (years after first census)
    horizon: float = 1.0        # L_i used to scale the accelerating form
    detect: str = "exact"       # M_O: exact | low_n | uniform

    def __post_init__(self):
        assert 0 < self.s < 1 and self.f >= 0 and self.sigma >= 0 and self.beta >= 0

    def g(self, n):
        out = np.ones_like(n, dtype=float)
        if self.beta > 0:
            small = (n > 0) & (n < N_REF)
            out[small] = np.exp(-self.beta * (1.0 / n[small] - 1.0 / N_REF))
        return out

    def shift(self, t):
        if self.decline == "linear":
            return self.d * t
        if self.decline == "accelerating":
            return self.d * t * t / self.horizon
        if self.decline == "step":
            return self.d if t >= self.t_step else 0.0
        return 0.0

    def expected_growth(self):
        """Arithmetic expected per-capita growth under M0 (abundance-independent)."""
        return mean_survival(self.s, self.sigma) + self.f


def step(n, gen, t, rng):
    z = rng.standard_normal(n.shape) - gen.shift(t)
    g = gen.g(n)
    logit_s = np.log(gen.s / (1 - gen.s)) + gen.sigma * z + np.log(g)
    s_t = expit(logit_s)
    f_t = gen.f * np.exp(gen.sigma * z - gen.sigma ** 2 / 2) * g
    return rng.binomial(n, s_t) + rng.poisson(n * f_t)


def observe(n, gen, rng):
    if gen.detect == "exact":
        return n.astype(float)
    p = 0.9 * np.ones(n.shape) if gen.detect == "uniform" else 1 - 0.3 * np.exp(-n / 10.0)
    return rng.binomial(n, p).astype(float)


def simulate(n0, census_years, gen, rng, reps):
    """Simulate `reps` trajectories from n0 at census_years[0]; returns recorded counts
    (reps x len(census_years)); the first census is fixed at n0 (matched initial state)."""
    years = np.asarray(census_years, dtype=int)
    rec = np.empty((reps, len(years)))
    n = np.full(reps, int(n0), dtype=np.int64)
    rec[:, 0] = n0
    t = 0
    for j in range(1, len(years)):
        for _ in range(years[j] - years[j - 1]):       # propagate through unrecorded years
            n = step(n, gen, t, rng)
            t += 1
        rec[:, j] = observe(n, gen, rng)
    return rec


def select_exact(rec, ext_index):
    """Selection S: first recorded census <= 1 occurs exactly at column ext_index."""
    le1 = rec <= 1
    first = np.where(le1.any(axis=1), le1.argmax(axis=1), -1)
    return first == ext_index


def interpolate(rec, census_years, interp_years):
    """Replace each listed census by linear interpolation (in years, unrounded) between
    the nearest censuses that are NOT themselves being filled, so adjacent gaps are
    filled jointly from genuine observations. Used only for fill sensitivities; the
    historical fill rule is unverified."""
    years = list(census_years)
    fill = set(interp_years)
    out = rec.copy()
    for y in interp_years:
        j = years.index(y)
        lo = max(k for k in range(j) if years[k] not in fill)
        hi = min(k for k in range(j + 1, len(years)) if years[k] not in fill)
        w = (years[j] - years[lo]) / (years[hi] - years[lo])
        out[:, j] = (1 - w) * rec[:, lo] + w * rec[:, hi]
    return out
