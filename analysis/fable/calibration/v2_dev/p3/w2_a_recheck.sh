export VBASE=/u/bwbrook/vortex/run1
source $VBASE/src/analysis/fable/calibration/kunanyi/env.sh >/dev/null 2>&1
echo "== $(TZ=Australia/Hobart date '+%F %T %Z') read-only recheck of W2 invalid settings"
python -I - <<'PY'
import json, os, sys
sys.path.insert(0, "/u/bwbrook/vortex/run1/src/analysis/fable/calibration/v2_dev"); os.chdir("/u/bwbrook/vortex/run1/src")
import p3_stage1b as p3
R = "/u/bwbrook/vortex/run1/s1b/run2"; c = json.load(open(os.path.join(R, "collect_W2.json")))
b = json.load(open("/u/bwbrook/vortex/run1/s1b/p3_settings_r2.json")); m = json.load(open("/u/bwbrook/vortex/run1/s1b/p3_metric.json"))
by = {s["dir"]: s for s in b["settings"]}; claimed = os.listdir(os.path.join(R, "claimed")); queue = os.listdir(os.path.join(R, "queue"))
for e in c["errors"]:
    d = e.split(":", 1)[0]; st = by[d]; sdir = os.path.join(R, "sets", d)
    L = len(m["outers"][f"{st['pop']}|{st['outer']}"]["recorded"]); bad = []
    for a, b_ in p3.ranges(sdir):
        S = p3.shard_state(sdir, a)
        if S is None: continue
        jp = os.path.join(sdir, f"sh{a:09d}_hits.jsonl"); size = os.path.getsize(jp) if os.path.exists(jp) else -1
        try:
            p3.verified(S, jp, a, a + S["batches_done"], L, S["status"] in ("complete", "failed", "cancelled"))
        except Exception as ex:
            rng = f"{a:09d}_{b_:09d}"
            bad.append(f"[{a},{b_}) {S['status']} done={S['batches_done']} jbytes={S['journal_bytes']} file={size}: {ex} | claims={[x.split('@')[1] for x in claimed if rng in x]} queued={sum(rng in x for x in queue)}")
    print(d, "terminal", p3.terminal(sdir), "| still bad:" if bad else "| now verifies", *bad[:3], sep=" ")
PY
echo RECHECK_DONE
