"""Summarise an outer_coverage.py run: per scenario, the k-NN library radius (largest K-th
neighbour distance across the nine populations) for the bank as built (1x) and projected
for larger banks (d_(K/m) for an m-fold bank), the measured 10%-thinned bank (0.1x) beside
its projection d_(10K) as a check, per-population medians, and the share of outer datasets
whose largest radius is within a few reference distances. Projected rows are planning
numbers: they ignore future-bank and MAD variation.

Usage: python coverage_summary.py OUTDIR
"""
import json, os, sys
import numpy as np

QS = (0.5, 0.9, 0.95, 0.99, 0.999)
REFS = (0.5, 1.0, 1.5, 2.0)


def main():
    outdir = sys.argv[1]
    cov = json.load(open(os.path.join(outdir, "coverage.json")))
    meta = cov["meta"]
    K, ks, names = meta["K"], meta["ks"], meta["populations"]
    for sc in meta["scenarios"]:
        z = {n: np.load(os.path.join(outdir, f"cov_{sc['name']}_{n}.npz")) for n in names}
        d = lambda k: np.max([z[n]["knn_full"][:, ks.index(k)] for n in names], axis=0)
        rows = [("0.1x (measured)", np.max([z[n]["knn_sub"] for n in names], axis=0)),
                ("0.1x (projected)", d(10 * K)), ("1x (as built)", d(K)),
                ("3x (projected)", d(667)), ("10x (projected)", d(200))]
        print(f"\n## {sc['name']} (variant {sc['variant']}, beta {sc['beta']:g}"
              f"{', fixed parameters' if sc.get('fixed') else ''}), M = {sc.get('M', meta['M'])}, K = {K}\n")
        print("| Bank | " + " | ".join(f"q{q:g}" for q in QS) + " | " +
              " | ".join(f"≤ {r:g}" for r in REFS) + " |")
        print("|---|" + "---:|" * (len(QS) + len(REFS)))
        for lab, x in rows:
            print(f"| {lab} | " + " | ".join(f"{v:.2f}" for v in np.quantile(x, QS)) + " | " +
                  " | ".join(f"{(x <= r).mean():.4f}" for r in REFS) + " |")
        print("\nPer-population median K-th distance (1x): " +
              ", ".join(f"{n} {np.median(z[n]['knn_full'][:, ks.index(K)]):.2f}" for n in names))


if __name__ == "__main__":
    main()
