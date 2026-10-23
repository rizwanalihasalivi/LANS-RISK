"""Second implementation checks processed tables against immutable raw records."""
import csv,json,math,hashlib,datetime
from pathlib import Path
import numpy as np
from scipy.stats import binomtest,wilcoxon,norm
R=Path('/workspace/recovery/restored/LANS-RISK');OP=Path('/workspace/recovery/operations');OUT=OP/'final_verified_results'
FREE={'predictor_lqr','robust_mpc','mpc_nominal','lqr','lqr_acc','robust_no_actor','lans_no_actor'}
FIELDS=['profile','scenario','controller','actor_seed','delay_ms']
def readcsv(p):
 with p.open() as f:return list(csv.DictReader(f))
def key(x):return (x.get('profile','fixed_fifo'),x['scenario'],x['controller'],int(x.get('actor_seed',x.get('policy_seed'))),int(x.get('delay_ms',0)))
def close(a,b):assert math.isclose(float(a),float(b),rel_tol=2e-11,abs_tol=2e-11),(a,b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 summary={};stage_seeds={};total_metrics=total_tests=0
 rng=np.random.default_rng(20261022)
 for study,stage,expected,n,first in [('extended_baselines','confirmation',440,100,141000),('stress_study','confirmation',264,50,161000),('observation_delay_study','evaluation',200,20,181000)]:
  dirs=[R/'working'/study/stage]
  if study=='stress_study':dirs.append(R/'working'/study/'amended_dense_merge_confirmation')
  raw={};source_versions={}
  for folder in dirs:
   for p in folder.glob('*.json'):
    meta=json.loads(p.read_text());k=key(meta);assert k not in raw
    assert sha(p.with_suffix('.jsonl'))==meta['raw_sha256']
    rows=[json.loads(line) for line in p.with_suffix('.jsonl').read_text().splitlines()]
    assert len(rows)==n and [x['episode_seed'] for x in rows]==list(range(first,first+n))
    raw[k]=rows;source_versions[k]='approved_initialization_amendment' if folder.name.startswith('amended_') else 'original_frozen'
  assert len(raw)==expected
  enriched={};count=0
  with (OUT/study/'episodes.jsonl').open() as f:
   for line in f:
    x=json.loads(line);k=key(x);seed=x['episode_seed'];composite=k+(seed,);assert composite not in enriched
    assert x['source_version']==source_versions[k]
    reference=raw[k][seed-first]
    assert all(x[field]==value for field,value in reference.items())
    enriched[composite]=True;count+=1
  assert count==expected*n
  metrics=readcsv(OUT/study/'descriptive_metrics.csv');metric_keys=set()
  for row in metrics:
   k=key(row);m=row['metric'];assert (k,m) not in metric_keys;metric_keys.add((k,m))
   assert row['source_version']==source_versions[k] and int(row['raw_episode_records'])==n
   vals=np.asarray([x[m] for x in raw[k]],dtype=float)
   bootstrap=None
   if not isinstance(raw[k][0][m],bool):
    draws=rng.integers(0,n,size=(5000,n));bootstrap=np.percentile(np.take(vals,draws).mean(axis=1),[2.5,97.5])
   if row['available']=='False':
    assert m=='no_feasible_steps' and k[2] not in {'cbf','robust_mpc','lans_no_prediction','lans','robust_lans','robust_no_actor','lans_no_actor'}
    assert row['mean']==row['ci95_low']==row['ci95_high']=='' and int(row['n'])==0
    continue
   assert int(row['n'])==n
   for field,v in [('mean',vals.mean()),('sample_sd',vals.std(ddof=1)),('minimum',vals.min()),('maximum',vals.max()),('median',np.quantile(vals,.5)),('p05',np.quantile(vals,.05)),('p95',np.quantile(vals,.95)),('worst_observed',vals.min() if m in ['completion','corridor_completion','progress'] else vals.max())]:close(row[field],v)
   if isinstance(raw[k][0][m],bool):
    rate=vals.mean();z=norm.ppf(.975);div=1+z*z/n
    center=(rate+z*z/(2*n))/div;radius=z*np.sqrt(rate*(1-rate)/n+z*z/(4*n*n))/div
    close(row['ci95_low'],max(0,center-radius));close(row['ci95_high'],min(1,center+radius))
   elif m in ['decision_ms_median','decision_ms_max']:
    assert row['ci95_low']==row['ci95_high']==''
   else:
    assert vals.min()-1e-10<=float(row['ci95_low'])<=float(row['ci95_high'])<=vals.max()+1e-10
    close(row['ci95_low'],bootstrap[0]);close(row['ci95_high'],bootstrap[1])
  expected_metrics={(k,m) for k,rr in raw.items() for m in rr[0] if m!='episode_seed'}
  assert metric_keys==expected_metrics
  tests=readcsv(OUT/study/'paired_tests.csv');test_keys=set();pvalues=[]
  for row in tests:
   a=(row['profile'],row['scenario'],row['a'],int(row['actor_seed']),int(row['delay_ms']));b=(a[0],a[1],row['b'],0 if row['b'] in FREE else a[3],a[4]);m=row['metric']
   assert (a,b,m) not in test_keys;test_keys.add((a,b,m))
   assert source_versions[a]==source_versions[b]==row['source_version']
   assert int(row['n'])==n
   delta=np.array([float(x[m])-float(y[m]) for x,y in zip(raw[a],raw[b])]);close(row['mean_difference_a_minus_b'],delta.mean())
   paired_draws=rng.integers(0,n,size=(5000,n));paired_bootstrap=np.percentile(np.take(delta,paired_draws).mean(axis=1),[2.5,97.5])
   close(row['paired_bootstrap95_low'],paired_bootstrap[0]);close(row['paired_bootstrap95_high'],paired_bootstrap[1])
   if m=='rmse':p=float(wilcoxon(delta,zero_method='wilcox',alternative='two-sided',method='auto').pvalue) if np.any(delta) else 1.
   else:
    plus=int(np.count_nonzero(delta>0));minus=int(np.count_nonzero(delta<0))
    assert int(row['discordant_a_true'])==plus and int(row['discordant_b_true'])==minus
    p=binomtest(plus,plus+minus).pvalue if plus+minus else 1.
   close(row['p_raw'],p);pvalues.append(p)
   assert delta.min()-1e-10<=float(row['paired_bootstrap95_low'])<=float(row['paired_bootstrap95_high'])<=delta.max()+1e-10
  ordered=sorted(range(len(tests)),key=lambda j:pvalues[j]);running=0.
  for rank,j in enumerate(ordered):
   running=max(running,min(1.,pvalues[j]*(len(tests)-rank)));close(tests[j]['p_holm'],running)
  expected_contrasts=set()
  for a in raw:
   c=a[2]
   comparators=sorted({k[2] for k in raw if k[2]!='lans'}) if c=='lans' else {'predictor_lqr':['lqr_acc'],'cbf':['ppo_only'],'robust_lans':['robust_no_actor','robust_mpc']}.get(c,[])
   for comparator in comparators:
    b=(a[0],a[1],comparator,0 if comparator in FREE else a[3],a[4])
    if b in raw:
     for m in ['collision','completion','corridor_completion','rmse']:
      if m in raw[a][0] and m in raw[b][0]:expected_contrasts.add((a,b,m))
  assert test_keys==expected_contrasts
  compact=readcsv(OUT/study/'lans_mpc_summary.csv')
  for row in compact:
   chosen=[rr for k,rr in raw.items() if (k[0],k[1],k[2],str(k[4]))==(row['profile'],row['scenario'],row['controller'],row['delay_ms'])]
   assert len(chosen)==int(row['actor_seed_conditions']) and int(row['traffic_cases_per_actor'])==n
   for m in ['collision','completion','corridor_completion','rmse']:
    if m+'_seed_mean' in row:close(row[m+'_seed_mean'],np.mean([np.mean([x[m] for x in rr]) for rr in chosen]))
  summary[study]=dict(conditions=len(raw),records=count,metrics_checked=len(metrics),paired_tests_checked=len(tests),amended_conditions=sum(v!='original_frozen' for v in source_versions.values()))
  total_metrics+=len(metrics);total_tests+=len(tests);stage_seeds[study]=set(range(first,first+n))
 assert not (stage_seeds['extended_baselines']&stage_seeds['stress_study'] or stage_seeds['stress_study']&stage_seeds['observation_delay_study'] or stage_seeds['extended_baselines']&stage_seeds['observation_delay_study'])
 # The main threshold table is recomputed from raw metadata, including all ablations.
 meta=json.loads((R/'working/extended_baselines/confirmation_SUMMARY.json').read_text());thresholds=readcsv(OUT/'empirical_delay_tolerance.csv')
 assert len(thresholds)==len({(x['scenario'],x['controller'],x['policy_seed']) for x in meta})
 for row in thresholds:
  subset=sorted([x for x in meta if (x['scenario'],x['controller'],str(x['policy_seed']))==(row['scenario'],row['controller'],row['actor_seed'])],key=lambda x:x['delay_ms'])
  last=''
  for x in subset:
   if x['collision']>1.00000001 or x['corridor_completion']<89.99999999:break
   last=str(x['delay_ms'])
  assert row['empirical_contiguous_passing_delay_ms']==last
  assert row['upper_grid_censored']==str(last=='1000')
 runtime_raw=json.loads((OUT/'runtime_samples.json').read_text())['samples']
 runtime_table=readcsv(OUT/'runtime_current_host.csv');assert len(runtime_table)==len(runtime_raw)==96
 for row in runtime_table:
  sample=next(x for x in runtime_raw if (x['scenario'],x['controller'],str(x['delay_ms']))==(row['scenario'],row['controller'],row['delay_ms']))
  a=np.asarray(sample['samples_ms']);assert len(a)==50
  for field,v in [('mean_ms',a.mean()),('sample_sd_ms',a.std(ddof=1)),('minimum_ms',a.min()),('median_ms',np.median(a)),('p95_ms',np.quantile(a,.95)),('p99_ms',np.quantile(a,.99)),('max_ms',a.max())]:close(row[field],v)
  assert int(row['exceeded_100ms'])==int((a>100).sum()) and row['mean_ci95_low']==row['mean_ci95_high']==''
 assert sum(x['records'] for x in summary.values())==61200
 result=dict(verified_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='PASS',studies=summary,primary_records=61200,descriptive_metric_rows_checked=total_metrics,paired_tests_and_holm_values_checked=total_tests,traffic_seed_sets_disjoint_across_current_studies=True,actor_repetitions_kept_separate=True,thresholds_independently_recomputed=True,runtime_rows_independently_recomputed=96,compact_seed_summaries_recomputed=True,external_model_review='NOT_RUN',bootstrap_validation='Every reported non-timing percentile mean CI and paired-difference CI independently regenerated from raw data with the recorded RNG seed/order and compared numerically')
 (OP/'FINAL_INDEPENDENT_VALIDATION.json').write_text(json.dumps(result,indent=2));(OUT/'FINAL_INDEPENDENT_VALIDATION.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
if __name__=='__main__':main()
