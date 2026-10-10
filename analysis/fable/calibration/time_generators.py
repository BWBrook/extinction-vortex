"""Generation cost of fresh selected outer datasets (one trajectory per population) for each
validation scenario: null, M_A, M_D forms, M_O forms, M_A + M_D mixtures and the three
fixed-parameter corners (from a scenarios.json written by run_dev_design.sh). Fitting cost
per dataset does not depend on the generator, so this is the generator-specific part of the
inventory. No bank, no fitting.

Usage: python time_generators.py CORNERS_JSON OUTJSON N_OUTER PROCS [SEED]
"""
import os, sys, json, time
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bank import designs
from e2e_benchmark import fresh_selected
from bank import DETECT

BETA_MIN = 0.9745192683713976
MD_HI = 2.0


def scenarios(corners_json):
    sc = [("null", {}, 0.0), ("MA_betamin", {}, BETA_MIN)]
    for form in ("linear", "accel", "step"):
        sc.append((f"MD_{form}", {"drift": {"form": form, "hi": MD_HI}}, 0.0))
        sc.append((f"MA+MD_{form}", {"drift": {"form": form, "hi": MD_HI}}, BETA_MIN))
    for law in DETECT:
        sc.append((f"MO_{law}", {"detect": law}, 0.0))
    for c in json.load(open(corners_json)):
        if c.get("fixed"):
            sc.append((c["name"], {"fixed": c["fixed"]}, 0.0))
    return sc


def task(args):
    i, name, spec, beta, n_outer, seed = args
    rng = np.random.default_rng(seed * 100 + i)
    des = designs()
    det = DETECT[spec["detect"]] if "detect" in spec else None
    per_pop = {n: 0.0 for n in des}
    latent_alive = 0
    t0 = time.process_time()
    for _ in range(n_outer):
        for n, d in des.items():
            t = time.process_time()
            rec, lat = fresh_selected(d, "ar_cat", rng, beta, spec.get("fixed", {}).get(n),
                                      spec.get("drift"), det)
            per_pop[n] += time.process_time() - t
            latent_alive += int(lat is not None and lat[-1] > 1)
    total = time.process_time() - t0
    return {"scenario": name, "beta": beta, "n_outer": n_outer, "cpu_s_per_dataset": total / n_outer,
            "cpu_s_per_pop": {n: v / n_outer for n, v in per_pop.items()},
            "latent_extant_at_endpoint": latent_alive if det is not None else None}


def main():
    corners_json, outjson, n_outer, procs = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 20261030
    jobs = [(i, n, s, b, n_outer, seed) for i, (n, s, b) in enumerate(scenarios(corners_json))]
    with Pool(procs) as pool:
        res = pool.map(task, jobs, chunksize=1)
    json.dump({"seed": seed, "n_outer": n_outer, "md_hi": MD_HI, "beta_min": BETA_MIN, "results": res},
              open(outjson, "w"), indent=1)
    for r in res:
        print(f"{r['scenario']:24s} {r['cpu_s_per_dataset']:8.2f} CPU-s/dataset"
              + (f"  latent extant {r['latent_extant_at_endpoint']}" if r["latent_extant_at_endpoint"] is not None else ""))


if __name__ == "__main__":
    main()
