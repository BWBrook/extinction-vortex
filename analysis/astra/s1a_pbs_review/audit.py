"""Bounded, no-PBS/no-simulation fixtures for Stage 1a dispatch contracts.

Real qsub/qstat absolute paths are replaced only in temporary script copies.
The collector is loaded by AST using standard-library dependencies only.
"""
import ast
import collections
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
K = ROOT / "analysis/fable/calibration/kunanyi"
P = ROOT / "analysis/fable/calibration/v2_dev"
RESULT = {}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run_submit_fixture(name, calls, fail_at=None):
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        stub = t / "qsub"
        stub.write_text("""#!/usr/bin/python3
import json,os,pathlib,sys
p=pathlib.Path(os.environ['AUDIT_CALLS'])
rows=p.read_text().splitlines() if p.exists() else []
n=len(rows)+1
with p.open('a') as f: f.write(json.dumps({'number':n,'args':sys.argv[1:]})+'\\n')
if n==int(os.environ.get('AUDIT_FAIL','-1')): sys.exit(7)
print(str(10000+n)+'.fixture')
""")
        stub.chmod(0o755)
        qs = t / "qstat"
        qs.write_text("#!/bin/bash\nprintf 'Mail_Users = fixture\nMail_Points = ae\n'\n")
        qs.chmod(0o755)
        script = t / "submit.sh"
        script.write_text((K / "s1a_submit.sh").read_text().replace("/opt/pbs/bin/qsub", str(stub)).replace("/opt/pbs/bin/qstat", str(qs)))
        env = dict(os.environ, AUDIT_CALLS=str(t / "calls.jsonl"))
        if fail_at is not None:
            env["AUDIT_FAIL"] = str(fail_at)
        runs = []
        for nj, nc, wall in calls:
            proc = subprocess.run(["bash", str(script), str(t / "base"), "settings.json", "main", str(nj), str(nc), wall], env=env, capture_output=True, text=True)
            ledger = t / "base/s1a/main/node_jobs.txt"
            runs.append({"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr,
                         "node_ledger_exists": ledger.exists(), "node_ledger_lines": len(ledger.read_text().splitlines()) if ledger.exists() else None})
        rec = [json.loads(s) for s in (t / "calls.jsonl").read_text().splitlines()]
        RESULT[name] = {"runs": runs, "qsub_calls": len(rec), "first_qsub": rec[0], "last_qsub": rec[-1]}


run_submit_fixture("normal_then_duplicate", [(45, 8, "02:45:00"), (45, 8, "02:45:00")])
run_submit_fixture("over_budget_same_worker_count", [(45, 8, "04:00:00")])
run_submit_fixture("partial_submission_failure", [(45, 8, "02:45:00")], fail_at=4)
run_submit_fixture("partial_failure_then_retry", [(45, 8, "02:45:00"), (45, 8, "02:45:00")], fail_at=4)
run_submit_fixture("collector_submission_failure", [(45, 8, "02:45:00")], fail_at=46)

# Node wrapper: real shell, fake runtime and Python, no generation.
with tempfile.TemporaryDirectory() as td:
    t = Path(td); envfile = t / "src/analysis/fable/calibration/kunanyi/env.sh"
    envfile.parent.mkdir(parents=True)
    envfile.write_text('cd "$VBASE/src"\n')
    (t / "bin").mkdir()
    stub = t / "bin/python"
    stub.write_text("""#!/usr/bin/python3
import json,os,pathlib,sys
w=int(sys.argv[-3]); pathlib.Path(os.environ['AUDIT_NODE'],str(w)+'.json').write_text(json.dumps(sys.argv[1:]))
sys.exit(3 if w==355 else 0)
""")
    stub.chmod(0o755)
    (t / "calls").mkdir()
    env = dict(os.environ, VBASE=str(t), SETTINGS="settings.json", OUTDIR="main", JOB="44", JOBCPUS="8", NW="360", WALL_SECS="9900", AUDIT_NODE=str(t / "calls"), PATH=str(t / "bin") + ":" + os.environ["PATH"])
    proc = subprocess.run(["bash", str(K / "s1a_node.pbs")], env=env, capture_output=True, text=True)
    rec = [json.loads(p.read_text()) for p in sorted((t / "calls").glob("*.json"))]
    RESULT["node_last_job"] = {"returncode": proc.returncode, "worker_ids": sorted(int(r[-3]) for r in rec), "nworkers": sorted(set(int(r[-2]) for r in rec)), "jobs_log": (t / "s1a/main/logs/jobs.log").read_text()}

