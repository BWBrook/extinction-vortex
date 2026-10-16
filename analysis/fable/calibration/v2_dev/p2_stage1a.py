"""Stage 1a: capped informative-sampler pilot for kunanyi (notes/astra_p1_and_repairs_review_20261015.md §4).
No fits, no full libraries, no empirical test. Sampler law as in p1_sampler.py (tested there): theta ~ frozen prior;
accept with L(E|theta)/M_E (Poisson then binomial, independent uniforms); one null path per accepted theta; retain if
S, A and the closed C-ball hold; restart otherwise. Settings: 9 populations x b1/b3/b5/b16 x trial IDs 0-9 x n in
{30, 300} noisy (720) plus one n = 0 control per population-outer pair (360).
Repairs required before scale (Astra 1657): actual imported-source and exported-input hashes bound and recorded in
every result; mask/MAD/query/radius exported once (workers never load a bank); atomic per-batch checkpoints with
deterministic resume and explicit complete/censored/failed states; a hard wall deadline; admissible-evidence checks
(n = 0 implies k = r = 0); exact coordinate equality when the radius is zero; exposure counts only simulated batches
(no path cap truncation). Scale repairs after the kunanyi smoke: checkpoints (hit records, then state) at most every
CKPT_SECS rather than every batch; a setting stops at the first batch boundary with at least HIT_STOP retained hits
(the declared storage limit; the batch that crosses it is kept whole). Pre-dispatch repairs (Astra 1698): a zero
checkpoint opens every setting, each checkpoint records the committed journal's length and SHA-256, recovery verifies
that prefix and replaces the file atomically (missing, short, altered or orphan journals are rejected); the collector
validates checkpoints, hit records and worker receipts and always publishes a current summary; a bound preflight
precedes any qsub. Run from the frozen source root.
  export   MANIFEST BASE S0_INPUTS S0_FULLDIR OUT_METRIC           (deep-server; loads each bank once)
  settings METRIC OUT_SETTINGS PROPOSALS_INFO PROPOSALS_N0 BATCH NWORKERS HIT_STOP [THROUGHPUT_JSON SECONDS_INFO SECONDS_N0]
           bind settings, budgets (fixed proposals, or seconds x measured smoke throughput per setting), LPT worker assignment
  test     METRIC                                                  guard, recovery and collector fixtures (exit non-zero on failure)
  preflight SETTINGS METRIC NJOBS JOBCPUS WALL_SECS CEILING_CPUH PRIOR_CPUH COLLECTOR_CPUH   bound check, shape, budget, fixtures
  run      SETTINGS METRIC OUTDIR WORKER NWORKERS DEADLINE_EPOCH  one worker; resumable
  collect  SETTINGS METRIC OUTDIR OUT_JSON
  throughput COLLECT_JSON OUT_JSON                             per-setting proposals per CPU-second from a smoke collect
"""
import contextlib, hashlib, io, json, math, os, platform, resource, shutil, sys, tempfile, time
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
CKPT_SECS = 60.0
DEADLINE_MARGIN = 600                       # s1a_node.pbs stops workers starting batches 10 minutes before the walltime
PREFIX_BATCHES = 5                          # the smoke's 100,000 proposals: the recomputed prefix of every final stream
COUNTERS = ("proposals", "poisson_accept", "theta_accept", "paths", "selected_SA", "overflow", "hits", "boundary",
            "hits_lo", "hits_hi", "rounding_excess")
HIT_KEYS = {"batch", "proposal_in_batch", "boundary", "theta", "recorded"}
EMPTY_SHA = hashlib.sha256(b"").hexdigest()
REPORT_RULE = ("Full-stream hits/proposals per setting is descriptive. Formal 95% retention intervals condition on the "
               "recomputed smoke prefix (batches 0-4, h0 hits) and use only later proposals: a setting ending at its "
               "proposal budget gets Clopper-Pearson on (suffix hits, suffix proposals); a setting ending at the hit "
               "stop gets the exact negative-binomial interval from n*, the suffix position of its (HIT_STOP - h0)-th "
               "suffix hit: [BetaInv(0.025; c, n*-c+1), BetaInv(0.975; c, n*-c)], c = HIT_STOP - h0. Together these "
               "are exact for each setting's declared curtailed design (outcomes ordered by n* when stopped, else by "
               "suffix hits); no coverage is claimed conditional on the subset of settings that completed. Censored, "
               "failed or interrupted settings get no formal interval: a Clopper-Pearson sensitivity interval on their "
               "committed suffix, labelled as assuming non-informative censoring. Time: observed CPU through the "
               "crossing batch for hit-stopped settings; "
               "rate-based projections to 2,000 for the others, labelled projections; zero hits give an upper "
               "retention bound and an unresolved cost. All 1,080 rows and complete-nine-population availability are "
               "reported.")


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


