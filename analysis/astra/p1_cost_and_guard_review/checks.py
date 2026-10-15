"""Bounded arithmetic replay and Stage 0 reuse-guard fixtures; no bank or fit.

Run with OPENBLAS_NUM_THREADS=1 /home/bwbrook/papers/dsipa-dev/.venv/bin/python
analysis/astra/p1_cost_and_guard_review/checks.py from the repository.
"""
import ast
import contextlib
import copy
from datetime import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import tempfile
from zoneinfo import ZoneInfo

import numpy as np
import scipy
from scipy import stats
from scipy.special import xlogy, xlog1py

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
V2 = ROOT / 'analysis/fable/calibration/v2_dev'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cost_replay():
    scan = json.loads((V2/'p1/p1_scan.json').read_text())
    pilot = json.loads((V2/'p1/p1_pilot.json').read_text())
    costs = json.loads((V2/'p1/p1_cost_projection.json').read_text())
    rows = []
    for stored in costs:
        key = str(stored['setting'])
        p, s = pilot['settings'][key], scan['settings'][key]
        seconds_per_prior = p['seconds']/p['proposals']
        rate = s['forecast_retained_per_prior_proposal']
        forecast = rate*p['proposals']
        hours4000 = 4000*seconds_per_prior/rate/3600
        assert abs(hours4000-stored['cpu_hours_per_4000_retained']) < 1e-10
        assert abs(forecast-stored['forecast_hits']) < 1e-12
        assert abs(seconds_per_prior*1e6-stored['us_per_proposal']) < 1e-12
        rows.append(dict(setting=int(key), pop=p['pop'], outer=p['outer'], kind=p['kind'], n=p['n'],
                         actual_proposals=p['proposals'], actual_paths=p['paths'], hits=p['ball_hits'],
                         forecast_hits_at_actual_denominator=forecast,
                         forecast_hits_at_one_million_proposals=s['forecast_expected_hits_at_proposal_cap'],
                         wall_microseconds_per_prior_proposal=seconds_per_prior*1e6,
                         total_sampling_wall_microseconds_per_simulated_path=p['seconds']/p['paths']*1e6,
                         forecast_worker_hours_for_4000=hours4000,
                         forecast_worker_hours_for_2000=hours4000/2))
    informative = [r for r in rows if r['n']]
    controls = [r for r in rows if not r['n']]
    return dict(rows=rows, all_20_cost_rows_reproduce=True,
                total_observed_hits=sum(r['hits'] for r in rows),
                total_forecast_hits=sum(r['forecast_hits_at_actual_denominator'] for r in rows),
                informative_total_wall_us_per_path_range=[min(r['total_sampling_wall_microseconds_per_simulated_path'] for r in informative),max(r['total_sampling_wall_microseconds_per_simulated_path'] for r in informative)],
                n0_total_wall_us_per_path_range=[min(r['total_sampling_wall_microseconds_per_simulated_path'] for r in controls),max(r['total_sampling_wall_microseconds_per_simulated_path'] for r in controls)],
                informative_wall_us_per_proposal_range=[min(r['wall_microseconds_per_prior_proposal'] for r in informative),max(r['wall_microseconds_per_prior_proposal'] for r in informative)],
                sampling_seconds_summed=sum(p['seconds'] for p in pilot['settings'].values()),
                pilot_wall_seconds_including_bank_metric_setup=pilot['wall_seconds'],
                stage1a_noisy_settings=9*4*2*10,
                full_noisy_population_outer_cells=9*4*2*200,
                full_noisy_and_ideal_population_outer_cells=2*9*4*2*200,
                limitation='Stored timings are wall time for one worker, not a measured scheduler CPU allocation. Whole-study retention, fitting and cluster throughput remain unmeasured.')


