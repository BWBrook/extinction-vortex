"""Validation-pipeline tests with mocked T1-T4 fits (no R): stress sampling-budget failure,
selected-draw provenance, manifest binding (validate/collect/empirical guard), chunk
assembly and gates, and conservative fit accounting (Astra 0.9 and 0.10 reviews). Needs
scipy and a small bank built by build_bank.py. Run from repo root:
    python3 analysis/fable/calibration/test_validation.py TOYBANKDIR WORKDIR
Each check prints PASS/FAIL; the script exits non-zero on any failure."""
import hashlib, json, os, shutil, sys
import numpy as np
sys.path.insert(0, "analysis/fable/calibration")
import e2e_benchmark as e2e
import validate
import collect_validation as cv
import empirical_q1
from bank import designs
from compare_nulls import clopper_pearson
from score_discrimination import score_dir

fails = 0
R, K = 20, 50
calls = []
INJECT = {"failed_sets": 0, "unflagged_nan": 0}


def check(name, ok, detail=""):
    global fails
    fails += not ok
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


def raises(fn):
    try:
        fn()
        return False
    except SystemExit:
        return True


def mock_fits(path_in, path_out, workers):
    calls.append(path_in)
    rng = np.random.default_rng(len(calls))
    T = rng.normal(size=(2 * R + 1, 4))
    failed = np.zeros(2 * R + 1, int)
    for i in range(1, 1 + INJECT["failed_sets"]):
        T[i] = np.nan; failed[i] = 1
    for i in range(R + 1, R + 1 + INJECT["unflagged_nan"]):
        T[i, 0] = np.nan
    with open(path_out, "w") as fh:
        fh.write('"set","T1","T2","T3","T4","failed","fallback"\n')
        for i in range(2 * R + 1):
            fh.write(",".join([str(i)] + [repr(float(x)) if np.isfinite(x) else "NA" for x in T[i]]
                              + [str(failed[i]), "0"]) + "\n")


e2e.run_fits = mock_fits
bankdir, work = sys.argv[1], sys.argv[2]
shutil.rmtree(work, ignore_errors=True)
os.makedirs(work)
des = designs()
banks = e2e.knn_banks(bankdir, "ar_cat", des, K)

# 1. Forced sampling-budget failure: terminates, keeps the parameter set, no replacement
dead = {"s": 1e-6, "f": 1e-6, "sigma": 0.5, "rho": 0.5, "p_c": 0.01, "delta": 0.7}
d = f"{work}/stress"
calls.clear()
e2e.run_chunk(banks, des, "ar_cat", d, [0, 1], R, K, 2, 5, 0.0, {}, {"0": {"wood_turtle_B": dead}, "1": {}},
              budget=400_000)
rows = [json.loads(l) for l in open(f"{d}/e2e_rows.jsonl")]
check("stress: one row per intended trial, no replacement", [r["trial_id"] for r in rows] == [0, 1])
check("stress: budget failure is indet_sampling", rows[0]["outcome"] == "indet_sampling"
      and rows[0]["sampling_failed"] == ["wood_turtle_B"])
check("stress: failed parameter set retained", rows[0]["fixed"]["wood_turtle_B"] == dead)
check("stress: no fits for the failed trial", len(calls) == 1 and calls[0].endswith("sets_1.csv"))

# 2. Selected-draw provenance for M_D and M_O
d = f"{work}/md"
e2e.run_chunk(banks, des, "ar_cat", d, [0], R, K, 2, 6, 0.0, {"drift": {"form": "step", "hi": 2.0}})
sel = json.loads(open(f"{d}/e2e_rows.jsonl").readline())["selected"]["marmot"]
check("M_D provenance: shift and step time", 0 <= sel["params"]["md_shift"] <= 2 and sel["params"]["md_tau"] >= 1)
d = f"{work}/mo"
e2e.run_chunk(banks, des, "ar_cat", d, [0], R, K, 2, 7, 0.0, {"detect": "lown"})
r = json.loads(open(f"{d}/e2e_rows.jsonl").readline())
check("M_O provenance: latent and recorded counts", all(
    all(a <= b for a, b in zip(v["recorded"][1:], v["latent"][1:])) for v in r["selected"].values()))

