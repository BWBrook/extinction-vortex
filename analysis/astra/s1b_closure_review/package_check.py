"""Saved-package and native preflight audit of ca94676; no population simulation or PBS.

Run on deep-server. Only writes the named Astra audit directory and its ledger.
The existing Fable regression smoke is inspected without mutation.
"""
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import tarfile
import time
from zoneinfo import ZoneInfo

BASE = Path('/data/fable/vortex')
V2, P3 = BASE/'v2_dev', BASE/'v2_dev/p3'
SRC = BASE/'kunanyi_stage/run1/src'
OUT = Path('/data/codex/artifacts/project/s1b_closure_review_20261017')
OUT.mkdir(parents=True, exist_ok=True)
start = time.monotonic()


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text())


prev = read(Path('/data/codex/artifacts/project/s1b_repair_review_20261017/raw_checks.json'))
b = read(P3/'p3_settings.json')
old = dict(b, runner_sha256=prev['bound_sources']['runner_sha256'])
assert hashlib.sha256(json.dumps(old).encode()).hexdigest() == prev['hashes']['p3_settings.json']
assert sha(P3/'p3_metric.json') == b['metric_sha256'] == prev['hashes']['p3_metric.json']
assert sha(V2/'p3_stage1b.py') == b['runner_sha256']
for key, path in [('p2_sha256',V2/'p2_stage1a.py'),('p1_sampler_sha256',V2/'p1_sampler.py')]:
    assert sha(path) == b[key] == prev['bound_sources'][key]
assert b['imported_source_sha256'] == prev['bound_sources']['imported_source_sha256']
for name,digest in b['imported_source_sha256'].items():
    assert sha(SRC/name) == digest
members = {}
with tarfile.open(P3/'s1b_stage.tar') as archive:
    for member in archive:
        if member.isfile():
            name = member.name.removeprefix('./')
            digest = hashlib.sha256(archive.extractfile(member).read()).hexdigest()
            assert digest == sha(P3/'stage'/name)
            members[name] = digest
for line in (P3/'stage/s1b/stage_sha256.txt').read_text().splitlines():
    digest,name = line.split(maxsplit=1)
    assert members[name.removeprefix('./')] == digest

# Actual preflight, including native 22-case synthetic suite and source bindings.
# This reservation is in an audit-owned file, never the production ledger.
ledger = OUT/'audit_reservations.tsv'
assert not ledger.exists(), 'Preserve the first audit ledger; do not silently rerun.'
cmd = ['/usr/bin/python3','-I',str(V2/'p3_stage1b.py'),'preflight',str(P3/'p3_settings.json'),
       str(P3/'p3_metric.json'),str(ledger),'astra_closure_fixture',str(OUT/'not_dispatched'),
       '520','8','172800','W1']
env = dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',FLEXIBLAS_NUM_THREADS='1',TMPDIR=str(OUT))
p = subprocess.run(cmd,cwd=SRC,env=env,capture_output=True,text=True,timeout=90)
(OUT/'native_preflight.log').write_text(p.stdout+p.stderr)
assert p.returncode == 0, p.stderr
receipt = json.loads(p.stdout.splitlines()[-1])
assert receipt['preflight'] == 'passed'
assert receipt['reservation_cpu_h'] == receipt['wave_reserved'] == receipt['campaign_reserved'] == 199688
assert '"all_ok": true' in p.stdout
smoke = P3/'smoke_deep3'
snapshot = dict(path=str(smoke),complete_report_present=(smoke/'collect_W1.json').exists(),
                completion_marker_present=(smoke/'DONE').exists(),
                worker_logs={p.name:p.stat().st_size for p in smoke.glob('w*.log')})
result = dict(scope=__doc__,timestamp=datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),host=platform.node(),
              hashes={p.name:sha(p) for p in (P3/'p3_settings.json',P3/'p3_metric.json',P3/'p3_settings_smoke.json',P3/'s1b_stage.tar')},
              runner_sha256=b['runner_sha256'],previous_settings_exactly_reconstructed=True,
              settings_rows_unchanged=len(b['settings']),stage_member_hashes=members,
              native_preflight=receipt,audit_ledger=ledger.read_text(),regression_smoke_snapshot=snapshot,
              elapsed_seconds=time.monotonic()-start)
(OUT/'package_check.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
