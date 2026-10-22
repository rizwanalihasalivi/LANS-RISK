"""Independent coverage/hash/metric audit; never changes experiment outputs."""
import sys,json,hashlib,math
from pathlib import Path
R=Path('/workspace/recovery/restored/LANS-RISK')
OP=Path('/workspace/recovery/operations')
SC=['highway','merge','intersection','roundabout']
METHODS=['predictor_lqr','cbf','robust_mpc','ppo_only','lans_no_prediction','lans','mpc_nominal','lqr','lqr_acc','robust_lans','robust_no_actor','lans_no_actor']
FREE={'predictor_lqr','robust_mpc','mpc_nominal','lqr','lqr_acc','robust_no_actor','lans_no_actor'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def audit(folder,stage):
 root=R/'working'/folder
 if folder=='extended_baselines':
  assert stage in ['development','confirmation']
  n,first=(100,141000) if stage=='confirmation' else (20,121000)
  expected={(s,c,k,d) for s in SC for c in METHODS for k in ([0] if c in FREE else ([42,43,44] if stage=='confirmation' else [42])) for d in [0,200,500,700,1000]}
  fields=['scenario','controller','policy_seed','delay_ms']
  freeze=json.loads((root/'EXTENDED_FREEZE.json').read_text())['sha256']
 elif folder=='stress_study':
  n,first=50,161000
  expected={(p,s,c,k,d) for p in ['weaker_actuation','denser_traffic'] for s in SC for c in ['predictor_lqr','cbf','robust_mpc','lans','mpc_nominal','lqr','lqr_acc'] for k in ([0] if c in FREE else [42,43,44]) for d in [0,500,1000]}
  fields=['profile','scenario','controller','actor_seed','delay_ms'];freeze=json.loads((root/'FREEZE.json').read_text())
 else:
  n,first=20,181000
  expected={(p,s,c,k) for p in ['uniform','bimodal','bursty','triangular','exponential'] for s in SC for c in ['lans','mpc_nominal','predictor_lqr','cbf','robust_mpc','lqr_acc'] for k in ([0] if c in FREE else [42,43,44])}
  fields=['profile','scenario','controller','actor_seed'];freeze=json.loads((root/'FREEZE.json').read_text())
 for name,h in freeze.items():assert sha(R/'working'/name)==h,name
 fp=hashlib.sha256(json.dumps(freeze,sort_keys=True).encode()).hexdigest()
 summaries=json.loads((root/(stage+'_SUMMARY.json')).read_text())
 assert len(summaries)==len(expected)
 files=list((root/stage).glob('*.json'));assert len(files)==len(expected)
 seen=set();unique=set();manifest={};metrics=0
 for path in files:
  x=json.loads(path.read_text());key=tuple(x[k] for k in fields)
  assert key in expected and key not in seen,key
  seen.add(key)
  assert x['count']==n and x['first']==first and x['source_hash']==fp
  raw=path.with_suffix('.jsonl');assert sha(raw)==x['raw_sha256']
  rr=[json.loads(line) for line in raw.read_text().splitlines()]
  assert len(rr)==n and [a['episode_seed'] for a in rr]==list(range(first,first+n))
  for a in rr:
   composite=key+(a['episode_seed'],);assert composite not in unique;unique.add(composite)
   for m,v in a.items():
    if isinstance(v,(float,int)):assert math.isfinite(v),(path,m)
   assert not a['completion'] or not a['collision']
   assert not a['corridor_completion'] or (a['completion'] and not a['collision'])
  for m in ['collision','completion','corridor_completion','corridor_exceedance','timeout']:
   if m in x:assert math.isclose(x[m],100*sum(a[m] for a in rr)/n,abs_tol=1e-10),(path,m)
  for m in ['progress','rmse','decision_ms_median','no_feasible_steps','npc_position_error_cv','npc_position_error_accel']:
   if m in x:assert math.isclose(x[m],sum(a[m] for a in rr)/n,rel_tol=1e-12,abs_tol=1e-12),(path,m)
  assert x in summaries
  manifest[str(path.relative_to(R))]=sha(path);manifest[str(raw.relative_to(R))]=sha(raw);metrics+=1
 assert seen==expected
 assert len(list((root/stage).glob('*.jsonl')))==len(expected)
 if folder=='extended_baselines' and stage=='confirmation':
  original=json.loads((R/'resume_operations/20261022T101858Z/PREFLIGHT.json').read_text())
  for p,h in original['existing_result_hashes'].items():assert sha(R/p)==h,('original batch changed',p)
 out=dict(folder=folder,stage=stage,conditions=len(seen),records=len(unique),frozen_hashes_verified=len(freeze),all_original_261_preserved=folder=='extended_baselines' and stage=='confirmation',all_metrics_recomputed=True,manifest=manifest)
 (OP/f'AUDIT_{folder}_{stage}.json').write_text(json.dumps(out,indent=2))
 print('AUDIT PASS',folder,stage,len(seen),len(unique),flush=True)
 return out
if __name__=='__main__':audit(*sys.argv[1:])
