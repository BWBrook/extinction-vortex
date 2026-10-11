"""Run the validation chunks assigned to one slot (protocol §4.3; freeze package §6), bound to
one frozen manifest.

All manifest paths are relative to BASE, the host's run directory (deep-server or kunanyi),
so the manifest and its digest are host-independent. Before any chunk runs, BASE must hold
the preflight receipt for this manifest digest (preflight.py: source, bank-shard and stress
hashes verified on this host). Every chunk directory records the manifest digest and its
settings; a complete chunk is skipped only if both match and its T files exist, and any
other existing chunk state stops the slot for a manual decision.

Chunks are taken from the manifest in order; slot SLOT of NSLOTS runs those whose position
is congruent to SLOT. Each slot process loads the banks once (about 28 GB).

R worker count is a runtime setting (results do not depend on it), not part of the manifest.

Usage: python validate.py MANIFEST BASE SLOT NSLOTS [R_WORKERS]
"""
import os, sys, json, time, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e2e_benchmark as e2e
from bank import designs


def manifest_digest(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def chunk_list(man):
    return [(s, c) for s in man["scenarios"] for c in s["chunks"]]


def chunk_settings(man, s, c):
    return {"variant": man["variant"], "R_train": man["R"], "R_test": man["R"], "K": man["K"],
            "budget": man["budget"], "bankdir": man["bankdir"], "block": s["block"], "scenario": s["name"],
            "role": s["role"], "beta": s["beta"], "spec": s["spec"], "stress": s["stress"],
            "seed": c["seed"], "trial_ids": c["trial_ids"], "dir": c["dir"]}


def chunk_state(man, digest, s, c, base):
    """'absent' (no directory), 'complete' (bound, all rows and their T files present) or
    'partial' (bound, incomplete). Raises if the chunk is bound to another manifest or other
    settings, or holds rows without metadata."""
    d = os.path.join(base, c["dir"])
    if not os.path.isdir(d):
        return "absent"
    meta_p, rows_p = os.path.join(d, "e2e_meta.json"), os.path.join(d, "e2e_rows.jsonl")
    if not os.path.exists(meta_p):
        if os.listdir(d):
            raise SystemExit(f"{d}: contents without chunk metadata")
        return "absent"
    meta = json.load(open(meta_p))
    if meta.get("manifest_digest") != digest or meta.get("settings") != chunk_settings(man, s, c):
        raise SystemExit(f"{d}: bound to a different manifest or settings")
    ids = set(range(*c["trial_ids"]))
    rows = [json.loads(l) for l in open(rows_p) if l.strip()] if os.path.exists(rows_p) else []
    done = {r["trial_id"]: r for r in rows}
    if set(done) - ids or len(done) != len(rows):
        raise SystemExit(f"{d}: rows outside the chunk or duplicated")
    if set(done) != ids:
        return "partial"
    for tid, r in done.items():
        if r.get("outcome") != "indet_sampling" and not os.path.exists(os.path.join(d, f"T_{tid}.csv")):
            return "partial"
    return "complete"


def require_preflight(base, digest):
    p = os.path.join(base, f"preflight_{digest[:16]}.json")
    if not os.path.exists(p) or json.load(open(p)).get("manifest_digest") != digest:
        raise SystemExit(f"no preflight receipt for manifest {digest[:16]} in {base}; run preflight.py")


def main():
    man_path, base, slot, nslots = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    workers = int(sys.argv[5]) if len(sys.argv) > 5 else 18
    man = json.load(open(man_path))
    digest = manifest_digest(man_path)
    require_preflight(base, digest)
    des = designs()
    stress_p = os.path.join(base, man["stress_sets"])
    if hashlib.sha256(open(stress_p, "rb").read()).hexdigest() != man["stress_sets_sha256"]:
        raise SystemExit("stress sets do not match the manifest")
    stress = {tid: {n: v["theta"] for n, v in pops.items()}
              for tid, pops in json.load(open(stress_p))["sets"].items()}
    mine = [x for i, x in enumerate(chunk_list(man)) if i % nslots == slot]
    t0 = time.time()
    banks = e2e.knn_banks(os.path.join(base, man["bankdir"]), man["variant"], des, man["K"])
    print(json.dumps({"slot": slot, "chunks": len(mine), "manifest_digest": digest,
                      "t_load_banks": round(time.time() - t0, 1)}), flush=True)
    for s, c in mine:
        state = chunk_state(man, digest, s, c, base)
        if state == "complete":
            continue
        if state == "partial":
            raise SystemExit(f"partial chunk {c['dir']}; decide before rerunning")
        d = os.path.join(base, c["dir"])
        os.makedirs(d, exist_ok=True)
        json.dump({"manifest_digest": digest, "settings": chunk_settings(man, s, c),
                   "R_train": man["R"], "r_workers": workers},
                  open(os.path.join(d, "e2e_meta.json"), "w"), indent=1)
        e2e.run_chunk(banks, des, man["variant"], d, list(range(*c["trial_ids"])), man["R"], man["K"],
                      workers, c["seed"], s["beta"], s["spec"], stress if s["stress"] else None,
                      man["budget"])


if __name__ == "__main__":
    main()
