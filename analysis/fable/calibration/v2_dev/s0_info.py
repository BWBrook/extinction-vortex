"""External-information Stage 0: no-fit weight diagnostics (notes/vortex_external_info_design_20261014.md §§2-4, 7).
For the exposed v1 outers b1/b3/b5/b16, trial IDs 0-199, it rebuilds each population's frozen K = 2,000 C-neighbourhood
in the primary bank and weights the members by stylized evidence about two rate functionals:
  s_bar(theta) = (1 - delta p_c) E_Z[logit^-1(logit s + sigma Z)],   f_bar(theta) = (1 - delta p_c) f.
Noisy stylized E: k ~ Binomial(n, s_bar_true), then r ~ Poisson(n f_bar_true), conditionally independent given theta.
Ideal comparator: the expected log-likelihood at the true functionals. n in {30, 300} is a per-population ideal
information index. No fits, no reference sampling, no new outer draws, no new bank. ESS < 100 is an exploratory
concentration flag only. Stage 0 cannot measure calibration or power. Run from the frozen source root.
  prepare MANIFEST BASE OUT_INPUTS          bind outers (original v1 rows), E draws and settings
  run     MANIFEST BASE INPUTS OUTDIR [POP]  one pass per population (POP alone = setup/resource pass)
  report  INPUTS OUTDIR OUT_JSON"""
import hashlib, json, os, platform, resource, sys, time
import numpy as np
import scipy
from scipy import stats
from scipy.spatial import cKDTree
sys.path.insert(0, "analysis/fable/calibration")
from bank import designs, calib_features, load_bank
from validate import manifest_digest

HERE = os.path.dirname(os.path.abspath(__file__))
HELPERS = ("s0_info.py",)
SCEN = ("null_prior_predictive", "null_low_s", "MA_betamin", "MA_d10_0.5")    # b1, b3, b5, b16
NS = (30, 300)
IDS = range(200)
PARAMS = ("s", "f", "sigma", "rho", "p_c", "delta")
ESS_FLAG = 100
GH_X, GH_W = np.polynomial.hermite_e.hermegauss(40)
GH_W = GH_W / GH_W.sum()
ROOT = 20261014


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def cell(ni, si):
    return 4 * ni + si


def rate_functionals(p):
    ls = np.log(p["s"] / (1 - p["s"]))
    es = np.zeros(np.shape(ls))
    for x, w in zip(GH_X, GH_W):
        es = es + w / (1 + np.exp(-(ls + p["sigma"] * x)))
    keep = 1 - p["delta"] * p["p_c"]
    return keep * es, keep * p["f"]


def logw_noisy(sb, fb, n, k, r):
    """Binomial(k; n, s_bar) + Poisson(r; n f_bar) log-likelihood; exact at boundaries (scipy logpmf)."""
    return stats.binom.logpmf(k, n, sb) + stats.poisson.logpmf(r, n * fb)


def logw_ideal(sb, fb, n, sb0, fb0):
    with np.errstate(divide="ignore", invalid="ignore"):
        return n * (sb0 * np.log(sb) + (1 - sb0) * np.log1p(-sb)) + n * (fb0 * np.log(fb) - fb)


def weight_stats(lw):
    """Stable normalisation. -inf members get zero weight; NaN anywhere, or no finite member, makes the set unusable."""
    if np.isnan(lw).any() or not np.isfinite(lw).any():
        return {"usable": False, "ess": None, "max_share": None}
    w = np.exp(lw - lw[np.isfinite(lw)].max())
    w[~np.isfinite(lw)] = 0.0
    sw = w.sum()
    return {"usable": True, "ess": float(sw * sw / (w * w).sum()), "max_share": float(w.max() / sw)}


