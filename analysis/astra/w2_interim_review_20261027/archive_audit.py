"""Check the saved W2-a archive without running its sampler or touching live output."""
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
    'archive': BASE / 'w2_a/W2.tar.gz',
    'summary': BASE / 'w2_a/collect_W2.json',
    'settings': BASE / 'w1_r2/p3_settings_r2.json',
    'metric': BASE / 'p3_metric.json',
}
hashes = {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in paths.items()}
assert hashes['archive'] == '55448298029d8bb2d1783f489ed5809dcc88345c84c6e8294c0e23744e9eec96'
assert hashes['archive'] == (BASE / 'w2_a/W2.tar.gz.sha256').read_text().split()[0]
assert hashes['settings'] == '248f9c7de660dcac19a3e6806fbf97bc512aca9cff42abd54e5fd0f4ee3bbd73'
assert hashes['metric'] == '2dc57d9f1b27da08b193d2fbd9b94ff24f721f45052483a22d6d35b779a85ff0'
b, c, metric = [json.loads(paths[k].read_bytes()) for k in ('settings', 'summary', 'metric')]
settings = {s['dir']: s for s in b['settings'] if s['wave'] == 'W2'}
rows = {r['dir']: r for r in c['rows']}
assert len(settings) == len(rows) == len(c['rows']) == 7272 and set(settings) == set(rows)
assert c['binding'] == dict(settings_sha256=hashes['settings'], metric_sha256=hashes['metric'],
                           runner_sha256='1e35b94ab3811cc0ddded21aeaa5258120500c9e60f02dd5a6ee0c9c89d50d75')
assert c['wave'] == c['tag'] == 'W2'
counts = collections.Counter(r['status'] for r in rows.values())
assert counts == {'COMPLETE': 183, 'incomplete': 7076, 'invalid': 13}
assert c['status'] == {k: counts.get(k, 0) for k in ('COMPLETE', 'CAPPED', 'FAILED', 'incomplete')}
assert c['collection_ok'] is False and c['n_errors'] == len(c['errors']) == 13
assert sorted(e.split(':', 1)[0] for e in c['errors']) == sorted(d for d, r in rows.items() if r['status'] == 'invalid')
assert sorted(c['incomplete']) == sorted(d for d, r in rows.items() if r['status'] == 'incomplete')
for d, row in rows.items():
    assert all(row[k] == settings[d][k] for k in ('index', 'pop', 'outer', 'n', 'library'))
    assert bool(row.get('library_sha256')) == (row['status'] == 'COMPLETE')
libs = {f'lib/{d}.jsonl': r for d, r in rows.items() if r['status'] == 'COMPLETE'}
seen = set()
records = uncompressed_bytes = 0
with tarfile.open(paths['archive'], mode='r|gz') as tf:
    for member in tf:
        name = member.name.removeprefix('./')
        assert member.isfile() and name not in seen, name
        seen.add(name)
        raw = tf.extractfile(member).read()
        assert len(raw) == member.size
        uncompressed_bytes += len(raw)
        if name not in libs:
            assert name in ('collect_W2.json', 'collect_W2.log'), name
            if name == 'collect_W2.json':
                assert raw == paths['summary'].read_bytes()
            continue
        row, previous = libs[name], (-1, -1)
        st = settings[row['dir']]
        length = len(metric['outers'][f"{st['pop']}|{st['outer']}"]['recorded'])
        assert hashlib.sha256(raw).hexdigest() == row['library_sha256']
        assert raw.endswith(b'\n') and raw.count(b'\n') == 2000
        for line in raw.splitlines():
            r = json.loads(line)
            assert set(r) == {'batch', 'proposal_in_batch', 'boundary', 'theta', 'recorded'}
            assert type(r['boundary']) is bool
            assert type(r['batch']) is int and type(r['proposal_in_batch']) is int
            key = r['batch'], r['proposal_in_batch']
            assert previous < key and 0 <= key[0] < st['cap_batches'] and 0 <= key[1] < 20000
            assert set(r['theta']) == {'s', 'f', 'sigma', 'rho', 'p_c', 'delta'}
            assert all(type(v) is float and math.isfinite(v) for v in r['theta'].values())
            path = r['recorded']
            assert isinstance(path, list) and len(path) == length and all(type(x) is int for x in path)
            assert all(x > 1 for x in path[1:-1]) and path[-1] <= 1
            previous = key
            records += 1
        assert previous[0] == row['kth_hit']
assert seen == set(libs) | {'collect_W2.json', 'collect_W2.log'} and records == 366000
result = {
    'timestamp': datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),
    'scope': __doc__, 'hashes': hashes, 'archive_bytes': paths['archive'].stat().st_size,
    'members': len(seen), 'libraries': len(libs), 'records': records,
    'uncompressed_bytes': uncompressed_bytes, 'counts': dict(counts),
    'all_assertions_passed': True, 'elapsed_seconds': time.monotonic() - START,
    'limits': 'No raw-journal replay or numerical regeneration. This verifies the immutable archived libraries, not live shards or completeness of first-K discovery.',
}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'archive_audit.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
