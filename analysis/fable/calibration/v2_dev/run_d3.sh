#!/bin/bash
# D3 paired oracle contrast (notes/vortex_v2_dev_plan_20261011.md §2), deep-server
set -eo pipefail
D=/data/fable/vortex/v2_dev/d3
SRC=/data/fable/vortex/kunanyi_stage/run1/src
BASE=/data/fable/vortex/kunanyi_run1/extract
M=../validation_manifest.json
P="python3 -I /data/fable/vortex/v2_dev/d3_oracle.py"
mkdir -p $D; cd $SRC
sha256sum /data/fable/vortex/v2_dev/d3_oracle.py > $D/runner_sha256.txt
echo "start $(date -Is)" >> $D/timeline.txt
[ -s $D/outers.json ] || $P outers $M $D/outers.json > $D/outers.log 2>&1
echo "outers $(date -Is)" >> $D/timeline.txt
[ -s $D/oracle/oracle_meta.json ] || $P bank $M $D/oracle 60 > $D/bank.log 2>&1
echo "bank $(date -Is)" >> $D/timeline.txt
$P run V $M $BASE $D/outers.json $D/oracle $D/V 30 > $D/V.log 2>&1 &
pv=$!
$P run O $M $BASE $D/outers.json $D/oracle $D/O 30 > $D/O.log 2>&1 &
po=$!
rc=0; wait $pv || rc=$?; wait $po || rc=$((rc + $?))
echo "arms rc=$rc $(date -Is)" >> $D/timeline.txt
$P score $M $D/outers.json $D/V $D/O $D/score.json > $D/score.log 2>&1
echo "done $(date -Is)" >> $D/timeline.txt
