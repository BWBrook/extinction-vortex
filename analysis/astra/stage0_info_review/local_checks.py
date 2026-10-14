"""Independent Stage 0 local binding and tiny implementation fixtures.

Run from the repository with OPENBLAS_NUM_THREADS=1 and the existing
/home/bwbrook/papers/dsipa-dev/.venv/bin/python. Reads the remote audit receipt;
imports only selected numerical/report functions via AST, never bank code.
"""
import ast
import contextlib
from datetime import datetime
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import tempfile
from zoneinfo import ZoneInfo

import numpy as np
import scipy
from scipy import stats
from scipy.special import expit, xlog1py, xlogy

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
V2 = ROOT / 'analysis/fable/calibration/v2_dev'
RUNNER = V2 / 's0_info.py'
SCEN = ('null_prior_predictive', 'null_low_s', 'MA_betamin', 'MA_d10_0.5')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def functions():
    wanted = {'sha', 'cell', 'rate_functionals', 'logw_noisy', 'logw_ideal', 'weight_stats', 'self_test', 'report'}
    tree = ast.parse(RUNNER.read_text())
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in wanted]
    assert len(nodes) == len(wanted)
    x, w = np.polynomial.hermite_e.hermegauss(40)
    ns = dict(np=np, stats=stats, hashlib=hashlib, json=json, os=os, SCEN=SCEN, NS=(30,300), ESS_FLAG=100,
              GH_X=x, GH_W=w/w.sum())
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(RUNNER), 'exec'), ns)
    return ns


def numerical_fixture(f):
    f['self_test']()
    sb, fb = np.array([.05,.25,.65,.95]), np.array([.02,.2,.6,1.7])
    checks = []
    for n,k,r in [(30,0,0),(30,30,1),(300,213,117)]:
        logw = xlogy(k,sb)+xlog1py(n-k,-sb)+xlogy(r,fb)-n*fb
        w = np.exp(logw-logw.max()); w /= w.sum()
        result = f['weight_stats'](f['logw_noisy'](sb,fb,n,k,r))
        checks.append(max(abs(result['ess']-1/np.dot(w,w)),abs(result['max_share']-w.max())))
    logw = xlogy(300*.7,sb)+xlog1py(300*(1-.7),-sb)+xlogy(300*.3,fb)-300*fb
    ideal_error = float(np.max(np.abs(logw-f['logw_ideal'](sb,fb,300,.7,.3))))
    assert max(checks) < 1e-10 and ideal_error < 1e-10
    # Exercise implementation edge cases not covered by the earlier independent
    # mathematical examples. These are dormant for valid interior bank rates.
    with np.errstate(over='ignore', invalid='ignore'):
        positive_inf = f['weight_stats'](np.array([0.,np.inf]))
    assert positive_inf == dict(usable=True,ess=1.,max_share=1.)
    endpoint = f['logw_ideal'](np.array([0.,1.]),np.array([0.,0.]),30,0.,0.)
    assert np.isnan(endpoint).all()
    intended = xlogy(0,np.array([0.,1.]))+xlog1py(30,-np.array([0.,1.]))+xlogy(0,np.array([0.,0.]))
    assert intended[0] == 0 and np.isneginf(intended[1])
    return dict(production_self_test_passed=True, finite_noisy_fixture_cases=len(checks),
                maximum_ess_or_share_error=max(checks), ideal_logweight_error=ideal_error,
                mixed_positive_inf_observed=positive_inf,
                ideal_zero_true_and_candidate_rates_return_nan=True,
                edge_case_scope='Malformed +inf weights and exact zero/one model rates; no observed invalid or boundary rates established in the completed finite summaries.')


