"""Audit saved repaired Stage 1b inputs and smoke outputs; no new population paths.

Run with system Python on deep-server from the staged source checkout.
Writes only the dated Astra audit directory, including a copy for recollection.
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
import subprocess
import tarfile
import time
from zoneinfo import ZoneInfo

ROOT = Path('/data/fable/vortex')
V2 = ROOT / 'v2_dev'
P3 = V2 / 'p3'
SRC = ROOT / 'kunanyi_stage/run1/src'
OUT = Path('/data/codex/artifacts/project/s1b_repair_review_20261017')
OUT.mkdir(parents=True, exist_ok=True)
START = time.monotonic()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_text())


b = read(P3 / 'p3_settings.json')
sm = read(P3 / 'p3_settings_smoke.json')
previous = read(Path('/data/codex/artifacts/project/s1b_package_review/raw_checks.json'))
assert len(b['settings']) == 21816
assert b['ceilings'] == dict(W1=200000, W2=1000000, campaign=1200000)
assert b['campaign'] == 's1b'
assert 'not a measured-CPU ceiling' in b['cap_rule']
for key, path in [('metric_sha256', P3/'p3_metric.json'), ('runner_sha256', V2/'p3_stage1b.py'),
                  ('p2_sha256', V2/'p2_stage1a.py'), ('p1_sampler_sha256', V2/'p1_sampler.py'),
                  ('pilot_settings_sha256', V2/'p2/p2_settings_s1a.json'),
                  ('pilot_collect_sha256', V2/'p2/s1a_main/collect_deep.json')]:
    assert sha(path.read_bytes()) == b[key], key
for path, digest in b['imported_source_sha256'].items():
    assert sha((SRC/path).read_bytes()) == digest
assert b['metric_sha256'] == previous['hashes']['p3_metric.json']
old = dict(b)
for key in ('campaign', 'ceilings', 'cap_rule'):
    old.pop(key)
old['runner_sha256'] = previous['bound_sources']['runner_sha256']
assert sha(json.dumps(old).encode()) == previous['hashes']['p3_settings.json']

stage_members = {}
with tarfile.open(P3/'s1b_stage.tar') as archive:
    for member in archive:
        if member.isfile():
            name = member.name.removeprefix('./')
            raw = archive.extractfile(member).read()
            assert sha(raw) == sha((P3/'stage'/name).read_bytes())
            stage_members[name] = sha(raw)
for line in (P3/'stage/s1b/stage_sha256.txt').read_text().splitlines():
    digest, name = line.split(maxsplit=1)
    assert stage_members[name.removeprefix('./')] == digest

deep, cluster = P3/'smoke_deep2', P3/'smoke2_kunanyi'
dc, kc = read(deep/'collect_W1.json'), read(cluster/'collect_W1.json')
assert dc['status'] == kc['status'] == dict(COMPLETE=4, CAPPED=2, FAILED=0, incomplete=0)
assert dc['collection_ok'] and kc['collection_ok']
assert kc['binding']['settings_sha256'] == sha((P3/'p3_settings_smoke.json').read_bytes())
assert dc['binding']['runner_sha256'] == kc['binding']['runner_sha256'] == b['runner_sha256']
archive_members = {}
with tarfile.open(cluster/'W1.tar.gz') as archive:
    for member in archive:
        assert member.isfile()
        raw = archive.extractfile(member).read()
        assert sha(raw) == sha((cluster/member.name).read_bytes())
        archive_members[member.name] = sha(raw)
comparisons = []
for dr, kr in zip(dc['rows'], kc['rows']):
    assert all(dr[k] == kr[k] for k in ('dir','index','pop','outer','n','library','status','prefix_end_batch','prefix_hits'))
    if dr['status'] != 'COMPLETE':
        continue
    d = dr['dir']
    db, kb = (deep/'lib'/f'{d}.jsonl').read_bytes(), (cluster/'lib'/f'{d}.jsonl').read_bytes()
    assert sha(db) == dr['library_sha256'] and sha(kb) == kr['library_sha256']
    assert db == (P3/'smoke_deep/lib'/f'{d}.jsonl').read_bytes()
    assert kb == (P3/'smoke_kunanyi/lib'/f'{d}.jsonl').read_bytes()
    dl, kl = [json.loads(x) for x in db.splitlines()], [json.loads(x) for x in kb.splitlines()]
    assert len(dl) == len(kl) == 2000
    differences = []
    for i, (a,z) in enumerate(zip(dl,kl)):
        assert {k:v for k,v in a.items() if k != 'theta'} == {k:v for k,v in z.items() if k != 'theta'}
        if a != z:
            fields = {k:dict(deep=a['theta'][k],cluster=z['theta'][k],ulps=abs(a['theta'][k]-z['theta'][k])/math.ulp(a['theta'][k]))
                      for k in a['theta'] if a['theta'][k] != z['theta'][k]}
            differences.append(dict(record_index=i,batch=a['batch'],proposal=a['proposal_in_batch'],fields=fields))
    serial = read(deep/f'serial_{d}.json')
    comparisons.append(dict(dir=d,records=2000,byte_identical=db==kb,differences=differences,serial_receipt=serial))

# Reconstruct the deep smoke's bound subset; only its ceiling differs from the final subset.
deep_sm = dict(sm, ceilings=dict(W1=40.0,W2=40.0,campaign=40.0))
deep_bytes = json.dumps(deep_sm).encode()
assert sha(deep_bytes) == dc['binding']['settings_sha256']
settings_copy = OUT/'deep_settings.json'
settings_copy.write_bytes(deep_bytes)
copy = OUT/'deep_copy'
if copy.exists():
    raise SystemExit('audit copy already exists; preserve it')
shutil.copytree(deep,copy)
env = dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',FLEXIBLAS_NUM_THREADS='1',TMPDIR=str(OUT))
proc = subprocess.run(['/usr/bin/python3','-I',str(V2/'p3_stage1b.py'),'collect',str(settings_copy),str(P3/'p3_metric.json'),str(copy),'W1',str(copy/'collect_W1.json')],
                      cwd=SRC,env=env,capture_output=True,text=True,timeout=60)
assert proc.returncode == 0, proc.stderr
assert read(copy/'collect_W1.json') == dc
test = subprocess.run(['/usr/bin/python3','-I',str(V2/'p3_stage1b.py'),'test'],cwd=SRC,env=env,capture_output=True,text=True,timeout=60)
(OUT/'p3_fixtures.log').write_text(test.stdout+test.stderr)
assert test.returncode == 0 and '"all_ok": true' in test.stdout

result = dict(scope=__doc__,timestamp=datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),host=platform.node(),
              hashes={p.name:sha(p.read_bytes()) for p in (P3/'p3_settings.json',P3/'p3_metric.json',P3/'s1b_stage.tar',cluster/'W1.tar.gz')},
              bound_sources={k:b[k] for k in ('runner_sha256','p2_sha256','p1_sampler_sha256','imported_source_sha256')},
              settings_rows_unchanged=21816,old_settings_hash_reconstructed=True,metric_unchanged=True,
              waves=dict(Counter(s['wave'] for s in b['settings'])),stage_member_hashes=stage_members,
              smoke_archive_member_hashes=archive_members,deep_status=dc['status'],cluster_status=kc['status'],
              library_comparisons=comparisons,recollect_deep_identical=True,collector_stdout=proc.stdout,
              native_synthetic_fixtures_passed=True,ceilings=b['ceilings'],cap_rule=b['cap_rule'],
              limitations=['Kunanyi archive has summary/log and four libraries, but no raw shards or scheduler receipts.',
                           'Comparison covers retained records, not all rejected proposals; CPU dispatch explanation unverified.',
                           'Previous metric and settings verification reused by exact hashes; no bank scan, export, new paths or fits.'],
              elapsed_seconds=time.monotonic()-START)
(OUT/'raw_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
