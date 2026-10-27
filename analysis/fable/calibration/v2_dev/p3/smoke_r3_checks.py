"""Checks for a round-3 smoke run (smoke_r3.sh): libraries against the smoke_deep3 reference, both collections (status,
errors, execution records), worker totals, death certificates and the injection log. Usage: smoke_r3_checks.py RUN REF"""
import collections, glob, hashlib, json, os, sys

run, ref = sys.argv[1:]
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
out = {"run": run}
for f in sorted(glob.glob(os.path.join(ref, "lib", "*.jsonl"))):
    mine = os.path.join(run, "lib", os.path.basename(f))
    out[f"library {os.path.basename(f)[:-6]}"] = ("identical" if os.path.exists(mine) and sha(mine) == sha(f) else
                                                  "DIFFERS" if os.path.exists(mine) else "missing") + " " + sha(f)[:16]
for w in ("W1", "W2"):
    c = json.load(open(os.path.join(run, f"collect_{w}.json")))
    out[f"collect {w}"] = {"ok": c["collection_ok"], "status": c["status"], "n_errors": c["n_errors"], "errors": c["errors"][:6],
                           **{k: c.get(k) for k in ("executions", "dead_executions", "open_executions", "queue_left", "claims_left")}}
tot = collections.Counter()
for f in glob.glob(os.path.join(run, "workers", "*.json")):
    for k, v in json.load(open(f)).items():
        if isinstance(v, int) and not isinstance(v, bool):
            tot[k] += v
out["worker exit records"] = len(glob.glob(os.path.join(run, "workers", "*.json")))
out["worker totals"] = dict(tot)
certs = [json.load(open(f)) for f in glob.glob(os.path.join(run, "workers", "dead", "*")) if not os.path.basename(f).startswith(".")]
out["certificates"] = {"n": len(certs), "rc": dict(collections.Counter(c.get("rc") for c in certs))}
dup = collections.Counter(n.split("@")[0].split("_", 2)[2] for n in os.listdir(os.path.join(run, "claimed")))
out["claim entries left"] = sum(dup.values()); out["ranges with two claim entries left"] = sum(v > 1 for v in dup.values())
ex = collections.Counter()
for xd in glob.glob(os.path.join(run, "sets", "*", "x")):
    for f in os.listdir(xd):
        if f.endswith(".end"):
            ex[json.load(open(os.path.join(xd, f)))["outcome"]] += 1
out["execution outcomes"] = dict(ex)
out["inject log"] = open(os.path.join(run, "inject.log")).read().splitlines()
print(json.dumps(out, indent=1))
