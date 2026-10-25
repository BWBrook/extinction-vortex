#!/bin/bash
# Stage 1b round-2 topup arrays on kunanyi (design 9f). Run from the login node under nohup, after the node script
# for topups has been pushed to $VB/s1b_node_topup.pbs:
#   NODE_SHA=<sha256> LABEL=b nohup bash .../s1b_topup_dispatch.sh > s1b/topup_b.log 2>&1 &
# Steps, each safe to repeat:
# 1. verify the pushed node script against NODE_SHA and install it (submitted arrays keep PBS's stored copy);
# 2. release the finished W1 round-2 reservation once, after PBS shows its array and collector finished;
# 3. count this user's live requests: the CPUs of every queued, running or held job and subjob (array parents
#    excluded), cross-checked against the running W2 array's own subjob count; refuse to size from an implausible total;
# 4. submit the W1 topup (W1_JOBS x 8, for the wave's remaining settings), then a W2 topup sized to the CPUs left under
#    CAP_CPUS (each topup also needs one CPU for its collector). Sizes are recorded on first submission and reused, so
#    a rerun resumes the same submissions. Written for bash 4.2.
set -euo pipefail
VB=${VB:-/u/bwbrook/vortex/run1}; S=$VB/s1b; PBS=${PBS_BIN:-/opt/pbs/bin}; C=src/analysis/fable/calibration
NODE_SHA=${NODE_SHA:?}; LABEL=${LABEL:?}; W1_JOBS=${W1_JOBS:-170}; CAP=${CAP_CPUS:-7000}; MIN_W2=${MIN_W2_JOBS:-20}
W2_ARRAY=${W2_ARRAY:-858016[]}; RELEASE=${RELEASE:-s1b_22b89261_a}; RELEASE_JOBS=${RELEASE_JOBS:-857922[] 857923}
ME=${PBS_USER:-$(id -un)}
export VBASE="$VB"
cd "$VB"
echo "== $(date '+%F %T %Z') node script"
if ! echo "$NODE_SHA  s1b_node_topup.pbs" | sha256sum -c -; then echo "node script digest mismatch: nothing installed"; exit 1; fi
cp s1b_node_topup.pbs "$C/kunanyi/s1b_node.pbs"
cmp -s s1b_node_topup.pbs "$C/kunanyi/s1b_node.pbs" || { echo "installed node script differs"; exit 1; }
echo "== release $RELEASE"
if grep -q "^release	$RELEASE	" "$S/reservations.tsv"; then
  echo "already released"
else
  for j in $RELEASE_JOBS; do
    "$PBS/qstat" -x -f "$j" | grep -q 'job_state = F' || { echo "$j is not finished"; exit 1; }
  done
  mkdir "$S/.ledger.lock"
  printf 'release\t%s\tmanual: %s job_state F (qstat -x, %s); in-flight ledger (design 9d)\n' "$RELEASE" "$RELEASE_JOBS" \
    "$(date '+%FT%T%z')" >> "$S/reservations.tsv"
  sync "$S/reservations.tsv"; rmdir "$S/.ledger.lock"
fi
requested() {      # CPUs of this user's queued, running and held jobs and subjobs; array parents excluded
  "$PBS/qstat" -t -u "$ME" | awk -v me="$ME" '$2 == me && $1 !~ /\[\]/ && $10 ~ /^[QRHWTSE]$/ {n += $7} END {print n + 0}'
}
w2_live() {        # the W2 array's queued, running and held subjobs, from its own state counts
  "$PBS/qstat" -f "$W2_ARRAY" | awk -F'[ :=]+' '/array_state_count/ {for (i = 1; i < NF; i++) if ($i == "Queued" || $i == "Running" || $i == "Held") n += $(i + 1)} END {print n + 0}'
}
size_file() { echo "$S/run2/topup_${LABEL}_$1.jobs"; }
export TMPDIR="$S/tmp"; mkdir -p "$TMPDIR"
for w in W1 W2; do
  J="$S/run2/submit_${w}_$LABEL/submit_journal.tsv"
  if [ -e "$(size_file $w)" ]; then
    n=$(cat "$(size_file $w)"); mode="resume"
  else
    req=$(requested); live=$(w2_live)
    echo "live requests: $req CPUs; $W2_ARRAY live subjobs: $live"
    if [ "$req" -lt $(( 8 * live )) ]; then echo "request total $req is below the W2 array's own $(( 8 * live )): not sizing"; exit 1; fi
    if [ "$w" = W1 ]; then n=$W1_JOBS; else n=$(( (CAP - req - 1) / 8 )); fi
    if [ $(( req + 8 * n + 1 )) -gt "$CAP" ]; then echo "$w: $n x 8 does not fit ($req of $CAP CPUs requested)"; exit 1; fi
    if [ "$w" = W2 ] && [ "$n" -lt "$MIN_W2" ]; then echo "W2: only $n subjobs fit; no W2 topup"; break; fi
    echo "$n" > "$(size_file $w)"; mode="topup"
  fi
  if [ -e "$J" ]; then mode="resume"; fi
  echo "== $(date '+%T') $w $mode $LABEL: $n x 8 x 48 h"
  bash "$C/kunanyi/s1b_submit.sh" "$VB" p3_settings_r2.json run2 "$w" "$n" 8 48:00:00 "$mode" "$LABEL"
done
echo "live requests now: $(requested) CPUs"
tail -n 4 "$S/reservations.tsv"
echo "TOPUP_DONE $(date '+%F %T %Z')"
