from pathlib import Path
import fcntl,subprocess,os,json
OP=Path('/workspace/recovery/operations');P='/workspace/recovery/venv/bin/python'
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',MPLCONFIGDIR='/workspace/recovery/mpl',NUMBA_CACHE_DIR='/workspace/recovery/numba-cache')
with (OP/'delivery.lock').open('w') as own:
 fcntl.flock(own,fcntl.LOCK_EX|fcntl.LOCK_NB)
 with (OP/'remaining.lock').open('a') as previous:
  fcntl.flock(previous,fcntl.LOCK_EX)
  events=[json.loads(x) for x in (OP/'pipeline-events.jsonl').read_text().splitlines()]
  assert events[-1].get('status')=='all_planned_experiments_complete',events[-1]
  for script in ['scientific_analysis.py','final_report_and_package.py']:
   with (OP/(script+'.log')).open('ab') as log:
    subprocess.run([P,str(OP/script)],stdout=log,stderr=subprocess.STDOUT,check=True)
