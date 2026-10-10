"""Validation-pipeline tests with mocked T1-T4 fits (no R): stress sampling-budget failure,
selected-draw provenance, and chunk assembly/gates (Astra 0.9 review). Needs scipy and a
small bank built by build_bank.py. Run from repo root:
    python3 analysis/fable/calibration/test_validation.py TOYBANKDIR WORKDIR
Each check prints PASS/FAIL; the script exits non-zero on any failure."""
import json, os, shutil, sys
import numpy as np
sys.path.insert(0, "analysis/fable/calibration")
import e2e_benchmark as e2e
import collect_validation as cv
from bank import designs
from compare_nulls import clopper_pearson

fails = 0
R, K = 20, 50
calls = []
INJECT = {"failed_sets": 0}


def check(name, ok, detail=""):
    global fails
    fails += not ok
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


def mock_fits(path_in, path_out, workers):
    calls.append(path_in)
    rng = np.random.default_rng(len(calls))
    T = rng.normal(size=(2 * R + 1, 4))
    failed = np.zeros(2 * R + 1, int)
    for i in range(1, 1 + INJECT["failed_sets"]):
        T[i] = np.nan; failed[i] = 1
    with open(path_out, "w") as fh:
        fh.write('"set","T1","T2","T3","T4","failed","fallback"\n')
        for i in range(2 * R + 1):
            fh.write(",".join([str(i)] + [repr(float(x)) if np.isfinite(x) else "NA" for x in T[i]]
                              + [str(failed[i]), "0"]) + "\n")


e2e.run_fits = mock_fits
bankdir, work = sys.argv[1], sys.argv[2]
shutil.rmtree(work, ignore_errors=True)
des = designs()
banks = e2e.knn_banks(bankdir, "ar_cat", des, K)

# 1. Forced sampling-budget failure: terminates, keeps the parameter set, no replacement
dead = {"s": 1e-6, "f": 1e-6, "sigma": 0.5, "rho": 0.5, "p_c": 0.01, "delta": 0.7}
stress = {"0": {"wood_turtle_B": dead}, "1": {}}
d = f"{work}/stress"
calls.clear()
e2e.run_chunk(banks, des, "ar_cat", d, [0, 1], R, K, 2, 5, 0.0, {}, stress, budget=400_000)
rows = [json.loads(l) for l in open(f"{d}/e2e_rows.jsonl")]
check("stress: one row per intended trial, no replacement", [r["trial_id"] for r in rows] == [0, 1])
check("stress: budget failure is indet_sampling", rows[0]["outcome"] == "indet_sampling"
      and rows[0]["sampling_failed"] == ["wood_turtle_B"])
check("stress: failed parameter set retained", rows[0]["fixed"]["wood_turtle_B"] == dead)
check("stress: no fits for the failed trial", len(calls) == 1 and calls[0].endswith("sets_1.csv"))
check("stress: successful trial uses the standard procedure",
      rows[1]["outcome"] in ("accept", "reject", "indet_straddle") and "kth_dist" in rows[1])

# 2. Selected-draw provenance for M_D and M_O
d = f"{work}/md"
e2e.run_chunk(banks, des, "ar_cat", d, [0], R, K, 2, 6, 0.0, {"drift": {"form": "step", "hi": 2.0}})
r = json.loads(open(f"{d}/e2e_rows.jsonl").readline())
sel = r["selected"]["marmot"]
check("M_D provenance: shift and step time of the selected draw",
      0 <= sel["params"]["md_shift"] <= 2 and sel["params"]["md_tau"] >= 1 and "rho" in sel["params"])
d = f"{work}/mo"
e2e.run_chunk(banks, des, "ar_cat", d, [0], R, K, 2, 7, 0.0, {"detect": "lown"})
r = json.loads(open(f"{d}/e2e_rows.jsonl").readline())
ok = all(len(v["latent"]) == len(v["recorded"]) and all(a <= b for a, b in zip(v["recorded"][1:], v["latent"][1:]))
         for v in r["selected"].values())
check("M_O provenance: latent and recorded counts per population", ok)

