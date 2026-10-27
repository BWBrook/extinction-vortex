#!/usr/bin/env python3
import contextlib
import errno
import hashlib
import importlib.util
import json
import os
import pathlib
import tempfile
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[3]
RUNNER = ROOT / "analysis/fable/calibration/v2_dev/p3_stage1b.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("r3_candidate", RUNNER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def layout(base):
    run = pathlib.Path(base) / "run"
    sdir = run / "sets" / "s00000"
    for rel in ("queue", "claimed", "workers/dead", "sets/s00000/r", "sets/s00000/x"):
        (run / rel).mkdir(parents=True, exist_ok=True)
    return run, sdir


def patched_rec(module, hidden):
    real = module.rec

    def rec(path):
        if os.fspath(path) in hidden:
            return None
        return real(path)

    return mock.patch.object(module, "rec", rec)


def link_then_lose_reply(module, selected):
    real = os.link

    def link(src, dst, *args, **kwargs):
        real(src, dst, *args, **kwargs)
        if os.fspath(dst) in selected:
            raise FileExistsError(errno.EEXIST, "injected lost LINK reply", dst)

    return mock.patch.object(module.os, "link", link)


def main():
    m = load_runner()
    cases = {}
    with tempfile.TemporaryDirectory(prefix="r3_state_") as td:
        run, sdir = layout(td)
        record = sdir / "r" / "000000000"

        with link_then_lose_reply(m, {os.fspath(record)}):
            returned = m.create(record, {"b": 10, "prio": 123})
        stored = m.rec(record)
        cases["lost_link_reply_same_token_is_success"] = {
            "pass": returned is True and stored["b"] == 10 and isinstance(stored.get("token"), str),
            "create_returned": returned,
            "record": stored,
        }

        stale_record = sdir / "r" / "000000010"
        with contextlib.ExitStack() as stack:
            stack.enter_context(link_then_lose_reply(m, {os.fspath(stale_record)}))
            stack.enter_context(patched_rec(m, {os.fspath(stale_record)}))
            returned = m.create(stale_record, {"b": 20, "prio": 123})
        cases["lost_reply_plus_stale_read_fails_closed"] = {
            "pass": returned is False and m.rec(stale_record)["b"] == 20,
            "create_returned": returned,
            "record_after_visibility_returns": m.rec(stale_record),
        }

        before = {p.name: m.rec(p) for p in (sdir / "r").iterdir() if not p.name.startswith(".")}
        st = {"pilot": None, "cap_batches": 100, "rate": 20000.0, "prior_hpb": 0.0,
              "wave": "W1", "dir": "s00000"}
        bound = {"min_shard_cpu_h": 1.0, "target_wall_h": 1.0, "max_inflight": 1, "overshoot": 1.0}
        with patched_rec(m, {os.fspath(record)}):
            m.plan(st, sdir, run, bound, "planner")
        after = {p.name: m.rec(p) for p in (sdir / "r").iterdir() if not p.name.startswith(".")}
        cases["stale_range_head_cannot_create_overlap"] = {
            "pass": after == before and "000000010" in after,
            "records_before": before,
            "records_after": after,
        }

        run2, sdir2 = layout(pathlib.Path(td) / "case_execution")
        rp = m.rpath(sdir2, 0)
        m.create(rp, {"b": 10, "prio": 123})
        xp0 = m.xpath(sdir2, 0, 0)
        m.create(xp0, {"owner": "worker-A", "host": "h", "pid": 1, "range": [0, 10], "time": 1.0})
        ticket = "W1_0000123_s00000_000000000_000000010"
        (run2 / "queue" / ticket).touch()
        outcome = None
        with patched_rec(m, {xp0}):
            try:
                m.take(run2, ticket, "worker-B")
            except m.Behind as ex:
                outcome = type(ex).__name__
        starts = sorted(p.name for p in (sdir2 / "x").iterdir() if not p.name.startswith(".") and not p.name.endswith(".end"))
        cases["stale_execution_start_cannot_admit_second_writer"] = {
            "pass": outcome == "Behind" and starts == ["000000000.0"] and m.rec(xp0)["owner"] == "worker-A",
            "outcome": outcome,
            "execution_starts": starts,
        }

        m.close(sdir2, 0, 0, "dead", "recovery")
        xp1 = m.xpath(sdir2, 0, 1)
        m.create(xp1, {"owner": "worker-C", "host": "h", "pid": 2, "range": [0, 10], "time": 2.0})
        (run2 / "queue" / ticket).touch()
        outcome = None
        with patched_rec(m, {xp1}):
            try:
                m.take(run2, ticket, "worker-D")
            except m.Behind as ex:
                outcome = type(ex).__name__
        starts = sorted(p.name for p in (sdir2 / "x").iterdir() if not p.name.startswith(".") and not p.name.endswith(".end"))
        cases["stale_latest_execution_cannot_skip_generation"] = {
            "pass": outcome == "Behind" and starts == ["000000000.0", "000000000.1"],
            "outcome": outcome,
            "execution_starts": starts,
        }

        run4, sdir4 = layout(pathlib.Path(td) / "case_stale_end")
        m.create(m.rpath(sdir4, 0), {"b": 10, "prio": 123})
        xp = m.xpath(sdir4, 0, 0)
        m.create(xp, {"owner": "worker-F", "host": "h", "pid": 3, "range": [0, 10], "time": 3.0})
        end = xp + ".end"
        m.create(end, {"outcome": "complete", "by": "worker-F", "time": 4.0})
        with open(run4 / "workers" / "dead" / "worker-F", "w") as fh:
            json.dump({"owner": "worker-F", "host": "h", "pid": 3, "rc": 0}, fh)
        (run4 / "queue" / ticket).touch()
        outcome = None
        with patched_rec(m, {end}):
            try:
                m.take(run4, ticket, "worker-G")
            except m.Behind as ex:
                outcome = type(ex).__name__
        starts = sorted(p.name for p in (sdir4 / "x").iterdir() if not p.name.startswith(".") and not p.name.endswith(".end"))
        cases["stale_execution_end_cannot_be_overwritten_or_advanced"] = {
            "pass": outcome == "Behind" and starts == ["000000000.0"] and m.rec(end)["outcome"] == "complete",
            "outcome": outcome,
            "execution_starts": starts,
            "end_after_visibility_returns": m.rec(end),
        }

        run3, sdir3 = layout(pathlib.Path(td) / "case_lost_take")
        m.create(m.rpath(sdir3, 0), {"b": 10, "prio": 123})
        (run3 / "queue" / ticket).touch()
        xp = m.xpath(sdir3, 0, 0)
        with link_then_lose_reply(m, {xp}):
            k = m.take(run3, ticket, "worker-E")
        starts = sorted(p.name for p in (sdir3 / "x").iterdir() if not p.name.startswith(".") and not p.name.endswith(".end"))
        cases["take_reconciles_lost_link_reply_without_duplicate"] = {
            "pass": k == 0 and starts == ["000000000.0"] and m.rec(xp)["owner"] == "worker-E",
            "execution": k,
            "execution_starts": starts,
        }

        base5 = pathlib.Path(td) / "case_collector_listing"
        run5, sdir5 = layout(base5)
        (run5 / "lib").mkdir()
        metric = base5 / "metric.json"
        settings = base5 / "settings.json"
        metric.write_text(json.dumps({
            "outers": {"synthetic|toy/0": {"recorded": [5, 4, 0]}},
            "pops": {"synthetic": {"keep": [], "mad": []}},
        }))
        st5 = {"index": 0, "pop": "synthetic", "outer": "toy/0", "n": 30,
               "E": {"n": 30, "k": 1, "r": 1}, "rate": 1.0, "cap_batches": 100,
               "prior_hpb": 0.0, "wave": "W1", "dir": "s00000", "library": "primary",
               "stream_tag": 2, "pilot": None}
        settings.write_text(json.dumps({"settings": [st5], "metric_sha256": "m", "runner_sha256": "r"}))
        off_chain = sdir5 / "r" / "000000010"
        m.create(off_chain, {"b": 20, "prio": 123})
        collected = run5 / "collect_fault.json"
        with mock.patch.object(m, "ls", lambda path: []):
            m.collect(settings, metric, run5, "W1", collected)
        summary = json.loads(collected.read_text())
        cases["collector_off_chain_check_depends_on_listing_completeness"] = {
            "pass": summary["collection_ok"] is True and summary["rows"][0]["ranges"] == 0 and off_chain.exists(),
            "collection_ok_with_omitted_off_chain_record": summary["collection_ok"],
            "reported_ranges": summary["rows"][0]["ranges"],
            "off_chain_record_exists": off_chain.exists(),
            "interpretation": "Evidence-scope limitation, not a reproduced second-writer path.",
        }

    result = {
        "runner": str(RUNNER.relative_to(ROOT)),
        "runner_sha256": hashlib.sha256(RUNNER.read_bytes()).hexdigest(),
        "cases": cases,
        "all_expected": all(v["pass"] for v in cases.values()),
        "scope": "Local POSIX fault injection of exact-read omissions and lost hard-link replies; not an NFS server conformance test.",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["all_expected"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
