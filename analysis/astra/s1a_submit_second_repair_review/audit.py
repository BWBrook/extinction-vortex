"""Replay 15 supplied stub tests and one consequential failed-reply ambiguity.

No actual scheduler, network, simulation or mail. Scheduler elapsed time is
modeled in stub state: an accepted job can finish and leave retained history
before its failed/delayed submission call returns. Production shell is intact.
"""
import ast
import hashlib
import json
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
    proc = subprocess.run([sys.executable, str(t / FIXTURE.name)], capture_output=True, text=True, timeout=240)
    baseline = json.loads((t / "s1a_submit_fixture.json").read_text())
    (HERE / "baseline_replay.json").write_text(json.dumps(baseline, indent=2) + "\n")
    baseline_run = {"returncode": proc.returncode, "all_ok": baseline["all_ok"], "checks": baseline["checks"], "stderr": proc.stderr}

# Load only stub definitions and scenario(), adding a full journal receipt to
# the test harness output. No production code is patched.
source = FIXTURE.read_text().replace('"journal_tail": journal[-3:]', '"journal": journal, "journal_tail": journal[-3:]')
tree = ast.parse(source)
body = []
for node in tree.body:
    if isinstance(node, ast.Assign) and any(isinstance(x, ast.Name) and x.id == "R" for x in node.targets):
        break
    body.append(node)
scope = {"__file__": str(FIXTURE)}
exec(compile(ast.Module(body=body, type_ignores=[]), str(FIXTURE), "exec"), scope)
original = dict(scope["STUBS"])
scope["STUBS"]["qsub"] = original["qsub"].replace(
    'if n == at and mode == "ambiguous":\n    sys.exit(1)',
    'if n == at and mode == "ambiguous":\n    if os.environ.get("ASTRA_EXPIRE_BEFORE_REPLY") == "1":\n        # Model an accepted job completing and history expiring while the submission reply is delayed.\n        st.write_text(json.dumps(jobs[:-1]))\n    sys.exit(1)')
fail = {"env": {"FIX_FAIL_AT": "4", "FIX_FAIL_MODE": "ambiguous", "ASTRA_EXPIRE_BEFORE_REPLY": "1"}}
results = {}
results["accepted_expired_before_failed_reply"] = scope["scenario"]([fail])
results["accepted_expired_before_failed_reply_then_resume"] = scope["scenario"]([fail, {"mode": "resume"}])

scope["STUBS"]["qsub"] = original["qsub"]
scope["STUBS"]["qstat"] = original["qstat"].replace(
    'a = sys.argv[1:]; jid = a[-1]; fail = os.environ.get("FIX_QSTAT_FAIL", "")',
    'a = sys.argv[1:]; jid = a[-1]; fail = os.environ.get("FIX_QSTAT_FAIL", "")\nif "-x" in a and os.environ.get("ASTRA_QSTAT_UNKNOWN") == "1":\n    print("Job Id: " + jid + "\\n    job_state = unknown"); sys.exit(0)')
results["successful_unclassifiable_qstat"] = scope["scenario"]([{"env": {"ASTRA_QSTAT_UNKNOWN": "1"}}])
scope["STUBS"]["qstat"] = original["qstat"].replace(
    'j = jobs.get(jid)',
    'j = jobs.get(jid)\nif j is not None and "-x" in a and os.environ.get("ASTRA_ALL_LIVE_STATES") == "1":\n    j["state"] = ["Q","R","H","W","T","E","S","U","B","M"][(int(jid.split(".")[0])-900000)%10]')
results["all_supported_live_states_keep_dependencies"] = scope["scenario"]([{"env": {"ASTRA_ALL_LIVE_STATES": "1"}}])

out = {"source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
       "submit_sha256": hashlib.sha256(SUBMIT.read_bytes()).hexdigest(),
       "fixture_sha256": hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
       "baseline": baseline_run, "additional": results, "scope": __doc__}
(HERE / "audit.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({"baseline": baseline_run, "additional": {k: {kk: vv for kk, vv in v.items() if kk not in ("journal", "journal_tail")} for k, v in results.items()}}, indent=2))
