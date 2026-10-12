"""D3: paired oracle contrast at the frozen low-s corner (notes/vortex_v2_dev_plan_20261011.md §2).
Development diagnostic; v1's frozen run code is imported unchanged. Run from the frozen source root.
  outers MANIFEST OUT_JSON                       200 fresh low-s outer datasets, one stream
  bank   MANIFEST OUTDIR PROCS                   fixed-theta_L bank (20 x 1e8 per population, one
                                                 extension to 40 shards if < 20,000 retained)
  run    ARM MANIFEST BASE OUTERS ORACLE OUTDIR WORKERS   ARM V (frozen primary bank) or O (oracle bank
                                                 in the primary bank's metric); resumable per trial
  report MANIFEST BASE OUTERS ORACLE DIR_V DIR_O RUNNER_SHA OUT_JSON   verified paired report (no fits):
                                                 bindings, shard and bank hashes, runtime, neighbour
                                                 draw IDs reconciled to the logged K-th distances, z
                                                 residuals (v1 complete-row rule), McNemar, Newcombe 10
The launch source (SHA-256 675bd8f2...) had `score` in place of `report`; Astra's 1546 review repairs
(support stop exits non-zero, resume checks bindings, sampling failures skip T files, method-10
correction, z convention, provenance) are applied here after the run, with no change to the fits."""
import hashlib, json, os, platform, sys, time
from multiprocessing import Pool
import numpy as np
import scipy
from scipy import stats
from scipy.spatial import cKDTree
sys.path.insert(0, "analysis/fable/calibration")
import e2e_benchmark as e2e
from bank import designs, simulate_chunk, calib_features, PARAM_NAMES
from validate import manifest_digest

ROOT = 8 * 10 ** 12 + 3 * 10 ** 6
N_OUT, SHARD, SHARDS, MIN_RETAINED, CHUNK = 200, 10 ** 8, 20, 20_000, 500_000
SMOKE = bool(os.environ.get("D3_SMOKE"))                 # tiny end-to-end check, never a result
if SMOKE:
    N_OUT, SHARD, SHARDS, MIN_RETAINED = 2, 2 * 10 ** 6, 2, 60
SEED = {"outers": ROOT, "V": ROOT + 10 ** 4, "O": ROOT + 2 * 10 ** 4, "bank": ROOT + 3 * 10 ** 4}


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def corner(man):
    s = next(s for s in man["scenarios"] if s["name"] == "null_low_s")
    return s["spec"]["fixed"]


def outers(man_path, out):
    man = json.load(open(man_path)); des = designs(); theta = corner(man)
    rng = np.random.default_rng(SEED["outers"]); res = []
    for i in range(N_OUT):
        draws = {n: e2e.fresh_selected(d, man["variant"], rng, 0.0, theta[n], None, None, man["budget"])
                 for n, d in des.items()}
        res.append({"trial": i, "selected": draws})
    json.dump({"manifest_digest": manifest_digest(man_path), "seed": SEED["outers"], "theta": theta,
               "budget": man["budget"], "outers": res}, open(out, "w"))
    print("outers", out, sha(out), "sampling failures",
          sum(any(v is None for v in r["selected"].values()) for r in res))


def bank_task(args):
    outdir, variant, pi, name, shard, theta = args
    d = designs()[name]; seed = SEED["bank"] + 100 * pi + shard
    rng = np.random.default_rng(seed); recs, ids, done, over = [], [], 0, 0
    while done < SHARD:
        rec, p, ov, sel = simulate_chunk(d, variant, min(CHUNK, SHARD - done), rng, fixed=theta)
        over += int(ov.sum()); recs.append(rec[sel].astype(np.int32))
        ids.append(shard * SHARD + done + np.flatnonzero(sel)); done += len(sel)
    rec = np.concatenate(recs)
    np.savez_compressed(os.path.join(outdir, f"oracle_{name}_s{shard:03d}.npz"), rec=rec,
                        draw_id=np.concatenate(ids), seed=seed, draws=SHARD, overflow=over)
    return {"population": name, "shard": shard, "seed": seed, "selected": len(rec), "overflow": over}


