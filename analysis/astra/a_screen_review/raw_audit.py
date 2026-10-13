"""Read-only, independent completed A-screen audit; run via stdin on deep-server.

No production imports, simulation, fits or tree construction. Reads one synthetic
T file at a time and streams hashes. Save stdout as the audit receipt.
"""
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import platform
import sys
import time
from zoneinfo import ZoneInfo
import numpy as np
import scipy
from scipy.stats import beta, binomtest

A = Path('/data/fable/vortex/v2_dev/a_screen')
BASE = Path('/data/fable/vortex/kunanyi_run1/extract')
SRC = Path('/data/fable/vortex/kunanyi_stage/run1/src')
MANIFEST = SRC.parent / 'validation_manifest.json'
MSHA = '96603037ec05036153f67b649757d067ca193c5e0a8610d3b855ef8f22139429'
N, R, K, SEED = 200, 2000, 2000, 8000006100000


def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def cp(k, n):
    return [float(beta.ppf(.025, k, n-k+1)) if k else 0.,
            float(beta.ppf(.975, k+1, n-k)) if k < n else 1.]


def method10(a, b, c, d):
    # Independent transcription checked against Newcombe Table III in prior audit.
    n = a+b+c+d
    z = 1.959964
    p = np.array([a+b, a+c], dtype=float)/n
    centre = (p+z*z/(2*n))/(1+z*z/n)
    half = z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    lower, upper = p-(centre-half), centre+half-p
    num = a*d-b*c
    if num > 0:
        num = max(num-n/2, 0)
    den = np.sqrt(float((a+b)*(c+d)*(a+c)*(b+d)))
    phi = num/den if den else 0.
    lo = np.sqrt(max(lower[0]**2+upper[1]**2-2*phi*lower[0]*upper[1], 0))
    hi = np.sqrt(max(upper[0]**2+lower[1]**2-2*phi*upper[0]*lower[1], 0))
    delta = p[1]-p[0]
    return np.round([delta-hi, delta+lo], 4).tolist()


