#!/usr/bin/env bash
set -euo pipefail
cd /workspace/LANS-RISK
python -c 'import sys; assert sys.version_info[:3] == (3,12,14), sys.version'
if [[ ! -f /workspace/recovery/LANS_RISK_26100_verified.zip ]]; then
  python restore_and_verify.py /workspace/recovery
fi
python - <<'PY'
from pathlib import Path
import hashlib,json,zipfile
root=Path('/workspace/LANS-RISK');meta=json.loads((root/'PARTS.json').read_text());archive=Path('/workspace/recovery')/meta['archive_name']
assert hashlib.sha256(archive.read_bytes()).hexdigest()==meta['archive_sha256']
target=Path('/workspace/recovery/restored')
if not (target/'LANS-RISK').exists():
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None
  for item in z.infolist():assert not Path(item.filename).is_absolute() and '..' not in Path(item.filename).parts
  z.extractall(target)
source=root/'recovery_results/operations';dest=Path('/workspace/recovery/operations');dest.mkdir(parents=True,exist_ok=True)
if source.is_dir():
 import shutil
 for p in source.iterdir():
  if p.is_file() and not (dest/p.name).exists():shutil.copyfile(p,dest/p.name)
PY
if [[ ! -x /workspace/recovery/venv/bin/python ]]; then python -m venv /workspace/recovery/venv; fi
export PIP_CACHE_DIR=/workspace/recovery/pip-cache
P=/workspace/recovery/venv/bin/python
"$P" -m pip install --index-url https://download.pytorch.org/whl/cpu torch==2.14.1
"$P" -m pip install numpy==2.3.5 numba==0.68.0 stable-baselines3==2.9.0 scipy==1.17.0 gymnasium==1.4.0 matplotlib==3.10.8 python-docx==1.2.0 pytest==9.1.1 pandas==3.0.6
"$P" -m pip check
if [[ -f /workspace/LANS-RISK/recovery_results/CHECKPOINT_MANIFEST.json && -f /workspace/recovery/operations/restore_latest_checkpoint.py ]]; then
  "$P" /workspace/recovery/operations/restore_latest_checkpoint.py
fi
python - <<'PY'
from pathlib import Path
import shutil
s=Path('/workspace/recovery/operations/runtime_profile.json');d=Path('/workspace/recovery/restored/LANS-RISK/deliverables/publication_results/runtime_profile.json')
if s.exists():
 if d.exists():assert d.read_bytes()==s.read_bytes(),'Preserve differing runtime sessions; do not overwrite'
 else:d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(s,d)
PY

# Approved completion checkpoint: merge immutable pairs only, never run experiments.
if [[ -f /workspace/LANS-RISK/completion_results/CHECKPOINT_MANIFEST.json ]]; then
  "$P" /workspace/LANS-RISK/completion_results/operations/restore_completed_checkpoint.py --repository /workspace/LANS-RISK --project /workspace/recovery/restored/LANS-RISK
  python /workspace/LANS-RISK/integrations/aris/lans_risk.py verify
else
  echo 'Final approved-amendment checkpoint is absent; original backup restoration alone is not the completed study.' >&2
  exit 1
fi
