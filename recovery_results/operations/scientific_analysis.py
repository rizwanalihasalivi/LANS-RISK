"""Supplementary independent, seed-specific descriptive and paired analyses."""
from pathlib import Path
import json,csv,hashlib,sys,os
os.environ.setdefault("XDG_CACHE_HOME","/workspace/recovery/cache")
Path(os.environ["XDG_CACHE_HOME"]).mkdir(parents=True,exist_ok=True)
import numpy as np
from scipy.stats import binomtest,wilcoxon
from audit_stage import audit,R,OP,FREE
OUT=OP/'verified_results';OUT.mkdir(exist_ok=True)
RNG=np.random.default_rng(20261022)
FEAS_LOGGED={'cbf','robust_mpc','lans_no_prediction','lans','robust_lans','robust_no_actor','lans_no_actor'}
def csvout(path,rows):
 assert rows
 with path.open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
def wilson(k,n):
 z=1.959963984540054;p=k/n;den=1+z*z/n
 mid=(p+z*z/(2*n))/den;rad=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
 return max(0,mid-rad),min(1,mid+rad)
def bootmean(a):
 return np.quantile(a[RNG.integers(0,len(a),(5000,len(a)))].mean(axis=1),[.025,.975])
def load(folder,stage):
 audit(folder,stage)
 data={}
 for p in sorted((R/'working'/folder/stage).glob('*.json')):
  x=json.loads(p.read_text());rows=[json.loads(v) for v in p.with_suffix('.jsonl').read_text().splitlines()]
  k=(x.get('profile','fixed_fifo'),x['scenario'],x['controller'],x.get('policy_seed',x.get('actor_seed')),x.get('delay_ms',0))
  assert k not in data;data[k]=rows
 return data

