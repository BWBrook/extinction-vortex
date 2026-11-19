"""Regenerate selected post-pilot batches for every COMPLETE setting with a dead execution."""

from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import sys
import tarfile

from audit_archive import DIGESTS


def digest(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def replay(root):
    p3 = root / "v2_dev/p3"
    stage = root / "r3d_rehearse_pos"
    src = stage / "src"
    sp = stage / "s1b/p3_settings_r3.json"
    mp = p3 / "p3_metric.json"
    archive = p3 / "w2_r3a/W2.tar.gz"
    summary = p3 / "w2_r3a/collect_W2.json"
    assert all(digest(path) == DIGESTS[name] for name, path in
               [("settings", sp), ("metric", mp), ("summary", summary), ("archive", archive)])
    b = json.loads(sp.read_bytes())
    metric = json.loads(mp.read_bytes())
    cal = src / "analysis/fable/calibration"
    p2_source = cal / "v2_dev/p2_stage1a.py"
    assert digest(p2_source) == b["p2_sha256"] and digest(cal / "v2_dev/p1_sampler.py") == b["p1_sampler_sha256"]
    assert all(digest(src / path) == sha for path, sha in b["imported_source_sha256"].items())
    os.chdir(src)
    sys.path[:0] = [str(p2_source.parent), str(cal)]
    import p2_stage1a as sampler
    assert sampler.runtime() in b["allowed_runtimes"]
    designs = sampler.designs()
    rows = json.loads(summary.read_bytes())["rows"]
    affected = {r["dir"]: r for r in rows if r["status"] == "COMPLETE" and r["dead_executions"]}
    settings = {s["dir"]: s for s in b["settings"]}
    seen, failures, totals = set(), [], Counter()
    batch_keys = []
    with tarfile.open(archive, "r|gz") as tf:
        for member in tf:
            d = Path(member.name).stem
            if d not in affected:
                continue
            assert member.name == f"lib/{d}.jsonl" and d not in seen
            seen.add(d)
            st = settings[d]
            raw = tf.extractfile(member).read()
            assert hashlib.sha256(raw).hexdigest() == affected[d]["library_sha256"]
            start = st["pilot"]["batches_done"] if st["pilot"] else 0
            lines = raw.splitlines(keepends=True)
            records = [json.loads(line) for line in lines]
            hit_batches = sorted({r["batch"] for r in records if r["batch"] >= start})
            last = hit_batches[-1]
            pos = records[-1]["proposal_in_batch"]
            uniform = start + int.from_bytes(hashlib.sha256(d.encode()).digest(), "big") % (last - start + 1)
            selected = sorted({hit_batches[0], hit_batches[len(hit_batches) // 2], last, uniform})
            outer = metric["outers"][f"{st['pop']}|{st['outer']}"]
            m = dict(outer, **metric["pops"][st["pop"]])
            for bi in selected:
                expected = [line for line, r in zip(lines, records) if r["batch"] == bi]
                got = sampler.one_batch(st, m, bi, b["batch"], designs)["hit_records"]
                if bi == last:
                    got = [r for r in got if r["proposal_in_batch"] <= pos]
                encoded = [(json.dumps(r) + "\n").encode() for r in got]
                totals.update(batches=1, nonempty_batches=int(bool(expected)), archive_records=len(expected))
                batch_keys.append(f"{d}:{bi}")
                if encoded != expected:
                    ids = lambda recs: [r["proposal_in_batch"] for r in recs]
                    failures.append({"setting": d, "batch": bi, "archive_ids": ids(map(json.loads, expected)),
                                     "regenerated_ids": ids(got)})
    assert seen == affected.keys() and len(seen) == 64
    return {"runtime": sampler.runtime(), "settings": len(seen), "proposals_per_batch": b["batch"],
            "sampler_sha256": b["p2_sha256"], **totals,
            "selected_setting_batch_keys_sha256": hashlib.sha256("\n".join(sorted(batch_keys)).encode()).hexdigest(),
            "batches_differing_in_identities_or_bytes": len(failures), "mismatches": failures}


if __name__ == "__main__":
    if not __debug__:
        sys.exit("Run with Python assertions enabled.")
    result = replay(Path(sys.argv[1]).resolve())
    print(json.dumps(result, indent=2))
    sys.exit(int(bool(result["mismatches"])))