def self_test():
    K = 2000
    st = weight_stats(np.zeros(K)); assert st["usable"] and abs(st["ess"] - K) < 1e-9 and abs(st["max_share"] - 1 / K) < 1e-12
    lw = np.full(K, -800.0); lw[0] = 0.0
    st = weight_stats(lw); assert st["ess"] < 1 + 1e-9 and st["max_share"] > 1 - 1e-12                     # concentrated; no underflow error
    lw = np.full(K, -np.inf); lw[:3] = -5.0
    st = weight_stats(lw); assert abs(st["ess"] - 3) < 1e-9                                                   # zero-probability members
    assert not weight_stats(np.full(K, -np.inf))["usable"]                                                   # nothing finite
    bad = np.zeros(K); bad[5] = np.nan
    assert not weight_stats(bad)["usable"]                                                                   # invalid input reported, not replaced
    p = {"s": np.array([0.5]), "f": np.array([0.2]), "sigma": np.array([0.0]), "p_c": np.array([0.0]), "delta": np.array([0.5])}
    sb, fb = rate_functionals(p); assert abs(sb[0] - 0.5) < 1e-12 and abs(fb[0] - 0.2) < 1e-12              # quadrature at sigma = 0
    lw0 = logw_noisy(np.array([0.3, 0.6]), np.array([0.2, 0.2]), 30, 0, 0); assert np.isfinite(lw0).all()   # boundary k = 0
    lwn = logw_noisy(np.array([0.3, 0.6]), np.array([0.2, 0.2]), 30, 30, 6); assert np.isfinite(lwn).all()  # boundary k = n


def prepare(man_path, base, out):
    self_test()
    man = json.load(open(man_path)); pops = list(designs())
    scen = {s["name"]: s for s in man["scenarios"]}
    outers, srcs = {}, {}
    for si, name in enumerate(SCEN):
        s = scen[name]
        for c in s["chunks"]:
            if c["trial_ids"][0] > IDS[-1]:
                continue
            p = os.path.join(base, c["dir"], "e2e_rows.jsonl"); srcs[c["dir"]] = sha(p)
            for l in open(p):
                r = json.loads(l)
                if r["trial_id"] not in IDS:
                    continue
                sel = r["selected"]
                assert list(sel) == pops, "population order"
                for pn in pops:
                    assert all(np.isfinite(sel[pn]["params"][k]) for k in PARAMS), (name, r["trial_id"], pn)
                    rec = sel[pn]["recorded"]
                    assert len(rec) == len(designs()[pn]["years"])
                    assert all(v > 1 for v in rec[1:-1]) and rec[-1] <= 1, ("selection rule", name, r["trial_id"], pn)
                outers[f"{name}/{r['trial_id']}"] = {"dir": c["dir"], "kth_v1": json.loads(r["kth_dist"]),
                                                     "pops": {pn: {"recorded": sel[pn]["recorded"],
                                                                   "theta": {k: sel[pn]["params"][k] for k in PARAMS}} for pn in pops}}
    assert len(outers) == 800, len(outers)
    if any(o["pops"][pn]["theta"] != outers["null_low_s/0"]["pops"][pn]["theta"]
           for k2, o in outers.items() if k2.startswith("null_low_s/") for pn in pops):
        raise SystemExit("b3 outers do not share the fixed corner theta")
    E = {}
    for ni, n in enumerate(NS):
        for si, name in enumerate(SCEN):
            c = cell(ni, si)
            for i in IDS:
                for pi, pn in enumerate(pops):
                    th = outers[f"{name}/{i}"]["pops"][pn]["theta"]
                    sb, fb = rate_functionals({k: np.array([v]) for k, v in th.items()})
                    rng = np.random.default_rng([ROOT, 1, c, i, pi])
                    k = int(rng.binomial(n, sb[0])); r = int(rng.poisson(n * fb[0]))
                    E[f"{c}/{i}/{pn}"] = {"n": n, "k": k, "r": r, "sbar_true": float(sb[0]), "fbar_true": float(fb[0])}
    bind = {"stage": "external-information Stage 0 (no fits)", "authorised": "Barry, Claude chat 14 Oct 2026; Astra board 1625",
            "manifest_digest": manifest_digest(man_path), "source_rows_sha256": srcs,
            "population_order": pops, "scenario_order": list(SCEN), "blocks": ["b1", "b3", "b5", "b16"], "trial_ids": [0, 199],
            "n_levels": list(NS), "cell_map": "cell = 4 * n_index + scenario_index",
            "stream": "numpy.random.default_rng([20261014, 1, cell, trial, population_index]); k = binomial(n, sbar) then r = poisson(n * fbar)",
            "bit_generator": np.random.default_rng(0).bit_generator.__class__.__name__,
            "K": man["K"], "quadrature": "Gauss-Hermite (probabilists'), 40 nodes, weights normalised to 1",
            "weights": "log-weights normalised by subtracting the finite maximum; -inf -> weight 0; NaN or no finite member -> unusable (reported, never uniform)",
            "ess_flag": ESS_FLAG, "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
            "helper_sha256": {h: sha(os.path.join(HERE, h)) for h in HELPERS}}
    json.dump({"bindings": bind, "outers": outers, "E": E}, open(out, "w"))
    print("inputs", out, sha(out), "outers", len(outers), "E", len(E))