def bank(man_path, outdir, procs):
    man = json.load(open(man_path)); theta = corner(man); names = list(designs())
    os.makedirs(outdir, exist_ok=True)
    jobs = [(outdir, man["variant"], pi, n, s, theta[n]) for pi, n in enumerate(names) for s in range(SHARDS)]
    with Pool(procs) as pool:
        tasks = pool.map(bank_task, jobs, chunksize=1)
    count = {n: sum(t["selected"] for t in tasks if t["population"] == n) for n in names}
    short = [n for n in names if count[n] < MIN_RETAINED]
    if short:
        jobs = [(outdir, man["variant"], names.index(n), n, s, theta[n]) for n in short
                for s in range(SHARDS, 2 * SHARDS)]
        with Pool(procs) as pool:
            tasks += pool.map(bank_task, jobs, chunksize=1)
        count = {n: sum(t["selected"] for t in tasks if t["population"] == n) for n in names}
    meta = {"theta": theta, "shard_draws": SHARD, "tasks": tasks, "retained": count,
            "extended": short, "min_retained": MIN_RETAINED, "numpy": np.__version__,
            "stop": [n for n in names if count[n] < MIN_RETAINED]}
    json.dump(meta, open(os.path.join(outdir, "oracle_meta.json"), "w"), indent=1)
    print("retained", count, "STOP" if meta["stop"] else "ok")
    if meta["stop"]:
        raise SystemExit(f"oracle bank short of support: {meta['stop']}")


def oracle_banks(oracle_dir, primary):
    """Oracle trajectories with a k-d tree in the primary bank's metric (same feature mask and MAD)."""
    meta = json.load(open(os.path.join(oracle_dir, "oracle_meta.json")))
    if meta["stop"]:
        raise SystemExit(f"oracle bank short of support: {meta['stop']}")
    out = {}
    for n, pb in primary.items():
        parts = [np.load(os.path.join(oracle_dir, f"oracle_{n}_s{t['shard']:03d}.npz"))
                 for t in sorted(meta["tasks"], key=lambda t: t["shard"]) if t["population"] == n]
        rec = np.concatenate([z["rec"] for z in parts]); ids = np.concatenate([z["draw_id"] for z in parts])
        c = calib_features(rec)
        out[n] = {"rec": rec, "draw_id": ids, "tree": cKDTree(c[:, pb["keep"]] / pb["mad"]),
                  "keep": pb["keep"], "mad": pb["mad"], "dropped": pb["dropped"]}
    return out


