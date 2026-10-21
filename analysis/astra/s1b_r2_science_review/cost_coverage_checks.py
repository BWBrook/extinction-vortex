"""Stage 1b round-two scientific contract/cost audit, no sampling or fits.

Reads committed collector/pilot/cost receipts and one 6.2 MB settings JSON
from deep-server. Does not alter production files or derive live settings.
Uses standard-library arithmetic independently of p3_w1_costs/p2_report.
"""
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
V2 = ROOT / 'analysis/fable/calibration/v2_dev'
REMOTE_SETTINGS = '/data/fable/vortex/v2_dev/p3/p3_settings.json'
SCEN = ('null_prior_predictive', 'null_low_s', 'MA_betamin', 'MA_d10_0.5')


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text())


def ckey(st):
    return st['pop'], st['outer'].split('/')[0], st['n']


def pilot_cost(row):
    # Independent transcription of the declared pilot projection, including
    # its explicitly unresolved zero-hit lower-limit substitution.
    if row.get('stop') == 'hits':
        return row['observed_cpu_hours_to_crossing_batch']
    if not row['proposals']:
        return None
    if row['hits']:
        return 2000 * row['cpu_seconds'] / row['hits'] / 3600
    exposure = row.get('suffix_proposals', 0)
    if not exposure:
        return None
    upper = -math.expm1(math.log(.05) / exposure)
    return 2000 / upper * row['cpu_seconds'] / row['proposals'] / 3600


def assert_close(a, b):
    if a is None or b is None:
        assert a is b, (a, b)
    else:
        assert math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-8), (a, b)