def run(man_path, base, inputs_path, outdir, only=None):
    t0 = time.time(); self_test()
    man = json.load(open(man_path)); d = json.load(open(inputs_path)); b = d["bindings"]
    if b["manifest_digest"] != manifest_digest(man_path) or b["helper_sha256"] != {h: sha(os.path.join(HERE, h)) for h in HELPERS} \
            or b["runtime"] != {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__}:
        raise SystemExit("run refused: manifest, helper bytes or runtime differ from the bound inputs")
    if any(sha(os.path.join(base, k2, "e2e_rows.jsonl")) != v for k2, v in b["source_rows_sha256"].items()):
        raise SystemExit("run refused: v1 source rows changed")
    bankdir = os.path.join(base, man["bankdir"])
    pops = b["population_order"] if only is None else [only]
    for pn in pops:
        if any(sha(os.path.join(bankdir, f)) != h for f, h in man["bank_sha256"].items() if f"_{pn}_" in f):
            raise SystemExit(f"run refused: {pn} bank bytes differ from the manifest")
    os.makedirs(outdir, exist_ok=True)
    K = b["K"]; keys = sorted(d["outers"])
    for pi_name in pops:
        tp = time.time(); pi = b["population_order"].index(pi_name)
        bk = load_bank(bankdir, man["variant"], pi_name)
        c = calib_features(bk["rec"]); mad = np.median(np.abs(c - np.median(c, 0)), 0); keep = mad > 0
        tree = cKDTree(c[:, keep] / mad[keep])
        sb_all, fb_all = rate_functionals(bk)                    # reused across n and both comparators
        obs = np.array([d["outers"][k]["pops"][pi_name]["recorded"] for k in keys])
        dist, idx = tree.query(calib_features(obs)[:, keep] / mad[keep], k=K, workers=8)
        d1, _ = tree.query(calib_features(obs)[:, keep] / mad[keep], k=K + 1, workers=8)
        res = []
        for j, key in enumerate(keys):
            name, i = key.split("/"); si = SCEN.index(name); i = int(i)
            sb, fb = sb_all[idx[j]], fb_all[idx[j]]
            logged = d["outers"][key]["kth_v1"][pi_name]
            row = {"outer": key, "kth": float(dist[j, -1]), "kth_v1_logged": logged,
                   "kth_mismatch": abs(round(float(dist[j, -1]), 4) - logged) > 1e-4, "tie": bool(d1[j, K - 1] == d1[j, K])}
            for ni, n in enumerate(NS):
                E = d["E"][f"{cell(ni, si)}/{i}/{pi_name}"]
                row[f"noisy_{n}"] = weight_stats(logw_noisy(sb, fb, n, E["k"], E["r"]))
                row[f"ideal_{n}"] = weight_stats(logw_ideal(sb, fb, n, E["sbar_true"], E["fbar_true"]))
            res.append(row)
        np.savez_compressed(os.path.join(outdir, f"members_{pi_name}.npz"), keys=np.array(keys), draw_id=bk["draw_id"][idx])
        json.dump({"population": pi_name, "bank_rows": int(len(bk["rec"])), "seconds": round(time.time() - tp, 1),
                   "peak_rss_gb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6, 2),
                   "members_sha256": sha(os.path.join(outdir, f"members_{pi_name}.npz")), "rows": res},
                  open(os.path.join(outdir, f"s0_{pi_name}.json"), "w"))
        print(pi_name, "rows", len(res), "s", round(time.time() - tp, 1), "peak GB",
              round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6, 2), flush=True)
        del bk, c, tree, sb_all, fb_all
    print("total s", round(time.time() - t0, 1))


