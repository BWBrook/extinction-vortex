"""Build sharded reference banks (protocol §3.4 step 1) for one or more null variants.

Each (variant, population, shard) task simulates SHARD_DRAWS prior-(b) draws with its own
seed and keeps the runs meeting the exact matched selection S and the cap event A. Shard
files keep the selected trajectories (int32 counts), parameters, global draw indices,
seed, draw count and overflow count. bank_meta.json records the layout that load_bank()
in bank.py verifies.

Usage: python build_bank.py OUTDIR SHARD_DRAWS SHARDS PROCS VARIANTS(comma list) BASE_SEED
Task seed = BASE_SEED * 1000 + task index.
"""
import os, sys, time, json
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bank import designs, simulate_chunk, PARAM_NAMES, CAP

CHUNK = 500_000


def task(args):
    outdir, variant, name, shard, shard_draws, seed = args
    d = designs()[name]
    rng = np.random.default_rng(seed)
    t0 = time.time()
    recs, pars, ids, n_over, done = [], {k: [] for k in PARAM_NAMES}, [], 0, 0
    while done < shard_draws:
        n = min(CHUNK, shard_draws - done)
        rec, p, over, sel = simulate_chunk(d, variant, n, rng)
        n_over += int(over.sum())
        recs.append(rec[sel].astype(np.int32))
        for k in PARAM_NAMES:
            pars[k].append(p[k][sel])
        ids.append(shard * shard_draws + done + np.flatnonzero(sel))
        done += n
    rec = np.concatenate(recs)
    np.savez_compressed(os.path.join(outdir, f"bank_{variant}_{name}_s{shard:03d}.npz"),
                        rec=rec, draw_id=np.concatenate(ids), seed=seed, draws=shard_draws,
                        overflow=n_over, **{k: np.concatenate(v) for k, v in pars.items()})
    return {"variant": variant, "population": name, "shard": shard, "seed": seed,
            "draws": shard_draws, "selected": len(rec), "overflow": n_over,
            "seconds": round(time.time() - t0, 1)}


def main():
    outdir, shard_draws, shards, procs = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    variants, base_seed = sys.argv[5].split(","), int(sys.argv[6])
    os.makedirs(outdir, exist_ok=True)
    names = list(designs())
    jobs = [(outdir, v, n, s, shard_draws, base_seed * 1000 + i) for i, (v, n, s) in
            enumerate((v, n, s) for v in variants for n in names for s in range(shards))]
    t0 = time.time()
    with Pool(procs) as pool:
        res = pool.map(task, jobs, chunksize=1)
    json.dump({"variants": variants, "populations": names, "shards": shards,
               "shard_draws": shard_draws, "base_seed": base_seed, "cap": CAP, "chunk": CHUNK,
               "numpy": np.__version__, "wall_seconds": round(time.time() - t0, 1), "tasks": res},
              open(os.path.join(outdir, "bank_meta.json"), "w"), indent=1)
    print(f"done: {len(res)} tasks in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