def main():
    start = time.monotonic()
    assert sha(MANIFEST) == MSHA
    man = json.loads(MANIFEST.read_text())
    assert (man['K'], man['R']) == (K, R)
    report = json.loads((A/'a_screen_report.json').read_text())
    outer = json.loads((A/'a_outers.json').read_text())
    assert outer['manifest_digest'] == MSHA and outer['block'] == 'null_low_s'
    assert [o['trial'] for o in outer['outers']] == list(range(N))
    source_hash = {p: sha(SRC/p) for p in man['source_sha256']}
    assert source_hash == man['source_sha256']
    source_rows = {}
    for d, h in outer['source_rows_sha256'].items():
        p = BASE/d/'e2e_rows.jsonl'
        assert sha(p) == h
        rows = [json.loads(l) for l in p.read_text().splitlines()]
        assert len(rows) == 100 and len({r['trial_id'] for r in rows}) == 100
        for row in rows:
            assert row['trial_id'] not in source_rows
            source_rows[row['trial_id']] = row
    assert sorted(source_rows) == list(range(N))
    a_rows, nbr = {}, {}
    compact_names = ['a_screen_report.json','a_outers.json','runner_sha256.txt','timeline.txt']
    for s in range(2):
        d = A/f'slot{s}'
        meta = json.loads((d/'e2e_meta.json').read_text())
        assert meta == report['bindings'] | {'slot': s}
        assert (meta['K'], meta['R_train'], meta['R_test'], meta['seed_base']) == (K,R,R,SEED)
        assert meta['source_sha256'] == source_hash and meta['manifest_digest'] == MSHA
        assert meta['outers_sha256'] == sha(A/'a_outers.json') and not meta['smoke']
        rows = [json.loads(l) for l in (d/'e2e_rows.jsonl').read_text().splitlines()]
        assert [r['trial_id'] for r in rows] == list(range(s,N,2))
        for row in rows:
            a_rows[row['trial_id']] = row
        with np.load(d/'neighbours.npz') as npz:
            assert set(npz.files).isdisjoint(nbr)
            nbr.update({k: npz[k] for k in npz.files})
        compact_names.extend([f'slot{s}/e2e_meta.json',f'slot{s}/e2e_rows.jsonl'])
    assert sorted(a_rows) == list(range(N))
    runner_hashes = {}
    for line in (A/'runner_sha256.txt').read_text().splitlines():
        h, p = line.split()
        assert sha(Path(p)) == h
        runner_hashes[p] = h
    assert report['bindings']['runner_sha256'] == runner_hashes[str(A.parent/'a_screen.py')]
    records, summaries, T_hash, obs_T = {}, {}, {}, {}
    obs_delta, replacement_p_equal = [], []
    support, ties = [], 0
    for o in outer['outers']:
        i = o['trial']
        row = source_rows[i]
        assert o['recorded'] == {n:p['recorded'] for n,p in row['selected'].items()}
        assert o['recorded'] == {n:p['recorded'] for n,p in a_rows[i]['selected'].items()}
        assert o['v1'] == {k: row.get(k) for k in o['v1']}
        assert all(p['params'] for p in row['selected'].values())
        radii = []
        for n in o['recorded']:
            key = f'{i}/{n}'
            ids = nbr[key]
            assert ids.shape == (K,) and len(np.unique(ids)) == K
            assert abs(round(float(nbr[key+'/kth'][0]),4)-json.loads(a_rows[i]['kth_dist'])[n]) <= 1e-4
            assert np.isfinite(nbr[key+'/origC_max']).all()
            radii.append(float(nbr[key+'/origC_max'][0]))
            ties += int(nbr[key+'/tie'][0])
        support.append(max(radii))
    assert len(nbr) == N*9*4
    for arm, rows in [('V1',source_rows),('A',a_rows)]:
        out = []
        for i in range(N):
            row = rows[i]
            path = (BASE/outer['outers'][i]['dir'] if arm == 'V1' else A/f'slot{i%2}')/f'T_{i}.csv'
            T_hash[str(path)] = sha(path)
            values = np.loadtxt(path,delimiter=',',skiprows=1)
            assert values.shape == (2*R+1,7) and np.array_equal(values[:,0], np.arange(2*R+1))
            assert np.isfinite(values).all() and not values[:,5].any()
            assert row['fit_failures'] == row['train_fail'] == row['test_fail'] == 0
            assert values[:,6].sum() == row['fallback']
            T = values[:,1:5]
            train, test = T[1:R+1],T[R+1:]
            mean, cov = train.mean(0), np.cov(train,rowvar=False,ddof=1)
            condition = float(np.linalg.cond(cov))
            assert condition < 1e6
            centered = np.vstack([T[0],test])-mean
            distance = np.sum(centered*np.linalg.solve(cov,centered.T).T,axis=1)
            p = (1+int((distance[1:] >= distance[0]).sum()))/(R+1)
            outcome = 'reject' if p < .05 else 'accept'
            assert p == row['p_lo'] == row['p_hi'] and outcome == row['outcome']
            assert np.isclose(distance[0],row['D_obs'],rtol=1e-10,atol=1e-12)
            if arm == 'V1':
                obs_T[i] = T[0]
            else:
                # Refits have tiny numerical differences; quantify and test their effect.
                # 1e-8 guard chosen after first inspection (observed max 1.20e-10).
                delta = np.abs(T[0]-obs_T[i])
                assert np.max(delta) < 1e-8
                obs_delta.append(delta)
                cv = obs_T[i]-mean
                dv = float(cv @ np.linalg.solve(cov,cv))
                pv = (1+int((distance[1:] >= dv).sum()))/(R+1)
                assert pv == p
                replacement_p_equal.append(pv == p)
            z = (T[0]-mean)/train.std(0,ddof=1)
            out.append({'trial':i,'outcome':outcome,'p':p,'D_obs':float(distance[0]),
                        'condition':condition,'z':z.tolist(),'fallbacks':row['fallback']})
        records[arm] = out
        counts = dict(Counter(r['outcome'] for r in out))
        z = np.array([r['z'] for r in out])
        support_arm = support if arm == 'A' else [max(json.loads(rows[i]['kth_dist']).values()) for i in range(N)]
        summaries[arm] = {'outcomes':counts,'exact_95':cp(counts['reject'],N),
                          'z_mean':z.mean(0).tolist(),'z_sd':z.std(0,ddof=1).tolist(),
                          'fallback_mean':float(np.mean([r['fallbacks'] for r in out])),
                          'max_condition':max(r['condition'] for r in out),
                          'original_C_max_radius_q10_50_90':np.quantile(support_arm,[.1,.5,.9]).tolist()}
        assert counts['reject'] == report['nonaccepts'][arm]
        assert np.round(summaries[arm]['exact_95'],4).tolist() == report['exact_95'][arm]
        assert np.round(z.mean(0),3).tolist() == report['mean_z_T1_T4'][arm]
        assert np.round(summaries[arm]['original_C_max_radius_q10_50_90'],4).tolist() == report['origC_max_kth_q10_50_90'][arm]
        print(f'{arm}: all 200 files verified; {counts}',file=sys.stderr,flush=True)
    v = np.array([r['outcome']=='reject' for r in records['V1']])
    a = np.array([r['outcome']=='reject' for r in records['A']])
    table = [int((v&a).sum()),int((v&~a).sum()),int((~v&a).sum()),int((~v&~a).sum())]
    _,b,c,_ = table
    mp = float(binomtest(min(b,c),b+c,.5).pvalue)
    interval = method10(*table)
    assert table == report['table_both_V1_only_A_only_neither']
    assert mp == report['mcnemar_exact_p'] and interval == report['paired_difference_95_newcombe10']
    assert (c-b)/N == report['paired_difference_A_minus_V1'] and ties == report['boundary_ties_A']
    bank_hash = {name:sha(BASE/man['bankdir']/name) for name in man['bank_sha256']}
    assert bank_hash == man['bank_sha256']
    print(f'All {len(bank_hash)} primary-bank hashes match',file=sys.stderr,flush=True)
    result = {'time_hobart':datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),
              'reviewed_commit':'1fe79ea9c5e605947544ba362b476a5b0f2f8c84',
              'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
              'manifest_sha256':MSHA,'source_sha256':source_hash,'runner_sha256':runner_hashes,
              'small_input_sha256':{p:sha(A/p) for p in compact_names},
              'T_sha256':T_hash,'neighbour_sha256':{f'slot{s}/neighbours.npz':sha(A/f'slot{s}'/'neighbours.npz') for s in range(2)},
              'primary_bank_files_matched':len(bank_hash),'bank_sha256':bank_hash,
              'matched_outer_population_records':N*9,'complete_unique_neighbour_sets':N*9,
              'paired_T_max_abs_difference_by_statistic':np.max(obs_delta,axis=0).tolist(),
              'v1_observed_T_substitution_preserves_all_A_p_values':all(replacement_p_equal),
              'summaries':summaries,'table_both_V1_only_A_only_neither':table,
              'paired_difference_A_minus_V1':(c-b)/N,'paired_difference_95_method10':interval,
              'mcnemar_exact_p':mp,'boundary_ties_A':ties,'trials':records,
              'wall_seconds':round(time.monotonic()-start,2),
              'limits':['No simulation, fitting or nearest-neighbour reconstruction replay.',
                        'Neighbour IDs checked for count/uniqueness and receipt identity, not independently rebuilt.',
                        'Hash checks verify present payloads, not absence of intervening mutation.',
                        'Completed no-failure/no-shrinkage cases only; latent branches reviewed separately.',
                        'Exposed development comparison at one corner, not prospective validation.']}
    print(json.dumps(result,allow_nan=False))


if __name__ == '__main__':
    main()
