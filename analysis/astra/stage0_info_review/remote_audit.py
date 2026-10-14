"""Read-only Stage 0 audit, executed on deep-server through stdin.

No bank arrays, trees, population simulation, reference draws or fits. Reads
one saved member NPZ at a time; replays only the 14,400 already-saved E draws.
The caller saves stdout. All result summaries are derived independently of
s0_info.report. No production Python modules are imported.
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
import scipy
from scipy.special import expit

BASE = Path('/data/fable/vortex/v2_dev/s0')
SRC = Path('/data/fable/vortex/kunanyi_stage/run1/src')
ORIGINAL = Path('/data/fable/vortex/kunanyi_run1/extract')
MANIFEST = SRC.parent / 'validation_manifest.json'
RUNNER = BASE.parent / 's0_info.py'
SCEN = ('null_prior_predictive', 'null_low_s', 'MA_betamin', 'MA_d10_0.5')
PARAMS = ('s', 'f', 'sigma', 'rho', 'p_c', 'delta')


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def object_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def q(values, probs=(.05, .25, .5, .75, .95)):
    return [round(float(v), 4) for v in np.quantile(values, probs)]


def main():
    started = time.monotonic()
    inputs = json.loads((BASE / 's0_inputs.json').read_text())
    report = json.loads((BASE / 's0_report.json').read_text())
    man = json.loads(MANIFEST.read_text())
    bind = inputs['bindings']
    pops = bind['population_order']
    outers = inputs['outers']
    expected = {f'{s}/{i}' for s in SCEN for i in range(200)}
    assert set(outers) == expected
    runtime = dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__)
    assert runtime == bind['runtime']
    assert sha(MANIFEST) == bind['manifest_digest']
    assert sha(RUNNER) == bind['helper_sha256']['s0_info.py']
    assert sha(BASE / 's0_inputs.json') == report['inputs_sha256']
    assert bind == report['bindings']
    sources = {str(p): sha(SRC / p) for p in man['source_sha256']}
    assert sources == man['source_sha256']
    bankmeta_path = ORIGINAL / man['bankdir'] / 'bank_meta.json'
    bankmeta = json.loads(bankmeta_path.read_text())
    assert sha(bankmeta_path) == man['bank_sha256']['bank_meta.json']
    original_shas, seen = {}, Counter()
    for folder, expected_sha in bind['source_rows_sha256'].items():
        path = ORIGINAL / folder / 'e2e_rows.jsonl'
        original_shas[folder] = sha(path)
        assert original_shas[folder] == expected_sha
        scenario = next(s for s in SCEN if any(
            c['dir'] == folder for z in man['scenarios'] if z['name'] == s for c in z['chunks']))
        for line in path.open():
            row = json.loads(line)
            key = f"{scenario}/{row['trial_id']}"
            if key not in outers:
                continue
            seen[key] += 1
            saved = outers[key]
            assert saved['dir'] == folder
            assert saved['kth_v1'] == json.loads(row['kth_dist'])
            assert list(row['selected']) == pops
            for pop in pops:
                r = row['selected'][pop]
                assert saved['pops'][pop] == dict(recorded=r['recorded'], theta={k: r['params'][k] for k in PARAMS})
                assert np.isfinite(list(saved['pops'][pop]['theta'].values())).all()
                assert all(v > 1 for v in r['recorded'][1:-1]) and r['recorded'][-1] <= 1
    assert set(seen) == expected and set(seen.values()) == {1}
    corner = next(s['spec']['fixed'] for s in man['scenarios'] if s['name'] == 'null_low_s')
    assert all(outers[f'null_low_s/{i}']['pops'][p]['theta'] == corner[p] for i in range(200) for p in pops)

    # Independent 40-node vector quadrature, then exact replay using saved rates
    # (not independently rounded rates) to isolate RNG provenance from arithmetic.
    gx, gw = np.polynomial.hermite_e.hermegauss(40)
    gw /= gw.sum()
    errors = []
    ekeys = set()
    for si, scenario in enumerate(SCEN):
        for i in range(200):
            for pi, pop in enumerate(pops):
                th = outers[f'{scenario}/{i}']['pops'][pop]['theta']
                keep = 1 - th['delta'] * th['p_c']
                sb = keep * float(np.dot(gw, expit(np.log(th['s']) - np.log1p(-th['s']) + th['sigma'] * gx)))
                fb = keep * th['f']
                for ni, n in enumerate((30, 300)):
                    cell = 4 * ni + si
                    ek = f'{cell}/{i}/{pop}'
                    ekeys.add(ek)
                    e = inputs['E'][ek]
                    errors.append(max(abs(sb-e['sbar_true']), abs(fb-e['fbar_true'])))
                    assert e['n'] == n and 0 <= e['k'] <= n and e['r'] >= 0
                    rng = np.random.default_rng([20261014, 1, cell, i, pi])
                    assert int(rng.binomial(n, e['sbar_true'])) == e['k']
                    assert int(rng.poisson(n * e['fbar_true'])) == e['r']
    assert ekeys == set(inputs['E']) and max(errors) < 1e-12

    raw, raw_shas, member_shas, members, costs = {}, {}, {}, {}, {}
    null_member_digests = {}
    for pop in pops:
        path = BASE / 'full' / f's0_{pop}.json'
        data = json.loads(path.read_text())
        raw_shas[path.name] = sha(path)
        assert data['population'] == pop
        rows = data['rows']
        assert len(rows) == len(expected) and {r['outer'] for r in rows} == expected
        raw[pop] = {r['outer']: r for r in rows}
        for row in rows:
            assert row['kth_v1_logged'] == outers[row['outer']]['kth_v1'][pop]
            assert row['kth_mismatch'] == (abs(round(row['kth'], 4)-row['kth_v1_logged']) > 1e-4)
            for kind in ('noisy_30', 'ideal_30', 'noisy_300', 'ideal_300'):
                st = row[kind]
                assert st['usable']
                assert np.isfinite([st['ess'], st['max_share']]).all()
                assert 1-1e-10 <= st['ess'] <= 2000+1e-10
                assert 1/2000-1e-10 <= st['max_share'] <= 1+1e-10
        path = BASE / 'full' / f'members_{pop}.npz'
        member_shas[path.name] = sha(path)
        assert member_shas[path.name] == data['members_sha256']
        with np.load(path) as z:
            keys, ids = z['keys'], z['draw_id']
            assert keys.tolist() == sorted(expected) and ids.shape == (800, 2000)
            assert np.issubdtype(ids.dtype, np.integer)
            duplicate_rows = sum(len(np.unique(v)) != 2000 for v in ids)
            assert duplicate_rows == 0
            assert ids.min() >= 0 and ids.max() < bankmeta['shards'] * bankmeta['shard_draws']
            nulls = {str(key): hashlib.sha256(np.sort(v).astype(np.int64).tobytes()).hexdigest()[:16]
                     for key, v in zip(keys, ids) if str(key).startswith(('null_prior_predictive/', 'null_low_s/'))}
            null_member_digests[pop] = object_sha(nulls)
            members[pop] = dict(shape=list(ids.shape), dtype=str(ids.dtype), duplicate_rows=duplicate_rows,
                                minimum=int(ids.min()), maximum=int(ids.max()), null_digest_count=len(nulls))
        count = sum(t['selected'] for t in bankmeta['tasks'] if t['variant'] == man['variant'] and t['population'] == pop)
        assert count == data['bank_rows']
        costs[pop] = {k: data[k] for k in ('seconds', 'peak_rss_gb', 'bank_rows', 'members_sha256')}
    assert costs == report['cost']

    counts = dict(neighbourhoods=sum(len(v) for v in raw.values()),
                  boundary_ties=sum(r['tie'] for d in raw.values() for r in d.values()),
                  kth_mismatches_vs_v1_log=sum(r['kth_mismatch'] for d in raw.values() for r in d.values()))
    assert counts == report['query']
    cells = {}
    for ni, n in enumerate((30, 300)):
        for si, scenario in enumerate(SCEN):
            cell = str(4 * ni + si)
            ks = [f'{scenario}/{i}' for i in range(200)]
            result = {}
            for kind in ('noisy', 'ideal'):
                label = f'{kind}_{n}'
                ess = np.array([[raw[p][k][label]['ess'] for k in ks] for p in pops])
                mx = np.array([[raw[p][k][label]['max_share'] for k in ks] for p in pops])
                usable = np.array([[raw[p][k][label]['usable'] for k in ks] for p in pops])
                st = dict(ess_q05_25_50_75_95={p:q(ess[j]) for j,p in enumerate(pops)},
                          max_share_q05_25_50_75_95={p:q(mx[j]) for j,p in enumerate(pops)},
                          unusable_sets={p:int((~usable[j]).sum()) for j,p in enumerate(pops)},
                          datasets=200, any_of_nine_flag_fraction=float(((ess < 100) | ~usable).any(axis=0).mean()),
                          any_of_nine_unusable_fraction=float((~usable).any(axis=0).mean()),
                          pooled_ess_q05_25_50_75_95=q(ess.ravel()))
                assert st == report['cells'][cell][kind], (cell, kind)
                result[kind] = st
            kth = {p:q([raw[p][k]['kth'] for k in ks], (.05,.5,.95)) for p in pops}
            assert kth == report['cells'][cell]['kth_q05_50_95']
            cells[cell] = dict(scenario=scenario, n=n, **result)
    out = dict(timestamp=datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),
               runtime=runtime, elapsed_seconds=round(time.monotonic()-started, 3),
               scope='Saved outputs, member IDs and source receipts only; no bank arrays/tree, new population simulation, reference draw or fit; replayed saved E draws.',
               paths=dict(base=str(BASE), source=str(SRC), original=str(ORIGINAL)),
               manifest_sha256=sha(MANIFEST), runner_sha256=sha(RUNNER),
               inputs_sha256=sha(BASE/'s0_inputs.json'), report_sha256=sha(BASE/'s0_report.json'),
               source_sha256=sources, bank_meta_sha256=sha(bankmeta_path),
               bank_shard_rehash_scope='No fresh shard rehash: s0 run verifies all 180 population shards; metadata freshly rehashed here.',
               source_rows_sha256=original_shas, outer_count=len(outers), exact_original_outer_matches=len(seen),
               original_outer_duplicate_counts=sorted(set(seen.values())), fixed_corner_matches=200*len(pops),
               E_replay_matches=len(ekeys), maximum_functional_error=max(errors),
               raw_sha256=raw_shas, member_sha256=member_shas, member_checks=members,
               null_member_digest_sha256=null_member_digests, query=counts, costs=costs, cells=cells,
               report_all_numeric_summaries_match=True, raw_unusable_sets=0,
               full_log_sha256=sha(BASE/'full.log'), full_log=(BASE/'full.log').read_text())
    print(json.dumps(out, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
