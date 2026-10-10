#!/usr/bin/env bash
# Run synthetic e2e arms concurrently on one bank set (each process holds the banks in
# memory), wait on every PID and verify each arm's checkpoint count.
# Usage: run_arms.sh RUNDIR BANKDIR VARIANT N_OUTER WORKERS ARM SEED BETA [SCENARIO_JSON|-] [ARM SEED BETA SCEN ...]
set -euo pipefail
RUN=$1; BANKS=$2; VAR=$3; NOUT=$4; W=$5; shift 5
SRC=$RUN/src/analysis/fable/calibration
pids=(); names=(); status=0
while [ $# -gt 0 ]; do
  arm=$1; seed=$2; beta=$3; scen=$4; shift 4
  extra=(); [ "$scen" != "-" ] && extra=("$scen")
  python3 $SRC/e2e_benchmark.py $BANKS $VAR $RUN/$arm $NOUT 2000 2000 $W $seed $beta "${extra[@]}" > $RUN/$arm.log 2>&1 &
  pids+=($!); names+=($arm)
done
for i in "${!pids[@]}"; do wait ${pids[$i]} || { echo "FAILED ${names[$i]}"; status=1; }; done
for a in "${names[@]}"; do
  n=$(wc -l < $RUN/$a/e2e_rows.jsonl 2>/dev/null || echo 0)
  [ "$n" -eq "$NOUT" ] || { echo "INCOMPLETE $a: $n/$NOUT"; status=1; }
done
[ $status -eq 0 ] && echo DONE
exit $status
