"""Outer-C library radii (Astra 0.6 review §3; 0.7 review): for fresh selected trajectories
generated under each scenario, compute only the calibration summaries C and record the
distances to their k-th nearest bank runs (MAD-scaled; zero-MAD columns dropped, as in
e2e_benchmark.py). No T1-T4 fitting.

Each population's fresh trajectories are generated independently, so row j across the nine
populations is one independent outer dataset. Recorded per outer trajectory: distances to
the KS-th nearest runs of the full bank, and to the K-th nearest run of a 10% Bernoulli
thinning of it (own MAD scaling), which checks the linear projection d_(K/m) for an m-fold
bank against a measured smaller bank.

Scenarios come from SCENARIOS_JSON, a list of {"name", "variant", "beta", "fixed", "M"}, where
"fixed" optionally maps populations to fixed parameter values and "M" optionally overrides
the number of outer trajectories; "-" or no argument gives the
null and M_A (beta = 8.66) prior-predictive scenarios for each variant in VARIANTS.

Usage: python outer_coverage.py BANKDIR OUTDIR M PROCS VARIANTS(comma list) [SCENARIOS_JSON] [SEED] [K]
"""
import os, sys, json, time
from multiprocessing import Pool
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bank import designs, calib_features, simulate_chunk, load_bank

SEED = 20261021
CHUNK = 200_000
KS = (20, 67, 200, 667, 2000, 20000)   # K/m for m = 100, 30, 10, 3, 1, 0.1 with K = 2000


def scaled_tree(c):
    mad = np.median(np.abs(c - np.median(c, axis=0)), axis=0)
    keep = mad > 0
    return cKDTree(c[:, keep] / mad[keep]), keep, mad[keep]


def task(args):
    tid, variant, name, scens, bankdir, outdir, M, seed, K = args
    t0 = time.time()
    rng = np.random.default_rng(seed * 100 + tid)
    d = designs()[name]
    cb = calib_features(load_bank(bankdir, variant, name)["rec"])
    full = scaled_tree(cb)
    sub = scaled_tree(cb[rng.random(len(cb)) < 0.1])
    res = []
    for sc in scens:
        fresh, draws, over = [], 0, 0
        m = sc.get("M", M)
        while sum(len(f) for f in fresh) < m:
            r, p, o, sel = simulate_chunk(d, variant, CHUNK, rng, beta=sc["beta"],
                                          fixed=sc.get("fixed", {}).get(name))
            draws += CHUNK; over += int(o.sum()); fresh.append(r[sel])
        cobs = calib_features(np.concatenate(fresh)[:m])
        tree, keep, mad = full
        knn_full = tree.query(cobs[:, keep] / mad, k=list(KS))[0]
        tree, keep, mad = sub
        knn_sub = tree.query(cobs[:, keep] / mad, k=[K])[0][:, 0]
        np.savez_compressed(os.path.join(outdir, f"cov_{sc['name']}_{name}.npz"), c_outer=cobs,
                            knn_full=knn_full, knn_sub=knn_sub, seed=seed * 100 + tid)
        res.append({"scenario": sc["name"], "variant": variant, "pop": name, "bank_selected": len(cb),
                    "fresh_draws": draws, "fresh_overflow": over})
    return [r | {"seconds": round(time.time() - t0, 1)} for r in res]


def main():
    bankdir, outdir, M, procs = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    variants = sys.argv[5].split(",")
    scens = (json.load(open(sys.argv[6])) if len(sys.argv) > 6 and sys.argv[6] != "-" else
             [{"name": f"{v}_{lab}", "variant": v, "beta": b} for v in variants
              for lab, b in (("null", 0.0), ("MA", 8.66))])
    seed = int(sys.argv[7]) if len(sys.argv) > 7 else SEED
    K = int(sys.argv[8]) if len(sys.argv) > 8 else 2000
    os.makedirs(outdir, exist_ok=True)
    names = list(designs())
    jobs = [(i, v, n, [s for s in scens if s["variant"] == v], bankdir, outdir, M, seed, K)
            for i, (v, n) in enumerate((v, n) for v in variants for n in names)]
    with Pool(procs) as pool:
        res = [r for rs in pool.map(task, jobs, chunksize=1) for r in rs]
    json.dump({"meta": {"bankdir": bankdir, "M": M, "K": K, "seed": seed, "ks": KS,
                        "scenarios": scens, "populations": names}, "tasks": res},
              open(os.path.join(outdir, "coverage.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
