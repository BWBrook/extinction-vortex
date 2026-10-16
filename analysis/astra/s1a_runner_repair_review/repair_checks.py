"""Bounded independent Stage1a repair audit: synthetic retained-hit recovery/collector tests.
No bank loading, new outer data, population pilot, fitting, or scheduler command.
"""
import builtins, contextlib, copy, hashlib, importlib.util, io, json, os, sys, time
from pathlib import Path
from unittest.mock import patch
from datetime import datetime
from zoneinfo import ZoneInfo
SRC=Path('/data/fable/vortex/kunanyi_stage/run1/src');os.chdir(SRC)
HP=Path('/data/fable/vortex/v2_dev/p2_stage1a.py');DP=HP.with_name('p2')
spec=importlib.util.spec_from_file_location('repair_audit',HP);p=importlib.util.module_from_spec(spec);sys.modules[spec.name]=p;spec.loader.exec_module(p)
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
res={'scope':__doc__,'timestamp':datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),'runner_sha256':p.sha(HP)}
bound=p.check(str(DP/'p2_settings_s1a.json'),str(DP/'p2_metric.json'))
res['bound_check_passes']=True
base_b={'batch':10,'hit_stop':99,'_binding':{'fixture':'repair-review-20261016'}}
base_st={'index':7,'pop':'synthetic','outer':'toy/0','n':0,'E':{'n':0,'k':0,'r':0},'proposal_budget':30,'batches':3}

def fake(st,mp,bi,B,des):
 r={k:0 for k in p.COUNTERS};r.update(proposals=B,poisson_accept=B,theta_accept=B,paths=B,selected_SA=2,hits=2,hits_lo=2,hits_hi=2)
 theta={'s':.5,'f':.3,'sigma':.5,'rho':.3,'p_c':.02,'delta':.7}
 r['hit_records']=[{'batch':bi,'proposal_in_batch':j,'boundary':False,'theta':theta,'recorded':[5,4,0]} for j in (1,3)]
 return r

def fresh(name):
 d=out/name;d.mkdir();return d

def go(d,**kw):
 return p.run_setting(kw.get('b',base_b),kw.get('st',base_st),{},str(d),kw.get('deadline',float('inf')),{},ckpt_secs=kw.get('cadence',0.))

def state(d):return json.loads((d/'s0007.json').read_text())
def data(d):return (d/'s0007_hits.jsonl').read_bytes() if (d/'s0007_hits.jsonl').exists() else b''
def comparable(S):return {k:S.get(k) for k in (*p.COUNTERS,'status','batches_done','stop','journal_bytes','journal_sha256')}

