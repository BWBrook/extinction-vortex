"""A-screen: fixed 200-case fitted screen of unchanged candidate A (notes/vortex_v2_dev_plan_20261011.md §8).
Development triage on exposed v1 b3 outers (trial IDs 0-199). v1's frozen run_chunk is used unchanged; the
only substitution is its calibration-feature function, replaced by C+ = (msq, acf, inc, h1, h2). Run from
the frozen source root.
  prepare MANIFEST BASE OUT_JSON                       extract the 200 outers and their stored v1 results
  run     MANIFEST BASE OUTERS OUTDIR SLOT NSLOTS WORKERS   one slot of the 200 trials (resumable, bound)
  report  MANIFEST BASE OUTERS OUTDIR NSLOTS OUT_JSON  paired report; exits non-zero on any failed check"""
import json, os, platform, sys
import numpy as np
import scipy
from scipy import stats
from scipy.spatial import cKDTree
sys.path.insert(0, "analysis/fable/calibration")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e2e_benchmark as e2e
from bank import designs, calib_features, load_bank
from validate import manifest_digest
from knn_nuisance_c import sha
from a0_cplus import h_features
from d3_oracle import newcombe10, z_resid

IDS = range(200)
SEED = 8 * 10 ** 12 + 6 * 10 ** 6 + 10 ** 5 * 1
SMOKE = bool(os.environ.get("A_SMOKE"))                   # tiny end-to-end check, never a result
if SMOKE:
    IDS = range(2)
CPLUS = ("msq", "acf", "inc", "h1", "h2")


def cplus(rec):
    return np.column_stack([calib_features(rec), h_features(rec)[0]])


def b3_chunks(man):
    s = next(s for s in man["scenarios"] if s["name"] == "null_low_s")
    return [c for c in s["chunks"] if c["trial_ids"][0] < IDS[-1] + 1]


def prepare(man_path, base, out):
    man = json.load(open(man_path)); chunks = b3_chunks(man)
    rows = {}
    for c in chunks:
        for l in open(os.path.join(base, c["dir"], "e2e_rows.jsonl")):
            r = json.loads(l)
            if r["trial_id"] in IDS:
                rows[r["trial_id"]] = r
    assert sorted(rows) == list(IDS)
    json.dump({"manifest_digest": manifest_digest(man_path), "block": "null_low_s",
               "source_rows_sha256": {c["dir"]: sha(os.path.join(base, c["dir"], "e2e_rows.jsonl")) for c in chunks},
               "outers": [{"trial": i, "dir": next(c["dir"] for c in chunks if c["trial_ids"][0] <= i < c["trial_ids"][1]),
                           "recorded": {n: v["recorded"] for n, v in rows[i]["selected"].items()},
                           "v1": {k: rows[i].get(k) for k in ("outcome", "p_lo", "p_hi", "kth_dist", "fit_failures")}}
                          for i in IDS]}, open(out, "w"))
    print("outers", out, sha(out))


def cplus_banks(man, base, K):
    out = {}
    for n in designs():
        b = load_bank(os.path.join(base, man["bankdir"]), man["variant"], n)
        c3 = calib_features(b["rec"]); cp = np.column_stack([c3, h_features(b["rec"])[0]])
        mad3 = np.median(np.abs(c3 - np.median(c3, 0)), 0); k3 = mad3 > 0
        mad = np.median(np.abs(cp - np.median(cp, 0)), 0); keep = mad > 0
        assert len(b["rec"]) >= K
        out[n] = {"rec": b["rec"], "draw_id": b["draw_id"], "c3": c3[:, k3] / mad3[k3], "k3": k3, "mad3": mad3[k3],
                  "tree": cKDTree(cp[:, keep] / mad[keep]), "keep": keep, "mad": mad[keep],
                  "dropped": [f for f, k in zip(CPLUS, keep) if not k]}
        del c3, cp
        print("bank", n, len(b["rec"]), flush=True)
    return out


