"""Bounded protocol-0.10 gate audit at df946937.

Synthetic T matrices and mocked entry points only: no bank loads, R fits,
empirical statistics or remote actions. Assertions characterize the reviewed
candidate's discrepancies; a repaired implementation should make them fail.
Run with the project scientific Python environment. Writes gate_audit.json
beside this script; all generated fixture files live in a tempfile directory.
"""
import csv, hashlib, json, os, pathlib, sys, tempfile
import numpy as np
REPO=pathlib.Path(__file__).resolve().parents[3]
SRC=REPO/'analysis/fable/calibration'
sys.path.insert(0, str(SRC))
import e2e_benchmark as e, score_discrimination as sc, collect_validation as cv, empirical_q1 as eq, validate as va
ROOT=pathlib.Path(tempfile.mkdtemp(prefix='protocol10_gate_'))
res={'fixture_root': str(ROOT), 'reviewed_commit': 'df9469377db01268c8c4ddd11d9968b642928dab',
     'source_sha256': {n: hashlib.sha256((SRC/n).read_bytes()).hexdigest() for n in
       ('e2e_benchmark.py','score_discrimination.py','collect_validation.py','validate.py','empirical_q1.py')}}
R=20
M=np.random.default_rng(29).normal(size=(2*R+1,4)); M[0]=M[1:R+1].mean(axis=0)

def csvfile(p, matrix, flags=None):
    if flags is None: flags=(~np.isfinite(matrix).all(axis=1)).astype(int)
    with open(p,'w') as f:
        w=csv.writer(f); w.writerow(['set','T1','T2','T3','T4','failed','fallback'])
        for i,t in enumerate(matrix): w.writerow([i,*t,flags[i],0])

def template(matrix=M, flags=None, name='T_template.csv'):
    p=ROOT/name; csvfile(p,matrix,flags); return p
TGOOD=template()

def makechunk(path, ids, matrix=M, T=TGOOD, metadata=None, omit=()):
    path=pathlib.Path(path); path.mkdir(parents=True,exist_ok=True)
    json.dump(metadata or {'R_train':R,'R_test':R,'K':50,'variant':'iid','beta':999,'manifest':'wrong.json'},open(path/'e2e_meta.json','w'))
    pb=e.p_bounds(matrix,R); log={'p_diagnostic':pb.get('p_lo','indeterminate'),'kth_dist':'{}','outcome':e.outcome(pb),**pb}
    with open(path/'e2e_rows.jsonl','w') as f:
        for i in ids:
            if i not in omit: f.write(json.dumps({'trial_id':i,**log})+'\n')
            os.link(T,path/f'T_{i}.csv')
    return {'dir':str(path),'trial_ids':[min(ids),max(ids)+1],'seed':999,'c':0}

def scenario(name,n, chunks, role='null', block=1):
    return {'name':name,'block':block,'role':role,'n_trials':n,'chunks':chunks,'beta':0,'spec':{},'stress':False}

# Exact gate thresholds; the reviewed code uses a strictly greater fit-stop threshold.
res['thresholds']={'null60_hi':cv.clopper_pearson(60,1000,.025)[1], 'null61_hi':cv.clopper_pearson(61,1000,.025)[1], 'power223_lo':cv.clopper_pearson(223,300,.1)[0], 'power224_lo':cv.clopper_pearson(224,300,.1)[0]}

# Full-size null, with deliberately wrong R/K/variant/beta/manifest metadata.
ch=makechunk(ROOT/'wrong_settings',range(1000))
s=scenario('null_wrong_settings',1000,[ch])
out=cv.collect_scenario(s)
res['collector_wrong_settings']={'chunk_R':R,'freeze_R':2000,'metadata':json.load(open(ROOT/'wrong_settings/e2e_meta.json')),'gate':out['null_gate'],'fit_failures':out['fit_failures']}

# Same 100 IDs read ten times: total 1000 counted, distinct IDs only 100.
cdup=makechunk(ROOT/'duplicate',range(100))
out=cv.collect_scenario(scenario('null_repeated_chunk',1000,[cdup]*10))
res['cross_chunk_duplicate']={'distinct_trials':100, 'counted_n':out['n'],'accepts':out['counts']['accept'],'gate':out['null_gate']}

# A completed, fully failed fitted trial whose JSON record was lost is skipped.
omit=set(range(970,1000))
cmiss=makechunk(ROOT/'missing_fitted_rows',range(1000),omit=omit)
TBAD=template(np.full_like(M,np.nan),name='T_allfailed.csv')
for i in omit:
    p=ROOT/'missing_fitted_rows'/f'T_{i}.csv';p.unlink();os.link(TBAD,p)
out=cv.collect_scenario(scenario('null_missing_fitted',1000,[cmiss]))
res['missing_fitted_rows']={'missing':out['counts']['missing'],'gate':out['null_gate'],'reported':out['fit_failures'],'fit_stop':out['fit_stop'],'actual_failed_present_Tfiles':30*(2*R+1),'actual_fitted_present_Tfiles':1000*(2*R+1),'actual_rate':.03}

# Missing T cells conflict with zero failure flags, accepted without malformed classification.
Mf=M.copy(); Mf[-2:]=np.nan
Tf=template(Mf,np.zeros(2*R+1),name='T_wrongflags.csv')
cf=makechunk(ROOT/'wrong_flags',range(1000),matrix=Mf,T=Tf)
out=cv.collect_scenario(scenario('null_wrongflags',1000,[cf]))
res['failed_flags_mismatch']={'actual_rate':2/(2*R+1),'reported':out['fit_failures'],'fit_stop':out['fit_stop'],'gate':out['null_gate']}

