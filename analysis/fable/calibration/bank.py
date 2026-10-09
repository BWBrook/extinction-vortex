"""Bank construction for the conditional calibration (protocol §3.4), with provenance.

Common to every null variant (Astra 0.5 review): the same prior (b) for (s, f, sigma),
the same exact matched selection, the same overflow cap (trajectories exceeding CAP are
rejected and counted), and per-draw provenance (draw index, parameters, overflow count).

Structural no-direct-feedback null (proposed H0 wording, draft 0.6): given the parameters
and the exogenous environment (z_t, catastrophe indicator B_t), each individual's survival
probability and expected recruitment do not depend on N_t, and the environment evolves
independently of N. Variants:
  iid      M0: z_t iid N(0,1)
  ar       z_t AR(1), rho ~ U(0, 0.9)
  cat      iid z_t plus catastrophes: B_t ~ Bernoulli(p_c), p_c ~ U(0, 0.05) per year,
           multiplier (1 - delta) on survival and recruitment, delta ~ U(0.5, 0.95)
  ar_cat   ar + cat
  heavy    z_t iid standardised Student-t, nu ~ U(2.5, 30) (continuous heavy tails; the
           Reed et al. 2003 "continuous tail" reading of die-offs)
The catastrophe prior is exploratory: Reed et al. (2003) report ~14% die-off occurrence
per generation; generation lengths of >= 3 years give annual rates of about <= 0.05.
"""
import csv, hashlib, json, os
import numpy as np

INPUT = "data/raw/williams2021/population_data.csv"
SHA = "fce2d8a232460b56f5566c41c03038a3f99ca978e0620a49867e5016a34df168"
POPS = {"wild_dog": "14", "marmot": "15", "ms_woodpecker": "6", "rc_woodpecker": "20",
        "golden_plover": "21", "whooping_crane": "10", "hawaiian_crow": "4",
        "wood_turtle_A": "8", "wood_turtle_B": "9"}
CAP = 10 ** 9
VARIANTS = ("iid", "ar", "cat", "ar_cat", "heavy")
PARAM_NAMES = ("s", "f", "sigma", "rho", "p_c", "delta", "nu")


def designs():
    raw = open(INPUT, "rb").read()
    assert hashlib.sha256(raw).hexdigest() == SHA, "input hash mismatch"
    rows = {r["ID"]: r for r in csv.DictReader(open(INPUT, newline="", encoding="utf-8"))}
    ycols = [c for c in next(iter(rows.values())) if c.isdigit()]
    out = {}
    for name, wid in POPS.items():
        obs = [(int(y), float(rows[wid][y])) for y in ycols if rows[wid][y] not in ("NULL", "")]
        ext = next(i for i, (_, v) in enumerate(obs) if v <= 1)
        obs = obs[: ext + 1]
        out[name] = {"years": [y for y, _ in obs], "counts": np.array([v for _, v in obs])}
    return out


def constant_changes(rec):
    """Rows whose non-final log changes are all equal: calib_features sets their lag-1
    autocorrelation to 0, and the protocol requires that flag to be recorded."""
    d = np.diff(np.log(rec[:, :-1]), axis=1)
    return ((d - d.mean(axis=1, keepdims=True)) ** 2).sum(axis=1) == 0


def calib_features(rec):
    """Non-final one-step log changes: mean square, lag-1 autocorrelation (0 if constant,
    flagged by the caller), fraction of increases."""
    d = np.diff(np.log(rec[:, :-1]), axis=1)
    msq = (d ** 2).mean(axis=1)
    dc = d - d.mean(axis=1, keepdims=True)
    den = (dc ** 2).sum(axis=1)
    ac = np.where(den > 0, (dc[:, 1:] * dc[:, :-1]).sum(axis=1) / np.where(den > 0, den, 1), 0.0)
    return np.column_stack([msq, ac, (d > 0).mean(axis=1)])


def draw_params(variant, n, rng):
    p = {"s": 1 / (1 + np.exp(-rng.normal(0, 1.5, n))),
         "f": np.exp(rng.uniform(np.log(0.01), np.log(2.0), n)),
         "sigma": rng.uniform(0.02, 1.0, n),
         "rho": np.zeros(n), "p_c": np.zeros(n), "delta": np.zeros(n), "nu": np.full(n, np.inf)}
    if variant in ("ar", "ar_cat"):
        p["rho"] = rng.uniform(0.0, 0.9, n)
    if variant in ("cat", "ar_cat"):
        p["p_c"] = rng.uniform(0.0, 0.05, n)
        p["delta"] = rng.uniform(0.5, 0.95, n)
    if variant == "heavy":
        p["nu"] = rng.uniform(2.5, 30.0, n)
    return p


