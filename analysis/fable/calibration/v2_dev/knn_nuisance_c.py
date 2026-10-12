"""V2 development diagnostics D1c (corrected D1) and D2 (association) on the exposed v1 null blocks.
No new outcomes are generated. Repairs Astra's review of D1 (notes/astra_v2_diagnostic_review_20261011.md):
  - the trend summary telescopes to the penultimate count (N0 and L are fixed per population), so the
    endpoint rank compares integer penultimate counts with half ties; a constant library keeps its
    midrank (0, 0.5 or 1) and is flagged (version 2, after Astra 1545);
  - bindings: manifest digest, every primary-bank file hash checked against the manifest, source hashes,
    runtime; per trial and population the recomputed K-th distance is compared with the rounded v1 record,
    boundary ties are flagged and a digest of the neighbour draw IDs is kept (full IDs go to NEIGHBOUR_NPZ);
  - D2 uses trial-level summaries (mean over the nine populations of rank - 0.5), one per trial, and
    reports association with the frozen rejection outcome with uncertainty, not attribution.
Growth proxies: nominal s + f, and the stationary mean multiplier (1 - delta p_c)(E logistic(logit s +
sigma Z) + f), Z ~ N(0, 1), ignoring selection (both are proxies, not the selected process's growth).
Version 2 (after Astra 1544-1546): membership comes from a separate k = K query, as v1's run_chunk makes;
the k = K + 1 query only flags boundary ties. With OLD_NPZ (version 1's neighbour IDs, from a truncated
K + 1 query) the number of changed memberships is counted. Version 1's outputs are kept as superseded.
Usage (from the frozen source root):
  python knn_nuisance_c.py MANIFEST BASE OUT_DIR NEIGHBOUR_NPZ [OLD_NPZ] [LIMIT]"""
import gzip, hashlib, json, os, platform, sys
import numpy as np
import scipy
from scipy import stats
from scipy.spatial import cKDTree
sys.path.insert(0, "analysis/fable/calibration")
from bank import designs, calib_features, load_bank
from validate import manifest_digest

PARAMS = ("s", "f", "sigma", "rho", "p_c", "delta")
SUMMARIES = ("s", "f", "sigma", "lam_nominal", "lam_mean", "pen")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def midrank(lib, x):
    """Fraction of lib below x plus half the ties, per row (lib: n x K, x: n)."""
    return (lib < x[:, None]).mean(1) + 0.5 * (lib == x[:, None]).mean(1)


GH_X, GH_W = np.polynomial.hermite_e.hermegauss(40)
GH_W = GH_W / GH_W.sum()


def lam_mean(p):
    ls = np.log(p["s"] / (1 - p["s"]))
    es = np.zeros_like(ls)
    for x, w in zip(GH_X, GH_W):
        es += w / (1 + np.exp(-(ls + p["sigma"] * x)))
    return (1 - p["delta"] * p["p_c"]) * (es + p["f"])


def self_test():
    lib = np.array([[5, 5, 5, 5]]); assert midrank(lib, np.array([5]))[0] == 0.5
    paths = np.array([[20, 9, 3, 7, 4, 0], [20, 4, 11, 2, 4, 1], [20, 6, 6, 6, 4, 0]])
    assert len(set(paths[:, -2])) == 1 and midrank(paths[:, -2][None, :], np.array([4]))[0] == 0.5


def ci_rate(k, n):
    lo = stats.beta.ppf(0.025, k, n - k + 1) if k else 0.0
    hi = stats.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
    return [int(k), int(n), round(k / n, 4) if n else None, round(float(lo), 4), round(float(hi), 4)]


def logistic_slope(x, y):
    """Univariate logistic regression of y on standardised x: slope per SD with a Wald 95% interval."""
    z = (x - x.mean()) / x.std()
    X = np.column_stack([np.ones_like(z), z]); b = np.zeros(2)
    for _ in range(50):
        mu = 1 / (1 + np.exp(-X @ b)); W = mu * (1 - mu)
        H = X.T @ (X * W[:, None]); step = np.linalg.solve(H, X.T @ (y - mu)); b += step
        if np.abs(step).max() < 1e-10:
            break
    se = np.sqrt(np.linalg.inv(H)[1, 1])
    return [round(float(b[1]), 4), round(float(b[1] - 1.96 * se), 4), round(float(b[1] + 1.96 * se), 4)]


