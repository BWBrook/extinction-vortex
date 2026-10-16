"""Same two-contender interleaving against a given p3 module: peak concurrent holders."""
import importlib.util, json, os, subprocess, sys, tempfile, threading, time
from unittest import mock
sys.path.insert(0, "analysis/fable/calibration/v2_dev")
spec = importlib.util.spec_from_file_location("p3x", sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
sdir = tempfile.mkdtemp(); pd = subprocess.Popen(["true"]); pd.wait()
os.mkdir(os.path.join(sdir, "lock"))
json.dump({"owner": "t:dead", "host": os.uname().nodename, "pid": pd.pid, "token": "dead"}, open(os.path.join(sdir, "lock", "owner.json"), "w"))
barrier, seen, guard = threading.Barrier(2), set(), threading.Lock(); real = m.owner_dead
def od(info, qstat=m.QSTAT):
    r = real(info, qstat)
    if info.get("token") == "dead" and threading.get_ident() not in seen:
        seen.add(threading.get_ident())
        if barrier.wait(10) == 0:
            time.sleep(0.3)          # this contender acts on its stale observation after the other has acquired
    return r
active, peak = [0], [0]
def contender(n):
    L = m.lock(sdir, n, "/bin/false")
    with guard: active[0] += 1; peak[0] = max(peak[0], active[0])
    time.sleep(0.5)
    with guard: active[0] -= 1
    try: m.unlock(L)
    except Exception as e: print("unlock:", type(e).__name__)
with mock.patch.object(m, "owner_dead", od):
    ts = [threading.Thread(target=contender, args=(n,), daemon=True) for n in ("A", "B")]
    [t.start() for t in ts]; [t.join(30) for t in ts]
print(sys.argv[1].rsplit("/", 1)[-1], "peak concurrent holders:", peak[0])
