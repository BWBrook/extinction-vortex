"""Bind the read-only remote receipts to this checkout and the prior reviewed package."""
import ast
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P2 = Path('analysis/fable/calibration/v2_dev/p2')
RUNNER = Path('analysis/fable/calibration/v2_dev/p2_stage1a.py')


def old_bytes(path):
    return subprocess.check_output(['git', 'show', f'81fcea3:{path}'], cwd=ROOT)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


old = json.loads(old_bytes(P2 / 'p2_settings_s1a.json'))
new = json.loads((ROOT / P2 / 'p2_settings_s1a.json').read_text())
changed = {k for k in old.keys() | new.keys() if old.get(k) != new.get(k)}
assert changed == {'runner_sha256', 'prefix_batches', 'report_rule'}
assert new['prefix_batches'] == 5
assert len(new['settings']) == 1080 and old['settings'] == new['settings']
remote = json.loads((HERE / 'remote_checks.json').read_text())
for path, key in [(RUNNER, 'runner'), (P2 / 'p2_settings_s1a.json', 'settings'),
                  (P2 / 'p2_metric.json', 'metric'), (P2 / 'throughput_kunanyi.json', 'throughput'),
                  (RUNNER.parent / 'p1_sampler.py', 'helper')]:
    assert sha((ROOT / path).read_bytes()) == remote['actual_hashes'][key]
    if key in {'metric', 'throughput', 'helper'}:
        assert (ROOT / path).read_bytes() == old_bytes(path)
for path, digest in remote['imported_source_hashes'].items():
    assert sha((ROOT / path).read_bytes()) == digest
    assert (ROOT / path).read_bytes() == old_bytes(path)
tar_matches = {}
for name, digest in remote['stage_listed_hashes'].items():
    path = Path(name.removeprefix('src/')) if name.startswith('src/') else P2 / Path(name).name
    assert sha((ROOT / path).read_bytes()) == digest
    tar_matches[name] = str(path)
old_ast = ast.parse(old_bytes(RUNNER))
new_ast = ast.parse((ROOT / RUNNER).read_text())
names = ('validate_E', 'factors', 'binom_factor', 'in_ball', 'one_batch')
for name in names:
    a = next(x for x in old_ast.body if isinstance(x, ast.FunctionDef) and x.name == name)
    b = next(x for x in new_ast.body if isinstance(x, ast.FunctionDef) and x.name == name)
    assert ast.dump(a, include_attributes=False) == ast.dump(b, include_attributes=False)
summary = json.loads((ROOT / P2 / 'dry3_summary.json').read_text())
assert summary['settings_sha256'] == remote['actual_hashes']['smoke_settings']
assert summary['hits'] == remote['dry3_totals']['hits'] == 38
assert summary['counter_and_hit_record_mismatches_vs_first_dry_run'] == [0, 0]
preflight = json.loads((HERE / 'preflight_replay.json').read_text())
assert [r['returncode'] for r in preflight['results']] == [0, 1, 1, 1]
assert all(r['receipt']['settings_sha256'] == remote['actual_hashes']['settings'] for r in preflight['results'])
prior_actual = 28 * 57 / 3600 + 6 / 3600
result = dict(timestamp=datetime.now(ZoneInfo('Australia/Hobart')).isoformat(), scope=__doc__,
              base='81fcea3', current=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              changed_settings_keys=sorted(changed), settings_unchanged=1080,
              unchanged_sampler_functions=list(names), metric_helper_bank_throughput_unchanged=True,
              stage_files_match_local=tar_matches, preflight_exit_codes=[r['returncode'] for r in preflight['results']],
              allocation_using_rounded_prior=991.44,
              smoke_allocated_cpu_hours_exact=prior_actual,
              allocation_using_exact_prior=990+1+prior_actual,
              prior_allocation_rounding_understatement=prior_actual-0.44)
print(json.dumps(result, indent=2, allow_nan=False))
