"""Verify the complete saved W1 archive on deep-server without extracting or changing it.

Each archived library must match its collector digest and contain 2,000 newline-
terminated records. This verifies archive/collector consistency, not the sampler law.
"""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import tarfile
import time
from zoneinfo import ZoneInfo

START = time.monotonic()
BASE = Path('/data/fable/vortex/v2_dev/p3/w1_r1')
OUT = Path('/data/codex/artifacts/project/s1b_r2_review_20261021')
OUT.mkdir(parents=True, exist_ok=True)
archive = BASE/'W1.tar.gz'
want_sha = (BASE/'W1.tar.gz.sha256').read_text().split()[0]
h = hashlib.sha256()
with archive.open('rb') as f:
    for block in iter(lambda: f.read(1 << 22), b''):
        h.update(block)
assert h.hexdigest() == want_sha
craw = (BASE/'collect_W1.json').read_bytes()
c = json.loads(craw)
libs = {f"lib/{r['dir']}.jsonl": r['library_sha256'] for r in c['rows'] if r['status'] == 'COMPLETE'}
assert len(libs) == 9695
seen = set()
total_bytes = records = 0
with tarfile.open(archive, mode='r|gz') as a:
    for m in a:
        assert m.isfile(), m.name
        name = m.name.removeprefix('./')
        assert name not in seen, name
        seen.add(name)
        data = a.extractfile(m).read()
        assert len(data) == m.size
        total_bytes += len(data)
        if name in libs:
            assert hashlib.sha256(data).hexdigest() == libs[name], name
            assert data.endswith(b'\n') and data.count(b'\n') == 2000, name
            records += 2000
        elif name == 'collect_W1.json':
            assert data == craw
        else:
            assert name == 'collect_W1.log', name
assert seen == set(libs) | {'collect_W1.json', 'collect_W1.log'}
result = {'scope': __doc__, 'timestamp': datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),
          'archive_sha256': h.hexdigest(), 'compressed_bytes': archive.stat().st_size,
          'members': len(seen), 'libraries': len(libs), 'records': records, 'uncompressed_bytes': total_bytes,
          'all_library_hashes_match': True, 'all_library_record_counts_2000': True, 'summary_identical': True,
          'elapsed_seconds': time.monotonic() - START}
(OUT/'archive_audit.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
