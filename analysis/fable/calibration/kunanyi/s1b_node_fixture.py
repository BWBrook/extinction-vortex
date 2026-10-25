"""Fixtures for s1b_node.pbs (no PBS, no simulation), covering the acceptance cases of Codex's node-plan review
(notes/astra_r2_node_plan_review_20261023.md). The actual node script runs under FIX_BASH with stubs on PATH: `python`
plays each worker from a scripted plan (exit status, run time, file actions on the wave's queue and claims), and for
logical-clock cases `date +%s` and `sleep` share a clock file, `mv` can fail or apply-then-fail when publishing a
certificate, and `find` can fail like an NFS scan error. The many-slot idle cases run in real time with short settings.
Writes s1b_node_fixture[_FIX_TAG].json beside itself."""
import hashlib, json, os, subprocess, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
NODE = Path(os.environ.get("FIX_NODE", HERE / "s1b_node.pbs"))
T0 = 1_000_000

STUB = r'''
import fcntl, json, os, sys, time
st = os.environ["FIX_STATE"]; name = os.path.basename(sys.argv[0]); logical = os.path.exists(os.path.join(st, "logical"))
def locked(fn):
    with open(os.path.join(st, "lock"), "a") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX); return fn()
def clock(add=0):
    p = os.path.join(st, "clock"); c = int(open(p).read()) + add
    if add:
        open(p, "w").write(str(c))
        ev = json.load(open(os.path.join(st, "events.json")))
        for e in [e for e in ev if e["t"] <= c]:
            act(e["do"]); ev.remove(e)
        json.dump(ev, open(os.path.join(st, "events.json"), "w"))
    return c
def act(do):
    for op, path in do:
        full = os.path.join(os.environ["FIX_RUN"], path)
        if op == "mk": open(full, "w").close()
        elif op == "rm" and os.path.exists(full): os.remove(full)
def log(kind, **kw):
    with open(os.path.join(st, "calls.jsonl"), "a") as fh: fh.write(json.dumps(dict(kind=kind, **kw)) + "\n")
if name == "date":
    if "+%s" in sys.argv[1:] and logical:
        print(locked(clock)); sys.exit(0)
    os.execv("/bin/date", ["date"] + sys.argv[1:])
if name == "sleep":
    n = float(sys.argv[1]); log("sleep", secs=n)
    if logical: locked(lambda: clock(int(n))); sys.exit(0)
    time.sleep(n); sys.exit(0)
if name == "find":
    log("find", dir=sys.argv[1])
    cfg = json.load(open(os.path.join(st, "find_fail.json"))); until, every = cfg["until"], cfg.get("every", 0)
    def count():
        p = os.path.join(st, "find_n"); n = (int(open(p).read()) if os.path.exists(p) else 0) + 1
        open(p, "w").write(str(n)); return n
    n = locked(count)
    if (locked(clock) if logical else time.time()) < until or (every and n % every == 0):
        print("find: Stale file handle (fixture)", file=sys.stderr); sys.exit(1)
    os.execv("/usr/bin/find", ["find"] + sys.argv[1:])
if name == "mv":
    src, dst = sys.argv[-2], sys.argv[-1]; mode = open(os.path.join(st, "mv_mode")).read().strip()
    if "/workers/dead/" in dst and mode != "ok":
        if mode == "fail_once":
            open(os.path.join(st, "mv_mode"), "w").write("ok"); sys.exit(1)
        if mode == "apply_fail":
            os.rename(src, dst); sys.exit(1)
        sys.exit(1)
    os.rename(src, dst); sys.exit(0)
if name == "python":                       # a worker: argv ends with OWNER DEADLINE
    def nxt():
        p = os.path.join(st, "plan.json"); plan = json.load(open(p))
        step = plan.pop(0) if plan else {"rc": 0}; json.dump(plan, open(p, "w")); return step
    step = locked(nxt); start = locked(clock) if logical else time.time()
    log("launch", owner=sys.argv[-2], deadline=int(sys.argv[-1]), pid=os.getpid(), t=start)
    act(step.get("do", []))
    if step.get("run"):
        if logical: locked(lambda: clock(step["run"]))
        else: time.sleep(step["run"])
    sys.exit(step["rc"])
'''


