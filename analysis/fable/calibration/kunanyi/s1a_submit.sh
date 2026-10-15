#!/bin/bash
# Submit Stage 1a: NNODES one-node jobs plus one afterany collector that emails Barry.
# Usage: s1a_submit.sh VBASE SETTINGS OUTDIR NNODES WALLTIME(HH:MM:SS)
set -euo pipefail
VBASE=$1; SETTINGS=$2; OUTDIR=$3; NNODES=$4; WALL=$5
IFS=: read -r h m s <<< "$WALL"; WALL_SECS=$(( 10#$h * 3600 + 10#$m * 60 + 10#$s ))
NW=$(( NNODES * 28 ))
K="$VBASE/src/analysis/fable/calibration/kunanyi"
mkdir -p "$VBASE/s1a/$OUTDIR/logs"
ids=()
for n in $(seq 0 $(( NNODES - 1 ))); do
  ids+=($(/opt/pbs/bin/qsub -l walltime="$WALL" -o "$VBASE/s1a/$OUTDIR/logs/node$n.out" -e "$VBASE/s1a/$OUTDIR/logs/node$n.err" \
    -v VBASE="$VBASE",SETTINGS="$SETTINGS",OUTDIR="$OUTDIR",NODE="$n",NW="$NW",WALL_SECS="$WALL_SECS" "$K/s1a_node.pbs"))
done
dep=$(IFS=:; echo "${ids[*]}")
cid=$(/opt/pbs/bin/qsub -W depend=afterany:"$dep" -o "$VBASE/s1a/$OUTDIR/logs/collect.out" -e "$VBASE/s1a/$OUTDIR/logs/collect.err" \
  -v VBASE="$VBASE",SETTINGS="$SETTINGS",OUTDIR="$OUTDIR" "$K/s1a_collect.pbs")
printf '%s\n' "${ids[@]}" > "$VBASE/s1a/$OUTDIR/node_jobs.txt"; echo "$cid" > "$VBASE/s1a/$OUTDIR/collect_job.txt"
echo "nodes: ${ids[*]}"; echo "collector: $cid"
/opt/pbs/bin/qstat -f "$cid" | grep -E "Mail_Users|Mail_Points|depend"
