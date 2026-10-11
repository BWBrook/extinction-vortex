"""Independent bounded fit-accounting repair audit (protocol 0.10, 11 Oct 2026).

Run with a Python environment containing NumPy/SciPy. Imports use the checkout
containing this script. All T matrices are synthetic, no trajectories or R fits
are generated, and no remote resources are accessed. Cases use valid bound
chunk metadata but do not exercise runtime/preflight or empirical execution.
Writes accounting_audit.json beside this script, including assertion results.
"""
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

import numpy as np

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "analysis/fable/calibration"
sys.path.insert(0, str(SRC))
import e2e_benchmark as e
import score_discrimination as score
import collect_validation as collect
from validate import chunk_settings

START = time.monotonic()
R = 20
WIDTH = 2 * R + 1
ROOT = Path(tempfile.mkdtemp(prefix="protocol10_accounting_repair_"))
RESULT = {
    "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
    "fixture_root": str(ROOT),
    "replicates_per_side": R,
    "scope": "synthetic T files; real scorer and collector; no R, banks, remote work, or empirical data",
    "source_sha256": {name: hashlib.sha256((SRC / name).read_bytes()).hexdigest()
                      for name in ("score_discrimination.py", "collect_validation.py", "e2e_benchmark.py", "validate.py")},
    "checks": [],
}
M = np.random.default_rng(52779).normal(size=(WIDTH, 4))
M[0] = M[1:R + 1].mean(axis=0)
TEMPLATES, LOGS = {}, {}


def check(name, condition, evidence):
    RESULT["checks"].append({"name": name, "pass": bool(condition), "evidence": evidence})
    print(("PASS " if condition else "FAIL ") + name, flush=True)


def template(name, matrix, flags=None):
    flags = (~np.isfinite(matrix).all(axis=1)).astype(int) if flags is None else flags
    path = ROOT / (name + ".csv")
    with path.open("w") as f:
        w = csv.writer(f)
        w.writerow(["set", "T1", "T2", "T3", "T4", "failed", "fallback"])
        for i, row in enumerate(matrix):
            w.writerow([i, *row, flags[i], 0])
    TEMPLATES[name] = path
    p = e.p_bounds(matrix, R)
    LOGS[name] = {"p_diagnostic": p.get("p_lo", "indeterminate"), "kth_dist": "{}", "outcome": e.outcome(p), **p}


template("good", M)
assert LOGS["good"]["outcome"] == "accept"
template("all_failed", np.full_like(M, np.nan))
nonfinite = M.copy()
nonfinite[-2:, 0] = [np.nan, np.inf]
template("unflagged_nonfinite", nonfinite, np.zeros(WIDTH))
flags = np.zeros(WIDTH)
flags[-1] = 1
template("flagged_finite", M, flags)
regions = M.copy()
regions[[0, 1, R + 1], 0] = np.nan
region_flags = np.zeros(WIDTH)
region_flags[[0, R + 2]] = 1
template("regions_union", regions, region_flags)
TEMPLATES["truncated"] = ROOT / "truncated.csv"
TEMPLATES["truncated"].write_text("set,T1,T2,T3,T4,failed,fallback\n0,1,1,1,1,0,0\n")
TEMPLATES["ragged"] = ROOT / "ragged.csv"
TEMPLATES["ragged"].write_text("set,T1,T2,T3,T4,failed,fallback\n0,1,1\n")


def case(name, n=1000, role="null", omitted=(), files=None, default="good", logs=None):
    files, logs, omitted = files or {}, logs or {}, set(omitted)
    base = ROOT / name
    directory = base / "chunk"
    directory.mkdir(parents=True)
    c = {"dir": "chunk", "trial_ids": [0, n], "seed": 7, "c": 0}
    s = {"block": 1 if role == "null" else 5 if role == "power" else 6,
         "name": name, "role": role, "n_trials": n, "beta": 0, "spec": {},
         "stress": False, "chunks": [c]}
    man = {"variant": "ar_cat", "R": R, "K": 50, "budget": 1000000,
           "bankdir": "unused_synthetic_bank", "scenarios": [s]}
    digest = hashlib.sha256(json.dumps(man, sort_keys=True).encode()).hexdigest()
    (directory / "e2e_meta.json").write_text(json.dumps({
        "manifest_digest": digest, "settings": chunk_settings(man, s, c), "R_train": R,
    }))
    with (directory / "e2e_rows.jsonl").open("w") as f:
        for i in range(n):
            selected_file = files.get(i, default)
            if selected_file is not None:
                os.link(TEMPLATES[selected_file], directory / f"T_{i}.csv")
            if i not in omitted:
                record = logs.get(i, LOGS.get(selected_file, LOGS[default]))
                f.write(json.dumps({"trial_id": i, **record}) + "\n")
    return man, digest, s, str(base), str(directory)


def collected(args):
    return collect.collect_scenario(*args[:4])


def counts_fixed(out, n):
    return out["n"] == n and sum(out["counts"][key] for key in score.OUTCOMES) == n


def summary(out):
    return {k: out[k] for k in ("n", "counts", "fit_failures", "fit_stop", "null_gate", "power_gate") if k in out}


# Reproduce the earlier 30/1000 missing-record defect using the real collector.
omitted = range(970, 1000)
for name, selected_file in (("missing_row_present_failed_T", "all_failed"), ("missing_row_no_T", None)):
    args = case(name, omitted=omitted, files={i: selected_file for i in omitted})
    out = collected(args)
    check(name, counts_fixed(out, 1000) and out["counts"]["missing"] == 30
          and out["fit_failures"] == {"failed_datasets": 30 * WIDTH, "fitted_datasets": 1000 * WIDTH,
                                     "flag_mismatches": 0, "rate": .03}
          and out["fit_stop"] is True and out["null_gate"]["pass"] is True, summary(out))

