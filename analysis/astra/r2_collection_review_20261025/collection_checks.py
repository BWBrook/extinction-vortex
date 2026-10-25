"""Saved-collector arithmetic and small reconciliation-contract fixtures.

No production archive is read. Temporary archives contain two synthetic
2,000-record libraries and exercise the unmodified reconciliation module.
"""
import collections
import contextlib
import copy
from datetime import datetime
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import subprocess
import tarfile
import tempfile
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
V2 = ROOT / "analysis/fable/calibration/v2_dev"
SOURCE = V2 / "p3_w1_reconcile.py"


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text())


def saved_summary_checks():
    paths = [V2/"p3/w1_r1_collect_W1.json", V2/"p3/w1_r2_collect_W1.json"]
    rounds = [read(p) for p in paths]
    by = [{r["dir"]:r for r in c["rows"]} for c in rounds]
    for c,rows in zip(rounds,by):
        assert len(rows) == len(c["rows"])
        counts=collections.Counter(r["status"] for r in rows.values())
        assert c["status"] == {k:counts.get(k,0) for k in ("COMPLETE","CAPPED","FAILED","incomplete")}
        assert set(c["incomplete"]) == {d for d,r in rows.items() if r["status"] == "incomplete"}
        assert sorted(e.split(":",1)[0] for e in c["errors"]) == sorted(d for d,r in rows.items() if r["status"] == "invalid")
        assert c["n_errors"] == len(c["errors"])
        assert c["collection_ok"] == (not c["errors"])
        for key in ("useful_cpu_h","discarded_cpu_h"):
            assert math.isclose(c[key],sum(r.get(key,0) for r in rows.values()),rel_tol=1e-12)
    before,after=by
    redo={d for d,r in before.items() if r["status"] in ("incomplete","invalid")}
    assert set(after) == redo
    ident=("index","pop","outer","n","library")
    assert all(all(before[d][k] == r[k] for k in ident) for d,r in after.items())
    kept={d:r for d,r in before.items() if d not in redo}
    assert not set(kept)&set(after)
    combined=kept|after
    assert set(combined)==set(before) and len(combined)==14544
    counts=collections.Counter(r["status"] for r in combined.values())
    assert counts==dict(COMPLETE=14493,CAPPED=3,incomplete=48)
    assert all(r["n"]==30 and r["library"]=="primary" for r in after.values() if r["status"]=="incomplete")
    availability={}
    for scenario in ("null_prior_predictive","null_low_s","MA_betamin","MA_d10_0.5"):
        availability[scenario]={}
        for n in (0,30):
            outer=collections.defaultdict(list)
            for r in combined.values():
                if r["library"]=="primary" and r["n"]==n and r["outer"].split("/")[0]==scenario:
                    outer[r["outer"]].append(r)
            assert len(outer)==200 and all(len(v)==9 and len({r["pop"] for r in v})==9 for v in outer.values())
            availability[scenario][n]=dict(denominator=200,
                all_nine_complete=sum(all(r["status"]=="COMPLETE" for r in v) for v in outer.values()),
                any_capped=sum(any(r["status"]=="CAPPED" for r in v) for v in outer.values()),
                any_incomplete=sum(any(r["status"]=="incomplete" for r in v) for v in outer.values()))
    cpus={}
    for label,c in zip(("round_1","round_2"),rounds):
        cpus[label]={status:{key:sum(r.get(key,0) for r in c["rows"] if r["status"]==status)
                           for key in ("useful_cpu_h","discarded_cpu_h")}
                     for status in sorted({r["status"] for r in c["rows"]})}
    return dict(inputs_sha256={str(p.relative_to(ROOT)):sha_bytes(p.read_bytes()) for p in paths},
                exact_replay_directory_set=True,collection_row_identities_unchanged=True,
                full_w1_status=dict(counts),w1_by_n_library_status=[dict(n=k[0],library=k[1],status=k[2],count=v)
                  for k,v in sorted(collections.Counter((r["n"],r["library"],r["status"]) for r in combined.values()).items())],
                capped_rows=[r for r in combined.values() if r["status"]=="CAPPED"],
                original_invalid_now=after["s18085"],dataset_availability=availability,
                cpu_by_round_status=cpus,round_2_accounted_cpu_h=rounds[1]["useful_cpu_h"]+rounds[1]["discarded_cpu_h"],
                scope="Collector-row arithmetic only; settings, journals and actual archives are checked separately.")


