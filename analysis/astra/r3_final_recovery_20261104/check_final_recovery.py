"""Focused publication-error closure checks against the actual round-3 worker."""
import errno
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import time
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
OLD = ROOT / 'analysis/astra/r3_recovery_closure_20261029/check_recovery_closure.py'
spec = importlib.util.spec_from_file_location('closure', OLD)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
p3, p2, prior = c.p3, c.p2, c.prior


def assert_recovered(row):
    assert not row['gap_reproduced']
    assert row['held_file_exists_at_crash']
    assert row['successor_predecessor_recovered'] == 1
    assert row['serial_library_equal'] and row['collection_ok']
    assert row['final_open_executions'] == row['superseded'] == 0


def ambiguous_add(base, side, reference):
    real_atomic = p2.atomic_json
    faults = []

    def write_then_error(obj, path):
        result = real_atomic(obj, path)
        if '/workers/held/' in str(path) and obj.get('tickets') and not faults:
            faults.append(True)
            raise OSError(errno.EIO, 'injected ambiguous publication: rename already succeeded')
        return result

    with mock.patch.object(p2, 'atomic_json', write_then_error):
        row = c.case(base, side, False, reference)
    assert faults == [True]
    assert row['held_write_attempts_before_crash'] == 2
    assert_recovered(row)
    row['fault'] = 'first addition published, then EIO reported'
    return row


def permanent_add(base):
    settings, metric, run, st, sdir = prior.make(base, max_inflight=1)
    queued = sorted(p.name for p in (run / 'queue').iterdir())
    real_replace = p2.os.replace
    faults = []

    def never_publish(src, dst):
        if '/workers/held/' in str(dst):
            faults.append(True)
            raise OSError(errno.ESTALE, 'held record rename permanently fails')
        return real_replace(src, dst)

    with mock.patch.object(p2.os, 'replace', never_publish), mock.patch.object(p3, 'MAX_ERRORS', 3):
        try:
            p3.work(str(settings), str(metric), str(run), 'W1', 'permanent[0].srv.0',
                    time.time() + 30, qstat=str(base / 'qstat'), des={})
            raise AssertionError('worker should end on persistent publication failure')
        except OSError as exc:
            assert exc.errno == errno.ESTALE
    result = {'publication_attempts': len(faults), 'execution_files': len(list((sdir / 'x').iterdir())),
              'queue_unchanged': queued == sorted(p.name for p in (run / 'queue').iterdir()),
              'claim_hints': len(list((run / 'claimed').iterdir()))}
    assert result['publication_attempts'] >= 3
    assert result['execution_files'] == result['claim_hints'] == 0 and result['queue_unchanged']
    return result


def removal_error(base, ambiguous, reference):
    settings, metric, run, st, sdir = prior.make(base, max_inflight=1)
    real_atomic = p2.atomic_json
    failures, removals = [], []

    def remove_error(obj, path):
        if '/workers/held/' in str(path) and not obj.get('tickets'):
            removals.append(True)
            if not failures:
                if ambiguous:
                    real_atomic(obj, path)
                failures.append(True)
                raise OSError(errno.ESTALE, 'first removal fails after rename' if ambiguous else 'first removal fails before rename')
        return real_atomic(obj, path)

    with mock.patch.object(p2, 'atomic_json', remove_error), mock.patch.object(p2, 'one_batch', prior.fake_batch):
        out = p3.work(str(settings), str(metric), str(run), 'W1', 'remove[0].srv.0',
                      time.time() + 30, qstat=str(base / 'qstat'), des={})
    summary, library = c.collect(settings, metric, run)
    held = json.loads((run / 'workers/held/remove[0].srv.0').read_text())
    result = {'ambiguous': ambiguous, 'faults': len(failures), 'removal_attempts': len(removals),
              'transient_errors': out['transient_errors'], 'final_held_tickets': held['tickets'],
              'collection_ok': summary['collection_ok'], 'serial_library_equal': library == reference,
              'open_executions': summary['open_executions'], 'superseded': out['superseded']}
    assert result['faults'] == result['transient_errors'] == 1
    assert result['removal_attempts'] >= 2 and not result['final_held_tickets']
    assert result['collection_ok'] and result['serial_library_equal']
    assert result['open_executions'] == result['superseded'] == 0
    return result


def main():
    with mock.patch.object(p3, 'K', 25), mock.patch.object(p3, 'BATCH', 10), \
            mock.patch.object(p3, 'RETRY_SECS', 0.0), mock.patch.object(p3, 'PARK_SECS', 0.0), \
            mock.patch.object(p3, 'BACKOFF_SECS', 0.0), tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        reference = c.serial(root / 'serial')
        cases = [c.case(root / f'{side}_{fault}', side, fault, reference)
                 for fault in (False, True) for side in ('before', 'after')]
        for row in cases:
            assert_recovered(row)
            assert row['held_write_attempts_before_crash'] == (2 if row['initial_intent_write_failed'] else 1)
        ambiguous = [ambiguous_add(root / f'ambiguous_{side}', side, reference) for side in ('before', 'after')]
        permanent = permanent_add(root / 'permanent')
        removals = [removal_error(root / f'remove_{amb}', amb, reference) for amb in (False, True)]
    result = {'runner_sha256': hashlib.sha256(Path(p3.__file__).read_bytes()).hexdigest(), 'runtime': p2.runtime(),
              'original_four_cases': cases, 'ambiguous_addition_cases': ambiguous,
              'permanent_addition_failure': permanent, 'removal_error_cases': removals,
              'all_nine_checks_passed': True,
              'limits': 'Tiny deterministic batches, actual worker and atomic writer, injected exceptions and process death; no real NFS/PBS failure or scientific validation.'}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
