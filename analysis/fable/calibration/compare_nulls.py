"""Common-tolerance / common-cap comparison of candidate no-feedback nulls (Astra 0.5 review).

For each variant x population: J prior-(b) draws (common cap, common selection), then
  acceptance rate and overflow rate;
  mid-rank percentile of each observed calibration summary within the selected runs
    (ties count half), with the number of tied values;
  joint hits: selected runs within standardised (MAD) distance 1.0 of c_obs, with an exact
    95% Clopper-Pearson interval on the per-draw hit rate, and implied draws for K = 2000.
Provenance: per task, the draw-index range, seed, accepted count and overflow count are
written to the provenance CSV; selected-run parameters are saved in an .npz bank file.
Synthetic draws only; c_obs is the exposure already logged (E20).

Usage: python compare_nulls.py OUTDIR DRAWS_PER_TASK [CHUNK] [PROCS]
"""
import os, sys, time, json
import numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bank import designs, calib_features, simulate_chunk, VARIANTS, PARAM_NAMES, CAP

BASE_SEED = 20261014       # development stream; final validation seeds are reserved >= 10**9


def _binom_cdf(k, n, p):
    """P(X <= k), X ~ Bin(n, p), by log-space summation (k small relative to n here)."""
    from math import lgamma, log, exp
    if p <= 0: return 1.0
    if p >= 1: return 0.0 if k < n else 1.0
    lp, lq = log(p), log1m(p)
    terms = [lgamma(n + 1) - lgamma(i + 1) - lgamma(n - i + 1) + i * lp + (n - i) * lq for i in range(k + 1)]
    m = max(terms)
    return min(1.0, exp(m) * sum(exp(t - m) for t in terms))


def log1m(p):
    from math import log1p
    return log1p(-p)


def clopper_pearson(k, n, a=0.05):
    """Exact two-sided interval by bisection on the binomial tails."""
    def bisect(f, lo, hi):
        for _ in range(200):
            mid = (lo + hi) / 2
            if f(mid): hi = mid
            else: lo = mid
        return (lo + hi) / 2
    lower = 0.0 if k == 0 else bisect(lambda p: 1 - _binom_cdf(k - 1, n, p) >= a / 2, 0.0, 1.0)
    upper = 1.0 if k == n else bisect(lambda p: _binom_cdf(k, n, p) <= a / 2, 0.0, 1.0)
    return lower, upper


def task(args):
    outdir, variant, name, draws, chunk, task_id = args
    d = designs()[name]
    seed = BASE_SEED * 1000 + task_id
    rng = np.random.default_rng(seed)
    t0 = time.time()
    recs, pars, n_over = [], {k: [] for k in PARAM_NAMES}, 0
    draw_ids = []
    done = 0
    while done < draws:
        n = min(chunk, draws - done)
        rec, p, over, sel = simulate_chunk(d, variant, n, rng)
        n_over += int(over.sum())
        recs.append(rec[sel])
        for k in PARAM_NAMES:
            pars[k].append(p[k][sel])
        draw_ids.append(done + np.flatnonzero(sel))
        done += n
    rec = np.concatenate(recs); draw_ids = np.concatenate(draw_ids)
    pars = {k: np.concatenate(v) for k, v in pars.items()}
    np.savez_compressed(os.path.join(outdir, f"bank_{variant}_{name}.npz"), rec=rec, draw_id=draw_ids,
                        seed=seed, draws=draws, overflow=n_over, **pars)
    c = calib_features(rec); cobs = calib_features(d["counts"][None, :])[0]
    mid = [((c[:, k] < cobs[k]).sum() + 0.5 * (c[:, k] == cobs[k]).sum()) / len(c) * 100 for k in range(3)]
    ties = [int((c[:, k] == cobs[k]).sum()) for k in range(3)]
    mad = np.median(np.abs(c - np.median(c, axis=0)), axis=0)
    mad = np.where(mad > 0, mad, np.nan)
    dist = np.sqrt(np.nansum(((c - cobs) / mad) ** 2, axis=1))
    hits = int((dist <= 1.0).sum())
    lo, hi = clopper_pearson(hits, draws)
    rate = hits / draws
    return {"variant": variant, "population": name, "seed": seed, "draws": draws,
            "selected": len(rec), "acceptance": len(rec) / draws, "overflow": n_over,
            "midrank_pct_msq": mid[0], "midrank_pct_ac": mid[1], "midrank_pct_inc": mid[2],
            "ties_msq": ties[0], "ties_ac": ties[1], "ties_inc": ties[2],
            "joint_hits_tol1": hits, "hit_rate": rate, "hit_rate_lo95": lo, "hit_rate_hi95": hi,
            "draws_for_K2000": (2000 / rate) if rate > 0 else float("inf"),
            "draws_for_K2000_upper": (2000 / lo) if lo > 0 else float("inf"),
            "seconds": round(time.time() - t0, 1)}


def main():
    outdir, draws = sys.argv[1], int(sys.argv[2])
    chunk = int(sys.argv[3]) if len(sys.argv) > 3 else 500_000
    procs = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    os.makedirs(outdir, exist_ok=True)
    jobs = [(outdir, v, name, draws, chunk, i) for i, (v, name) in
            enumerate((v, n) for v in VARIANTS for n in designs())]
    t0 = time.time()
    with Pool(procs) as pool:
        res = pool.map(task, jobs)
    import csv
    with open(os.path.join(outdir, "comparison.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(res[0].keys())); w.writeheader(); w.writerows(res)
    json.dump({"draws_per_task": draws, "chunk": chunk, "procs": procs, "cap": CAP,
               "base_seed": BASE_SEED, "wall_seconds": round(time.time() - t0, 1)},
              open(os.path.join(outdir, "run_meta.json"), "w"), indent=1)
    print(f"done: {len(res)} tasks in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
