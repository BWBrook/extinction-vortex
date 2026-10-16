"""Stage 1b: full noisy-design sampling campaign (notes/vortex_stage1b_design_20261016.md; authorised by Barry, board
1759). The sampler law, per-batch streams, recovery and hit-record format are p2_stage1a's, unchanged.
A library is the first K retained pairs of its setting in stream order (batch, proposal_in_batch). Work is split into
batch ranges ("shards") of any size; each shard is run by p2_stage1a.run_setting from its first batch, so a shard's
output depends only on (setting, range) and the library is invariant to shard boundaries, order and parallelism.
Planning (which ranges exist, how many run at once) adapts to observed rates and affects cost only.
  export        MANIFEST BASE S0_INPUTS S0_FULLDIR OUT_METRIC   p2_stage1a.export over trial IDs 0-199 (deep-server)
  verify_export METRIC P2_METRIC                                pilot pairs and their E identical to Stage 1a's
  settings      METRIC PILOT_SETTINGS PILOT_COLLECT OUT          bind 21,600 primary + 216 check settings (stable IDs)
  subset        SETTINGS OUT DIRS CAP_CPU_H TARGET_WALL_H MIN_SHARD_CPU_H   smoke settings (reduced cap and planner targets)
  seed          SETTINGS PILOT_DIR RUN WAVE                      import verified pilot prefixes; first tickets
  work          SETTINGS METRIC RUN OWNER DEADLINE_EPOCH         pull worker: claim, run, plan successors
  collect       SETTINGS METRIC RUN WAVE OUT_JSON                validate shards, assemble libraries, account CPU
  preflight     SETTINGS METRIC NJOBS JOBCPUS WALL_SECS CEILING PRIOR WAVE   bound check, ceiling, fixtures
  test                                                            synthetic fixtures (exit non-zero on failure)
Run directory RUN: queue/ (tickets), claimed/ (ticket@owner), sets/<dir>/ (pilot prefix, ranges/, shard checkpoints and
journals, COMPLETE/CAPPED/FAILED markers, lock/), lib/ (assembled libraries), workers/. Run from the frozen source root."""
import hashlib, json, math, os, random, shutil, subprocess, sys, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import p2_stage1a as p2

HERE = os.path.dirname(os.path.abspath(__file__))
TRIALS_1B = range(200)
K, BATCH = 2000, 20000
CAP_CPU_H, MIN_SHARD_CPU_H, TARGET_WALL_H, MAX_INFLIGHT, OVERSHOOT, CKPT_SECS = 2000.0, 2.0, 24.0, 28, 1.15, 300.0
PRIOR_HITS = 2.0                 # pseudo-hits of the cell's pooled pilot rate, shrinking a setting's own hit-rate estimate
DEADLINE_MARGIN = 900
COLLECTOR_CPU_H = 8.0            # s1b_collect.pbs: 1 core x 8 h walltime, charged against the wave ceiling
WAVES = {"W1": (0, 30), "W2": (300,)}
CHECK_OUTERS = {"null_prior_predictive": (7, 4), "null_low_s": (6, 4), "MA_betamin": (6, 8), "MA_d10_0.5": (6, 1)}
TERMINAL = ("COMPLETE", "CAPPED", "FAILED")


def primary_index(pi, si, t, ni):
    """Stable IDs: the pilot's 1,080 indices for trials 0-9; trials 10-199 appended from 1,080."""
    return ((pi * 4 + si) * 10 + t) * 3 + ni if t < 10 else 1080 + ((pi * 4 + si) * 190 + (t - 10)) * 3 + ni


# ---------------------------------------------------------------- export
def export(man_path, base, s0_inputs, s0_full, out):
    p2.TRIALS = TRIALS_1B
    p2.export(man_path, base, s0_inputs, s0_full, out)


def verify_export(metric_path, p2_metric_path):
    m, q = json.load(open(metric_path)), json.load(open(p2_metric_path))
    bad = [k for k in q["outers"] if m["outers"].get(k) != q["outers"][k]] + [k for k in q["E"] if m["E"].get(k) != q["E"][k]]
    bad += [k for k in ("pops", "source_bank_sha256", "bank_meta_sha256", "s0_inputs_sha256") if m[k] != q[k]]
    print(json.dumps({"outers": len(m["outers"]), "E": len(m["E"]), "pilot_outers_identical": len(q["outers"]),
                      "pilot_E_identical": len(q["E"]), "mismatches": bad[:10]}))
    if bad or len(m["outers"]) != 7200 or len(m["E"]) != 14400:
        raise SystemExit("export verification failed")


