"""Independent arithmetic and uncertainty audit using saved Stage 1a rows only.
No sampler imports, new population paths, bank scans, fitting or remote execution.
"""
import collections, hashlib, json, math, sys, time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
start=time.perf_counter()
root=Path(__file__).resolve().parents[3]
base=root/'analysis/fable/calibration/v2_dev/p2'
paths={'collect':base/'s1a_main/collect_deep.json','report':base/'s1a_main/s1a_report.json','settings':base/'p2_settings_s1a.json'}
c,rep,b=[json.loads(paths[k].read_text()) for k in ('collect','report','settings')]
rows=c['rows'];K=2000;M=200;B=4000
pops=list(dict.fromkeys(r['pop'] for r in rows));scens=list(dict.fromkeys(r['outer'].split('/')[0] for r in rows));ns=(0,30,300)
res={'scope':__doc__,'timestamp':datetime.now(ZoneInfo('Australia/Hobart')).isoformat(),'python':sys.version,'numpy':np.__version__,'sha256':{k:hashlib.sha256(v.read_bytes()).hexdigest() for k,v in paths.items()}}
cost={r['index']:(r['cpu_seconds']/3600 if r.get('stop')=='hits' else K*r['cpu_seconds']/3600/r['hits'] if r['hits'] else K*r['cpu_seconds']/3600/3 if r['proposals'] else None) for r in rows}
cell={};sums={n:0. for n in ns};zero=[]
for pop in pops:
 for sc in scens:
  for n in ns:
   rr=[r for r in rows if r['pop']==pop and r['outer'].split('/')[0]==sc and r['n']==n]
   a=np.array([cost[r['index']] if cost[r['index']] is not None else np.nan for r in rr])
   cell[pop,sc,n]=a;sums[n]+=float(np.nanmean(a))*M
res['inventory_independent']={'by_n':sums,'total':sum(sums.values()),'reported_total':rep['stage1b_inventory']['cpu_h_total'],'difference':sum(sums.values())-rep['stage1b_inventory']['cpu_h_total']}
res['counts']={'rows':len(rows),'positive_hit_complete':sum(r['hits']>0 and r['status']=='complete' for r in rows),'positive_hit_censored':sum(r['hits']>0 and r['status']=='censored' for r in rows),'zero_with_exposure':sum(r['hits']==0 and r['proposals']>0 for r in rows),'no_exposure':sum(r['proposals']==0 for r in rows),'hits':sum(r['hits'] for r in rows),'worker_cpu_h':sum(r['cpu_seconds'] for r in rows)/3600}
for r in rows:
 if r['hits']==0 and r['proposals']:
  # Exact one-sided 95% suffix zero-success binomial bound, stable for enormous N.
  pu=-math.expm1(math.log(.05)/r['suffix_proposals'])
  exact_lb=K*r['cpu_seconds']/3600/r['proposals']/pu
  zero.append({'index':r['index'],'proposals':r['proposals'],'suffix_proposals':r['suffix_proposals'],'plug_lower_cost':cost[r['index']],'exact_suffix_95_expected_cost_lower':exact_lb,'fraction_difference':exact_lb/cost[r['index']]-1,'scaled_200_outer_contribution':cost[r['index']]*20,'formal_cost_upper':None})
res['zero_hit']=zero
zsum=sum(z['scaled_200_outer_contribution'] for z in zero)
res['zero_placeholder_sensitivity']={'current_contribution':zsum,'total_without_zero_placeholders':sum(sums.values())-zsum,'total_if_10x_lower_placeholder':sum(sums.values())+9*zsum,'total_if_100x_lower_placeholder':sum(sums.values())+99*zsum,'note':'Illustrative substitutions only; no new estimates or confidence bounds.'}
# Reproduce exactly the report's independent-cell bootstrap using known cell order/seed.
rng=np.random.default_rng([20261016,1]);ind=np.zeros(B)
for a in cell.values():
 v=a[np.isfinite(a)];ind+=v[rng.integers(0,len(v),(B,len(v)))].mean(1)*M
