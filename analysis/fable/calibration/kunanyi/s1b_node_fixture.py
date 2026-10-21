"""Fixtures for s1b_node.pbs (no PBS, no simulation), after Codex's node-identity reproduction (board 2142). The actual
node script runs under FIX_BASH with a stub `python` on PATH that plays the worker; lock functions are the runner's
own, loaded by AST without its scientific imports. Writes s1b_node_fixture[_FIX_TAG].json beside itself.
 1. Two invocations with one PBS job identity (a rerun): owner names differ, each reaped process has a certificate
    naming its host, pid and exit status, and the first invocation's certificate never breaks the second's live lock.
 2. A worker that exits non-zero is restarted under a new owner name; both processes are certified; done file written."""
import ast, errno, hashlib, json, math, os, random, shutil, subprocess, sys, tempfile, time, types
from pathlib import Path

HERE = Path(__file__).resolve().parent
NODE = Path(os.environ.get("FIX_NODE", HERE / "s1b_node.pbs")); P3 = HERE.parent / "v2_dev" / "p3_stage1b.py"


def load():
    p = types.ModuleType("runner_lock_functions")
    p.__dict__.update(__file__=str(P3), p2=types.SimpleNamespace(), errno=errno, hashlib=hashlib, json=json, math=math,
                      os=os, random=random, shutil=shutil, subprocess=subprocess, sys=sys, tempfile=tempfile, time=time)
    nodes = [n for n in ast.parse(P3.read_text()).body if isinstance(n, (ast.Assign, ast.FunctionDef, ast.ClassDef))]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(P3), "exec"), p.__dict__)
    return p


def worker():                                    # the stub python: argv ends with OWNER DEADLINE
    state, owner = Path(os.environ["FIX_STATE"]), sys.argv[-2]
    with open(state / "owners.jsonl", "a") as fh:
        fh.write(json.dumps({"owner": owner, "pid": os.getpid()}) + "\n")
    mode = os.environ["FIX_MODE"]
    if mode == "exit":
        return 0
    if mode == "crash_once":
        flag = state / "crashed"
        if not flag.exists():
            flag.touch(); sys.exit(3)
        return 0
    p = load(); L = p.lock(os.environ["FIX_SDIR"], owner)            # mode "hold": take the lock, keep it until told
    (state / "holding").write_text(json.dumps({"owner": owner, "pid": os.getpid(), "token": L[1]}))
    t_end = time.time() + 20
    while not (state / "release").exists() and time.time() < t_end:
        time.sleep(0.02)
    p.unlock(L); (state / "released").touch()


def node(d, mode, jobid, bash):
    base, state = d / "base", d / "state"
    env = dict(os.environ, VBASE=str(base), SETTINGS="unused.json", OUTDIR="run", WAVE="W1", TAG="W1", JOBCPUS="1",
               WALL_SECS="3600", PBS_JOBID=jobid, PBS_ARRAY_INDEX="0", PATH=f"{d / 'bin'}{os.pathsep}{os.environ['PATH']}",
               FIX_SCRIPT=str(Path(__file__).resolve()), FIX_STATE=str(state), FIX_SDIR=str(base / "s1b/run/sets/s00007"),
               FIX_MODE=mode)
    return subprocess.Popen([bash, str(NODE)], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def setup(d):
    base = d / "base"; (base / "s1b/run/sets/s00007").mkdir(parents=True); (base / "s1b/run/submit_W1/logs").mkdir(parents=True)
    env_sh = base / "src/analysis/fable/calibration/kunanyi/env.sh"; env_sh.parent.mkdir(parents=True)
    env_sh.write_text('cd "$VBASE/src"\n'); (d / "state").mkdir(); (d / "bin").mkdir()
    stub = d / "bin/python"; stub.write_text(f'#!/bin/sh\nexec {sys.executable} "$FIX_SCRIPT" worker "$@"\n'); stub.chmod(0o755)
    return base / "s1b/run"


def cert(run, owner):
    return json.loads((run / "workers/dead" / owner).read_text())


def main():
    bash = os.environ.get("FIX_BASH", "bash"); res = {}
    with tempfile.TemporaryDirectory() as td:
        d = Path(td); run = setup(d); state = d / "state"
        first = node(d, "exit", "same[0].fixture", bash); first.communicate(timeout=30)
        o1 = json.loads((state / "owners.jsonl").read_text().splitlines()[0])
        second = node(d, "hold", "same[0].fixture", bash)
        t0 = time.time()
        while not (state / "holding").exists() and time.time() - t0 < 20:
            time.sleep(0.05)
        o2 = json.loads((state / "holding").read_text()); p = load()
        try:
            p.lock(str(run / "sets/s00007"), "thief[1].fixture.0r0nfeed", patience=1.0); stolen = True
        except p.LockBusy:
            stolen = False
        (state / "release").touch(); second.communicate(timeout=30)
        c1, c2 = cert(run, o1["owner"]), cert(run, o2["owner"])
        res["rerun_owner_names_differ"] = o1["owner"] != o2["owner"] and o1["owner"].startswith("same[0].fixture.0r0n") \
            and o2["owner"].startswith("same[0].fixture.0r0n") and o1["owner"].rsplit(".", 1)[0] == "same[0].fixture"
        res["certificates_name_exact_processes"] = (c1["pid"], c1["rc"], c1["host"]) == (o1["pid"], 0, os.uname().nodename) \
            and (c2["pid"], c2["rc"]) == (o2["pid"], 0)
        res["earlier_certificate_cannot_break_live_lock"] = not stolen and (state / "released").exists() \
            and first.returncode == 0 and second.returncode == 0
    with tempfile.TemporaryDirectory() as td:
        d = Path(td); run = setup(d); state = d / "state"
        n = node(d, "crash_once", "crash[0].fixture", bash); n.communicate(timeout=60)
        own = [json.loads(x) for x in (state / "owners.jsonl").read_text().splitlines()]
        log = (run / "submit_W1/logs/w.0.0.log").read_text()
        res["failed_worker_restarted_under_new_name_and_certified"] = len(own) == 2 \
            and own[0]["owner"].split(".")[-1].startswith("0r0n") and own[1]["owner"].split(".")[-1].startswith("0r1n") \
            and [cert(run, o["owner"])["rc"] for o in own] == [3, 0] and "exited 3" in log and n.returncode == 0 \
            and (run / "submit_W1/logs/done.0").read_text().startswith("subjob 0 host")
    bv = subprocess.run([bash, "-c", "echo $BASH_VERSION"], capture_output=True, text=True).stdout.strip()
    out = {"scope": __doc__, "bash_version": bv, "node_sha256": hashlib.sha256(NODE.read_bytes()).hexdigest(),
           "runner_sha256": hashlib.sha256(P3.read_bytes()).hexdigest(), "checks": res, "all_ok": all(res.values())}
    tag = os.environ.get("FIX_TAG", "")
    (HERE / f"s1b_node_fixture{('_' + tag) if tag else ''}.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"bash_version": bv, "checks": res, "all_ok": out["all_ok"]}, indent=1))
    sys.exit(0 if out["all_ok"] else 1)


if __name__ == "__main__":
    worker() if len(sys.argv) > 1 and sys.argv[1] == "worker" else main()
