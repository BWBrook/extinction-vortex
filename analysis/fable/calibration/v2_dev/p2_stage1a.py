"""Stage 1a: capped informative-sampler pilot for kunanyi (notes/astra_p1_and_repairs_review_20261015.md §4).
No fits, no full libraries, no empirical test. Sampler law as in p1_sampler.py (tested there): theta ~ frozen prior;
accept with L(E|theta)/M_E (Poisson then binomial, independent uniforms); one null path per accepted theta; retain if
S, A and the closed C-ball hold; restart otherwise. Settings: 9 populations x b1/b3/b5/b16 x trial IDs 0-9 x n in
{30, 300} noisy (720) plus one n = 0 control per population-outer pair (360).
Repairs required before scale (Astra 1657): actual imported-source and exported-input hashes bound and recorded in
every result; mask/MAD/query/radius exported once (workers never load a bank); atomic per-batch checkpoints with
deterministic resume and explicit complete/censored/failed states; a hard wall deadline; admissible-evidence checks
(n = 0 implies k = r = 0); exact coordinate equality when the radius is zero; exposure counts only simulated batches
(no path cap truncation). Run from the frozen source root.
  export   MANIFEST BASE S0_INPUTS S0_FULLDIR OUT_METRIC           (deep-server; loads each bank once)
  settings METRIC OUT_SETTINGS PROPOSALS_INFO PROPOSALS_N0 BATCH NWORKERS [THROUGHPUT_JSON SECONDS_INFO SECONDS_N0]
           bind settings, budgets (fixed proposals, or seconds x measured smoke throughput per setting), LPT worker assignment
  test     METRIC                                                  guard/resume fixtures (exits non-zero on failure)
  run      SETTINGS METRIC OUTDIR WORKER NWORKERS DEADLINE_EPOCH  one worker; resumable
  collect  SETTINGS METRIC OUTDIR OUT_JSON
  throughput COLLECT_JSON OUT_JSON                             per-setting proposals per CPU-second from a smoke collect
"""
import hashlib, json, math, os, platform, resource, shutil, sys, tempfile, time
import numpy as np
import scipy
from scipy.special import xlogy, xlog1py
sys.path.insert(0, "analysis/fable/calibration")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bank
from bank import designs, calib_features, load_bank
from p1_sampler import rate_functionals, simulate_given

HERE = os.path.dirname(os.path.abspath(__file__))
POPS = ("wild_dog", "marmot", "ms_woodpecker", "rc_woodpecker", "golden_plover", "whooping_crane", "hawaiian_crow",
        "wood_turtle_A", "wood_turtle_B")
SCEN = ("null_prior_predictive", "null_low_s", "MA_betamin", "MA_d10_0.5")
TRIALS = range(10)
NS = (30, 300)
PARAMS = ("s", "f", "sigma", "rho", "p_c", "delta")
IMPORTED = ("analysis/fable/calibration/bank.py",)
LOG_TOL = 1e-9
ROOT = 20261015


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def runtime():
    return {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__}


def atomic_json(obj, path):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".tmp_")
    with os.fdopen(fd, "w") as fh:
        json.dump(obj, fh)
        fh.flush(); os.fsync(fh.fileno())
    os.replace(tmp, path)


def validate_E(E):
    n, k, r = E["n"], E["k"], E["r"]
    ok = all(isinstance(x, int) for x in (n, k, r)) and n >= 0 and 0 <= k <= n and r >= 0
    if n == 0:
        ok = ok and k == 0 and r == 0
    if not ok:
        raise SystemExit(f"inadmissible evidence {E}")


def factors(th, E):
    """Poisson then binomial log acceptance factors (h - H); n = 0 gives zeros."""
    n, k, r = E["n"], E["k"], E["r"]
    vbar = th["f"] * (1 - th["delta"] * th["p_c"])
    if n == 0:
        return np.zeros(len(vbar)), None
    hp = xlogy(r, vbar) - n * vbar - (xlogy(r, r / n) - r)
    return hp, (n, k)


def binom_factor(u, n, k):
    return xlogy(k, u) + xlog1py(n - k, -u) - (xlogy(k, k / n) + xlog1py(n - k, -k / n))


def in_ball(cs, q, radius):
    """Closed ball in the exported metric. radius == 0 means exact equality on every retained coordinate."""
    if radius == 0.0:
        eq = np.all(cs == q, axis=1)
        return {"in": eq, "boundary": eq, "in_lo": np.zeros(len(cs), bool), "in_hi": eq}
    d = np.sqrt(((cs - q) ** 2).sum(1))
    lo, hi = np.nextafter(radius, -np.inf), np.nextafter(radius, np.inf)
    return {"in": d <= radius, "boundary": d == radius, "in_lo": d <= lo, "in_hi": d <= hi}


