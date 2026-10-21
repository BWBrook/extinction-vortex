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
  select        SETTINGS OUT DIRS_FILE                           a round's settings: listed dirs, rebound to this runner
  seed          SETTINGS PILOT_DIR RUN WAVE                      import verified pilot prefixes; first tickets
  work          SETTINGS METRIC RUN WAVE OWNER DEADLINE_EPOCH    pull worker for one wave: claim, run, plan successors
  collect       SETTINGS METRIC RUN WAVE OUT_JSON                validate shards, assemble libraries, account CPU
  preflight     SETTINGS METRIC LEDGER ARRAY_NAME OUTDIR NJOBS JOBCPUS WALL_SECS WAVE   bound check, fixtures, reservation
  test                                                            synthetic fixtures (exit non-zero on failure)
Run directory RUN: queue/ (tickets), claimed/ (ticket@owner), sets/<dir>/ (pilot prefix, ranges/, shard checkpoints and
journals, COMPLETE/CAPPED/FAILED markers, lock/), lib/ (assembled libraries), workers/ (exit records; dead/ holds the
death certificates s1b_node.pbs writes for each worker process it has reaped). Every queue transition (claim, requeue,
release) and every plan happens under the setting's owner-safe lock; planning reconciles each unfinished range to exactly
one ticket or claim. On the shared NFS filesystem, stale-handle errors are retried and never end a worker; lock waits are
bounded, so a lock held by a crashed worker delays only its own setting. The per-setting cap is a fixed proposal budget (2,000 CPU-h equivalent at the bound
rate); allocated-CPU ceilings per wave and campaign are enforced by the reservation ledger. Run from the frozen source root."""
import errno, hashlib, json, math, os, random, shutil, subprocess, sys, tempfile, time
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
CLAIM_PATIENCE, LOCK_PATIENCE = 5.0, 600.0      # seconds a lock wait may last when claiming / when committing a shard
PBS_SUSPECT_SECS = 300.0         # a lock is checked against PBS only after this long, and each job at most this often
RECOVER_SECS = 600.0             # how often a worker requeues claims of certified-dead workers
PARK_SECS, BACKOFF_SECS, MAX_ERRORS = 60.0, 0.5, 30   # retry delay of an interrupted claim; error backoff and its limit
RETRY_SECS = 30.0                # a collector's pause before re-reading a setting that failed validation


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


def select(settings_path, out, dirs_path):
    """A later round's settings: the listed dirs of a bound settings file, every other field unchanged, rebound to this
    runner (a new binding, so a round never resumes another round's shards)."""
    b = json.load(open(settings_path)); want = [x.strip() for x in open(dirs_path) if x.strip()]
    st = [x for x in b["settings"] if x["dir"] in set(want)]
    if len(want) != len(set(want)) or len(st) != len(want):
        raise SystemExit("unknown or duplicate dir")
    b.update(settings=st, runner_sha256=p2.sha(os.path.abspath(__file__)), derived_from_sha256=p2.sha(settings_path),
             stage=b["stage"] + f" -- selected round ({len(st)} settings)")
    json.dump(b, open(out, "w"))
    print("select", out, p2.sha(out), len(st), {w: sum(x["wave"] == w for x in st) for w in WAVES})


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
def nfs(fn, *a, tries=6):
    """fn(*a), retrying NFS stale-handle errors: a path replaced by another client's rename between lookup and read."""
    for k in range(tries):
        try:
            return fn(*a)
        except OSError as ex:
            if ex.errno != errno.ESTALE or k == tries - 1:
                raise
            time.sleep(0.1 * (k + 1))


def _jread(path):
    with open(path) as fh:
        return json.load(fh)


def ls(path):
    return nfs(os.listdir, path)


def jload(path):
    return nfs(_jread, path)


def pid_alive(pid):
    try:
        os.kill(int(pid), 0); return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


_PBS = {}                        # (qstat, job) -> (time of query, finished); a finished answer is final


def certified(cert, info):
    """A death certificate for this exact owner: s1b_node.pbs writes workers/dead/<owner> ({owner, host, pid, rc}) after
    reaping the process. Owner names are unique per node invocation; for a lock (info with a pid) the certificate must
    also name the lock owner's host and pid."""
    own = info.get("owner")
    if not (cert and own):
        return False
    try:
        c = jload(os.path.join(cert, own))
    except (OSError, ValueError):
        return False
    return c.get("owner") == own and (info.get("pid") is None or (c.get("host"), c.get("pid")) == (info.get("host"), info.get("pid")))


def owner_dead(info, qstat=QSTAT, cert=None, pbs=True, deadline=math.inf):
    """Positive evidence only: a death certificate for the exact owner process, same host and pid gone, or (when pbs) the
    owner's PBS job reported finished (job_state F). Each job is queried at most once per PBS_SUSPECT_SECS, failed
    queries included, and never past the deadline."""
    if certified(cert, info):
        return True
    if info.get("host") == os.uname().nodename and info.get("pid") is not None:
        return not pid_alive(info["pid"])
    job = (info.get("owner") or "").rsplit(".", 1)[0]
    if not pbs or ("[" not in job and ".kunanyi" not in job):
        return False
    c = _PBS.get((qstat, job))
    if c and (c[1] or time.time() - c[0] < PBS_SUSPECT_SECS):
        return c[1]
    left = deadline - time.time()
    if left <= 1.0:
        return False
    _PBS[(qstat, job)] = (time.time(), False)
    try:
        out = subprocess.run([qstat, "-x", "-f", job], capture_output=True, text=True, timeout=min(60.0, left)).stdout
    except Exception:
        return False
    r = any(l.strip() == "job_state = F" for l in out.splitlines()); _PBS[(qstat, job)] = (time.time(), r)
    return r


class LockStale(RuntimeError):
    """A lock's owner and the reclaimer of that lock have both ended: fail closed for operator recovery."""


class LockBusy(RuntimeError):
    """A lock stayed with a live (not positively ended) owner for longer than the caller's patience."""


class OwnerUncertain(BaseException):
    """Releasing a held lock failed, so whether this process still owns it is unknown. Not caught by the worker: the
    process ends (exit 75) and its node script's death certificate lets other workers break the lock."""


def _owner(path):
    try:
        return jload(os.path.join(path, "owner.json"))
    except (OSError, ValueError):
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


def _reclaim(d, observed, me, qstat=QSTAT, cert=None, deadline=math.inf):
    """Break the ended generation `observed` of lock d. Only one reclaimer at a time (the d.reclaim mutex), and only while
    d still holds that generation's token: a stale observation can never remove a successor's lock. A reclaim mutex whose
    own owner has ended is not broken automatically (LockStale)."""
    r = f"{d}.reclaim"
    if not _publish(r, me):
        info = _owner(r)
        if info and owner_dead(info, qstat, cert, deadline=deadline):
            raise LockStale(f"{r}: reclaim mutex held by an ended owner; operator recovery needed")
        return False
    try:
        cur = _owner(d)
        if cur and cur["token"] == observed["token"] and owner_dead(cur, qstat, cert, deadline=deadline):
            os.rename(d, f"{d}.broken.{observed['token']}")
            return True
        return False
    finally:
        rel = f"{r}.rel.{me['token']}"
        os.rename(r, rel); shutil.rmtree(rel, ignore_errors=True)


def lock(sdir, owner, qstat=QSTAT, patience=None, deadline=math.inf):
    """Owner-safe lock: a directory holding owner.json, published by an atomic rename (never an empty directory, so a
    rename cannot replace a live one). It is broken only on positive evidence that its owner has ended, never on age,
    and only through _reclaim; unlock requires the acquiring token. PBS is asked about an owner only once the same lock
    generation has been seen for PBS_SUSPECT_SECS. A failed publication may still have taken effect (an NFS reply lost
    after the rename), so it stays unresolved until the lock's token is read: this call's token means acquired, a
    foreign token means contention. A wait longer than patience seconds, or past the deadline, raises LockBusy, or
    OwnerUncertain while the last publication is unresolved, so a lock this process may hold is never forgotten."""
    d = os.path.join(sdir, "lock"); cert = os.path.join(os.path.dirname(os.path.dirname(sdir)), "workers", "dead")
    me = {"owner": owner, "host": os.uname().nodename, "pid": os.getpid(), "token": os.urandom(8).hex()}
    t0, seen = time.time(), {}
    while True:
        if _publish(d, me):
            return d, me["token"]
        unresolved = True
        info = _owner(d)
        if info is not None and info.get("token") == me["token"]:
            return d, me["token"]
        if info is None:
            time.sleep(0.05)
        else:
            unresolved = False                          # a foreign owner's record: known contention
            first = seen.setdefault(info.get("token"), time.time())
            if owner_dead(info, qstat, cert, pbs=time.time() - first >= PBS_SUSPECT_SECS, deadline=deadline) \
                    and _reclaim(d, info, me, qstat, cert, deadline):
                continue
            time.sleep(0.05 + random.random() * 0.1)
        if (patience is not None and time.time() - t0 > patience) or time.time() > deadline:
            if unresolved:
                raise OwnerUncertain(f"{d}: publication outcome unknown and the owner record unreadable at the wait limit")
            raise LockBusy(f"{d}: held by a live owner past the wait limit")


def unlock(L):
    """Release by token. If reading the owner record or the releasing rename fails, ownership is uncertain:
    OwnerUncertain ends the process, whose certified death lets others break the lock (a retried rename could remove a
    successor's lock)."""
    d, token = L
    try:
        info = jload(os.path.join(d, "owner.json"))
    except OSError as ex:
        raise OwnerUncertain(f"{d}: owner record unreadable at release: {ex}")
    if info["token"] != token:
        raise RuntimeError(f"{d}: lock is not owned by this holder")
    rel = f"{d}.rel.{token}"
    try:
        os.rename(d, rel)
    except OSError as ex:
        raise OwnerUncertain(f"{d}: releasing rename failed: {ex}")
    shutil.rmtree(rel, ignore_errors=True)      # NFS keeps a silly-renamed file that a reader still holds


class held:
    def __init__(self, sdir, owner, qstat=QSTAT, patience=None, deadline=math.inf):
        self.args = (sdir, owner, qstat, patience, deadline)

    def __enter__(self):
        self.L = lock(*self.args); return self.L

    def __exit__(self, *exc):
        unlock(self.L)


def ranges(sdir):
    rd = os.path.join(sdir, "ranges")
    return sorted(tuple(int(x) for x in f.split("-")) for f in ls(rd)) if os.path.isdir(rd) else []


def shard_state(sdir, a):
    p = os.path.join(sdir, f"sh{a:09d}.json")
    return jload(p) if os.path.exists(p) else None


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
    live = None                                     # listed only when an unfinished range needs reconciling (O(1) seeding)

    def is_live(a, b_):
        nonlocal live
        if live is None:
            live = {n.rsplit("_", 2)[1] + "_" + n.rsplit("_", 2)[2] for n in ls(q) if f"_{st['dir']}_" in n}
            live |= {n.split("@")[0].rsplit("_", 2)[1] + "_" + n.split("@")[0].rsplit("_", 2)[2]
                     for n in ls(c) if f"_{st['dir']}_" in n}
        return f"{a:09d}_{b_:09d}" in live
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
            if not is_live(a, b_):
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
    for d in ("queue", "claimed", "sets", "lib", "workers", "workers/dead"):
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


def claim(run, owner, wave, qstat=QSTAT, deadline=math.inf):
    """Claim one of this wave's tickets (atomic rename) while holding its setting's lock: a random one of the first 32
    tickets in priority order among settings not yet found busy. A setting whose lock stays busy for CLAIM_PATIENCE (or
    awaits an operator) is passed over with all its tickets, and the scan continues past it until a ticket is claimed,
    every setting with tickets has been found busy, or the deadline passes. None means the wave has no tickets;
    LockBusy means it has tickets but none could be claimed."""
    q = os.path.join(run, "queue"); busy = set()
    while time.time() < deadline:
        names = sorted(n for n in ls(q) if n.startswith(f"{wave}_"))
        if not names:
            return None
        head = [t for t in names if parse_ticket(t)[1] not in busy][:32]
        if not head:
            raise LockBusy(f"no claimable ticket: all {len(busy)} settings with tickets are busy")
        random.shuffle(head)
        for t in head:
            d = parse_ticket(t)[1]
            if d in busy:
                continue
            if time.time() >= deadline:
                break
            try:
                with held(os.path.join(run, "sets", d), owner, qstat, CLAIM_PATIENCE, deadline):
                    try:
                        os.rename(os.path.join(q, t), os.path.join(run, "claimed", f"{t}@{owner}"))
                        return t
                    except FileNotFoundError:
                        continue
            except LockBusy:
                busy.add(d)
            except LockStale as ex:                      # that setting waits for an operator; others proceed
                busy.add(d); print(f"skipping {t}: {ex}", file=sys.stderr, flush=True)
    raise LockBusy("claim reached the deadline")


def recover_stale(run, owner, wave, qstat=QSTAT, pbs=True, deadline=math.inf):
    """Requeue this wave's claims whose owner has positively ended, under the setting lock: a death certificate, or
    (when pbs) the owning PBS job reported finished (job_state F). The scan stops at the deadline."""
    me = owner.rsplit(".", 1)[0]; cert = os.path.join(run, "workers", "dead"); seen, n = {}, 0
    for c in ls(os.path.join(run, "claimed")):
        if time.time() >= deadline:
            break
        t, own = c.split("@", 1); job = own.rsplit(".", 1)[0]
        if own == owner or not t.startswith(f"{wave}_"):
            continue
        if own not in seen:
            seen[own] = owner_dead({"owner": own, "host": None}, qstat, cert, pbs=pbs and job != me, deadline=deadline)
        if seen[own]:
            try:
                with held(os.path.join(run, "sets", parse_ticket(t)[1]), owner, qstat, CLAIM_PATIENCE, deadline):
                    try:
                        os.rename(os.path.join(run, "claimed", c), os.path.join(run, "queue", t)); n += 1
                    except FileNotFoundError:
                        pass
            except (LockStale, LockBusy) as ex:
                print(f"not requeued {c}: {ex}", file=sys.stderr, flush=True)
    return n


def adopt(run, owner, wave, parked):
    """This worker's own claims left by an interrupted iteration (a stale handle, a busy lock): (the one whose retry time
    has come first, or None; the earliest later retry time, or None)."""
    now = time.time()
    mine = [c.split("@", 1)[0] for c in ls(os.path.join(run, "claimed")) if c.split("@", 1)[1] == owner]
    mine = [t for t in mine if t.startswith(f"{wave}_") and parked.get(t, 0.0) != math.inf]
    ready = [t for t in mine if parked.get(t, 0.0) <= now]
    later = [parked[t] for t in mine if parked.get(t, 0.0) > now]
    return (min(ready, key=lambda t: parked.get(t, 0.0)) if ready else None), (min(later) if later else None)


def work(settings_path, metric_path, run, wave, owner, deadline, qstat=QSTAT, des=None):
    """Pull worker. An OSError in an iteration (an NFS stale handle that outlived its retries) or a lock that stays busy
    leaves the claim with this worker, which resumes it later from its checkpoint; MAX_ERRORS consecutive errors end it."""
    b = check(settings_path, metric_path) if des is None else json.load(open(settings_path))
    metric = json.load(open(metric_path)); des = des if des is not None else p2.designs()
    bind = binding(b, settings_path); by_dir = {s["dir"]: s for s in b["settings"]}
    deadline = float(deadline)
    done = {"shards": 0, "discarded_tickets": 0, "requeued_censored": 0, "stale_requeued": 0, "failed_shards": 0,
            "transient_errors": 0, "lock_busy": 0, "adopted": 0}
    parked, errs, last_rec = {}, 0, time.time()

    def patience():
        return max(5.0, min(LOCK_PATIENCE, deadline - time.time()))

    def run_ticket(t):
        _, d, a, b_ = parse_ticket(t)
        st, sdir, cpath = by_dir[d], os.path.join(run, "sets", d), os.path.join(run, "claimed", f"{t}@{owner}")
        if terminal(sdir):
            with held(sdir, owner, qstat, patience(), deadline + LOCK_PATIENCE):
                os.unlink(cpath)
            done["discarded_tickets"] += 1; return None
        end, h, crossing, _ = prefix(st, sdir)
        hs = K - h if end == a and not crossing else 10 ** 9
        mp = dict(metric["outers"][f"{st['pop']}|{st['outer']}"], keep=metric["pops"][st["pop"]]["keep"],
                  mad=metric["pops"][st["pop"]]["mad"])
        sst = {"index": st["index"], "pop": st["pop"], "outer": st["outer"], "n": st["n"], "E": st["E"],
               "stream_tag": st["stream_tag"], "proposal_budget": st["cap_batches"] * BATCH, "batches": b_ - a}
        fail = None
        try:
            S = p2.run_setting({"batch": BATCH, "hit_stop": hs, "_binding": bind}, sst, mp, sdir, deadline, des,
                               ckpt_secs=CKPT_SECS, first_batch=a, name=f"sh{a:09d}",
                               cancelled=lambda: os.path.exists(os.path.join(sdir, "COMPLETE")))
        except OSError as ex:
            if ex.errno in (errno.ESTALE, errno.EIO):      # transient: keep the claim; it resumes from its checkpoint
                raise
            fail = ex
        except (SystemExit, Exception) as ex:       # refused recovery or an unexpected error fails the setting, not the worker
            fail = ex
        if fail is not None:
            with held(sdir, owner, qstat, patience(), deadline + LOCK_PATIENCE):
                if not terminal(sdir):
                    mark(sdir, "FAILED", {"range": a, "failure": f"{type(fail).__name__}: {fail}"})
                os.unlink(cpath)
            done["failed_shards"] += 1; return None
        try:
            with held(sdir, owner, qstat, patience(), deadline + LOCK_PATIENCE):
                if S["status"] == "censored":
                    os.rename(cpath, os.path.join(run, "queue", t)); done["requeued_censored"] += 1
                else:
                    plan(st, sdir, run, b); os.unlink(cpath); done["shards"] += 1
        except LockStale as ex:                          # the claim stays; the setting is reported incomplete
            print(f"left claim {t}: {ex}", file=sys.stderr, flush=True); done["lock_stale"] = done.get("lock_stale", 0) + 1
            parked[t] = math.inf
        return S["status"]

    while time.time() < deadline:
        t = None
        try:
            if time.time() - last_rec >= RECOVER_SECS:
                done["stale_requeued"] += recover_stale(run, owner, wave, qstat, False, deadline); last_rec = time.time()
            t, later = adopt(run, owner, wave, parked)
            if t is not None:
                done["adopted"] += 1
            else:
                t = claim(run, owner, wave, qstat, deadline)
                if t is None:
                    done["stale_requeued"] += recover_stale(run, owner, wave, qstat, True, deadline)
                    t = claim(run, owner, wave, qstat, deadline)
                    if t is None:
                        if later is None:
                            break
                        time.sleep(max(0.0, min(60.0, max(1.0, later - time.time()), deadline - time.time()))); continue
            status = run_ticket(t); errs = 0
            if status == "censored":
                break
        except LockBusy as ex:
            done["lock_busy"] += 1; print(f"busy {t}: {ex}", file=sys.stderr, flush=True)
            if t is not None:
                parked[t] = time.time() + PARK_SECS
            else:
                time.sleep(max(0.0, min(BACKOFF_SECS * (10 + 20 * random.random()), deadline - time.time())))
        except OSError as ex:
            errs += 1; done["transient_errors"] += 1
            print(f"transient error at {t}: {type(ex).__name__}: {ex}", file=sys.stderr, flush=True)
            if t is not None:
                parked[t] = time.time() + PARK_SECS
            if errs >= MAX_ERRORS:
                raise
            time.sleep(max(0.0, min(60.0, BACKOFF_SECS * 2 ** errs, deadline - time.time())))
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
    """Validate every setting of the wave and assemble its libraries. OUT is collect_<TAG>.json; its log and pack list are
    collect_<TAG>.log and pack_<TAG>.txt in RUN, so collections of a wave's arrays never share files. A collection taken
    while any worker of the wave may still run is a snapshot: the settings that fail validation are re-read once, after a
    single RETRY_SECS pause, and only a collection taken after every array of the wave has ended is authoritative."""
    p2.atomic_json({"collection_ok": False, "state": "collecting"}, out)
    base = os.path.basename(out)
    tag = base[len("collect_"):-len(".json")] if base.startswith("collect_") and base.endswith(".json") else wave
    b = json.load(open(settings_path)); bind = binding(b, settings_path); metric = json.load(open(metric_path))
    rows, errors = [], []
    status = {"COMPLETE": 0, "CAPPED": 0, "FAILED": 0, "incomplete": 0}

    def one(st, sdir, row):
        L = len(metric["outers"][f"{st['pop']}|{st['outer']}"]["recorded"])
        pl = st["pilot"]; lines = []; useful = discarded = 0.0
        p0 = pl["batches_done"] if pl else 0
        if pl:
            S = jload(os.path.join(sdir, "pilot.json"))
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
        return row

    def attempt(st):
        ident = {k: st[k] for k in ("dir", "index", "pop", "outer", "n", "library")}
        try:
            return one(st, os.path.join(run, "sets", st["dir"]), dict(ident)), None
        except Exception as ex:
            return dict(ident, status="invalid"), f"{st['dir']}: {type(ex).__name__}: {ex}"
    wave_st = [st for st in b["settings"] if st["wave"] == wave]
    got = [attempt(st) for st in wave_st]
    if any(e for _, e in got):                            # one pause, then a single re-read of the settings that failed
        time.sleep(RETRY_SECS)
        got = [attempt(st) if e else (r, e) for st, (r, e) in zip(wave_st, got)]
    for row, e in got:
        if e:
            errors.append(e)
        else:
            status[row["status"]] += 1
        rows.append(row)
    summary = {"collection_ok": not errors, "wave": wave, "binding": bind, "status": status, "n_errors": len(errors),
               "errors": errors[:1000], "useful_cpu_h": sum(r.get("useful_cpu_h", 0) for r in rows),
               "discarded_cpu_h": sum(r.get("discarded_cpu_h", 0) for r in rows),
               "incomplete": [r["dir"] for r in rows if r["status"] == "incomplete"],
               "queue_left": len(ls(os.path.join(run, "queue"))), "claims_left": len(ls(os.path.join(run, "claimed"))),
               "tag": tag, "rows": rows}
    p2.atomic_json(summary, out)
    pack = [os.path.relpath(out, run), f"collect_{tag}.log"] + [f"lib/{r['dir']}.jsonl" for r in rows if r.get("library_sha256")]
    fd, tmpf = tempfile.mkstemp(dir=run, prefix=".tmp_")
    with os.fdopen(fd, "w") as fh:
        fh.write("\n".join(pack) + "\n")
    os.replace(tmpf, os.path.join(run, f"pack_{tag}.txt"))
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
    global K, BATCH, RETRY_SECS
    me = sys.modules[__name__]; res = {}; tmp = tempfile.mkdtemp(); saved = (K, BATCH, RETRY_SECS)
    K, BATCH, RETRY_SECS = 25, 10, 0.0

    def certify(run, owner, host, pid):                  # what s1b_node.pbs writes after reaping a worker process
        os.makedirs(os.path.join(run, "workers", "dead"), exist_ok=True)
        json.dump({"owner": owner, "host": host, "pid": pid, "rc": 137}, open(os.path.join(run, "workers", "dead", owner), "w"))
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

            def od(info, qstat=QSTAT, *a_, **kw_):
                r_ = real_od(info, qstat, *a_, **kw_)
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
            # NFS stale handles (W1, 21 Oct: 97 workers ended by ESTALE): reads are retried; one that outlives its retries in
            # bookkeeping parks the claim, which the same worker resumes from its checkpoint; the library is unchanged
            d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st, sdir = seeded(d, 0.05, mi=4, tw=1e-6)
            real_read, real_plan, nread, nplan = me._jread, me.plan, [0], [0]

            def flaky_read(p_):
                nread[0] += 1
                if nread[0] % 3 == 0:
                    raise OSError(errno.ESTALE, "Stale file handle (fixture)")
                return real_read(p_)

            def flaky_plan(*a_):
                nplan[0] += 1
                if nplan[0] == 2:
                    raise OSError(errno.ESTALE, "Stale file handle (fixture, past its retries)")
                return real_plan(*a_)
            with mock.patch.object(me, "_jread", flaky_read), mock.patch.object(me, "plan", flaky_plan), \
                    mock.patch.object(me, "PARK_SECS", 0.0), mock.patch.object(me, "BACKOFF_SECS", 0.0):
                out_ = work(sp, mp, run, "W1", "jobS[0].srv.0r0", time.time() + 3600, qstat=fakeq, des={})
            res["stale_handles_retried_and_parked_claim_resumed"] = out_["transient_errors"] == 1 and out_["adopted"] == 1 \
                and nread[0] >= 3 and collect_ok(sp, mp, run, "c.json") and lib(run) == serial \
                and not os.listdir(os.path.join(run, "claimed"))
            # a lock held by a live owner on another host: claims pass over it within CLAIM_PATIENCE and PBS is not asked;
            # after PBS_SUSPECT_SECS PBS is asked at most once per interval; a death certificate breaks it without PBS
            d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st, sdir = seeded(d, 0.05, mi=2)
            qlog, fqR = os.path.join(d, "qstat.log"), os.path.join(d, "qstatR")
            open(fqR, "w").write(f"#!/bin/sh\necho x >> {qlog}\necho '    job_state = R'\n"); os.chmod(fqR, 0o755)
            os.mkdir(os.path.join(sdir, "lock"))
            json.dump({"owner": "live[3].kunanyi-ohpc.0r0", "host": "elsewhere", "pid": 1, "token": "busy"},
                      open(os.path.join(sdir, "lock", "owner.json"), "w"))
            t0_ = time.time(); got_ = "unset"
            with mock.patch.object(me, "CLAIM_PATIENCE", 0.5):
                try:
                    got_ = claim(run, "jobQ[0].srv.0r0", "W1", qstat=fqR)
                except LockBusy:
                    got_ = "busy"
                os.makedirs(os.path.join(run, "sets", "s00008", "lock"))      # a second setting, first in priority, blocked too
                json.dump({"owner": "live[4].kunanyi-ohpc.0r0", "host": "elsewhere", "pid": 1, "token": "busy8"},
                          open(os.path.join(run, "sets", "s00008", "lock", "owner.json"), "w"))
                for j in range(40):
                    open(os.path.join(run, "queue", f"W1_0000001_s00008_{j * 5:09d}_{j * 5 + 5:09d}"), "w").close()
                shutil.rmtree(os.path.join(sdir, "lock"))                    # s00007 freed: claimed past s00008's 40 tickets
                got2 = claim(run, "jobQ[0].srv.0r0", "W1", qstat=fqR)
            res["busy_lock_passed_over_without_pbs_queries"] = got_ == "busy" and time.time() - t0_ < 15 and not os.path.exists(qlog) \
                and got2 is not None and "_s00007_" in got2
            os.rename(os.path.join(run, "claimed", f"{got2}@jobQ[0].srv.0r0"), os.path.join(run, "queue", got2))
            os.mkdir(os.path.join(sdir, "lock"))
            json.dump({"owner": "live[3].kunanyi-ohpc.0r0", "host": "elsewhere", "pid": 1, "token": "busy"},
                      open(os.path.join(sdir, "lock", "owner.json"), "w"))
            _PBS.clear(); n_q = -1
            with mock.patch.object(me, "PBS_SUSPECT_SECS", 0.4):
                try:
                    lock(sdir, "jobQ[0].srv.1r0", fqR, patience=1.0)
                except LockBusy:
                    n_q = len(open(qlog).read().splitlines()) if os.path.exists(qlog) else 0
            res["pbs_asked_at_most_once_per_interval"] = n_q in (1, 2)
            os.remove(qlog); certify(run, "live[3].kunanyi-ohpc.0r0", "elsewhere", 1)
            L_ = lock(sdir, "jobQ[0].srv.2r0", fqR, patience=5.0); unlock(L_)
            res["certified_dead_owner_lock_broken_without_pbs"] = not os.path.exists(qlog)
            # a crashed worker's claim, its job still running: requeued through its death certificate and resumed
            d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st, sdir = seeded(d, 0.05); calls = [0]
            fqR2 = os.path.join(d, "qstatR"); open(fqR2, "w").write("#!/bin/sh\necho '    job_state = R'\n"); os.chmod(fqR2, 0o755)
            with mock.patch.object(p2, "one_batch", dies):
                try:
                    work(sp, mp, run, "W1", "jobL[0].kunanyi-ohpc.0r0", time.time() + 3600, qstat=fqR2, des={})
                except KeyboardInterrupt:
                    pass
            left = os.listdir(os.path.join(run, "claimed"))
            certify(run, "jobL[0].kunanyi-ohpc.0r0", os.uname().nodename, 0)
            with mock.patch.object(me, "RECOVER_SECS", 0.0):
                out_ = work(sp, mp, run, "W1", "jobL[0].kunanyi-ohpc.1r0", time.time() + 3600, qstat=fqR2, des={})
            res["crashed_worker_claim_recovered_by_certificate_while_job_live"] = len(left) == 1 and out_["stale_requeued"] >= 1 \
                and collect_ok(sp, mp, run, "c.json") and lib(run) == serial
            # Codex 2142, 1: a certificate names one process incarnation. An old certificate under the same owner name but
            # another pid never breaks a live owner's lock
            d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st, sdir = seeded(d, 0.05, mi=2)
            pd3 = subprocess.Popen(["true"]); pd3.wait()
            certify(run, "same[0].kunanyi-ohpc.0r0n1", os.uname().nodename, pd3.pid)
            os.mkdir(os.path.join(sdir, "lock"))
            json.dump({"owner": "same[0].kunanyi-ohpc.0r0n1", "host": os.uname().nodename, "pid": os.getpid(), "token": "live"},
                      open(os.path.join(sdir, "lock", "owner.json"), "w"))
            try:
                lock(sdir, "thief[1].kunanyi-ohpc.0r0n2", fakeq, patience=0.5); stolen = True
            except LockBusy:
                stolen = False
            res["stale_certificate_cannot_break_a_live_incarnation"] = not stolen and _owner(os.path.join(sdir, "lock"))["token"] == "live"
            # Codex 2142, 2: a failed releasing rename ends the worker (OwnerUncertain) instead of leaving it waiting on its
            # own lock; its certified death lets the next worker break the lock and finish the setting
            d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st, sdir = seeded(d, 0.05, mi=2); fired = []
            real_rename = os.rename

            def bad_rename(src, dst):
                if ".rel." in str(dst) and str(src).endswith(os.path.join("s00007", "lock")) and not fired:
                    fired.append(dst); raise OSError(errno.ESTALE, "Stale file handle (fixture, at release)")
                return real_rename(src, dst)
            with mock.patch.object(os, "rename", bad_rename):
                try:
                    work(sp, mp, run, "W1", "jobU[0].kunanyi-ohpc.0r0n1", time.time() + 3600, qstat=fakeq, des={}); ended = False
                except OwnerUncertain:
                    ended = True
            held_by = _owner(os.path.join(sdir, "lock"))
            certify(run, held_by["owner"], held_by["host"], held_by["pid"])
            out_ = work(sp, mp, run, "W1", "jobU[0].kunanyi-ohpc.1r0n1", time.time() + 3600, qstat=fakeq, des={})
            res["uncertain_release_ends_worker_and_lock_is_recovered"] = ended and len(fired) == 1 \
                and held_by["owner"] == "jobU[0].kunanyi-ohpc.0r0n1" and collect_ok(sp, mp, run, "c.json") and lib(run) == serial
            # Codex 2156: a publication that took effect but reported ESTALE, then an owner-record read outage. Short
            # (1 s, within the read retries): the token is reconciled and the worker completes. Long (3 s, past retries
            # and claim patience): the wait ends in OwnerUncertain, never LockBusy with the token forgotten; once reads
            # recover the certified process's lock is broken and the setting completes
            outcomes = {}
            for name, burst in (("short", 1.0), ("long", 3.0)):
                d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st, sdir = seeded(d, 0.05, mi=2); fired, t_out = [], [0.0]
                lk = os.path.join(sdir, "lock")

                def lost_reply(src, dst):
                    if str(dst) == lk and ".new." in str(src) and not fired:
                        real_rename(src, dst); fired.append(dst); t_out[0] = time.time() + burst
                        raise OSError(errno.ESTALE, "Stale file handle (fixture: lock published, reply lost)")
                    return real_rename(src, dst)

                def outage(p_):
                    if p_ == os.path.join(lk, "owner.json") and time.time() < t_out[0]:
                        raise OSError(errno.ESTALE, "Stale file handle (fixture: owner record unreadable)")
                    return real_read(p_)
                with mock.patch.object(os, "rename", lost_reply), mock.patch.object(me, "_jread", outage), \
                        mock.patch.object(me, "CLAIM_PATIENCE", 0.5):
                    try:
                        work(sp, mp, run, "W1", f"job{name}[0].kunanyi-ohpc.0r0n1", time.time() + 3600, qstat=fakeq, des={})
                        ended = False
                    except OwnerUncertain:
                        ended = True
                time.sleep(max(0.0, t_out[0] - time.time()))
                held_by = _owner(lk)
                if ended and held_by:
                    certify(run, held_by["owner"], held_by["host"], held_by["pid"])
                    work(sp, mp, run, "W1", f"job{name}[0].kunanyi-ohpc.1r0n1", time.time() + 3600, qstat=fakeq, des={})
                outcomes[name] = (ended, len(fired), held_by["owner"] if held_by else None,
                                  collect_ok(sp, mp, run, "c.json") and lib(run) == serial)
            res["uncertain_acquisition_reconciled_or_ended_and_recovered"] = \
                outcomes["short"] == (False, 1, None, True) and outcomes["long"] == (True, 1, "joblong[0].kunanyi-ohpc.0r0n1", True)
            # control: a known foreign live owner still yields LockBusy, never OwnerUncertain
            d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st, sdir = seeded(d, 0.05, mi=2)
            os.mkdir(os.path.join(sdir, "lock"))
            json.dump({"owner": "live[5].kunanyi-ohpc.0r0n9", "host": "elsewhere", "pid": 1, "token": "busy5"},
                      open(os.path.join(sdir, "lock", "owner.json"), "w"))
            try:
                lock(sdir, "jobF[0].kunanyi-ohpc.0r0n1", fakeq, patience=0.5); kind = "acquired"
            except LockBusy:
                kind = "LockBusy"
            except OwnerUncertain:
                kind = "OwnerUncertain"
            res["known_foreign_owner_is_contention_not_uncertainty"] = kind == "LockBusy"
            # Codex 2142, 3: six busy settings with 28 tickets each ahead of one healthy setting: claim reaches it
            d = tempfile.mkdtemp(dir=tmp); run = os.path.join(d, "run")
            for x in ("queue", "claimed", "workers/dead"):
                os.makedirs(os.path.join(run, x))
            for i in range(7):
                sd_ = os.path.join(run, "sets", f"s{i:05d}"); os.makedirs(sd_)
                if i < 6:
                    os.mkdir(os.path.join(sd_, "lock"))
                    json.dump({"owner": f"ghost[{i}].elsewhere.0r0", "host": "elsewhere", "pid": 1, "token": f"g{i}"},
                              open(os.path.join(sd_, "lock", "owner.json"), "w"))
                for j in range(28 if i < 6 else 1):
                    open(os.path.join(run, "queue", f"W1_0000001_s{i:05d}_{j:09d}_{j + 1:09d}"), "w").close()
            with mock.patch.object(me, "CLAIM_PATIENCE", 0.1):
                got3 = claim(run, "reader[0].kunanyi-ohpc.0r0", "W1", qstat="/bin/false")
            res["busy_frontier_cannot_hide_a_healthy_setting"] = got3 == "W1_0000001_s00006_000000000_000000001"
            # Codex 2142, 4: the worker deadline bounds a whole recovery scan; failed PBS queries are cached
            d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st, sdir = seeded(d, 0.05)
            for t_ in os.listdir(os.path.join(run, "queue")):
                os.remove(os.path.join(run, "queue", t_))
            certify(run, "ended[0].kunanyi-ohpc.0r0", "elsewhere", 1)
            for i in range(14):
                sd_ = os.path.join(run, "sets", f"s{i + 100:05d}"); os.makedirs(os.path.join(sd_, "lock"))
                json.dump({"owner": f"busy[{i}].elsewhere.0r0", "host": "elsewhere", "pid": 1, "token": f"b{i}"},
                          open(os.path.join(sd_, "lock", "owner.json"), "w"))
                for j in range(28):
                    open(os.path.join(run, "claimed", f"W1_0000001_s{i + 100:05d}_{j:09d}_{j + 1:09d}@ended[0].kunanyi-ohpc.0r0"), "w").close()
            t0_ = time.time()
            with mock.patch.object(me, "CLAIM_PATIENCE", 0.2), mock.patch.object(me, "BACKOFF_SECS", 0.0):
                work(sp, mp, run, "W1", "late[0].kunanyi-ohpc.0r0", t0_ + 2.0, qstat=fakeq, des={})
            res["deadline_bounds_recovery_scan"] = time.time() - t0_ < 6.0
            slowq, qlog2 = os.path.join(d, "qstat_slow"), os.path.join(d, "slow.log")
            open(slowq, "w").write(f"#!/bin/sh\necho x >> {qlog2}\nsleep 5\n"); os.chmod(slowq, 0o755)
            _PBS.clear(); t0_ = time.time()
            answers = [owner_dead({"owner": "slow[0].kunanyi-ohpc.0r0", "host": "elsewhere"}, slowq, deadline=t0_ + 1.5)
                       for _ in range(4)]
            res["failed_pbs_query_cached_and_deadline_clipped"] = answers == [False] * 4 and time.time() - t0_ < 4.0 \
                and len(open(qlog2).read().splitlines()) == 1
            # collector: pack list and log isolated per tag; a setting changing while read is retried once
            d = tempfile.mkdtemp(dir=tmp); sp, mp, run, st, sdir = drive(d, 0.05, 8, mi=4, tw=1e-6)
            for tg in ("W1_b", "W1_c"):
                collect(sp, mp, run, "W1", os.path.join(run, f"collect_{tg}.json"))
            pk = open(os.path.join(run, "pack_W1_b.txt")).read().split()
            res["collector_pack_and_log_isolated_per_tag"] = pk[:2] == ["collect_W1_b.json", "collect_W1_b.log"] \
                and open(os.path.join(run, "pack_W1_c.txt")).read().split()[:2] == ["collect_W1_c.json", "collect_W1_c.log"]
            os.rename(os.path.join(sdir, "COMPLETE"), os.path.join(d, "COMPLETE.held"))
            real_time = me.time

            class Pause:                                      # the marker lands while the collector pauses before re-reading
                time = staticmethod(real_time.time)

                @staticmethod
                def sleep(x):
                    os.rename(os.path.join(d, "COMPLETE.held"), os.path.join(sdir, "COMPLETE"))
            with mock.patch.object(me, "time", Pause):
                ok_retry = collect_ok(sp, mp, run, "c_retry.json")
            res["collector_retries_a_setting_changed_while_read"] = ok_retry and lib(run) == serial
            sp3 = os.path.join(d, "settings3.json"); b3 = json.load(open(sp)); base_st = b3["settings"][0]
            b3["settings"] = [dict(base_st, dir=f"s0900{i}", index=900 + i) for i in range(3)]; json.dump(b3, open(sp3, "w"))
            for i in range(3):
                os.makedirs(os.path.join(run, "sets", f"s0900{i}")); open(os.path.join(run, "sets", f"s0900{i}", "COMPLETE"), "w").close()
            pauses = []

            class Count:
                time = staticmethod(real_time.time)

                @staticmethod
                def sleep(x):
                    pauses.append(x)
            with mock.patch.object(me, "time", Count):
                collect_ok(sp3, mp, run, "c_wide.json")
            wide = json.load(open(os.path.join(run, "c_wide.json")))
            res["collector_pauses_once_for_a_wave_wide_failure"] = len(pauses) == 1 and wide["n_errors"] == 3
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
        K, BATCH, RETRY_SECS = saved
        shutil.rmtree(tmp, ignore_errors=True)
    res["all_ok"] = all(res.values())
    print(json.dumps(res | {"rejection_reasons": reasons}, indent=1))
    if not res["all_ok"]:
        raise SystemExit("tests failed")


if __name__ == "__main__":
    cmd, a = sys.argv[1], sys.argv[2:]
    try:
        {"export": export, "verify_export": verify_export, "settings": settings, "subset": subset, "select": select,
         "seed": seed, "work": work, "collect": collect, "preflight": preflight, "test": test}[cmd](*a)
    except OwnerUncertain as ex:                  # end now; the node script certifies this process and restarts the slot
        print(f"owner uncertain, ending: {ex}", file=sys.stderr, flush=True)
        sys.exit(75)
