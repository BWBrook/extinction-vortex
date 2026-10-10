"""Empirical Q1 test (protocol §7; freeze package §7): the frozen procedure applied once to
the nine observed series, on the primary bank, with replicate stream 9.5e12 + ANALYSIS_ID.

It refuses to run unless VALIDATION_SUMMARY is a collect_validation.py output for this
manifest with no V-fail and no fit stop. Not to be run before the validation freeze.
The secondary per-statistic p_k (Holm) are not implemented here.

Usage: python empirical_q1.py MANIFEST VALIDATION_SUMMARY OUTDIR ANALYSIS_ID
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e2e_benchmark as e2e
from bank import designs

STREAM = 95 * 10 ** 11


def guard(man_path, summary_path):
    if not os.path.exists(summary_path):
        raise SystemExit("no validation summary: the empirical test runs only after validation")
    s = json.load(open(summary_path))
    if os.path.abspath(s.get("manifest", "")) != os.path.abspath(man_path):
        raise SystemExit("validation summary is for a different manifest")
    if s.get("v_fail") is not False or s.get("fit_stop") is not False:
        raise SystemExit("validation did not pass (V-fail or fit stop): no labelled empirical test")
    return s


def main():
    man_path, summary_path, outdir, a = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    summary = guard(man_path, summary_path)
    man = json.load(open(man_path))
    des = designs()
    banks = e2e.knn_banks(man["bankdir"], man["variant"], des, man["K"])
    os.makedirs(outdir, exist_ok=True)
    json.dump({"manifest": man_path, "validation_summary": summary_path, "analysis_id": a,
               "seed": STREAM + a, "R_train": man["R"], "R_test": man["R"], "K": man["K"],
               "labels_available": summary["labels_available"]},
              open(os.path.join(outdir, "e2e_meta.json"), "w"), indent=1)
    e2e.run_chunk(banks, des, man["variant"], outdir, [a], man["R"], man["K"], man["workers"], STREAM + a,
                  observed={n: d["counts"] for n, d in des.items()})


if __name__ == "__main__":
    main()
