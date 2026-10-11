"""Independent bounded recheck of protocol-0.10 configuration binding.

Only synthetic T files and mocked bank/run/R interfaces are used. The actual
manifest is inspected as data; no bank files, empirical results, or R are read.
Run with the dsipa-dev Python environment. All fixtures are temporary; the
adjacent JSON records checks and the precise limits of point-in-time preflight.
"""
import contextlib
import copy
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import scipy

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "analysis/fable/calibration"
sys.path.insert(0, str(SRC))
import collect_validation as cv
import e2e_benchmark as e2e
import empirical_q1 as eq
import preflight as pf
import validate as va

OUT = Path(__file__).with_suffix(".json")
checks = {}
limits = {}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(p, value):
    Path(p).write_text(json.dumps(value))


def refused(fn):
    try:
        fn()
    except SystemExit as exc:
        return str(exc)
    return None


def check(name, passed, detail=None):
    checks[name] = {"pass": bool(passed), "detail": detail}
    if not passed:
        raise AssertionError(name)


def command(fn, argv):
    with patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()):
        return fn()


manifest_path = SRC / "freeze_v1/validation_manifest.json"
frozen = json.loads(manifest_path.read_text())
digest = va.manifest_digest(manifest_path)
check("frozen_digest", digest == "96603037ec05036153f67b649757d067ca193c5e0a8610d3b855ef8f22139429", digest)
all_dirs = [c["dir"] for s in frozen["scenarios"] for c in s["chunks"]]
all_seeds = [c["seed"] for s in frozen["scenarios"] for c in s["chunks"]]
check("frozen_manifest_unique_dirs_seeds", len(all_dirs) == len(set(all_dirs)) == len(set(all_seeds)) == 170)
check("frozen_manifest_trial_partition", all(
    [i for c in s["chunks"] for i in range(*c["trial_ids"])] == list(range(s["n_trials"]))
    for s in frozen["scenarios"]))
check("frozen_manifest_declared_roles", [s["role"] for s in frozen["scenarios"]] ==
      ["null"] * 4 + ["power"] + ["descriptive"] * 11 + ["stress"])

R = 20
matrix = np.random.default_rng(78413).normal(size=(2 * R + 1, 4))
matrix[0] = matrix[1:R + 1].mean(axis=0)
bounds = e2e.p_bounds(matrix, R)
row = {"p_diagnostic": bounds["p_lo"], "kth_dist": "{}", "outcome": e2e.outcome(bounds), **bounds}
assert row["outcome"] == "accept"
runtime = {"python": "mock-python", "numpy": np.__version__, "scipy": scipy.__version__,
           "R": "mock-R", "nlme": "mock-nlme"}

