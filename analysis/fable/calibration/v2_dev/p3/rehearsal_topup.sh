#!/bin/bash
# Rehearsal of s1b_topup_dispatch.sh with stub PBS: the production run2 shape (settings 248f9c7d, W1 and W2 seeded
# submissions), a production-like ledger, a live listing of 379 running W2 subjobs and a held collector that grows with
# each stub qsub. CASE = pos (then rerun) | badsha | badcount.
set -uo pipefail
CASE=$1; X=/data/fable/vortex/topup_rehearse_$CASE; T=/tmp/topup_reh_in
rm -rf $X; mkdir -p $X/src $X/s1b/run2/submit_W1 $X/s1b/run2/submit_W2 $X/s1b/run2/queue $X/s1b/run2/claimed $X/bin
cp -a /data/fable/vortex/r2dev6/src/. $X/src/
cp $T/s1b_submit.sh $T/s1b_collect.pbs $T/s1b_topup_dispatch.sh $X/src/analysis/fable/calibration/kunanyi/
cp /data/fable/vortex/v2_dev/p3/w1_r2/p3_settings_r2.json /data/fable/vortex/v2_dev/p3/p3_metric.json $X/s1b/
cp $T/s1b_node.pbs $X/s1b_node_topup.pbs; ln -sf "$(command -v python3)" $X/bin/python
SHA=$(sha256sum $X/s1b/p3_settings_r2.json | cut -d" " -f1)
for w in W1 W2; do n=300; [ $w = W2 ] && n=570
  echo "settings=p3_settings_r2.json sha256=$SHA outdir=$X/s1b/run2 wave=$w tag=$w jobs=$n cpus=8 walltime=48:00:00" > $X/s1b/run2/submit_$w/run.json
  printf "request a s1b_x_a\naccepted a s1b_x_a 0.fixture\n" > $X/s1b/run2/submit_$w/submit_journal.tsv
done
{ printf "reserve\ts1b\tW1\ts1b_5e346b76_a\t199688.000\t2026-10-17T10:55:43+1100\tsettings=86545d6b outdir=/u/bwbrook/vortex/run1/s1b/run jobs=520 cpus=8 wall=172800\n"
  printf "release\ts1b_5e346b76_a\tmanual: F\n"
  printf "reserve\ts1b\tW1\ts1b_22b89261_a\t115208.000\t2026-10-21T21:53:06+1100\tsettings=$SHA outdir=$X/s1b/run2 jobs=300 cpus=8 wall=172800\n"
  printf "reserve\ts1b\tW2\ts1b_3a5e71fa_a\t218888.000\t2026-10-21T22:06:19+1100\tsettings=$SHA outdir=$X/s1b/run2 jobs=570 cpus=8 wall=172800\n"; } > $X/s1b/reservations.tsv
python3 -c "
exec(open('/tmp/stage_r2_in/stubs.py').read())
for k in ('qsub', 'qselect'): open('$X/bin/' + k, 'w').write('#!/usr/bin/python3\n' + STUBS[k])"
cp $T/stub_qstat.py $X/bin/qstat; echo '[]' > $X/jobs.json; chmod +x $X/bin/*
printf 'export OMP_NUM_THREADS=1 PATH="$VBASE/bin:$PATH"\ncd "$VBASE/src"\n' > $X/src/analysis/fable/calibration/kunanyi/env.sh
export PATH=$X/bin:$PATH PBS_BIN=$X/bin FIX_CASE=$CASE FIX_STATE=$X/jobs.json FIX_LEDGER=$X/qsub_ledger.jsonl FIX_CALLS=$X/qsub_calls.jsonl FIX_QSELECT_CALLS=$X/qselect.n S1A_CONFIRM_SECS=0 PBS_USER=bwbrook
NS=$(sha256sum $T/s1b_node.pbs | cut -d" " -f1); [ "$CASE" = badsha ] && NS=$(printf '0%.0s' $(seq 64))
run() { VB=$X NODE_SHA=$NS LABEL=b W1_JOBS=170 bash $X/src/analysis/fable/calibration/kunanyi/s1b_topup_dispatch.sh > $X/dispatch_$1.log 2>&1; echo $?; }
rc1=$(run 1); rc2=x; [ "$CASE" = pos ] && rc2=$(run 2)
echo "CASE $CASE rc1=$rc1 rc2=$rc2 qsub_calls=$(cat $X/qsub_calls.jsonl 2>/dev/null | wc -l) ledger_lines=$(wc -l < $X/s1b/reservations.tsv) node_installed=$(cmp -s $T/s1b_node.pbs $X/src/analysis/fable/calibration/kunanyi/s1b_node.pbs && echo yes || echo no) | $(grep -v '^ ' $X/dispatch_1.log | tail -n 1 | cut -c1-130)"
