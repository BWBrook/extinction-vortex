"""Original failure sequences replayed on final code, with new JSON certificates.

The recovery timeout fixture advances a logical clock at the held boundary.
All other lock paths and worker storage use unchanged AST-loaded source.
"""
from helpers import *


def certificate(run, owner, host='elsewhere', pid=1, rc=75):
    (run / 'workers/dead' / owner).write_text(json.dumps(
        {'owner': owner, 'host': host, 'pid': pid, 'rc': rc}))


def busy_queue(tmp, name, p, count=6):
    run = tmp / name
    for path in ('queue', 'claimed', 'sets', 'workers/dead'):
        (run / path).mkdir(parents=True, exist_ok=True)
    for i in range(count + 1):
        sd = run / 'sets' / f's{i:05d}'; sd.mkdir()
        if i < count:
            (sd / 'lock').mkdir()
            (sd / 'lock/owner.json').write_text(json.dumps(
                {'owner': f'ghost[{i}].elsewhere.0r0nold', 'host': 'elsewhere',
                 'pid': 1, 'token': f'ghost-{i}'}))
        for j in range(28 if i < count else 1):
            (run / 'queue' / f'W1_0000001_s{i:05d}_{j:09d}_{j + 1:09d}').touch()
    return run, f'W1_0000001_s{count:05d}_000000000_000000001'


