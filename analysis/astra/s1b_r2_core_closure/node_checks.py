"""Actual repaired node script with bounded synthetic worker processes.

Identity replay uses the real lock/reclaim functions. Exit-75 recovery executes
the actual runner __main__ dispatch and work/storage functions with a synthetic
batch, and skips only the numerical-runtime/source-binding import check.
"""
from helpers import *

NODE = ROOT / 'analysis/fable/calibration/kunanyi/s1b_node.pbs'


def worker():
    state = Path(os.environ['AUDIT_STATE']); owner = sys.argv[-2]
    with (state / 'owners.jsonl').open('a') as fh:
        fh.write(json.dumps({'owner': owner, 'pid': os.getpid()}) + '\n')
    mode = os.environ['AUDIT_MODE']
    if mode == 'exit': return
    p, p2, clock = modules(); p.time = time; p2.time = time
    sd = Path(os.environ['AUDIT_SDIR']); run = sd.parents[1]
    if mode == 'hold':
        L = p.lock(str(sd), owner)
        (state / 'ready.json').write_text(json.dumps({'owner': owner, 'pid': os.getpid(), 'token': L[1]}))
        until = time.time() + 10
        while not (state / 'release').exists() and time.time() < until: time.sleep(.02)
        p.unlock(L); (state / 'released').touch(); return
    p2.one_batch = fake_batch(p2); p2.designs = lambda: {}
    p.check = lambda sp, mp: json.loads(Path(sp).read_text())
    flag = state / 'fault_injected'
    def faulty_release(src, dst):
        if str(src) == str(sd / 'lock') and '.rel.' in str(dst) and not flag.exists():
            flag.touch()
            if mode == 'release_after_apply': os.rename(src, dst)
            raise OSError(errno.ESTALE, 'single audit release failure')
        return os.rename(src, dst)
    p.os = proxy_os(rename=faulty_release)
    p.sys = types.SimpleNamespace(argv=[str(P3), 'work', str(run.parent / 'settings.json'),
                  str(run.parent / 'metric.json'), str(run), 'W1', owner, str(time.time() + 20)],
                  stderr=sys.stderr, exit=sys.exit)
    p.__dict__['__name__'] = '__main__'
    dispatch = [n for n in ast.parse(P3.read_text()).body if isinstance(n, ast.If)][-1]
    exec(compile(ast.Module(body=[dispatch], type_ignores=[]), str(P3), 'exec'), p.__dict__)


def setup(d):
    base = d / 'base'; run = base / 's1b/run'; state = d / 'state'; state.mkdir()
    (run / 'sets/s00007').mkdir(parents=True); (run / 'submit_W1/logs').mkdir(parents=True)
    envfile = base / 'src/analysis/fable/calibration/kunanyi/env.sh'
    envfile.parent.mkdir(parents=True); envfile.write_text('cd "$VBASE/src"\n')
    bindir = d / 'bin'; bindir.mkdir()
    stub = bindir / 'python'
    stub.write_text('#!/bin/sh\nexec /usr/bin/python3 "$AUDIT_SCRIPT" worker "$@"\n'); stub.chmod(0o755)
    env = os.environ | {'VBASE': str(base), 'SETTINGS': 'unused.json', 'OUTDIR': 'run',
           'WAVE': 'W1', 'TAG': 'W1', 'JOBCPUS': '1', 'WALL_SECS': '3600',
           'PBS_JOBID': 'same[0].fixture', 'PBS_ARRAY_INDEX': '0',
           'PATH': str(bindir) + os.pathsep + os.environ['PATH'],
           'AUDIT_SCRIPT': str(Path(__file__).resolve()), 'AUDIT_STATE': str(state),
           'AUDIT_SDIR': str(run / 'sets/s00007')}
    return run, state, env


