export VBASE=/u/bwbrook/vortex/run1
R=$VBASE/s1b/run; L=$R/submit_W1/logs; Q=/opt/pbs/bin/qstat; P=$VBASE/s1b/probe; t0=$(date +%s); el() { echo "   [+$(( $(date +%s) - t0 ))s]"; }
echo "== now $(TZ=Australia/Hobart date '+%F %T %Z')"
$Q -f 821089 2>&1 | grep -E 'job_state|stime|resources_used.(walltime|mem)|Exit_status|qstat'; ls -la $R | grep -E 'collect_|W1.tar|pack_'; tail -n 3 $R/collect_W1.log 2>/dev/null; el
/opt/pbs/bin/qmgr -c 'list server' 2>&1 | grep -E 'max_array_size|max_run|max_queued|max_job_array' ; /opt/pbs/bin/qmgr -c 'list queue normal' 2>&1 | grep -E 'max_run|max_queued|resources_max|resources_default'; el
echo "== jobs.log failed lines"; grep 'failed: [1-9]' $L/jobs.log | sort | uniq -c | sort -rn | head -25; el
echo "== node .err non-empty: $(find $L -name 'node.*.err' -size +0 | wc -l)"; find $L -name 'node.*.err' -size +0 -exec cat {} + | sed -E 's/[0-9]+/N/g' | sort | uniq -c | sort -rn | head -15; el
echo "== worker logs non-empty: $(find $L -name 'w.*.log' -size +0 | wc -l)"; find $L -name 'w.*.log' -size +0 -exec tail -n 1 {} \; | sed -E 's/[0-9]{3,}/N/g' | cut -c1-200 | sort | uniq -c | sort -rn | head -25; el
echo "== exit files per subjob"; ls $R/workers | sed -E 's/^821088\[([0-9]+)\].*/\1/' | sort -n | uniq -c | awk '{c[$1]++} END {for (k in c) print "subjobs with", k, "exit files:", c[k]}'
ls $R/workers | sed -E 's/^821088\[([0-9]+)\].*/\1/' | sort -n | uniq > $P/idx_with_exits.txt; comm -23 <(seq 0 519 | sort) <(sort $P/idx_with_exits.txt) | sort -n | tr '\n' ' ' | cut -c1-600; echo; el
echo "== stale claims"; ls $R/claimed | sed -E 's/^(W1_[0-9]+_[a-z0-9]+)_.*@(.*)$/\1 \2/' | head -20; el
echo "== per-subjob PBS accounting (slow)"
$Q -x -t -f '821088[]' > $P/subjobs_f.txt 2>&1; el
awk '/^Job Id:/{if(id!="")print id,es,wt,mem,vmem,host; id=$3; es="NA"; wt="NA"; mem="NA"; vmem="NA"; host="NA"} /Exit_status =/{es=$3} /resources_used.walltime =/{wt=$3} /resources_used.mem =/{mem=$3} /resources_used.vmem =/{vmem=$3} /exec_host =/{host=$3} END{print id,es,wt,mem,vmem,host}' $P/subjobs_f.txt > $P/subjobs.tsv
echo "Exit_status counts:"; awk '$1 ~ /\[[0-9]+\]/{print $2}' $P/subjobs.tsv | sort | uniq -c | sort -rn
echo "walltime (h) distribution:"; awk '$1 ~ /\[[0-9]+\]/ && $3!="NA"{split($3,t,":"); h=t[1]+t[2]/60; b=(h>=47.75)?"≥47.75":(h>=40?"40-47.75":(h>=24?"24-40":"<24")); c[b]++} END{for(k in c)print " ",k,c[k]}' $P/subjobs.tsv
echo "mem (GB) max and top 10:"; awk '$1 ~ /\[[0-9]+\]/ && $4!="NA"{m=$4; sub(/kb/,"",m); printf "%.2f %s %s %s\n", m/1048576, $1, $2, $6}' $P/subjobs.tsv | sort -rn | head -10
echo "non-zero exits (first 30):"; awk '$1 ~ /\[[0-9]+\]/ && $2!="0"' $P/subjobs.tsv | head -30; el; echo DIAG_DONE
