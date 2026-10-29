"""Exercise repaired dispatch with actual shell enforcement and a bounded PBS model."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / 'analysis/fable/calibration/kunanyi'
OUT = Path(__file__).resolve().parent
FILES = ['v2_dev/p1_sampler.py', 'v2_dev/p2_stage1a.py', 'v2_dev/p3_stage1b.py',
         'v2_dev/p3_r2_determinism.py', 'kunanyi/s1b_node.pbs', 'kunanyi/s1b_collect.pbs',
         'kunanyi/s1b_submit.sh', 'kunanyi/s1b_capacity.sh', 'kunanyi/s1b_round3_dispatch.sh',
         'kunanyi/s1b_topup_dispatch.sh']
ns = {}
exec((ROOT / 'analysis/fable/calibration/v2_dev/p3/rehearsal_round3_stubs.py').read_text(), ns)
STUBS = ns['STUBS']
PYTHON = r'''
import json,os,pathlib,sys
a=sys.argv[1:]
with open(os.environ['FIX_PY_CALLS'],'a') as f: f.write(json.dumps(a)+'\n')
if len(a)>1 and a[1]=='-':
 pathlib.Path(a[3]).write_text('s00001\n')
 pathlib.Path(a[4]).write_text('W1 18\nW2 6917\n')
elif len(a)>2 and a[2]=='select':
 pathlib.Path(a[4]).write_text('{"fixture":true}\n')
else: print('{"preflight":"passed"}')
'''
QSTAT = r'''
import json,os,pathlib,sys
a=sys.argv[1:]; jobs=json.loads(pathlib.Path(os.environ['FIX_STATE']).read_text())
mode=os.environ.get('VISIBILITY','full')
if '-u' in a:
 if mode=='listing_failure': sys.exit(2)
 me=a[a.index('-u')+1]; load=int(os.environ.get('FIX_LOAD','0'))
 print('Job ID Username Queue Jobname SessID NDS TSK Memory Time S Time')
 if load: print(f'777777.fixture {me} normal other -- 1 {load} 1gb 48:00 R --')
 for k,j in enumerate(jobs):
  if j['state']=='F' or (mode=='hide_w1' and k==0) or (mode=='hide_w1_collector' and k==1): continue
  ar=j['args']; num=j['id'].split('.')[0]
  if '-J' in ar:
   n=int(ar[ar.index('-J')+1].split('-')[1])+1
   cpus=int(next(x for x in ar if 'ncpus=' in x).split('ncpus=')[1].split(':')[0])
   print(f'{num}[].fixture {me} normal {j["name"]} -- 1 {cpus} 1gb 48:00 B --')
   visible=0 if mode=='parent_only_w1' and k==0 else 1 if mode=='one_subjob_w1' and k==0 else n
   for i in range(visible): print(f'{num}[{i}].fixture {me} normal {j["name"]} -- 1 {cpus} 1gb 48:00 Q --')
  else: print(f'{j["id"]} {me} normal {j["name"]} -- 1 1 1gb 08:00 Q --')
 sys.exit(0)
jid=a[-1]
if jid.split('[')[0].split('.')[0] in ['857922','857923','858016','858017','860989','860990','860992','860993']:
 print('job_state = F'); sys.exit(0)
j=next((x for x in jobs if x['id']==jid),None)
if j is None: sys.exit(153)
if mode=='exact_query_failure' and '-x' in a: sys.exit(2)
print('job_state = '+j['state'])
if '-J' in j['args']:
 n=int(j['args'][j['args'].index('-J')+1].split('-')[1])+1
 print(f'array_state_count = Queued:{n if j["state"]!="F" else 0} Running:0 Held:0 Expired:0')
else: print('Mail_Users = fixture\nMail_Points = ae')
'''

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def prepare(base):
    c = Path('src/analysis/fable/calibration')
    stage = base / 'stage_round3'
    for rel in FILES:
        p = stage / c / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if rel.startswith('kunanyi/') and (SRC / Path(rel).name).exists():
            shutil.copy2(SRC / Path(rel).name, p)
        else:
            p.write_text('fixture\n')
    manifest = stage / 's1b/stage_sha256.txt'
    manifest.parent.mkdir(parents=True)
    manifest.write_text(''.join(f'{sha(stage/c/r)}  ./{c/r}\n' for r in FILES))
    tar = base / 's1b_stage_round3.tar'
    with tarfile.open(tar, 'w') as tf:
        for p in sorted(stage.rglob('*')):
            if p.is_file(): tf.add(p, arcname='./' + str(p.relative_to(stage)))
    shutil.copytree(stage / 'src', base / 'src')
    (base / 's1b/run2').mkdir(parents=True)
    (base / 's1b/reservations.tsv').write_text('')
    for f in ('p3_settings_r2.json', 'run2/collect_W1_b.json', 'run2/collect_W2_b.json'):
        (base / 's1b' / f).write_text('{}\n')
    (base / 'jobs.json').write_text('[]')
    (base / 'bin').mkdir()
    for name, body in {'qsub':STUBS['qsub'], 'qselect':STUBS['qselect'], 'qstat':QSTAT, 'python':PYTHON}.items():
        p = base / 'bin' / name
        p.write_text(f'#!{sys.executable}\n'+body)
        p.chmod(0o755)
    (base / c / 'kunanyi/env.sh').write_text(f'export PATH="{base}/bin:$PATH"\ncd "$VBASE/src"\n')
    return dict(os.environ, VB=str(base), PBS_BIN=str(base/'bin'), PBS_USER='fixture',
                FIX_STATE=str(base/'jobs.json'), FIX_LEDGER=str(base/'ledger.jsonl'),
                FIX_CALLS=str(base/'calls.jsonl'), FIX_QSELECT_CALLS=str(base/'qselect.n'),
                FIX_PY_CALLS=str(base/'py.jsonl'), STAGE_SHA=sha(tar), W1_SUMMARY_SHA='stub', W2_SUMMARY_SHA='stub',
                CAP_CPUS='7000', MIN_W2_JOBS='20', LIST_TRIES='1', LIST_SECS='0', S1A_CONFIRM_SECS='0')


def demand(base, load=0):
    total=load
    for j in json.loads((base/'jobs.json').read_text()):
        if j['state']=='F': continue
        a=j['args']
        total += (int(a[a.index('-J')+1].split('-')[1])+1)*8 if '-J' in a else 1
    return total


def run(base, env, script='s1b_round3_dispatch.sh'):
    before=len((base/'calls.jsonl').read_text().splitlines()) if (base/'calls.jsonl').exists() else 0
    p=subprocess.run(['bash',str(SRC/script)],env=env,text=True,capture_output=True)
    after=len((base/'calls.jsonl').read_text().splitlines()) if (base/'calls.jsonl').exists() else 0
    return {'rc':p.returncode,'qsub_calls':after-before,'actual_live_cpu_requests':demand(base,int(env.get('FIX_LOAD','0'))),
            'stdout':p.stdout.replace(str(base),'<fixture>'),'stderr':p.stderr.replace(str(base),'<fixture>')}


def case(mode, stale=False, followup=False):
    with tempfile.TemporaryDirectory(prefix='r3_cap_closure_') as td:
        base=Path(td); env=prepare(base); env['VISIBILITY']=mode
        if stale:
            (base/'s1b/run3').mkdir(); (base/'s1b/run3/r3_W2.jobs').write_text('874\n'); env['FIX_LOAD']='72'
        results=[run(base,env)]
        if followup:
            env['VISIBILITY']='full'; results.append(run(base,env))
        return results


def topup_stale():
    with tempfile.TemporaryDirectory(prefix='r3_cap_topup_') as td:
        base=Path(td); env=prepare(base); first=run(base,env)
        assert first['rc']==0
        jobs=json.loads((base/'jobs.json').read_text())
        for j in jobs: j['state']='F'
        (base/'jobs.json').write_text(json.dumps(jobs))
        (base/'s1b/run3/topup_b_W2.jobs').write_text('874\n')
        env.update(LABEL='b',WAVES='W2',REF=jobs[2]['id'],FIX_LOAD='72')
        result=run(base,env,'s1b_topup_dispatch.sh')
        result['new_size']=int((base/'s1b/run3/topup_b_W2.jobs').read_text())
        return result


cases={
    'normal_and_resume':case('full',followup=True),
    'stale_size_recomputed':case('full',stale=True),
    'accepted_w1_wholly_unlisted':case('hide_w1',followup=True),
    'accepted_w1_collector_unlisted':case('hide_w1_collector',followup=True),
    'user_listing_query_failure':case('listing_failure'),
    'exact_array_query_failure':case('exact_query_failure'),
    'inconsistent_parent_only_listing':case('parent_only_w1'),
    'inconsistent_one_subjob_listing':case('one_subjob_w1'),
    'topup_stale_size_recomputed':topup_stale(),
}
assert [(r['rc'],r['qsub_calls'],r['actual_live_cpu_requests']) for r in cases['normal_and_resume']]==[(0,4,6994),(0,0,6994)]
assert cases['stale_size_recomputed'][0]['rc']==0 and cases['stale_size_recomputed'][0]['actual_live_cpu_requests']==6994
assert [(r['rc'],r['qsub_calls']) for r in cases['accepted_w1_wholly_unlisted']]==[(1,1),(0,3)]
assert [(r['rc'],r['qsub_calls']) for r in cases['accepted_w1_collector_unlisted']]==[(1,2),(0,2)]
assert cases['user_listing_query_failure'][0]['rc']!=0 and cases['user_listing_query_failure'][0]['qsub_calls']==0
assert cases['exact_array_query_failure'][0]['rc']!=0 and cases['exact_array_query_failure'][0]['qsub_calls']==1
assert cases['inconsistent_parent_only_listing'][0]['rc']==0 and cases['inconsistent_parent_only_listing'][0]['actual_live_cpu_requests']==7498
assert cases['inconsistent_one_subjob_listing'][0]['rc']==0 and cases['inconsistent_one_subjob_listing'][0]['actual_live_cpu_requests']==7490
assert cases['topup_stale_size_recomputed']['rc']==0 and cases['topup_stale_size_recomputed']['new_size']==865
assert cases['topup_stale_size_recomputed']['actual_live_cpu_requests']==6993
result={'source_sha256':{n:sha(SRC/n) for n in ['s1b_submit.sh','s1b_capacity.sh','s1b_round3_dispatch.sh','s1b_topup_dispatch.sh']},
        'cap':7000,'all_assertions_passed':True,'cases':cases,
        'limits':'Actual dispatcher, submitter and capacity shell code; simulated PBS, preflight, summary selection and tiny stage. Parent/partial listings are injected inconsistent PBS responses, not observed behavior or established normal -t output.'}
(OUT/'capacity_closure_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'all_assertions_passed':True,'cases':{k:[{x:r[x] for x in ('rc','qsub_calls','actual_live_cpu_requests')} for r in v] if isinstance(v,list) else {x:v[x] for x in ('rc','qsub_calls','actual_live_cpu_requests','new_size')} for k,v in cases.items()}},indent=2))
