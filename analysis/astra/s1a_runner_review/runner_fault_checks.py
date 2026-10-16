"""Bounded Stage 1a runner audit. No production pilot, bank loading or fits.
Synthetic batches drive crash cases; a two-batch setting775 comparison uses actual dynamics.
"""
import builtins, copy, importlib.util, json, os, sys, time
from pathlib import Path
from unittest.mock import patch
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
SRC=Path('/data/fable/vortex/kunanyi_stage/run1/src'); os.chdir(SRC)
HP=Path('/data/fable/vortex/v2_dev/p2_stage1a.py'); DP=HP.with_name('p2')
spec=importlib.util.spec_from_file_location('p2audit',HP); p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
out=Path(sys.argv[1]); out.mkdir(parents=True,exist_ok=True)
res={'scope':__doc__,'timestamp':datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),'runner_sha256':p.sha(HP)}
bound=p.check(str(DP/'p2_settings_s1a.json'),str(DP/'p2_metric.json'))
res['actual_bound_check_passes']=True
res['actual_imported_paths']={'bank':p.bank.__file__,'simulate_given_module':p.simulate_given.__module__,'runner':p.__file__}
# The guard really rejects a changed metric file and forbidden runtime.
changed=out/'changed_metric.json';changed.write_bytes((DP/'p2_metric.json').read_bytes()+b'\n')
try: p.check(str(DP/'p2_settings_s1a.json'),str(changed));metric_bad=False
except SystemExit: metric_bad=True
with patch.object(p,'runtime',lambda:{'python':'invalid','numpy':'invalid','scipy':'invalid'}):
 try:p.check(str(DP/'p2_settings_s1a.json'),str(DP/'p2_metric.json'));rt_bad=False
 except SystemExit:rt_bad=True
res['negative_bindings']={'changed_metric_rejected':metric_bad,'forbidden_runtime_rejected':rt_bad}
# Additional input cases absent from canonical test.
reject=[]
for E in ({'n':30,'k':float('nan'),'r':1},{'n':30,'k':2,'r':float('inf')},{'n':float('nan'),'k':2,'r':1},{'n':-1,'k':0,'r':0}):
 try:p.validate_E(E);reject.append(False)
 except SystemExit:reject.append(True)
res['nonfinite_or_negative_E_rejected']=reject
res['zero_radius_no_underflow_match']=p.in_ball(np.array([[0.],[1e-200]]),np.array([0.]),0.)['in'].tolist()==[True,False]

# Actual retained-record indexing check: independently reconstruct setting 775 batches0 and1.
metric=json.loads((DP/'p2_metric.json').read_text());des=p.designs()
st=bound['settings'][775]; mp=dict(metric['outers'][f"{st['pop']}|{st['outer']}"],**{k:metric['pops'][st['pop']][k] for k in ('keep','mad')})
actual=[]
for bi in (0,1):
 B=20000; got=p.one_batch(st,mp,bi,B,des)
 rng=np.random.default_rng([20261015,2,775,bi]);th=p.bank.draw_params('ar_cat',B,rng)
 up,ub=np.log(rng.random(B)),np.log(rng.random(B));u,v=p.rate_functionals(th)
 E=st['E'];hp=p.factors(th,E)[0];hb=p.binom_factor(u,E['n'],E['k'])
 ids=np.flatnonzero((up<hp)&(ub<hb));acc={k:th[k][ids] for k in p.PARAMS}
 rec,params,over,sel=p.simulate_given(des[st['pop']],'ar_cat',acc,rng)
 keep=np.array(mp['keep']);mad=np.array(mp['mad']);cs=p.calib_features(rec[sel])[:,keep]/mad[keep]
 d=np.sqrt(((cs-np.array(mp['q']))**2).sum(1)); hit=d<=mp['radius']; selected_ids=np.flatnonzero(sel)
 expected=[]
 for j in np.flatnonzero(hit):
  a=selected_ids[j]
  expected.append({'batch':bi,'proposal_in_batch':int(ids[a]),'boundary':bool(d[j]==mp['radius']),'theta':{k:float(acc[k][a]) for k in p.PARAMS},'recorded':rec[a].astype(int).tolist()})
 assert got['hit_records']==expected
 assert got['theta_accept']==got['paths']==len(ids)
 assert got['selected_SA']==int(sel.sum()) and got['overflow']==int(over.sum())
 actual.append({'batch':bi,'proposals':B,'accepted':len(ids),'hits':len(expected),'records_match':True})
res['actual_two_batch_775']=actual

# Fault fixtures use two identifiable synthetic hits per completed batch.
base_b={'batch':10,'hit_stop':99,'_binding':{'fixture':'s1a-audit-20261016'}}
base_st={'index':7,'pop':'synthetic','outer':'toy/0','n':0,'E':{'n':0,'k':0,'r':0},'proposal_budget':20,'batches':2}
keys=('proposals','poisson_accept','theta_accept','paths','selected_SA','overflow','hits','boundary','hits_lo','hits_hi','rounding_excess')
def batch(st,mp,bi,B,des):
 r={k:0 for k in keys};r.update(proposals=B,poisson_accept=B,theta_accept=B,paths=B,selected_SA=2,hits=2,hits_lo=2,hits_hi=2)
 r['hit_records']=[{'batch':bi,'proposal_in_batch':j,'boundary':False,'theta':{'s':.5},'recorded':[4,3,0]} for j in (1,3)]
 return r

