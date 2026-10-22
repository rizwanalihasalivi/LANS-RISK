"""Local second copy of complete batch pairs; immutable files with hash manifests."""
from pathlib import Path
import json,hashlib,shutil,os,datetime
R=Path('/workspace/recovery/restored/LANS-RISK');D=Path('/workspace/recovery/checkpoints');D.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mirror():
 manifest={};counts={}
 for folder,stage in [('extended_baselines','confirmation'),('stress_study','confirmation'),('observation_delay_study','evaluation')]:
  count=0
  for p in sorted((R/'working'/folder/stage).glob('*.json')):
   try:
    x=json.loads(p.read_text());raw=p.with_suffix('.jsonl')
    if not raw.exists() or sha(raw)!=x['raw_sha256']:continue
    assert len(raw.read_text().splitlines())==x['count']
   except (json.JSONDecodeError,FileNotFoundError):continue
   for src in [p,raw]:
    rel=src.relative_to(R);dest=D/rel;dest.parent.mkdir(parents=True,exist_ok=True);h=sha(src)
    if dest.exists():assert sha(dest)==h,('completed batch changed',src)
    else:
     tmp=dest.with_suffix(dest.suffix+'.pending');shutil.copyfile(src,tmp)
     assert sha(tmp)==h;tmp.replace(dest)
    manifest[str(rel)]=h
   count+=1
  counts[folder+'/'+stage]=count
 out=dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),counts=counts,sha256=manifest,scope='Independent local copy on same machine; does not protect against machine/disk loss')
 tmp=D/'CHECKPOINT_MANIFEST.pending';tmp.write_text(json.dumps(out,indent=2));tmp.replace(D/'CHECKPOINT_MANIFEST.json')
 print(json.dumps(counts),flush=True)
 return out
if __name__=='__main__':mirror()
