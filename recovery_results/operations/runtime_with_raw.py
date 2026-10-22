"""Run unchanged timing code; retain its post-loop sample array before reduction.
The hook operates only on the final median reduction, outside the timed calls.
"""
from pathlib import Path
import sys,runpy,json,datetime,os
for name in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[name]='1'
import numpy as np
R=Path('/workspace/recovery/restored/LANS-RISK');OP=Path('/workspace/recovery/operations')
# Initialize numerical-library registrations before the post-processing hook.
sys.path.insert(0,str(R/'working/extended_baselines'))
import experiment
profile=R/'working/publication_tools/runtime_profile.py';original=np.median;samples=[]
partial=(OP/('runtime_samples_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+str(os.getpid())+'.jsonl')).open('x')
def retain(a,*args,**kwargs):
 frame=sys._getframe(1)
 if Path(frame.f_code.co_filename)==profile:
  loc=frame.f_locals
  assert len(a)==50 and loc['step']==69
  samples.append(dict(scenario=loc['scenario'],controller=loc['method'],delay_ms=loc['delay']*100,samples_ms=[float(x) for x in a]))
  partial.write(json.dumps(samples[-1])+'\n');partial.flush();os.fsync(partial.fileno())
 return original(a,*args,**kwargs)
np.median=retain
try:runpy.run_path(str(profile),run_name='__main__')
finally:
 np.median=original
 partial.close()
from audit_stage import SC,METHODS
assert len(samples)==96
result=json.loads((R/'deliverables/publication_results/runtime_profile.json').read_text());seen=set()
for s in samples:
 key=s['scenario'],s['controller'],s['delay_ms'];assert key not in seen;seen.add(key)
 r=next(x for x in result['results'] if (x['scenario'],x['controller'],x['delay_ms'])==key)
 a=np.array(s['samples_ms']);assert len(a)==r['n']==50 and np.isfinite(a).all()
 for k,v in [('median_ms',np.median(a)),('p95_ms',np.quantile(a,.95)),('p99_ms',np.quantile(a,.99)),('max_ms',max(a))]:assert float(v)==r[k],(key,k)
 assert int((a>100).sum())==r['exceeded_100ms']
assert seen=={(s,c,d) for s in SC for c in METHODS for d in [0,1000]}
out=dict(time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='50 warmed samples per condition from the unchanged runtime_profile.py. Retained at its post-loop median reduction; no clock, controller, model, seed, or timing-loop changes.',conditions=96,timed_samples=4800,source_hashes=result['source_hashes'],samples=samples)
(OP/'runtime_samples.json').write_text(json.dumps(out,indent=2));print('PASS: all4800raw timing samples retained; every runtime statistic recomputed exactly')
