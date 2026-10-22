export VBASE=/u/bwbrook/vortex/run1
R=$VBASE/s1b/run2; Q=/opt/pbs/bin/qstat; t0=$(date +%s); el() { echo "   [+$(( $(date +%s) - t0 ))s]"; }
echo "== now $(TZ=Australia/Hobart date '+%F %T %Z')"
for j in '857922[]' '858016[]'; do echo "-- $j"; $Q -f "$j" 2>&1 | grep -E 'job_state|array_state_count|qstat:'; done
for j in 857923 858017; do echo "-- $j $($Q -x -f $j 2>&1 | grep -E 'job_state|Exit_status' | tr -s ' ' | tr '\n' ' ')"; done; el
echo "queue W1 $(ls $R/queue | grep -c '^W1_')  W2 $(ls $R/queue | grep -c '^W2_')  claimed $(ls $R/claimed | wc -l)  exit-records $(ls $R/workers | grep -c json)  certificates $(ls $R/workers/dead | wc -l)"
for w in W1 W2; do L=$R/submit_$w/logs; echo "$w: done-files $(ls $L | grep -c '^done\.')  failed-slot lines $(cat $L/done.* 2>/dev/null | grep -vc 'slots failed: 0')  restarts $(grep -h 'exited' $L/w.* 2>/dev/null | wc -l)  owner-uncertain $(grep -h 'owner uncertain' $L/w.* 2>/dev/null | wc -l)  transient-lines $(grep -h '^transient error' $L/w.* 2>/dev/null | wc -l)"; done; el
echo "restart exit codes:"; grep -h 'exited' $R/submit_W*/logs/w.* 2>/dev/null | awk '{print $NF}' | sort | uniq -c
echo "worker-log error tails:"; find $R/submit_W*/logs -name 'w.*.log' -size +0 -exec grep -h -E 'Error|error|Traceback' {} + 2>/dev/null | sed -E 's/[0-9]{3,}/N/g; s/\[[0-9]+\]/[N]/g' | cut -c1-150 | sort | uniq -c | sort -rn | head -12; el
source $VBASE/src/analysis/fable/calibration/kunanyi/env.sh >/dev/null 2>&1
python -I - <<'PY'
import json, os, collections, time, glob
from concurrent.futures import ThreadPoolExecutor
R = "/u/bwbrook/vortex/run1/s1b/run2"; t = time.time()
S = json.load(open("/u/bwbrook/vortex/run1/s1b/p3_settings_r2.json"))["settings"]
W = collections.Counter()
for f in glob.glob(os.path.join(R, "workers", "*.json")):
    try: W.update({k: v for k, v in json.load(open(f)).items() if isinstance(v, int)})
    except Exception: W["unreadable"] += 1
print("worker exit totals", dict(W))
def one(s):
    d = os.path.join(R, "sets", s["dir"]); ls = set(os.listdir(d)) if os.path.isdir(d) else set()
    m = next((x for x in ("COMPLETE", "CAPPED", "FAILED") if x in ls), "open")
    h = (s.get("pilot") or {}).get("hits", 0); c = 0.0
    for f in (x for x in ls if x.startswith("sh") and x.endswith(".json")):
        try: st = json.load(open(os.path.join(d, f)))
        except Exception: continue
        c += st.get("cpu_seconds", 0); h += st.get("hits", 0)
    return s["wave"], s["n"], m, h, c, s["dir"]
with ThreadPoolExecutor(24) as ex: res = list(ex.map(one, S))
by = collections.defaultdict(collections.Counter); cpu = collections.Counter(); prog = collections.defaultdict(list); big = []
for w, n, m, h, c, d in res:
    by[(w, n)][m] += 1; cpu[(w, n)] += c
    if m == "open": prog[(w, n)].append(min(h, 2000) / 2000); big.append((c / 3600, d, w, n, h))
for k in sorted(by):
    p = sorted(prog[k]); q = lambda f: p[int(f * (len(p) - 1))] if p else float("nan")
    print(f"{k[0]} n={k[1]}: {dict(by[k])}  worker CPU-h {cpu[k]/3600:.0f}  open hit-progress median {q(.5):.2f} p90 {q(.9):.2f}")
print("total worker CPU-h", round(sum(cpu.values()) / 3600), f" scan {time.time()-t:.0f}s")
print("largest open settings by CPU-h:", [(round(c), d, w, n, h) for c, d, w, n, h in sorted(big, reverse=True)[:8]])
PY
el
$Q -x -t -f '857922[]' > /u/bwbrook/vortex/run1/s1b/probe/r2_w1_subjobs.txt 2>&1; $Q -x -t -f '858016[]' > /u/bwbrook/vortex/run1/s1b/probe/r2_w2_subjobs.txt 2>&1
for f in w1 w2; do awk -v f=$f '/^Job Id: .*\[[0-9]+\]/{n++} /job_state =/{s[$3]++} /Exit_status =/{e[$3]++} /resources_used.walltime/{split($3,t,":");w+=t[1]+t[2]/60+t[3]/3600} /resources_used.cput/{split($3,t,":");c+=t[1]+t[2]/60+t[3]/3600} END{printf "%s subjobs:", f; for(k in s)printf " %s=%d",k,s[k]; printf " | exit:"; for(k in e)printf " %s=%d",k,e[k]; printf " | allocated CPU-h %.0f cput-h %.0f\n",w*8,c}' /u/bwbrook/vortex/run1/s1b/probe/r2_${f}_subjobs.txt; done; el; echo R2PROBE_DONE