def analyze(folder,stage):
 data=load(folder,stage);out=OUT/folder;out.mkdir(exist_ok=True)
 table=[];long=[];pairs=[]
 for key,rr in data.items():
  profile,scenario,method,seed,delay=key
  labels=dict(study=folder,stage=stage,profile=profile,scenario=scenario,controller=method,actor_seed=seed,delay_ms=delay)
  for r in rr:
   enriched=dict(**labels,**r)
   if 'no_feasible_steps' in r:enriched['no_feasible_steps_available']=method in FEAS_LOGGED
   long.append(enriched)
  for metric in sorted(set.intersection(*(set(r) for r in rr))-{'episode_seed'}):
   vals=np.array([r[metric] for r in rr],float);binary=isinstance(rr[0][metric],bool)
   lo,hi=wilson(int(vals.sum()),len(vals)) if binary else bootmean(vals)
   table.append(dict(**labels,metric=metric,n=len(vals),unit='fraction' if binary else ('ms' if '_ms' in metric else ('m' if metric in ['rmse','npc_position_error_cv','npc_position_error_accel'] else ('steps' if metric in ['steps','no_feasible_steps'] else 'native'))),mean=float(vals.mean()),sample_sd=float(vals.std(ddof=1)),minimum=float(vals.min()),maximum=float(vals.max()),p05=float(np.quantile(vals,.05)),median=float(np.median(vals)),p95=float(np.quantile(vals,.95)),ci95_low=float(lo),ci95_high=float(hi),ci_method='Wilson' if binary else 'percentile bootstrap mean 5000 traffic-case draws',worst_observed=float(vals.min() if metric in ['completion','corridor_completion','progress'] else vals.max())))
   record=table[-1];record.update(raw_episode_records=len(rr),available=True,recording_note='Saved episode metric')
   if metric in ['decision_ms_median','decision_ms_max']:
    record.update(ci95_low=None,ci95_high=None,ci_method='Not inferred: shared execution timing; use sequential diagnostic sample',recording_note='Per-episode timing under shared execution sessions; descriptive variability only')
   if metric=='no_feasible_steps':
    if method in FEAS_LOGGED:record['recording_note']='Controller-specific logged flag; CBF and sampled-plan feasibility have different semantics'
    else:
     record.update(n=0,available=False,recording_note='Runner default or fixed zero; no applicable feasibility measurement',ci_method='Not estimated: unavailable diagnostic')
     for field in ['mean','sample_sd','minimum','maximum','p05','median','p95','ci95_low','ci95_high','worst_observed']:record[field]=None
 for key,ra in data.items():
  profile,s,c,k,d=key
  baselines=sorted({kk[2] for kk in data if kk[2]!='lans'}) if c=='lans' else {'predictor_lqr':['lqr_acc'],'cbf':['ppo_only'],'robust_lans':['robust_no_actor','robust_mpc']}.get(c,[])
  for baseline in baselines:
   kb=0 if baseline in FREE else k;other=(profile,s,baseline,kb,d)
   if other not in data:continue
   rb=data[other];assert [r['episode_seed'] for r in ra]==[r['episode_seed'] for r in rb]
   for m in ['collision','completion','corridor_completion','rmse']:
    if m not in ra[0] or m not in rb[0]:continue
    delta=np.array([float(a[m])-float(b[m]) for a,b in zip(ra,rb)]);lo,hi=bootmean(delta)
    if m!='rmse':
     plus=int((delta>0).sum());minus=int((delta<0).sum());discord=plus+minus
     p=float(binomtest(plus,discord,.5).pvalue) if discord else 1.;test='exact paired discordance (McNemar binomial)'
    else:
     p=float(wilcoxon(delta,zero_method='wilcox',alternative='two-sided',method='auto').pvalue) if np.any(delta) else 1.
     plus=minus=discord=None;test='two-sided Wilcoxon signed-rank (symmetry assumption; scipy auto)'
    pairs.append(dict(study=folder,profile=profile,scenario=s,a=c,b=baseline,actor_seed=k,delay_ms=d,metric=m,n=len(delta),mean_difference_a_minus_b=float(delta.mean()),paired_bootstrap95_low=float(lo),paired_bootstrap95_high=float(hi),discordant_a_true=plus,discordant_b_true=minus,test=test,p_raw=p,p_holm=0.))
 # One explicitly defined multiplicity family: all listed contrasts/metrics in each study, including planned ablations.
 order=np.argsort([r['p_raw'] for r in pairs]);prev=0.
 for rank,idx in enumerate(order):
  prev=max(prev,min(1.,(len(order)-rank)*pairs[idx]['p_raw']));pairs[idx]['p_holm']=prev
 csvout(out/'descriptive_metrics.csv',table);csvout(out/'paired_tests.csv',pairs)
 with (out/'episodes.jsonl').open('w') as f:
  for r in long:f.write(json.dumps(r,allow_nan=False)+'\n')
 # Compact summary at each fixed delay, mean across actor seeds, never an independent sample.
 compare=[]
 for profile,s,d in sorted({(k[0],k[1],k[4]) for k in data}):
  for c in ['lans','mpc_nominal','robust_mpc']:
   rr=[r for key,rows in data.items() if (key[0],key[1],key[2],key[4])==(profile,s,c,d) for r in [rows]]
   if not rr:continue
   v=dict(profile=profile,scenario=s,delay_ms=d,controller=c,actor_seed_conditions=len(rr),traffic_cases_per_actor=len(rr[0]))
   for m in ['collision','completion','corridor_completion','rmse']:
    if m in rr[0][0]:v[m+'_seed_mean']=float(np.mean([np.mean([a[m] for a in row]) for row in rr]))
   compare.append(v)
 csvout(out/'lans_mpc_summary.csv',compare)
 return data

