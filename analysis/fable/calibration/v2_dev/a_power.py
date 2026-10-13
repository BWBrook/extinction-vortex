"""A power screen: unchanged candidate A on exposed v1 b5 (M_A at beta_min) and b16 (Delta10 = 0.5), trial IDs
0-299 of each, paired with their stored v1 results (plan §9; Astra's 13 October review). Practical
discrimination comparison only: it cannot identify why A's null rate changed, select or validate A, or bound
power at other effects. v1's frozen run_chunk is used unchanged apart from the C+ calibration-feature function
(as in a_screen.py, whose launched version is kept). Repairs from Astra's review: bank and helper bytes are
verified at run and report; the report checks the expected settings, not only slot consistency, and each row's
selected series against the bound outers; a resume requires every completed row's T file.
Run from the frozen source root.
  prepare MANIFEST BASE OUT_JSON                          extract the 600 outers, v1 results and bindings
  run     MANIFEST BASE OUTERS OUTDIR SLOT NSLOTS WORKERS  one slot (resumable, bound)
  report  MANIFEST BASE OUTERS OUTDIR NSLOTS OUT_JSON     exits non-zero on any failed check"""
import json, os, platform, sys
import numpy as np
import scipy
from scipy import stats
sys.path.insert(0, "analysis/fable/calibration")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e2e_benchmark as e2e
from bank import designs, calib_features
from validate import manifest_digest
from knn_nuisance_c import sha
from a_screen import cplus, cplus_banks, CPLUS
from d3_oracle import newcombe10, z_resid

HERE = os.path.dirname(os.path.abspath(__file__))
HELPERS = ("a_power.py", "a_screen.py", "a0_cplus.py", "knn_nuisance_c.py", "d3_oracle.py")
BLOCKS = {"MA_betamin": 5, "MA_d10_0.5": 16}
SMOKE = bool(os.environ.get("A_SMOKE"))                    # tiny end-to-end check, never a result
IDS = range(2) if SMOKE else range(300)
UNITS = [(b, i) for b in BLOCKS for i in IDS]


def seed(block, i):
    return 8 * 10 ** 12 + 6 * 10 ** 6 + 2 * 10 ** 5 + 10 ** 4 * BLOCKS[block] + i


def settings(man):
    K, R = (50, 20) if SMOKE else (man["K"], man["R"])
    return {"K": K, "R_train": R, "R_test": R, "features": list(CPLUS), "smoke": SMOKE,
            "seeds": {f"{b}/{i}": seed(b, i) for b, i in UNITS}}


def helper_hashes():
    return {h: sha(os.path.join(HERE, h)) for h in HELPERS}


def bank_ok(man, base):
    bankdir = os.path.join(base, man["bankdir"])
    return all(sha(os.path.join(bankdir, f)) == h for f, h in man["bank_sha256"].items())


def prepare(man_path, base, out):
    man = json.load(open(man_path))
    outers, src = {}, {}
    for s in man["scenarios"]:
        if s["name"] not in BLOCKS:
            continue
        for c in s["chunks"]:
            if c["trial_ids"][0] > IDS[-1]:
                continue
            p = os.path.join(base, c["dir"], "e2e_rows.jsonl"); src[c["dir"]] = sha(p)
            for l in open(p):
                r = json.loads(l)
                if r["trial_id"] in IDS:
                    outers[f"{s['name']}/{r['trial_id']}"] = {
                        "dir": c["dir"], "recorded": {n: v["recorded"] for n, v in r["selected"].items()},
                        "v1": {k: r.get(k) for k in ("outcome", "p_lo", "p_hi", "kth_dist", "fit_failures")}}
    assert sorted(outers) == sorted(f"{b}/{i}" for b, i in UNITS)
    json.dump({"manifest_digest": manifest_digest(man_path), "source_rows_sha256": src,
               "settings": settings(man), "helper_sha256": helper_hashes(), "outers": outers}, open(out, "w"))
    print("outers", out, sha(out))


