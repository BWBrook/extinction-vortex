#!/bin/bash
# Rehearsals of s1b_round2_dispatch.sh (stage s1b_stage_r3.tar) on deep-server with stub PBS: a fake round-1 summary
# that is correctly bound and shaped (61 incomplete, 1 invalid), the round-1 sources installed, real install, select,
# preflight and seeds. CASE = pos (then a rerun that must resume) | checksum | bad_sha | bad_binding | dup_row |
# bad_identity | bad_status | err_not_invalid. Negative cases must stop before the ledger, settings and PBS.
set -uo pipefail
CASE=$1; X=/data/fable/vortex/r3rehearse_$CASE; rm -rf $X; mkdir -p $X/src $X/s1b/run $X/bin
cp -a /data/fable/vortex/r2dev4/src/. $X/src/
cp /data/fable/vortex/v2_dev/p3/stage/src/analysis/fable/calibration/v2_dev/*.py $X/src/analysis/fable/calibration/v2_dev/
cp /data/fable/vortex/v2_dev/p3/stage/src/analysis/fable/calibration/kunanyi/s1b_* $X/src/analysis/fable/calibration/kunanyi/
rm -f $X/src/analysis/fable/calibration/v2_dev/p3_r2_determinism.py $X/src/analysis/fable/calibration/kunanyi/s1b_round2_dispatch.sh
ln -s "$(command -v python3)" $X/bin/python 2>/dev/null; mkdir -p /data/fable/vortex/r2dev4/bin
cp /data/fable/vortex/v2_dev/p3/{p3_settings.json,p3_metric.json} $X/s1b/; ln -s /data/fable/vortex/v2_dev/p2/s1a_main/main $X/s1b/pilot
printf "reserve\ts1b\tW1\ts1b_5e346b76_a\t199688.000\t2026-10-17T10:55:43+1100\tsettings=86545d6b outdir=/u/bwbrook/vortex/run1/s1b/run jobs=520 cpus=8 wall=172800\n" > $X/s1b/reservations.tsv
SHA=$(python3 - $X $CASE <<'PY'
import collections, hashlib, json, sys
X, case = sys.argv[1:]; sp = f"{X}/s1b/p3_settings.json"; b = json.load(open(sp))
w1 = [s for s in b["settings"] if s["wave"] == "W1"]; rows = []
for i, st in enumerate(w1):
    r = {k: st[k] for k in ("dir", "index", "pop", "outer", "n", "library")}
    r["status"] = "incomplete" if i % 240 == 7 else ("invalid" if i == 100 else "COMPLETE")
    if r["status"] == "COMPLETE": r["library_sha256"] = "0" * 64
    rows.append(r)
n = collections.Counter(r["status"] for r in rows)
c = {"collection_ok": False, "wave": "W1", "binding": {"settings_sha256": hashlib.sha256(open(sp, "rb").read()).hexdigest(),
     "metric_sha256": b["metric_sha256"], "runner_sha256": b["runner_sha256"]},
     "status": {k: n.get(k, 0) for k in ("COMPLETE", "CAPPED", "FAILED", "incomplete")}, "n_errors": 1,
     "errors": [f"{w1[101 if case == "err_not_invalid" else 100]["dir"]}: ValueError: verified K-hit prefix without a COMPLETE marker"],
     "incomplete": [r["dir"] for r in rows if r["status"] == "incomplete"], "rows": rows}
if case == "bad_binding": c["binding"]["runner_sha256"] = "other"
if case == "dup_row": rows.append(dict(rows[0]))
if case == "bad_identity": rows[5]["outer"] = "x/0"
if case == "bad_status": rows[6]["status"] = "weird"
open(f"{X}/s1b/run/collect_W1.json", "w").write(json.dumps(c))
print(hashlib.sha256(open(f"{X}/s1b/run/collect_W1.json", "rb").read()).hexdigest() if case != "bad_sha" else "0" * 64)
exec(open("/tmp/stage_r2_in/stubs.py").read())
for k, v in STUBS.items():
    if k != "python": open(f"{X}/bin/{k}", "w").write(f"#!/usr/bin/python3\n{v}")
json.dump([{"id": "821088[]", "name": "s1b_5e346b76_a", "args": [], "state": "F"},
           {"id": "821089", "name": "s1b_5e346b76_c", "args": [], "state": "F"}], open(f"{X}/jobs.json", "w"))
PY
)
chmod +x $X/bin/*; rm -f $X/bin/python
export PBS_BIN=$X/bin FIX_STATE=$X/jobs.json FIX_LEDGER=$X/qsub_ledger.jsonl FIX_CALLS=$X/qsub_calls.jsonl FIX_QSELECT_CALLS=$X/qselect.n S1A_CONFIRM_SECS=0
cp /data/fable/vortex/v2_dev/p3/s1b_stage_r3.tar $X/s1b_stage_r2.tar
cd $X && rm -rf stage_r2 && mkdir stage_r2 && tar -xf s1b_stage_r2.tar -C stage_r2
[ "$CASE" = checksum ] && echo "# tampered" >> stage_r2/src/analysis/fable/calibration/v2_dev/p3_stage1b.py
run() { VB=$X ROUND1_SUMMARY_SHA=$SHA W1_JOBS=300 W2_JOBS=570 bash $X/stage_r2/src/analysis/fable/calibration/kunanyi/s1b_round2_dispatch.sh > $X/dispatch_$1.log 2>&1; echo $?; }
rc1=$(run 1); rc2=x; [ "$CASE" = pos ] && rc2=$(run 2)
nq=$(cat $X/qsub_calls.jsonl 2>/dev/null | wc -l); nl=$(wc -l < $X/s1b/reservations.tsv)
inst=$(cmp -s $X/src/analysis/fable/calibration/v2_dev/p3_stage1b.py /data/fable/vortex/v2_dev/p3/stage/src/analysis/fable/calibration/v2_dev/p3_stage1b.py && echo round1-runner || echo new-runner)
echo "CASE $CASE rc1=$rc1 rc2=$rc2 qsub_calls=$nq ledger_lines=$nl settings_r2=$([ -e $X/s1b/p3_settings_r2.json ] && echo yes || echo no) src_runner=$inst | $(grep -v "^ " $X/dispatch_1.log | tail -n 1 | cut -c1-120)"
[ "$CASE" = pos ] && { grep -E "round 1:|already released|submit W|sha256sum|p3_settings_r2|DISPATCH_DONE" $X/dispatch_2.log | cut -c1-150; grep -c . $X/qsub_ledger.jsonl; }
