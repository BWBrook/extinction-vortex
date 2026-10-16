#!/bin/bash
# Submit Stage 1a: NJOBS jobs of JOBCPUS workers plus one afterany collector that emails Barry.
# Usage: s1a_submit.sh VBASE SETTINGS OUTDIR NJOBS JOBCPUS WALLTIME(HH:MM:SS) CEILING_CPUH PRIOR_CPUH [resume]
# The run identity (settings hash, output directory, shape, walltime, ceiling) is fixed in run.json; a lock directory
# admits one submitter. The bound preflight runs before any qsub. Each job has a unique PBS name (from the settings hash,
# output directory and job index). Every qsub is journalled before it is made and as soon as it is accepted, and the journal is synced. Before
# submitting a job the script asks PBS (including finished jobs) whether that name already exists, so an accepted job
# whose qsub reply was lost is reconciled rather than duplicated. A second dispatch is refused; "resume" submits only
# jobs never accepted, then the collector once, depending on every accepted job not yet finished.
set -euo pipefail
VBASE=$1; SETTINGS=$2; OUTDIR=$3; NJOBS=$4; JOBCPUS=$5; WALL=$6; CEIL=$7; PRIOR=$8; MODE=${9:-new}
PBS=${PBS_BIN:-/opt/pbs/bin}
IFS=: read -r h m s <<< "$WALL"; WALL_SECS=$(( 10#$h * 3600 + 10#$m * 60 + 10#$s ))
NW=$(( NJOBS * JOBCPUS )); MEM="$(( JOBCPUS / 2 + 1 ))gb"
S="$VBASE/s1a"; R="$S/$OUTDIR"; K="$VBASE/src/analysis/fable/calibration/kunanyi"; J="$R/submit_journal.tsv"
die() { echo "s1a_submit: $*" >&2; exit 1; }
[ "$MODE" = new ] || [ "$MODE" = resume ] || die "mode must be new or resume"
mkdir -p "$R/logs"
mkdir "$R/.submit.lock" 2>/dev/null || die "another submission holds $R/.submit.lock (remove it only if none is running)"
trap 'rmdir "$R/.submit.lock"' EXIT
SHA=$(sha256sum "$S/$SETTINGS" | cut -d' ' -f1); RID=$(printf '%s %s' "$SHA" "$R" | sha256sum | cut -c1-8)
ID="settings=$SETTINGS sha256=$SHA outdir=$R jobs=$NJOBS cpus=$JOBCPUS walltime=$WALL ceiling=$CEIL prior=$PRIOR"
if [ -e "$J" ]; then             # a journal fixes the identity; before any request, a refused attempt leaves nothing bound
  if [ ! -f "$R/run.json" ] || [ "$(cat "$R/run.json")" != "$ID" ]; then die "run identity differs from $R/run.json"; fi
else
  echo "$ID" > "$R/run.json"; sync "$R/run.json"
fi
if [ "$MODE" = new ]; then [ ! -e "$J" ] || die "already dispatched (journal exists); use resume"; fi
if [ "$MODE" = resume ]; then [ -e "$J" ] || die "nothing to resume (no journal)"; fi
( source "${S1A_ENV:-$K/env.sh}"
  python -I analysis/fable/calibration/v2_dev/p2_stage1a.py preflight "$S/$SETTINGS" "$S/p2_metric.json" \
    "$NJOBS" "$JOBCPUS" "$WALL_SECS" "$CEIL" "$PRIOR" 1 ) > "$R/logs/preflight.log" 2>&1 \
  || die "preflight refused or failed; see $R/logs/preflight.log"
head -n 1 "$R/logs/preflight.log"
note() { printf '%s\n' "$*" >> "$J"; sync "$J"; }
accepted() { if [ -e "$J" ]; then awk -v k="$1" '$1 == "accepted" && $2 == k {print $4}' "$J" | tail -n 1; fi; }
submit() {   # key name qsub-args... -> $got. Reconcile with PBS by name, else journal the request, qsub, journal the ID.
  local key=$1 name=$2 found n; shift 2
  found=$("$PBS/qselect" -x -N "$name" | sed '/^$/d')
  n=$(printf '%s' "$found" | grep -c . || true)
  [ "$n" -le 1 ] || die "$n PBS jobs named $name; reconcile by hand"
  if [ "$n" -eq 1 ]; then note "accepted $key $name $found reconciled"; got=$found; return; fi
  note "request $key $name"
  if ! got=$("$PBS/qsub" -N "$name" "$@") || [ -z "$got" ]; then
    note "uncertain $key $name"; die "qsub for $name failed or returned no ID; resume reconciles it"
  fi
  note "accepted $key $name $got"
}
ids=()
for j in $(seq 0 $(( NJOBS - 1 ))); do
  got=$(accepted "j$j")
  if [ -z "$got" ]; then
    submit "j$j" "s1a_${RID}_j$j" -l select=1:ncpus="$JOBCPUS":mem="$MEM" -l walltime="$WALL" \
      -o "$R/logs/job$j.out" -e "$R/logs/job$j.err" \
      -v VBASE="$VBASE",SETTINGS="$SETTINGS",OUTDIR="$OUTDIR",JOB="$j",JOBCPUS="$JOBCPUS",NW="$NW",WALL_SECS="$WALL_SECS" \
      "$K/s1a_node.pbs"
  fi
  ids+=("$got")
done
printf '%s\n' "${ids[@]}" > "$R/node_jobs.txt"
got=$(accepted c)
if [ -z "$got" ]; then
  live=()
  for id in "${ids[@]}"; do if "$PBS/qstat" "$id" > /dev/null 2>&1; then live+=("$id"); fi; done
  dep=(); if [ ${#live[@]} -gt 0 ]; then dep=(-W depend=afterany:"$(IFS=:; echo "${live[*]}")"); fi
  submit c "s1a_${RID}_c" "${dep[@]}" -o "$R/logs/collect.out" -e "$R/logs/collect.err" \
    -v VBASE="$VBASE",SETTINGS="$SETTINGS",OUTDIR="$OUTDIR" "$K/s1a_collect.pbs"
fi
cid=$got; echo "$cid" > "$R/collect_job.txt"
echo "jobs: ${#ids[@]} x $JOBCPUS cpus, $MEM, walltime $WALL (${ids[0]} .. ${ids[-1]}); collector: $cid"
"$PBS/qstat" -f "$cid" | grep -E "Mail_Users|Mail_Points|depend" || true
