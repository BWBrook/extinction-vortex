"""Bounded P1 audit: no bank scan, fitted test, outer draw, or throughput pilot.
Run from frozen source root on deep-server with numerical threads fixed to one.
"""
import copy, hashlib, importlib.util, json, math, os, platform, sys, time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import scipy
from scipy.integrate import quad
from scipy.special import expit
from scipy.stats import binom, poisson

P1 = Path('/data/fable/vortex/v2_dev/p1')
S0 = Path('/data/fable/vortex/v2_dev/s0')
SRC = Path('/data/fable/vortex/kunanyi_stage/run1/src')
BASE = Path('/data/fable/vortex/kunanyi_run1/extract')
MP = SRC.parent/'validation_manifest.json'
HELPER = P1.parent/'p1_sampler.py'
os.chdir(SRC)
spec=importlib.util.spec_from_file_location('p1', HELPER)
p=importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
sha=lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
b=json.loads((P1/'p1_bound.json').read_text()); m=json.loads(MP.read_text())
pilot=json.loads((P1/'p1_pilot.json').read_text()); scan=json.loads((P1/'p1_scan.json').read_text())
t0=time.monotonic(); result={'scope':__doc__, 'timestamp':datetime.now(ZoneInfo('Australia/Hobart')).isoformat(), 'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__}}
p.check_binding(str(MP),b)
result['sha256']={str(path):sha(path) for path in [HELPER,MP,*P1.glob('*.json')]}
source_hashes={rel:sha(SRC/rel) for rel in m['source_sha256']}
assert source_hashes == m['source_sha256']
result['source_files_verified']=source_hashes
meta=BASE/m['bankdir']/'bank_meta.json'
result['bank_meta_sha256']=sha(meta)
assert sha(meta)==m['bank_sha256']['bank_meta.json']
meta_obj=json.loads(meta.read_text())
assert meta_obj['shards']*meta_obj['shard_draws']==b['bank_draws_per_population']
result['bank_scope']='Metadata hash and raw-attempt denominator verified; no bank shard rehash or array read.'
assert sha(S0/'s0_inputs.json')==b['s0_inputs_sha256']
s0=json.loads((S0/'s0_inputs.json').read_text())
radii={}
for pop in ('wild_dog','hawaiian_crow'):
 path=S0/'full'/f's0_{pop}.json'
 assert sha(path)==b['s0_output_sha256'][pop]
 radii[pop]={r['outer']:r['kth'] for r in json.loads(path.read_text())['rows']}
for st in b['settings']:
 assert st['radius']==radii[st['pop']][st['outer']]
 assert st['outer_recorded']==s0['outers'][st['outer']]['pops'][st['pop']]['recorded']
 if st['kind']=='n0':
  assert st['E']=={'n':0,'k':0,'r':0}
 else:
  scenario,trial=st['outer'].split('/')
  cell=4*st['n_index']+{'null_prior_predictive':0,'null_low_s':1}[scenario]
  e=s0['E'][f"{cell}/{trial}/{st['pop']}"]
  expect={'n':e['n'],'k':e['k'],'r':e['r']} if st['kind']=='noisy' else {'n':e['n'],'k':e['n']*e['sbar_true'],'r':e['n']*e['fbar_true']}
  assert st['E']==expect and set(st['E'])=={'n','k','r'}
result['stage0_settings_exact_matches']=len(b['settings'])
assert pilot['bound_sha256']==sha(P1/'p1_bound.json')
assert b['caps']=={'proposals':p.CAP_PROPOSALS,'paths':p.CAP_PATHS,'batch_proposals':p.BATCH}

# Independent full-PMF ratios cover endpoints, zero counts and ordinary cases.
cases=0; maxerr=0.; maxfactor=-math.inf
for n in (1,30,300):
 for k in sorted({0,n//2,n}):
  for r in (0,1,3,2*n):
   for u in (0.,.0001,.2,.5,.9,.9999,1.):
    for v in (0.,.0001,.01,.1,1.,2.):
     hb,hp=p.log_factors(np.array([u]),np.array([v]),n,k,r)
     got=float(hb[0]+hp[0]); expected=float(binom.logpmf(k,n,u)+poisson.logpmf(r,n*v)-binom.logpmf(k,n,k/n)-poisson.logpmf(r,r))
     maxfactor=max(maxfactor,float(hb[0]),float(hp[0])); assert maxfactor<=1e-9
     if math.isfinite(got):
      maxerr=max(maxerr,abs(got-expected)); assert abs(got-expected)<2e-10
     else: assert np.isneginf(expected)
     cases+=1
ideal=0
for n in (30,300):
 for u0,v0 in ((0.,0.),(.17,.035),(.48,.32),(1.,2.)):
  hb,hp=p.log_factors(np.array([u0]),np.array([v0]),n,n*u0,n*v0)
  assert abs(hb[0])+abs(hp[0])<1e-10
  for u in (0.,.1,.3,.7,1.):
   for v in (0.,.01,.3,1.,2.):
    hb,hp=p.log_factors(np.array([u]),np.array([v]),n,n*u0,n*v0)
    assert hb[0]<=1e-9 and hp[0]<=1e-9
    ideal+=1
result['log_factors']={'noisy_cases':cases,'ideal_cases':ideal,'max_full_pmf_error':maxerr,'max_log_factor':maxfactor}

# Numerical survival functional against adaptive quadrature, independent of GH40.
qerr=0.
for s in (.0001,.01,.2,.5,.99,.9999):
 for sig in (.02,.5,1.):
  theta={k:np.array([v]) for k,v in {'s':s,'f':.32,'sigma':sig,'rho':.8,'p_c':.05,'delta':.95}.items()}
  u,v=p.rate_functionals(theta)
  logit=math.log(s/(1-s)); integ=quad(lambda z:expit(logit+sig*z)*math.exp(-z*z/2)/math.sqrt(2*math.pi),-12,12,epsabs=2e-13)[0]
  expected=(1-.05*.95)*integ
  qerr=max(qerr,abs(u[0]-expected)); assert abs(u[0]-expected)<1e-10
  assert v[0]==.32*(1-.05*.95)
result['rate_quadrature']={'cases':18,'max_abs_error':qerr}

# First bound batch per setting, theta/evidence only; saved samples must match exactly.
# This is 20 x 50k parameter proposals, not population trajectories or a pilot.
replayed=[]
for st in b['settings']:
 rng=np.random.default_rng([20261015,st['index'],0])
 th=p.bank.draw_params(m['variant'],p.BATCH,rng)
 up,ub=np.log(rng.random(p.BATCH)),np.log(rng.random(p.BATCH))
 u,v=p.rate_functionals(th); e=st['E']
 hb,hp=p.log_factors(u,v,e['n'],e['k'],e['r'])
 ids=np.flatnonzero((up<hp)&(ub<hb))[:50]
 sample=[{key:float(th[key][j]) for key in ('s','f','sigma','rho','p_c','delta')} for j in ids]
 assert sample==pilot['settings'][str(st['index'])]['sample_theta']
 replayed.append(len(sample))
result['saved_theta_replay']={'settings':20,'samples_matching':sum(replayed),'parameter_proposals':20*p.BATCH,'new_population_paths':0}

# Heterogeneous frozen-prior wrapper equivalence, including returned parameters/flags.
wrapper=[]
for pop in ('wild_dog','hawaiian_crow'):
 for seed in (13,257,999,20261015):
  n=500
  a=p.bank.simulate_chunk(p.designs()[pop],m['variant'],n,np.random.default_rng(seed))
  rng=np.random.default_rng(seed); th=p.bank.draw_params(m['variant'],n,rng)
  z=p.simulate_given(p.designs()[pop],m['variant'],{k:v for k,v in th.items() if k!='nu'},rng)
  assert np.array_equal(a[0],z[0]) and np.array_equal(a[2],z[2]) and np.array_equal(a[3],z[3])
  assert all(np.array_equal(a[1][k],z[1][k]) for k in a[1])
  wrapper.append({'population':pop,'seed':seed,'paths_each':n,'exact':True})
result['heterogeneous_wrapper']=wrapper

# Strict boundary / adjacent float examples and zero-radius declared equality.
cb=p.ball(np.array([[3.,4.],[3.,4.000001]]),np.array([0.,0.]),np.array([True,True]),np.array([1.,1.]),5.)
assert cb['in'].tolist()==[True,False] and cb['boundary'].tolist()==[True,False]
assert cb['in_lo'].tolist()==[False,False] and cb['in_hi'].tolist()==[True,False]
zcb=p.ball(np.array([[0.],[1e-200],[1.]]),np.array([0.]),np.array([True]),np.array([1.]),0.)
result['zero_radius_counterexample']={'features':[0.,1e-200,1.],'expected_exact_feature_match':[True,False,False],'observed':zcb['in'].tolist(),'present_bound_radii_all_positive':all(s['radius']>0 for s in b['settings'])}
# n0 guard is required by proposal; current inputs valid, but function itself accepts bad counts.
hb,hp=p.log_factors(np.array([.5]),np.array([.3]),0,1,1)
result['invalid_n0_evidence']={'n':0,'k':1,'r':1,'observed_log_factors':[float(hb[0]),float(hp[0])],'rejected':False}

# Completed cap/count accounting and stored path selection (no fresh trajectories).
total={k:0 for k in ('proposals','paths','selected_SA','overflow','ball_hits','ball_boundary')}
for st in b['settings']:
 s=pilot['settings'][str(st['index'])]
 assert s['proposals']<=p.CAP_PROPOSALS and s['paths']<=p.CAP_PATHS
 assert s['paths']==s['theta_accept']<=s['poisson_accept']<=s['proposals']
 assert s['ball_hits']<=s['selected_SA']<=s['paths']
 assert s['ball_hits_lower_adjacent']<=s['ball_hits']<=s['ball_hits_upper_adjacent']
 assert s['ball_boundary']==s['ball_hits']-s['ball_hits_lower_adjacent']
 assert not s['bound_violation'] and s['rounding_excess']==0
 expected='path cap' if st['kind']=='n0' else 'proposal cap'
 assert s['stopped']==expected
 assert s['proposals']==(p.CAP_PATHS if st['kind']=='n0' else p.CAP_PROPOSALS)
 assert len(s['sample_paths'])==s['ball_hits']
 if s['sample_paths']:
  x=np.array(s['sample_paths']); assert (x[:,1:-1]>1).all() and (x[:,-1]<=1).all()
 for k in total: total[k]+=s[k]
result['completed_accounting']={**total,'settings':20,'theta_accept_equals_paths_all':True,'stored_paths_satisfy_selection':True}
result['forecast_at_actual_denominators']=sum(scan['settings'][key]['forecast_retained_per_prior_proposal']*s['proposals'] for key,s in pilot['settings'].items())
result['elapsed_seconds']=round(time.monotonic()-t0,3)
Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('sha256','source_files_verified')},indent=2))
