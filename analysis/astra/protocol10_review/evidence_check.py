"""Read-only independent audit of completed development screens and freeze inputs.

Run from any directory with the project's existing scientific Python environment.
Reads completed artifacts on deep-server via SSH; no simulation, fitting or remote writes.
"""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
F = ROOT / 'analysis/fable/calibration/freeze_v1'
D = ROOT / 'analysis/fable/calibration/dev_screen200_v1'

REMOTE = r'''
import csv, hashlib, io, json
from pathlib import Path
import numpy as np
from scipy.stats import beta
base=Path('/data/fable/vortex/production_banks_20261010T081726Z')
screen=Path('/data/fable/vortex/banks10x_20261009T041220Z/dev_screen200_v1')
def digest(p):
    with open(p,'rb') as fh:
        return hashlib.file_digest(fh,'sha256').hexdigest()
out={'screen':{}, 'hashes':{}, 'bank_files':{}, 'package_files':{}}
for arm in ('null','betamin'):
    folder=screen/arm
    rows=[json.loads(line) for line in (folder/'e2e_rows.jsonl').read_text().splitlines()]
    assert [r['outer'] for r in rows]==list(range(200))
    result={'reject':[], 'failed_trials':[], 'failed_datasets':0, 'fitted_datasets':0,
            'fallbacks':0, 'max_condition':0, 'shrinkage_trials':[], 'mean_observed_T':None}
    obs=[]
    for k,logged in enumerate(rows):
        path=folder/f'T_{k}.csv'
        out['hashes'][f'{arm}/T_{k}.csv']=digest(path)
        a=np.genfromtxt(path,delimiter=',',names=True)
        assert len(a)==4001 and np.array_equal(a['set'],np.arange(4001))
        x=np.column_stack([a[f'T{j}'] for j in range(1,5)])
        bad=~np.isfinite(x).all(axis=1)
        assert np.array_equal(a['failed'],bad.astype(int))
        assert np.isfinite(x[0]).all()
        assert bad[1:2001].sum()<=40
        z=x[1:2001][~bad[1:2001]]
        mean=z.mean(axis=0); cov=np.cov(z,rowvar=False)
        cond=float(np.linalg.cond(cov))
        result['max_condition']=max(result['max_condition'],cond)
        if cond>1e6:
            result['shrinkage_trials'].append(k)
            centered=z-mean; n,p=centered.shape
            s=centered.T@centered/n; target=np.trace(s)/p*np.eye(p)
            delta=((s-target)**2).sum()
            outer=centered[:,:,None]*centered[:,None,:]
            b=min(((outer-s)**2).sum()/n**2,delta)
            cov=s if delta==0 else b/delta*target+(1-b/delta)*s
        def distance(t):
            v=t-mean
            return np.sum(v*np.linalg.solve(cov,v.T).T,axis=1)
        d0=distance(x[:1])[0]
        dt=distance(x[2001:])
        lo=(1+int(np.sum(dt[np.isfinite(dt)]>=d0)))/2001
        hi=lo+int(np.sum(~np.isfinite(dt)))/2001
        assert abs(lo-logged['p_lo'])<1e-12 and abs(hi-logged['p_hi'])<1e-12
        outcome='reject' if hi<.05 else ('accept' if lo>=.05 else 'indet_straddle')
        assert outcome==logged['outcome']
        if outcome=='reject':result['reject'].append(k)
        if bad.any():result['failed_trials'].append(k)
        result['failed_datasets']+=int(bad.sum());result['fitted_datasets']+=len(x)
        result['fallbacks']+=int(a['fallback'].sum());obs.append(x[0])
    result['mean_observed_T']=np.mean(obs,axis=0).tolist()
    result['ci_95']=[float(beta.ppf(.025,len(result['reject']),201-len(result['reject']))),
                     float(beta.ppf(.975,len(result['reject'])+1,200-len(result['reject'])))]
    result['upper_9875']=float(beta.ppf(.9875,len(result['reject'])+1,200-len(result['reject'])))
    out['screen'][arm]=result
    for f in ('e2e_rows.jsonl','e2e_meta.json'):out['hashes'][f'{arm}/{f}']=digest(folder/f)
for bank in ('primary','stability','iid'):
    for p in sorted((base/f'bank_{bank}').glob('*.npz')):
        out['bank_files'][str(p.relative_to(base))]=digest(p)
    out['package_files'][f'bank_{bank}_meta.json']=digest(base/f'bank_{bank}_meta.json')
for line in (base/'package_inputs_sha256.txt').read_text().splitlines():
    sha,path=line.split(maxsplit=1);got=digest(path);assert got==sha,path
    out['package_files'][str(Path(path).relative_to(base))]=got
for f in ('empirical_position_ar_cat.json','empirical_position_iid.json','gen_times.json'):
    out['package_files'][f]=digest(base/f)
for line in (base/'freeze_source_sha256.txt').read_text().splitlines():
    sha,path=line.split(maxsplit=1);assert digest(base/'freeze_src'/path)==sha,path
out['staged_freeze_source_hashes_match']=True
libs=np.load(base/'effect/libraries_ar_cat.npz')
stress=json.loads((base/'stress_sets.json').read_text())
effect=json.loads((base/'effect/effect_target_ar_cat.json').read_text())
out['stress_structure']={k:type(v).__name__ for k,v in stress.items()} if isinstance(stress,dict) else type(stress).__name__
out['library_keys']=list(libs.files)
matched=0
for pops in stress['sets'].values():
    for pop,d in pops.items():
        for k,v in d['theta'].items():
            assert float(libs[f'{pop}__{k}'][d['library_index']])==v
            matched+=1
out['stress_library_match']={'matched_selected_parameter_values':matched,'matched_vectors':matched//6}
out['library_quantiles_match']=all(np.array_equal(np.quantile(libs[f'{pop}__{k}'],[.1,.5,.9]),qs)
    for pop,vals in effect['library_quantiles'].items() for k,qs in vals.items())
out['pooled_medians_match']=all(float(np.median(np.concatenate([libs[f'{pop}__{k}'] for pop in effect['library_quantiles']])))==v
    for k,v in effect['pooled_medians'].items())
out['gate_thresholds']={'null60':float(beta.ppf(.9875,61,940)), 'null61':float(beta.ppf(.9875,62,939)),
                        'power223':float(beta.ppf(.05,223,78)), 'power224':float(beta.ppf(.05,224,77))}
print(json.dumps(out))
'''


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def manifest(p):
    return {name: sha for sha, name in (line.split(maxsplit=1) for line in p.read_text().splitlines())}


