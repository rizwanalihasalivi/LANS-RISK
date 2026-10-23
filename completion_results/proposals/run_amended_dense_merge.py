"""Separate, explicitly approved sampler-amendment study. Original files stay frozen."""
from pathlib import Path
import os,sys,json,hashlib,argparse,importlib.util,multiprocessing
from concurrent.futures import ProcessPoolExecutor,as_completed
for name in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[name]='1'
R=Path('/workspace/recovery/restored/LANS-RISK');OP=Path('/workspace/recovery/operations');HERE=Path(__file__).resolve().parent
STAGE='amended_dense_merge_confirmation'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=R/'working/stress_study/experiment.py';spec=importlib.util.spec_from_file_location('stress_amended_core',p);core=importlib.util.module_from_spec(spec);sys.modules[spec.name]=core;spec.loader.exec_module(core)
candidate=HERE/'benchmark_attempts_200000.py'
ns={'__file__':str(R/'working/traffic_v2/benchmark.py'),'__name__':'amended_traffic_cap'};exec(compile(candidate.read_text(),str(candidate),'exec'),ns)
class AmendedMergeEnv(ns['TrafficEnv']):
 def __init__(self,scenario,delay,profile):
  assert scenario=='merge' and profile=='denser_traffic'
  super().__init__(scenario,delay=delay,direct=True)
  self.profile=profile;self.config=self.config.copy();self.config['nominal_npcs']+=1
original_hashes=core.hashes
amendment_files=[candidate,Path(__file__).resolve(),HERE/'AMENDMENT_PROTOCOL.md']
def amended_hashes():
 h=original_hashes()
 for path in amendment_files:h['_approved_amendment/'+path.name]=sha(path)
 return h

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--approved-initialization-amendment',action='store_true');parser.add_argument('--approval-note',required=True);parser.add_argument('--workers',type=int,default=4);args=parser.parse_args()
 if not args.approved_initialization_amendment:raise SystemExit('Explicit user approval is required; proposal not run')
 base_freeze=json.loads((core.ROOT/'FREEZE.json').read_text());assert original_hashes()==base_freeze
 preflight=json.loads((HERE/'INITIALIZATION_AMENDMENT_PREFLIGHT.json').read_text());assert preflight['accepted']==50 and preflight['candidate_sha256']==sha(candidate)
 originals={str(p.relative_to(R)):sha(p) for p in (core.ROOT/'confirmation').glob('*') if p.is_file()}
 assert len(originals)==462
 assert not any(p.name.startswith('denser_traffic_merge_') for p in (core.ROOT/'confirmation').glob('*.json'))
 (OP/'STRESS_ORIGINAL_231_HASHES.json').write_text(json.dumps(originals,indent=2))
 core.StressEnv=AmendedMergeEnv;core.hashes=amended_hashes
 source_map=amended_hashes();fingerprint=hashlib.sha256(json.dumps(source_map,sort_keys=True).encode()).hexdigest()
 descriptor=dict(status='approved_initialization_amendment',approval_note=args.approval_note,original_conditions_preserved=231,amended_conditions=33,amended_records=1650,stage=STAGE,original_attempt_limit=10000,amended_attempt_limit=200000,source_hash=fingerprint,source_hashes=source_map,original_source_hash=hashlib.sha256(json.dumps(base_freeze,sort_keys=True).encode()).hexdigest(),source_files={p.name:str(p) for p in amendment_files},preflight_sha256=sha(HERE/'INITIALIZATION_AMENDMENT_PREFLIGHT.json'),scope='Only denser Merge; unchanged traffic seeds, safety predicates, physical settings, models and controllers; separate source version')
 (OP/'DENSE_MERGE_AMENDMENT.json').write_text(json.dumps(descriptor,indent=2))
 jobs=[(STAGE,'denser_traffic','merge',c,k,d,50,161000) for c in core.METHODS for k in ([0] if c in core.base.ACTOR_FREE else [42,43,44]) for d in [0,5,10]];assert len(jobs)==33
 results=[]
 with ProcessPoolExecutor(args.workers,mp_context=multiprocessing.get_context('fork')) as pool:
  for future in as_completed([pool.submit(core.evaluate,j) for j in jobs]):
   x=future.result();results.append(x);print(json.dumps(x),flush=True)
 assert len(results)==33
 for x in results:
  assert x['source_hash']==fingerprint and x['count']==50 and x['first']==161000
  raw=core.ROOT/STAGE/f"{x['profile']}_{x['scenario']}_{x['controller']}_{x['actor_seed']}_{x['delay_ms']//100}.jsonl"
  assert sha(raw)==x['raw_sha256'];rr=[json.loads(v) for v in raw.read_text().splitlines()];assert len(rr)==50 and [r['episode_seed'] for r in rr]==list(range(161000,161050))
 for name,h in originals.items():assert sha(R/name)==h
 assert original_hashes()==base_freeze
 (core.ROOT/(STAGE+'_SUMMARY.json')).write_text(json.dumps(results,indent=2))
 print('COMPLETE approved separate amendment:33conditions/1650records; all231original conditions and original sources preserved',flush=True)
if __name__=='__main__':main()
