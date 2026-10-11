#!/usr/bin/env bash
# Run the manifest's validation chunks on deep-server with NSLOTS concurrent bank-holding
# processes (at most three: about 28 GB each), after the preflight receipt exists; wait on
# every PID, then assemble and gate the results. DONE means the processes and the collector
# completed; the scientific outcome is in OUT_JSON.
# Usage: run_validation.sh MANIFEST BASE NSLOTS OUT_JSON [R_WORKERS]
set -euo pipefail
MAN=$1; BASE=$2; NS=$3; OUT=$4; W=${5:-18}
[ "$NS" -le 3 ] || { echo "at most 3 bank-holding processes on deep-server"; exit 2; }
SRC=$(cd "$(dirname "$0")" && pwd)
pids=(); status=0
for ((i = 0; i < NS; i++)); do
  python3 $SRC/validate.py $MAN $BASE $i $NS $W > $BASE/slot_$i.log 2>&1 & pids+=($!)
done
for i in "${!pids[@]}"; do wait ${pids[$i]} || { echo "FAILED slot $i"; status=1; }; done
[ $status -eq 0 ] || exit $status
python3 $SRC/collect_validation.py $MAN $BASE $OUT
echo DONE
