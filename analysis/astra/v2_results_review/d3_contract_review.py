"""Bounded D3 receipt audit and in-memory branch fixtures; no bank loads or fits.

Run from any directory with a Python containing NumPy/SciPy. Only the sibling
JSON receipt is written. These fixtures describe reuse risks, not evidence that
the completed D3 run encountered them; the parent's raw-T audit is separate.
"""
from contextlib import ExitStack, redirect_stdout
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
from types import SimpleNamespace
from unittest.mock import patch
from zoneinfo import ZoneInfo

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
os.chdir(ROOT)
SOURCE = "analysis/fable/calibration/v2_dev/d3_oracle.py"
D3 = Path("analysis/fable/calibration/v2_dev/d3")
MAN = Path("analysis/fable/calibration/freeze_v1/validation_manifest.json")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Stream(io.StringIO):
    def close(self):
        pass


class MemoryFiles:
    def __init__(self, inputs):
        self.inputs, self.reads, self.writes = inputs, [], {}

    def open(self, path, mode="r", *args, **kwargs):
        key = str(path)
        if "w" in mode or "a" in mode:
            self.writes[key] = Stream(self.inputs.get(key, "") if "a" in mode else "")
            self.writes[key].seek(0, 2)
            return self.writes[key]
        self.reads.append(key)
        return Stream(self.inputs[key])


def run_fixture(m, mode):
    manifest = {"K": 2, "R": 2, "bankdir": "primary", "variant": "ar_cat", "source_sha256": {}}
    meta = {"arm": "V", "manifest_digest": "digest", "outers_sha256": "hash",
            "oracle_meta_sha256": None, "K": 2, "R_train": 2, "R_test": 2,
            "seed_base": m.SEED["V"], "r_workers": 1,
            "runtime": {"python": platform.python_version(), "numpy": m.np.__version__,
                        "scipy": m.scipy.__version__}, "source_sha256": {}}
    inputs = {"manifest": json.dumps(manifest),
              "outers": json.dumps({"outers": [{"trial": 0, "selected": {}}]}),
              "oracle/oracle_meta.json": json.dumps({"stop": ["p"]})}
    if mode != "support":
        inputs["out/e2e_rows.jsonl"] = json.dumps({"trial_id": 0, "outcome": "accept"}) + "\n"
        if mode != "missing_meta":
            inputs["out/e2e_meta.json"] = json.dumps(meta | ({"manifest_digest": "old"} if mode == "changed_meta" else {}))
    files = MemoryFiles(inputs)
    calls = []
    with ExitStack() as st:
        for obj, name, val in [
            (m, "designs", lambda: {}), (m, "sha", lambda p: "hash"),
            (m, "manifest_digest", lambda p: "digest"), (m, "SMOKE", False),
            (m.e2e, "knn_banks", lambda *a: {}),
            (m.e2e, "run_chunk", lambda *a, **k: calls.append("run_chunk")),
            (m.os, "makedirs", lambda *a, **k: None),
            (m.os.path, "exists", lambda p: str(p) in inputs),
            (m.np, "savez_compressed", lambda *a, **k: calls.append("save_neighbours"))]:
            st.enter_context(patch.object(obj, name, val))
        st.enter_context(patch("builtins.open", files.open))
        error = None
        try:
            m.run("V", "manifest", "base", "outers", "oracle", "out", 1)
        except SystemExit as exc:
            error = str(exc)
    return {"error": error, "calls": calls, "read_paths": files.reads,
            "written_paths": list(files.writes)}


