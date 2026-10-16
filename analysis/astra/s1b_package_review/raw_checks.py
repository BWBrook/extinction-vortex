"""Saved Stage 1b input/smoke audit on deep-server; no new population simulation.

Run via Python stdin. Writes only /data/codex/artifacts/project/s1b_package_review.
The supplied p3 test uses synthetic hash-derived hit records, not trajectories.
"""
from collections import Counter
from datetime import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import statistics
import subprocess
import sys
import tarfile
import time
from zoneinfo import ZoneInfo

import numpy as np

ROOT = Path('/data/fable/vortex')
V2 = ROOT / 'v2_dev'
P3 = V2 / 'p3'
SRC = ROOT / 'kunanyi_stage/run1/src'
OUT = Path('/data/codex/artifacts/project/s1b_package_review')
OUT.mkdir(parents=True, exist_ok=True)
START = time.monotonic()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(p):
    return json.loads(p.read_text())


settings_path, metric_path = P3 / 'p3_settings.json', P3 / 'p3_metric.json'
b, m = read(settings_path), read(metric_path)
ps = read(V2 / 'p2/p2_settings_s1a.json')
pc = read(V2 / 'p2/s1a_main/collect_deep.json')
pm = read(V2 / 'p2/p2_metric.json')
sm = read(P3 / 'p3_settings_smoke.json')
assert len(b['settings']) == 21816 and b['batch'] == 20000 and b['K'] == 2000
assert sha(metric_path.read_bytes()) == b['metric_sha256']
assert sha((V2 / 'p3_stage1b.py').read_bytes()) == b['runner_sha256']
assert sha((V2 / 'p2_stage1a.py').read_bytes()) == b['p2_sha256']
assert sha((V2 / 'p1_sampler.py').read_bytes()) == b['p1_sampler_sha256']
assert sha((V2 / 'p2/p2_settings_s1a.json').read_bytes()) == b['pilot_settings_sha256']
assert sha((V2 / 'p2/s1a_main/collect_deep.json').read_bytes()) == b['pilot_collect_sha256']
for path, digest in b['imported_source_sha256'].items():
    assert sha((SRC / path).read_bytes()) == digest
assert len(m['outers']) == 7200 and len(m['E']) == 14400
assert all(m['outers'][k] == v for k, v in pm['outers'].items())
assert all(m['E'][k] == v for k, v in pm['E'].items())
assert all(m[k] == pm[k] for k in ('pops', 'source_bank_sha256', 'bank_meta_sha256', 's0_inputs_sha256'))

# Bind every exported recorded series, radius and evidence record to saved Stage 0.
# The 180 bank shards are not rescanned; their previously checked binding is unchanged.
s0p = V2 / 's0/s0_inputs.json'
s0 = read(s0p)
assert sha(s0p.read_bytes()) == m['s0_inputs_sha256']
sys.path.insert(0, str(SRC / 'analysis/fable/calibration'))
import bank
pops = list(m['pops'])
scens = ['null_prior_predictive', 'null_low_s', 'MA_betamin', 'MA_d10_0.5']
checked_outers = checked_E = 0
for pop in pops:
    saved = {r['outer']: r for r in read(V2 / f's0/full/s0_{pop}.json')['rows']}
    keep = np.asarray(m['pops'][pop]['keep'], dtype=bool)
    mad = np.asarray(m['pops'][pop]['mad'])
    for si, sc in enumerate(scens):
        for t in range(200):
            key = f'{sc}/{t}'
            record = s0['outers'][key]['pops'][pop]['recorded']
            q = (bank.calib_features(np.array([record]))[0][keep] / mad[keep]).tolist()
            assert m['outers'][f'{pop}|{key}'] == dict(recorded=record, q=q, radius=saved[key]['kth'])
            checked_outers += 1
            for ni, n in enumerate((30, 300)):
                e = s0['E'][f'{4*ni+si}/{t}/{pop}']
                assert m['E'][f'{pop}|{key}|{n}'] == {k: e[k] for k in ('n', 'k', 'r')}
                checked_E += 1