# ---------------------------------------------------------------- settings
def settings(metric_path, pilot_settings_path, pilot_collect_path, out):
    metric, ps, pc = json.load(open(metric_path)), json.load(open(pilot_settings_path)), json.load(open(pilot_collect_path))
    if not pc["collection_ok"] or pc["binding"]["settings_sha256"] != p2.sha(pilot_settings_path):
        raise SystemExit("pilot collection is not ok or not bound to these pilot settings")
    prow = {r["index"]: r for r in pc["rows"]}
    rate = {i: r["proposals"] / r["cpu_seconds"] for i, r in prow.items() if r["proposals"] and r["cpu_seconds"] > 0}
    cell, cellhits = {}, {}
    for s_ in ps["settings"]:
        c_ = (s_["pop"], s_["outer"].split("/")[0], s_["n"])
        if s_["index"] in rate:
            cell.setdefault(c_, []).append(rate[s_["index"]])
        h_, n_ = cellhits.get(c_, (0, 0)); r_ = prow[s_["index"]]
        cellhits[c_] = (h_ + r_["hits"], n_ + r_["batches_done"])
    st = []
    for pi, pop in enumerate(p2.POPS):
        for si, sc in enumerate(p2.SCEN):
            for t in TRIALS_1B:
                for ni, n in enumerate((0,) + p2.NS):
                    i = primary_index(pi, si, t, ni)
                    E = {"n": 0, "k": 0, "r": 0} if n == 0 else metric["E"][f"{pop}|{sc}/{t}|{n}"]
                    p2.validate_E(E)
                    r_ = rate.get(i) if t < 10 else None
                    r_ = r_ or float(np.median(cell[(pop, sc, n)]))
                    pilot = None
                    if t < 10:
                        old = ps["settings"][i]
                        assert (old["pop"], old["outer"], old["n"]) == (pop, f"{sc}/{t}", n), "pilot index mismatch"
                        row = prow[i]
                        pilot = {k: row[k] for k in ("batches_done", "hits", "journal_bytes", "journal_sha256", "status",
                                                      "proposals", "cpu_seconds")}
                    ch, cn = cellhits[(pop, sc, n)]
                    base = {"index": i, "pop": pop, "outer": f"{sc}/{t}", "n": n, "E": E, "rate": r_,
                            "prior_hpb": ch / cn if cn else 0.0,
                            "cap_batches": int(CAP_CPU_H * 3600 * r_ // BATCH), "wave": "W1" if n in (0, 30) else "W2"}
                    st.append(base | {"dir": f"s{i:05d}", "library": "primary", "stream_tag": 2, "pilot": pilot})
                    if t == CHECK_OUTERS[sc][0] or t == CHECK_OUTERS[sc][1]:
                        st.append(base | {"dir": f"c{i:05d}", "library": "check", "stream_tag": 3, "pilot": None})
    st.sort(key=lambda x: (x["library"] != "primary", x["index"]))
    assert sorted(x["index"] for x in st if x["library"] == "primary") == list(range(21600))
    b = {"stage": "1b full noisy-design sampling (no fits)", "K": K, "batch": BATCH, "cap_cpu_h": CAP_CPU_H,
         "min_shard_cpu_h": MIN_SHARD_CPU_H, "target_wall_h": TARGET_WALL_H, "max_inflight": MAX_INFLIGHT,
         "overshoot": OVERSHOOT, "checkpoint_seconds": CKPT_SECS, "waves": WAVES, "check_outers": CHECK_OUTERS,
         "metric_sha256": p2.sha(metric_path), "runner_sha256": p2.sha(os.path.abspath(__file__)),
         "p2_sha256": p2.sha(os.path.join(HERE, "p2_stage1a.py")), "p1_sampler_sha256": p2.sha(os.path.join(HERE, "p1_sampler.py")),
         "imported_source_sha256": {f: p2.sha(f) for f in p2.IMPORTED},
         "pilot_settings_sha256": p2.sha(pilot_settings_path), "pilot_collect_sha256": p2.sha(pilot_collect_path),
         "allowed_runtimes": [{"python": "3.11.7", "numpy": "1.26.4", "scipy": "1.11.4"},
                              {"python": "3.12.3", "numpy": "1.26.4", "scipy": "1.11.4"}],
         "stream": "default_rng([20261015, stream_tag, index, batch]); tag 2 primary (pilot streams continued), tag 3 check",
         "library_rule": "first K retained pairs ordered by (batch, proposal_in_batch) within a contiguous verified prefix of "
                         "batches 0..m; holes block completion; failure to fill K by cap_batches is CAPPED",
         "settings": st}
    json.dump(b, open(out, "w"))
    print("settings", out, p2.sha(out), len(st), "primary", sum(x["library"] == "primary" for x in st),
          "check", sum(x["library"] == "check" for x in st))


def subset(settings_path, out, dirs, cap_cpu_h, target_wall_h, min_shard_cpu_h):
    """Smoke settings: selected dirs with a reduced per-setting cap and planner targets (runner and bindings unchanged)."""
    b = json.load(open(settings_path)); want = dirs.split(",")
    st = [dict(x) for x in b["settings"] if x["dir"] in want]
    if sorted(x["dir"] for x in st) != sorted(want):
        raise SystemExit("unknown dir")
    for x in st:
        x["cap_batches"] = int(float(cap_cpu_h) * 3600 * x["rate"] // BATCH)
    b.update(settings=st, cap_cpu_h=float(cap_cpu_h), target_wall_h=float(target_wall_h), min_shard_cpu_h=float(min_shard_cpu_h),
             stage=b["stage"] + " -- SMOKE SUBSET", derived_from_sha256=p2.sha(settings_path))
    json.dump(b, open(out, "w"))
    print("subset", out, p2.sha(out), len(st))


def check(settings_path, metric_path):
    b = json.load(open(settings_path))
    if b["metric_sha256"] != p2.sha(metric_path) or b["runner_sha256"] != p2.sha(os.path.abspath(__file__)) \
            or b["p2_sha256"] != p2.sha(os.path.join(HERE, "p2_stage1a.py")) \
            or b["p1_sampler_sha256"] != p2.sha(os.path.join(HERE, "p1_sampler.py")) \
            or any(p2.sha(f) != h for f, h in b["imported_source_sha256"].items()) or p2.runtime() not in b["allowed_runtimes"]:
        raise SystemExit("refused: metric, runner, helpers, imported source or runtime differ from the bound settings")
    return b


def binding(b, settings_path):
    return {"settings_sha256": p2.sha(settings_path), "metric_sha256": b["metric_sha256"], "runner_sha256": b["runner_sha256"]}


# ---------------------------------------------------------------- per-setting state
def lock(sdir, stale=600):
    d = os.path.join(sdir, "lock")
    while True:
        try:
            os.mkdir(d); return d
        except FileExistsError:
            try:
                if time.time() - os.stat(d).st_mtime > stale:
                    os.rename(d, f"{d}.stale.{os.getpid()}.{time.time_ns()}")
                    continue
            except FileNotFoundError:
                continue
            time.sleep(0.05 + random.random() * 0.1)


def unlock(d):
    os.rmdir(d)


def ranges(sdir):
    rd = os.path.join(sdir, "ranges")
    return sorted(tuple(int(x) for x in f.split("-")) for f in os.listdir(rd)) if os.path.isdir(rd) else []


def shard_state(sdir, a):
    p = os.path.join(sdir, f"sh{a:09d}.json")
    return json.load(open(p)) if os.path.exists(p) else None


def prefix(st, sdir):
    """Contiguous verified prefix: (end batch, hits, crossing, rows). crossing = (range start, stop batch) when K is reached."""
    pl = st["pilot"]
    end, h = (pl["batches_done"], pl["hits"]) if pl else (0, 0)
    rows = []
    if h >= K:
        return end, h, ("pilot", end), rows
    for a, b_ in ranges(sdir):
        if a != end:
            break
        S = shard_state(sdir, a)
        if not S or S["status"] != "complete":
            break
        stop_end = a + S["batches_done"]
        rows.append((a, S)); h += S["hits"]
        if h >= K:
            return stop_end, h, (a, stop_end), rows
        end = b_
    return end, h, None, rows


def terminal(sdir):
    for m in TERMINAL:
        if os.path.exists(os.path.join(sdir, m)):
            return m
    return None


def mark(sdir, m, info):
    fd = os.open(os.path.join(sdir, m), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    with os.fdopen(fd, "w") as fh:
        json.dump(info, fh)
        fh.flush(); os.fsync(fh.fileno())


def ticket_name(st, a, b_, prio):
    return f"{st['wave']}_{prio:07d}_{st['dir']}_{a:09d}_{b_:09d}"


def plan(st, sdir, run, b):
    """Under the setting lock: set a terminal marker, or create successor ranges (marker, then ticket)."""
    if terminal(sdir):
        return
    rs = ranges(sdir)
    for a, _ in rs:
        S = shard_state(sdir, a)
        if S and S["status"] == "failed":
            mark(sdir, "FAILED", {"range": a, "failure": S.get("failure")}); return
    end, h, crossing, _ = prefix(st, sdir)
    if crossing:
        mark(sdir, "COMPLETE", {"end_batch": end, "hits": h, "crossing": crossing}); return
    cap = st["cap_batches"]
    if end >= cap:
        mark(sdir, "CAPPED", {"end_batch": end, "hits": h}); return
    pl = st["pilot"]
    H = (pl["hits"] if pl else 0); N = (pl["batches_done"] if pl else 0); C = (pl["cpu_seconds"] if pl else 0.0)
    inflight, inflight_left = 0, 0
    for a, b_ in rs:
        S = shard_state(sdir, a)
        done = S["batches_done"] if S else 0
        if S and S["status"] == "complete":
            H += S["hits"]; N += done; C += S["cpu_seconds"]
        else:
            inflight += 1; inflight_left += (b_ - a) - done
            if S:
                H += S["hits"]; N += done; C += S["cpu_seconds"]
    mins, tw, mi, ov = b["min_shard_cpu_h"], b["target_wall_h"], b["max_inflight"], b["overshoot"]   # bound planner
    cpb = C / N / 3600 if N and C > 0 else BATCH / st["rate"] / 3600              # CPU-h per batch
    ph = st.get("prior_hpb", 0.0)                                                 # cell prior, PRIOR_HITS pseudo-hits
    hpb = (H + PRIOR_HITS) / (N + PRIOR_HITS / ph) if ph > 0 else (H / N if N else 0.0)
    cursor = max([b_ for _, b_ in rs] + [pl["batches_done"] if pl else 0])
    exp_hits = H + hpb * inflight_left
    need = cap if hpb == 0 else min(cap, cursor + max(0, math.ceil((K - exp_hits) / hpb * ov)))
    new_h = max(0, need - cursor) * cpb
    F = min(mi, max(1, math.ceil((new_h + inflight_left * cpb) / tw)))
    slots = F - inflight
    if (slots <= 0 or need <= cursor) and inflight == 0 and cursor < cap:
        need, slots = min(cap, cursor + max(1, math.ceil(mins / cpb))), 1
    if slots <= 0 or need <= cursor:
        return
    size = max(math.ceil(mins / cpb), math.ceil((need - cursor) / slots))
    prio = max(0, 9_999_999 - int(min(9_999_999, (need - cursor) * cpb * 100)))
    os.makedirs(os.path.join(sdir, "ranges"), exist_ok=True)
    a = cursor
    while slots > 0 and a < need:
        b_ = min(cap, a + size)
        fd = os.open(os.path.join(sdir, "ranges", f"{a:09d}-{b_:09d}"), os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.close(fd)
        open(os.path.join(run, "queue", ticket_name(st, a, b_, prio)), "w").close()
        a, slots = b_, slots - 1


# ---------------------------------------------------------------- seed (pilot prefix import)
def seed(settings_path, pilot_dir, run, wave):
    b = json.load(open(settings_path))
    for d in ("queue", "claimed", "sets", "lib", "workers"):
        os.makedirs(os.path.join(run, d), exist_ok=True)
    n = {"imported": 0, "complete_at_seed": 0, "planned": 0}
    for st in b["settings"]:
        if st["wave"] != wave:
            continue
        sdir = os.path.join(run, "sets", st["dir"]); os.makedirs(sdir, exist_ok=True)
        pl = st["pilot"]
        if pl and not os.path.exists(os.path.join(sdir, "pilot.json")):
            name = os.path.join(pilot_dir, f"s{st['index']:04d}")
            S = json.load(open(name + ".json"))
            data = open(name + "_hits.jsonl", "rb").read()[:pl["journal_bytes"]] if pl["journal_bytes"] else b""
            if {k: S[k] for k in pl} != pl or hashlib.sha256(data).hexdigest() != pl["journal_sha256"]:
                raise SystemExit(f"{st['dir']}: pilot checkpoint or journal differs from the bound pilot collection")
            p2.replace_bytes(os.path.join(sdir, "pilot_hits.jsonl"), data)
            p2.atomic_json(S, os.path.join(sdir, "pilot.json")); n["imported"] += 1
        L = lock(sdir)
        try:
            plan(st, sdir, run, b)
        finally:
            unlock(L)
        n["complete_at_seed" if terminal(sdir) == "COMPLETE" else "planned"] += 1
    print("seed", wave, n)


# ---------------------------------------------------------------- worker
def claim(run, owner):
    q = os.path.join(run, "queue")
    for _ in range(3):
        names = sorted(os.listdir(q))
        if not names:
            return None
        head = names[:32]; random.shuffle(head)
        for t in head:
            try:
                os.rename(os.path.join(q, t), os.path.join(run, "claimed", f"{t}@{owner}"))
                return t
            except FileNotFoundError:
                continue
    return None


def recover_stale(run, owner, qstat="/opt/pbs/bin/qstat"):
    """Requeue claims whose owning PBS job is positively finished (job_state F)."""
    me = owner.rsplit(".", 1)[0]; seen, n = {}, 0
    for c in os.listdir(os.path.join(run, "claimed")):
        t, own = c.split("@", 1); job = own.rsplit(".", 1)[0]
        if job == me:
            continue
        if job not in seen:
            try:
                out = subprocess.run([qstat, "-x", "-f", job], capture_output=True, text=True, timeout=60).stdout
                seen[job] = any(l.strip() == "job_state = F" for l in out.splitlines())
            except Exception:
                seen[job] = False
        if seen[job]:
            try:
                os.rename(os.path.join(run, "claimed", c), os.path.join(run, "queue", t)); n += 1
            except FileNotFoundError:
                pass
    return n


def work(settings_path, metric_path, run, owner, deadline, qstat="/opt/pbs/bin/qstat", des=None):
    b = check(settings_path, metric_path) if des is None else json.load(open(settings_path))
    metric = json.load(open(metric_path)); des = des if des is not None else p2.designs()
    bind = binding(b, settings_path); by_dir = {s["dir"]: s for s in b["settings"]}
    deadline = float(deadline); done = {"shards": 0, "discarded_tickets": 0, "requeued_censored": 0, "stale_requeued": 0}
    while time.time() < deadline:
        t = claim(run, owner)
        if t is None:
            done["stale_requeued"] += recover_stale(run, owner, qstat)
            t = claim(run, owner)
            if t is None:
                break
        wave, prio, d, a, b_ = t.split("_")[0], t.split("_")[1], t.split("_")[2], int(t.split("_")[3]), int(t.split("_")[4])
        st, sdir, cpath = by_dir[d], os.path.join(run, "sets", d), os.path.join(run, "claimed", f"{t}@{owner}")
        if terminal(sdir):
            os.unlink(cpath); done["discarded_tickets"] += 1; continue
        end, h, crossing, _ = prefix(st, sdir)
        hs = K - h if end == a and not crossing else 10 ** 9
        mp = dict(metric["outers"][f"{st['pop']}|{st['outer']}"], keep=metric["pops"][st["pop"]]["keep"],
                  mad=metric["pops"][st["pop"]]["mad"])
        sst = {"index": st["index"], "pop": st["pop"], "outer": st["outer"], "n": st["n"], "E": st["E"],
               "stream_tag": st["stream_tag"], "proposal_budget": st["cap_batches"] * BATCH, "batches": b_ - a}
        try:
            S = p2.run_setting({"batch": BATCH, "hit_stop": hs, "_binding": bind}, sst, mp, sdir, deadline, des,
                               ckpt_secs=CKPT_SECS, first_batch=a, name=f"sh{a:09d}",
                               cancelled=lambda: os.path.exists(os.path.join(sdir, "COMPLETE")))
        except (SystemExit, Exception) as ex:       # refused recovery or an unexpected error fails the setting, not the worker
            L = lock(sdir)
            try:
                if not terminal(sdir):
                    mark(sdir, "FAILED", {"range": a, "failure": f"{type(ex).__name__}: {ex}"})
            finally:
                unlock(L)
            os.unlink(cpath); done["failed_shards"] = done.get("failed_shards", 0) + 1; continue
        if S["status"] == "censored":
            os.rename(cpath, os.path.join(run, "queue", t)); done["requeued_censored"] += 1; break
        L = lock(sdir)
        try:
            plan(st, sdir, run, b)
        finally:
            unlock(L)
        os.unlink(cpath); done["shards"] += 1
    p2.atomic_json({"owner": owner, "binding": bind, "runtime": p2.runtime(), "host": os.uname().nodename, **done},
                   os.path.join(run, "workers", f"{owner}.json"))
    return done


# ---------------------------------------------------------------- collect (validate, assemble, account)
def read_journal(path, S):
    data = open(path, "rb").read()[:S["journal_bytes"]] if S["journal_bytes"] else b""
    if hashlib.sha256(data).hexdigest() != S["journal_sha256"] or data.count(b"\n") != S["hits"]:
        raise ValueError("journal differs from its checkpoint")
    return data.splitlines(True)


def collect(settings_path, metric_path, run, wave, out):
    p2.atomic_json({"collection_ok": False, "state": "collecting"}, out)
    b = json.load(open(settings_path)); bind = binding(b, settings_path); metric = json.load(open(metric_path))
    rows, errors = [], []
    status = {"COMPLETE": 0, "CAPPED": 0, "FAILED": 0, "incomplete": 0}
    for st in b["settings"]:
        if st["wave"] != wave:
            continue
        sdir = os.path.join(run, "sets", st["dir"]); row = {k: st[k] for k in ("dir", "index", "pop", "outer", "n", "library")}
        try:
            L = len(metric["outers"][f"{st['pop']}|{st['outer']}"]["recorded"])
            lines, prev, useful, discarded = [], (-1, -1), 0.0, 0.0
            pl = st["pilot"]
            if pl:
                S = json.load(open(os.path.join(sdir, "pilot.json")))
                if {k: S[k] for k in pl} != pl:
                    raise ValueError("pilot prefix differs from the bound pilot collection")
                lines += read_journal(os.path.join(sdir, "pilot_hits.jsonl"), S); useful += pl["cpu_seconds"]
            rs = ranges(sdir); cover = pl["batches_done"] if pl else 0
            if any(a2 < b1 for (a1, b1), (a2, b2) in zip(rs, rs[1:])):
                raise ValueError("overlapping ranges")
            end, h, crossing, prow = prefix(st, sdir)
            for a, S in prow:
                if S["binding"] != bind or S.get("first_batch", 0) != a or S["index"] != st["index"]:
                    raise ValueError(f"shard {a} bound to other inputs")
                lines += read_journal(os.path.join(sdir, f"sh{a:09d}_hits.jsonl"), S); useful += S["cpu_seconds"]
            in_prefix = {a for a, _ in prow}
            for a, b_ in rs:
                S = shard_state(sdir, a)
                if S and a not in in_prefix:
                    discarded += S["cpu_seconds"]
            for ln in lines:
                hrec = json.loads(ln)
                if set(hrec) != p2.HIT_KEYS or set(hrec["theta"]) != set(p2.PARAMS) or len(hrec["recorded"]) != L:
                    raise ValueError("hit record schema")
                if (hrec["batch"], hrec["proposal_in_batch"]) <= prev:
                    raise ValueError("hit identities duplicated or out of order")
                prev = (hrec["batch"], hrec["proposal_in_batch"])
            mk = terminal(sdir)
            if mk == "COMPLETE":
                if not crossing or len(lines) < K:
                    raise ValueError("COMPLETE marker without a verified K-hit prefix")
                lib = b"".join(lines[:K]); p2.replace_bytes(os.path.join(run, "lib", f"{st['dir']}.jsonl"), lib)
                row |= {"library_sha256": hashlib.sha256(lib).hexdigest(), "kth_hit": json.loads(lines[K - 1])["batch"]}
            elif mk == "CAPPED" and not (end >= st["cap_batches"] and h < K):
                raise ValueError("CAPPED marker inconsistent with the prefix")
            row |= {"status": mk or "incomplete", "prefix_end_batch": end, "prefix_hits": h, "useful_cpu_h": useful / 3600,
                    "discarded_cpu_h": discarded / 3600, "ranges": len(rs)}
            status[mk or "incomplete"] += 1
        except Exception as ex:
            errors.append(f"{st['dir']}: {type(ex).__name__}: {ex}"); row["status"] = "invalid"
        rows.append(row)
    summary = {"collection_ok": not errors, "wave": wave, "binding": bind, "status": status, "n_errors": len(errors),
               "errors": errors[:1000], "useful_cpu_h": sum(r.get("useful_cpu_h", 0) for r in rows),
               "discarded_cpu_h": sum(r.get("discarded_cpu_h", 0) for r in rows),
               "queue_left": len(os.listdir(os.path.join(run, "queue"))), "claims_left": len(os.listdir(os.path.join(run, "claimed"))),
               "rows": rows}
    p2.atomic_json(summary, out)
    pack = [os.path.relpath(out, run), f"collect_{wave}.log"] + [f"lib/{r['dir']}.jsonl" for r in rows if r.get("library_sha256")]
    fd, tmpf = tempfile.mkstemp(dir=run, prefix=".tmp_")
    with os.fdopen(fd, "w") as fh:
        fh.write("\n".join(pack) + "\n")
    os.replace(tmpf, os.path.join(run, f"pack_{wave}.txt"))
    print("collection_ok", summary["collection_ok"], wave, status, "useful", round(summary["useful_cpu_h"], 1),
          "discarded", round(summary["discarded_cpu_h"], 1), "errors", len(errors))
    if errors:
        raise SystemExit(f"collection failed: {errors[0]}")


# ---------------------------------------------------------------- preflight and fixtures
def preflight(settings_path, metric_path, njobs, jobcpus, wall_secs, ceiling, prior, wave):
    b = check(settings_path, metric_path)
    alloc = int(njobs) * int(jobcpus) * int(wall_secs) / 3600 + float(prior) + COLLECTOR_CPU_H
    errs = [] if alloc <= float(ceiling) else [f"allocation bound {alloc:.1f} exceeds the {ceiling} CPU-h ceiling"]
    if wave not in WAVES:
        errs.append(f"unknown wave {wave}")
    print(json.dumps({"preflight": "refused" if errs else "passed", "errors": errs, "settings_sha256": p2.sha(settings_path),
                      "runtime": p2.runtime(), "wave": wave, "allocated_cpu_hours_bound": round(alloc, 3), "ceiling": float(ceiling)}))
    if errs:
        raise SystemExit("preflight refused")
    test()


def test():
    """Synthetic fixtures: hits are a deterministic function of (index, batch, proposal); K and batch are small."""
    from unittest import mock
    global K, BATCH, MIN_SHARD_CPU_H
    me = sys.modules[__name__]; res = {}; tmp = tempfile.mkdtemp()
    saved = (K, BATCH, MIN_SHARD_CPU_H)
    K, BATCH, MIN_SHARD_CPU_H = 25, 10, 0.0

    def fake(st, mp, bi, B, des):
        keys = ("poisson_accept", "theta_accept", "paths", "selected_SA", "overflow", "hits", "boundary", "hits_lo", "hits_hi",
                "rounding_excess")
        r = {k: 0 for k in keys}; r["proposals"] = B; r["hit_records"] = []
        for j in range(B):
            u = int(hashlib.sha256(f"{st.get('stream_tag', 2)}/{st['index']}/{bi}/{j}".encode()).hexdigest()[:8], 16) / 2 ** 32
            if u < st["E"].get("rate", 0.05):
                r["hit_records"].append({"batch": bi, "proposal_in_batch": j, "boundary": False,
                                         "theta": {k: 0.5 for k in p2.PARAMS}, "recorded": [4, 3, 0]})
        r.update(poisson_accept=B, theta_accept=B, paths=B, selected_SA=len(r["hit_records"]), hits=len(r["hit_records"]),
                 hits_lo=len(r["hit_records"]), hits_hi=len(r["hit_records"]))
        return r

    def make(d, rate, pilot=None, cap=400):
        sp, mp = os.path.join(d, "settings.json"), os.path.join(d, "metric.json")
        json.dump({"outers": {"synthetic|toy/0": {"recorded": [5, 4, 0], "q": [], "radius": 1.0}},
                   "pops": {"synthetic": {"keep": [], "mad": []}}}, open(mp, "w"))
        st = {"index": 7, "pop": "synthetic", "outer": "toy/0", "n": 30, "E": {"n": 30, "k": 1, "r": 1, "rate": rate},
              "rate": BATCH / 3600 / 0.05, "cap_batches": cap, "prior_hpb": 0.5 * BATCH * 0.05, "wave": "W1", "dir": "s00007", "library": "primary",
              "stream_tag": 2, "pilot": pilot}
        json.dump({"settings": [st], "metric_sha256": "m", "runner_sha256": "r", "min_shard_cpu_h": MIN_SHARD_CPU_H,
                   "target_wall_h": TARGET_WALL_H, "max_inflight": MAX_INFLIGHT, "overshoot": OVERSHOOT}, open(sp, "w"))
        run = os.path.join(d, "run")
        for x in ("queue", "claimed", "sets/s00007", "lib", "workers"):
            os.makedirs(os.path.join(run, x), exist_ok=True)
        return sp, mp, run, st

    def drive(d, rate, order_seed, cap=400, inflight=None, cancel_mid=False):
        sp, mp, run, st = make(d, rate, cap=cap)
        b = json.load(open(sp)); sdir = os.path.join(run, "sets", st["dir"])
        L = lock(sdir); plan(st, sdir, run, b); unlock(L)
        random.seed(order_seed)                              # claim order among queued tickets varies with the seed
        work(sp, mp, run, f"job{order_seed}[0].srv.0", time.time() + 3600, qstat="/bin/false", des={})
        return sp, mp, run, st

    try:
        with mock.patch.object(p2, "one_batch", fake), mock.patch.object(me, "MAX_INFLIGHT", 6), \
                mock.patch.object(me, "TARGET_WALL_H", 1e-6):
            libs = []
            for seed_ in (1, 2, 3):
                d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st = drive(d, 0.05, seed_)
                collect(sp, mp, run, "W1", os.path.join(d, "c.json"))
                libs.append(open(os.path.join(run, "lib", "s00007.jsonl"), "rb").read())
                c = json.load(open(os.path.join(d, "c.json")))
            with mock.patch.object(me, "MAX_INFLIGHT", 1):
                d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st = drive(d, 0.05, 9)
                collect(sp, mp, run, "W1", os.path.join(d, "c.json"))
                serial = open(os.path.join(run, "lib", "s00007.jsonl"), "rb").read()
            res["library_invariant_to_shard_plan_and_order"] = len(set(libs + [serial])) == 1 and serial.count(b"\n") == K
            res["parallel_plan_used_several_ranges"] = c["rows"][0]["ranges"] > 1
            d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st = drive(d, 0.0, 4, cap=40)
            collect(sp, mp, run, "W1", os.path.join(d, "c.json")); c = json.load(open(os.path.join(d, "c.json")))
            res["zero_rate_setting_is_capped"] = c["status"]["CAPPED"] == 1 and c["rows"][0]["prefix_end_batch"] == 40
            # stale claim of a finished job is requeued; a live one is not
            d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st = make(d, 0.05)
            open(os.path.join(run, "claimed", "W1_0000001_s00007_000000000_000000005@dead[1].srv.0"), "w").close()
            open(os.path.join(run, "claimed", "W1_0000001_s00007_000000005_000000010@live[2].srv.0"), "w").close()
            fq = os.path.join(d, "qstat"); open(fq, "w").write("#!/bin/sh\ncase \"$3\" in dead*) echo '    job_state = F';; *) echo '    job_state = R';; esac\n")
            os.chmod(fq, 0o755)
            n = recover_stale(run, "me[0].srv.0", qstat=fq)
            res["stale_claim_requeued_only_for_finished_job"] = n == 1 and os.listdir(os.path.join(run, "queue")) == \
                ["W1_0000001_s00007_000000000_000000005"]
            # a worker killed mid-shard leaves its claim; once its job is finished the claim is requeued and resumed
            d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st = make(d, 0.05)
            b = json.load(open(sp)); sdir = os.path.join(run, "sets", st["dir"]); L = lock(sdir); plan(st, sdir, run, b); unlock(L)
            calls = [0]

            def dies(*a_):
                calls[0] += 1
                if calls[0] == 4:
                    raise KeyboardInterrupt("worker killed")
                return fake(*a_)
            with mock.patch.object(p2, "one_batch", dies):
                try:
                    work(sp, mp, run, "jobA[0].srv.0", time.time() + 3600, qstat="/bin/false", des={})
                except KeyboardInterrupt:
                    pass
            left = os.listdir(os.path.join(run, "claimed"))
            fq = os.path.join(d, "qstat"); open(fq, "w").write("#!/bin/sh\necho '    job_state = F'\n"); os.chmod(fq, 0o755)
            work(sp, mp, run, "jobB[0].srv.0", time.time() + 3600, qstat=fq, des={})
            collect(sp, mp, run, "W1", os.path.join(d, "c.json"))
            res["killed_worker_claim_recovered_and_resumed"] = len(left) == 1 and left[0].endswith("@jobA[0].srv.0") and \
                open(os.path.join(run, "lib", "s00007.jsonl"), "rb").read() == serial
            res["no_claim_after_deadline"] = work(sp, mp, run, "jobC[0].srv.0", time.time() - 1, qstat="/bin/false", des={})["shards"] == 0
            # collector rejects a tampered shard journal and overlapping ranges
            hp = "sh000000000_hits.jsonl"
            blob = open(os.path.join(sdir, hp), "rb").read(); open(os.path.join(sdir, hp), "wb").write(blob.replace(b"\"batch\": ", b"\"batch\":  ", 1))
            try:
                collect(sp, mp, run, "W1", os.path.join(d, "c2.json")); res["collector_rejects_tampered_journal"] = False
            except SystemExit:
                res["collector_rejects_tampered_journal"] = not json.load(open(os.path.join(d, "c2.json")))["collection_ok"]
            # a refused recovery (journal without a checkpoint) fails the setting and the worker carries on
            d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st = make(d, 0.05)
            b = json.load(open(sp)); sdir = os.path.join(run, "sets", st["dir"]); L = lock(sdir); plan(st, sdir, run, b); unlock(L)
            first = sorted(os.listdir(os.path.join(run, "queue")))[0]; a0 = int(first.split("_")[3])
            open(os.path.join(sdir, f"sh{a0:09d}_hits.jsonl"), "w").write("orphan\n")          # journal without a checkpoint
            out_ = work(sp, mp, run, "jobD[0].srv.0", time.time() + 3600, qstat="/bin/false", des={})
            res["refused_recovery_fails_setting_not_worker"] = terminal(sdir) == "FAILED" and out_.get("failed_shards", 0) >= 1 \
                and not os.listdir(os.path.join(run, "claimed"))
            # pilot prefix import refuses a journal that differs from the bound pilot collection
            d = tempfile.mkdtemp(dir=tmp); pdir = os.path.join(d, "pilot"); os.makedirs(pdir)
            data = b'{"x": 1}\n'
            S = {"batches_done": 3, "hits": 1, "journal_bytes": len(data), "journal_sha256": hashlib.sha256(data).hexdigest(),
                 "status": "complete", "proposals": 30, "cpu_seconds": 1.0}
            json.dump(S, open(os.path.join(pdir, "s0007.json"), "w")); open(os.path.join(pdir, "s0007_hits.jsonl"), "wb").write(b'{"x": 2}\n')
            sp, mp, run, st = make(d, 0.05, pilot=dict(S))
            try:
                seed(sp, pdir, run, "W1"); res["seed_rejects_altered_pilot_journal"] = False
            except SystemExit:
                res["seed_rejects_altered_pilot_journal"] = True
    finally:
        K, BATCH, MIN_SHARD_CPU_H = saved
        shutil.rmtree(tmp, ignore_errors=True)
    res["all_ok"] = all(res.values())
    print(json.dumps(res, indent=1))
    if not res["all_ok"]:
        raise SystemExit("tests failed")


if __name__ == "__main__":
    cmd, a = sys.argv[1], sys.argv[2:]
    {"export": export, "verify_export": verify_export, "settings": settings, "subset": subset, "seed": seed, "work": work,
     "collect": collect, "preflight": preflight, "test": test}[cmd](*a)
