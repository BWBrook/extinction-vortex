"""Read-only independent Stage 1a input and saved-smoke audit on deep-server.
No bank loading, population simulation, model fit, or scheduler operation.
Run through stdin; stdout is a JSON receipt. MADs are checked structurally,
not recomputed from all bank rows; all q/E/radius mappings are recomputed.
"""
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import platform
import time
from zoneinfo import ZoneInfo
import numpy as np

ROOT=Path('/data/fable/vortex')
V2=ROOT/'v2_dev'; P2=V2/'p2'
SRC=ROOT/'kunanyi_stage/run1/src'
MAN=SRC.parent/'validation_manifest.json'
SCEN=('null_prior_predictive','null_low_s','MA_betamin','MA_d10_0.5')
POPS=('wild_dog','marmot','ms_woodpecker','rc_woodpecker','golden_plover','whooping_crane','hawaiian_crow','wood_turtle_A','wood_turtle_B')

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def read(p):
    return json.loads(Path(p).read_text())

def c_feature(rec):
    changes=np.diff(np.log(np.asarray(rec,dtype=float)[:-1]))
    centered=changes-changes.mean()
    ss=np.sum(centered**2)
    return np.array([np.mean(changes**2),np.sum(centered[1:]*centered[:-1])/ss if ss>0 else 0.,np.mean(changes>0)])