def settings(metric_path, out, prop_info, prop_n0, batch, nworkers, hit_stop, throughput=None, sec_info=None, sec_n0=None):
    metric = json.load(open(metric_path))
    prop_info, prop_n0, batch, nworkers, hit_stop = int(prop_info), int(prop_n0), int(batch), int(nworkers), int(hit_stop)
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
         "batch": batch, "nworkers": nworkers, "hit_stop": hit_stop, "checkpoint_seconds": CKPT_SECS,
         "prefix_batches": PREFIX_BATCHES, "report_rule": REPORT_RULE,
         "throughput_sha256": sha(throughput) if throughput else None,
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
    rng = np.random.default_rng([ROOT, st.get("stream_tag", 2), st["index"], bi])     # tag 3: Stage 1b check libraries
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


def journal_prefix(hits_p, S):
    """The committed hit-journal bytes, verified against the checkpoint (length, SHA-256, record count)."""
    n = S["journal_bytes"]; data = b""
    if n:
        if not os.path.exists(hits_p):
            raise SystemExit(f"setting {S['index']}: committed hit journal missing ({n} bytes expected)")
        with open(hits_p, "rb") as fh:
            data = fh.read(n)
        if len(data) < n:
            raise SystemExit(f"setting {S['index']}: committed hit journal short ({len(data)} of {n} bytes)")
    if hashlib.sha256(data).hexdigest() != S["journal_sha256"] or data.count(b"\n") != S["hits"]:
        raise SystemExit(f"setting {S['index']}: committed hit journal differs from its checkpoint")
    return data


def replace_bytes(path, data):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".tmp_")
    with os.fdopen(fd, "wb") as fh:
        fh.write(data)
        fh.flush(); os.fsync(fh.fileno())
    os.replace(tmp, path)


