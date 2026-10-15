"""Local metadata reconciliation only; scientific/numerical checks ran on deep-server."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];P1=ROOT/'analysis/fable/calibration/v2_dev/p1';AUDIT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((AUDIT/'remote_checks.json').read_text());b=json.loads((P1/'p1_bound.json').read_text())
remote=r['sha256'];matches={}
for name in ('p1_bound.json','p1_scan.json','p1_pilot.json'):
 matches[name]=sha(P1/name)==remote['/data/fable/vortex/v2_dev/p1/'+name]
assert all(matches.values())
assert sha(P1.parent/'p1_sampler.py')==b['helper_sha256']==remote['/data/fable/vortex/v2_dev/p1_sampler.py']
assert all(sha(ROOT/path)==h for path,h in r['source_files_verified'].items())
localtext=(P1/'test.log').read_text();replaytext=(AUDIT/'canonical_test_replay.log').read_text()
dec=json.JSONDecoder();a,_=dec.raw_decode(localtext);z,_=dec.raw_decode(replaytext);assert a==z
p=json.loads((P1/'p1_pilot.json').read_text());scan=json.loads((P1/'p1_scan.json').read_text());cost=json.loads((P1/'p1_cost_projection.json').read_text())
for row in cost:
 s=p['settings'][str(row['setting'])];f=scan['settings'][str(row['setting'])]['forecast_retained_per_prior_proposal']
 assert abs(row['forecast_hits']-f*s['proposals'])<1e-12
 assert abs(row['theta_acceptance']-s['theta_accept']/s['proposals'])<1e-12
assert len(b['settings'])==20 and len(set(s['index'] for s in b['settings']))==20
result={'scope':__doc__,'reviewed_sampler_commit':'b781db17921008724e15f0eca671ea3b767964ef','local_HEAD_at_check':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'local_remote_artifacts_equal':matches,'helper_and_12_frozen_source_files_equal':True,'canonical_test_JSON_exact_replay':True,'all_cost_forecast_denominators_match_actual_proposals':True,'settings':20}
(AUDIT/'local_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
