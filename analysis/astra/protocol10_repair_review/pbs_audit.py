"""Syntax and bounded collector-failure check; no PBS, network or R execution."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
K = ROOT / 'analysis/fable/calibration/kunanyi'


def main():
    sources = sorted(K.glob('*.sh')) + sorted(K.glob('*.pbs'))
    syntax = {}
    for p in sources:
        r = subprocess.run(['bash', '-n', str(p)], text=True, capture_output=True)
        assert r.returncode == 0
        syntax[p.name] = r.returncode
    with tempfile.TemporaryDirectory(prefix='vortex-pbs-review-') as temp:
        base = Path(temp)
        envdir = base / 'src/analysis/fable/calibration/kunanyi'
        envdir.mkdir(parents=True)
        # Replace only the sourced environment in the temporary VBASE. The
        # committed collect.pbs itself executes unchanged.
        (envdir / 'env.sh').write_text('cd "$VBASE/src"\n')
        bins = base / 'bin'; bins.mkdir()
        python = bins / 'python'
        python.write_text('#!/bin/sh\nexit 17\n'); python.chmod(0o755)
        (base / 'validation_v1').mkdir(); (base / 'slot_logs').mkdir()
        (base / 'preflight_fixture.json').write_text('{}\n')
        env = os.environ | {'VBASE': str(base), 'PATH': str(bins) + ':' + os.environ['PATH']}
        r = subprocess.run(['bash', str(K / 'collect.pbs')], env=env, capture_output=True, text=True)
        result = {'reviewed_wrapper_commit': 'ede7451', 'shell_syntax': syntax,
                  'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                  'collector_failure_fixture': {'injected_collector_exit': 17,
                    'pbs_script_exit': r.returncode, 'log': (base / 'collect.log').read_text(),
                    'summary_exists': (base / 'validation_summary.json').exists(),
                    'archive_exists': (base / 'validation_v1.tar.gz').exists()},
                  'scope': 'Local shell syntax and mocked failure propagation only; no job submission or host feasibility test.'}
        assert r.returncode == 0 and 'collector exit 17' in result['collector_failure_fixture']['log']
        assert result['collector_failure_fixture']['summary_exists'] is False
    Path(__file__).with_suffix('.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
