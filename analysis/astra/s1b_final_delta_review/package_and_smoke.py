"""Final Stage 1b lazy-planning delta: saved package/smoke verification on deep-server.

No population simulation, production reservation or PBS command. Writes only the
named Astra audit directory, including an isolated copy for smoke recollection.
"""
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
V2, P3 = BASE/'v2_dev', BASE/'v2_dev/p3'
SRC = BASE/'kunanyi_stage/run1/src'
OUT = Path('/data/codex/artifacts/project/s1b_final_delta_review_20261017')
OUT.mkdir(parents=True, exist_ok=True)
start = time.monotonic()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def sha(p):
    return digest(p.read_bytes())


def read(p):
    return json.loads(p.read_text())


prev = read(Path('/data/codex/artifacts/project/s1b_closure_review_20261017/package_check.json'))
b, sm = read(P3/'p3_settings.json'), read(P3/'p3_settings_smoke.json')
old = dict(b, runner_sha256=prev['runner_sha256'])
assert digest(json.dumps(old).encode()) == prev['hashes']['p3_settings.json']
assert sha(P3/'p3_metric.json') == b['metric_sha256'] == prev['hashes']['p3_metric.json']
assert sha(V2/'p3_stage1b.py') == b['runner_sha256']
members = {}
with tarfile.open(P3/'s1b_stage.tar') as archive:
    for member in archive:
        if member.isfile():
            name = member.name.removeprefix('./')
            h = digest(archive.extractfile(member).read())
            assert h == sha(P3/'stage'/name)
            members[name] = h
for line in (P3/'stage/s1b/stage_sha256.txt').read_text().splitlines():
    h,name = line.split(maxsplit=1)
    assert members[name.removeprefix('./')] == h

smoke = P3/'smoke_deep3'
c = read(smoke/'collect_W1.json')
assert (smoke/'DONE').exists() and c['collection_ok']
assert c['status'] == dict(COMPLETE=4,CAPPED=2,FAILED=0,incomplete=0)
assert not c['errors'] and not c['incomplete'] and c['queue_left'] == c['claims_left'] == 0
old_sm = dict(sm, runner_sha256=prev['runner_sha256'],derived_from_sha256=prev['hashes']['p3_settings.json'])
old_bytes = json.dumps(old_sm).encode()
assert digest(old_bytes) == c['binding']['settings_sha256'] == prev['hashes']['p3_settings_smoke.json']
libraries = []
for r in c['rows']:
    if r['status'] != 'COMPLETE':
        continue
    name = r['dir']; raw = (smoke/'lib'/f'{name}.jsonl').read_bytes()
    receipt = read(smoke/f'serial_{name}.json')
    assert len(raw.splitlines()) == 2000 and digest(raw) == r['library_sha256']
    assert receipt['identical'] and receipt['serial_sha256'] == receipt['sharded_sha256'] == digest(raw)
    assert raw == (P3/'smoke_deep/lib'/f'{name}.jsonl').read_bytes()
    assert raw == (P3/'smoke_deep2/lib'/f'{name}.jsonl').read_bytes()
    libraries.append(dict(dir=name,sha256=digest(raw),records=2000,previous_deep_bytes_identical=True,serial_receipt_matches=True))

copy = OUT/'smoke_copy'
assert not copy.exists(), 'Preserve previous audit copy.'
shutil.copytree(smoke,copy)
old_path = OUT/'smoke_bound_settings.json'; old_path.write_bytes(old_bytes)
env = dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',FLEXIBLAS_NUM_THREADS='1',TMPDIR=str(OUT))
p = subprocess.run(['/usr/bin/python3','-I',str(V2/'p3_stage1b.py'),'collect',str(old_path),str(P3/'p3_metric.json'),str(copy),'W1',str(copy/'collect_W1.json')],
                   cwd=SRC,env=env,capture_output=True,text=True,timeout=60)
assert p.returncode == 0 and read(copy/'collect_W1.json') == c, p.stderr

ledger = OUT/'audit_reservations.tsv'; assert not ledger.exists()
q = subprocess.run(['/usr/bin/python3','-I',str(V2/'p3_stage1b.py'),'preflight',str(P3/'p3_settings.json'),str(P3/'p3_metric.json'),
                    str(ledger),'astra_final_fixture',str(OUT/'not_dispatched'),'520','8','172800','W1'],
                   cwd=SRC,env=env,capture_output=True,text=True,timeout=90)
(OUT/'native_preflight.log').write_text(q.stdout+q.stderr)
assert q.returncode == 0 and '"all_ok": true' in q.stdout, q.stderr
preflight = json.loads(q.stdout.splitlines()[-1])
assert preflight['preflight'] == 'passed' and preflight['wave_reserved'] == preflight['reservation_cpu_h'] == 199688
result = dict(scope=__doc__,timestamp=datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),
              hashes={p.name:sha(p) for p in (P3/'p3_settings.json',P3/'p3_settings_smoke.json',P3/'p3_metric.json',P3/'s1b_stage.tar')},
              runner_sha256=b['runner_sha256'],settings_rows_unchanged=len(b['settings']),
              prior_settings_reconstructed_exactly=True,stage_member_hashes=members,
              completed_smoke_status=c['status'],completed_smoke_binding=c['binding'],libraries=libraries,
              recollect_with_current_collector_identical=True,native_preflight=preflight,
              limitations=['Kunanyi NFS fixture and staging results attributed to Fable board 1809; not rerun here.',
                           'Serial recomputation receipts checked against libraries; no fresh numerical recomputation.',
                           'No fresh full-W1 seed timing run; 653 seconds and NFS estimate are Fable measurements.'],
              elapsed_seconds=time.monotonic()-start)
(OUT/'package_and_smoke.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