quant=lambda a:{f'q{int(q*100)}':float(np.quantile(a,q)) for q in (.05,.5,.95)}
res['bootstrap_independent_cell']=quant(ind);res['bootstrap_reported']=rep['stage1b_inventory']['bootstrap_total_q']
# Conditional empirical sensitivities only: preserve sharing of the same outer across evidence levels.
rng=np.random.default_rng([20261016,2]);paired=np.zeros(B)
for pop in pops:
 for sc in scens:
  ix=rng.integers(0,10,(B,10))
  for n in ns:paired+=np.nanmean(cell[pop,sc,n][ix],axis=1)*M
res['bootstrap_paired_n_within_population_scenario']=quant(paired)
# Whole nine-population dataset blocks; no claim this captures unseen tails or Monte Carlo uncertainty.
rng=np.random.default_rng([20261016,3]);joint=np.zeros(B)
for sc in scens:
 ix=rng.integers(0,10,(B,10))
 for pop in pops:
  for n in ns:joint+=np.nanmean(cell[pop,sc,n][ix],axis=1)*M
res['bootstrap_whole_outer_within_scenario']=quant(joint)
res['bootstrap_notes']='All resampling holds estimated costs and zero-hit lower substitutions fixed. These are sensitivity calculations, not calibrated budget intervals.'
# Direct binomial CDF inversion for the three largest one-hit rows, independently of beta quantiles.
def cdf(k,n,p):
 term=math.exp(n*math.log1p(-p));total=term
 for j in range(1,k+1):term*=((n-j+1)/j)*(p/(1-p));total+=term
 return total
def invcdf_p(k,n,target):
 lo=0.;hi=max(1.e-14,10.*(k+2)/n)
 while cdf(k,n,hi)>target:hi*=2
 for _ in range(100):
  mid=(lo+hi)/2
  if cdf(k,n,mid)>target:lo=mid
  else:hi=mid
 return (lo+hi)/2
iv=[]
for idx in (524,335,836):
 r=rows[idx];h=r['suffix_hits'];N=r['suffix_proposals'];lo=invcdf_p(h-1,N,.975);hi=invcdf_p(h,N,.025);cpp=r['cpu_seconds']/r['proposals']/3600
 iv.append({'index':idx,'hits':r['hits'],'suffix_hits':h,'point':cost[idx],'independent_retention_interval':[lo,hi],'saved_retention_interval':r['ci95_suffix'],'conditional_mean_cost_interval':[K*cpp/hi,K*cpp/lo]})
res['expensive_interval_reconstruction']=iv
worst=iv[0]
res['single_row_interval_sensitivity']={'index':worst['index'],'current_total':sum(sums.values()),'total_if_only_this_row_at_its_pointwise_upper_cost':sum(sums.values())+20*(worst['conditional_mean_cost_interval'][1]-worst['point']),'note':'Illustrative change in one cell mean; not a joint confidence bound or replacement forecast.'}
res['scenario_maximum_qualification']={'scenario':'null_prior_predictive','n':300,'reported_resolved_max':rep['cpu_hours_to_K']['by_scenario_n']['null_prior_predictive']['n=300']['q100'],'resolved_count':rep['cpu_hours_to_K']['by_scenario_n']['null_prior_predictive']['n=300']['n'],'planned_count':90,'omitted_zero_hit_row':242,'omitted_cost_lower':cost[242]}
res['nine_population_caps']={}
for n in (30,300):
 vals=[]
 for sc in scens:
  for t in range(10):
   rr=[r for r in rows if r['n']==n and r['outer']==f'{sc}/{t}']
   vals.append(max(cost[r['index']] for r in rr) if all(r['hits']>0 for r in rr) else None)
 res['nine_population_caps'][str(n)]={str(cap):sum(x is not None and x<=cap for x in vals) for cap in (10,25,50,100,250,500,1000)}
res['censored']=[{'index':r['index'],'proposals':r['proposals'],'hits':r['hits'],'point':cost[r['index']],'formal_interval_present':'ci95_suffix' in r,'sensitivity_interval_present':'sensitivity_interval95_suffix' in r} for r in rows if r['status']=='censored']
res['pilot_credit']={'already_used_cpu_hours':sum(r['cpu_seconds'] for r in rows)/3600,'gross_minus_used':sum(sums.values())-sum(r['cpu_seconds'] for r in rows)/3600,'note':'Gross inventory mixes from-scratch projections and one observed completed cost. Remaining-budget accounting must be stated separately; simple subtraction is illustrative.'}
res['elapsed_s']=time.perf_counter()-start
out=Path(__file__).with_name('cost_checks.json');out.write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res,indent=2))
