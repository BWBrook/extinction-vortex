#!/bin/bash
# Stage 1b round 2 on kunanyi (design section 9). Run from the login node under nohup, after round 1's array and
# collector have finished, from the extracted stage itself:
#   cd $VB && rm -rf stage_r2 && mkdir stage_r2 && tar -xf s1b_stage_r2.tar -C stage_r2 &&
#   nohup bash stage_r2/src/analysis/fable/calibration/kunanyi/s1b_round2_dispatch.sh > s1b/dispatch_r2.log 2>&1 &
# Steps, each safe to repeat, so rerunning the script after an interruption continues where it stopped:
# 1. verify the stage checksums (a failure stops here) and install the runner, determinism check and PBS scripts;
# 2. gate round 1's summary: its exact verified digest, its binding to the round-1 settings, metric and runner, the
#    unique W1 inventory with unchanged row identities, known statuses with consistent counts, and errors one-to-one
#    with the rows marked invalid; then select round 2's dirs (incomplete and invalid W1, every W2) and bind
#    p3_settings_r2.json to the new runner (an existing file must be identical);
# 3. release round 1's spent reservation in the ledger, once, citing PBS (Barry lifted the ceilings, 21 Oct; board 2123);
# 4. submit W1 round 2 and the first W2 array into run2: new where a wave has no journal, resume where it has one.
# Written for bash 4.2.
set -euo pipefail
VB=${VB:-/u/bwbrook/vortex/run1}; S=$VB/s1b; Q=${PBS_BIN:-/opt/pbs/bin}/qstat; C=src/analysis/fable/calibration
ROUND1_SUMMARY_SHA=${ROUND1_SUMMARY_SHA:-2aa92fb0bd8c9d8d2235bddb59c1b55be47f404f14d1eaf9ff800d05b7ba28ab}
export VBASE="$VB"                        # env.sh changes into $VBASE/src
W1_JOBS=${W1_JOBS:-300}; W2_JOBS=${W2_JOBS:-570}
cd "$VB"
echo "== $(date '+%F %T %Z') verify stage"
if ! (cd stage_r2 && sha256sum -c --quiet s1b/stage_sha256.txt); then echo "stage checksum failed: nothing installed"; exit 1; fi
echo "stage OK"
for j in '821088[]' 821089; do
  "$Q" -x -f "$j" | grep -q 'job_state = F' || { echo "round 1 job $j is not finished"; exit 1; }
done
echo "== install"
cp stage_r2/$C/v2_dev/p3_stage1b.py stage_r2/$C/v2_dev/p3_r2_determinism.py "$C/v2_dev/"
cp stage_r2/$C/kunanyi/s1b_node.pbs stage_r2/$C/kunanyi/s1b_collect.pbs stage_r2/$C/kunanyi/s1b_submit.sh \
   stage_r2/$C/kunanyi/s1b_round2_dispatch.sh "$C/kunanyi/"
for f in v2_dev/p1_sampler.py v2_dev/p2_stage1a.py v2_dev/p3_stage1b.py v2_dev/p3_r2_determinism.py kunanyi/s1b_node.pbs \
         kunanyi/s1b_collect.pbs kunanyi/s1b_submit.sh; do
  cmp -s "stage_r2/$C/$f" "$C/$f" || { echo "installed $f differs from the stage"; exit 1; }
