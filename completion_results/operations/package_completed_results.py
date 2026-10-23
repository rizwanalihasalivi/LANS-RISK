"""One complete scientific delivery with separately labelled approved amendment."""
from pathlib import Path
import json,hashlib,zipfile,stat,subprocess
R=Path('/workspace/recovery/restored/LANS-RISK');OP=Path('/workspace/recovery/operations');OUT=OP/'final_verified_results';REPO=Path('/workspace/LANS-RISK')
def sha(p):
 with p.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def main():
 state=json.loads((OUT/'STUDY_COMPLETENESS.json').read_text());assert state['all_requested_experiments_complete'] and state['amendment_executed']
 assert json.loads((OUT/'FINAL_INDEPENDENT_VALIDATION.json').read_text())['status']=='PASS'
 remote=json.loads((OP/'FINAL_REMOTE_VERIFICATION.json').read_text());assert remote['independent_remote_result_files_verified']==1808
 commit=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip();assert commit==remote['commit']
 bundle=Path('/workspace/recovery/LANS_RISK_FINAL_VERIFIED_RESULTS.zip');pending=bundle.with_suffix('.pending');assert not bundle.exists() and not pending.exists()
 paths=[];excluded=[]
 for p in R.rglob('*'):
  if not p.is_file():continue
  if any(x in {'.git','.venv','.cache','__pycache__','.pytest_cache'} for x in p.parts):excluded.append(str(p.relative_to(R)));continue
  paths.append(('project/'+str(p.relative_to(R)),p))
 for p in OP.rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and p.suffix not in {'.lock','.pending'}:
   name='results/'+str(p.relative_to(OUT)) if p.is_relative_to(OUT) else 'operations/'+str(p.relative_to(OP));paths.append((name,p))
 # Include the exact tracked repository, including original snapshot chunks and portable ARIS links.
 # The duplicate original archive supports the adapter's immutable backup checks offline.
 for entry in subprocess.check_output(['git','-C',str(REPO),'ls-files','-z']).split(b'\0'):
  if entry:
   name=entry.decode();paths.append(('aris_repository/'+name,REPO/name))
 assert len({name for name,p in paths})==len(paths)
 manifest={}
 intro='''# Final verified LANS-RISK results — approved initialization amendment disclosed

Read results/SCIENTIFIC_REPORT.md, results/STUDY_COMPLETENESS.json and results/FINAL_INDEPENDENT_VALIDATION.json first.
All required conditions are complete under the approved amended plan: main44,000episodes, robustness13,200episodes, observation-delay4,000episodes and4,800runtime samples. Development4,800episodes is separate. The33dense-Merge robustness conditions use the explicitly approved200,000-attempt initialization cap; the other231robustness conditions use the original freeze. Original files/models/seeds and all261initial batches are preserved.

results/ is the authoritative final analysis, figures, tables, captions and report.
project/ is the complete restored frozen project plus the separate amended stage, including code/configs/models/checkpoints/raw results/historical studies.
operations/ preserves recovery, execution logs, proposal, approval, audits, analysis and reproduction tools. Its verified_results/ folder is the historical blocked report; final_verified_results was mapped to results/.
aris_repository/ is the tracked GitHub repository at the recorded delivery commit, including the pinned ARIS skill pack, original snapshot chunks, original recovery_results and new completion_results. Its root README describes the original26,100snapshot; use completion_results/results for current status. Git internals and the Python venv are excluded; versions and setup/reproduction instructions are included.

The archive's ARIS skill links are Unix symlinks. If your ZIP extractor converts them to text files, run RESTORE_ARIS_LINKS.py from this extracted package; it recreates only exact managed links without changing source or results. The GitHub branch preserves links directly.

No external-model peer review or safety certification is claimed. Historical blocked states and proposals remain as provenance. Final limitations and approved-protocol distinction are in the report. Verify the ZIP SHA256 sidecar and PACKAGE_MANIFEST.json payload hashes before use.
'''
 linkscript='''from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parent
manifest=json.loads((root/'PACKAGE_MANIFEST.json').read_text())
for name,item in manifest.items():
 if item.get('kind')!='symlink':continue
 p=root/name;target=item['target']
 if p.is_symlink():
  assert str(p.readlink())==target
  continue
 if p.exists():
  assert p.is_file() and p.read_bytes()==target.encode(), ('Refusing to replace modified path',p)
  p.unlink()
 p.parent.mkdir(parents=True,exist_ok=True);p.symlink_to(target,target_is_directory=True)
 assert p.resolve().is_dir(),p
print('Managed ARIS links verified/restored; source and results unchanged')
'''
 with zipfile.ZipFile(pending,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  def write(name,data,kind='file',target=None):
   if kind=='symlink':
    info=zipfile.ZipInfo(name);info.create_system=3;info.external_attr=(stat.S_IFLNK|0o777)<<16;z.writestr(info,data)
   else:z.writestr(name,data)
   manifest[name]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),kind=kind)
   if target is not None:manifest[name]['target']=target
  for name,p in sorted(paths):
   if p.is_symlink():write(name,str(p.readlink()).encode(),'symlink',str(p.readlink()))
   else:write(name,p.read_bytes())
  write('README.md',intro.encode());write('RESTORE_ARIS_LINKS.py',linkscript.encode())
  write('DELIVERY_PROVENANCE.json',json.dumps(dict(github_commit=commit,github_branch=remote['branch'],original_backup_commit='d306a7bea4c4f7399cc91c9e4891055bc47bd04b',amendment_source_hash=json.loads((OP/'DENSE_MERGE_AMENDMENT.json').read_text())['source_hash']),indent=2).encode())
  write('PACKAGE_EXCLUSIONS.json',json.dumps(dict(regenerable_project_files=excluded,excluded='Git internals, venv, regenerable caches; package versions and commit provenance included',included_repository_scope='All git-tracked files, including original archive chunks, ARIS integration and completion_results'),indent=2).encode())
  z.writestr('PACKAGE_MANIFEST.json',json.dumps(manifest,indent=2))
 with zipfile.ZipFile(pending) as z:
  assert z.testzip() is None
  assert set(z.namelist())==set(manifest)|{'PACKAGE_MANIFEST.json'}
  for name,x in manifest.items():
   data=z.read(name);assert len(data)==x['bytes'] and hashlib.sha256(data).hexdigest()==x['sha256'],name
 pending.rename(bundle)
 delivery=dict(path=str(bundle),bytes=bundle.stat().st_size,sha256=sha(bundle),payload_files=len(manifest),zip_crc_and_every_payload_hash_verified=True,all_required_experiments_complete_under_approved_amendment=True,original_unamended_robustness_complete=False,amended_conditions=33,github_commit=commit)
 bundle.with_suffix('.json').write_text(json.dumps(delivery,indent=2));print(json.dumps(delivery),flush=True)
if __name__=='__main__':main()