def run(arm, man_path, base, outers_path, oracle_dir, outdir, workers):
    man = json.load(open(man_path)); des = designs(); K, R = (50, 20) if SMOKE else (man["K"], man["R"])
    od = json.load(open(outers_path)); os.makedirs(outdir, exist_ok=True)
    primary = e2e.knn_banks(os.path.join(base, man["bankdir"]), man["variant"], des, K)
    banks = primary if arm == "V" else oracle_banks(oracle_dir, primary)
    if arm == "O":
        del primary
    rows_p, meta_p = os.path.join(outdir, "e2e_rows.jsonl"), os.path.join(outdir, "e2e_meta.json")
    ids = [json.loads(l)["trial_id"] for l in open(rows_p)] if os.path.exists(rows_p) else []
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate trial rows")
    done = set(ids)
    meta = {"arm": arm, "manifest_digest": manifest_digest(man_path), "outers_sha256": sha(outers_path),
               "oracle_meta_sha256": sha(os.path.join(oracle_dir, "oracle_meta.json")) if arm == "O" else None,
               "K": K, "R_train": R, "R_test": R, "seed_base": SEED[arm], "r_workers": workers,
               "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
               "source_sha256": {f: sha(f) for f in man["source_sha256"]}}
    if os.path.exists(meta_p) and json.load(open(meta_p)) != meta:
        raise SystemExit("resume refused: bindings differ from the existing run")
    json.dump(meta, open(meta_p, "w"), indent=1)
    nbr_p = os.path.join(outdir, "neighbours.npz")
    nbr = dict(np.load(nbr_p)) if os.path.exists(nbr_p) else {}
    for o in od["outers"]:
        i = o["trial"]
        if i in done:
            continue
        if any(v is None for v in o["selected"].values()):
            with open(rows_p, "a") as fh:
                fh.write(json.dumps({"trial_id": i, "sampling_failed": [n for n, v in o["selected"].items() if v is None],
                                     "p_diagnostic": "indeterminate", "outcome": "indet_sampling"}) + "\n")
            continue
        obs = {n: np.array(v["recorded"]) for n, v in o["selected"].items()}
        for n, b in banks.items():
            q = calib_features(obs[n][None, :])[0][b["keep"]] / b["mad"]
            _, idx = b["tree"].query(q, k=K)                  # the query run_chunk makes
            dist1, _ = b["tree"].query(q, k=K + 1)
            # arm V: row indices into load_bank's concatenation of the primary bank; arm O: oracle draw IDs
            nbr[f"{i}/{n}"] = idx if arm == "V" else b["draw_id"][idx]
            nbr[f"{i}/{n}/tie"] = np.array([dist1[K - 1] == dist1[K]])
        e2e.run_chunk(banks, des, man["variant"], outdir, [i], R, K, workers, SEED[arm] + i, observed=obs)
        np.savez_compressed(nbr_p, **nbr)


def z_resid(path, R):
    """Standardised T residuals (T_obs - mean_train) / sd_train over v1's complete training rows
    (p_bounds: all four T finite), sd with ddof = 1 as np.cov; None if T is unreadable or the
    observed row is not finite. Returns (z, usable training rows)."""
    T = e2e.read_T(path, R)
    if T is None:
        return None, 0
    M = T[0]; tr = M[1:R + 1]; ok = np.isfinite(tr).all(1)
    if not np.isfinite(M[0]).all() or ok.sum() < 2:
        return None, int(ok.sum())
    sd = tr[ok].std(0, ddof=1)
    return [None if v == 0 else round(float((M[0][k] - tr[ok][:, k].mean()) / v), 5) for k, v in enumerate(sd)], int(ok.sum())


def newcombe10(a, b, c, d):
    """Newcombe (1998) method 10 hybrid-score 95% interval for the paired difference
    P(O reject) - P(V reject) = (c - b)/n, from the 2 x 2 table a = both reject, b = V only,
    c = O only, d = neither."""
    n = a + b + c + d; z = 1.959964

    def wilson(k):
        p = k / n; den = 1 + z * z / n
        ctr = (p + z * z / (2 * n)) / den; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
        return p, ctr - h, ctr + h
    p1, l1, u1 = wilson(a + b); p2, l2, u2 = wilson(a + c)
    den = np.sqrt(float((a + b) * (c + d) * (a + c) * (b + d)))
    num = a * d - b * c
    if num > 0:
        num = max(num - n / 2, 0.0)                     # method 10 correction (Newcombe 1998, s. 5)
    phi = num / den if den > 0 else 0.0
    D = p1 - p2
    dl = np.sqrt(max((p1 - l1) ** 2 - 2 * phi * (p1 - l1) * (u2 - p2) + (u2 - p2) ** 2, 0.0))
    du = np.sqrt(max((u1 - p1) ** 2 - 2 * phi * (u1 - p1) * (p2 - l2) + (p2 - l2) ** 2, 0.0))
    return [round(float(-(D + du)), 4), round(float(-(D - dl)), 4)]


