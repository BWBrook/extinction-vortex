"""A0: no-fit pre-screen for candidate A (notes/vortex_v2_dev_plan_20261011.md §3). For the exposed v1
null outers (b1-b4) it rebuilds K-neighbourhoods in C+ = (msq, acf, inc, h1, h2) on the frozen primary
bank and compares them with the v1 C neighbourhoods: the true-value midranks of s, f, sigma and the
stationary-mean proxy within the library, and support measured in the ORIGINAL C metric (v1 mask and
MAD) plus the per-dimension neighbour spread. h1, h2: OLS slope and intercept of (d_t - mean d)^2 on
1/N_t over v1's non-final transitions; a constant predictor gives h1 = 0, h2 = mean, flagged.
Development evidence on exposed outputs; no fits, no new outcomes.
Usage (from the frozen source root): python a0_cplus.py MANIFEST BASE OUT_JSON"""
import hashlib, json, os, platform, sys
import numpy as np
import scipy
from scipy.spatial import cKDTree
sys.path.insert(0, "analysis/fable/calibration")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bank import designs, calib_features, load_bank
from validate import manifest_digest
from knn_nuisance_c import midrank, lam_mean, sha

PARAMS = ("s", "f", "sigma", "rho", "p_c", "delta")


def h_features(rec):
    start = np.asarray(rec)[:, :-2]
    flat = (start == start[:, :1]).all(1)                  # constant predictor, judged on integer counts
    rec = np.asarray(rec, float)
    d = np.diff(np.log(rec[:, :-1]), axis=1)
    x = 1.0 / rec[:, :-2]
    y = (d - d.mean(1, keepdims=True)) ** 2
    xc = x - x.mean(1, keepdims=True)
    vx = (xc ** 2).sum(1)
    h1 = np.where(flat, 0.0, (xc * (y - y.mean(1, keepdims=True))).sum(1) / np.where(flat, 1, vx))
    h2 = y.mean(1) - h1 * x.mean(1)
    return np.column_stack([h1, h2]), flat


def self_test():
    rec = np.array([[10, 10, 10, 10, 0], [40, 20, 10, 4, 1]])
    h, flat = h_features(rec)
    assert flat[0] and h[0, 0] == 0 and not flat[1]


def main():
    self_test()
    man_path, base, out = sys.argv[1:4]
    man = json.load(open(man_path)); K = man["K"]; des = designs()
    bankdir = os.path.join(base, man["bankdir"])
    bad = [f for f, h in man["bank_sha256"].items() if sha(os.path.join(bankdir, f)) != h]
    if bad:
        raise SystemExit(f"bank hash mismatch {bad[:3]}")
    blocks = [s for s in man["scenarios"] if s["role"] == "null"]
    rows = {s["name"]: [json.loads(l) for c in s["chunks"] for l in open(os.path.join(base, c["dir"], "e2e_rows.jsonl"))]
            for s in blocks}
    res = {"diagnostic": "A0 C+ neighbourhood pre-screen (no fits)", "manifest_digest": manifest_digest(man_path),
           "bank_files_verified": len(man["bank_sha256"]), "script_sha256": sha(__file__), "K": K,
           "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
           "blocks": {b: {} for b in rows}}
    for n, d in des.items():
        bk = load_bank(bankdir, man["variant"], n)
        c = calib_features(bk["rec"]); h, flat_b = h_features(bk["rec"])
        cp = np.column_stack([c, h])
        mad3 = np.median(np.abs(c - np.median(c, 0)), 0); k3 = mad3 > 0
        mad5 = np.median(np.abs(cp - np.median(cp, 0)), 0); k5 = mad5 > 0
        tree3 = cKDTree(c[:, k3] / mad3[k3]); tree5 = cKDTree(cp[:, k5] / mad5[k5])
        vals = {p: bk[p] for p in ("s", "f", "sigma")}; vals["lam_mean"] = lam_mean(bk)
        for b, rr in rows.items():
            obs = np.array([r["selected"][n]["recorded"] for r in rr])
            co = calib_features(obs); ho, flat_o = h_features(obs); cpo = np.column_stack([co, ho])
            q3 = co[:, k3] / mad3[k3]
            _, i3 = tree3.query(q3, k=K, workers=16)
            _, i5 = tree5.query(cpo[:, k5] / mad5[k5], k=K, workers=16)
            tp = {p: np.array([r["selected"][n]["params"][p] for r in rr]) for p in PARAMS}
            tv = {p: tp[p] for p in ("s", "f", "sigma")}; tv["lam_mean"] = lam_mean(tp)
            entry = {"flat_predictor_outer": int(flat_o.sum()), "flat_predictor_bank_frac": round(float(flat_b.mean()), 5),
                     "dropped_C+": [f for f, k in zip(("msq", "acf", "inc", "h1", "h2"), k5) if not k]}
            for lab, idx in (("C", i3), ("C+", i5)):
                rk = {p: midrank(vals[p][idx], tv[p]) for p in vals}
                dC = np.sqrt((((c[idx][:, :, k3] / mad3[k3]) - q3[:, None, :]) ** 2).sum(2))
                spread = np.std(cp[idx], axis=1) / np.where(mad5 > 0, mad5, 1)
                entry[lab] = {**{f"{p}_rank_mean": round(float(rk[p].mean()), 4) for p in rk},
                              **{f"{p}_rank_q10_50_90": np.quantile(rk[p], [.1, .5, .9]).round(4).tolist() for p in rk},
                              "origC_max_dist_q10_50_90": np.quantile(dC.max(1), [.1, .5, .9]).round(4).tolist(),
                              "origC_median_dist_median": round(float(np.median(np.median(dC, 1))), 4),
                              "spread_per_dim_median_in_mad_units": dict(zip(("msq", "acf", "inc", "h1", "h2"),
                                                                             np.median(spread, 0).round(4).tolist()))}
            res["blocks"][b][n] = entry
        del bk, c, h, cp, tree3, tree5, vals
        print("done", n, flush=True)
    for b, v in res["blocks"].items():
        res["blocks"][b]["_summary"] = {lab: {p: [round(min(v[n][lab][f"{p}_rank_mean"] for n in des), 3),
                                                  round(max(v[n][lab][f"{p}_rank_mean"] for n in des), 3)]
                                              for p in ("s", "f", "sigma", "lam_mean")} for lab in ("C", "C+")}
        print(b, json.dumps(res["blocks"][b]["_summary"]))
    json.dump(res, open(out, "w"), indent=1, allow_nan=False)


if __name__ == "__main__":
    main()