def figures(folder,data):
 import matplotlib
 matplotlib.use('Agg');matplotlib.rcParams['pdf.fonttype']=42;matplotlib.rcParams['ps.fonttype']=42
 import matplotlib.pyplot as plt
 out=OUT/folder
 profiles=sorted({k[0] for k in data})
 for profile in profiles:
  fig,axes=plt.subplots(2,4,figsize=(13,6),sharey=True)
  for i,s in enumerate(['highway','merge','intersection','roundabout']):
   for j,m in enumerate(['collision','corridor_completion']):
    ax=axes[j,i]
    for c in ['lans','mpc_nominal','predictor_lqr','cbf','robust_mpc','lqr_acc']:
     dd=sorted({k[4] for k in data if k[:3]==(profile,s,c)})
     if not dd:continue
     means=[];mins=[];maxs=[]
     for d in dd:
      means_seed=[100*np.mean([r[m] for r in rr]) for key,rr in data.items() if (key[0],key[1],key[2],key[4])==(profile,s,c,d)]
      means.append(np.mean(means_seed));mins.append(min(means_seed));maxs.append(max(means_seed))
     line=ax.plot(dd,means,'o-',label=c,markersize=3)[0];ax.fill_between(dd,mins,maxs,color=line.get_color(),alpha=.12)
    ax.set_title(s);ax.set_ylim(-3,103);ax.grid(alpha=.2);ax.set_xticks(dd)
    if i==0:ax.set_ylabel(m.replace('_',' ')+' (%)')
    if j==1:ax.set_xlabel('Command delay (ms)' if folder!='observation_delay_study' else 'Command delay = 0 ms')
  h,l=axes[0,0].get_legend_handles_labels();fig.legend(h,l,loc='lower center',ncol=3)
  fig.suptitle(folder+' / '+profile+' — '+('exploratory evaluation' if folder=='observation_delay_study' else 'confirmation')+'; seed means and ranges')
  fig.tight_layout(rect=(0,.09,1,.94))
  fig.savefig(out/(profile+'.pdf'));fig.savefig(out/(profile+'.png'),dpi=300);plt.close(fig)

