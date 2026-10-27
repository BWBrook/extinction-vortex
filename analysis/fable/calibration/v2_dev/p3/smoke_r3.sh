#!/bin/bash
# Round-3 adversarial smoke on deep-server (design 9h): node scripts as PBS runs them, but each worker's global queue/ and
# claimed/ listings omit every entry with probability 0.3 (smoke_omit.py); a foreign-host ghost lock on s00073 released
# only by a death certificate at 15 min; a kill -9 of a random worker every 3 min until 30 min. Usage:
#   smoke_r3.sh VBASE OUTDIR SETTINGS      (candidate: r3dev1 smoke_r3 p3_settings_smoke_r3.json;
#                                           bound control: r2dev6 smoke_r3ctl p3_settings_smoke_r2.json)
set -u
export VBASE=$1; S=$VBASE/s1b; OUT=$2; RUN=$S/$OUT; SET=$3; export OMIT_P=0.3
C=$VBASE/src/analysis/fable/calibration; P="python3 -I $C/v2_dev/p3_stage1b.py"
rm -rf $RUN; mkdir -p $RUN/submit_W1/logs $RUN/submit_W2/logs; cd $VBASE/src
sed 's#v2_dev/p3_stage1b.py work#v2_dev/p3/smoke_omit.py work#' $C/kunanyi/s1b_node.pbs > $RUN/s1b_node_omit.pbs
grep -q 'smoke_omit.py work' $RUN/s1b_node_omit.pbs || { echo "node copy not redirected"; exit 1; }
for w in W1 W2; do $P seed $S/$SET $S/pilot $RUN $w; done
G=$RUN/sets/s00073/lock; mkdir $G
echo "{\"owner\": \"ghost[0].elsewhere.0r0\", \"host\": \"elsewhere\", \"pid\": 1, \"token\": \"ghost\"}" > $G/owner.json
T0=$(date +%s); echo "start $(date +%T) omit_p $OMIT_P runner $(sha256sum $C/v2_dev/p3_stage1b.py | cut -c1-16)" > $RUN/inject.log
run_node() { env VBASE=$VBASE SETTINGS=$SET OUTDIR=$OUT WAVE=$1 JOBCPUS=$2 WALL_SECS=5400 PBS_JOBID="$3" PBS_ARRAY_INDEX=$4 TAG=$1 \
  bash $RUN/s1b_node_omit.pbs > $RUN/submit_$1/logs/node.$4.out 2>&1; echo "node $3 rc $?" >> $RUN/inject.log; }
run_node W1 8 "smk[0].deep" 0 & run_node W1 8 "smk[1].deep" 1 & run_node W2 4 "smk2[0].deep" 0 &
( while [ $(( $(date +%s) - T0 )) -lt 1800 ]; do
    sleep 180
    v=$(pgrep -f "smoke_omit.py work .*$S/$OUT " | shuf -n 1); [ -n "$v" ] && kill -9 $v && echo "$(date +%T) killed $v ($(( $(date +%s) - T0 ))s)" >> $RUN/inject.log
  done ) &
( sleep 900; printf "%s\n" "{\"owner\": \"ghost[0].elsewhere.0r0\", \"host\": \"elsewhere\", \"pid\": 1, \"rc\": 137}" > $RUN/workers/dead/.ghost.tmp && mv $RUN/workers/dead/.ghost.tmp $RUN/workers/dead/"ghost[0].elsewhere.0r0"; echo "$(date +%T) ghost certified (JSON)" >> $RUN/inject.log ) &
wait
for w in W1 W2; do $P collect $S/$SET $S/p3_metric.json $RUN $w $RUN/collect_$w.json > $RUN/collect_$w.log 2>&1; echo "collect $w rc $?" >> $RUN/inject.log; tail -n 1 $RUN/collect_$w.log; done
python3 -I $C/v2_dev/p3_r2_determinism.py /data/fable/vortex/v2_dev/p3/smoke_deep3 $RUN <(printf 's00073\ns00142\ns00247\ns00772\ns01080\nc00021\n') $RUN/determinism_vs_deep3.json > /dev/null 2>&1
echo "determinism rc $?" >> $RUN/inject.log
echo DONE $(date +%T) >> $RUN/inject.log
