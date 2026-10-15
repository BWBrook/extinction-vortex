"""Synthetic runner guard tests only: bank loading and population simulation replaced by stubs.
No new pilot, bank, outer dataset or fit. Original files are not modified.
"""
import contextlib, copy, importlib.util, io, json, os, sys
from pathlib import Path
from unittest.mock import patch
import numpy as np
SRC=Path('/data/fable/vortex/kunanyi_stage/run1/src'); os.chdir(SRC)
MP=SRC.parent/'validation_manifest.json'; HP=Path('/data/fable/vortex/v2_dev/p1_sampler.py')
spec=importlib.util.spec_from_file_location('p1guard', HP); p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
b=json.loads(HP.with_name('p1').joinpath('p1_bound.json').read_text())
outdir=Path(sys.argv[1]);outdir.mkdir(parents=True,exist_ok=True)
results={'scope':__doc__}
# check_binding never inspects imported dependency bytes: replacing the live function is undetected.
with patch.object(p.bank,'draw_params',lambda *a: (_ for _ in ()).throw(RuntimeError('changed dependency'))):
 p.check_binding(str(MP),b)
results['changed_imported_generator_not_rejected']=True

def fake_draw(variant,n,rng):
 return {k:np.full(n,v) for k,v in {'s':.5,'f':.3,'sigma':.1,'rho':.1,'p_c':0.,'delta':.5,'nu':np.inf}.items()}
def fake_sim(design,variant,theta,rng):
 n=len(theta['s']); return np.tile([4.,3.,0.],(n,1)),theta,np.zeros(n,bool),np.ones(n,bool)
def run(label,e):
 target=copy.deepcopy(b);st=target['settings'][0]
 st.update(E=e,outer_recorded=[4.,3.,0.],radius=1.,kind='synthetic',n=e['n'])
 target['settings']=[st]
 bp=outdir/f'{label}_bound.json'; op=outdir/f'{label}_result.json';bp.write_text(json.dumps(target))
 with patch.object(p,'CAP_PROPOSALS',4),patch.object(p,'CAP_PATHS',3),patch.object(p,'BATCH',4), \
      patch.object(p,'metric',lambda *a:(None,None,np.array([True,True,True]),np.ones(3))), \
      patch.object(p,'designs',lambda:{'wild_dog':{}}),patch.object(p.bank,'draw_params',fake_draw), \
      patch.object(p,'simulate_given',fake_sim),contextlib.redirect_stdout(io.StringIO()):
  p.pilot(str(MP),'unused',str(bp),str(op),1.)
 s=json.loads(op.read_text())['settings']['0']
 return {k:s[k] for k in ('proposals','theta_accept','paths','selected_SA','ball_hits','bound_violation','stopped')}
results['invalid_n0_runner']=run('invalid_n0',{'n':0,'k':1,'r':1})
results['nan_evidence_runner']=run('nan_E',{'n':30,'k':12,'r':float('nan')})
results['path_cap_truncation']=run('path_cap',{'n':0,'k':0,'r':0})
# tiny-boundary logic is tested in remote_checks.py; current radii all >0.
(outdir/'guard_repros.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
