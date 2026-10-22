"""One final explicit checkpoint of available data/reporting; no source or visibility edits."""
from pathlib import Path
import subprocess,shutil,json,datetime,fcntl
from checkpoint_mirror import mirror
OP=Path('/workspace/recovery/operations');REPO=Path('/workspace/LANS-RISK');DEST=REPO/'recovery_results';BRANCH='backup/recovery-remaining-20261022T102500Z'
def git(*args):return subprocess.check_output(['git','-C',str(REPO),*args],text=True,stderr=subprocess.STDOUT).strip()
with (OP/'remote-checkpoint.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert git('branch','--show-current')==BRANCH
 initial='d306a7bea4c4f7399cc91c9e4891055bc47bd04b'
 original_files=git('ls-tree','-r','--name-only',initial).splitlines();git('diff','--exit-code',initial,'--',*original_files)
 x=mirror();assert sum(x['counts'].values())==871
 for p in OP.iterdir():
  if p.is_file() and p.suffix in {'.py','.sh','.json','.md','.txt','.log','.jsonl','.patch'}:
   target=DEST/'operations'/p.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
 for source,sub in [(OP/'proposals','proposals'),(OP/'verified_results','results')]:
  shutil.copytree(source,DEST/sub,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 git('add','--','recovery_results');git('commit','-m','Preserve verified 44000 confirmation records and available results; dense Merge blocked')
 git('push','origin',f'HEAD:refs/heads/{BRANCH}')
 head=git('rev-parse','HEAD');assert git('ls-remote','origin',f'refs/heads/{BRANCH}').split()[0]==head
 event=dict(time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),event='available_results_and_reporting_checkpoint',conditions=871,counts=x['counts'],commit=head,branch=BRANCH,remote_ref_verified=True,all_requested_experiments_complete=False,blocked_conditions=33)
 with (OP/'REMOTE_CHECKPOINTS.jsonl').open('a') as f:f.write(json.dumps(event)+'\n')
 print(json.dumps(event),flush=True)
