"""End-to-end development benchmark of the frozen-procedure candidate (protocol §3.4/§4.3),
on SYNTHETIC outer datasets only (no empirical T1-T4, no empirical p-value).

Per outer dataset: fresh selected trajectories (one per population, independent of the
bank) -> calibration summaries -> per-population library of K nearest bank runs within the
tolerance -> R_train and R_test replicate datasets -> T1-T4 in R (tstats_batch.R) ->
training mean/covariance (Ledoit-Wolf shrinkage if ill-conditioned) -> D -> p with the
conservative tie rule. Component timings, shortfalls and fit failures are recorded.

Each trial gets a procedural outcome under the fixed-denominator rules (protocol §4.3):
reject / accept, or indeterminate (calibration shortfall, observed-fit failure, unusable
training covariance, or test-fit bounds straddling ALPHA). The raw p (lower bound, ignoring
shortfalls) is kept only as a diagnostic. Rows are appended to e2e_rows.jsonl as each trial
completes, so an aborted arm keeps its finished trials.

Usage: python e2e_benchmark.py BANKDIR VARIANT OUTDIR N_OUTER [R] [K] [TOL] [R_WORKERS] [BETA_OUTER] [SEED]
BETA_OUTER > 0 generates the outer datasets under M_A (feedback) on the same environment
variant; the reference banks are always the no-feedback null of that variant.
"""
import os, sys, time, json, subprocess, csv
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bank import designs, calib_features, simulate_chunk

SEED = 20261015                          # development stream (disjoint from final >= 10**9)
ALPHA = 0.05


def fresh_selected(design, variant, rng, beta=0.0):
    while True:
        rec, p, over, sel = simulate_chunk(design, variant, 200_000, rng, beta=beta)
        if sel.any():
            return rec[np.flatnonzero(sel)[0]]


def ledoit_wolf(X):
    """Ledoit-Wolf shrinkage towards scaled identity (standard formula)."""
    n, p = X.shape
    Xc = X - X.mean(axis=0)
    S = Xc.T @ Xc / n
    mu = np.trace(S) / p
    F = mu * np.eye(p)
    d2 = ((S - F) ** 2).sum()
    b2 = sum(((np.outer(x, x) - S) ** 2).sum() for x in Xc) / n ** 2
    b2 = min(b2, d2)
    return (b2 / d2) * F + (1 - b2 / d2) * S if d2 > 0 else S


def p_bounds(M, R):
    """D and both p bounds from stacked T1-T4 rows: observed, R training, R test."""
    obs, train, test = M[0], M[1:R + 1], M[R + 1:2 * R + 1]
    ok = ~np.isnan(train).any(axis=1)
    out = {"train_fail": int((~ok).sum()), "test_fail": int(np.isnan(test).any(axis=1).sum())}
    if np.isnan(obs).any():
        return out | {"status": "obsfit"}
    mu = train[ok].mean(axis=0)
    S = np.cov(train[ok].T)
    try:
        cond = np.linalg.cond(S)
        out["cond"] = float(cond)
        if not cond <= 1e6:
            S = ledoit_wolf(train[ok])
        Si = np.linalg.inv(S)
    except np.linalg.LinAlgError:
        return out | {"status": "cov"}
    D = lambda X: np.einsum("ij,jk,ik->i", X - mu, Si, X - mu)
    dt = D(test); d_obs = float(D(obs[None, :])[0])
    if not np.isfinite(d_obs):
        return out | {"status": "cov"}
    fails = ~np.isfinite(dt)
    exceed = int((dt[~fails] >= d_obs).sum())
    return out | {"status": "ok", "D_obs": d_obs, "p_lo": (1 + exceed) / (R + 1),
                  "p_hi": (1 + exceed + int(fails.sum())) / (R + 1)}


def outcome(shortfall, s):
    if shortfall:
        return "indet_calib"
    if s["status"] != "ok":
        return "indet_" + s["status"]
    if s["p_hi"] < ALPHA:
        return "reject"
    return "accept" if s["p_lo"] >= ALPHA else "indet_straddle"


