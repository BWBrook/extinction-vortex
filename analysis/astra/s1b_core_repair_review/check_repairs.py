"""Finite replay of the earlier Stage 1b planner/collector defects and lock races.

Actual p3 module plus unmodified AST-extracted p2 storage/runner functions;
every one_batch call is synthetic. No proposals or population paths are drawn.
"""
import ast
import builtins
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import types
from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / 'analysis/fable/calibration/v2_dev'
OUT = Path(__file__).resolve().parent
P2, P3 = SRC / 'p2_stage1a.py', SRC / 'p3_stage1b.py'
p2 = types.ModuleType('p2_stage1a')
p2.__dict__.update(hashlib=hashlib, json=json, os=os, tempfile=tempfile,
                   time=time, CKPT_SECS=60., EMPTY_SHA=hashlib.sha256(b'').hexdigest())
names = ('sha', 'atomic_json', 'journal_prefix', 'replace_bytes', 'run_setting')
for node in ast.parse(P2.read_text()).body:
    if ((isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and
          t.id in ('COUNTERS', 'PARAMS', 'HIT_KEYS') for t in node.targets)) or
            (isinstance(node, ast.FunctionDef) and node.name in names)):
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(P2), 'exec'), p2.__dict__)


def forbidden(*args, **kwargs):
    raise AssertionError('Unmocked scientific sampler is forbidden in this audit')


p2.one_batch = forbidden
p2.runtime = lambda: {'audit': 'synthetic shim; no numerical runtime qualification'}
sys.modules['p2_stage1a'] = p2
spec = importlib.util.spec_from_file_location('s1b_repair_audit_target', P3)
p = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = p
spec.loader.exec_module(p)
p.K, p.BATCH = 5, 10
result = {'scope': __doc__, 'source_sha256': {'p2': p2.sha(P2), 'p3': p2.sha(P3)},
          'p2_functions_loaded_verbatim_from_ast': names, 'cases': {}}
cases = result['cases']


def make(tmp, name):
    d = tmp / name
    d.mkdir()
    run = d / 'run'
    for x in ('queue', 'claimed', 'sets/s00007/ranges', 'lib', 'workers'):
        (run / x).mkdir(parents=True, exist_ok=True)
    st = {'index': 7, 'pop': 'synthetic', 'outer': 'toy/0', 'n': 30,
          'E': {'n': 30, 'k': 1, 'r': 1}, 'rate': 10 / 3600,
          'cap_batches': 20, 'prior_hpb': 1., 'wave': 'W1', 'dir': 's00007',
          'library': 'primary', 'stream_tag': 2, 'pilot': None}
    b = {'settings': [st], 'metric_sha256': 'synthetic-metric',
         'runner_sha256': 'synthetic-runner', 'cap_cpu_h': 20.,
         'min_shard_cpu_h': 0., 'target_wall_h': 24., 'max_inflight': 1, 'overshoot': 1.}
    sp, mp = d / 'settings.json', d / 'metric.json'
    sp.write_text(json.dumps(b))
    mp.write_text(json.dumps({'outers': {'synthetic|toy/0': {'recorded': [4, 3, 0]}},
                             'pops': {'synthetic': {'keep': [], 'mad': []}}}))
    return d, run, run / 'sets/s00007', st, b, sp, mp


def fake(hits, shift=0):
    def f(st, mp, bi, B, des):
        x = {k: 0 for k in p2.COUNTERS}
        x.update(proposals=B, poisson_accept=B, theta_accept=B, paths=B,
                 selected_SA=hits, hits=hits, hits_lo=hits, hits_hi=hits)
        x['hit_records'] = [dict(batch=bi + shift, proposal_in_batch=j, boundary=False,
                                 theta={k: .5 for k in p2.PARAMS}, recorded=[4, 3, 0])
                            for j in range(hits)]
        return x
    return f


def shard(st, b, sp, sd, a, end, n, hits, shift=0, hit_stop=10**9):
    (sd / 'ranges' / f'{a:09d}-{end:09d}').touch()
    sst = dict(st, proposal_budget=st['cap_batches'] * p.BATCH, batches=n)
    with patch.object(p2, 'one_batch', fake(hits, shift)):
        return p2.run_setting({'batch': p.BATCH, 'hit_stop': hit_stop,
                               '_binding': p.binding(b, sp)}, sst, {}, str(sd),
                              float('inf'), {}, ckpt_secs=0., first_batch=a,
                              name=f'sh{a:09d}')


