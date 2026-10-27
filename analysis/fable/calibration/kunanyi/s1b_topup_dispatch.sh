#!/bin/bash
# Stage 1b topup arrays on kunanyi (design 9f, 9h): further arrays for waves already seeded into OUTDIR, under the
# installed runner, node and collector scripts. Run from the login node under nohup:
#   LABEL=b WAVES=W2 REF='<array id>[]' RELEASES='<name>=<job>,<job> ...' \
#     nohup bash .../s1b_topup_dispatch.sh > s1b/topup_r3_b.log 2>&1 &
# Steps, each safe to repeat:
# 1. release each named finished reservation once, after PBS shows every job it names finished (job_state F);
# 2. count this user's live requests: the CPUs of every queued, running or held job and subjob (array parents excluded),
#    cross-checked against REF, one of this user's arrays (live or finished: PBS history is consulted, so a finished
#    array counts zero live subjobs); refuse to size from an implausible total or an unanswered reference;
# 3. for each wave of WAVES in order, submit a topup: W1_JOBS x 8 for W1, the CPUs left under CAP_CPUS for W2 (each
#    topup also needs one CPU for its collector). Sizes are recorded on first submission and reused, so a rerun resumes
#    the same submissions. Written for bash 4.2.
set -euo pipefail
VB=${VB:-/u/bwbrook/vortex/run1}; S=$VB/s1b; PBS=${PBS_BIN:-/opt/pbs/bin}; C=src/analysis/fable/calibration
LABEL=${LABEL:?}; WAVES=${WAVES:?}; REF=${REF:?}; RELEASES=${RELEASES-}
SETTINGS=${SETTINGS:-p3_settings_r3.json}; OUTDIR=${OUTDIR:-run3}
W1_JOBS=${W1_JOBS:-170}; CAP=${CAP_CPUS:-7000}; MIN_W2=${MIN_W2_JOBS:-20}; ME=${PBS_USER:-$(id -un)}
for w in $WAVES; do case "$w" in W1|W2) ;; *) echo "unknown wave $w"; exit 1 ;; esac; done
export VBASE="$VB"
cd "$VB"
echo "== $(date '+%F %T %Z') topup $LABEL: waves $WAVES into $OUTDIR ($SETTINGS)"
for rel in $RELEASES; do
  name=${rel%%=*}; jobs=$(echo "${rel#*=}" | tr , ' ')
  echo "== release $name"
  if grep -q "^release	$name	" "$S/reservations.tsv"; then echo "already released"; continue; fi
  for j in $jobs; do "$PBS/qstat" -x -f "$j" | grep -q 'job_state = F' || { echo "$j is not finished"; exit 1; }; done
  mkdir "$S/.ledger.lock"
  printf 'release\t%s\tmanual: %s job_state F (qstat -x, %s); in-flight ledger (design 9d)\n' "$name" "$jobs" \
    "$(date '+%FT%T%z')" >> "$S/reservations.tsv"
  sync "$S/reservations.tsv"; rmdir "$S/.ledger.lock"
done
requested() {      # CPUs of this user's queued, running and held jobs and subjobs; array parents excluded
  "$PBS/qstat" -t -u "$ME" | awk -v me="$ME" '$2 == me && $1 !~ /\[\]/ && $10 ~ /^[QRHWTSE]$/ {n += $7} END {print n + 0}'
}
ref_live() {       # REF's queued, running and held subjobs from its own state counts, history included
  local out
  out=$("$PBS/qstat" -x -f "$REF") || { echo "reference $REF: no PBS answer" >&2; return 1; }
  echo "$out" | grep -q 'array_state_count' || { echo "reference $REF is not an array" >&2; return 1; }
  echo "$out" | awk -F'[ :=]+' '/array_state_count/ {for (i = 1; i < NF; i++) if ($i == "Queued" || $i == "Running" || $i == "Held") n += $(i + 1)} END {print n + 0}'
}
size_file() { echo "$S/$OUTDIR/topup_${LABEL}_$1.jobs"; }
export TMPDIR="$S/tmp"; mkdir -p "$TMPDIR"
for w in $WAVES; do
  J="$S/$OUTDIR/submit_${w}_$LABEL/submit_journal.tsv"
  if [ -e "$(size_file $w)" ]; then
    n=$(cat "$(size_file $w)")
  else
    req=$(requested); live=$(ref_live)
    echo "live requests: $req CPUs; $REF live subjobs: $live"
    if [ "$req" -lt $(( 8 * live )) ]; then echo "request total $req is below $REF's own $(( 8 * live )): not sizing"; exit 1; fi
    if [ "$w" = W1 ]; then n=$W1_JOBS; else n=$(( (CAP - req - 1) / 8 )); fi
    if [ $(( req + 8 * n + 1 )) -gt "$CAP" ]; then echo "$w: $n x 8 does not fit ($req of $CAP CPUs requested)"; exit 1; fi
    if [ "$w" = W2 ] && [ "$n" -lt "$MIN_W2" ]; then echo "W2: only $n subjobs fit; no W2 topup"; break; fi
    echo "$n" > "$(size_file $w)"
  fi
  if [ -e "$J" ]; then mode="resume"; else mode="topup"; fi
  echo "== $(date '+%T') $w $mode $LABEL: $n x 8 x 48 h"
  bash "$C/kunanyi/s1b_submit.sh" "$VB" "$SETTINGS" "$OUTDIR" "$w" "$n" 8 48:00:00 "$mode" "$LABEL"
done
echo "live requests now: $(requested) CPUs"
tail -n 4 "$S/reservations.tsv"
echo "TOPUP_DONE $(date '+%F %T %Z')"
