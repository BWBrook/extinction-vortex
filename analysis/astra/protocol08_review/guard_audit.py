#!/usr/bin/env python3
"""Bounded protocol-0.8 guard audit against immutable Git source; no population/R runs.

Run: /home/bwbrook/papers/dsipa-dev/.venv/bin/python analysis/astra/protocol08_review/guard_audit.py
Writes only guard_audit.json beside this script; fixtures and candidate copies are temporary.
Exit 0 means the requested repairs pass and the recorded residual is reproduced, not validation.
"""
import contextlib
import copy
import csv
import hashlib
import importlib
import io
import json
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

import numpy as np
import scipy

COMMIT = "f8546ecdfc3d95f2c7ad8837f463a34576122e29"
REPO = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RESULTS = []


def record(name, passed, **detail):
    RESULTS.append({"name": name, "passed": bool(passed), **detail})


def score(module, root, fmt, arms, n=3):
    capture = io.StringIO()
    output = root / "scored.csv"
    argv = ["score_discrimination.py", fmt, str(root), str(n), str(output), *arms]
    try:
        with patch.object(sys, "argv", argv), contextlib.redirect_stdout(capture):
            module.main()
        return {"ok": True, "summary": json.loads(capture.getvalue()),
                "rows": list(csv.DictReader(output.open()))}
    except (Exception, SystemExit) as exc:
        return {"ok": False, "exception": type(exc).__name__, "message": str(exc)}


def write_T(path, values, v1=False):
    flags = np.zeros((len(values), 1 if v1 else 2))
    np.savetxt(path, np.column_stack([np.arange(len(values)), values, flags]),
               delimiter=",", header="set,T1,T2,T3,T4,failed" + ("" if v1 else ",fallback"),
               comments="")


