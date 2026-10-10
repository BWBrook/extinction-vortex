#!/usr/bin/env bash
# Development power screen (synthetic only) for the adopted ar_cat null with the k-NN library
# on the 10x banks, at production replicate counts: a null arm and M_A arms at beta_min,
# 2 beta_min, Delta10 = 0.3 and Delta10 = 0.5 (prior-predictive nuisances), N_OUTER each,
# at most three arms at once (each holds the banks in memory).
# Usage: run_power_screen.sh RUNDIR BANKDIR N_OUTER WORKERS
set -euo pipefail
RUN=$1; BANKS=$2; NOUT=$3; W=$4
SRC=$RUN/src/analysis/fable/calibration
arm() { python3 $SRC/e2e_benchmark.py $BANKS ar_cat $RUN/$1 $NOUT 2000 2000 $W $2 $3 > $RUN/$1.log 2>&1; }
status=0
run_wave() {
  local pids=() names=()
  while [ $# -gt 0 ]; do arm $1 $2 $3 & pids+=($!); names+=($1); shift 3; done
  for i in "${!pids[@]}"; do wait ${pids[$i]} || { echo "FAILED ${names[$i]}"; status=1; }; done
}
run_wave null 20261023 0 betamin 20261024 0.9745192683713976 beta2min 20261025 1.9490385367427951
run_wave d10_0.3 20261026 4.458436799234155 d10_0.5 20261027 8.664339756999317
for a in null betamin beta2min d10_0.3 d10_0.5; do
  n=$(wc -l < $RUN/$a/e2e_rows.jsonl 2>/dev/null || echo 0)
  [ "$n" -eq "$NOUT" ] || { echo "INCOMPLETE $a: $n/$NOUT"; status=1; }
done
[ $status -eq 0 ] && echo DONE
exit $status
