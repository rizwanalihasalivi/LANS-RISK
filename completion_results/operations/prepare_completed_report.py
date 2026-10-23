"""Produce final report only after complete original/amended coverage audits."""
from pathlib import Path
import json,csv,datetime,hashlib,shutil
from zoneinfo import ZoneInfo
from audit_stage import audit,R,OP,sha
from audit_completed_robustness import audit_completed
OUT=OP/'final_verified_results'
def readcsv(path):
 with path.open() as f:return list(csv.DictReader(f))
def main():
 audits=[audit('extended_baselines','development'),audit('extended_baselines','confirmation'),audit('observation_delay_study','evaluation')];stress=audit_completed()
 assert stress['approved_amended_plan_complete']
 approval=json.loads((OP/'AMENDMENT_APPROVAL.json').read_text());assert approval['approved']
 snapshot=json.loads(Path('/workspace/LANS-RISK/SNAPSHOT_MANIFEST.json').read_text());checked=[]
 for name,item in snapshot.items():
  p=R/name
  if p.suffix=='.py' or p.name in ['PROTOCOL.md','EXTENDED_FREEZE.json','FREEZE.json'] or ('models' in str(p.parent) and p.suffix in ['.zip','.json']):
   assert sha(p)==item['sha256'],name;checked.append(name)
 import numpy as np
 runtime=json.loads((R/'deliverables/publication_results/runtime_profile.json').read_text());raw=json.loads((OP/'runtime_samples.json').read_text());assert len(runtime['results'])==len(raw['samples'])==96
 seen=set()
 for a in raw['samples']:
  key=tuple(a[n] for n in ['scenario','controller','delay_ms']);assert key not in seen;seen.add(key)
  row=next(x for x in runtime['results'] if tuple(x[n] for n in ['scenario','controller','delay_ms'])==key);v=np.array(a['samples_ms']);assert len(v)==50 and np.isfinite(v).all()
  for field,value in [('median_ms',np.median(v)),('p95_ms',np.quantile(v,.95)),('p99_ms',np.quantile(v,.99)),('max_ms',v.max())]:assert row[field]==float(value)
  assert row['exceeded_100ms']==int((v>100).sum())
 assert sum(len(x['samples_ms']) for x in raw['samples'])==4800
 assert json.loads((OP/'MODEL_SEED_AUDIT.json').read_text())['unique_policy_tensor_sets']==12
 assert '13 passed' in (OP/'preflight-tests.log').read_text()
 regression=json.loads((OP/'AMENDED_DYNAMICS_REGRESSION.json').read_text());assert regression['status']=='PASS' and regression['identical_step_transitions']==180
 for folder in ['extended_baselines','stress_study','observation_delay_study']:
  for name in ['descriptive_metrics.csv','paired_tests.csv','episodes.jsonl','publication_tables.pdf','publication_tables.tex']:assert (OUT/folder/name).stat().st_size>0
 now=datetime.datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
 old=(OP/'verified_results/SCIENTIFIC_REPORT.md').read_text()
 old=old.replace('# LANS-RISK — verified results and one blocked robustness subset','# LANS-RISK — final verified results with approved initialization amendment')
 lines=old.splitlines();lines[2]=f'Prepared {now} (Asia/Shanghai).';old='\n'.join(lines)+'\n'
 start=old.index('**The originally frozen');end=old.index('\n\n| Stage',start)
 old=old[:start]+'**All required experimental conditions are complete under the user-approved amended plan.** The main confirmation uses the unchanged original protocol. Robustness comprises 231 original conditions plus 33 separately labelled dense-Merge conditions with an approved initialization-attempt cap of 200,000 instead of 10,000. The original unamended robustness stage remains 231/264; this report does not relabel amended results as original-frozen results.'+old[end:]
 old=old.replace('| Robustness |231/264|11,550/13,200|Dense Merge blocked|','| Robustness |264/264|13,200|231 original + 33 approved sampler-amended conditions|')
 old=old.replace('59,550 verified episode records; adding development gives 64,350','61,200 verified episode records; adding development gives 66,000')
 start=old.index('## Exact blocker and tested proposal');end=old.index('## Observation delay and timing',start)
 section='''## Approved dense-Merge amendment and completed robustness

The original dense-Merge initializer exhausted its 10,000-attempt rejection budget for 15 of the 50 fixed traffic seeds 161000–161049. This was an initialization failure, not a controller collision. The user explicitly approved a separate study raising only that limit to 200,000. The exact approval record, one-line patch, original/candidate hashes, preflight and execution logs are in operations/.

All 33 dense-Merge conditions have now completed on all 50 prescribed traffic seeds, producing 1,650 verified episode records. The candidate benchmark differs by exactly one cap substitution. All 35 initial states that succeeded under the original cap were exactly preserved in preflight; all 50 amended initializations passed the original collision-free acceptance predicate. Seeds, density, physical dynamics, controller algorithms, frozen models, prediction/candidate budgets and episode counts were preserved. No case was removed or replaced. An additional diagnostic regression check matched nine paired initializations and 180 step transitions exactly across three delays for original-accepted cases, and checked both scope guards; these are software checks, not additional research evidence. The amendment uses a separate directory and source fingerprint; all 231 original robustness conditions and the original frozen source files remain unchanged.

The completed robustness analysis combines the 231 original conditions with these 33 amended conditions, labels source_version in machine-readable tables, and recalculates Holm corrections over the entire completed robustness contrast family. Do not describe the combined study as wholly conducted under the original unamended freeze. The amendment was selected after a setup failure; interpretation should disclose that timing and its limited scope.

Dense-Merge results below use the same 50 traffic cases for every controller. LANS values are descriptive actor-seed means, not pooled independent samples; per-actor intervals and paired tests are provided separately.

| FIFO ms | LANS collision % | MPC collision % | LANS corridor % | MPC corridor % | LANS RMSE m | MPC RMSE m |
|---:|---:|---:|---:|---:|---:|---:|
'''
 summary=readcsv(OUT/'stress_study/lans_mpc_summary.csv')
 for d in ['0','500','1000']:
  a=next(x for x in summary if (x['profile'],x['scenario'],x['controller'],x['delay_ms'])==('denser_traffic','merge','lans',d));b=next(x for x in summary if (x['profile'],x['scenario'],x['controller'],x['delay_ms'])==('denser_traffic','merge','mpc_nominal',d))
  section+=f"| {d} | {100*float(a['collision_seed_mean']):.2f} | {100*float(b['collision_seed_mean']):.2f} | {100*float(a['corridor_completion_seed_mean']):.2f} | {100*float(b['corridor_completion_seed_mean']):.2f} | {float(a['rmse_seed_mean']):.4f} | {float(b['rmse_seed_mean']):.4f} |\n"
 contrasts=readcsv(OUT/'stress_study/paired_tests.csv')
 comparisons=[x for x in contrasts if (x['profile'],x['scenario'],x['a'],x['b'],x['metric'])==('denser_traffic','merge','lans','mpc_nominal','rmse')]
 assert len(comparisons)==9
 if all(float(x['mean_difference_a_minus_b'])>0 and float(x['p_holm'])<.05 for x in comparisons):
  section+=f"\nLANS and nominal MPC have equal observed collision and corridor-completion rates at these three delays; equal rates do not prove equivalence. Nominal MPC has lower descriptive mean RMSE at every tested delay. All nine per-actor/delay RMSE comparisons have positive LANS-minus-MPC paired mean differences and Holm-adjusted p<0.05 (largest adjusted p={max(float(x['p_holm']) for x in comparisons):.4f}, correction over all {len(contrasts):,} robustness tests). These signed-rank results have the assumptions and limitations documented in STATISTICAL_METHODS.md.\n"
 section+='\nThese outcomes are finite-sample synthetic stress tests. They do not establish safety certification, general robustness, or a universal controller ranking. All other robustness results, including losses, are retained in stress_study/.\n\n'
 old=old[:start]+section+old[end:]
 old=old.replace('within each available study','within each completed study')
 old=old.replace('Current interruption was a reproducible application initialization exception, not a memory kill.','The final blocked subset was resolved by the approved initialization-only amendment; the original exception is preserved in the logs.')
 old+='''
## ARIS integration and review status

A pinned MIT-licensed ARIS Codex skill pack and LANS-RISK adapter are included. ARIS integration does not supply compute or make an independent scientific verdict. The final validation uses a separate deterministic implementation to recompute descriptive statistics, paired tests, Holm adjustments, coverage, seed identities and evidence hashes. No external-model peer review was run or claimed. Preserved historical files contain earlier blocked states; the final results/ report, completeness record and audit are authoritative.
'''
 (OUT/'SCIENTIFIC_REPORT.md').write_text(old)
 shutil.copyfile(OP/'verified_results/empirical_delay_tolerance.csv',OUT/'empirical_delay_tolerance.csv')
 complete=dict(all_requested_experiments_complete=True,completion_scope='Required documented plan with explicit approved dense-Merge initialization amendment',original_unamended_robustness_complete=False,amendment_executed=True,approval_pending=False,main_confirmation=dict(conditions=440,records=44000,complete=True,original_261_preserved=True),robustness=dict(conditions=264,records=13200,complete_under_approved_amendment=True,original_conditions=231,amended_conditions=33,amended_records=1650,missing_conditions=[]),observation_delay=dict(conditions=200,records=4000,complete=True),runtime=dict(conditions=96,raw_samples=4800,complete=True),development=dict(conditions=240,records=4800,complete=True),primary_episode_records=61200,including_development_episode_records=66000,external_model_review='NOT_RUN',limitations=['Approved initialization cap amendment for dense Merge','Synthetic benchmark and finite case sets','No sensor-study RMSE recorded','No saved full trajectories for independent per-step replay of reported episode errors','Consecutive runtime samples do not support independent-replicate confidence intervals or WCET'])
 (OUT/'STUDY_COMPLETENESS.json').write_text(json.dumps(complete,indent=2)+'\n')
 final=dict(prepared_at_asia_shanghai=now,all_required_conditions_verified=True,all_requested_experiments_complete=True,amendment_disclosed=True,original_unamended_robustness_complete=False,original_batches_preserved=261,remaining_main_batches_computed=179,original_scientific_artifacts_rechecked=len(checked),original_robustness_conditions_preserved=231,amended_conditions=33,amended_records=1650,primary_episode_records=61200,including_development_episode_records=66000,models_with_distinct_tensor_content=12,raw_timing_samples=4800,semantic_tests_passed=13)
 (OP/'FINAL_COMPLETENESS_AUDIT.json').write_text(json.dumps(final,indent=2));(OUT/'FINAL_COMPLETENESS_AUDIT.json').write_text(json.dumps(final,indent=2))
 reproducibility=(OP/'verified_results/REPRODUCIBILITY.md').read_text()
 reproducibility=reproducibility.replace('No missing dense-Merge outcomes are represented as collisions or zeros.','The33dense-Merge amended conditions are stored separately and labelled; no initialization failure was counted as a controller collision.')
 a=reproducibility.index('7. Do not blindly');b=reproducibility.index('\n8.',a)
 reproducibility=reproducibility[:a]+'''7. The original frozen robustness runner reproducibly fails dense-Merge initialization. The user approved the separate200000-attempt amendment recorded in operations/AMENDMENT_APPROVAL.json. The actual driver is operations/proposals/run_amended_dense_merge.py and its source map is operations/DENSE_MERGE_AMENDMENT.json. All33amended conditions are cached in project/working/stress_study/amended_dense_merge_confirmation; original231remain under confirmation. Running the same approved driver with --approved-initialization-amendment --approval-note describing the recorded approval --workers4 reuses valid completed pairs; do not replace original source/freeze files. audit_completed_robustness.py verifies the264-condition union and exact one-line sampler change. Scientific analysis is scientific_analysis_completed.py; prepare_completed_report.py and independent_final_validation.py produce and verify final reporting. Historical blocked-package helpers remain as provenance and must not be used to generate current claims. All helpers currently use /workspace/recovery paths; adapt path constants only if relocating, preserve original scientific source content, and record that operational change.''' + reproducibility[b:]
 reproducibility+='''
13. The final approved-amendment checkpoint, reports, ARIS integration and validation scripts are on branch integration/aris-frozen-workflow in the same GitHub repository. recovery_results/ preserves the original871condition pairs. completion_results/ adds33amended pairs and final reports. The original backup branch remains unchanged. restore_completed_checkpoint.py merges only matching verified pairs after the original restoration and refuses conflicting overwrites.
14. The main figures include all12controllers and required ablations; complete baseline/ablation inference is in extended_baselines/paired_tests.csv. The original development and exploratory observation stages remain separate, with disjoint traffic-seed ranges. Repeated actor seeds share traffic cases and are not independent extra samples.
'''
 (OUT/'REPRODUCIBILITY.md').write_text(reproducibility)
 print('FINAL REPORT READY: all required conditions verified under approved amendment',flush=True)
if __name__=='__main__':main()
