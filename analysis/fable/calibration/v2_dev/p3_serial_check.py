"""Recompute each COMPLETE smoke setting serially (pilot prefix + one unsharded range from the pilot end) and compare
its first-K library bytes with the sharded library. Independent of p3 planning, claims and assembly."""
import hashlib, json, os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p2_stage1a as p2
settings, metric, run, d = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
b = json.load(open(settings)); m = json.load(open(metric)); des = p2.designs()
st = next(x for x in b["settings"] if x["dir"] == d)
pl = st["pilot"]; sdir = os.path.join(run, "sets", d)
lines = open(os.path.join(sdir, "pilot_hits.jsonl"), "rb").read().splitlines(True) if pl else []
if len(lines) < 2000:
    mp = dict(m["outers"][f"{st['pop']}|{st['outer']}"], keep=m["pops"][st["pop"]]["keep"], mad=m["pops"][st["pop"]]["mad"])
    sst = {"index": st["index"], "pop": st["pop"], "outer": st["outer"], "n": st["n"], "E": st["E"], "stream_tag": st["stream_tag"],
           "proposal_budget": st["cap_batches"] * 20000, "batches": st["cap_batches"] - pl["batches_done"]}
    tmp = tempfile.mkdtemp()
    S = p2.run_setting({"batch": 20000, "hit_stop": 2000 - len(lines), "_binding": {"serial": True}}, sst, mp, tmp, float("inf"), des,
                       first_batch=pl["batches_done"], name="serial")
    lines += open(os.path.join(tmp, "serial_hits.jsonl"), "rb").read().splitlines(True)
lib = b"".join(lines[:2000]); shard = open(os.path.join(run, "lib", f"{d}.jsonl"), "rb").read()
print(json.dumps({"dir": d, "serial_sha256": hashlib.sha256(lib).hexdigest(), "sharded_sha256": hashlib.sha256(shard).hexdigest(),
                  "identical": lib == shard}))
