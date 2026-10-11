"""Reproduce the bounded v2 plan review; no bank loading, simulation or fits.

Run with an existing NumPy/SciPy environment. This is a development audit,
not validation of Candidate B. Only disjoint stored power arms are transformed.
"""
import ast
from collections import Counter
from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path
import platform
from zoneinfo import ZoneInfo

import numpy as np
import scipy
from scipy.spatial import cKDTree

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEV = ROOT / 'analysis/fable/calibration/v2_dev'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def isolated(path, name):
    tree = ast.parse(path.read_text())
    fn = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == name)
    ns = {'np': np}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(path), 'exec'), ns)
    return ns[name]


def method10(a, b, c, d):
    """Independent Newcombe 1998 section 5 transcription; O minus V sign."""
    n = a + b + c + d
    z = 1.959964
    p = np.array([a + b, a + c], dtype=float) / n
    centre = (p + z*z/(2*n)) / (1 + z*z/n)
    half = z * np.sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1+z*z/n)
    down, up = p - (centre-half), (centre+half) - p
    num = a*d-b*c
    if num > 0:
        num = max(num-n/2, 0)
    den = np.sqrt(float((a+b)*(c+d)*(a+c)*(b+d)))
    phi = num/den if den else 0.
    left = np.sqrt(max(down[0]**2 + up[1]**2 - 2*phi*down[0]*up[1], 0))
    right = np.sqrt(max(up[0]**2 + down[1]**2 - 2*phi*up[0]*down[1], 0))
    diff = p[0]-p[1]
    return np.round([-diff-right, -diff+left], 4).tolist()


