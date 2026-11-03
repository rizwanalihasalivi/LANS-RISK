"""Verify the new completion checkpoint and restore absent pairs only; never run experiments."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target',default='/workspace/recovery/restored/LANS-RISK')
    a=p.parse_args();root=Path(__file__).resolve().parent
    manifest=json.loads((root/'MANIFEST.json').read_text())
    for name,digest in manifest.items():
        path=Path(name)
        assert not path.is_absolute() and '..' not in path.parts
        assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest,name
    target=Path(a.target);restored=0
    for source in sorted((root/'working').rglob('*')):
        if not source.is_file():continue
        dest=target/source.relative_to(root)
        if dest.exists():assert dest.read_bytes()==source.read_bytes(),('Refusing to overwrite different evidence',dest)
        else:dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest);restored+=1
    print('Completion checkpoint verified; new files restored:',restored,'; no experiments launched')


if __name__=='__main__':main()
