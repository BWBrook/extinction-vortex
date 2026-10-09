#!/usr/bin/env python3
"""Reproduce known draft-0.6 failure-handling defects with tiny mocked inputs.

Run from any directory with Python and NumPy:
    python3 analysis/astra/protocol06_checks/probe_failure_branches.py

No population simulation, R process, remote access, or persistent fixture is
used. Exit 0 means all three known defects were reproduced; it does not mean
that the scientific procedure or its implementation passed validation.
"""

import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

import numpy as np


def load_candidate():
    repo = Path(__file__).resolve().parents[3]
    source = repo / "analysis/fable/calibration/e2e_benchmark.py"
    # Importing the candidate must not leave bytecode in Fable's directory.
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(source.parent))
    spec = importlib.util.spec_from_file_location("candidate_e2e", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return repo, source, module


def probe_outer(module, scenario):
    with tempfile.TemporaryDirectory(prefix="vortex-failure-probe-") as tmp:
        root = Path(tmp)
        bankdir, outdir = root / "banks", root / "out"
        bankdir.mkdir()
        rec = np.array([[100, 20, 2, 0], [100, 5, 3, 0], [100, 99, 2, 0]], float)
        np.savez(bankdir / "bank_iid_fixture.npz", rec=rec)
        designs = {
            "fixture": {
                "years": [0, 1, 2, 3],
                "counts": np.array([100, 95, 90, 0]),
            }
        }

        def fake_r_run(args, check):
            assert check is True
            assert args[0] == "Rscript"
            # Row 0 is observed; rows 1:9 train; rows 9:17 test.
            values = (
                np.random.default_rng(6).normal(size=(17, 4))
                if scenario == "shortfall"
                else np.ones((17, 4))
            )
            np.savetxt(
                args[3],
                np.column_stack([np.arange(17), values, np.zeros(17)]),
                delimiter=",",
                header="set,T1,T2,T3,T4,failed",
                comments="",
            )
            return subprocess.CompletedProcess(args, 0)

        argv = [
            "e2e_benchmark.py", str(bankdir), "iid", str(outdir),
            "1", "8", "2", "0.000001", "1",
        ]
        result_path = outdir / "e2e_results.json"
        with (
            patch.object(module, "designs", return_value=designs),
            patch.object(
                module, "fresh_selected", return_value=np.array([100, 95, 90, 0])
            ),
            patch.object(module.subprocess, "run", side_effect=fake_r_run),
            patch.object(sys, "argv", argv),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            try:
                module.main()
                row = json.loads(result_path.read_text())["outer"][0]
                return {
                    "scenario": scenario,
                    "shortfall": row["shortfall"],
                    "p": row["p"],
                    "results_json_created": True,
                }
            except Exception as exc:
                return {
                    "scenario": scenario,
                    "exception_type": type(exc).__name__,
                    "exception_message": str(exc),
                    "results_json_created": result_path.exists(),
                }


def probe_bare_wait():
    # This is the background-launch/bare-wait structure used by the driver.
    shell = """set -euo pipefail
(exit 7) &
(exit 9) &
wait
printf 'bare_wait_status=%s\\n' "$?"
printf 'reached_DONE=1\\n'
"""
    result = subprocess.run(["bash", "-c", shell], capture_output=True, text=True)
    return {
        "scenario": "bare_wait",
        "child_exit_codes": [7, 9],
        "driver_exit_code": result.returncode,
        "stdout": result.stdout.splitlines(),
    }


def main():
    repo, source, module = load_candidate()
    print("Known-defect reproduction only: no simulation, real R fit, or remote access.")
    print("candidate_source=" + str(source.relative_to(repo)))
    print("candidate_sha256=" + hashlib.sha256(source.read_bytes()).hexdigest())
    print("numpy_version=" + np.__version__)
    shortfall = probe_outer(module, "shortfall")
    singular = probe_outer(module, "singular_training")
    bare_wait = probe_bare_wait()
    for result in (shortfall, singular, bare_wait):
        print(json.dumps(result, sort_keys=True))

    reproduced = (
        shortfall.get("shortfall") == "fixture"
        and isinstance(shortfall.get("p"), (int, float))
        and np.isfinite(shortfall["p"])
        and shortfall["results_json_created"]
        and singular.get("exception_type") == "LinAlgError"
        and not singular["results_json_created"]
        and bare_wait["driver_exit_code"] == 0
        and bare_wait["stdout"] == ["bare_wait_status=0", "reached_DONE=1"]
    )
    if not reproduced:
        print("An expected defect was not reproduced; inspect the candidate and output.")
        return 1
    print("Reproduced all 3 known defects. Exit 0 records reproduction, not validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