# Summary generated for old manifest then manifest changed in place; guard still accepts.
mp=ROOT/'manifest.json'; sp=ROOT/'summary.json'
json.dump({'R':2000,'K':2000,'variant':'ar_cat'},open(mp,'w'))
oldsha=hashlib.sha256(mp.read_bytes()).hexdigest()
json.dump({'manifest':str(mp),'v_fail':False,'fit_stop':False,'labels_available':['O2','O3']},open(sp,'w'))
json.dump({'R':20,'K':50,'variant':'iid'},open(mp,'w'))
res['guard_changed_manifest']={'original_sha256':oldsha,'current_sha256':hashlib.sha256(mp.read_bytes()).hexdigest(),'accepted':bool(eq.guard(str(mp),str(sp)))}
mp.unlink()
res['guard_absent_manifest']={'accepted':bool(eq.guard(str(mp),str(sp)))}

# Complete row IDs with deliberately wrong metadata are skipped by validate.main.
stress=ROOT/'stress.json';json.dump({'sets':{}},open(stress,'w'))
restart=dict(R=2000,K=2000,workers=18,bankdir='/missing',variant='ar_cat',budget=1000000,stress_sets=str(stress),scenarios=[s])
json.dump(restart,open(mp,'w'))
oldargv=sys.argv;old_des=va.designs;old_knn=va.e2e.knn_banks;old_run=va.e2e.run_chunk
calls=[]
try:
    sys.argv=['validate.py',str(mp),'0','1'];va.designs=lambda:{};va.e2e.knn_banks=lambda *args:{};va.e2e.run_chunk=lambda *args,**kwargs:calls.append('ran')
    va.main();res['restart_wrong_metadata']={'returned_success':True,'run_chunk_calls':len(calls)}
finally:
    sys.argv=oldargv;va.designs=old_des;va.e2e.knn_banks=old_knn;va.e2e.run_chunk=old_run

# Duplicate within a chunk is correctly refused.
p=ROOT/'duplicate/e2e_rows.jsonl';first=p.read_text().splitlines()[0]
with open(p,'a') as f:f.write(first+'\n')
try: sc.score_dir('v3',str(ROOT/'duplicate'),range(100));res['within_chunk_duplicate_refused']=False
except SystemExit:res['within_chunk_duplicate_refused']=True

# Valid JSON that has no ID crashes, rather than the documented missing outcome.
p=ROOT/'malformed_jsonrow';p.mkdir();json.dump({'R_train':R},open(p/'e2e_meta.json','w'));(p/'e2e_rows.jsonl').write_text('{}\n')
try:sc.score_dir('v3',str(p),range(1));res['malformed_row_result']='returned'
except Exception as ex:res['malformed_row_result']=type(ex).__name__+': '+str(ex)

# Characterization assertions: these establish the reported behavior without
# claiming the deliberately altered fixtures are the actual frozen inputs.
t=res['thresholds']
assert t['null60_hi'] <= .08 < t['null61_hi']
assert t['power223_lo'] < .70 <= t['power224_lo']
r=res['collector_wrong_settings']
assert r['chunk_R'] != r['freeze_R'] and r['gate']['pass']
assert r['fit_failures']['fitted_datasets'] == 1000*(2*R+1)
r=res['cross_chunk_duplicate']
assert r['distinct_trials'] == 100 and r['counted_n'] == r['accepts'] == 1000 and r['gate']['pass']
r=res['missing_fitted_rows']
assert r['missing'] == 30 and r['gate']['pass'] and r['fit_stop'] is False
assert r['reported'] == {'failed_datasets':0,'fitted_datasets':970*(2*R+1),'rate':0.0}
assert r['actual_failed_present_Tfiles']/r['actual_fitted_present_Tfiles'] == .03
r=res['failed_flags_mismatch']
assert r['actual_rate'] > .02 and r['reported']['rate'] == 0 and r['fit_stop'] is False
r=res['guard_changed_manifest']
assert r['original_sha256'] != r['current_sha256'] and r['accepted']
assert res['guard_absent_manifest']['accepted']
assert res['restart_wrong_metadata'] == {'returned_success':True,'run_chunk_calls':0}
assert res['within_chunk_duplicate_refused']
assert res['malformed_row_result'] == "KeyError: 'trial_id'"
# Separately establish that the supplied immutable manifest itself has the
# correct complete design; overlap examples above are guard probes only.
frozen=json.load(open(SRC/'freeze_v1/validation_manifest.json'))
assert [(s['block'],s['role'],s['n_trials']) for s in frozen['scenarios']] == [
    (b,'null' if b<=4 else 'power' if b==5 else 'stress' if b==17 else 'descriptive',
     1000 if b<=4 else 300) for b in range(1,18)]
for s in frozen['scenarios']:
    ids=[i for c in s['chunks'] for i in range(*c['trial_ids'])]
    assert ids == list(range(s['n_trials']))
assert sum(len(s['chunks']) for s in frozen['scenarios']) == 170
res['actual_frozen_manifest']={'blocks':17,'chunks':170,'trials':7900,'correct_roles_counts_and_ids':True}
res['characterization_assertions_passed']=True
out=pathlib.Path(__file__).with_suffix('.json')
out.write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res,indent=2))
