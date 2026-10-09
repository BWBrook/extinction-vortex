"""Development benchmark (synthetic bank sizing) for protocol §3.4 under prior (b).

For each of the nine deposited series (hash-verified Williams CC0 input), the
design is: first census N_first, the deposited annual census years up to the
first count <= 1 (rule E), and that extinction census. Prior (b) draws
(logit s ~ N(0,1.5^2), log f ~ U(log .01, log 2), sigma ~ U(.02, 1)) are simulated
under M0 (Fable sampler semantics, per-trajectory parameters) and kept if the
first recorded count <= 1 is exactly the observed extinction census.

Reports per population: acceptance rate a; the fraction q of accepted runs whose
MAD-standardised calibration summaries C lie within 0.25 of the observed C; and
the implied bank draws for K = 2000 within tolerance, J = 2000 / (a q).
Exposure: computes observed calibration summaries C (not T1-T4, no p-values).
Run from repo root: uv run --with numpy python analysis/fable/calibration/bank_benchmark.py [draws]
"""
import csv, hashlib, sys, time
import numpy as np

INPUT = "data/raw/williams2021/population_data.csv"
SHA = "fce2d8a232460b56f5566c41c03038a3f99ca978e0620a49867e5016a34df168"
POPS = {"wild_dog": "14", "marmot": "15", "ms_woodpecker": "6", "rc_woodpecker": "20",
        "golden_plover": "21", "whooping_crane": "10", "hawaiian_crow": "4",
        "wood_turtle_A": "8", "wood_turtle_B": "9"}


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


def calib_features(rec):
    """rec: (R, L) recorded counts up to and including the extinction census.
    Uses non-final transitions only (all before the extinction census)."""
    x = np.log(rec[:, :-1])
    d = np.diff(x, axis=1)                       # one-step log changes, final transition excluded
    msq = (d ** 2).mean(axis=1)
    dc = d - d.mean(axis=1, keepdims=True)
    den = (dc ** 2).sum(axis=1)
    ac = np.where(den > 0, (dc[:, 1:] * dc[:, :-1]).sum(axis=1) / np.where(den > 0, den, 1), 0.0)
    inc = (d > 0).mean(axis=1)
    return np.column_stack([msq, ac, inc])


def bank(design, draws, rng):
    years = design["years"]; L = len(years); n0 = int(design["counts"][0])
    s = 1 / (1 + np.exp(-rng.normal(0, 1.5, draws)))
    f = np.exp(rng.uniform(np.log(0.01), np.log(2.0), draws))
    sig = rng.uniform(0.02, 1.0, draws)
    lgs = np.log(s / (1 - s))
    n = np.full(draws, n0, dtype=np.int64)
    rec = np.empty((draws, L)); rec[:, 0] = n0
    alive = np.ones(draws, bool)
    for j in range(1, L):
        for _ in range(years[j] - years[j - 1]):
            idx = np.flatnonzero(alive)
            z = rng.standard_normal(idx.size)
            st = 1 / (1 + np.exp(-(lgs[idx] + sig[idx] * z)))
            ft = f[idx] * np.exp(sig[idx] * z - sig[idx] ** 2 / 2)
            n[idx] = rng.binomial(n[idx], st) + rng.poisson(n[idx] * ft)
        rec[:, j] = n
        if j < L - 1:
            alive &= n > 1                           # early rejection: rule E met too early
    keep = alive & (rec[:, -1] <= 1)
    return rec[keep], np.column_stack([s, f, sig])[keep]


def main(draws):
    rng = np.random.default_rng(20261009)
    print(f"prior (b) draws per population: {draws}")
    print("population        L  N_first  accepted  a        q(|C-c_obs|<=0.25)  J for K=2000   seconds")
    for name, d in designs().items():
        t0 = time.time()
        rec, par = bank(d, draws, rng)
        cobs = calib_features(d["counts"][None, :])[0]
        if len(rec) >= 50:
            c = calib_features(rec)
            mad = np.median(np.abs(c - np.median(c, axis=0)), axis=0)
            mad[mad == 0] = np.nan
            dist = np.sqrt(np.nansum(((c - cobs) / mad) ** 2, axis=1))
            q = (dist <= 0.25).mean()
        else:
            q = np.nan
        a = len(rec) / draws
        J = 2000 / (a * q) if a > 0 and q and q > 0 else np.inf
        print(f"{name:16s} {len(d['years']):2d}  {int(d['counts'][0]):6d}  {len(rec):8d}  {a:.5f}  {q:.4f}              {J:12.3g}   {time.time() - t0:6.1f}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 200_000)
