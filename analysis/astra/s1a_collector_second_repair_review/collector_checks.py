"""Focused second-repair collector checks. Synthetic batches only; no population simulation."""
import contextlib, hashlib, importlib.util, io, json, os, sys
from pathlib import Path
from unittest.mock import patch
from datetime import datetime
from zoneinfo import ZoneInfo
os.chdir('/data/fable/vortex/kunanyi_stage/run1/src')
HP=Path('/data/fable/vortex/v2_dev/p2_stage1a.py')
spec=importlib.util.spec_from_file_location('second_repair_audit',HP)
p=importlib.util.module_from_spec(spec);sys.modules[spec.name]=p;spec.loader.exec_module(p)
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
res={'scope':__doc__,'timestamp':datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),'runner_sha256':p.sha(HP),'cases':{}}
def fake(st,mp,bi,B,des):
 r={k:0 for k in p.COUNTERS};r.update(proposals=B,poisson_accept=B,theta_accept=B,paths=B,selected_SA=2,hits=2,hits_lo=2,hits_hi=2)
 theta={'s':.5,'f':.3,'sigma':.5,'rho':.3,'p_c':.02,'delta':.7}
 r['hit_records']=[{'batch':bi,'proposal_in_batch':j,'boundary':False,'theta':theta,'recorded':[5,4,0]} for j in (1,3)]
 return r
mutations={
 'negative_fields':{'overflow':-7,'rounding_excess':-9,'cpu_seconds':-1.},
 'string_batches':{'batches_done':'3'},
 'boolean_counter':{'overflow':False},
 'negative_wall':{'wall_seconds':-1.},
 'nonfinite_cpu':{'cpu_seconds':float('nan')},
 'invalid_digest':{'journal_sha256':'g'*64},
 'unknown_status':{'status':'finished'},
 'unknown_stop':{'stop':'deadline'},
 'invalid_failure':{'status':'failed','failure':42},
 'wrong_index':{'index':1},
 'running_past_budget':{'status':'running','batches_done':4},
 'failed_past_budget':{'status':'failed','batches_done':4,'failure':'fixture failure'},
}
for kind in ['valid',*mutations,'missing_workers','missing_provenance','invalid_runtime','empty_host','negative_rss','nonfinite_rss','row_exception','censored','failed','running','hit_stop']:
 d=out/kind;d.mkdir();rd=d/'run';rd.mkdir();mp=d/'metric.json';sp=d/'settings.json';cp=d/'collect.json'
 mp.write_text(json.dumps({'outers':{'synthetic|toy/0':{'recorded':[5,4,0]}}}))
 sts=[{'index':i,'worker':i,'pop':'synthetic','outer':'toy/0','n':0,'E':{'n':0,'k':0,'r':0},'proposal_budget':30,'batches':3} for i in (0,1)]
 config={'metric_sha256':p.sha(mp),'runner_sha256':'fixture','batch':10,'nworkers':2,'hit_stop':3 if kind=='hit_stop' else 99,'prefix_batches':1,'allowed_runtimes':[p.runtime()],'settings':sts}
 sp.write_text(json.dumps(config));binding={'settings_sha256':p.sha(sp),'metric_sha256':p.sha(mp),'runner_sha256':'fixture'}
 def producer(st,mp,bi,B,des):
  if kind in ('running','censored','failed') and st['index']==0 and bi==2:raise KeyboardInterrupt('fixture interruption')
  return fake(st,mp,bi,B,des)
 with patch.object(p,'one_batch',producer):
  for st in sts:
   try:p.run_setting(dict(config,_binding=binding),st,{},str(rd),float('inf'),{},ckpt_secs=0.)
   except KeyboardInterrupt:pass
   p.atomic_json({'worker':st['worker'],'nworkers':2,'binding':binding,'host':'audit-host','runtime':p.runtime(),'peak_rss_gib':.1},str(rd/f"worker{st['worker']:04d}.json"))
 ck=rd/'s0000.json';S=json.loads(ck.read_text())
 if kind in mutations:S.update(mutations[kind])
 if kind in ('running_past_budget','failed_past_budget'):S.pop('stop',None)
 if kind in ('running','censored','failed'):
  S['status']=kind
  if kind=='failed':S['failure']='fixture failure'
 p.atomic_json(S,str(ck))
 wp=rd/'worker0000.json';w=json.loads(wp.read_text())
 if kind=='missing_provenance':w={k:w[k] for k in ('worker','nworkers','binding')}
 elif kind=='invalid_runtime':w['runtime']={'python':'0','numpy':'0','scipy':'0'}
 elif kind=='empty_host':w['host']=''
 elif kind=='negative_rss':w['peak_rss_gib']=-1.
 elif kind=='nonfinite_rss':w['peak_rss_gib']=float('inf')
 p.atomic_json(w,str(wp))
 if kind=='missing_workers':
  for w in rd.glob('worker*.json'):w.unlink()
 cp.write_text('{"collection_ok":true,"run_complete":true,"stale":true}')
 original=p.check_setting
 def check(st,*a,**kw):
  if kind=='row_exception' and st['index']==0:raise TypeError('injected per-row exception')
  return original(st,*a,**kw)
 with patch.object(p,'check_setting',check), contextlib.redirect_stdout(io.StringIO()):
  try:p.collect(str(sp),str(mp),str(rd),str(cp));exit_value=0
  except SystemExit as ex:exit_value=str(ex)
 c=json.loads(cp.read_text())
 res['cases'][kind]={'exit':exit_value,**{k:c[k] for k in ('collection_ok','run_complete','provenance_complete','workers_missing','status','errors')},'row_ids':[r['index'] for r in c['rows']],'row_statuses':[r['status'] for r in c['rows']],'stale_survives':'stale' in c,'row0':c['rows'][0]}
