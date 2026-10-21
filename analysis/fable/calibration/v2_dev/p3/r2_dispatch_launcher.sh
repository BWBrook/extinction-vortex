VB=/u/bwbrook/vortex/run1; cd $VB || exit 1
echo "== $(TZ=Australia/Hobart date '+%F %T %Z') on $(uname -n)"
echo "ae12731301848d9c2caca2f5b05e2e02c3c91566522d9056f92348bce098faaf  s1b_stage_r2.tar" | sha256sum -c - || { echo STAGE_TAR_MISMATCH; exit 1; }
if [ -e s1b/run2 ]; then echo "note: s1b/run2 exists, so the dispatch resumes"; fi
if pgrep -u bwbrook -f s1b_round2_dispatch.sh > /dev/null; then echo "a dispatch is already running"; exit 1; fi
rm -rf stage_r2 && mkdir stage_r2 && tar -xf s1b_stage_r2.tar -C stage_r2
nohup bash stage_r2/src/analysis/fable/calibration/kunanyi/s1b_round2_dispatch.sh > s1b/dispatch_r2.log 2>&1 < /dev/null & pid=$!
sleep 1; tail -n +1 -f --pid=$pid s1b/dispatch_r2.log
wait $pid; echo "DISPATCH_EXIT $?"
/opt/pbs/bin/qstat -u bwbrook | tail -n 6
