#!/bin/bash
# Submit one Stage 1b wave: a PBS job array of NJOBS subjobs x JOBCPUS pull workers, plus one afterany collector that
# emails Barry. Written for bash 4.2. Same journal, reconciliation and dependency contract as the audited Stage 1a
# submitter; keys are a (the array) and c (the collector). New mode first seeds the wave (pilot prefixes, first tickets).
# Topup mode adds a further array (and its collector) for a wave already seeded in OUTDIR, under its own LABEL: its own
# journal, logs, PBS names and archive (WAVE_LABEL.tar.gz); it never seeds. Resume with the same LABEL resumes a topup.
# Usage: s1b_submit.sh VBASE SETTINGS OUTDIR WAVE NJOBS JOBCPUS WALLTIME(HH:MM:SS) [new|resume|topup] [LABEL]
# Ceilings are bound in the settings; the campaign reservation ledger $VBASE/s1b/reservations.tsv (held under a
# campaign-wide lock for the whole submission) carries spending history across output directories.
# The run identity (settings hash, output directory, shape, walltime, ceiling) is fixed in run.json once a journal
# exists; a lock directory admits one submitter; the bound preflight runs before any qsub. Each job has a unique PBS
# name (settings hash, output directory, key). The synced journal records, per key (a or c):
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
VBASE=$1; SETTINGS=$2; OUTDIR=$3; WAVE=$4; NJOBS=$5; JOBCPUS=$6; WALL=$7; MODE=${8:-new}; LABEL=${9:-}
PBS=${PBS_BIN:-/opt/pbs/bin}
IFS=: read -r h m s <<< "$WALL"; WALL_SECS=$(( 10#$h * 3600 + 10#$m * 60 + 10#$s ))
MEM="$(( JOBCPUS + 2 ))gb"
die() { echo "s1b_submit: $*" >&2; exit 1; }
case "$MODE" in
  new) [ -z "$LABEL" ] || die "new mode takes no label" ;;
  resume) ;;
  topup) [ -n "$LABEL" ] || die "topup mode needs a label" ;;
  *) die "mode must be new, resume or topup" ;;
esac
[ -z "$LABEL" ] || [[ "$LABEL" =~ ^[a-z0-9]+$ ]] || die "a label is lower-case letters and digits"
TAG="$WAVE${LABEL:+_$LABEL}"
S="$VBASE/s1b"; RUN="$S/$OUTDIR"; R="$RUN/submit_$TAG"; K="$VBASE/src/analysis/fable/calibration/kunanyi"; J="$R/submit_journal.tsv"
if [ "$MODE" = topup ]; then [ -e "$RUN/submit_$WAVE/submit_journal.tsv" ] || die "topup needs the wave's seeded first submission in $RUN/submit_$WAVE"; fi
mkdir -p "$R/logs"
mkdir "$S/.ledger.lock" 2>/dev/null || die "another Stage 1b submission holds $S/.ledger.lock (remove it only if none is running)"
trap 'rmdir "$S/.ledger.lock"' EXIT
mkdir "$R/.submit.lock" 2>/dev/null || die "another submission holds $R/.submit.lock (remove it only if none is running)"
trap 'rmdir "$R/.submit.lock"; rmdir "$S/.ledger.lock"' EXIT
SHA=$(sha256sum "$S/$SETTINGS" | cut -d' ' -f1)
RID=$(printf '%s %s %s %s %s' "$SHA" "$R" "$NJOBS" "$JOBCPUS" "$WALL" | sha256sum | cut -c1-8)   # a new shape is a new name
ID="settings=$SETTINGS sha256=$SHA outdir=$RUN wave=$WAVE tag=$TAG jobs=$NJOBS cpus=$JOBCPUS walltime=$WALL"
if [ -e "$J" ]; then             # a journal fixes the identity; before any request, a refused attempt leaves nothing bound
  if [ ! -f "$R/run.json" ] || [ "$(cat "$R/run.json")" != "$ID" ]; then die "run identity differs from $R/run.json"; fi
else
  echo "$ID" > "$R/run.json"; sync "$R/run.json"
fi
if [ "$MODE" != resume ]; then [ ! -e "$J" ] || die "already dispatched (journal exists); use resume"; fi
if [ "$MODE" = resume ]; then [ -e "$J" ] || die "nothing to resume (no journal)"; fi
( source "${S1A_ENV:-$K/env.sh}"
  python -I analysis/fable/calibration/v2_dev/p3_stage1b.py preflight "$S/$SETTINGS" "$S/p3_metric.json" \
    "$S/reservations.tsv" "s1b_${RID}_a" "$RUN" "$NJOBS" "$JOBCPUS" "$WALL_SECS" "$WAVE" ) > "$R/logs/preflight.log" 2>&1 \
  || die "preflight refused or failed; see $R/logs/preflight.log"
tail -n 1 "$R/logs/preflight.log"
if [ "$MODE" = new ]; then
  ( source "${S1A_ENV:-$K/env.sh}"
    python -I analysis/fable/calibration/v2_dev/p3_stage1b.py seed "$S/$SETTINGS" "$S/pilot" "$RUN" "$WAVE" ) \
    > "$R/logs/seed.log" 2>&1 || die "seed failed; see $R/logs/seed.log"
  tail -n 1 "$R/logs/seed.log"
fi
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
submit a "s1b_${RID}_a" -J 0-$(( NJOBS - 1 )) -l select=1:ncpus="$JOBCPUS":mem="$MEM" -l walltime="$WALL" \
  -o "$R/logs/node.^array_index^.out" -e "$R/logs/node.^array_index^.err" \
  -v VBASE="$VBASE",SETTINGS="$SETTINGS",OUTDIR="$OUTDIR",WAVE="$WAVE",TAG="$TAG",JOBCPUS="$JOBCPUS",WALL_SECS="$WALL_SECS" \
  "$K/s1b_node.pbs"
ids=("$got")
printf '%s\n' "${ids[@]}" > "$R/array_job.txt"
read -r cst cid <<< "$(state c)"
if [ "$cst" = accepted ]; then
  got=$cid
else
  lookup "s1b_${RID}_c"; dep=()
  if [ "$n" -eq 0 ]; then
    live=()
    id=${ids[0]}
    if ! terminal a "$id"; then
      out=$("$PBS/qstat" -x -f "$id") || die "cannot query $id, so the collector was not submitted; resume when PBS answers, or append 'terminal a $id manual: <evidence>' if it is verifiably finished"
      js=$(printf '%s\n' "$out" | awk -F' = ' '$1 ~ /^ *job_state$/ {print $2}')
      case "$js" in
        F) ;;
        Q|R|H|W|T|E|S|U|B|M) live+=("$id") ;;
        *) die "unclassified state '$js' for $id, so the collector was not submitted" ;;
      esac
    fi
    if [ ${#live[@]} -gt 0 ]; then dep=(-W depend=afterany:"$(IFS=:; echo "${live[*]}")"); fi
  fi
  submit c "s1b_${RID}_c" ${dep[@]+"${dep[@]}"} -o "$R/logs/collect.out" -e "$R/logs/collect.err" \
    -v VBASE="$VBASE",SETTINGS="$SETTINGS",OUTDIR="$OUTDIR",WAVE="$WAVE",TAG="$TAG" "$K/s1b_collect.pbs"
fi
cid=$got; echo "$cid" > "$R/collect_job.txt"
echo "wave $WAVE ($TAG): array ${ids[0]} ($NJOBS x $JOBCPUS cpus, $MEM, walltime $WALL); collector: $cid"
"$PBS/qstat" -f "$cid" | grep -E "Mail_Users|Mail_Points|depend" || true
