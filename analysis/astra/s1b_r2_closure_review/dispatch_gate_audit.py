"""Run the exact revised dispatch summary gate on the saved round-1 inputs, without dispatch."""
from pathlib import Path
import hashlib,json,re,subprocess
P3=Path('/data/fable/vortex/v2_dev/p3')
OUT=Path('/data/codex/artifacts/project/s1b_r2_closure_20261021')
p=P3/'stage_r4/src/analysis/fable/calibration/kunanyi/s1b_round2_dispatch.sh'
digest=hashlib.sha256(p.read_bytes()).hexdigest()
assert digest=='7108d21c9146ca74079bcbf36d1d0baba7c940f181641b0a51320b3c3afac177'
code=p.read_text().split("<<'PY'\n",1)[1].split('\nPY\n',1)[0]
summary=P3/'w1_r1/collect_W1.json'
dirs=OUT/'exact_gate_dirs.txt'
r=subprocess.run(['/usr/bin/python3','-I','-',str(summary),str(P3/'p3_settings.json'),str(dirs),'2aa92fb0bd8c9d8d2235bddb59c1b55be47f404f14d1eaf9ff800d05b7ba28ab'],input=code,capture_output=True,text=True,timeout=30)
(OUT/'dispatch_gate.log').write_text(r.stdout+r.stderr)
assert r.returncode==0,r.stderr
assert dirs.read_bytes()==(OUT/'dirs_r2.txt').read_bytes()
result={'wrapper_sha256':digest,'summary_sha256':hashlib.sha256(summary.read_bytes()).hexdigest(),'exit':r.returncode,'gate_output':r.stdout.strip(),'selected_dirs':len(dirs.read_text().splitlines()),'independent_selection_matches':True,'scope':'Exact embedded Python gate only; no PBS, installed-source mutation, or production ledger write.'}
(OUT/'dispatch_gate_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
