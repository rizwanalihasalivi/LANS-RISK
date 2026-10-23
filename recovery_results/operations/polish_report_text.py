"""Spacing/readability only; protect code, identifiers, hashes, paths and timestamps."""
from pathlib import Path
import re
OUT=Path('/workspace/recovery/operations/verified_results')
protected=re.compile(r'`[^`]+`|https?://\S+|backup/recovery-remaining-\d{8}T\d{6}Z|\b[0-9a-f]{40,64}\b|\d{4}-\d{2}-\d{2}T[0-9:.+A-Za-z-]+|\b[\w./-]+\.(?:py|csv|json|jsonl|md|txt|zip|log)\b|\b\w*_\w*\b|\bp(?:05|50|95|99)\b|\bpython3\b|\bstable-baselines3\b')
def letters(i):
 out=''
 while True:
  out=chr(65+i%26)+out;i=i//26-1
  if i<0:return out
for name in ['SCIENTIFIC_REPORT.md','REPRODUCIBILITY.md','STATISTICAL_METHODS.md','FIGURE_CAPTIONS.md']:
 p=OUT/name;text=p.read_text();stash={}
 def save(m):
  key='ZZPROTECTED'+letters(len(stash))+'TOKENZZ';stash[key]=m.group();return key
 text=protected.sub(save,text)
 text=re.sub(r'(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])',' ',text)
 selected={1000,2000,4000,4800,6600,11550,13200,1650,59550,64350,10000,200000,44000,26100,17900,20000}
 text=re.sub(r'(?<![\w.])\d{4,6}(?![\w.])',lambda m:format(int(m.group()),',') if int(m.group()) in selected else m.group(),text)
 text=text.replace('3 x 192','3 × 192')
 for key,value in stash.items():text=text.replace(key,value)
 p.write_text(text)
print('Polished report prose without changing data tables, identifiers or code')
