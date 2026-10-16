"""Stage 1b: full noisy-design sampling campaign (notes/vortex_stage1b_design_20261016.md; authorised by Barry, board
1759). The sampler law, per-batch streams, recovery and hit-record format are p2_stage1a's, unchanged.
A library is the first K retained pairs of its setting in stream order (batch, proposal_in_batch). Work is split into
batch ranges ("shards") of any size; each shard is run by p2_stage1a.run_setting from its first batch, so a shard's
output depends only on (setting, range) and the library is invariant to shard boundaries, order and parallelism.
Planning (which ranges exist, how many run at once) adapts to observed rates and affects cost only.
  export        MANIFEST BASE S0_INPUTS S0_FULLDIR OUT_METRIC   p2_stage1a.export over trial IDs 0-199 (deep-server)
  verify_export METRIC P2_METRIC                                pilot pairs and their E identical to Stage 1a's
  settings      METRIC PILOT_SETTINGS PILOT_COLLECT OUT          bind 21,600 primary + 216 check settings (stable IDs)
  subset        SETTINGS OUT DIRS CAP_CPU_H TARGET_WALL_H MIN_SHARD_CPU_H CEILING   smoke settings (own campaign and ceiling)
  seed          SETTINGS PILOT_DIR RUN WAVE                      import verified pilot prefixes; first tickets
  work          SETTINGS METRIC RUN WAVE OWNER DEADLINE_EPOCH    pull worker for one wave: claim, run, plan successors
  collect       SETTINGS METRIC RUN WAVE OUT_JSON                validate shards, assemble libraries, account CPU
  preflight     SETTINGS METRIC LEDGER ARRAY_NAME OUTDIR NJOBS JOBCPUS WALL_SECS WAVE   bound check, fixtures, reservation
  test                                                            synthetic fixtures (exit non-zero on failure)
Run directory RUN: queue/ (tickets), claimed/ (ticket@owner), sets/<dir>/ (pilot prefix, ranges/, shard checkpoints and
journals, COMPLETE/CAPPED/FAILED markers, lock/), lib/ (assembled libraries), workers/. Every queue transition (claim,
requeue, release) and every plan happens under the setting's owner-safe lock; planning reconciles each unfinished range
to exactly one ticket or claim. The per-setting cap is a fixed proposal budget (2,000 CPU-h equivalent at the bound
rate); allocated-CPU ceilings per wave and campaign are enforced by the reservation ledger. Run from the frozen source root."""
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
COLLECTOR_CPU_H = 8.0
QSTAT = "/opt/pbs/bin/qstat"
CEILINGS = {"W1": 200_000.0, "W2": 1_000_000.0, "campaign": 1_200_000.0}     # allocated CPU-h (Barry, board 1759)            # s1b_collect.pbs: 1 core x 8 h walltime, charged against the wave ceiling
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
         "campaign": "s1b", "ceilings": CEILINGS,
         "cap_rule": "per-setting proposal budget cap_batches x batch, equal to 2,000 CPU-h at the setting's bound rate "
                     "(pilot realised throughput, or its cell median); a fixed stopping rule, not a measured-CPU ceiling",
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


