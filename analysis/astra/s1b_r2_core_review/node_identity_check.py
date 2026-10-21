"""Actual node script invoked twice with one PBS identity; no PBS or population work."""
import ast
from datetime import datetime
import errno
import hashlib
import json
import math
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import time
import types
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
P3 = ROOT / 'analysis/fable/calibration/v2_dev/p3_stage1b.py'
NODE = ROOT / 'analysis/fable/calibration/kunanyi/s1b_node.pbs'


def load():
    p = types.ModuleType('actual_lock_functions')
    p.__dict__.update(__file__=str(P3), p2=types.SimpleNamespace(), errno=errno, hashlib=hashlib,
                      json=json, math=math, os=os, random=random, shutil=shutil,
                      subprocess=subprocess, sys=sys, tempfile=tempfile, time=time)
    nodes = [n for n in ast.parse(P3.read_text()).body
             if isinstance(n, (ast.Assign, ast.FunctionDef, ast.ClassDef))]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(P3), 'exec'), p.__dict__)
    return p


def worker():
    state = Path(os.environ['AUDIT_STATE'])
    owner = sys.argv[-2]
    if not (state / 'first_owner').exists():
        (state / 'first_owner').write_text(owner)
        return
    p = load(); sd = Path(os.environ['AUDIT_SDIR'])
    L = p.lock(str(sd), owner)
    (state / 'ready.json').write_text(json.dumps({'owner': owner, 'pid': os.getpid(), 'token': L[1]}))
    deadline = time.time() + 10
    while not (state / 'release').exists() and time.time() < deadline:
        time.sleep(.02)
    try:
        p.unlock(L)
        result = 'released'
    except RuntimeError as ex:
        result = str(ex)
    (state / 'worker_result').write_text(result)


if len(sys.argv) > 1 and sys.argv[1] == 'worker':
    worker()
else:
    with tempfile.TemporaryDirectory(prefix='s1b-r2-node-') as tmpname:
        d = Path(tmpname); base = d / 'base'; run = base / 's1b/run'
        state = d / 'state'; state.mkdir()
        sd = run / 'sets/s00007'; sd.mkdir(parents=True)
        (run / 'submit_W1/logs').mkdir(parents=True)
        envfile = base / 'src/analysis/fable/calibration/kunanyi/env.sh'
        envfile.parent.mkdir(parents=True)
        envfile.write_text('cd "$VBASE/src"\n')
        bindir = d / 'bin'; bindir.mkdir()
        fake = bindir / 'python'
        fake.write_text('#!/bin/sh\nexec /usr/bin/python3 "$AUDIT_SCRIPT" worker "$@"\n')
        fake.chmod(0o755)
        env = os.environ | {'VBASE': str(base), 'SETTINGS': 'unused.json', 'OUTDIR': 'run',
                            'WAVE': 'W1', 'TAG': 'W1', 'JOBCPUS': '1', 'WALL_SECS': '3600',
                            'PBS_JOBID': 'same[0].fixture', 'PBS_ARRAY_INDEX': '0',
                            'PATH': str(bindir) + os.pathsep + os.environ['PATH'],
                            'AUDIT_SCRIPT': str(Path(__file__).resolve()), 'AUDIT_STATE': str(state),
                            'AUDIT_SDIR': str(sd)}
        first = subprocess.run(['bash', str(NODE)], env=env, capture_output=True, text=True, timeout=10)
        assert first.returncode == 0
        first_owner = (state / 'first_owner').read_text()
        cert = run / 'workers/dead' / first_owner
        assert cert.exists()
        second = subprocess.Popen(['bash', str(NODE)], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            until = time.time() + 10
            while not (state / 'ready.json').exists() and time.time() < until:
                time.sleep(.02)
            ready = json.loads((state / 'ready.json').read_text())
            p = load()
            old_info = p._owner(str(sd / 'lock'))
            live_before = p.pid_alive(ready['pid'])
            dead_before = p.owner_dead(old_info, cert=str(run / 'workers/dead'), pbs=False)
            other = p.lock(str(sd), 'different[0].fixture.0r0', patience=1)
            stolen_while_live = p.pid_alive(ready['pid']) and p._owner(str(sd / 'lock'))['token'] == other[1]
            (state / 'release').touch()
            stdout, stderr = second.communicate(timeout=10)
            result = {'first_node_exit': first.returncode, 'second_node_exit': second.returncode,
                      'first_owner': first_owner, 'second_owner': ready['owner'],
                      'stale_certificate_present_before_second_process': True,
                      'second_worker_alive_before_reclaim': live_before,
                      'owner_dead_returned_true_for_live_second_worker': dead_before,
                      'live_lock_stolen': stolen_while_live,
                      'second_worker_unlock_result': (state / 'worker_result').read_text(),
                      'node_source_sha256': hashlib.sha256(NODE.read_bytes()).hexdigest(),
                      'timestamp': datetime.now(ZoneInfo('Australia/Hobart')).isoformat()}
            assert ready['owner'] == first_owner and live_before and dead_before and stolen_while_live
            assert 'not owned' in result['second_worker_unlock_result']
            p.unlock(other)
            (OUT / 'node_identity_check.json').write_text(json.dumps(result, indent=2) + '\n')
            print(json.dumps(result, indent=2))
        finally:
            (state / 'release').touch()
            if second.poll() is None:
                second.terminate(); second.wait(timeout=10)