def loc(name):
 d=out/name;d.mkdir();return d

def snap(d,S=None):
 ck=d/'s0007.json';hp=d/'s0007_hits.jsonl';lines=hp.read_text().splitlines() if hp.exists() else []
 s=S if S is not None else json.loads(ck.read_text()) if ck.exists() else None
 return {'state':({k:s[k] for k in ('status','batches_done','proposals','paths','hits')} if s else None),'journal_lines':len(lines),'record_ids':[ [json.loads(l)['batch'],json.loads(l)['proposal_in_batch']] for l in lines]}

def run(d,**kwargs):
 return p.run_setting(kwargs.get('b',base_b),kwargs.get('st',base_st),{},str(d),kwargs.get('deadline',float('inf')),{},ckpt_secs=kwargs.get('cadence',0.))

with patch.object(p,'one_batch',batch):
 # First commit fsyncs hits, then process dies before the first atomic state write.
 d=loc('first_commit_crash')
 with patch.object(p,'atomic_json',side_effect=KeyboardInterrupt('crash before first state replace')):
  try:run(d)
  except KeyboardInterrupt:pass
 before=snap(d);S=run(d);after=snap(d,S)
 res['orphan_first_commit']={'before_resume':before,'after_resume':after,'journal_matches_count':after['journal_lines']==S['hits']}

 # Last fully committed state is retained when second checkpoint atomic write is interrupted.
 d=loc('later_commit_crash');orig=p.atomic_json;calls=[0]
 def later(obj,path):
  calls[0]+=1
  if calls[0]==2:raise KeyboardInterrupt('crash before second state replace')
  orig(obj,path)
 with patch.object(p,'atomic_json',later):
  try:run(d)
  except KeyboardInterrupt:pass
 before=snap(d);S=run(d);after=snap(d,S)
 res['existing_checkpoint_with_tail']={'before_resume':before,'after_resume':after,'journal_matches_count':after['journal_lines']==S['hits']}

 def committed_first(d):
  def kill_second(st,mp,bi,B,des):
   if bi==1:raise KeyboardInterrupt('kill before batch two')
   return batch(st,mp,bi,B,des)
  with patch.object(p,'one_batch',kill_second):
   try:run(d)
   except KeyboardInterrupt:pass

 for kind in ('short','missing'):
  d=loc(kind+'_journal');committed_first(d);hp=d/'s0007_hits.jsonl'
  if kind=='short':hp.write_text(hp.read_text().splitlines()[0]+'\n')
  else:hp.unlink()
  before=snap(d);S=run(d);after=snap(d,S)
  res[kind+'_committed_journal']={'before_resume':before,'after_resume':after,'journal_matches_count':after['journal_lines']==S['hits']}

 # The recovery path itself truncates the existing committed journal before rewriting it.
 d=loc('crash_during_recovery');committed_first(d);orig_open=builtins.open;hp=d/'s0007_hits.jsonl'
 def crash_open(path,mode='r',*args,**kwargs):
  if str(path)==str(hp) and mode=='w':
   f=orig_open(path,mode,*args,**kwargs);f.close();raise KeyboardInterrupt('kill immediately after destructive open')
  return orig_open(path,mode,*args,**kwargs)
 with patch.object(builtins,'open',crash_open):
  try:run(d)
  except KeyboardInterrupt:pass
 before=snap(d);S=run(d);after=snap(d,S)
 res['recovery_rewrite_crash']={'before_second_resume':before,'after_second_resume':after,'journal_matches_count':after['journal_lines']==S['hits']}

 # A terminal checkpoint returns early without validating its journal.
 d=loc('complete_missing_journal');S=run(d);(d/'s0007_hits.jsonl').unlink();again=run(d)
 res['complete_missing_journal']=snap(d,again)

 # Censoring commits completed exposure and pending hits before returning.
 d=loc('deadline');clock=[0.]
 def timed_batch(*args):
  result=batch(*args);clock[0]+=1.;return result
 with patch.object(p.time,'time',lambda:clock[0]),patch.object(p,'one_batch',timed_batch):S=run(d,deadline=.5,cadence=60.)
 res['deadline_after_one_batch']=snap(d,S)
 assert S['status']=='censored' and S['batches_done']==1 and S['hits']==2 and S['proposals']==10

 # Whole crossing batch is retained, then no further batch starts.
 d=loc('hit_stop');S=run(d,b=dict(base_b,hit_stop=3),st=dict(base_st,batches=10,proposal_budget=100),cadence=60.)
 res['hit_stop_crossing_batch']=dict(snap(d,S),stop=S['stop'])
 assert S['hits']==4 and S['batches_done']==2 and S['stop']=='hits' and S['proposals']==20

 # Bound failure records a failed state rather than a successful zero yield.
 d=loc('runtime_failure')
 with patch.object(p,'one_batch',side_effect=RuntimeError('bound violation (injected)')):S=run(d)
 res['bound_failure']=dict(snap(d,S),failure=S['failure'])
 assert S['status']=='failed' and S['proposals']==0

res['limits']='No bank/outer/library construction, no fitting, no full1080 pilot; only canonical unit suite, two actual 20k-proposal batches twice for reference checking, and synthetic fault cases.'
(out/'fault_checks.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res,indent=2))
