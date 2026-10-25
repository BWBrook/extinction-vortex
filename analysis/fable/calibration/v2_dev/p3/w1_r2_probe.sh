export VBASE=/u/bwbrook/vortex/run1
S=$VBASE/s1b; R=$S/run2; P=$S/probe; Q=/opt/pbs/bin/qstat; t0=$(date +%s); el() { echo "   [+$(( $(date +%s) - t0 ))s]"; }
echo "== now $(TZ=Australia/Hobart date '+%F %T %Z')"
echo "-- W1 r2 collector 857923: $($Q -x -f 857923 | grep -E 'job_state|Exit_status|resources_used.walltime|stime|mtime' | tr -s ' ' | tr '\n' ' ')"
echo "-- W1 r2 array 857922[]: $($Q -x -f '857922[]' | grep -E 'job_state|array_state_count' | tr -s ' ' | tr '\n' ' ')"
echo "-- W2 array 858016[]: $($Q -f '858016[]' 2>&1 | grep -E 'job_state|array_state_count' | tr -s ' ' | tr '\n' ' ')"
echo "-- W2 collector 858017: $($Q -x -f 858017 | grep -E 'job_state' | tr -s ' ')"
ls -la $R | grep -E 'collect_|W1|pack_'; tail -n 3 $R/collect_W1.log; cat $R/W1.tar.gz.sha256 2>/dev/null; el
source $VBASE/src/analysis/fable/calibration/kunanyi/env.sh >/dev/null 2>&1
python -I - <<'PY'
import json, collections, re
c = json.load(open("/u/bwbrook/vortex/run1/s1b/run2/collect_W1.json"))
print("collection_ok", c["collection_ok"], "status", c["status"], "n_errors", c["n_errors"], "incomplete", len(c["incomplete"]),
      "useful", round(c["useful_cpu_h"]), "discarded", round(c["discarded_cpu_h"]), "queue_left", c["queue_left"], "claims_left", c["claims_left"], "tag", c.get("tag"))
for k, v in collections.Counter(re.sub(r"\d+", "N", e.split(": ", 1)[1])[:140] for e in c["errors"]).most_common(10): print(v, k)
print("row status", dict(collections.Counter(r["status"] for r in c["rows"])))
b = json.load(open("/u/bwbrook/vortex/run1/s1b/p3_settings_r2.json"))
w1 = [s["dir"] for s in b["settings"] if s["wave"] == "W1"]
open("/u/bwbrook/vortex/run1/s1b/probe/w1r2_dirs.txt", "w").write("\n".join(w1) + "\n")
print("W1 r2 settings", len(w1), "rows", len(c["rows"]), "same set", set(w1) == {r["dir"] for r in c["rows"]})
PY
el
echo "== determinism: round 1 run vs run2 over the W1 r2 dirs"
cd $VBASE/src && nohup python -I analysis/fable/calibration/v2_dev/p3_r2_determinism.py $S/run $S/run2 $P/w1r2_dirs.txt $P/w1r2_determinism.json > $P/w1r2_determinism.log 2>&1 < /dev/null & dp=$!
wait $dp; echo "determinism exit $?"; tail -n 2 $P/w1r2_determinism.log; el
echo W1R2_DONE