def main():
    result = json.loads(subprocess.check_output(['ssh', 'deep-server', 'env', 'OPENBLAS_NUM_THREADS=1',
                                               'python3', '-'], input=REMOTE, text=True))
    archived_t = manifest(D / 'T_sha256.txt')
    assert len(archived_t) == 400
    assert archived_t == {k: v for k, v in result['hashes'].items() if k.endswith('.csv')}
    for k, v in result['hashes'].items():
        if not k.endswith('.csv'):
            assert digest(D / k) == v, k
    banks = {}
    for b in ('primary', 'stability', 'iid'):
        banks.update(manifest(F / f'bank_{b}_sha256.txt'))
    assert len(banks) == 540 and banks == result['bank_files']
    for k, v in result['package_files'].items():
        p = F / Path(k).name
        if p.exists():
            assert digest(p) == v, k
    source = manifest(F / 'freeze_source_sha256.txt')
    for name, sha in source.items():
        assert digest(ROOT / name) == sha, name
        data = subprocess.check_output(['git', 'show', '49f65ce:' + name], cwd=ROOT)
        assert hashlib.sha256(data).hexdigest() == sha, name
    seeds = set()
    result['bank_counts'] = {}
    for b in ('primary', 'stability', 'iid'):
        m = json.loads((F / f'bank_{b}_meta.json').read_text())
        assert len(m['tasks']) == 180
        selected = {}; over = {}
        for t in m['tasks']:
            assert t['draws'] == 100_000_000 and t['seed'] not in seeds
            seeds.add(t['seed']); p = t['population']
            selected[p] = selected.get(p, 0) + t['selected']
            over[p] = over.get(p, 0) + t['overflow']
        assert all(sum(t['draws'] for t in m['tasks'] if t['population'] == p) == 2_000_000_000
                   for p in selected)
        result['bank_counts'][b] = {'selected_by_population': selected,
                                   'max_overflow_fraction': max(over.values()) / 2e9}
    result['reviewed_commit'] = subprocess.check_output(['git', 'rev-parse', 'df94693'], cwd=ROOT, text=True).strip()
    result['source_files_checked'] = len(source)
    result['limitations'] = ['No new simulation or fit; bank generation and effect risks were not replayed.',
                            'Empirical C-only artifacts were hashed; no empirical T statistics or p-values accessed.']
    Path(__file__).with_suffix('.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('screen','source_files_checked','bank_counts',
                                           'library_quantiles_match','pooled_medians_match','gate_thresholds',
                                           'stress_structure')}, indent=2))


if __name__ == '__main__':
    main()