def report_fixture(f, bind):
    """No fabricated results escape the temp directory; save observations only."""
    with tempfile.TemporaryDirectory(prefix='s0-report-contract-') as temp:
        path = Path(temp)
        bad_bind = dict(bind, runtime={'python':'changed'}, helper_sha256={'s0_info.py':'changed'})
        inputs = path/'inputs.json'
        inputs.write_text(json.dumps({'bindings':bad_bind}))
        rows=[]
        for scenario in SCEN:
            for i in range(200):
                if scenario == SCEN[0] and i == 199:
                    continue
                row = dict(outer=f'{scenario}/{i}',kth=0.1,kth_mismatch=False,tie=False)
                for kind in ('noisy_30','ideal_30','noisy_300','ideal_300'):
                    row[kind] = dict(usable=True,ess=2000.,max_share=.0005)
                rows.append(row)
        for pop in bind['population_order']:
            (path/f's0_{pop}.json').write_text(json.dumps(dict(population='wrong',seconds=0,peak_rss_gb=0,
                                                             bank_rows=2000,members_sha256='missing',rows=rows)))
        out=path/'result.json'
        with contextlib.redirect_stdout(io.StringIO()):
            f['report'](str(inputs),str(path),str(out))
        report=json.loads(out.read_text())
        assert report['cells']['0']['noisy']['datasets'] == 199
        assert report['query']['neighbourhoods'] == 7191
        assert report['bindings']['runtime'] == {'python':'changed'}
        assert report['bindings']['helper_sha256']['s0_info.py'] == 'changed'
        return dict(report_accepted_all_populations_missing_same_outer=True,
                    observed_cell0_denominator=199,observed_neighbourhood_count=7191,
                    changed_helper_and_runtime_bindings_accepted=True,
                    wrong_population_labels_and_absent_member_payloads_accepted=True,
                    impact='Reuse guard failure; independent checks show the completed report has exactly 200 unique complete outers per cell and matching artifact hashes.')


def main():
    remote=json.loads((HERE/'remote_audit.json').read_text())
    inputs=json.loads((V2/'s0/s0_inputs.json').read_text())
    for name,expected in [('s0_inputs.json',remote['inputs_sha256']),('s0_report.json',remote['report_sha256'])]:
        assert sha(V2/'s0'/name) == expected
    assert sha(RUNNER) == remote['runner_sha256']
    assert sha(ROOT/'analysis/fable/calibration/freeze_v1/validation_manifest.json') == remote['manifest_sha256']
    listed={}
    for line in (V2/'s0/full_outputs_sha256.txt').read_text().splitlines():
        if line.strip():
            h,name=line.split()
            listed[name]=h
    assert listed == remote['raw_sha256'] | remote['member_sha256']
    launch='1f82fe4'
    launch_hashes={}
    for rel in ['analysis/fable/calibration/v2_dev/s0_info.py','analysis/fable/calibration/v2_dev/s0/s0_inputs.json']:
        content=subprocess.check_output(['git','show',f'{launch}:{rel}'],cwd=ROOT)
        launch_hashes[rel]=hashlib.sha256(content).hexdigest()
        assert launch_hashes[rel] == sha(ROOT/rel)
    pops=inputs['bindings']['population_order']
    prior={p:{} for p in pops}
    prior_path=V2/'d1c2_trials.jsonl.gz'
    with gzip.open(prior_path,'rt') as fh:
        for line in fh:
            row=json.loads(line)
            if row['block'] not in SCEN[:2] or row['trial_id'] not in range(200):
                continue
            key=f"{row['block']}/{row['trial_id']}"
            for p in pops:
                assert key not in prior[p]
                prior[p][key]=row['pop'][p]['nbr']
    digest={p:object_sha(prior[p]) for p in pops}
    assert all(len(v)==400 for v in prior.values())
    assert digest == remote['null_member_digest_sha256']
    f=functions()
    old=ROOT/'analysis/astra/artifact_review_20261014/info_checks.json'
    prior_numeric=json.loads(old.read_text())['numerical_fixtures']
    result=dict(timestamp=datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),
                runtime=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
                head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                remote_receipt_sha256=sha(HERE/'remote_audit.json'),
                committed_raw_and_member_hash_matches=len(listed),local_and_remote_inputs_report_runner_manifest_match=True,
                pre_weight_commit=launch,pre_weight_commit_hashes=launch_hashes,
                d1c2_file_sha256=sha(prior_path),null_neighbourhood_digest_matches=3600,
                null_member_digest_sha256=digest,
                reuse_previous_quadrature_receipt=dict(path=str(old.relative_to(ROOT)),sha256=sha(old),
                    cases=prior_numeric['GH40_vs_adaptive_quad_cases'],max_absolute_error=prior_numeric['GH40_max_absolute_error']),
                actual_helper_fixtures=numerical_fixture(f),report_contract_fixture=report_fixture(f,inputs['bindings']))
    (HERE/'local_checks.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result,indent=2,allow_nan=False))


if __name__=='__main__':
    main()
