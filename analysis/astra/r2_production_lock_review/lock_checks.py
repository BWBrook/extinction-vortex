"""Production-lock classification and certificate/recovery checks, no NFS/PBS.

The observed kernel rename refusal is used directly. The EEXIST variant maps
that known refusal to the equivalent requested errno; it never performs a
successful contender publication. Logical time schedules the holder's normal
release just before the claimant's wait limit. All runner functions are the
unchanged current source, loaded by the existing bounded audit helper.
"""
from helpers import *


def certify(run, owner, pid, host=None):
    c = {'owner': owner, 'host': host or os.uname().nodename, 'pid': pid, 'rc': 75}
    (run / 'workers/dead' / owner).write_text(json.dumps(c))
    return c


result = {'scope': __doc__, 'commit': subprocess.check_output(
    ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'source_sha256': {'p3': hashlib.sha256(P3.read_bytes()).hexdigest(),
                      'node': hashlib.sha256((ROOT / 'analysis/fable/calibration/kunanyi/s1b_node.pbs').read_bytes()).hexdigest()},
    'cases': {}}
cases = result['cases']
with tempfile.TemporaryDirectory(prefix='r2-production-lock-') as td:
    tmp = Path(td)
    # Fixed randomness only controls the wait cadence; it does not alter code.
    for name, reported_errno, release_on_last_attempt in (
            ('known_live_owner_control', None, False),
            ('ordinary_enotempty_then_holder_release', None, True),
            ('ordinary_eexist_then_holder_release', errno.EEXIST, True)):
        p, _, clock = modules(); d, run, sd, st, b, sp, mp = make(tmp, name, p)
        p.random = types.SimpleNamespace(random=lambda: .61)
        foreign = p.lock(str(sd), 'foreign[0].fixture.0r0nforeign')
        start = clock.now; refusals = []; released = []; contender_successes = []
        original_rename = os.rename
        def checked_rename(src, dst):
            if str(dst) == str(sd / 'lock') and '.new.' in str(src):
                try:
                    value = original_rename(src, dst)
                    contender_successes.append(str(src)); return value
                except OSError as ex:
                    assert ex.errno in (errno.EEXIST, errno.ENOTEMPTY)
                    refusals.append({'at': clock.now - start, 'kernel_errno': ex.errno,
                                     'reported_errno': reported_errno or ex.errno})
                    if release_on_last_attempt and clock.now - start > 4.99 and not released:
                        p.unlock(foreign); released.append(clock.now - start)
                    if reported_errno is not None:
                        raise OSError(reported_errno, 'equivalent known contention refusal')
                    raise
            return original_rename(src, dst)
        p.os = proxy_os(rename=checked_rename)
        try:
            L = p.lock(str(sd), 'contender[0].fixture.0r0nnew', patience=p.CLAIM_PATIENCE,
                       deadline=start + 30)
            outcome = 'acquired'; p.unlock(L)
        except p.OwnerUncertain as ex:
            outcome = 'OwnerUncertain'; diagnostic = str(ex)
        except p.LockBusy as ex:
            outcome = 'LockBusy'; diagnostic = str(ex)
        expected = 'OwnerUncertain' if release_on_last_attempt else 'LockBusy'
        assert outcome == expected and not contender_successes
        assert bool(released) == release_on_last_attempt
        assert (sd / 'lock').exists() != release_on_last_attempt
        cases[name] = {'outcome': outcome, 'publication_successes': contender_successes,
            'refusals': len(refusals), 'kernel_errnos': sorted({x['kernel_errno'] for x in refusals}),
            'reported_errnos': sorted({x['reported_errno'] for x in refusals}),
            'last_refusal_at_seconds': refusals[-1]['at'], 'holder_released_at_seconds': released,
            'elapsed_seconds': clock.now - start, 'lock_exists_at_exit': (sd / 'lock').exists(),
            'diagnostic': diagnostic, 'nfs_or_read_fault_injected': False}
        if not release_on_last_attempt: p.unlock(foreign)

    # The same ordinary disappearance well before the patience boundary heals.
    p, _, clock = modules(); d, run, sd, st, b, sp, mp = make(tmp, 'early_release', p)
    foreign = p.lock(str(sd), 'foreign[0].fixture.0r0nforeign'); fired = []
    def early_release(src, dst):
        if str(dst) == str(sd / 'lock') and '.new.' in str(src) and not fired:
            try: return os.rename(src, dst)
            except OSError as ex:
                assert ex.errno in (errno.EEXIST, errno.ENOTEMPTY)
                fired.append(ex.errno); p.unlock(foreign); raise
        return os.rename(src, dst)
    p.os = proxy_os(rename=early_release); start = clock.now
    L = p.lock(str(sd), 'early[0].fixture.0r0nnew', patience=5)
    assert p._owner(L[0])['owner'] == 'early[0].fixture.0r0nnew'
    p.unlock(L)
    cases['ordinary_early_release_control'] = {'outcome': 'acquired_and_released', 'elapsed_seconds': clock.now - start}

    # A dead contender's claim certificate cannot authorize breaking a different
    # live lock. It permits claim recovery only once the setting lock is free.
    p, _, clock = modules(); d, run, sd, st, b, sp, mp = make(tmp, 'certificate', p)
    ticket = next((run / 'queue').iterdir()).name
    dead = 'dead[0].fixture.0r0ndead'
    os.rename(run / 'queue' / ticket, run / 'claimed' / f'{ticket}@{dead}')
    foreign = p.lock(str(sd), 'live[0].fixture.0r0nlive')
    info = p._owner(foreign[0]); certify(run, dead, 99999999)
    assert not p.owner_dead(info, cert=str(run / 'workers/dead'), pbs=False)
    start = clock.now; stderr = io.StringIO()
    with contextlib.redirect_stderr(stderr):
        first = p.recover_stale(str(run), 'rescuer[0].fixture.0r0nnew', 'W1', pbs=False, deadline=clock.now + 10)
    preserved = p._owner(foreign[0])['token'] == foreign[1]
    assert first == 0 and preserved and (run / 'claimed' / f'{ticket}@{dead}').exists()
    p.unlock(foreign)
    second = p.recover_stale(str(run), 'rescuer[0].fixture.0r0nnew', 'W1', pbs=False, deadline=clock.now + 10)
    assert second == 1 and not os.listdir(run / 'claimed') and (run / 'queue' / ticket).exists()
    cases['certificate_is_permission_not_proof_of_recovery'] = {
        'first_recovery_count': first, 'foreign_live_lock_preserved': preserved,
        'later_recovery_count_after_release': second, 'claimed_after': [],
        'queued_after': [ticket], 'elapsed_seconds': clock.now - start,
        'initial_recovery_diagnostic': stderr.getvalue(),
        'certificate_scope': 'synthetic ended-owner claim; no live production certificate audit'}

result['all_assertions_passed'] = True
result['timestamp'] = datetime.now(ZoneInfo('Australia/Hobart')).isoformat()
(OUT / 'lock_checks.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
