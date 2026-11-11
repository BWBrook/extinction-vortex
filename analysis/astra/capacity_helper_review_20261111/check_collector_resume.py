"""Replay the accepted-array/missing-collector recovery with stub PBS."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / 'analysis/fable/calibration/kunanyi'
OUT = Path(__file__).resolve().parent
old = subprocess.check_output(['git', 'show', '048329e:analysis/fable/calibration/kunanyi/s1b_capacity.sh'])
new = (SRC / 's1b_capacity.sh').read_bytes()
results = {}
with tempfile.TemporaryDirectory(prefix='collector_resume_review_') as td:
    target = Path(td)
    for name in ('s1a_submit_fixture.py', 's1b_submit_fixture.py', 's1b_submit.sh'):
        shutil.copyfile(SRC / name, target / name)
    source = (target / 's1b_submit_fixture.py').read_text().split('\nR = {', 1)[0]
    source = source.replace('        for step in steps:\n',
        '        for step in steps:\n'
        '            if step.get("install_helper"):\n'
        '                (HERE / "s1b_capacity.sh").write_bytes(REPAIRED_HELPER)\n')
    ns = {'__file__': str(target / 's1b_submit_fixture.py'), 'REPAIRED_HELPER': new}
    exec(compile(source, str(target / 's1b_submit_fixture.py'), 'exec'), ns)
    for shell in ('bash', '/home/bwbrook/.local/opt/bash-4.2.46-bin'):
        os.environ['FIX_BASH'] = shell
        cases = {}
        faults = {
            'normal_resume': {},
            'collector_at_capacity': {'load': 2840},
            'accepted_array_hidden': {'env': {'FIX_HIDE': '900000.fixture'}},
            'exact_query_failure': {'env': {'FIX_QSTAT_FAIL': 'all'}},
        }
        for name, fault in faults.items():
            (target / 's1b_capacity.sh').write_bytes(old)
            second = {'install_helper': True, 'mode': 'resume', 'env': {'FIX_PAD': '30000'}}
            second.update({k: v for k, v in fault.items() if k != 'env'})
            second['env'].update(fault.get('env', {}))
            steps = [{'env': {'FIX_PAD': '30000'}}, second,
                     {'mode': 'resume', 'load': 0, 'env': {'FIX_PAD': '30000'}},
                     {'mode': 'resume', 'env': {'FIX_PAD': '30000'}}]
            r = ns['scenario'](steps)
            assert r['runs'][0]['rc'] != 0 and r['runs'][0]['qsub_calls'] == 1
            success = name == 'normal_resume'
            assert (r['runs'][1]['rc'] == 0) == success
            assert [x['qsub_calls'] for x in r['runs']] == ([1, 1, 0, 0] if success else [1, 0, 1, 0])
            assert all(x['rc'] == 0 for x in r['runs'][2:])
            assert r['arrays_created'] == r['collectors_created'] == 1
            assert r['collector_depends_on'] == r['array_ids']
            cases[name] = r
        results[shell] = cases
    del os.environ['FIX_BASH']
receipt = {'reviewed_helper_sha256': hashlib.sha256(new).hexdigest(),
           'scenarios_by_shell': results, 'all_assertions_passed': True,
           'limits': 'Actual submitter and helper with stub PBS; only the helper is replaced between the accepted array and collector-only resume. No real scheduler requests or live occupancy verification.'}
(OUT / 'collector_resume_checks.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'all_assertions_passed': True, 'cases_per_shell': len(faults)}))
