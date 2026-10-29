"""Replay the round-3 stage and final-summary contracts without PBS or simulation."""
import collections
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[3]
C = Path('analysis/fable/calibration')
P = ROOT / C / 'v2_dev/p3'
DISPATCH = ROOT / C / 'kunanyi/s1b_round3_dispatch.sh'
BUILD = P / 'build_stage_r3.sh'
SETTINGS_SHA = '248f9c7de660dcac19a3e6806fbf97bc512aca9cff42abd54e5fd0f4ee3bbd73'
SELECTED_SHA = '8c46667e4ab9e8a8bd03911eda81f9de072df25f1f40cfbb953c4108965cb3b9'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stage_case(base, tar, stage_sha, name):
    base.mkdir()
    installed = base / 'src' / C
    staged = base / 'stage_round3'
    staged.mkdir()
    with tarfile.open(tar) as tf:
        tf.extractall(staged, filter='data')
    shutil.copyfile(tar, base / 's1b_stage_round3.tar')
    (base / 's1b').mkdir()
    runner = installed / 'v2_dev/p3_stage1b.py'
    runner.parent.mkdir(parents=True)
    runner.write_text('old installed runner\n')
    original_sha = sha(runner)
    (installed / 'kunanyi').mkdir()
    for rel in ('v2_dev/p1_sampler.py', 'v2_dev/p2_stage1a.py'):
        shutil.copyfile(staged / 'src' / C / rel, installed / rel)
    (installed / 'kunanyi/env.sh').write_text('return 77\n')
    bindir = base / 'bin'
    bindir.mkdir()
    (bindir / 'qstat').write_text(
        '#!/bin/sh\nprintf "called\\n" >> "$VB/qstat_calls"\n'
        + ('printf "job_state = Q\\n"\n' if name == 'unfinished_round2' else 'printf "job_state = F\\n"\n'))
    (bindir / 'qstat').chmod(0o755)
    staged_runner = staged / 'src' / C / 'v2_dev/p3_stage1b.py'
    if name in ('tampered_file', 'substituted_manifest'):
        staged_runner.write_text(staged_runner.read_text() + '\nSTAGE_SUBSTITUTE = True\n')
    if name == 'substituted_manifest':
        manifest = staged / 's1b/stage_sha256.txt'
        lines = []
        for line in manifest.read_text().splitlines():
            _, rel = line.split('  ', 1)
            lines.append(f'{sha(staged / rel)}  {rel}\n')
        manifest.write_text(''.join(lines))
    if name == 'substituted_tar':
        with (base / 's1b_stage_round3.tar').open('ab') as f:
            f.write(b'substituted tar bytes\n')
    env = dict(os.environ, VB=str(base), PBS_BIN=str(bindir), STAGE_SHA=stage_sha,
               W1_SUMMARY_SHA='unused', W2_SUMMARY_SHA='unused')
    done = subprocess.run(['bash', str(DISPATCH)], cwd=ROOT, env=env, text=True, capture_output=True)
    installed_changed = sha(runner) != original_sha
    calls = len((base / 'qstat_calls').read_text().splitlines()) if (base / 'qstat_calls').exists() else 0
    if name == 'valid_stage':
        assert done.returncode == 77 and installed_changed and calls == 8
        assert sha(runner) == sha(ROOT / C / 'v2_dev/p3_stage1b.py')
        assert 'stage OK' in done.stdout and '== round-3 settings' in done.stdout
    else:
        assert done.returncode == 1 and not installed_changed
        assert calls == (1 if name == 'unfinished_round2' else 0)
    return {'case': name, 'exit_code': done.returncode, 'installed_runner_changed': installed_changed,
            'qstat_stub_calls': calls, 'last_stdout_line': done.stdout.strip().splitlines()[-1],
            'stderr': done.stderr.strip()}


