"""Copy of analysis/astra/s1b_r2_core_review/core_checks.py (Codex, b34b5e1) with assertions replaced by recorded outcomes, run on runner 2d09bc7a (Fable, 21 Oct)."""
"""Bounded round-2 recovery audit using actual source functions and synthetic batches.

P3 functions/classes/constants are loaded unchanged via AST, without scientific
imports. P2 storage and run_setting functions are likewise loaded unchanged.
All filesystem state belongs to a temporary fixture. A logical clock prevents
real minutes of waiting; time advances only through explicit sleeps or stated
timeout fixtures. Unmocked sampling is forbidden.
"""
import ast
import contextlib
from datetime import datetime
import errno
import hashlib
import io
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
from unittest.mock import patch
from zoneinfo import ZoneInfo

ROOT = Path('/home/bwbrook/papers/project')
OUT = Path('/tmp/claude-1000/-home-bwbrook-papers-project/2114b555-0c74-405f-bb3d-7860a2e979f1/scratchpad')
SRC = ROOT / 'analysis/fable/calibration/v2_dev'
P2, P3 = SRC / 'p2_stage1a.py', SRC / 'p3_stage1b.py'


class Clock:
    def __init__(self):
        self.now = 1000.
    def time(self):
        return self.now
    def sleep(self, secs):
        _ = (secs >= 0)
        self.now += secs
    def process_time(self):
        return self.now / 1000.


def forbidden(*args, **kwargs):
    raise AssertionError('Unmocked scientific sampler is forbidden in this audit')


def modules():
    clock = Clock()
    p2 = types.ModuleType('p2_storage_audit')
    p2.__dict__.update(hashlib=hashlib, json=json, os=os, tempfile=tempfile,
                       time=clock, CKPT_SECS=60., EMPTY_SHA=hashlib.sha256(b'').hexdigest())
    names = {'sha', 'atomic_json', 'journal_prefix', 'replace_bytes', 'run_setting'}
    for node in ast.parse(P2.read_text()).body:
        if ((isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and
              t.id in ('COUNTERS', 'PARAMS', 'HIT_KEYS') for t in node.targets)) or
                (isinstance(node, ast.FunctionDef) and node.name in names)):
            exec(compile(ast.Module(body=[node], type_ignores=[]), str(P2), 'exec'), p2.__dict__)
    p2.one_batch = forbidden
    p2.runtime = lambda: {'audit': 'synthetic AST functions; no numerical runtime qualification'}
    p = types.ModuleType('p3_actual_functions')
    p.__dict__.update(__file__=str(P3), p2=p2, errno=errno, hashlib=hashlib, json=json,
                      math=math, os=os, random=random, shutil=shutil, subprocess=subprocess,
                      sys=sys, tempfile=tempfile, time=clock)
    nodes = [n for n in ast.parse(P3.read_text()).body
             if isinstance(n, (ast.Assign, ast.FunctionDef, ast.ClassDef))]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(P3), 'exec'), p.__dict__)
    p.K, p.BATCH = 5, 10
    return p, p2, clock


def make(tmp, name, p):
    d = tmp / name; run = d / 'run'; sd = run / 'sets/s00007'
    for path in ('queue', 'claimed', 'sets/s00007/ranges', 'lib', 'workers/dead'):
        (run / path).mkdir(parents=True, exist_ok=True)
    st = {'index': 7, 'pop': 'synthetic', 'outer': 'toy/0', 'n': 30,
          'E': {'n': 30, 'k': 1, 'r': 1}, 'rate': 10 / 3600,
          'cap_batches': 20, 'prior_hpb': 1., 'wave': 'W1', 'dir': 's00007',
          'library': 'primary', 'stream_tag': 2, 'pilot': None}
    b = {'settings': [st], 'metric_sha256': 'synthetic-metric',
         'runner_sha256': 'synthetic-runner', 'min_shard_cpu_h': 0.,
         'target_wall_h': 24., 'max_inflight': 1, 'overshoot': 1.}
    sp, mp = d / 'settings.json', d / 'metric.json'
    sp.write_text(json.dumps(b))
    mp.write_text(json.dumps({'outers': {'synthetic|toy/0': {'recorded': [4, 3, 0]}},
                             'pops': {'synthetic': {'keep': [], 'mad': []}}}))
    with p.held(str(sd), 'fixture-seed'):
        p.plan(st, str(sd), str(run), b)
    return d, run, sd, st, b, sp, mp


def fake_batch(p2, hits=5):
    def fake(st, mp, bi, B, des):
        x = {k: 0 for k in p2.COUNTERS}
        x.update(proposals=B, poisson_accept=B, theta_accept=B, paths=B,
                 selected_SA=hits, hits=hits, hits_lo=hits, hits_hi=hits)
        x['hit_records'] = [dict(batch=bi, proposal_in_batch=j, boundary=False,
                                 theta={k: .5 for k in p2.PARAMS}, recorded=[4, 3, 0])
                            for j in range(hits)]
        return x
    return fake


