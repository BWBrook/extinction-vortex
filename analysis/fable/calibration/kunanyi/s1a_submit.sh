#!/bin/bash
# Submit Stage 1a: NJOBS jobs of JOBCPUS workers plus one afterany collector that emails Barry. Written for bash 4.2.
# Usage: s1a_submit.sh VBASE SETTINGS OUTDIR NJOBS JOBCPUS WALLTIME(HH:MM:SS) CEILING_CPUH PRIOR_CPUH [resume]
# The run identity (settings hash, output directory, shape, walltime, ceiling) is fixed in run.json once a journal
# exists; a lock directory admits one submitter; the bound preflight runs before any qsub. Each job has a unique PBS
# name (settings hash, output directory, index). The synced journal records, per key (jN or c):
#   request KEY NAME                      written before the qsub
#   accepted KEY NAME ID [reconciled]     qsub returned ID, or PBS showed exactly one job of that name
#   uncertain KEY NAME                    qsub failed or gave no ID, and PBS did not show exactly one job of that name
# An empty PBS answer never proves non-acceptance: an accepted job can finish and leave history before its reply. A key
# whose last entry is request or uncertain therefore stays unresolved until PBS shows the job or an operator, after
# checking tracejob or the accounting logs, appends "accepted KEY NAME ID manual: <evidence>" or
# "rejected KEY NAME manual: <evidence>". A second dispatch is refused; "resume" submits only keys never requested or
# rejected by an operator. The collector depends on every accepted job not positively confirmed finished (qstat -x
# job_state F); a failed or unclassifiable query stops before the collector qsub, and a verified finished job whose
# history has expired can be recorded as "terminal KEY ID manual: <evidence>".
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
state() {   # the last submission entry for KEY: "TYPE ID"
  if [ -e "$J" ]; then
    awk -v k="$1" '($1 == "request" || $1 == "accepted" || $1 == "rejected" || $1 == "uncertain") && $2 == k {
      t = $1; id = ($1 == "accepted") ? $4 : ""} END {print t, id}' "$J"
  fi
}
lookup() { found=$("$PBS/qselect" -x -N "$1" | sed '/^$/d'); n=$(printf '%s' "$found" | grep -c . || true); }
submit() {   # KEY NAME qsub-args... -> $got
  local key=$1 name=$2 st id; shift 2
  read -r st id <<< "$(state "$key")"
  if [ "$st" = accepted ]; then got=$id; return; fi
  lookup "$name"
  [ "$n" -le 1 ] || die "$n PBS jobs named $name; reconcile by hand"
  if [ "$n" -eq 1 ]; then note "accepted $key $name $found reconciled"; got=$found; return; fi
  if [ "$st" = request ] || [ "$st" = uncertain ]; then
    die "unresolved earlier request for $name and PBS has no record of it (history may have expired); verify with tracejob or the accounting logs, append 'accepted $key $name ID manual: <evidence>' or 'rejected $key $name manual: <evidence>' to $J, then resume"
  fi
  note "request $key $name"
  if got=$("$PBS/qsub" -N "$name" "$@") && [ -n "$got" ]; then note "accepted $key $name $got"; return; fi
  sleep "${S1A_CONFIRM_SECS:-10}"
  if found=$("$PBS/qselect" -x -N "$name" | sed '/^$/d') && [ "$(printf '%s' "$found" | grep -c . || true)" -eq 1 ]; then
    note "accepted $key $name $found reconciled"; got=$found; return
  fi
  note "uncertain $key $name"; die "qsub for $name failed and PBS does not show exactly one such job; resolve it as the journal header describes, then resume"
}
terminal() { [ -e "$J" ] && awk -v k="$1" -v id="$2" '$1 == "terminal" && $2 == k && $3 == id {f = 1} END {exit !f}' "$J"; }
ids=()
for j in $(seq 0 $(( NJOBS - 1 ))); do
  submit "j$j" "s1a_${RID}_j$j" -l select=1:ncpus="$JOBCPUS":mem="$MEM" -l walltime="$WALL" \
    -o "$R/logs/job$j.out" -e "$R/logs/job$j.err" \
    -v VBASE="$VBASE",SETTINGS="$SETTINGS",OUTDIR="$OUTDIR",JOB="$j",JOBCPUS="$JOBCPUS",NW="$NW",WALL_SECS="$WALL_SECS" \
    "$K/s1a_node.pbs"
  ids+=("$got")
done
printf '%s\n' "${ids[@]}" > "$R/node_jobs.txt"
read -r cst cid <<< "$(state c)"
if [ "$cst" = accepted ]; then
  got=$cid
else
  lookup "s1a_${RID}_c"; dep=()
  if [ "$n" -eq 0 ]; then
    live=()
    for j in $(seq 0 $(( NJOBS - 1 ))); do
      id=${ids[$j]}
      if terminal "j$j" "$id"; then continue; fi
      out=$("$PBS/qstat" -x -f "$id") || die "cannot query $id (j$j), so the collector was not submitted; resume when PBS answers, or append 'terminal j$j $id manual: <evidence>' if it is verifiably finished"
      js=$(printf '%s\n' "$out" | awk -F' = ' '$1 ~ /^ *job_state$/ {print $2}')
      case "$js" in
        F) ;;
        Q|R|H|W|T|E|S|U|B|M) live+=("$id") ;;
        *) die "unclassified state '$js' for $id (j$j), so the collector was not submitted" ;;
      esac
    done
    if [ ${#live[@]} -gt 0 ]; then dep=(-W depend=afterany:"$(IFS=:; echo "${live[*]}")"); fi
  fi
  submit c "s1a_${RID}_c" ${dep[@]+"${dep[@]}"} -o "$R/logs/collect.out" -e "$R/logs/collect.err" \
    -v VBASE="$VBASE",SETTINGS="$SETTINGS",OUTDIR="$OUTDIR" "$K/s1a_collect.pbs"
fi
cid=$got; echo "$cid" > "$R/collect_job.txt"
echo "jobs: ${#ids[@]} x $JOBCPUS cpus, $MEM, walltime $WALL (${ids[0]} .. ${ids[$(( ${#ids[@]} - 1 ))]}); collector: $cid"
"$PBS/qstat" -f "$cid" | grep -E "Mail_Users|Mail_Points|depend" || true
