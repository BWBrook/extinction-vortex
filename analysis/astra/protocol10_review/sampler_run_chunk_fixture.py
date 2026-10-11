"""Mocked two-trial protocol 0.10 stress fixture; no R or remote compute."""
import pathlib,os,sys,json,tempfile
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[3]
os.chdir(ROOT)
CAL=ROOT/'analysis/fable/calibration'
sys.path.insert(0,str(CAL))
import e2e_benchmark as e
from bank import designs
pops=list(designs()); des={n:{'years':[0,1,2,3],'counts':np.array([20,12,4,0])} for n in pops}
class Tree:
    def query(self,x,k): return np.array([0.,1.,2.]),np.arange(k)
banks={n:{'tree':Tree(),'keep':np.array([True]*3),'mad':np.ones(3),'dropped':[],
          'rec':np.array([[20,12,4,0],[20,9,3,1],[20,14,2,0]])} for n in pops}
source=json.load(open(CAL/'freeze_v1/stress_sets.json'))['sets']
stress={tid:{n:source[tid][n]['theta'] for n in pops} for tid in ('0','1')}
seen=[]; fits=[]
def fresh(d,variant,rng,beta,fixed,drift,det,budget):
    seen.append(dict(fixed)); idx=len(seen)-1
    if idx==0: return None
    return {'recorded':[20,12,4,0],'params':dict(fixed),'draws':budget}
e.fresh_selected=fresh
e.run_fits=lambda inp,outp,workers:fits.append(inp)
rng=np.random.default_rng(8); T=rng.normal(size=(21,4))
e.read_T=lambda path,R:(T,np.zeros(21),np.zeros(21))
with tempfile.TemporaryDirectory(prefix='protocol10_chunk_') as td:
    e.run_chunk(banks,des,'ar_cat',td,[0,1],10,3,1,80,stress=stress,budget=1000000)
    rows=[json.loads(line) for line in open(pathlib.Path(td)/'e2e_rows.jsonl')]
assert [r['trial_id'] for r in rows]==[0,1]
assert rows[0]['outcome']=='indet_sampling' and rows[0]['sampling_failed']==[pops[0]]
assert rows[0]['fixed']=={pops[0]:stress['0'][pops[0]]}
assert seen==[stress[tid][n] for tid in ('0','1') for n in pops]
assert len(fits)==1 and fits[0].endswith('sets_1.csv')
assert rows[1]['outcome'] in ('accept','reject','indet_straddle')
assert all(rows[1]['selected'][n]['params']==stress['1'][n] for n in pops)
print(json.dumps({'intended_trials':2,'retained_trials':2,'calls':len(seen),'parameter_inputs_exact':True,'replacement':False,'fits':len(fits),'success_retains_intended_theta':True},indent=2))
