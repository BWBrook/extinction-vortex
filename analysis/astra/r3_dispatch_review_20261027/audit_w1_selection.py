#!/usr/bin/env python3
"""Audit the final W1 summary and its round-3 selection contract."""
import collections, hashlib, json, pathlib, sys

ROOT=pathlib.Path(__file__).resolve().parents[3]
S=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/"analysis/fable/calibration/v2_dev/p3/w1_r2/p3_settings_r2.json"
C=pathlib.Path(sys.argv[2]) if len(sys.argv)>2 else ROOT/"analysis/fable/calibration/v2_dev/p3/w1_r2b_collect_W1_b.json"
RUNNER_SHA="c56d0af653f1d7ecd525cacc5b6a191d8a1cadf398b601fc4327f3f6da34983b"
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads(S.read_bytes()); c=json.loads(C.read_bytes())
inv={s["dir"]:s for s in b["settings"] if s["wave"]=="W1"}; rows=c["rows"]
assert len(inv)==len(rows)==4847 and len({r["dir"] for r in rows})==4847
assert c["binding"]=={"settings_sha256":sha(S),"metric_sha256":b["metric_sha256"],"runner_sha256":b["runner_sha256"]}
for r in rows:
    assert all(r[k]==inv[r["dir"]][k] for k in ("index","pop","outer","n","library"))
n=collections.Counter(r["status"] for r in rows)
assert c["status"]=={k:n.get(k,0) for k in ("COMPLETE","CAPPED","FAILED","incomplete")}
invalid=sorted(r["dir"] for r in rows if r["status"]=="invalid")
assert sorted(e.split(":",1)[0] for e in c["errors"])==invalid
redo=[r["dir"] for r in rows if r["status"] in ("incomplete","invalid","FAILED")]
selected=[s for s in b["settings"] if s["dir"] in set(redo)]
assert len(redo)==len(set(redo))==len(selected)==18 and all(s==inv[s["dir"]] for s in selected)
out={"settings_sha256":sha(S),"summary_sha256":sha(C),"runner_r2_sha256":b["runner_sha256"],
     "runner_r3_sha256":RUNNER_SHA,"status":dict(n),"selected_count":len(selected),
     "selected_dirs":redo,"failed_included":sum(r["status"]=="FAILED" for r in rows),
     "summary_identity_fields_match_settings":True,
     "selection_rule":"incomplete, invalid, or FAILED; COMPLETE and CAPPED excluded"}
path=pathlib.Path(__file__).with_name("audit_w1_selection.json");path.write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))
