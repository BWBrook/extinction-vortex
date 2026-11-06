"""Audit the W1 collection package and the bounded claims in its receipt."""
import collections
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[3]
P = ROOT / 'analysis/fable/calibration/v2_dev/p3'
archive, settings = map(Path, sys.argv[1:3])
sha = lambda b: hashlib.sha256(b).hexdigest()
archive_hash = sha(archive.read_bytes())
assert archive_hash == '5e0de4764cc1eedc55ca8ed930bd7548bae93d9b49106878b8e5e78175cbcf13'
summary_bytes = (P / 'w1_r3_collect_W1.json').read_bytes()
summary_hash = sha(summary_bytes)
assert summary_hash == '020a9bbf71df52a52fed96c31de94e25eec1428d0ad33ebbc572dc3323ff4c64'
with tarfile.open(archive) as tf:
    members = tf.getmembers()
    assert len(members) == 2 and all(m.isfile() for m in members)
    assert {m.name for m in members} == {'collect_W1.json', 'collect_W1.log'}
    assert tf.extractfile('collect_W1.json').read() == summary_bytes
settings_bytes = settings.read_bytes()
assert sha(settings_bytes) == 'fa7728290d33fb3f0baf30603d731c769de925739815d9a3b4efb77ddb97b9cd'
b, c = json.loads(settings_bytes), json.loads(summary_bytes)
assert c['binding'] == {k: v for k, v in {
    'settings_sha256': sha(settings_bytes), 'runner_sha256': b['runner_sha256'],
    'metric_sha256': b['metric_sha256']}.items()}
assert sha((ROOT / 'analysis/fable/calibration/v2_dev/p3_stage1b.py').read_bytes()) == b['runner_sha256']
expected = {s['dir']: s for s in b['settings'] if s['wave'] == 'W1'}
rows = {r['dir']: r for r in c['rows']}
assert len(c['rows']) == len(rows) == len(expected) == 18
assert rows.keys() == expected.keys()
for d, r in rows.items():
    assert all(r[k] == expected[d][k] for k in ('index', 'pop', 'outer', 'n', 'library'))
    assert r['prefix_end_batch'] <= expected[d]['cap_batches']
counts = collections.Counter(r['status'] for r in rows.values())
assert counts == {'CAPPED': 1, 'incomplete': 17}
assert c['status'] == dict(COMPLETE=0, CAPPED=1, FAILED=0, incomplete=17)
assert c['collection_ok'] and c['n_errors'] == 0 and not c['errors']
assert sorted(c['incomplete']) == sorted(d for d, r in rows.items() if r['status'] == 'incomplete')
for k in ('useful_cpu_h', 'discarded_cpu_h', 'executions', 'dead_executions', 'open_executions'):
    assert math.isclose(sum(r[k] for r in rows.values()), c[k])
capped = rows['s14782']
assert capped['status'] == 'CAPPED' and capped['prefix_end_batch'] == expected['s14782']['cap_batches']
assert capped['prefix_hits'] < b['K']
pilot_cpu = sum(s['pilot']['cpu_seconds'] / 3600 for s in expected.values() if s['pilot'])
receipt = (P / 'w1_r3_collection_20261106.txt').read_text()
first_excerpt = receipt.split('## W1 topup b')[0]
walltimes = re.findall(r'^\s*(\d+) Nov 4 \d+:\d+:\d+ (\d+:\d+:\d+)$', first_excerpt, re.M)
assert len(walltimes) == 40
long_in_excerpt = sum(int(n) for n, w in walltimes if w.startswith('47:'))
assert long_in_excerpt == 9
out = {
    'archive_sha256': archive_hash, 'summary_sha256': summary_hash,
    'settings_sha256': sha(settings_bytes), 'archive_regular_members': [m.name for m in members],
    'archived_summary_byte_identical': True, 'exact_18_setting_inventory_and_bindings': True,
    'row_status_counts': dict(counts), 'capped_setting': capped,
    'row_totals': {k: c[k] for k in ('useful_cpu_h', 'discarded_cpu_h', 'executions', 'dead_executions', 'open_executions')},
    'historical_imported_pilot_cpu_h': pilot_cpu,
    'recorded_shard_cpu_h_excluding_pilot': c['useful_cpu_h'] + c['discarded_cpu_h'] - pilot_cpu,
    'walltime_excerpt_subjobs': sum(int(n) for n, w in walltimes),
    'walltime_excerpt_long_subjobs_lower_bound': long_in_excerpt,
    'retirement_slot_notes': {'idle': 384, 'cutoff': 120},
    'limits': 'Archive contains summary and log only, no raw execution records or libraries. No independent raw-state recollection, scheduler accounting, full subjob histogram, or run2/run3 determinism replay. CPU totals are recorded state accounting, not complete PBS usage. Queue and claim totals cover the shared run directory, not W1 alone.',
    'all_assertions_passed': True,
}
Path(__file__).with_name('collection_audit.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))
