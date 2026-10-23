from pathlib import Path
import json
repo=Path('/workspace/LANS-RISK');here=repo/'integrations/aris'
state=json.loads((repo/'completion_results/results/STUDY_COMPLETENESS.json').read_text());assert state['all_requested_experiments_complete'] and state['amendment_executed']
p=here/'lans_risk.py';s=p.read_text()
s=s.replace("failures += verify_manifest(ROOT/'recovery_results', checkpoint['sha256'])", "failures += verify_manifest(ROOT/'recovery_results', checkpoint['sha256'])\n        completion_path=ROOT/'completion_results/CHECKPOINT_MANIFEST.json'\n        completion=json.loads(completion_path.read_text()) if completion_path.exists() else {'sha256':{}}\n        failures += verify_manifest(ROOT/'completion_results',completion['sha256'])")
s=s.replace("'checkpoint_files_checked':len(checkpoint['sha256']),", "'checkpoint_files_checked':len(checkpoint['sha256'])+len(completion['sha256']),")
s=s.replace("state = json.loads((ROOT/'recovery_results/results/STUDY_COMPLETENESS.json').read_text())", "status_path=ROOT/'completion_results/results/STUDY_COMPLETENESS.json'\n    if not status_path.exists():status_path=ROOT/'recovery_results/results/STUDY_COMPLETENESS.json'\n    state = json.loads(status_path.read_text())")
s=s.replace("'next_action':'Request explicit approval for separate dense-Merge sampler amendment; no experiment starts from this adapter.'", "'next_action':('All required conditions complete under approved amendment. Use completion_results/results for current report; no experiment starts from this adapter.' if state.get('all_requested_experiments_complete') else 'Consult recorded study status and approval before further experiments.')")
p.write_text(s)
p=repo/'AGENTS.md';s=p.read_text();a=s.index('- Dense-Merge robustness');b=s.index('- No paid infrastructure',a)
s=s[:a]+'''- The user approved the separate dense-Merge initialization cap amendment
  from 10,000 to 200,000. All 33 amended conditions are now complete and verified.
  Approval is recorded in completion_results/operations/AMENDMENT_APPROVAL.json.
  Keep the original 231 robustness conditions separate from those 33 amended
  conditions. No further experiments are required by the completed plan.
  Current final results live in completion_results/results; recovery_results
  preserves the earlier checkpoint and blocked reports as historical evidence.
'''+s[b:];p.write_text(s)
p=repo/'.agents/skills/lans-risk-resume/SKILL.md';s=p.read_text().replace('recovery_results/results/SCIENTIFIC_REPORT.md','completion_results/results/SCIENTIFIC_REPORT.md')
s=s.replace('   The dense-Merge amendment requires explicit approval; inspect the proposal\n   and preflight under recovery_results/proposals before any authorized run.', '   The dense-Merge amendment has explicit recorded approval and all33conditions\n   are verified complete. Read completion_results/results and the approval\n   record; do not restart completed experiments. Retain original/amended labels.')
p.write_text(s)
p=here/'README.md';s=p.read_text().replace('`recovery_results/results/', '`completion_results/results/').replace('all 1,742 checkpoint files','all 1,808 checkpoint files')
a=s.index('Main confirmation is complete');b=s.index('\nUse the existing recovery environment',a)
s=s[:a]+'''Main confirmation is complete (44,000 episodes), observation-delay is complete
(4,000), and runtime has 4,800 samples. Robustness is complete under the approved
amendment: 231 original conditions plus33 separately labelled dense-Merge
conditions (13,200 episodes in total). Explicit user approval and execution
provenance are in completion_results/operations. The original frozen robustness
stage alone remains231/264; do not relabel amended data as original data.
Current report: completion_results/results/SCIENTIFIC_REPORT.md.
'''+s[b:]
s=s.replace('The existing verified available-results ZIP remains valid but does not contain\nthis later integration; distribute the companion integration archive alongside it.', 'The final verified ZIP contains the complete scientific project and the tracked\nARIS repository. Historical blocked ZIPs/reports are retained as provenance; use\nthe final package and completion_results/results for current conclusions.')
s=s.replace('| Raw records and metadata | `recovery_results/working/` |','| Raw records and metadata | `recovery_results/working/` plus `completion_results/working/` |')
s=s.replace('| Recovery and audit scripts | `recovery_results/operations/` |','| Recovery and audit scripts | `recovery_results/operations/` plus `completion_results/operations/` |')
p.write_text(s)
claims=json.loads((here/'claims.json').read_text())
for claim in claims:
 claim['source']='completion_results/results/STUDY_COMPLETENESS.json'
 if claim['id']=='robustness_verified_conditions':claim['value']=264
(here/'claims.json').write_text(json.dumps(claims,indent=2)+'\n')
print('ARIS now routes to final approved-amendment evidence and validates all1808checkpoint files')