def run_node(d, plan, jobid="job[0].fixture", cpus=1, logical=True, wall=172800, env=None, events=(), find_fail=0,
             mv="ok", queue=(), claims=(), fresh=True, find_every=0):
    base, st, run = d / "base", d / "state", d / "base/s1b/run"
    if fresh:
        for p in (run / "queue", run / "claimed", run / "submit_W1/logs", st, d / "bin", d / "tmp",
                  base / "src/analysis/fable/calibration/kunanyi"):
            p.mkdir(parents=True, exist_ok=True)
        (base / "src/analysis/fable/calibration/kunanyi/env.sh").write_text('cd "$VBASE/src"\n')
        for n in ("python", "date", "sleep", "find", "mv"):
            (d / "bin" / n).write_text(f"#!{sys.executable}\n{STUB}"); (d / "bin" / n).chmod(0o755)
    (st / "clock").write_text(str(T0)); (st / "lock").touch()
    (st / "logical").touch() if logical else (st / "logical").unlink(missing_ok=True)
    (st / "plan.json").write_text(json.dumps(plan)); (st / "events.json").write_text(json.dumps(list(events)))
    (st / "find_fail.json").write_text(json.dumps({"until": find_fail, "every": find_every})); (st / "mv_mode").write_text(mv)
    (st / "find_n").unlink(missing_ok=True)
    for q in queue:
        (run / "queue" / q).touch()
    for c in claims:
        (run / "claimed" / c).touch()
    e = dict(os.environ, VBASE=str(base), SETTINGS="unused.json", OUTDIR="run", WAVE="W1", TAG="W1", JOBCPUS=str(cpus),
             WALL_SECS=str(wall), PBS_JOBID=jobid, PBS_ARRAY_INDEX="0", PATH=f"{d / 'bin'}{os.pathsep}{os.environ['PATH']}",
             FIX_STATE=str(st), FIX_RUN=str(run), TMPDIR=str(d / "tmp"), POLL_SECS="300", IDLE_MAX_SECS="1800",
             JITTER_SECS="0", GRACE_SECS="30", REFILL_SECS="5", RETRY_SECS="10", MAX_FAIL="3", CERT_TRIES="3",
             MARGIN_SECS="1800", LAUNCH_CUTOFF_SECS="600")
    e.update(env or {})
    t = time.time()
    try:
        p = subprocess.run([os.environ.get("FIX_BASH", "bash"), str(NODE)], env=e, capture_output=True, text=True, timeout=60,
                           start_new_session=True)
    except subprocess.TimeoutExpired as ex:                   # a wrapper that never ends: kill its process group
        subprocess.run(["pkill", "-9", "-f", str(d)], check=False)
        p = subprocess.CompletedProcess(ex.cmd, "timeout", "", "")
    calls = [json.loads(x) for x in (st / "calls.jsonl").read_text().splitlines()] if (st / "calls.jsonl").exists() else []
    (st / "calls.jsonl").unlink(missing_ok=True)
    logs = "".join(f.read_text() for f in sorted((run / "submit_W1/logs").glob("w.*.log")))
    done = (run / "submit_W1/logs/done.0").read_text() if (run / "submit_W1/logs/done.0").exists() else ""
    return {"rc": p.returncode, "launches": [c for c in calls if c["kind"] == "launch"], "finds": sum(c["kind"] == "find" for c in calls),
            "sleeps": [c["secs"] for c in calls if c["kind"] == "sleep"], "log": logs, "done": done,
            "clock": int((st / "clock").read_text()) - T0, "real_s": time.time() - t, "run": run}


def certs_ok(r):
    dead = r["run"] / "workers/dead"
    for l in r["launches"]:
        c = json.loads((dead / l["owner"]).read_text())
        if (c["owner"], c["pid"]) != (l["owner"], l["pid"]):
            return False
    return True


def distinct(*rs):
    owners = [l["owner"] for r in rs for l in r["launches"]]
    return len(owners) == len(set(owners))


def gens(r):
    return [int(l["owner"].rsplit(".", 1)[1].split("r")[1].split("n")[0]) for l in r["launches"]]