def run_setting(b, st, mp, outdir, deadline, des, ckpt_secs=CKPT_SECS, first_batch=0, name=None, cancelled=None):
    """One setting (or, for Stage 1b, one shard: st["batches"] batches from first_batch, files named by name), resumable.
    Commit order: hit records (append, fsync), then the checkpoint recording the journal's committed length and SHA-256.
    A fresh setting first writes a zero checkpoint, so every later journal byte is either committed or an uncommitted
    tail; recovery verifies the committed prefix and replaces the file with it atomically. cancelled() is polled at the
    start and at each commit; when true the run commits and ends as "cancelled"."""
    name = name or f"s{st['index']:04d}"
    ck = os.path.join(outdir, f"{name}.json"); hits_p = os.path.join(outdir, f"{name}_hits.jsonl")
    keys = COUNTERS
    if os.path.exists(ck):
        try:
            S = json.load(open(ck))
        except ValueError as e:
            raise SystemExit(f"setting {st['index']}: unreadable checkpoint ({e})")
        if S.get("binding") != b["_binding"] or S.get("index") != st["index"] or S.get("first_batch", 0) != first_batch:
            raise SystemExit(f"setting {st['index']}: checkpoint bound to other inputs")
        data = journal_prefix(hits_p, S)
        size = os.path.getsize(hits_p) if os.path.exists(hits_p) else 0
        if S["status"] in ("complete", "failed", "cancelled"):
            if size != len(data):
                raise SystemExit(f"setting {st['index']}: terminal checkpoint with {size - len(data)} uncommitted journal bytes")
            return S
        if size != len(data):
            replace_bytes(hits_p, data)
    else:
        if os.path.exists(hits_p):
            raise SystemExit(f"setting {st['index']}: hit journal without a checkpoint")
        S = {"index": st["index"], "binding": b["_binding"], "batches_done": 0, "status": "running", "cpu_seconds": 0.0,
             "wall_seconds": 0.0, "journal_bytes": 0, "journal_sha256": EMPTY_SHA, **{k: 0 for k in keys}}
        if first_batch:
            S["first_batch"] = first_batch
        atomic_json(S, ck)
        data = b""
    jh, pending, last = hashlib.sha256(data), [], time.time()

    def commit(status):
        if pending:
            blob = "".join(json.dumps(h) + "\n" for h in pending).encode()
            with open(hits_p, "ab") as fh:
                fh.write(blob)
                fh.flush(); os.fsync(fh.fileno())
            jh.update(blob); S["journal_bytes"] += len(blob); S["journal_sha256"] = jh.hexdigest()
            pending.clear()
        S["status"] = status; atomic_json(S, ck)

    if cancelled and cancelled():
        commit("cancelled"); return S
    while S["batches_done"] < st["batches"] and S["hits"] < b["hit_stop"]:
        if time.time() > deadline:
            commit("censored"); return S
        t0, c0 = time.time(), time.process_time()
        bi = first_batch + S["batches_done"]
        B = min(b["batch"], st["proposal_budget"] - bi * b["batch"])
        try:
            r = one_batch(st, mp, bi, B, des)
        except RuntimeError as e:
            S["failure"] = str(e); commit("failed"); return S
        pending.extend(r["hit_records"])
        for k in keys:
            S[k] += r[k]
        S["batches_done"] += 1
        S["cpu_seconds"] += time.process_time() - c0; S["wall_seconds"] += time.time() - t0
        if time.time() - last >= ckpt_secs:
            if cancelled and cancelled():
                commit("cancelled"); return S
            commit("running"); last = time.time()
    S["stop"] = "hits" if S["hits"] >= b["hit_stop"] else "budget"
    commit("complete")
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
    """Fixtures (exit non-zero on any failure): evidence and radius guards; real-stream resume, cadence and hit stop;
    injected crashes at every state write and during recovery; rejected short/missing/altered/orphan journals and
    terminal states; deadline and bound-failure states; collector validation."""
    from unittest import mock
    me = sys.modules[__name__]
    metric = json.load(open(metric_path)); des = designs(); res = {}
    for bad in ({"n": 0, "k": 1, "r": 0}, {"n": 30, "k": 31, "r": 0}, {"n": 30, "k": 3, "r": -1}, {"n": 30, "k": 3.5, "r": 2},
                {"n": 30, "k": float("nan"), "r": 1}, {"n": -1, "k": 0, "r": 0}):
        try:
            validate_E(bad); res[f"rejects_{bad}"] = False
        except SystemExit:
            res[f"rejects_{bad}"] = True
    q = np.array([1.0, 2.0])
    r0 = in_ball(np.array([[1.0, 2.0], [1.0, np.nextafter(2.0, 3.0)], [1.0, 2.1]]), q, 0.0)   # adjacent float is not equal
    res["radius_zero_exact_equality"] = r0["in"].tolist() == [True, False, False]
    tmp = []

    def fresh():
        tmp.append(tempfile.mkdtemp()); return tmp[-1]

    def journal(d, i):
        p = os.path.join(d, f"s{i:04d}_hits.jsonl")
        return open(p, "rb").read() if os.path.exists(p) else b""

    keys = ("proposals", "theta_accept", "paths", "selected_SA", "hits", "boundary")
    try:
        # real streams: hawaiian crow, null_low_s/0, n = 30, two batches
        st = {"index": 9999, "pop": "hawaiian_crow", "outer": "null_low_s/0", "n": 30,
              "E": metric["E"]["hawaiian_crow|null_low_s/0|30"], "proposal_budget": 40_000, "batches": 2}
        mp = dict(metric["outers"]["hawaiian_crow|null_low_s/0"], keep=metric["pops"]["hawaiian_crow"]["keep"],
                  mad=metric["pops"]["hawaiian_crow"]["mad"])
        b = {"batch": 20_000, "hit_stop": 10 ** 9, "_binding": {"fixture": True}}
        d1, d2, d3 = fresh(), fresh(), fresh()
        full = run_setting(b, st, mp, d1, float("inf"), des)
        part = run_setting(b, dict(st, batches=1), mp, d2, float("inf"), des)          # one batch, then "killed"
        S = json.load(open(os.path.join(d2, "s9999.json"))); S["status"] = "running"; atomic_json(S, os.path.join(d2, "s9999.json"))
        resumed = run_setting(b, st, mp, d2, float("inf"), des)
        res["resume_deterministic"] = all(full[k] == resumed[k] for k in keys) and resumed["batches_done"] == 2 \
            and journal(d1, 9999) == journal(d2, 9999)
        every = run_setting(b, st, mp, d3, float("inf"), des, ckpt_secs=0.0)
        res["checkpoint_cadence_invariant"] = all(full[k] == every[k] for k in keys) and every["status"] == "complete"
        # smoke setting 775 (crow, null_low_s/8, n = 30) has its first hits in batches 1 and 2 on both machines
        st775 = {"index": 775, "pop": "hawaiian_crow", "outer": "null_low_s/8", "n": 30,
                 "E": metric["E"]["hawaiian_crow|null_low_s/8|30"], "proposal_budget": 100_000, "batches": 5}
        mp775 = dict(metric["outers"]["hawaiian_crow|null_low_s/8"], keep=metric["pops"]["hawaiian_crow"]["keep"],
                     mad=metric["pops"]["hawaiian_crow"]["mad"])
        h1 = run_setting(dict(b, hit_stop=1), st775, mp775, d1, float("inf"), des)
        res["hit_stop_at_batch_boundary"] = (h1["status"], h1["stop"], h1["batches_done"], h1["hits"]) == ("complete", "hits", 2, 1)
        censored = run_setting(b, dict(st, index=9998), mp, d1, time.time() - 1, des)
        res["deadline_censors_without_exposure"] = censored["status"] == "censored" and censored["proposals"] == 0

        # injected faults on a synthetic batch with two identifiable hits per batch
        ckeys = keys + ("poisson_accept", "overflow", "hits_lo", "hits_hi", "rounding_excess", "batches_done", "status",
                        "journal_bytes", "journal_sha256")

        def fake(st, mp, bi, B, des):
            r = {k: 0 for k in ("poisson_accept", "overflow", "rounding_excess")}
            r.update(proposals=B, poisson_accept=B, theta_accept=B, paths=B, selected_SA=2, hits=2, boundary=0, hits_lo=2, hits_hi=2)
            r["hit_records"] = [{"batch": bi, "proposal_in_batch": j, "boundary": False, "theta": {k: 0.5 for k in PARAMS},
                                 "recorded": [4, 3, 0]} for j in (1, 3)]
            return r
        fb = {"batch": 10, "hit_stop": 99, "_binding": {"fixture": "faults"}}
        fst = {"index": 7, "pop": "synthetic", "outer": "toy/0", "n": 0, "E": {"n": 0, "k": 0, "r": 0}, "proposal_budget": 30, "batches": 3}

        def go(d, **kw):
            return run_setting(kw.get("b", fb), kw.get("st", fst), {}, d, kw.get("deadline", float("inf")), {},
                               ckpt_secs=kw.get("cadence", 0.0))

        def view(d, S):
            return ({k: S.get(k) for k in ckeys}, journal(d, 7))

        def killed_after_first_batch(d):
            def kill(st, mp, bi, B, des):
                if bi == 1:
                    raise KeyboardInterrupt("killed before batch 1")
                return fake(st, mp, bi, B, des)
            with mock.patch.object(me, "one_batch", kill):
                try:
                    go(d)
                except KeyboardInterrupt:
                    pass
        with mock.patch.object(me, "one_batch", fake):
            d = fresh(); ref = view(d, go(d))
            res["fault_reference"] = {"hits": ref[0]["hits"], "journal_lines": ref[1].count(b"\n")}
            orig_json, orig_replace = atomic_json, os.replace
            for n in (1, 2, 3, 4):        # state write n: 1 is the zero checkpoint; 2 follows the first hit fsync
                d = fresh(); calls = [0]

                def crash(obj, path, n=n):
                    calls[0] += 1
                    if calls[0] == n:
                        raise KeyboardInterrupt(f"killed at state write {n}")
                    orig_json(obj, path)
                with mock.patch.object(me, "atomic_json", crash):
                    try:
                        go(d)
                    except KeyboardInterrupt:
                        pass
                res[f"crash_at_state_write_{n}_recovers"] = view(d, go(d)) == ref
            d = fresh(); killed_after_first_batch(d)
            with open(os.path.join(d, "s0007_hits.jsonl"), "a") as fh:
                fh.write('{"batch": 1, "proposal_in_batch": 1, "partial')                 # uncommitted, torn tail

            def crash_replace(src, dst):
                if dst.endswith("_hits.jsonl"):
                    raise KeyboardInterrupt("killed while replacing the journal")
                orig_replace(src, dst)
            with mock.patch.object(os, "replace", crash_replace):
                try:
                    go(d)
                except KeyboardInterrupt:
                    pass
            res["crash_during_recovery_recovers"] = view(d, go(d)) == ref
            for kind in ("short", "missing", "altered", "orphan", "terminal_tail", "terminal_missing", "corrupt_checkpoint"):
                d = fresh(); hp, ckp = os.path.join(d, "s0007_hits.jsonl"), os.path.join(d, "s0007.json")
                if kind.startswith("terminal"):
                    go(d)
                elif kind != "orphan":
                    killed_after_first_batch(d)
                if kind == "short":
                    blob = open(hp, "rb").read().splitlines(True)[0]; open(hp, "wb").write(blob)
                elif kind in ("missing", "terminal_missing"):
                    os.unlink(hp)
                elif kind == "altered":
                    blob = open(hp, "rb").read().replace(b'"proposal_in_batch": 1', b'"proposal_in_batch": 2', 1)
                    open(hp, "wb").write(blob)
                elif kind == "orphan":
                    open(hp, "w").write(json.dumps(fake(fst, {}, 0, 10, {})["hit_records"][0]) + "\n")
                elif kind == "terminal_tail":
                    open(hp, "a").write('{"batch": 9}\n')
                elif kind == "corrupt_checkpoint":
                    open(ckp, "w").write('{"broken"')
                try:
                    go(d); res[f"rejects_{kind}"] = False
                except SystemExit:
                    res[f"rejects_{kind}"] = True
            d = fresh(); clock = [0.0]

            def timed(*a):
                r = fake(*a); clock[0] += 1.0; return r
            with mock.patch.object(time, "time", lambda: clock[0]), mock.patch.object(me, "one_batch", timed):
                S = go(d, deadline=0.5, cadence=60.0)
            res["deadline_commits_completed_batch"] = (S["status"], S["batches_done"], S["hits"], journal(d, 7).count(b"\n")) \
                == ("censored", 1, 2, 2)
            d = fresh(); S = go(d, b=dict(fb, hit_stop=3), st=dict(fst, batches=10, proposal_budget=100), cadence=60.0)
            res["hit_stop_keeps_crossing_batch"] = (S["hits"], S["batches_done"], S["stop"], S["proposals"]) == (4, 2, "hits", 20)
            d = fresh()
            with mock.patch.object(me, "one_batch", side_effect=RuntimeError("bound violation (injected)")):
                S = go(d)
            res["bound_failure_is_failed_state"] = S["status"] == "failed" and S["proposals"] == 0

            # collector: valid, malformed, duplicated, stale-worker and corrupt cases against bound fixture inputs
            def collect_case(kind):
                d = fresh(); setp, metp, out = os.path.join(d, "settings.json"), os.path.join(d, "metric.json"), os.path.join(d, "collect.json")
                rd = os.path.join(d, "run"); os.makedirs(rd)
                json.dump({"outers": {"synthetic|toy/0": {"recorded": [5, 4, 0]}}}, open(metp, "w"))
                sts = [dict(fst, index=0, worker=0), dict(fst, index=1, worker=1)]
                json.dump({"metric_sha256": sha(metp), "runner_sha256": "fixture", "batch": 10, "nworkers": 2, "hit_stop": 99,
                           "prefix_batches": 1, "allowed_runtimes": [runtime()], "settings": sts}, open(setp, "w"))
                bind = {"settings_sha256": sha(setp), "metric_sha256": sha(metp), "runner_sha256": "fixture"}
                run_setting(dict(fb, _binding=bind), sts[0], {}, rd, float("inf"), {}, ckpt_secs=0.0)
                receipt = {"worker": 0, "nworkers": 2, "binding": bind, "runtime": runtime(), "host": "fixture", "peak_rss_gib": 0.01}
                atomic_json(receipt, os.path.join(rd, "worker0000.json"))
                if kind == "bad_type_then_valid":
                    run_setting(dict(fb, _binding=bind), sts[1], {}, rd, float("inf"), {}, ckpt_secs=0.0)
                    S = json.load(open(os.path.join(rd, "s0000.json"))); S["batches_done"] = "3"; atomic_json(S, os.path.join(rd, "s0000.json"))
                elif kind == "negative_fields":
                    S = json.load(open(os.path.join(rd, "s0000.json"))); S.update(overflow=-7, rounding_excess=-9, cpu_seconds=-1.0)
                    atomic_json(S, os.path.join(rd, "s0000.json"))
                elif kind == "bad_provenance":
                    atomic_json(receipt | {"runtime": {"python": "0", "numpy": "0", "scipy": "0"}}, os.path.join(rd, "worker0000.json"))
                hp = os.path.join(rd, "s0000_hits.jsonl")
                if kind == "malformed":
                    blob = open(hp, "rb").read(); lines = blob.splitlines(True)
                    bad = b"x" * (len(lines[0]) - 1) + b"\n"
                    blob = bad + b"".join(lines[1:]); open(hp, "wb").write(blob)
                    S = json.load(open(os.path.join(rd, "s0000.json"))); S["journal_sha256"] = hashlib.sha256(blob).hexdigest()
                    atomic_json(S, os.path.join(rd, "s0000.json"))
                elif kind == "stale_worker":
                    atomic_json({"worker": 9999, "nworkers": 99999, "binding": {"stale": True}}, os.path.join(rd, "worker9999.json"))
                elif kind == "invariant":
                    S = json.load(open(os.path.join(rd, "s0000.json"))); S["paths"] += 1; atomic_json(S, os.path.join(rd, "s0000.json"))
                elif kind == "corrupt_with_old_summary":
                    open(out, "w").write('{"collection_ok": true, "stale": true}')
                    open(os.path.join(rd, "s0000.json"), "w").write('{"broken"')
                try:
                    collect(setp, metp, rd, out); ok = True
                except SystemExit:
                    ok = False
                return ok, json.load(open(out))
            with contextlib.redirect_stdout(io.StringIO()):
                ok, c = collect_case("valid")
                res["collect_valid_with_missing_setting_and_worker"] = ok and c["collection_ok"] and not c["run_complete"] \
                    and c["status"]["missing"] == 1 and len(c["rows"]) == 2 and c["workers_missing"] == [1] \
                    and not c["provenance_complete"]
                for kind in ("malformed", "stale_worker", "invariant", "corrupt_with_old_summary", "negative_fields", "bad_provenance"):
                    ok, c = collect_case(kind)
                    res[f"collect_rejects_{kind}"] = not ok and not c["collection_ok"] and "stale" not in c and bool(c["errors"])
                ok, c = collect_case("bad_type_then_valid")
                res["collect_isolates_bad_type_row"] = not ok and [r["status"] for r in c["rows"]] == ["invalid", "complete"] \
                    and c["status"]["invalid"] == 1 and c["status"]["complete"] == 1
    finally:
        for d in tmp:
            shutil.rmtree(d, ignore_errors=True)
    res["all_ok"] = all(v for k, v in res.items() if k != "fault_reference")
    print(json.dumps(res, indent=1))
    if not res["all_ok"]:
        raise SystemExit("tests failed")


