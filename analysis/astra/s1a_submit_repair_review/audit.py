"""Independent bounded replay/adversarial tests of the repaired submitter.

All scheduler calls go to temporary Python stubs. No PBS, simulation, network,
or mail is used. The peer fixture is copied before execution to keep it intact.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
K = ROOT / "analysis/fable/calibration/kunanyi"
SUBMIT = K / "s1a_submit.sh"
FIXTURE = K / "s1a_submit_fixture.py"

with tempfile.TemporaryDirectory() as td:
    t = Path(td)
    for p in (SUBMIT, FIXTURE):
        shutil.copy2(p, t / p.name)
    proc = subprocess.run([sys.executable, str(t / FIXTURE.name)], capture_output=True, text=True, timeout=180)
    baseline = json.loads((t / "s1a_submit_fixture.json").read_text())
    (HERE / "baseline_replay.json").write_text(json.dumps(baseline, indent=2) + "\n")
    baseline_run = {"returncode": proc.returncode, "all_ok": baseline["all_ok"], "checks": baseline["checks"], "stderr": proc.stderr}

# Reuse only the peer's isolated stub constructors and scenario function, then
# independently add failure classes that its ten scenarios do not represent.
tree = ast.parse(FIXTURE.read_text())
body = []
for node in tree.body:
    if isinstance(node, ast.Assign) and any(isinstance(x, ast.Name) and x.id == "R" for x in node.targets):
        break
    body.append(node)
scope = {"__file__": str(FIXTURE)}
exec(compile(ast.Module(body=body, type_ignores=[]), str(FIXTURE), "exec"), scope)
original = dict(scope["STUBS"])
results = {}

scope["STUBS"]["qselect"] = original["qselect"].replace(
    'if j["name"] == name and ("-x" in a or j["state"] != "F"):',
    'if j["name"] == name and ("-x" in a or j["state"] != "F") and not (os.environ.get("ASTRA_EXPIRED_HISTORY") == "1" and j["state"] == "F"):')
results["lost_node_reply_then_history_expires"] = scope["scenario"]([
    {"env": {"FIX_FAIL_AT": "4", "FIX_FAIL_MODE": "ambiguous"}},
    {"finish": 4, "mode": "resume", "env": {"ASTRA_EXPIRED_HISTORY": "1"}},
])
results["lost_collector_reply_then_history_expires"] = scope["scenario"]([
    {"env": {"FIX_FAIL_AT": "46", "FIX_FAIL_MODE": "ambiguous"}},
    {"finish": 46, "mode": "resume", "env": {"ASTRA_EXPIRED_HISTORY": "1"}},
])

scope["STUBS"]["qselect"] = original["qselect"]
scope["STUBS"]["qstat"] = original["qstat"].replace(
    'if j is None or j["state"] == "F":',
    'if os.environ.get("ASTRA_QSTAT_ALL_ERROR") == "1" or (os.environ.get("ASTRA_QSTAT_ONE_ERROR") == "1" and a[-1] == "900000.fixture"):\n    print("qstat: cannot connect to server", file=sys.stderr); sys.exit(15007)\nif j is None or j["state"] == "F":')
results["one_qstat_transport_error"] = scope["scenario"]([{"env": {"ASTRA_QSTAT_ONE_ERROR": "1"}}])
results["all_qstat_transport_error"] = scope["scenario"]([{"env": {"ASTRA_QSTAT_ALL_ERROR": "1"}}])

scope["STUBS"]["qstat"] = original["qstat"]
scope["STUBS"]["qselect"] = original["qselect"].replace(
    'a = sys.argv[1:]; name = a[a.index("-N") + 1]',
    'a = sys.argv[1:]; name = a[a.index("-N") + 1]\nif os.environ.get("ASTRA_QSELECT_ERROR") == "1":\n    print("qselect: history request failed", file=sys.stderr); sys.exit(1)')
results["qselect_error_before_dispatch"] = scope["scenario"]([{"env": {"ASTRA_QSELECT_ERROR": "1"}}])
results["qselect_error_during_uncertain_recovery"] = scope["scenario"]([
    {"env": {"FIX_FAIL_AT": "4", "FIX_FAIL_MODE": "ambiguous"}},
    {"mode": "resume", "env": {"ASTRA_QSELECT_ERROR": "1"}},
])

# Directly isolate preflight for arithmetic/shape behavior only. Its check/test
# calls are sentinels; the main audit separately reviews actual bound inputs.
runner = ROOT / "analysis/fable/calibration/v2_dev/p2_stage1a.py"
rtree = ast.parse(runner.read_text())
pre = ast.Module(body=[n for n in rtree.body if isinstance(n, ast.FunctionDef) and n.name == "preflight"], type_ignores=[])
bound = json.loads((runner.parent / "p2/p2_settings_s1a.json").read_text())
calls = []
pscope = {"check": lambda *args: (calls.append("check"), bound)[1], "test": lambda *args: calls.append("test"),
          "sha": lambda p: "fixture", "runtime": lambda: {"fixture": True}, "DEADLINE_MARGIN": 600,
          "json": json}
exec(compile(pre, str(runner), "exec"), pscope)
import contextlib
import io
preflights = {}
for label, nj, nc, wall, ceiling, prior in [
    ("proposed", 45, 8, 9900, 1000, .44),
    ("over_budget", 45, 8, 14400, 1000, .44),
    ("wrong_workers", 44, 8, 9900, 1000, .44),
    ("too_short", 45, 8, 7800, 1000, .44),
]:
    calls.clear(); err = None
    with contextlib.redirect_stdout(io.StringIO()) as log:
        try:
            pscope["preflight"]("settings", "metric", nj, nc, wall, ceiling, prior, 1)
        except BaseException as exc:
            err = type(exc).__name__ + ": " + str(exc)
    preflights[label] = {"error": err, "calls": list(calls), "receipt": json.loads(log.getvalue())}

out = {"source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
       "submit_sha256": hashlib.sha256(SUBMIT.read_bytes()).hexdigest(),
       "fixture_sha256": hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
       "baseline": baseline_run, "adversarial": results, "isolated_preflight": preflights,
       "scope": __doc__}
(HERE / "audit.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({"baseline": baseline_run, "adversarial": {k: {kk: vv for kk, vv in v.items() if kk != "runs"} for k, v in results.items()}, "preflight": preflights}, indent=2))
