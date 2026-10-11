"""Bounded protocol 0.10 stress-sampler audit; no R or remote compute.

Run with a Python environment providing NumPy and SciPy; writes sampler_audit.json.
"""
import json, os, pathlib, sys, subprocess, tempfile
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[3]
os.chdir(ROOT)
CAL=ROOT/'analysis/fable/calibration'
sys.path.insert(0,str(CAL))
import e2e_benchmark as e
from bank import designs
out={}
man=json.load(open(CAL/'freeze_v1/validation_manifest.json'))
st=json.load(open(CAL/'freeze_v1/stress_sets.json'))
pops=sorted(designs())
assert sorted(map(int,st['sets']))==list(range(300))
rng=np.random.default_rng(9*10**12+17*10**6+999)
seen={n:{} for n in pops}; repeats=0
for tid in range(300):
    pp=st['sets'][str(tid)]
    assert sorted(pp)==pops
    for n in pops:
        j=int(rng.integers(2000)); obj=pp[n]
        assert obj['library_index']==j
        assert set(obj['theta'])==set(('s','f','sigma','rho','p_c','delta'))
        assert all(np.isfinite(v) for v in obj['theta'].values())
        if j in seen[n]:
            assert seen[n][j]==obj['theta']; repeats+=1
        seen[n][j]=obj['theta']
out['archived_stress']={'sets':300,'populations':len(pops),'index_rng_matches':2700,'repeated_index_theta_matches':repeats}
seeds=[c['seed'] for s in man['scenarios'] for c in s['chunks']]
assert len(seeds)==len(set(seeds))==170
assert st['seed'] not in seeds
for s in man['scenarios']:
    ids=[i for c in s['chunks'] for i in range(*c['trial_ids'])]
    assert ids==list(range(s['n_trials']))
    assert all(c['seed']==9*10**12+10**6*s['block']+c['c'] for c in s['chunks'])
assert sum(s['n_trials'] for s in man['scenarios'])==7900
out['manifest']={'blocks':17,'unique_chunk_seeds':170,'trials':7900,'stress_seed_disjoint':True}
bank_seeds=[]
for name in ('primary','stability','iid'):
    meta=json.load(open(CAL/f'freeze_v1/bank_{name}_meta.json'))
    bank_seeds.extend(t['seed'] for t in meta['tasks'])
assert len(bank_seeds)==len(set(bank_seeds))==540
validation_seeds=set(seeds)|{st['seed']}
assert validation_seeds.isdisjoint(bank_seeds)
assert validation_seeds.isdisjoint({9_500_000_000_000+a for a in range(1,23)})
out['seed_disjointness']={'validation_and_stress':171,'unique_bank_tasks':540,'empirical_analyses':22,'disjoint':True}
with tempfile.TemporaryDirectory(prefix='protocol10_manifest_') as td:
    td=pathlib.Path(td); lp=td/'libs.npz'; mp=td/'manifest.json'; sp=td/'stress.json'
    cols=('s','f','sigma','rho','p_c','delta')
    arrays={f'{n}__{k}':np.arange(2000)+pi*10000+ki*100000 for pi,n in enumerate(pops) for ki,k in enumerate(cols)}
    np.savez(lp,**arrays)
    proc=subprocess.run([sys.executable,str(CAL/'make_manifest.py'),str(CAL/'freeze_v1/effect_target_ar_cat.json'),str(lp),man['bankdir'],man['root'],str(mp),str(sp),str(man['workers']),man['code_commit']],capture_output=True,text=True,check=True)
    freshman=json.load(open(mp)); freshst=json.load(open(sp))
    assert freshman['scenarios']==man['scenarios']
    assert all(freshman[k]==man[k] for k in ('variant','R','K','budget','beta_min','workers','code_commit'))
    for tid in range(300):
        for n in pops:
            obj=freshst['sets'][str(tid)][n]; j=obj['library_index']
            assert j==st['sets'][str(tid)][n]['library_index']
            assert all(obj['theta'][k]==float(arrays[f'{n}__{k}'][j]) for k in cols)
    out['make_manifest_fixture']={'stdout':proc.stdout.strip(),'parameter_row_coherence':True,'scenarios_match_archive':True}
old=e.simulate_chunk
calls=[]
def fail(design,variant,n,rng,**kwargs):
    calls.append(n)
    return np.zeros((n,3)),{},np.zeros(n,bool),np.zeros(n,bool)
e.simulate_chunk=fail
assert e.fresh_selected({},'ar_cat',np.random.default_rng(1)) is None
assert calls==[200000]*5
calls.clear()
assert e.fresh_selected({},'ar_cat',np.random.default_rng(1),budget=200003) is None
assert calls==[200000,3]
out['budget']={'default_exact_attempts':1000000,'remainder_cap_calls':calls.copy()}
def success(design,variant,n,rng,**kwargs):
    rec=np.tile([20,7,1],(n,1)); p={'s':np.full(n,.7),'md_shift':np.arange(n)/n,'md_tau':np.arange(n)+1,'latent':rec+1}
    sel=np.zeros(n,bool); sel[3]=True; sel[6]=True
    return rec,p,np.zeros(n,bool),sel
e.simulate_chunk=success
sel=e.fresh_selected({},'ar_cat',np.random.default_rng(1),detect=lambda n:.9,budget=10)
assert sel['params']=={'s':.7,'md_shift':.3,'md_tau':4.0}
assert sel['latent']==[21,8,2] and sel['recorded']==[20,7,1]
out['selected_provenance']={'first_selected_index_retained':3,'md_parameters_and_full_counts':True,'draws_field':sel['draws']}
e.simulate_chunk=old
# Real bounded generator: verify fresh-selected output matches the exact chosen row.
oldchunk=e.GEN_CHUNK; e.GEN_CHUNK=10000
d={'years':[0,1,2,3],'counts':np.array([10,7,3,0])}
for kind,kw in [('MD',{'drift':{'form':'step','hi':2.}}),('MO',{'detect':lambda n:np.full(np.shape(n),.9)})]:
    rec,p,o,sl=old(d,'ar_cat',10000,np.random.default_rng(77),**kw)
    assert sl.any(); i=np.flatnonzero(sl)[0]
    rr=e.fresh_selected(d,'ar_cat',np.random.default_rng(77),budget=10000,**kw)
    assert rr['recorded']==rec[i].astype(int).tolist()
    assert rr['params']=={k:float(v[i]) for k,v in p.items() if k!='latent' and np.isfinite(v[i])}
    if kind=='MO': assert rr['latent']==p['latent'][i].astype(int).tolist()
    out[kind+'_real_fixture']={'draws':10000,'selected_count':int(sl.sum()),'chosen_row':int(i),'exact_provenance_match':True}
e.GEN_CHUNK=oldchunk
print(json.dumps(out,indent=2))
json.dump(out,open(pathlib.Path(__file__).with_name('sampler_audit.json'),'w'),indent=2)