# Isolate production collect without importing or executing simulation code.
tree = ast.parse((P / "p2_stage1a.py").read_text())
module = ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "collect"], type_ignores=[])
scope = {"json": json, "os": os, "sha": sha}
exec(compile(module, str(P / "p2_stage1a.py"), "exec"), scope)
for case in ["missing", "failed", "running", "censored", "corrupt_with_old_summary", "malformed_hit_json", "stale_worker"]:
    with tempfile.TemporaryDirectory() as td:
        t = Path(td); settings = t / "settings.json"; metric = t / "metric.json"; out = t / "collect.json"
        st = {"index": 0, "pop": "fixture", "outer": "fixture/0", "n": 0, "proposal_budget": 10}
        settings.write_text(json.dumps({"metric_sha256": "bound_metric", "runner_sha256": "bound_runner", "settings": [st]}))
        metric.write_text("current metric differs from bound metric")
        binding = {"settings_sha256": sha(settings), "metric_sha256": "bound_metric", "runner_sha256": "bound_runner"}
        state = {"binding": binding, "status": case if case in ("failed", "running", "censored") else "complete", "hits": 0, "proposals": 10, "cpu_seconds": 1}
        if case != "missing":
            (t / "s0000.json").write_text(json.dumps(state))
        if case == "corrupt_with_old_summary":
            out.write_text('{"stale": true}')
            (t / "s0000.json").write_text('{"broken"')
        if case == "malformed_hit_json":
            state["hits"] = 1
            (t / "s0000.json").write_text(json.dumps(state))
            (t / "s0000_hits.jsonl").write_text("not JSON\n")
        if case == "stale_worker":
            (t / "worker9999.json").write_text('{"worker":9999,"nworkers":99999,"binding":{"stale":true}}')
        err = None
        with contextlib.redirect_stdout(io.StringIO()) as log:
            try:
                scope["collect"](str(settings), str(metric), str(t), str(out))
            except BaseException as exc:
                err = type(exc).__name__ + ": " + str(exc)
        RESULT["collect_" + case] = {"error": err, "stdout": log.getvalue(), "output": json.loads(out.read_text()) if out.exists() else None}

# Execute the production PBS collector shell with the same AST-isolated collect.
# PBS directives are comments to Bash, so this cannot send email or submit work.
for case in ("all_missing", "corrupt_with_old_summary"):
    with tempfile.TemporaryDirectory() as td:
        t = Path(td); envfile = t / "src/analysis/fable/calibration/kunanyi/env.sh"
        envfile.parent.mkdir(parents=True)
        envfile.write_text('cd "$VBASE/src"\n')
        (t / "bin").mkdir()
        stub = t / "bin/python"
        stub.write_text("""#!/usr/bin/python3
import ast,hashlib,json,os,pathlib,sys
tree=ast.parse(pathlib.Path(os.environ['AUDIT_RUNNER']).read_text())
module=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='collect'],type_ignores=[])
scope={'json':json,'os':os,'sha':lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()}
exec(compile(module,'collector_fixture','exec'),scope)
scope['collect'](*sys.argv[4:])
""")
        stub.chmod(0o755)
        state = t / "s1a/main"; (state / "logs").mkdir(parents=True)
        (state / "logs/collect.out").write_text("live PBS stdout")
        (state / "logs/collect.err").write_text("live PBS stderr")
        settings = t / "s1a/settings.json"
        settings.write_text(json.dumps({"metric_sha256": "metric", "runner_sha256": "runner", "settings": [{"index": 0, "pop": "fixture", "outer": "fixture/0", "n": 0, "proposal_budget": 10}]}))
        (t / "s1a/p2_metric.json").write_text('{}')
        if case == "corrupt_with_old_summary":
            (state / "s0000.json").write_text('{broken')
            (state / "collect.json").write_text('{"old_success": true}')
        env = dict(os.environ, VBASE=str(t), SETTINGS="settings.json", OUTDIR="main", AUDIT_RUNNER=str(P / "p2_stage1a.py"), PATH=str(t / "bin") + ":" + os.environ["PATH"])
        proc = subprocess.run(["bash", str(K / "s1a_collect.pbs")], env=env, capture_output=True, text=True, timeout=15)
        archive = t / "s1a/main.tar.gz"
        with tarfile.open(archive) as tf:
            names = tf.getnames(); summary = json.loads(tf.extractfile("main/collect.json").read())
        RESULT["collector_shell_" + case] = {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr, "archive_members": names, "archived_summary": summary, "checksum_matches": (t / "s1a/main.tar.gz.sha256").read_text().split()[0] == sha(archive), "live_logs_excluded": "main/logs/collect.out" not in names and "main/logs/collect.err" not in names}