def report(inputs_path, outdir, out):
    d = json.load(open(inputs_path)); b = d["bindings"]; pops = b["population_order"]
    per = {pn: json.load(open(os.path.join(outdir, f"s0_{pn}.json"))) for pn in pops}
    q = lambda v: [round(float(x), 4) for x in np.quantile(v, [0.05, 0.25, 0.5, 0.75, 0.95])] if len(v) else None
    res = {"stage": b["stage"], "inputs_sha256": sha(inputs_path), "bindings": {k: v for k, v in b.items()},
           "note": "ESS < 100 is an exploratory concentration flag only; Stage 0 cannot measure calibration or power.",
           "cost": {pn: {"seconds": per[pn]["seconds"], "peak_rss_gb": per[pn]["peak_rss_gb"], "bank_rows": per[pn]["bank_rows"],
                         "members_sha256": per[pn]["members_sha256"]} for pn in pops},
           "query": {"kth_mismatches_vs_v1_log": sum(r["kth_mismatch"] for pn in pops for r in per[pn]["rows"]),
                     "boundary_ties": sum(r["tie"] for pn in pops for r in per[pn]["rows"]),
                     "neighbourhoods": sum(len(per[pn]["rows"]) for pn in pops)},
           "cells": {}}
    for ni, n in enumerate(NS):
        for si, name in enumerate(SCEN):
            cl = {"scenario": name, "block": ["b1", "b3", "b5", "b16"][si], "n": n,
                  "theta_law": "fixed low-s corner" if name == "null_low_s" else "prior (b) per outer"}
            for comp in ("noisy", "ideal"):
                key = f"{comp}_{n}"
                rows = {pn: [r for r in per[pn]["rows"] if r["outer"].startswith(name + "/")] for pn in pops}
                ess = {pn: [r[key]["ess"] for r in rows[pn] if r[key]["usable"]] for pn in pops}
                mx = {pn: [r[key]["max_share"] for r in rows[pn] if r[key]["usable"]] for pn in pops}
                unusable = {pn: sum(not r[key]["usable"] for r in rows[pn]) for pn in pops}
                outer_ids = sorted({r["outer"] for pn in pops for r in rows[pn]})
                flag_any = 0; unus_any = 0
                for o in outer_ids:
                    rs = [next(r for r in rows[pn] if r["outer"] == o) for pn in pops]
                    unus_any += any(not r[key]["usable"] for r in rs)
                    flag_any += any((not r[key]["usable"]) or r[key]["ess"] < ESS_FLAG for r in rs)
                cl[comp] = {"ess_q05_25_50_75_95": {pn: q(ess[pn]) for pn in pops},
                            "max_share_q05_25_50_75_95": {pn: q(mx[pn]) for pn in pops},
                            "unusable_sets": unusable,
                            "datasets": len(outer_ids),
                            "any_of_nine_flag_fraction": round(flag_any / len(outer_ids), 4),
                            "any_of_nine_unusable_fraction": round(unus_any / len(outer_ids), 4),
                            "pooled_ess_q05_25_50_75_95": q([e for pn in pops for e in ess[pn]])}
            cl["kth_q05_50_95"] = {pn: [round(float(x), 4) for x in np.quantile([r["kth"] for r in per[pn]["rows"] if r["outer"].startswith(name + "/")], [0.05, 0.5, 0.95])]
                                   for pn in pops}
            res["cells"][f"{cell(ni, si)}"] = cl
    json.dump(res, open(out, "w"), indent=1, allow_nan=False)
    for c, cl in res["cells"].items():
        print(c, cl["block"], cl["n"], "noisy flag", cl["noisy"]["any_of_nine_flag_fraction"], "ideal flag", cl["ideal"]["any_of_nine_flag_fraction"],
              "pooled ESS median noisy/ideal", cl["noisy"]["pooled_ess_q05_25_50_75_95"][2], cl["ideal"]["pooled_ess_q05_25_50_75_95"][2])


if __name__ == "__main__":
    cmd, a = sys.argv[1], sys.argv[2:]
    if cmd == "prepare":
        prepare(*a)
    elif cmd == "run":
        run(*a)
    elif cmd == "report":
        report(*a)