def run(man_path, base, outers_path, outdir, slot, nslots, workers):
    slot, nslots = int(slot), int(nslots)
    man = json.load(open(man_path)); des = designs(); st = settings(man); K, R = st["K"], st["R_train"]
    od = json.load(open(outers_path))
    if od["settings"] != st or od["helper_sha256"] != helper_hashes() or od["manifest_digest"] != manifest_digest(man_path):
        raise SystemExit("run refused: settings, helper bytes or manifest differ from the bound outers file")
    if not bank_ok(man, base):
        raise SystemExit("run refused: primary bank bytes differ from the manifest")
    sdir = os.path.join(outdir, f"slot{slot}"); os.makedirs(sdir, exist_ok=True)
    rows_p, meta_p, nbr_p = (os.path.join(sdir, f) for f in ("e2e_rows.jsonl", "e2e_meta.json", "neighbours.npz"))
    meta = {"screen": "A-power", "slot": slot, "nslots": nslots, "outers_sha256": sha(outers_path),
            "r_workers": int(workers), "bank_verified": True,
            "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
            "source_sha256": {f: sha(f) for f in man["source_sha256"]}}
    done = []
    for b in BLOCKS:
        p = os.path.join(sdir, b, "e2e_rows.jsonl")
        done += [(b, json.loads(l)["trial_id"]) for l in open(p)] if os.path.exists(p) else []
    nbr = dict(np.load(nbr_p)) if os.path.exists(nbr_p) else {}
    if done:
        if not os.path.exists(meta_p) or json.load(open(meta_p)) != meta:
            raise SystemExit("resume refused: missing or different bindings")
        if len(done) != len(set(done)) or any(f"{b}/{i}/{n}" not in nbr for b, i in done for n in des) \
                or any(not os.path.exists(os.path.join(sdir, b, f"T_{i}.csv")) for b, i in done):
            raise SystemExit("resume refused: duplicate rows, missing neighbour receipts or missing T files")
    json.dump(meta, open(meta_p, "w"), indent=1)
    banks = cplus_banks(man, base, K)
    e2e.calib_features = cplus                             # the single substitution in the frozen run_chunk
    for b, i in [u for k, u in enumerate(UNITS) if k % nslots == slot and u not in set(done)]:
        o = od["outers"][f"{b}/{i}"]
        obs = {n: np.array(o["recorded"][n]) for n in des}
        for n, bk in banks.items():
            q = cplus(obs[n][None, :])[0][bk["keep"]] / bk["mad"]
            dist, idx = bk["tree"].query(q, k=K)
            d1, _ = bk["tree"].query(q, k=K + 1)
            q3 = calib_features(obs[n][None, :])[0][bk["k3"]] / bk["mad3"]
            nbr[f"{b}/{i}/{n}"] = bk["draw_id"][idx]
            nbr[f"{b}/{i}/{n}/tie"] = np.array([d1[K - 1] == d1[K]])
            nbr[f"{b}/{i}/{n}/kth"] = np.array([dist[-1]])
            nbr[f"{b}/{i}/{n}/origC_max"] = np.array([np.sqrt(((bk["c3"][idx] - q3) ** 2).sum(1)).max()])
        e2e.run_chunk(banks, des, man["variant"], os.path.join(sdir, b), [i], R, K, workers, seed(b, i), observed=obs)
        np.savez_compressed(nbr_p, **nbr)


