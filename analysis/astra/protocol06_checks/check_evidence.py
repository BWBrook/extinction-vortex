"""Deterministic audit of archived development results; no simulations or empirical tests."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CAL = ROOT / "analysis/fable/calibration"
rows = list(csv.DictReader((CAL / "compare_nulls_v1/comparison.csv").open()))
assert len(rows) == 45
assert len({(r["variant"], r["population"]) for r in rows}) == 45
print("Reviewed repository snapshot: 1813bfc")
print("Comparison: 45 unique variant/population rows; no new draws.")
print("Rule evaluated: 3 * archived upper draw requirement <= 1e9.")
for variant in dict.fromkeys(r["variant"] for r in rows):
    subset = [r for r in rows if r["variant"] == variant]
    required = [(r["population"], 3 * float(r["draws_for_K2000_upper"])) for r in subset]
    failures = [(name, n) for name, n in required if n > 1e9]
    print(f"{variant}: {9 - len(failures)}/9 within cap; maximum {max(n for _, n in required):,.0f}")
    for name, n in failures:
        print(f"  exceeds cap: {name}, {n:,.0f} draws")

print("\nArchived e2e_v1: classify tolerance shortfalls before interpreting diagnostic p.")
n_shortfall = 0
for variant in ("iid", "ar_cat"):
    result = json.loads((CAL / f"e2e_v1/e2e_results_{variant}.json").read_text())
    for row in result["outer"]:
        shortfall = bool(row["shortfall"])
        n_shortfall += shortfall
        status = "indeterminate (calibration shortfall)" if shortfall else "no recorded calibration/fit failure"
        print(f"{variant}, outer {row['outer']}: {status}; diagnostic p={row['p']:.6f}; fit failures={row['fit_failures']}")
assert n_shortfall == 3
print("Three of four synthetic outer trials contribute null failures under the specified rule.")
print("This is a reclassification of four development trials, not a validation rejection-rate estimate.")

manifest = dict(line.split(maxsplit=1)[::-1] for line in
                (CAL / "compare_nulls_v1/source_sha256.txt").read_text().splitlines())
recovered = Path(__file__).parent / "recovered_e2e_v1/e2e_benchmark.py"
digest = hashlib.sha256(recovered.read_bytes()).hexdigest()
assert digest == manifest["analysis/fable/calibration/e2e_benchmark.py"]
print(f"\nRecovered e2e_v1 source matches archived SHA-256: {digest}")
print("Source was recovered from the original deep-server run directory; it was an uncommitted overlay.")
