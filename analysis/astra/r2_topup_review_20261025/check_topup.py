"""Actual submission/collector shell integration for the proposed top-ups.

Temporary PBS and scientific-worker stubs only. Actual preflight reservation
body is exercised; native validation and seed are stubbed. No live PBS or
production mutation. The collector stub isolates TAG/archive file naming.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
helper = HERE.parent/'s1b_r2_scheduler_review/check_scheduler.py'
exec(compile(helper.read_text().split("\nout={'scope':", 1)[0], str(helper), 'exec'))
OUT = HERE


def integration():
    with tempfile.TemporaryDirectory() as td:
        box = Sandbox(td)
        sp = box.s/'p3_settings_r2.json'; sp.write_bytes((box.s/'p3_settings.json').read_bytes())
        run = box.s/'run2'; run.mkdir()
        original_hash = sha(sp)
        for wave in ('W1', 'W2'):
            r = run/f'submit_{wave}'; r.mkdir()
            (r/'run.json').write_text(f'settings=p3_settings_r2.json sha256={original_hash} outdir={run} wave={wave} tag={wave} jobs=1 cpus=8 walltime=48:00:00\n')
            (r/'submit_journal.tsv').write_text(f'accepted a original_{wave} fixture-original-{wave}\n')
        led = box.s/'reservations.tsv'
        led.write_text('reserve\ts1b\tW1\ts1b_22b89261_a\t115208.000\tfixture\toriginal-W1\n'
                       'reserve\ts1b\tW2\ts1b_3a5e71fa_a\t218888.000\tfixture\toriginal-W2\n'
                       'release\ts1b_22b89261_a\tmanual: isolated fixture models verified terminal W1 array and collector\n')
        args = ['bash', str(box.k/'s1b_submit.sh'), str(box.vb), 'p3_settings_r2.json', 'run2']
        w1 = box.run(args+['W1','170','8','48:00:00','topup','b'])
        w2 = box.run(args+['W2','325','8','48:00:00','topup','b'])
        repeat = box.run(args+['W1','170','8','48:00:00','resume','b'])
        subset = json.loads(sp.read_text()); subset['settings'] = subset['settings'][:1]
        (box.s/'subset48.json').write_text(json.dumps(subset))
        badargs = args.copy(); badargs[3] = 'subset48.json'
        badsubset = box.run(badargs+['W1','170','8','48:00:00','topup','c'])
        wrongrun = args.copy(); wrongrun[4] = 'run3'
        badrun = box.run(wrongrun+['W1','170','8','48:00:00','topup','d'])
        calls = [json.loads(l) for l in (box.d/'python.jsonl').read_text().splitlines()]
        jobs = box.jobs(); arrays = [j for j in jobs if j['name'].endswith('_a')]
        collectors = [j for j in jobs if j['name'].endswith('_c')]
        envs = [{x.split('=',1)[0]:x.split('=',1)[1] for x in j['args'][j['args'].index('-v')+1].split(',')} for j in arrays]
        dependencies = [j['args'][j['args'].index('-W')+1] for j in collectors]
        ledger_ns = {}; exec(FUNCTIONS, dict(os=os,json=json,time=time), ledger_ns)
        active = ledger_ns['ledger_active'](str(led), 's1b')
        result = {'W1_170': w1, 'W2_325_arithmetic_example': w2, 'resume_W1_b': repeat,
                  'subset_refused': badsubset, 'new_run_refused': badrun,
                  'settings_bytes_preserved': sha(sp) == original_hash,
                  'runner_commands': [c[2] for c in calls], 'array_environments': envs,
                  'array_ranges': [j['args'][j['args'].index('-J')+1] for j in arrays],
                  'array_resource_flags': [[j['args'][i+1] for i,x in enumerate(j['args']) if x=='-l'] for j in arrays],
                  'collector_dependencies': dependencies, 'array_ids': [j['id'] for j in arrays],
                  'ledger': led.read_text().splitlines(), 'active_reservations': active}
        assert [x['rc']==0 for x in (w1,w2,repeat,badsubset,badrun)] == [True,True,True,False,False]
        assert [x['new_qsub_calls'] for x in (w1,w2,repeat,badsubset,badrun)] == [2,2,0,0,0]
        assert result['runner_commands'] == ['preflight']*3
        assert result['array_ranges'] == ['0-169','0-324']
        assert result['settings_bytes_preserved'] and result['collector_dependencies'] == ['depend=afterany:'+j['id'] for j in arrays]
        assert all(e['SETTINGS']=='p3_settings_r2.json' and e['OUTDIR']=='run2' and e['JOBCPUS']=='8' and e['WALL_SECS']=='172800' for e in envs)
        assert [e['TAG'] for e in envs] == ['W1_b','W2_b']
        assert sorted(e['cpu_h'] for e in active.values()) == [65288.0,124808.0,218888.0]
        assert 's1b_22b89261_a' not in active and 's1b_3a5e71fa_a' in active
        return result


def archive_naming():
    with tempfile.TemporaryDirectory() as td:
        d=Path(td); vb=d/'vbase'; k=vb/'src/analysis/fable/calibration/kunanyi'; k.mkdir(parents=True)
        run=vb/'s1b/run2'; run.mkdir(parents=True); bin_=d/'bin'; bin_.mkdir()
        (k/'env.sh').write_text(f'export PATH="{bin_}:$PATH"\ncd "$VBASE/src"\n')
        executable(bin_/'python', '''import os,sys,json
from pathlib import Path
run=Path(sys.argv[-3]); tag=os.environ['TAG']; out=Path(sys.argv[-1])
out.write_text(json.dumps({'tag':tag,'collection_ok':True})+'\\n')
(run/f'pack_{tag}.txt').write_text(out.name+'\\n'+f'collect_{tag}.log\\n')
print('fixture collector '+tag)
''')
        previous={'W1.tar.gz':b'prior immutable archive sentinel', 'W1.tar.gz.sha256':b'prior checksum sentinel',
                  'collect_W1.json':b'prior summary sentinel', 'collect_W1.log':b'prior log sentinel', 'pack_W1.txt':b'prior pack sentinel'}
        for name,body in previous.items(): (run/name).write_bytes(body)
        env=dict(os.environ,VBASE=str(vb),OUTDIR='run2',SETTINGS='p3_settings_r2.json',WAVE='W1',TAG='W1_b')
        p=subprocess.run(['bash',str(K/'s1b_collect.pbs')],env=env,text=True,capture_output=True,timeout=10)
        names=subprocess.check_output(['tar','-tzf',str(run/'W1_b.tar.gz')],text=True).splitlines()
        check=subprocess.run(['sha256sum','-c','W1_b.tar.gz.sha256'],cwd=run,text=True,capture_output=True)
        unchanged=all((run/name).read_bytes()==body for name,body in previous.items())
        assert p.returncode==0 and check.returncode==0 and unchanged
        assert names==['collect_W1_b.json','collect_W1_b.log']
        return {'rc':p.returncode,'prior_W1_files_unchanged':unchanged,'archive_members':names,'checksum_rc':check.returncode}


result={'scope':__doc__,'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [P3]+[K/n for n in ('s1b_node.pbs','s1b_submit.sh','s1b_collect.pbs','env.sh')]},
        'integration':integration(),'archive_naming':archive_naming(),
        'resource_arithmetic':{'W1_max_simultaneous_shards':48*28,'W1_jobs_covering_that_bound':(48*28+7)//8,
            'W1_170_slots':170*8,'W1_48h_reservation':170*8*48+8,
            '25Oct_snapshot_live_subjobs':379,'W2_topup_max_if_snapshot_live_resource_count_applies':(7000-379*8-170*8-3)//8,
            'cpus_with_325_W2_topup_and_three_collectors':(379+170+325)*8+3,
            'whole_W2_original_reservation_retained':570*8*48+8,
            'campaign_reservation_after_170_W1_and_325_W2':570*8*48+8+170*8*48+8+325*8*48+8,
            'nominal_W1_170_all_idle_30min_cpu_h':170*8*0.5}}
(OUT/'evidence.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'integration_passed':True,'archive_naming':result['archive_naming'],'resource_arithmetic':result['resource_arithmetic']},indent=2))
