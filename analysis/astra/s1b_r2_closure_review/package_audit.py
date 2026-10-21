"""Read saved Stage 1b round-2 evidence; run synthetic preflight and copied recollection.

Run with system Python on deep-server. Writes only OUT. No population simulation,
production reservation, seed, or PBS submission is performed.
"""
from collections import Counter
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import time
from zoneinfo import ZoneInfo

BASE = Path('/data/fable/vortex')
P3 = BASE/'v2_dev/p3'
SMOKE_BASE = BASE/'r2dev5'
OUT = Path('/data/codex/artifacts/project/s1b_r2_closure_20261021')
OUT.mkdir(parents=True, exist_ok=True)
START = time.monotonic()


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 22), b''):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    return json.loads(path.read_text())


tar = P3/'s1b_stage_r4.tar'
assert sha(tar) == '3eafd94d5b48f7b49409674f2d1cb1006bb4971c1b14a1ae526e6ec1f1eaaa8f'
members = {}
with tarfile.open(tar) as a:
    for m in a:
        if m.isfile():
            n = m.name.removeprefix('./')
            assert n not in members and '..' not in Path(n).parts and not n.startswith('/')
            h = hashlib.sha256(a.extractfile(m).read()).hexdigest()
            assert h == sha(P3/'stage_r4'/n)
            members[n] = h
manifest = (P3/'stage_r4/s1b/stage_sha256.txt').read_text().splitlines()
assert len(manifest) == 8
smoke_source_comparison = {}
for line in manifest:
    h, name = line.split(maxsplit=1)
    name = name.removeprefix('./')
    assert members[name] == h
    smoke_hash = sha(SMOKE_BASE/name)
    smoke_source_comparison[name] = {'stage': h, 'smoke_tree': smoke_hash, 'identical': h == smoke_hash}
    assert h == smoke_hash, name

settings = P3/'p3_settings.json'
metric = P3/'p3_metric.json'
b = read(settings)
c = read(P3/'w1_r1/collect_W1.json')
assert c['binding'] == {'settings_sha256': sha(settings), 'metric_sha256': sha(metric),
                        'runner_sha256': b['runner_sha256']}
assert c['n_errors'] == len(c['errors']) == 1
assert c['errors'] == ['s18085: ValueError: verified K-hit prefix without a COMPLETE marker']
full = {s['dir']: s for s in b['settings']}
assert len(full) == len(b['settings']) == 21816
w1 = {d for d, s in full.items() if s['wave'] == 'W1'}
assert len(c['rows']) == len({r['dir'] for r in c['rows']}) == len(w1) == 14544
assert {r['dir'] for r in c['rows']} == w1
for row in c['rows']:
    assert all(row[k] == full[row['dir']][k] for k in ('index', 'pop', 'outer', 'n', 'library'))
counts = dict(Counter(r['status'] for r in c['rows']))
assert counts == {'COMPLETE': 9695, 'incomplete': 4846, 'CAPPED': 2, 'invalid': 1}, counts
redo = [r['dir'] for r in c['rows'] if r['status'] in ('incomplete', 'invalid')]
w2 = [s['dir'] for s in b['settings'] if s['wave'] == 'W2']
dirs = OUT/'dirs_r2.txt'
dirs.write_text('\n'.join(redo + w2) + '\n')
selected = OUT/'p3_settings_r2.json'
src = P3/'stage_r4/src'
runner = src/'analysis/fable/calibration/v2_dev/p3_stage1b.py'
cwd = SMOKE_BASE/'src'
env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
           FLEXIBLAS_NUM_THREADS='1', TMPDIR=str(OUT), PYTHONDONTWRITEBYTECODE='1')


def run(args, log, timeout=120):
    p = subprocess.run(['/usr/bin/python3', '-B', '-I', str(runner), *map(str, args)],
                       cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
    (OUT/log).write_text(p.stdout + p.stderr)
    assert p.returncode == 0, (log, p.returncode, p.stderr)
    return p.stdout


run(['select', settings, selected, dirs], 'select.log')
s = read(selected)
assert len(s['settings']) == 12119 and {x['dir'] for x in s['settings']} == set(redo + w2)
assert all(x == full[x['dir']] for x in s['settings'])
assert {k: v for k, v in s.items() if k not in ('settings', 'stage', 'runner_sha256', 'derived_from_sha256')} == {
    k: v for k, v in b.items() if k not in ('settings', 'stage', 'runner_sha256', 'derived_from_sha256')}
assert s['derived_from_sha256'] == sha(settings) and s['runner_sha256'] == sha(runner)

ledger = OUT/'audit_reservations.tsv'
assert not ledger.exists(), 'Preserve an earlier audit ledger.'
preflight_text = run(['preflight', selected, metric, ledger, 'astra_r2_closure_W1', OUT/'not_dispatched',
                      300, 8, 172800, 'W1'], 'native_preflight.log', timeout=180)
assert '"all_ok": true' in preflight_text
preflight = json.loads(preflight_text.splitlines()[-1])
assert preflight['reservation_cpu_h'] == preflight['wave_reserved'] == 115208

smoke = SMOKE_BASE/'s1b/smoke_r2'
smoke_settings = SMOKE_BASE/'s1b/p3_settings_smoke_r2.json'
smoke_b = read(smoke_settings)
assert smoke_b['runner_sha256'] == sha(runner)
assert smoke_b['metric_sha256'] == sha(metric)
copy = OUT/'smoke_copy'
assert not copy.exists(), 'Preserve an earlier audit copy.'
shutil.copytree(smoke, copy)
smoke_result = {}
for wave in ('W1', 'W2'):
    expected = read(smoke/f'collect_{wave}.json')
    assert expected['collection_ok'] and not expected['errors'] and not expected['incomplete']
    assert expected['queue_left'] == expected['claims_left'] == 0
    run(['collect', smoke_settings, metric, copy, wave, copy/f'collect_{wave}.json'], f'recollect_{wave}.log')
    assert read(copy/f'collect_{wave}.json') == expected
    smoke_result[wave] = expected['status']
libraries = []
for row in read(smoke/'collect_W1.json')['rows']:
    if row['status'] == 'COMPLETE':
        name = row['dir'] + '.jsonl'
        raw = (smoke/'lib'/name).read_bytes()
        assert len(raw.splitlines()) == 2000
        assert hashlib.sha256(raw).hexdigest() == row['library_sha256'] == sha(P3/'smoke_deep3/lib'/name)
        libraries.append({'dir': row['dir'], 'sha256': row['library_sha256'], 'records': 2000})
assert len(libraries) == 4
result = {'scope': __doc__, 'timestamp': datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),
          'stage_tar_sha256': sha(tar), 'stage_member_sha256': members,
          'smoke_source_comparison': smoke_source_comparison,
          'round1_summary_sha256': sha(P3/'w1_r1/collect_W1.json'), 'round1_binding': c['binding'],
          'round1_counts': counts, 'selected_sha256': sha(selected), 'selected_counts': {'W1': len(redo), 'W2': len(w2)},
          'selected_rows_identical': True, 'other_settings_fields_identical': True,
          'native_preflight': preflight, 'smoke_recollection_identical': smoke_result, 'smoke_libraries': libraries,
          'limitations': ['No fresh population paths or fresh serial recomputation.',
                          'No live Kunanyi filesystem qualification or production ledger/PBS action.'],
          'elapsed_seconds': time.monotonic() - START}
(OUT/'package_audit.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