def run(man_path, base, outers_path, outdir, slot, nslots, workers):
    slot, nslots = int(slot), int(nslots)
    man = json.load(open(man_path)); des = designs(); K, R = (50, 20) if SMOKE else (man["K"], man["R"])
    od = json.load(open(outers_path)); os.makedirs(outdir, exist_ok=True)
    sdir = os.path.join(outdir, f"slot{slot}"); os.makedirs(sdir, exist_ok=True)
    rows_p, meta_p, nbr_p = (os.path.join(sdir, f) for f in ("e2e_rows.jsonl", "e2e_meta.json", "neighbours.npz"))
    meta = {"screen": "A-screen", "slot": slot, "nslots": nslots, "manifest_digest": manifest_digest(man_path),
            "outers_sha256": sha(outers_path), "K": K, "R_train": R, "R_test": R, "seed_base": SEED,
            "features": list(CPLUS), "r_workers": int(workers), "smoke": SMOKE,
            "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
            "source_sha256": {f: sha(f) for f in man["source_sha256"]}, "runner_sha256": sha(os.path.abspath(__file__))}
    ids = [json.loads(l)["trial_id"] for l in open(rows_p)] if os.path.exists(rows_p) else []
    nbr = dict(np.load(nbr_p)) if os.path.exists(nbr_p) else {}
    if ids:
        if not os.path.exists(meta_p) or json.load(open(meta_p)) != meta:
            raise SystemExit("resume refused: missing or different bindings")
        if len(ids) != len(set(ids)) or any(f"{i}/{n}" not in nbr for i in ids for n in des):
            raise SystemExit("resume refused: duplicate rows or missing neighbour receipts")
    json.dump(meta, open(meta_p, "w"), indent=1)
    banks = cplus_banks(man, base, K)
    e2e.calib_features = cplus                            # the single substitution in the frozen run_chunk
    mine = [i for i in IDS if i % nslots == slot and i not in set(ids)]
    for i in mine:
        o = od["outers"][i]; assert o["trial"] == i
        obs = {n: np.array(o["recorded"][n]) for n in des}
        for n, b in banks.items():
            q = cplus(obs[n][None, :])[0][b["keep"]] / b["mad"]
            dist, idx = b["tree"].query(q, k=K)
            d1, _ = b["tree"].query(q, k=K + 1)
            q3 = calib_features(obs[n][None, :])[0][b["k3"]] / b["mad3"]
            nbr[f"{i}/{n}"] = b["draw_id"][idx]
            nbr[f"{i}/{n}/tie"] = np.array([d1[K - 1] == d1[K]])
            nbr[f"{i}/{n}/kth"] = np.array([dist[-1]])
            nbr[f"{i}/{n}/origC_max"] = np.array([np.sqrt(((b["c3"][idx] - q3) ** 2).sum(1)).max()])
        e2e.run_chunk(banks, des, man["variant"], sdir, [i], R, K, workers, SEED + i, observed=obs)
        np.savez_compressed(nbr_p, **nbr)