def report_fixture(m, sampling_failure=False):
    """Two fake trials, one population; all bank/statistic operations are replaced."""
    rows = [{"trial_id": i, "outcome": "indet_sampling" if sampling_failure and i == 0 else "accept",
             "kth_dist": json.dumps({"p": 0.1})} for i in range(2)]
    meta = {"manifest_digest": "wrong", "outers_sha256": "hash", "oracle_meta_sha256": "hash",
            "source_sha256": {}, "K": 2, "R_train": 2, "R_test": 2, "seed_base": 0, "runtime": {}}
    inputs = {"manifest": json.dumps({"K": 2, "R": 2, "bankdir": "bank", "variant": "ar_cat",
                                       "source_sha256": {}, "bank_sha256": {}}),
              "outers": json.dumps({"outers": [{"trial": i, "selected": {"p": None if sampling_failure and i == 0
                                      else {"recorded": [1, 2]}}} for i in range(2)]}),
              "oracle/oracle_meta.json": json.dumps({"stop": [], "extended": [], "retained": {"p": 2},
                                                       "tasks": [{"population": "p", "shard": 0}]}),
              "runner_sha": "hash runner"}
    for arm in ("V", "O"):
        inputs[f"{arm}/e2e_meta.json"] = json.dumps(meta)
        inputs[f"{arm}/e2e_rows.jsonl"] = "".join(json.dumps(r) + "\n" for r in rows)
    files = MemoryFiles(inputs)
    fake_bank = {"rec": m.np.array([[1., 1.], [3., 3.]]), "draw_id": m.np.array([0, 1])}
    import bank
    with ExitStack() as st:
        for obj, name, val in [
            (m, "N_OUT", 2), (m, "designs", lambda: {"p": {}}),
            (m, "sha", lambda p: "hash"), (m, "manifest_digest", lambda p: "digest"),
            (m, "calib_features", lambda a: a), (m, "z_resid", lambda *a: ([0., 0., 0., 0.], 2)),
            (m.os, "listdir", lambda p: []), (bank, "load_bank", lambda *a: fake_bank),
            (m.np, "load", lambda p: {} if str(p).endswith("neighbours.npz") else fake_bank),
            (m.np, "savez_compressed", lambda *a, **k: None),
            (subprocess, "run", lambda *a, **k: SimpleNamespace(stdout="mock runtime"))]:
            st.enter_context(patch.object(obj, name, val))
        st.enter_context(patch("builtins.open", files.open))
        st.enter_context(redirect_stdout(io.StringIO()))
        error = None
        try:
            m.report("manifest", "base", "outers", "oracle", "V", "O", "runner_sha", "report.json")
        except TypeError as exc:
            error = str(exc)
    report = json.loads(files.writes["report.json"].getvalue()) if "report.json" in files.writes else None
    return {"error": error, "report_written": report is not None,
            "manifest_check": report["checks"]["manifest_digest_bound"] if report else None,
            "neighbour_sets": {a: report["checks"]["neighbour_reconciliation"][a]["sets"] for a in ("V", "O")} if report else None}