done
echo "== round-2 settings"
( source "$VB/$C/kunanyi/env.sh"
  python -I - "$S/run/collect_W1.json" "$S/p3_settings.json" "$S/dirs_r2.txt" "$ROUND1_SUMMARY_SHA" <<'PY'
import collections, hashlib, json, sys
cp, sp, out, want = sys.argv[1:]
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
if sha(cp) != want:
    raise SystemExit("round 1 summary is not the verified one")
c = json.load(open(cp)); b = json.load(open(sp))
if c.get("wave") != "W1" or c.get("binding") != {"settings_sha256": sha(sp), "metric_sha256": b["metric_sha256"],
                                                  "runner_sha256": b["runner_sha256"]}:
    raise SystemExit("round 1 summary is not bound to the round-1 settings, metric and runner")
w1 = {s["dir"]: s for s in b["settings"] if s["wave"] == "W1"}
rows = c.get("rows") or []; dirs = [r["dir"] for r in rows]
if len(dirs) != len(set(dirs)) or set(dirs) != set(w1):
    raise SystemExit("round 1 rows are not exactly the W1 inventory")
known = ("COMPLETE", "CAPPED", "FAILED", "incomplete", "invalid")
for r in rows:
    if any(r.get(k) != w1[r["dir"]][k] for k in ("index", "pop", "outer", "n", "library")):
        raise SystemExit(f"{r['dir']}: row identity differs from the settings")
    if r.get("status") not in known or (r["status"] == "COMPLETE") != bool(r.get("library_sha256")):
        raise SystemExit(f"{r['dir']}: unknown status or library inconsistent with status")
n = collections.Counter(r["status"] for r in rows)
if c.get("status") != {k: n.get(k, 0) for k in known[:4]} or sorted(c.get("incomplete", [])) != sorted(
        r["dir"] for r in rows if r["status"] == "incomplete"):
    raise SystemExit("round 1 status counts or incomplete list inconsistent with its rows")
inv = sorted(r["dir"] for r in rows if r["status"] == "invalid"); err = sorted(e.split(":", 1)[0] for e in c.get("errors", []))
if c.get("n_errors") != len(err) or err != inv or c.get("collection_ok") != (not inv):
    raise SystemExit("round 1 errors are not one-to-one with the rows marked invalid")
redo = [r["dir"] for r in rows if r["status"] in ("incomplete", "invalid")]        # rerun from batch 0 under round 2
w2 = [s["dir"] for s in b["settings"] if s["wave"] == "W2"]
open(out, "w").write("\n".join(redo + w2) + "\n")
print("round 1:", dict(n), "invalid", inv, "| round 2 dirs: W1", len(redo), "W2", len(w2))
PY
  python -I "$VB/$C/v2_dev/p3_stage1b.py" select "$S/p3_settings.json" "$S/p3_settings_r2.json.new" "$S/dirs_r2.txt" )
if [ -e "$S/p3_settings_r2.json" ]; then
  cmp -s "$S/p3_settings_r2.json.new" "$S/p3_settings_r2.json" || { echo "existing p3_settings_r2.json differs"; exit 1; }
  rm "$S/p3_settings_r2.json.new"
else
  mv "$S/p3_settings_r2.json.new" "$S/p3_settings_r2.json"
fi
sha256sum "$S/p3_settings_r2.json"
echo "== release round 1"
if grep -q "^release	s1b_5e346b76_a	" "$S/reservations.tsv"; then
  echo "already released"
else
  mkdir "$S/.ledger.lock"
  printf 'release\ts1b_5e346b76_a\tmanual: array 821088[] and collector 821089 job_state F (qstat -x, %s); ceilings now bound in-flight reservations (Barry 21 Oct 2026, board 2123; design 9d)\n' \
    "$(date '+%FT%T%z')" >> "$S/reservations.tsv"
  sync "$S/reservations.tsv"; rmdir "$S/.ledger.lock"
fi
tail -n 2 "$S/reservations.tsv"
export TMPDIR="$S/tmp"; mkdir -p "$TMPDIR"
for w in W1 W2; do
  if [ "$w" = W1 ]; then n=$W1_JOBS; else n=$W2_JOBS; fi
  if [ -e "$S/run2/submit_$w/submit_journal.tsv" ]; then mode=resume; else mode=new; fi
  echo "== $(date '+%T') submit $w ($mode; $n x 8 x 48 h)"
  bash "$C/kunanyi/s1b_submit.sh" "$VB" p3_settings_r2.json run2 "$w" "$n" 8 48:00:00 "$mode"
done
tail -n 3 "$S/reservations.tsv"
echo "DISPATCH_DONE $(date '+%F %T %Z')"
