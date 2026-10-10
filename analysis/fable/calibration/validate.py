"""Run the validation chunks assigned to one slot (protocol §4.3; freeze package §6).

Chunks are taken from the manifest in order; slot SLOT of NSLOTS runs those whose position
is congruent to SLOT. Each slot process loads the banks once (about 28 GB), so at most three
slots run at once on deep-server (run_validation.sh). A chunk whose rows are complete is
skipped; a partial chunk stops the slot for a manual decision rather than being resumed
silently. Each chunk directory gets e2e_meta.json (contract v3) recording its manifest entry.

Usage: python validate.py MANIFEST SLOT NSLOTS
"""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e2e_benchmark as e2e
from bank import designs


def chunk_list(man):
    return [(s, c) for s in man["scenarios"] for c in s["chunks"]]


def main():
    man_path, slot, nslots = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    man = json.load(open(man_path))
    des = designs()
    stress_sets = json.load(open(man["stress_sets"]))["sets"]
    stress = {tid: {n: v["theta"] for n, v in pops.items()} for tid, pops in stress_sets.items()}
    mine = [x for i, x in enumerate(chunk_list(man)) if i % nslots == slot]
    t0 = time.time()
    banks = e2e.knn_banks(man["bankdir"], man["variant"], des, man["K"])
    print(json.dumps({"slot": slot, "chunks": len(mine), "t_load_banks": round(time.time() - t0, 1)}), flush=True)
    for s, c in mine:
        ids = list(range(*c["trial_ids"]))
        rows_path = os.path.join(c["dir"], "e2e_rows.jsonl")
        if os.path.exists(rows_path):
            done = {json.loads(l)["trial_id"] for l in open(rows_path) if l.strip()}
            if done == set(ids):
                continue
            raise SystemExit(f"partial chunk {c['dir']}: {len(done)}/{len(ids)} rows; decide before rerunning")
        os.makedirs(c["dir"], exist_ok=True)
        json.dump({"manifest": man_path, "block": s["block"], "scenario": s["name"], "chunk": c,
                   "beta": s["beta"], "spec": s["spec"], "variant": man["variant"], "R_train": man["R"],
                   "R_test": man["R"], "K": man["K"], "budget": man["budget"], "r_workers": man["workers"]},
                  open(os.path.join(c["dir"], "e2e_meta.json"), "w"), indent=1)
        e2e.run_chunk(banks, des, man["variant"], c["dir"], ids, man["R"], man["K"], man["workers"],
                      c["seed"], s["beta"], s["spec"], stress if s["stress"] else None, man["budget"])


if __name__ == "__main__":
    main()