# No records or T outputs: unknown status is all failed on the fixed denominator.
args = case("absent_chunk")
empty_base = ROOT / "entirely_absent_base"
empty_base.mkdir()
out = collect.collect_scenario(*args[:3], str(empty_base))
check("absent_chunk_all_failed", counts_fixed(out, 1000) and out["counts"]["missing"] == 1000
      and out["fit_failures"]["failed_datasets"] == out["fit_failures"]["fitted_datasets"] == 1000 * WIDTH
      and out["fit_stop"] is True, summary(out))

# Retain missing or malformed T output despite a previously accepted JSON row.
for name, file_kind in (("missing_T_after_accept", None), ("truncated_T_after_accept", "truncated"),
                        ("ragged_T_after_accept", "ragged")):
    args = case(name, files={0: file_kind}, logs={0: LOGS["good"]})
    rows, cc, ff = score.score_dir("v3", args[4], range(1000), R)
    out = collected(args)
    check(name, rows[0]["outcome"] == "indet_malformed" and rows[0]["logged_outcome"] == "accept"
          and cc["indet_malformed"] == 1 and ff["failed_datasets"] == WIDTH
          and ff["fitted_datasets"] == 1000 * WIDTH and counts_fixed(out, 1000),
          {"retained_row": rows[0], "collector": summary(out)})

# Inconsistent flags cannot hide non-finite T cells; positive flags also count.
for name, kind, failed, mismatch in (("unflagged_nonfinite", "unflagged_nonfinite", 2, 2),
                                     ("flagged_finite", "flagged_finite", 1, 1)):
    args = case(name, default=kind)
    out = collected(args)
    check(name, counts_fixed(out, 1000) and out["fit_failures"]["failed_datasets"] == failed * 1000
          and out["fit_failures"]["flag_mismatches"] == mismatch * 1000
          and out["fit_failures"]["fitted_datasets"] == 1000 * WIDTH and out["fit_stop"] is True,
          summary(out))
args = case("observed_training_test_union", n=1, default="regions_union")
rows, cc, ff = score.score_dir("v3", args[4], range(1), R)
check("observed_training_test_union", ff == {"failed_datasets": 4, "fitted_datasets": WIDTH, "flag_mismatches": 3}
      and cc["indet_obsfit"] == 1, {"counts": cc, "failures": ff})

# Only explicit no-T sampling failures receive the no-fit exemption.
sampling = {"outcome": "indet_sampling", "sampling_failed": ["synthetic_population"]}
ids = range(980, 1000)
args = case("verified_sampling_exemption", files={i: None for i in ids}, logs={i: sampling for i in ids})
out = collected(args)
check("verified_sampling_exemption", counts_fixed(out, 1000) and out["counts"]["indet_sampling"] == 20
      and out["fit_failures"] == {"failed_datasets": 0, "fitted_datasets": 980 * WIDTH,
                                 "flag_mismatches": 0, "rate": 0.0}
      and out["fit_stop"] is False and out["null_gate"]["non_accepts"] == 20, summary(out))
for name, row, has_file in (("sampling_missing_failed_population", {"outcome": "indet_sampling"}, False),
                            ("sampling_with_T_file", sampling, True)):
    args = case(name, n=1, files={0: "good" if has_file else None}, logs={0: row})
    error = None
    try:
        score.score_dir("v3", args[4], range(1), R)
    except SystemExit as ex:
        error = str(ex)
    check(name, error is not None and "inconsistent sampling-failure record" in error, {"error": error})

# Exact threshold boundaries, preserving intended null and power denominators.
for role, n, failures in (("null", 1000, 19), ("null", 1000, 20), ("null", 1000, 21),
                           ("power", 300, 6), ("power", 300, 7), ("descriptive", 300, 7)):
    ids = range(failures)
    args = case(f"boundary_{role}_{failures}", n=n, role=role, omitted=ids,
                files={i: "all_failed" for i in ids})
    out = collected(args)
    expected_rate = failures / n
    expected_stop = expected_rate > .02
    check(f"fit_stop_boundary_{role}_{failures}_of_{n}", counts_fixed(out, n)
          and out["fit_failures"]["failed_datasets"] == failures * WIDTH
          and out["fit_failures"]["fitted_datasets"] == n * WIDTH
          and out["fit_failures"]["rate"] == expected_rate
          and (out.get("fit_stop") is expected_stop if role != "descriptive" else "fit_stop" not in out),
          summary(out))

# Valid T files still require matching logged results after malformed relaxation.
for name, altered in (("valid_T_wrong_outcome", {**LOGS["good"], "outcome": "reject"}),
                       ("valid_T_nan_logged_bound", {**LOGS["good"], "p_hi": float("nan")})):
    args = case(name, n=1, logs={0: altered})
    error = None
    try:
        score.score_dir("v3", args[4], range(1), R)
    except SystemExit as ex:
        error = str(ex)
    check(name, error is not None and "recomputed" in error, {"error": error})

RESULT["passed"] = sum(c["pass"] for c in RESULT["checks"])
RESULT["failed"] = sum(not c["pass"] for c in RESULT["checks"])
RESULT["elapsed_seconds"] = round(time.monotonic() - START, 3)
Path(__file__).with_suffix(".json").write_text(json.dumps(RESULT, indent=2) + "\n")
print(json.dumps({k: RESULT[k] for k in ("passed", "failed", "elapsed_seconds")}))
assert RESULT["failed"] == 0, "See accounting_audit.json for failed checks"