def report(man_path, base, outers_path, outdir, nslots, out):
    man = json.load(open(man_path)); des = designs(); st = settings(man); R = st["R_train"]
    od = json.load(open(outers_path)); osha = sha(outers_path)
    metas, rows, nbr = [], {}, {}
    for s in range(int(nslots)):
        sdir = os.path.join(outdir, f"slot{s}")
        metas.append(json.load(open(os.path.join(sdir, "e2e_meta.json"))))
        for b in BLOCKS:
            p = os.path.join(sdir, b, "e2e_rows.jsonl")
            for l in open(p) if os.path.exists(p) else []:
                r = json.loads(l); key = f"{b}/{r['trial_id']}"
                if key in rows:
                    raise SystemExit(f"duplicate trial {key}")
                rows[key] = r | {"_T": os.path.join(sdir, b, f"T_{r['trial_id']}.csv")}
        nbr.update(dict(np.load(os.path.join(sdir, "neighbours.npz"))))
    keys = [f"{b}/{i}" for b, i in UNITS]
    strip = lambda m: {k: v for k, v in m.items() if k != "slot"}
    checks = {
        "all_trials_once": sorted(rows) == sorted(keys),
        "expected_settings": od["settings"] == st,
        "slot_bindings_identical": all(strip(m) == strip(metas[0]) for m in metas),
        "manifest_digest": od["manifest_digest"] == manifest_digest(man_path),
        "outers_sha256": all(m["outers_sha256"] == osha for m in metas),
        "helper_bytes": od["helper_sha256"] == helper_hashes(),
        "bank_bytes": bank_ok(man, base) and all(m["bank_verified"] for m in metas),
        "source_rows_sha256": all(sha(os.path.join(base, d, "e2e_rows.jsonl")) == h for d, h in od["source_rows_sha256"].items()),
        "source_matches_manifest": all(m["source_sha256"] == man["source_sha256"] for m in metas)
                                   and all(sha(f) == h for f, h in man["source_sha256"].items()),
        "selected_series_match_outers": all(rows[k]["selected"][n]["recorded"] == od["outers"][k]["recorded"][n]
                                            for k in keys for n in des),
        "T_files_present": all(os.path.exists(rows[k]["_T"]) for k in keys),
        "neighbour_receipts_complete": all(f"{k}/{n}{x}" in nbr for k in keys for n in des for x in ("", "/tie", "/kth", "/origC_max")),
        "kth_matches_log": all(abs(round(float(nbr[f"{k}/{n}/kth"][0]), 4) - json.loads(rows[k]["kth_dist"])[n]) <= 1e-4
                               for k in keys for n in des if "kth_dist" in rows[k])}
    bad = [k for k, v in checks.items() if not v]
    if bad:
        raise SystemExit(f"report refused, failed checks: {bad}")
    res = {"screen": "A power screen, practical discrimination comparison (plan §9)", "checks": checks,
           "settings_K_R": [st["K"], st["R_train"]], "blocks": {}}
    for b in BLOCKS:
        ks = [f"{b}/{i}" for i in IDS]; n_ = len(ks)
        detA = np.array([rows[k]["outcome"] == "reject" for k in ks])
        detV = np.array([od["outers"][k]["v1"]["outcome"] == "reject" for k in ks])
        bb = int((detV & ~detA).sum()); c = int((~detV & detA).sum()); a = int((detV & detA).sum()); d = n_ - a - bb - c
        zA = [z_resid(rows[k]["_T"], R) for k in ks]
        zV = [z_resid(os.path.join(base, od["outers"][k]["dir"], f"T_{k.split('/')[1]}.csv"), R) for k in ks]
        mz = lambda zl: np.nanmean(np.array([[np.nan if v is None else v for v in z] for z, _ in zl if z is not None]), 0).round(3).tolist()
        res["blocks"][b] = {
            "n": n_, "outcomes_A": {o: int(sum(rows[k]["outcome"] == o for k in ks)) for o in sorted({rows[k]["outcome"] for k in ks})},
            "detections": {"V1": int(detV.sum()), "A": int(detA.sum())},
            "exact_95": {lab: [round(float(x), 4) for x in stats.binomtest(int(v.sum()), n_).proportion_ci()]
                         for lab, v in (("V1", detV), ("A", detA))},
            "table_both_V1_only_A_only_neither": [a, bb, c, d],
            "mcnemar_exact_p": float(stats.binomtest(min(bb, c), bb + c, 0.5).pvalue) if bb + c else 1.0,
            "paired_difference_A_minus_V1": round((c - bb) / n_, 4),
            "paired_difference_95_newcombe10": newcombe10(a, bb, c, d),
            "fit_failures_A": int(sum(rows[k].get("fit_failures", 0) for k in ks)),
            "mean_z_T1_T4": {"V1": mz(zV), "A": mz(zA)},
            "origC_max_kth_q10_50_90": {
                "V1": np.quantile([max(json.loads(od["outers"][k]["v1"]["kth_dist"]).values()) for k in ks], [.1, .5, .9]).round(4).tolist(),
                "A": np.quantile([max(float(nbr[f"{k}/{n}/origC_max"][0]) for n in des) for k in ks], [.1, .5, .9]).round(4).tolist()},
            "t_fits_mean_s": round(float(np.mean([rows[k]["t_fits"] for k in ks if "t_fits" in rows[k]])), 1)}
    json.dump(res, open(out, "w"), indent=1, allow_nan=False)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    cmd, a = sys.argv[1], sys.argv[2:]
    {"prepare": prepare, "run": run, "report": report}[cmd](*a)
