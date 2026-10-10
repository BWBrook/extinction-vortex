"""End-to-end run of the development procedure (protocol §3.4/§4.3) on SYNTHETIC outer
datasets only (no empirical T1-T4, no empirical p-value).

Per outer dataset: fresh selected trajectories (one per population, independent of the
bank) -> calibration summaries -> per-population k-NN library (the K nearest bank runs in
MAD-scaled summary space; no hard tolerance) -> R_train and R_test replicate datasets ->
T1-T4 in R (tstats_batch.R) -> training mean/covariance (Ledoit-Wolf shrinkage if
ill-conditioned) -> D -> p bounds with the conservative tie rule.

Output contract (one JSON object per trial, appended to e2e_rows.jsonl as it completes):
outer, timings, kth_dist (per population), flags (zero-MAD features dropped per population;
populations whose outer series has constant changes), fit_failures, fallback, train_fail,
test_fail, cond, D_obs, p_lo, p_hi, p_diagnostic (= p_lo, or "indeterminate"), outcome,
T_obs. Outcomes: reject (p_hi < ALPHA), accept (p_lo >= ALPHA), or indeterminate:
indet_malformed (T file not 2R+1 ordered sets), indet_obsfit, indet_train (more than
TRAIN_FAIL_MAX of the training fits failed), indet_cov (unusable training covariance),
indet_straddle. Every bank must hold at least K selected runs.

Usage: python e2e_benchmark.py BANKDIR VARIANT OUTDIR N_OUTER R K R_WORKERS SEED [BETA_OUTER] [SCENARIO_JSON]
BETA_OUTER > 0 generates the outer datasets under M_A on the same environment variant; the
reference is always that variant's no-feedback bank. SCENARIO_JSON maps each population to
fixed parameter values for a fixed-parameter scenario (otherwise prior-predictive).
"""
import os, sys, time, json, subprocess, csv
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bank import designs, calib_features, constant_changes, simulate_chunk, load_bank

ALPHA = 0.05
TRAIN_FAIL_MAX = 0.02
FEATURES = ("msq", "acf", "inc")


def fresh_selected(design, variant, rng, beta=0.0, fixed=None):
    while True:
        rec, p, over, sel = simulate_chunk(design, variant, 200_000, rng, beta=beta, fixed=fixed)
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


def read_T(path, R):
    """T1-T4 matrix, failure flags and fallback counts from tstats_batch.R output, or None
    unless the file holds exactly the sets 0..2R in order."""
    try:
        T = np.genfromtxt(path, delimiter=",", names=True)
    except ValueError:
        return None
    need = ("set", "T1", "T2", "T3", "T4", "failed", "fallback")
    if T.ndim != 1 or any(c not in (T.dtype.names or ()) for c in need):
        return None
    if len(T) != 2 * R + 1 or not np.array_equal(T["set"], np.arange(2 * R + 1)):
        return None
    return np.column_stack([T["T1"], T["T2"], T["T3"], T["T4"]]), T["failed"], T["fallback"]


def p_bounds(M, R):
    """D and both p bounds from stacked T1-T4 rows: observed, R training, R test."""
    if M is None or M.shape != (2 * R + 1, 4):
        return {"status": "malformed"}
    obs, train, test = M[0], M[1:R + 1], M[R + 1:]
    ok = np.isfinite(train).all(axis=1)
    out = {"train_fail": int((~ok).sum()), "test_fail": int((~np.isfinite(test).all(axis=1)).sum())}
    if not np.isfinite(obs).all():
        return out | {"status": "obsfit"}
    if out["train_fail"] > int(TRAIN_FAIL_MAX * R):
        return out | {"status": "train"}
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


def outcome(s, shortfall=""):
    """Procedural outcome; `shortfall` applies only to archived hard-tolerance runs."""
    if shortfall:
        return "indet_calib"
    if s["status"] != "ok":
        return "indet_" + s["status"]
    if s["p_hi"] < ALPHA:
        return "reject"
    return "accept" if s["p_lo"] >= ALPHA else "indet_straddle"


