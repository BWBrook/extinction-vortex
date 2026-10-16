#!/bin/bash
# Submit Stage 1a: NJOBS jobs of JOBCPUS workers plus one afterany collector that emails Barry.
# Usage: s1a_submit.sh VBASE SETTINGS OUTDIR NJOBS JOBCPUS WALLTIME(HH:MM:SS)
set -euo pipefail
VBASE=$1; SETTINGS=$2; OUTDIR=$3; NJOBS=$4; JOBCPUS=$5; WALL=$6
IFS=: read -r h m s <<< "$WALL"; WALL_SECS=$(( 10#$h * 3600 + 10#$m * 60 + 10#$s ))
NW=$(( NJOBS * JOBCPUS )); MEM="$(( JOBCPUS / 2 + 1 ))gb"
K="$VBASE/src/analysis/fable/calibration/kunanyi"
mkdir -p "$VBASE/s1a/$OUTDIR/logs"
ids=()
for j in $(seq 0 $(( NJOBS - 1 ))); do
  ids+=($(/opt/pbs/bin/qsub -l select=1:ncpus="$JOBCPUS":mem="$MEM" -l walltime="$WALL" \
    -o "$VBASE/s1a/$OUTDIR/logs/job$j.out" -e "$VBASE/s1a/$OUTDIR/logs/job$j.err" \
    -v VBASE="$VBASE",SETTINGS="$SETTINGS",OUTDIR="$OUTDIR",JOB="$j",JOBCPUS="$JOBCPUS",NW="$NW",WALL_SECS="$WALL_SECS" "$K/s1a_node.pbs"))
done
dep=$(IFS=:; echo "${ids[*]}")
cid=$(/opt/pbs/bin/qsub -W depend=afterany:"$dep" -o "$VBASE/s1a/$OUTDIR/logs/collect.out" -e "$VBASE/s1a/$OUTDIR/logs/collect.err" \
  -v VBASE="$VBASE",SETTINGS="$SETTINGS",OUTDIR="$OUTDIR" "$K/s1a_collect.pbs")
printf '%s\n' "${ids[@]}" > "$VBASE/s1a/$OUTDIR/node_jobs.txt"; echo "$cid" > "$VBASE/s1a/$OUTDIR/collect_job.txt"
echo "jobs: ${#ids[@]} x $JOBCPUS cpus, $MEM, walltime $WALL (${ids[0]} .. ${ids[-1]})"; echo "collector: $cid"
/opt/pbs/bin/qstat -f "$cid" | grep -E "Mail_Users|Mail_Points"
