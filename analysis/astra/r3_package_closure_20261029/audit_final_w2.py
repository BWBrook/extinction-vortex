"""Verify the final W2 archive and account for its complete recovery inventory."""
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
START = time.monotonic()
paths = {
    'archive': BASE / 'w2_r2b/W2_b.tar.gz',
    'summary': BASE / 'w2_r2b/collect_W2_b.json',
    'previous_summary': BASE / 'w2_a/collect_W2.json',
    'settings': BASE / 'w1_r2/p3_settings_r2.json',
    'metric': BASE / 'p3_metric.json',
    'w1_summary': BASE / 'w1_r2b/collect_W1_b.json',
}


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


hashes = {k: sha(p) for k, p in paths.items()}
assert hashes['archive'] == 'c760f0c62222fae8a67ae1544d728d2d21e03d674752bb0349191c9a46f8624d'
assert hashes['summary'] == 'beabe2d1678fe45b5c74fbd42db6153adaa2cd72ddfc3b25abec1177377f703b'
assert hashes['previous_summary'] == '9bfe0ca4e2c833bdd2e6c5eeb1e26aecc50e1777e68f7a1aba07bee3e8704a08'
assert hashes['settings'] == '248f9c7de660dcac19a3e6806fbf97bc512aca9cff42abd54e5fd0f4ee3bbd73'
assert hashes['metric'] == '2dc57d9f1b27da08b193d2fbd9b94ff24f721f45052483a22d6d35b779a85ff0'
assert hashes['w1_summary'] == '8d7028079000e6788c40c306d1df15b2cf41d50881e8f7554c1f20fd70ad4335'
b, c, c0, metric, c1 = [json.loads(paths[k].read_bytes()) for k in
                        ('settings', 'summary', 'previous_summary', 'metric', 'w1_summary')]
settings = {s['dir']: s for s in b['settings'] if s['wave'] == 'W2'}
rows, previous = [{r['dir']: r for r in q['rows']} for q in (c, c0)]
assert len(settings) == len(rows) == len(c['rows']) == 7272
assert set(settings) == set(rows) == set(previous)
assert c['binding'] == c0['binding'] == dict(settings_sha256=hashes['settings'], metric_sha256=hashes['metric'],
                                           runner_sha256='1e35b94ab3811cc0ddded21aeaa5258120500c9e60f02dd5a6ee0c9c89d50d75')
assert c['wave'] == 'W2' and c['tag'] == 'W2_b'
counts = collections.Counter(r['status'] for r in rows.values())
assert counts == {'COMPLETE': 355, 'incomplete': 6901, 'invalid': 16}
assert c['status'] == {k: counts.get(k, 0) for k in ('COMPLETE', 'CAPPED', 'FAILED', 'incomplete')}
assert c['collection_ok'] is False and c['n_errors'] == len(c['errors']) == 16
assert sorted(e.split(':', 1)[0] for e in c['errors']) == sorted(d for d, r in rows.items() if r['status'] == 'invalid')
assert sorted(c['incomplete']) == sorted(d for d, r in rows.items() if r['status'] == 'incomplete')
for d, row in rows.items():
    assert all(row[k] == settings[d][k] for k in ('index', 'pop', 'outer', 'n', 'library'))
    assert bool(row.get('library_sha256')) == (row['status'] == 'COMPLETE')
    if previous[d]['status'] == 'COMPLETE':
        assert row['status'] == 'COMPLETE' and row['library_sha256'] == previous[d]['library_sha256']
