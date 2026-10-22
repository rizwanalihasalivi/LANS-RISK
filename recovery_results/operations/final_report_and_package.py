"""Final report + complete immutable archive; requires every independent audit."""
from pathlib import Path
import json,csv,hashlib,zipfile,datetime,shutil,sys,fcntl,subprocess
from zoneinfo import ZoneInfo
from audit_stage import audit,R,OP
OUT=OP/'verified_results'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csvread(p):
 with p.open() as f:return list(csv.DictReader(f))

def main():
 audits=[audit('extended_baselines','development'),audit('extended_baselines','confirmation'),audit('stress_study','confirmation'),audit('observation_delay_study','evaluation')]
 runtime=json.loads((R/'deliverables/publication_results/runtime_profile.json').read_text());assert len(runtime['results'])==96
 freeze=json.loads((R/'working/extended_baselines/EXTENDED_FREEZE.json').read_text())['sha256']
 for name,h in freeze.items():assert sha(R/'working'/name)==h
 for folder in ['extended_baselines','stress_study','observation_delay_study']:
  for file in ['descriptive_metrics.csv','paired_tests.csv','episodes.jsonl','lans_mpc_summary.csv']:assert (OUT/folder/file).stat().st_size>0
 old=json.loads((OP/'PREFLIGHT_261.json').read_text())
 for name,h in old['existing_result_hashes'].items():assert sha(R/name)==h
 # Every restored .py, protocol, freeze file and model from the original snapshot must remain unchanged.
 original=json.loads(Path('/workspace/LANS-RISK/SNAPSHOT_MANIFEST.json').read_text());checked=[]
 for name,item in original.items():
  p=R/name
  if p.suffix=='.py' or p.name in ['PROTOCOL.md','EXTENDED_FREEZE.json','FREEZE.json'] or ('models' in str(p.parent) and p.suffix in ['.zip','.json']):
   assert p.exists() and sha(p)==item['sha256'],('original scientific artifact changed',name)
   checked.append(name)
 now=datetime.datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
 doc=dict(completed_at_asia_shanghai=now,backup_commit='d306a7bea4c4f7399cc91c9e4891055bc47bd04b',archive_sha256='1a6f4c4133b52f93e27dffb2242aa82881b6391fa9c619bd9a74a5d90ce0643e',original_batches_unchanged=261,new_confirmation_batches=179,confirmation_records=44000,stress_records=13200,observation_delay_records=4000,development_records=4800,runtime_conditions=96,timed_calls_per_runtime_condition=50,retained_raw_timing_samples=4800,semantic_preflight_tests_passed=13,smoke_records_hash_verified=176,all_planned_synthetic_studies_audited=True,original_scientific_artifacts_rechecked=len(checked),code_models_settings_unchanged=True,network_github_backup_branch_verified=True,scope='Frozen synthetic suite and archived reported-results literature comparison; paper-specific vehicle reproductions not claimed')
 (OUT/'FINAL_VERIFIED.json').write_text(json.dumps(doc,indent=2));(OP/'FINAL_VERIFIED.json').write_text(json.dumps(doc,indent=2))
 # Wait for our final incremental mirror to finish before archiving its logs.
 with (OP/'remote-checkpoint.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
 subprocess.run([sys.executable,str(OP/'verify_remote.py')],check=True)
 summary=csvread(OUT/'extended_baselines/lans_mpc_summary.csv')
 # Compute empirical tolerance independently, requiring every lower tested delay to pass.
 data={}
 for p in (R/'working/extended_baselines/confirmation').glob('*.json'):
  x=json.loads(p.read_text());data[x['scenario'],x['controller'],x['policy_seed'],x['delay_ms']]=x
 thresholds=[]
 for s,c,k in sorted({v[:3] for v in data}):
  last=None
  for delay in [0,200,500,700,1000]:
   x=data[s,c,k,delay]
   if x['collision']>1.00000001 or x['corridor_completion']<89.99999999:break
   last=delay
  thresholds.append(dict(scenario=s,controller=c,actor_seed=k,empirical_contiguous_passing_delay_ms=last,upper_grid_censored=last==1000))
 with (OUT/'empirical_delay_tolerance.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(thresholds[0]));w.writeheader();w.writerows(thresholds)
 lines=['# LANS-RISK: verified experimental results','',f'Completed: {now} (Asia/Shanghai).','',
 'The frozen synthetic experimental plan is complete:44000 independent-confirmation episode records across440 conditions,13200 model-mismatch/density records across264 conditions,4000 exploratory observation-delay records across200 conditions, and96 sequential runtime conditions with50 timed calls each. The4800 development records were independently rechecked. “Independent confirmation” means held-out traffic relative to development; repeated actor seeds and methods share paired traffic cases. No cross-paper numerical winner is inferred.','',
 '## Recovery and integrity','',
 'Recovered GitHub commit `d306a7bea4c4f7399cc91c9e4891055bc47bd04b`; remote backup branch matched this SHA. All eight part hashes, whole ZIP SHA256/CRC and every snapshot-manifest file passed verification before extraction. The261 original batches/26100 episodes remain byte-for-byte unchanged. Only179 missing confirmation batches were computed. Every completed condition has a verified metadata/raw pair, matching frozen source fingerprint, expected traffic seed sequence and unique composite condition/episode key. Summary metrics were recomputed from raw records. See independent `AUDIT_*.json` files and `FINAL_VERIFIED.json`.','',
 f'{len(checked)} restored code/protocol/freeze/model artifacts were compared with the original snapshot manifest at finalization. Frozen experiment code, models, seeds, controller parameters and confirmation settings were not changed. Recovery/analysis tools live outside the experiment tree.','',
 'The earlier log evidence supports process-environment replacement; it does not identify the platform termination cause. This run used four single-thread workers, process locking, persistent stage logs and periodic verified local copies. Incremental verified checkpoints were also pushed to the separate GitHub branch `backup/recovery-remaining-20261022T102500Z`, with remote-ref verification logged in `REMOTE_CHECKPOINTS.jsonl`; the original backup branch and repository visibility were preserved. No paid infrastructure was acquired. These measures cannot prevent future platform resets or turn same-disk copies into independent durable storage.','',
 '## LANS versus matched MPC','',
 'The nominal MPC baseline shares traffic, information access, plant, physical FIFO, action limits, reference-speed ceiling, acceleration-aware predictor,30-step horizon and3×192 candidate search budget with nominal LANS. Controller objectives, ranking, trajectory retention, actor use and warm-start representation differ; equal samples do not prove equal compute. The finite-scenario robust variants use their documented matched scenario budgets. These are generic synthetic baselines, not certified tube MPC or paper-specific reproductions.','',
 'At the1000ms command-delay endpoint, the table gives collision and corridor completion percentages. LANS entries are descriptive means over the three actor seeds; MPC runs once on the same100 traffic cases. Inference remains per actor seed in the CSVs.','',
 '| Scenario | LANS collision % | MPC collision % | LANS corridor completion % | MPC corridor completion % |','|---|---:|---:|---:|---:|']
 for s in ['highway','merge','intersection','roundabout']:
  a=next(x for x in summary if x['scenario']==s and x['controller']=='lans' and x['delay_ms']=='1000')
  b=next(x for x in summary if x['scenario']==s and x['controller']=='mpc_nominal' and x['delay_ms']=='1000')
  lines.append(f"| {s} | {100*float(a['collision_seed_mean']):.2f} | {100*float(b['collision_seed_mean']):.2f} | {100*float(a['corridor_completion_seed_mean']):.2f} | {100*float(b['corridor_completion_seed_mean']):.2f} |")
 lines+=['','Empirical delay criterion: collision<=1% and corridor completion>=90% at every lower tested delay. Values are observed grid thresholds, not certified bounds or statistically demonstrated1% risk guarantees. A1000ms threshold is right-censored at the largest tested delay.','', '| Scenario | LANS seed42 /43 /44 (ms) | Nominal MPC (ms) |','|---|---|---|']
 for s in ['highway','merge','intersection','roundabout']:
  def tol(c,k):
   x=next(x for x in thresholds if (x['scenario'],x['controller'],x['actor_seed'])==(s,c,k))['empirical_contiguous_passing_delay_ms']
   return 'none' if x is None else str(x)
  lines.append(f"| {s} | {' / '.join(tol('lans',k) for k in [42,43,44])} | {tol('mpc_nominal',0)} |")
 lines+=['','All12 controllers, all delays and all ablations are retained. LANS-without-prediction and actor-free LANS isolate their documented changes; PPO-only removes the supervisor bundle and does not isolate one safety mechanism. Robust-LANS versus robust-no-actor assesses the actor within that variant. See all-seed tables and paired tests for ties, losses and uncertainty; no universal overall superiority claim is made.','',
 '## Robustness, sensor delay and timing','',
 'The prespecified robustness profiles separately reduce acceleration/steering authority to80%/90% or add one NPC, using50 fresh cases per condition at0/500/1000ms. The exploratory sensor-delay study evaluates uniform, bimodal, bursty, triangular and exponential packet-delay profiles on20 fresh cases per condition, with zero physical command delay. All observations after the known initial state can be stale. These protocols answer different questions and must not be pooled.','',
 'Current-machine sequential timing uses20 warmup calls followed by50 timed calls for each scenario/controller at0/1000ms command FIFO, actor42 where applicable. All4800 warmed timing samples were retained by an external helper at the original script’s post-loop median reduction, without changing its clock or timed controller calls. Every timing statistic was recomputed exactly. See `runtime_samples.json`, `runtime_current_host.csv` and `runtime.pdf`. Shared-host scheduling and changing states affect times. The observed maximum/p99 is not a WCET bound. Confirmation runtime records span the old and restored machines and are diagnostic only.','',
 '## Statistics and supported metrics','',
 'Per-condition files provide mean, sample SD, observed minimum/maximum and quantiles, and95% intervals for every saved numeric outcome. Binary rates use Wilson intervals; continuous means use5000 deterministic bootstrap draws over traffic cases. Paired LANS-minus-baseline tests use exact discordance tests for binary outcomes and Wilcoxon signed-rank for RMSE, with Holm correction across the listed tests within each study. Marginal bootstrap intervals are not multiplicity-adjusted. See `STATISTICAL_METHODS.md` for assumptions, units and direction.','',
 'Safety outcomes include collision, corridor completion/exceedance and infeasible-step counts where recorded. RMSE, progress, timeouts and predictor errors are available in the main study; robustness preserves RMSE. Observation-delay raw data do not contain RMSE, so none is invented. Unrecorded near-miss, minimum-clearance, jerk and energy metrics cannot be reconstructed from these aggregate episode records. Raw files are episode-level, not full state/action trajectories: episode RMSE and simulator event flags are checked against frozen computation logic, while their stage aggregates are independently recomputed. Per-step RMSE cannot be independently rederived without unstored trajectories.','',
 '## Figures, tables and reproducibility','',
 'Start with the adjacent `FIGURE_CAPTIONS.md`, `empirical_delay_tolerance.csv` and per-study `descriptive_metrics.csv`, `paired_tests.csv`, `lans_mpc_summary.csv`, `episodes.jsonl`. PDF figures are vector graphics; additional PNGs are300dpi. The complete12-controller ablation figures and tables are under `project/deliverables/publication_results/confirmation/`. Historical results remain clearly separate.','',
 'The archived five-paper comparison retains author-reported results and source-version limitations in `project/deliverables/publication_results/PAPER_REPORTED_COMPARISON.md`; those citations and numbers are not newly reproduced here. See the archived `CURRENT_SCOPE.json`: exact paper-specific vehicle reproductions were explicitly outside the agreed required scope. No new citation or paper-specific significance claim is introduced.','',
 'The ZIP includes the complete restored project with code, configurations, models/checkpoints, raw/processed data, historical evidence and logs, plus recovery scripts, independent audits and all new reporting. Original Git internals, virtual environments and regenerable caches are excluded; installed package versions and instructions are included. `PACKAGE_MANIFEST.json` gives every included file hash. See `REPRODUCIBILITY.md` for audit and replay commands.','',
 '## Limitations','',
 'Synthetic finite-horizon disc-vehicle scenarios, fixed trained actors and100 confirmation traffic cases per condition limit generalization. No real-vehicle safety claim, formal feasibility/safety guarantee, equal-wall-time comparison, cross-paper leaderboard, zero-risk proof, or unsampled-delay guarantee is supported. Observation-delay evaluation is exploratory and small. The frozen plan and completed data are preserved rather than altered to improve results.']
 (OUT/'FINAL_SCIENTIFIC_REPORT.md').write_text('\n'.join(lines)+'\n')
 (OUT/'REPRODUCIBILITY.md').write_text('''# Reproducibility
The archive is self-contained for scientific artifacts; dependencies must be installed from their verified package registries. Do not overwrite results to reproduce them. Use a separate extraction directory for an optional fresh rerun; audit retained results first. No Git worktree is needed.

1. Verify the ZIP SHA256 in the delivery sidecar. Then verify each path/size/SHA256 in PACKAGE_MANIFEST.json. Preserve historical logs as evidence.
2. Python3.12.14; create a venv outside `project`. Install CPU torch2.14.1 from https://download.pytorch.org/whl/cpu, then numpy2.3.5,numba0.68.0,stable-baselines3 2.9.0,scipy1.17.0,gymnasium1.4.0 and reporting/test dependencies from `operations/installed-packages.txt`. CPU torch uses the CPU index; do not silently substitute GPU packages or different core versions. Run pip check. Keep TLS/signature verification enabled.
3. Set OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 and writable MPLCONFIGDIR/NUMBA_CACHE_DIR outside frozen source folders.
4. Existing original commands, from `project/working/extended_baselines`: python experiment.py --stage confirmation --workers 4. Valid completed metadata/raw pairs are cached. Never change source/model hashes, seeds, traffic ranges or parameters. Historical absolute paths and PID waiters are not portable. Recovery helpers in `operations/` record the exact paths used on this machine; adapt only root paths on a fresh machine.
5. Subsequent stage commands from `project`: python working/stress_study/experiment.py --stage confirmation --workers 4; python ../operations/runtime_with_raw.py (after adjusting its root paths, this executes the unchanged runtime_profile.py and retains its post-loop sample array); python working/observation_delay_study/run_study.py --stage evaluation --workers 4. Run sequentially, not together, and validate each stage before continuing. Do not rerun stages merely to obtain more favorable results.
6. Existing semantic preflight: python -m pytest -q working/extended_baselines/test_extended.py working/publication_tools/test_reporting_and_stress.py working/publication_tools/test_sensor_view.py working/observation_delay_study/test_channel.py. All13 checks passed in this recovery.
7. Independent audit/analysis scripts in `operations` validate exact condition sets, expected seeds, paired raw hashes, frozen sources, unchanged original261 batches and recomputed summaries. Their ROOT constants point to the recorded restored path; adjust paths for relocation only. Operations scripts are not frozen experiment code. Audit source fingerprints first. For optional fresh experiments, preserve the original archive and separately retain generated data; incomplete writes have no mid-batch recovery and must be preserved/quarantined before retries.
8. For platform-reset recovery, the separate GitHub branch `backup/recovery-remaining-20261022T102500Z` contains incremental `recovery_results` with raw pairs, hashes and recovery tools. Restore/verify the original snapshot first, then use `operations/restore_latest_checkpoint.py` (adjust only root paths if relocated) to merge matching pairs without overwriting different files. Rerun coverage/freeze checks before resumption. Runtime and final reporting are delivered in this ZIP; do not assume live processes survive.
9. `FINAL_VERIFIED.json` and `AUDIT_*.json` record current-instance verification. Saving onboarding install/start instructions is separate from publishing an environment snapshot. Process survival or restoration in a future cloud task has not been independently verified.
''')
 # Copy key reporting outputs to the ZIP top-level; preserve full project paths below.
 bundle=Path('/workspace/recovery/LANS_RISK_VERIFIED_RESULTS.zip');pending=bundle.with_suffix('.pending')
 assert not bundle.exists() and not pending.exists()
 exclusions=[];paths=[]
 for p in R.rglob('*'):
  if not p.is_file():continue
  if any(v in {'__pycache__','.pytest_cache','.cache','.venv','.git'} for v in p.parts):exclusions.append(str(p.relative_to(R)));continue
  paths.append(('project/'+str(p.relative_to(R)),p))
 for p in OP.rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and p.suffix not in {'.lock','.pending'}:
   name=('results/'+str(p.relative_to(OUT))) if p.is_relative_to(OUT) else 'operations/'+str(p.relative_to(OP))
   paths.append((name,p))
 for name in ['README.md','RECOVERY_PLAN.md','INVESTIGATION.md','PARTS.json','BACKUP_VERIFICATION.json','SNAPSHOT_MANIFEST.json','EXCLUSIONS.json','restore_and_verify.py']:
  paths.append(('backup_provenance/'+name,Path('/workspace/LANS-RISK')/name))
 assert len({n for n,p in paths})==len(paths)
 manifest={}
 with zipfile.ZipFile(pending,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for name,p in sorted(paths):
   b=p.read_bytes();z.writestr(name,b);manifest[name]=dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
  intro=b'''# Verified LANS-RISK results package
Start with results/FINAL_SCIENTIFIC_REPORT.md, results/FINAL_VERIFIED.json and results/FIGURE_CAPTIONS.md.
results/ contains new independently audited tables, statistical methods and publication figures.
project/ contains the complete restored research project, all frozen code/models/configurations, raw data, historical studies/checkpoints and logs.
operations/ contains recovery, checkpointing, independent audit/analysis/packaging scripts and execution logs.
backup_provenance/ records the original verified GitHub snapshot and restoration procedure.
Historical manuscript drafts and status files under project/ describe their original stages; use results/FINAL_SCIENTIFIC_REPORT.md for the current scientific findings and limitations.
Verify PACKAGE_MANIFEST.json and the delivered ZIP SHA256 sidecar before use. Read results/REPRODUCIBILITY.md before replaying experiments. No live process or platform persistence guarantee is implied.
'''
  z.writestr('README.md',intro);manifest['README.md']=dict(bytes=len(intro),sha256=hashlib.sha256(intro).hexdigest())
  z.writestr('PACKAGE_MANIFEST.json',json.dumps(manifest,indent=2))
  z.writestr('PACKAGE_EXCLUSIONS.json',json.dumps(dict(excluded_regenerable_files=exclusions,third_party_environment='Excluded; installed-packages.txt and setup instructions provided',outer_git_chunks='Already reassembled/verified; full restored content included instead'),indent=2))
 with zipfile.ZipFile(pending) as z:
  assert z.testzip() is None
  for name,item in manifest.items():
   b=z.read(name);assert len(b)==item['bytes'] and hashlib.sha256(b).hexdigest()==item['sha256'],name
 pending.rename(bundle)
 delivery=dict(path=str(bundle),bytes=bundle.stat().st_size,sha256=sha(bundle),files=len(manifest),zip_crc_and_all_payload_hashes_verified=True)
 bundle.with_suffix('.json').write_text(json.dumps(delivery,indent=2));print(json.dumps(delivery),flush=True)
if __name__=='__main__':main()
