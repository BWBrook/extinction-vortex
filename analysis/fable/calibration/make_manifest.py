"""Write the validation run manifest (protocol §4.3; freeze package §6) and draw the
fixed-mixture stress parameter sets once. The manifest is host-independent: the bank,
stress sets and chunk directories are paths relative to the run directory BASE given to
preflight.py, validate.py, collect_validation.py and empirical_q1.py. It embeds the SHA-256
of the run's source files, of every bank shard and of the stress sets, and pins the NumPy,
SciPy and nlme versions.

Blocks b = 1..17, each split into 10 chunks c with seed 9e12 + 1e6*b + c and contiguous
trial IDs. Corners and beta_min come from the effect-target JSON computed on the primary
bank; stress parameter sets are drawn once, uniformly from each population's empirical
library (seed 9e12 + 1e6*17 + 999), and retained with their library indices.

Usage: python make_manifest.py EFFECT_JSON LIBRARIES_NPZ BANK_SHA256_LIST BASE OUT_MANIFEST SRCROOT CODE_COMMIT
(writes BASE/stress_sets.json; BANK_SHA256_LIST is `sha256sum` output for the primary bank's
shards; SRCROOT is the staged repository root)
"""
import hashlib, json, math, os, sys
import numpy as np

FREE = ("s", "f", "sigma", "rho", "p_c", "delta")
MD_HI = 2.0
CHUNKS = 10
SEED_BASE = 9 * 10 ** 12
BANKDIR, ROOT, STRESS = "bank_primary", "validation_v1", "stress_sets.json"
SOURCES = [f"analysis/fable/calibration/{f}" for f in (
    "bank.py", "e2e_benchmark.py", "tstats_batch.R", "score_discrimination.py", "compare_nulls.py",
    "validate.py", "preflight.py", "collect_validation.py", "run_validation.sh", "empirical_q1.py",
    "make_manifest.py")] + ["data/raw/williams2021/population_data.csv"]
RUNTIME_PINS = {"numpy": "1.26.4", "scipy": "1.11.4", "nlme": "3.1.171"}


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    effect_json, lib_npz, bank_list, base, out_manifest, src, commit = sys.argv[1:8]
    e = json.load(open(effect_json))
    bmin = e["beta_min"]["beta"]
    corners = {c: {n: v["theta"] for n, v in pops.items()} for c, pops in e["corners"].items()}
    d10 = lambda x: -math.log(1 - x) / 0.08
    blocks = [
        (1, "null_prior_predictive", 0.0, {}, 1000, "null"),
        (2, "null_high_sigma", 0.0, {"fixed": corners["high_sigma"]}, 1000, "null"),
        (3, "null_low_s", 0.0, {"fixed": corners["low_s"]}, 1000, "null"),
        (4, "null_strong_env", 0.0, {"fixed": corners["strong_env"]}, 1000, "null"),
        (5, "MA_betamin", bmin, {}, 300, "power"),
        (6, "MA_2betamin", 2 * bmin, {}, 300, "descriptive"),
        (7, "MD_linear", 0.0, {"drift": {"form": "linear", "hi": MD_HI}}, 300, "descriptive"),
        (8, "MD_accel", 0.0, {"drift": {"form": "accel", "hi": MD_HI}}, 300, "descriptive"),
        (9, "MD_step", 0.0, {"drift": {"form": "step", "hi": MD_HI}}, 300, "descriptive"),
        (10, "MO_lown", 0.0, {"detect": "lown"}, 300, "descriptive"),
        (11, "MO_uniform", 0.0, {"detect": "uniform"}, 300, "descriptive"),
        (12, "MA_MD_linear", bmin, {"drift": {"form": "linear", "hi": MD_HI}}, 300, "descriptive"),
        (13, "MA_MD_accel", bmin, {"drift": {"form": "accel", "hi": MD_HI}}, 300, "descriptive"),
        (14, "MA_MD_step", bmin, {"drift": {"form": "step", "hi": MD_HI}}, 300, "descriptive"),
        (15, "MA_d10_0.3", d10(0.3), {}, 300, "descriptive"),
        (16, "MA_d10_0.5", d10(0.5), {}, 300, "descriptive"),
        (17, "stress_fitted_parameters", 0.0, {}, 300, "stress"),
    ]
    scen = []
    for b, name, beta, spec, n, role in blocks:
        size = n // CHUNKS
        scen.append({"block": b, "name": name, "beta": beta, "spec": spec, "n_trials": n, "role": role,
                     "stress": role == "stress",
                     "chunks": [{"c": c, "seed": SEED_BASE + 10 ** 6 * b + c,
                                 "dir": f"{ROOT}/b{b:02d}_{name}/c{c:02d}",
                                 "trial_ids": [c * size, (c + 1) * size]} for c in range(CHUNKS)]})
    lib = np.load(lib_npz)
    pops = sorted({k.split("__")[0] for k in lib.files})
    srng = np.random.default_rng(SEED_BASE + 10 ** 6 * 17 + 999)
    sets = {}
    for tid in range(300):
        sets[str(tid)] = {}
        for n in pops:
            j = int(srng.integers(len(lib[f"{n}__s"])))
            sets[str(tid)][n] = {"library_index": j, "theta": {k: float(lib[f"{n}__{k}"][j]) for k in FREE}}
    stress_path = os.path.join(base, STRESS)
    json.dump({"seed": SEED_BASE + 10 ** 6 * 17 + 999, "library_sha256": sha(lib_npz), "sets": sets},
              open(stress_path, "w"), indent=1)
    banks = {os.path.basename(f): h for h, f in (l.split() for l in open(bank_list) if l.strip())}
    banks["bank_meta.json"] = sha(os.path.join(base, BANKDIR, "bank_meta.json"))
    json.dump({"variant": "ar_cat", "R": 2000, "K": 2000, "budget": 10 ** 6, "code_commit": commit,
               "bankdir": BANKDIR, "bank_sha256": banks, "stress_sets": STRESS,
               "stress_sets_sha256": sha(stress_path), "effect_sha256": sha(effect_json),
               "source_sha256": {f: sha(os.path.join(src, f)) for f in SOURCES},
               "runtime_pins": RUNTIME_PINS, "beta_min": bmin, "scenarios": scen},
              open(out_manifest, "w"), indent=1)
    print(f"{len(scen)} scenarios, {sum(len(s['chunks']) for s in scen)} chunks, "
          f"{sum(s['n_trials'] for s in scen)} trials")


if __name__ == "__main__":
    main()
