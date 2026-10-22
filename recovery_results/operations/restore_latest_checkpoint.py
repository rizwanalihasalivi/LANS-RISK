"""Merge verified complete pairs from a recovery branch without overwriting results."""
from pathlib import Path
import json,hashlib,shutil
SOURCE=Path('/workspace/LANS-RISK/recovery_results');ROOT=Path('/workspace/recovery/restored/LANS-RISK')
meta=json.loads((SOURCE/'CHECKPOINT_MANIFEST.json').read_text())
for name,h in meta['sha256'].items():
 assert not Path(name).is_absolute() and '..' not in Path(name).parts
 p=SOURCE/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==h,name
for name,h in meta['sha256'].items():
 src=SOURCE/name;dst=ROOT/name
 if dst.exists():assert hashlib.sha256(dst.read_bytes()).hexdigest()==h,('Refusing to replace different result',name)
 else:dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
print('Merged complete immutable pairs:',meta['counts'])
print('Revalidate frozen hashes/condition coverage and process identity before resuming. No experiment launched.')
