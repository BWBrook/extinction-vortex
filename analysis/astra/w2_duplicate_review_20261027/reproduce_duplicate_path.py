#!/usr/bin/env python3
"""Small local reproductions for the bound Stage-1b runner's duplicate-shard path."""

import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "analysis/fable/calibration/v2_dev"))
import p2_stage1a as p2  # noqa: E402
import p3_stage1b as p3  # noqa: E402


BARRIER = None


def one_hit(st, metric, batch, size, designs):
    BARRIER.wait(timeout=10)
    return {
        "proposals": p3.BATCH,
        "poisson_accept": 1,
        "theta_accept": 1,
        "paths": 1,
        "selected_SA": 1,
        "overflow": 0,
        "hits": 1,
        "boundary": 0,
        "hits_lo": 1,
        "hits_hi": 1,
        "rounding_excess": 0,
        "hit_records": [{
            "batch": batch,
            "proposal_in_batch": 0,
            "boundary": False,
            "theta": {k: 0.5 for k in p2.PARAMS},
            "recorded": [2, 1],
        }],
    }


def run_same_shard(outdir, results):
    try:
        state = p2.run_setting(
            {"batch": p3.BATCH, "hit_stop": 10, "_binding": {"test": "same-shard"}},
            {
                "index": 1,
                "pop": "test",
                "outer": "test/0",
                "n": 0,
                "E": {"n": 0, "k": 0, "r": 0},
                "stream_tag": 2,
                "proposal_budget": p3.BATCH,
                "batches": 1,
            },
            {},
            outdir,
            time.time() + 30,
            {},
            ckpt_secs=10**9,
            first_batch=0,
            name="sh000000000",
        )
        results.put({"ok": True, "status": state["status"]})
    except BaseException as ex:
        results.put({"ok": False, "error": f"{type(ex).__name__}: {ex}"})


def main():
    global BARRIER
    with tempfile.TemporaryDirectory(prefix="w2_duplicate_review_") as td:
        base = Path(td)
        run = base / "run"
        sdir = run / "sets/s00001"
        for path in (run / "queue", run / "claimed", run / "workers/dead", sdir / "ranges"):
            path.mkdir(parents=True, exist_ok=True)

        st = {
            "dir": "s00001",
            "index": 1,
            "wave": "W2",
            "pilot": None,
            "cap_batches": 2,
            "rate": 1.0,
            "prior_hpb": 0.0,
        }
        design = {
            "min_shard_cpu_h": 1.0,
            "target_wall_h": 24.0,
            "max_inflight": 1,
            "overshoot": 1.0,
        }
        (sdir / "ranges/000000000-000000001").touch()
        p2.atomic_json(
            {
                "status": "running",
                "batches_done": 0,
                "hits": 0,
                "cpu_seconds": 0.0,
            },
            str(sdir / "sh000000000.json"),
        )
        ticket = p3.ticket_name(st, 0, 1, 0)
        first_claim = run / "claimed" / f"{ticket}@ownerA"
        first_claim.touch()

        real_ls = p3.ls

        def omit_live_claim(path):
            if Path(path) == run / "claimed":
                return []
            return real_ls(path)

        p3.ls = omit_live_claim
        try:
            # Exercise plan through its real caller contract: the planner owns
            # the setting lock while it reconciles range state and queue hints.
            with p3.held(str(sdir), "planner", patience=5, deadline=time.time() + 10):
                p3.plan(st, str(sdir), str(run), design)
        finally:
            p3.ls = real_ls

        republished = sorted(os.listdir(run / "queue"))
        claimed = p3.claim(str(run), "ownerB", "W2", deadline=time.time() + 10)
        duplicate_claims = sorted(os.listdir(run / "claimed"))

        shard = base / "same_shard"
        shard.mkdir()
        initial = {
            "index": 1,
            "binding": {"test": "same-shard"},
            "batches_done": 0,
            "status": "running",
            "cpu_seconds": 0.0,
            "wall_seconds": 0.0,
            "journal_bytes": 0,
            "journal_sha256": p2.EMPTY_SHA,
            **{k: 0 for k in p2.COUNTERS},
        }
        p2.atomic_json(initial, str(shard / "sh000000000.json"))
        BARRIER = mp.get_context("fork").Barrier(2)
        p2.one_batch = one_hit
        ctx = mp.get_context("fork")
        results = ctx.Queue()
        workers = [ctx.Process(target=run_same_shard, args=(str(shard), results)) for _ in range(2)]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(15)
        worker_results = [results.get(timeout=2) for _ in workers]
        checkpoint = json.loads((shard / "sh000000000.json").read_text())
        journal = (shard / "sh000000000_hits.jsonl").read_bytes()
        committed = checkpoint["journal_bytes"]
        verify_error = None
        try:
            p3.verified(checkpoint, str(shard / "sh000000000_hits.jsonl"), 0, 1, 2, True)
        except Exception as ex:
            verify_error = f"{type(ex).__name__}: {ex}"

        out = {
            "bound_runner_sha256": hashlib.sha256(Path(p3.__file__).read_bytes()).hexdigest(),
            "runtime": p2.runtime(),
            "planner_called_under_setting_lock": True,
            "omitted_listing_republished_ticket": republished == [ticket],
            "second_worker_claimed_republication": claimed == ticket,
            "claims_for_same_range": duplicate_claims,
            "two_claims_exist": len(duplicate_claims) == 2,
            "concurrent_worker_results": worker_results,
            "journal_lines": journal.count(b"\n"),
            "journal_bytes": len(journal),
            "checkpoint_journal_bytes": committed,
            "journal_exactly_double_checkpoint": len(journal) == 2 * committed,
            "journal_halves_identical": journal[:committed] == journal[committed:],
            "strict_verification_error": verify_error,
        }
        print(json.dumps(out, indent=2, sort_keys=True))
        if not (
            out["omitted_listing_republished_ticket"]
            and out["second_worker_claimed_republication"]
            and out["two_claims_exist"]
            and all(x["ok"] for x in worker_results)
            and out["journal_exactly_double_checkpoint"]
            and out["journal_halves_identical"]
            and verify_error == "ValueError: journal length differs from its checkpoint"
        ):
            raise SystemExit(1)


if __name__ == "__main__":
    main()
