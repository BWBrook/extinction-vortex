"""Copy of analysis/astra/r2_node_review_20261025/combined_checks.py (Codex, 369b2db) with its two bug-asserting checks recorded instead of asserted (controls kept as assertions); run by Fable on node 8fe10208, 25 Oct."""
"""Independent combined-failure checks of the actual node shell.

Uses a copied upstream fixture's bounded worker/clock stubs. Production shell
bytes remain unchanged. A process-group timeout bounds the alternating-scan
case, including any descendants; no PBS or population work is performed.
"""
import importlib.util
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time
import types
from datetime import datetime
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = Path('/home/bwbrook/papers/project')
NODE = ROOT / 'analysis/fable/calibration/kunanyi/s1b_node.pbs'
spec = importlib.util.spec_from_file_location('fixture_copy', HERE / 's1b_node_fixture.py')
f = importlib.util.module_from_spec(spec); spec.loader.exec_module(f); f.NODE = NODE
BASE_STUB = f.STUB
record = {'node_sha256': hashlib.sha256(NODE.read_bytes()).hexdigest(), 'cases': {}}


def compact(r):
    return {k: v for k, v in r.items() if k != 'run'}


with tempfile.TemporaryDirectory(prefix='r2-node-combined-') as td:
    tmp = Path(td)
    # Every third find fails: each first wave check is empty, each post-pause
    # check is unknown. This is a constructed recurring visibility failure.
    f.STUB = BASE_STUB.replace('if name == "find":\n', '''if name == "find":
    def scan_count():
        p = os.path.join(st, "scan_count")
        n = int(open(p).read()) + 1 if os.path.exists(p) else 1
        open(p, "w").write(str(n)); return n
    n = locked(scan_count)
    log("scan_attempt", n=n, t=locked(clock), path=sys.argv[1])
    if n % 3 == 0:
        log("scan_unknown", n=n, t=locked(clock))
        print("find: Stale file handle (bounded alternating fixture)", file=sys.stderr)
        sys.exit(1)
''')
    outcome = {}
    def bounded_run(cmd, **kwargs):
        kwargs.pop('timeout', None)
        if kwargs.pop('capture_output', False):
            kwargs.update(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc = subprocess.Popen(cmd, start_new_session=True, **kwargs)
        try:
            stdout, stderr = proc.communicate(timeout=4)
            outcome['forced_termination'] = False
        except subprocess.TimeoutExpired:
            outcome['forced_termination'] = True
            os.killpg(proc.pid, signal.SIGTERM)
            stdout, stderr = proc.communicate(timeout=3)
        outcome['exit'] = proc.returncode
        return types.SimpleNamespace(returncode=proc.returncode, stdout=stdout, stderr=stderr)
    f.subprocess = types.SimpleNamespace(run=bounded_run)
    d = tmp / 'alternating'; d.mkdir()
    r = f.run_node(d, [{'rc': 0}], wall=10,
                   env={'MARGIN_SECS': '0', 'LAUNCH_CUTOFF_SECS': '0', 'GRACE_SECS': '30'})
    count = int((d / 'state/scan_count').read_text())
    # run_node removes its event log after parsing; counts and clock remain.
    record['cases']['empty_unknown_loop_past_deadline'] = compact(r) | outcome | {
        'total_find_attempts': count, 'find_attempts_at_cutoff_or_later': count - 2,
        'launch_cutoff_and_deadline_offset': 10,
        'note': 'after first clipped pause, the logical clock stays at cutoff; scans continue without any sleep'}

    d = tmp / 'idle_budget'; d.mkdir()
    r = f.run_node(d, [{'rc': 0}], env={'IDLE_MAX_SECS': '30', 'GRACE_SECS': '10'})
    count = int((d / 'state/scan_count').read_text())
    record['cases']['empty_unknown_loop_ignores_idle_budget'] = compact(r) | outcome | {
        'total_find_attempts': count, 'idle_budget_seconds': 30,
        'launch_cutoff_offset': 170400,
        'note': 'all slots idle throughout; empty branch bypasses idle budget even long before the launch cutoff'}

    # Verify exact certificates (host/PID/rc included) and absence of overlapping
    # children before each next launch, through 75, 0 and unexpected failures.
    f.subprocess = subprocess
    f.STUB = BASE_STUB.replace(
        'log("launch", owner=sys.argv[-2], deadline=int(sys.argv[-1]), pid=os.getpid(), t=start)',
        '''prior = []
    calls = os.path.join(st, "calls.jsonl")
    if os.path.exists(calls):
        prior = [json.loads(x) for x in open(calls) if json.loads(x).get("kind") == "launch"]
    if prior:
        last = prior[-1]
        c = json.load(open(os.path.join(os.environ["FIX_RUN"], "workers/dead", last["owner"])))
        exact = (c["owner"], c["host"], c["pid"], c["rc"]) == (last["owner"], os.uname().nodename, last["pid"], last["planned_rc"])
        try:
            os.kill(last["pid"], 0); alive = True
        except ProcessLookupError:
            alive = False
        log("prior_certificate_check", exact=exact, prior_child_alive=alive)
        if not exact or alive: sys.exit(98)
    log("launch", owner=sys.argv[-2], deadline=int(sys.argv[-1]), pid=os.getpid(), t=start, planned_rc=step["rc"])''')
    d = tmp / 'mixed'; d.mkdir()
    r = f.run_node(d, [{'rc': 3}, {'rc': 75}, {'rc': 0}, {'rc': 3}, {'rc': 75}, {'rc': 3}], queue=['W1_work'])
    assert r['rc'] == 1 and len(r['launches']) == 6 and f.gens(r) == list(range(6))
    assert [x['planned_rc'] for x in r['launches']] == [3, 75, 0, 3, 75, 3]
    cs = [json.loads((r['run'] / 'workers/dead' / x['owner']).read_text()) for x in r['launches']]
    assert [x['rc'] for x in cs] == [3, 75, 0, 3, 75, 3]
    record['cases']['mixed_restarts_verify_prior_certificate_and_no_overlap'] = compact(r) | {
        'certificates': cs, 'verified_before_replacements': len(r['launches']) - 1}

    # Applied-but-failed rename AND one failed readback per certificate. The
    # replacement must wait for a later successful exact readback.
    cat_stub = f.STUB + '''
if name == "cat":
    path = sys.argv[-1]
    if "/workers/dead/" in path:
        key = os.path.join(st, "cat_" + os.path.basename(path))
        if not os.path.exists(key):
            open(key, "w").close(); log("cat_failed_once", owner=os.path.basename(path)); sys.exit(1)
        log("cat_success", owner=os.path.basename(path))
    os.execv("/bin/cat", ["cat"] + sys.argv[1:])
'''
    d = tmp / 'certificate_combined'; (d / 'bin').mkdir(parents=True)
    cat = d / 'bin/cat'; cat.write_text(f'#!{os.sys.executable}\n{cat_stub}'); cat.chmod(0o755)
    r = f.run_node(d, [{'rc': 75}, {'rc': 0}], mv='apply_fail')
    assert r['rc'] == 0 and len(r['launches']) == 2 and f.certs_ok(r)
    assert r['launches'][1]['t'] - r['launches'][0]['t'] >= 15
    record['cases']['ambiguous_certificate_rename_plus_readback_failure'] = compact(r) | {
        'all_final_certificates_match_child_owner_and_pid': True}

record['timestamp'] = datetime.now(ZoneInfo('Australia/Hobart')).isoformat()
(HERE / 'combined_checks.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record, indent=2))