def main():
    self_test()
    man_path, base, outdir, nbr_path = sys.argv[1:5]
    old = dict(np.load(sys.argv[5])) if len(sys.argv) > 5 and sys.argv[5] != "-" else None
    limit = int(sys.argv[6]) if len(sys.argv) > 6 else None
    man = json.load(open(man_path)); K = man["K"]; des = designs()
    if os.environ.get("D1C_POPS"):                      # smoke test on a subset of populations
        des = {n: des[n] for n in os.environ["D1C_POPS"].split(",")}
    bankdir = os.path.join(base, man["bankdir"])
    bad_bank = [] if os.environ.get("D1C_POPS") else \
        [f for f, h in man["bank_sha256"].items() if sha(os.path.join(bankdir, f)) != h]
    bad_src = [f for f, h in man["source_sha256"].items() if sha(f) != h]
    if bad_bank or bad_src:
        raise SystemExit(f"hash mismatch: bank {bad_bank[:3]} source {bad_src[:3]}")
    blocks = [s for s in man["scenarios"] if s["role"] == "null"]
    rows = {s["name"]: [json.loads(l) for c in s["chunks"]
                        for l in open(os.path.join(base, c["dir"], "e2e_rows.jsonl"))][:limit] for s in blocks}
    os.makedirs(outdir, exist_ok=True)
    per = {b: {n: {} for n in des} for b in rows}
    nbr = {}
    for n, d in des.items():
        bk = load_bank(bankdir, man["variant"], n)
        c = calib_features(bk["rec"])
        mad = np.median(np.abs(c - np.median(c, axis=0)), axis=0); keep = mad > 0
        tree = cKDTree(c[:, keep] / mad[keep])
        pen, n0, L = bk["rec"][:, -2].astype(np.int64), bk["rec"][:, 0], bk["rec"].shape[1]
        vals = {p: bk[p] for p in PARAMS}
        vals["lam_nominal"] = bk["s"] + bk["f"]
        vals["lam_mean"] = lam_mean(bk)
        for b, rr in rows.items():
            obs = np.array([r["selected"][n]["recorded"] for r in rr])
            assert obs.shape[1] == L
            q = calib_features(obs)[:, keep] / mad[keep]
            dist, idx = tree.query(q, k=K, workers=16)          # membership: the query v1 made
            d1, _ = tree.query(q, k=K + 1, workers=16)
            tie = d1[:, K - 1] == d1[:, K]
            logged = np.array([json.loads(r["kth_dist"])[n] for r in rr])
            tp = {p: np.array([r["selected"][n]["params"][p] for r in rr]) for p in PARAMS}
            tv = dict(tp, lam_nominal=tp["s"] + tp["f"], lam_mean=lam_mean(tp))
            rk = {p: midrank(vals[p][idx], tv[p]) for p in ("s", "f", "sigma", "lam_nominal", "lam_mean")}
            lp = pen[idx]
            const = (lp == lp[:, :1]).all(1)
            rk["pen"] = midrank(lp, obs[:, -2].astype(np.int64))
            per[b][n] = {"rank": rk, "const": const, "tie": tie, "kth": dist[:, -1], "logged": logged,
                         "n0_mismatch": int((n0[idx] != obs[:, :1]).sum()),
                         "lib_median": {p: np.median(vals[p][idx], 1) for p in ("s", "lam_mean")},
                         "true": {p: tv[p] for p in ("s", "lam_mean")},
                         "nbr_digest": [hashlib.sha256(np.sort(bk["draw_id"][i]).astype(np.int64).tobytes()).hexdigest()[:16]
                                        for i in idx]}
            nbr[f"{b}/{n}"] = bk["draw_id"][idx].astype(np.int64)
            if old is not None:
                o = old[f"{b}/{n}"]
                per[b][n]["changed"] = [int(K - np.intersect1d(o[r], nbr[f"{b}/{n}"][r]).size) for r in range(len(rr))]
        del bk, c, tree, vals
        print("done", n, flush=True)
    np.savez_compressed(nbr_path, **nbr)

    def nul(x):
        return None if x is None or not np.isfinite(x) else round(float(x), 4)

    out = {"diagnostic": "D1c/D2, development evidence on exposed v1 outputs",
           "manifest_digest": manifest_digest(man_path), "bank_files_verified": len(man["bank_sha256"]),
           "source_files_verified": len(man["source_sha256"]), "script_sha256": sha(__file__),
           "neighbour_ids_npz_sha256": sha(nbr_path), "K": K, "limit": limit,
           "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
           "blocks": {}}
    with gzip.open(os.path.join(outdir, "d1c_trials.jsonl.gz"), "wt") as fh:
        for b, rr in rows.items():
            rej = np.array([r["outcome"] == "reject" for r in rr]); P = per[b]
            for i, r in enumerate(rr):
                fh.write(json.dumps({"block": b, "trial_id": r["trial_id"], "outcome": r["outcome"], "p_hi": r["p_hi"],
                                     "pop": {n: {**{k: nul(P[n]["rank"][k][i]) for k in SUMMARIES},
                                                 "kth": nul(P[n]["kth"][i]), "kth_v1": P[n]["logged"][i],
                                                 "tie": bool(P[n]["tie"][i]), "const_pen": bool(P[n]["const"][i]),
                                                 "nbr": P[n]["nbr_digest"][i]}
                                             for n in des}}) + "\n")
            summ = {k: np.nanmean(np.column_stack([P[n]["rank"][k] for n in des]), 1) - 0.5 for k in SUMMARIES}
            kdiff = np.concatenate([np.abs(np.round(P[n]["kth"], 4) - P[n]["logged"]) for n in des])
            blk = {"n": len(rr), "rejections": int(rej.sum()),
                   "reconstruction": {"kth_max_abs_diff_vs_v1_rounded": float(kdiff.max()),
                                      "kth_over_1e-4": int((kdiff > 1e-4).sum()),
                                      "boundary_ties": int(sum(P[n]["tie"].sum() for n in des)),
                                      "n0_mismatches": int(sum(P[n]["n0_mismatch"] for n in des))},
                   "constant_penultimate_library": {n: int(P[n]["const"].sum()) for n in des},
                   "membership_vs_version1": None if old is None else {
                       "sets_changed": int(sum(sum(c > 0 for c in P[n]["changed"]) for n in des)),
                       "members_changed_max": int(max(max(P[n]["changed"]) for n in des)),
                       "sets_changed_without_tie_flag": int(sum(sum(c > 0 and not t for c, t in zip(P[n]["changed"], P[n]["tie"]))
                                                                for n in des))},
                   "per_population": {n: {**{f"{k}_rank_mean": nul(np.nanmean(P[n]["rank"][k])) for k in SUMMARIES},
                                          **{f"{k}_rank_q10_50_90": [nul(q) for q in np.nanquantile(P[n]["rank"][k], [.1, .5, .9])]
                                             for k in ("s", "lam_mean", "pen")},
                                          "s_true_mean": nul(P[n]["true"]["s"].mean()),
                                          "s_libmedian_mean": nul(P[n]["lib_median"]["s"].mean()),
                                          "lam_mean_true_mean": nul(P[n]["true"]["lam_mean"].mean()),
                                          "lam_mean_libmedian_mean": nul(P[n]["lib_median"]["lam_mean"].mean())}
                                      for n in des},
                   "trial_summary_q10_50_90": {k: [nul(q) for q in np.quantile(v, [.1, .5, .9])] for k, v in summ.items()},
                   "trial_summary_spearman": {a: {c: nul(stats.spearmanr(summ[a], summ[c])[0]) for c in SUMMARIES}
                                              for a in SUMMARIES},
                   "association": {}}
            for k, v in summ.items():
                t = np.quantile(v, [1 / 3, 2 / 3]); g = np.digitize(v, t)
                blk["association"][k] = {
                    "reject_by_tertile": [ci_rate(rej[g == j].sum(), (g == j).sum()) for j in range(3)],
                    "logistic_slope_per_sd": logistic_slope(v, rej.astype(float))
                    if 0 < rej.sum() < len(rej) and np.isfinite(v).all() else None,
                    "spearman_with_p_hi": nul(stats.spearmanr(v, [r["p_hi"] for r in rr])[0])}
            out["blocks"][b] = blk
    json.dump(out, open(os.path.join(outdir, "d1c_summary.json"), "w"), indent=1, allow_nan=False)
    for b, blk in out["blocks"].items():
        print(b, blk["rejections"], blk["reconstruction"], blk["membership_vs_version1"],
              {k: (blk["association"][k]["logistic_slope_per_sd"], [x[2] for x in blk["association"][k]["reject_by_tertile"]])
               for k in SUMMARIES})


if __name__ == "__main__":
    main()