def check_setting(st, b, binding, metric, outdir):
    """One setting's row and its consistency errors (checkpoint, counters, terminal state, journal and hit records)."""
    from scipy.stats import beta as beta_dist
    i, B, cap, pre = st["index"], b["batch"], b["hit_stop"], b["prefix_batches"]
    ck, hp = os.path.join(outdir, f"s{i:04d}.json"), os.path.join(outdir, f"s{i:04d}_hits.jsonl")
    row = {k: st[k] for k in ("index", "pop", "outer", "n", "proposal_budget", "worker")}
    errs = []
    if not os.path.exists(ck):
        return row | {"status": "missing"}, errs
    try:
        S = json.load(open(ck))
        assert isinstance(S, dict)
    except (ValueError, AssertionError) as e:
        return row | {"status": "invalid"}, [f"setting {i}: unreadable checkpoint ({e})"]
    need = ("binding", "index", "status", "batches_done", "cpu_seconds", "wall_seconds", "journal_bytes", "journal_sha256") + COUNTERS
    if any(k not in S for k in need):
        return row | {"status": "invalid"}, [f"setting {i}: checkpoint lacks {[k for k in need if k not in S]}"]
    bad = [k for k in ("index", "batches_done", "journal_bytes") + COUNTERS if type(S[k]) is not int or S[k] < 0]
    bad += [k for k in ("cpu_seconds", "wall_seconds") if type(S[k]) not in (int, float) or not math.isfinite(S[k]) or S[k] < 0]
    if not (isinstance(S["journal_sha256"], str) and len(S["journal_sha256"]) == 64
            and all(c in "0123456789abcdef" for c in S["journal_sha256"])):
        bad.append("journal_sha256")
    if S["status"] not in ("complete", "censored", "failed", "running"):
        bad.append("status")
    if "stop" in S and S["stop"] not in ("hits", "budget"):
        bad.append("stop")
    if bad:
        return row | {"status": "invalid"}, [f"setting {i}: checkpoint fields of wrong type or domain {bad}"]
    row |= {k: S[k] for k in S if k != "binding"}
    e = lambda m: errs.append(f"setting {i}: {m}")
    if S["binding"] != binding or S["index"] != i:
        e("checkpoint bound to other inputs")
    nb, status, stop = S["batches_done"], S["status"], S.get("stop")
    if S["proposals"] != min(nb * B, st["proposal_budget"]):
        e("proposals differ from the committed batches")
    if not (0 <= S["theta_accept"] <= S["poisson_accept"] <= S["proposals"]) or S["paths"] != S["theta_accept"] \
            or S["selected_SA"] + S["overflow"] > S["paths"] or not (S["hits_lo"] <= S["hits"] <= S["hits_hi"] <= S["selected_SA"]) \
            or not (0 <= S["boundary"] <= S["hits"]):
        e("counter invariants fail")
    if status == "complete":
        if not ((stop == "budget" and nb == st["batches"] and S["hits"] < cap) or (stop == "hits" and S["hits"] >= cap and nb <= st["batches"])):
            e("complete state without a consistent stop")
    elif status == "censored":
        if not (nb < st["batches"] and S["hits"] < cap):
            e("censored state outside its budget or past the hit stop")
    elif status == "failed":
        if not isinstance(S.get("failure"), str):
            e("failed state without a failure")
    raw = open(hp, "rb").read() if os.path.exists(hp) else b""
    n = S["journal_bytes"]; data = raw[:n]; row["uncommitted_tail_bytes"] = max(len(raw) - n, 0)
    if len(raw) < n:
        e("hit journal missing or short")
    elif status in ("complete", "failed") and len(raw) != n:
        e("uncommitted journal bytes after a terminal checkpoint")
    if hashlib.sha256(data).hexdigest() != S["journal_sha256"]:
        e("hit journal differs from its checkpoint")
    L = len(metric["outers"][f"{st['pop']}|{st['outer']}"]["recorded"])
    recs, prev = [], (-1, -1)
    for ln in data.splitlines():
        try:
            h = json.loads(ln)
        except ValueError:
            e("malformed hit record"); break
        ok = isinstance(h, dict) and set(h) == HIT_KEYS and type(h["batch"]) is int and type(h["proposal_in_batch"]) is int \
            and type(h["boundary"]) is bool and isinstance(h["theta"], dict) and set(h["theta"]) == set(PARAMS) \
            and all(type(v) is float and math.isfinite(v) for v in h["theta"].values()) and isinstance(h["recorded"], list) \
            and len(h["recorded"]) == L and all(type(x) is int for x in h["recorded"])
        if not ok:
            e("hit record schema"); break
        if not (0 <= h["batch"] < nb and 0 <= h["proposal_in_batch"] < min(B, st["proposal_budget"] - h["batch"] * B)):
            e("hit identity outside the committed batches"); break
        if (h["batch"], h["proposal_in_batch"]) <= prev:
            e("hit identities duplicated or out of order"); break
        if not (all(x > 1 for x in h["recorded"][1:-1]) and h["recorded"][-1] <= 1):
            e("hit record fails selection S"); break
        prev = (h["batch"], h["proposal_in_batch"]); recs.append(h)
    else:
        if len(recs) != S["hits"] or sum(h["boundary"] for h in recs) != S["boundary"]:
            e("hit records differ from the checkpoint counts")
    if errs:
        return row, errs
    pre_n = min(pre * B, S["proposals"]); suf = [h for h in recs if h["batch"] >= pre]
    h0, sn, sh = S["hits"] - len(suf), S["proposals"] - pre_n, len(suf)
    row |= {"prefix_hits": h0, "prefix_proposals": pre_n, "suffix_hits": sh, "suffix_proposals": sn,
            "retention_per_proposal": S["hits"] / S["proposals"] if S["proposals"] else None,      # full stream: descriptive
            "zero_hit_upper95": 3.0 / S["proposals"] if S["proposals"] and not S["hits"] else None}
    cpp = S["cpu_seconds"] / S["proposals"] if S["proposals"] else None
    if status == "complete" and stop == "hits" and cap - h0 >= 1:
        c = cap - h0; kth = suf[c - 1]; nstar = kth["batch"] * B + kth["proposal_in_batch"] + 1 - pre_n
        row |= {"suffix_proposals_to_cap": nstar, "observed_cpu_hours_to_crossing_batch": S["cpu_seconds"] / 3600,
                "ci95_suffix": [float(beta_dist.ppf(0.025, c, nstar - c + 1)),
                                float(beta_dist.ppf(0.975, c, nstar - c)) if nstar > c else 1.0],
                "ci_method": "exact negative binomial (stopped at the hit cap)"}
    elif sn:
        cp = [float(beta_dist.ppf(0.025, sh, sn - sh + 1)) if sh else 0.0,
              float(beta_dist.ppf(0.975, sh + 1, sn - sh)) if sh < sn else 1.0]
        row |= ({"ci95_suffix": cp, "ci_method": "Clopper-Pearson (ended at its proposal budget)"} if status == "complete" else
                {"sensitivity_interval95_suffix": cp,
                 "sensitivity_note": "not a formal interval: assumes the censoring, failure or interruption is non-informative"})
        row["projected_cpu_hours_to_2000"] = cap / (S["hits"] / S["proposals"]) * cpp / 3600 if S["hits"] else None
    return row, errs