def subset(settings_path, out, dirs, cap_cpu_h, target_wall_h, min_shard_cpu_h, ceiling):
    """Smoke settings: selected dirs with a reduced per-setting cap and planner targets (runner and bindings unchanged)."""
    b = json.load(open(settings_path)); want = dirs.split(",")
    st = [dict(x) for x in b["settings"] if x["dir"] in want]
    if sorted(x["dir"] for x in st) != sorted(want):
        raise SystemExit("unknown dir")
    for x in st:
        x["cap_batches"] = int(float(cap_cpu_h) * 3600 * x["rate"] // BATCH)
    b.update(settings=st, cap_cpu_h=float(cap_cpu_h), target_wall_h=float(target_wall_h), min_shard_cpu_h=float(min_shard_cpu_h),
             stage=b["stage"] + " -- SMOKE SUBSET", derived_from_sha256=p2.sha(settings_path), campaign="s1b-smoke",
             ceilings={"W1": float(ceiling), "W2": float(ceiling), "campaign": float(ceiling)})
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
def pid_alive(pid):
    try:
        os.kill(int(pid), 0); return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def owner_dead(info, qstat=QSTAT):
    """Positive evidence only: same host and pid gone, or the owner's PBS job reported finished (job_state F)."""
    if info.get("host") == os.uname().nodename:
        return not pid_alive(info["pid"])
    job = info.get("owner", "").rsplit(".", 1)[0]
    if "[" not in job and ".kunanyi" not in job:
        return False
    try:
        out = subprocess.run([qstat, "-x", "-f", job], capture_output=True, text=True, timeout=60).stdout
    except Exception:
        return False
    return any(l.strip() == "job_state = F" for l in out.splitlines())


class LockStale(RuntimeError):
    """A lock's owner and the reclaimer of that lock have both ended: fail closed for operator recovery."""


def _owner(path):
    try:
        return json.load(open(os.path.join(path, "owner.json")))
    except (FileNotFoundError, NotADirectoryError, ValueError):
        return None


def _publish(path, me):
    """Atomically create directory path holding owner.json; False if it already exists."""
    tmp = f"{path}.new.{me['token']}"
    os.mkdir(tmp)
    with open(os.path.join(tmp, "owner.json"), "w") as fh:
        json.dump(me, fh); fh.flush(); os.fsync(fh.fileno())
    try:
        os.rename(tmp, path); return True
    except OSError:
        shutil.rmtree(tmp, ignore_errors=True); return False


def _reclaim(d, observed, me, qstat=QSTAT):
    """Break the ended generation `observed` of lock d. Only one reclaimer at a time (the d.reclaim mutex), and only while
    d still holds that generation's token: a stale observation can never remove a successor's lock. A reclaim mutex whose
    own owner has ended is not broken automatically (LockStale)."""
    r = f"{d}.reclaim"
    if not _publish(r, me):
        info = _owner(r)
        if info and owner_dead(info, qstat):
            raise LockStale(f"{r}: reclaim mutex held by an ended owner; operator recovery needed")
        return False
    try:
        cur = _owner(d)
        if cur and cur["token"] == observed["token"] and owner_dead(cur, qstat):
            os.rename(d, f"{d}.broken.{observed['token']}")
            return True
        return False
    finally:
        rel = f"{r}.rel.{me['token']}"
        os.rename(r, rel); shutil.rmtree(rel)


def lock(sdir, owner, qstat=QSTAT):
    """Owner-safe lock: a directory holding owner.json, published by an atomic rename (never an empty directory, so a
    rename cannot replace a live one). It is broken only on positive evidence that its owner has ended, never on age,
    and only through _reclaim; unlock requires the acquiring token."""
    d = os.path.join(sdir, "lock")
    me = {"owner": owner, "host": os.uname().nodename, "pid": os.getpid(), "token": os.urandom(8).hex()}
    while True:
        if _publish(d, me):
            return d, me["token"]
        info = _owner(d)
        if info is None:
            time.sleep(0.05); continue
        if owner_dead(info, qstat) and _reclaim(d, info, me, qstat):
            continue
        time.sleep(0.05 + random.random() * 0.1)


def unlock(L):
    d, token = L
    info = json.load(open(os.path.join(d, "owner.json")))
    if info["token"] != token:
        raise RuntimeError(f"{d}: lock is not owned by this holder")
    rel = f"{d}.rel.{token}"
    os.rename(d, rel); shutil.rmtree(rel)


class held:
    def __init__(self, sdir, owner, qstat=QSTAT):
        self.args = (sdir, owner, qstat)

    def __enter__(self):
        self.L = lock(*self.args); return self.L

    def __exit__(self, *exc):
        unlock(self.L)


def ranges(sdir):
    rd = os.path.join(sdir, "ranges")
    return sorted(tuple(int(x) for x in f.split("-")) for f in os.listdir(rd)) if os.path.isdir(rd) else []


def shard_state(sdir, a):
    p = os.path.join(sdir, f"sh{a:09d}.json")
    return json.load(open(p)) if os.path.exists(p) else None


def prefix(st, sdir):
    """Contiguous prefix: (end batch, hits, crossing, rows). A completed non-crossing range advances the prefix only when
    it committed every batch of its range; a short range ends the prefix unless the cumulative hits reach K inside it."""
    pl = st["pilot"]
    end, h = (pl["batches_done"], pl["hits"]) if pl else (0, 0)
    rows = []
    if h >= K:
        return end, h, ("pilot", end), rows
    for a, b_ in ranges(sdir):
        if a != end:
            break
        S = shard_state(sdir, a)
        if not S or S["status"] != "complete" or not (0 <= S["batches_done"] <= b_ - a):
            break
        rows.append((a, S)); h += S["hits"]
        if h >= K:
            return a + S["batches_done"], h, (a, a + S["batches_done"]), rows
        if S["batches_done"] != b_ - a:
            break
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
    """Caller holds the setting lock. Set a terminal marker; else reconcile every unfinished range so it has exactly one
    queued ticket or live claim (republishing an orphan once), then create successor ranges (marker, then ticket)."""
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
    mins, tw, mi, ov = b["min_shard_cpu_h"], b["target_wall_h"], b["max_inflight"], b["overshoot"]   # bound planner
    q, c = os.path.join(run, "queue"), os.path.join(run, "claimed")
    live = {n.rsplit("_", 2)[1] + "_" + n.rsplit("_", 2)[2] for n in os.listdir(q) if f"_{st['dir']}_" in n}
    live |= {n.split("@")[0].rsplit("_", 2)[1] + "_" + n.split("@")[0].rsplit("_", 2)[2] for n in os.listdir(c) if f"_{st['dir']}_" in n}
    pl = st["pilot"]
    H = (pl["hits"] if pl else 0); N = (pl["batches_done"] if pl else 0); C = (pl["cpu_seconds"] if pl else 0.0)
    inflight, inflight_left, orphans = 0, 0, []
    for a, b_ in rs:
        S = shard_state(sdir, a)
        done = S["batches_done"] if S else 0
        if S:
            H += S["hits"]; N += done; C += S["cpu_seconds"]
        if not S or S["status"] not in ("complete", "cancelled"):
            inflight += 1; inflight_left += (b_ - a) - done
            if f"{a:09d}_{b_:09d}" not in live:
                orphans.append((a, b_))
    cpb = C / N / 3600 if N and C > 0 else BATCH / st["rate"] / 3600              # CPU-h per batch
    ph = st.get("prior_hpb", 0.0)                                                 # cell prior, PRIOR_HITS pseudo-hits
    hpb = (H + PRIOR_HITS) / (N + PRIOR_HITS / ph) if ph > 0 else (H / N if N else 0.0)
    for a, b_ in orphans:                                                         # interrupted publication: republish once
        open(os.path.join(q, ticket_name(st, a, b_, 0)), "w").close()
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
        open(os.path.join(q, ticket_name(st, a, b_, prio)), "w").close()
        a, slots = b_, slots - 1


# ---------------------------------------------------------------- seed (pilot prefix import)
def seed(settings_path, pilot_dir, run, wave, qstat=QSTAT):
    b = json.load(open(settings_path)); owner = f"seed:{os.uname().nodename}:{os.getpid()}"
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
        with held(sdir, owner, qstat):
            plan(st, sdir, run, b)
        n["complete_at_seed" if terminal(sdir) == "COMPLETE" else "planned"] += 1
    print("seed", wave, n)


# ---------------------------------------------------------------- worker
def parse_ticket(t):
    w, prio, d, a, b_ = t.split("_")
    return w, d, int(a), int(b_)


def claim(run, owner, wave, qstat=QSTAT):
    """Claim one of this wave's tickets (atomic rename) while holding its setting's lock."""
    q = os.path.join(run, "queue")
    for _ in range(3):
        names = sorted(n for n in os.listdir(q) if n.startswith(f"{wave}_"))
        if not names:
            return None
        head = names[:32]; random.shuffle(head)
        for t in head:
            try:
                with held(os.path.join(run, "sets", parse_ticket(t)[1]), owner, qstat):
                    try:
                        os.rename(os.path.join(q, t), os.path.join(run, "claimed", f"{t}@{owner}"))
                        return t
                    except FileNotFoundError:
                        continue
            except LockStale as ex:                      # that setting waits for an operator; others proceed
                print(f"skipping {t}: {ex}", file=sys.stderr, flush=True)
    return None


def recover_stale(run, owner, wave, qstat=QSTAT):
    """Requeue this wave's claims whose owning PBS job is positively finished (job_state F), under the setting lock."""
    me = owner.rsplit(".", 1)[0]; seen, n = {}, 0
    for c in os.listdir(os.path.join(run, "claimed")):
        t, own = c.split("@", 1); job = own.rsplit(".", 1)[0]
        if job == me or not t.startswith(f"{wave}_"):
            continue
        if job not in seen:
            seen[job] = owner_dead({"owner": own, "host": None}, qstat)
        if seen[job]:
            try:
                with held(os.path.join(run, "sets", parse_ticket(t)[1]), owner, qstat):
                    try:
                        os.rename(os.path.join(run, "claimed", c), os.path.join(run, "queue", t)); n += 1
                    except FileNotFoundError:
                        pass
            except LockStale as ex:
                print(f"not requeued {c}: {ex}", file=sys.stderr, flush=True)
    return n


def work(settings_path, metric_path, run, wave, owner, deadline, qstat=QSTAT, des=None):
    b = check(settings_path, metric_path) if des is None else json.load(open(settings_path))
    metric = json.load(open(metric_path)); des = des if des is not None else p2.designs()
    bind = binding(b, settings_path); by_dir = {s["dir"]: s for s in b["settings"]}
    deadline = float(deadline)
    done = {"shards": 0, "discarded_tickets": 0, "requeued_censored": 0, "stale_requeued": 0, "failed_shards": 0}
    while time.time() < deadline:
        t = claim(run, owner, wave, qstat)
        if t is None:
            done["stale_requeued"] += recover_stale(run, owner, wave, qstat)
            t = claim(run, owner, wave, qstat)
            if t is None:
                break
        _, d, a, b_ = parse_ticket(t)
        st, sdir, cpath = by_dir[d], os.path.join(run, "sets", d), os.path.join(run, "claimed", f"{t}@{owner}")
        if terminal(sdir):
            with held(sdir, owner, qstat):
                os.unlink(cpath)
            done["discarded_tickets"] += 1; continue
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
            with held(sdir, owner, qstat):
                if not terminal(sdir):
                    mark(sdir, "FAILED", {"range": a, "failure": f"{type(ex).__name__}: {ex}"})
                os.unlink(cpath)
            done["failed_shards"] += 1; continue
        try:
            with held(sdir, owner, qstat):
                if S["status"] == "censored":
                    os.rename(cpath, os.path.join(run, "queue", t)); done["requeued_censored"] += 1
                else:
                    plan(st, sdir, run, b); os.unlink(cpath); done["shards"] += 1
        except LockStale as ex:                          # the claim stays; the setting is reported incomplete
            print(f"left claim {t}: {ex}", file=sys.stderr, flush=True); done["lock_stale"] = done.get("lock_stale", 0) + 1
        if S["status"] == "censored":
            break
    p2.atomic_json({"owner": owner, "wave": wave, "binding": bind, "runtime": p2.runtime(), "host": os.uname().nodename, **done},
                   os.path.join(run, "workers", f"{owner}.json"))
    return done


# ---------------------------------------------------------------- collect (validate, assemble, account)
def records(data, lo, hi, L, prev):
    """Validate journal lines: schema, identity within committed batches [lo, hi), strictly increasing after prev."""
    out = []
    for ln in data.splitlines(True):
        h = json.loads(ln)
        ok = isinstance(h, dict) and set(h) == p2.HIT_KEYS and type(h["batch"]) is int and type(h["proposal_in_batch"]) is int \
            and type(h["boundary"]) is bool and isinstance(h["theta"], dict) and set(h["theta"]) == set(p2.PARAMS) \
            and all(type(v) is float and math.isfinite(v) for v in h["theta"].values()) and isinstance(h["recorded"], list) \
            and len(h["recorded"]) == L and all(type(x) is int for x in h["recorded"])
        if not ok:
            raise ValueError("hit record schema")
        if not (lo <= h["batch"] < hi and 0 <= h["proposal_in_batch"] < BATCH):
            raise ValueError(f"hit identity outside committed batches [{lo}, {hi})")
        if (h["batch"], h["proposal_in_batch"]) <= prev:
            raise ValueError("hit identities duplicated or out of order")
        if not (all(x > 1 for x in h["recorded"][1:-1]) and h["recorded"][-1] <= 1):
            raise ValueError("hit record fails selection S")
        prev = (h["batch"], h["proposal_in_batch"]); out.append((ln, h))
    return out, prev


def verified(S, path, lo, hi, L, terminal_status):
    """Checkpoint fields, counters and journal for committed batches [lo, hi); returns validated records."""
    need = ("index", "status", "batches_done", "cpu_seconds", "wall_seconds", "journal_bytes", "journal_sha256") + p2.COUNTERS
    if any(k not in S for k in need):
        raise ValueError("checkpoint lacks fields")
    if any(type(S[k]) is not int or S[k] < 0 for k in ("batches_done", "journal_bytes") + p2.COUNTERS) or \
            any(type(S[k]) not in (int, float) or not math.isfinite(S[k]) or S[k] < 0 for k in ("cpu_seconds", "wall_seconds")):
        raise ValueError("checkpoint fields of wrong type or domain")
    if S["proposals"] != S["batches_done"] * BATCH:
        raise ValueError("proposals differ from committed batches")
    if not (S["theta_accept"] <= S["poisson_accept"] <= S["proposals"]) or S["paths"] != S["theta_accept"] \
            or S["selected_SA"] + S["overflow"] > S["paths"] or not (S["hits_lo"] <= S["hits"] <= S["hits_hi"] <= S["selected_SA"]) \
            or S["boundary"] > S["hits"]:
        raise ValueError("counter invariants fail")
    raw = open(path, "rb").read() if os.path.exists(path) else b""
    if len(raw) < S["journal_bytes"] or (terminal_status and len(raw) != S["journal_bytes"]):
        raise ValueError("journal length differs from its checkpoint")
    data = raw[:S["journal_bytes"]]
    if hashlib.sha256(data).hexdigest() != S["journal_sha256"] or data.count(b"\n") != S["hits"]:
        raise ValueError("journal differs from its checkpoint")
    recs, _ = records(data, lo, hi, L, (-1, -1))
    if sum(h["boundary"] for _, h in recs) != S["boundary"]:
        raise ValueError("boundary records differ from the checkpoint")
    return recs


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
            pl = st["pilot"]; lines = []; useful = discarded = 0.0
            p0 = pl["batches_done"] if pl else 0
            if pl:
                S = json.load(open(os.path.join(sdir, "pilot.json")))
                if {k: S[k] for k in pl} != pl or S.get("index") != st["index"]:
                    raise ValueError("pilot prefix differs from the bound pilot collection")
                lines += [ln for ln, _ in verified(S, os.path.join(sdir, "pilot_hits.jsonl"), 0, p0, L, True)]
                useful += S["cpu_seconds"]
            rs = ranges(sdir); pos = p0
            for a, b_ in rs:                                      # declared ranges tile [pilot end, cursor) exactly
                if a != pos or b_ <= a or b_ > st["cap_batches"]:
                    raise ValueError(f"ranges do not tile from batch {p0}: [{a}, {b_}) at {pos}")
                pos = b_
            states = {}
            for a, b_ in rs:                                      # every declared shard is validated before any use
                S = shard_state(sdir, a)
                if S is None:
                    continue
                if S.get("binding") != bind or S.get("index") != st["index"] or S.get("first_batch", 0) != a:
                    raise ValueError(f"shard {a}: bound to other inputs")
                if S["status"] not in ("complete", "censored", "running", "cancelled", "failed"):
                    raise ValueError(f"shard {a}: unknown status")
                if S["status"] == "complete" and S.get("stop") not in ("hits", "budget"):
                    raise ValueError(f"shard {a}: complete without a stop reason")
                if S["status"] == "complete" and S.get("stop") == "budget" and S["batches_done"] != b_ - a:
                    raise ValueError(f"shard {a}: complete by budget without covering its range")
                if not 0 <= S["batches_done"] <= b_ - a:
                    raise ValueError(f"shard {a}: committed batches exceed its range")
                recs = verified(S, os.path.join(sdir, f"sh{a:09d}_hits.jsonl"), a, a + S["batches_done"], L,
                                S["status"] in ("complete", "failed", "cancelled"))
                states[a] = (S, recs)
            end, h, crossing, prow = prefix(st, sdir)
            in_prefix = {a for a, _ in prow}
            prev = (-1, -1)
            for ln in lines:
                prev = (json.loads(ln)["batch"], json.loads(ln)["proposal_in_batch"])
            for a, _ in prow:
                S, recs = states[a]; useful += S["cpu_seconds"]
                for ln, hrec in recs:
                    if (hrec["batch"], hrec["proposal_in_batch"]) <= prev:
                        raise ValueError("hit identities out of global order")
                    prev = (hrec["batch"], hrec["proposal_in_batch"]); lines.append(ln)
            for a, (S, _) in states.items():
                if a not in in_prefix:
                    discarded += S["cpu_seconds"]
                    if S["status"] == "complete" and S["batches_done"] != dict(rs)[a] - a and not crossing:
                        raise ValueError(f"shard {a}: short completed range outside a crossing")
            mk = terminal(sdir)
            if mk == "COMPLETE":
                if not crossing or len(lines) < K:
                    raise ValueError("COMPLETE marker without a verified K-hit prefix")
                lib = b"".join(lines[:K]); p2.replace_bytes(os.path.join(run, "lib", f"{st['dir']}.jsonl"), lib)
                row |= {"library_sha256": hashlib.sha256(lib).hexdigest(), "kth_hit": json.loads(lines[K - 1])["batch"]}
            elif mk == "CAPPED" and not (end >= st["cap_batches"] and h < K and not crossing):
                raise ValueError("CAPPED marker inconsistent with the prefix")
            elif mk is None and crossing:
                raise ValueError("verified K-hit prefix without a COMPLETE marker")
            row |= {"status": mk or "incomplete", "prefix_end_batch": end, "prefix_hits": h, "useful_cpu_h": useful / 3600,
                    "discarded_cpu_h": discarded / 3600, "ranges": len(rs)}
            status[mk or "incomplete"] += 1
        except Exception as ex:
            errors.append(f"{st['dir']}: {type(ex).__name__}: {ex}"); row["status"] = "invalid"
        rows.append(row)
    summary = {"collection_ok": not errors, "wave": wave, "binding": bind, "status": status, "n_errors": len(errors),
               "errors": errors[:1000], "useful_cpu_h": sum(r.get("useful_cpu_h", 0) for r in rows),
               "discarded_cpu_h": sum(r.get("discarded_cpu_h", 0) for r in rows),
               "incomplete": [r["dir"] for r in rows if r["status"] == "incomplete"],
               "queue_left": len(os.listdir(os.path.join(run, "queue"))), "claims_left": len(os.listdir(os.path.join(run, "claimed"))),
               "rows": rows}
    p2.atomic_json(summary, out)
    pack = [os.path.relpath(out, run), f"collect_{wave}.log"] + [f"lib/{r['dir']}.jsonl" for r in rows if r.get("library_sha256")]
    fd, tmpf = tempfile.mkstemp(dir=run, prefix=".tmp_")
    with os.fdopen(fd, "w") as fh:
        fh.write("\n".join(pack) + "\n")
    os.replace(tmpf, os.path.join(run, f"pack_{wave}.txt"))
    print("collection_ok", summary["collection_ok"], wave, status, "useful", round(summary["useful_cpu_h"], 1),
          "discarded", round(summary["discarded_cpu_h"], 1), "incomplete", len(summary["incomplete"]), "errors", len(errors))
    if errors:
        raise SystemExit(f"collection failed: {errors[0]}")


# ---------------------------------------------------------------- campaign account, preflight and fixtures
def ledger_active(ledger, campaign):
    """Replay the ledger in order: a reserve line activates a name (its first active line binds wave, CPU-h and identity);
    a release line deactivates it; a later reserve of the same name is active again."""
    active = {}
    if os.path.exists(ledger):
        for ln in open(ledger).read().splitlines():
            f = ln.split("\t")
            if f[0] == "reserve" and f[1] == campaign and f[3] not in active:
                active[f[3]] = {"wave": f[2], "cpu_h": float(f[4]), "identity": f[6] if len(f) > 6 else ""}
            elif f[0] == "release":
                active.pop(f[1], None)
    return active


def reserve(ledger, campaign, ceilings, wave, name, cpu_h, identity):
    """Campaign reservation account (the submitter holds its lock). Same name and same identity is idempotent; same name
    with any other wave, CPU-h or identity is refused; an unresolved submission stays charged until an explicit
    'release NAME manual: <evidence>' line."""
    active = ledger_active(ledger, campaign)
    tot_c, tot_w = sum(e["cpu_h"] for e in active.values()), sum(e["cpu_h"] for e in active.values() if e["wave"] == wave)
    if name in active:
        e = active[name]
        if (e["wave"], round(e["cpu_h"], 3), e["identity"]) != (wave, round(cpu_h, 3), identity):
            raise SystemExit(f"reservation {name} is bound to {e}; this request differs (release it with evidence first)")
        return {"recorded": False, "wave_reserved": tot_w, "campaign_reserved": tot_c}
    if tot_w + cpu_h > ceilings[wave] or tot_c + cpu_h > ceilings["campaign"]:
        raise SystemExit(f"reservation {cpu_h:.1f} CPU-h would exceed a ceiling: wave {wave} {tot_w:.1f}/{ceilings[wave]}, "
                         f"campaign {tot_c:.1f}/{ceilings['campaign']}")
    with open(ledger, "a") as fh:
        fh.write("\t".join(["reserve", campaign, wave, name, f"{cpu_h:.3f}", time.strftime("%Y-%m-%dT%H:%M:%S%z"), identity]) + "\n")
        fh.flush(); os.fsync(fh.fileno())
    return {"recorded": True, "wave_reserved": tot_w + cpu_h, "campaign_reserved": tot_c + cpu_h}


def preflight(settings_path, metric_path, ledger, name, outdir, njobs, jobcpus, wall_secs, wave):
    """Bound check and fixtures, then the campaign reservation (array cores x walltime + the collector)."""
    b = check(settings_path, metric_path)
    if wave not in WAVES:
        raise SystemExit(f"unknown wave {wave}")
    cpu_h = int(njobs) * int(jobcpus) * int(wall_secs) / 3600 + COLLECTOR_CPU_H
    test()
    identity = f"settings={p2.sha(settings_path)} outdir={outdir} jobs={int(njobs)} cpus={int(jobcpus)} wall={int(wall_secs)}"
    r = reserve(ledger, b["campaign"], b["ceilings"], wave, name, cpu_h, identity)
    print(json.dumps({"preflight": "passed", "settings_sha256": p2.sha(settings_path), "runtime": p2.runtime(), "wave": wave,
                      "campaign": b["campaign"], "array_name": name, "reservation_cpu_h": round(cpu_h, 3), **r,
                      "ceilings": b["ceilings"]}))


def test():
    """Synthetic fixtures (K = 25, batches of 10): hits are a deterministic function of (stream tag, index, batch, proposal)."""
    from unittest import mock
    global K, BATCH
    me = sys.modules[__name__]; res = {}; tmp = tempfile.mkdtemp(); saved = (K, BATCH)
    K, BATCH = 25, 10
    fakeq = os.path.join(tmp, "qstat_F"); open(fakeq, "w").write("#!/bin/sh\necho '    job_state = F'\n"); os.chmod(fakeq, 0o755)

    def fake(st, mp, bi, B, des):
        keys = ("poisson_accept", "theta_accept", "paths", "selected_SA", "overflow", "hits", "boundary", "hits_lo", "hits_hi",
                "rounding_excess")
        r = {k: 0 for k in keys}; r["proposals"] = B; r["hit_records"] = []
        for j in range(B):
            u = int(hashlib.sha256(f"{st.get('stream_tag', 2)}/{st['index']}/{bi}/{j}".encode()).hexdigest()[:8], 16) / 2 ** 32
            if u < st["E"].get("rate", 0.05):
                r["hit_records"].append({"batch": bi, "proposal_in_batch": j, "boundary": False,
                                         "theta": {k: 0.5 for k in p2.PARAMS}, "recorded": [4, 3, 0]})
        n = len(r["hit_records"])
        r.update(poisson_accept=B, theta_accept=B, paths=B, selected_SA=n, hits=n, hits_lo=n, hits_hi=n)
        return r

    def make(d, rate, pilot=None, cap=400, mi=MAX_INFLIGHT, tw=TARGET_WALL_H, wave="W1"):
        sp, mp = os.path.join(d, "settings.json"), os.path.join(d, "metric.json")
        json.dump({"outers": {"synthetic|toy/0": {"recorded": [5, 4, 0], "q": [], "radius": 1.0}},
                   "pops": {"synthetic": {"keep": [], "mad": []}}}, open(mp, "w"))
        st = {"index": 7, "pop": "synthetic", "outer": "toy/0", "n": 30, "E": {"n": 30, "k": 1, "r": 1, "rate": rate},
              "rate": BATCH / 3600 / 0.05, "cap_batches": cap, "prior_hpb": 0.5 * BATCH * 0.05, "wave": wave, "dir": "s00007",
              "library": "primary", "stream_tag": 2, "pilot": pilot}
        json.dump({"settings": [st], "metric_sha256": "m", "runner_sha256": "r", "min_shard_cpu_h": 0.0, "target_wall_h": tw,
                   "max_inflight": mi, "overshoot": OVERSHOOT}, open(sp, "w"))
        run = os.path.join(d, "run")
        for x in ("queue", "claimed", "sets/s00007", "lib", "workers"):
            os.makedirs(os.path.join(run, x), exist_ok=True)
        return sp, mp, run, st, os.path.join(run, "sets", "s00007")

    def seeded(d, rate, **kw):
        sp, mp, run, st, sdir = make(d, rate, **kw); b = json.load(open(sp))
        with held(sdir, "t:seed", fakeq):
            plan(st, sdir, run, b)
        return sp, mp, run, st, sdir

    def drive(d, rate, order_seed, **kw):
        sp, mp, run, st, sdir = seeded(d, rate, **kw)
        random.seed(order_seed)
        work(sp, mp, run, "W1", f"job{order_seed}[0].srv.0", time.time() + 3600, qstat=fakeq, des={})
        return sp, mp, run, st, sdir

    def lib(run):
        return open(os.path.join(run, "lib", "s00007.jsonl"), "rb").read()

    reasons = {}

    def collect_ok(sp, mp, run, name, tag=None):
        try:
            collect(sp, mp, run, "W1", os.path.join(run, name)); return True
        except SystemExit:
            if tag:
                reasons[tag] = json.load(open(os.path.join(run, name)))["errors"][0]
            return False

    try:
        with mock.patch.object(p2, "one_batch", fake):
            libs = []
            for s_ in (1, 2, 3):
                d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st, sdir = drive(d, 0.05, s_, mi=6, tw=1e-6)
                collect(sp, mp, run, "W1", os.path.join(d, "c.json")); libs.append(lib(run))
                nr = json.load(open(os.path.join(d, "c.json")))["rows"][0]["ranges"]
            d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st, sdir = drive(d, 0.05, 9, mi=1, tw=1e-6)
            collect(sp, mp, run, "W1", os.path.join(d, "c.json")); serial = lib(run)
            res["library_invariant_to_shard_plan_and_order"] = len(set(libs + [serial])) == 1 and serial.count(b"\n") == K
            res["parallel_plan_used_several_ranges"] = nr > 1
            d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st, sdir = drive(d, 0.0, 4, cap=40, mi=6, tw=1e-6)
            collect(sp, mp, run, "W1", os.path.join(d, "c.json")); c = json.load(open(os.path.join(d, "c.json")))
            res["zero_rate_setting_is_capped"] = c["status"]["CAPPED"] == 1 and c["rows"][0]["prefix_end_batch"] == 40
            # publication interrupted between the range marker and its ticket: re-planning republishes it exactly once
            d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st, sdir = make(d, 0.05, mi=4, tw=1e-6); b = json.load(open(sp))
            with mock.patch.object(me, "ticket_name", side_effect=KeyboardInterrupt("killed before the ticket")):
                try:
                    with held(sdir, "t:p", fakeq):
                        plan(st, sdir, run, b)
                except KeyboardInterrupt:
                    pass
            stranded = (len(ranges(sdir)), len(os.listdir(os.path.join(run, "queue"))))
            for _ in range(2):
                with held(sdir, "t:p", fakeq):
                    plan(st, sdir, run, b)
            tickets = sorted(os.listdir(os.path.join(run, "queue")))
            once = len({parse_ticket(t)[2] for t in tickets}) == len(tickets) == len(ranges(sdir))
            work(sp, mp, run, "W1", "jobP[0].srv.0", time.time() + 3600, qstat=fakeq, des={})
            res["interrupted_publication_republished_once"] = stranded == (1, 0) and once and collect_ok(sp, mp, run, "c.json") \
                and lib(run) == serial
            # owner-safe locks: an aged live owner is not displaced; a dead owner is; a late unlock cannot free a successor
            d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st, sdir = make(d, 0.05)
            A = lock(sdir, "t:A", fakeq); old = time.time() - 601; os.utime(os.path.join(sdir, "lock"), (old, old))
            got = []
            th = __import__("threading").Thread(target=lambda: got.append(lock(sdir, "t:B", fakeq)), daemon=True); th.start()
            th.join(1.0); res["aged_live_owner_not_displaced"] = not got
            unlock(A); th.join(5.0); res["successor_acquires_after_release"] = bool(got)
            Bk = got[0]; os.rename(os.path.join(sdir, "lock"), os.path.join(sdir, "lock.mv"))   # A's view: B considered gone
            C = lock(sdir, "t:C", fakeq)
            try:
                unlock(Bk); late = False
            except (RuntimeError, FileNotFoundError):
                late = True
            res["late_unlock_cannot_free_successor"] = late and json.load(open(os.path.join(sdir, "lock", "owner.json")))["owner"] == "t:C"
            unlock(C)
            pd = subprocess.Popen(["true"]); pd.wait()
            os.mkdir(os.path.join(sdir, "lock"))
            json.dump({"owner": "t:dead", "host": os.uname().nodename, "pid": pd.pid, "token": "x"}, open(os.path.join(sdir, "lock", "owner.json"), "w"))
            D = lock(sdir, "t:D", fakeq); res["dead_owner_lock_recovered"] = True; unlock(D)
            # two contenders both observe the same ended generation before either reclaims (Astra 1800): one holder at a time
            import threading
            pd2 = subprocess.Popen(["true"]); pd2.wait()
            os.mkdir(os.path.join(sdir, "lock"))
            json.dump({"owner": "t:dead2", "host": os.uname().nodename, "pid": pd2.pid, "token": "dead2"},
                      open(os.path.join(sdir, "lock", "owner.json"), "w"))
            barrier, seen_t, guard = threading.Barrier(2), set(), threading.Lock()
            real_od = me.owner_dead

            def od(info, qstat=QSTAT):
                r_ = real_od(info, qstat)
                if info.get("token") == "dead2" and threading.get_ident() not in seen_t:
                    seen_t.add(threading.get_ident())
                    if barrier.wait(10) == 0:
                        time.sleep(0.3)      # acts on its stale observation only after the other contender has acquired
                return r_
            active, peak, done_ = [0], [0], []

            def contender(name):
                L_ = lock(sdir, name, fakeq)
                with guard:
                    active[0] += 1; peak[0] = max(peak[0], active[0])
                time.sleep(0.5)
                with guard:
                    active[0] -= 1
                unlock(L_); done_.append(name)
            with mock.patch.object(me, "owner_dead", od):
                ths = [threading.Thread(target=contender, args=(n_,), daemon=True) for n_ in ("t:A2", "t:B2")]
                for t_ in ths:
                    t_.start()
                for t_ in ths:
                    t_.join(30)
            res["concurrent_reclaim_one_holder_then_successor"] = peak[0] == 1 and sorted(done_) == ["t:A2", "t:B2"]
            live = lock(sdir, "t:live", fakeq)
            stale = {"owner": "t:old", "host": os.uname().nodename, "pid": pd2.pid, "token": "old-generation"}
            res["stale_observation_cannot_remove_successor"] = not _reclaim(os.path.join(sdir, "lock"), stale,
                {"owner": "t:r", "host": "h", "pid": os.getpid(), "token": "rtok"}, fakeq) and \
                _owner(os.path.join(sdir, "lock"))["owner"] == "t:live"
            unlock(live)
            os.mkdir(os.path.join(sdir, "lock")); os.mkdir(os.path.join(sdir, "lock.reclaim"))
            for x in ("lock", "lock.reclaim"):
                json.dump({"owner": "t:gone", "host": os.uname().nodename, "pid": pd2.pid, "token": x},
                          open(os.path.join(sdir, x, "owner.json"), "w"))
            try:
                lock(sdir, "t:E", fakeq); res["dead_reclaimer_fails_closed"] = False
            except LockStale:
                res["dead_reclaimer_fails_closed"] = os.path.isdir(os.path.join(sdir, "lock"))
            # stale claims: requeued only for a finished job, within the worker's own wave
            d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st, sdir = make(d, 0.05)
            open(os.path.join(run, "claimed", "W1_0000001_s00007_000000000_000000005@dead[1].srv.0"), "w").close()
            open(os.path.join(run, "claimed", "W1_0000001_s00007_000000005_000000010@live[2].srv.0"), "w").close()
            open(os.path.join(run, "claimed", "W2_0000001_s00007_000000010_000000015@dead[1].srv.0"), "w").close()
            fq = os.path.join(d, "qstat"); open(fq, "w").write("#!/bin/sh\ncase \"$3\" in dead*) echo '    job_state = F';; *) echo '    job_state = R';; esac\n")
            os.chmod(fq, 0o755)
            n = recover_stale(run, "me[0].srv.0", "W1", qstat=fq)
            res["stale_claim_requeued_only_for_finished_job_in_wave"] = n == 1 and os.listdir(os.path.join(run, "queue")) == \
                ["W1_0000001_s00007_000000000_000000005"]
            # a W2 worker does not take W1 tickets
            d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st, sdir = seeded(d, 0.05)
            res["wave_filter"] = work(sp, mp, run, "W2", "jobW[0].srv.0", time.time() + 3600, qstat=fakeq, des={})["shards"] == 0 \
                and len(os.listdir(os.path.join(run, "queue"))) >= 1
            # a worker killed mid-shard leaves its claim; once its job is finished the claim is requeued and resumed
            d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st, sdir = seeded(d, 0.05); calls = [0]

            def dies(*a_):
                calls[0] += 1
                if calls[0] == 4:
                    raise KeyboardInterrupt("worker killed")
                return fake(*a_)
            with mock.patch.object(p2, "one_batch", dies):
                try:
                    work(sp, mp, run, "W1", "jobA[0].srv.0", time.time() + 3600, qstat=fakeq, des={})
                except KeyboardInterrupt:
                    pass
            left = os.listdir(os.path.join(run, "claimed"))
            work(sp, mp, run, "W1", "jobB[0].srv.0", time.time() + 3600, qstat=fakeq, des={})
            res["killed_worker_claim_recovered_and_resumed"] = len(left) == 1 and left[0].endswith("@jobA[0].srv.0") and \
                collect_ok(sp, mp, run, "c.json") and lib(run) == serial
            res["no_claim_after_deadline"] = work(sp, mp, run, "W1", "jobC[0].srv.0", time.time() - 1, qstat=fakeq, des={})["shards"] == 0
            # collector rejections: a tampered journal; ranges not covered; identities outside committed batches; a bad
            # discarded shard (wrong binding, negative CPU) that never enters the library
            hp = os.path.join(sdir, f"sh{ranges(sdir)[0][0]:09d}_hits.jsonl")
            blob = open(hp, "rb").read(); open(hp, "wb").write(blob.replace(b"\"batch\": ", b"\"batch\":  ", 1))
            res["collector_rejects_tampered_journal"] = not collect_ok(sp, mp, run, "c2.json", "tampered_journal")
            open(hp, "wb").write(blob)

            def edit(sdir, a, fn, recs=None):
                ck = os.path.join(sdir, f"sh{a:09d}.json"); S = json.load(open(ck)); fn(S)
                if recs is not None:
                    data = "".join(json.dumps(r) + "\n" for r in recs).encode()
                    open(os.path.join(sdir, f"sh{a:09d}_hits.jsonl"), "wb").write(data)
                    S.update(journal_bytes=len(data), journal_sha256=hashlib.sha256(data).hexdigest(), hits=len(recs),
                             hits_lo=len(recs), hits_hi=len(recs), selected_SA=max(S["selected_SA"], len(recs)))
                json.dump(S, open(ck, "w"))
            d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st, sdir = drive(d, 0.05, 5, mi=6, tw=1e-6)
            a0, b0 = ranges(sdir)[0]
            edit(sdir, a0, lambda S: S.update(batches_done=1, proposals=BATCH))
            res["collector_rejects_uncovered_range"] = not collect_ok(sp, mp, run, "c3.json", "uncovered_range")
            d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st, sdir = drive(d, 0.05, 6, mi=6, tw=1e-6)
            a0, b0 = ranges(sdir)[0]
            recs = [{"batch": 9999, "proposal_in_batch": j, "boundary": False, "theta": {k: 0.5 for k in p2.PARAMS},
                     "recorded": [4, 3, 0]} for j in range(3)]
            edit(sdir, a0, lambda S: None, recs)
            res["collector_rejects_identity_outside_range"] = not collect_ok(sp, mp, run, "c4.json", "identity_outside_range")
            d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st, sdir = drive(d, 0.05, 7, mi=6, tw=1e-6)
            last = ranges(sdir)[-1][0]
            if shard_state(sdir, last) is None:
                p2.atomic_json(dict(shard_state(sdir, ranges(sdir)[0][0]), first_batch=last), os.path.join(sdir, f"sh{last:09d}.json"))
            edit(sdir, last, lambda S: S.update(binding={"other": 1}, cpu_seconds=-3600.0))
            res["collector_rejects_bad_discarded_shard"] = not collect_ok(sp, mp, run, "c5.json", "bad_discarded_shard")
            # a refused recovery (journal without a checkpoint) fails the setting and the worker carries on
            d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st, sdir = seeded(d, 0.05)
            a0 = sorted(parse_ticket(t)[2] for t in os.listdir(os.path.join(run, "queue")))[0]
            open(os.path.join(sdir, f"sh{a0:09d}_hits.jsonl"), "w").write("orphan\n")
            out_ = work(sp, mp, run, "W1", "jobD[0].srv.0", time.time() + 3600, qstat=fakeq, des={})
            res["refused_recovery_fails_setting_not_worker"] = terminal(sdir) == "FAILED" and out_["failed_shards"] >= 1 \
                and not os.listdir(os.path.join(run, "claimed"))
            # pilot prefix import refuses a journal that differs from the bound pilot collection
            d = tempfile.mkdtemp(dir=tmp); pdir = os.path.join(d, "pilot"); os.makedirs(pdir)
            data = b'{"x": 1}\n'
            S = {"batches_done": 3, "hits": 1, "journal_bytes": len(data), "journal_sha256": hashlib.sha256(data).hexdigest(),
                 "status": "complete", "proposals": 30, "cpu_seconds": 1.0}
            json.dump(S, open(os.path.join(pdir, "s0007.json"), "w")); open(os.path.join(pdir, "s0007_hits.jsonl"), "wb").write(b'{"x": 2}\n')
            sp, mp, run, st, sdir = make(d, 0.05, pilot=dict(S))
            try:
                seed(sp, pdir, run, "W1", qstat=fakeq); res["seed_rejects_altered_pilot_journal"] = False
            except SystemExit:
                res["seed_rejects_altered_pilot_journal"] = True
        # campaign account (Astra 1800): chronological replay; identity bound at first reservation; retries idempotent
        led = os.path.join(tmp, "ledger.tsv"); ceil = {"W1": 200000.0, "W2": 1000000.0, "campaign": 1200000.0}
        idA = "settings=x outdir=/r/run jobs=520 cpus=8 wall=172800"
        r1 = reserve(led, "s1b", ceil, "W1", "s1b_aaaa_a", 199688.0, idA)
        r2 = reserve(led, "s1b", ceil, "W1", "s1b_aaaa_a", 199688.0, idA)
        refused = []
        for args in (("W1", "s1b_aaaa_a", 200072.0, idA.replace("520", "521")),        # same name, other shape
                     ("W1", "s1b_bbbb_a", 199688.0, idA.replace("/r/run", "/r/run2"))):  # fresh directory
            try:
                reserve(led, "s1b", ceil, *args); refused.append(False)
            except SystemExit:
                refused.append(True)
        open(led, "a").write("release\ts1b_aaaa_a\tmanual: tracejob shows no job\n")
        r3 = reserve(led, "s1b", ceil, "W1", "s1b_aaaa_a", 199688.0, idA)                   # same-name retry after release
        try:
            reserve(led, "s1b", ceil, "W1", "s1b_bbbb_a", 199688.0, idA.replace("/r/run", "/r/run2")); after_release = False
        except SystemExit:
            after_release = True
        act = ledger_active(led, "s1b")
        res["campaign_account"] = r1["recorded"] and not r2["recorded"] and refused == [True, True] and r3["recorded"] \
            and after_release and list(act) == ["s1b_aaaa_a"] and act["s1b_aaaa_a"]["cpu_h"] == 199688.0
    finally:
        K, BATCH = saved
        shutil.rmtree(tmp, ignore_errors=True)
    res["all_ok"] = all(res.values())
    print(json.dumps(res | {"rejection_reasons": reasons}, indent=1))
    if not res["all_ok"]:
        raise SystemExit("tests failed")


if __name__ == "__main__":
    cmd, a = sys.argv[1], sys.argv[2:]
    {"export": export, "verify_export": verify_export, "settings": settings, "subset": subset, "seed": seed, "work": work,
     "collect": collect, "preflight": preflight, "test": test}[cmd](*a)
