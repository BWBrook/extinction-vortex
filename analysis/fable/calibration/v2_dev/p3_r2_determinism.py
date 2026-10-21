"""Round-to-round determinism (design section 9c; no fits): a setting re-run in a later round from batch 0 must
reproduce every hit record that an earlier round committed for the same batches, since streams are fixed per
(stream tag, index, batch). Compares committed journal lines batch by batch, for each setting present in both runs.
  p3_r2_determinism.py RUN_EARLIER RUN_LATER DIRS_FILE OUT_JSON
Each run's committed records are its shard journals' committed prefixes (checkpoint journal_bytes), any status; the
pilot prefix is shared input and is not compared. Reports byte-identical lines, records equal in identity
(batch, proposal_in_batch) but not bytes, and identities present in one run only, over the batches both committed."""
import json, os, sys


def committed(sdir):
    """{batch: [line bytes]} and the set of committed batches, over every shard of one setting directory."""
    recs, batches = {}, set()
    for f in sorted(os.listdir(sdir)):
        if not (f.startswith("sh") and f.endswith(".json")):
            continue
        S = json.load(open(os.path.join(sdir, f))); a = S.get("first_batch", int(f[2:11]))
        batches.update(range(a, a + S["batches_done"]))
        data = open(os.path.join(sdir, f[:-5] + "_hits.jsonl"), "rb").read()[:S["journal_bytes"]] if S["journal_bytes"] else b""
        for ln in data.splitlines(True):
            recs.setdefault(json.loads(ln)["batch"], []).append(ln)
    return recs, batches


def main(run_a, run_b, dirs_file, out):
    res, tot = {}, {"settings": 0, "batches_compared": 0, "identical_lines": 0, "identity_only_equal": 0, "unmatched": 0}
    for d in [x.strip() for x in open(dirs_file) if x.strip()]:
        pa, pb = os.path.join(run_a, "sets", d), os.path.join(run_b, "sets", d)
        if not (os.path.isdir(pa) and os.path.isdir(pb)):
            continue
        (ra, ba), (rb, bb) = committed(pa), committed(pb)
        both = ba & bb; same = ident = unmatched = 0
        for k in both:
            la, lb = ra.get(k, []), rb.get(k, [])
            ia = {(json.loads(x)["batch"], json.loads(x)["proposal_in_batch"]): x for x in la}
            ib = {(json.loads(x)["batch"], json.loads(x)["proposal_in_batch"]): x for x in lb}
            for key in ia.keys() | ib.keys():
                if key in ia and key in ib:
                    same += ia[key] == ib[key]; ident += ia[key] != ib[key]
                else:
                    unmatched += 1
        res[d] = {"batches_compared": len(both), "identical_lines": same, "identity_only_equal": ident, "unmatched": unmatched}
        tot["settings"] += 1
        for k in ("batches_compared", "identical_lines", "identity_only_equal", "unmatched"):
            tot[k] += res[d][k]
    json.dump({"scope": __doc__, "runs": [run_a, run_b], "total": tot, "settings": res}, open(out, "w"), indent=1)
    print(json.dumps(tot))


if __name__ == "__main__":
    main(*sys.argv[1:])