result = {'scope': __doc__, 'commit': subprocess.check_output(
    ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'source_sha256': {'p2': hashlib.sha256(P2.read_bytes()).hexdigest(),
                      'p3': hashlib.sha256(P3.read_bytes()).hexdigest()}, 'cases': {}}
cases = result['cases']
with tempfile.TemporaryDirectory(prefix='s1b-r2-closure-') as tmpname:
    tmp = Path(tmpname)
    p, p2, clock = modules(); d, run, sd, st, b, sp, mp = make(tmp, 'control', p)
    p2.one_batch = fake_batch(p2)
    receipt = p.work(str(sp), str(mp), str(run), 'W1', 'control[0].fixture.0r0nnew', clock.now + 15, des={})
    assert p.terminal(str(sd)) == 'COMPLETE' and not os.listdir(run / 'claimed')
    cases['normal_worker_control'] = {'receipt': receipt, 'terminal': p.terminal(str(sd))}

    # Original single failed unlock; the intended outcome is now process escape.
    p, p2, clock = modules(); d, run, sd, st, b, sp, mp = make(tmp, 'unlock', p)
    p2.one_batch = fake_batch(p2); fired = []; owner = 'unlock[0].fixture.0r0nnew'
    def failed_unlock(src, dst):
        if str(src) == str(sd / 'lock') and '.rel.' in str(dst) and not fired:
            fired.append(True); raise OSError(errno.ESTALE, 'one release failure')
        return os.rename(src, dst)
    p.os = proxy_os(rename=failed_unlock); start = clock.now
    try:
        p.work(str(sp), str(mp), str(run), 'W1', owner, clock.now + 15, des={})
        raise AssertionError('uncertain owner returned normally')
    except p.OwnerUncertain as ex:
        cases['single_unlock_failure_ends_worker'] = {
            'exception': type(ex).__name__, 'elapsed_seconds': clock.now - start,
            'claims_preserved': len(os.listdir(run / 'claimed')),
            'owned_lock_preserved': p._owner(str(sd / 'lock'))['owner'] == owner}
    assert len(fired) == 1 and clock.now - start == 0
    assert len(os.listdir(run / 'claimed')) == 1

    # Original blocked frontier: all six settings remain unavailable.
    p, p2, clock = modules(); run, healthy = busy_queue(tmp, 'busy', p)
    start = clock.now
    got = p.claim(str(run), 'reader[0].fixture.0r0nnew', 'W1', qstat='/bin/false', deadline=start + 60)
    assert got == healthy
    cases['busy_frontier_reaches_healthy_setting'] = {'ticket': got, 'logical_elapsed_seconds': clock.now - start}

    # Same busy frontier with too little time: no new claim after deadline.
    p, p2, clock = modules(); run, healthy = busy_queue(tmp, 'busy_deadline', p)
    start = clock.now
    try:
        p.claim(str(run), 'reader[0].fixture.0r0nnew', 'W1', qstat='/bin/false', deadline=start + 2)
        raise AssertionError('claim should stop at deadline')
    except p.LockBusy:
        pass
    assert clock.now - start <= 2.15 and not os.listdir(run / 'claimed')
    cases['claim_deadline'] = {'logical_elapsed_seconds': clock.now - start, 'claims': []}

    # Original 392-claim recovery, adapted only for JSON cert / deadline arg.
    p, p2, clock = modules(); d, run, sd, st, b, sp, mp = make(tmp, 'recovery', p)
    for path in (run / 'queue').iterdir(): path.unlink()
    ended = 'ended[0].fixture.0r0nold'; certificate(run, ended)
    for i in range(14):
        for j in range(28):
            (run / 'claimed' / f'W1_0000001_s{i:05d}_{j:09d}_{j + 1:09d}@{ended}').touch()
    waits = []
    @contextlib.contextmanager
    def timeout_context(sdir, owner, qstat, patience, deadline):
        waits.append({'start': clock.now, 'patience': patience, 'deadline': deadline})
        clock.sleep(min(patience, max(0., deadline - clock.now)))
        raise p.LockBusy('fixture live-owner wait')
        yield
    p.held = timeout_context; start = clock.now; deadline = start + 60
    with contextlib.redirect_stderr(io.StringIO()):
        receipt = p.work(str(sp), str(mp), str(run), 'W1', 'new[0].fixture.0r0nnew', deadline, des={})
    cases['recovery_stops_at_deadline'] = {
        'claims_total': 392, 'waits': len(waits), 'elapsed_seconds': clock.now - start,
        'waits_started_after_deadline': sum(x['start'] >= deadline for x in waits),
        'claims_preserved': len(os.listdir(run / 'claimed')), 'receipt': receipt,
        'injection_boundary': 'held context reports normal five-second live-owner timeout'}
    assert len(waits) == 12 and clock.now == deadline and len(os.listdir(run / 'claimed')) == 392

    # Positive PBS control and original uncached-exception sequence.
    p, p2, clock = modules(); info = {'owner': 'job[0].fixture.0r0nnew', 'host': 'elsewhere'}
    calls = []
    def live_query(*args, **kwargs):
        calls.append(clock.now); return types.SimpleNamespace(stdout='    job_state = R\n', returncode=0)
    p.subprocess = types.SimpleNamespace(run=live_query)
    for _ in range(4):
        assert not p.owner_dead(info); clock.sleep(60.)
    assert len(calls) == 1
    cases['pbs_live_cache_control'] = {'queries': list(calls)}
    p._PBS.clear(); calls.clear(); start = clock.now
    def timed_out(*args, **kwargs):
        calls.append({'start': clock.now, 'timeout': kwargs['timeout']})
        clock.sleep(kwargs['timeout']); raise subprocess.TimeoutExpired(args[0], kwargs['timeout'])
    p.subprocess = types.SimpleNamespace(run=timed_out)
    for _ in range(4): assert not p.owner_dead(info)
    assert len(calls) == 1 and clock.now - start == 60 and p._PBS
    cases['pbs_timeout_cached'] = {'queries': list(calls), 'elapsed_seconds': clock.now - start, 'cache': repr(p._PBS)}
    p._PBS.clear(); calls.clear(); start = clock.now
    for _ in range(4): assert not p.owner_dead(info, deadline=start + 1.5)
    assert len(calls) == 1 and calls[0]['timeout'] == 1.5 and clock.now - start == 1.5
    cases['pbs_timeout_deadline_clipped'] = {'queries': list(calls), 'elapsed_seconds': clock.now - start}

    # Newly declared uncertain-acquisition path: rename applies but reports ESTALE.
    p, p2, clock = modules(); d, run, sd, st, b, sp, mp = make(tmp, 'acquire', p)
    fired = []
    def uncertain_publish(src, dst):
        if str(dst) == str(sd / 'lock') and '.new.' in str(src) and not fired:
            os.rename(src, dst); fired.append(True); raise OSError(errno.ESTALE, 'rename applied, reply lost')
        return os.rename(src, dst)
    p.os = proxy_os(rename=uncertain_publish)
    L = p.lock(str(sd), 'acquire[0].fixture.0r0nnew', patience=5, deadline=clock.now + 5)
    assert p._owner(L[0])['token'] == L[1] and len(fired) == 1
    p.unlock(L); assert not (sd / 'lock').exists()
    cases['uncertain_acquire_recognised_by_token'] = {'faults_injected': 1, 'released': True}

    # Censoring at the sampling deadline can still commit under its bounded grace.
    p, p2, clock = modules(); d, run, sd, st, b, sp, mp = make(tmp, 'censored_commit', p)
    normal = fake_batch(p2, hits=0); start = clock.now; deadline = start + 1
    def deadline_batch(*args, **kwargs):
        clock.sleep(1.); return normal(*args, **kwargs)
    p2.one_batch = deadline_batch
    receipt = p.work(str(sp), str(mp), str(run), 'W1', 'censor[0].fixture.0r0nnew', deadline, des={})
    assert receipt['requeued_censored'] == 1 and not os.listdir(run / 'claimed')
    assert p.shard_state(str(sd), 0)['status'] == 'censored'
    cases['deadline_checkpoint_commit'] = {'receipt': receipt, 'elapsed_seconds': clock.now - start,
                                          'queue_count': len(os.listdir(run / 'queue'))}

result['all_assertions_passed'] = True
result['timestamp'] = datetime.now(ZoneInfo('Australia/Hobart')).isoformat()
(OUT / 'core_checks.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
