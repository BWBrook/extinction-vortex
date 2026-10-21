#!/bin/bash
# Rehearsal of s1b_round2_dispatch.sh on deep-server: stub PBS, a fake validated round-1 collection (60 open W1 dirs),
# the production-like ledger, the round-1 stage installed; real stage build, install, select, preflight and seeds.
set -euo pipefail
X=/data/fable/vortex/r2rehearse${NEG:-0}; rm -rf $X; mkdir -p $X/src $X/s1b/run $X/bin
cp -a /data/fable/vortex/r2dev2/src/. $X/src/                                   # tree with the deep env.sh stand-in
cp /data/fable/vortex/v2_dev/p3/stage/src/analysis/fable/calibration/v2_dev/*.py $X/src/analysis/fable/calibration/v2_dev/   # round 1 runner
cp /data/fable/vortex/v2_dev/p3/stage/src/analysis/fable/calibration/kunanyi/s1b_* $X/src/analysis/fable/calibration/kunanyi/
rm -f $X/src/analysis/fable/calibration/v2_dev/p3_r2_determinism.py
cp /data/fable/vortex/v2_dev/p3/{p3_settings.json,p3_metric.json} $X/s1b/; ln -s /data/fable/vortex/v2_dev/p2/s1a_main/main $X/s1b/pilot
printf "reserve\ts1b\tW1\ts1b_5e346b76_a\t199688.000\t2026-10-17T10:55:43+1100\tsettings=86545d6b outdir=/u/bwbrook/vortex/run1/s1b/run jobs=520 cpus=8 wall=172800\n" > $X/s1b/reservations.tsv
python3 - $X <<PY
import json, sys
X = sys.argv[1]; b = json.load(open(f"{X}/s1b/p3_settings.json"))
w1 = [s["dir"] for s in b["settings"] if s["wave"] == "W1"]
rows = [{"dir": d, "status": "incomplete" if i % 240 == 7 else ("invalid" if i == 100 else "COMPLETE")} for i, d in enumerate(w1)]
bad = w1[100] if "${NEG:-0}" == "0" else w1[101]
json.dump({"collection_ok": False, "wave": "W1", "status": {}, "n_errors": 1, "rows": rows,
           "errors": [f"{bad}: ValueError: verified K-hit prefix without a COMPLETE marker"]}, open(f"{X}/s1b/run/collect_W1.json", "w"))
exec(open("/tmp/stage_r2_in/stubs.py").read())
for k, v in STUBS.items():
    open(f"{X}/bin/{k}", "w").write(f"#!/usr/bin/python3\n{v}")
json.dump([{"id": "821088[]", "name": "s1b_5e346b76_a", "args": [], "state": "F"}, {"id": "821089", "name": "s1b_5e346b76_c", "args": [], "state": "F"}],
          open(f"{X}/jobs.json", "w"))
print("open W1 dirs", sum(r["status"] == "incomplete" for r in rows))
PY
rm $X/bin/python; chmod +x $X/bin/*
G=/tmp/stage_r2_build; rm -rf $G; mkdir -p $G/src/analysis/fable/calibration/v2_dev $G/src/analysis/fable/calibration/kunanyi $G/s1b
cp /tmp/stage_r2_in/{p1_sampler,p2_stage1a,p3_stage1b,p3_r2_determinism}.py $G/src/analysis/fable/calibration/v2_dev/
cp /tmp/stage_r2_in/s1b_{node.pbs,collect.pbs,submit.sh,round2_dispatch.sh} $G/src/analysis/fable/calibration/kunanyi/
(cd $G && find . -type f ! -name stage_sha256.txt | sort | xargs sha256sum > s1b/stage_sha256.txt && tar -cf $X/s1b_stage_r2.tar .)
sha256sum $X/s1b_stage_r2.tar
export PBS_BIN=$X/bin FIX_STATE=$X/jobs.json FIX_LEDGER=$X/qsub_ledger.jsonl FIX_CALLS=$X/qsub_calls.jsonl FIX_QSELECT_CALLS=$X/qselect.n S1A_CONFIRM_SECS=0
cd $X && rm -rf stage_r2 && mkdir stage_r2 && tar -xf s1b_stage_r2.tar -C stage_r2
time VB=$X W1_JOBS=300 W2_JOBS=570 bash $X/stage_r2/src/analysis/fable/calibration/kunanyi/s1b_round2_dispatch.sh
echo "== qsub calls"; python3 -c "
import json; [print(j[\"name\"], j[\"args\"][j[\"args\"].index(\"-v\")+1][:160], (j[\"args\"][j[\"args\"].index(\"-J\")+1] if \"-J\" in j[\"args\"] else \"\")) for j in map(json.loads, open(\"$X/qsub_ledger.jsonl\"))]"
echo "== ledger"; cat $X/s1b/reservations.tsv
echo "== run2"; ls $X/s1b/run2; ls $X/s1b/run2/queue | cut -c1-2 | sort | uniq -c; ls $X/s1b/run2/sets | wc -l
echo REHEARSAL_DONE
