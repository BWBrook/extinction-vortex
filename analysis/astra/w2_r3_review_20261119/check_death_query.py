"""Check how the bound runner treats PBS query results. All responses are mocks."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "analysis/fable/calibration"))
sys.path.insert(0, str(ROOT / "analysis/fable/calibration/v2_dev"))
import p3_stage1b as runner


def check(initial_status, initial_state, later_state):
    owner = {"owner": "fixture[1].server.slot", "host": None}
    responses = [
        subprocess.CompletedProcess([], rc, stdout=f"job_state = {state}\n" if state else "", stderr="")
        for rc, state in [(initial_status, initial_state), (0, later_state)]
    ]
    runner._PBS.clear()
    with patch.object(runner.subprocess, "run", side_effect=responses) as query:
        with patch.object(runner.time, "time", return_value=1000):
            first = runner.owner_dead(owner, qstat="fixture-only")
        with patch.object(runner.time, "time", return_value=1001 + runner.PBS_SUSPECT_SECS):
            after_expiry = runner.owner_dead(owner, qstat="fixture-only")
    return {"initial_rc": initial_status, "initial_state": initial_state, "later_state": later_state,
            "first_classified_dead": first, "after_negative_cache_interval_classified_dead": after_expiry,
            "queries": query.call_count}


if __name__ == "__main__":
    sha = hashlib.sha256(Path(runner.__file__).read_bytes()).hexdigest()
    assert sha == "92674ee8aa685b2a20bf5a689a3cbba836b195b8657ba8f79c5da161f315b765"
    cases = [check(0, "R", "F"), check(2, "", "F"), check(0, "F", "R"), check(2, "F", "R")]
    results = [(r["first_classified_dead"], r["after_negative_cache_interval_classified_dead"], r["queries"])
               for r in cases]
    assert results == [(False, True, 2), (False, True, 2), (True, True, 1), (True, True, 1)]
    print(json.dumps({"bound_runner_sha256": sha, "cases": cases,
                      "failed_matching_reply_accepted_and_cached": True}, indent=2))
