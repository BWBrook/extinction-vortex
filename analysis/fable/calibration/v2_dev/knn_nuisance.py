"""V2 mechanism diagnostic on v1 outputs (development evidence; no new outcomes generated).
Reconstructs each null trial's K-neighbourhood exactly (cKDTree query on the logged recorded
series against the frozen primary bank; only the R draws from it were random) and compares the
outer series with its library: true vs library nuisance parameters, and the outer non-final mean
log change (trend, not in C) vs the library's.
Usage: python knn_nuisance.py SRCROOT MANIFEST BASE OUT_JSON"""
import json, os, sys
import numpy as np
src, man_path, base, out = sys.argv[1:5]
sys.path.insert(0, os.path.join(src, "analysis/fable/calibration"))
from bank import designs, calib_features, load_bank, PARAM_NAMES
from e2e_benchmark import knn_banks
man = json.load(open(man_path)); K = man["K"]; des = designs()
blocks = [s for s in man["scenarios"] if s["role"] == "null"]
rows = {s["name"]: [json.loads(l) for c in s["chunks"] for l in open(os.path.join(base, c["dir"], "e2e_rows.jsonl"))]
        for s in blocks}
banks = knn_banks(os.path.join(base, man["bankdir"]), man["variant"], des, K)

def trend(rec):
    return np.diff(np.log(rec[:, :-1]), axis=1).mean(axis=1)

res = {"K": K, "note": "development diagnostic on exposed v1 outputs", "blocks": {}}
for name, rr in rows.items():
    rej = np.array([r["outcome"] == "reject" for r in rr])
    blk = {"n": len(rr), "populations": {}}
    for n, b in banks.items():
        params = load_bank(os.path.join(base, man["bankdir"]), man["variant"], n)
        obs = [np.array(r["selected"][n]["recorded"]) for r in rr]
        cobs = calib_features(np.array(obs))
        _, idx = b["tree"].query(cobs[:, b["keep"]] / b["mad"], k=K, workers=16)
        tr_lib = trend(b["rec"])[idx]
        tr_obs = trend(np.array(obs))
        pr = (tr_lib < tr_obs[:, None]).mean(1) + 0.5 * (tr_lib == tr_obs[:, None]).mean(1)
        z = (tr_obs - tr_lib.mean(1)) / tr_lib.std(1)
        d = {"trend_rank_mean": round(float(pr.mean()), 4), "trend_z_mean": round(float(z.mean()), 3),
             "trend_z_mean_rejected": round(float(z[rej].mean()), 3) if rej.any() else None,
             "trend_z_mean_accepted": round(float(z[~rej].mean()), 3)}
        for p in ("s", "f", "sigma"):
            true = np.array([r["selected"][n]["params"][p] for r in rr])
            lib = params[p][idx]
            d[f"{p}_true_mean"] = round(float(true.mean()), 4)
            d[f"{p}_libmedian_mean"] = round(float(np.median(lib, 1).mean()), 4)
            d[f"{p}_true_rank_in_lib"] = round(float((lib < true[:, None]).mean(1).mean()), 4)
        blk["populations"][n] = d
        del params
        print(name, n, d, flush=True)
    res["blocks"][name] = blk
json.dump(res, open(out, "w"), indent=1)
