"""Replay the repaired node and assert closure of the previous two counterexamples."""
import contextlib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / 'analysis/fable/calibration/v2_dev/p3/codex_node_combined_on_8fe10208.py'
FIXTURE = ROOT / 'analysis/astra/r2_node_review_20261025/s1b_node_fixture.py'
source = SOURCE.read_text()
source = source.replace("HERE / 's1b_node_fixture.py'", repr(str(FIXTURE)))
source = source.replace("(HERE / 'combined_checks.json')", 'Path(' + repr(str(HERE / 'node_checks.json')) + ')')
with (HERE / 'node_checks.log').open('w') as log, contextlib.redirect_stdout(log):
    exec(compile(source, str(SOURCE), 'exec'), {'__name__': '__main__', '__file__': str(SOURCE)})
result = json.loads((HERE / 'node_checks.json').read_text())
cases = result['cases']
for name, elapsed in [('empty_unknown_loop_past_deadline', 10), ('empty_unknown_loop_ignores_idle_budget', 30)]:
    case = cases[name]
    assert not case['forced_termination'] and case['rc'] == 0 and case['clock'] == elapsed
    assert len(case['launches']) == 1 and case['done']
cases['empty_unknown_loop_past_deadline']['note'] = 'Repaired node retires at cutoff with zero scans at or beyond cutoff.'
cases['empty_unknown_loop_ignores_idle_budget']['note'] = 'Repaired node retires at the whole-subjob idle budget.'
result['source_sha256'] = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
result['fixture_sha256'] = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
result['closure_assertions_passed'] = True
(HERE / 'node_checks.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'node_sha256': result['node_sha256'], 'closure_assertions_passed': True}))