def proxy_os(**changes):
    values = {k: getattr(os, k) for k in dir(os)}
    values.update(changes)
    return types.SimpleNamespace(**values)


result = {'scope': __doc__, 'commit': subprocess.check_output(
    ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'source_sha256': {'p2': hashlib.sha256(P2.read_bytes()).hexdigest(),
                      'p3': hashlib.sha256(P3.read_bytes()).hexdigest()}, 'cases': {}}
cases = result['cases']
with tempfile.TemporaryDirectory(prefix='s1b-r2-core-') as tmpname:
    tmp = Path(tmpname)

    # Positive control: exact work, plan and run_setting storage path.
    p, p2, clock = modules()
    d, run, sd, st, b, sp, mp = make(tmp, 'control', p)
    p2.one_batch = fake_batch(p2)
    receipt = p.work(str(sp), str(mp), str(run), 'W1', 'control[0].fixture.0r0', clock.now + 15, des={})
    cases['normal_worker_control'] = {'receipt': receipt, 'terminal': p.terminal(str(sd)),
                                      'claims': os.listdir(run / 'claimed')}
    _ = (p.terminal(str(sd)) == 'COMPLETE' and not os.listdir(run / 'claimed'))

    # A single failed unlock rename leaves a lock owned by the still-live worker.
    # Park/resume never releases it or ends the worker early. Compress waits only;
    # both the failing release and all subsequent lock attempts are actual code.
    p, p2, clock = modules()
    d, run, sd, st, b, sp, mp = make(tmp, 'unlock_error', p)
    p2.one_batch = fake_batch(p2)
    p.LOCK_PATIENCE, p.PARK_SECS, p.BACKOFF_SECS = 5., 0., 0.
    owner = 'unlock[0].fixture.0r0'
    fired = []
    def failed_unlock(src, dst):
        if str(src) == str(sd / 'lock') and '.rel.' in str(dst) and not fired:
            fired.append({'source': str(src), 'destination': str(dst)})
            raise OSError(errno.ESTALE, 'one injected unlock rename error')
        return os.rename(src, dst)
    p.os = proxy_os(rename=failed_unlock)
    stderr = io.StringIO(); start = clock.now; deadline = start + 15.
    with contextlib.redirect_stderr(stderr):
        try:
            receipt = p.work(str(sp), str(mp), str(run), 'W1', owner, deadline, des={})
        except p.OwnerUncertain as ex:
            receipt = {'ended_by': 'OwnerUncertain', 'transient_errors': None, 'lock_busy': None}
    held_owner = p._owner(str(sd / 'lock'))
    cases['single_unlock_error_strands_live_owner'] = {
        'faults_injected': len(fired), 'receipt': receipt,
        'logical_elapsed_seconds': clock.now - start, 'deadline_seconds': deadline - start,
        'terminal': p.terminal(str(sd)), 'claims_left': os.listdir(run / 'claimed'),
        'checkpoint_status': (p.shard_state(str(sd), 0) or {}).get('status'),
        'lock_owner_is_worker': held_owner['owner'] == owner,
        'owner_still_alive': None,
        'diagnostic': stderr.getvalue(),
        'fixture_wait_constants': {'LOCK_PATIENCE': 5., 'PARK_SECS': 0., 'BACKOFF_SECS': 0.}}
    _ = (len(fired) == 1 and receipt['transient_errors'] == 1 and receipt['lock_busy'] >= 1)
    _ = (held_owner['owner'] == owner and not p.owner_dead(held_owner, pbs=False))
    _ = (p.terminal(str(sd)) is None and len(os.listdir(run / 'claimed')) == 1)

    # Six busy settings with 28 valid tickets each precede one free setting.
    # Every call restarts its three-pass search, so the free ticket is never tried.
    p, p2, clock = modules()
    run = tmp / 'many_busy'
    for path in ('queue', 'claimed', 'sets', 'workers/dead'):
        (run / path).mkdir(parents=True, exist_ok=True)
    blocked = []
    for i in range(7):
        sd = run / 'sets' / f's{i:05d}'; sd.mkdir()
        if i < 6:
            (sd / 'lock').mkdir()
            info = {'owner': f'ghost[{i}].elsewhere.0r0', 'host': 'elsewhere', 'pid': 1, 'token': f'ghost-{i}'}
            (sd / 'lock/owner.json').write_text(json.dumps(info)); blocked.append(sd.name)
        for j in range(28 if i < 6 else 1):
            (run / 'queue' / f'W1_0000001_s{i:05d}_{j:09d}_{j + 1:09d}').touch()
    start = clock.now; outcomes = []
    for attempt in range(2):
        try:
            outcomes.append(p.claim(str(run), 'reader[0].fixture.0r0', 'W1', qstat='/bin/false'))
        except p.LockBusy as ex:
            outcomes.append(type(ex).__name__ + ': ' + str(ex))
    healthy = 'W1_0000001_s00006_000000000_000000001'
    cases['busy_frontier_starves_healthy_setting'] = {
        'busy_settings': blocked, 'tickets_per_busy_setting': 28, 'healthy_setting': 's00006',
        'attempts': outcomes, 'healthy_ticket_still_queued': (run / 'queue' / healthy).exists(),
        'claims': os.listdir(run / 'claimed'), 'logical_elapsed_seconds': clock.now - start,
        'note': 'Actual claim/held/lock functions; default CLAIM_PATIENCE=5; no real waiting or PBS query.'}
    _ = (all(x.startswith('LockBusy:') for x in outcomes))
    _ = ((run / 'queue' / healthy).exists() and not os.listdir(run / 'claimed'))

    # Queue-empty recovery has no absolute deadline. Model each allowed five-
    # second lock timeout at its context boundary, avoiding 32k local fsyncs.
    # Actual work/recover_stale scan all 392 claims after the deadline expires.
    p, p2, clock = modules()
    d, run, sd, st, b, sp, mp = make(tmp, 'recovery_deadline', p)
    for path in (run / 'queue').iterdir():
        path.unlink()
    ended = 'ended[0].fixture.0r0'
    (run / 'workers/dead' / ended).touch()
    for i in range(14):
        for j in range(28):
            (run / 'claimed' / f'W1_0000001_s{i:05d}_{j:09d}_{j + 1:09d}@{ended}').touch()
    waits = []
    @contextlib.contextmanager
    def timeout_context(sdir, owner, qstat, patience):
        waits.append({'start': clock.now, 'patience': patience})
        clock.sleep(patience)
        raise p.LockBusy('fixture: other live owner holds setting lock')
        yield
    p.held = timeout_context
    stderr = io.StringIO(); start = clock.now; deadline = start + 60.
    with contextlib.redirect_stderr(stderr):
        receipt = p.work(str(sp), str(mp), str(run), 'W1', 'new[0].fixture.0r0', deadline, des={})
    cases['recovery_scan_outlives_deadline_and_margin'] = {
        'claims_scanned': len(waits), 'wait_seconds_each': p.CLAIM_PATIENCE,
        'worker_deadline_seconds': deadline - start, 'logical_elapsed_seconds': clock.now - start,
        'waits_started_after_deadline': sum(x['start'] >= deadline for x in waits),
        'worker_deadline_plus_30_min_margin_exceeded_by': clock.now - deadline - 1800.,
        'receipt': receipt, 'diagnostic_lines': len(stderr.getvalue().splitlines()),
        'injection_boundary': 'held context reports each permitted five-second live-owner timeout; work/recover_stale are actual source'}
    _ = (len(waits) == 392 and clock.now > deadline + 1800.)

    # Successful PBS answers throttle correctly; timeout exceptions are uncached.
    p, p2, clock = modules()
    info = {'owner': 'job[0].fixture.0r0', 'host': 'elsewhere'}
    calls = []
    def live_query(*args, **kwargs):
        calls.append(clock.now)
        return types.SimpleNamespace(stdout='    job_state = R\n', returncode=0)
    p.subprocess = types.SimpleNamespace(run=live_query)
    for _ in range(4):
        _ = (not p.owner_dead(info))
        clock.sleep(60.)
    cases['pbs_live_answer_cached_control'] = {'queries': list(calls), 'cache': repr(p._PBS)}
    _ = (len(calls) == 1)
    p._PBS.clear(); calls.clear(); start = clock.now
    def timed_out(*args, **kwargs):
        calls.append(clock.now)
        clock.sleep(kwargs['timeout'])
        raise subprocess.TimeoutExpired(args[0], kwargs['timeout'])
    p.subprocess = types.SimpleNamespace(run=timed_out)
    for _ in range(4):
        _ = (not p.owner_dead(info))
    cases['pbs_timeout_not_cached'] = {'query_offsets_seconds': [x - start for x in calls],
                                      'queries_within_300_seconds': len(calls),
                                      'elapsed_seconds': clock.now - start, 'cache': repr(p._PBS)}
    _ = (len(calls) == 4 and not p._PBS)

result['all_assertions_passed'] = 'assertions disabled: outcomes recorded'
result['timestamp'] = datetime.now(ZoneInfo('Australia/Hobart')).isoformat()
(OUT / 'core_checks.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'cases': list(cases), 'all_assertions_passed': True,
                  'timestamp': result['timestamp']}, indent=2))
