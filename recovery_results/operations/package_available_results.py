"""Verified available-results delivery; deliberately never claims a complete frozen plan."""
from pathlib import Path
import json,csv,hashlib,zipfile,datetime,subprocess,sys,math
from zoneinfo import ZoneInfo
from audit_stage import audit,R,OP
OUT=OP/'verified_results'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csvread(p):
 with p.open() as f:return list(csv.DictReader(f))
def prepare_report():
 audit('extended_baselines','development');audit('extended_baselines','confirmation');audit('observation_delay_study','evaluation')
 subprocess.run([sys.executable,str(OP/'audit_partial_stress.py')],check=True)
 assert not (R/'working/stress_study/amended_dense_merge_confirmation').exists(),'Review amended data explicitly; this is the unamended blocked-package path'
 for name,h in json.loads((OP/'PREFLIGHT_261.json').read_text())['existing_result_hashes'].items():assert sha(R/name)==h
 original=json.loads(Path('/workspace/LANS-RISK/SNAPSHOT_MANIFEST.json').read_text());checked=[]
 for name,item in original.items():
  p=R/name
  if p.suffix=='.py' or p.name in ['PROTOCOL.md','EXTENDED_FREEZE.json','FREEZE.json'] or ('models' in str(p.parent) and p.suffix in ['.zip','.json']):
   assert sha(p)==item['sha256'],name;checked.append(name)
 runtime=json.loads((R/'deliverables/publication_results/runtime_profile.json').read_text());raw=json.loads((OP/'runtime_samples.json').read_text());assert len(runtime['results'])==len(raw['samples'])==96
 import numpy as np
 seen=set()
 for a in raw['samples']:
  key=tuple(a[n] for n in ['scenario','controller','delay_ms']);assert key not in seen;seen.add(key)
  row=next(x for x in runtime['results'] if tuple(x[n] for n in ['scenario','controller','delay_ms'])==key);v=np.array(a['samples_ms']);assert len(v)==50 and np.isfinite(v).all()
  for field,value in [('median_ms',np.median(v)),('p95_ms',np.quantile(v,.95)),('p99_ms',np.quantile(v,.99)),('max_ms',v.max())]:assert row[field]==float(value)
  assert row['exceeded_100ms']==int((v>100).sum())
 assert sum(len(x['samples_ms']) for x in raw['samples'])==4800
 model=json.loads((OP/'MODEL_SEED_AUDIT.json').read_text());assert model['unique_policy_tensor_sets']==12
 assert '13 passed' in (OP/'preflight-tests.log').read_text()
 pre=json.loads((OP/'proposals/INITIALIZATION_AMENDMENT_PREFLIGHT.json').read_text());assert pre['accepted']==50 and pre['original_failures']==15 and pre['unchanged_original_success_cases']==35
 for folder in ['extended_baselines','stress_study','observation_delay_study']:
  for name in ['descriptive_metrics.csv','paired_tests.csv','episodes.jsonl','publication_tables.pdf','publication_tables.tex']:assert (OUT/folder/name).stat().st_size>0
 now=datetime.datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
 summary=csvread(OUT/'extended_baselines/lans_mpc_summary.csv');metadata=json.loads((R/'working/extended_baselines/confirmation_SUMMARY.json').read_text());assert len(metadata)==440
 thresholds=[]
 for s,c,k in sorted({(x['scenario'],x['controller'],x['policy_seed']) for x in metadata}):
  last=None
  for d in [0,200,500,700,1000]:
   x=next(x for x in metadata if (x['scenario'],x['controller'],x['policy_seed'],x['delay_ms'])==(s,c,k,d))
   if x['collision']>1.00000001 or x['corridor_completion']<89.99999999:break
   last=d
  thresholds.append(dict(scenario=s,controller=c,actor_seed=k,empirical_contiguous_passing_delay_ms=last,upper_grid_censored=last==1000))
 with (OUT/'empirical_delay_tolerance.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(thresholds[0]));w.writeheader();w.writerows(thresholds)
 lines=['# LANS-RISK — verified results and one blocked robustness subset','',f'Prepared {now} (Asia/Shanghai).','',
 '**The originally frozen experiment plan is not fully complete.** All179remaining main confirmation batches were completed and verified. The only missing experiment is33denser-Merge robustness conditions (1650planned episode records), blocked by the frozen initialization rejection limit. No unapproved amendment has run.','',
 '| Stage | Verified conditions | Verified records/samples | State |','|---|---:|---:|---|','| Main confirmation |440/440|44000|Complete; all261original batches unchanged|','| Robustness |231/264|11550/13200|Dense Merge blocked|','| Observation-delay evaluation |200/200|4000|Complete; exploratory|','| Sequential runtime |96/96|4800timed calls|Complete|','| Development |240/240|4800|Re-audited|','',
 'The main/robustness/sensor deliveries contain59550verified episode records; adding development gives64350. The176archived smoke checks and older studies are separate. Repeated methods and actor seeds share paired traffic cases; these totals are not counts of independent traffic samples.','',
 '## Main LANS-versus-MPC finding','',
 'All three frozen LANS actors and the matched nominal MPC baseline have the same observed contiguous passing command-delay thresholds:1000ms on Highway,700ms on Merge,1000ms on Intersection, and500ms on Roundabout. LANS did not improve this delay-threshold endpoint. Identical observed thresholds do not establish statistical equivalence or equal tracking/safety behavior. The1000ms entries are right-censored at the largest tested delay.','',
 'The empirical criterion is collision<=1% and corridor completion>=90% at every lower tested delay on the0/200/500/700/1000ms grid. It is not a certified delay bound or proof that true collision risk is<=1%; even0/100collisions has a Wilson95% upper bound of about3.7%. Cold-FIFO startup may constrain the endpoint before feedback takes effect.','',
 'At1000ms, LANS entries below are descriptive means across actors42/43/44; MPC is run once on the same100traffic cases. Per-seed intervals, sample SDs and paired tests are in the CSVs.','',
 '| Scenario | LANS collision % | MPC collision % | LANS corridor % | MPC corridor % | LANS RMSE m | MPC RMSE m |','|---|---:|---:|---:|---:|---:|---:|']
 for s in ['highway','merge','intersection','roundabout']:
  a=next(x for x in summary if (x['scenario'],x['controller'],x['delay_ms'])==(s,'lans','1000'));b=next(x for x in summary if (x['scenario'],x['controller'],x['delay_ms'])==(s,'mpc_nominal','1000'))
  lines.append(f"| {s} | {100*float(a['collision_seed_mean']):.2f} | {100*float(b['collision_seed_mean']):.2f} | {100*float(a['corridor_completion_seed_mean']):.2f} | {100*float(b['corridor_completion_seed_mean']):.2f} | {float(a['rmse_seed_mean']):.4f} | {float(b['rmse_seed_mean']):.4f} |")
 lines+=['','Tracking differences are condition-specific: at this endpoint MPC has lower mean RMSE on Highway/Intersection, while LANS has lower mean RMSE on Merge/Roundabout. Both methods fail the corridor criterion at1000ms on Merge/Roundabout. Interpret RMSE jointly with safety and completion, especially when collisions shorten episodes. No universal LANS superiority claim is supported.','',
 'The nominal comparison shares plant, information access, physical FIFO, action limits, reference-speed ceiling, acceleration-aware predictor,30-step prediction horizon and3x192candidate budget. Objectives, trajectory ranking, actor use and retention/warm starts differ; equal candidate counts do not prove equal compute. The finite-scenario robust comparator is a generic three-scenario sampled planner, not certified tube MPC. All12controllers and planned ablation contrasts are retained. PPO-only removes a supervisor bundle; it does not isolate one safety mechanism.','',
 '## Exact blocker and tested proposal','',
 'The original robustness runner exited1 at the dense-Merge initializer with `RuntimeError: No collision-free initial traffic sample`. Its10000-attempt rejection limit is exhausted for15of the50fixed traffic seeds161000–161049. Every33-condition dense-Merge batch therefore stops before a complete50-case result can be saved. All132weaker-actuation conditions and99denser Highway/Intersection/Roundabout conditions are complete, with source hashes and raw metrics verified. This is a frozen-code setup failure, not evidence that a controller collided or that the physical scenario is impossible. Uninitialized cases are not assigned fabricated performance outcomes.','',
 'The proposal in operations/proposals/initialization_limit.patch changes only the rejection-attempt budget from10000to200000 in a separate derivative. Proposal-only preflight initialized all50seeds safely and exactly preserved all35initial states that succeeded under the original cap. It does not change traffic seeds, density, safety predicates, controller/model parameters, delays or episode counts. It has not been used for controller experiments. Running those33conditions requires an explicit exception to the user freeze instruction; results must have a separate amended source fingerprint and be disclosed as an amendment. The original files, freeze manifests and completed results remain intact.','',
 '## Observation delay and timing','',
 'The completed exploratory observation study uses five synthetic packet-delay profiles, four scenarios and20fresh cases per condition, with zero physical command delay. Initial state is known; subsequent full-state observations can be stale. It is not a DAROM reproduction or a learned delay-encoder evaluation. The reported figures retain all failures and seed variation. Do not equate a2s packet-delay bound with fixed2s command-delay tolerance.','',
 'Runtime uses the unchanged original profiling loop:20warmup then50timed calls per scenario/controller at0/1000ms FIFO, actor42 where needed. A separate helper retains the post-loop timing array; all4800samples and original median/p95/p99/max/exceedance statistics were independently checked. Mean/sample SD are provided. Samples span evolving states and resets; no independent-replicate CI, WCET bound or real-time guarantee is inferred. Main confirmation timing spans original and resumed execution sessions and is diagnostic only.','',
 '## Metrics, statistical methods and recording limitations','',
 'Binary outcomes have per-condition Wilson95% intervals; non-timing continuous outcome means and paired differences use5000deterministic traffic-case bootstrap draws. Tables give sample SD, observed extrema and quantiles. Exact paired-discordance tests cover binary outcomes; RMSE uses two-sided Wilcoxon signed-rank with documented assumptions. Holm correction covers all listed contrasts/outcomes within each available study. No actor-seed pooling is used for inference; bootstrap intervals are marginal, not simultaneous. Zero-discordance bootstrap intervals do not prove equivalence. Additional inherited analyses use their recorded bootstrap seeds and contrast families; use results/ as the authoritative new analysis. See STATISTICAL_METHODS.md.','',
 'The raw no_feasible_steps field is meaningful only for the logged CBF and sampled-plan variants. MPC nominal/PPO/LQR methods have no such measured flag and predictor LQR hardcodes it false. Their default/fixed zeros are marked unavailable in processed tables, with raw episode count retained. Logged flag definitions differ between CBF and candidate planners, so cross-method solver-feasibility rankings are unsupported.','',
 'Observation-delay raw records do not contain RMSE. Full per-step state/action/error trajectories were not stored, so per-episode RMSE and event flags are checked against frozen computation logic while saved outcome aggregates are independently recomputed. Unrecorded near-miss/clearance/jerk/energy quantities are not invented. Episode length can vary after collision. Scientific claims are limited to this synthetic, finite-horizon disc-vehicle benchmark and these fixed actors/cases. No formal safety or real-vehicle guarantee follows.','',
 '## Integrity, recovery and package contents','',
 'The GitHub backup ref matched commit d306a7bea4c4f7399cc91c9e4891055bc47bd04b. All8archive chunks, the whole archive SHA256/CRC and every snapshot-manifest file passed verification before extraction. All261original batches remain byte-for-byte unchanged. Every completed current condition has a valid raw/metadata pair, exact expected traffic seeds and unique composite condition/episode keys; saved outcome aggregates were recomputed. All12frozen actors have the expected embedded training seeds and distinct policy-tensor content. Thirteen semantic preflight tests passed. See the independent AUDIT_*.json, MODEL_SEED_AUDIT.json and SMOKE_AUDIT.json files.','',
 f'{len(checked)}original code/protocol/freeze/model artifacts were rechecked against the initial snapshot manifest. No frozen source/model file was changed. The main runner executed only179missing batches; valid original batches returned cached results.','',
 'Previous interruption evidence supports process-environment replacement, but the platform cause is not established. This run used four single-thread workers, process locking, persistent exit/stage logs and verified incremental GitHub checkpoints on backup/recovery-remaining-20261022T102500Z. The original backup branch and visibility settings were not modified. No paid infrastructure was acquired. No exposed control guarantees a non-preemptible machine; remote data verification and resumable complete-pair checkpoints mitigate loss. Current interruption was a reproducible application initialization exception, not a memory kill.','',
 'The ZIP contains the complete restored project, raw/processed results, all frozen code/configurations/models/checkpoints, historical studies/manuscript drafts, logs, vector PDF/300dpi PNG figures, per-seed PDF/LaTeX tables, captions, independent audits and reproduction/recovery tools. Historical files may describe earlier stages; this report and STUDY_COMPLETENESS.json govern current claims. Original Git internals, virtual environments and regenerable caches are excluded and documented. The earlier20000-record study and five-paper author-reported literature comparison are separate; exact paper-specific vehicle reproductions are outside the archived agreed required scope. No new citation or cross-paper numerical winner is invented.']
 (OUT/'SCIENTIFIC_REPORT.md').write_text('\n'.join(lines)+'\n')
 (OUT/'REPRODUCIBILITY.md').write_text('''# Reproducibility and safe continuation
1. Verify the delivered ZIP SHA256 sidecar and every payload path/size/hash in PACKAGE_MANIFEST.json. Source datasets are under project/working; the enriched files under results/ add condition labels and diagnostic-coverage flags. No missing dense-Merge outcomes are represented as collisions or zeros.
2. Use Python3.12.14. Create a venv outside project. Install CPU torch2.14.1 from https://download.pytorch.org/whl/cpu; then install numpy2.3.5,numba0.68.0,stable-baselines3 2.9.0,scipy1.17.0,gymnasium1.4.0 and the exact reporting/test versions in operations/installed-packages.txt. Run pip check. Preserve TLS and artifact verification. No Git worktree is needed; use the existing isolated checkout.
3. Set OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 and writable MPLCONFIGDIR, XDG_CACHE_HOME and NUMBA_CACHE_DIR outside frozen source folders.
4. Do not rerun historical PID waiters, historical prepare.py (236batch assertion) or the initial recovery preflight after progress (261assertion). Current source root was /workspace/recovery/restored/LANS-RISK; helpers record absolute paths and need path-only adaptation when relocated.
5. Main command from project/working/extended_baselines: python experiment.py --stage confirmation --workers 4. All440valid results are now cached; this checks/collects them without recomputing episodes. Protect the original261hashes in operations/PREFLIGHT_261.json and all current manifests. Source hashes must match EXTENDED_FREEZE.json.
6. Observation command from project: python working/observation_delay_study/run_study.py --stage evaluation --workers 4. All200conditions are cached. Independent audit_stage.py validates coverage, seed ranges, raw hashes and saved aggregates. audit_partial_stress.py deliberately reports the original stress stage incomplete at231/264.
7. Do not blindly rerun the original robustness confirmation: it reproducibly fails dense-Merge initialization under the frozen10000-attempt limit. The proposal patch/preflight and separate run_amended_dense_merge.py driver are under operations/proposals. NO amended controller run was authorized or executed. An explicit user-approved protocol exception is required; use a separate source fingerprint/stage, preserve originals, and disclose the amendment. Never rewrite old source hashes or substitute seeds.
8. Runtime raw data: results/runtime_samples.json and operations/runtime_profile.json. The runtime_with_raw.py helper executes the unchanged original profiling loop and retains the50post-warmup samples at its post-loop reduction. It verifies all4800samples against every original summary statistic. A new timing run must preserve the old run and be labelled with its own host/session; do not interpret consecutive samples as independent timing replicates.
9. Existing semantic checks from project: python -m pytest -q working/extended_baselines/test_extended.py working/publication_tools/test_reporting_and_stress.py working/publication_tools/test_sensor_view.py working/observation_delay_study/test_channel.py. All13passed in this recovery. Frozen simulator steps are0.1s, up to160steps; collisions can shorten episodes.
10. Optional full independent replay must use a separate extraction and preserve reference stage directories/summary files outside the replay locations; otherwise the runner correctly returns caches. Never do this to the authoritative recovery tree. Original raw SHA256 values prove integrity, not bitwise equality of newly measured timings. Compare seeded non-timing outcomes, record hardware/software and never count repeated case replays as new independent evidence.
11. Incremental durable recovery is on GitHub branch backup/recovery-remaining-20261022T102500Z. Restore/verify the original chunked snapshot first, then merge matching complete pairs using restore_latest_checkpoint.py; it refuses to overwrite different results. Do not assume processes survive a platform reset. Independent remote byte verification is recorded separately.
12. Environment install/start instructions are a saved draft. Saving does not execute, apply or publish that configuration. Current-instance results are verified; publication and validation in a fresh task have not been performed.
''')
 (OUT/'AVAILABLE_RESULTS_AUDIT.json').write_text(json.dumps(dict(prepared_at_asia_shanghai=now,all_available_data_verified=True,all_requested_experiments_complete=False,main_confirmation_records=44000,original_batches_preserved=261,remaining_main_batches_computed=179,robustness_records=11550,robustness_missing_conditions=33,robustness_unrun_records=1650,observation_records=4000,runtime_conditions=96,raw_timing_samples=4800,development_records=4800,models_with_verified_distinct_tensor_content=12,original_scientific_artifacts_rechecked=len(checked),amendment_executed=False,required_decision='Explicit permission for the separate sampler amendment, or retain frozen-code incompleteness'),indent=2))
 print('REPORT READY: verified available results; full plan explicitly incomplete',flush=True)
def package():
 assert (OUT/'AVAILABLE_RESULTS_AUDIT.json').exists()
 bundle=Path('/workspace/recovery/LANS_RISK_VERIFIED_RESULTS_BLOCKED.zip');pending=bundle.with_suffix('.pending');assert not bundle.exists() and not pending.exists()
 paths=[];excluded=[]
 for p in R.rglob('*'):
  if not p.is_file():continue
  if any(x in {'.git','.venv','.cache','__pycache__','.pytest_cache'} for x in p.parts):excluded.append(str(p.relative_to(R)));continue
  paths.append(('project/'+str(p.relative_to(R)),p))
 for p in OP.rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and p.suffix not in {'.lock','.pending'}:
   name=('results/'+str(p.relative_to(OUT))) if p.is_relative_to(OUT) else 'operations/'+str(p.relative_to(OP));paths.append((name,p))
 for name in ['README.md','RECOVERY_PLAN.md','INVESTIGATION.md','PARTS.json','BACKUP_VERIFICATION.json','SNAPSHOT_MANIFEST.json','EXCLUSIONS.json','restore_and_verify.py']:paths.append(('backup_provenance/'+name,Path('/workspace/LANS-RISK')/name))
 assert len({n for n,p in paths})==len(paths);manifest={}
 with zipfile.ZipFile(pending,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for name,p in sorted(paths):
   b=p.read_bytes();z.writestr(name,b);manifest[name]=dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
  intro=b'''# Verified LANS-RISK results - full plan blocked on one protocol decision
Start with results/SCIENTIFIC_REPORT.md, results/STUDY_COMPLETENESS.json and results/AVAILABLE_RESULTS_AUDIT.json.
Main44000, sensor4000 and runtime4800samples are complete; robustness has11550/13200records. The33dense-Merge conditions are not completed under the frozen sampler.
No sampler amendment/controller experiment has been approved or executed. Proposal-only preflight is clearly labelled under operations/proposals.
results/ contains authoritative new tables/figures/statistics/captions. project/ preserves the full restored research project, frozen code/configs/models/checkpoints, raw data, older studies and logs. operations/ contains recovery/audit/analysis/proposal tools and execution evidence.
Historical manuscript/status files describe their original stages; this report/completeness record govern current claims. Read results/REPRODUCIBILITY.md before replaying anything.
'''
  z.writestr('README.md',intro);manifest['README.md']=dict(bytes=len(intro),sha256=hashlib.sha256(intro).hexdigest())
  z.writestr('PACKAGE_MANIFEST.json',json.dumps(manifest,indent=2));z.writestr('PACKAGE_EXCLUSIONS.json',json.dumps(dict(regenerable_files=excluded,third_party_environment='Not bundled; exact versions and setup instructions included',git_internals='Excluded; commit/ref/hash provenance included',original_archive_chunks='Already verified/reassembled; all restored contents included instead'),indent=2))
 with zipfile.ZipFile(pending) as z:
  assert z.testzip() is None
  for name,x in manifest.items():
   b=z.read(name);assert len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256'],name
 pending.rename(bundle);delivery=dict(path=str(bundle),bytes=bundle.stat().st_size,sha256=sha(bundle),payload_files=len(manifest),zip_crc_and_all_payload_hashes_verified=True,all_requested_experiments_complete=False,blocked_robustness_conditions=33)
 bundle.with_suffix('.json').write_text(json.dumps(delivery,indent=2));print(json.dumps(delivery),flush=True)
if __name__=='__main__':
 if '--package' in sys.argv:package()
 else:prepare_report()
