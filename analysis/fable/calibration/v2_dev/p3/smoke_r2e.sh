#!/bin/bash
# Round-2 fault-injection smoke on deep-server: node scripts as PBS would run them, a foreign-host ghost lock on s00073
# released only by a death certificate at 15 min, and a kill -9 of a random worker every 4 min until 40 min.
set -u
export VBASE=/data/fable/vortex/r2dev6; S=$VBASE/s1b; RUN=$S/smoke_r2; SET=p3_settings_smoke_r2.json
P="python3 -I $VBASE/src/analysis/fable/calibration/v2_dev/p3_stage1b.py"
rm -rf $RUN; mkdir -p $RUN/submit_W1/logs $RUN/submit_W2/logs; cd $VBASE/src
for w in W1 W2; do $P seed $S/$SET $S/pilot $RUN $w; done
G=$RUN/sets/s00073/lock; mkdir $G
echo "{\"owner\": \"ghost[0].elsewhere.0r0\", \"host\": \"elsewhere\", \"pid\": 1, \"token\": \"ghost\"}" > $G/owner.json
T0=$(date +%s); echo "start $(date +%T)" > $RUN/inject.log
run_node() { env VBASE=$VBASE SETTINGS=$SET OUTDIR=smoke_r2 WAVE=$1 JOBCPUS=$2 WALL_SECS=5400 PBS_JOBID="$3" PBS_ARRAY_INDEX=$4 TAG=$1 \
  bash $VBASE/src/analysis/fable/calibration/kunanyi/s1b_node.pbs > $RUN/submit_$1/logs/node.$4.out 2>&1; echo "node $3 rc $?" >> $RUN/inject.log; }
run_node W1 8 "smk[0].deep" 0 & run_node W1 8 "smk[1].deep" 1 & run_node W2 4 "smk2[0].deep" 0 &
( while [ $(( $(date +%s) - T0 )) -lt 1800 ]; do
    sleep 180
    v=$(pgrep -f "p3_stage1b.py work .*r2dev6/s1b/smoke_r2" | shuf -n 1); [ -n "$v" ] && kill -9 $v && echo "$(date +%T) killed $v ($(( $(date +%s) - T0 ))s)" >> $RUN/inject.log
  done ) &
( sleep 900; printf "%s\n" "{\"owner\": \"ghost[0].elsewhere.0r0\", \"host\": \"elsewhere\", \"pid\": 1, \"rc\": 137}" > $RUN/workers/dead/.ghost.tmp && mv $RUN/workers/dead/.ghost.tmp $RUN/workers/dead/"ghost[0].elsewhere.0r0"; echo "$(date +%T) ghost certified (JSON)" >> $RUN/inject.log ) &
( while pgrep -f "s1b_node.pbs" > /dev/null; do
    for w in W1 W2; do ps -o rss=,args= -C python | grep "work .*smoke_r2 $w" | awk -v w=$w "{print w, \$1}"; done >> $RUN/rss.txt; sleep 30
  done ) &
wait
for w in W1 W2; do $P collect $S/$SET $S/p3_metric.json $RUN $w $RUN/collect_$w.json > $RUN/collect_$w.log 2>&1; tail -n 1 $RUN/collect_$w.log; done
echo DONE $(date +%T) >> $RUN/inject.log
