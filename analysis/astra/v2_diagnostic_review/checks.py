"""Bounded review of D1's retained summaries and numerical trend calculation.

No banks, population simulations, model fits or empirical statistics are read.
Run with the existing dsipa-dev Python environment (NumPy/SciPy).
"""
import ast
from datetime import datetime
import hashlib
from itertools import product
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

import numpy as np
import scipy
from scipy.stats import beta

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SRC = ROOT / 'analysis/fable/calibration'
D1 = SRC / 'v2_dev'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = json.loads((SRC / 'freeze_v1/validation_manifest.json').read_text())
    data = json.loads((D1 / 'knn_nuisance.json').read_text())
    hashes = {name: digest(ROOT / name) for name in [
        'analysis/fable/calibration/bank.py',
        'analysis/fable/calibration/e2e_benchmark.py']}
    assert all(value == manifest['source_sha256'][name] for name, value in hashes.items())
    assert data['K'] == manifest['K'] == 2000
    blocks = {s['name']: s for s in manifest['scenarios'] if s['role'] == 'null'}
    assert set(data['blocks']) == set(blocks)
    ranges = {}
    fixed_values_checked = 0
    undefined = []
    for name, block in data['blocks'].items():
        assert block['n'] == blocks[name]['n_trials'] == 1000
        assert len(block['populations']) == 9
        ranges[name] = {key: [min(p[key] for p in block['populations'].values()),
                              max(p[key] for p in block['populations'].values())]
                        for key in ['s_true_rank_in_lib', 'sigma_true_rank_in_lib',
                                    'f_true_rank_in_lib', 'trend_rank_mean']}
        for pop, values in block['populations'].items():
            for key, value in values.items():
                if isinstance(value, float) and not np.isfinite(value):
                    undefined.append(f'{name}/{pop}/{key}')
            for parameter in ('s', 'f', 'sigma'):
                if 'fixed' in blocks[name]['spec']:
                    truth = blocks[name]['spec']['fixed'][pop][parameter]
                    assert values[f'{parameter}_true_mean'] == round(truth, 4)
                    fixed_values_checked += 1

    def refuse_constant(token):
        raise ValueError(token)

    try:
        json.loads((D1 / 'knn_nuisance.json').read_text(), parse_constant=refuse_constant)
    except ValueError as exc:
        strict_json_error = str(exc)
    else:
        strict_json_error = None
    assert strict_json_error == 'NaN' and len(undefined) == 12

    # Execute the actual small trend function in isolation, without its bank-loading main body.
    tree = ast.parse((D1 / 'knn_nuisance.py').read_text())
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'trend')
    isolated = ast.Module(body=[function], type_ignores=[])
    namespace = {'np': np}
    exec(compile(isolated, str(D1 / 'knn_nuisance.py'), 'exec'), namespace)
    # These are exhaustive arithmetic fixtures, not draws from the study's population generator.
    trajectories = np.array([[20, *middle, 2, 0]
                             for middle in product([2, 3, 4, 6, 12, 18, 30], repeat=3)])
    calculated = namespace['trend'](trajectories)
    exact_endpoint_form = np.log(trajectories[:, -2] / trajectories[:, 0]) / (trajectories.shape[1] - 2)
    assert np.unique(exact_endpoint_form).size == 1
    assert np.unique(calculated).size > 1
    selected = calculated.min()
    broken_rank = float(np.mean(calculated < selected) + .5 * np.mean(calculated == selected))
    assert broken_rank != .5

    result = {
        'reviewed_commit': 'a60b266ddfd36ef395c25433937c2a4f8f925928',
        'time_hobart': datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),
        'python': sys.version, 'numpy': np.__version__, 'scipy': scipy.__version__,
        'scope': 'Local summary/source checks and deterministic arithmetic fixtures; no bank reload, new population simulation or fitting.',
        'd1_source_sha256': digest(D1 / 'knn_nuisance.py'),
        'd1_summary_sha256': digest(D1 / 'knn_nuisance.json'),
        'manifest_sha256': digest(SRC / 'freeze_v1/validation_manifest.json'),
        'frozen_source_hashes_match': hashes,
        'fixed_corner_mean_values_checked': fixed_values_checked,
        'reported_rank_ranges_reproduced': ranges,
        'undefined_fields': undefined,
        'strict_json_error': strict_json_error,
        'trend_fixture': {
            'n_paths': len(trajectories), 'initial': 20, 'penultimate': 2, 'length': 6,
            'correct_midrank_for_every_path': .5,
            'computed_distinct_trend_values': np.unique(calculated).tolist(),
            'computed_lowest_path_midrank': broken_rank,
            'lowest_path': trajectories[np.argmin(calculated)].tolist(),
            'highest_path': trajectories[np.argmax(calculated)].tolist(),
            'effect_on_actual_D1_ranks': 'Not measured: per-trial libraries/ranks are not retained in D1 output.'},
        'planning_illustration_only': {
            'hypothetical_rejections': 10, 'n': 200,
            'two_sided_95_CP': [float(beta.ppf(.025, 10, 191)), float(beta.ppf(.975, 11, 190))],
            'one_sided_9875_upper_CP': float(beta.ppf(.9875, 11, 190)),
            'note': 'Illustrates uncertainty of a 200-trial diagnostic; not an observed result or a v2 gate.'},
        'limitations': ['Fixture runtime differs from the frozen v1 runtime.',
                       'Aggregate rank ranges do not verify per-trial matching or identify a mechanism.',
                       'This is not independent reconstruction of the large bank neighbourhoods.']}
    (HERE / 'checks.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({k: result[k] for k in ['fixed_corner_mean_values_checked', 'strict_json_error',
                     'trend_fixture', 'planning_illustration_only']}, indent=2))


if __name__ == '__main__':
    main()