def main():
    bankdir, variant, outdir, n_outer = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    R = int(sys.argv[5]) if len(sys.argv) > 5 else 2000
    K = int(sys.argv[6]) if len(sys.argv) > 6 else 2000
    tol = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
    workers = sys.argv[8] if len(sys.argv) > 8 else "16"
    beta_outer = float(sys.argv[9]) if len(sys.argv) > 9 else 0.0
    seed = int(sys.argv[10]) if len(sys.argv) > 10 else SEED
    os.makedirs(outdir, exist_ok=True)
    rng = np.random.default_rng(seed)
    des = designs()
    t0 = time.time()
    banks = {}
    for name in des:
        b = np.load(os.path.join(bankdir, f"bank_{variant}_{name}.npz"))
        c = calib_features(b["rec"])
        mad = np.median(np.abs(c - np.median(c, axis=0)), axis=0)
        banks[name] = (b["rec"], c, np.where(mad > 0, mad, np.nan))
    t_load = time.time() - t0
    rows = []
    here = os.path.dirname(os.path.abspath(__file__))
    for k in range(n_outer):
        tk = {"outer": k}
        t = time.time()
        obs = {name: fresh_selected(d, variant, rng, beta_outer) for name, d in des.items()}
        tk["t_outer_sim"] = time.time() - t
        t = time.time()
        libs, shortfall, maxd = {}, [], {}
        for name, (rec, c, mad) in banks.items():
            cobs = calib_features(obs[name][None, :])[0]
            dist = np.sqrt(np.nansum(((c - cobs) / mad) ** 2, axis=1))
            order = np.argsort(dist)[:K]
            maxd[name] = float(dist[order[-1]])
            if maxd[name] > tol:
                shortfall.append(name)
            libs[name] = rec[order]
        tk["t_library"] = time.time() - t
        tk["shortfall"] = ";".join(shortfall)
        tk["max_lib_dist"] = json.dumps({n: round(v, 3) for n, v in maxd.items()})
        t = time.time()
        path_in = os.path.join(outdir, f"sets_{k}.csv")
        with open(path_in, "w", newline="") as fh:
            w = csv.writer(fh); w.writerow(["set", "pop", "year", "N"])
            for name, d in des.items():
                for y, v in zip(d["years"], obs[name]):
                    w.writerow([0, name, y, int(v)])
            for r in range(1, 2 * R + 1):
                for name, d in des.items():
                    traj = libs[name][rng.integers(K)]
                    for y, v in zip(d["years"], traj):
                        w.writerow([r, name, y, int(v)])
        tk["t_write"] = time.time() - t
        t = time.time()
        path_out = os.path.join(outdir, f"T_{k}.csv")
        subprocess.run(["Rscript", os.path.join(here, "tstats_batch.R"), path_in, path_out, workers], check=True)
        tk["t_fits"] = time.time() - t
        T = np.genfromtxt(path_out, delimiter=",", names=True)
        tk["fit_failures"] = int(np.nansum(T["failed"]))
        M = np.column_stack([T["T1"], T["T2"], T["T3"], T["T4"]])
        sc = p_bounds(M, R)
        tk |= {x: sc[x] for x in ("train_fail", "test_fail", "cond", "D_obs", "p_lo", "p_hi") if x in sc}
        tk["p_diagnostic"] = sc.get("p_lo", "indeterminate")
        tk["outcome"] = outcome(tk["shortfall"], sc)
        tk["T_obs"] = json.dumps([round(float(v), 5) for v in M[0]])
        os.remove(path_in)
        rows.append(tk)
        with open(os.path.join(outdir, "e2e_rows.jsonl"), "a") as fh:
            fh.write(json.dumps(tk) + "\n")
        print(json.dumps(tk), flush=True)
    meta = {"variant": variant, "R_train": R, "R_test": R, "K": K, "tol": tol, "r_workers": workers,
            "seed": seed, "beta_outer": beta_outer, "t_load_banks": round(t_load, 1), "total_seconds": round(time.time() - t0, 1)}
    json.dump({"meta": meta, "outer": rows}, open(os.path.join(outdir, "e2e_results.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
