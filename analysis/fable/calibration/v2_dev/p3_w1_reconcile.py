"""W1 across rounds (design section 9c; no fits): strict reconciliation of each round's collection and libraries, and the
partition of the W1 inventory into round-1 terminal libraries, round-2 terminal libraries and what remains.
  p3_w1_reconcile.py SETTINGS_R1 SETTINGS_R2 METRIC COLLECT_R1 ARCHIVE_R1 COLLECT_R2 ARCHIVE_R2 OUT_JSON
For each round: the summary's binding is its round's (settings, metric, runner); rows are exactly that round's W1
settings with unchanged identities and known statuses, consistent counts, no errors except rows marked invalid, and a
library exactly when COMPLETE. Every library in the archive matches its digest, has K records, is strictly ordered by
(batch, proposal_in_batch), and its K-th record's batch is the row's kth_hit. Across rounds: round-2 rows are exactly
round 1's incomplete and invalid settings; terminal settings of the two rounds are disjoint; together with round 2's
remaining settings they partition the W1 inventory. Exit 1 on any failure."""
import collections, hashlib, json, sys, tarfile

K = 2000
KNOWN = ("COMPLETE", "CAPPED", "FAILED", "incomplete", "invalid")


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def round_check(name, settings_path, metric_path, collect_path, archive_path, fails):
    b = json.load(open(settings_path)); c = json.load(open(collect_path)); m = json.load(open(metric_path))
    want = {"settings_sha256": sha(settings_path), "metric_sha256": b["metric_sha256"], "runner_sha256": b["runner_sha256"]}
    if c.get("binding") != want or b["metric_sha256"] != sha(metric_path):
        fails.append(f"{name}: binding differs from its settings, metric or runner")
    w1 = {s["dir"]: s for s in b["settings"] if s["wave"] == "W1"}
    rows = c["rows"]; dirs = [r["dir"] for r in rows]
    if len(dirs) != len(set(dirs)) or set(dirs) != set(w1):
        fails.append(f"{name}: rows are not exactly the round's W1 settings")
    n = collections.Counter(r["status"] for r in rows)
    if c["status"] != {k: n.get(k, 0) for k in KNOWN[:4]} or sorted(c["incomplete"]) != sorted(r["dir"] for r in rows if r["status"] == "incomplete"):
        fails.append(f"{name}: status counts or incomplete list inconsistent")
    inv = sorted(r["dir"] for r in rows if r["status"] == "invalid")
    if sorted(e.split(":", 1)[0] for e in c["errors"]) != inv or c["n_errors"] != len(c["errors"]):
        fails.append(f"{name}: errors not one-to-one with invalid rows")
    libs = {}
    with tarfile.open(archive_path, "r:gz") as tf:
        for mem in tf:
            if mem.name.startswith("lib/") and mem.name.endswith(".jsonl"):
                libs[mem.name[4:-6]] = tf.extractfile(mem).read()
    for r in rows:
        st = w1.get(r["dir"])
        if st is None:
            continue
        if any(r.get(k) != st[k] for k in ("index", "pop", "outer", "n", "library")) or r["status"] not in KNOWN:
            fails.append(f"{name} {r['dir']}: identity or status"); continue
        if (r["status"] == "COMPLETE") != bool(r.get("library_sha256")) or (r["status"] == "COMPLETE") != (r["dir"] in libs):
            fails.append(f"{name} {r['dir']}: library presence inconsistent with status"); continue
        if r["status"] != "COMPLETE":
            continue
        data = libs[r["dir"]]
        if hashlib.sha256(data).hexdigest() != r["library_sha256"]:
            fails.append(f"{name} {r['dir']}: library digest"); continue
        recs = [json.loads(x) for x in data.splitlines()]
        keys = [(h["batch"], h["proposal_in_batch"]) for h in recs]
        L = len(m["outers"][f"{st['pop']}|{st['outer']}"]["recorded"])
        if len(recs) != K or keys != sorted(set(keys)) or recs[-1]["batch"] != r["kth_hit"] \
                or any(len(h["recorded"]) != L for h in recs):
            fails.append(f"{name} {r['dir']}: library records (count, order, K-th batch or path length)")
    if set(libs) - {r["dir"] for r in rows if r["status"] == "COMPLETE"}:
        fails.append(f"{name}: archive holds libraries without a COMPLETE row")
    return b, c, {k: n.get(k, 0) for k in KNOWN}, len(libs)


def main(s1, s2, metric, c1, a1, c2, a2, out):
    fails = []
    b1, r1, n1, l1 = round_check("round 1", s1, metric, c1, a1, fails)
    b2, r2, n2, l2 = round_check("round 2", s2, metric, c2, a2, fails)
    inv = {s["dir"] for s in b1["settings"] if s["wave"] == "W1"}
    st1 = {r["dir"]: r["status"] for r in r1["rows"]}; st2 = {r["dir"]: r["status"] for r in r2["rows"]}
    redo = {d for d, s in st1.items() if s in ("incomplete", "invalid")}
    if set(st2) != redo:
        fails.append("round 2 rows are not exactly round 1's incomplete and invalid settings")
    t1 = {d for d, s in st1.items() if s in ("COMPLETE", "CAPPED", "FAILED")}
    t2 = {d for d, s in st2.items() if s in ("COMPLETE", "CAPPED", "FAILED")}
    left = {d for d, s in st2.items() if s in ("incomplete", "invalid")}
    if t1 & t2 or t1 | t2 | left != inv or (t1 | t2) & left:
        fails.append("rounds do not partition the W1 inventory")
    rest = {s["dir"]: s for s in b1["settings"] if s["dir"] in left}
    res = {"scope": __doc__, "ok": not fails, "failures": fails[:200],
           "round_1": {"status": n1, "libraries": l1, "binding": r1["binding"]},
           "round_2": {"status": n2, "libraries": l2, "binding": r2["binding"]},
           "w1": {"inventory": len(inv), "terminal_round_1": len(t1), "terminal_round_2": len(t2), "remaining": len(left),
                  "remaining_by_n": dict(collections.Counter(rest[d]["n"] for d in left))}}
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "scope"}, indent=1)[:3000])
    sys.exit(0 if res["ok"] else 1)


if __name__ == "__main__":
    main(*sys.argv[1:])