def compact_receipts():
    man = json.loads(MAN.read_text())
    od = json.loads((D3 / "outers.json").read_text())
    om = json.loads((D3 / "oracle_meta.json").read_text())
    meta = {a: json.loads((D3 / a / "e2e_meta.json").read_text()) for a in ("V", "O")}
    rows = {a: [json.loads(l) for l in (D3 / a / "e2e_rows.jsonl").read_text().splitlines()] for a in meta}
    recorded = {i["trial"]: {n: v["recorded"] for n, v in i["selected"].items()} for i in od["outers"]}
    counts = {n: sum(t["selected"] for t in om["tasks"] if t["population"] == n) for n in om["retained"]}
    theta = next(s["spec"]["fixed"] for s in man["scenarios"] if s["name"] == "null_low_s")
    launch = subprocess.check_output(["git", "show", f"ff847a8:{SOURCE}"])
    return {
        "ordered_unique_0_to_199": {a: [r["trial_id"] for r in rr] == list(range(200)) for a, rr in rows.items()},
        "outers_ordered_unique_0_to_199": [o["trial"] for o in od["outers"]] == list(range(200)),
        "all_3600_arm_population_records_match_saved_outers": all(
            {n: v["recorded"] for n, v in r["selected"].items()} == recorded[r["trial_id"]]
            for rr in rows.values() for r in rr),
        "sampling_failures": sum(any(v is None for v in o["selected"].values()) for o in od["outers"]),
        "logged_fit_failures": {a: sum(r["fit_failures"] for r in rr) for a, rr in rows.items()},
        "logged_train_test_failures": {a: sum(r["train_fail"] + r["test_fail"] for r in rr) for a, rr in rows.items()},
        "outer_metadata_bound": all(mm["outers_sha256"] == sha(D3 / "outers.json") for mm in meta.values()),
        "manifest_bound": od["manifest_digest"] == sha(MAN) and all(mm["manifest_digest"] == sha(MAN) for mm in meta.values()),
        "oracle_meta_bound": meta["O"]["oracle_meta_sha256"] == sha(D3 / "oracle_meta.json"),
        "K_R_and_arm_seed_match_specification": all(mm["arm"] == a and mm["K"] == man["K"] and
            mm["R_train"] == mm["R_test"] == man["R"] and mm["seed_base"] == 8000003000000 +
            (10000 if a == "V" else 20000) for a, mm in meta.items()),
        "all_six_outer_parameters_and_oracle_theta_match_corner": od["theta"] == om["theta"] == theta and
            all(v["params"] == theta[n] for o in od["outers"] for n, v in o["selected"].items()),
        "outer_seed_and_budget_match_specification": od["seed"] == 8000003000000 and od["budget"] == man["budget"],
        "source_maps_match_manifest_and_current_files": all(mm["source_sha256"] == man["source_sha256"] for mm in meta.values()) and all(sha(p) == h for p, h in man["source_sha256"].items()),
        "launch_runner_matches_git_ff847a8": hashlib.sha256(launch).hexdigest() == (D3 / "runner_sha256.txt").read_text().split()[0],
        "oracle_tasks_unique_and_complete": len(om["tasks"]) == 180 and len({(t["population"], t["shard"]) for t in om["tasks"]}) == 180 and all({t["shard"] for t in om["tasks"] if t["population"] == n} == set(range(20)) for n in counts),
        "oracle_recorded_counts_reconcile": counts == om["retained"],
        "oracle_recorded_min_retained": min(counts.values()),
        "oracle_stop": om["stop"], "oracle_extended": om["extended"],
        "timeline_start_entries": (D3 / "timeline.txt").read_text().count("start "),
        "no_restart_limit": "One saved driver start and sequential unique rows are consistent with no restart; do not prove no manual direct-arm restart.",
    }


def main():
    spec = importlib.util.spec_from_file_location("reviewed_d3", SOURCE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    fixtures = {mode: run_fixture(m, mode) for mode in ("changed_meta", "missing_meta", "missing_neighbours", "support")}
    fixtures["sampling_failure_report"] = report_fixture(m, True)
    fixtures["false_binding_and_missing_neighbours_report"] = report_fixture(m)
    checks = [fixtures["changed_meta"]["error"] == "resume refused: bindings differ from the existing run",
              fixtures["missing_meta"]["error"] is None and "out/e2e_meta.json" in fixtures["missing_meta"]["written_paths"],
              fixtures["missing_neighbours"]["calls"] == [],
              "run_chunk" in fixtures["support"]["calls"] and "oracle/oracle_meta.json" not in fixtures["support"]["read_paths"],
              fixtures["sampling_failure_report"]["error"] == "'NoneType' object is not subscriptable",
              fixtures["false_binding_and_missing_neighbours_report"]["report_written"] and fixtures["false_binding_and_missing_neighbours_report"]["manifest_check"] is False]
    result = {"reviewed_at": datetime.now(ZoneInfo("Australia/Hobart")).isoformat(),
              "scope": "Compact local receipts and mocked branches only; no T rescoring, bank loads, fits, or remote operations.",
              "repo_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
              "source_sha256": {p: sha(p) for p in [SOURCE, "analysis/fable/calibration/v2_dev/run_d3.sh", str(MAN)]},
              "script_sha256": sha(__file__), "local_receipts": compact_receipts(),
              "fixtures": fixtures, "all_expected_observations_reproduced": all(checks),
              "limitations": ["Reported bank and neighbour SHA values are not independent verification of remote payloads.",
                              "Reported K-th-distance reconciliation establishes distances of saved sets, not exact query membership independently.",
                              "R/nlme were recorded at report time; launch-time versions remain unproven by these compact receipts.",
                              "No mocked defect establishes occurrence in the completed run; conditional repair needed only before reuse."]}
    Path(__file__).with_suffix(".json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"all_expected_observations_reproduced": all(checks), "local_receipts": result["local_receipts"]}, indent=2))
    assert all(checks)


if __name__ == "__main__":
    main()
