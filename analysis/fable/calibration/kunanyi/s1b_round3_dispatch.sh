#!/bin/bash
# Stage 1b round 3 on kunanyi (design 9h): the repaired ownership runner reruns, from each setting's bound pilot prefix,
# every setting that round 2 left incomplete, invalid or FAILED in either wave. Run from the login node under nohup, once
# every round-2 array and collector has finished and both final summaries have been fetched and verified, from the
# extracted stage itself:
#   cd $VB && echo "<stage sha256>  s1b_stage_round3.tar" | sha256sum -c && rm -rf stage_round3 && mkdir stage_round3 &&
#   tar -xf s1b_stage_round3.tar -C stage_round3 && STAGE_SHA=<stage sha256> W1_SUMMARY_SHA=<sha256> W2_SUMMARY_SHA=<sha256> \
#     nohup bash stage_round3/src/analysis/fable/calibration/kunanyi/s1b_round3_dispatch.sh > s1b/dispatch_r3.log 2>&1 &
# Steps, each safe to repeat, so rerunning the script after an interruption continues where it stopped:
# 1. verify the stage: the tar's digest is the reviewed STAGE_SHA, the extracted manifest is the tar's own, and every
#    extracted file matches it (a failure stops here);
# 2. require PBS to show every round-2 array and collector finished (round-2 workers run the installed runner, so the
#    new one is installed only after this), then install the runner, PBS scripts and dispatchers;
# 3. gate each wave's final round-2 summary (run2/collect_<WAVE>_b.json): its exact verified digest, its binding to the
#    round-2 settings, metric and runner, the unique wave inventory with unchanged row identities, known statuses with
#    consistent counts, and errors one-to-one with the rows marked invalid; select round 3's dirs (every incomplete,
#    invalid or FAILED row of both waves) and bind p3_settings_r3.json to the new runner (an existing file must be
#    identical);
# 4. release round 2's remaining reservations, each once, citing PBS;
# 5. size and submit W1 round 3, then W2 round 3, into run3 (new where a wave has no journal, resume where it has one):
#    W1 gets one 8-CPU subjob per 8 of its settings' 28 in-flight ranges (at most W1_MAX_JOBS); W2 the CPUs left under
#    CAP_CPUS by this user's live requests (each array also needs one CPU for its collector), sized only once every job
#    accepted in run3 is in the live listing or finished. A size binds once its submission journal exists; before that
#    it is recomputed. The submitter checks capacity again before any new request. A wave with no settings to rerun is
#    skipped. Written for bash 4.2.
set -euo pipefail
VB=${VB:-/u/bwbrook/vortex/run1}; S=$VB/s1b; PBS=${PBS_BIN:-/opt/pbs/bin}; C=src/analysis/fable/calibration
STAGE_SHA=${STAGE_SHA:?}; W1_SUMMARY_SHA=${W1_SUMMARY_SHA:?}; W2_SUMMARY_SHA=${W2_SUMMARY_SHA:?}
W1_MAX_JOBS=${W1_MAX_JOBS:-170}; CAP=${CAP_CPUS:-7000}; MIN_W2=${MIN_W2_JOBS:-20}; ME=${PBS_USER:-$(id -un)}
R2_JOBS='857922[] 857923 858016[] 858017 860989[] 860990 860992[] 860993'
R2_RELEASES='s1b_3a5e71fa_a=858016[],858017 s1b_b373da8c_a=860989[],860990 s1b_f093f541_a=860992[],860993'
export VBASE="$VB"                        # env.sh changes into $VBASE/src
cd "$VB"
echo "== $(date '+%F %T %Z') verify stage"
if ! echo "$STAGE_SHA  s1b_stage_round3.tar" | sha256sum -c --quiet; then echo "stage tar is not the reviewed one: nothing installed"; exit 1; fi
if ! tar -xOf s1b_stage_round3.tar ./s1b/stage_sha256.txt | cmp -s - stage_round3/s1b/stage_sha256.txt; then
  echo "extracted manifest differs from the stage tar's: nothing installed"; exit 1
