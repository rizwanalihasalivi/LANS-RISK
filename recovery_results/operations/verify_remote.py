"""Read checkpoint bytes from an independently fetched bare repository."""
from pathlib import Path
import subprocess,json,hashlib,tarfile,datetime
OP=Path('/workspace/recovery/operations');BARE=Path('/workspace/recovery/remote-verification.git');BRANCH='backup/recovery-remaining-20261022T102500Z'
def git(*a):return subprocess.check_output(['git','--git-dir='+str(BARE),*a])
def verify(refresh=True):
 if refresh:subprocess.run(['git','--git-dir='+str(BARE),'fetch','--depth','1','origin',f'+refs/heads/{BRANCH}:refs/heads/{BRANCH}'],check=True)
 commit=git('rev-parse','HEAD').decode().strip()
 proc=subprocess.Popen(['git','--git-dir='+str(BARE),'archive','--format=tar','HEAD','recovery_results'],stdout=subprocess.PIPE)
 blobs={}
 with tarfile.open(fileobj=proc.stdout,mode='r|') as tar:
  for item in tar:
   if item.isfile():blobs[item.name]=tar.extractfile(item).read()
 assert proc.wait()==0
 meta=json.loads(blobs['recovery_results/CHECKPOINT_MANIFEST.json'])
 for name,h in meta['sha256'].items():assert hashlib.sha256(blobs['recovery_results/'+name]).hexdigest()==h,name
 # Also verify every original archive chunk against its pinned hash in this independent fetch.
 parts=json.loads(git('show','HEAD:PARTS.json'))
 for part in parts['parts']:
  b=git('show','HEAD:'+part['path']);assert len(b)==part['bytes'] and hashlib.sha256(b).hexdigest()==part['sha256']
 out=dict(time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,branch=BRANCH,independent_fetch_raw_hashes_verified=len(meta['sha256']),counts=meta['counts'],original_archive_chunks_verified=len(parts['parts']),scope='Actual remote bytes verified from separate bare clone, not only local push status/ref comparison')
 (OP/'INDEPENDENT_REMOTE_VERIFICATION.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
 return out
if __name__=='__main__':verify()
