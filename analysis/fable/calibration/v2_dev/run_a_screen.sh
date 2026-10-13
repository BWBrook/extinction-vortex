#!/bin/bash
# A-screen (notes/vortex_v2_dev_plan_20261011.md §8), deep-server: two slots of 100 trials, 30 R workers each.
# Slot 1 starts after slot 0 has built its C+ bank, to stagger the memory peak.
set -eo pipefail
D=/data/fable/vortex/v2_dev/a_screen
SRC=/data/fable/vortex/kunanyi_stage/run1/src
BASE=/data/fable/vortex/kunanyi_run1/extract
M=../validation_manifest.json
P="python3 -I /data/fable/vortex/v2_dev/a_screen.py"
mkdir -p $D; cd $SRC
sha256sum /data/fable/vortex/v2_dev/{a_screen,a0_cplus,knn_nuisance_c,d3_oracle}.py > $D/runner_sha256.txt
echo "start $(date -Is)" >> $D/timeline.txt
[ -s $D/a_outers.json ] || $P prepare $M $BASE $D/a_outers.json > $D/prepare.log 2>&1
$P run $M $BASE $D/a_outers.json $D 0 2 30 > $D/slot0.log 2>&1 &
p0=$!
until grep -q "^bank wood_turtle_B" $D/slot0.log 2>/dev/null; do kill -0 $p0 2>/dev/null || break; sleep 20; done
echo "slot0 bank built $(date -Is)" >> $D/timeline.txt
$P run $M $BASE $D/a_outers.json $D 1 2 30 > $D/slot1.log 2>&1 &
p1=$!
rc=0; wait $p0 || rc=$?; wait $p1 || rc=$((rc + $?))
echo "slots rc=$rc $(date -Is)" >> $D/timeline.txt
[ "$rc" -eq 0 ] || exit "$rc"
$P report $M $BASE $D/a_outers.json $D 2 $D/a_screen_report.json > $D/report.log 2>&1
echo "done $(date -Is)" >> $D/timeline.txt