with tempfile.TemporaryDirectory(prefix="astra-binding-") as tmp:
    base = Path(tmp)
    mp = base / "manifest.json"
    stress = base / "stress.json"
    save(stress, {"sets": {}})
    scenario = {"block": 1, "name": "null", "role": "null", "n_trials": 2, "beta": 0.0,
                "spec": {}, "stress": False,
                "chunks": [{"c": 0, "seed": 101, "dir": "chunk", "trial_ids": [0, 2]}]}
    man = {"variant": "ar_cat", "R": R, "K": 50, "budget": 1_000_000,
           "bankdir": "toybank", "stress_sets": "stress.json", "stress_sets_sha256": sha(stress),
           "scenarios": [scenario]}
    save(mp, man)
    md = va.manifest_digest(mp)
    c = scenario["chunks"][0]
    chunk = base / c["dir"]
    check("chunk_absent", va.chunk_state(man, md, scenario, c, base) == "absent")
    chunk.mkdir()
    meta = {"manifest_digest": md, "settings": va.chunk_settings(man, scenario, c), "R_train": R}
    save(chunk / "e2e_meta.json", meta)
    (chunk / "e2e_rows.jsonl").write_text("".join(json.dumps(row | {"trial_id": i}) + "\n" for i in range(2)))
    for i in range(2):
        with (chunk / f"T_{i}.csv").open("w") as fh:
            writer = csv.writer(fh)
            writer.writerow(["set", "T1", "T2", "T3", "T4", "failed", "fallback"])
            writer.writerows([j, *values, 0, 0] for j, values in enumerate(matrix))
    check("chunk_complete", va.chunk_state(man, md, scenario, c, base) == "complete")
    check("changed_digest_refused", refused(lambda: va.chunk_state(man, "changed", scenario, c, base)))
    changed_fields = {}
    for key, value in meta["settings"].items():
        mutated = copy.deepcopy(meta)
        mutated["settings"][key] = {"stale": value}
        save(chunk / "e2e_meta.json", mutated)
        changed_fields[key] = refused(lambda: va.chunk_state(man, md, scenario, c, base)) is not None
    save(chunk / "e2e_meta.json", meta)
    check("every_chunk_setting_bound", all(changed_fields.values()), changed_fields)
    missing_t = chunk / "T_1.csv"
    held = missing_t.read_bytes()
    missing_t.unlink()
    check("missing_required_T_is_partial", va.chunk_state(man, md, scenario, c, base) == "partial")
    missing_t.write_bytes(held)
    rows_path = chunk / "e2e_rows.jsonl"
    rows_saved = rows_path.read_text()
    rows_path.write_text(rows_saved + json.dumps(row | {"trial_id": 0}) + "\n")
    check("duplicate_rows_refused", refused(lambda: va.chunk_state(man, md, scenario, c, base)))
    rows_path.write_text(rows_saved + json.dumps(row | {"trial_id": 2}) + "\n")
    check("out_of_chunk_rows_refused", refused(lambda: va.chunk_state(man, md, scenario, c, base)))
    rows_path.write_text(rows_saved)
    pre_path = base / f"preflight_{md[:16]}.json"
    check("missing_preflight_refused", refused(lambda: va.require_preflight(base, md)))
    save(pre_path, {"manifest_digest": "stale", "runtime": runtime, "host": "mock-host"})
    check("stale_preflight_digest_refused", refused(lambda: va.require_preflight(base, md)))
    pre = {"manifest_digest": md, "runtime": runtime, "host": "mock-host"}
    save(pre_path, pre)
    with patch.object(va, "designs", return_value={}), patch.object(e2e, "knn_banks", return_value={}), \
            patch.object(e2e, "run_chunk") as runner:
        command(va.main, ["validate", str(mp), str(base), "0", "1", "1"])
        check("main_restart_skips_bound_complete", runner.call_count == 0)
        missing_t.unlink()
        check("main_restart_partial_refused", refused(lambda: command(va.main,
              ["validate", str(mp), str(base), "0", "1", "1"])))
        check("main_partial_refusal_precedes_rerun", runner.call_count == 0)
        missing_t.write_bytes(held)
    valid = cv.collect_scenario(man, md, scenario, base)
    check("collector_bound_chunk_uses_manifest_R", valid["counts"]["accept"] == 2 and
          valid["fit_failures"]["fitted_datasets"] == 2 * (2 * R + 1))
    # Legacy top-level metadata no longer determines R: actual manifest drives shape checks.
    save(chunk / "e2e_meta.json", meta | {"R_train": 2000})
    check("collector_ignores_stale_legacy_R", cv.collect_scenario(man, md, scenario, base) == valid)
    save(chunk / "e2e_meta.json", meta)
    dup = scenario | {"n_trials": 4, "chunks": [c, c]}
    check("collector_repeated_chunk_refused", refused(lambda: cv.collect_scenario(man, md, dup, base)))
    overlap = scenario | {"n_trials": 3, "chunks": [c, c | {"dir": "other", "trial_ids": [1, 2]}]}
    check("collector_overlapping_ids_refused", refused(lambda: cv.collect_scenario(man, md, overlap, base)))
    repeat_dir = scenario | {"n_trials": 4, "chunks": [c, c | {"trial_ids": [2, 4]}]}
    check("collector_repeat_directory_refused", refused(lambda: cv.collect_scenario(man, md, repeat_dir, base)))
    # Even a bound directory with short T vectors cannot borrow a stale R from its metadata.
    larger = man | {"R": 2000}
    save(chunk / "e2e_meta.json", {"manifest_digest": md,
         "settings": va.chunk_settings(larger, scenario, c), "R_train": R})
    short = cv.collect_scenario(larger, md, scenario, base)
    check("collector_short_T_vs_manifest_R_fails_closed", short["counts"]["indet_malformed"] == 2 and
          short["fit_failures"]["failed_datasets"] == 8002 and short["fit_stop"], short["fit_failures"])
    save(chunk / "e2e_meta.json", meta)

    sp = base / "summary.json"
    outdir = base / "empirical"
    summary = {"manifest_digest": md, "v_fail": False, "fit_stop": False,
               "labels_available": ["O2", "O3"], "runtime": runtime}
    save(sp, summary)
    check("empirical_guard_passing_summary", eq.guard(mp, base, sp, outdir) == summary)
    save(mp, man | {"budget": 1})
    check("empirical_guard_inplace_change_refused", refused(lambda: eq.guard(mp, base, sp, outdir)))
    save(mp, man)
    for field in ("v_fail", "fit_stop"):
        save(sp, summary | {field: True})
        check(f"empirical_guard_{field}_refused", refused(lambda: eq.guard(mp, base, sp, outdir)))
    save(sp, summary | {"runtime": runtime | {"R": "other-R"}})
    check("empirical_guard_runtime_receipt_mismatch_refused", refused(lambda: eq.guard(mp, base, sp, outdir)))
    save(sp, summary)
    with patch.object(eq, "designs", return_value={}), patch.object(e2e, "knn_banks", return_value={}), \
            patch.object(e2e, "run_chunk") as runner:
        command(eq.main, ["empirical", str(mp), str(base), str(sp), str(outdir), "1"])
        check("empirical_main_writes_binding_before_run", runner.call_count == 1 and
              json.loads((outdir / "e2e_meta.json").read_text())["manifest_digest"] == md)
        check("empirical_main_once_per_output_directory", refused(lambda: command(eq.main,
              ["empirical", str(mp), str(base), str(sp), str(outdir), "1"])))
        check("empirical_second_attempt_no_run", runner.call_count == 1)
    # These are accurately scoped limits, not regressions or proof of actual drift.
    limits["empirical_once_only"] = "Refuses a nonempty destination; not a global registry across other paths."
    limits["preflight_execution_binding"] = "Receipt is point-in-time evidence; require_preflight checks manifest digest, not live runtime, host, source or bank freshness."
    limits["restart_completion"] = "Requires T-file presence for fitted rows, not contents; collector validates contents and conservatively counts malformed files."
    limits["manifest_structure"] = "Overlap checking is within each scenario; actual frozen manifest has globally unique chunk directories and seeds."

    # The collector's real entrypoint writes the digest and runtime carried by
    # the guard, and preserves the power-fail/O2-O3 path without blocking Q1.
    power = copy.deepcopy(scenario)
    power.update(block=5, name="power", role="power", beta=0.97)
    power["chunks"][0].update(dir="power_chunk", seed=202)
    aggregate_man = man | {"scenarios": [scenario, power], "code_commit": "fixture-source"}
    aggregate_path = base / "aggregate_manifest.json"
    save(aggregate_path, aggregate_man)
    aggregate_digest = va.manifest_digest(aggregate_path)
    for s in aggregate_man["scenarios"]:
        ch = s["chunks"][0]
        target = base / ch["dir"]
        target.mkdir(exist_ok=True)
        save(target / "e2e_meta.json", {"manifest_digest": aggregate_digest,
             "settings": va.chunk_settings(aggregate_man, s, ch), "R_train": R})
        (target / "e2e_rows.jsonl").write_text(rows_saved)
        for i in range(2):
            (target / f"T_{i}.csv").write_bytes(held)
    save(base / f"preflight_{aggregate_digest[:16]}.json", pre | {"manifest_digest": aggregate_digest})
    aggregate_out = base / "aggregate_summary.json"
    command(cv.main, ["collector", str(aggregate_path), str(base), str(aggregate_out)])
    aggregate_summary = json.loads(aggregate_out.read_text())
    check("collector_main_digest_runtime_propagation", aggregate_summary["manifest_digest"] == aggregate_digest
          and aggregate_summary["runtime"] == runtime and aggregate_summary["host"] == "mock-host"
          and aggregate_summary["code_commit"] == "fixture-source")
    check("collector_main_power_fail_remains_labelled", aggregate_summary["v_fail"] is False and
          aggregate_summary["fit_stop"] is False and aggregate_summary["power_gate_pass"] is False
          and aggregate_summary["labels_available"] == ["O2", "O3"])
    check("collector_summary_accepted_by_empirical_guard", eq.guard(aggregate_path, base, aggregate_out,
          base / "new_empirical")["manifest_digest"] == aggregate_digest)

    # Exercise preflight itself without running R: real hashes and Python versions,
    # tiny files, and a mocked R-version subprocess response.
    srcroot = base / "src"
    srcroot.mkdir()
    (srcroot / "worker.py").write_text("pass\n")
    bank = base / "toybank"
    bank.mkdir()
    (bank / "shard").write_bytes(b"toy-bank")
    pins = {"numpy": np.__version__, "scipy": scipy.__version__, "nlme": "mock-nlme"}
    pm = man | {"source_sha256": {"worker.py": sha(srcroot / "worker.py")},
                "bank_sha256": {"shard": sha(bank / "shard")}, "runtime_pins": pins}
    pp = base / "preflight_manifest.json"
    save(pp, pm)
    args = ["preflight", str(pp), str(base), str(srcroot)]
    with patch.object(pf.subprocess, "run", return_value=SimpleNamespace(stdout="mock-R|mock-nlme")) as rcall:
        command(pf.main, args)
        receipt = json.loads((base / f"preflight_{va.manifest_digest(pp)[:16]}.json").read_text())
        check("preflight_actual_hashes_and_runtime_receipt", receipt["checked_source"] == 1 and
              receipt["checked_bank_shards"] == 1 and receipt["runtime"]["R"] == "mock-R")
        check("no_real_R_invocation", rcall.call_count == 1)
        for name, target in (("source", srcroot / "worker.py"), ("bank", bank / "shard"), ("stress", stress)):
            original = target.read_bytes()
            target.write_bytes(original + b"changed")
            check(f"preflight_changed_{name}_refused", refused(lambda: command(pf.main, args)))
            target.write_bytes(original)
        save(pp, pm | {"runtime_pins": pins | {"nlme": "other-nlme"}})
        check("preflight_pin_mismatch_refused", refused(lambda: command(pf.main, args)))

result = {"source_commit": "52779d0", "working_tree_commit_at_review": "ede7451",
          "manifest_digest": digest,
          "source_sha256": {n: sha(SRC / n) for n in
              ("validate.py", "collect_validation.py", "empirical_q1.py", "preflight.py")},
          "checks_passed": len(checks), "checks": checks, "limits": limits,
          "disposition": "PASS: requested binding and restart repairs; no current scientific/run blocker found in this scope.",
          "execution_scope": "Tiny synthetic local fixtures, mocked banks/run_chunk/R subprocess. No actual R, banks, remote work, population simulation or empirical T/p-value access."}
OUT.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"checks_passed": len(checks), "disposition": result["disposition"]}))