fi
if ! (cd stage_round3 && sha256sum -c --quiet s1b/stage_sha256.txt); then echo "stage checksum failed: nothing installed"; exit 1; fi
echo "stage OK"
for j in $R2_JOBS; do
  out=$("$PBS/qstat" -x -f "$j") || { echo "round 2 job $j: no PBS answer"; exit 1; }
  grep -q 'job_state = F' <<< "$out" || { echo "round 2 job $j is not finished"; exit 1; }
done
echo "round 2 jobs finished: $R2_JOBS"
echo "== install"
cp stage_round3/$C/v2_dev/p3_stage1b.py stage_round3/$C/v2_dev/p3_r2_determinism.py "$C/v2_dev/"
cp stage_round3/$C/kunanyi/s1b_node.pbs stage_round3/$C/kunanyi/s1b_collect.pbs stage_round3/$C/kunanyi/s1b_submit.sh \
   stage_round3/$C/kunanyi/s1b_capacity.sh stage_round3/$C/kunanyi/s1b_round3_dispatch.sh \
   stage_round3/$C/kunanyi/s1b_topup_dispatch.sh "$C/kunanyi/"
for f in v2_dev/p1_sampler.py v2_dev/p2_stage1a.py v2_dev/p3_stage1b.py v2_dev/p3_r2_determinism.py kunanyi/s1b_node.pbs \
         kunanyi/s1b_collect.pbs kunanyi/s1b_submit.sh kunanyi/s1b_capacity.sh kunanyi/s1b_round3_dispatch.sh \
         kunanyi/s1b_topup_dispatch.sh; do
  cmp -s "stage_round3/$C/$f" "$C/$f" || { echo "installed $f differs from the stage"; exit 1; }
done
echo "== round-3 settings"
( source "$VB/$C/kunanyi/env.sh"
  python -I - "$S/p3_settings_r2.json" "$S/dirs_r3.txt" "$S/dirs_r3_counts.txt" "$S/run2/collect_W1_b.json" "$W1_SUMMARY_SHA" \
    "$S/run2/collect_W2_b.json" "$W2_SUMMARY_SHA" <<'PY'
import collections, hashlib, json, sys
sp, out, counts, *gates = sys.argv[1:]
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
b = json.load(open(sp)); redo, per = [], []
bind = {"settings_sha256": sha(sp), "metric_sha256": b["metric_sha256"], "runner_sha256": b["runner_sha256"]}
known = ("COMPLETE", "CAPPED", "FAILED", "incomplete", "invalid")
for wave, (cp, want) in zip(("W1", "W2"), zip(gates[::2], gates[1::2])):
    if sha(cp) != want:
        raise SystemExit(f"{wave}: round 2 summary is not the verified one")
    c = json.load(open(cp))
    if c.get("wave") != wave or c.get("binding") != bind:
        raise SystemExit(f"{wave}: round 2 summary is not bound to the round-2 settings, metric and runner")
    inv = {s["dir"]: s for s in b["settings"] if s["wave"] == wave}
    rows = c.get("rows") or []; dirs = [r["dir"] for r in rows]
    if len(dirs) != len(set(dirs)) or set(dirs) != set(inv):
        raise SystemExit(f"{wave}: round 2 rows are not exactly the wave inventory")
    for r in rows:
        if any(r.get(k) != inv[r["dir"]][k] for k in ("index", "pop", "outer", "n", "library")):
            raise SystemExit(f"{r['dir']}: row identity differs from the settings")
        if r.get("status") not in known or (r["status"] == "COMPLETE") != bool(r.get("library_sha256")):
            raise SystemExit(f"{r['dir']}: unknown status or library inconsistent with status")
    n = collections.Counter(r["status"] for r in rows)
    if c.get("status") != {k: n.get(k, 0) for k in known[:4]} or sorted(c.get("incomplete", [])) != sorted(
            r["dir"] for r in rows if r["status"] == "incomplete"):
        raise SystemExit(f"{wave}: round 2 status counts or incomplete list inconsistent with its rows")
    bad = sorted(r["dir"] for r in rows if r["status"] == "invalid"); err = sorted(e.split(":", 1)[0] for e in c.get("errors", []))
    if c.get("n_errors") != len(err) or err != bad or c.get("collection_ok") != (not bad):
        raise SystemExit(f"{wave}: round 2 errors are not one-to-one with the rows marked invalid")
    mine = [r["dir"] for r in rows if r["status"] in ("incomplete", "invalid", "FAILED")]     # rerun from the pilot prefix
    redo += mine; per.append(f"{wave} {len(mine)}\n")
    print(f"round 2 {wave}:", dict(n), "| round 3 dirs:", len(mine))
open(out, "w").write("\n".join(redo) + "\n"); open(counts, "w").write("".join(per))
PY
  python -I "$VB/$C/v2_dev/p3_stage1b.py" select "$S/p3_settings_r2.json" "$S/p3_settings_r3.json.new" "$S/dirs_r3.txt" )
