#!/bin/bash
# Rehearsals of s1b_round3_dispatch.sh and s1b_topup_dispatch.sh (stage s1b_stage_round3.tar) on deep-server with stub PBS:
# round 2's verified W1 (48 incomplete) and W2-a (7,076 incomplete, 13 invalid) summaries standing in for the final ones,
# the round-2 sources installed, a production-like ledger, real install, select, preflight (fixtures) and seeds.
# CASE = pos (then a rerun that must resume; then the W1 round-3 jobs finished and a W2-only topup, released and rerun)
#      | checksum | notF | bad_sha | err_not_invalid | badref. Negative cases must stop before install, settings,
#      ledger or PBS as their gate requires. Usage: rehearsal_round3.sh CASE STAGE_TAR STUBS_DIR
set -uo pipefail
CASE=$1; TAR=$2; IN=$3; V=/data/fable/vortex; X=$V/r3d_rehearse_$CASE; P=$V/v2_dev/p3
rm -rf $X; mkdir -p $X/src $X/s1b/run2 $X/bin
cp -a $V/r2dev6/src/. $X/src/
cp $P/w1_r2/p3_settings_r2.json $P/p3_metric.json $X/s1b/; ln -s $V/v2_dev/p2/s1a_main/main $X/s1b/pilot
cp $P/w1_r2/collect_W1.json $X/s1b/run2/collect_W1_b.json; cp $P/w2_a/collect_W2.json $X/s1b/run2/collect_W2_b.json
if [ "$CASE" = err_not_invalid ]; then
  python3 - $X/s1b/run2/collect_W2_b.json <<'PY'
import json, sys
c = json.load(open(sys.argv[1])); ok = next(r["dir"] for r in c["rows"] if r["status"] == "incomplete")
c["errors"][0] = ok + ":" + c["errors"][0].split(":", 1)[1]; json.dump(c, open(sys.argv[1], "w"))
PY
fi
S1=$(sha256sum $X/s1b/run2/collect_W1_b.json | cut -d" " -f1); S2=$(sha256sum $X/s1b/run2/collect_W2_b.json | cut -d" " -f1)
[ "$CASE" = bad_sha ] && S2=$(printf '0%.0s' $(seq 64))
SHA=$(sha256sum $X/s1b/p3_settings_r2.json | cut -d" " -f1)
{ printf "reserve\ts1b\tW1\ts1b_5e346b76_a\t199688.000\t2026-10-17T10:55:43+1100\tsettings=86545d6b outdir=/u/bwbrook/vortex/run1/s1b/run jobs=520 cpus=8 wall=172800\n"
  printf "release\ts1b_5e346b76_a\tmanual: F\n"
  printf "reserve\ts1b\tW1\ts1b_22b89261_a\t115208.000\t2026-10-21T21:53:06+1100\tsettings=$SHA outdir=$X/s1b/run2 jobs=300 cpus=8 wall=172800\n"
  printf "reserve\ts1b\tW2\ts1b_3a5e71fa_a\t218888.000\t2026-10-21T22:06:19+1100\tsettings=$SHA outdir=$X/s1b/run2 jobs=570 cpus=8 wall=172800\n"
  printf "release\ts1b_22b89261_a\tmanual: F\n"
  printf "reserve\ts1b\tW1\ts1b_b373da8c_a\t65288.000\t2026-10-25T16:19:21+1100\tsettings=$SHA outdir=$X/s1b/run2 jobs=170 cpus=8 wall=172800\n"
  printf "reserve\ts1b\tW2\ts1b_f093f541_a\t146312.000\t2026-10-25T16:22:46+1100\tsettings=$SHA outdir=$X/s1b/run2 jobs=381 cpus=8 wall=172800\n"; } > $X/s1b/reservations.tsv