if __name__=='__main__':
 for folder,stage in [('extended_baselines','confirmation'),('stress_study','confirmation'),('observation_delay_study','evaluation')]:
  data=analyze(folder,stage);figures(folder,data)
 (OUT/'STATISTICAL_METHODS.md').write_text('''# Statistical methods and interpretation
All condition-level estimates retain scenario, delay/profile and actor seed. Traffic seeds are paired across methods. Actor repetitions are not additional independent traffic cases; actor-free baselines are run once. Binary means/SD/CIs are fractions in descriptive_metrics.csv. The sample SD describes episode outcomes, not the standard error. Wilson 95% intervals describe each event rate; no observed collisions does not imply zero true risk. Continuous non-timing outcome means and paired-difference intervals use5000 percentile bootstrap draws of traffic cases with deterministic analysis seed20261022. These intervals are marginal and not simultaneous; degenerate intervals at zero discordance do not prove equivalence. Exact paired-discordance tests apply to binary outcomes. RMSE uses two-sided Wilcoxon signed-rank tests, which require a symmetric distribution of paired differences for a location interpretation. Ties/zeros are handled by SciPy auto/wilcox; all-zero differences receive p=1. Holm correction covers all listed contrasts and outcomes within each study (LANS versus each comparator plus predictor-LQR/LQR+ACC, CBF/PPO-only and robust-LANS/actor-free or robust-MPC where available); it does not combine the historical studies or bootstrap interval coverage. Positive a-minus-b differences favor method a for completion, and favor method b for collisions/RMSE. Descriptive seed means are not extra statistical samples. Worst values are observed episode extremes, not safety bounds or WCET. The raw no_feasible_steps field is meaningful only for CBF and the nominal/robust sampled-plan LANS variants (including robust_mpc). MPC nominal, PPO-only and plain LQR methods have no such recorded flag; predictor LQR hardcodes it false. Their runner-default zeros are marked unavailable in processed descriptive tables and with a coverage flag in enriched episode files. Feasibility-flag semantics also differ between CBF and finite candidate planners, so these counts do not establish solver feasibility or support a cross-method infeasibility ranking. Metrics absent from saved raw data (including RMSE in the observation-delay study and unrecorded near-miss/jerk metrics) are unavailable and are never fabricated. Main-study per-episode timing means/SD are descriptive and their confidence intervals are not inferred under shared execution sessions. Runtime mean/SD are descriptive over50consecutive evolving-state calls; no independent-replicate confidence interval is inferred for that timing sample. Runtime values are host-dependent diagnostics; old and new confirmation timings are from different execution sessions and must not be treated as a controlled speed comparison. Sequential runtime_profile.json is the current-machine timing evidence.\n''')
 print('COMPLETE independent scientific analysis',flush=True)
 # Additional observation figure compares the five distribution profiles at zero command delay.
 import matplotlib.pyplot as plt
 obs=load('observation_delay_study','evaluation')
 profiles=['uniform','bimodal','bursty','triangular','exponential']
 fig,axes=plt.subplots(2,4,figsize=(14,7),sharey=True)
 for i,s in enumerate(['highway','merge','intersection','roundabout']):
  for j,metric in enumerate(['collision','corridor_completion']):
   ax=axes[j,i]
   for c in ['lans','mpc_nominal','predictor_lqr','cbf','robust_mpc','lqr_acc']:
    mean=[];low=[];high=[]
    for p in profiles:
     v=[100*np.mean([r[metric] for r in rows]) for k,rows in obs.items() if k[:3]==(p,s,c)]
     mean.append(np.mean(v));low.append(min(v));high.append(max(v))
    line=ax.plot(range(5),mean,'o-',label=c,markersize=3)[0]
    ax.fill_between(range(5),low,high,color=line.get_color(),alpha=.1)
   ax.set_xticks(range(5),profiles,rotation=35,ha='right');ax.set_ylim(-3,103);ax.set_title(s);ax.grid(alpha=.2)
   if i==0:ax.set_ylabel(metric.replace('_',' ')+' (%)')
 h,l=axes[0,0].get_legend_handles_labels();fig.legend(h,l,loc='lower center',ncol=3)
 fig.suptitle('Exploratory delayed full-state observations; zero command delay')
 fig.tight_layout(rect=(0,.08,1,.95));fig.savefig(OUT/'observation_profiles.pdf');fig.savefig(OUT/'observation_profiles.png',dpi=300);plt.close(fig)
 runtime=json.loads((R/'deliverables/publication_results/runtime_profile.json').read_text())
 assert runtime['source_hashes']==json.loads((R/'working/extended_baselines/EXTENDED_FREEZE.json').read_text())['sha256']
 assert len(runtime['results'])==96
 seen=set()
 for row in runtime['results']:
  k=row['scenario'],row['controller'],row['delay_ms'];assert k not in seen;seen.add(k)
  assert row['n']==50 and 0<=row['median_ms']<=row['p95_ms']<=row['p99_ms']<=row['max_ms']
  assert 0<=row['exceeded_100ms']<=50
 raw_runtime=json.loads((OP/'runtime_samples.json').read_text())
 assert raw_runtime['conditions']==96 and raw_runtime['timed_samples']==4800
 assert raw_runtime['source_hashes']==runtime['source_hashes']
 (OUT/'runtime_samples.json').write_text(json.dumps(raw_runtime,indent=2))
 for row in runtime['results']:
  raw=next(x for x in raw_runtime['samples'] if (x['scenario'],x['controller'],x['delay_ms'])==(row['scenario'],row['controller'],row['delay_ms']))
  a=np.array(raw['samples_ms']);assert len(a)==50 and np.isfinite(a).all()
  row.update(mean_ms=float(a.mean()),sample_sd_ms=float(a.std(ddof=1)),minimum_ms=float(a.min()),mean_ci95_low=None,mean_ci95_high=None,ci_note='Not inferred: consecutive evolving-state calls; no independent timing replicates')
 csvout(OUT/'runtime_current_host.csv',runtime['results'])
 fig,axes=plt.subplots(2,2,figsize=(14,9))
 for ax,s in zip(axes.flat,['highway','merge','intersection','roundabout']):
  methods=sorted({r['controller'] for r in runtime['results']});x=np.arange(len(methods))
  for d,off in [(0,-.16),(1000,.16)]:
   rows=[next(r for r in runtime['results'] if (r['scenario'],r['controller'],r['delay_ms'])==(s,c,d)) for c in methods]
   median=np.array([r['median_ms'] for r in rows]);p99=np.array([r['p99_ms'] for r in rows])
   ax.bar(x+off,median,.3,label=f'{d} ms FIFO: median')
   ax.scatter(x+off,p99,marker='_',color='black',s=25)
  ax.axhline(100,color='red',ls='--',lw=.8);ax.set_yscale('log');ax.set_title(s);ax.set_ylabel('Decision time (ms, log scale)');ax.set_xticks(x,methods,rotation=65,ha='right');ax.grid(axis='y',alpha=.2)
 axes[0,0].legend(fontsize=8);fig.suptitle('Sequential warmed CPU measurements: bars median, black ticks p99')
 fig.tight_layout(rect=(0,0,1,.96));fig.savefig(OUT/'runtime.pdf');fig.savefig(OUT/'runtime.png',dpi=300);plt.close(fig)
 (OUT/'FIGURE_CAPTIONS.md').write_text('''# Figure and table captions
- `extended_baselines/fixed_fifo.pdf`: Independent confirmation over100 traffic cases per condition; nominal LANS, nominal acceleration-aware CEM MPC, predictor LQR, numerical CBF, finite-scenario robust MPC and LQR+ACC. Rows show collision and corridor completion; columns show the four scenarios. Lines average the three frozen actor seeds where applicable; shading is their minimum–maximum range, not a confidence interval. Actor-free baselines are run once on the same traffic cases. Physical command FIFO spans0–1000ms. Per-seed Wilson intervals and paired Holm-adjusted tests are in the adjacent CSV files.
- `stress_study/weaker_actuation.pdf` and `denser_traffic.pdf`: Prespecified frozen-controller sensitivity checks,50 new traffic cases per condition. The two perturbations are evaluated separately. Same line/shading conventions as above. These are synthetic model-mismatch and traffic-density tests; no real-traffic guarantee follows.
- `observation_profiles.pdf`: Exploratory full-state stochastic sensor-delay evaluation with20 new traffic cases per condition and five explicit synthetic distributions. Physical command delay is zero. Lines show seed means and shaded seed ranges. The initial state is known; subsequent observed state may be stale. This is separate from the fixed command-delay study and is not a DAROM reproduction. See per-seed rate intervals; small samples and zero events do not prove zero risk.
- `runtime.pdf`: Sequential warmed decision-time diagnostics on this cloud CPU, actor42 where needed,20 warmup then50 timed calls per condition. Bars show median and black ticks p99; the dashed100ms line is the simulator step duration. Timing affects neither the frozen FIFO nor plant dynamics. Samples span evolving states and resets, not repeated identical states; p99 with50 calls is an empirical upper quantile, not a hard deadline or WCET guarantee.
- Historical/legacy `main_latency` and `ablations_latency` figures under `project/deliverables/publication_results/confirmation/` show the complete12-controller confirmation including the prespecified ablations. Seed-range shading is descriptive. Tables retain all losses and ties. No universal controller winner is assumed.
- `descriptive_metrics.csv`: Per condition and metric, count, sample SD, observed extrema/quantiles, mean and marginal95% interval. Binary quantities use fractions, not percentages. No actor-seed pooling is used for inference. Additional inherited analyses under project use their own documented bootstrap seeds and contrast/multiplicity families; their Monte Carlo intervals or adjusted p values can differ. Use results/ as the authoritative new analysis and do not interchange those inference definitions. `paired_tests.csv` reports paired a-minus-b effects for the listed baseline and ablation contrasts, bootstrap intervals, raw p values and Holm p values within each study. `lans_mpc_summary.csv` averages actor-seed condition means only for display.
''')
 print('COMPLETE figures/runtime validation',flush=True)
 # Publication tables retain every LANS actor separately beside the actor-free MPC baseline.
 from matplotlib.backends.backend_pdf import PdfPages
 import csv
 for folder in ['extended_baselines','stress_study','observation_delay_study']:
  with (OUT/folder/'descriptive_metrics.csv').open() as f:descriptive=list(csv.DictReader(f))
  selected=[x for x in descriptive if x['controller'] in ['lans','mpc_nominal']]
  lookup={(x['profile'],x['scenario'],x['controller'],x['actor_seed'],int(x['delay_ms']),x['metric']):x for x in selected}
  rowkeys=sorted({k[:-1] for k in lookup})
  has_rmse=any(x['metric']=='rmse' for x in selected)
  columns=['Profile / FIFO (ms)','Controller / actor','Collision % [95% CI]','Corridor completion % [95% CI]']+(['RMSE m: mean (SD)'] if has_rmse else [])
  tex=['% Requires booktabs and longtable. Rates and confidence intervals in percent; n per condition shown in caption.',r'\begin{longtable}{llcc'+('c' if has_rmse else '')+'}',r'\caption{'+folder.replace('_',' ')+r': paired-case LANS and nominal MPC, per actor seed. Wilson95\% intervals; RMSE reports sample SD.}'+r'\\',r'\toprule',' & '.join(x.replace('%',r'\%') for x in columns)+r' \\',r'\midrule']
  with PdfPages(OUT/folder/'publication_tables.pdf') as pdf:
   for scenario in ['highway','merge','intersection','roundabout']:
    table=[]
    tex.append(r'\multicolumn{'+str(len(columns))+r'}{l}{\textbf{'+scenario+r'}} \\')
    for profile,s,c,k,d in rowkeys:
     if s!=scenario:continue
     metric=lambda m:lookup[profile,s,c,k,d,m]
     rate=lambda m:f"{100*float(metric(m)['mean']):.1f} [{100*float(metric(m)['ci95_low']):.1f}, {100*float(metric(m)['ci95_high']):.1f}]"
     row=[profile.replace('_',' ')+f' / {d}',('LANS / '+k) if c=='lans' else 'MPC / actor-free',rate('collision'),rate('corridor_completion')]
     if has_rmse:
      rmse=metric('rmse');row.append(f"{float(rmse['mean']):.3f} ({float(rmse['sample_sd']):.3f})")
     table.append(row);tex.append(' & '.join(row)+r' \\')
    fig,ax=plt.subplots(figsize=(13,8));ax.axis('off')
    ax.set_title(folder.replace('_',' ')+' — '+scenario+'; per-seed estimates',fontsize=13,pad=18)
    t=ax.table(cellText=table,colLabels=columns,cellLoc='center',loc='center',colWidths=([.21,.16,.21,.26,.16] if has_rmse else [.27,.21,.23,.29]))
    t.auto_set_font_size(False);t.set_fontsize(8);t.scale(1,1.65)
    for (row,col),cell in t.get_celld().items():
     cell.set_linewidth(.25)
     if row==0:cell.set_facecolor('#e7edf3');cell.set_text_props(weight='bold')
     elif row%2==0:cell.set_facecolor('#f4f6f8')
    n=100 if folder=='extended_baselines' else (50 if folder=='stress_study' else 20)
    fig.text(.5,.04,f'n={n} paired traffic cases per condition. Repeated actor seeds share traffic cases; intervals are marginal Wilson95%.\nMPC is run once per condition. RMSE SD describes episode variability; paired tests are in paired_tests.csv.',ha='center',fontsize=9)
    fig.tight_layout(rect=(.02,.09,.98,.96));pdf.savefig(fig);fig.savefig(OUT/folder/('publication_table_'+scenario+'.png'),dpi=300);plt.close(fig)
  tex.extend([r'\bottomrule',r'\end{longtable}'])
  (OUT/folder/'publication_tables.tex').write_text('\n'.join(tex)+'\n')
 with (OUT/'FIGURE_CAPTIONS.md').open('a') as f:f.write('\n- `publication_tables.pdf`/`.tex` in each study: per-scenario LANS actors42/43/44 and actor-free nominal MPC tables. Each row retains its own paired traffic sample, n=100/50/20 for main/robustness/observation studies. Binary rates use marginal Wilson95% intervals. RMSE is mean (sample SD) when present; no RMSE is invented for observation delay. LaTeX requires booktabs/longtable. Tables preserve failures and do not pool actor repetitions.\n')
 print('COMPLETE publication tables',flush=True)