# 3. A bound mini manifest run through validate.main
base = f"{work}/base"
os.makedirs(base)
os.symlink(os.path.abspath(bankdir), f"{base}/bank_primary")
json.dump({"seed": 0, "sets": {}}, open(f"{base}/stress_sets.json", "w"))
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
man = {"variant": "ar_cat", "R": R, "K": K, "budget": 10 ** 6, "bankdir": "bank_primary",
       "stress_sets": "stress_sets.json", "stress_sets_sha256": sha(f"{base}/stress_sets.json"),
       "scenarios": [
           {"block": 1, "name": "null", "role": "null", "n_trials": 4, "beta": 0.0, "spec": {}, "stress": False,
            "chunks": [{"c": c, "seed": 10 + c, "dir": f"v/b01/c{c:02d}", "trial_ids": [2 * c, 2 * c + 2]}
                       for c in range(2)]},
           {"block": 5, "name": "power", "role": "power", "n_trials": 2, "beta": 0.97, "spec": {}, "stress": False,
            "chunks": [{"c": 0, "seed": 20, "dir": "v/b05/c00", "trial_ids": [0, 2]}]}]}
mp = f"{work}/manifest.json"
json.dump(man, open(mp, "w"))
digest = validate.manifest_digest(mp)
check("validate: refuses to run without a preflight receipt",
      raises(lambda: (setattr(sys, "argv", ["validate.py", mp, base, "0", "1", "2"]), validate.main())))
runtime = {"python": "3", "numpy": "1.26.4", "scipy": "1.11.4", "R": "R", "nlme": "3.1.171"}
json.dump({"manifest_digest": digest, "host": "test", "runtime": runtime},
          open(f"{base}/preflight_{digest[:16]}.json", "w"))
INJECT["failed_sets"] = 3
sys.argv = ["validate.py", mp, base, "0", "1", "2"]
validate.main()
INJECT["failed_sets"] = 0
n_calls = len(calls)
validate.main()
check("validate: a rerun skips bound complete chunks", len(calls) == n_calls)
res = cv.collect_scenario(man, digest, man["scenarios"][0], base)
check("collector: complete denominators", sum(v for k, v in res["counts"].items()
                                               if not k.startswith(("raw", "null_gate", "detections"))) == 4)
check("collector: fit failures over observed+training+test datasets",
      res["fit_failures"]["failed_datasets"] == 12 and res["fit_failures"]["fitted_datasets"] == 4 * (2 * R + 1))

# 4. Conservative fit accounting (Astra 0.10 fixtures)
c1 = f"{base}/v/b01/c01"
rows_p = f"{c1}/e2e_rows.jsonl"
keep = open(rows_p).read().splitlines()
open(rows_p, "w").write(keep[0] + "\n")
_, cc, ff = score_dir("v3", c1, range(2, 4), R)
check("missing row with a present T file: failures counted from the file",
      cc["missing"] == 1 and ff["failed_datasets"] == 6 and ff["fitted_datasets"] == 2 * (2 * R + 1))
os.rename(f"{c1}/T_3.csv", f"{c1}/T_3.bak")
_, cc, ff = score_dir("v3", c1, range(2, 4), R)
check("missing row and no T file: unknown status counted as all failed", ff["failed_datasets"] == 3 + 2 * R + 1)
os.rename(f"{c1}/T_3.bak", f"{c1}/T_3.csv")
open(rows_p, "w").write("\n".join(keep) + "\n")
lines = open(f"{c1}/T_2.csv").read().splitlines()
open(f"{c1}/T_2.csv", "w").write("\n".join(lines[:5]) + "\n")
rw, cc, ff = score_dir("v3", c1, range(2, 4), R)
check("truncated T after a logged row: indet_malformed, all failed, no abort",
      cc["indet_malformed"] == 1 and rw[0]["logged_outcome"] is not None and ff["failed_datasets"] == 3 + 2 * R + 1)
