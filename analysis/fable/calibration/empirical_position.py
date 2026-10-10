"""K-th nearest-neighbour distance of each population's observed calibration summaries C
(exposure E20; no T1-T4) in a variant's bank, and the largest across the nine: the
empirical position that protocol §3.4 step 3 reports against the radius strata.
With COVDIR (an outer_coverage.py run) and SCENARIO, also the share of that scenario's
outer datasets whose largest radius is at most the empirical one.

Usage: python empirical_position.py BANKDIR VARIANT [K] [COVDIR SCENARIO]
"""
import os, sys, json
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bank import designs, calib_features, load_bank


def main():
    bankdir, variant = sys.argv[1], sys.argv[2]
    K = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
    out = {}
    for n, d in designs().items():
        c = calib_features(load_bank(bankdir, variant, n)["rec"])
        mad = np.median(np.abs(c - np.median(c, axis=0)), axis=0)
        keep = mad > 0
        cobs = calib_features(d["counts"][None, :])[0]
        out[n] = float(cKDTree(c[:, keep] / mad[keep]).query(cobs[keep] / mad[keep], k=[K])[0][0])
    res = {"variant": variant, "K": K, "kth_dist": out, "largest": max(out.values())}
    if len(sys.argv) > 5:
        covdir, scen = sys.argv[4], sys.argv[5]
        ks = json.load(open(os.path.join(covdir, "coverage.json")))["meta"]["ks"]
        worst = np.max([np.load(os.path.join(covdir, f"cov_{scen}_{n}.npz"))["knn_full"][:, ks.index(K)]
                        for n in out], axis=0)
        res |= {"scenario": scen, "share_at_or_below": float((worst <= res["largest"]).mean())}
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
