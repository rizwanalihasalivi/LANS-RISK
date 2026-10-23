"""Incremental backup of complete approved-amendment pairs; preserve recovery_results."""
from pathlib import Path
import json,hashlib,subprocess,datetime,shutil
R=Path('/workspace/recovery/restored/LANS-RISK');OP=Path('/workspace/recovery/operations');REPO=Path('/workspace/LANS-RISK');DEST=REPO/'completion_results';STAGE='amended_dense_merge_confirmation';BRANCH='integration/aris-frozen-workflow'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(REPO),*args],text=True,stderr=subprocess.STDOUT).strip()
def checkpoint(final=False):
 assert git('branch','--show-current')==BRANCH
 descriptor=json.loads((OP/'DENSE_MERGE_AMENDMENT.json').read_text());manifest={};n=0
 for p in sorted((R/'working/stress_study'/STAGE).glob('*.json')):
  x=json.loads(p.read_text());raw=p.with_suffix('.jsonl')
  assert x['source_hash']==descriptor['source_hash'] and sha(raw)==x['raw_sha256'] and x['count']==50 and x['first']==161000
  rr=[json.loads(v) for v in raw.read_text().splitlines()];assert len(rr)==50 and [v['episode_seed'] for v in rr]==list(range(161000,161050))
  for src in [p,raw]:
   relative=src.relative_to(R);dst=DEST/relative;dst.parent.mkdir(parents=True,exist_ok=True)
   if dst.exists():assert sha(dst)==sha(src)
   else:shutil.copyfile(src,dst)
   manifest[str(relative)]=sha(src)
  n+=1
 ops=DEST/'operations';ops.mkdir(parents=True,exist_ok=True)
 names=['AMENDMENT_APPROVAL.json','DENSE_MERGE_AMENDMENT.json','STRESS_ORIGINAL_231_HASHES.json','amended-dense-merge.log','audit_completed_robustness.py','scientific_analysis_completed.py','checkpoint_completion.py']
 if final:names += ['AUDIT_COMPLETED_ROBUSTNESS.json','ROBUSTNESS_COMBINED_SUMMARY.json','FINAL_COMPLETENESS_AUDIT.json','independent_final_validation.py','FINAL_INDEPENDENT_VALIDATION.json','prepare_completed_report.py','package_completed_results.py','final-analysis.log','final-validation.log','final-independent-validation.log','restore_completed_checkpoint.py','verify_completed_remote.py','finish_approved_plan.py','refresh_aris_final.py','render_final_report.py','test_amended_dynamics.py','AMENDED_DYNAMICS_REGRESSION.json','amended-dynamics-regression.log','write_final_index.py','AMENDMENT_HOST_EVIDENCE.json','START_HERE_COMPLETED_ENVIRONMENT.md','install_completed_environment.sh','render_publication_tables.py','final-table-layout.log']
 for name in names:
  p=OP/name
  if p.exists():shutil.copyfile(p,ops/name)
 shutil.copytree(OP/'proposals',DEST/'proposals',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
 if final:
  assert n==33
  shutil.copytree(OP/'final_verified_results',DEST/'results',dirs_exist_ok=True)
  shutil.copyfile(R/'working/stress_study'/(STAGE+'_SUMMARY.json'),DEST/'working/stress_study'/(STAGE+'_SUMMARY.json'))
 meta=dict(time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),amended_conditions=n,amended_records=50*n,original_conditions=231,combined_conditions=231+n,complete=final,sha256=manifest)
 (DEST/'CHECKPOINT_MANIFEST.json').write_text(json.dumps(meta,indent=2))
 git('add','--','completion_results')
 if git('diff','--cached','--name-only'):git('commit','-m',f'Preserve approved dense-Merge amendment: {n}/33 verified conditions'+(' and final analyses' if final else ''))
 git('push','origin',f'HEAD:refs/heads/{BRANCH}')
 commit=git('rev-parse','HEAD');assert git('ls-remote','origin',f'refs/heads/{BRANCH}').split()[0]==commit
 event=dict(**meta,commit=commit,branch=BRANCH);event.pop('sha256')
 with (OP/'COMPLETION_REMOTE_CHECKPOINTS.jsonl').open('a') as f:f.write(json.dumps(event)+'\n')
 print(json.dumps(event),flush=True)
if __name__=='__main__':
 import sys
 checkpoint('--final' in sys.argv)