if [ -e "$S/p3_settings_r3.json" ]; then
  cmp -s "$S/p3_settings_r3.json.new" "$S/p3_settings_r3.json" || { echo "existing p3_settings_r3.json differs"; exit 1; }
  rm "$S/p3_settings_r3.json.new"
else
  mv "$S/p3_settings_r3.json.new" "$S/p3_settings_r3.json"
fi
sha256sum "$S/p3_settings_r3.json"
for rel in $R2_RELEASES; do
  name=${rel%%=*}; jobs=$(echo "${rel#*=}" | tr , ' ')
  echo "== release $name"
  if grep -q "^release	$name	" "$S/reservations.tsv"; then echo "already released"; continue; fi
  for j in $jobs; do
    out=$("$PBS/qstat" -x -f "$j") || { echo "$j: no PBS answer"; exit 1; }
    grep -q 'job_state = F' <<< "$out" || { echo "$j is not finished"; exit 1; }
  done
  mkdir "$S/.ledger.lock"
  printf 'release\t%s\tmanual: %s job_state F (qstat -x, %s); in-flight ledger (design 9d)\n' "$name" "$jobs" \
    "$(date '+%FT%T%z')" >> "$S/reservations.tsv"
  sync "$S/reservations.tsv"; rmdir "$S/.ledger.lock"
done
source "$C/kunanyi/s1b_capacity.sh"
export TMPDIR="$S/tmp"; mkdir -p "$TMPDIR" "$S/run3"
for w in W1 W2; do
  J="$S/run3/submit_$w/submit_journal.tsv"; F="$S/run3/r3_$w.jobs"
  m=$(awk -v w="$w" '$1 == w {print $2}' "$S/dirs_r3_counts.txt")
  if [ "$m" -eq 0 ]; then echo "== $w: no settings to rerun"; continue; fi
  wait_listed "$S/run3"
  if [ -e "$J" ] && [ -e "$F" ]; then
    n=$(cat "$F")
  else
    req=$(live_cpus); echo "live requests: $req CPUs"
    if [ "$w" = W1 ]; then n=$(( (m * 28 + 7) / 8 )); if [ "$n" -gt "$W1_MAX_JOBS" ]; then n=$W1_MAX_JOBS; fi
    else n=$(( (CAP - req - 1) / 8 )); fi
    if [ $(( req + 8 * n + 1 )) -gt "$CAP" ]; then echo "$w: $n x 8 does not fit ($req of $CAP CPUs requested)"; exit 1; fi
    if [ "$w" = W2 ] && [ "$n" -lt "$MIN_W2" ]; then echo "W2: only $n subjobs fit"; exit 1; fi
    echo "$n" > "$F"
  fi
  if [ -e "$J" ]; then mode=resume; else mode=new; fi
  echo "== $(date '+%T') submit $w round 3 ($mode; $m settings; $n x 8 x 48 h)"
  bash "$C/kunanyi/s1b_submit.sh" "$VB" p3_settings_r3.json run3 "$w" "$n" 8 48:00:00 "$mode"
done
echo "live requests now: $(live_cpus) CPUs"
tail -n 5 "$S/reservations.tsv"
echo "DISPATCH_DONE $(date '+%F %T %Z')"
