"""Independent D3 result audit, executed on deep-server via stdin.

Reads completed synthetic T files and receipts. No production scorer imports,
bank/tree construction, simulation or fitting. One CPU, bounded file-at-a-time
memory. JSON goes to stdout; only the caller saves the audit receipt.
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

BASE = Path('/data/fable/vortex/v2_dev/d3')
SRC = Path('/data/fable/vortex/kunanyi_stage/run1/src')
MANIFEST = SRC.parent / 'validation_manifest.json'
MANIFEST_SHA = '96603037ec05036153f67b649757d067ca193c5e0a8610d3b855ef8f22139429'
LAUNCH_SHA = '675bd8f24fd8e051d2f5245f929c8ea12e6967116513e9fbd7a4fbe5fcf3c89e'
R, K, N = 2000, 2000, 200


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def cp(k, n):
    return [float(beta.ppf(.025, k, n-k+1)) if k else 0.,
            float(beta.ppf(.975, k+1, n-k)) if k < n else 1.]


def method10(a, b, c, d):
    # Independent transcription checked against published Table III in the prior review.
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
    width_lo = np.sqrt(max(lower[0]**2+upper[1]**2-2*phi*lower[0]*upper[1], 0))
    width_hi = np.sqrt(max(upper[0]**2+lower[1]**2-2*phi*upper[0]*lower[1], 0))
    delta = p[0]-p[1]
    return np.round([-delta-width_hi, -delta+width_lo], 4).tolist()


def main():
    started = time.monotonic()
    assert sha(MANIFEST) == MANIFEST_SHA
    manifest = json.loads(MANIFEST.read_text())
    assert manifest['K'] == K and manifest['R'] == R
    fixed = next(s for s in manifest['scenarios'] if s['name'] == 'null_low_s')['spec']['fixed']
    outers = json.loads((BASE/'outers.json').read_text())
    oracle = json.loads((BASE/'oracle/oracle_meta.json').read_text())
    report = json.loads((BASE/'d3_report.json').read_text())
    z_report = json.loads((BASE/'d3_report_z.json').read_text())
    assert outers['theta'] == fixed == oracle['theta']
    assert outers['manifest_digest'] == MANIFEST_SHA and outers['budget'] == manifest['budget']
    assert len(outers['outers']) == N and [o['trial'] for o in outers['outers']] == list(range(N))
    assert not oracle['stop'] and not oracle['extended']
    assert all(value >= 20000 for value in oracle['retained'].values())
    assert len(oracle['tasks']) == 180
    assert len({t['seed'] for t in oracle['tasks']}) == 180
    for n, count in oracle['retained'].items():
        assert sum(t['selected'] for t in oracle['tasks'] if t['population'] == n) == count
        assert sorted(t['shard'] for t in oracle['tasks'] if t['population'] == n) == list(range(20))
    for o in outers['outers']:
        assert set(o['selected']) == set(fixed)
        for n, selected in o['selected'].items():
            assert selected is not None and selected['params'] == fixed[n]
            assert selected['draws'] <= manifest['budget']
    assert (BASE/'runner_sha256.txt').read_text().split()[0] == LAUNCH_SHA
    source_hashes = {p: sha(SRC/p) for p in manifest['source_sha256']}
    assert source_hashes == manifest['source_sha256']
    small_files = ['outers.json', 'oracle/oracle_meta.json', 'd3_report.json', 'd3_report_z.json',
                   'V/e2e_meta.json', 'V/e2e_rows.jsonl', 'O/e2e_meta.json', 'O/e2e_rows.jsonl',
                   'timeline.txt', 'runner_sha256.txt', 'bank.log']
    input_hashes = {p: sha(BASE/p) for p in small_files}
    records, summaries, all_t_hashes, obs_T = {}, {}, {}, {}
    for arm, stream in [('V', 8000003010000), ('O', 8000003020000)]:
        meta = json.loads((BASE/arm/'e2e_meta.json').read_text())
        logged = [json.loads(line) for line in (BASE/arm/'e2e_rows.jsonl').read_text().splitlines()]
        assert len(logged) == N and [r['trial_id'] for r in logged] == list(range(N))
        assert meta['manifest_digest'] == MANIFEST_SHA
        assert meta['outers_sha256'] == sha(BASE/'outers.json')
        assert meta['source_sha256'] == source_hashes
        assert (meta['K'], meta['R_train'], meta['R_test'], meta['seed_base']) == (K,R,R,stream)
        if arm == 'O':
            assert meta['oracle_meta_sha256'] == sha(BASE/'oracle/oracle_meta.json')
        arm_rows, arm_z = [], []
        for row, outer in zip(logged, outers['outers']):
            tid = row['trial_id']
            assert {n: p['recorded'] for n,p in row['selected'].items()} == {
                n: p['recorded'] for n,p in outer['selected'].items()}
            path = BASE/arm/f'T_{tid}.csv'
            all_t_hashes[f'{arm}/T_{tid}.csv'] = sha(path)
            values = np.loadtxt(path, delimiter=',', skiprows=1)
            assert values.shape == (2*R+1,7) and np.array_equal(values[:,0], np.arange(2*R+1))
            assert np.isfinite(values).all(), (arm,tid,'nonfinite')
            assert not values[:,5].any(), (arm,tid,'fit failure')
            assert row['fit_failures'] == row['train_fail'] == row['test_fail'] == 0
            assert values[:,6].sum() == row['fallback']
            T = values[:,1:5]
            train, test = T[1:R+1], T[R+1:]
            mean = train.mean(0)
            cov = np.cov(train, rowvar=False, ddof=1)
            condition = float(np.linalg.cond(cov))
            assert condition < 1e6, (arm,tid,'shrinkage would require separate audit')
            centred = np.vstack([T[0], test])-mean
            distances = np.sum(centred*np.linalg.solve(cov,centred.T).T,axis=1)
            assert np.isfinite(distances).all()
            p = (1+int((distances[1:] >= distances[0]).sum()))/(R+1)
            outcome = 'reject' if p < .05 else 'accept'
            assert p == row['p_lo'] == row['p_hi'] and outcome == row['outcome'], (arm,tid)
            assert np.isclose(distances[0],row['D_obs'],rtol=1e-10,atol=1e-12)
            z = (T[0]-mean)/train.std(0,ddof=1)
            assert np.allclose(z,z_report[arm][tid],rtol=0,atol=5.01e-6)
            if arm == 'V':
                obs_T[tid] = T[0]
            else:
                assert np.array_equal(T[0],obs_T[tid]), ('paired observed statistics',tid)
            arm_z.append(z)
            arm_rows.append({'trial': tid, 'outcome': outcome, 'p': p,
                             'D_obs': float(distances[0]), 'condition': condition,
                             'z': z.tolist(), 'fallbacks': row['fallback'],
                             'max_radius_logged': max(json.loads(row['kth_dist']).values())})
        records[arm] = arm_rows
        counts = Counter(r['outcome'] for r in arm_rows)
        rejections = counts['reject']
        Z = np.array(arm_z)
        summaries[arm] = {'outcomes': dict(counts), 'nonaccepts': rejections, 'exact_95': cp(rejections,N),
                          'z_mean': Z.mean(0).tolist(), 'z_sd': Z.std(0,ddof=1).tolist(),
                          'max_condition': max(r['condition'] for r in arm_rows),
                          'fit_failures': 0, 'training_rows_per_trial': R,
                          'max_radius_q10_50_90': np.quantile([r['max_radius_logged'] for r in arm_rows],[.1,.5,.9]).tolist()}
        assert report['outcomes'][arm] == dict(counts)
        assert report['nonaccepts'][arm] == rejections
        assert report['exact_95'][arm] == np.round(cp(rejections,N),4).tolist()
        assert report['z_T1_T4'][arm]['mean'] == np.round(Z.mean(0),3).tolist()
        assert report['z_T1_T4'][arm]['sd'] == np.round(Z.std(0,ddof=1),3).tolist()
        assert report['max_kth_q10_50_90'][arm] == np.round(summaries[arm]['max_radius_q10_50_90'],4).tolist()
        print(f'{arm}: all 200 T files rescored; {rejections}/200 reject',file=sys.stderr,flush=True)
    v = np.array([r['outcome']=='reject' for r in records['V']])
    o = np.array([r['outcome']=='reject' for r in records['O']])
    table = [int((v&o).sum()),int((v&~o).sum()),int((~v&o).sum()),int((~v&~o).sum())]
    a,b,c,d = table
    mp = float(binomtest(min(b,c),b+c,.5).pvalue)
    interval = method10(a,b,c,d)
    assert table == report['table_both_V_only_O_only_neither']
    assert mp == report['mcnemar_exact_p'] and interval == report['paired_difference_95_newcombe10']
    assert (c-b)/N == report['paired_difference_O_minus_V']
    archive_hashes = {f'{a}/{p}': sha(BASE/a/p) for a in ['V','O']
                      for p in ['neighbours.npz','neighbour_draw_ids.npz']}
    for arm in ['V','O']:
        assert archive_hashes[f'{arm}/neighbour_draw_ids.npz'] == report['checks']['neighbour_reconciliation'][arm]['draw_id_archive_sha256']
    # Stream hashes of new oracle shards, without opening their arrays or rebuilding trees.
    oracle_hashes = {name: sha(BASE/'oracle'/name) for name in report['checks']['oracle_shard_sha256']}
    assert len(oracle_hashes) == 180 and oracle_hashes == report['checks']['oracle_shard_sha256']
    result = {'scope': 'Independent complete synthetic D3 T-file rescoring and identity audit; no production scorer imports.',
              'time_hobart': datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),
              'reviewed_commit': '7b41881c8b73f70b64a915d0957e1ea2f308c114',
              'runtime': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__},
              'manifest_sha256': MANIFEST_SHA, 'launch_runner_receipt_sha256': LAUNCH_SHA,
              'source_hashes_match_manifest': True, 'source_sha256': source_hashes,
              'small_input_sha256': input_hashes, 'T_sha256': all_t_hashes,
              'neighbour_archive_sha256': archive_hashes, 'oracle_shards_matched': len(oracle_hashes),
              'outer_and_oracle_theta_match_frozen_corner': True, 'sampling_failures': 0,
              'oracle_support_counts_reconcile': oracle['retained'], 'oracle_extension': oracle['extended'],
              'summaries': summaries, 'table_both_V_only_O_only_neither': table,
              'paired_difference_O_minus_V': (c-b)/N, 'mcnemar_exact_p': mp,
              'paired_difference_95_method10': interval, 'trials': records,
              'wall_seconds': round(time.monotonic()-started,2),
              'limits': ['No population generation, reference draw, fitting or nearest-neighbour reconstruction replay.',
                         'Primary bank files were not rehashed in this audit; frozen manifest and current source bindings were checked.',
                         'Oracle and neighbour archive identity checked against reported hashes, not against a pre-launch seal.',
                         'An absence of duplicate rows does not independently prove there was no restart.',
                         'R/nlme versions are report-time receipts, not launch-time environment attestations.',
                         'Current no-failure/no-shrinkage cases verified; this audit does not exercise those alternative scoring branches.',
                         'This is a development diagnostic at one fixed nuisance corner, not prospective validation.']}
    print(json.dumps(result,allow_nan=False))


if __name__ == '__main__':
    main()