def node(env, mode):
    return subprocess.Popen(['bash', str(NODE)], env=env | {'AUDIT_MODE': mode},
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def cert(run, owner): return json.loads((run / 'workers/dead' / owner).read_text())


if len(sys.argv) > 1 and sys.argv[1] == 'worker':
    worker()
else:
    results = {'scope': __doc__, 'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
               'source_sha256': {'p3': hashlib.sha256(P3.read_bytes()).hexdigest(),
                                  'node': hashlib.sha256(NODE.read_bytes()).hexdigest()}, 'cases': {}}
    with tempfile.TemporaryDirectory(prefix='s1b-r2-node-closure-') as tmpname:
        tmp = Path(tmpname); d = tmp / 'identity'; d.mkdir(); run, state, env = setup(d)
        first = node(env, 'exit'); first.communicate(timeout=10); assert first.returncode == 0
        first_owner = json.loads((state / 'owners.jsonl').read_text().splitlines()[0])
        c1 = cert(run, first_owner['owner'])
        assert (c1['pid'], c1['host'], c1['rc']) == (first_owner['pid'], os.uname().nodename, 0)
        second = node(env, 'hold')
        try:
            until = time.time() + 10
            while not (state / 'ready.json').exists() and time.time() < until: time.sleep(.02)
            ready = json.loads((state / 'ready.json').read_text()); p, _, _ = modules(); p.time = time
            info = p._owner(str(run / 'sets/s00007/lock')); certdir = str(run / 'workers/dead')
            assert ready['owner'] != first_owner['owner']
            assert ready['owner'].rsplit('.', 1)[0] == 'same[0].fixture'
            assert not p.owner_dead(info, cert=certdir, pbs=False)
            # Stronger control: even copying an old pid under the new owner name fails.
            (run / 'workers/dead' / ready['owner']).write_text(json.dumps(c1 | {'owner': ready['owner']}))
            assert not p.certified(certdir, info)
            try:
                p.lock(str(run / 'sets/s00007'), 'thief[0].fixture.0r0nother', patience=.5)
                raise AssertionError('live lock stolen')
            except p.LockBusy: pass
            assert p.pid_alive(ready['pid']) and p._owner(str(run / 'sets/s00007/lock'))['token'] == ready['token']
            (state / 'release').touch(); second.communicate(timeout=10)
            assert second.returncode == 0 and (state / 'released').exists()
            c2 = cert(run, ready['owner'])
            assert (c2['pid'], c2['host'], c2['rc']) == (ready['pid'], os.uname().nodename, 0)
            results['cases']['same_job_rerun'] = {'first_owner': first_owner, 'second_owner': ready,
                'first_certificate': c1, 'second_certificate': c2, 'live_lock_preserved': True,
                'same_name_wrong_pid_certificate_rejected': True, 'node_exit_codes': [first.returncode, second.returncode]}
        finally:
            (state / 'release').touch()
            if second.poll() is None: second.terminate(); second.wait(timeout=10)

        for mode in ('release_before_apply', 'release_after_apply'):
            d = tmp / mode; d.mkdir(); run, state, env = setup(d)
            p, p2, clock = modules()
            scratch, seeded_run, sd, st, b, sp, mp = make(tmp, mode + '_seed', p)
            # Only the fixture setup is copied; the runner receives its expected tree.
            shutil.copytree(seeded_run, run, dirs_exist_ok=True)
            shutil.copy2(sp, run.parent / 'settings.json'); shutil.copy2(mp, run.parent / 'metric.json')
            proc = node(env, mode)
            try:
                stdout, stderr = proc.communicate(timeout=35)
                owners = [json.loads(x) for x in (state / 'owners.jsonl').read_text().splitlines()]
                cs = [cert(run, x['owner']) for x in owners]
                log = (run / 'submit_W1/logs/w.0.0.log').read_text()
                assert proc.returncode == 0 and len(owners) == 2
                assert [c['rc'] for c in cs] == [75, 0]
                assert [c['pid'] for c in cs] == [x['pid'] for x in owners]
                assert 'owner uncertain, ending:' in log and 'exited 75' in log
                assert p.terminal(str(run / 'sets/s00007')) == 'COMPLETE'
                assert not os.listdir(run / 'claimed') and not (run / 'sets/s00007/lock').exists()
                results['cases'][mode] = {'node_exit': proc.returncode, 'certificates': cs,
                    'terminal': 'COMPLETE', 'claims': [], 'lock_left': False,
                    'original_processes_reaped': all(not p.pid_alive(x['pid']) for x in owners),
                    'worker_log': log}
            finally:
                if proc.poll() is None: proc.terminate(); proc.wait(timeout=10)
    results['all_assertions_passed'] = True
    results['timestamp'] = datetime.now(ZoneInfo('Australia/Hobart')).isoformat()
    (OUT / 'node_checks.json').write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps(results, indent=2))
