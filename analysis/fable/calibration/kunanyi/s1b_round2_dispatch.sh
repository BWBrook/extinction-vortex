#!/bin/bash
# Stage 1b round 2 on kunanyi (design section 9). Run from the login node under nohup, after round 1's array and
# collector have finished, from the extracted stage itself:
#   cd $VB && rm -rf stage_r2 && mkdir stage_r2 && tar -xf s1b_stage_r2.tar -C stage_r2 &&
#   nohup bash stage_r2/src/analysis/fable/calibration/kunanyi/s1b_round2_dispatch.sh > s1b/dispatch_r2.log 2>&1 &
# Steps:
# 1. verify and install the stage (runner, determinism check, node, collector and submitter scripts);
# 2. derive the round-2 dirs (round 1's incomplete and invalid W1 settings, from its finished collection, whose errors
#    must all belong to settings it marked invalid; plus every W2 setting)
#    and bind p3_settings_r2.json to the new runner with `select`;
# 3. release round 1's spent reservation in the ledger, citing PBS (Barry lifted the ceilings, 21 Oct; board 2123);
# 4. submit W1 round 2 and the first W2 array into run2 (each seeds its wave). Written for bash 4.2.
set -euo pipefail
VB=${VB:-/u/bwbrook/vortex/run1}; S=$VB/s1b; Q=${PBS_BIN:-/opt/pbs/bin}/qstat; C=src/analysis/fable/calibration
export VBASE="$VB"                        # env.sh changes into $VBASE/src
W1_JOBS=${W1_JOBS:-300}; W2_JOBS=${W2_JOBS:-570}
cd "$VB"
echo "== $(date '+%F %T %Z') verify stage"
(cd stage_r2 && sha256sum -c --quiet s1b/stage_sha256.txt) && echo "stage OK"
for j in '821088[]' 821089; do
  "$Q" -x -f "$j" | grep -q 'job_state = F' || { echo "round 1 job $j is not finished"; exit 1; }
done
echo "== install"
cp stage_r2/$C/v2_dev/p3_stage1b.py stage_r2/$C/v2_dev/p3_r2_determinism.py "$C/v2_dev/"
cp stage_r2/$C/kunanyi/s1b_node.pbs stage_r2/$C/kunanyi/s1b_collect.pbs stage_r2/$C/kunanyi/s1b_submit.sh \
   stage_r2/$C/kunanyi/s1b_round2_dispatch.sh "$C/kunanyi/"
for f in v2_dev/p1_sampler.py v2_dev/p2_stage1a.py v2_dev/p3_stage1b.py v2_dev/p3_r2_determinism.py kunanyi/s1b_node.pbs kunanyi/s1b_collect.pbs kunanyi/s1b_submit.sh; do
  cmp -s "stage_r2/$C/$f" "$C/$f" || { echo "installed $f differs from the stage"; exit 1; }
done
echo "== round-2 settings"
( source "$VB/$C/kunanyi/env.sh"
  python -I - "$S/run/collect_W1.json" "$S/p3_settings.json" "$S/dirs_r2.txt" <<'PY'
import json, sys
c = json.load(open(sys.argv[1])); b = json.load(open(sys.argv[2]))
w1 = {s["dir"] for s in b["settings"] if s["wave"] == "W1"}
if c.get("wave") != "W1" or "rows" not in c or {r["dir"] for r in c["rows"]} != w1:
    raise SystemExit("round 1 W1 collection is not a finished summary of every W1 setting")
inv = {r["dir"] for r in c["rows"] if r["status"] == "invalid"}
if c["n_errors"] != len(c["errors"]) or {e.split(":", 1)[0] for e in c["errors"]} != inv:
    raise SystemExit("round 1 errors are not confined to settings marked invalid")
redo = [r["dir"] for r in c["rows"] if r["status"] in ("incomplete", "invalid")]       # rerun from batch 0 under round 2
w2 = [s["dir"] for s in b["settings"] if s["wave"] == "W2"]
open(sys.argv[3], "w").write("\n".join(redo + w2) + "\n")
print("round 1:", c["status"], "invalid", sorted(inv), "| round 2 dirs: W1", len(redo), "W2", len(w2))
PY
  python -I "$VB/$C/v2_dev/p3_stage1b.py" select "$S/p3_settings.json" "$S/p3_settings_r2.json" "$S/dirs_r2.txt" )
echo "== release round 1"
mkdir "$S/.ledger.lock"
printf 'release\ts1b_5e346b76_a\tmanual: array 821088[] and collector 821089 job_state F (qstat -x, %s); ceilings now bound in-flight reservations (Barry 21 Oct 2026, board 2123; design 9d)\n' \
  "$(date '+%FT%T%z')" >> "$S/reservations.tsv"
sync "$S/reservations.tsv"; rmdir "$S/.ledger.lock"
tail -n 2 "$S/reservations.tsv"
export TMPDIR="$S/tmp"; mkdir -p "$TMPDIR"
echo "== $(date '+%T') submit W1 round 2 ($W1_JOBS x 8 x 48 h)"
bash "$C/kunanyi/s1b_submit.sh" "$VB" p3_settings_r2.json run2 W1 "$W1_JOBS" 8 48:00:00
echo "== $(date '+%T') submit W2, first array ($W2_JOBS x 8 x 48 h)"
bash "$C/kunanyi/s1b_submit.sh" "$VB" p3_settings_r2.json run2 W2 "$W2_JOBS" 8 48:00:00
tail -n 3 "$S/reservations.tsv"
echo "DISPATCH_DONE $(date '+%F %T %Z')"
