"""Read the refreshed Stage 1a tar on deep-server and compare it to this checkout.

Only metadata and the small tar are read remotely. No extraction, simulation,
preflight, scheduler command or smoke replay is performed.
"""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REMOTE = '''
from pathlib import Path
import hashlib,json,platform,tarfile
p=Path('/data/fable/vortex/v2_dev/p2/s1a_stage_final.tar')
h=lambda b:hashlib.sha256(b).hexdigest()
with tarfile.open(p) as t:
    members={m.name.removeprefix('./'):h(t.extractfile(m).read()) for m in t.getmembers() if m.isfile()}
    manifest=t.extractfile('./s1a/stage_sha256.txt').read().decode()
listed={name.removeprefix('./'):sha for sha,name in (line.split(maxsplit=1) for line in manifest.splitlines())}
assert len(listed)==8 and set(members)==set(listed)|{'s1a/stage_sha256.txt'}
assert all(members[name]==sha for name,sha in listed.items())
print(json.dumps(dict(host=platform.node(),python=platform.python_version(),tar_path=str(p),tar_sha256=h(p.read_bytes()),tar_bytes=p.stat().st_size,listed=listed,manifest_sha256=members['s1a/stage_sha256.txt'])))
'''
proc = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', 'deep-server', 'python3 -'],
                      input=REMOTE, capture_output=True, text=True, timeout=30, check=True)
data = json.loads(proc.stdout)
assert data['host'] == 'deep-server'
unchanged = []
for name, digest in data['listed'].items():
    path = name.removeprefix('src/') if name.startswith('src/') else 'analysis/fable/calibration/v2_dev/p2/' + Path(name).name
    raw = (ROOT / path).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == digest
    if not path.endswith('/s1a_submit.sh'):
        assert raw == subprocess.check_output(['git', 'show', '7800f18:' + path], cwd=ROOT)
        unchanged.append(path)
assert data['tar_sha256'].startswith('a0f2270f')
data.update(timestamp=datetime.now(ZoneInfo('Australia/Hobart')).isoformat(), scope=__doc__,
            all_eight_files_match=True, unchanged_seven_files=unchanged)
(HERE / 'package_check.json').write_text(json.dumps(data, indent=2) + '\n')
print(json.dumps(data, indent=2))
