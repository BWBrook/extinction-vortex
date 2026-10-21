"""Read-only source audit with isolated PBS stubs. No live PBS, remote runs or production ledgers.

Tests the literal dispatch admission gate, actual select/ledger/preflight bodies
(native binding and scientific self-tests stubbed), actual submit/dispatch shell,
and actual collector shell with deterministic concurrent collector stubs.
"""
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
K = ROOT / 'analysis/fable/calibration/kunanyi'
P3 = ROOT / 'analysis/fable/calibration/v2_dev/p3_stage1b.py'
DISPATCH = (K / 's1b_round2_dispatch.sh').read_text()
GATE = DISPATCH.split("<<'PY'\n", 1)[1].split('\nPY\n', 1)[0]
BASH42 = Path('/tmp/claude-1000/-home-bwbrook-papers-project/2114b555-0c74-405f-bb3d-7860a2e979f1/scratchpad/bash42/bash-4.2/bash')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def executable(path, body):
    path.write_text(f'#!{sys.executable}\n{body}\n')
    path.chmod(0o755)


def fixture_inputs():
    b = {'stage': 'fixture', 'settings': [
        {'dir': f's{i:05d}', 'index': i, 'pop': 'fixture', 'outer': f'b1/{i}', 'n': 30 if i < 3 else 300,
         'library': 'primary', 'wave': 'W1' if i < 3 else 'W2'} for i in range(4)],
         'campaign': 's1b', 'ceilings': {'W1': 200000, 'W2': 1000000, 'campaign': 1200000}}
    c = {'wave': 'W1', 'collection_ok': False, 'binding': {'settings_sha256': 'fixture-original',
        'runner_sha256': 'fixture-old-runner', 'metric_sha256': 'fixture-metric'},
         'rows': [dict(s, status=status) for s, status in zip(b['settings'], ['COMPLETE', 'incomplete', 'invalid'])],
         'status': {'COMPLETE': 1, 'CAPPED': 0, 'FAILED': 0, 'incomplete': 1},
         'n_errors': 1, 'errors': ['s00002: ValueError: verified K-hit prefix without a COMPLETE marker']}
    return b, c


def gate_tests():
    b, c = fixture_inputs()
    variants = {'normal': c}
    x = copy.deepcopy(c); x['binding']['settings_sha256'] = 'WRONG'; variants['wrong_settings_binding'] = x
    x = copy.deepcopy(c); del x['binding']; variants['missing_binding'] = x
    x = copy.deepcopy(c); x['rows'][0]['status'] = 'UNKNOWN'; variants['unknown_status'] = x
    x = copy.deepcopy(c); x['rows'][0]['index'] = 98765; x['rows'][0]['pop'] = 'other'; variants['wrong_row_identity'] = x
    x = copy.deepcopy(c); x['rows'].append(copy.deepcopy(x['rows'][0])); variants['duplicate_complete_row'] = x
    x = copy.deepcopy(c); x['rows'].pop(0); variants['missing_dir'] = x
    x = copy.deepcopy(c); x['n_errors'] = 2; variants['truncated_errors'] = x
    x = copy.deepcopy(c); x['errors'].append('s00000: ValueError: non-invalid error'); x['n_errors'] = 2
    variants['error_outside_invalid'] = x
    result = {}
    with tempfile.TemporaryDirectory() as td:
        d = Path(td); (d/'settings.json').write_text(json.dumps(b))
        for name, value in variants.items():
            (d/'collect.json').write_text(json.dumps(value)); (d/'dirs.txt').unlink(missing_ok=True)
            p = subprocess.run([sys.executable, '-', str(d/'collect.json'), str(d/'settings.json'), str(d/'dirs.txt')],
                               input=GATE, text=True, capture_output=True)
            result[name] = {'rc': p.returncode, 'stderr': p.stderr.strip(),
                            'selected': (d/'dirs.txt').read_text().splitlines() if (d/'dirs.txt').exists() else None}
    return result


src = (K/'s1a_submit_fixture.py').read_text()
ns = {}
exec(src[src.index('STUBS = {'):src.index('\n\n\ndef scenario')], {}, ns)
STUBS = ns['STUBS']
tree = ast.parse(P3.read_text())
FUNCTIONS = '\n\n'.join(ast.unparse(n) for n in tree.body if isinstance(n, ast.FunctionDef)
                         and n.name in ('select', 'ledger_active', 'reserve', 'preflight'))
PYTHON = '''import sys,os,json,time,types,hashlib
open(os.environ['FIX_PY_CALLS'],'a').write(json.dumps(sys.argv[1:])+'\\n')
if sys.argv[2] == '-':
    sys.argv = sys.argv[2:]
    exec(compile(sys.stdin.read(),'<literal-dispatch-gate>','exec'))
    raise SystemExit(0)
__file__ = os.path.abspath(sys.argv[2])
p2=types.SimpleNamespace(sha=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest(),runtime=lambda:{'stub':True})
check=lambda settings,metric:json.load(open(settings))
test=lambda:None
COLLECTOR_CPU_H=8
WAVES={'W1':(0,30),'W2':(300,)}
''' + FUNCTIONS + '''
cmd=sys.argv[3]
if cmd=='seed':
    print('seed stub')
elif cmd in ('select','preflight'):
    globals()[cmd](*sys.argv[4:])
else:
    raise SystemExit('unsupported stub command '+cmd)
'''


