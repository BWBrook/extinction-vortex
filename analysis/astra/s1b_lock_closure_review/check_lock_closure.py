"""Finite closure of the dead-owner lock race; no sampler or numerical imports.

Loads the unchanged lock/queue functions via AST from old Git and current source.
Both race runs use the same event-controlled interleaving, actual threads, real
filesystem calls and the real same-host PID-death test.
"""
import ast
import contextlib
from datetime import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import types
from unittest.mock import patch
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
TARGET = 'analysis/fable/calibration/v2_dev/p3_stage1b.py'
OLD = 'ced47a8'
NAMES = {'pid_alive', 'owner_dead', '_owner', '_publish', '_reclaim', 'lock',
         'unlock', 'held', 'LockStale', 'parse_ticket', 'claim', 'recover_stale'}


def load(source, label):
    module = types.ModuleType(label)
    module.__dict__.update(os=os, json=json, shutil=shutil, subprocess=subprocess,
                           sys=sys, time=time, random=random, QSTAT='/opt/pbs/bin/qstat')
    nodes = [node for node in ast.parse(source).body
             if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in NAMES]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), label, 'exec'), module.__dict__)
    return module


old_source = subprocess.check_output(['git', 'show', f'{OLD}:{TARGET}'], cwd=ROOT, text=True)
new_source = (ROOT / TARGET).read_text()
old, new = load(old_source, 'old_actual_lock_functions'), load(new_source, 'current_actual_lock_functions')
child = subprocess.Popen(['/bin/true']); child.wait()
dead_pid = child.pid
assert not new.pid_alive(dead_pid)
result = {'scope': __doc__, 'old_commit': OLD,
          'current_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
          'source_sha256': {'old': hashlib.sha256(old_source.encode()).hexdigest(),
                            'current': hashlib.sha256(new_source.encode()).hexdigest()},
          'functions_loaded_verbatim_from_ast': sorted(NAMES), 'cases': {}}


def owner(token, dead=False):
    return {'owner': token, 'host': os.uname().nodename,
            'pid': dead_pid if dead else os.getpid(), 'token': token}


def install(directory, info):
    directory.mkdir()
    (directory / 'owner.json').write_text(json.dumps(info))


def race(module, directory):
    directory.mkdir()
    install(directory / 'lock', owner('dead-generation', dead=True))
    both_read = threading.Barrier(2)
    a_acquired, b_resolution, a_released = (threading.Event() for _ in range(3))
    guard = threading.Lock()
    seen, events, acquired, errors = set(), [], {}, {}
    active = peak = 0
    original_dead = module.owner_dead

    def observed(info, qstat=module.QSTAT):
        name = threading.current_thread().name
        r = original_dead(info, qstat)
        if info['token'] == 'dead-generation' and name not in seen:
            seen.add(name)
            events.append(name + ' read dead generation')
            both_read.wait(timeout=5)
            if name == 'B':
                assert a_acquired.wait(timeout=5)
        return r

    def contender(name):
        nonlocal active, peak
        try:
            acquired[name] = module.lock(str(directory), name)
            with guard:
                active += 1
                peak = max(peak, active)
                events.append(name + ' acquired')
            if name == 'A':
                a_acquired.set()
                assert b_resolution.wait(timeout=5)
            else:
                b_resolution.set()
                assert a_released.wait(timeout=5)
            with guard:
                active -= 1
            try:
                module.unlock(acquired[name])
                events.append(name + ' released')
            except Exception as ex:
                errors[name] = type(ex).__name__ + ': ' + str(ex)
            finally:
                if name == 'A':
                    a_released.set()
        except Exception as ex:
            errors[name] = type(ex).__name__ + ': ' + str(ex)
            b_resolution.set(); a_released.set(); a_acquired.set()

    with contextlib.ExitStack() as stack:
        stack.enter_context(patch.object(module, 'owner_dead', observed))
        if hasattr(module, '_reclaim'):
            original_reclaim = module._reclaim
            def reclaim(d, obs, me, qstat=module.QSTAT):
                r = original_reclaim(d, obs, me, qstat)
                if me['owner'] == 'B' and obs['token'] == 'dead-generation':
                    assert r is False and module._owner(d)['token'] == acquired['A'][1]
                    events.append('B stale reclaim refused while A holds')
                    b_resolution.set()
                return r
            stack.enter_context(patch.object(module, '_reclaim', reclaim))
        threads = [threading.Thread(target=contender, args=(n,), name=n, daemon=True) for n in ('A', 'B')]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=6)
    assert not any(t.is_alive() for t in threads), events
    return {'peak_holders': peak, 'events': events, 'errors': errors,
            'both_acquired': sorted(acquired) == ['A', 'B'],
            'lock_removed_after_completion': not (directory / 'lock').exists()}


