"""Bounded Stage 1b core review: actual p3 code plus exact p2 storage/runner functions.

SciPy and pandas are absent locally. The p2 shim loads only unchanged-source AST
functions for byte storage, hashing and run_setting, and rejects unmocked
one_batch. All batches below are synthetic; no scientific sampler is imported.
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
import time
import types
from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / 'analysis/fable/calibration/v2_dev'
OUT = Path(__file__).resolve().parent
P2 = SRC / 'p2_stage1a.py'
P3 = SRC / 'p3_stage1b.py'
started = time.perf_counter()

p2 = types.ModuleType('p2_stage1a')
p2.__dict__.update(hashlib=hashlib, json=json, os=os, tempfile=tempfile,
                   time=time, CKPT_SECS=60., EMPTY_SHA=hashlib.sha256(b'').hexdigest())
tree = ast.parse(P2.read_text())
for node in tree.body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in
                                          ('COUNTERS', 'PARAMS', 'HIT_KEYS') for t in node.targets):
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(P2), 'exec'), p2.__dict__)
names = ('sha', 'atomic_json', 'journal_prefix', 'replace_bytes', 'run_setting')
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name in names:
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(P2), 'exec'), p2.__dict__)

def forbidden(*args, **kwargs):
    raise AssertionError('Unmocked scientific sampler is forbidden in this audit')

p2.one_batch = forbidden
p2.runtime = lambda: {'audit': 'synthetic shim; no numerical runtime qualification'}
sys.modules['p2_stage1a'] = p2
spec = importlib.util.spec_from_file_location('s1b_core_audit_target', P3)
p = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = p
spec.loader.exec_module(p)
res = {'scope': __doc__, 'timestamp': datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),
       'source_sha256': {'p2': p2.sha(P2), 'p3': p2.sha(P3)},
       'p2_functions_loaded_verbatim_from_ast': names, 'cases': {}}

# Native numerical imports are deliberately absent. This is a control-flow
# replay of the published all-synthetic p3 suite, not a qualified-runtime test.
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    p.test()
(OUT / 'published_synthetic_suite.log').write_text(buf.getvalue())
last = buf.getvalue().rfind('{')
res['published_synthetic_suite'] = json.loads(buf.getvalue()[last:])

p.K, p.BATCH = 5, 10
with tempfile.TemporaryDirectory(prefix='s1b-python-audit-') as tmp:
    tmp = Path(tmp)

    def make(name, cap=20):
        d = tmp / name
        d.mkdir()
        run = d / 'run'
        for x in ('queue', 'claimed', 'sets/s00007/ranges', 'lib', 'workers'):
            (run / x).mkdir(parents=True, exist_ok=True)
        st = {'index': 7, 'pop': 'synthetic', 'outer': 'toy/0', 'n': 30,
              'E': {'n': 30, 'k': 1, 'r': 1}, 'rate': 10 / 3600,
              'cap_batches': cap, 'prior_hpb': 1., 'wave': 'W1', 'dir': 's00007',
              'library': 'primary', 'stream_tag': 2, 'pilot': None}
        b = {'settings': [st], 'metric_sha256': 'synthetic-metric',
             'runner_sha256': 'synthetic-runner', 'cap_cpu_h': float(cap),
             'min_shard_cpu_h': 0., 'target_wall_h': 24., 'max_inflight': 1,
             'overshoot': 1.}
        sp, mp = d / 'settings.json', d / 'metric.json'
        sp.write_text(json.dumps(b))
        mp.write_text(json.dumps({'outers': {'synthetic|toy/0': {'recorded': [4, 3, 0]}},
                                 'pops': {'synthetic': {'keep': [], 'mad': []}}}))
        return d, run, run / 'sets/s00007', st, b, sp, mp

    def fake(hits, batch_shift=0):
        def f(st, mp, bi, B, des):
            x = {k: 0 for k in p2.COUNTERS}
            x.update(proposals=B, poisson_accept=B, theta_accept=B, paths=B,
                     selected_SA=hits, hits=hits, hits_lo=hits, hits_hi=hits)
            x['hit_records'] = [dict(batch=bi + batch_shift, proposal_in_batch=j,
                                     boundary=False, theta={k: .5 for k in p2.PARAMS},
                                     recorded=[4, 3, 0]) for j in range(hits)]
            return x
        return f

    def shard(st, b, sp, sdir, a, end, batches_done, hits, batch_shift=0):
        (sdir / 'ranges' / f'{a:09d}-{end:09d}').touch()
        sst = dict(st, proposal_budget=st['cap_batches'] * p.BATCH, batches=batches_done)
        with patch.object(p2, 'one_batch', fake(hits, batch_shift)):
            return p2.run_setting({'batch': p.BATCH, 'hit_stop': 10**9,
                                   '_binding': p.binding(b, sp)}, sst, {}, str(sdir),
                                  float('inf'), {}, ckpt_secs=0., first_batch=a,
                                  name=f'sh{a:09d}')

    def collect(d, run, sp, mp):
        dest = d / 'collect.json'
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                p.collect(str(sp), str(mp), str(run), 'W1', str(dest))
                exit_value = 0
            except SystemExit as ex:
                exit_value = str(ex)
        c = json.loads(dest.read_text())
        return {'exit': exit_value, **c}

    # Crash between the range marker and its queue ticket, then a normal plan retry.
    d, run, sd, st, b, sp, mp = make('orphan_range')
    original_open = builtins.open
    def crash_ticket(path, *args, **kwargs):
        if str(path).startswith(str(run / 'queue') + os.sep):
            raise KeyboardInterrupt('injected crash after range marker before ticket')
        return original_open(path, *args, **kwargs)
    try:
        with patch.object(builtins, 'open', crash_ticket):
            p.plan(st, str(sd), str(run), b)
    except KeyboardInterrupt:
        pass
    before = {'ranges': p.ranges(str(sd)), 'queue': os.listdir(run / 'queue')}
    p.plan(st, str(sd), str(run), b)
    res['cases']['orphan_range_after_retry'] = {'before': before,
        'after': {'ranges': p.ranges(str(sd)), 'queue': os.listdir(run / 'queue'),
                  'claim': p.claim(str(run), 'newjob.0'), 'terminal': p.terminal(str(sd))}}

    # A live owner older than the age threshold is evicted, and its unlock removes
    # the replacement owner's lock. No waiting or process killing is needed.
    d, run, sd, st, b, sp, mp = make('lock_ownership')
    old = p.lock(str(sd))
    os.utime(old, (time.time() - 601, time.time() - 601))
    new = p.lock(str(sd))
    new_exists_before = os.path.isdir(new)
    stale_dirs = [x.name for x in sd.iterdir() if x.name.startswith('lock.stale.')]
    p.unlock(old)
    res['cases']['aged_live_lock_is_stolen'] = {'both_calls_returned_same_path': old == new,
        'replacement_lock_existed': new_exists_before, 'stale_dirs': stale_dirs,
        'old_owner_unlock_removed_new_owner_lock': not os.path.exists(new)}

    # Two internally valid one-batch checkpoints behind ten-batch range markers.
    # The collector must detect uncomputed gaps before blessing first K.
    d, run, sd, st, b, sp, mp = make('false_contiguous_prefix')
    shard(st, b, sp, sd, 0, 10, 1, 2)
    shard(st, b, sp, sd, 10, 20, 1, 3)
    p.plan(st, str(sd), str(run), b)
    c = collect(d, run, sp, mp)
    lib = run / 'lib/s00007.jsonl'
    res['cases']['short_complete_ranges_hide_gaps'] = {
        'collection_ok': c['collection_ok'], 'status': c['status'], 'row': c['rows'][0],
        'library_batches': [json.loads(x)['batch'] for x in lib.read_text().splitlines()]}

    # A complete early prefix plus a malformed, negative-accounting later shard.
    d, run, sd, st, b, sp, mp = make('nonprefix_validation')
    shard(st, b, sp, sd, 0, 1, 1, 5)
    (sd / 'ranges/000000001-000000002').touch()
    p2.atomic_json({'status': 'running', 'binding': {'wrong': True}, 'cpu_seconds': -3600.},
                   str(sd / 'sh000000001.json'))
    p.plan(st, str(sd), str(run), b)
    c = collect(d, run, sp, mp)
    res['cases']['nonprefix_shard_not_validated'] = {
        'collection_ok': c['collection_ok'], 'status': c['status'],
        'discarded_cpu_h': c['discarded_cpu_h'], 'errors': c['errors']}

    # Journal hash/count and field names agree, but identities are outside the range.
    d, run, sd, st, b, sp, mp = make('out_of_range_identity')
    shard(st, b, sp, sd, 0, 1, 1, 5, batch_shift=9999)
    p.plan(st, str(sd), str(run), b)
    c = collect(d, run, sp, mp)
    res['cases']['out_of_range_hit_identity_accepted'] = {
        'collection_ok': c['collection_ok'], 'status': c['status'], 'row': c['rows'][0]}

    # Proposal cap corresponds to 2 nominal CPU-h; synthetic process_time says
    # every batch cost 2 CPU-h instead of the assumed 1 CPU-h. No real work runs.
    d, run, sd, st, b, sp, mp = make('nominal_cpu_cap', cap=2)
    st['prior_hpb'] = 0.
    sp.write_text(json.dumps(b))
    p.plan(st, str(sd), str(run), b)
    ticks = iter((0., 7200., 7200., 14400.))
    with patch.object(p2, 'one_batch', fake(0)), patch.object(time, 'process_time', lambda: next(ticks)):
        done = p.work(str(sp), str(mp), str(run), 'syntheticjob.0', time.time() + 10,
                      qstat='/bin/false', des={})
    c = collect(d, run, sp, mp)
    res['cases']['nominal_cpu_cap_not_measured_cap'] = {
        'declared_cpu_h': b['cap_cpu_h'], 'cap_batches': st['cap_batches'],
        'measured_synthetic_cpu_h': c['useful_cpu_h'] + c['discarded_cpu_h'],
        'status': c['status'], 'worker': done}

    # Stable IDs and namespace separation, without generating any proposals.
    ids = [p.primary_index(pi, si, t, ni) for pi in range(9) for si in range(4)
           for t in range(200) for ni in range(3)]
    pilot = [p.primary_index(pi, si, t, ni) for pi in range(9) for si in range(4)
             for t in range(10) for ni in range(3)]
    res['stream_identity_checks'] = {
        'all_primary_ids_once': sorted(ids) == list(range(21600)),
        'pilot_ids_preserved': pilot == list(range(1080)),
        'check_namespace': 'stream_tag 3; primary tag 2; same stable index; verified in source',
        'p2_default_tag_preserved': 'st.get("stream_tag", 2)' in P2.read_text()}

smoke = json.loads((SRC / 'p3/smoke_kunanyi_collect_W1.json').read_text())
res['saved_smoke_actual_cap_comparison'] = [
    {'dir': r['dir'], 'nominal_cap_cpu_h': 1.5, 'status': r['status'],
     'cpu_h': r['useful_cpu_h'] + r['discarded_cpu_h'],
     'fraction_over_nominal_cap': (r['useful_cpu_h'] + r['discarded_cpu_h']) / 1.5 - 1}
    for r in smoke['rows'] if r['dir'] in ('s01080', 'c00021')]
res['elapsed_s'] = time.perf_counter() - started
(OUT / 'core_checks.json').write_text(json.dumps(res, indent=2) + '\n')
print(json.dumps(res, indent=2))
