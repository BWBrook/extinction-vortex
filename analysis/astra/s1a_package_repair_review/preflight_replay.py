"""Replay the four stated preflight commands on deep-server, without scheduler access.

Only the valid case reaches the runner's bounded unit fixtures. The other cases
must refuse before them. The runner owns temporary scratch and cleans it.
"""
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

ROOT = Path('/data/fable/vortex')
P2 = ROOT / 'v2_dev/p2'
env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
cases = [('valid', 45, 8, 9900), ('over_budget', 45, 8, 14400),
         ('wrong_shape', 44, 8, 9900), ('short_deadline', 45, 8, 7800)]
results = []
for name, jobs, cpus, wall in cases:
    args = [sys.executable, '-I', str(ROOT / 'v2_dev/p2_stage1a.py'), 'preflight',
            str(P2 / 'p2_settings_s1a.json'), str(P2 / 'p2_metric.json'),
            str(jobs), str(cpus), str(wall), '1000', '0.44', '1']
    start = time.monotonic()
    p = subprocess.run(args, cwd=ROOT / 'kunanyi_stage/run1/src', env=env,
                       capture_output=True, text=True, timeout=30)
    preflight, _, rest = p.stdout.partition('\n')
    result = dict(case=name, command=args, returncode=p.returncode,
                  receipt=json.loads(preflight), stderr=p.stderr,
                  elapsed_seconds=time.monotonic()-start)
    if name == 'valid':
        assert p.returncode == 0 and result['receipt']['preflight'] == 'passed'
        result['fixtures'] = json.loads(rest)
        assert result['fixtures']['all_ok']
    else:
        assert p.returncode != 0 and result['receipt']['preflight'] == 'refused'
        assert not rest.strip()
    results.append(result)
print(json.dumps(dict(timestamp=datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),
                      scope=__doc__, results=results), indent=2, allow_nan=False))
