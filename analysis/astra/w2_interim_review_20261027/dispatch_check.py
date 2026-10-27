"""Probe current topup dispatcher with a finished original W2 array; no PBS calls."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DISPATCH = ROOT / 'analysis/fable/calibration/kunanyi/s1b_topup_dispatch.sh'
NODE = ROOT / 'analysis/fable/calibration/kunanyi/s1b_node.pbs'
QSTAT = '''#!/usr/bin/env python3
import os,sys
a=sys.argv[1:]
if '-u' in a:
    user=a[a.index('-u')+1]
    for i in range(381): print(f"860992[{i}].fixture {user} normal s1b 1 1 8 10gb 48:00 R 1:00")
    for i in range(14): print(f"860989[{i}].fixture {user} normal s1b 1 1 8 10gb 48:00 R 1:00")
    for i in (860990,860993): print(f"{i}.fixture {user} normal collect 1 1 1 16gb 08:00 H 0:00")
elif a[-1] in ('857922[]','857923') and '-x' in a: print('job_state = F')
elif a[-1]=='860992[]': print('job_state = B\\narray_state_count = Queued:0 Running:381 Held:0 Expired:0')
elif a[-1]=='858016[]':
    if '-x' in a: print('job_state = F\\narray_state_count = Queued:0 Running:0 Held:0 Expired:570')
    else:
        print('qstat: Unknown Job Id 858016[]',file=sys.stderr);sys.exit(153)
else: sys.exit(154)
'''
results = {}
with tempfile.TemporaryDirectory(prefix='w2-dispatch-review-') as td:
    for name, override in [('finished_default_reference', {}), ('live_reference_explicit', {'W2_ARRAY': '860992[]'})]:
        base = Path(td) / name
        kunanyi = base / 'src/analysis/fable/calibration/kunanyi'
        kunanyi.mkdir(parents=True)
        (base / 's1b/run2').mkdir(parents=True)
        (base / 'bin').mkdir()
        (base / 's1b_node_topup.pbs').write_bytes(NODE.read_bytes())
        (base / 's1b/reservations.tsv').write_text('release\ts1b_22b89261_a\tfixture already released\n')
        (base / 'bin/qstat').write_text(QSTAT)
        (base / 'bin/qstat').chmod(0o755)
        (kunanyi / 's1b_submit.sh').write_text('printf "%s\\n" "$*" >> "$VB/submissions.txt"\n')
        env = dict(os.environ, VB=str(base), NODE_SHA=hashlib.sha256(NODE.read_bytes()).hexdigest(),
                   LABEL='c', PBS_BIN=str(base / 'bin'), PBS_USER='fixture', **override)
        p = subprocess.run(['bash', str(DISPATCH)], env=env, text=True, capture_output=True, timeout=10)
        subs = (base / 'submissions.txt').read_text().splitlines() if (base / 'submissions.txt').exists() else []
        results[name] = {'exit': p.returncode, 'stdout': p.stdout.replace(str(base), '<temporary>'),
                         'stderr': p.stderr, 'submissions': [s.replace(str(base), '<temporary>') for s in subs]}
assert results['finished_default_reference']['exit'] == 153
assert results['finished_default_reference']['submissions'] == []
assert results['live_reference_explicit']['exit'] == 0
assert len(results['live_reference_explicit']['submissions']) == 2
out = {'scope': __doc__, 'dispatcher_sha256': hashlib.sha256(DISPATCH.read_bytes()).hexdigest(), 'cases': results,
       'limits': 'qstat models a scheduler that omits finished jobs unless -x; no live qstat replay. Submitter is a recording stub; its CPU reservations are not simulated.'}
(HERE / 'dispatch_check.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))