def fixture_checks():
    spec=importlib.util.spec_from_file_location("reconcile_under_review",SOURCE)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    assert mod.K==2000
    results=[]

    def run(name,change,expected,limitation=None):
        with tempfile.TemporaryDirectory(prefix="r2-reconcile-review-") as tmp:
            p=Path(tmp)
            metric={"outers":{"test|scenario/0":{"recorded":[10,5,0]}}}
            def st(d,i,n):
                return dict(dir=d,index=i,pop="test",outer="scenario/0",n=n,library="primary",
                            wave="W1",stream_tag=2,cap_batches=10000,rate=1.,E={"k":3},pilot=None)
            states=[st("s00000",0,0),st("s00001",1,30),st("s00002",2,30)]
            settings=[dict(settings=copy.deepcopy(states),runner_sha256="a"*64,p1_sampler_sha256="c"*64),
                      dict(settings=copy.deepcopy(states[1:]),runner_sha256="b"*64,p1_sampler_sha256="c"*64)]
            lib=b"".join((json.dumps(dict(batch=i,proposal_in_batch=0,recorded=[10,5,0],theta={"s":.5}))+"\n").encode()
                         for i in range(2000))
            def row(s,status):
                r={k:s[k] for k in ("dir","index","pop","outer","n","library")}
                r.update(status=status,prefix_end_batch=2000 if status=="COMPLETE" else 0,
                         prefix_hits=2000 if status=="COMPLETE" else 0,useful_cpu_h=1.,discarded_cpu_h=0.)
                if status=="COMPLETE":r.update(library_sha256=sha_bytes(lib),kth_hit=1999)
                return r
            collections_=[dict(rows=[row(states[0],"COMPLETE"),row(states[1],"incomplete"),row(states[2],"invalid")]),
                          dict(rows=[row(states[1],"COMPLETE"),row(states[2],"incomplete")])]
            archives=[[('lib/s00000.jsonl',lib)],[('lib/s00001.jsonl',lib)]]
            extra={}
            change(settings,collections_,archives,extra)
            mpath=p/"metric.json";mpath.write_text(json.dumps(metric));mh=sha_bytes(mpath.read_bytes())
            spaths=[];cpaths=[];apaths=[]
            for i,(s,c,members) in enumerate(zip(settings,collections_,archives)):
                s["metric_sha256"]=mh
                sp=p/f"settings{i}.json";sp.write_text(json.dumps(s));spaths.append(sp)
                rows=c["rows"];ns=collections.Counter(r["status"] for r in rows)
                errors=[r["dir"]+": synthetic invalid" for r in rows if r["status"]=="invalid"]
                c.update(binding=dict(settings_sha256=sha_bytes(sp.read_bytes()),metric_sha256=mh,runner_sha256=s["runner_sha256"]),
                         status={k:ns.get(k,0) for k in ("COMPLETE","CAPPED","FAILED","incomplete")},
                         incomplete=[r["dir"] for r in rows if r["status"]=="incomplete"],errors=errors,n_errors=len(errors),
                         collection_ok=not errors,wave="W1",tag="W1")
                if i==1:c.update(extra.get("collection_fields",{}))
                cp=p/f"collect{i}.json";cp.write_text(json.dumps(c));cpaths.append(cp)
                embedded=(b'{"wrong":"summary"}' if i==1 and extra.get("embedded_wrong") else cp.read_bytes())
                ap=p/f"archive{i}.tar.gz";apaths.append(ap)
                with tarfile.open(ap,"w:gz") as tf:
                    for filename,data in [("collect_W1.json",embedded),("collect_W1.log",b"fixture\n")]+members:
                        info=tarfile.TarInfo(filename);info.size=len(data);tf.addfile(info,io.BytesIO(data))
            out=p/"out.json"
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    mod.main(str(spaths[0]),str(spaths[1]),str(mpath),str(cpaths[0]),str(apaths[0]),str(cpaths[1]),str(apaths[1]),str(out))
            except SystemExit as ex:code=ex.code
            else:raise AssertionError("no exit code")
            result=read(out)
            assert code==expected and result["ok"]==(expected==0),(name,code,result)
            results.append(dict(name=name,exit=code,ok=result["ok"],failures=result["failures"],limitation=limitation))

    run("valid_partition",lambda s,c,a,x:None,0)
    def changed_row(s,c,a,x):c[1]["rows"][0]["pop"]="other"
    run("row_identity_mismatch_rejected",changed_row,1)
    def duplicate_row(s,c,a,x):c[1]["rows"].append(copy.deepcopy(c[1]["rows"][0]))
    run("duplicate_collection_row_rejected",duplicate_row,1)
    def missing_library(s,c,a,x):a[1].clear()
    run("missing_complete_library_rejected",missing_library,1)
    def digest_bad(s,c,a,x):a[1][0]=(a[1][0][0],b"altered")
    run("library_digest_mismatch_rejected",digest_bad,1)
    def immutable_change(s,c,a,x):
        s[1]["settings"][0].update(stream_tag=99,cap_batches=1,E={"k":99})
        s[1]["p1_sampler_sha256"]="d"*64
    run("cross_round_sampling_fields_changed",immutable_change,0,
        "Each summary is checked against its own settings; unchanged cross-round sampling fields/helpers are not established.")
    def duplicate_setting(s,c,a,x):s[1]["settings"].append(copy.deepcopy(s[1]["settings"][0]))
    run("duplicate_settings_directory_collapsed",duplicate_setting,0,
        "Settings inventory is made into a dictionary before duplicate detection.")
    def duplicate_member(s,c,a,x):a[1].insert(0,(a[1][0][0],b"wrong earlier duplicate"))
    run("duplicate_archive_member_shadowed",duplicate_member,0,
        "The last same-named library silently overwrites an earlier member.")
    run("embedded_summary_disagrees",lambda s,c,a,x:x.update(embedded_wrong=True),0,
        "The embedded collection summary is ignored; caller must compare it with the external summary.")
    def invalid_path(s,c,a,x):
        recs=[json.loads(line) for line in a[1][0][1].splitlines()]
        for r in recs:r["recorded"]=[1,1,2]
        data=b"".join((json.dumps(r)+"\n").encode() for r in recs)
        a[1][0]=(a[1][0][0],data);c[1]["rows"][0]["library_sha256"]=sha_bytes(data)
    run("selection_invalid_path_accepted",invalid_path,0,
        "Reconciler checks path length, not the collector's full record/selection contract.")
    return results


def main():
    result=dict(timestamp=datetime.now(ZoneInfo("Australia/Hobart")).isoformat(),
                target_head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
                reconciler_sha256=sha_bytes(SOURCE.read_bytes()),saved=saved_summary_checks(),fixtures=fixture_checks())
    (HERE/"collection_checks.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(dict(status=result["saved"]["full_w1_status"],fixtures=len(result["fixtures"]),
                         round_2_cpu_h=result["saved"]["round_2_accounted_cpu_h"],
                         accepted_limits=[r["name"] for r in result["fixtures"] if r["limitation"]]),indent=2))


if __name__=="__main__":
    main()
