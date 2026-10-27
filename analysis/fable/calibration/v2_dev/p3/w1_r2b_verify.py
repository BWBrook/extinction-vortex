import hashlib, json, sys, tarfile
d = sys.argv[1]; c = json.load(open(f"{d}/collect_W1_b.json"))
want = {f"lib/{r['dir']}.jsonl": r["library_sha256"] for r in c["rows"] if r.get("library_sha256")}
seen, bad, names, emb = {}, [], [], None
with tarfile.open(f"{d}/W1_b.tar.gz") as tf:
    for m in tf:
        names.append(m.name)
        if not m.isfile():
            continue
        b = tf.extractfile(m).read(); n = m.name[2:] if m.name.startswith("./") else m.name
        if n in want:
            if hashlib.sha256(b).hexdigest() != want[n] or b.count(b"\n") != 2000:
                bad.append(n)
            seen[n] = 1
        elif n == "collect_W1_b.json":
            emb = hashlib.sha256(b).hexdigest() == hashlib.sha256(open(f"{d}/collect_W1_b.json", "rb").read()).hexdigest()
print(json.dumps({"members": len(names), "unique": len(set(names)), "libraries": len(seen), "expected": len(want), "bad": bad[:5],
                  "embedded_summary_identical": emb, "status": c["status"], "errors": c["errors"],
                  "binding": {k: v[:8] for k, v in c["binding"].items()}}))
