"""Bounded missing-output/restart follow-up at protocol-0.10 candidate df946937.

Standalone synthetic fixture; no bank loads, R fits, empirical statistics or
remote actions. Assertions characterize the reviewed defects and are expected
to fail after repairs. Writes gate_followup.json beside this script. All
generated trial data live in a tempfile directory.
"""
import csv
import hashlib
import json
import pathlib
import sys
import tempfile

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[3]
SRC = REPO / "analysis/fable/calibration"
sys.path.insert(0, str(SRC))
import e2e_benchmark as e
import score_discrimination as sc
import validate as va
import empirical_q1 as eq

P = pathlib.Path(tempfile.mkdtemp(prefix="protocol10_gate_followup_"))
res = {
    "fixture_root": str(P),
    "reviewed_commit": "df9469377db01268c8c4ddd11d9968b642928dab",
    "source_sha256": {n: hashlib.sha256((SRC / n).read_bytes()).hexdigest() for n in
                      ("e2e_benchmark.py", "score_discrimination.py", "validate.py", "empirical_q1.py")},
}
R = 20
M = np.random.default_rng(29).normal(size=(2 * R + 1, 4))
M[0] = M[1:R + 1].mean(axis=0)
pb = e.p_bounds(M, R)
assert e.outcome(pb) == "accept"
d = P / "chunk"
d.mkdir()
tp = d / "T_0.csv"
with tp.open("w") as f:
    w = csv.writer(f)
    w.writerow(["set", "T1", "T2", "T3", "T4", "failed", "fallback"])
    for i, row in enumerate(M):
        w.writerow([i, *row, 0, 0])
(d / "e2e_rows.jsonl").write_text(json.dumps({
    "trial_id": 0, "p_diagnostic": pb["p_lo"], "kth_dist": "{}",
    "outcome": "accept", **pb,
}) + "\n")
(d / "e2e_meta.json").write_text(json.dumps({"R_train": R, "R_test": R, "K": 50}))
original = tp.read_bytes()
tp.unlink()
try:
    sc.score_dir("v3", str(d), range(1))
    res["missing_T_after_success"] = "returned"
except SystemExit as ex:
    res["missing_T_after_success"] = "SystemExit: " + str(ex)
tp.write_text("set,T1,T2,T3,T4,failed,fallback\n0,1,1,1,1,0,0\n")
try:
    sc.score_dir("v3", str(d), range(1))
    res["malformed_T_after_success"] = "returned"
except SystemExit as ex:
    res["malformed_T_after_success"] = "SystemExit: " + str(ex)

# A one-trial restart fixture isolates the row-completeness predicate; all
# parameters match its metadata, so the malformed T file is the only defect.
stress = P / "stress.json"
stress.write_text('{"sets": {}}')
mp = P / "manifest.json"
man = {
    "R": R, "K": 50, "workers": 1, "bankdir": "UNUSED", "variant": "ar_cat",
    "budget": 1000000, "stress_sets": str(stress), "scenarios": [{
        "block": 1, "name": "synthetic_restart_fixture", "role": "null", "n_trials": 1,
        "beta": 0, "spec": {}, "stress": False,
        "chunks": [{"dir": str(d), "trial_ids": [0, 1], "seed": 7, "c": 0}],
    }],
}
mp.write_text(json.dumps(man))
oldargv, old_des, old_knn, old_run = sys.argv, va.designs, va.e2e.knn_banks, va.e2e.run_chunk
calls = []
try:
    sys.argv = ["validate.py", str(mp), "0", "1"]
    va.designs = lambda: {}
    va.e2e.knn_banks = lambda *args: {}
    va.e2e.run_chunk = lambda *args, **kwargs: calls.append("ran")
    va.main()
    res["restart_malformed_T"] = {"returned_success": True, "run_chunk_calls": len(calls)}
finally:
    sys.argv, va.designs, va.e2e.knn_banks, va.e2e.run_chunk = oldargv, old_des, old_knn, old_run
    tp.write_bytes(original)

# An empirical substitute proves that existing output does not block the
# entry point. The fit writer is mocked; no observed counts or fits are read.
sp = P / "summary.json"
sp.write_text(json.dumps({
    "manifest": str(mp), "v_fail": False, "fit_stop": False, "labels_available": ["O2", "O3"],
}))
out = P / "empirical_rerun"
out.mkdir()
(out / "e2e_rows.jsonl").write_text('{"trial_id": 1, "outcome": "accept"}\n')
(out / "T_1.csv").write_text("KEEP EXISTING\n")
oldargv, old_des, old_knn, old_run = sys.argv, eq.designs, eq.e2e.knn_banks, eq.e2e.run_chunk
calls = []


def fake_run(*args, **kwargs):
    calls.append("ran")
    pathlib.Path(args[3], "T_1.csv").write_text("OVERWRITTEN\n")


try:
    sys.argv = ["empirical_q1.py", str(mp), str(sp), str(out), "1"]
    eq.designs = lambda: {}
    eq.e2e.knn_banks = lambda *args: {}
    eq.e2e.run_chunk = fake_run
    eq.main()
    res["empirical_existing_output"] = {
        "run_chunk_calls": len(calls), "old_T_overwritten": (out / "T_1.csv").read_text() == "OVERWRITTEN\n",
    }
finally:
    sys.argv, eq.designs, eq.e2e.knn_banks, eq.e2e.run_chunk = oldargv, old_des, old_knn, old_run

for key in ("missing_T_after_success", "malformed_T_after_success"):
    assert res[key].startswith("SystemExit: ")
    assert "recomputed outcome indet_malformed != logged accept" in res[key]
assert res["restart_malformed_T"] == {"returned_success": True, "run_chunk_calls": 0}
assert res["empirical_existing_output"] == {"run_chunk_calls": 1, "old_T_overwritten": True}
res["characterization_assertions_passed"] = True
pathlib.Path(__file__).with_suffix(".json").write_text(json.dumps(res, indent=2) + "\n")
print(json.dumps(res, indent=2))
