"""Write 20 synthetic nine-population datasets (one selected null trajectory per population,
catastrophe-null bank) for estimator timing. Synthetic only."""
import sys, csv
import numpy as np
sys.path.insert(0, "analysis/fable/calibration")
from bank_benchmark import designs
from bank_catastrophe_scan import bank_cat
rng = np.random.default_rng(20261013)
out = csv.writer(open(sys.argv[1], "w", newline=""))
out.writerow(["set", "pop", "year", "N"])
banks = {name: (d, bank_cat(d, 200000, rng)) for name, d in designs().items()}
for k in range(20):
    for name, (d, rec) in banks.items():
        row = rec[rng.integers(len(rec))]
        for y, v in zip(d["years"], row):
            out.writerow([k, name, y, int(v)])
