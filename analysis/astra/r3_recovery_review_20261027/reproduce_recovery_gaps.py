"""Focused round-3 recovery/collector counterexamples for p3_stage1b.py."""
import hashlib
import contextlib
import io
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "analysis/fable/calibration/v2_dev"
sys.path.insert(0, str(SRC))
import p3_stage1b as p3  # noqa: E402
import p2_stage1a as p2  # noqa: E402


def make(base, rate=0.05, cap=400, max_inflight=2):
    base = Path(base)
    base.mkdir(parents=True, exist_ok=True)
    settings = base / "settings.json"
    metric = base / "metric.json"
    metric.write_text(json.dumps({
        "outers": {"synthetic|toy/0": {"recorded": [5, 4, 0], "q": [], "radius": 1.0}},
        "pops": {"synthetic": {"keep": [], "mad": []}},
    }))
    st = {
        "index": 7, "pop": "synthetic", "outer": "toy/0", "n": 30,
        "E": {"n": 30, "k": 1, "r": 1, "rate": rate},
        "rate": p3.BATCH / 3600 / 0.05, "cap_batches": cap,
        "prior_hpb": 0.5 * p3.BATCH * 0.05, "wave": "W1", "dir": "s00007",
        "library": "primary", "stream_tag": 2, "pilot": None,
    }
    bundle = {
        "settings": [st], "metric_sha256": "m", "runner_sha256": "r",
        "min_shard_cpu_h": 0.0, "target_wall_h": 1e-6,
        "max_inflight": max_inflight, "overshoot": p3.OVERSHOOT,
    }
    settings.write_text(json.dumps(bundle))
    run = base / "run"
    for rel in ("queue", "claimed", "sets/s00007", "lib", "workers"):
        (run / rel).mkdir(parents=True, exist_ok=True)
    sdir = run / "sets/s00007"
    with p3.held(str(sdir), "seed", str(base / "qstat")):
        p3.plan(st, str(sdir), str(run), bundle, "seed")
    return settings, metric, run, st, sdir


def fake_batch(st, mp, batch, n, des):
    keys = (
        "poisson_accept", "theta_accept", "paths", "selected_SA", "overflow",
        "hits", "boundary", "hits_lo", "hits_hi", "rounding_excess",
    )
    ans = {k: 0 for k in keys}
    ans["proposals"] = n
    ans["hit_records"] = []
    for j in range(n):
        u = int(hashlib.sha256(f"{st.get('stream_tag', 2)}/{st['index']}/{batch}/{j}".encode()).hexdigest()[:8], 16) / 2**32
        if u < st["E"].get("rate", 0.05):
            ans["hit_records"].append({
                "batch": batch, "proposal_in_batch": j, "boundary": False,
                "theta": {k: 0.5 for k in p2.PARAMS}, "recorded": [4, 3, 0],
            })
    hits = len(ans["hit_records"])
    ans.update(poisson_accept=n, theta_accept=n, paths=n, selected_SA=hits,
               hits=hits, hits_lo=hits, hits_hi=hits)
    return ans


def write_certificate(run, owner):
    path = Path(run) / "workers/dead" / owner
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "owner": owner, "host": os.uname().nodename, "pid": os.getpid(), "rc": 137,
    }))


def pre_hold_crash_with_omitted_hints(base):
    settings, metric, run, st, sdir = make(base)
    predecessor = "job[0].kunanyi-ohpc.0r0nabc"
    successor = "job[0].kunanyi-ohpc.0r1nabc"
    real_settle = p3.settle
    fired = []

    def crash_after_settle(src, dst):
        real_settle(src, dst)
        fired.append((src, dst))
        raise KeyboardInterrupt("killed after execution creation and hint settlement")

    with mock.patch.object(p3, "settle", crash_after_settle):
        try:
            p3.work(str(settings), str(metric), str(run), "W1", predecessor,
                    time.time() + 60, qstat=str(Path(base) / "qstat"), des={})
        except KeyboardInterrupt:
            pass
    tickets = sorted((run / "claimed").iterdir())
    ticket = tickets[0].name.split("@", 1)[0]
    a = p3.parse_ticket(ticket)[2]
    before = p3.execution(str(sdir), a)
    held_path = run / "workers/held" / predecessor
    write_certificate(run, predecessor)
    real_ls = p3.ls

    def omit_hint_directories(path):
        if os.path.normpath(path) in (os.path.normpath(run / "queue"), os.path.normpath(run / "claimed")):
            return []
        return real_ls(path)

    with mock.patch.object(p3, "ls", omit_hint_directories):
        done = p3.work(str(settings), str(metric), str(run), "W1", successor,
                       time.time() + 60, qstat=str(Path(base) / "qstat"), des={})
    after = p3.execution(str(sdir), a)
    return {
        "transition_reached": len(fired) == 1,
        "execution_open_before_successor": before[1] is not None and before[2] is None,
        "predecessor_held_record_exists": held_path.exists(),
        "successor_predecessor_recovered": done["predecessor_recovered"],
        "execution_open_after_successor": after[1] is not None and after[2] is None,
        "claim_hint_still_exists_but_was_omitted": len(list((run / "claimed").iterdir())) == 1,
        "queue_hints_visible_after_mock": len(list((run / "queue").iterdir())),
        "gap_reproduced": (
            len(fired) == 1 and before[1] is not None and before[2] is None
            and not held_path.exists() and done["predecessor_recovered"] == 0
            and after[1] is not None and after[2] is None
        ),
    }


