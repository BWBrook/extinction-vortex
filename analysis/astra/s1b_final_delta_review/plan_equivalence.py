"""Bounded old/current planner equivalence under its actual setting lock.

Loads source functions unchanged via AST; all checkpoints and counters are
synthetic. No sampler imports, proposals, population paths or scheduler calls.
"""
import ast
from datetime import datetime
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
TARGET = 'analysis/fable/calibration/v2_dev/p3_stage1b.py'
OLD = 'ca94676'
NAMES = {'pid_alive', 'owner_dead', '_owner', '_publish', '_reclaim', 'lock',
         'unlock', 'held', 'LockStale', 'ranges', 'shard_state', 'prefix',
         'terminal', 'mark', 'ticket_name', 'plan'}
old_source = subprocess.check_output(['git', 'show', f'{OLD}:{TARGET}'], cwd=ROOT, text=True)
new_source = (ROOT / TARGET).read_text()


def load(source, name):
    module = types.ModuleType(name)
    module.__dict__.update(os=os, json=json, math=math, random=random, shutil=shutil,
                           subprocess=subprocess, time=time, sys=sys, K=5, BATCH=10,
                           PRIOR_HITS=2., QSTAT='/opt/pbs/bin/qstat',
                           TERMINAL=('COMPLETE', 'CAPPED', 'FAILED'))
    nodes = [node for node in ast.parse(source).body
             if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in NAMES]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), name, 'exec'), module.__dict__)
    return module


modules = {'old': load(old_source, 'old_planner'), 'current': load(new_source, 'current_planner')}


def shard(a, end, status=None, done=0, hits=0, location=None):
    return {'a': a, 'end': end, 'status': status, 'done': done,
            'hits': hits, 'location': location}


cases = [
    {'name': 'fresh_setting'},
    {'name': 'pilot_prefix_only', 'pilot': {'batches_done': 2, 'hits': 1, 'cpu_seconds': 20.}},
    *[{'name': 'existing_terminal_' + s, 'terminal': s} for s in ('COMPLETE', 'CAPPED', 'FAILED')],
    {'name': 'failed_shard', 'shards': [shard(0, 2, 'failed', 1)]},
    {'name': 'new_complete_marker', 'shards': [shard(0, 5, 'complete', 1, 5)]},
    {'name': 'new_capped_marker', 'shards': [shard(0, 20, 'complete', 20)]},
    {'name': 'complete_nonterminal_successor', 'shards': [shard(0, 2, 'complete', 2, 1)]},
    {'name': 'cancelled_range', 'shards': [shard(0, 2, 'cancelled', 1)]},
    {'name': 'unstarted_orphan', 'shards': [shard(0, 5)]},
    {'name': 'running_orphan', 'shards': [shard(0, 5, 'running', 1, 1)]},
    {'name': 'censored_orphan', 'shards': [shard(0, 5, 'censored', 1, 1)]},
    {'name': 'queued_range', 'shards': [shard(0, 5, location='queue')]},
    {'name': 'live_claim', 'shards': [shard(0, 5, 'running', 1, 1, 'claim')]},
    {'name': 'completed_range_still_claimed', 'shards': [shard(0, 2, 'complete', 2, 1, 'claim')]},
    {'name': 'mixed_multiple_unfinished', 'shards': [
        shard(0, 2, 'complete', 2, 1), shard(2, 4, 'cancelled', 1),
        shard(4, 8, 'running', 1, 1, 'claim'), shard(8, 12, location='queue'),
        shard(12, 16, 'censored', 1), shard(16, 20)]},
]


