from pathlib import Path
import json,hashlib,datetime
R=Path('/workspace/recovery/restored/LANS-RISK');OP=Path('/workspace/recovery/operations')
results={}
for folder,stage,total in [('extended_baselines','confirmation',440),('stress_study','confirmation',264),('observation_delay_study','evaluation',200)]:
 seen=set();records=0
 for p in (R/'working'/folder/stage).glob('*.json'):
  try:
   x=json.loads(p.read_text());b=p.with_suffix('.jsonl').read_bytes()
   assert hashlib.sha256(b).hexdigest()==x['raw_sha256']
   rr=[json.loads(line) for line in b.splitlines()];assert len(rr)==x['count']
   key=tuple(x.get(f) for f in ['profile','scenario','controller','policy_seed','actor_seed','delay_ms']);assert key not in seen;seen.add(key)
   assert [v['episode_seed'] for v in rr]==list(range(x['first'],x['first']+x['count']))
   records+=len(rr)
  except json.JSONDecodeError:continue
 results[folder]=dict(verified_pairs=len(seen),expected=total,records=records)
print(json.dumps(results))
p=OP/'pipeline-events.jsonl'
if p.exists():print('Pipeline:',p.read_text().splitlines()[-1])
q=OP/'REMOTE_CHECKPOINTS.jsonl'
if q.exists():
 x=json.loads(q.read_text().splitlines()[-1]);print('Remote:',x['conditions'],x['commit'])
for p in ['remaining_stages.log','finish_delivery.log','scientific_analysis.py.log','final_report_and_package.py.log']:
 path=OP/p
 if path.exists() and path.stat().st_size:print(p, '\n'.join(path.read_text().splitlines()[-2:]))