def collector_accepts_terminal_with_open_execution(base):
    settings, metric, run, st, sdir = make(base, rate=1.0, max_inflight=2)
    tickets = sorted(p.name for p in (run / "queue").iterdir())
    assert len(tickets) >= 2
    later = max(tickets, key=lambda t: p3.parse_ticket(t)[2])
    earlier = min(tickets, key=lambda t: p3.parse_ticket(t)[2])
    open_k = p3.take(str(run), later, "jobB[0].srv.0", qstat=str(Path(base) / "qstat"))
    with mock.patch.object(p2, "one_batch", fake_batch):
        p3.work(str(settings), str(metric), str(run), "W1", "jobA[0].srv.0",
                time.time() + 60, qstat=str(Path(base) / "qstat"), des={})
    out = run / "collect_probe.json"
    with contextlib.redirect_stdout(io.StringIO()):
        p3.collect(str(settings), str(metric), str(run), "W1", str(out))
    summary = json.loads(out.read_text())
    a = p3.parse_ticket(later)[2]
    execution = p3.execution(str(sdir), a)
    return {
        "earlier_ticket": earlier,
        "later_ticket": later,
        "later_execution_number": open_k,
        "terminal": p3.terminal(str(sdir)),
        "later_execution_still_open": execution[1] is not None and execution[2] is None,
        "collection_ok": summary["collection_ok"],
        "summary_open_executions": summary["open_executions"],
        "row_status": summary["rows"][0]["status"],
        "library_records": sum(1 for _ in open(run / "lib/s00007.jsonl", "rb")),
        "gap_reproduced": (
            p3.terminal(str(sdir)) == "COMPLETE"
            and execution[1] is not None and execution[2] is None
            and summary["collection_ok"] and summary["open_executions"] == 1
        ),
    }


def late_shared_file_writes_fail_closed(base):
    settings, metric, run, st, sdir = make(base, rate=1.0, max_inflight=1)
    with mock.patch.object(p2, "one_batch", fake_batch):
        p3.work(str(settings), str(metric), str(run), "W1", "jobA[0].srv.0",
                time.time() + 60, qstat=str(Path(base) / "qstat"), des={})
    checkpoint = sdir / "sh000000000.json"
    journal = sdir / "sh000000000_hits.jsonl"
    final_checkpoint = checkpoint.read_bytes()
    final_journal = journal.read_bytes()

    journal.write_bytes(final_journal + final_journal.splitlines(True)[-1])
    tail_out = run / "collect_late_tail.json"
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            p3.collect(str(settings), str(metric), str(run), "W1", str(tail_out))
        tail_rejected = False
    except SystemExit:
        tail_rejected = True
    tail_error = json.loads(tail_out.read_text())["errors"][0]

    journal.write_bytes(b"")
    final = json.loads(final_checkpoint)
    stale = dict(final)
    stale.update({
        "status": "running", "batches_done": 0, "cpu_seconds": 0.0,
        "wall_seconds": 0.0, "journal_bytes": 0, "journal_sha256": p2.EMPTY_SHA,
    })
    stale.pop("stop", None)
    stale.pop("failure", None)
    for key in p2.COUNTERS:
        stale[key] = 0
    checkpoint.write_text(json.dumps(stale))
    pair_out = run / "collect_late_pair.json"
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            p3.collect(str(settings), str(metric), str(run), "W1", str(pair_out))
        pair_rejected = False
    except SystemExit:
        pair_rejected = True
    pair_error = json.loads(pair_out.read_text())["errors"][0]
    return {
        "late_journal_tail_rejected": tail_rejected,
        "late_journal_tail_error": tail_error,
        "coherent_stale_zero_pair_rejected": pair_rejected,
        "coherent_stale_zero_pair_error": pair_error,
    }


def main():
    old = p3.K, p3.BATCH, p3.RETRY_SECS
    p3.K, p3.BATCH, p3.RETRY_SECS = 25, 10, 0.0
    try:
        with tempfile.TemporaryDirectory() as td:
            a = pre_hold_crash_with_omitted_hints(Path(td) / "a")
            b = collector_accepts_terminal_with_open_execution(Path(td) / "b")
            c = late_shared_file_writes_fail_closed(Path(td) / "c")
    finally:
        p3.K, p3.BATCH, p3.RETRY_SECS = old
    print(json.dumps({
        "pre_hold_crash": a,
        "collector_open_execution": b,
        "late_shared_file_writes": c,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