new = {d for d, r in rows.items() if r['status'] == 'COMPLETE' and previous[d]['status'] != 'COMPLETE'}
assert len(new) == 172
redo = sorted(d for d, r in rows.items() if r['status'] in ('incomplete', 'invalid', 'FAILED'))
redo1 = sorted(r['dir'] for r in c1['rows'] if r['status'] in ('incomplete', 'invalid', 'FAILED'))
assert len(redo) == 6917 and len(redo1) == 18 and not set(redo) & set(redo1)
libs = {f'lib/{d}.jsonl': r for d, r in rows.items() if r['status'] == 'COMPLETE'}
seen, checked_records, uncompressed = set(), 0, 0
with tarfile.open(paths['archive'], mode='r|gz') as tf:
    for member in tf:
        name = member.name.removeprefix('./')
        assert member.isfile() and name not in seen, name
        seen.add(name)
        raw = tf.extractfile(member).read()
        assert len(raw) == member.size
        uncompressed += len(raw)
        if name not in libs:
            assert name in ('collect_W2_b.json', 'collect_W2_b.log'), name
            if name == 'collect_W2_b.json':
                assert raw == paths['summary'].read_bytes()
            continue
        row = libs[name]
        assert hashlib.sha256(raw).hexdigest() == row['library_sha256']
        assert raw.endswith(b'\n') and raw.count(b'\n') == 2000
        if row['dir'] not in new:
            continue
        st, prev = settings[row['dir']], (-1, -1)
        length = len(metric['outers'][f"{st['pop']}|{st['outer']}"]['recorded'])
        for line in raw.splitlines():
            r = json.loads(line)
            assert set(r) == {'batch', 'proposal_in_batch', 'boundary', 'theta', 'recorded'}
            assert type(r['boundary']) is bool and type(r['batch']) is int and type(r['proposal_in_batch']) is int
            key = r['batch'], r['proposal_in_batch']
            assert prev < key and 0 <= key[0] < st['cap_batches'] and 0 <= key[1] < 20000
            assert set(r['theta']) == {'s', 'f', 'sigma', 'rho', 'p_c', 'delta'}
            assert all(type(v) is float and math.isfinite(v) for v in r['theta'].values())
            path = r['recorded']
            assert isinstance(path, list) and len(path) == length and all(type(x) is int for x in path)
            assert all(x > 1 for x in path[1:-1]) and path[-1] <= 1
            prev = key
            checked_records += 1
        assert prev[0] == row['kth_hit']
assert seen == set(libs) | {'collect_W2_b.json', 'collect_W2_b.log'} and checked_records == 344000
by_status = {}
for row in rows.values():
    key = row['status'] + '|' + row['library']
    cell = by_status.setdefault(key, {'rows': 0, 'prefix_cpu_h': 0.0, 'outside_prefix_cpu_h': 0.0})
    cell['rows'] += 1
    cell['prefix_cpu_h'] += row.get('useful_cpu_h', 0)
    cell['outside_prefix_cpu_h'] += row.get('discarded_cpu_h', 0)
inside = sum(v['prefix_cpu_h'] for k, v in by_status.items() if k.startswith('incomplete|'))
outside = sum(v['outside_prefix_cpu_h'] for k, v in by_status.items() if k.startswith('incomplete|'))
primary = [r for r in rows.values() if r['library'] == 'primary']
checks = [r for r in rows.values() if r['library'] == 'check']
groups = collections.defaultdict(list)
for r in primary:
    groups[r['outer']].append(r)
assert len(primary) == 7200 and len(checks) == 72 and len(groups) == 800
assert all(len(rs) == 9 for rs in groups.values())
available = [sum(r['status'] == 'COMPLETE' for r in rs) for rs in groups.values()]
out = {
    'timestamp': datetime.now(ZoneInfo('Australia/Hobart')).isoformat(), 'scope': __doc__, 'hashes': hashes,
    'archive_bytes': paths['archive'].stat().st_size, 'members': len(seen), 'libraries': len(libs),
    'records_hashed_and_counted': 355 * 2000, 'new_library_count': len(new),
    'new_records_structurally_checked': checked_records,
    'previously_audited_libraries_byte_identical': 183, 'uncompressed_bytes': uncompressed,
    'counts': dict(counts), 'round3_counts': {'W1': len(redo1), 'W2': len(redo), 'total': len(redo1) + len(redo)},
    'recovery_dirs_sha256': hashlib.sha256(('\n'.join(sorted(redo1 + redo)) + '\n').encode()).hexdigest(),
    'by_status_library': by_status,
    'historical_incomplete_cpu_h': {'prefix': inside, 'outside_prefix': outside, 'sum': inside + outside,
                                   'days_at_7000_cpus': (inside + outside) / (7000 * 24)},
    'w2_primary_outer_datasets': {'denominator': 800, 'all_nine_complete': available.count(9),
                                'maximum_populations_complete': max(available)},
    'all_assertions_passed': True, 'elapsed_seconds': time.monotonic() - START,
    'limits': '183 previously audited libraries hash matched, not reparsed. No raw production journal or numerical replay. Historical CPU excludes invalid and losing duplicate work and includes reused pilot CPU; not a forecast.',
}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'final_w2_archive_audit.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))
