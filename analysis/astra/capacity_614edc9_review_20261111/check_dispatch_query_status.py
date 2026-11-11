"""Check actual dispatcher gate prefixes against failed and long qstat replies."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[3]
C = 'analysis/fable/calibration/kunanyi'
VERSIONS = {'old': '614edc9^', 'candidate': '614edc9', 'working_tree': 'working_tree'}
SHELLS = ['bash', '/home/bwbrook/.local/opt/bash-4.2.46-bin']


def source(rev, name):
    if rev == 'working_tree':
        return (ROOT / C / name).read_text()
    return subprocess.check_output(['git', 'show', f'{rev}:{C}/{name}'], cwd=ROOT, text=True)


def one(shell, rev, gate, error, padding):
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        (base / 's1b').mkdir()
        ledger = base / 's1b/reservations.tsv'
        ledger.write_text('reserve\ts1b\tW1\told_reservation\t100\n')
        binp = base / 'bin'
        binp.mkdir()
        qs = binp / 'qstat'
        qs.write_text('#!/usr/bin/env python3\nimport os\nprint("    job_state = F")\n'
                      'print("    array_state_count = Queued:0 Running:0 Held:0")\n'
                      'print("".join("    pad = " + "x" * 100 + "\\n" for _ in range(int(os.environ["PAD"]))))\n'
                      'raise SystemExit(int(os.environ["QSTAT_RC"]))\n')
        qs.chmod(0o755)
        env = dict(os.environ, VB=str(base), PBS_BIN=str(binp), LABEL='b', WAVES='W2', REF='9000[]',
                   RELEASES='old_reservation=9000[]', PAD=str(padding), QSTAT_RC=str(error),
                   W1_SUMMARY_SHA='unused', W2_SUMMARY_SHA='unused')
        if gate == 'topup_release':
            raw = source(rev, 's1b_topup_dispatch.sh').split('source "$C/kunanyi/s1b_capacity.sh"', 1)[0]
        elif gate == 'round3_release':
            block = source(rev, 's1b_round3_dispatch.sh').split('for rel in $R2_RELEASES; do', 1)[1].split('source \"$C/kunanyi/s1b_capacity.sh\"', 1)[0]
            raw = 'set -euo pipefail\nS=\"$VB/s1b\"; PBS=\"$PBS_BIN\"; R2_RELEASES=\"$RELEASES\"\nfor rel in $R2_RELEASES; do' + block
        else:
            stage = base / 'stage_round3'
            (stage / 's1b').mkdir(parents=True)
            (stage / 'sentinel').write_text('review-only stage\n')
            digest = hashlib.sha256((stage / 'sentinel').read_bytes()).hexdigest()
            (stage / 's1b/stage_sha256.txt').write_text(f'{digest}  ./sentinel\n')
            tar = base / 's1b_stage_round3.tar'
            with tarfile.open(tar, 'w') as tf:
                tf.add(stage, arcname='.')
            env['STAGE_SHA'] = hashlib.sha256(tar.read_bytes()).hexdigest()
            raw = source(rev, 's1b_round3_dispatch.sh').split('echo "== install"', 1)[0]
        done = subprocess.run([shell, '-c', raw + '\necho GATE_PASSED\n'], cwd=ROOT, env=env,
                              capture_output=True, text=True)
        return {'gate': gate, 'qstat_rc': error, 'padding_lines': padding,
                'script_rc': done.returncode, 'gate_passed': 'GATE_PASSED' in done.stdout,
                'reservation_released': '\nrelease\told_reservation\t' in ledger.read_text(),
                'last_stdout': done.stdout.strip().splitlines()[-1] if done.stdout.strip() else ''}


def main():
    source_hashes = {name: hashlib.sha256((ROOT / C / name).read_bytes()).hexdigest()
                     for name in ('s1b_round3_dispatch.sh', 's1b_topup_dispatch.sh')}
    result = {}
    for shell in SHELLS:
        key = subprocess.check_output([shell, '-c', 'echo "$BASH_VERSION"'], text=True).strip()
        result[key] = {}
        for name, rev in VERSIONS.items():
            rows = [one(shell, rev, gate, error, padding)
                    for gate in ('topup_release', 'round3_release', 'preinstall') for error, padding in ((0, 0), (2, 0), (0, 3000))]
            result[key][name] = rows
            for r in rows:
                if r['qstat_rc'] == 2:
                    assert r['gate_passed'] == (name == 'candidate')
                    if r['gate'].endswith('_release'):
                        assert r['reservation_released'] == (name == 'candidate')
                else:
                    assert r['gate_passed'] == (r['padding_lines'] == 0 or name != 'old')
    assert source_hashes == {name: hashlib.sha256((ROOT / C / name).read_bytes()).hexdigest() for name in source_hashes}
    out = {'scope': __doc__, 'results': result, 'working_tree_source_sha256': source_hashes,
           'working_tree_source_unchanged_during_tests': True, 'all_three_working_tree_gates_passed': True,
           'candidate_regression_reproduced': True,
           'limits': 'Actual gate prefixes and real Bash, with read-only qstat stubs and temporary ledger/stage. No PBS, production installation, reservations or jobs changed.'}
    Path(__file__).with_name('dispatch_query_status.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
