from pathlib import Path
import json,hashlib,math
from audit_stage import R,OP,SC,FREE
root=R/'working/stress_study';freeze=json.loads((root/'FREEZE.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name,h in freeze.items():assert sha(R/'working'/name)==h
fingerprint=hashlib.sha256(json.dumps(freeze,sort_keys=True).encode()).hexdigest()
methods=['predictor_lqr','cbf','robust_mpc','lans','mpc_nominal','lqr','lqr_acc']
expected={(p,s,c,k,d) for p in ['weaker_actuation','denser_traffic'] for s in SC for c in methods for k in ([0] if c in FREE else [42,43,44]) for d in [0,500,1000]}
seen=set();unique=set();manifest={};summaries=[]
for p in (root/'confirmation').glob('*.json'):
 x=json.loads(p.read_text());key=tuple(x[k] for k in ['profile','scenario','controller','actor_seed','delay_ms']);assert key in expected and key not in seen;seen.add(key)
 assert p.name==f"{key[0]}_{key[1]}_{key[2]}_{key[3]}_{key[4]//100}.json"
 assert x['count']==50 and x['first']==161000 and x['source_hash']==fingerprint
 raw=p.with_suffix('.jsonl');assert sha(raw)==x['raw_sha256'];rr=[json.loads(v) for v in raw.read_text().splitlines()]
 assert len(rr)==50 and [v['episode_seed'] for v in rr]==list(range(161000,161050))
 for a in rr:
  assert math.isfinite(a['rmse']) and a['rmse']>=0
  assert not a['completion'] or not a['collision']
  assert not a['corridor_completion'] or (a['completion'] and not a['collision'])
  k=key+(a['episode_seed'],);assert k not in unique;unique.add(k)
 for m in ['collision','completion','corridor_completion']:assert math.isclose(x[m],100*sum(a[m] for a in rr)/50,abs_tol=1e-10)
 for q in [p,raw]:manifest[str(q.relative_to(R))]=sha(q)
 summaries.append(x)
missing=expected-seen;assert len(seen)==231 and len(unique)==11550 and len(missing)==33
assert all(k[:2]==('denser_traffic','merge') for k in missing)
assert len(list((root/'confirmation').glob('*.jsonl')))==231
out=dict(status='INCOMPLETE_FROZEN_STAGE',verified_conditions=231,expected_conditions=264,verified_records=11550,expected_records=13200,missing_conditions=sorted(missing),frozen_source_files_verified=len(freeze),source_hash=fingerprint,saved_outcome_aggregates_recomputed=True,reason='Frozen initialization rejection cap exhausted; do not treat uninitialized cases as controller collisions or completed episodes',manifest=manifest)
(OP/'AUDIT_STRESS_ORIGINAL_PARTIAL.json').write_text(json.dumps(out,indent=2));(OP/'STRESS_ORIGINAL_PARTIAL_SUMMARY.json').write_text(json.dumps(summaries,indent=2));print('PASS:231complete frozen-source conditions/11550records; exactly33dense-Merge conditions blocked')
