"""Incremental verified result checkpoint on a new branch; original backup untouched."""
from pathlib import Path
import shutil,subprocess,json,time,hashlib,datetime,fcntl
from checkpoint_mirror import mirror
REPO=Path('/workspace/LANS-RISK');OP=Path('/workspace/recovery/operations');DEST=REPO/'recovery_results';BRANCH='backup/recovery-remaining-20261022T102500Z'
def git(*args):return subprocess.check_output(['git','-C',str(REPO),*args],text=True,stderr=subprocess.STDOUT).strip()
with (OP/'remote-checkpoint.lock').open('w') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 previous=-1;failures=0
 while True:
  x=mirror();count=sum(x['counts'].values());done=(OP/'FINAL_VERIFIED.json').exists()
  if count>=previous+10 or (done and count!=previous):
   try:
    assert git('branch','--show-current')==BRANCH
    # Copy only immutable verified pairs; every preserved hash must agree.
    for name,h in x['sha256'].items():
     src=Path('/workspace/recovery/checkpoints')/name;dst=DEST/name;dst.parent.mkdir(parents=True,exist_ok=True)
     b=src.read_bytes();assert hashlib.sha256(b).hexdigest()==h
     if dst.exists():assert hashlib.sha256(dst.read_bytes()).hexdigest()==h
     else:dst.write_bytes(b)
    (DEST/'CHECKPOINT_MANIFEST.json').write_text(json.dumps(x,indent=2))
    ops=DEST/'operations';ops.mkdir(exist_ok=True)
    for p in OP.iterdir():
     if p.is_file() and p.suffix in {'.py','.sh','.json','.log','.jsonl','.txt'} and p.name!='remote-checkpoint.log':shutil.copyfile(p,ops/p.name)
    git('add','--','recovery_results')
    git('commit','-m',f'Preserve verified recovery checkpoint: {count} completed conditions')
    git('push','origin',f'HEAD:refs/heads/{BRANCH}')
    commit=git('rev-parse','HEAD');remote=git('ls-remote','origin',f'refs/heads/{BRANCH}').split()[0];assert commit==remote
    event=dict(time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),conditions=count,counts=x['counts'],commit=commit,remote_ref_verified=True,branch=BRANCH)
    with (OP/'REMOTE_CHECKPOINTS.jsonl').open('a') as f:f.write(json.dumps(event)+'\n')
    print(json.dumps(event),flush=True);previous=count;failures=0
   except Exception as exc:
    failures+=1;print('Remote checkpoint failure',type(exc).__name__,str(exc),flush=True)
    if failures>=3:raise
  if done:break
  time.sleep(30)