def collect(settings_path, metric_path, outdir, out):
    """Validate every checkpoint, journal and worker receipt against the bound settings and publish a current summary
    atomically. An in-progress failure summary is written first, so no earlier summary survives a crash or abort.
    collection_ok: every present result is consistent; run_complete: also every setting is complete."""
    atomic_json({"collection_ok": False, "run_complete": False, "state": "collecting"}, out)
    errors, rows, workers, binding, missing_workers = [], [], [], None, None
    status = {"complete": 0, "censored": 0, "failed": 0, "running": 0, "missing": 0, "invalid": 0}
    try:
        b = json.load(open(settings_path))
        binding = {"settings_sha256": sha(settings_path), "metric_sha256": b["metric_sha256"], "runner_sha256": b["runner_sha256"]}
        if sha(metric_path) != b["metric_sha256"]:
            errors.append("metric differs from the bound settings")
        metric = json.load(open(metric_path))
        for st in b["settings"]:
            try:
                row, errs = check_setting(st, b, binding, metric, outdir)
            except Exception as ex:                    # one bad setting never hides the others
                row = {k: st.get(k) for k in ("index", "pop", "outer", "n", "proposal_budget", "worker")}
                errs = [f"setting {st.get('index')}: unexpected {type(ex).__name__}: {ex}"]
            if errs:
                row = row | {"recorded_status": row.get("status"), "status": "invalid", "errors": errs}
            rows.append(row); errors += errs
            status[row["status"]] += 1
        for f in sorted(os.listdir(outdir)):
            if f.startswith("worker") and f.endswith(".json"):
                try:
                    w = json.load(open(os.path.join(outdir, f)))
                    good = w["binding"] == binding and w["nworkers"] == b["nworkers"] and type(w["worker"]) is int \
                        and 0 <= w["worker"] < b["nworkers"] and f == f"worker{w['worker']:04d}.json" \
                        and w["runtime"] in b["allowed_runtimes"] and isinstance(w["host"], str) and w["host"] \
                        and type(w["peak_rss_gib"]) in (int, float) and math.isfinite(w["peak_rss_gib"]) and w["peak_rss_gib"] >= 0
                except (ValueError, KeyError, TypeError):
                    good = False
                if good:
                    workers.append(w)
                else:
                    errors.append(f"{f}: worker receipt unreadable, bound to other inputs, out of range or with invalid provenance")
        missing_workers = sorted(set(range(b["nworkers"])) - {w["worker"] for w in workers})
    except Exception as ex:
        errors.append(f"collection aborted: {type(ex).__name__}: {ex}")
    summary = {"collection_ok": not errors, "run_complete": not errors and status["complete"] == len(rows) and bool(rows),
               "provenance_complete": not errors and missing_workers == [], "workers_missing": missing_workers,
               "n_errors": len(errors), "errors": errors[:1000], "binding": binding, "status": status, "workers": workers,
               "rows": rows}
    atomic_json(summary, out)
    print("collection_ok", summary["collection_ok"], "run_complete", summary["run_complete"],
          "provenance_complete", summary["provenance_complete"], "status", status,
          "cpu_hours", round(sum(r.get("cpu_seconds", 0) for r in rows) / 3600, 2), "hits", sum(r.get("hits", 0) for r in rows),
          "errors", len(errors))
    if errors:
        raise SystemExit(f"collection failed: {errors[0]}")