primary = [s for s in b['settings'] if s['library'] == 'primary']
checks = [s for s in b['settings'] if s['library'] == 'check']
assert [s['index'] for s in primary] == list(range(21600))
assert len({s['dir'] for s in b['settings']}) == 21816
assert len({(s['pop'], s['outer'], s['n']) for s in primary}) == 21600
rates, priors = {}, {}
for r in pc['rows']:
    cell = (r['pop'], r['outer'].split('/')[0], r['n'])
    if r['proposals'] and r['cpu_seconds']:
        rates.setdefault(cell, []).append(r['proposals'] / r['cpu_seconds'])
    h, n = priors.get(cell, (0, 0))
    priors[cell] = (h + r['hits'], n + r['batches_done'])
for s in b['settings']:
    sc, t = s['outer'].split('/'); t = int(t)
    pi, si, ni = pops.index(s['pop']), scens.index(sc), (0, 30, 300).index(s['n'])
    expected_id = ((pi*4+si)*10+t)*3+ni if t < 10 else 1080+((pi*4+si)*190+t-10)*3+ni
    assert s['index'] == expected_id
    assert s['E'] == (dict(n=0, k=0, r=0) if s['n'] == 0 else m['E'][f"{s['pop']}|{s['outer']}|{s['n']}"])
    assert s['wave'] == ('W1' if s['n'] in (0, 30) else 'W2')
    cell = (s['pop'], sc, s['n'])
    r = pc['rows'][s['index']] if t < 10 else None
    rate = r['proposals']/r['cpu_seconds'] if r and r['proposals'] and r['cpu_seconds'] else statistics.median(rates[cell])
    assert s['rate'] == rate and s['cap_batches'] == int(2000*3600*rate//20000)
    assert s['prior_hpb'] == priors[cell][0]/priors[cell][1]
    if s['library'] == 'primary':
        assert s['stream_tag'] == 2
        if t < 10:
            old = ps['settings'][s['index']]
            assert all(s[k] == old[k] for k in ('index', 'pop', 'outer', 'n', 'E'))
            assert all(v == r[k] for k, v in s['pilot'].items())
        else:
            assert s['pilot'] is None
    else:
        assert s['stream_tag'] == 3 and s['pilot'] is None
        assert t in b['check_outers'][sc]

stage_members = {}
with tarfile.open(P3 / 's1b_stage.tar') as tf:
    for member in tf:
        if member.isfile():
            name = member.name.removeprefix('./')
            raw = tf.extractfile(member).read()
            assert sha(raw) == sha((P3 / 'stage' / name).read_bytes())
            stage_members[name] = sha(raw)
for line in (P3 / 'stage/s1b/stage_sha256.txt').read_text().splitlines():
    digest, name = line.split(maxsplit=1)
    assert stage_members[name.removeprefix('./')] == digest

deep, cluster = P3 / 'smoke_deep', P3 / 'smoke_kunanyi'
dc, kc = read(deep / 'collect_W1.json'), read(cluster / 'collect_W1.json')
assert dc['status'] == kc['status'] == dict(COMPLETE=4, CAPPED=2, FAILED=0, incomplete=0)
assert dc['collection_ok'] and kc['collection_ok']
assert kc['binding']['settings_sha256'] == sha((P3 / 'p3_settings_smoke.json').read_bytes())
archive_members = {}
with tarfile.open(cluster / 'W1.tar.gz') as tf:
    for member in tf:
        assert member.isfile()
        raw = tf.extractfile(member).read()
        assert sha(raw) == sha((cluster / member.name).read_bytes())
        archive_members[member.name] = sha(raw)
comparisons = []
for dr, kr in zip(dc['rows'], kc['rows']):
    assert all(dr[k] == kr[k] for k in ('dir', 'index', 'pop', 'outer', 'n', 'library', 'status', 'prefix_end_batch', 'prefix_hits', 'ranges'))
    if dr['status'] != 'COMPLETE':
        continue
    d = dr['dir']
    db, kb = (deep / 'lib' / f'{d}.jsonl').read_bytes(), (cluster / 'lib' / f'{d}.jsonl').read_bytes()
    assert sha(db) == dr['library_sha256'] and sha(kb) == kr['library_sha256']
    dl, kl = [json.loads(x) for x in db.splitlines()], [json.loads(x) for x in kb.splitlines()]
    assert len(dl) == len(kl) == 2000
    differences = []
    for i, (a, z) in enumerate(zip(dl, kl)):
        assert {k:v for k,v in a.items() if k != 'theta'} == {k:v for k,v in z.items() if k != 'theta'}
        if a != z:
            fields = {k: dict(deep=a['theta'][k], cluster=z['theta'][k], ulps=abs(a['theta'][k]-z['theta'][k])/math.ulp(a['theta'][k])) for k in a['theta'] if a['theta'][k] != z['theta'][k]}
            differences.append(dict(record_index=i, batch=a['batch'], proposal=a['proposal_in_batch'], fields=fields))
    comparisons.append(dict(dir=d, records=2000, byte_identical=db==kb, differences=differences))

# Recreate the earlier bound settings by the documented two hash changes.
# The saved smoke's SHA-256 verifies this reconstruction exactly.
oldfull = dict(b, runner_sha256=dc['binding']['runner_sha256'])
oldsm = dict(sm, runner_sha256=dc['binding']['runner_sha256'], derived_from_sha256=sha(json.dumps(oldfull).encode()))
oldbytes = json.dumps(oldsm).encode()
assert sha(oldbytes) == dc['binding']['settings_sha256']
oldpath = OUT / 'smoke_deep_original_settings.json'
oldpath.write_bytes(oldbytes)
copy = OUT / 'smoke_deep_copy'
if copy.exists():
    raise SystemExit('audit copy already exists; do not overwrite')
shutil.copytree(deep, copy)
env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', FLEXIBLAS_NUM_THREADS='1', TMPDIR=str(OUT))
cmd = ['/usr/bin/python3', '-I', str(V2 / 'p3_stage1b.py'), 'collect', str(oldpath), str(metric_path), str(copy), 'W1', str(copy / 'collect_W1.json')]
proc = subprocess.run(cmd, cwd=SRC, env=env, capture_output=True, text=True, timeout=60)
assert proc.returncode == 0, proc.stderr
assert read(copy / 'collect_W1.json') == dc
test = subprocess.run(['/usr/bin/python3', '-I', str(V2 / 'p3_stage1b.py'), 'test'], cwd=SRC, env=env, capture_output=True, text=True, timeout=60)
(OUT / 'p3_fixtures.log').write_text(test.stdout + test.stderr)
assert test.returncode == 0 and '"all_ok": true' in test.stdout

result = dict(scope=__doc__, timestamp=datetime.now(ZoneInfo('Australia/Hobart')).isoformat(), host=platform.node(),
              hashes={p.name: sha(p.read_bytes()) for p in (settings_path, metric_path, P3/'s1b_stage.tar', cluster/'W1.tar.gz')},
              bound_sources={k:b[k] for k in ('runner_sha256','p2_sha256','p1_sampler_sha256','imported_source_sha256')},
              primary_settings=len(primary), check_settings=len(checks), waves=dict(Counter(s['wave'] for s in b['settings'])),
              old_metric_pairs_identical=len(pm['outers']), old_E_identical=len(pm['E']), saved_s0_outers_checked=checked_outers,
              saved_s0_E_checked=checked_E, new_metric_pairs=checked_outers-len(pm['outers']),
              stage_member_hashes=stage_members, smoke_archive_member_hashes=archive_members,
              deep_status=dc['status'], cluster_status=kc['status'], library_comparisons=comparisons,
              smoke_cap_cpu_h=sm['cap_cpu_h'], capped_cluster_rows=[r for r in kc['rows'] if r['status']=='CAPPED'],
              recollect_deep_identical=True, collector_stdout=proc.stdout, p3_synthetic_fixtures_passed=True,
              limitations=['Kunanyi archive contains only summary/log and four libraries, not shard journals or scheduler receipts.',
                           'No current Kunanyi connection; CPU dispatch explanation unverified; smoke comparisons do not prove all rejected decisions agree.',
                           'Existing bank-content hashes reused; no bank scan, export, new paths, fits or PBS commands.'],
              elapsed_seconds=time.monotonic()-START)
(OUT / 'raw_checks.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
