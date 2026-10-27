"""Verify W1's final round-two archive; inspect new records and hash unchanged libraries."""
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
    'archive': BASE / 'w1_r2b/W1_b.tar.gz',
    'summary': BASE / 'w1_r2b/collect_W1_b.json',
    'previous_summary': BASE / 'w1_r2/collect_W1.json',
    'round1_summary': BASE / 'w1_r1/collect_W1.json',
    'settings': BASE / 'w1_r2/p3_settings_r2.json',
    'metric': BASE / 'p3_metric.json',
}

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

hashes = {k: sha(p) for k, p in paths.items()}
assert hashes['archive'] == '849cd0ba2d65b30d987c594416a773d78902b8e0e1aa5ce00fb78ed4c1e2ab21'
assert hashes['summary'] == '8d7028079000e6788c40c306d1df15b2cf41d50881e8f7554c1f20fd70ad4335'
assert hashes['previous_summary'] == '3cd158028c58477c1652aa727dcbec19450a2a507f016926b83b48774fd92fb5'
assert hashes['settings'] == '248f9c7de660dcac19a3e6806fbf97bc512aca9cff42abd54e5fd0f4ee3bbd73'
assert hashes['metric'] == '2dc57d9f1b27da08b193d2fbd9b94ff24f721f45052483a22d6d35b779a85ff0'
b, c, c0, c1, metric = [json.loads(paths[k].read_bytes()) for k in
                       ('settings', 'summary', 'previous_summary', 'round1_summary', 'metric')]
settings = {s['dir']: s for s in b['settings'] if s['wave'] == 'W1'}
rows, previous, first = [{r['dir']: r for r in q['rows']} for q in (c, c0, c1)]
assert len(settings) == len(rows) == len(c['rows']) == 4847 and set(settings) == set(rows) == set(previous)
assert c['binding'] == c0['binding'] == dict(settings_sha256=hashes['settings'], metric_sha256=hashes['metric'],
                                           runner_sha256='1e35b94ab3811cc0ddded21aeaa5258120500c9e60f02dd5a6ee0c9c89d50d75')
assert c['wave'] == 'W1' and c['tag'] == 'W1_b'
counts = collections.Counter(r['status'] for r in rows.values())
assert counts == {'COMPLETE': 4820, 'CAPPED': 9, 'incomplete': 15, 'invalid': 3}
assert c['status'] == {k: counts.get(k, 0) for k in ('COMPLETE', 'CAPPED', 'FAILED', 'incomplete')}
assert c['collection_ok'] is False and c['n_errors'] == len(c['errors']) == 3
assert sorted(e.split(':', 1)[0] for e in c['errors']) == sorted(d for d, r in rows.items() if r['status'] == 'invalid')
assert sorted(c['incomplete']) == sorted(d for d, r in rows.items() if r['status'] == 'incomplete')
for d, row in rows.items():
    assert all(row[k] == settings[d][k] for k in ('index', 'pop', 'outer', 'n', 'library'))
    assert bool(row.get('library_sha256')) == (row['status'] == 'COMPLETE')
    if previous[d]['status'] == 'COMPLETE':
        assert row['status'] == 'COMPLETE' and row['library_sha256'] == previous[d]['library_sha256']
new = {d for d, r in rows.items() if r['status'] == 'COMPLETE' and previous[d]['status'] != 'COMPLETE'}
assert len(new) == 22
redo = sorted(d for d, r in rows.items() if r['status'] in ('incomplete', 'invalid', 'FAILED'))
assert len(redo) == 18 and all(settings[d]['n'] == 30 and settings[d]['library'] == 'primary' for d in redo)
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
            assert name in ('collect_W1_b.json', 'collect_W1_b.log'), name
            if name == 'collect_W1_b.json':
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
assert seen == set(libs) | {'collect_W1_b.json', 'collect_W1_b.log'} and checked_records == 44000
retained_first = {d: r for d, r in first.items() if r['status'] in ('COMPLETE', 'CAPPED')}
assert not set(retained_first) & set(rows)
combined = dict(retained_first, **rows)
assert set(combined) == set(first) and len(combined) == 14544
result = {
    'timestamp': datetime.now(ZoneInfo('Australia/Hobart')).isoformat(), 'scope': __doc__, 'hashes': hashes,
    'archive_bytes': paths['archive'].stat().st_size, 'members': len(seen), 'libraries': len(libs),
    'records_hashed_and_counted': 4820 * 2000, 'new_libraries': sorted(new), 'new_records_structurally_checked': checked_records,
    'previously_audited_libraries_byte_identical': 4798, 'uncompressed_bytes': uncompressed, 'counts': dict(counts),
    'combined_w1_counts': dict(collections.Counter(r['status'] for r in combined.values())), 'round3_w1_dirs': redo,
    'round3_w1_jobs_by_current_rule': (28 * len(redo) + 7) // 8,
    'all_assertions_passed': True, 'elapsed_seconds': time.monotonic() - START,
    'limits': 'Previously audited 4798 libraries verified by identical hashes, not reparsed. No raw-journal or numerical regeneration.',
}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'archive_delta_audit.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