def main():
    raw_path = ROOT / 'analysis/astra/validation_v1_audit/raw_score.json.gz'
    raw = json.load(gzip.open(raw_path, 'rt'))
    blocks = {b['summary']['block']: b for b in raw['blocks']}
    nulls = {b['summary']['name']: b for b in raw['blocks'] if b['summary']['role'] == 'null'}
    summary = json.loads((DEV / 'd1c_summary.json').read_text())
    assert summary['manifest_digest'] == raw['manifest_sha256']
    assert summary['script_sha256'] == sha(DEV / 'knn_nuisance_c.py')
    with gzip.open(DEV / 'd1c_trials.jsonl.gz', 'rt') as f:
        rows = [json.loads(line) for line in f]
    assert len(rows) == 4000
    assert len({(r['block'], r['trial_id']) for r in rows}) == len(rows)
    reconciled = {}
    for name, b in nulls.items():
        old = {r['trial_id']: r for r in b['rows']}
        current = [r for r in rows if r['block'] == name]
        assert {r['trial_id'] for r in current} == set(old)
        ties = Counter()
        undefined = Counter()
        denominators = Counter()
        for r in current:
            o = old[r['trial_id']]
            assert r['outcome'] == o['outcome'] and r['p_hi'] == o['p_hi']
            assert len(r['pop']) == 9
            assert all(p['kth'] == p['kth_v1'] for p in r['pop'].values())
            assert max(p['kth'] for p in r['pop'].values()) == o['largest_radius_logged']
            for pop, p in r['pop'].items():
                ties[pop] += p['tie']
                undefined[pop] += p['pen'] is None
            denominators[sum(p['pen'] is not None for p in r['pop'].values())] += 1
        assert sum(ties.values()) == summary['blocks'][name]['reconstruction']['boundary_ties']
        assert all(count == summary['blocks'][name]['pen_rank_undefined'][p]['constant_library']
                   for p, count in undefined.items())
        reconciled[name] = {'rows': len(current), 'matched_population_distances': 9*len(current),
                            'boundary_ties': sum(ties.values()), 'null_pen_ranks_by_population': dict(undefined),
                            'number_of_populations_in_pen_mean': dict(denominators)}

    # Constant libraries have valid midranks; only a variance-based z is undefined.
    midrank = isolated(DEV / 'knn_nuisance_c.py', 'midrank')
    lib = np.full((3, 4), 5)
    rank = midrank(lib, np.array([4, 5, 6]))
    assert rank.tolist() == [0., .5, 1.]

    # A tied counterexample to K+1 followed by truncation reconstructing a K query.
    tree = cKDTree(np.zeros((8, 2)))
    query_k = tree.query([0, 0], k=3)[1].tolist()
    query_k_plus_1 = tree.query([0, 0], k=4)[1][:3].tolist()
    assert set(query_k) != set(query_k_plus_1)

    # The checked-in function is method 8. Check our method 10 against a published table.
    current_ci = isolated(DEV / 'd3_oracle.py', 'newcombe10')
    assert current_ci(100, 0, 0, 100) == [0., 0.]
    assert method10(100, 0, 0, 100) == [-.0097, .0097]
    assert method10(20, 12, 2, 16) == [-.3292, -.0562]  # Table III, reversed sign
    assert method10(27, 0, 0, 27) == [-.0351, .0351]    # Table III continued

    # Reuse the audited low-s table only as a post-hoc development power screen.
    # Do not use these same null rows to claim calibration of their own CDF.
    cal_rows = blocks[3]['rows']
    assert len(cal_rows) == 1000 and all(r['outcome'] in ('accept', 'reject') for r in cal_rows)
    cal = np.sort([r['p_hi'] for r in cal_rows])
    power = {}
    for block in (5, 6, 15, 16):
        b = blocks[block]
        rr = b['rows']
        assert len(rr) == 300 and all(r['outcome'] in ('accept', 'reject') for r in rr)
        p = np.array([r['p_hi'] for r in rr])
        q = np.maximum(p, (1 + np.searchsorted(cal, p, side='right')) / 1001)
        assert np.all(q >= p)
        power[b['summary']['name']] = {'block': block, 'n': len(rr),
                                      'raw_rejections': int((p < .05).sum()),
                                      'low_s_wrapper_rejections': int((q < .05).sum()),
                                      'raw_p_q10_50_90': np.quantile(p, [.1,.5,.9]).tolist(),
                                      'wrapped_p_q10_50_90': np.quantile(q, [.1,.5,.9]).tolist()}
    pgrid = np.arange(1, 2002) / 2001
    qgrid = np.maximum(pgrid, (1 + np.searchsorted(cal, pgrid, side='right')) / 1001)
    files = [raw_path, DEV/'knn_nuisance_c.py', DEV/'d1c_summary.json', DEV/'d1c_trials.jsonl.gz',
             DEV/'d3_oracle.py', DEV/'run_d3.sh', ROOT/'notes/vortex_v2_dev_plan_20261011.md']
    result = {
        'reviewed_commit': '29c45c940e6ecca7db0ec94ea992c76e36219a1a',
        'time_hobart': datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__},
        'input_sha256': {str(p.relative_to(ROOT)): sha(p) for p in files},
        'd1c_reconciliation': reconciled,
        'constant_library_midrank_fixture': {'library': [5]*4, 'observed': [4,5,6], 'ranks': rank.tolist()},
        'neighbour_tie_fixture': {'K': 3, 'query_K': query_k, 'query_K_plus_1_truncated': query_k_plus_1,
                                  'same_membership': set(query_k) == set(query_k_plus_1)},
        'paired_ci_fixture': {'table_a_b_c_d': [100,0,0,100], 'current': current_ci(100,0,0,100),
                              'method10': method10(100,0,0,100), 'published_table_cases_passed': 2},
        'candidate_B_low_s_only_screen': {'calibration_block': 3, 'n_cal': 1000,
                                         'power': power, 'largest_rejecting_raw_p_on_v1_grid': float(pgrid[qgrid < .05].max()),
                                         'limits': 'Post-hoc development screen on disjoint stored power arms. Not a new calibrated procedure or validation; full B including this same table can only reduce these detections. A new table can differ.'},
        'limits': ['No primary bank, neighbour npz or D3 results loaded.',
                   'All p bounds/outcomes reconciled to the independent v1 audit; per-population original kth records not reread.',
                   'Matching rounded distances does not prove membership identity.',
                   'This script reproduces current defects; it must be versioned rather than overwritten after peer repairs.']}
    (HERE/'checks.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'rows_reconciled': len(rows), 'power_screen': power, 'fixture_checks': 'passed'}, indent=2))


if __name__ == '__main__':
    main()
