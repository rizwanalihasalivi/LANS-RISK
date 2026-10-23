from pathlib import Path
import os,subprocess,json,datetime,fcntl
from audit_stage import audit
R=Path('/workspace/recovery/restored/LANS-RISK');OP=Path('/workspace/recovery/operations');P='/workspace/recovery/venv/bin/python'
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',MPLCONFIGDIR='/workspace/recovery/mpl',NUMBA_CACHE_DIR='/workspace/recovery/numba-cache')
def event(**x):
 with (OP/'pipeline-events.jsonl').open('a') as f:f.write(json.dumps(dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),**x))+'\n')
def run(label,args):
 event(stage=label,status='start',command=args)
 with (OP/(label+'.log')).open('ab') as log:code=subprocess.run([P,*args],cwd=R,stdout=log,stderr=subprocess.STDOUT).returncode
 event(stage=label,status='exit',exit_code=code)
 if code:raise RuntimeError((label,code))
with (OP/'remaining.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 run('runtime',[str(OP/'runtime_with_raw.py')])
 run('observation-smoke',['working/observation_delay_study/run_study.py','--stage','smoke','--workers','1'])
 run('observation-evaluation',['working/observation_delay_study/run_study.py','--stage','evaluation','--workers','4'])
 audit('observation_delay_study','evaluation')
 event(status='independent_stages_complete_stress_blocker_pending')
