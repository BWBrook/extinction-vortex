"""Independent completed A-power audit. Read via stdin on deep-server.
No production scorer imports, simulation, fitting or nearest-neighbour replay.
One CPU; file-at-a-time T reads and streamed bank hashing.
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

A = Path('/data/fable/vortex/v2_dev/a_power')
BASE = Path('/data/fable/vortex/kunanyi_run1/extract')
SRC = Path('/data/fable/vortex/kunanyi_stage/run1/src')
MANIFEST = SRC.parent/'validation_manifest.json'
MSHA = '96603037ec05036153f67b649757d067ca193c5e0a8610d3b855ef8f22139429'
N, R, K = 300, 2000, 2000
BLOCKS = {'MA_betamin': 5, 'MA_d10_0.5': 16}


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
    started = time.monotonic()
    assert sha(MANIFEST) == MSHA
    man = json.loads(MANIFEST.read_text())
    assert (man['K'],man['R']) == (K,R)
    od = json.loads((A/'a_power_outers.json').read_text())
    report = json.loads((A/'a_power_report.json').read_text())
    keys = {f'{b}/{i}' for b in BLOCKS for i in range(N)}
    assert set(od['outers']) == keys and od['manifest_digest'] == MSHA
    expected = {'K':K,'R_train':R,'R_test':R,'features':['msq','acf','inc','h1','h2'],
                'smoke':False,'seeds':{f'{b}/{i}':8000006200000+10000*num+i
                                      for b,num in BLOCKS.items() for i in range(N)}}
    assert od['settings'] == expected
    sources = {p:sha(SRC/p) for p in man['source_sha256']}
    assert sources == man['source_sha256']
    helpers = {p:sha(A.parent/p) for p in od['helper_sha256']}
    assert helpers == od['helper_sha256'] and len(helpers) == 5
    source_rows = {}
    source_hashes = {}
    for scenario in man['scenarios']:
        b = scenario['name']
        if b not in BLOCKS:
            continue
        for c in scenario['chunks']:
            if c['trial_ids'][0] >= N:
                continue
            p = BASE/c['dir']/'e2e_rows.jsonl'
            source_hashes[c['dir']] = sha(p)
            rows = [json.loads(line) for line in p.read_text().splitlines()]
            for row in rows:
                i = row['trial_id']; key = f'{b}/{i}'
                assert key not in source_rows and 0 <= i < N
                assert od['outers'][key]['dir'] == c['dir']
                source_rows[key] = row
    assert set(source_rows) == keys and source_hashes == od['source_rows_sha256']
    a_rows, nbr, metas = {}, {}, []
    compact = ['a_power_outers.json','a_power_report.json','timeline.txt']
    for slot in range(2):
        sd = A/f'slot{slot}'
        meta = json.loads((sd/'e2e_meta.json').read_text());metas.append(meta)
        assert meta['slot'] == slot and meta['nslots'] == 2 and meta['bank_verified']
        assert meta['outers_sha256'] == sha(A/'a_power_outers.json')
        assert meta['source_sha256'] == sources and meta['r_workers'] == 30
        compact.append(f'slot{slot}/e2e_meta.json')
        for b in BLOCKS:
            rel = f'slot{slot}/{b}/e2e_rows.jsonl';compact.append(rel)
            rows = [json.loads(line) for line in (A/rel).read_text().splitlines()]
            assert [r['trial_id'] for r in rows] == list(range(slot,N,2))
            for row in rows:
                key = f"{b}/{row['trial_id']}";assert key not in a_rows
                a_rows[key] = row
        with np.load(sd/'neighbours.npz') as npz:
            assert set(npz.files).isdisjoint(nbr)
            nbr.update({k:npz[k] for k in npz.files})
    assert metas[0] == metas[1] | {'slot':0}
    assert set(a_rows) == keys and len(nbr) == 2*N*9*4
    radii, ties = {}, {}
    for key,o in od['outers'].items():
        original = source_rows[key]
        assert o['recorded'] == {n:p['recorded'] for n,p in original['selected'].items()}
        assert o['recorded'] == {n:p['recorded'] for n,p in a_rows[key]['selected'].items()}
        assert len(o['recorded']) == 9
        assert o['v1'] == {k:original.get(k) for k in o['v1']}
        rr, tt = [],0
        for pop in o['recorded']:
            prefix = f'{key}/{pop}'
            ids = nbr[prefix]
            assert ids.shape == (K,) and len(np.unique(ids)) == K
            assert abs(round(float(nbr[prefix+'/kth'][0]),4)-json.loads(a_rows[key]['kth_dist'])[pop]) <= 1e-4
            radius = float(nbr[prefix+'/origC_max'][0]); assert np.isfinite(radius)
            rr.append(radius);tt += int(nbr[prefix+'/tie'][0])
        radii[key],ties[key] = max(rr),tt
    records,summary,thashes = {},{},{}
    differences,substitutions = {},{}
    for b in BLOCKS:
        records[b],summary[b],observed = {},{},{}
        differences[b],substitutions[b] = [],[]
        for arm,rows in [('V1',source_rows),('A',a_rows)]:
            arm_records = []
            for i in range(N):
                key = f'{b}/{i}';row = rows[key];o = od['outers'][key]
                directory = BASE/o['dir'] if arm == 'V1' else A/f'slot{i%2}'/b
                path = directory/f'T_{i}.csv';thashes[str(path)] = sha(path)
                try:
                    x = np.loadtxt(path,delimiter=',',skiprows=1)
                except ValueError:
                    x = np.genfromtxt(path,delimiter=',',skip_header=1)
                assert x.shape == (2*R+1,7) and np.array_equal(x[:,0],np.arange(2*R+1))
                assert x[:,6].sum() == row['fallback']
                T = x[:,1:5];train,test = T[1:R+1],T[R+1:]
                bad = ~np.isfinite(T).all(axis=1)
                assert np.array_equal(bad, x[:,5] == 1) and not bad[0]
                nf_train,nf_test = int(bad[1:R+1].sum()),int(bad[R+1:].sum())
                assert int(bad.sum()) == row['fit_failures']
                assert (nf_train,nf_test) == (row['train_fail'],row['test_fail'])
                assert nf_train <= .02*R
                if arm == 'A':
                    assert nf_train == nf_test == 0
                train = train[~bad[1:R+1]]
                mean,cov = train.mean(0),np.cov(train,rowvar=False,ddof=1)
                condition = float(np.linalg.cond(cov)); assert condition < 1e6
                centered = np.vstack([T[0],test])-mean
                distance = np.sum(centered*np.linalg.solve(cov,centered.T).T,axis=1)
                reference = distance[1:][~bad[R+1:]]
                exceed = int((reference >= distance[0]).sum())
                p_lo,p_hi = (1+exceed)/(R+1),(1+exceed+nf_test)/(R+1)
                outcome = 'reject' if p_hi < .05 else ('accept' if p_lo >= .05 else 'indet_straddle')
                assert (p_lo,p_hi) == (row['p_lo'],row['p_hi']) and outcome == row['outcome'],(key,arm)
                assert np.isclose(distance[0],row['D_obs'],rtol=1e-10,atol=1e-12)
                if arm == 'V1':
                    observed[i] = T[0]
                else:
                    delta = abs(T[0]-observed[i]);differences[b].append(delta)
                    assert max(delta) < 1e-8, (key,'observed T difference',delta)
                    cv = observed[i]-mean;dv = float(cv @ np.linalg.solve(cov,cv))
                    ev = int((reference >= dv).sum())
                    pv = ((1+ev)/(R+1),(1+ev+nf_test)/(R+1))
                    substitutions[b].append(pv == (p_lo,p_hi))
                    assert pv == (p_lo,p_hi),(key,'stored observed T changes p')
                z = (T[0]-mean)/train.std(0,ddof=1)
                arm_records.append({'trial':i,'p_lo':p_lo,'p_hi':p_hi,'outcome':outcome,'D_obs':float(distance[0]),
                                    'condition':condition,'z':z.tolist(),'fallbacks':row['fallback'],
                                    'train_fail':nf_train,'test_fail':nf_test})
            records[b][arm] = arm_records
            counts = dict(Counter(r['outcome'] for r in arm_records));k = counts['reject']
            Z = np.array([r['z'] for r in arm_records])
            support = [radii[f'{b}/{i}'] if arm == 'A' else max(json.loads(rows[f'{b}/{i}']['kth_dist']).values()) for i in range(N)]
            summary[b][arm] = {'outcomes':counts,'exact_95':cp(k,N),'mean_z':Z.mean(0).tolist(),
                               'sd_z':Z.std(0,ddof=1).tolist(),'fallback_mean':float(np.mean([r['fallbacks'] for r in arm_records])),
                               'train_failures':sum(r['train_fail'] for r in arm_records),
                               'test_failures':sum(r['test_fail'] for r in arm_records),
                               'max_condition':max(r['condition'] for r in arm_records),
                               'original_C_max_radius_q10_50_90':np.quantile(support,[.1,.5,.9]).tolist()}
            published = report['blocks'][b]
            assert k == published['detections'][arm]
            assert np.round(cp(k,N),4).tolist() == published['exact_95'][arm]
            assert np.round(Z.mean(0),3).tolist() == published['mean_z_T1_T4'][arm]
            assert np.round(np.quantile(support,[.1,.5,.9]),4).tolist() == published['origC_max_kth_q10_50_90'][arm]
            print(f'{b}/{arm}: {k}/{N} reject; all T rows checked',file=sys.stderr,flush=True)
        v = np.array([r['outcome']=='reject' for r in records[b]['V1']])
        a = np.array([r['outcome']=='reject' for r in records[b]['A']])
        table = [int((v&a).sum()),int((v&~a).sum()),int((~v&a).sum()),int((~v&~a).sum())]
        _,vc,ac,_ = table
        mp = float(binomtest(min(vc,ac),vc+ac,.5).pvalue); interval = method10(*table)
        pub = report['blocks'][b]
        assert table == pub['table_both_V1_only_A_only_neither']
        assert mp == pub['mcnemar_exact_p'] and interval == pub['paired_difference_95_newcombe10']
        assert round((ac-vc)/N,4) == pub['paired_difference_A_minus_V1']
        summary[b]['paired'] = {'table':table,'difference':(ac-vc)/N,'interval_method10':interval,'mcnemar_exact_p':mp}
        summary[b]['boundary_ties'] = sum(ties[f'{b}/{i}'] for i in range(N))
        summary[b]['paired_observed_T_max_absolute_difference'] = np.max(differences[b],axis=0).tolist()
        summary[b]['baseline_observed_T_preserves_all_A_p'] = all(substitutions[b])
    bank_hashes = {name:sha(BASE/man['bankdir']/name) for name in man['bank_sha256']}
    assert bank_hashes == man['bank_sha256']
    print(f'All {len(bank_hashes)} frozen bank files match',file=sys.stderr,flush=True)
    out = {'scope':'Independent completed A-power rescoring and present-payload provenance, no production scorer imports.',
           'time_hobart':datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),
           'reviewed_commit':'20c85745f417c093b22743a304d0521c962cd986',
           'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
           'manifest_sha256':MSHA,'source_sha256':sources,'helper_sha256':helpers,
           'small_input_sha256':{p:sha(A/p) for p in compact},'source_rows_sha256':source_hashes,
           'T_sha256':thashes,'neighbour_sha256':{f'slot{s}/neighbours.npz':sha(A/f'slot{s}'/'neighbours.npz') for s in range(2)},
           'bank_files_matched':len(bank_hashes),'bank_sha256':bank_hashes,
           'matched_outer_population_records':2*N*9,'unique_neighbour_sets':2*N*9,
           'summary':summary,'trials':records,'wall_seconds':round(time.monotonic()-started,2),
           'limits':['No generation, fitting or nearest-neighbour reconstruction replay.',
                     'Original-C distances checked against saved receipts, not rebuilt independently.',
                     'Hashes verify inspected payloads, not absence of intervening mutation or restart.',
                     'Completed no-shrinkage branch; baseline fit failures use complete training rows and fixed-denominator p bounds.',
                     'Exposed development cases at two effects; no prospective validation or empirical inference.']}
    print(json.dumps(out,allow_nan=False))


if __name__ == '__main__':
    main()
