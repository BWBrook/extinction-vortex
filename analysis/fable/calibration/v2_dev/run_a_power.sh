#!/bin/bash
# A power screen (notes/vortex_v2_dev_plan_20261011.md §9), deep-server: two slots of 300 trials, 30 R workers each.
# Slot 1 starts after slot 0 has built its C+ bank, to stagger the memory peak. Set A_SMOKE=1 for the smoke test.
set -eo pipefail
D=${A_DIR:-/data/fable/vortex/v2_dev/a_power}
SRC=/data/fable/vortex/kunanyi_stage/run1/src
BASE=/data/fable/vortex/kunanyi_run1/extract
M=../validation_manifest.json
P="python3 -I /data/fable/vortex/v2_dev/a_power.py"
mkdir -p $D; cd $SRC
echo "start $(date -Is)" >> $D/timeline.txt
[ -s $D/a_power_outers.json ] || $P prepare $M $BASE $D/a_power_outers.json > $D/prepare.log 2>&1
$P run $M $BASE $D/a_power_outers.json $D 0 2 30 > $D/slot0.log 2>&1 &
p0=$!
until grep -q "^bank wood_turtle_B" $D/slot0.log 2>/dev/null; do kill -0 $p0 2>/dev/null || break; sleep 20; done
echo "slot0 bank built $(date -Is)" >> $D/timeline.txt
$P run $M $BASE $D/a_power_outers.json $D 1 2 30 > $D/slot1.log 2>&1 &
p1=$!
rc=0; wait $p0 || rc=$?; wait $p1 || rc=$((rc + $?))
echo "slots rc=$rc $(date -Is)" >> $D/timeline.txt
[ "$rc" -eq 0 ] || exit "$rc"
$P report $M $BASE $D/a_power_outers.json $D 2 $D/a_power_report.json > $D/report.log 2>&1
echo "done $(date -Is)" >> $D/timeline.txt