def main():
    cp = V2/'p3/w1_r1_collect_W1.json'
    pp = V2/'p2/s1a_main/collect_deep.json'
    rp = V2/'p3/w1_r1_costs.json'
    collect, pilot, published = read(cp), read(pp), read(rp)
    settings_bytes = subprocess.check_output(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','deep-server',
                                              'cat '+REMOTE_SETTINGS])
    settings = json.loads(settings_bytes)
    assert sha_bytes(settings_bytes) == collect['binding']['settings_sha256']
    assert sha_bytes(pp.read_bytes()) == settings['pilot_collect_sha256']
    st = {s['dir']:s for s in settings['settings']}
    rows = collect['rows']
    assert len({r['dir'] for r in rows}) == len(rows)
    assert {r['dir'] for r in rows} == {s['dir'] for s in st.values() if s['wave']=='W1'}
    projected = {r['index']:pilot_cost(r) for r in pilot['rows']}
    priors = defaultdict(list)
    for s in st.values():
        if s['library']=='primary' and projected.get(s['index']) is not None:
            priors[ckey(s)].append(projected[s['index']])
    prior_means = {c:statistics.mean(v) for c,v in priors.items()}
    calculated, completed_costs = {}, defaultdict(list)
    for r in rows:
        s=st[r['dir']]; pl=s['pilot']; p0=pl['batches_done'] if pl else 0
        pilot_cpu=pl['cpu_seconds']/3600 if pl else 0.
        trial=int(s['outer'].split('/')[1]); cell=ckey(s)
        gross=r.get('useful_cpu_h',0.)+r.get('discarded_cpu_h',0.)
        x=dict(dir=r['dir'],cell=cell,trial=trial,n=s['n'],library=s['library'],status=r['status'],
               gross_checkpoint_cpu_h=gross,pilot_cpu_h=pilot_cpu,round1_cpu_h=gross-pilot_cpu,
               projection=projected.get(s['index']) if trial<10 else prior_means[cell])
        if r['status']=='COMPLETE' and r.get('kth_hit') is not None and r['prefix_end_batch']>p0:
            batches=r['kth_hit']+1
            cpb=r['useful_cpu_h']/r['prefix_end_batch']
            x.update(crossing_cost_estimate=batches*cpb+r['discarded_cpu_h'],
                     throughput_ratio=cpb/(20000/s['rate']/3600),
                     hit_ratio=(2000/batches)/s['prior_hpb'] if s['prior_hpb'] else None,
                     discard_share=r['discarded_cpu_h']/gross if gross else 0.)
            completed_costs[cell].append(x['crossing_cost_estimate'])
        calculated[r['dir']]=x
    means={k:statistics.mean(v) for k,v in completed_costs.items()}
    by_dir=rows_by_dir(rows)
    groups={}
    for n in (0,30):
        for is_pilot in (True,False):
            key=f"n={n} {'pilot' if is_pilot else 'unseen'} outers"
            selected=[x for x in calculated.values() if x['n']==n and (x['trial']<10)==is_pilot and x['library']=='primary']
            done=[x for x in selected if 'crossing_cost_estimate' in x]
            actual=sum(x['crossing_cost_estimate'] for x in done)
            projected_total=sum(x['projection'] for x in done if x['projection'] is not None)
            unprojected=[x for x in done if x['projection'] is None]
            stats=dict(settings=len(selected),complete_resolved=len(done),actual_cpu_h=actual,
                       projected_cpu_h=projected_total,actual_over_projected=actual/projected_total,
                       median_throughput_ratio=statistics.median(x['throughput_ratio'] for x in done),
                       median_hit_ratio=statistics.median(x['hit_ratio'] for x in done if x['hit_ratio'] is not None),
                       median_discard_share=statistics.median(x['discard_share'] for x in done))
            for k,v in stats.items():
                assert_close(v,published['groups'][key][k])
            checkpoint=sum(x['gross_checkpoint_cpu_h'] for x in done)
            groups[key]=dict(reproduced=stats,status_counts=dict(Counter(x['status'] for x in selected)),
                             included_actual_but_missing_projection=[dict(dir=x['dir'],cpu_h=x['crossing_cost_estimate']) for x in unprojected],
                             matched_only_actual_over_projected=(actual-sum(x['crossing_cost_estimate'] for x in unprojected))/projected_total,
                             completed_fraction=len(done)/len(selected),recorded_cpu_h_same_completed_subset=checkpoint,
                             recorded_over_projected=checkpoint/projected_total,
                             proration_removed_cpu_h=checkpoint-actual,
                             completed_prefixes_beyond_crossing=sum(by_dir[x['dir']]['prefix_end_batch']>
                                                                  by_dir[x['dir']]['kth_hit']+1 for x in done))
    restart={x['dir']:max(means.get(x['cell'],x['projection'] or 0.),1.25*x['round1_cpu_h'])
             for x in calculated.values() if x['status']=='incomplete'}
    assert len(restart)==published['incomplete']==4846
    assert_close(sum(restart.values()),published['incomplete_restart_estimate_cpu_h'])
    assert_close(sum(x['round1_cpu_h'] for x in calculated.values()),published['w1_spent_round1_cpu_h'])
    invalid=[x for x in calculated.values() if x['status']=='invalid']
    invalid_estimates=[dict(dir=x['dir'],collector_cpu_missing=True,
                           completed_cell_mean=means.get(x['cell']),pilot_cell_projection=x['projection']) for x in invalid]

    primary=[r for r in rows if r['library']=='primary']
    by_identity={(r['outer'],r['n'],r['pop']):r for r in primary}
    pops=sorted({r['pop'] for r in primary})
    coverage={}
    for scenario in SCEN:
        sc={}
        for n in (0,30):
            sets=[[by_identity[f'{scenario}/{i}',n,p] for p in pops] for i in range(200)]
            sc[str(n)]=dict(denominator=200,all_nine_complete=sum(all(r['status']=='COMPLETE' for r in rs) for rs in sets),
                           any_capped=sum(any(r['status']=='CAPPED' for r in rs) for rs in sets),
                           any_open=sum(any(r['status'] in ('incomplete','invalid') for r in rs) for rs in sets))
        sc['paired_n0_n30_complete']=sum(all(by_identity[f'{scenario}/{i}',n,p]['status']=='COMPLETE'
                                                   for n in (0,30) for p in pops) for i in range(200))
        coverage[scenario]=sc
    cell_status=defaultdict(Counter)
    for r in primary:
        cell_status[ckey(r)][r['status']]+=1
    terminal={r['dir'] for r in rows if r['status'] in ('COMPLETE','CAPPED','FAILED')}
    redo={r['dir'] for r in rows if r['status'] in ('incomplete','invalid')}
    w2={s['dir'] for s in st.values() if s['wave']=='W2'}
    assert not (terminal&redo or terminal&w2 or redo&w2)
    assert terminal|redo|w2==set(st)
    caps=[dict(dir=r['dir'],outer=r['outer'],pop=r['pop'],n=r['n'],prefix_end_batch=r['prefix_end_batch'],
               bound_cap_batches=st[r['dir']]['cap_batches'],prefix_hits=r['prefix_hits']) for r in rows if r['status']=='CAPPED']
    assert all(r['prefix_end_batch']==r['bound_cap_batches'] for r in caps)
    max_open=max((r for r in rows if r['status']=='incomplete'),key=lambda r:r['prefix_end_batch'])
    result=dict(timestamp=datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),
                head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                inputs_sha256={str(p.relative_to(ROOT)):sha_bytes(p.read_bytes()) for p in (cp,pp,rp)}|
                              {'deep-server:'+REMOTE_SETTINGS:sha_bytes(settings_bytes)},
                scope='Read-only metadata arithmetic; no population simulation, library reassembly, production writes or PBS action.',
                all_published_cost_statistics_reproduced=True,groups=groups,
                statuses=dict(Counter(r['status'] for r in rows)),
                checkpoint_cpu_h=dict(useful=collect['useful_cpu_h'],discarded=collect['discarded_cpu_h'],
                     total=sum(x['gross_checkpoint_cpu_h'] for x in calculated.values()),
                     included_pilot=sum(x['pilot_cpu_h'] for x in calculated.values()),
                     nonpilot=sum(x['round1_cpu_h'] for x in calculated.values()),
                     missing_invalid_rows=len(invalid)),
                restart_heuristic=dict(priced_rows=len(restart),cpu_h=sum(restart.values()),
                     actual_open_rows=len(redo),omitted_invalid=invalid_estimates,
                     cells_with_completed_costs=len(means),
                     add_invalid_using_same_cell_mean_only=sum(restart.values())+sum(x['completed_cell_mean'] for x in invalid_estimates)),
                coverage=coverage,cell_status={'|'.join(map(str,k)):dict(v) for k,v in sorted(cell_status.items())},
                inventory_partition=dict(w1=len(rows),primary_w1=len(primary),check_w1=len(rows)-len(primary),
                     retained_terminal=len(terminal),redo_w1=len(redo),w2=len(w2),round2=len(redo|w2),full_union=len(st)),
                capped_prefixes=caps,
                determinism_scaling=dict(max_open_dir=max_open['dir'],committed_prefix_batches=max_open['prefix_end_batch'],
                     python_integer_bytes=sys.getsizeof(10**6),
                     one_set_integer_payload_lower_bound_bytes=(max_open['prefix_end_batch']-257)*sys.getsizeof(10**6),
                     excludes='Python set hash tables, second run, intersection, per-batch loops and interpreter overhead.'),
                qualification='Completion-conditioned cost summaries and heuristic future budgets are not full-cell means or prediction intervals. Final scientific denominators remain200 per scenario/n, including CAPPED outcomes; check libraries are not extra outer replicates.')
    (HERE/'cost_coverage_checks.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ('statuses','checkpoint_cpu_h','restart_heuristic','coverage','inventory_partition','determinism_scaling')},indent=2))


def rows_by_dir(rows):
    return {r['dir']:r for r in rows}


if __name__=='__main__':
    main()