def snapshots(directory):
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(directory.rglob('owner.json'))}


with tempfile.TemporaryDirectory(prefix='s1b-lock-closure-') as tmpname:
    tmp = Path(tmpname)
    result['cases']['old_race'] = race(old, tmp / 'old')
    result['cases']['new_race_then_successor'] = race(new, tmp / 'new')
    a, b = result['cases']['old_race'], result['cases']['new_race_then_successor']
    assert a['peak_holders'] == 2 and 'not owned' in a['errors']['A']
    assert b['peak_holders'] == 1 and not b['errors'] and b['both_acquired']
    assert b['events'].index('A released') < b['events'].index('B acquired')
    assert b['lock_removed_after_completion']

    # Both the original owner and its reclaimer have ended. No lock is removed.
    sd = tmp / 'stalled'; sd.mkdir()
    install(sd / 'lock', owner('ended-lock', dead=True))
    install(sd / 'lock.reclaim', owner('ended-reclaimer', dead=True))
    before = snapshots(sd)
    try:
        new.lock(str(sd), 'new-worker')
        raise AssertionError('must fail closed')
    except new.LockStale as ex:
        message = str(ex)
    assert snapshots(sd) == before
    result['cases']['dead_reclaimer_fails_closed'] = {
        'exception': 'LockStale', 'message': message, 'owner_files_unchanged': True}

    # On a quiescent fixture, an operator can preserve/remove the dead reclaim
    # mutex; the normal lock path then reclaims the positively ended lock.
    os.rename(sd / 'lock.reclaim', sd / 'operator-preserved-reclaim')
    L = new.lock(str(sd), 'after-operator-recovery')
    preserved = (sd / 'operator-preserved-reclaim/owner.json').read_bytes()
    assert hashlib.sha256(preserved).hexdigest() == before['lock.reclaim/owner.json']
    new.unlock(L)
    result['cases']['quiescent_operator_recovery'] = {
        'ended_reclaimer_evidence_preserved': True, 'normal_acquire_then_release': True,
        'restriction': 'Fixture had no active contenders; operator recovery requires quiescence and owner-death evidence.'}

    # Claim skips an explicitly stalled setting, retains its ticket, and serves
    # a healthy setting. Random order is disabled only to force the stalled one first.
    run = tmp / 'run'
    for path in ('queue', 'claimed', 'sets/s00007', 'sets/s00008'):
        (run / path).mkdir(parents=True, exist_ok=True)
    stalled = run / 'sets/s00007'
    install(stalled / 'lock', owner('ended-lock', dead=True))
    install(stalled / 'lock.reclaim', owner('ended-reclaimer', dead=True))
    tickets = ['W1_0000001_s00007_000000000_000000001', 'W1_0000001_s00008_000000000_000000001']
    for ticket in tickets:
        (run / 'queue' / ticket).touch()
    before = snapshots(stalled)
    stderr = io.StringIO()
    with patch.object(random, 'shuffle', lambda xs: None), contextlib.redirect_stderr(stderr):
        claimed = new.claim(str(run), 'healthy-worker', 'W1')
    assert claimed == tickets[1] and (run / 'queue' / tickets[0]).exists()
    assert snapshots(stalled) == before
    assert 'operator recovery needed' in stderr.getvalue()
    result['cases']['claim_skips_stalled_setting'] = {
        'healthy_setting_claimed': claimed, 'stalled_ticket_retained': True,
        'stalled_owner_files_unchanged': True, 'diagnostic': stderr.getvalue()}

    # Recovery of finished PBS claims likewise leaves the stalled claim intact.
    # The local fake executable returns only a finished-job record; no PBS is contacted.
    fakeq = tmp / 'qstat-fixture'
    fakeq.write_text('#!/bin/sh\nprintf "    job_state = F\\n"\n')
    fakeq.chmod(0o755)
    (run / 'queue' / tickets[0]).unlink()
    stalled_claim = tickets[0] + '@old[1].srv.0'
    (run / 'claimed' / stalled_claim).touch()
    stderr = io.StringIO()
    with contextlib.redirect_stderr(stderr):
        n = new.recover_stale(str(run), 'new[2].srv.0', 'W1', str(fakeq))
    assert n == 0 and (run / 'claimed' / stalled_claim).exists()
    assert snapshots(stalled) == before
    assert 'not requeued' in stderr.getvalue()
    result['cases']['recovery_retains_stalled_claim'] = {
        'requeued': n, 'stalled_claim_retained': True,
        'stalled_owner_files_unchanged': True, 'diagnostic': stderr.getvalue()}

result['all_assertions_passed'] = True
result['timestamp'] = datetime.now(ZoneInfo('Australia/Hobart')).isoformat()
(OUT / 'lock_closure_checks.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
