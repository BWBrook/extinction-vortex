"""Independent streaming check of the saved W1 round-2 archive and input partition.

Read-only inputs on deep-server. This checks archived output consistency and
record contracts; it does not replay raw shard journals or numerical sampling.
The earlier round's library audit is retained, with its archive digest rechecked.
"""
import collections
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import sys
import tarfile
import time
from zoneinfo import ZoneInfo

BASE = Path('/data/fable/vortex/v2_dev/p3')
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
START = time.monotonic()
EXPECTED = {
    'archive_r1': 'bb604f1cc10317b8ea279af471208985c1b3bf464d729b4d284d0418a6538779',
    'archive_r2': 'c12e5378589c010f6e4b01d1bbb3cbd19d4d61ca4675aced79269e1e4f0624cc',
    'summary_r2': '3cd158028c58477c1652aa727dcbec19450a2a507f016926b83b48774fd92fb5',
    'settings_r1': '86545d6b83dec07e31b84fa97a5fd43b5dc4130170c48e01f92b9f7f0320520a',
    'settings_r2': '248f9c7de660dcac19a3e6806fbf97bc512aca9cff42abd54e5fd0f4ee3bbd73',
    'metric': '2dc57d9f1b27da08b193d2fbd9b94ff24f721f45052483a22d6d35b779a85ff0',
    'runner_r2': '1e35b94ab3811cc0ddded21aeaa5258120500c9e60f02dd5a6ee0c9c89d50d75',
}


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


paths = {
    'settings_r1': BASE / 'p3_settings.json',
    'settings_r2': BASE / 'w1_r2/p3_settings_r2.json',
    'metric': BASE / 'p3_metric.json',
    'summary_r1': BASE / 'w1_r1/collect_W1.json',
    'summary_r2': BASE / 'w1_r2/collect_W1.json',
    'archive_r1': BASE / 'w1_r1/W1.tar.gz',
    'archive_r2': BASE / 'w1_r2/W1.tar.gz',
}
hashes = {key: sha(path) for key, path in paths.items()}
for key, expected in EXPECTED.items():
    if key != 'runner_r2':
        assert hashes[key] == expected, (key, hashes[key])
for rnd in (1, 2):
    declared = (BASE / f'w1_r{rnd}/W1.tar.gz.sha256').read_text().split()[0]
    assert hashes[f'archive_r{rnd}'] == declared
print(json.dumps({'phase': 'input_hashes', 'hashes': hashes}), flush=True)
b1, b2 = [json.loads(paths[f'settings_r{r}'].read_bytes()) for r in (1, 2)]
c1, c2 = [json.loads(paths[f'summary_r{r}'].read_bytes()) for r in (1, 2)]
metric = json.loads(paths['metric'].read_bytes())
settings1 = {s['dir']: s for s in b1['settings']}
settings2 = {s['dir']: s for s in b2['settings']}
assert len(settings1) == len(b1['settings']) == 21816
assert len(settings2) == len(b2['settings']) == 12119
for d, st in settings2.items():
    assert st == settings1[d], d
redo = {r['dir'] for r in c1['rows'] if r['status'] in ('incomplete', 'invalid')}
assert set(settings2) == redo | {d for d, s in settings1.items() if s['wave'] == 'W2'}
derived = dict(b1, settings=[s for s in b1['settings'] if s['dir'] in settings2],
               runner_sha256=EXPECTED['runner_r2'], derived_from_sha256=hashes['settings_r1'],
               stage=b1['stage'] + f' -- selected round ({len(settings2)} settings)')
assert b2 == derived
assert hashlib.sha256(json.dumps(derived).encode()).hexdigest() == hashes['settings_r2']

rounds = {}
for rnd, b, c in ((1, b1, c1), (2, b2, c2)):
    wanted = {s['dir']: s for s in b['settings'] if s['wave'] == 'W1'}
    rows = {r['dir']: r for r in c['rows']}
    assert len(rows) == len(c['rows']) and set(rows) == set(wanted)
    assert c['wave'] == 'W1'
    assert c['binding'] == dict(settings_sha256=hashes[f'settings_r{rnd}'],
                                metric_sha256=hashes['metric'], runner_sha256=b['runner_sha256'])
    counts = collections.Counter(r['status'] for r in rows.values())
    assert set(counts) <= {'COMPLETE', 'CAPPED', 'FAILED', 'incomplete', 'invalid'}
    assert c['status'] == {k: counts.get(k, 0) for k in ('COMPLETE', 'CAPPED', 'FAILED', 'incomplete')}
    invalid = sorted(r['dir'] for r in rows.values() if r['status'] == 'invalid')
    assert sorted(e.split(':', 1)[0] for e in c['errors']) == invalid
    assert c['n_errors'] == len(c['errors']) and c['collection_ok'] == (not c['errors'])
    assert sorted(c['incomplete']) == sorted(r['dir'] for r in rows.values() if r['status'] == 'incomplete')
    for d, row in rows.items():
        st = wanted[d]
        assert all(row[k] == st[k] for k in ('index', 'pop', 'outer', 'n', 'library')), d
        assert bool(row.get('library_sha256')) == (row['status'] == 'COMPLETE'), d
        if row['status'] == 'CAPPED':
            assert row['prefix_end_batch'] >= st['cap_batches'] and row['prefix_hits'] < 2000, d
    rounds[rnd] = {'counts': dict(counts), 'rows': rows}
