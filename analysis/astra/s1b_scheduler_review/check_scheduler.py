"""Bounded review of Stage 1b shell contracts. No PBS, populations, fits or network.

Runs the supplied submission fixture in a temporary copy; extracts the actual
claim function for a queue-only wave-isolation check; runs node and collector
scripts against tiny executable stubs. All temporary jobs/files are removed.
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


def executable(path, body):
    path.write_text(f"#!{sys.executable}\n{body}\n")
    path.chmod(0o755)


def existing_fixture():
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        for name in ("s1b_submit.sh", "s1b_submit_fixture.py", "s1a_submit_fixture.py"):
            shutil.copy2(K / name, d / name)
        p = subprocess.run([sys.executable, str(d / "s1b_submit_fixture.py")], capture_output=True, text=True)
        return {"rc": p.returncode, **json.loads((d / "s1b_submit_fixture.json").read_text())}


def wave_isolation():
    tree = ast.parse(P3.read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "claim")
    ns = {"os": os, "random": random}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(P3), "exec"), ns)
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "queue").mkdir()
        (d / "claimed").mkdir()
        ticket = "W1_0000001_s00007_000000000_000000005"
        (d / "queue" / ticket).touch()
        owner = "W2-job[0].fixture.0"
        got = ns["claim"](td, owner)
        return {"w2_owner": owner, "residual_ticket": ticket, "claimed": got,
                "w1_ticket_claimed_by_w2": got == ticket,
                "node_passes_wave_to_work": '"$WAVE"' in (K / "s1b_node.pbs").read_text().split('p3_stage1b.py work', 1)[1].split('pids+=', 1)[0]}


def batch_script(mode, python_rc=0, tar_rc=0):
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        vb = d / "vbase"
        k = vb / "src/analysis/fable/calibration/kunanyi"
        k.mkdir(parents=True)
        b = d / "bin"
        b.mkdir()
        run = vb / "s1b/run"
        (run / "submit_W1/logs").mkdir(parents=True)
        (run / "pack_W1.txt").write_text("collect_W1.json\n")
        (run / "collect_W1.json").write_text('{"tiny_fixture": true}\n')
        (k / "env.sh").write_text(f'export PATH="{b}:$PATH"\ncd "$VBASE/src"\n')
        executable(b / "python", f"import sys; sys.exit({python_rc})")
        executable(b / "sleep", "pass")
        if tar_rc:
            executable(b / "tar", f"import sys; sys.exit({tar_rc})")
        env = dict(os.environ, VBASE=str(vb), OUTDIR="run", SETTINGS="settings.json", WAVE="W1",
                   JOBCPUS="2", WALL_SECS="3600", PBS_JOBID="1[0].fixture", PBS_ARRAY_INDEX="0")
        p = subprocess.run(["bash", str(K / f"s1b_{mode}.pbs")], env=env, capture_output=True, text=True)
        return {"rc": p.returncode, "python_rc": python_rc, "tar_rc": tar_rc,
                "archive_created": (run / "W1.tar.gz").exists(),
                "checksum_created": (run / "W1.tar.gz.sha256").exists()}


def repeated_outdir():
    """Exercise actual submitter and arithmetic under the original scheduler stubs."""
    src = (K / "s1a_submit_fixture.py").read_text()
    ns = {}
    exec(src[src.index("STUBS = {"):src.index("\n\n\ndef scenario")], {}, ns)
    stubs = ns["STUBS"]
    # Use the actual p3 preflight calculation/validation, excluding the source
    # bindings and synthetic runner tests that are outside this shell fixture.
    tree = ast.parse(P3.read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "preflight")
    preflight_source = ast.unparse(fn)
    python_body = f'''import sys,json,types
COLLECTOR_CPU_H=8.0
WAVES={{"W1":(0,30),"W2":(300,)}}
check=lambda *a: {{}}
test=lambda: None
p2=types.SimpleNamespace(sha=lambda x:"stub",runtime=lambda:{{"stub":True}})
{preflight_source}
if "preflight" in sys.argv:
    preflight(*sys.argv[sys.argv.index("preflight")+1:])
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
        (vb / "s1b/settings.json").write_text('{}')
        envf = d / "env.sh"
        envf.write_text(f'export PATH="{b}:$PATH"\ncd "$VBASE/src"\n')
        env = dict(os.environ, PBS_BIN=str(b), S1A_ENV=str(envf), S1A_CONFIRM_SECS="0", FIX_STATE=str(d / "jobs.json"),
                   FIX_LEDGER=str(d / "ledger.jsonl"), FIX_CALLS=str(d / "calls.jsonl"), FIX_QSELECT_CALLS=str(d / "qselect.n"))
        runs = []
        for outdir in ("run", "run_retry"):
            p = subprocess.run(["bash", str(K / "s1b_submit.sh"), str(vb), "settings.json", outdir, "W1", "520", "8",
                                "48:00:00", "200000", "0"], env=env, capture_output=True, text=True)
            runs.append({"outdir": outdir, "rc": p.returncode,
                         "preflight": json.loads((vb / f"s1b/{outdir}/submit_W1/logs/preflight.log").read_text())})
        jobs = [json.loads(x) for x in (d / "ledger.jsonl").read_text().splitlines()]
        return {"runs": runs, "arrays": sum(j["name"].endswith("_a") for j in jobs),
                "collectors": sum(j["name"].endswith("_c") for j in jobs),
                "combined_reservation_cpu_h": sum(r["preflight"]["allocated_cpu_hours_bound"] for r in runs)}


out = {"scope": __doc__, "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
       "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in (K / "s1b_submit.sh", K / "s1b_node.pbs", K / "s1b_collect.pbs", P3)},
       "syntax": {name: subprocess.run(["bash", "-n", str(K / name)]).returncode
                  for name in ("s1b_submit.sh", "s1b_node.pbs", "s1b_collect.pbs")},
       "existing_fixture": existing_fixture(), "wave_isolation": wave_isolation(),
       "node_success": batch_script("node"), "node_worker_failure": batch_script("node", python_rc=3),
       "collector_success": batch_script("collect"), "collector_python_failure": batch_script("collect", python_rc=3),
       "collector_pack_failure": batch_script("collect", tar_rc=2),
       "repeated_outdir": repeated_outdir()}
target = Path(__file__).with_name("scheduler_evidence.json")
target.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({"evidence": str(target), "existing_fixture_all_ok": out["existing_fixture"]["all_ok"],
                  "wave_isolation": out["wave_isolation"], "repeated_outdir": out["repeated_outdir"],
                  "batch_returncodes": {k: v["rc"] for k, v in out.items() if k.startswith(("node_", "collector_"))}}, indent=2))
