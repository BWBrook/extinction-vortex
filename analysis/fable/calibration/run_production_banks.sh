#!/usr/bin/env bash
# Designated banks for the validation freeze package (synthetic only): primary ar_cat,
# stability ar_cat and iid sensitivity banks (2e9 draws per population each, frozen seed
# families 8.1e12 / 8.2e12 / 8.3e12 + task), then beta_min and corners by the fixed recipe on
# the primary bank, the empirical K-th-neighbour positions, and generator timings for the
# recomputed corners. Usage: run_production_banks.sh RUNDIR PROCS
set -euo pipefail
RUN=$1; P=$2
SRC=$RUN/src/analysis/fable/calibration
python3 $SRC/build_bank.py $RUN/bank_primary 100000000 20 $P ar_cat 8100000000 > $RUN/bank_primary.log 2>&1
python3 $SRC/build_bank.py $RUN/bank_stability 100000000 20 $P ar_cat 8200000000 > $RUN/bank_stability.log 2>&1
python3 $SRC/build_bank.py $RUN/bank_iid 100000000 20 $P iid 8300000000 > $RUN/bank_iid.log 2>&1
python3 $SRC/effect_target.py $RUN/bank_primary ar_cat $RUN/effect 2000 100000 2000000 20261031 > $RUN/effect.log 2>&1
python3 $SRC/empirical_position.py $RUN/bank_primary ar_cat 2000 > $RUN/empirical_position_ar_cat.json
python3 $SRC/empirical_position.py $RUN/bank_iid iid 2000 > $RUN/empirical_position_iid.json
python3 - "$RUN" <<'PY'
import json, sys
run = sys.argv[1]
e = json.load(open(f"{run}/effect/effect_target_ar_cat.json"))
json.dump([{"name": f"ar_cat_{c}", "variant": "ar_cat", "beta": 0.0,
            "fixed": {n: v["theta"] for n, v in pops.items()}} for c, pops in e["corners"].items()],
          open(f"{run}/corners.json", "w"), indent=1)
PY
python3 $SRC/time_generators.py $RUN/corners.json $RUN/gen_times.json 20 13 20261032 > $RUN/gen_times.log 2>&1
echo DONE
