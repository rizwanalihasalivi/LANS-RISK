"""Independent audit of 231 original and 33 approved-amendment conditions."""
from pathlib import Path
import json,hashlib,math,datetime,subprocess,sys
from audit_stage import R,OP,SC,FREE,sha
FIELDS=['profile','scenario','controller','actor_seed','delay_ms']
def audit_completed():
 subprocess.run([sys.executable,str(OP/'audit_partial_stress.py')],check=True)
 root=R/'working/stress_study';desc=json.loads((OP/'DENSE_MERGE_AMENDMENT.json').read_text());stage=desc['stage']
 candidate=Path(desc['source_files']['benchmark_attempts_200000.py'])
 source=R/'working/traffic_v2/benchmark.py'
 assert candidate.read_text()==source.read_text().replace('range(10000)','range(200000)'), 'Amendment must be exactly one cap substitution'
 assert source.read_text().count('range(10000)')==1
 freeze=json.loads((root/'FREEZE.json').read_text());source_map=dict(freeze)
 for name,path in desc['source_files'].items():source_map['_approved_amendment/'+name]=sha(Path(path))
 assert source_map==desc['source_hashes']
 fp=hashlib.sha256(json.dumps(source_map,sort_keys=True).encode()).hexdigest();assert fp==desc['source_hash']
 for name,h in freeze.items():assert sha(R/'working'/name)==h,name
 original=json.loads((OP/'STRESS_ORIGINAL_231_HASHES.json').read_text());assert len(original)==462
 for name,h in original.items():assert sha(R/name)==h,name
 expected={('denser_traffic','merge',c,k,d) for c in ['predictor_lqr','cbf','robust_mpc','lans','mpc_nominal','lqr','lqr_acc'] for k in ([0] if c in FREE else [42,43,44]) for d in [0,500,1000]}
 summaries=json.loads((root/(stage+'_SUMMARY.json')).read_text());assert len(summaries)==33
 seen=set();unique=set();manifest={};combined=[]
 for path in sorted((root/stage).glob('*.json')):
  x=json.loads(path.read_text());key=tuple(x[n] for n in FIELDS)
  assert key in expected and key not in seen;seen.add(key)
  assert x in summaries and x['source_hash']==fp and x['count']==50 and x['first']==161000
  assert path.name==f'{key[0]}_{key[1]}_{key[2]}_{key[3]}_{key[4]//100}.json'
  raw=path.with_suffix('.jsonl');assert sha(raw)==x['raw_sha256']
  rr=[json.loads(line) for line in raw.read_text().splitlines()]
  assert len(rr)==50 and [r['episode_seed'] for r in rr]==list(range(161000,161050))
  for r in rr:
   assert set(r)=={'episode_seed','collision','completion','corridor_completion','rmse'}
   assert isinstance(r['episode_seed'],int)
   for m in ['collision','completion','corridor_completion']:assert isinstance(r[m],bool)
   assert math.isfinite(r['rmse']) and r['rmse']>=0
   assert not r['completion'] or not r['collision']
   assert not r['corridor_completion'] or r['completion']
   record=key+(r['episode_seed'],);assert record not in unique;unique.add(record)
  for m in ['collision','completion','corridor_completion']:assert math.isclose(x[m],100*sum(r[m] for r in rr)/50,abs_tol=1e-10)
  for p in [path,raw]:manifest[str(p.relative_to(R))]=sha(p)
  combined.append(dict(**x,source_version='approved_initialization_amendment',source_stage=stage))
 assert seen==expected and len(unique)==1650 and len(list((root/stage).glob('*.jsonl')))==33
 old=json.loads((OP/'STRESS_ORIGINAL_PARTIAL_SUMMARY.json').read_text())
 combined.extend(dict(**x,source_version='original_frozen',source_stage='confirmation') for x in old)
 all_expected={(p,s,c,k,d) for p in ['weaker_actuation','denser_traffic'] for s in SC for c in ['predictor_lqr','cbf','robust_mpc','lans','mpc_nominal','lqr','lqr_acc'] for k in ([0] if c in FREE else [42,43,44]) for d in [0,500,1000]}
 assert len(combined)==264 and {tuple(x[n] for n in FIELDS) for x in combined}==all_expected
 (OP/'ROBUSTNESS_COMBINED_SUMMARY.json').write_text(json.dumps(sorted(combined,key=lambda x:tuple(x[n] for n in FIELDS)),indent=2))
 out=dict(status='COMPLETE_WITH_DISCLOSED_APPROVED_INITIALIZATION_AMENDMENT',verified_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),original_conditions=231,amended_conditions=33,total_conditions=264,total_records=13200,amended_records=1650,original_frozen_stage_complete=False,approved_amended_plan_complete=True,original_frozen_files_verified=len(freeze),original_result_files_preserved=len(original),amendment_is_exact_one_line_cap_change=True,source_hash=fp,unique_condition_episode_keys=True,traffic_seed_range=[161000,161049],manifest={**original,**manifest})
 (OP/'AUDIT_COMPLETED_ROBUSTNESS.json').write_text(json.dumps(out,indent=2));print('AUDIT PASS robustness:231original+33amended,13200records,originals unchanged',flush=True)
 return out
if __name__=='__main__':audit_completed()