def export(man_path, base, s0_inputs, s0_full, out):
    man = json.load(open(man_path)); s0 = json.load(open(s0_inputs))
    assert tuple(s0["bindings"]["population_order"]) == POPS
    metric = {"source_bank_sha256": {}, "pops": {}, "outers": {}, "s0_inputs_sha256": sha(s0_inputs)}
    bankdir = os.path.join(base, man["bankdir"])
    for pop in POPS:
        files = {f: h for f, h in man["bank_sha256"].items() if f"_{pop}_" in f}
        if any(sha(os.path.join(bankdir, f)) != h for f, h in files.items()):
            raise SystemExit(f"{pop}: bank bytes differ from the manifest")
        bk = load_bank(bankdir, man["variant"], pop)
        c = calib_features(bk["rec"]); mad = np.median(np.abs(c - np.median(c, 0)), 0); keep = mad > 0
        metric["pops"][pop] = {"keep": keep.tolist(), "mad": mad.tolist(), "bank_rows": int(len(c))}
        metric["source_bank_sha256"][pop] = files
        rows = {r["outer"]: r for r in json.load(open(os.path.join(s0_full, f"s0_{pop}.json")))["rows"]}
        for sc in SCEN:
            for t in TRIALS:
                key = f"{sc}/{t}"
                rec = s0["outers"][key]["pops"][pop]["recorded"]
                q = (calib_features(np.array([rec]))[0][keep] / mad[keep]).tolist()
                metric["outers"][f"{pop}|{key}"] = {"recorded": rec, "q": q, "radius": rows[key]["kth"]}
        del bk, c
        print("exported", pop, flush=True)
    metric["bank_meta_sha256"] = sha(os.path.join(bankdir, "bank_meta.json"))
    if metric["bank_meta_sha256"] != man["bank_sha256"]["bank_meta.json"]:
        raise SystemExit("bank_meta.json differs from the manifest")
    metric["E"] = {}
    for ni, n in enumerate(NS):
        for si, sc in enumerate(SCEN):
            for t in TRIALS:
                for pop in POPS:
                    e = s0["E"][f"{4 * ni + si}/{t}/{pop}"]
                    metric["E"][f"{pop}|{sc}/{t}|{n}"] = {"n": e["n"], "k": e["k"], "r": e["r"]}
    json.dump(metric, open(out, "w"))
    print("metric", out, sha(out))