class Sandbox:
    def __init__(self, parent):
        self.d = Path(parent); self.bin = self.d/'bin'; self.bin.mkdir()
        self.vb = self.d/'vbase'; self.s = self.vb/'s1b'; self.s.mkdir(parents=True)
        cpath = Path('src/analysis/fable/calibration')
        self.k = self.vb/cpath/'kunanyi'; self.k.mkdir(parents=True)
        files = ['v2_dev/p1_sampler.py', 'v2_dev/p2_stage1a.py', 'v2_dev/p3_stage1b.py',
                 'v2_dev/p3_r2_determinism.py', 'kunanyi/s1b_node.pbs', 'kunanyi/s1b_collect.pbs',
                 'kunanyi/s1b_submit.sh', 'kunanyi/s1b_round2_dispatch.sh']
        for name in files:
            for dest in (self.vb/cpath/name, self.vb/'stage_r2'/cpath/name):
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT/'analysis/fable/calibration'/name, dest)
        stage = self.vb/'stage_r2'; (stage/'s1b').mkdir()
        (stage/'s1b/stage_sha256.txt').write_text(''.join(f'{sha(stage/cpath/f)}  {cpath/f}\n' for f in files))
        for name, body in STUBS.items():
            if name == 'python': body = PYTHON
            if name == 'qstat':
                body = "import sys\nif sys.argv[-1] in ('821088[]','821089'):\n print('    job_state = F'); raise SystemExit(0)\n" + body
            executable(self.bin/name, body)
        (self.k/'env.sh').write_text(f'export PATH="{self.bin}:$PATH"\ncd "$VBASE/src"\n')
        b,c = fixture_inputs()
        (self.s/'p3_settings.json').write_text(json.dumps(b)); (self.s/'p3_metric.json').write_text('{}')
        (self.s/'run').mkdir(); (self.s/'run/collect_W1.json').write_text(json.dumps(c))
        (self.s/'reservations.tsv').write_text('reserve\ts1b\tW1\ts1b_5e346b76_a\t199688.000\tfixture\toriginal\n')
        self.env = dict(os.environ, VB=str(self.vb), VBASE=str(self.vb), PBS_BIN=str(self.bin),
                        S1A_ENV=str(self.k/'env.sh'), S1A_CONFIRM_SECS='0', FIX_STATE=str(self.d/'jobs.json'),
                        FIX_LEDGER=str(self.d/'jobs.jsonl'), FIX_CALLS=str(self.d/'calls.jsonl'),
                        FIX_QSELECT_CALLS=str(self.d/'qselect.n'), FIX_PY_CALLS=str(self.d/'python.jsonl'))

    def calls(self):
        return [json.loads(x) for x in (self.d/'calls.jsonl').read_text().splitlines()] if (self.d/'calls.jsonl').exists() else []

    def jobs(self):
        return [json.loads(x) for x in (self.d/'jobs.jsonl').read_text().splitlines()] if (self.d/'jobs.jsonl').exists() else []

    def run(self, args, extra=None):
        before = len(self.calls())
        p = subprocess.run(args, env=dict(self.env, **(extra or {})), capture_output=True, text=True, timeout=30)
        return {'rc':p.returncode, 'new_qsub_calls':len(self.calls())-before,
                'stdout':p.stdout.replace(str(self.d),'<tmp>'), 'stderr':p.stderr.replace(str(self.d),'<tmp>')}


def dispatch_tests():
    with tempfile.TemporaryDirectory() as td:
        box = Sandbox(td)
        args = ['bash', str(box.k/'s1b_round2_dispatch.sh')]
        first = box.run(args, {'FIX_FAIL_AT':'3','FIX_FAIL_MODE':'reject'})
        retry = box.run(args)
        return {'first_W2_array_rejected':first, 'wrapper_retry':retry, 'jobs':box.jobs(),
                'ledger':(box.s/'reservations.tsv').read_text().splitlines()}


def checksum_failure():
    with tempfile.TemporaryDirectory() as td:
        box=Sandbox(td)
        staged=box.vb/'stage_r2/src/analysis/fable/calibration/v2_dev/p3_stage1b.py'
        staged.open('a').write('\n# isolated fixture: bytes changed after stage manifest was made\n')
        result=box.run(['bash',str(box.k/'s1b_round2_dispatch.sh')])
        return {'result':result,'jobs_created':len(box.jobs()),
                'changed_runner_installed':sha(staged)==sha(box.vb/'src/analysis/fable/calibration/v2_dev/p3_stage1b.py'),
                'ledger':(box.s/'reservations.tsv').read_text().splitlines()}


