#!/usr/bin/env bash
# Submit the validation on the kunanyi login node: NSLOTS one-node slot jobs and a collector
# that runs after all of them. Refuses to submit without this host's preflight receipt.
# Usage: bash submit.sh VBASE NSLOTS
set -euo pipefail
VBASE=$1; NS=$2
D=$VBASE/src/analysis/fable/calibration/kunanyi
DIG=$(sha256sum "$VBASE/validation_manifest.json" | cut -c1-16)
[ -f "$VBASE/preflight_$DIG.json" ] || { echo "no preflight receipt for $DIG"; exit 2; }
mkdir -p "$VBASE/slot_logs"
ids=()
for ((i = 0; i < NS; i++)); do
  ids+=($(/opt/pbs/bin/qsub -o "$VBASE/slot_logs/slot_$i.out" -e "$VBASE/slot_logs/slot_$i.err" \
          -v VBASE=$VBASE,SLOT=$i,NSLOTS=$NS "$D/slot.pbs"))
done
dep=$(IFS=:; echo "${ids[*]}")
cid=$(/opt/pbs/bin/qsub -o "$VBASE/collect.out" -e "$VBASE/collect.err" -v VBASE=$VBASE \
      -W depend=afterany:$dep "$D/collect.pbs")
printf '%s\n' "${ids[@]}" > "$VBASE/slot_jobs.txt"; echo "$cid" > "$VBASE/collect_job.txt"
echo "submitted ${#ids[@]} slots; collector $cid"
