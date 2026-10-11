"""Replay the bounded D3 contract review using in-memory fixtures only.

Run with /home/bwbrook/papers/dsipa-dev/.venv/bin/python. This script imports
the reviewed functions but mocks every bank, simulator, fit and run-directory
operation. It writes only its requested JSON receipt. A matched observation
confirms a defect in the reviewed source; it is not a validation pass.
"""
from __future__ import annotations

import argparse
from contextlib import redirect_stdout
from datetime import datetime
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from unittest.mock import patch
from zoneinfo import ZoneInfo

sys.dont_write_bytecode = True

REVIEWED_HASHES = {
    "analysis/fable/calibration/v2_dev/d3_oracle.py":
        "675bd8f24fd8e051d2f5245f929c8ea12e6967116513e9fbd7a4fbe5fcf3c89e",
    "analysis/fable/calibration/v2_dev/run_d3.sh":
        "76f0d2d6d01cc789fc66e2f4d2a3de6edd1711b3def7a99393b2e48a7b5222e5",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class MemoryFiles:
    """Minimal open replacement retaining writes, without creating files."""

    def __init__(self, inputs):
        self.inputs = inputs
        self.reads = []
        self.writers = {}

    def open(self, path, mode="r", *args, **kwargs):
        key = str(path)
        if "w" in mode:
            stream = io.StringIO()
            self.writers[key] = stream
            return stream
        self.reads.append(key)
        if key not in self.inputs:
            raise FileNotFoundError(key)
        return io.StringIO(self.inputs[key])

    def written_json(self, key):
        return json.loads(self.writers[key].getvalue())


def check_support_stop(module):
    calls = []

    class EmptySelectionPool:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def map(self, function, jobs, **kwargs):
            calls.append(len(jobs))
            return [{"population": job[3], "shard": job[4], "seed": 0,
                     "selected": 0, "overflow": 0} for job in jobs]

    manifest = {"variant": "ar_cat", "scenarios": [
        {"name": "null_low_s", "spec": {"fixed": {"p": {}}}}]}
    files = MemoryFiles({"manifest": json.dumps(manifest)})
    log = io.StringIO()
    with patch("builtins.open", files.open), \
            patch.object(module, "Pool", EmptySelectionPool), \
            patch.object(module, "designs", lambda: {"p": {}}), \
            patch.object(module.os, "makedirs", lambda *a, **k: None), \
            patch.object(module, "simulate_chunk", side_effect=AssertionError("simulation forbidden")), \
            redirect_stdout(log):
        result = module.bank("manifest", "oracle", 1)
    meta = files.written_json("oracle/oracle_meta.json")
    observed = {"returned_normally": result is None, "recorded_stop": meta["stop"],
                "retained": meta["retained"], "pool_job_counts": calls,
                "stdout": log.getvalue().strip()}
    matched = (result is None and meta["stop"] == ["p"] and
               meta["retained"] == {"p": 0} and calls == [20, 20])
    return {"source_lines": "d3_oracle.py:68-86; run_d3.sh:14-18",
            "finding": "Exhausted support extension returns success, allowing the shell to launch arm V fits.",
            "expected_defect_reproduced": matched, "observed": observed}


def check_resume_binding(module):
    manifest = {"K": 2000, "R": 2000, "bankdir": "bank_primary", "variant": "ar_cat",
                "source_sha256": {}}
    files = MemoryFiles({
        "manifest": json.dumps(manifest),
        "outers": json.dumps({"outers": [{"trial": 0, "selected": {}}]}),
        "out/e2e_rows.jsonl": json.dumps({"trial_id": 0, "outcome": "accept"}) + "\n",
        "out/e2e_meta.json": json.dumps({"manifest_digest": "old_manifest", "outers_sha256": "old_outers"}),
    })
    with patch("builtins.open", files.open), \
            patch.object(module, "designs", lambda: {}), \
            patch.object(module.e2e, "knn_banks", lambda *a, **k: {}), \
            patch.object(module.e2e, "run_chunk", side_effect=AssertionError("fit forbidden")), \
            patch.object(module.os, "makedirs", lambda *a, **k: None), \
            patch.object(module.os.path, "exists", lambda p: str(p) in files.inputs), \
            patch.object(module, "sha", lambda p: "new_digest"), \
            patch.object(module, "manifest_digest", lambda p: "new_manifest"):
        module.run("V", "manifest", "base", "outers", "oracle", "out", 1)
    meta = files.written_json("out/e2e_meta.json")
    matched = ("out/e2e_meta.json" not in files.reads and
               meta["manifest_digest"] == "new_manifest" and
               "out/e2e_rows.jsonl" not in files.writers)
    return {"source_lines": "d3_oracle.py:113-125",
            "finding": "Resume skips an existing row and overwrites its configuration metadata without comparing the old binding.",
            "expected_defect_reproduced": matched,
            "observed": {"read_paths": files.reads, "written_paths": list(files.writers),
                         "new_manifest_digest": meta["manifest_digest"],
                         "new_outers_digest": meta["outers_sha256"]}}


def check_sampling_failure_report(module):
    rows = [
        {"trial_id": 0, "outcome": "indet_sampling", "sampling_failed": ["p"]},
        {"trial_id": 1, "outcome": "accept", "kth_dist": json.dumps({"p": 0.1})},
    ]
    encoded = "".join(json.dumps(row) + "\n" for row in rows)
    files = MemoryFiles({"manifest": json.dumps({"R": 2}),
                         "V/e2e_rows.jsonl": encoded, "O/e2e_rows.jsonl": encoded})
    attempted = []

    def no_sampling_T(path, R):
        attempted.append(str(path))
        raise FileNotFoundError(str(path))

    error = None
    with patch("builtins.open", files.open), patch.object(module, "N_OUT", 2), \
            patch.object(module, "SMOKE", False), \
            patch.object(module.e2e, "read_T", no_sampling_T):
        try:
            module.score("manifest", "outers", "V", "O", "score")
        except FileNotFoundError as exc:
            error = {"type": type(exc).__name__, "path": str(exc)}
    matched = error is not None and attempted == ["V/T_0.csv"] and "score" not in files.writers
    return {"source_lines": "d3_oracle.py:126-130,143-148,170-193",
            "finding": "A deliberately absent T file for a retained sampling failure prevents the complete paired report.",
            "expected_defect_reproduced": matched,
            "observed": {"exception": error, "T_paths_attempted": attempted,
                         "report_written": "score" in files.writers}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_suffix(".json"))
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[3]
    os.chdir(repo)
    paths = list(REVIEWED_HASHES) + [
        "analysis/fable/calibration/bank.py", "analysis/fable/calibration/e2e_benchmark.py",
        "analysis/fable/calibration/validate.py", "analysis/fable/calibration/freeze_v1/validation_manifest.json",
        "notes/vortex_v2_dev_plan_20261011.md"]
    source_hashes = {path: sha(repo / path) for path in paths}
    source_matches = all(source_hashes[path] == expected for path, expected in REVIEWED_HASHES.items())
    spec = importlib.util.spec_from_file_location("reviewed_d3", repo / paths[0])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with patch.object(module, "SMOKE", False), patch.object(module, "SHARDS", 20), \
            patch.object(module, "MIN_RETAINED", 20000):
        checks = [check_support_stop(module), check_resume_binding(module),
                  check_sampling_failure_report(module)]
    result = {
        "reviewed_at": datetime.now(ZoneInfo("Australia/Hobart")).isoformat(),
        "repo_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "scope": "Three in-memory D3 contract fixtures; defect confirmation, not validation.",
        "review_target_source_hashes_match": source_matches,
        "source_sha256": source_hashes, "audit_script_sha256": sha(__file__),
        "runtime": {"python": platform.python_version(), "numpy": module.np.__version__,
                    "scipy": module.scipy.__version__},
        "checks": checks,
        "all_expected_defects_reproduced": source_matches and all(c["expected_defect_reproduced"] for c in checks),
        "limitations": [
            "No remote files, jobs, live logs or partial outcomes were read or changed.",
            "No banks were loaded and no populations, reference datasets or fits were generated.",
            "Filesystem operations inside reviewed functions were mocked; only this receipt was written.",
            "Fixtures establish reachable code defects, not their occurrence in the live D3 run.",
            "The support-stop implication for arm V follows the reviewed shell source; the production shell was not executed.",
            "Newcombe intervals, trend ties and power are covered by the parent's separate checks.py, not this receipt.",
            "Fixture runtime is recorded and differs from the frozen production runtime; no production replay is claimed.",
        ],
    }
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"all_expected_defects_reproduced": result["all_expected_defects_reproduced"],
                      "checks": len(checks), "receipt": str(args.output)}))
    if not result["all_expected_defects_reproduced"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
