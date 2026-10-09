"""Development scan: how calibration-tolerance choice drives bank size, and where the
observed calibration summaries sit within the selected prior-(b) predictive. Synthetic
draws only; observed C summaries are the same exposure as bank_benchmark.py."""
import sys, time
import numpy as np
sys.path.insert(0, "analysis/fable/calibration")
from bank_benchmark import designs, bank, calib_features

draws = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000
rng = np.random.default_rng(20261010)
tols = (0.25, 0.5, 1.0)
print(f"prior (b) draws per population: {draws}")
print("population        accepted  pct(msq) pct(ac) pct(inc)  " + "  ".join(f"q@{t:<4} J(K=2000)" for t in tols))
for name, d in designs().items():
    rec, par = bank(d, draws, rng)
    c = calib_features(rec); cobs = calib_features(d["counts"][None, :])[0]
    pct = [(c[:, k] < cobs[k]).mean() * 100 for k in range(3)]
    mad = np.median(np.abs(c - np.median(c, axis=0)), axis=0)
    dist = np.sqrt((((c - cobs) / mad) ** 2).sum(axis=1))
    a = len(rec) / draws
    cells = []
    for t in tols:
        q = (dist <= t).mean()
        cells.append(f"{q:.4f}  {2000 / (a * q) if q > 0 else float('inf'):9.3g}")
    print(f"{name:16s} {len(rec):8d}  {pct[0]:6.1f}  {pct[1]:6.1f}  {pct[2]:6.1f}   " + "  ".join(cells))
