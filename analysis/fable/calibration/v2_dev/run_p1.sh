#!/bin/bash
# Informative-sampler prototype: tests, bank scan, then the balanced pilot, all within a 30-minute wall ceiling.
# One worker; numerical libraries single-threaded.
set -eo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 FLEXIBLAS_NUM_THREADS=1
D=/data/fable/vortex/v2_dev/p1
M=../validation_manifest.json; BASE=/data/fable/vortex/kunanyi_run1/extract
P="python3 -I /data/fable/vortex/v2_dev/p1_sampler.py"
cd /data/fable/vortex/kunanyi_stage/run1/src
T0=$(date +%s); echo "start $(date -Is)" > $D/timeline.txt
/usr/bin/time -v $P test $M $BASE $D/p1_bound.json > $D/test.log 2>&1
echo "test $(date -Is)" >> $D/timeline.txt
/usr/bin/time -v $P scan $M $BASE $D/p1_bound.json $D/p1_scan.json > $D/scan.log 2>&1
echo "scan $(date -Is)" >> $D/timeline.txt
LEFT=$(( 1800 - ($(date +%s) - T0) - 60 ))
echo "pilot budget seconds $LEFT" >> $D/timeline.txt
/usr/bin/time -v $P pilot $M $BASE $D/p1_bound.json $D/p1_pilot.json $LEFT > $D/pilot.log 2>&1
echo "done $(date -Is) total_seconds $(( $(date +%s) - T0 ))" >> $D/timeline.txt
