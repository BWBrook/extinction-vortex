export VBASE=/u/bwbrook/vortex/run1
R=$VBASE/s1b/run; Q=/opt/pbs/bin/qstat; t0=$(date +%s); el() { echo "   [+$(( $(date +%s) - t0 ))s]"; }
echo "== now $(TZ=Australia/Hobart date '+%F %T %Z')"
ls -la $R | grep -E 'collect_|W1.tar|pack_' ; el
echo "queue $(ls $R/queue | wc -l)  claimed $(ls $R/claimed | wc -l)  worker-exits $(ls $R/workers | wc -l)"
L=$R/submit_W1/logs; echo "jobs.log lines $(cat $L/jobs.log 2>/dev/null | wc -l)  with failed workers $(grep -c 'failed: [1-9]' $L/jobs.log 2>/dev/null)"; el
$Q -f '821088[]' 2>&1 | grep -E 'job_state|array_state_count|qstat'; $Q -f 821089 2>&1 | grep -E 'job_state|qstat'; el
source $VBASE/src/analysis/fable/calibration/kunanyi/env.sh >/dev/null 2>&1; el
python -I - <<'PY'
import json, os, collections, time, glob
from concurrent.futures import ThreadPoolExecutor
R = "/u/bwbrook/vortex/run1/s1b/run"; t = time.time()
W = collections.Counter()
for f in glob.glob(os.path.join(R, "workers", "*.json")):
    try: W.update({k: v for k, v in json.load(open(f)).items() if isinstance(v, int)})
    except Exception: W["unreadable"] += 1
print("worker exits totals", dict(W))
S = [s for s in json.load(open("/u/bwbrook/vortex/run1/s1b/p3_settings.json"))["settings"] if s["wave"] == "W1"]
def one(s):
    d = os.path.join(R, "sets", s["dir"]); ls = set(os.listdir(d)) if os.path.isdir(d) else set()
    m = next((x for x in ("COMPLETE", "CAPPED", "FAILED") if x in ls), "open")
    h = (s.get("pilot") or {}).get("hits", 0); c = 0.0; st_ = collections.Counter()
    for f in (x for x in ls if x.startswith("sh") and x.endswith(".json")):
        try: st = json.load(open(os.path.join(d, f)))
        except Exception: st_["unreadable"] += 1; continue
        c += st.get("cpu_seconds", 0); st_[st["status"]] += 1; h += st.get("hits", 0)
    return s["n"], m, h, c, st_, s["dir"]
with ThreadPoolExecutor(24) as ex: res = list(ex.map(one, S))
by = collections.defaultdict(collections.Counter); cpu = collections.Counter(); sh = collections.Counter(); prog = collections.defaultdict(list); big = []
for n, m, h, c, st_, d in res:
    by[n][m] += 1; cpu[n] += c; sh.update(st_)
    if m == "open": prog[n].append(min(h, 2000) / 2000); big.append((c / 3600, d, n, h))
for n in sorted(by):
    p = sorted(prog[n]); q = lambda f: p[int(f * (len(p) - 1))] if p else float("nan")
    print(f"n={n}: {dict(by[n])}  worker CPU-h {cpu[n]/3600:.0f}  open hit-progress median {q(.5):.2f} p10 {q(.1):.2f} p90 {q(.9):.2f}")
print("shard states", dict(sh), " total worker CPU-h", round(sum(cpu.values()) / 3600), f" scan {time.time()-t:.0f}s")
print("open settings by CPU-h so far (top 12): ", [(round(c), d, n, h) for c, d, n, h in sorted(big, reverse=True)[:12]])
PY
el; $Q -x -f '821088[]' | grep -E 'array_state_count|job_state'; el; echo PROBE_DONE
