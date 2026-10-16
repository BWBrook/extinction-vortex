"""Review the final submitter delta using local scheduler stubs only.

Usage: python3 checks.py /path/to/source-built/bash-4.2.46
No PBS command, simulation, build, mail or remote operation is performed.
The supplied fixture is copied into temporary directories; peer outputs remain intact.
"""
import ast
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
K = ROOT / 'analysis/fable/calibration/kunanyi'
SUBMIT = K / 's1a_submit.sh'
FIXTURE = K / 's1a_submit_fixture.py'
OLD = subprocess.check_output(['git', 'show', '7800f18:analysis/fable/calibration/kunanyi/s1a_submit.sh'], cwd=ROOT)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def harness(submit):
    source = FIXTURE.read_text()
    before = '"journal_tail": journal[-3:]'
    assert source.count(before) == 1
    source = source.replace(before, '"journal": journal, "journal_tail": journal[-3:]')
    body = []
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and any(isinstance(n, ast.Name) and n.id == 'R' for n in node.targets):
            break
        body.append(node)
    scope = {'__file__': str(FIXTURE)}
    exec(compile(ast.Module(body=body, type_ignores=[]), str(FIXTURE), 'exec'), scope)
    scope['SUBMIT'] = submit
    return scope


started = datetime.now(ZoneInfo('Australia/Hobart')).isoformat()
shells = {'bash52': Path(shutil.which('bash')), 'bash42': Path(sys.argv[1]).resolve()}
result = {}
for label, shell in shells.items():
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        shutil.copy2(SUBMIT, temp / SUBMIT.name)
        shutil.copy2(FIXTURE, temp / FIXTURE.name)
        env = dict(os.environ, FIX_BASH=str(shell))
        proc = subprocess.run([sys.executable, str(temp / FIXTURE.name)], env=env,
                              capture_output=True, text=True, timeout=240)
        baseline = json.loads((temp / 's1a_submit_fixture.json').read_text())
        assert proc.returncode == 0 and baseline['all_ok'] and len(baseline['checks']) == 17
        assert baseline['submit_sha256'] == sha(SUBMIT.read_bytes())
        (HERE / f'{label}_replay.json').write_text(json.dumps(baseline, indent=2) + '\n')
        old = temp / 'old_submit.sh'
        old.write_bytes(OLD)
        os.environ['FIX_BASH'] = str(shell)
        paired = {}
        for version, path in [('old', old), ('new', SUBMIT)]:
            scope = harness(path)
            scenario = scope['scenario']
            # Recreate the previous counterexample independently of the new
            # ambiguous_expired branch: accept, remove history, lose the reply.
            before = 'if n == at and mode == "ambiguous":\n    sys.exit(1)'
            original = scope['STUBS']['qsub']
            assert original.count(before) == 1
            scope['STUBS']['qsub'] = original.replace(before,
                'if n == at and mode == "ambiguous":\n    st.write_text(json.dumps(jobs[:-1]))\n    sys.exit(1)')
            delayed = scenario([{'env': {'FIX_FAIL_AT': '4', 'FIX_FAIL_MODE': 'ambiguous'}}, {'mode': 'resume'}])
            scope['STUBS']['qsub'] = original
            finished = scenario([{'env': {'FIX_FAIL_AT': '46', 'FIX_FAIL_MODE': 'reject'}},
                {'operator': [('rejected', 'c', None, 'fixture server receipt confirms no acceptance')],
                 'finish': list(range(45)), 'mode': 'resume'}])
            paired[version] = {'delayed_reply_expired_history': delayed, 'all_nodes_finished': finished}
        assert paired['old']['delayed_reply_expired_history']['node_jobs_created'] == 46
        assert paired['old']['delayed_reply_expired_history']['allocated_cpu_hours_bound'] == 1013.445
        d = paired['new']['delayed_reply_expired_history']
        assert [r['rc'] for r in d['runs']] == [1, 1]
        assert [r['qsub_calls'] for r in d['runs']] == [4, 0]
        assert d['node_jobs_created'] == 4 and d['collectors_created'] == 0
        assert d['journal_tail'][-1].startswith('uncertain j3 ')
        assert not any(line.startswith('rejected ') for line in d['journal'])
        f = paired['new']['all_nodes_finished']
        assert f['runs'][-1]['rc'] == 0 and f['collectors_created'] == 1 and f['collector_depends_on'] == 0
        assert f['workers_each_owned_once'] and f['allocated_cpu_hours_bound'] == 991.445
        if label == 'bash42':
            f = paired['old']['all_nodes_finished']
            assert f['runs'][-1]['rc'] != 0 and f['collectors_created'] == 0
            assert 'unbound variable' in '\n'.join(f['runs'][-1]['stderr'])
        for name in ('s1a_submit.sh', 's1a_node.pbs', 's1a_collect.pbs'):
            subprocess.run([str(shell), '-n', str(K / name)], check=True)
        result[label] = {'shell_path': str(shell), 'shell_sha256': sha(shell.read_bytes()),
                         'version': baseline['bash_version'], 'canonical_checks': 17, 'paired': paired}
        print(label, baseline['bash_version'], '17 checks and paired regressions pass', flush=True)

out = {'started_hobart': started, 'completed_hobart': datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),
       'scope': __doc__, 'reviewed_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
       'submit_sha256': sha(SUBMIT.read_bytes()), 'fixture_sha256': sha(FIXTURE.read_bytes()),
       'old_submit_sha256': sha(OLD), 'shells': result, 'all_ok': True}
(HERE / 'checks.json').write_text(json.dumps(out, indent=2) + '\n')
