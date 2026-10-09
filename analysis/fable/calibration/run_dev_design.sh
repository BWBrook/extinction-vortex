#!/usr/bin/env bash
# Development design run on the 10x banks (synthetic only): effect target and corners under
# ar_cat; library radii for prior-predictive, M_A and corner scenarios; measured end-to-end
# cost at production replicate counts. Usage: run_dev_design.sh RUNDIR BANKDIR
set -euo pipefail
RUN=$1; BANKS=$2
SRC=$RUN/src/analysis/fable/calibration
python3 $SRC/effect_target.py $BANKS ar_cat $RUN/effect 2000 100000 2000000 20261020 > $RUN/effect.log 2>&1
python3 - "$RUN" <<'PY'
import json, sys
run = sys.argv[1]
e = json.load(open(f"{run}/effect/effect_target_ar_cat.json"))
bm = e["beta_min"]
sc = [{"name": "ar_cat_null", "variant": "ar_cat", "beta": 0.0},
      {"name": "ar_cat_MA_dev", "variant": "ar_cat", "beta": 8.66},
      {"name": "iid_null", "variant": "iid", "beta": 0.0},
      {"name": "iid_MA_dev", "variant": "iid", "beta": 8.66}]
if bm:
    sc.append({"name": "ar_cat_MA_betamin", "variant": "ar_cat", "beta": bm["beta"]})
for c, pops in e["corners"].items():
    sc.append({"name": f"ar_cat_{c}", "variant": "ar_cat", "beta": 0.0, "M": 2000,
               "fixed": {n: v["theta"] for n, v in pops.items()}})
json.dump(sc, open(f"{run}/scenarios.json", "w"), indent=1)
PY
python3 $SRC/outer_coverage.py $BANKS $RUN/coverage 20000 9 ar_cat,iid $RUN/scenarios.json 20261021 2000 > $RUN/coverage.log 2>&1
python3 $SRC/coverage_summary.py $RUN/coverage > $RUN/coverage_summary.md
/usr/bin/time -v python3 $SRC/e2e_benchmark.py $BANKS ar_cat $RUN/e2e_cost 4 2000 2000 32 20261022 > $RUN/e2e_cost.log 2> $RUN/e2e_cost.time
n=$(wc -l < $RUN/e2e_cost/e2e_rows.jsonl)
[ "$n" -eq 4 ] || { echo "INCOMPLETE e2e_cost: $n/4"; exit 1; }
echo DONE