python3 -c "
exec(open('$IN/stubs.py').read())
for k in ('qsub', 'qselect'): open('$X/bin/' + k, 'w').write('#!/usr/bin/python3\n' + STUBS[k])"
cp $IN/rehearsal_round3_stub_qstat.py $X/bin/qstat; echo '[]' > $X/jobs.json; chmod +x $X/bin/*
printf 'export OMP_NUM_THREADS=1 PATH="$VBASE/bin:$PATH"\ncd "$VBASE/src"\n' > $X/src/analysis/fable/calibration/kunanyi/env.sh
export PATH=$X/bin:$PATH PBS_BIN=$X/bin FIX_STATE=$X/jobs.json FIX_LEDGER=$X/qsub_ledger.jsonl FIX_CALLS=$X/qsub_calls.jsonl FIX_QSELECT_CALLS=$X/qselect.n S1A_CONFIRM_SECS=0 PBS_USER=bwbrook
[ "$CASE" = notF ] && export FIX_NOT_F=860993
cp $TAR $X/s1b_stage_round3.tar; cd $X && mkdir stage_round3 && tar -xf s1b_stage_round3.tar -C stage_round3
[ "$CASE" = checksum ] && echo "# tampered" >> stage_round3/src/analysis/fable/calibration/v2_dev/p3_stage1b.py
K=$X/src/analysis/fable/calibration/kunanyi
run() { VB=$X W1_SUMMARY_SHA=$S1 W2_SUMMARY_SHA=$S2 bash $X/stage_round3/src/analysis/fable/calibration/kunanyi/s1b_round3_dispatch.sh > $X/dispatch_$1.log 2>&1; echo $?; }
topup() { VB=$X LABEL=b WAVES=W2 REF="$1" RELEASES="$2" bash $K/s1b_topup_dispatch.sh > $X/topup_$3.log 2>&1; echo $?; }
if [ "$CASE" = badref ]; then
  rc1=$(run 1); rc2=$(topup 999999.fixture "" 1)
else
  rc1=$(run 1); rc2=x; [ "$CASE" = pos ] && rc2=$(run 2)
fi
nq=$(cat $X/qsub_calls.jsonl 2>/dev/null | wc -l); nl=$(wc -l < $X/s1b/reservations.tsv)
inst=$(cmp -s $X/src/analysis/fable/calibration/v2_dev/p3_stage1b.py $X/stage_round3/src/analysis/fable/calibration/v2_dev/p3_stage1b.py && echo new-runner || echo round2-runner)
echo "CASE $CASE rc1=$rc1 rc2=$rc2 qsub_calls=$nq ledger_lines=$nl settings_r3=$([ -e $X/s1b/p3_settings_r3.json ] && echo yes || echo no) src_runner=$inst | $(grep -v '^ ' $X/dispatch_1.log | tail -n 1 | cut -c1-120)"
if [ "$CASE" = pos ]; then
  grep -E "round 2 W|release|already released|submit W|live requests|p3_settings_r3|DISPATCH_DONE" $X/dispatch_1.log $X/dispatch_2.log | cut -c1-160
  W1A=$(python3 -c "import json; j=[x for x in json.load(open('$X/jobs.json')) if 'WAVE=W1' in ' '.join(x['args']) and '-J' in x['args']]; print(j[0]['id'], j[0]['name'])")
  W1C=$(python3 -c "import json; j=[x for x in json.load(open('$X/jobs.json')) if 'WAVE=W1' in ' '.join(x['args']) and '-J' not in x['args']]; print(j[0]['id'])")
  W2A=$(python3 -c "import json; j=[x for x in json.load(open('$X/jobs.json')) if 'WAVE=W2' in ' '.join(x['args']) and '-J' in x['args']]; print(j[0]['id'])")
  python3 - $X/jobs.json "${W1A%% *}" "$W1C" <<'PY'
import json, sys
p, *ids = sys.argv[1:]; jobs = json.load(open(p))
for j in jobs:
    if j["id"] in ids: j["state"] = "F"
json.dump(jobs, open(p, "w"))
PY
  rc3=$(topup "$W2A" "${W1A#* }=${W1A%% *},$W1C" 1); n3=$(cat $X/qsub_calls.jsonl | wc -l)
  rc4=$(topup "$W2A" "${W1A#* }=${W1A%% *},$W1C" 2); n4=$(cat $X/qsub_calls.jsonl | wc -l)
  echo "TOPUP rc3=$rc3 qsub_calls=$n3 rc4=$rc4 qsub_calls=$n4 ledger_lines=$(wc -l < $X/s1b/reservations.tsv)"
  grep -E "release|already|live requests|W2 (topup|resume)|TOPUP_DONE" $X/topup_1.log $X/topup_2.log | cut -c1-160
  tail -n 4 $X/s1b/reservations.tsv | cut -c1-160
  wc -l < $X/s1b/dirs_r3.txt; cat $X/s1b/dirs_r3_counts.txt; sha256sum $X/s1b/p3_settings_r3.json
  ls $X/s1b/run3; for w in W1 W2; do grep -c . $X/s1b/run3/submit_$w/submit_journal.tsv; done
fi
