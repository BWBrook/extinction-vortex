"""Reconcile Fagan & Holmes (2006) Table 1 summaries with the Williams et al. (2021) series.

Bounded source check, not a reconstruction of F&H's fitted statistics. Inputs:
the Williams Dryad file population_data.csv (doi:10.5061/dryad.jwstqjq8c,
version 2, CC0; hash in source_manifest.csv), plus the F&H Table 1 values that
a T3 delegate transcribed from the author PDF into fh_table1.csv.

Definitions used for the three F&H columns (our reading of the table headings):
  increase = smallest census size from which the next available census was larger;
  start    = census size at the start of the final non-increasing run ending in the
             last non-zero census ("size when final decline began");
  final    = last non-zero census before the first zero.
Consecutive available censuses are used; missing years are reported, not filled.

Run from the repo root: python3 notes/t3/fh_table1_reconciliation.py
(default input: data/raw/williams2021/population_data.csv, CC0; its SHA-256 is
checked against notes/t3/source_manifest.csv before any value is read).
"""
import csv
import hashlib
import sys
from pathlib import Path

DEFAULT_INPUT = Path("data/raw/williams2021/population_data.csv")

PAIRS = {  # F&H id -> Williams id
    "FH01": "14", "FH02": "15", "FH03": "6", "FH04": "20", "FH05": "21",
    "FH06": "10", "FH07": "4", "FH08": "8", "FH09": "9",
}


def leading_int(text):
    digits = ""
    for ch in text.strip():
        if ch.isdigit():
            digits += ch
        elif digits:
            break
    return int(digits) if digits else None


def summarise(years, values):
    obs = [(y, v) for y, v in zip(years, values) if v is not None]
    zero_at = next(i for i, (_, v) in enumerate(obs) if v == 0)
    pre = obs[:zero_at]
    vals = [v for _, v in pre]
    rises = [a for a, b in zip(vals, vals[1:]) if b > a]
    k = len(vals) - 1
    while k > 0 and vals[k - 1] >= vals[k]:
        k -= 1
    span = range(pre[0][0], pre[-1][0] + 1)
    missing = [y for y in span if y not in {yy for yy, _ in pre}]
    return {
        "first_year": pre[0][0], "last_nonzero_year": pre[-1][0], "zero_year": obs[zero_at][0],
        "n_nonzero": len(pre), "missing_years": missing,
        "increase": min(rises) if rises else None, "start": vals[k], "final": vals[-1],
    }


def verify_hash(path, here):
    manifest = {r["file"]: r["sha256"] for r in csv.DictReader(open(here / "source_manifest.csv", newline="", encoding="utf-8"))}
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if digest != manifest.get(Path(path).name):
        sys.exit("input hash %s does not match source_manifest.csv; refusing to run" % digest)
    return digest


def main(path):
    here = Path(__file__).resolve().parent
    print("input sha256 verified:", verify_hash(path, here))
    fh = {r["fh_id"]: r for r in csv.DictReader(open(here / "fh_table1.csv", newline="", encoding="utf-8"))}
    rows = {r["ID"]: r for r in csv.DictReader(open(path, newline="", encoding="utf-8"))}
    year_cols = [c for c in next(iter(rows.values())) if c.isdigit()]
    total = 0
    print("fh_id W  years FH / W(first..last nonzero) / W(first..zero census)  n_nonzero  increase(FH/W)  start(FH/W)  final(FH/W)  missing_years")
    for fh_id, w_id in PAIRS.items():
        r = rows[w_id]
        vals = [None if r[c] in ("NULL", "") else float(r[c]) for c in year_cols]
        s = summarise([int(c) for c in year_cols], vals)
        f = fh[fh_id]
        w_years = s["last_nonzero_year"] - s["first_year"] + 1
        w_years_zero = s["zero_year"] - s["first_year"] + 1
        total += s["n_nonzero"]
        trio = [(leading_int(f["smallest_pop_from_which_increase"]), s["increase"]),
                (leading_int(f["pop_at_final_decline_start"]), s["start"]),
                (leading_int(f["final_pop_before_extinction"]), s["final"])]
        cells = ["%s/%s%s" % (a, "NA" if b is None else int(b), "" if (b is not None and a == int(b)) else " *")
                 for a, b in trio]
        print("%s %-3s %2s / %2d (%d-%d) / %2d (to %d)   %3d        %-14s %-12s %-12s %s" % (
            fh_id, w_id, f["years_monitored_FH"], w_years, s["first_year"], s["last_nonzero_year"],
            w_years_zero, s["zero_year"], s["n_nonzero"], cells[0], cells[1], cells[2], s["missing_years"] or "-"))
    print("total non-zero censuses in Williams series for the nine populations: %d (F&H text: 148;"
          " comparable only once each F&H window is settled)" % total)
    print("'*' marks a mismatch between F&H Table 1 and the value recomputed from the Williams series.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT)
