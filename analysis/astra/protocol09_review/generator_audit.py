"""Small immutable-source checks for protocol 0.9; no banks, R, or remote work.

Run with the existing NumPy/SciPy environment:
  /home/bwbrook/papers/dsipa-dev/.venv/bin/python analysis/astra/protocol09_review/generator_audit.py
Only test_bank.py's draw counts are reduced in its temporary execution copy.
"""
import contextlib
import csv
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[3]
NEW, OLD = "f74f4f7", "fb28d8a"
PREFIX = "analysis/fable/calibration/"
results = []
hashes = {}


def source(commit, path):
    data = subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT)
    hashes[f"{commit}:{path}"] = hashlib.sha256(data).hexdigest()
    return data


def check(name, condition, details=None):
    results.append({"check": name, "pass": bool(condition), "details": details})
    if not condition:
        raise AssertionError(name)


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    out = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(out)
    return out


def write_T(path, matrix):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["set", "T1", "T2", "T3", "T4", "failed", "fallback"])
        w.writerows([i, *row, 0, 0] for i, row in enumerate(matrix))


t0 = time.monotonic()
with tempfile.TemporaryDirectory(prefix="vortex-protocol09-audit-") as tmp:
    tmp = Path(tmp)
    src = tmp / PREFIX
    src.mkdir(parents=True)
    for name in ("bank.py", "e2e_benchmark.py", "score_discrimination.py", "test_bank.py"):
        (src / name).write_bytes(source(NEW, PREFIX + name))
    oldpath = tmp / "old_bank.py"
    oldpath.write_bytes(source(OLD, PREFIX + "bank.py"))
    data_path = tmp / "data/raw/williams2021/population_data.csv"
    data_path.parent.mkdir(parents=True)
    data_path.write_bytes(source(NEW, "data/raw/williams2021/population_data.csv"))
    os.chdir(tmp)
    sys.path.insert(0, str(src))
    import bank
    import e2e_benchmark as e2e
    old = module(oldpath, "old_bank")
    designs = bank.designs()

    # Compare all nine fixed census designs, both active environmental variants,
    # and null/M_A at the same seed. All returned parameter arrays are checked.
    parity = []
    for name, design in designs.items():
        for variant in ("iid", "ar_cat"):
            for beta in (0.0, 0.9745192683713976):
                a = old.simulate_chunk(design, variant, 2000, np.random.default_rng(609), beta=beta)
                b = bank.simulate_chunk(design, variant, 2000, np.random.default_rng(609), beta=beta)
                ok = all(np.array_equal(a[i], b[i]) for i in (0, 2, 3))
                ok &= all(np.array_equal(a[1][key], b[1][key]) for key in a[1])
                parity.append({"population": name, "variant": variant, "beta": beta, "equal": bool(ok)})
    check("unchanged null and M_A: 36 configurations x 2000 draws", all(x["equal"] for x in parity), parity)

    test_text = (src / "test_bank.py").read_text()
    reduced = test_text.replace("40_000", "5_000").replace("200_000", "5_000")
    assert reduced != test_text
    (src / "test_bank_small.py").write_text(reduced)
    run = subprocess.run([sys.executable, str(src / "test_bank_small.py")], text=True, capture_output=True,
                         cwd=tmp, timeout=45)
    check("existing limiting tests at 5000 draws per simulation", run.returncode == 0,
          {"stdout": run.stdout, "stderr": run.stderr, "count_replacements": {"40000": 5000, "200000": 5000}})

    # Deterministic recording of the two vital-rate calls tests the actual
    # annual propagation, including gaps, rather than only drift_offset().
    fixed = {"s": .7, "f": .25, "sigma": .4, "rho": .6, "p_c": 0., "delta": 0., "nu": np.inf}
    original_draw, original_innov = bank.draw_params, bank.innovations

    class Recorder:
        def __init__(self):
            self.survival, self.recruitment = [], []
        def uniform(self, low, high, n):
            return np.full(n, .8)
        def integers(self, low, high, n):
            return np.full(n, 2)
        def random(self, n):
            return np.ones(n)
        def binomial(self, n, p):
            self.survival.append(p.copy())
            return n.copy()
        def poisson(self, lam):
            self.recruitment.append(lam.copy())
            return np.zeros(len(lam), dtype=np.int64)

    propagation = []
    try:
        bank.draw_params = lambda variant, n, rng: {k: np.full(n, v) for k, v in fixed.items()}
        for form in ("linear", "accel", "step"):
            for beta in (0., .9745192683713976):
                call = [0]
                def innovation(p, n, rng):
                    call[0] += 1
                    return np.full(n, 1. if call[0] == 1 else 0.)
                bank.innovations = innovation
                rng = Recorder()
                rec, params, over, sel = bank.simulate_chunk(
                    {"years": [2000, 2002, 2005], "counts": [20, 10, 0]},
                    "ar_cat", 3, rng, beta=beta, drift={"form": form, "hi": 2.})
                ts = np.arange(1, 6)
                offset = {"linear": .8 * ts / 5, "accel": .8 * (ts / 5) ** 2,
                          "step": .8 * (ts >= 2)}[form]
                ze = .6 ** (ts - 1) - offset
                g = np.exp(-beta * (1 / 20 - 1 / 50))
                st = 1 / (1 + np.exp(-(np.log(.7 / .3) + .4 * ze + np.log(g))))
                lam = 20 * .25 * g * np.exp(.4 * ze - .4 ** 2 / 2)
                ok = np.allclose(np.array(rng.survival)[:, 0], st, atol=1e-14, rtol=1e-14)
                ok &= np.allclose(np.array(rng.recruitment)[:, 0], lam, atol=1e-14, rtol=1e-14)
                propagation.append({"form": form, "beta": beta, "correct": bool(ok)})
        check("actual annual M_D and mixture vital rates, AR state and gap propagation", all(x["correct"] for x in propagation), propagation)
    finally:
        bank.draw_params, bank.innovations = original_draw, original_innov

    # Verify the same main generator state is left after observation sampling,
    # compared with a null run at the specified latent initial count.
    streams = []
    for law, detect in bank.DETECT.items():
        design = designs["golden_plover"]
        latent_design = {"years": design["years"], "counts": design["counts"].copy()}
        latent_design["counts"][0] = round(design["counts"][0] / float(detect(design["counts"][0])))
        r1, r2 = np.random.default_rng(111), np.random.default_rng(111)
        a = bank.simulate_chunk(design, "ar_cat", 5000, r1, detect=detect)
        b = bank.simulate_chunk(latent_design, "ar_cat", 5000, r2)
        ok = np.array_equal(a[1]["latent"], b[0]) and r1.bit_generator.state == r2.bit_generator.state
        streams.append({"law": law, "equal": bool(ok), "selected": int(a[3].sum()),
                        "selected_latently_extant": int((a[1]["latent"][a[3], -1] > 1).sum())})
    check("M_O latent path and main RNG unchanged at its specified latent initial count", all(x["equal"] for x in streams), streams)

    # Tiny synthetic statistic fixtures exercise the actual scorer script.
    R = 20
    matrix = np.random.default_rng(82).normal(size=(2 * R + 1, 4))
    sc = e2e.p_bounds(matrix, R)
    assert sc["status"] == "ok"
    runroot = tmp / "score_fixtures"
    for fmt in ("v1", "v2"):
        arm = runroot / fmt
        arm.mkdir(parents=True)
        rows = []
        for i in range(3):
            write_T(arm / f"T_{i}.csv", matrix)
            rows.append({"outer": i, "p": sc["p_lo"], "shortfall": "", "max_lib_dist": {},
                         "p_lo": sc["p_lo"], "p_hi": sc["p_hi"], "p_diagnostic": sc["p_lo"],
                         "outcome": e2e.outcome(sc), "kth_dist": {}})
        (arm / "e2e_results.json").write_text(json.dumps({"meta": {"R_train": R}, "outer": rows}))
        (arm / "e2e_meta.json").write_text(json.dumps({"R_train": R}))
        (arm / "e2e_rows.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        command = [sys.executable, str(src / "score_discrimination.py"), fmt, str(runroot), "3", str(tmp / f"{fmt}.csv"), fmt]
        run = subprocess.run(command, text=True, capture_output=True, timeout=10)
        summary = json.loads(run.stdout) if run.returncode == 0 else {}
        check(f"{fmt} scorer retains all three rows (no bounds-loop shadow)",
              run.returncode == 0 and summary[fmt]["missing"] == 0 and summary[fmt][e2e.outcome(sc)] == 3,
              {"summary": summary, "stderr": run.stderr})
        for key in (("p",) if fmt == "v1" else ("p_lo", "p_hi")):
            badrows = [dict(r) for r in rows]
            badrows[1][key] = float("nan")
            (arm / "e2e_results.json").write_text(json.dumps({"meta": {"R_train": R}, "outer": badrows}))
            (arm / "e2e_rows.jsonl").write_text("".join(json.dumps(r) + "\n" for r in badrows))
            run = subprocess.run(command, text=True, capture_output=True, timeout=10)
            check(f"{fmt} rejects logged NaN {key} on second row", run.returncode != 0 and "outer 1" in run.stderr
                  and "does not match logged nan" in run.stderr, {"stderr": run.stderr})

    # Return-value probe, deliberately no simulation: the selected metadata
    # exists at the generator boundary and is discarded by fresh_selected.
    real_simulate = e2e.simulate_chunk
    p = {"md_shift": np.array([.6, .8]), "md_tau": np.array([2, 3]),
         "latent": np.array([[20, 8, 0], [20, 6, 3]])}
    e2e.simulate_chunk = lambda *a, **kw: (np.array([[20, 8, 2], [20, 6, 1]]), p,
                                          np.zeros(2, bool), np.array([False, True]))
    try:
        md_return = e2e.fresh_selected({}, "ar_cat", None, drift={"form": "step", "hi": 2.})
        mo_return = e2e.fresh_selected({}, "ar_cat", None, detect=bank.DETECT["lown"])
    finally:
        e2e.simulate_chunk = real_simulate
    check("provenance gap reproduced: M_D draw discarded at e2e boundary",
          len(md_return) == 2 and md_return[1] is None,
          {"available_md_shift": .8, "available_md_tau": 3, "returned": [md_return[0].tolist(), md_return[1]]})
    check("M_O full selected latent path returned to main", np.array_equal(mo_return[1], p["latent"][1]),
          {"note": "main writes only latent_final at lines 155-156; this probe does not run main or R"})

receipt = {
    "reviewed_commit": subprocess.check_output(["git", "rev-parse", NEW], cwd=ROOT, text=True).strip(),
    "comparison_commit": subprocess.check_output(["git", "rev-parse", OLD], cwd=ROOT, text=True).strip(),
    "time_hobart": datetime.now(ZoneInfo("Australia/Hobart")).isoformat(),
    "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
    "source_sha256": hashes,
    "elapsed_seconds": round(time.monotonic() - t0, 3),
    "checks": results,
    "scope": "Immutable git-show copies; max 5000 paths per call; no R, banks, remote work, or archived raw-statistic replay.",
    "finding": {"severity": "medium", "file": PREFIX + "e2e_benchmark.py", "lines": [38, 45, 152, 156, 194],
                "description": "M_D md_shift/md_tau are only transient simulator arrays and discarded by fresh_selected; M_O full latent counts are transient and only endpoint is persisted. Protocol lines 531 and 542 say kept per draw. Persist selected draw metadata before validation or narrow the contract explicitly."},
}
target = ROOT / "analysis/astra/protocol09_review/generator_audit.json"
target.write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({"checks_passed": len(results), "elapsed_seconds": receipt["elapsed_seconds"], "receipt": str(target)}, indent=2))
