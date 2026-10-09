"""Summarise an outer_coverage.py run. Per scenario: per-population and all-nine coverage
for the measured 10% thinned bank (0.1x) and actual bank (1x), and projections for larger
banks; then all-nine coverage over bank multiple x tolerance, and the effective tolerance a
k-NN library would need.

Projection for an m-fold bank: success when d_(K/m) <= tol (expected neighbour counts scale
linearly with bank size; MAD changes are ignored). The 0.1x projection, d_(10K) <= tol, is
printed beside the measured 0.1x value as a check. Projected values are planning numbers.

Usage: python coverage_summary.py OUTDIR
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compare_nulls import clopper_pearson

MULTS = (3, 10, 30, 100)
TOLS = (1.0, 1.25, 1.5, 2.0, 3.0)


def main():
    outdir = sys.argv[1]
    cov = json.load(open(os.path.join(outdir, "coverage.json")))
    meta = cov["meta"]
    K, M, tol, ks = meta["K"], meta["M"], meta["tol"], meta["ks"]
    names = list(dict.fromkeys(t["pop"] for t in cov["tasks"]))
    cols = ["0.1x", "0.1x (proj.)", "1x"] + [f"{m}x (proj.)" for m in MULTS]
    for v, b in meta["scenarios"]:
        zs = {n: np.load(os.path.join(outdir, f"cov_{v}_b{b:g}_{n}.npz")) for n in names}
        d = lambda n, k: zs[n]["knn_full"][:, ks.index(k)]
        print(f"\n## {v}, beta = {b:g} ({'M_A' if b else 'null'}), M = {M}, K = {K}, tol = {tol:g}\n")
        print("| Population | " + " | ".join(cols) + " |")
        print("|---|" + "---:|" * len(cols))
        ok = {c: np.ones(M, bool) for c in cols}
        for n in names:
            succ = {"0.1x": zs[n]["knn_sub"] <= tol, "0.1x (proj.)": d(n, 10 * K) <= tol,
                    "1x": d(n, K) <= tol}
            succ |= {f"{m}x (proj.)": d(n, round(K / m)) <= tol for m in MULTS}
            for c in cols:
                ok[c] &= succ[c]
            print(f"| {n} | " + " | ".join(f"{succ[c].mean():.4f}" for c in cols) + " |")
        cells = []
        for c in cols:
            k = int(ok[c].sum()); lo, hi = clopper_pearson(k, M)
            cells.append(f"**{k / M:.4f}** [{lo:.4f}, {hi:.4f}]")
        print("| **All nine** (95% CP) | " + " | ".join(cells) + " |")

        print("\nAll-nine coverage by bank multiple (rows) and tolerance (columns):\n")
        print("| Bank multiple (k = K/m) | " + " | ".join(f"tol {t:g}" for t in TOLS) + " |")
        print("|---|" + "---:|" * len(TOLS))
        for m in (1,) + MULTS:
            k = round(K / m)
            cells = [f"{np.all([d(n, k) <= t for n in names], axis=0).mean():.4f}" for t in TOLS]
            print(f"| {m}x ({k}) | " + " | ".join(cells) + " |")
        print("\nk-NN library (no hard tolerance): largest K-th neighbour distance across the nine,\n"
              "projected by bank multiple (quantiles over outer datasets):\n")
        qs = (0.5, 0.9, 0.95, 0.99, 0.999)
        print("| Bank multiple | " + " | ".join(f"q{q:g}" for q in qs) + " |")
        print("|---|" + "---:|" * len(qs))
        for m in (1,) + MULTS:
            worst = np.max([d(n, round(K / m)) for n in names], axis=0)
            print(f"| {m}x | " + " | ".join(f"{x:.2f}" for x in np.quantile(worst, qs)) + " |")


if __name__ == "__main__":
    main()