def stage0_functions():
    path = V2/'s0_info.py'
    tree = ast.parse(path.read_text())
    names = {'sha','cell','rate_functionals','logw_noisy','logw_ideal','weight_stats','self_test','report'}
    selected = [n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
    assert len(selected)==len(names)
    x,w=np.polynomial.hermite_e.hermegauss(40)
    ns=dict(np=np, scipy=scipy, stats=stats, xlogy=xlogy, xlog1py=xlog1py,
            hashlib=hashlib,json=json,os=os,SCEN=('null_prior_predictive','null_low_s','MA_betamin','MA_d10_0.5'),
            NS=(30,300),ESS_FLAG=100,GH_X=x,GH_W=w/w.sum())
    exec(compile(ast.Module(body=selected,type_ignores=[]),str(path),'exec'),ns)
    return ns


def guard_fixtures():
    f=stage0_functions()
    f['self_test']()
    inf=f['weight_stats'](np.array([0.,np.inf]))
    assert inf == dict(usable=False,ess=None,max_share=None)
    endpoints=f['logw_ideal'](np.array([0.,1.]),np.array([0.,0.]),30,0.,0.)
    assert endpoints[0]==0 and np.isneginf(endpoints[1])
    binding=copy.deepcopy(json.loads((V2/'s0/s0_inputs.json').read_text())['bindings'])
    # A freshly prepared fixture, not an alteration of archived evidence.
    binding['helper_sha256']={'s0_info.py':sha(V2/'s0_info.py')}
    binding['runtime']=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__)
    keys=[f'{sc}/{i}' for sc in f['SCEN'] for i in range(200)]
    fixture=dict(bindings=binding,outers={k:{} for k in keys})
    rows=[]
    for k in keys:
        row=dict(outer=k,kth=.1,kth_mismatch=False,tie=False)
        for comp in ('noisy_30','ideal_30','noisy_300','ideal_300'):
            row[comp]=dict(usable=True,ess=2000.,max_share=.0005)
        rows.append(row)
    results={}
    with tempfile.TemporaryDirectory(prefix='s0-repair-audit-') as temp:
        base=Path(temp); inputs=base/'inputs.json'; inputs.write_text(json.dumps(fixture))
        good={}
        for pop in binding['population_order']:
            mp=base/f'members_{pop}.npz'
            np.savez_compressed(mp,keys=np.array(keys),draw_id=np.arange(2000,dtype=np.int64)[None,:].repeat(800,axis=0))
            good[pop]=dict(population=pop,binding=dict(inputs_sha256=sha(inputs),runner_sha256=sha(V2/'s0_info.py'),runtime=binding['runtime'],manifest_digest=binding['manifest_digest']),
                           seconds=0,peak_rss_gb=0,bank_rows=2000,members_sha256=sha(mp),rows=rows)
        first=binding['population_order'][0]
        for case in ('valid','drop_one_outer','duplicate_outer','wrong_population','wrong_input_hash','wrong_runtime','wrong_manifest','wrong_member_hash','missing_binding','wrong_runner_hash'):
            per=copy.deepcopy(good)
            target=per[first]
            if case=='drop_one_outer': target['rows'].pop()
            elif case=='duplicate_outer': target['rows'][-1]=copy.deepcopy(target['rows'][0])
            elif case=='wrong_population': target['population']='incorrect'
            elif case=='wrong_input_hash': target['binding']['inputs_sha256']='incorrect'
            elif case=='wrong_runtime': target['binding']['runtime']={}
            elif case=='wrong_manifest': target['binding']['manifest_digest']='incorrect'
            elif case=='wrong_member_hash': target['members_sha256']='incorrect'
            elif case=='missing_binding': target.pop('binding')
            elif case=='wrong_runner_hash': target['binding']['runner_sha256']='incorrect'
            for pop,obj in per.items(): (base/f's0_{pop}.json').write_text(json.dumps(obj))
            try:
                with contextlib.redirect_stdout(io.StringIO()): f['report'](str(inputs),str(base),str(base/'report.json'))
            except SystemExit as e:
                results[case]=dict(accepted=False,message=str(e))
            else:
                res=json.loads((base/'report.json').read_text())
                results[case]=dict(accepted=True,neighbourhoods=res['query']['neighbourhoods'])
            assert results[case]['accepted'] == (case in ('valid','wrong_runner_hash'))
    return dict(self_test_passed=True,positive_infinity_weights_rejected=True,ideal_boundary_limits_correct=True,
                report_cases=results,remaining_guard='report does not compare output binding.runner_sha256 to inputs bindings.helper_sha256[s0_info.py]; malformed runner provenance is accepted. No effect established on archived Stage 0 outputs.')


def main():
    files=['p1/p1_scan.json','p1/p1_pilot.json','p1/p1_bound.json','p1/p1_cost_projection.json','s0_info.py']
    result=dict(timestamp=datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),
                runtime=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
                source_sha256={p:sha(V2/p) for p in files},cost_replay=cost_replay(),stage0_reuse_fixtures=guard_fixtures())
    (HERE/'receipt.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result['cost_replay'].items() if k!='rows'},indent=2))
    print(json.dumps(result['stage0_reuse_fixtures'],indent=2))


if __name__=='__main__': main()