def main():
    sources = {}
    sys.dont_write_bytecode = True
    with tempfile.TemporaryDirectory(prefix="vortex-p08-guards-") as tmp:
        root = Path(tmp)
        src = root / "source"
        src.mkdir()
        for name in ("bank.py", "e2e_benchmark.py", "score_discrimination.py"):
            rel = "analysis/fable/calibration/" + name
            content = subprocess.check_output(["git", "show", COMMIT + ":" + rel], cwd=REPO)
            (src / name).write_bytes(content)
            sources[rel] = hashlib.sha256(content).hexdigest()
        sys.path.insert(0, str(src))
        bank = importlib.import_module("bank")
        e2e = importlib.import_module("e2e_benchmark")
        scorer = importlib.import_module("score_discrimination")
        # No implementation of simulation, library construction or R fitting is called.
        def forbidden(*args, **kwargs):
            raise AssertionError("real population simulation or R process is forbidden")
        bank.simulate_chunk = e2e.simulate_chunk = forbidden
        e2e.fresh_selected = forbidden

        ragged = root / "ragged.csv"
        ragged.write_text("set,T1,T2,T3,T4,failed,fallback\n0,1,2,3,4,0,0\n1,2,3\n")
        for name, reader in (("v2", e2e.read_T), ("v1", scorer.read_T_v1)):
            record(name + "_ragged_T_classified", reader(ragged, 8) is None)

        values = np.random.default_rng(617).normal(size=(17, 4))
        values[0] = 10
        values[-2:] = np.nan
        bounds = e2e.p_bounds(values, 8)
        assert bounds["status"] == "ok" and bounds["p_hi"] > bounds["p_lo"]
        for fmt in ("v1", "v2"):
            run = root / fmt
            run.mkdir()
            present = run / "present"
            present.mkdir()
            write_T(present / "T_0.csv", values, v1=fmt == "v1")
            if fmt == "v2":
                meta = {"R_train": 8, "R_test": 8, "n_outer": 3}
                lg = {"outer": 0, "p_lo": bounds["p_lo"], "p_hi": bounds["p_hi"],
                      "p_diagnostic": bounds["p_lo"], "outcome": e2e.outcome(bounds),
                      "kth_dist": "{}", "fallback": 0}
                (present / "e2e_meta.json").write_text(json.dumps(meta))
                (present / "e2e_rows.jsonl").write_text(json.dumps(lg) + "\n{truncated\n")
                meta_only = run / "metadata_only"
                meta_only.mkdir()
                (meta_only / "e2e_meta.json").write_text(json.dumps(meta))
                arms = ["present", "metadata_only", "absent"]
            else:
                lg = {"outer": 0, "p": bounds["p_lo"], "shortfall": "", "max_lib_dist": 0.2}
                (present / "e2e_results.json").write_text(json.dumps({"meta": {"R_train": 8}, "outer": [lg]}))
                arms = ["present", "absent"]
            result = score(scorer, run, fmt, arms)
            passed = result["ok"] and len(result["rows"]) == 3 * len(arms)
            if result["ok"]:
                for arm in arms:
                    counts = result["summary"][arm]
                    expected_missing = 2 if arm == "present" else 3
                    passed &= counts["missing"] == expected_missing
                    passed &= counts["null_gate_count"] == expected_missing and counts["detections"] == 0
            record(fmt + "_valid_and_fixed_denominators", passed, result=result)
            if fmt == "v2":
                for label, upper in (("finite_mismatch", bounds["p_hi"] + .01), ("nan", float("nan"))):
                    altered = lg | {"p_hi": upper}
                    (present / "e2e_rows.jsonl").write_text(json.dumps(altered) + "\n")
                    result = score(scorer, run, fmt, ["present"])
                    record("v2_p_hi_" + label, (not result["ok"]) if label == "finite_mismatch" else result["ok"],
                           expectation="reject mismatch" if label == "finite_mismatch" else "reproduce residual: NaN accepted",
                           result=result)
                # A producer-classified malformed file stays indeterminate in the scorer.
                (present / "T_0.csv").write_text(ragged.read_text())
                altered = lg | {"outcome": "indet_malformed", "p_diagnostic": "indeterminate"}
                (present / "e2e_rows.jsonl").write_text(json.dumps(altered) + "\n")
                result = score(scorer, run, fmt, ["present"])
                record("v2_ragged_scorer", result["ok"] and result["summary"]["present"]["indet_malformed"] == 1,
                       result=result)
            else:
                (present / "T_0.csv").write_text(ragged.read_text())
                result = score(scorer, run, fmt, ["present"])
                record("v1_ragged_scorer", result["ok"] and result["summary"]["present"]["indet_malformed"] == 1,
                       result=result)

        meta = {"shards": 2, "shard_draws": 10, "tasks": [
            {"variant": "iid", "population": "fixture", "shard": k, "seed": 100 + k, "selected": 2}
            for k in range(2)]}
        shards = [{"rec": np.array([[20, 3, 0], [20, 2, 1]], np.int32),
                   "draw_id": np.array([1, 4]) + 10 * k, "draws": 10, "seed": 100 + k,
                   "overflow": 0, **{name: np.ones(2) for name in bank.PARAM_NAMES}}
                  for k in range(2)]
        mutations = {
            "duplicate_ids": lambda m, s: s[0].update(draw_id=np.array([1, 1])),
            "decreasing_ids": lambda m, s: s[0].update(draw_id=np.array([4, 1])),
            "below_range_ids": lambda m, s: s[1].update(draw_id=np.array([9, 14])),
            "above_range_ids": lambda m, s: s[0].update(draw_id=np.array([1, 10])),
            "selected_count": lambda m, s: m["tasks"][0].update(selected=3),
            "parameter_length": lambda m, s: s[0].update(s=np.ones(1)),
            "id_length": lambda m, s: s[0].update(draw_id=np.array([1])),
            "trajectory_width": lambda m, s: s[1].update(rec=np.ones((2, 4))),
            "seed": lambda m, s: s[0].update(seed=99),
            "draw_count": lambda m, s: s[0].update(draws=9),
            "missing_shard": lambda m, s: m["tasks"].pop(),
        }
        for label, mutation in [("valid", None), *mutations.items()]:
            bm, bs = copy.deepcopy(meta), copy.deepcopy(shards)
            if mutation:
                mutation(bm, bs)
            d = root / ("bank_" + label)
            d.mkdir()
            (d / "bank_meta.json").write_text(json.dumps(bm))
            for k, fields in enumerate(bs):
                np.savez(d / f"bank_iid_fixture_s{k:03d}.npz", **fields)
            try:
                loaded = bank.load_bank(d, "iid", "fixture")
                record("bank_" + label, label == "valid" and loaded["draw_id"].tolist() == [1, 4, 11, 14],
                       accepted=True)
            except AssertionError:
                record("bank_" + label, label != "valid", accepted=False, exception="AssertionError")
    receipt = {"commit": COMMIT, "source_sha256": sources,
               "timestamp_hobart": datetime.now(ZoneInfo("Australia/Hobart")).isoformat(),
               "python": sys.executable, "numpy": np.__version__, "scipy": scipy.__version__,
               "scope": "tiny mocked statistics and bank shards; no population simulation, R, remote access, empirical test or source changes",
               "checks": RESULTS, "all_expected_behaviors_observed": all(r["passed"] for r in RESULTS),
               "residual": {"severity": "P2", "file": "analysis/fable/calibration/score_discrimination.py", "lines": [86, 89],
                            "finding": "Non-finite logged p_hi (JSON NaN) bypasses abs-difference > tolerance; scorer exits successfully although recomputed p_hi is finite. Same comparison pattern applies to p_lo."}}
    (HERE / "guard_audit.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"checks": len(RESULTS), "all_expected_behaviors_observed": receipt["all_expected_behaviors_observed"],
                      "receipt": str(HERE / "guard_audit.json"), "residual": receipt["residual"]}, indent=2))
    return 0 if receipt["all_expected_behaviors_observed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
