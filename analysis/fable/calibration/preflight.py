"""Preflight for validation on one host: verify that the staged source, the bank shards and
the stress sets match the hashes embedded in the frozen manifest, and that NumPy, SciPy and
R's nlme are the pinned versions; then write BASE/preflight_<digest16>.json (with the full
runtime, including the R version), which validate.py requires before any chunk runs and
the empirical guard compares with the validation run's.

Usage: python preflight.py MANIFEST BASE SRCROOT
(SRCROOT is the staged repository root holding analysis/fable/calibration and data/raw)
"""
import os, sys, json, hashlib, platform, time, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate import manifest_digest


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def main():
    man_path, base, src = sys.argv[1], sys.argv[2], sys.argv[3]
    man = json.load(open(man_path))
    digest = manifest_digest(man_path)
    bad = [f for f, h in man["source_sha256"].items() if sha(os.path.join(src, f)) != h]
    bad += [f for f, h in man["bank_sha256"].items() if sha(os.path.join(base, man["bankdir"], f)) != h]
    if sha(os.path.join(base, man["stress_sets"])) != man["stress_sets_sha256"]:
        bad.append(man["stress_sets"])
    if bad:
        raise SystemExit(f"preflight failed: {len(bad)} mismatched files, e.g. {bad[:5]}")
    import numpy, scipy
    r = subprocess.run(["Rscript", "-e", 'cat(R.version.string, as.character(packageVersion("nlme")), sep="|")'],
                       capture_output=True, text=True, check=True).stdout.split("|")
    runtime = {"python": platform.python_version(), "numpy": numpy.__version__, "scipy": scipy.__version__,
               "R": r[0], "nlme": r[1]}
    off = {k: (runtime[k], v) for k, v in man["runtime_pins"].items() if runtime[k] != v}
    if off:
        raise SystemExit(f"preflight failed: runtime differs from the pins: {off}")
    receipt = {"manifest_digest": digest, "host": platform.node(), "checked_source": len(man["source_sha256"]),
               "checked_bank_shards": len(man["bank_sha256"]), "runtime": runtime,
               "time": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    json.dump(receipt, open(os.path.join(base, f"preflight_{digest[:16]}.json"), "w"), indent=1)
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