def report(man_path, base, outers_path, outdir, nslots, out):
    man = json.load(open(man_path)); des = designs(); R = 20 if SMOKE else man["R"]
    od = json.load(open(outers_path)); osha = sha(outers_path)
    metas, rows, nbr = [], {}, {}
    for s in range(int(nslots)):
        sdir = os.path.join(outdir, f"slot{s}")
        metas.append(json.load(open(os.path.join(sdir, "e2e_meta.json"))))
        for l in open(os.path.join(sdir, "e2e_rows.jsonl")):
            r = json.loads(l)
            if r["trial_id"] in rows:
                raise SystemExit(f"duplicate trial {r['trial_id']}")
            rows[r["trial_id"]] = r | {"_dir": sdir}
        nbr.update(dict(np.load(os.path.join(sdir, "neighbours.npz"))))
    strip = lambda m: {k: v for k, v in m.items() if k != "slot"}
    checks = {
        "all_trials_once": sorted(rows) == list(IDS),
        "slot_bindings_identical": all(strip(m) == strip(metas[0]) for m in metas),
        "manifest_digest": metas[0]["manifest_digest"] == manifest_digest(man_path) == od["manifest_digest"],
        "outers_sha256": metas[0]["outers_sha256"] == osha,
        "source_rows_sha256": all(sha(os.path.join(base, d, "e2e_rows.jsonl")) == h for d, h in od["source_rows_sha256"].items()),
        "source_matches_manifest": metas[0]["source_sha256"] == man["source_sha256"]
                                   and all(sha(f) == h for f, h in man["source_sha256"].items()),
        "neighbour_receipts_complete": all(f"{i}/{n}{x}" in nbr for i in IDS for n in des for x in ("", "/tie", "/kth", "/origC_max")),
        "kth_matches_log": all(abs(round(float(nbr[f"{i}/{n}/kth"][0]), 4) - json.loads(rows[i]["kth_dist"])[n]) <= 1e-4
                               for i in IDS for n in des if "kth_dist" in rows[i])}
    bad = [k for k, v in checks.items() if not v]
    if bad:
        raise SystemExit(f"report refused, failed checks: {bad}")
    rejA = np.array([rows[i]["outcome"] != "accept" for i in IDS])
    rejV = np.array([od["outers"][i]["v1"]["outcome"] != "accept" for i in IDS])
    b = int((rejV & ~rejA).sum()); c = int((~rejV & rejA).sum()); a = int((rejV & rejA).sum()); d = len(IDS) - a - b - c
    zA = [z_resid(os.path.join(rows[i]["_dir"], f"T_{i}.csv"), R) for i in IDS]
    zV = [z_resid(os.path.join(base, od["outers"][i]["dir"], f"T_{i}.csv"), R) for i in IDS]
    mz = lambda zl: np.nanmean(np.array([[np.nan if v is None else v for v in z] for z, _ in zl if z is not None]), 0).round(3).tolist()
    origA = [max(float(nbr[f"{i}/{n}/origC_max"][0]) for n in des) for i in IDS]
    origV = [max(json.loads(od["outers"][i]["v1"]["kth_dist"]).values()) for i in IDS]
    n_ = len(IDS)
    res = {"screen": "A-screen, development triage (plan §8)", "n": n_, "checks": checks, "bindings": metas[0],
           "outcomes_A": {k: int(sum(rows[i]["outcome"] == k for i in IDS)) for k in sorted({rows[i]["outcome"] for i in IDS})},
           "nonaccepts": {"V1": int(rejV.sum()), "A": int(rejA.sum())},
           "exact_95": {k: [round(float(x), 4) for x in stats.binomtest(int(v.sum()), n_).proportion_ci()]
                        for k, v in (("V1", rejV), ("A", rejA))},
           "table_both_V1_only_A_only_neither": [a, b, c, d],
           "mcnemar_exact_p": float(stats.binomtest(min(b, c), b + c, 0.5).pvalue) if b + c else 1.0,
           "paired_difference_A_minus_V1": round((c - b) / n_, 4),
           "paired_difference_95_newcombe10": newcombe10(a, b, c, d),
           "fit_failures_A": int(sum(rows[i].get("fit_failures", 0) for i in IDS)),
           "mean_z_T1_T4": {"V1": mz(zV), "A": mz(zA)},
           "origC_max_kth_q10_50_90": {"V1": np.quantile(origV, [.1, .5, .9]).round(4).tolist(),
                                       "A": np.quantile(origA, [.1, .5, .9]).round(4).tolist()},
           "boundary_ties_A": int(sum(bool(nbr[f"{i}/{n}/tie"][0]) for i in IDS for n in des)),
           "t_fits_mean_s": round(float(np.mean([rows[i]["t_fits"] for i in IDS if "t_fits" in rows[i]])), 1)}
    json.dump(res, open(out, "w"), indent=1, allow_nan=False)
    print(json.dumps({k: v for k, v in res.items() if k != "bindings"}, indent=1))


if __name__ == "__main__":
    cmd, a = sys.argv[1], sys.argv[2:]
    {"prepare": prepare, "run": run, "report": report}[cmd](*a)
