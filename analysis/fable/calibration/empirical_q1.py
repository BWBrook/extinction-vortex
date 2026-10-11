"""Empirical Q1 test (protocol §7; freeze package §7): the frozen procedure applied once to
the nine observed series, on the primary bank, with replicate stream 9.5e12 + ANALYSIS_ID.

It refuses to run unless VALIDATION_SUMMARY is a collect_validation.py output whose manifest
digest equals this manifest's current digest, with no V-fail and no fit stop, and whose
recorded runtime equals this host's preflight runtime for the same manifest. It also refuses
an existing, non-empty OUTDIR, so the once-only run cannot be repeated or appended to. Not to
be run before the validation freeze. The secondary per-statistic p_k (Holm) are not
implemented here.

Usage: python empirical_q1.py MANIFEST BASE VALIDATION_SUMMARY OUTDIR ANALYSIS_ID
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e2e_benchmark as e2e
from bank import designs
from validate import manifest_digest, require_preflight

STREAM = 95 * 10 ** 11


def guard(man_path, base, summary_path, outdir):
    if not os.path.exists(summary_path):
        raise SystemExit("no validation summary: the empirical test runs only after validation")
    s = json.load(open(summary_path))
    digest = manifest_digest(man_path)
    if s.get("manifest_digest") != digest:
        raise SystemExit("validation summary is for a different manifest (digest mismatch)")
    if s.get("v_fail") is not False or s.get("fit_stop") is not False:
        raise SystemExit("validation did not pass (V-fail or fit stop): no labelled empirical test")
    require_preflight(base, digest)
    pre = json.load(open(os.path.join(base, f"preflight_{digest[:16]}.json")))
    if pre["runtime"] != s.get("runtime"):
        raise SystemExit("this host's runtime differs from the validation run's")
    if os.path.isdir(outdir) and os.listdir(outdir):
        raise SystemExit(f"{outdir} already holds results: the empirical test runs once")
    return s


def main():
    man_path, base, summary_path, outdir, a = sys.argv[1:5] + [int(sys.argv[5])]
    summary = guard(man_path, base, summary_path, outdir)
    man = json.load(open(man_path))
    des = designs()
    banks = e2e.knn_banks(os.path.join(base, man["bankdir"]), man["variant"], des, man["K"])
    os.makedirs(outdir, exist_ok=True)
    json.dump({"manifest_digest": summary["manifest_digest"], "validation_summary": summary_path,
               "analysis_id": a, "seed": STREAM + a, "R_train": man["R"], "R_test": man["R"], "K": man["K"],
               "labels_available": summary["labels_available"], "runtime": summary["runtime"]},
              open(os.path.join(outdir, "e2e_meta.json"), "w"), indent=1)
    e2e.run_chunk(banks, des, man["variant"], outdir, [a], man["R"], man["K"], 18, STREAM + a,
                  observed={n: d["counts"] for n, d in des.items()})


if __name__ == "__main__":
    main()
