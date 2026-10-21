"""Recheck saved smoke D fault receipts and replay the final sparse comparator; no new population simulation."""
from pathlib import Path
import collections,json,re,subprocess
B=Path('/data/fable/vortex/r2dev5')
R=B/'s1b/smoke_r2'
OUT=Path('/data/codex/artifacts/project/s1b_r2_closure_20261021')
certs=[]
for p in sorted((R/'workers/dead').iterdir()):
    if p.name.startswith('.'): continue
    c=json.loads(p.read_text())
    assert c['owner']==p.name and isinstance(c['pid'],int) and c['pid']>0
    assert isinstance(c['rc'],int) and isinstance(c['host'],str) and c['host']
    certs.append(c)
assert len(certs)==26
nonces={c['owner'].rsplit('n',1)[1] for c in certs if c['owner'].startswith(('smk[','smk2['))}
assert len(nonces)==3
log=(R/'inject.log').read_text()
assert len(re.findall(r'killed \d+',log))==5
assert log.count(' rc 0')==3 and 'DONE' in log
assert (R/'sets/s00073/lock.broken.ghost').is_dir()
dirs=OUT/'smoke_comparison_dirs.txt'
dirs.write_text('s00073\ns00142\ns00247\ns00772\ns01080\nc00021\n')
a=Path('/data/fable/vortex/v2_dev/p3/smoke_deep3')
tool=B/'src/analysis/fable/calibration/v2_dev/p3_r2_determinism.py'
p=subprocess.run(['/usr/bin/python3','-B','-I',str(tool),str(a),str(R),str(dirs),str(OUT/'determinism_replay.json')],capture_output=True,text=True,timeout=60)
(OUT/'determinism_replay.log').write_text(p.stdout+p.stderr)
assert p.returncode==0,p.stderr
actual=json.loads((OUT/'determinism_replay.json').read_text())
assert actual==json.loads((R/'determinism_vs_deep3.json').read_text())
result={'certificates':len(certs),'worker_invocation_nonces':len(nonces),'certificate_rc_counts':dict(collections.Counter(c['rc'] for c in certs)),'injected_kills':5,'successful_node_wrappers':3,'ghost_lock_reclaimed':True,'determinism_replay_matches_saved':True,'determinism_totals':actual['total'],'scope':'Saved smoke D evidence; no new simulation or live NFS fault reproduction.'}
(OUT/'smoke_receipts.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