def summary_case(base, settings, gate, name):
    base.mkdir()
    summaries = [base / f'{wave}.json' for wave in ('W1', 'W2')]
    for dest, wave in zip(summaries, ('W1', 'W2')):
        shutil.copyfile(P / f'{wave.lower()}_r2b_collect_{wave}_b.json', dest)
    if name in ('errors_not_invalid', 'changed_identity', 'failed_recovery'):
        c = json.loads(summaries[1].read_text())
        row = next(r for r in c['rows'] if r['status'] == 'incomplete')
        if name == 'errors_not_invalid':
            c['errors'][0] = row['dir'] + ':' + c['errors'][0].split(':', 1)[1]
        elif name == 'changed_identity':
            row['n'] += 1
        else:
            row['status'] = 'FAILED'
            c['status']['incomplete'] -= 1
            c['status']['FAILED'] += 1
            c['incomplete'].remove(row['dir'])
        summaries[1].write_text(json.dumps(c))
    digests = [sha(p) for p in summaries]
    if name == 'wrong_digest':
        digests[1] = '0' * 64
    dirs, counts = base / 'dirs.txt', base / 'counts.txt'
    argv = [sys.executable, '-I', '-', str(settings), str(dirs), str(counts)]
    for p, h in zip(summaries, digests):
        argv += [str(p), h]
    done = subprocess.run(argv, input=gate, text=True, capture_output=True, cwd=ROOT)
    passes = name in ('valid_summaries', 'failed_recovery')
    assert (done.returncode == 0) == passes
    result = {'case': name, 'exit_code': done.returncode, 'stdout': done.stdout.strip(), 'stderr': done.stderr.strip()}
    if passes:
        wanted = dirs.read_text().splitlines()
        assert len(wanted) == len(set(wanted)) == 6935
        assert counts.read_text() == 'W1 18\nW2 6917\n'
        result.update(selected_count=len(wanted), per_wave={'W1': 18, 'W2': 6917})
        if name == 'failed_recovery':
            assert row['dir'] in wanted
            result['failed_row_included'] = row['dir']
    else:
        assert not dirs.exists() and not counts.exists()
    return result, dirs


def main():
    settings = Path(sys.argv[1]).resolve()
    assert sha(settings) == SETTINGS_SHA
    gate = DISPATCH.read_text().split("<<'PY'\n", 1)[1].split('\nPY\n', 1)[0]
    with tempfile.TemporaryDirectory(prefix='astra_r3_stage_closure_') as td:
        tmp = Path(td)
        tars = [tmp / f'stage{i}.tar' for i in (1, 2)]
        for path in tars:
            subprocess.run(['bash', str(BUILD), '8be1b4e', str(path)], cwd=ROOT, capture_output=True, check=True)
        stage_sha = sha(tars[0])
        assert stage_sha == sha(tars[1]) and stage_sha.startswith('53603d42')
        manifest_files = {}
        with tarfile.open(tars[0]) as tf:
            manifest = tf.extractfile('./s1b/stage_sha256.txt').read()
            for line in manifest.decode().splitlines():
                digest, rel = line.split('  ', 1)
                blob = tf.extractfile(rel).read()
                assert hashlib.sha256(blob).hexdigest() == digest
                local = ROOT / rel.removeprefix('./src/')
                assert sha(local) == digest
                manifest_files[str(local.relative_to(ROOT))] = digest
        assert len(manifest_files) == 10
        stages = [stage_case(tmp / name, tars[0], stage_sha, name) for name in
                  ('valid_stage', 'tampered_file', 'substituted_tar', 'substituted_manifest', 'unfinished_round2')]
        summaries = []
        for name in ('valid_summaries', 'wrong_digest', 'errors_not_invalid', 'changed_identity', 'failed_recovery'):
            receipt, dirs = summary_case(tmp / name, settings, gate, name)
            summaries.append(receipt)
        dirs = tmp / 'valid_summaries/dirs.txt'
        selected = tmp / 'selected.json'
        done = subprocess.run(['uv', 'run', '--offline', '--python', '3.12', '--with', 'numpy==1.26.4',
                               '--with', 'scipy==1.11.4', 'python', str(ROOT / C / 'v2_dev/p3_stage1b.py'),
                               'select', str(settings), str(selected), str(dirs)],
                              cwd=ROOT, capture_output=True, text=True, check=True)
        assert sha(selected) == SELECTED_SHA
        original, new = [json.loads(p.read_text()) for p in (settings, selected)]
        want = set(dirs.read_text().splitlines())
        assert new['settings'] == [s for s in original['settings'] if s['dir'] in want]
        changed = {k for k in set(original) | set(new) if original.get(k) != new.get(k)}
        assert changed == {'settings', 'runner_sha256', 'derived_from_sha256', 'stage'}
        assert new['derived_from_sha256'] == sha(settings)
        assert new['runner_sha256'] == manifest_files[str(C / 'v2_dev/p3_stage1b.py')]
        result = {'target_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  'stage_source_commit': '8be1b4e', 'stage_sha256': stage_sha,
                  'stage_manifest_sha256': hashlib.sha256(manifest).hexdigest(),
                  'two_builds_identical': True, 'all_ten_stage_files_equal_review_checkout': manifest_files,
                  'stage_cases': stages, 'summary_gate_cases': summaries,
                  'settings_r2_sha256': sha(settings), 'settings_r3_sha256': sha(selected),
                  'selected_rows_unchanged': True, 'changed_top_level_fields': sorted(changed),
                  'selected_rows_by_wave': dict(collections.Counter(s['wave'] for s in new['settings'])),
                  'all_assertions_passed': True,
                  'limits': 'Local stage extraction/install gate and exact summary/select replay only; no PBS, preflight, simulation, archive-content or remote transport execution.'}
    out = Path(__file__).with_name('stage_inventory_checks.json')
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
