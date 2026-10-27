#!/usr/bin/env python3
"""Bounded shell checks for round-3 stage identity and capacity accounting."""
import hashlib, json, os, pathlib, shutil, subprocess, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
R3 = ROOT / "analysis/fable/calibration/kunanyi/s1b_round3_dispatch.sh"
TOP = ROOT / "analysis/fable/calibration/kunanyi/s1b_topup_dispatch.sh"
FILES = ["v2_dev/p1_sampler.py", "v2_dev/p2_stage1a.py", "v2_dev/p3_stage1b.py",
         "v2_dev/p3_r2_determinism.py", "kunanyi/s1b_node.pbs", "kunanyi/s1b_collect.pbs",
         "kunanyi/s1b_submit.sh", "kunanyi/s1b_round3_dispatch.sh", "kunanyi/s1b_topup_dispatch.sh"]
PY = r'''#!/bin/sh
if [ "$1" = -I ] && [ "$2" = - ]; then
  printf 'W1 %s\nW2 %s\n' "${FIX_W1_M:-1}" "${FIX_W2_M:-1}" > "$5"
  : > "$4"; exit 0
fi
if [ "$3" = select ]; then printf '{"stage":"fixture"}\n' > "$5"; exit 0; fi
exit 90
'''
SUBMIT = r'''#!/bin/bash
set -eu
VB=$1; O=$3; W=$4; N=$5; M=${8:-new}; L=${9:-}; T=$W${L:+_$L}
mkdir -p "$VB/s1b/$O/submit_$T"
printf '%s %s %s\n' "$W" "$N" "$M" >> "$VB/submissions"
printf 'accepted a fixture fixture\n' > "$VB/s1b/$O/submit_$T/submit_journal.tsv"
'''
QSTAT = r'''#!/usr/bin/env python3
import os,sys
a=sys.argv[1:]
if '-u' in a:
 u=a[a.index('-u')+1]
 for i in range(int(os.environ.get('FIX_EXTERNAL8','0'))):
  print(f'e{i} {u} normal x 1 1 8 1gb 1:00 R 0:00')
elif a[-1] == os.environ.get('FIX_REF','ref[]'):
 n=int(os.environ.get('FIX_REF_LIVE','0')); print(f'array_state_count = Queued:{n} Running:0 Held:0 Expired:0')
else: print('job_state = F')
'''

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def setup(base, w1=1, w2=1):
    c = pathlib.Path("src/analysis/fable/calibration")
    stage = base / "stage_round3" / c
    installed = base / c
    for rel in FILES:
        p = stage / rel; p.parent.mkdir(parents=True, exist_ok=True)
        if rel == "kunanyi/s1b_round3_dispatch.sh": p.write_bytes(R3.read_bytes())
        elif rel == "kunanyi/s1b_topup_dispatch.sh": p.write_bytes(TOP.read_bytes())
        elif rel == "kunanyi/s1b_submit.sh": p.write_text(SUBMIT)
        elif rel == "v2_dev/p3_stage1b.py": p.write_text("UNREVIEWED_SELF_CONSISTENT_STAGE = True\n")
        else: p.write_text("fixture\n")
    manifest = base / "stage_round3/s1b/stage_sha256.txt"; manifest.parent.mkdir(parents=True)
    manifest.write_text("".join(f"{sha(stage/rel)}  ./src/analysis/fable/calibration/{rel}\n" for rel in FILES))
    (installed/"v2_dev").mkdir(parents=True); (installed/"kunanyi").mkdir()
    for rel in ("v2_dev/p1_sampler.py", "v2_dev/p2_stage1a.py", "kunanyi/s1b_submit.sh"):
        shutil.copy2(stage/rel, installed/rel)
    (installed/"kunanyi/env.sh").write_text('export PATH="'+str(base/'bin')+':$PATH"\n')
    (base/"s1b/run2").mkdir(parents=True); (base/"s1b/tmp").mkdir()
    (base/"s1b/reservations.tsv").write_text("")
    for p in (base/"s1b/p3_settings_r2.json", base/"s1b/run2/collect_W1_b.json", base/"s1b/run2/collect_W2_b.json"):
        p.write_text("{}\n")
    bindir=base/"bin"; bindir.mkdir(); (bindir/"python").write_text(PY); (bindir/"python").chmod(0o755)
    (bindir/"qstat").write_text(QSTAT); (bindir/"qstat").chmod(0o755)
    env=dict(os.environ, PATH=f"{bindir}:{os.environ['PATH']}", PBS_BIN=str(bindir), PBS_USER="fixture",
             FIX_W1_M=str(w1), FIX_W2_M=str(w2), W1_SUMMARY_SHA="x", W2_SUMMARY_SHA="y",
             CAP_CPUS="7000", MIN_W2_JOBS="1", VB=str(base), VBASE=str(base))
    return env

