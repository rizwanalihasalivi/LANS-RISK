from pathlib import Path
import json,hashlib,zipfile,datetime,sys,os
ROOT=Path('/workspace/recovery/restored/LANS-RISK');STUDY=ROOT/'working/extended_baselines'
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:a=[x.decode() for x in (p/'cmdline').read_bytes().split(b'\0') if x]
 except (OSError,UnicodeDecodeError):continue
 if a and Path(a[0]).name.startswith('python') and any(Path(v).name in {'experiment.py','run_study.py','watch_results.py'} for v in a[1:]):raise RuntimeError(f'Existing experiment/monitor process {p.name}; investigate before resuming')
now=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');out=ROOT/'resume_operations'/now;out.mkdir()
freeze=json.loads((STUDY/'EXTENDED_FREEZE.json').read_text())['sha256']
files=[p for p in STUDY.rglob('*') if p.is_file() and not any(x in {'__pycache__','.pytest_cache'} for x in p.parts)]
files+= [ROOT/'working'/relative for relative in freeze]
files=list(dict.fromkeys(files));manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
archive=out/'before_resume.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,str(p.relative_to(ROOT)))
 z.writestr('BACKUP_MANIFEST.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for name,digest in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
(out/'BACKUP.json').write_text(json.dumps(dict(path=str(archive),sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),files=len(files),bytes=archive.stat().st_size,verified=True),indent=2))
# Verification after the verified backup exists.
for name,digest in freeze.items():assert hashlib.sha256((ROOT/'working'/name).read_bytes()).hexdigest()==digest,name
sys.path.insert(0,str(STUDY));import experiment as e
assert e.sources()==freeze
expected={(s,c,k,d) for s in e.SCENARIOS for c in e.METHODS for k in ([0] if c in e.ACTOR_FREE else [42,43,44]) for d in [0,200,500,700,1000]}
assert len(expected)==440
fingerprint=hashlib.sha256(json.dumps(freeze,sort_keys=True).encode()).hexdigest();seen=set();saved={}
for p in (STUDY/'confirmation').glob('*.json'):
 x=json.loads(p.read_text());key=tuple(x[n] for n in ['scenario','controller','policy_seed','delay_ms'])
 assert key in expected and key not in seen;seen.add(key)
 assert x['count']==100 and x['first']==141000 and x['source_hash']==fingerprint
 raw=p.with_suffix('.jsonl');assert hashlib.sha256(raw.read_bytes()).hexdigest()==x['raw_sha256']
 rr=[json.loads(line) for line in raw.read_text().splitlines()]
 assert len(rr)==100 and [v['episode_seed'] for v in rr]==list(range(141000,141100))
 saved[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
 saved[str(raw.relative_to(ROOT))]=hashlib.sha256(raw.read_bytes()).hexdigest()
assert len(seen)==261,(len(seen),'Expected verified261batches')
assert all(p.with_suffix('.json').exists() for p in (STUDY/'confirmation').glob('*.jsonl'))
(out/'PREFLIGHT.json').write_text(json.dumps(dict(valid_batches=len(seen),valid_episodes=100*len(seen),remaining_batches=len(expected-seen),remaining_episodes=100*len(expected-seen),expected_keys=sorted(expected),existing_result_hashes=saved,source_fingerprint=fingerprint),indent=2))
(ROOT/'resume_operations/LATEST.txt').write_text(str(out)+'\n')
print(json.dumps(dict(operation=str(out),backup=str(archive),verified_batches=len(seen),verified_episodes=26100,remaining_episodes=17900)))
