"""Restore verified original and approved amended pairs without overwriting conflicts."""
from pathlib import Path
import argparse,hashlib,json,shutil

def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def restore(repo,project):
 originals=json.loads((repo/'recovery_results/CHECKPOINT_MANIFEST.json').read_text())
 amendment=json.loads((repo/'completion_results/CHECKPOINT_MANIFEST.json').read_text())
 assert amendment['complete'] and amendment['amended_conditions']==33, 'Require a fully verified final checkpoint'
 descriptor=json.loads((repo/'completion_results/operations/DENSE_MERGE_AMENDMENT.json').read_text())
 for name,h in descriptor['source_hashes'].items():
  if not name.startswith('_approved_amendment/'):
   assert digest(project/'working'/name)==h,('frozen source mismatch',name)
 planned=[]
 for folder,manifest in [('recovery_results',originals),('completion_results',amendment)]:
  for name,h in manifest['sha256'].items():
   relative=Path(name);assert not relative.is_absolute() and '..' not in relative.parts
   src=repo/folder/relative;dst=project/relative
   assert digest(src)==h,('backup hash mismatch',src)
   assert not dst.exists() or digest(dst)==h,('refusing conflicting overwrite',dst)
   planned.append((src,dst))
 for src,dst in planned:
  if not dst.exists():dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
 # Recreate stage summaries solely from verified metadata, without changing sources.
 for folder,stage in [('extended_baselines','confirmation'),('stress_study','amended_dense_merge_confirmation'),('observation_delay_study','evaluation')]:
  files=sorted((project/'working'/folder/stage).glob('*.json'))
  rows=[json.loads(p.read_text()) for p in files];summary=project/'working'/folder/(stage+'_SUMMARY.json')
  if summary.exists():
   old=json.loads(summary.read_text());assert sorted(map(lambda x:json.dumps(x,sort_keys=True),old))==sorted(map(lambda x:json.dumps(x,sort_keys=True),rows)),('summary conflict',summary)
  else:summary.write_text(json.dumps(rows,indent=2))
 print(json.dumps({'verified_result_files':len(planned),'amended_conditions':amendment['amended_conditions'],'conflicts':0,'frozen_source_files_unchanged':True}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,required=True);p.add_argument('--project',type=Path,required=True);a=p.parse_args();restore(a.repository.resolve(),a.project.resolve())
