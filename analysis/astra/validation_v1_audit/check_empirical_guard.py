"""Verify the actual v1 summary is refused before any empirical work.

Run with the existing dsipa-dev Python environment (NumPy/SciPy available).
"""
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / 'analysis/fable/calibration'
sys.path.insert(0, str(SOURCE))
from empirical_q1 import guard

try:
    guard(SOURCE / 'freeze_v1/validation_manifest.json',
          '/nonexistent-validation-base',
          SOURCE / 'validation_v1/validation_summary.json',
          '/nonexistent-empirical-output')
except SystemExit as exc:
    message = str(exc)
    assert message == 'validation did not pass (V-fail or fit stop): no labelled empirical test', message
    result = {'pass': True, 'actual_summary_refused': True, 'message': message,
              'scope': 'Called actual guard only; no preflight, bank loading, fitting or empirical-statistic calculation.',
              'python': sys.executable}
    (HERE / 'empirical_guard.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
else:
    raise AssertionError('Guard incorrectly allowed failed validation')