def report(man_path, base, outers_path, oracle_dir, dir_v, dir_o, runner_sha, out):
    import subprocess
    from bank import load_bank
    man = json.load(open(man_path)); R, K = man["R"], man["K"]; des = designs(); dirs = {"V": dir_v, "O": dir_o}
    meta = {a: json.load(open(os.path.join(d, "e2e_meta.json"))) for a, d in dirs.items()}
    rows = {}
    for a, d in dirs.items():
        rr = [json.loads(l) for l in open(os.path.join(d, "e2e_rows.jsonl"))]
        assert len(rr) == len({r["trial_id"] for r in rr}), f"{a}: duplicate rows"
        rows[a] = {r["trial_id"]: r for r in rr}
    ids = range(N_OUT)
    assert all(set(rows[a]) == set(ids) for a in rows), "incomplete arm"
    od = json.load(open(outers_path)); osha = sha(outers_path)
    omp = os.path.join(oracle_dir, "oracle_meta.json"); om = json.load(open(omp))
    bankdir = os.path.join(base, man["bankdir"])
    checks = {
        "manifest_digest_bound": all(m["manifest_digest"] == manifest_digest(man_path) for m in meta.values()),
        "outers_sha256_bound": all(m["outers_sha256"] == osha for m in meta.values()),
        "oracle_meta_bound": meta["O"]["oracle_meta_sha256"] == sha(omp),
        "source_matches_manifest": all(m["source_sha256"] == man["source_sha256"] for m in meta.values())
                                   and all(sha(f) == h for f, h in man["source_sha256"].items()),
        "primary_bank_files_match_manifest": all(sha(os.path.join(bankdir, f)) == h for f, h in man["bank_sha256"].items()),
        "oracle_support_stop": om["stop"], "oracle_extended": om["extended"], "oracle_retained": om["retained"],
        "sampling_failures": sum(any(v is None for v in o["selected"].values()) for o in od["outers"]),
        "K_R_seeds": {a: [m["K"], m["R_train"], m["R_test"], m["seed_base"]] for a, m in meta.items()},
        "runtime_logged": {a: m["runtime"] for a, m in meta.items()},
        "R_nlme_at_report": subprocess.run(["Rscript", "-e", 'cat(R.version.string, as.character(packageVersion("nlme")))'],
                                           capture_output=True, text=True).stdout,
        "launch_runner_sha256": open(runner_sha).read().split()[0],
        "oracle_shard_sha256": {f: sha(os.path.join(oracle_dir, f)) for f in sorted(os.listdir(oracle_dir)) if f.endswith(".npz")}}
    # neighbour receipts: V row indices -> draw IDs; recompute each stored set's K-th distance
    nb = {a: dict(np.load(os.path.join(d, "neighbours.npz"))) for a, d in dirs.items()}
    recon = {a: {"sets": 0, "kth_mismatch": 0, "ties": 0} for a in dirs}
    drawids = {"V": {}, "O": {}}
    for n in des:
        pb = load_bank(bankdir, man["variant"], n)
        c = calib_features(pb["rec"]); mad = np.median(np.abs(c - np.median(c, axis=0)), axis=0); keep = mad > 0
        parts = [np.load(os.path.join(oracle_dir, f"oracle_{n}_s{t['shard']:03d}.npz"))
                 for t in sorted(om["tasks"], key=lambda t: t["shard"]) if t["population"] == n]
        orec = np.concatenate([z["rec"] for z in parts]); oid = np.concatenate([z["draw_id"] for z in parts])
        for i in ids:
            q = calib_features(np.array(od["outers"][i]["selected"][n]["recorded"])[None, :])[0][keep] / mad[keep]
            for a in dirs:
                key = f"{i}/{n}"
                if key not in nb[a]:
                    continue
                if a == "V":
                    members = pb["rec"][nb[a][key]]; drawids["V"][key] = pb["draw_id"][nb[a][key]]
                else:
                    members = orec[np.searchsorted(oid, nb[a][key])]; drawids["O"][key] = nb[a][key]
                kth = np.sqrt(((calib_features(members)[:, keep] / mad[keep] - q) ** 2).sum(1)).max()
                logged = json.loads(rows[a][i]["kth_dist"])[n]
                recon[a]["sets"] += 1; recon[a]["ties"] += int(nb[a][key + "/tie"][0])
                recon[a]["kth_mismatch"] += int(abs(round(float(kth), 4) - logged) > 1e-4)
        del pb, c, orec, oid
    for a in dirs:
        p = os.path.join(dirs[a], "neighbour_draw_ids.npz"); np.savez_compressed(p, **drawids[a])
        recon[a]["draw_id_archive_sha256"] = sha(p)
    checks["neighbour_reconciliation"] = recon
    rej = {a: np.array([rows[a][i]["outcome"] != "accept" for i in ids]) for a in rows}
    b = int((rej["V"] & ~rej["O"]).sum()); c = int((~rej["V"] & rej["O"]).sum())
    a2 = int((rej["V"] & rej["O"]).sum()); d2 = N_OUT - a2 - b - c
    zz = {}
    for a in dirs:
        zl = [z_resid(os.path.join(dirs[a], f"T_{i}.csv"), R) if rows[a][i]["outcome"] != "indet_sampling" else (None, 0)
              for i in ids]
        Z = np.array([[np.nan if v is None else v for v in z] for z, _ in zl if z is not None])
        zz[a] = {"per_trial": [z for z, _ in zl], "usable_training_rows": [u for _, u in zl],
                 "trials_with_z": len(Z), "mean": np.nanmean(Z, 0).round(3).tolist(),
                 "sd": np.nanstd(Z, 0, ddof=1).round(3).tolist()}
    kth = {a: [max(json.loads(rows[a][i]["kth_dist"]).values()) for i in ids if "kth_dist" in rows[a][i]] for a in rows}
    res = {"diagnostic": "D3 paired oracle contrast, verified report", "outers_sha256": osha, "n": N_OUT,
           "checks": checks,
           "outcomes": {a: {k: sum(r["outcome"] == k for r in rows[a].values())
                            for k in sorted({r["outcome"] for r in rows[a].values()})} for a in rows},
           "nonaccepts": {a: int(rej[a].sum()) for a in rej},
           "exact_95": {a: [round(float(x), 4) for x in stats.binomtest(int(rej[a].sum()), N_OUT).proportion_ci()]
                        for a in rej},
           "table_both_V_only_O_only_neither": [a2, b, c, d2], "mcnemar_exact_p": float(stats.binomtest(min(b, c), b + c, 0.5).pvalue)
           if b + c else 1.0, "paired_difference_O_minus_V": round((c - b) / N_OUT, 4),
           "paired_difference_95_newcombe10": newcombe10(a2, b, c, d2),
           "fit_failures": {a: sum(r.get("fit_failures", 0) for r in rows[a].values()) for a in rows},
           "z_T1_T4": {a: {k: v for k, v in zz[a].items() if k != "per_trial"} for a in zz},
           "max_kth_q10_50_90": {a: np.quantile(kth[a], [.1, .5, .9]).round(4).tolist() for a in kth}}
    json.dump(res, open(out, "w"), indent=1, allow_nan=False)
    json.dump({a: zz[a]["per_trial"] for a in zz}, open(out.replace(".json", "_z.json"), "w"))
    print(json.dumps({k: v for k, v in res.items() if k != "checks"}, indent=1))
    print(json.dumps({k: v for k, v in checks.items() if k != "oracle_shard_sha256"}, indent=1))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "outers":
        outers(sys.argv[2], sys.argv[3])
    elif cmd == "bank":
        bank(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    elif cmd == "run":
        run(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8])
    elif cmd == "report":
        report(*sys.argv[2:10])