# Budget and assignment arithmetic, using the bound local settings/throughput.
b = json.loads((P / "p2/p2_settings_s1a.json").read_text())
rates = json.loads((P / "p2/throughput_kunanyi.json").read_text())
loads = collections.defaultdict(float); combos = collections.defaultdict(list)
for st in b["settings"]:
    loads[st["worker"]] += st["proposal_budget"] / rates[f'{st["pop"]}|{st["outer"]}|{st["n"]}']
    combos[st["worker"]].append(st["n"])
RESULT["budget"] = {"settings": len(b["settings"]), "workers": len(loads), "worker_ids": [min(loads), max(loads)], "settings_per_worker": dict(collections.Counter(len(v) for v in combos.values())), "one_control_two_info_each": all(len(v) == 3 and v.count(0) == 1 for v in combos.values()), "expected_cpu_hours": sum(loads.values()) / 3600, "min_worker_seconds": min(loads.values()), "max_worker_seconds": max(loads.values()), "total_proposals": sum(st["proposal_budget"] for st in b["settings"]), "node_allocated_cpu_hours": 45 * 8 * 2.75, "collector_max_cpu_hours": 1, "smoke_allocated_cpu_hours": 28 * 57 / 3600, "smoke_collector_cpu_hours": 6 / 3600, "total_ceiling": 45 * 8 * 2.75 + 1 + (28 * 57 + 6) / 3600}

# Optional copied artifact; never touches the remote original.
archive = Path("/tmp/astra_s1a_stage_final_review.tar")
if archive.exists():
    with tarfile.open(archive) as tf:
        members = {m.name: tf.extractfile(m).read() for m in tf.getmembers() if m.isfile()}
    rows = []
    for line in members["./s1a/stage_sha256.txt"].decode().splitlines():
        expected, name = line.split(maxsplit=1)
        data = members[name]
        local = ROOT / name.removeprefix("./src/") if name.startswith("./src/") else P / "p2" / Path(name).name
        rows.append({"name": name, "sha256": hashlib.sha256(data).hexdigest(), "manifest_matches": hashlib.sha256(data).hexdigest() == expected, "local_exists": local.exists(), "local_matches": local.exists() and local.read_bytes() == data})
    RESULT["stage_bundle"] = {"archive_sha256": sha(archive), "bytes": archive.stat().st_size, "manifest_rows": rows, "files": sorted(members), "preexisting_dependencies_omitted": ["src/analysis/fable/calibration/bank.py", "src/analysis/fable/calibration/kunanyi/env.sh"]}

RESULT["source_sha256"] = {str(p.relative_to(ROOT)): sha(p) for p in [K / "s1a_submit.sh", K / "s1a_node.pbs", K / "s1a_collect.pbs", P / "p2_stage1a.py"]}
(OUT / "audit.json").write_text(json.dumps(RESULT, indent=2) + "\n")
print(json.dumps({k: v for k, v in RESULT.items() if k in ("budget", "node_last_job", "stage_bundle")}, indent=2))
