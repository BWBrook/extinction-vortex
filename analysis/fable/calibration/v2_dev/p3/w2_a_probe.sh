export VBASE=/u/bwbrook/vortex/run1
S=$VBASE/s1b; R=$S/run2; Q=/opt/pbs/bin/qstat
echo "== now $(TZ=Australia/Hobart date '+%F %T %Z')"
for j in 858017 860990 860993; do echo "-- $j: $($Q -x -f $j | grep -E 'job_state|Exit_status|stime|mtime' | tr -s ' ' | tr '\n' ' ')"; done
for j in '858016[]' '860989[]' '860992[]'; do echo "-- $j: $($Q -x -f "$j" | grep -E 'job_state|array_state_count' | tr -s ' ' | tr '\n' ' ')"; done
echo "live requests: $($Q -t -u bwbrook | awk '$2 == "bwbrook" && $1 !~ /\[\]/ && $10 ~ /^[QRHWTSE]$/ {n += $7} END {print n + 0}') CPUs"
ls -la $R | grep -E 'collect_|W2|W1_b|pack_'; tail -n 2 $R/collect_W2.log; cat $R/W2.tar.gz.sha256 2>/dev/null
source $VBASE/src/analysis/fable/calibration/kunanyi/env.sh >/dev/null 2>&1
python -I - <<'PY'
import json, collections, re
c = json.load(open("/u/bwbrook/vortex/run1/s1b/run2/collect_W2.json"))
print("W2 collection_ok", c["collection_ok"], "status", c["status"], "n_errors", c["n_errors"], "incomplete", len(c["incomplete"]),
      "useful", round(c["useful_cpu_h"]), "discarded", round(c["discarded_cpu_h"]), "queue_left", c["queue_left"], "claims_left", c["claims_left"], "tag", c.get("tag"))
for k, v in collections.Counter(re.sub(r"\d+", "N", e.split(": ", 1)[1])[:140] for e in c["errors"]).most_common(8): print(v, k)
print("row status", dict(collections.Counter(r["status"] for r in c["rows"])))
PY
for w in W1_b W2_b W2; do L=$R/submit_$w/logs; [ -d $L ] && echo "$w: done $(ls $L | grep -c '^done\.') restarts75 $(grep -h 'exited 75' $L/w.* 2>/dev/null | wc -l) other-exits $(grep -h 'exited' $L/w.* 2>/dev/null | grep -vc 'exited 75') cert-fail $(grep -h 'could not be published' $L/w.* 2>/dev/null | wc -l) idle-retire $(grep -h 'slot retires' $L/w.* 2>/dev/null | wc -l)"; done
echo W2A_DONE