with patch.object(p,'one_batch',fake):
 d=fresh('reference');ref=go(d);refblob=data(d)
 cases={}
 # Torn first append: actual bytes are truncated midway while the zero checkpoint survives.
 d=fresh('torn_first_append');orig_open=builtins.open
 class TornWriter:
  def __init__(self,fh):self.fh=fh
  def __enter__(self):return self
  def __exit__(self,*args):self.fh.close()
  def write(self,blob):
   self.fh.write(blob[:len(blob)//2]);self.fh.flush();os.fsync(self.fh.fileno());raise KeyboardInterrupt('torn first append')
 def torn_open(path,mode='r',*args,**kw):
  fh=orig_open(path,mode,*args,**kw)
  return TornWriter(fh) if str(path).endswith('_hits.jsonl') and mode=='ab' else fh
 with patch.object(builtins,'open',torn_open):
  try:go(d)
  except KeyboardInterrupt:pass
 before={'committed_hits':state(d)['hits'],'uncommitted_bytes':len(data(d))};S=go(d)
 cases['torn_first_append']={'before':before,'same_counters':comparable(S)==comparable(ref),'same_records':data(d)==refblob}
 # Interrupt after a checkpoint rename, when the new committed state already exists.
 d=fresh('after_state_replace');orig_replace=os.replace;calls=[0]
 def after_state(src,dst):
  orig_replace(src,dst)
  if str(dst).endswith('s0007.json'):
   calls[0]+=1
   if calls[0]==2:raise KeyboardInterrupt('after state replace')
 with patch.object(os,'replace',after_state):
  try:go(d)
  except KeyboardInterrupt:pass
 before={'committed_hits':state(d)['hits'],'journal_lines':data(d).count(b'\n')};S=go(d)
 cases['after_state_replace']={'before':before,'same_counters':comparable(S)==comparable(ref),'same_records':data(d)==refblob}
 # Interrupt after recovery has atomically replaced the journal with its committed prefix.
 d=fresh('after_recovery_replace')
 def kill_second(st,mp,bi,B,des):
  if bi==1:raise KeyboardInterrupt('before next batch')
  return fake(st,mp,bi,B,des)
 with patch.object(p,'one_batch',kill_second):
  try:go(d)
  except KeyboardInterrupt:pass
 with (d/'s0007_hits.jsonl').open('ab') as fh:fh.write(b'{"incomplete')
 def after_recovery(src,dst):
  orig_replace(src,dst)
  if str(dst).endswith('_hits.jsonl'):raise KeyboardInterrupt('after recovery replacement')
 with patch.object(os,'replace',after_recovery):
  try:go(d)
  except KeyboardInterrupt:pass
 before={'committed_hits':state(d)['hits'],'journal_lines':data(d).count(b'\n')};S=go(d)
 cases['after_recovery_replace']={'before':before,'same_counters':comparable(S)==comparable(ref),'same_records':data(d)==refblob}
 assert all(x['same_counters'] and x['same_records'] for x in cases.values())
 res['independent_recovery_cases']=cases

 # Minimal two-setting collection fixtures. Both checkpoints and journals are genuine run_setting outputs.
 def collect_fixture(kind):
  d=fresh('collect_'+kind);rd=d/'run';rd.mkdir();mp=d/'metric.json';sp=d/'settings.json';cp=d/'collect.json'
  mp.write_text(json.dumps({'outers':{'synthetic|toy/0':{'recorded':[5,4,0]}}}))
  sts=[dict(base_st,index=i,worker=i) for i in (0,1)]
  config={'metric_sha256':p.sha(mp),'runner_sha256':'fixture','batch':10,'nworkers':2,'hit_stop':99,'prefix_batches':1,'allowed_runtimes':[p.runtime()],'settings':sts}
  sp.write_text(json.dumps(config));binding={'settings_sha256':p.sha(sp),'metric_sha256':p.sha(mp),'runner_sha256':'fixture'}
  for st in sts:
   p.run_setting(dict(base_b,_binding=binding),st,{},str(rd),float('inf'),{},ckpt_secs=0.)
   p.atomic_json({'worker':st['worker'],'nworkers':2,'binding':binding,'host':'audit-host','runtime':p.runtime(),'peak_rss_gib':.1},str(rd/f"worker{st['worker']:04d}.json"))
  if kind=='missing_workers':
   for w in rd.glob('worker*.json'):w.unlink()
  elif kind=='invalid_worker_runtime':
   wp=rd/'worker0000.json';w=json.loads(wp.read_text());w['runtime']={'python':'0','numpy':'0','scipy':'0'};p.atomic_json(w,str(wp))
  elif kind=='missing_worker_provenance':
   wp=rd/'worker0000.json';w=json.loads(wp.read_text());w={k:w[k] for k in ('worker','nworkers','binding')};p.atomic_json(w,str(wp))
  elif kind=='bad_checkpoint_type':
   ck=rd/'s0000.json';S=json.loads(ck.read_text());S['batches_done']='3';p.atomic_json(S,str(ck))
  elif kind=='negative_counters':
   ck=rd/'s0000.json';S=json.loads(ck.read_text());S['overflow']=-7;S['rounding_excess']=-9;S['cpu_seconds']=-1.;p.atomic_json(S,str(ck))
  elif kind=='json_corrupt_checkpoint':(rd/'s0000.json').write_text('{"broken"')
  elif kind=='malformed_record':
   hp=rd/'s0000_hits.jsonl';blob=hp.read_bytes();lines=blob.splitlines(True);lines[0]=b'x'*(len(lines[0])-1)+b'\n';blob=b''.join(lines);hp.write_bytes(blob)
   ck=rd/'s0000.json';S=json.loads(ck.read_text());S['journal_sha256']=hashlib.sha256(blob).hexdigest();p.atomic_json(S,str(ck))
  elif kind=='duplicate_record':
   hp=rd/'s0000_hits.jsonl';ls=hp.read_bytes().splitlines(True);ls[1]=ls[0];blob=b''.join(ls);hp.write_bytes(blob)
   ck=rd/'s0000.json';S=json.loads(ck.read_text());S['journal_bytes']=len(blob);S['journal_sha256']=hashlib.sha256(blob).hexdigest();p.atomic_json(S,str(ck))
  elif kind=='orphan_journal':(rd/'s0000.json').unlink()
  cp.write_text('{"collection_ok":true,"run_complete":true,"stale":true}')
  with contextlib.redirect_stdout(io.StringIO()):
   try:p.collect(str(sp),str(mp),str(rd),str(cp));exit_value=0
   except SystemExit as ex:exit_value=str(ex)
  c=json.loads(cp.read_text())
  return {'exit':exit_value,'collection_ok':c['collection_ok'],'run_complete':c['run_complete'],'status':c['status'],'rows':len(c['rows']),'row_ids':[r['index'] for r in c['rows']],'workers':len(c['workers']),'errors':c['errors'],'stale_summary_survives':'stale' in c,'row0':c['rows'][0] if c['rows'] else None}
 res['collector_cases']={kind:collect_fixture(kind) for kind in ('valid','json_corrupt_checkpoint','malformed_record','duplicate_record','bad_checkpoint_type','missing_workers','invalid_worker_runtime','missing_worker_provenance','negative_counters','orphan_journal')}
(out/'repair_checks.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps({'independent_recovery_cases':res['independent_recovery_cases'],'collector_cases':{k:{kk:vv for kk,vv in v.items() if kk!='row0'} for k,v in res['collector_cases'].items()}},indent=2))
