from pathlib import Path
import time,subprocess,sys,os,json,datetime
OP=Path('/workspace/recovery/operations');R=Path('/workspace/recovery/restored/LANS-RISK');summary=R/'working/stress_study/amended_dense_merge_confirmation_SUMMARY.json'
while not summary.exists():
 try:os.kill(68621,0)
 except ProcessLookupError:raise SystemExit('Amendment runner stopped without complete summary; inspect log and resume verified pairs')
 time.sleep(10)
for script,log in [('scientific_analysis_completed.py','final-analysis.log'),('prepare_completed_report.py','final-validation.log'),('independent_final_validation.py','final-independent-validation.log')]:
 print('START',script,datetime.datetime.now(datetime.timezone.utc).isoformat(),flush=True)
 with (OP/log).open('w') as stream:
  subprocess.run([sys.executable,str(OP/script)],stdout=stream,stderr=subprocess.STDOUT,check=True,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','MPLCONFIGDIR':'/workspace/recovery/cache/matplotlib'})
 print('PASS',script,flush=True)
print('All scientific analyses and independent numerical validations finished',flush=True)
