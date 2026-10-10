#!/usr/bin/env bash
# Run the manifest's validation chunks with NSLOTS concurrent bank-holding processes (at most
# three on deep-server: about 28 GB each), wait on every PID, then assemble and gate the
# results. DONE means the processes and the collector completed; the scientific outcome is
# in OUT_JSON. Usage: run_validation.sh MANIFEST NSLOTS OUT_JSON
set -euo pipefail
MAN=$1; NS=$2; OUT=$3
[ "$NS" -le 3 ] || { echo "at most 3 bank-holding processes"; exit 2; }
SRC=$(cd "$(dirname "$0")" && pwd)
pids=(); status=0
for ((i = 0; i < NS; i++)); do
  python3 $SRC/validate.py $MAN $i $NS > $(dirname $MAN)/slot_$i.log 2>&1 & pids+=($!)
done
for i in "${!pids[@]}"; do wait ${pids[$i]} || { echo "FAILED slot $i"; status=1; }; done
[ $status -eq 0 ] || exit $status
python3 $SRC/collect_validation.py $MAN $OUT
echo DONE
