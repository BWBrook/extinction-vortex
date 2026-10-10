"""Bounded protocol-0.9 audit: immutable sources, shell fixtures, no science runs."""
import hashlib
import json
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
REV = "f74f4f7c1c5e72dbae854eaa6cef93abdeafa8ec"
CAL = "analysis/fable/calibration/"


def source(path):
    return subprocess.check_output(["git", "show", f"{REV}:{path}"], cwd=ROOT)


def main():
    paths = [CAL + p for p in ("run_arms.sh", "run_production_banks.sh", "build_bank.py",
                              "time_generators.py", "e2e_benchmark.py", "score_discrimination.py")]
    out = {"revision": REV, "scope": "Immutable source and completed timing archive only. No remote calls, simulation, or R.",
           "sha256": {p: hashlib.sha256(source(p)).hexdigest() for p in paths}}
    out["shell_syntax"] = {}
    for p in paths[:2]:
        result = subprocess.run(["bash", "-n"], input=source(p), capture_output=True)
        out["shell_syntax"][p] = {"exit": result.returncode, "stderr": result.stderr.decode()}

    # The bank builder's formula is explicitly BASE_SEED * 1000 + task index.
    bank_seeds = {label: [base * 1000 + i for i in range(9 * 20)]
                  for label, base in (("primary", 8100000000), ("stability", 8200000000), ("iid", 8300000000))}
    flat = [x for seeds in bank_seeds.values() for x in seeds]
    out["bank_seeds"] = {label: {"first": seeds[0], "last": seeds[-1], "tasks": len(seeds)}
                         for label, seeds in bank_seeds.items()}
    out["bank_seeds_unique"] = len(flat) == len(set(flat))
    val = [9000000000000 + 1000000 * b + c for b in range(1, 18) for c in range(10)]
    out["validation_seeds"] = {"chunk_index_assumption": "c=0..9 (package does not choose zero- or one-based)",
                               "count": len(val), "unique": len(val) == len(set(val)),
                               "disjoint_primary_banks": not set(val).intersection(flat)}
    out["shared_sensitivity_family"] = {"family": 8700000000000,
        "uses_in_protocol": ["F&H-length windows", "wild-dog fills x2", "identical-count mask"],
        "finding": "No task suballocation is given. Separate build_bank invocations restart task index at zero."}

    out["launcher_fixtures"] = {}
    stub = '''import json, pathlib, sys
out = pathlib.Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True)
n = int(sys.argv[4]); mode = out.name
rows = n - 1 if mode == "short" else n
with (out / "e2e_rows.jsonl").open("w") as f:
    for k in range(rows):
        row = {"outer": 0 if mode == "duplicate" else k, "outcome": "indet_train" if mode == "all_unresolved" else "accept", "fit_failures": 4001 if mode == "all_unresolved" else 0}
        f.write(json.dumps(row) + "\\n")
raise SystemExit(7 if mode == "exit7" else 0)
'''
    with tempfile.TemporaryDirectory(prefix="vortex-run-contract-") as tmp:
        root = pathlib.Path(tmp)
        runner = root / "run_arms.sh"
        runner.write_bytes(source(CAL + "run_arms.sh"))
        for mode in ("normal", "short", "exit7", "duplicate", "all_unresolved"):
            run = root / mode
            src = run / "src" / CAL
            src.mkdir(parents=True)
            (src / "e2e_benchmark.py").write_text(stub)
            result = subprocess.run(["bash", str(runner), str(run), "unused-bank", "ar_cat", "3", "1",
                                     mode, "9000001000000", "0", "-"], capture_output=True, text=True)
            out["launcher_fixtures"][mode] = {"exit": result.returncode,
                                               "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
    expected = {"normal": 0, "short": 1, "exit7": 1, "duplicate": 0, "all_unresolved": 0}
    assert all(out["launcher_fixtures"][k]["exit"] == v for k, v in expected.items())
    out["launcher_interpretation"] = "Driver catches child-process failure and incomplete line count. DONE means transport completion only; it neither validates trial IDs nor evaluates scientific gates. These fixtures do not assert that such outputs occurred in real runs."

    timing = json.loads(source(CAL + "alt_check_v1/gen_times.json"))
    times = [r["cpu_s_per_dataset"] for r in timing["results"]]
    out["generator_timing"] = {"scenarios": len(times), "datasets_per_scenario": timing["n_outer"],
        "minimum_cpu_s": min(times), "maximum_cpu_s": max(times),
        "maximum_fraction_of_1370_cpu_s": max(times) / 1370,
        "scope": "Outer generation only; no bank loading, neighbour selection, reference fitting or covariance.",
        "beta_min": timing["beta_min"],
        "fixed_in_timing_source": "BETA_MIN = 0.9745192683713976; designated-bank effect output is not consumed."}
    out["source_unchanged_since_package_code"] = {}
    for p in paths:
        if p.endswith(("run_arms.sh", "run_production_banks.sh")):
            continue
        old = subprocess.check_output(["git", "show", f"a31e5bc:{p}"], cwd=ROOT)
        out["source_unchanged_since_package_code"][p] = source(p) == old
    out["pending_contract"] = [
        "A manifest mapping scenario, chunk, stream, parameters, intended count and output directory; a final fixed-denominator scenario aggregation and gate report.",
        "Fit-failure rate denominator: T-output failed flag counts a four-statistic dataset; final scenario accounting must cover observed, training and test replicates, including incomplete trials.",
        "Concurrency ceiling: run_arms starts every supplied arm concurrently; the measured 28 GB per process and 125 GB host prohibit launching all ten chunks together.",
        "Unique suballocation for repeated sensitivity-family 8.7e12 jobs, or explicit intended stream reuse.",
        "All-scenario end-to-end cost remains projected; 13 generator-only timings cannot establish total equality to within one percent."
    ]
    target = pathlib.Path(__file__).with_suffix(".json")
    target.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"output": str(target), "bank_seeds_unique": out["bank_seeds_unique"],
                      "launcher_fixtures": {k: v["exit"] for k, v in out["launcher_fixtures"].items()},
                      "generator_timing": out["generator_timing"]}, indent=2))


if __name__ == "__main__":
    main()