def knn_banks(bankdir, variant, des, K):
    """Per population: bank trajectories, k-d tree on MAD-scaled summaries (zero-MAD columns
    dropped) and the scaling used."""
    banks = {}
    for name in des:
        b = load_bank(bankdir, variant, name)
        assert len(b["rec"]) >= K, f"{variant}/{name}: {len(b['rec'])} selected runs < K = {K}"
        c = calib_features(b["rec"])
        mad = np.median(np.abs(c - np.median(c, axis=0)), axis=0)
        keep = mad > 0
        banks[name] = {"rec": b["rec"], "tree": cKDTree(c[:, keep] / mad[keep]), "keep": keep,
                       "mad": mad[keep], "dropped": [f for f, k in zip(FEATURES, keep) if not k]}
    return banks


def main():
    bankdir, variant, outdir, n_outer = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    R, K, workers, seed = int(sys.argv[5]), int(sys.argv[6]), sys.argv[7], int(sys.argv[8])
    beta_outer = float(sys.argv[9]) if len(sys.argv) > 9 else 0.0
    scenario = json.load(open(sys.argv[10])) if len(sys.argv) > 10 else {}
    os.makedirs(outdir, exist_ok=True)
    rng = np.random.default_rng(seed)
    des = designs()
    t0 = time.time()
    banks = knn_banks(bankdir, variant, des, K)
    meta = {"variant": variant, "R_train": R, "R_test": R, "K": K, "r_workers": workers, "seed": seed,
            "beta_outer": beta_outer, "scenario": scenario, "n_outer": n_outer,
            "t_load_banks": round(time.time() - t0, 1)}
    json.dump(meta, open(os.path.join(outdir, "e2e_meta.json"), "w"), indent=1)
    here = os.path.dirname(os.path.abspath(__file__))
    for k in range(n_outer):
        tk = {"outer": k}
        t = time.time()
        obs = {n: fresh_selected(d, variant, rng, beta_outer, scenario.get(n)) for n, d in des.items()}
        tk["t_outer_sim"] = time.time() - t
        t = time.time()
        libs, kth = {}, {}
        for n, b in banks.items():
            cobs = calib_features(obs[n][None, :])[0]
            dist, idx = b["tree"].query(cobs[b["keep"]] / b["mad"], k=K)
            kth[n] = float(dist[-1])
            libs[n] = b["rec"][idx]
        tk["t_library"] = time.time() - t
        tk["kth_dist"] = json.dumps({n: round(v, 4) for n, v in kth.items()})
        tk["flags"] = json.dumps({"zero_mad_dropped": {n: b["dropped"] for n, b in banks.items() if b["dropped"]},
                                  "constant_changes": [n for n in des if constant_changes(obs[n][None, :])[0]]})
        t = time.time()
        path_in = os.path.join(outdir, f"sets_{k}.csv")
        with open(path_in, "w", newline="") as fh:
            w = csv.writer(fh); w.writerow(["set", "pop", "year", "N"])
            for n, d in des.items():
                for y, v in zip(d["years"], obs[n]):
                    w.writerow([0, n, y, int(v)])
            for r in range(1, 2 * R + 1):
                for n, d in des.items():
                    traj = libs[n][rng.integers(K)]
                    for y, v in zip(d["years"], traj):
                        w.writerow([r, n, y, int(v)])
        tk["t_write"] = time.time() - t
        t = time.time()
        path_out = os.path.join(outdir, f"T_{k}.csv")
        subprocess.run(["Rscript", os.path.join(here, "tstats_batch.R"), path_in, path_out, workers], check=True)
        tk["t_fits"] = time.time() - t
        T = read_T(path_out, R)
        sc = p_bounds(None if T is None else T[0], R)
        if T is not None:
            tk["fit_failures"] = int(np.nansum(T[1])); tk["fallback"] = int(np.nansum(T[2]))
            tk["T_obs"] = json.dumps([round(float(v), 5) for v in T[0][0]])
        tk |= {x: sc[x] for x in ("train_fail", "test_fail", "cond", "D_obs", "p_lo", "p_hi") if x in sc}
        tk["p_diagnostic"] = sc.get("p_lo", "indeterminate")
        tk["outcome"] = outcome(sc)
        os.remove(path_in)
        with open(os.path.join(outdir, "e2e_rows.jsonl"), "a") as fh:
            fh.write(json.dumps(tk) + "\n")
        print(json.dumps(tk), flush=True)
    meta["total_seconds"] = round(time.time() - t0, 1)
    json.dump(meta, open(os.path.join(outdir, "e2e_meta.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