def topup_tests():
    with tempfile.TemporaryDirectory() as td:
        box = Sandbox(td)
        # Old production reservation is released in this isolated fixture only.
        (box.s/'reservations.tsv').open('a').write('release\ts1b_5e346b76_a\tmanual: fixture terminal\n')
        args = ['bash', str(box.k/'s1b_submit.sh'), str(box.vb), 'p3_settings.json', 'run2', 'W1', '1', '8', '48:00:00']
        first = box.run(args)
        b = json.loads((box.s/'p3_settings.json').read_text())
        (box.s/'other_settings.json').write_text(json.dumps(b,indent=2))
        other = args.copy(); other[3] = 'other_settings.json'
        topup = box.run(other+['topup','b'])
        jobs = box.jobs()
        return {'first':first, 'topup_different_settings_same_content':topup,
                'original_hash':sha(box.s/'p3_settings.json'), 'topup_hash':sha(box.s/'other_settings.json'),
                'jobs':jobs, 'original_jobs_still_live':json.loads((box.d/'jobs.json').read_text()),
                'runner_calls':[json.loads(x) for x in (box.d/'python.jsonl').read_text().splitlines()],
                'ledger':(box.s/'reservations.tsv').read_text().splitlines()}


def collector_race():
    with tempfile.TemporaryDirectory() as td:
        d=Path(td); vb=d/'vbase'; k=vb/'src/analysis/fable/calibration/kunanyi'; k.mkdir(parents=True)
        run=vb/'s1b/run2'; run.mkdir(parents=True); bin_=d/'bin'; bin_.mkdir()
        (k/'env.sh').write_text(f'export PATH="{bin_}:$PATH"\ncd "$VBASE/src"\n')
        executable(bin_/'python', '''import os,sys,json,time
from pathlib import Path
run=Path(sys.argv[-3]); tag=os.environ['TAG']; out=Path(sys.argv[-1])
if tag=='W1_c':
 for _ in range(500):
  if (run/'b_ready').exists():break
  time.sleep(.01)
out.write_text(json.dumps({'tag':tag,'collection_ok':True})+'\\n')
(run/'pack_W1.txt').write_text(out.name+'\\ncollect_W1.log\\n')
print('collector '+tag,flush=True)
if tag=='W1_b':
 (run/'b_ready').touch()
 for _ in range(500):
  if (run/'c_ready').exists():break
  time.sleep(.01)
else:(run/'c_ready').touch()
''')
        env=dict(os.environ,VBASE=str(vb),OUTDIR='run2',SETTINGS='settings.json',WAVE='W1')
        procs={tag:subprocess.Popen(['bash',str(K/'s1b_collect.pbs')],env=dict(env,TAG=tag),
                                   stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for tag in ('W1_b','W1_c')}
        result={}
        for tag,p in procs.items():
            stdout,stderr=p.communicate(timeout=15)
            names=subprocess.run(['tar','-tzf',str(run/f'{tag}.tar.gz')],capture_output=True,text=True)
            result[tag]={'rc':p.returncode,'stdout':stdout,'stderr':stderr,'archive_members':names.stdout.splitlines(),
                         'checksum_exists':(run/f'{tag}.tar.gz.sha256').exists()}
        return result


def supplied_fixture(shell):
    with tempfile.TemporaryDirectory() as td:
        d=Path(td)
        for name in ('s1b_submit.sh','s1b_submit_fixture.py','s1a_submit_fixture.py'):shutil.copy2(K/name,d/name)
        p=subprocess.run([sys.executable,str(d/'s1b_submit_fixture.py')],env=dict(os.environ,FIX_BASH=str(shell)),
                         text=True,capture_output=True,timeout=60)
        return {'rc':p.returncode,**json.loads((d/'s1b_submit_fixture.json').read_text())}


out={'scope':__doc__,'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
     'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [P3]+[K/n for n in
        ('s1b_round2_dispatch.sh','s1b_submit.sh','s1b_node.pbs','s1b_collect.pbs')]},
     'gate':gate_tests(),'dispatch':dispatch_tests(),'checksum_failure':checksum_failure(),
     'topup':topup_tests(),'collector_race':collector_race(),
     'published_bash52':supplied_fixture('bash'),
     'published_bash42':supplied_fixture(BASH42) if BASH42.exists() else {'not_available':str(BASH42)},
     'arithmetic':{'W1_cpu_h':300*8*48+8,'W2_cpu_h':570*8*48+8,'combined_cpu_h':870*8*48+16,
                   'requested_cpus_including_collectors':870*8+2,'subjobs_including_collectors':870+2}}
(OUT/'evidence.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'gate_rcs':{k:v['rc'] for k,v in out['gate'].items()},
                  'dispatch_rcs':[out['dispatch'][k]['rc'] for k in ('first_W2_array_rejected','wrapper_retry')],
                  'checksum_failure':{'rc':out['checksum_failure']['result']['rc'],
                                      'jobs_created':out['checksum_failure']['jobs_created']},
                  'topup_rc':out['topup']['topup_different_settings_same_content']['rc'],
                  'collector_race':out['collector_race'],'bash52':out['published_bash52']['all_ok'],
                  'bash42':out['published_bash42'].get('all_ok',out['published_bash42'])},indent=2))
