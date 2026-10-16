"""Tiny scheduler/ledger review; real shell and extracted real reserve/preflight.

No PBS, SSH, populations or fits. Source/runtime binding and sampler self-tests
are stubbed here; arithmetic, ledger parsing/writing and submit orchestration
are the reviewed implementation. Scientific validation is outside this check.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
K = ROOT / "analysis/fable/calibration/kunanyi"
P3 = ROOT / "analysis/fable/calibration/v2_dev/p3_stage1b.py"
BASH42 = Path("/tmp/claude-1000/-home-bwbrook-papers-project/2114b555-0c74-405f-bb3d-7860a2e979f1/scratchpad/bash42/bash-4.2/bash")
TREE = ast.parse(P3.read_text())


def source(names):
    return "\n\n".join(ast.unparse(n) for n in TREE.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names)


def executable(path, body):
    path.write_text(f"#!{sys.executable}\n{body}\n")
    path.chmod(0o755)


def supplied_fixture(shell):
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        for name in ("s1b_submit.sh", "s1b_submit_fixture.py", "s1a_submit_fixture.py"):
            shutil.copy2(K / name, d / name)
        p = subprocess.run([sys.executable, str(d / "s1b_submit_fixture.py")], env=dict(os.environ, FIX_BASH=str(shell)),
                           capture_output=True, text=True)
        return {"rc": p.returncode, **json.loads((d / "s1b_submit_fixture.json").read_text())}


def shell_case(steps):
    src = (K / "s1a_submit_fixture.py").read_text()
    ns = {}
    exec(src[src.index("STUBS = {"):src.index("\n\n\ndef scenario")], {}, ns)
    stubs = ns["STUBS"]
    python_body = f'''import sys,json,types,os,time
COLLECTOR_CPU_H=8.0
WAVES={{"W1":(0,30),"W2":(300,)}}
check=lambda settings,*a: json.load(open(settings))
test=lambda: None
p2=types.SimpleNamespace(sha=lambda x:"binding-stub",runtime=lambda:{{"stub":True}})
{source({"reserve", "preflight"})}
if "preflight" in sys.argv:
    preflight(*sys.argv[sys.argv.index("preflight")+1:])
elif "seed" in sys.argv:
    sys.exit(int(os.environ.get("FIX_SEED_RC","0")))
'''
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        b = d / "bin"
        b.mkdir()
        for name, body in stubs.items():
            executable(b / name, python_body if name == "python" else body)
        vb = d / "vbase"
        (vb / "src").mkdir(parents=True)
        (vb / "s1b").mkdir()
        settings = {"campaign": "s1b", "ceilings": {"W1": 200000.0, "W2": 1000000.0, "campaign": 1200000.0}}
        (vb / "s1b/settings.json").write_text(json.dumps(settings))
        envf = d / "env.sh"
        envf.write_text(f'export PATH="{b}:$PATH"\ncd "$VBASE/src"\n')
        env = dict(os.environ, PBS_BIN=str(b), S1A_ENV=str(envf), S1A_CONFIRM_SECS="0", FIX_STATE=str(d / "jobs.json"),
                   FIX_LEDGER=str(d / "ledger.jsonl"), FIX_CALLS=str(d / "calls.jsonl"), FIX_QSELECT_CALLS=str(d / "qselect.n"))
        runs = []
        for step in steps:
            outdir = step.get("outdir", "run")
            journal = vb / f"s1b/{outdir}/submit_W1/submit_journal.tsv"
            reservations = vb / "s1b/reservations.tsv"
            if step.get("release_and_reject"):
                name = journal.read_text().splitlines()[0].split()[2]
                with reservations.open("a") as f:
                    f.write(f"release\t{name}\tmanual: stub accounting verifies no accepted job\n")
                with journal.open("a") as f:
                    f.write(f"rejected a {name} manual: stub accounting verifies no accepted job\n")
            args = ["bash", str(K / "s1b_submit.sh"), str(vb), "settings.json", outdir, "W1", str(step.get("jobs", 520)), "8", "48:00:00"]
            if step.get("mode"):
                args.append(step["mode"])
            p = subprocess.run(args, env=dict(env, **step.get("env", {})), capture_output=True, text=True)
            log = vb / f"s1b/{outdir}/submit_W1/logs/preflight.log"
            runs.append({"step": step, "rc": p.returncode, "stderr": p.stderr.strip().replace(td, "<tmp>"),
                         "preflight_log": log.read_text().strip() if log.exists() else "",
                         "reservations_after": reservations.read_text().splitlines() if reservations.exists() else []})
        jobs = [json.loads(x) for x in (d / "ledger.jsonl").read_text().splitlines()] if (d / "ledger.jsonl").exists() else []
        cpu_h = 0
        for j in jobs:
            a = j["args"]
            cpu_h += (int(a[a.index("-J") + 1].split("-")[1]) + 1) * 8 * 48 if "-J" in a else 8
        return {"runs": runs, "arrays_created": sum(j["name"].endswith("_a") for j in jobs),
                "collectors_created": sum(j["name"].endswith("_c") for j in jobs), "actual_accepted_cpu_h": cpu_h}


def wave_isolation():
    # Test the actual claim filter; lock mechanics are independently reviewed.
    from contextlib import nullcontext
    ns = {"os": os, "random": random, "QSTAT": "unused", "held": lambda *a: nullcontext()}
    exec(source({"parse_ticket", "claim", "recover_stale"}), ns)
    ns["owner_dead"] = lambda *a: True
    with tempfile.TemporaryDirectory() as td:
        run = Path(td)
        (run / "queue").mkdir()
        (run / "claimed").mkdir()
        for wave in ("W1", "W2"):
            (run / "queue" / f"{wave}_0000001_s00007_000000000_000000005").touch()
            (run / "claimed" / f"{wave}_0000001_s00007_000000005_000000010@dead[0].fixture.0").touch()
        got = ns["claim"](td, "W2[0].fixture.0", "W2")
        recovered = ns["recover_stale"](td, "W2[0].fixture.0", "W2")
        return {"claimed": got, "stale_requeued": recovered,
                "queue": sorted(p.name for p in (run / "queue").iterdir()),
                "claims": sorted(p.name for p in (run / "claimed").iterdir()),
                "worker_invocation_passes_wave": '"$RUN" "$WAVE"' in (K / "s1b_node.pbs").read_text()}


out = {"scope": __doc__, "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
       "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                         (K / "s1b_submit.sh", K / "s1b_node.pbs", K / "s1b_submit_fixture.py", P3)},
       "syntax": {name: subprocess.run(["bash", "-n", str(K / name)]).returncode for name in ("s1b_submit.sh", "s1b_node.pbs", "s1b_collect.pbs")},
       "supplied_fixture_bash52": supplied_fixture("bash"),
       "supplied_fixture_bash42": supplied_fixture(BASH42) if BASH42.exists() else None,
       "wave_isolation": wave_isolation(),
       "fresh_directory_now_refused": shell_case([{}, {"outdir": "run_retry"}]),
       "prejournal_changed_shape": shell_case([{"jobs": 1, "env": {"FIX_SEED_RC": "7"}}, {"jobs": 521}]),
       "release_then_same_name_retry": shell_case([{"env": {"FIX_FAIL_AT": "1", "FIX_FAIL_MODE": "reject"}},
                                                  {"release_and_reject": True, "mode": "resume"}, {"outdir": "run_retry"}]),
       "seed_failure_same_shape_idempotent": shell_case([{"env": {"FIX_SEED_RC": "7"}}, {}]),
       "ambiguous_history_expired_still_reserved": shell_case([{"env": {"FIX_FAIL_AT": "1", "FIX_FAIL_MODE": "ambiguous_expired"}},
                                                              {"mode": "resume"}, {"outdir": "run_retry"}])}
path = Path(__file__).with_name("repair_evidence.json")
path.write_text(json.dumps(out, indent=2) + "\n")
summary = {k: {"run_rcs": [r["rc"] for r in v["runs"]], "accepted_cpu_h": v["actual_accepted_cpu_h"]}
           for k, v in out.items() if isinstance(v, dict) and "runs" in v}
print(json.dumps({"evidence": str(path), "fixtures_bash52": out["supplied_fixture_bash52"]["all_ok"],
                  "fixtures_bash42": out["supplied_fixture_bash42"] and out["supplied_fixture_bash42"]["all_ok"],
                  "wave_isolation": out["wave_isolation"], **summary}, indent=2))
