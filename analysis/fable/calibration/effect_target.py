"""Development computation of the effect target beta_min (protocol §3.3) and the numeric
fixed-parameter corner scenarios (§4.3) under one null variant.

1. Library at the observed calibration summaries: for each population, the K nearest bank
   runs to its observed C (exposure E20; no T1-T4), giving that population's library of
   parameter vectors.
2. beta_min: at the component-wise medians of the nine libraries pooled, simulate RUNS
   paths from N0 for 10 years under the null (beta = 0) and under M_A on the same
   environment, on the Delta10 grid 0.025, 0.05, ..., 0.9 (beta = -ln(1 - Delta10) / 0.08,
   so g(10) = 1 - Delta10; 0.9 is beta_max). beta_min is the smallest grid value at which
   P(count <= 1 within 10 years) rises by at least 0.10 over the null. N0 = 20, or 50 if
   the null probability from 20 exceeds 0.85. Overflowed paths are counted, not extinct.
3. Corners, per population (fixed parameters at that population's library medians, except):
   high_sigma: sigma at the library 90th percentile; low_s: s at the 10th percentile;
   strong_env: rho and p_c at their 90th percentiles. The selection rate at each fixed
   parameter vector is measured with SEL_DRAWS draws.

Usage: python effect_target.py BANKDIR VARIANT OUTDIR [K] [RUNS] [SEL_DRAWS] [SEED]
"""
import os, sys, json
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bank import designs, calib_features, simulate_chunk, load_bank

FREE = ("s", "f", "sigma", "rho", "p_c", "delta")
GRID = np.round(np.arange(1, 37) * 0.025, 3)
CORNERS = {"high_sigma": {"sigma": 0.9}, "low_s": {"s": 0.1}, "strong_env": {"rho": 0.9, "p_c": 0.9}}


def library(b, cobs, K):
    c = calib_features(b["rec"])
    mad = np.median(np.abs(c - np.median(c, axis=0)), axis=0)
    keep = mad > 0
    dist, idx = cKDTree(c[:, keep] / mad[keep]).query(cobs[keep] / mad[keep], k=K)
    return {k: b[k][idx] for k in FREE}, float(dist[-1])


def p_extinct(theta, variant, n0, beta, runs, rng):
    design = {"years": list(range(11)), "counts": np.array([n0] + [n0] * 10)}
    rec, p, over, sel = simulate_chunk(design, variant, runs, rng, beta=beta, fixed=theta)
    ext = (rec[:, 1:] <= 1).any(axis=1) & ~over
    return float(ext.mean()), int(over.sum())


def main():
    bankdir, variant, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
    K = int(sys.argv[4]) if len(sys.argv) > 4 else 2000
    runs = int(sys.argv[5]) if len(sys.argv) > 5 else 100_000
    sel_draws = int(sys.argv[6]) if len(sys.argv) > 6 else 2_000_000
    seed = int(sys.argv[7]) if len(sys.argv) > 7 else 20261020
    os.makedirs(outdir, exist_ok=True)
    rng = np.random.default_rng(seed)
    des = designs()
    libs, kth = {}, {}
    for n, d in des.items():
        libs[n], kth[n] = library(load_bank(bankdir, variant, n), calib_features(d["counts"][None, :])[0], K)
    np.savez_compressed(os.path.join(outdir, f"libraries_{variant}.npz"),
                        **{f"{n}__{k}": v for n, lib in libs.items() for k, v in lib.items()})
    pooled = {k: float(np.median(np.concatenate([libs[n][k] for n in des]))) for k in FREE}

    n0 = 20
    p0, over0 = p_extinct(pooled, variant, n0, 0.0, runs, rng)
    if p0 > 0.85:
        n0 = 50
        p0, over0 = p_extinct(pooled, variant, n0, 0.0, runs, rng)
    grid = []
    for dl in GRID:
        beta = -np.log(1 - dl) / 0.08
        pa, over = p_extinct(pooled, variant, n0, beta, runs, rng)
        grid.append({"delta10": float(dl), "beta": float(beta), "p_null": p0, "p_MA": pa,
                     "diff": pa - p0, "overflow": over})
    hit = [g for g in grid if g["diff"] >= 0.10]
    beta_min = hit[0] if hit else None

    corners = {}
    for cname, spec in CORNERS.items():
        corners[cname] = {}
        for n, d in des.items():
            theta = {k: float(np.median(libs[n][k])) for k in FREE}
            theta |= {k: float(np.quantile(libs[n][k], q)) for k, q in spec.items()}
            sel_n, over_n, done = 0, 0, 0
            while done < sel_draws:
                r, p, o, sel = simulate_chunk(d, variant, 500_000, rng, fixed=theta)
                sel_n += int(sel.sum()); over_n += int(o.sum()); done += 500_000
            corners[cname][n] = {"theta": theta, "selection_rate": sel_n / done, "overflow": over_n}
    out = {"variant": variant, "K": K, "runs": runs, "seed": seed, "library_kth_dist": kth,
           "library_quantiles": {n: {k: [float(x) for x in np.quantile(libs[n][k], [0.1, 0.5, 0.9])]
                                     for k in FREE} for n in des},
           "pooled_medians": pooled, "n0": n0, "p_null": p0, "overflow_null": over0,
           "grid": grid, "beta_min": beta_min, "corners": corners}
    json.dump(out, open(os.path.join(outdir, f"effect_target_{variant}.json"), "w"), indent=1)
    print(json.dumps({"pooled_medians": pooled, "n0": n0, "p_null": p0, "beta_min": beta_min,
                      "selection_rates": {c: {n: v["selection_rate"] for n, v in cs.items()}
                                          for c, cs in corners.items()}}, indent=1))


if __name__ == "__main__":
    main()