# 3. Chunk assembly and gates
man = {"scenarios": [
    {"block": 1, "name": "null", "role": "null", "n_trials": 4, "beta": 0.0, "spec": {}, "stress": False,
     "chunks": [{"c": c, "seed": 10 + c, "dir": f"{work}/b01/c{c:02d}", "trial_ids": [2 * c, 2 * c + 2]}
                for c in range(2)]},
    {"block": 5, "name": "power", "role": "power", "n_trials": 2, "beta": 0.97, "spec": {}, "stress": False,
     "chunks": [{"c": 0, "seed": 20, "dir": f"{work}/b05/c00", "trial_ids": [0, 2]}]}]}
INJECT["failed_sets"] = 3
for s in man["scenarios"]:
    for c in s["chunks"]:
        os.makedirs(c["dir"], exist_ok=True)
        json.dump({"R_train": R}, open(f"{c['dir']}/e2e_meta.json", "w"))
        e2e.run_chunk(banks, des, "ar_cat", c["dir"], list(range(*c["trial_ids"])), R, K, 2, c["seed"], s["beta"])
INJECT["failed_sets"] = 0
res = cv.collect_scenario(man["scenarios"][0])
check("collector: complete denominators", sum(res["counts"][k] for k in ("accept", "reject", "missing")) +
      sum(v for k, v in res["counts"].items() if k.startswith("indet_")) == 4)
check("collector: fit-failure rate over observed+training+test datasets",
      res["fit_failures"] == {"failed_datasets": 12, "fitted_datasets": 4 * (2 * R + 1),
                              "rate": 12 / (4 * (2 * R + 1))})
rp = f"{work}/b01/c01/e2e_rows.jsonl"
keep = open(rp).read().splitlines()
open(rp, "w").write(keep[0] + "\n")
check("collector: a missing trial stays in the denominator", cv.collect_scenario(man["scenarios"][0])["counts"]["missing"] == 1)
open(rp, "w").write("\n".join(keep + [keep[0]]) + "\n")
try:
    cv.collect_scenario(man["scenarios"][0]); check("collector: duplicate refused", False)
except SystemExit:
    check("collector: duplicate refused", True)
extra = json.loads(keep[0]); extra["trial_id"] = 99
open(rp, "w").write("\n".join(keep + [json.dumps(extra)]) + "\n")
try:
    cv.collect_scenario(man["scenarios"][0]); check("collector: row outside the chunk refused", False)
except SystemExit:
    check("collector: row outside the chunk refused", True)
check("gates: 60/1000 passes and 61 fails the 0.08 upper bound",
      clopper_pearson(60, 1000, 0.025)[1] <= 0.08 < clopper_pearson(61, 1000, 0.025)[1])
check("gates: 224/300 passes and 223 fails the 0.70 lower bound",
      clopper_pearson(224, 300, 0.10)[0] >= 0.70 > clopper_pearson(223, 300, 0.10)[0])

# 4. Observed-data path (synthetic substitute) and the empirical guard
rng = np.random.default_rng(3)
fake = {n: np.array(e2e.fresh_selected(dd, "ar_cat", rng)["recorded"]) for n, dd in des.items()}
d = f"{work}/observed"
e2e.run_chunk(banks, des, "ar_cat", d, [7], R, K, 2, 8, observed=fake)
r = json.loads(open(f"{d}/e2e_rows.jsonl").readline())
check("observed path: given series are the outer dataset",
      r["trial_id"] == 7 and all(r["selected"][n]["recorded"] == fake[n].tolist() for n in des)
      and r["outcome"] in ("accept", "reject", "indet_straddle"))
import empirical_q1
mp = f"{work}/m.json"
for name, summ in (("missing summary", None),
                   ("V-fail", {"manifest": mp, "v_fail": True, "fit_stop": False}),
                   ("other manifest", {"manifest": "/x.json", "v_fail": False, "fit_stop": False})):
    sp = f"{work}/summary_{len(name)}.json"
    if summ is not None:
        json.dump(summ, open(sp, "w"))
    try:
        empirical_q1.guard(mp, sp); check(f"empirical guard refuses: {name}", False)
    except SystemExit:
        check(f"empirical guard refuses: {name}", True)
json.dump({"manifest": mp, "v_fail": False, "fit_stop": False, "labels_available": ["O2", "O3"]},
          open(f"{work}/ok.json", "w"))
check("empirical guard accepts a passing summary for the same manifest",
      empirical_q1.guard(mp, f"{work}/ok.json")["labels_available"] == ["O2", "O3"])

print("FAILURES:", fails)
sys.exit(1 if fails else 0)
