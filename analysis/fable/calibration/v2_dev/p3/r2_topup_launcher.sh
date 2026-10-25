VB=/u/bwbrook/vortex/run1; cd $VB || exit 1
echo "== $(TZ=Australia/Hobart date '+%F %T %Z') on $(uname -n)"
printf '%s\n' "8fe102080e1433ef880f0d1f30f8ef5cd127881c46cde0ae44bf38a40e5729c6  s1b_node_topup.pbs" "e85c24b90448a291a02db3e0e12c7d5aada8836af1f74dfb90e56e3c483e1d26  s1b_topup_dispatch.sh" | sha256sum -c - || { echo PUSHED_FILES_MISMATCH; exit 1; }
sha256sum src/analysis/fable/calibration/kunanyi/s1b_submit.sh src/analysis/fable/calibration/kunanyi/s1b_collect.pbs src/analysis/fable/calibration/v2_dev/p3_stage1b.py | cut -c1-16,65-
sha256sum s1b/probe/w1r2_determinism.json
if pgrep -u bwbrook -f s1b_topup_dispatch.sh > /dev/null; then echo "a topup dispatch is already running"; exit 1; fi
NODE_SHA=8fe102080e1433ef880f0d1f30f8ef5cd127881c46cde0ae44bf38a40e5729c6 LABEL=b nohup bash s1b_topup_dispatch.sh > s1b/topup_b.log 2>&1 < /dev/null & pid=$!
sleep 1; tail -n +1 -f --pid=$pid s1b/topup_b.log
wait $pid; echo "TOPUP_EXIT $?"
/opt/pbs/bin/qstat -u bwbrook | tail -n 8
