"""Proposal-only preflight; never launches controller experiments or changes originals."""
from pathlib import Path
import sys,json,importlib.util,hashlib,time
R=Path('/workspace/recovery/restored/LANS-RISK');OP=Path('/workspace/recovery/operations');HERE=Path(__file__).resolve().parent
p=R/'working/stress_study/experiment.py';spec=importlib.util.spec_from_file_location('stress_original_preflight',p);original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
source=R/'working/traffic_v2/benchmark.py';candidate=HERE/'benchmark_attempts_200000.py'
ns={'__file__':str(source),'__name__':'proposal_traffic_cap'};exec(compile(candidate.read_text(),str(candidate),'exec'),ns)
class CandidateEnv(ns['TrafficEnv']):
 def __init__(self):
  super().__init__('merge',delay=0,direct=True)
  self.profile='denser_traffic';self.config=self.config.copy();self.config['nominal_npcs']+=1
failed={x['seed'] for x in json.loads((OP/'STRESS_SPAWN_DIAGNOSIS.json').read_text()) if x['scenario']=='merge'}
def state(env):return [[*v.position,float(v.heading),float(v.velocity),float(v.desired_speed)] for v in [env.ego,*env.npcs]]
results=[]
for seed in range(161000,161050):
 start=time.monotonic();env=CandidateEnv();env.reset(seed=seed)
 assert len(env.npcs)==7
 minimum=min(float(original.np.linalg.norm(a.position-b.position)) for i,a in enumerate([env.ego,*env.npcs]) for b in [env.ego,*env.npcs][i+1:]);assert minimum>6
 snapshot=state(env);identical=None
 if seed not in failed:
  old=original.StressEnv('merge',0,'denser_traffic');old.reset(seed=seed);assert snapshot==state(old);old.close();identical=True
 results.append(dict(seed=seed,accepted=True,minimum_initial_pair_distance_m=minimum,original_limit_exhausted=seed in failed,identical_to_original_when_original_accepts=identical,preflight_seconds=time.monotonic()-start))
 print(seed,'PASS',flush=True);env.close()
out=dict(status='PROPOSAL_ONLY_NOT_APPLIED',tested_seeds=50,accepted=50,original_failures=len(failed),unchanged_original_success_cases=sum(x['identical_to_original_when_original_accepts'] is True for x in results),candidate_sha256=hashlib.sha256(candidate.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),results=results)
(HERE/'INITIALIZATION_AMENDMENT_PREFLIGHT.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='results'}),flush=True)