r1, r2 = rounds[1]['rows'], rounds[2]['rows']
t1 = {d for d, r in r1.items() if r['status'] in ('COMPLETE', 'CAPPED', 'FAILED')}
t2 = {d for d, r in r2.items() if r['status'] in ('COMPLETE', 'CAPPED', 'FAILED')}
left = {d for d, r in r2.items() if r['status'] in ('incomplete', 'invalid')}
assert set(r2) == redo and not (t1 & t2 or t1 & left or t2 & left)
assert t1 | t2 | left == set(r1)
assert len(left) == 48 and all(settings2[d]['n'] == 30 for d in left)

libs = {f'lib/{d}.jsonl': r for d, r in r2.items() if r['status'] == 'COMPLETE'}
assert len(libs) == 4798
seen = set()
total_records = uncompressed_bytes = checked = 0
fields = {'batch', 'proposal_in_batch', 'boundary', 'theta', 'recorded'}
params = {'s', 'f', 'sigma', 'rho', 'p_c', 'delta'}
with tarfile.open(paths['archive_r2'], mode='r|gz') as tf:
    for member in tf:
        name = member.name.removeprefix('./')
        assert member.isfile() and name not in seen, name
        seen.add(name)
        raw = tf.extractfile(member).read()
        assert len(raw) == member.size
        uncompressed_bytes += len(raw)
        if name not in libs:
            assert name in ('collect_W1.json', 'collect_W1.log'), name
            if name == 'collect_W1.json':
                assert raw == paths['summary_r2'].read_bytes()
            continue
        row = libs[name]
        assert hashlib.sha256(raw).hexdigest() == row['library_sha256'], name
        assert raw.endswith(b'\n') and raw.count(b'\n') == 2000, name
        st = settings2[row['dir']]
        length = len(metric['outers'][f"{st['pop']}|{st['outer']}"]['recorded'])
        previous = (-1, -1)
        for line in raw.splitlines():
            rec = json.loads(line)
            assert set(rec) == fields and type(rec['boundary']) is bool, name
            assert type(rec['batch']) is int and type(rec['proposal_in_batch']) is int, name
            key = (rec['batch'], rec['proposal_in_batch'])
            assert previous < key and 0 <= key[0] < st['cap_batches'] and 0 <= key[1] < 20000, name
            assert isinstance(rec['theta'], dict) and set(rec['theta']) == params, name
            assert all(type(v) is float and math.isfinite(v) for v in rec['theta'].values()), name
            path = rec['recorded']
            assert isinstance(path, list) and len(path) == length and all(type(x) is int for x in path), name
            assert all(x > 1 for x in path[1:-1]) and path[-1] <= 1, name
            previous = key
            total_records += 1
        assert previous[0] == row['kth_hit'], name
        checked += 1
        if checked == 1 or checked % 1000 == 0:
            print(json.dumps({'phase': 'library_records', 'libraries': checked,
                              'records': total_records, 'elapsed_s': time.monotonic() - START}), flush=True)
assert seen == set(libs) | {'collect_W1.json', 'collect_W1.log'}
assert total_records == 9596000
result = {
    'scope': __doc__, 'timestamp': datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),
    'hashes': hashes, 'archive_bytes': paths['archive_r2'].stat().st_size,
    'members': len(seen), 'libraries': checked, 'records': total_records,
    'uncompressed_bytes': uncompressed_bytes, 'all_assertions_passed': True,
    'settings_exact_reproduction': True, 'all_scientific_setting_fields_unchanged': True,
    'round1_counts': rounds[1]['counts'], 'round2_counts': rounds[2]['counts'],
    'w1_partition': {'round1_terminal': len(t1), 'round2_terminal': len(t2),
                     'incomplete': len(left), 'inventory': len(r1)},
    'remaining_dirs': sorted(left),
    'pilot_cpu_h_imported_into_round2': sum((s.get('pilot') or {}).get('cpu_seconds', 0)
                                          for s in settings2.values() if s['wave'] == 'W1') / 3600,
    'elapsed_seconds': time.monotonic() - START,
}
(OUT / 'archive_audit.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2), flush=True)