def main():
    res, rec = {}, {}
    with tempfile.TemporaryDirectory() as td:
        def D(name):
            p = Path(td) / name; p.mkdir(); return p
        # 1. more than 20 consecutive exit-75 children, then success: refilled within time, distinct owners, certified
        r = run_node(D("a"), [{"rc": 75}] * 25 + [{"rc": 0}])
        res["exit75_refilled_without_cap_and_certified"] = len(r["launches"]) == 26 and gens(r) == list(range(26)) \
            and distinct(r) and certs_ok(r) and r["rc"] == 0 and "slots failed: 0" in r["done"] \
            and "/logs/" not in r["log"] and r["log"].count("exited 75 (owner uncertain); launching again") == 25
        # 2. non-75 failures interspersed with 75 and 0 (queued work present): finite budget, generations never reset
        r = run_node(D("b"), [{"rc": 3}, {"rc": 75}, {"rc": 0}, {"rc": 3}, {"rc": 75}, {"rc": 3}, {"rc": 0}], queue=["W1_t1"])
        res["non75_failures_have_a_finite_budget"] = len(r["launches"]) == 6 and gens(r) == list(range(6)) \
            and r["rc"] == 1 and "slots failed: 1" in r["done"] and "exited 3 (3 of 3)" in r["log"]
        # 3. after exit 0: queued work refills; claims only wait under the idle budget; empty retires; other wave ignored
        r = run_node(D("c1"), [{"rc": 0}, {"rc": 0, "do": [["rm", "queue/W1_t1"]]}], queue=["W1_t1"])
        q_only = len(r["launches"]) == 2 and "has no queued tickets or claims" in r["log"]
        r = run_node(D("c2"), [{"rc": 0}], claims=["W1_0000001_s00001_000000000_000000010@remote[1].x.0r0nab"])
        c_only = len(r["launches"]) == 1 and 1800 <= r["clock"] <= 1801 and "idle for 1800s with wave W1 inflight" in r["log"] \
            and len(r["sleeps"]) <= 8
        rec["claims_only_idle"] = {"logical_seconds": r["clock"], "polls": len(r["sleeps"]), "finds": r["finds"]}
        r = run_node(D("c3"), [{"rc": 0}])
        neither = len(r["launches"]) == 1 and r["clock"] == 30 and "has no queued tickets or claims" in r["log"]
        r = run_node(D("c4"), [{"rc": 0}], queue=["W2_t1"], claims=["W2_x@remote[1].x.0r0nab"])
        other = len(r["launches"]) == 1 and "has no queued tickets or claims" in r["log"]
        res["exit0_refills_on_queued_work_waits_on_claims_retires_when_empty"] = q_only and c_only and neither and other
        # 4. the last claim is requeued as a ticket between observations: the post-pause check finds the work
        r = run_node(D("d"), [{"rc": 0}, {"rc": 0, "do": [["rm", "queue/W1_s"]]}], claims=["W1_c@remote[1].x.0r0nab"],
                     events=[{"t": T0 + 400, "do": [["rm", "claimed/W1_c@remote[1].x.0r0nab"], ["mk", "queue/W1_s"]]}])
        res["work_published_between_observations_is_found"] = len(r["launches"]) == 2 and r["launches"][1]["t"] - T0 <= 700
        # 5. scan errors are unknown, never "empty": retried while failing; then queued work refills; persistent -> idle cap
        r = run_node(D("e1"), [{"rc": 0}, {"rc": 0, "do": [["rm", "queue/W1_t"]]}], queue=["W1_t"], find_fail=T0 + 700)
        transient = len(r["launches"]) == 2 and r["log"].count("has no queued tickets or claims") == 1 \
            and r["launches"][1]["t"] >= T0 + 700
        r = run_node(D("e2"), [{"rc": 0}], find_fail=T0 + 10 ** 7)
        persistent = len(r["launches"]) == 1 and "wave W1 unknown; slot retires" in r["log"] \
            and "has no queued tickets or claims" not in r["log"]
        res["scan_errors_are_unknown_never_empty"] = transient and persistent
        # 6. certificate publication: a persistent failure stops the slot visibly; an applied-but-failed rename reconciles
        r = run_node(D("f1"), [{"rc": 75}, {"rc": 0}], mv="fail")
        fail_stop = len(r["launches"]) == 1 and "could not be published; slot stops" in r["log"] and r["rc"] == 1
        r = run_node(D("f2"), [{"rc": 75}, {"rc": 0}], mv="apply_fail")
        applied = len(r["launches"]) == 2 and certs_ok(r) and r["rc"] == 0
        res["certificate_published_and_read_back_before_any_replacement"] = fail_stop and applied
        # 7. the same PBS job rerun, with repeated refills: every owner distinct and every certificate exact
        dg = D("g"); r1 = run_node(dg, [{"rc": 75}, {"rc": 75}, {"rc": 0}], jobid="same[0].fixture")
        r2 = run_node(dg, [{"rc": 75}, {"rc": 0}], jobid="same[0].fixture", fresh=False)
        res["rerun_and_refills_never_reuse_an_owner"] = distinct(r1, r2) and certs_ok(r1) and certs_ok(r2) \
            and r1["launches"][0]["owner"].rsplit("n", 1)[1] != r2["launches"][0]["owner"].rsplit("n", 1)[1]
        # 8. the deadline: passed at start; crossed in a pause; reached during a certificate retry. One deadline for all
        r = run_node(D("h1"), [{"rc": 0}], wall=2000)
        passed = len(r["launches"]) == 0
        r = run_node(D("h2"), [{"rc": 75, "run": 170397}, {"rc": 0}])       # cutoff T0 + 170,400; the 5 s pause crosses it
        crossed = len(r["launches"]) == 1 and r["clock"] == 170400
        r = run_node(D("h3"), [{"rc": 75, "run": 170395}, {"rc": 0}], mv="fail_once")   # the 10 s certificate retry crosses it
        in_retry = len(r["launches"]) == 1 and certs_ok(r)
        r = run_node(D("h4"), [{"rc": 75}, {"rc": 75, "run": 500}, {"rc": 0}])
        same = len({l["deadline"] for l in r["launches"]}) == 1 and r["launches"][0]["deadline"] == T0 + 172800 - 1800
        r = run_node(D("h5"), [{"rc": 75, "run": 170000}, {"rc": 0}])       # well before the cutoff: refilled as usual
        before = len(r["launches"]) == 2
        res["no_launch_after_the_cutoff_and_one_deadline"] = passed and crossed and in_retry and same and before
        # 9. eight idle slots, one remote claim, no queue (real time): the subjob retires after its idle budget
        fast = {"POLL_SECS": "1", "IDLE_MAX_SECS": "3", "GRACE_SECS": "1", "REFILL_SECS": "1", "RETRY_SECS": "1"}
        r = run_node(D("i1"), [{"rc": 0}] * 8, cpus=8, logical=False, env=fast, claims=["W1_c@remote[1].x.0r0nab"])
        idle = len(r["launches"]) == 8 and r["real_s"] < 15 and r["log"].count("idle for 3s with wave W1 inflight") == 8
        rec["idle_subjob"] = {"real_seconds": round(r["real_s"], 1), "launches": len(r["launches"]), "finds": r["finds"]}
        # ... while one sibling still works, idle slots keep the (already held) cores until it ends, then the budget runs
        r = run_node(D("i2"), [{"rc": 0, "run": 5}] + [{"rc": 0}] * 7, cpus=8, logical=False, env=fast,
                     claims=["W1_c@remote[1].x.0r0nab"])
        sib = len(r["launches"]) == 8 and r["real_s"] >= 7 and r["log"].count("slot retires") == 8   # 5 s + 3 s, 1 s clock
        rec["idle_with_busy_sibling"] = {"real_seconds": round(r["real_s"], 1), "finds": r["finds"]}
        res["idle_subjob_residence_is_bounded"] = idle and sib
        # 10. Codex 2391/2393: readings alternating empty and unknown (every third scan fails). Long before the cutoff the
        # idle budget still ends the wait; at the cutoff the slot retires instead of scanning without pause
        r = run_node(D("j1"), [{"rc": 0}], find_every=3, env={"IDLE_MAX_SECS": "30", "GRACE_SECS": "10"})
        j1 = r["rc"] == 0 and len(r["launches"]) == 1 and "idle for 30s" in r["log"] and r["finds"] <= 6 and r["clock"] <= 40 \
            and "has no queued tickets or claims" not in r["log"]
        r2 = run_node(D("j2"), [{"rc": 0}], find_every=3, wall=1800 + 600 + 10)
        j2 = r2["rc"] == 0 and len(r2["launches"]) == 1 and "launch cutoff reached while idle" in r2["log"] and r2["finds"] <= 4
        rec["empty_unknown_alternation"] = {"before_cutoff": {"logical_seconds": r["clock"], "finds": r["finds"]},
                                            "at_cutoff": {"logical_seconds": r2["clock"], "finds": r2["finds"]}}
        res["alternating_empty_unknown_bounded_by_idle_budget_and_cutoff"] = j1 and j2
    bv = subprocess.run([os.environ.get("FIX_BASH", "bash"), "-c", "echo $BASH_VERSION"], capture_output=True, text=True).stdout.strip()
    out = {"scope": __doc__, "bash_version": bv, "node_sha256": hashlib.sha256(NODE.read_bytes()).hexdigest(), "checks": res,
           "observations": rec, "all_ok": all(res.values())}
    tag = os.environ.get("FIX_TAG", "")
    (HERE / f"s1b_node_fixture{('_' + tag) if tag else ''}.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"bash_version": bv, "checks": res, "observations": rec, "all_ok": out["all_ok"]}, indent=1))
    sys.exit(0 if out["all_ok"] else 1)


if __name__ == "__main__":
    main()