def collect(d, run, sp, mp):
    dest = run / 'collect_W1.json'
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            p.collect(str(sp), str(mp), str(run), 'W1', str(dest))
            code = 0
        except SystemExit as ex:
            code = str(ex)
    return {'exit': code, **json.loads(dest.read_text())}


def planned(st, sd, run, b):
    with p.held(str(sd), 'audit-plan'):
        p.plan(st, str(sd), str(run), b)


with tempfile.TemporaryDirectory(prefix='s1b-core-repair-') as tmpname:
    tmp = Path(tmpname)

    # Exact earlier publication failure, followed by repeated recovery and a live claim.
    d, run, sd, st, b, sp, mp = make(tmp, 'orphan')
    original_open = builtins.open
    def crash_ticket(path, *args, **kwargs):
        if str(path).startswith(str(run / 'queue') + os.sep):
            raise KeyboardInterrupt('after range marker, before ticket')
        return original_open(path, *args, **kwargs)
    try:
        with patch.object(builtins, 'open', crash_ticket):
            planned(st, sd, run, b)
    except KeyboardInterrupt:
        pass
    before = {'ranges': p.ranges(str(sd)), 'queued': len(list((run / 'queue').iterdir()))}
    planned(st, sd, run, b)
    planned(st, sd, run, b)
    queued = list((run / 'queue').iterdir())
    ticket = p.claim(str(run), 'audit-worker', 'W1')
    planned(st, sd, run, b)
    cases['orphan_repaired_once_without_duplicating_claim'] = {
        'before': before, 'queue_after_two_retries': [x.name for x in queued],
        'claimed': ticket, 'queue_after_replanning_live_claim': os.listdir(run / 'queue'),
        'claims_after_replanning': os.listdir(run / 'claimed')}
    assert before['queued'] == 0 and len(queued) == 1 and ticket
    assert not os.listdir(run / 'queue') and len(os.listdir(run / 'claimed')) == 1

    # Age alone no longer breaks a live owner's lock; token-safe release also works.
    d, run, sd, st, b, sp, mp = make(tmp, 'live_lock')
    held = p.lock(str(sd), 'live-owner')
    os.utime(held[0], (time.time() - 100000., time.time() - 100000.))
    class ObservedWait(Exception):
        pass
    try:
        with patch.object(time, 'sleep', side_effect=ObservedWait):
            p.lock(str(sd), 'would-be-stealer')
    except ObservedWait:
        pass
    unchanged = json.loads((sd / 'lock/owner.json').read_text())['token'] == held[1]
    try:
        p.unlock((held[0], 'wrong-token'))
        refused = False
    except RuntimeError:
        refused = True
    cases['old_live_lock_and_foreign_unlock'] = {'aged_live_owner_preserved': unchanged,
                                               'foreign_unlock_refused': refused}
    assert unchanged and refused
    p.unlock(held)

    # Two actual threads both observe the dead generation. A acquires and remains
    # inside its critical section before B acts on its old observation. The hook
    # controls scheduling only; owner_dead itself still uses the real PID check.
    d, run, sd, st, b, sp, mp = make(tmp, 'dead_lock_race')
    (sd / 'lock').mkdir()
    dead = {'owner': 'dead-owner', 'host': os.uname().nodename,
            'pid': 2147483647, 'token': 'dead-generation'}
    assert not p.pid_alive(dead['pid'])
    (sd / 'lock/owner.json').write_text(json.dumps(dead))
    original_dead = p.owner_dead
    both_read = threading.Barrier(2)
    a_acquired = threading.Event()
    acquired, failures, events = {}, {}, []
    def interleaved_dead(info, qstat=p.QSTAT):
        if info['token'] == dead['token']:
            name = threading.current_thread().name
            events.append(name + ' read dead generation')
            both_read.wait(timeout=5)
            if name == 'B':
                assert a_acquired.wait(timeout=5)
        return original_dead(info, qstat)
    def contender(name):
        try:
            acquired[name] = p.lock(str(sd), 'live-' + name)
            events.append(name + ' acquired without releasing')
            if name == 'A':
                a_acquired.set()
        except Exception as ex:
            failures[name] = repr(ex)
    with patch.object(p, 'owner_dead', interleaved_dead):
        threads = [threading.Thread(target=contender, args=(n,), name=n, daemon=True) for n in ('A', 'B')]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=6)
    assert not failures and not any(t.is_alive() for t in threads), (failures, events)
    current = json.loads((sd / 'lock/owner.json').read_text())
    try:
        p.unlock(acquired['A'])
        stale_release = 'unexpectedly accepted'
    except RuntimeError as ex:
        stale_release = str(ex)
    cases['dead_owner_reclaim_race'] = {
        'events': events, 'both_acquired_without_release': len(acquired) == 2,
        'acquired_tokens': {n: L[1] for n, L in acquired.items()},
        'current_owner': current, 'A_unlock': stale_release,
        'broken_generations': [json.loads(x.read_text()) for x in sorted(sd.glob('lock.broken.*/owner.json'))]}
    assert len(acquired) == 2 and acquired['A'][1] != acquired['B'][1]
    assert current['token'] == acquired['B'][1] and current['pid'] == os.getpid()
    assert 'not owned' in stale_release
    p.unlock(acquired['B'])

    # Three original collector counterexamples must now fail.
    d, run, sd, st, b, sp, mp = make(tmp, 'short_ranges')
    shard(st, b, sp, sd, 0, 10, 1, 2)
    shard(st, b, sp, sd, 10, 20, 1, 3)
    planned(st, sd, run, b)
    c = collect(d, run, sp, mp)
    cases['short_complete_ranges_rejected'] = c
    assert not c['collection_ok'] and c['rows'][0]['status'] == 'invalid'
    assert not (run / 'lib/s00007.jsonl').exists()

    d, run, sd, st, b, sp, mp = make(tmp, 'nonprefix')
    shard(st, b, sp, sd, 0, 1, 1, 5)
    (sd / 'ranges/000000001-000000002').touch()
    p2.atomic_json({'status': 'running', 'binding': {'wrong': True}, 'cpu_seconds': -3600.},
                   str(sd / 'sh000000001.json'))
    planned(st, sd, run, b)
    c = collect(d, run, sp, mp)
    cases['malformed_discarded_shard_rejected'] = c
    assert not c['collection_ok'] and c['rows'][0]['status'] == 'invalid'

    d, run, sd, st, b, sp, mp = make(tmp, 'outside_range')
    shard(st, b, sp, sd, 0, 1, 1, 5, shift=9999)
    planned(st, sd, run, b)
    c = collect(d, run, sp, mp)
    cases['outside_range_identity_rejected'] = c
    assert not c['collection_ok'] and c['rows'][0]['status'] == 'invalid'

    # Negative accounting alone is rejected, even in a discarded shard.
    d, run, sd, st, b, sp, mp = make(tmp, 'negative_cost')
    shard(st, b, sp, sd, 0, 1, 1, 5)
    shard(st, b, sp, sd, 1, 2, 1, 0)
    state = sd / 'sh000000001.json'
    S = json.loads(state.read_text()); S['cpu_seconds'] = -3600.
    p2.atomic_json(S, str(state))
    planned(st, sd, run, b)
    c = collect(d, run, sp, mp)
    cases['negative_discarded_cpu_rejected'] = c
    assert not c['collection_ok'] and 'domain' in c['errors'][0]

    # A valid hit stop inside a larger declared range, plus cancelled later work.
    d, run, sd, st, b, sp, mp = make(tmp, 'positive_control')
    shard(st, b, sp, sd, 0, 10, 10, 5, hit_stop=5)
    shard(st, b, sp, sd, 10, 20, 1, 0)
    state = sd / 'sh000000010.json'
    S = json.loads(state.read_text()); S['status'] = 'cancelled'; S['stop'] = 'cancelled'
    p2.atomic_json(S, str(state))
    planned(st, sd, run, b)
    c = collect(d, run, sp, mp)
    cases['valid_early_hit_stop_and_cancelled_later_shard'] = c
    assert c['collection_ok'] and c['status']['COMPLETE'] == 1
    assert len((run / 'lib/s00007.jsonl').read_text().splitlines()) == p.K

result['timestamp'] = datetime.now(ZoneInfo('Australia/Hobart')).isoformat()
result['all_assertions_passed'] = True
(OUT / 'repair_checks.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'all_assertions_passed': True, 'cases': list(cases),
                  'remaining_blocker': 'dead_owner_reclaim_race'}, indent=2))