checks={}
for kind in mutations:
 if kind not in ('running_past_budget','failed_past_budget'):
  c=res['cases'][kind];checks['reject_'+kind]=not c['collection_ok'] and c['row_statuses']==['invalid','complete']
for kind in ('missing_provenance','invalid_runtime','empty_host','negative_rss','nonfinite_rss'):
 c=res['cases'][kind];checks['reject_'+kind]=not c['collection_ok'] and not c['provenance_complete'] and c['workers_missing']==[0] and c['row_ids']==[0,1]
c=res['cases']['missing_workers'];checks['missing_workers_separate']=c['collection_ok'] and c['run_complete'] and not c['provenance_complete'] and c['workers_missing']==[0,1]
c=res['cases']['row_exception'];checks['per_row_exception_isolated']=not c['collection_ok'] and c['row_ids']==[0,1] and c['row_statuses']==['invalid','complete']
for kind in ('running','failed','censored'):
 c=res['cases'][kind];r=c['row0'];checks['sensitivity_'+kind]=c['collection_ok'] and not c['run_complete'] and 'ci95_suffix' not in r and 'ci_method' not in r and len(r['sensitivity_interval95_suffix'])==2 and 'not a formal interval' in r['sensitivity_note']
for kind,method in [('valid','Clopper-Pearson'),('hit_stop','exact negative binomial')]:
 c=res['cases'][kind];r=c['row0'];checks['formal_'+kind]=c['collection_ok'] and c['run_complete'] and c['provenance_complete'] and 'ci95_suffix' in r and r['ci_method'].startswith(method) and 'sensitivity_interval95_suffix' not in r
checks['all_old_summaries_replaced']=all(not c['stale_survives'] for c in res['cases'].values())
checks['report_rule_qualified']='no coverage is claimed conditional on the subset of settings that completed' in p.REPORT_RULE and 'get no formal interval' in p.REPORT_RULE
res['required_checks']=checks;res['required_checks_all_pass']=all(checks.values())
res['limited_additional_observations']={k:{q:res['cases'][k][q] for q in ('collection_ok','run_complete','row_ids','row_statuses','errors')} for k in ('wrong_index','running_past_budget','failed_past_budget')}
(out/'collector_checks.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps({k:v for k,v in res.items() if k!='cases'},indent=2))
assert res['required_checks_all_pass']
