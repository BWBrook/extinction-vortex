"""Independently recollect a private copy of the saved final adversarial smoke."""
import contextlib
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
from zoneinfo import ZoneInfo

BASE = Path('/data/fable/vortex/r3dev4')
SOURCE = BASE / 'src/analysis/fable/calibration/v2_dev'
ORIGINAL = BASE / 's1b/smoke_r3'
REFERENCE = Path('/data/fable/vortex/v2_dev/p3/smoke_deep3')
OUT = Path(sys.argv[1])
COPY = OUT / 'smoke_copy'
OUT.mkdir(parents=True, exist_ok=True)
assert not COPY.exists(), 'Use a new output directory for each replay'
sys.dont_write_bytecode = True
os.chdir(BASE / 'src')
sys.path.insert(0, str(SOURCE))
import p3_stage1b as p3

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(Path(p3.__file__)) == '92674ee8aa685b2a20bf5a689a3cbba836b195b8657ba8f79c5da161f315b765'
shutil.copytree(ORIGINAL, COPY)
results = {}
for wave in ('W1', 'W2'):
    with (OUT / f'collect_{wave}_parent.log').open('w') as log, contextlib.redirect_stdout(log):
        p3.collect(str(BASE / 's1b/p3_settings_smoke_r3.json'), str(BASE / 's1b/p3_metric.json'), str(COPY), wave,
                   str(COPY / f'collect_{wave}_parent.json'))
    original = json.loads((ORIGINAL / f'collect_{wave}.json').read_bytes())
    replay = json.loads((COPY / f'collect_{wave}_parent.json').read_bytes())
    assert {k: v for k, v in original.items() if k != 'tag'} == {k: v for k, v in replay.items() if k != 'tag'}
    assert replay['collection_ok'] and not replay['open_executions'] and not replay['queue_left'] and not replay['claims_left']
    results[wave] = {'saved_summary_sha256': sha(ORIGINAL / f'collect_{wave}.json'),
                     'status': replay['status'], 'executions': replay['executions'],
                     'dead_executions': replay['dead_executions'], 'open_executions': replay['open_executions'],
                     'all_fields_except_tag_exactly_reproduced': True}
libs = {}
for path in sorted((REFERENCE / 'lib').glob('*.jsonl')):
    h = sha(path)
    assert sha(COPY / 'lib' / path.name) == sha(ORIGINAL / 'lib' / path.name) == h
    libs[path.name] = h
assert len(libs) == 4
out = {'scope': __doc__, 'timestamp': datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),
       'runner_sha256': sha(Path(p3.__file__)), 'runtime': p3.p2.runtime(), 'wave_replays': results,
       'libraries_identical_to_saved_and_reference': libs, 'all_assertions_passed': True,
       'limits': 'Recollection of existing raw smoke shards; no new simulator execution, RPC fault injection or production mutation.'}
(OUT / 'smoke_archive_replay.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))
