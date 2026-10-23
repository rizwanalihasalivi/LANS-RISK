#!/usr/bin/env python3
"""Offline ARIS adapter. No experiment launcher, API calls or source mutations."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

def verify_manifest(root, manifest):
    failures = []
    for name, expected in manifest.items():
        path = root / name
        if not path.is_file():
            failures.append(f'missing: {name}')
        else:
            with path.open('rb') as stream:
                actual = hashlib.file_digest(stream, 'sha256').hexdigest()
            if actual != expected:
                failures.append(f'changed: {name}')
    return failures

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['status', 'verify', 'evidence'])
    args = parser.parse_args()
    if args.action == 'verify':
        lock = json.loads((HERE/'UPSTREAM_LOCK.json').read_text())
        protected = json.loads((HERE/'PROTECTED_FILES.json').read_text())
        checkpoint = json.loads((ROOT/'recovery_results/CHECKPOINT_MANIFEST.json').read_text())
        failures = verify_manifest(HERE/'upstream', lock['files'])
        failures += verify_manifest(ROOT, protected)
        failures += verify_manifest(ROOT/'recovery_results', checkpoint['sha256'])
        for p in (HERE/'upstream/skills/skills-codex').iterdir():
            if p.is_dir():
                link = ROOT/'.agents/skills'/p.name
                if not link.is_symlink() or link.resolve() != p.resolve():
                    failures.append(f'invalid skill link: {p.name}')
        print(json.dumps({'integration_integrity_passed':not failures,
                          'upstream_commit':lock['commit'],
                          'protected_files_checked':len(protected),
                          'checkpoint_files_checked':len(checkpoint['sha256']),
                          'failures':failures},indent=2))
        return int(bool(failures))
    if args.action == 'evidence':
        return subprocess.run([sys.executable,str(HERE/'upstream/tools/evidence_check.py'),
            str(ROOT),'--batch',str(HERE/'claims.json')],check=False).returncode
    state = json.loads((ROOT/'recovery_results/results/STUDY_COMPLETENESS.json').read_text())
    print(json.dumps({'study':state,'next_action':'Request explicit approval for separate dense-Merge sampler amendment; no experiment starts from this adapter.',
                     'external_model_review':'NOT_RUN',
                     'runtime_root':'Restore using recovery_results/operations/install_environment.sh; consult START_HERE_ENVIRONMENT.md. Existing host: /workspace/recovery/restored/LANS-RISK.',
                     'note':'Saved study status; run verify to validate the preserved evidence bytes.'},indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