d = f"{work}/unflagged"
INJECT["unflagged_nan"] = 2
e2e.run_chunk(banks, des, "ar_cat", d, [0], R, K, 2, 9)
INJECT["unflagged_nan"] = 0
json.dump({"R_train": R}, open(f"{d}/e2e_meta.json", "w"))
_, cc, ff = score_dir("v3", d, [0], R)
check("unflagged non-finite T cells are counted", ff["failed_datasets"] == 2 and ff["flag_mismatches"] == 2)

# 5. Configuration binding
m2 = dict(man, R=2000, K=2000)
mp2 = f"{work}/manifest2.json"
json.dump(m2, open(mp2, "w"))
check("collector refuses chunks bound to other settings",
      raises(lambda: cv.collect_scenario(m2, validate.manifest_digest(mp2), m2["scenarios"][1], base)))
check("restart refuses chunks bound to another manifest",
      raises(lambda: validate.chunk_state(m2, validate.manifest_digest(mp2), m2["scenarios"][1],
                                          m2["scenarios"][1]["chunks"][0], base)))
dup = man["scenarios"][0] | {"chunks": [man["scenarios"][0]["chunks"][0]] * 2}
check("collector refuses overlapping chunks", raises(lambda: cv.collect_scenario(man, digest, dup, base)))
summ = {"manifest_digest": digest, "v_fail": False, "fit_stop": False, "labels_available": ["O2", "O3"],
        "runtime": runtime}
sp = f"{work}/summary.json"
json.dump(summ, open(sp, "w"))
check("empirical guard accepts a passing summary for this manifest and runtime",
      empirical_q1.guard(mp, base, sp, f"{work}/emp_new")["labels_available"] == ["O2", "O3"])
json.dump(dict(man, budget=5), open(mp, "w"))
check("empirical guard refuses after the manifest changes in place", raises(lambda: empirical_q1.guard(mp, base, sp, f"{work}/emp_new")))
json.dump(man, open(mp, "w"))
json.dump(summ | {"runtime": runtime | {"nlme": "3.1.170"}}, open(sp, "w"))
check("empirical guard refuses a different runtime", raises(lambda: empirical_q1.guard(mp, base, sp, f"{work}/emp_new")))
json.dump(summ | {"v_fail": True}, open(sp, "w"))
check("empirical guard refuses a V-fail", raises(lambda: empirical_q1.guard(mp, base, sp, f"{work}/emp_new")))
json.dump(summ, open(sp, "w"))
os.makedirs(f"{work}/emp_done"); open(f"{work}/emp_done/e2e_rows.jsonl", "w").write("{}\n")
check("empirical guard refuses a populated output directory", raises(lambda: empirical_q1.guard(mp, base, sp, f"{work}/emp_done")))

# 6. Observed-data path (synthetic substitute) and gate arithmetic
rng = np.random.default_rng(3)
fake = {n: np.array(e2e.fresh_selected(dd, "ar_cat", rng)["recorded"]) for n, dd in des.items()}
d = f"{work}/observed"
e2e.run_chunk(banks, des, "ar_cat", d, [7], R, K, 2, 8, observed=fake)
r = json.loads(open(f"{d}/e2e_rows.jsonl").readline())
check("observed path: given series are the outer dataset",
      r["trial_id"] == 7 and all(r["selected"][n]["recorded"] == fake[n].tolist() for n in des))
check("gates: 60/1000 passes and 61 fails the 0.08 upper bound",
      clopper_pearson(60, 1000, 0.025)[1] <= 0.08 < clopper_pearson(61, 1000, 0.025)[1])
check("gates: 224/300 passes and 223 fails the 0.70 lower bound",
      clopper_pearson(224, 300, 0.10)[0] >= 0.70 > clopper_pearson(223, 300, 0.10)[0])

print("FAILURES:", fails)
sys.exit(1 if fails else 0)
