"""Compact A-power receipt/repair audit; no fits, simulations or bank loading.

Run with OPENBLAS_NUM_THREADS=1 /home/bwbrook/papers/dsipa-dev/.venv/bin/python
analysis/astra/a_power_review/contract_checks.py. Only the sibling JSON is retained.
Parent audit owns all remote raw-T, bank-byte and neighbour-payload checks.
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
from tempfile import TemporaryDirectory
from unittest.mock import patch
from zoneinfo import ZoneInfo

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
os.chdir(ROOT)
SOURCE = Path("analysis/fable/calibration/v2_dev/a_power.py")
ARCHIVE = SOURCE.parent / "a_power"
MANIFEST = Path("analysis/fable/calibration/freeze_v1/validation_manifest.json")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def dump(path, data):
    Path(path).write_text(json.dumps(data))


def receipts(m):
    man = json.loads(MANIFEST.read_text())
    od = json.loads((ARCHIVE / "a_power_outers.json").read_text())
    report = json.loads((ARCHIVE / "a_power_report.json").read_text())
    metas = [json.loads((ARCHIVE / f"slot{s}/e2e_meta.json").read_text()) for s in range(2)]
    rows, slots = {}, {}
    for s in range(2):
        for b in m.BLOCKS:
            for line in (ARCHIVE / f"slot{s}" / b / "e2e_rows.jsonl").read_text().splitlines():
                row = json.loads(line); key = f"{b}/{row['trial_id']}"
                assert key not in rows
                rows[key] = row; slots[key] = s
    keys = [f"{b}/{i}" for b, i in m.UNITS]
    expected_chunks = {c["dir"] for s in man["scenarios"] if s["name"] in m.BLOCKS
                       for c in s["chunks"] if c["trial_ids"][0] < 300}
    chunk_for = {f"{s['name']}/{i}": c["dir"] for s in man["scenarios"] if s["name"] in m.BLOCKS
                 for c in s["chunks"] for i in range(*c["trial_ids"]) if i < 300}
    tables = {}
    for b in m.BLOCKS:
        table = [0, 0, 0, 0]
        for i in range(300):
            key = f"{b}/{i}"; a = rows[key]["outcome"] == "reject"; v = od["outers"][key]["v1"]["outcome"] == "reject"
            table[0 if a and v else 1 if v else 2 if a else 3] += 1
        tables[b] = table
    seeds = od["settings"]["seeds"]
    checks = {
        "runner_unchanged_since_9f48fd1": git("show", f"9f48fd1:{SOURCE}") == SOURCE.read_bytes(),
        "driver_unchanged_since_e4519c7": git("show", f"e4519c7:{SOURCE.parent / 'run_a_power.sh'}") == (SOURCE.parent / "run_a_power.sh").read_bytes(),
        "bound_helpers_match_9f48fd1": all(hashlib.sha256(git("show", f"9f48fd1:{SOURCE.parent / name}")).hexdigest() == h
                                           for name, h in od["helper_sha256"].items()),
        "bound_helpers_match_current": od["helper_sha256"] == m.helper_hashes(),
        "candidate_A_helpers_unchanged_since_6316a90": all(git("show", f"6316a90:{SOURCE.parent / name}") == (SOURCE.parent / name).read_bytes()
                                                        for name in m.HELPERS if name != "a_power.py"),
        "frozen_sources_match": all(sha(p) == h for p, h in man["source_sha256"].items()),
        "slot_source_bindings_match": all(meta["source_sha256"] == man["source_sha256"] for meta in metas),
        "manifest_binding": od["manifest_digest"] == sha(MANIFEST),
        "outers_binding": all(meta["outers_sha256"] == sha(ARCHIVE / "a_power_outers.json") for meta in metas),
        "exact_600_cases": sorted(rows) == sorted(keys) == sorted(od["outers"]) and len(rows) == 600,
        "exact_source_chunks": set(od["source_rows_sha256"]) == expected_chunks and len(expected_chunks) == 20,
        "correct_chunk_assignments": all(o["dir"] == chunk_for[k] for k, o in od["outers"].items()),
        "all_5400_series_match": all(rows[k]["selected"][n]["recorded"] == rec for k, o in od["outers"].items() for n, rec in o["recorded"].items()),
        "expected_settings": od["settings"] == m.settings(man),
        "full_seed_map_matches_plan": seeds == {f"{b}/{i}": 8000006200000 + 10000 * block + i for b, block in m.BLOCKS.items() for i in range(300)},
        "seeds_unique_and_disjoint_from_A_screen": len(set(seeds.values())) == 600 and not set(seeds.values()).intersection(range(8000006100000, 8000006100200)),
        "slots_match_declared_partition": all(slots[k] == j % 2 for j, k in enumerate(keys)),
        "slot_meta_expected": all(meta["screen"] == "A-power" and meta["slot"] == s and meta["nslots"] == 2 and meta["r_workers"] == 30
                                  and meta["bank_verified"] is True for s, meta in enumerate(metas)),
        "paired_tables_match": all(tables[b] == report["blocks"][b]["table_both_V1_only_A_only_neither"] for b in m.BLOCKS),
        "no_recorded_failures_or_indeterminates": all(r["outcome"] in ("accept", "reject") and r["fit_failures"] == r["train_fail"] == r["test_fail"] == 0 for r in rows.values()),
        "all_observed_reused_without_generation": all(v["draws"] == 0 and v["params"] == {} for r in rows.values() for v in r["selected"].values()),
    }
    return {"checks": checks, "paired_tables": tables,
            "seed_ranges": {b: [seeds[f"{b}/0"], seeds[f"{b}/299"]] for b in m.BLOCKS},
            "binding_timestamps": {commit: git("show", "-s", "--format=%cI", commit).decode().strip() for commit in ("e4519c7", "9f48fd1")},
            "timeline": (ARCHIVE / "timeline.txt").read_text().splitlines(),
            "limits": "Remote raw-T rescoring and bank/neighbour bytes belong to the separate parent audit."}


def repaired_guard(m, mode):
    """Two completed mock trials: no new trial executes and no bank is loaded."""
    with TemporaryDirectory(prefix="astra_power_contract_") as tmp, ExitStack() as stack:
        p = Path(tmp); out = p / "out"; sd = out / "slot0"; sd.mkdir(parents=True)
        bd = p / "bank"; bd.mkdir(); payload = bd / "receipt_fixture"; payload.write_text("fixture bytes")
        man = {"K": 2, "R": 2, "variant": "ar_cat", "bankdir": "bank", "bank_sha256": {payload.name: sha(payload)}, "source_sha256": {}}
        mp = p / "manifest.json"; dump(mp, man)
        units = [(b, 0) for b in m.BLOCKS]; selected = {"p": {"recorded": [10, 4, 1]}}
        calls = []
        for obj, name, value in [(m, "IDS", range(1)), (m, "UNITS", units), (m, "SMOKE", False),
                                 (m, "designs", lambda: {"p": {}}), (m, "cplus_banks", lambda *a: {}),
                                 (m, "z_resid", lambda *a: ([0., 0., 0., 0.], 2)),
                                 (m.e2e, "run_chunk", lambda *a, **k: calls.append("unexpected trial")),
                                 (m.e2e, "calib_features", m.e2e.calib_features)]:
            stack.enter_context(patch.object(obj, name, value))
        stack.enter_context(redirect_stdout(io.StringIO()))
        od = {"manifest_digest": sha(mp), "source_rows_sha256": {}, "settings": m.settings(man), "helper_sha256": m.helper_hashes(),
              "outers": {f"{b}/0": {"dir": "unused_mock_v1", "recorded": {"p": [10, 4, 1]},
                                     "v1": {"outcome": "accept", "kth_dist": json.dumps({"p": .1})}} for b in m.BLOCKS}}
        op = p / "outers.json"; dump(op, od)
        nbr = {}
        for b in m.BLOCKS:
            d = sd / b; d.mkdir(); (d / "T_0.csv").write_text("mock T file presence only")
            row = {"trial_id": 0, "selected": selected, "outcome": "accept", "kth_dist": json.dumps({"p": .1}), "fit_failures": 0, "t_fits": 0}
            (d / "e2e_rows.jsonl").write_text(json.dumps(row) + "\n")
            for suffix, value in (("", [1, 2]), ("/tie", [False]), ("/kth", [.1]), ("/origC_max", [.1])):
                nbr[f"{b}/0/p{suffix}"] = m.np.array(value)
        m.np.savez_compressed(sd / "neighbours.npz", **nbr)
        meta = {"screen": "A-power", "slot": 0, "nslots": 1, "outers_sha256": sha(op), "r_workers": 1, "bank_verified": True,
                "runtime": {"python": platform.python_version(), "numpy": m.np.__version__, "scipy": m.scipy.__version__}, "source_sha256": {}}
        if "helper" in mode:
            od["helper_sha256"]["a_power.py"] = "changed"; dump(op, od)
        elif "settings" in mode:
            od["settings"]["K"] = 999; dump(op, od)
        elif "bank" in mode:
            payload.write_text("changed bytes")
        elif "missing_T" in mode:
            (sd / "MA_betamin/T_0.csv").unlink()
        elif "changed_series" in mode:
            rp = sd / "MA_betamin/e2e_rows.jsonl"; row = json.loads(rp.read_text()); row["selected"]["p"]["recorded"][0] += 1
            rp.write_text(json.dumps(row) + "\n")
        meta["outers_sha256"] = sha(op); dump(sd / "e2e_meta.json", meta)
        error = None
        try:
            if mode.startswith("run"):
                m.run(str(mp), tmp, str(op), str(out), 0, 1, 1)
            else:
                m.report(str(mp), tmp, str(op), str(out), 1, str(p / "report.json"))
        except SystemExit as exc:
            error = str(exc)
        return {"refused": error is not None, "error": error, "unexpected_trial_calls": len(calls)}


def main():
    spec = importlib.util.spec_from_file_location("a_power_audit", SOURCE)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    observed = receipts(m)
    modes = ["run_complete_resume", "run_missing_T", "run_changed_bank", "run_changed_helper",
             "report_baseline", "report_changed_bank", "report_changed_helper", "report_changed_settings", "report_changed_series"]
    fixtures = {mode: repaired_guard(m, mode) for mode in modes}
    assert all(observed["checks"].values()), observed["checks"]
    assert all(v["refused"] == (mode not in ("run_complete_resume", "report_baseline")) and v["unexpected_trial_calls"] == 0 for mode, v in fixtures.items())
    result = {"scope": "Current compact receipts and narrow repairs; no fits, simulations, production bank loading or peer edits",
              "time_hobart": datetime.now(ZoneInfo("Australia/Hobart")).isoformat(), "head": git("rev-parse", "HEAD").decode().strip(),
              "observed": observed, "guard_fixtures": fixtures,
              "assessment": "No material current-record defect found. Requested repairs refuse their targeted cases. Parent owns raw-T and remote-byte verification.",
              "scientific_limit": "D3 exact six-coordinate theta versus prior(b) is a one-corner null-reference comparison, not an ordered s/f precision bracket or a power result; precision-response monotonicity is unestablished."}
    path = Path(__file__).with_suffix(".json"); path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(path), "observed_checks": len(observed["checks"]), "guard_cases": len(fixtures)}))


if __name__ == "__main__":
    main()