def innovations(p, n, rng):
    e = rng.standard_normal(n)
    heavy = np.isfinite(p["nu"])
    if heavy.any():
        nu = p["nu"][heavy]
        t = rng.standard_t(nu)
        e[heavy] = t / np.sqrt(nu / (nu - 2))          # unit variance
    return e


def simulate_chunk(design, variant, n, rng, beta=0.0, n_ref=50.0, fixed=None):
    """Simulate n prior draws for one design; returns (rec, params, overflow_mask, selected_mask).
    beta > 0 applies the M_A feedback multiplier g(N) = exp(-beta (1/N - 1/n_ref)) for 0<N<n_ref.
    fixed maps parameter names to values that replace the prior draws (fixed-parameter scenarios)."""
    years = design["years"]; L = len(years); n0 = int(design["counts"][0])
    p = draw_params(variant, n, rng)
    for k, v in (fixed or {}).items():
        p[k] = np.full(n, float(v))
    lgs = np.log(p["s"] / (1 - p["s"]))
    N = np.full(n, n0, dtype=np.int64)
    z = innovations(p, n, rng)
    rec = np.empty((n, L)); rec[:, 0] = n0
    alive = np.ones(n, bool); overflow = np.zeros(n, bool)
    first = True
    for j in range(1, L):
        for _ in range(years[j] - years[j - 1]):
            if not first:
                z = p["rho"] * z + np.sqrt(1 - p["rho"] ** 2) * innovations(p, n, rng)
            first = False
            mult = np.where(rng.random(n) < p["p_c"], 1 - p["delta"], 1.0)
            idx = np.flatnonzero(alive)
            g = np.ones(idx.size)
            if beta > 0:
                small = (N[idx] > 0) & (N[idx] < n_ref)
                g[small] = np.exp(-beta * (1.0 / N[idx][small] - 1.0 / n_ref))
            logit = lgs[idx] + p["sigma"][idx] * z[idx] + np.log(g)
            st = mult[idx] / (1 + np.exp(-logit))
            ft = mult[idx] * g * p["f"][idx] * np.exp(p["sigma"][idx] * z[idx] - p["sigma"][idx] ** 2 / 2)
            lam = N[idx] * ft
            bad = ~np.isfinite(lam) | (lam > CAP)       # rate overflow counts as overflow
            if bad.any():
                overflow[idx[bad]] = True; alive[idx[bad]] = False; N[idx[bad]] = 0
                ok = ~bad; idx, st, lam = idx[ok], st[ok], lam[ok]
            N[idx] = rng.binomial(N[idx], st) + rng.poisson(lam)
            big = N > CAP
            overflow |= big; alive &= ~big; N[big] = 0
        rec[:, j] = N
        if j < L - 1:
            alive &= N > 1
    selected = alive & (rec[:, -1] <= 1) & ~overflow
    return rec, p, overflow, selected


def load_bank(bankdir, variant, name):
    """Concatenate the shards of one population's bank (build_bank.py layout), checking each
    shard's seed and draw count against bank_meta.json."""
    meta = json.load(open(os.path.join(bankdir, "bank_meta.json")))
    tasks = sorted((t for t in meta["tasks"] if t["variant"] == variant and t["population"] == name),
                   key=lambda t: t["shard"])
    assert [t["shard"] for t in tasks] == list(range(meta["shards"])), f"incomplete bank {variant}/{name}"
    parts = []
    for t in tasks:
        z = np.load(os.path.join(bankdir, f"bank_{variant}_{name}_s{t['shard']:03d}.npz"))
        assert int(z["seed"]) == t["seed"] and int(z["draws"]) == meta["shard_draws"]
        parts.append(z)
    out = {k: np.concatenate([z[k] for z in parts]) for k in ("rec", "draw_id") + PARAM_NAMES}
    out["draws"] = meta["shards"] * meta["shard_draws"]
    out["overflow"] = sum(int(z["overflow"]) for z in parts)
    return out
