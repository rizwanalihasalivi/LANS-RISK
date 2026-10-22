from pathlib import Path
import sys,json,hashlib,zipfile
root=Path(__file__).resolve().parent
meta=json.loads((root/'PARTS.json').read_text())
target=Path(sys.argv[1]);target.mkdir(parents=True,exist_ok=True)
archive=target/meta['archive_name']
if archive.exists():raise SystemExit('Refusing to overwrite existing archive: '+str(archive))
tmp=archive.with_suffix('.pending')
if tmp.exists():raise SystemExit('Refusing to overwrite existing partial restore: '+str(tmp))
whole=hashlib.sha256()
with tmp.open('xb') as output:
 for part in meta['parts']:
  path=root/part['path'];data=path.read_bytes()
  assert len(data)==part['bytes'] and hashlib.sha256(data).hexdigest()==part['sha256'],part['path']
  output.write(data);whole.update(data)
assert tmp.stat().st_size==meta['archive_bytes'] and whole.hexdigest()==meta['archive_sha256']
with zipfile.ZipFile(tmp) as z:
 assert z.testzip() is None
 manifest=json.loads(z.read('SNAPSHOT_MANIFEST.json'))
 for name,item in manifest.items():
  assert not Path(name).is_absolute() and '..' not in Path(name).parts
  data=z.read('LANS-RISK/'+name)
  assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256'],name
tmp.rename(archive)
print('PASS: archive and every manifested file verified:',archive)
print('No files extracted; no experiment launched.')