def run_case(module, root, case):
    run = root / 'run'; sd = run / 'sets/s00007'
    for path in ('queue', 'claimed', 'sets/s00007'):
        (run / path).mkdir(parents=True, exist_ok=True)
    st = {'dir': 's00007', 'wave': 'W1', 'pilot': case.get('pilot'),
          'cap_batches': 20, 'rate': 1., 'prior_hpb': 1.}
    b = {'min_shard_cpu_h': 0., 'target_wall_h': 24., 'max_inflight': 3, 'overshoot': 1.}
    for x in case.get('shards', []):
        (sd / 'ranges').mkdir(exist_ok=True)
        (sd / 'ranges' / f"{x['a']:09d}-{x['end']:09d}").touch()
        if x['status']:
            S = {'status': x['status'], 'batches_done': x['done'], 'hits': x['hits'],
                 'cpu_seconds': 10. * x['done'], 'failure': 'fixture' if x['status'] == 'failed' else None}
            (sd / f"sh{x['a']:09d}.json").write_text(json.dumps(S))
        ticket = module.ticket_name(st, x['a'], x['end'], 17)
        if x['location'] == 'queue':
            (run / 'queue' / ticket).touch()
        elif x['location'] == 'claim':
            (run / 'claimed' / (ticket + '@synthetic-owner')).touch()
    if 'terminal' in case:
        (sd / case['terminal']).write_text('{"fixture": true}')
    # Other settings may change while this setting is locked; their names are
    # excluded identically from both snapshots. Include both wave namespaces.
    (run / 'queue/W1_0000001_s99999_000000000_000000005').touch()
    (run / 'claimed/W2_0000001_c00007_000000000_000000005@peer').touch()
    listings = {'queue': 0, 'claimed': 0}
    real_listdir = os.listdir
    proxy = types.SimpleNamespace(**{k: getattr(os, k) for k in dir(os)})
    def counted(path):
        if str(path) == str(run / 'queue'):
            listings['queue'] += 1
        if str(path) == str(run / 'claimed'):
            listings['claimed'] += 1
        return real_listdir(path)
    proxy.listdir = counted
    module.os = proxy
    with module.held(str(sd), 'equivalence-fixture'):
        module.plan(st, str(sd), str(run), b)
    first_listings = dict(listings)
    snapshot = {str(p.relative_to(run)): p.read_text() for p in sorted(run.rglob('*')) if p.is_file()}
    # Replanning exercises publication idempotence and lazy scanning of ranges
    # created by the first call; compare old/current after this call as well.
    with module.held(str(sd), 'equivalence-fixture'):
        module.plan(st, str(sd), str(run), b)
    second_snapshot = {str(p.relative_to(run)): p.read_text() for p in sorted(run.rglob('*')) if p.is_file()}
    return {'first_snapshot': snapshot, 'second_snapshot': second_snapshot,
            'first_listings': first_listings,
            'second_listings': {k: listings[k] - first_listings[k] for k in listings}}


result = {'scope': __doc__, 'old_commit': OLD,
          'current_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
          'source_sha256': {'old': hashlib.sha256(old_source.encode()).hexdigest(),
                            'current': hashlib.sha256(new_source.encode()).hexdigest()}, 'cases': []}
with tempfile.TemporaryDirectory(prefix='s1b-plan-equivalence-') as tmpname:
    tmp = Path(tmpname)
    for case in cases:
        runs = {label: run_case(module, tmp / case['name'] / label, case)
                for label, module in modules.items()}
        a, b = runs['old'], runs['current']
        assert a['first_snapshot'] == b['first_snapshot'], case['name']
        assert a['second_snapshot'] == b['second_snapshot'], case['name']
        for counts in (b['first_listings'], b['second_listings']):
            assert counts['queue'] == counts['claimed'] and counts['queue'] <= 1
        result['cases'].append({'name': case['name'], 'first_state_identical': True,
                                'repeated_plan_state_identical': True,
                                'old_listings': [a['first_listings'], a['second_listings']],
                                'current_listings': [b['first_listings'], b['second_listings']],
                                'output_paths': sorted(b['first_snapshot'])})

result['production_callers_inspected'] = {
    'seed': 'plan at line 392 is inside with held(sdir, owner, qstat)',
    'work': 'plan at line 485 is inside with held(sdir, owner, qstat); claim unlink follows under same lock',
    'other_calls': 'remaining direct plan calls are local synthetic test fixtures'}
result['all_assertions_passed'] = True
result['timestamp'] = datetime.now(ZoneInfo('Australia/Hobart')).isoformat()
(OUT / 'plan_equivalence.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'cases': len(cases), 'all_assertions_passed': True,
                  'source_sha256': result['source_sha256'], 'timestamp': result['timestamp']}, indent=2))
