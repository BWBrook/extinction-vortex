"""Review second-repair bindings and saved smoke; reuse the prior bounded preflight replay.

Run locally from this checkout. Remote operations only read saved files and run
the existing small preflight fixtures on deep-server. No PBS command is used.
"""
import ast
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PRIOR = ROOT / 'analysis/astra/s1a_package_repair_review'
P2 = Path('analysis/fable/calibration/v2_dev/p2')
RUNNER = P2.parent / 'p2_stage1a.py'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def old_bytes(path):
    return subprocess.check_output(['git', 'show', f'2404fda:{path}'], cwd=ROOT)


def remote_python(source):
    p = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10',
                        'deep-server', 'python3 -'], input=source, text=True,
                       capture_output=True, timeout=60, check=True)
    return json.loads(p.stdout)


# The previous reader remains suitable except that this round re-collects the
# archived smoke rather than rerunning it. Keep its original runner binding.
reader = (PRIOR / 'remote_checks.py').read_text()
before = "'runner_sha256': actual['runner']}"
assert reader.count(before) == 1
reader = reader.replace(before, "'runner_sha256': smoke['runner_sha256']}")
before = "assert collect['collection_ok'] and collect['run_complete'] and collect['n_errors'] == 0"
assert reader.count(before) == 1
reader = reader.replace(before, before + "\n    assert collect['provenance_complete'] and collect['workers_missing'] == []")
before = "'dry3_collect_sha256': digest((P2 / 'dry3/collect.json').read_bytes()),"
assert reader.count(before) == 1
reader = reader.replace(before, before + "\n        'smoke_execution_runner_sha256': smoke['runner_sha256'],\n        'current_collection_provenance_complete': collect['provenance_complete'],")
remote = remote_python(reader)
(HERE / 'remote_checks.json').write_text(json.dumps(remote, indent=2) + '\n')

replay = (PRIOR / 'preflight_replay.py').read_text()
assert replay.count("'1000', '0.44', '1'") == 1
replay = replay.replace("'1000', '0.44', '1'", "'1000', '0.445', '1'")
preflight = remote_python(replay)
(HERE / 'preflight_replay.json').write_text(json.dumps(preflight, indent=2) + '\n')

old = json.loads(old_bytes(P2 / 'p2_settings_s1a.json'))
new = json.loads((ROOT / P2 / 'p2_settings_s1a.json').read_text())
changed = {k for k in old.keys() | new.keys() if old.get(k) != new.get(k)}
assert changed == {'runner_sha256', 'report_rule'}
assert old['settings'] == new['settings'] and len(new['settings']) == 1080
assert new['prefix_batches'] == 5
for path, key in [(RUNNER, 'runner'), (P2 / 'p2_settings_s1a.json', 'settings'),
                  (P2 / 'p2_metric.json', 'metric'), (P2 / 'throughput_kunanyi.json', 'throughput'),
                  (RUNNER.parent / 'p1_sampler.py', 'helper')]:
    assert digest((ROOT / path).read_bytes()) == remote['actual_hashes'][key]
    if key in {'metric', 'throughput', 'helper'}:
        assert (ROOT / path).read_bytes() == old_bytes(path)
for path, sha in remote['imported_source_hashes'].items():
    assert digest((ROOT / path).read_bytes()) == sha
    assert (ROOT / path).read_bytes() == old_bytes(path)
for name, sha in remote['stage_listed_hashes'].items():
    path = Path(name.removeprefix('src/')) if name.startswith('src/') else P2 / Path(name).name
    assert digest((ROOT / path).read_bytes()) == sha
old_ast = ast.parse(old_bytes(RUNNER))
new_ast = ast.parse((ROOT / RUNNER).read_text())
unchanged = ('validate_E', 'factors', 'binom_factor', 'in_ball', 'one_batch',
             'run_setting', 'journal_prefix', 'preflight')
for name in unchanged:
    a = next(n for n in old_ast.body if isinstance(n, ast.FunctionDef) and n.name == name)
    b = next(n for n in new_ast.body if isinstance(n, ast.FunctionDef) and n.name == name)
    assert ast.dump(a, include_attributes=False) == ast.dump(b, include_attributes=False)
prior_remote = json.loads((PRIOR / 'remote_checks.json').read_text())
assert remote['actual_hashes']['smoke_settings'] == prior_remote['actual_hashes']['smoke_settings']
assert remote['smoke_execution_runner_sha256'] == prior_remote['actual_hashes']['runner']
assert remote['dry3_totals'] == prior_remote['dry3_totals']
summary = json.loads((ROOT / P2 / 'dry3_summary.json').read_text())
assert summary['settings_sha256'] == remote['actual_hashes']['smoke_settings']
assert summary['provenance_complete'] and summary['workers_missing'] == []
assert summary['hits'] == remote['dry3_totals']['hits'] == 38
assert [r['returncode'] for r in preflight['results']] == [0, 1, 1, 1]
assert all(r['receipt']['settings_sha256'] == remote['actual_hashes']['settings'] for r in preflight['results'])
assert preflight['results'][0]['receipt']['allocated_cpu_hours_bound'] == 991.445
out = dict(timestamp=datetime.now(ZoneInfo('Australia/Hobart')).isoformat(), scope=__doc__,
           base='2404fda', reviewed_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
           changed_settings_keys=sorted(changed), settings_unchanged=1080,
           unchanged_functions=list(unchanged), metric_helper_bank_throughput_unchanged=True,
           all_eight_staged_files_match_checkout=True, archived_smoke_provenance_preserved=True,
           preflight_exit_codes=[r['returncode'] for r in preflight['results']],
           allocated_cpu_hours_bound=991.445,
           reused_reader_sha256=digest((PRIOR / 'remote_checks.py').read_bytes()),
           reused_preflight_driver_sha256=digest((PRIOR / 'preflight_replay.py').read_bytes()))
(HERE / 'checks.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))
