from pathlib import Path
import subprocess,json,hashlib,tarfile,datetime
OP=Path('/workspace/recovery/operations');BARE=Path('/workspace/recovery/remote-verification.git');BRANCH='integration/aris-frozen-workflow';REF='refs/heads/'+BRANCH

def git(*args):return subprocess.check_output(['git','--git-dir='+str(BARE),*args])
def main():
 subprocess.run(['git','--git-dir='+str(BARE),'fetch','--depth','1','origin','+'+REF+':'+REF],check=True)
 commit=git('rev-parse',REF).decode().strip()
 proc=subprocess.Popen(['git','--git-dir='+str(BARE),'archive','--format=tar',REF,'recovery_results','completion_results','integrations/aris','AGENTS.md','.agents'],stdout=subprocess.PIPE)
 blobs={}
 with tarfile.open(fileobj=proc.stdout,mode='r|') as tar:
  for member in tar:
   if member.isfile():blobs[member.name]=tar.extractfile(member).read()
 assert proc.wait()==0
 counts={};files=0
 for prefix in ['recovery_results','completion_results']:
  meta=json.loads(blobs[prefix+'/CHECKPOINT_MANIFEST.json'])
  for name,h in meta['sha256'].items():assert hashlib.sha256(blobs[prefix+'/'+name]).hexdigest()==h,name
  files+=len(meta['sha256']);counts[prefix]=meta.get('counts',{'amended_dense_merge':meta.get('amended_conditions')})
 assert files==1808
 state=json.loads(blobs['completion_results/results/STUDY_COMPLETENESS.json']);assert state['all_requested_experiments_complete'] and state['amendment_executed']
 assert json.loads(blobs['completion_results/results/FINAL_INDEPENDENT_VALIDATION.json'])['status']=='PASS'
 lock=json.loads(blobs['integrations/aris/UPSTREAM_LOCK.json'])
 for name,h in lock['files'].items():assert hashlib.sha256(blobs['integrations/aris/upstream/'+name]).hexdigest()==h
 parts=json.loads(git('show',REF+':PARTS.json'))
 for part in parts['parts']:
  data=git('show',REF+':'+part['path']);assert len(data)==part['bytes'] and hashlib.sha256(data).hexdigest()==part['sha256']
 result=dict(time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,branch=BRANCH,independent_remote_result_files_verified=files,conditions=904,counts=counts,original_archive_chunks_verified=len(parts['parts']),aris_vendor_files_verified=len(lock['files']),final_scientific_validation_status='PASS',scope='Remote bytes independently fetched and hashed, not merely local push acknowledgement')
 (OP/'FINAL_REMOTE_VERIFICATION.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
if __name__=='__main__':main()
