"""Copy of analysis/astra/r2_node_plan_review/check_current_node.py (Codex, 6c773da) with a clock-advancing sleep stub, a 300 s timeout and baseline assertions replaced by recorded outcomes; run by Fable on node 00ed12fb, 23 Oct."""
"""Bounded observations of the CURRENT node script, not a proposed implementation.

Actual Bash node wrapper, one slot, stub worker/time/sleep/certificate rename.
No PBS, simulation, remote writes, production directories or source mutation.
The resulting baseline pins acceptance cases for the 23 October refill proposal.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path('/home/bwbrook/papers/project')
OUT = Path(__file__).resolve().parent
NODE = ROOT / 'analysis/fable/calibration/kunanyi/s1b_node.pbs'


def exe(path, code):
    path.write_text(f'#!{sys.executable}\n{code}\n')
    path.chmod(0o755)


def scenario(name, codes, *, failed_certificate=False, cross_deadline=False, claims=False, initial_expired=False):
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp); vb = base/'vb'; bin_ = base/'bin'; bin_.mkdir()
        k = vb/'src/analysis/fable/calibration/kunanyi'; k.mkdir(parents=True)
        run = vb/'s1b/run2'; logs = run/'submit_W2_b/logs'; logs.mkdir(parents=True)
        (run/'queue').mkdir(); (run/'claimed').mkdir()
        if claims: (run/'claimed/W2_0000000_s00002_000000000_000000010@other.0r0nabc').touch()
        clock = base/'clock'; clock.write_text('1000000')
        record = base/'calls.jsonl'
        exe(bin_/'date', '''import os,sys,subprocess
from pathlib import Path
if sys.argv[1:]==['+%s']: print(Path(os.environ['FIX_CLOCK']).read_text())
else: raise SystemExit(subprocess.call(['/bin/date']+sys.argv[1:]))
''')
        exe(bin_/'sleep', '''import os,sys
from pathlib import Path
c=Path(os.environ['FIX_CLOCK'])
if os.environ.get('FIX_CROSS_DEADLINE')=='1': c.write_text('1009000')
else: c.write_text(str(int(c.read_text())+int(float(sys.argv[1]))))
''')
        exe(bin_/'mv', '''import os,sys
if os.environ.get('FIX_FAIL_CERT')=='1':
 print('fixture: certificate rename refused',file=sys.stderr); raise SystemExit(1)
os.rename(sys.argv[1],sys.argv[2])
''')
        exe(bin_/'python', '''import json,os,sys
from pathlib import Path
p=Path(os.environ['FIX_CALLS']); calls=[json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []
owner=sys.argv[-2]; deadline=int(sys.argv[-1]); run=Path(sys.argv[-4])
codes=json.loads(os.environ['FIX_CODES']); rc=codes[min(len(calls),len(codes)-1)]
previous_cert=None
if calls:
 cp=run/'workers/dead'/calls[-1]['owner']
 previous_cert=json.loads(cp.read_text()) if cp.exists() else None
with p.open('a') as f:
 f.write(json.dumps({'owner':owner,'pid':os.getpid(),'deadline':deadline,'clock':int(Path(os.environ['FIX_CLOCK']).read_text()),'rc':rc,'previous_cert':previous_cert})+'\\n')
raise SystemExit(rc)
''')
        (k/'env.sh').write_text('cd "$VBASE/src"\n')
        env = dict(os.environ, PATH=str(bin_)+':'+os.environ['PATH'], VBASE=str(vb), OUTDIR='run2', TAG='W2_b',
                   WAVE='W2', SETTINGS='p3_settings_r2.json', PBS_ARRAY_INDEX='7', PBS_JOBID='123[7].kunanyi',
                   JOBCPUS='1', WALL_SECS='1800' if initial_expired else '10000', FIX_CLOCK=str(clock),
                   FIX_CALLS=str(record), FIX_CODES=json.dumps(codes), FIX_FAIL_CERT=str(int(failed_certificate)),
                   FIX_CROSS_DEADLINE=str(int(cross_deadline)))
        p = subprocess.run(['bash', str(NODE)], env=env, text=True, capture_output=True, timeout=300)
        calls = [json.loads(l) for l in record.read_text().splitlines()] if record.exists() else []
        certs = [json.loads(f.read_text()) for f in (run/'workers/dead').iterdir() if not f.name.startswith('.')] if (run/'workers/dead').exists() else []
        result = {'rc': p.returncode, 'launches': len(calls), 'calls': calls, 'certificates': certs,
                  'done': ((logs/'done.7').read_text().strip() if (logs/'done.7').exists() else None), 'stderr': p.stderr.replace(tmp, '<tmp>'),
                  'same_wave_claims_remaining': len(list((run/'claimed').iterdir())),
                  'launches_at_or_after_worker_deadline': sum(c['clock'] >= c['deadline'] for c in calls)}
        assert len({c['owner'] for c in calls}) == len(calls)
        return result


cases = {
    'exit75_cap': scenario('exit75_cap', [75]),
    'non75_cap': scenario('non75_cap', [2]),
    'zero_with_claims': scenario('zero_with_claims', [0], claims=True),
    'certificate_failure': scenario('certificate_failure', [75, 0], failed_certificate=True),
    'deadline_crossed_during_sleep': scenario('deadline_crossed_during_sleep', [75, 0], cross_deadline=True),
    'deadline_elapsed_at_start': scenario('deadline_elapsed_at_start', [0], initial_expired=True),
}





out = {'scope': __doc__, 'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
       'node_sha256': hashlib.sha256(NODE.read_bytes()).hexdigest(), 'cases': cases,
       'arithmetic': {'initial_requested_cpus_including_collectors': 300*8+570*8+2,
                      'probe_requested_cpus_including_collectors': (291+186+384)*8+2,
                      'max_additional_8cpu_subjobs_after_W1_and_collector_end_if_full_W2_remains': (7000-570*8-1-1)//8,
                      'idle_300x8_for_48h_allocated_cpu_h': 300*8*48,
                      '4560_slots_divided_by_10_second_pause': 4560/10}}
(OUT/'new_node_outcomes.json').write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps({k:{x:v[x] for x in ('rc','launches','launches_at_or_after_worker_deadline')} for k,v in cases.items()},indent=2))
