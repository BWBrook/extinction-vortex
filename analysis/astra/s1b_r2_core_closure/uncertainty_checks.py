"""Bounded inspection of uncertainty limits, beyond the five original replays.

These checks record outcomes, not an assertion of launch readiness. Both use
actual ownership code with targeted transient NFS faults and a logical clock.
"""
from helpers import *

result = {'scope': __doc__, 'source_sha256': hashlib.sha256(P3.read_bytes()).hexdigest(), 'cases': {}}
with tempfile.TemporaryDirectory(prefix='s1b-r2-uncertainty-') as td:
    tmp = Path(td)
    p, p2, clock = modules(); d, run, sd, st, b, sp, mp = make(tmp, 'reclaimer', p)
    old = {'owner': 'old[0].fixture.0r0nold', 'host': 'elsewhere', 'pid': 1, 'token': 'old-token'}
    (sd / 'lock').mkdir(); (sd / 'lock/owner.json').write_text(json.dumps(old))
    (run / 'workers/dead' / old['owner']).write_text(json.dumps(old | {'rc': 75}))
    fired = []
    def ambiguous_reclaimer(src, dst):
        if str(dst) == str(sd / 'lock.reclaim') and '.new.' in str(src) and not fired:
            os.rename(src, dst); fired.append(True); raise OSError(errno.ESTALE, 'reclaimer published, reply lost')
        return os.rename(src, dst)
    p.os = proxy_os(rename=ambiguous_reclaimer); start = clock.now
    try:
        p.lock(str(sd), 'retry[0].fixture.0r0nnew', patience=5, deadline=start + 10)
        outcome = 'acquired'
    except p.LockBusy:
        outcome = 'LockBusy'
    reclaimer = p._owner(str(sd / 'lock.reclaim'))
    assert outcome == 'LockBusy' and reclaimer['pid'] == os.getpid()
    # Model the node certificate after the process ends; invoke only _reclaim
    # to check the documented fail-closed branch, never remove the mutex.
    (run / 'workers/dead' / reclaimer['owner']).write_text(json.dumps(reclaimer | {'rc': 75}))
    try:
        p._reclaim(str(sd / 'lock'), old, dict(reclaimer, owner='another[0].fixture.0r0n3', token='next'),
                   cert=str(run / 'workers/dead'))
        after_cert = 'reclaimed'
    except p.LockStale:
        after_cert = 'LockStale'
    assert after_cert == 'LockStale'
    result['cases']['ambiguous_reclaimer_publication'] = {
        'faults_injected': len(fired), 'initial_outcome': outcome,
        'logical_elapsed_seconds': clock.now - start, 'after_owner_certified': after_cert,
        'scope': 'known manual-recovery boundary; no second holder or lost claim'}

    # A reply-lost primary publication plus a bounded unreadable-owner burst.
    # The burst ends after eight logical seconds; it exceeds five-second claim
    # patience. Subsequent invocations have lost the first acquisition token.
    p, p2, clock = modules(); d, run, sd, st, b, sp, mp = make(tmp, 'read_burst', p)
    p2.one_batch = fake_batch(p2); fired = []; reads = []; start = clock.now
    def ambiguous_lock(src, dst):
        if str(dst) == str(sd / 'lock') and '.new.' in str(src) and not fired:
            os.rename(src, dst); fired.append(True); raise OSError(errno.ESTALE, 'lock published, reply lost')
        return os.rename(src, dst)
    original_read = p._jread
    def temporarily_unreadable(path):
        if str(path) == str(sd / 'lock/owner.json') and clock.now < start + 8:
            reads.append(clock.now); raise OSError(errno.ESTALE, 'temporary unreadable published lock')
        return original_read(path)
    p.os = proxy_os(rename=ambiguous_lock); p._jread = temporarily_unreadable
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        receipt = p.work(str(sp), str(mp), str(run), 'W1', 'reader[0].fixture.0r0nnew', start + 30, des={})
    owner = p._owner(str(sd / 'lock'))
    assert len(fired) == 1 and owner['owner'] == 'reader[0].fixture.0r0nnew'
    assert not p.owner_dead(owner, cert=str(run / 'workers/dead'), pbs=False)
    assert p.terminal(str(sd)) is None and len(os.listdir(run / 'queue')) == 1
    result['cases']['ambiguous_primary_publication_and_read_burst'] = {
        'rename_faults': len(fired), 'read_faults': len(reads), 'read_burst_seconds': 8,
        'worker_budget_seconds': 30, 'logical_elapsed_seconds': clock.now - start,
        'receipt': receipt, 'terminal': p.terminal(str(sd)), 'queue_count': len(os.listdir(run / 'queue')),
        'lock_still_owned_by_live_worker': True, 'diagnostic': err.getvalue(),
        'scope': 'combined ambiguous-acquire and owner-read outage; single-rename case passes separately'}
result['timestamp'] = datetime.now(ZoneInfo('Australia/Hobart')).isoformat()
(OUT / 'uncertainty_checks.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