def preflight(settings_path, metric_path, njobs, jobcpus, wall_secs, ceiling_cpuh, prior_cpuh, collector_cpuh):
    """Before any qsub: the real bound check (runner, helper, imported source, metric, runtime), the dispatch shape,
    the cumulative allocated-hour ceiling, the deadline margin, then the fixtures."""
    b = check(settings_path, metric_path)
    njobs, jobcpus, wall_secs = int(njobs), int(jobcpus), int(wall_secs)
    alloc = njobs * jobcpus * wall_secs / 3600 + float(prior_cpuh) + float(collector_cpuh)
    owners = {s["worker"] for s in b["settings"]}
    errs = []
    if [s["index"] for s in b["settings"]] != list(range(len(b["settings"]))):
        errs.append("setting indices are not 0..N-1")
    if njobs * jobcpus != b["nworkers"] or owners != set(range(b["nworkers"])):
        errs.append(f"shape {njobs} x {jobcpus} does not match the {b['nworkers']} bound workers")
    if alloc > float(ceiling_cpuh):
        errs.append(f"allocation {alloc:.2f} CPU-h exceeds the {ceiling_cpuh} CPU-h ceiling")
    if b["max_worker_expected_seconds"] > wall_secs - DEADLINE_MARGIN:
        errs.append("expected worker load exceeds the worker deadline")
    print(json.dumps({"preflight": "refused" if errs else "passed", "errors": errs, "settings_sha256": sha(settings_path),
                      "runtime": runtime(), "jobs": njobs, "cpus_per_job": jobcpus, "wall_seconds": wall_secs,
                      "allocated_cpu_hours_bound": round(alloc, 3), "ceiling": float(ceiling_cpuh),
                      "deadline_margin": round(1 - b["max_worker_expected_seconds"] / (wall_secs - DEADLINE_MARGIN), 3)}))
    if errs:
        raise SystemExit("preflight refused")
    test(metric_path)


def throughput(collect_json, out):
    c = json.load(open(collect_json))
    if c["status"]["complete"] != len(c["rows"]):
        raise SystemExit(f"smoke incomplete: {c['status']}")
    rate = {f"{r['pop']}|{r['outer']}|{r['n']}": r["proposals"] / r["cpu_seconds"] for r in c["rows"]}
    json.dump(rate, open(out, "w"), indent=0)
    v = sorted(rate.values()); print("settings", len(v), "proposals per CPU-s: min", round(v[0]), "median", round(v[len(v) // 2]), "max", round(v[-1]))


if __name__ == "__main__":
    cmd, a = sys.argv[1], sys.argv[2:]
    {"export": export, "settings": settings, "test": test, "preflight": preflight, "run": run, "collect": collect,
     "throughput": throughput}[cmd](*a)
