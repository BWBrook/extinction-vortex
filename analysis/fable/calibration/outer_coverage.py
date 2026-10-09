"""Outer-C coverage check (Astra 0.6 review §3): for fresh selected trajectories generated
under each scenario, compute only the calibration summaries C and count bank runs within
the tolerance. A population succeeds when it has >= K hits; an outer dataset succeeds only
when all nine do. No T1-T4 fitting.

Each population's fresh trajectories are generated independently, so row j across the nine
populations is one independent outer dataset. A population succeeds when its K-th
nearest bank run lies within the tolerance (equivalent to >= K hits). This is measured for
the full bank and for a 10% Bernoulli thinning of it (one tenth the draws, own MAD
scaling). Distances to the k-th nearest runs of the full bank (KS) are also recorded: a
bank m times larger succeeds at tolerance tol approximately when d_(K/m) <= tol, which
gives coverage jointly over bank size and tolerance (k = 10K checks the projection against
the measured thinned bank) and the effective tolerance a k-NN library would use. Neighbour searches use a k-d tree on the MAD-scaled summaries (columns
with zero MAD dropped, as the e2e distance ignores them).

Usage: python outer_coverage.py BANKDIR OUTDIR M PROCS [SEED] [K] [TOL]
"""
import os, sys, json, time
from multiprocessing import Pool
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bank import designs, calib_features, simulate_chunk

SCENARIOS = (("iid", 0.0), ("iid", 8.66), ("ar_cat", 0.0), ("ar_cat", 8.66))
SEED = 20261018
CHUNK = 200_000
KS = (20, 67, 200, 667, 2000, 20000)   # K/m for m = 100, 30, 10, 3, 1, 0.1 with K = 2000


def scaled(cb):
    mad = np.median(np.abs(cb - np.median(cb, axis=0)), axis=0)
    keep = mad > 0
    return keep, mad[keep]


def task(args):
    tid, variant, beta, name, bankdir, outdir, M, seed, K, tol = args
    t0 = time.time()
    rng = np.random.default_rng(seed * 100 + tid)
    d = designs()[name]
    rec = np.load(os.path.join(bankdir, f"bank_{variant}_{name}.npz"))["rec"]
    cb = calib_features(rec)
    sub = cb[rng.random(len(cb)) < 0.1]
    trees = {}
    for key, c in (("full", cb), ("sub", sub)):
        keep, mad = scaled(c)
        trees[key] = (cKDTree(c[:, keep] / mad), keep, mad)
    fresh, draws, over = [], 0, 0
    while sum(len(f) for f in fresh) < M:
        r, p, o, sel = simulate_chunk(d, variant, CHUNK, rng, beta=beta)
        draws += CHUNK; over += int(o.sum()); fresh.append(r[sel])
    fresh = np.concatenate(fresh)[:M]
    cobs = calib_features(fresh)
    knn = {}
    for key, (tree, keep, mad) in trees.items():
        ks = list(KS) if key == "full" else [K]
        knn[key] = tree.query(cobs[:, keep] / mad, k=ks)[0]
    ok_full = knn["full"][:, KS.index(K)] <= tol
    ok_sub = knn["sub"][:, 0] <= tol
    np.savez_compressed(os.path.join(outdir, f"cov_{variant}_b{beta:g}_{name}.npz"),
                        c_outer=cobs, knn_full=knn["full"], knn_sub=knn["sub"][:, 0],
                        seed=seed * 100 + tid)
    return {"variant": variant, "beta": beta, "pop": name, "bank_selected": len(cb),
            "sub_selected": len(sub), "fresh_draws": draws, "fresh_overflow": over,
            "q_full": float(ok_full.mean()), "q_sub": float(ok_sub.mean()),
            "seconds": round(time.time() - t0, 1)}


def main():
    bankdir, outdir, M, procs = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else SEED
    K = int(sys.argv[6]) if len(sys.argv) > 6 else 2000
    tol = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
    os.makedirs(outdir, exist_ok=True)
    names = list(designs())
    jobs = [(i, v, b, n, bankdir, outdir, M, seed, K, tol)
            for i, ((v, b), n) in enumerate((s, n) for s in SCENARIOS for n in names)]
    with Pool(procs) as pool:
        res = pool.map(task, jobs, chunksize=1)
    summ = []
    for v, b in SCENARIOS:
        ok_full = np.ones(M, bool); ok_sub = np.ones(M, bool)
        for n in names:
            z = np.load(os.path.join(outdir, f"cov_{v}_b{b:g}_{n}.npz"))
            ok_full &= z["knn_full"][:, KS.index(K)] <= tol; ok_sub &= z["knn_sub"] <= tol
        summ.append({"variant": v, "beta": b, "M": M, "all9_full": int(ok_full.sum()),
                     "all9_sub": int(ok_sub.sum())})
    json.dump({"meta": {"bankdir": bankdir, "M": M, "K": K, "tol": tol, "seed": seed,
                        "scenarios": SCENARIOS, "ks": KS}, "tasks": res, "all_nine": summ},
              open(os.path.join(outdir, "coverage.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