def run_r3(name, w1, w2, external=0, stale=None):
    td=tempfile.TemporaryDirectory(prefix="r3_dispatch_review_"); base=pathlib.Path(td.name); env=setup(base,w1,w2)
    env["FIX_EXTERNAL8"]=str(external)
    if stale:
        (base/"s1b/run3").mkdir(); (base/f"s1b/run3/r3_{stale[0]}.jobs").write_text(str(stale[1])+"\n")
    p=subprocess.run(["bash",str(R3)],env=env,text=True,capture_output=True)
    subs=(base/"submissions").read_text().splitlines() if (base/"submissions").exists() else []
    marker_path=base/"src/analysis/fable/calibration/v2_dev/p3_stage1b.py"
    marker=marker_path.read_text() if marker_path.exists() else ""
    out={"name":name,"exit":p.returncode,"submissions":subs,"installed_unreviewed_marker":marker.startswith("UNREVIEWED"),
         "stdout":p.stdout,"stderr":p.stderr}
    td.cleanup(); return out

def run_topup():
    td=tempfile.TemporaryDirectory(prefix="r3_topup_review_"); base=pathlib.Path(td.name); env=setup(base)
    (base/"s1b/run3").mkdir(); (base/"s1b/run3/topup_b_W2.jobs").write_text("874\n")
    env.update(FIX_EXTERNAL8="9",FIX_REF="ref[]",FIX_REF_LIVE="9",LABEL="b",WAVES="W2",REF="ref[]",
               SETTINGS="p3_settings_r3.json",OUTDIR="run3")
    p=subprocess.run(["bash",str(TOP)],env=env,text=True,capture_output=True)
    subs=(base/"submissions").read_text().splitlines() if (base/"submissions").exists() else []
    out={"name":"topup_stale_size_after_interruption","exit":p.returncode,"submissions":subs,
         "precondition":"size file exists; matching submit journal does not; live load subsequently rose from 0 to 72 CPUs",
         "actual_requests_if_accepted":72+874*8+1,
         "stdout_tail":p.stdout.splitlines()[-5:],"stderr":p.stderr}; td.cleanup(); return out

cases=[run_r3("w1_accepted_but_not_yet_visible_to_qstat",18,1),
       run_r3("round3_stale_w2_size_after_interruption",0,1,external=9,stale=("W2",874)),run_topup()]
cases[0]["precondition"]="W1 qsub accepted 63 x 8 plus collector; the immediately following user listing omits it"
cases[0]["actual_requests_if_accepted"]=63*8+1+874*8+1
cases[1]["precondition"]="size file exists; matching submit journal does not; live load subsequently rose from 0 to 72 CPUs"
cases[1]["actual_requests_if_accepted"]=72+874*8+1
assert all(c["exit"]==0 for c in cases)
assert cases[0]["submissions"][:2]==["W1 63 new","W2 874 new"]
assert cases[1]["submissions"]==["W2 874 new"] and cases[2]["submissions"]==["W2 874 topup"]
assert all(c["actual_requests_if_accepted"]>7000 for c in cases)
assert cases[0]["installed_unreviewed_marker"]
out={"round3_dispatch_sha256":sha(R3),"topup_dispatch_sha256":sha(TOP),
     "reviewed_stage_tar_sha256":"ddb014b0aad32fce2f4b4ed927c2d38aaf1253e1588235f2f7fd476a7f3ab84a",
     "cap":7000,"cases":cases,
     "interpretation":"Actual scripts accept all three requests above the cap. The stage case separately shows only that the dispatcher relies on the launch procedure for external stage identity."}
path=pathlib.Path(__file__).with_name("review_dispatch_contracts.json"); path.write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))
