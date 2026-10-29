"""Recheck exact successor recovery, including a failed held-intent publication."""
import contextlib
import errno
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import time
from unittest import mock


ROOT = Path(__file__).resolve().parents[3]
PRIOR = ROOT / "analysis/astra/r3_recovery_review_20261027/reproduce_recovery_gaps.py"
spec = importlib.util.spec_from_file_location("prior_recovery", PRIOR)
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
p3, p2 = prior.p3, prior.p2


class Crash(BaseException):
    pass


def collect(settings, metric, run):
    output = run / "review_collect.json"
    with contextlib.redirect_stdout(io.StringIO()):
        p3.collect(str(settings), str(metric), str(run), "W1", str(output))
    return json.loads(output.read_text()), (run / "lib/s00007.jsonl").read_bytes()


def serial(base):
    settings, metric, run, _, _ = prior.make(base, max_inflight=1)
    with mock.patch.object(p2, "one_batch", prior.fake_batch):
        p3.work(str(settings), str(metric), str(run), "W1", "serial[0].srv.0",
                time.time() + 30, qstat=str(base / "qstat"), des={})
    summary, library = collect(settings, metric, run)
    assert summary["collection_ok"] and summary["open_executions"] == 0
    return library


def case(base, side, fail_intent, reference):
    settings, metric, run, st, sdir = prior.make(base, max_inflight=1)
    predecessor = "job[0].kunanyi-ohpc.0r0nabc"
    successor = "job[0].kunanyi-ohpc.0r1nabc"
    held_path = run / "workers/held" / predecessor
    ticket = next((run / "queue").iterdir()).name
    a = p3.parse_ticket(ticket)[2]
    real_settle, real_unlock, real_atomic, real_replace = p3.settle, p3.unlock, p2.atomic_json, p2.os.replace
    crashed, held_writes = [], []

    def intent_write(obj, path):
        if Path(path) == held_path:
            held_writes.append(dict(obj))
            if fail_intent and len(held_writes) == 1:
                def fail_replace(src, dst):
                    if Path(dst) == held_path:
                        raise OSError(errno.ESTALE, "injected rename failure before held-intent publication")
                    return real_replace(src, dst)
                with mock.patch.object(p2.os, "replace", fail_replace):
                    return real_atomic(obj, path)
        return real_atomic(obj, path)

    def crash_settle(src, dst):
        if side == "after":
            real_settle(src, dst)
        crashed.append(1)
        raise Crash(f"after execution creation, {side} hint settlement")

    def unlock_unless_crashed(lock):
        if not crashed:
            return real_unlock(lock)

    with mock.patch.object(p2, "atomic_json", intent_write), \
            mock.patch.object(p3, "settle", crash_settle), \
            mock.patch.object(p3, "unlock", unlock_unless_crashed), \
            mock.patch.object(p3, "PARK_SECS", 0.0), \
            mock.patch.object(p3, "BACKOFF_SECS", 0.0):
        try:
            p3.work(str(settings), str(metric), str(run), "W1", predecessor,
                    time.time() + 30, qstat=str(base / "qstat"), des={})
        except Crash:
            pass
    before = p3.execution(str(sdir), a)
    assert crashed == [1] and before[1] and before[2] is None
    assert p3._owner(str(sdir / "lock"))["owner"] == predecessor
    prior.write_certificate(run, predecessor)
    with mock.patch.object(p3, "ls", lambda path: []):
        result = p3.work(str(settings), str(metric), str(run), "W1", successor,
                         time.time() + 30, qstat=str(base / "qstat"), des={})
    after = p3.execution(str(sdir), a)
    closed = after[2] is not None
    output = {
        "crash_side": side,
        "initial_intent_write_failed": fail_intent,
        "held_write_attempts_before_crash": len(held_writes),
        "held_file_exists_at_crash": held_path.exists(),
        "exact_owner_certificate_present": p3.certified(str(run / "workers/dead"), {"owner": predecessor}),
        "lock_left_held": True,
        "open_execution_before_successor": True,
        "successor_predecessor_recovered": result["predecessor_recovered"],
        "open_execution_after_successor": not closed,
        "gap_reproduced": not held_path.exists() and not closed and result["predecessor_recovered"] == 0,
    }
    if closed:
        with mock.patch.object(p2, "one_batch", prior.fake_batch):
            later = p3.work(str(settings), str(metric), str(run), "W1", "later[0].srv.0",
                            time.time() + 30, qstat=str(base / "qstat"), des={})
        summary, library = collect(settings, metric, run)
        output.update(collection_ok=summary["collection_ok"],
                      serial_library_equal=library == reference,
                      final_open_executions=summary["open_executions"],
                      superseded=result["superseded"] + later["superseded"])
    return output


def main():
    with mock.patch.object(p3, "K", 25), mock.patch.object(p3, "BATCH", 10), \
            mock.patch.object(p3, "RETRY_SECS", 0.0):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reference = serial(root / "serial")
            checks = [case(root / f"{side}_{fault}", side, fault, reference)
                      for fault in (False, True) for side in ("before", "after")]
    for c in checks:
        if c["initial_intent_write_failed"]:
            assert c["gap_reproduced"] and c["held_write_attempts_before_crash"] == 1
        else:
            assert c["held_file_exists_at_crash"] and c["successor_predecessor_recovered"] == 1
            assert c["serial_library_equal"] and c["collection_ok"]
            assert c["final_open_executions"] == 0 and c["superseded"] == 0
    result = {
        "runner_sha256": hashlib.sha256(Path(p3.__file__).read_bytes()).hexdigest(),
        "runtime": p2.runtime(),
        "cases": checks,
        "all_expected_observations_confirmed": True,
        "limits": "Tiny deterministic batches; actual atomic_json reaches os.replace, injected ESTALE prevents that held-intent rename; process death injected; all listings hidden only for exact successor. No actual NFS or PBS use.",
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    Path(__file__).with_name("recovery_closure_checks.json").write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
