"""Independent completed-v1 audit, run on deep-server via stdin; no production imports.

Reads the sealed archive and extracted files, recalculates all trial scores from T,
and emits a JSON audit. Four bounded CPU processes; no fitting or simulation/writes.
"""
import hashlib
import json
import math
import multiprocessing as mp
from pathlib import Path
import sys
import tarfile
import time

import numpy as np
from scipy.stats import beta as beta_dist

BASE = Path('/data/fable/vortex/kunanyi_run1')
EXTRACT = BASE / 'extract'
MANIFEST = Path('/data/fable/vortex/production_banks_20261010T081726Z/validation_manifest_v2.json')
ARCHIVE_SHA = '312d91e4f52b9e973a313f2242752ac013e35c827ef9d6a21a25c240f3a507f1'
MANIFEST_SHA = '96603037ec05036153f67b649757d067ca193c5e0a8610d3b855ef8f22139429'
BINS = np.array([.2050, .2956, .4049, .5613])


def digest(path):
    with open(path, 'rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def sha_stream(stream):
    h = hashlib.sha256()
    for b in iter(lambda: stream.read(4 << 20), b''):
        h.update(b)
    return h.hexdigest()


def cp(k, n, alpha):
    return [float(beta_dist.ppf(alpha / 2, k, n - k + 1)) if k else 0.,
            float(beta_dist.ppf(1 - alpha / 2, k + 1, n - k)) if k < n else 1.]


def calculate(t, R):
    observed, train, test = t[0], t[1:R+1], t[R+1:]
    good = np.isfinite(train).all(axis=1)
    result = {'train_fail': int((~good).sum()), 'test_fail': int((~np.isfinite(test).all(axis=1)).sum())}
    if not np.isfinite(observed).all():
        return result | {'outcome': 'indet_obsfit'}
    if result['train_fail'] > math.floor(.02 * R):
        return result | {'outcome': 'indet_train'}
    z = train[good]
    mean = z.mean(axis=0)
    covariance = np.cov(z, rowvar=False)
    condition = float(np.linalg.cond(covariance))
    shrunk = condition > 1e6
    if shrunk:
        centered = z - mean
        n, p = centered.shape
        s = centered.T @ centered / n
        target = np.eye(p) * np.trace(s) / p
        delta = np.square(s - target).sum()
        if delta:
            outer = centered[:, :, None] * centered[:, None, :]
            weight = min(np.square(outer - s).sum() / n**2, delta) / delta
            covariance = weight * target + (1-weight) * s
        else:
            covariance = s
    try:
        centered = np.vstack((observed, test)) - mean
        distances = np.sum(centered * np.linalg.solve(covariance, centered.T).T, axis=1)
    except np.linalg.LinAlgError:
        return result | {'outcome': 'indet_cov'}
    d0, reference = distances[0], distances[1:]
    if not np.isfinite(d0):
        return result | {'outcome': 'indet_cov'}
    good = np.isfinite(reference)
    exceed = int((reference[good] >= d0).sum())
    lo = (exceed + 1) / (R + 1)
    hi = (exceed + 1 + int((~good).sum())) / (R + 1)
    outcome = 'reject' if hi < .05 else ('accept' if lo >= .05 else 'indet_straddle')
    return result | {'outcome': outcome, 'p_lo': lo, 'p_hi': hi, 'D_obs': float(d0),
                     'condition': condition, 'shrinkage': shrunk,
                     'observed_T': observed.tolist(), 'training_mean_T': mean.tolist(),
                     'marginal_standardized_residual': ((observed-mean)/np.sqrt(np.diag(covariance))).tolist()}


def score_scenario(s):
    R = 2000
    rows = []
    hashes = {}
    failures = 0
    fallbacks = 0
    flag_mismatch = 0
    for c in s['chunks']:
        folder = EXTRACT / c['dir']
        metadata = json.loads((folder/'e2e_meta.json').read_text())
        assert metadata['manifest_digest'] == MANIFEST_SHA
        assert metadata['R_train'] == R
        logged = [json.loads(l) for l in (folder/'e2e_rows.jsonl').read_text().splitlines() if l.strip()]
        ids = list(range(*c['trial_ids']))
        assert [r['trial_id'] for r in logged] == ids
        for r in logged:
            tid = r['trial_id']
            path = folder/f'T_{tid}.csv'
            hashes[str(path.relative_to(EXTRACT))] = digest(path)
            try:
                values = np.loadtxt(path, delimiter=',', skiprows=1)
            except ValueError:
                values = np.genfromtxt(path, delimiter=',', skip_header=1)
            assert values.shape == (4001, 7), str(path)
            assert np.array_equal(values[:, 0], np.arange(4001))
            t = values[:, 1:5]
            nonfinite = ~np.isfinite(t).all(axis=1)
            flagged = values[:, 5] == 1
            failures += int((nonfinite | flagged).sum())
            flag_mismatch += int((nonfinite != flagged).sum())
            fallbacks += int(values[:, 6].sum())
            check = calculate(t, R)
            assert check['outcome'] == r['outcome'], (s['block'], tid, check, r['outcome'])
            if 'p_lo' in check:
                assert abs(check['p_lo']-r['p_lo']) < 1e-12, (s['block'], tid, 'p_lo')
                assert abs(check['p_hi']-r['p_hi']) < 1e-12, (s['block'], tid, 'p_hi')
            radii = json.loads(r['kth_dist'])
            largest = max(radii.values())
            rows.append({'trial_id': tid, 'chunk': c['c'], 'largest_radius_logged': largest,
                         'radius_bin': int(np.searchsorted(BINS, largest, side='left'))+1,
                         **check})
    assert len(rows) == s['n_trials']
    rejects = sum(r['outcome'] == 'reject' for r in rows)
    accepts = sum(r['outcome'] == 'accept' for r in rows)
    n = len(rows)
    strata = [{'bin': b, 'n': sum(r['radius_bin']==b for r in rows),
               'reject': sum(r['radius_bin']==b and r['outcome']=='reject' for r in rows)} for b in range(1,6)]
    summary = {'block': s['block'], 'name': s['name'], 'role': s['role'], 'n': n,
               'reject': rejects, 'accept': accepts, 'unresolved': n-rejects-accepts,
               'failed_datasets': failures, 'fitted_datasets': n*4001, 'fallbacks': fallbacks,
               'flag_mismatches': flag_mismatch, 'radius_strata_from_rounded_logged_distances': strata,
               'pvalue_deciles': np.histogram([r['p_lo'] for r in rows], np.linspace(0,1,11))[0].tolist(),
               'shrinkage_count': sum(r.get('shrinkage', False) for r in rows)}
    if s['role']=='null':
        summary |= {'non_accepts': n-accepts, 'null_upper_9875': cp(n-accepts, n, .025)[1],
                    'null_pass': n-accepts <= 60}
    if s['role']=='power':
        summary |= {'power_lower_95': cp(rejects,n,.1)[0], 'power_pass': rejects>=224}
    print(f"audited block {s['block']}: {rejects}/{n}; {failures} failed datasets", file=sys.stderr, flush=True)
    return {'summary': summary, 'rows': rows, 'T_hashes': hashes}


def verify_archive():
    archive = BASE/'validation_v1.tar.gz'
    assert digest(archive) == ARCHIVE_SHA
    matched = 0
    hashes = {}
    with tarfile.open(archive, 'r|gz') as tf:
        for member in tf:
            if not member.isfile():
                continue
            path = EXTRACT/member.name
            assert path.is_file(), member.name
            h = sha_stream(tf.extractfile(member))
            assert h == digest(path), member.name
            hashes[member.name] = h
            matched += 1
    print(f'archive SHA and {matched} extracted members verified', file=sys.stderr, flush=True)
    return {'archive_sha256': ARCHIVE_SHA, 'matched_extracted_files': matched, 'member_sha256': hashes}


def main():
    started = time.monotonic()
    assert digest(MANIFEST) == MANIFEST_SHA
    man = json.loads(MANIFEST.read_text())
    assert len(man['scenarios']) == 17
    assert man['R'] == man['K'] == 2000
    with mp.Pool(4) as pool:
        async_scores = pool.map_async(score_scenario, man['scenarios'])
        archive = verify_archive()
        scored = async_scores.get()
    summary = json.loads((EXTRACT/'validation_summary.json').read_text())
    by_block = {r['block']:r for r in summary['scenarios']}
    for b in scored:
        s = b['summary']; other = by_block[s['block']]
        assert s['n'] == other['n'] and s['reject'] == other['counts']['reject']
        assert s['accept'] == other['counts']['accept']
        assert s['failed_datasets'] == other['fit_failures']['failed_datasets']
        assert s['fitted_datasets'] == other['fit_failures']['fitted_datasets']
        for key, val in b['T_hashes'].items():
            assert archive['member_sha256'][key] == val
    v_fail = any(not b['summary']['null_pass'] for b in scored if b['summary']['role']=='null')
    fit_stop = any(b['summary']['failed_datasets']/b['summary']['fitted_datasets']>.02
                   for b in scored if b['summary']['role'] in ('null','power'))
    power_pass = next(b['summary']['power_pass'] for b in scored if b['summary']['role']=='power')
    assert v_fail == summary['v_fail'] and fit_stop == summary['fit_stop'] and power_pass == summary['power_gate_pass']
    result = {'method': 'Independent NumPy covariance/solve/ranks; no production scorer imports.',
              'manifest_sha256': MANIFEST_SHA, 'archive': archive, 'blocks': scored,
              'v_fail': v_fail, 'fit_stop': fit_stop, 'power_pass': power_pass,
              'summary_sha256': digest(EXTRACT/'validation_summary.json'),
              'wall_seconds': round(time.monotonic()-started,1),
              'limits': ['No refitting or resimulation.', 'Radius bins use the stored four-decimal distances.',
                         'Scoring verification does not establish statistical calibration or the cause of failure.']}
    print(json.dumps(result))


if __name__=='__main__':
    main()
