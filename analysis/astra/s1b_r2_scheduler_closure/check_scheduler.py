"""Independent closure checks of the repaired Stage 1b dispatch and collector paths.

Uses actual shell scripts and extracted actual Python admission, selection,
reservation and collection bodies. Native scientific checks and seeding are
stubbed; no live PBS, remote compute or production data are touched. The previous
review's helper definitions provide the isolated directory and scheduler stubs.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
prior = HERE.parent / 's1b_r2_scheduler_review/check_scheduler.py'
exec(compile(prior.read_text().split("\nout={'scope':", 1)[0], str(prior), 'exec'))
OUT = HERE


def fixture_inputs():
    b = {'stage': 'fixture', 'settings': [
        {'dir': f's{i:05d}', 'index': i, 'pop': 'fixture', 'outer': f'b1/{i}', 'n': 30 if i < 3 else 300,
         'library': 'primary', 'wave': 'W1' if i < 3 else 'W2'} for i in range(4)],
         'campaign': 's1b', 'ceilings': {'W1': 200000, 'W2': 1000000, 'campaign': 1200000},
         'metric_sha256': 'fixture-metric', 'runner_sha256': 'fixture-round1-runner'}
    c = {'wave': 'W1', 'collection_ok': False,
         'binding': {'settings_sha256': hashlib.sha256(json.dumps(b).encode()).hexdigest(),
                     'runner_sha256': b['runner_sha256'], 'metric_sha256': b['metric_sha256']},
         'rows': [dict(s, status=status) for s, status in zip(b['settings'], ['COMPLETE', 'incomplete', 'invalid'])],
         'status': {'COMPLETE': 1, 'CAPPED': 0, 'FAILED': 0, 'incomplete': 1}, 'incomplete': ['s00001'],
         'n_errors': 1, 'errors': ['s00002: ValueError: verified K-hit prefix without a COMPLETE marker']}
    c['rows'][0]['library_sha256'] = '1' * 64
    return b, c


OldSandbox = Sandbox


class Sandbox(OldSandbox):
    def __init__(self, parent):
        super().__init__(parent)
        self.env['ROUND1_SUMMARY_SHA'] = sha(self.s/'run/collect_W1.json')


def gate_tests():
    b, c = fixture_inputs()
    variants = {'normal': c, 'wrong_summary_digest': c}
    def variant(name, change):
        x = copy.deepcopy(c); change(x); variants[name] = x
    variant('wrong_wave', lambda x: x.update(wave='W2'))
    variant('missing_binding', lambda x: x.pop('binding'))
    for key in ('settings_sha256', 'metric_sha256', 'runner_sha256'):
        variant('wrong_' + key, lambda x, key=key: x['binding'].update({key: 'WRONG'}))
    variant('unknown_status', lambda x: x['rows'][0].update(status='UNKNOWN'))
    for key in ('index', 'pop', 'outer', 'n', 'library'):
        variant('wrong_row_' + key, lambda x, key=key: x['rows'][0].update({key: 'WRONG'}))
    variant('duplicate_complete_row', lambda x: x['rows'].append(copy.deepcopy(x['rows'][0])))
    variant('missing_dir', lambda x: x['rows'].pop(0))
    variant('complete_without_library', lambda x: x['rows'][0].pop('library_sha256'))
    variant('incomplete_with_library', lambda x: x['rows'][1].update(library_sha256='1' * 64))
    variant('wrong_counts', lambda x: x['status'].update(COMPLETE=2))
    variant('wrong_incomplete_list', lambda x: x.update(incomplete=[]))
    variant('truncated_errors', lambda x: x.update(n_errors=2))
    variant('error_outside_invalid', lambda x: x.update(errors=['s00001: invalid']))
    variant('wrong_collection_ok', lambda x: x.update(collection_ok=True))
    result = {}
    with tempfile.TemporaryDirectory() as td:
        d = Path(td); sp = d/'settings.json'; cp = d/'collect.json'; dst = d/'dirs.txt'
        sp.write_text(json.dumps(b))
        for name, value in variants.items():
            cp.write_text(json.dumps(value)); dst.unlink(missing_ok=True)
            want = sha(cp) if name != 'wrong_summary_digest' else '0' * 64
            p = subprocess.run([sys.executable, '-', str(cp), str(sp), str(dst), want],
                               input=GATE, text=True, capture_output=True)
            selected = dst.read_text().splitlines() if dst.exists() else None
            result[name] = {'rc': p.returncode, 'stderr': p.stderr.strip(), 'selected': selected}
            assert (p.returncode == 0) == (name == 'normal'), (name, result[name])
            if name == 'normal': assert selected == ['s00001', 's00002', 's00003']
            else: assert selected is None
    return result


def dispatch_tests():
    with tempfile.TemporaryDirectory() as td:
        box = Sandbox(td); args = ['bash', str(box.k/'s1b_round2_dispatch.sh')]
        first = box.run(args, {'FIX_FAIL_AT': '3', 'FIX_FAIL_MODE': 'reject'})
        unresolved = box.run(args)
        journal = box.s/'run2/submit_W2/submit_journal.tsv'
        name = next(x.split()[2] for x in journal.read_text().splitlines() if x.startswith('request a '))
        journal.open('a').write(f'rejected a {name} manual: isolated stub scheduler proves no job accepted\n')
        resolved = box.run(args)
        repeated = box.run(args)
        lines = (box.s/'reservations.tsv').read_text().splitlines()
        release = [x for x in lines if x.startswith('release\t')]
        result = {'first_W2_array_rejected': first, 'unresolved_retry': unresolved,
                  'reconciled_retry': resolved, 'complete_retry': repeated, 'jobs': box.jobs(), 'ledger': lines}
        assert [x['rc'] == 0 for x in (first, unresolved, resolved, repeated)] == [False, False, True, True], result
        assert [x['new_qsub_calls'] for x in (first, unresolved, resolved, repeated)] == [3, 0, 2, 0], result
        assert len(release) == 1 and len(box.jobs()) == 4 and len(lines) == 4, result
        return result


def existing_settings_mismatch():
    with tempfile.TemporaryDirectory() as td:
        box = Sandbox(td); p = box.s/'p3_settings_r2.json'; original = b'{"existing": true}\n'; p.write_bytes(original)
        result = box.run(['bash', str(box.k/'s1b_round2_dispatch.sh')])
        result.update(existing_bytes_preserved=p.read_bytes() == original,
                      ledger_lines=len((box.s/'reservations.tsv').read_text().splitlines()))
        assert result['rc'] != 0 and result['new_qsub_calls'] == 0 and result['existing_bytes_preserved'] and result['ledger_lines'] == 1, result
        return result


def topup_tests():
    with tempfile.TemporaryDirectory() as td:
        box = Sandbox(td); (box.s/'reservations.tsv').open('a').write('release\ts1b_5e346b76_a\tmanual: fixture terminal\n')
        args = ['bash', str(box.k/'s1b_submit.sh'), str(box.vb), 'p3_settings.json', 'run2', 'W1', '1', '8', '48:00:00']
        first = box.run(args); valid = box.run(args + ['topup', 'b'])
        orig = (box.s/'p3_settings.json').read_bytes()
        (box.s/'same_settings.json').write_bytes(orig)
        other = args.copy(); other[3] = 'same_settings.json'
        filename = box.run(other + ['topup', 'c'])
        (box.s/'p3_settings.json').write_bytes(orig + b'\n')
        digest = box.run(args + ['topup', 'd'])
        (box.s/'p3_settings.json').write_bytes(orig)
        resume = box.run(args + ['resume', 'b'])
        result = {'first': first, 'valid_topup': valid, 'different_filename_same_bytes': filename,
                  'same_filename_different_bytes': digest, 'resume_valid_topup': resume, 'jobs': box.jobs()}
        assert [x['rc'] == 0 for x in (first, valid, filename, digest, resume)] == [True, True, False, False, True], result
        assert [x['new_qsub_calls'] for x in (first, valid, filename, digest, resume)] == [2, 2, 0, 0, 0], result
        return result


def collector_race():
    # Exercise actual collect() tag/pack code and actual collector shell with an
    # empty scientific inventory; force both summaries to precede either archive.
    bodies = '\n\n'.join(ast.unparse(n) for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('binding', 'collect'))
    p2tree = ast.parse((P3.parent/'p2_stage1a.py').read_text())
    atomic = '\n\n'.join(ast.unparse(n) for n in p2tree.body if isinstance(n, ast.FunctionDef) and n.name == 'atomic_json')
    script = '''import os,sys,json,time,hashlib,tempfile,types
from pathlib import Path
''' + atomic + '''
p2=types.SimpleNamespace(atomic_json=atomic_json,sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest())
ls=os.listdir
''' + bodies + '''
tag=os.environ['TAG']; run=Path(sys.argv[-3])
if tag=='W1_c':
 for _ in range(500):
  if (run/'b_ready').exists():break
  time.sleep(.01)
collect(*sys.argv[-5:])
print('collector '+tag,flush=True)
if tag=='W1_b':
 (run/'b_ready').touch()
 for _ in range(500):
  if (run/'c_ready').exists():break
  time.sleep(.01)
else:(run/'c_ready').touch()
'''
    with tempfile.TemporaryDirectory() as td:
        d = Path(td); vb = d/'vbase'; k = vb/'src/analysis/fable/calibration/kunanyi'; k.mkdir(parents=True)
        run = vb/'s1b/run2'; run.mkdir(parents=True); (run/'queue').mkdir(); (run/'claimed').mkdir()
        (vb/'s1b/settings.json').write_text(json.dumps({'settings': [], 'metric_sha256': 'metric', 'runner_sha256': 'runner'}))
        (vb/'s1b/p3_metric.json').write_text('{}')
        bin_ = d/'bin'; bin_.mkdir(); executable(bin_/'python', script)
        (k/'env.sh').write_text(f'export PATH="{bin_}:$PATH"\ncd "$VBASE/src"\n')
        env = dict(os.environ, VBASE=str(vb), OUTDIR='run2', SETTINGS='settings.json', WAVE='W1')
        procs = {tag: subprocess.Popen(['bash', str(K/'s1b_collect.pbs')], env=dict(env, TAG=tag),
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for tag in ('W1_b', 'W1_c')}
        result = {}
        for tag, p in procs.items():
            stdout, stderr = p.communicate(timeout=15)
            tar = run/f'{tag}.tar.gz'
            names = subprocess.run(['tar', '-tzf', str(tar)], capture_output=True, text=True)
            summary = subprocess.run(['tar', '-xOf', str(tar), f'collect_{tag}.json'], capture_output=True, text=True)
            check = subprocess.run(['sha256sum', '-c', f'{tag}.tar.gz.sha256'], cwd=run, capture_output=True, text=True)
            result[tag] = {'rc': p.returncode, 'stdout': stdout, 'stderr': stderr, 'archive_members': names.stdout.splitlines(),
                           'summary_tag': json.loads(summary.stdout)['tag'] if summary.returncode == 0 else None,
                           'checksum_rc': check.returncode}
            assert p.returncode == 0 and check.returncode == 0 and result[tag]['summary_tag'] == tag, result[tag]
            assert names.stdout.splitlines() == [f'collect_{tag}.json', f'collect_{tag}.log'], result[tag]
        return result


checksum = checksum_failure()
assert checksum['result']['rc'] != 0 and checksum['jobs_created'] == 0 and not checksum['changed_runner_installed'], checksum
assert len(checksum['ledger']) == 1, checksum
out = {'scope': 'Actual repaired shell scripts and literal/extracted Python bodies with explicit native-science and seed stubs; no live PBS.',
       'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
       'source_sha256': {str(p.relative_to(ROOT)): sha(p) for p in [P3] + [K/n for n in
           ('s1b_round2_dispatch.sh', 's1b_submit.sh', 's1b_collect.pbs')]},
       'checksum_failure': checksum, 'gate': gate_tests(), 'dispatch': dispatch_tests(),
       'existing_settings_mismatch': existing_settings_mismatch(), 'topup': topup_tests(),
       'collector_race': collector_race(), 'supplied_submit_fixture': supplied_fixture('bash')}
assert out['supplied_submit_fixture']['all_ok'], out['supplied_submit_fixture']
(OUT/'evidence.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps({'gate_cases': len(out['gate']), 'gate_refusals': sum(v['rc'] != 0 for v in out['gate'].values()),
                  'checksum_fail_closed': True, 'dispatch_resume': True, 'topup_binding': True,
                  'concurrent_collector_archives': out['collector_race'], 'supplied_submit_fixture': True}, indent=2))
