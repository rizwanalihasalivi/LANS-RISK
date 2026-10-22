"""Sequential stage execution, explicit exit records, no stale-PID assumptions."""
from pathlib import Path
import subprocess,os,json,fcntl,datetime
from audit_stage import audit
ROOT=Path('/workspace/recovery/restored/LANS-RISK');OP=Path('/workspace/recovery/operations');P='/workspace/recovery/venv/bin/python'
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',MPLCONFIGDIR='/workspace/recovery/mpl',NUMBA_CACHE_DIR='/workspace/recovery/numba-cache')
def event(**x):
 with (OP/'pipeline-events.jsonl').open('a') as f:f.write(json.dumps(dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),**x))+'\n')
def run(label,args,cwd=ROOT):
 event(stage=label,status='start',command=args,cwd=str(cwd))
 with (OP/(label+'.log')).open('ab') as f:
  result=subprocess.run([P,*args],cwd=cwd,stdout=f,stderr=subprocess.STDOUT)
 event(stage=label,status='exit',exit_code=result.returncode)
 result.check_returncode()
with (OP/'remaining.lock').open('w') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 with (OP/'confirmation.lock').open('a') as existing:
  fcntl.flock(existing,fcntl.LOCK_EX)
  audit('extended_baselines','confirmation')
 run('confirmation-analysis',['working/analyze_extended.py','confirmation'])
 run('stress-smoke',['working/stress_study/experiment.py','--stage','smoke','--workers','1'])
 run('stress-confirmation',['working/stress_study/experiment.py','--stage','confirmation','--workers','4'])
 audit('stress_study','confirmation')
 run('runtime',['working/publication_tools/runtime_profile.py'])
 run('observation-smoke',['working/observation_delay_study/run_study.py','--stage','smoke','--workers','1'])
 run('observation-evaluation',['working/observation_delay_study/run_study.py','--stage','evaluation','--workers','4'])
 audit('observation_delay_study','evaluation')
 run('publication',['working/publication_tools/build_results.py'])
 run('legacy-final-audit',['working/publication_tools/finalize_all.py'])
 event(status='all_planned_experiments_complete')