def main():
    t0=time.monotonic()
    m=read(P2/'p2_metric.json'); b=read(P2/'p2_settings_s1a.json')
    man=read(MAN); inputs=read(V2/'s0/s0_inputs.json')
    assert sha(V2/'s0/s0_inputs.json')==m['s0_inputs_sha256']
    assert sha(P2/'p2_metric.json')==b['metric_sha256']
    assert sha(V2/'p2_stage1a.py')==b['runner_sha256']
    assert sha(V2/'p1_sampler.py')==b['p1_sampler_sha256']
    assert all(sha(SRC/p)==h for p,h in b['imported_source_sha256'].items())
    assert m['bank_meta_sha256']==man['bank_sha256']['bank_meta.json']
    bankmeta=ROOT/'kunanyi_run1/extract'/man['bankdir']/'bank_meta.json'
    assert sha(bankmeta)==m['bank_meta_sha256']
    shard_map={k:v for d in m['source_bank_sha256'].values() for k,v in d.items()}
    assert shard_map=={k:v for k,v in man['bank_sha256'].items() if k!='bank_meta.json'}
    expected_outers={f'{p}|{s}/{t}' for p in POPS for s in SCEN for t in range(10)}
    assert set(m['outers'])==expected_outers
    assert set(m['E'])=={f'{k}|{n}' for k in expected_outers for n in (30,300)}
    raw_hashes={}; qdiffs=[]
    for p in POPS:
        metrics=m['pops'][p]; mad=np.array(metrics['mad']); keep=np.array(metrics['keep'],bool)
        assert mad.shape==keep.shape==(3,) and np.isfinite(mad).all() and (mad>=0).all()
        assert np.array_equal(keep,mad>0)
        raw_path=V2/'s0/full'/f's0_{p}.json'
        raw=read(raw_path); raw_hashes[p]=sha(raw_path)
        assert raw['population']==p and raw['bank_rows']==metrics['bank_rows']
        rows={r['outer']:r for r in raw['rows']}
        for si,s in enumerate(SCEN):
            for t in range(10):
                o=f'{s}/{t}'; key=f'{p}|{o}'; v=m['outers'][key]
                assert v['recorded']==inputs['outers'][o]['pops'][p]['recorded']
                assert v['radius']==rows[o]['kth']
                assert np.isfinite(v['radius']) and v['radius']>=0
                expected=c_feature(v['recorded'])[keep]/mad[keep]
                err=float(np.max(abs(expected-np.array(v['q'])))); qdiffs.append(err)
                assert err<1e-12
                for ni,n in enumerate((30,300)):
                    e=inputs['E'][f'{4*ni+si}/{t}/{p}']
                    assert m['E'][f'{key}|{n}']=={k:e[k] for k in ('n','k','r')}
    expected_keys=[(p,f'{s}/{t}',n) for p in POPS for s in SCEN for t in range(10) for n in (0,30,300)]
    assert [(x['pop'],x['outer'],x['n']) for x in b['settings']]==expected_keys
    assert [x['index'] for x in b['settings']]==list(range(1080))
    throughput=read(P2/'throughput_kunanyi.json')
    assert sha(P2/'throughput_kunanyi.json')==b['throughput_sha256']
    loads=np.zeros(b['nworkers']); allocation={}
    for st in b['settings']:
        key=f"{st['pop']}|{st['outer']}|{st['n']}"
        expected_e={'n':0,'k':0,'r':0} if st['n']==0 else m['E'][key]
        assert st['E']==expected_e
        secs=825 if st['n']==0 else 3300
        budget=max(20000,int(throughput[key]*secs)//20000*20000)
        assert st['proposal_budget']==budget and st['batches']==budget//20000
        assert st['expected_seconds']==budget/throughput[key]
    for st in sorted(b['settings'],key=lambda x:(-x['expected_seconds'],x['index'])):
        w=min(range(b['nworkers']),key=lambda i:(loads[i],i))
        assert st['worker']==w
        loads[w]+=st['expected_seconds']; allocation.setdefault(w,[]).append(st['n'])
    assert all(len(v)==3 and v.count(0)==1 and all(n in (0,30,300) for n in v) for v in allocation.values())
    assert max(loads)==b['max_worker_expected_seconds']
    dirs={'deep_original':P2/'dry','kunanyi':P2/'kunanyi_smoke/smoke','deep_repaired':P2/'dry2'}
    names=('proposals','poisson_accept','theta_accept','paths','selected_SA','overflow','hits','boundary','hits_lo','hits_hi','rounding_excess','batches_done','status')
    totals=Counter(); hit_settings=[]; comparisons=Counter(); objects={}
    receipts={}; hits_by_n=Counter(); rate_ratios={n:[] for n in (0,30,300)}
    for name,path in dirs.items():
        collect=read(path/'collect.json'); objects[name]=collect
        receipts[name]=dict(path=str(path),collect_sha256=sha(path/'collect.json'),status=collect['status'])
        assert collect['status']==dict(complete=1080,censored=0,failed=0,missing=0,running=0)
    for i,st in enumerate(b['settings']):
        snapshots={name:read(path/f's{i:04d}.json') for name,path in dirs.items()}
        journals={name:(path/f's{i:04d}_hits.jsonl').read_text().splitlines() if (path/f's{i:04d}_hits.jsonl').exists() else [] for name,path in dirs.items()}
        base=snapshots['deep_original']; records=journals['deep_original']
        for name,S in snapshots.items():
            assert all(S[k]==base[k] for k in names)
            assert journals[name]==records and len(records)==S['hits']
            comparisons[name]+=1
        assert base['proposals']==100000 and base['batches_done']==5
        for key in names[:-1]: totals[key]+=base[key]
        hits_by_n[st['n']]+=base['hits']
        if base['hits']:hit_settings.append(i)
        rate_ratios[st['n']].append(base['cpu_seconds']/snapshots['kunanyi']['cpu_seconds'])
        key=f"{st['pop']}|{st['outer']}|{st['n']}"
        assert throughput[key]==snapshots['kunanyi']['proposals']/snapshots['kunanyi']['cpu_seconds']
        for rec in map(json.loads,records):
            assert 0<=rec['batch']<5 and 0<=rec['proposal_in_batch']<20000
            assert set(rec['theta'])=={'s','f','sigma','rho','p_c','delta'}
            x=rec['recorded']; assert all(a>1 for a in x[1:-1]) and x[-1]<=1
    assert totals['hits']==38 and len(hit_settings)==34
    out=dict(timestamp=datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),runtime=dict(python=platform.python_version(),numpy=np.__version__),
             scope=__doc__,metric_sha256=sha(P2/'p2_metric.json'),settings_sha256=sha(P2/'p2_settings_s1a.json'),
             runner_sha256=sha(V2/'p2_stage1a.py'),source_shard_hash_map_matches=len(shard_map),
             actual_bank_meta_hash_match=True,metric_outer_records_and_radii_match=360,evidence_records_match=720,
             normalized_query_max_error=max(qdiffs),mads='finite nonnegative/mask structural check only; not recomputed from full banks',
             raw_s0_sha256=raw_hashes,settings_exact_count=1080,settings_n_counts=dict(Counter(st['n'] for st in b['settings'])),
             proposal_budgets_exact=True,lpt_assignment_exact=True,worker_count=len(loads),worker_load_seconds_range=[min(loads),max(loads)],
             expected_worker_hours=float(sum(loads)/3600),total_proposal_budget=sum(s['proposal_budget'] for s in b['settings']),
             smoke_saved_result_comparisons=dict(comparisons),smoke_archives=receipts,smoke_totals=dict(totals),smoke_hits_by_n=dict(hits_by_n),
             smoke_settings_with_hits=hit_settings,kunanyi_to_deep_rates_median={n:float(np.median(v)) for n,v in rate_ratios.items()},
             elapsed_seconds=time.monotonic()-t0)
    print(json.dumps(out,indent=2,allow_nan=False))

if __name__=='__main__':main()