def settings(metric_path, out, prop_info, prop_n0, batch, nworkers, throughput=None, sec_info=None, sec_n0=None):
    metric = json.load(open(metric_path)); prop_info, prop_n0, batch, nworkers = int(prop_info), int(prop_n0), int(batch), int(nworkers)
    rate = json.load(open(throughput)) if throughput else None            # {"pop|outer|n": proposals per CPU-second}
    st = []
    for pop in POPS:
        for sc in SCEN:
            for t in TRIALS:
                for n in (0,) + NS:
                    E = {"n": 0, "k": 0, "r": 0} if n == 0 else metric["E"][f"{pop}|{sc}/{t}|{n}"]
                    validate_E(E)
                    if rate:
                        secs = float(sec_n0) if n == 0 else float(sec_info)
                        budget = max(batch, int(rate[f"{pop}|{sc}/{t}|{n}"] * secs) // batch * batch)
                    else:
                        budget = prop_n0 if n == 0 else prop_info
                    st.append({"index": len(st), "pop": pop, "outer": f"{sc}/{t}", "n": n, "E": E,
                               "proposal_budget": budget, "batches": math.ceil(budget / batch),
                               "expected_seconds": (budget / rate[f"{pop}|{sc}/{t}|{n}"]) if rate else None})
    load = [0.0] * nworkers                                               # LPT on expected seconds (or budgets)
    for s_ in sorted(st, key=lambda x: (-(x["expected_seconds"] or x["proposal_budget"]), x["index"])):
        w = min(range(nworkers), key=lambda i: (load[i], i)); s_["worker"] = w
        load[w] += s_["expected_seconds"] or s_["proposal_budget"]
    b = {"stage": "1a capped informative-sampler pilot (no fits)", "metric_sha256": sha(metric_path),
         "runner_sha256": sha(os.path.abspath(__file__)), "p1_sampler_sha256": sha(os.path.join(HERE, "p1_sampler.py")),
         "imported_source_sha256": {f: sha(f) for f in IMPORTED},
         "allowed_runtimes": [{"python": "3.11.7", "numpy": "1.26.4", "scipy": "1.11.4"},
                              {"python": "3.12.3", "numpy": "1.26.4", "scipy": "1.11.4"}],
         "batch": batch, "nworkers": nworkers, "throughput_sha256": sha(throughput) if throughput else None,
         "seconds_info": sec_info, "seconds_n0": sec_n0,
         "stream": f"numpy.random.default_rng([{ROOT}, 2, setting_index, batch_index]); draw_params(B), Poisson "
                   "uniforms(B), binomial uniforms(B), then simulate_given(all accepted theta) in that order",
         "ball": "closed; float64 sqrt(sum((C[keep]/mad[keep] - q)^2)) <= radius; radius 0 means exact coordinate equality",
         "assignment": "longest-processing-time packing of expected seconds (or budgets) onto NWORKERS; ties by index",
         "max_worker_expected_seconds": max(load) if rate else None, "settings": st}
    json.dump(b, open(out, "w"))
    print("settings", out, sha(out), len(st), "total proposals", sum(x["proposal_budget"] for x in st),
          "max worker load", round(max(load), 1))


def check(settings_path, metric_path):
    b = json.load(open(settings_path))
    if b["metric_sha256"] != sha(metric_path) or b["runner_sha256"] != sha(os.path.abspath(__file__)) \
            or b["p1_sampler_sha256"] != sha(os.path.join(HERE, "p1_sampler.py")) \
            or any(sha(f) != h for f, h in b["imported_source_sha256"].items()) or runtime() not in b["allowed_runtimes"]:
        raise SystemExit("refused: metric, runner, helper, imported source or runtime differ from the bound settings")
    return b


def one_batch(st, mp, bi, B, des):
    rng = np.random.default_rng([ROOT, 2, st["index"], bi])
    th = bank.draw_params("ar_cat", B, rng)
    up, ub = np.log(rng.random(B)), np.log(rng.random(B))
    E = st["E"]; hp, nb = factors(th, E)
    out = {"proposals": B, "poisson_accept": 0, "theta_accept": 0, "paths": 0, "selected_SA": 0, "overflow": 0,
           "hits": 0, "boundary": 0, "hits_lo": 0, "hits_hi": 0, "rounding_excess": 0, "hit_records": []}
    if (hp > LOG_TOL).any():
        raise RuntimeError("bound violation (Poisson)")
    out["rounding_excess"] += int((hp > 0).sum())
    idx = np.flatnonzero(up < hp); out["poisson_accept"] = int(len(idx))
    sub = {k: th[k][idx] for k in PARAMS}
    if nb is not None:
        u, _ = rate_functionals(sub); hb = binom_factor(u, *nb)
        if (hb > LOG_TOL).any():
            raise RuntimeError("bound violation (binomial)")
        out["rounding_excess"] += int((hb > 0).sum())
        okb = ub[idx] < hb
    else:
        okb = np.ones(len(idx), bool)
    pid = idx[okb]; acc = {k: v[okb] for k, v in sub.items()}
    out["theta_accept"] = int(len(pid))
    if len(pid):
        rec, p, over, sel = simulate_given(des[st["pop"]], "ar_cat", acc, rng)      # every accepted theta is simulated
        out["paths"] = int(len(pid)); out["overflow"] = int(over.sum()); out["selected_SA"] = int(sel.sum())
        if sel.any():
            keep = np.array(mp["keep"]); mad = np.array(mp["mad"])
            cs = calib_features(rec[sel])[:, keep] / mad[keep]
            bl = in_ball(cs, np.array(mp["q"]), mp["radius"])
            out["hits"] = int(bl["in"].sum()); out["boundary"] = int(bl["boundary"].sum())
            out["hits_lo"] = int(bl["in_lo"].sum()); out["hits_hi"] = int(bl["in_hi"].sum())
            sp = pid[sel]
            for j in np.flatnonzero(bl["in"]):
                out["hit_records"].append({"batch": bi, "proposal_in_batch": int(sp[j]), "boundary": bool(bl["boundary"][j]),
                                           "theta": {k: float(acc[k][np.flatnonzero(sel)[j]]) for k in PARAMS},
                                           "recorded": rec[sel][j].astype(int).tolist()})
    return out


def run_setting(b, st, mp, outdir, deadline, des):
    ck = os.path.join(outdir, f"s{st['index']:04d}.json"); hits_p = os.path.join(outdir, f"s{st['index']:04d}_hits.jsonl")
    keys = ("proposals", "poisson_accept", "theta_accept", "paths", "selected_SA", "overflow", "hits", "boundary",
            "hits_lo", "hits_hi", "rounding_excess")
    if os.path.exists(ck):
        S = json.load(open(ck))
        if S["binding"] != b["_binding"]:
            raise SystemExit(f"setting {st['index']}: checkpoint bound to other inputs")
        if S["status"] in ("complete", "failed"):
            return S
        lines = open(hits_p).read().splitlines() if os.path.exists(hits_p) else []
        with open(hits_p, "w") as fh:                       # drop hit records past the last committed batch
            for l in lines[:S["hits"]]:
                fh.write(l + "\n")
    else:
        S = {"index": st["index"], "binding": b["_binding"], "batches_done": 0, "status": "running", "cpu_seconds": 0.0,
             "wall_seconds": 0.0, **{k: 0 for k in keys}}
    while S["batches_done"] < st["batches"]:
        if time.time() > deadline:
            S["status"] = "censored"; atomic_json(S, ck); return S
        t0, c0 = time.time(), time.process_time()
        bi = S["batches_done"]
        B = min(b["batch"], st["proposal_budget"] - bi * b["batch"])
        try:
            r = one_batch(st, mp, bi, B, des)
        except RuntimeError as e:
            S["status"] = "failed"; S["failure"] = str(e); atomic_json(S, ck); return S
        if r["hit_records"]:
            with open(hits_p, "a") as fh:
                for h in r["hit_records"]:
                    fh.write(json.dumps(h) + "\n")
                fh.flush(); os.fsync(fh.fileno())
        for k in keys:
            S[k] += r[k]
        S["batches_done"] += 1
        S["cpu_seconds"] += time.process_time() - c0; S["wall_seconds"] += time.time() - t0
        atomic_json(S, ck)
    S["status"] = "complete"; atomic_json(S, ck)
    return S


def run(settings_path, metric_path, outdir, worker, nworkers, deadline):
    b = check(settings_path, metric_path); metric = json.load(open(metric_path))
    b["_binding"] = {"settings_sha256": sha(settings_path), "metric_sha256": b["metric_sha256"], "runner_sha256": b["runner_sha256"]}
    worker, nworkers, deadline = int(worker), int(nworkers), float(deadline)
    os.makedirs(outdir, exist_ok=True); des = designs()
    if nworkers != b["nworkers"]:
        raise SystemExit("refused: NWORKERS differs from the bound assignment")
    for st in sorted((x for x in b["settings"] if x["worker"] == worker), key=lambda x: x["index"]):
        validate_E(st["E"])
        mp = metric["outers"][f"{st['pop']}|{st['outer']}"]
        mp = dict(mp, keep=metric["pops"][st["pop"]]["keep"], mad=metric["pops"][st["pop"]]["mad"])
        if not (math.isfinite(mp["radius"]) and mp["radius"] >= 0):
            raise SystemExit(f"setting {st['index']}: invalid radius")
        run_setting(b, st, mp, outdir, deadline, des)       # past the deadline this writes an explicit censored checkpoint
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1048576           # KiB -> GiB
    atomic_json({"worker": worker, "nworkers": nworkers, "peak_rss_gib": round(peak, 3), "runtime": runtime(),
                 "host": platform.node(), "binding": b["_binding"]}, os.path.join(outdir, f"worker{worker:04d}.json"))


def test(metric_path):
    """Guard and resume fixtures on a tiny temporary setting (one population, two short batches)."""
    metric = json.load(open(metric_path)); des = designs(); res = {}
    for bad in ({"n": 0, "k": 1, "r": 0}, {"n": 30, "k": 31, "r": 0}, {"n": 30, "k": 3, "r": -1}, {"n": 30, "k": 3.5, "r": 2}):
        try:
            validate_E(bad); res[f"rejects_{bad}"] = False
        except SystemExit:
            res[f"rejects_{bad}"] = True
    q = np.array([1.0, 2.0])
    r0 = in_ball(np.array([[1.0, 2.0], [1.0, np.nextafter(2.0, 3.0)], [1.0, 2.1]]), q, 0.0)   # adjacent float is not equal
    res["radius_zero_exact_equality"] = r0["in"].tolist() == [True, False, False]
    st = {"index": 9999, "pop": "hawaiian_crow", "outer": "null_low_s/0", "n": 30,
          "E": metric["E"]["hawaiian_crow|null_low_s/0|30"], "proposal_budget": 40_000, "batches": 2}
    mp = dict(metric["outers"]["hawaiian_crow|null_low_s/0"], keep=metric["pops"]["hawaiian_crow"]["keep"],
              mad=metric["pops"]["hawaiian_crow"]["mad"])
    b = {"batch": 20_000, "_binding": {"fixture": True}}
    d1, d2 = tempfile.mkdtemp(), tempfile.mkdtemp()
    try:
        full = run_setting(b, st, mp, d1, float("inf"), des)
        part = run_setting(b, dict(st, batches=1), mp, d2, float("inf"), des)          # one batch, then "killed"
        S = json.load(open(os.path.join(d2, "s9999.json"))); S["status"] = "running"; atomic_json(S, os.path.join(d2, "s9999.json"))
        resumed = run_setting(b, st, mp, d2, float("inf"), des)
        keys = ("proposals", "theta_accept", "paths", "selected_SA", "hits", "boundary")
        res["resume_deterministic"] = all(full[k] == resumed[k] for k in keys) and resumed["batches_done"] == 2
        censored = run_setting(b, dict(st, index=9998), mp, d1, time.time() - 1, des)
        res["deadline_censors_without_exposure"] = censored["status"] == "censored" and censored["proposals"] == 0
        res["fixture_counts"] = {k: full[k] for k in keys}
    finally:
        shutil.rmtree(d1); shutil.rmtree(d2)
    res["all_ok"] = all(v for k, v in res.items() if k != "fixture_counts")
    print(json.dumps(res, indent=1))
    if not res["all_ok"]:
        raise SystemExit("tests failed")


def collect(settings_path, metric_path, outdir, out):
    b = json.load(open(settings_path))
    binding = {"settings_sha256": sha(settings_path), "metric_sha256": b["metric_sha256"], "runner_sha256": b["runner_sha256"]}
    rows, status = [], {"complete": 0, "censored": 0, "failed": 0, "missing": 0, "running": 0}
    for st in b["settings"]:
        ck = os.path.join(outdir, f"s{st['index']:04d}.json")
        if not os.path.exists(ck):
            status["missing"] += 1; rows.append({**st, "status": "missing"}); continue
        S = json.load(open(ck))
        if S["binding"] != binding:
            raise SystemExit(f"setting {st['index']}: bound to other inputs")
        nh = len(open(os.path.join(outdir, f"s{st['index']:04d}_hits.jsonl")).read().splitlines()) \
            if os.path.exists(os.path.join(outdir, f"s{st['index']:04d}_hits.jsonl")) else 0
        if nh != S["hits"]:
            raise SystemExit(f"setting {st['index']}: hit records {nh} != checkpoint {S['hits']}")
        status[S["status"]] += 1
        rate = S["hits"] / S["proposals"] if S["proposals"] else None
        upper = (3.0 / S["proposals"] if S["hits"] == 0 else None) if S["proposals"] else None      # ~95% one-sided for zero hits
        cpu_per_prop = S["cpu_seconds"] / S["proposals"] if S["proposals"] else None
        to2000 = (2000 / rate * cpu_per_prop / 3600) if rate else None
        rows.append({k: st[k] for k in ("index", "pop", "outer", "n")} | {k: S[k] for k in S if k not in ("binding",)} |
                    {"retention_per_proposal": rate, "zero_hit_upper95": upper, "cpu_hours_to_2000": to2000})
    workers = [json.load(open(os.path.join(outdir, f))) for f in sorted(os.listdir(outdir)) if f.startswith("worker")]
    json.dump({"binding": binding, "status": status, "workers": workers, "rows": rows}, open(out, "w"), indent=1, allow_nan=False)
    print("status", status, "cpu_hours", round(sum(r.get("cpu_seconds", 0) for r in rows) / 3600, 2),
          "hits", sum(r.get("hits", 0) for r in rows))


def throughput(collect_json, out):
    c = json.load(open(collect_json))
    if c["status"]["complete"] != len(c["rows"]):
        raise SystemExit(f"smoke incomplete: {c['status']}")
    rate = {f"{r['pop']}|{r['outer']}|{r['n']}": r["proposals"] / r["cpu_seconds"] for r in c["rows"]}
    json.dump(rate, open(out, "w"), indent=0)
    v = sorted(rate.values()); print("settings", len(v), "proposals per CPU-s: min", round(v[0]), "median", round(v[len(v) // 2]), "max", round(v[-1]))


if __name__ == "__main__":
    cmd, a = sys.argv[1], sys.argv[2:]
    {"export": export, "settings": settings, "test": test, "run": run, "collect": collect, "throughput": throughput}[cmd](*a)
