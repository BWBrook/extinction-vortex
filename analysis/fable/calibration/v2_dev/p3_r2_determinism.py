"""Round-to-round determinism (design section 9c; no fits): a setting re-run in a later round from batch 0 must
reproduce every hit record that an earlier round committed for the same batches, since streams are fixed per
(stream tag, index, batch). For each listed setting, both runs' shard journals are verified against their checkpoints
(committed prefix length and SHA-256, every record inside its shard's committed batches); committed batch coverage is
kept as intervals, and the hit records of each run that fall inside the other run's coverage are compared by identity
(batch, proposal_in_batch) and then by bytes. The pilot prefix is shared input and is not compared.
  p3_r2_determinism.py RUN_EARLIER RUN_LATER DIRS_FILE OUT_JSON
Every listed setting must exist in both runs, once; a hit identity may not repeat within a shard, nor carry two
different records within a run. Exit 0: all compared records identical and coverage positive; 1: an
identity present in one run only, a missing setting, an unverifiable journal or no coverage; 2: identities all
match but some records differ in bytes (for example a last-place floating-point difference between hosts)."""
import bisect, hashlib, json, os, sys


def shards(sdir):
    """[(lo, hi, {(batch, proposal_in_batch): line})] for every shard checkpoint of one setting, journals verified."""
    out = []
    for f in sorted(os.listdir(sdir)):
        if not (f.startswith("sh") and f.endswith(".json")):
            continue
        S = json.load(open(os.path.join(sdir, f))); a = S.get("first_batch", int(f[2:11])); hi = a + S["batches_done"]
        data = open(os.path.join(sdir, f[:-5] + "_hits.jsonl"), "rb").read()[:S["journal_bytes"]] if S["journal_bytes"] else b""
        if len(data) != S["journal_bytes"] or hashlib.sha256(data).hexdigest() != S["journal_sha256"]:
            raise ValueError(f"{sdir}/{f}: journal does not match its checkpoint")
        recs = {}
        for ln in data.splitlines(True):
            h = json.loads(ln)
            if not a <= h["batch"] < hi:
                raise ValueError(f"{sdir}/{f}: record outside the shard's committed batches")
            if (h["batch"], h["proposal_in_batch"]) in recs:
                raise ValueError(f"{sdir}/{f}: duplicate hit identity")
            recs[(h["batch"], h["proposal_in_batch"])] = ln
        out.append((a, hi, recs))
    return out


def merged(iv):
    out = []
    for lo, hi in sorted(x for x in iv if x[1] > x[0]):
        if out and lo <= out[-1][1]:
            out[-1][1] = max(out[-1][1], hi)
        else:
            out.append([lo, hi])
    return out


def inside(m, b):
    k = bisect.bisect_right([x[0] for x in m], b) - 1
    return k >= 0 and m[k][0] <= b < m[k][1]


def joined(shs, d):
    """One run's records for a setting: committed shards may overlap (a re-planned range), but an identity may appear
    in two shards only with identical bytes."""
    out = {}
    for _, _, r in shs:
        for k, v in r.items():
            if k in out and out[k] != v:
                raise ValueError(f"{d}: one identity with two different records")
            out[k] = v
    return out


def main(run_a, run_b, dirs_file, out):
    tot = {"settings": 0, "batches_compared": 0, "records_compared": 0, "identical": 0, "bytes_differ": 0, "unmatched": 0}
    res, problems = {}, []
    dirs = [x.strip() for x in open(dirs_file) if x.strip()]
    if len(dirs) != len(set(dirs)):
        problems.append("duplicate settings requested"); dirs = list(dict.fromkeys(dirs))
    for d in dirs:
        pa, pb = os.path.join(run_a, "sets", d), os.path.join(run_b, "sets", d)
        if not (os.path.isdir(pa) and os.path.isdir(pb)):
            problems.append(f"{d}: missing from a run"); continue
        try:
            sa, sb = shards(pa), shards(pb)
        except (OSError, ValueError, KeyError) as ex:
            problems.append(f"{d}: {type(ex).__name__}: {ex}"); continue
        ma, mb = merged([(lo, hi) for lo, hi, _ in sa]), merged([(lo, hi) for lo, hi, _ in sb])
        cover = sum(max(0, min(x[1], y[1]) - max(x[0], y[0])) for x in ma for y in mb)
        try:
            ra, rb = joined(sa, d), joined(sb, d)
        except ValueError as ex:
            problems.append(str(ex)); continue
        keys = {k for k in ra if inside(mb, k[0])} | {k for k in rb if inside(ma, k[0])}
        same = sum(1 for k in keys if k in ra and k in rb and ra[k] == rb[k])
        diff = sum(1 for k in keys if k in ra and k in rb and ra[k] != rb[k])
        res[d] = {"batches_compared": cover, "records_compared": len(keys), "identical": same, "bytes_differ": diff,
                  "unmatched": len(keys) - same - diff}
        tot["settings"] += 1
        for k in res[d]:
            tot[k] += res[d][k]
    code = 1 if problems or tot["unmatched"] or not tot["batches_compared"] else (2 if tot["bytes_differ"] else 0)
    json.dump({"scope": __doc__, "runs": [run_a, run_b], "exit": code, "total": tot, "problems": problems, "settings": res},
              open(out, "w"), indent=1)
    print(json.dumps({"exit": code, **tot, "problems": len(problems)}))
    sys.exit(code)


if __name__ == "__main__":
    main(*sys.argv[1:])
