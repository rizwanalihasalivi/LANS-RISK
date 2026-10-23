from pathlib import Path
import matplotlib
matplotlib.use('Agg');matplotlib.rcParams['pdf.fonttype']=42
import matplotlib.pyplot as plt
OUT=Path('/workspace/recovery/operations/final_verified_results')
R=Path('/workspace/recovery/restored/LANS-RISK')
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
 tex=['% Requires booktabs and longtable. Rates and confidence intervals in percent; n per condition shown in caption.',r'\begin{longtable}{llcc'+('c' if has_rmse else '')+'}',r'\caption{'+folder.replace('_',' ')+r': paired-case LANS and nominal MPC, per actor seed. Wilson95\% intervals; RMSE reports sample SD. Dense-Merge robustness uses the approved sampler amendment.}'+r'\\',r'\toprule',' & '.join(x.replace('%',r'\%') for x in columns)+r' \\',r'\midrule']
 with PdfPages(OUT/folder/'publication_tables.pdf') as pdf:
  for scenario in ['highway','merge','intersection','roundabout']:
   table=[]
   tex.append(r'\multicolumn{'+str(len(columns))+r'}{l}{\textbf{'+scenario+r'}} \\')
   for profile,s,c,k,d in rowkeys:
    if s!=scenario:continue
    metric=lambda m:lookup[profile,s,c,k,d,m]
    rate=lambda m:f"{100*float(metric(m)['mean']):.1f} [{100*float(metric(m)['ci95_low']):.1f}, {100*float(metric(m)['ci95_high']):.1f}]"
    row=[profile.replace('_',' ')+('*' if folder=='stress_study' and profile=='denser_traffic' and s=='merge' else '')+f' / {d}',('LANS / '+k) if c=='lans' else 'MPC / actor-free',rate('collision'),rate('corridor_completion')]
    if has_rmse:
     rmse=metric('rmse');row.append(f"{float(rmse['mean']):.3f} ({float(rmse['sample_sd']):.3f})")
    table.append(row);tex.append(' & '.join(row)+r' \\')
   fig,ax=plt.subplots(figsize=(13,max(8,.28*(len(table)+1)+2)));ax.axis('off')
   fig.suptitle(folder.replace('_',' ')+' — '+scenario+'; per-seed estimates'+('\n*dense Merge uses the approved sampler amendment' if folder=='stress_study' and scenario=='merge' else ''),fontsize=13,y=.97)
   t=ax.table(cellText=table,colLabels=columns,cellLoc='center',loc='center',bbox=[0,0,1,1],colWidths=([.21,.16,.21,.26,.16] if has_rmse else [.27,.21,.23,.29]))
   t.auto_set_font_size(False);t.set_fontsize(8)
   for (row,col),cell in t.get_celld().items():
    cell.set_linewidth(.25)
    if row==0:cell.set_facecolor('#e7edf3');cell.set_text_props(weight='bold')
    elif row%2==0:cell.set_facecolor('#f4f6f8')
   n=100 if folder=='extended_baselines' else (50 if folder=='stress_study' else 20)
   fig.text(.5,.04,f'n={n} paired traffic cases per condition. Repeated actor seeds share traffic cases; intervals are marginal Wilson95%.\nMPC is run once per condition. RMSE SD describes episode variability; paired tests are in paired_tests.csv.',ha='center',fontsize=9)
   fig.subplots_adjust(left=.03,right=.97,bottom=.13,top=.88);pdf.savefig(fig);fig.savefig(OUT/folder/('publication_table_'+scenario+'.png'),dpi=300);plt.close(fig)
 tex.extend([r'\bottomrule',r'\end{longtable}'])
 (OUT/folder/'publication_tables.tex').write_text('\n'.join(tex)+'\n')
with (OUT/'FIGURE_CAPTIONS.md').open('a') as f:f.write('\n- `publication_tables.pdf`/`.tex` in each study: per-scenario LANS actors42/43/44 and actor-free nominal MPC tables. Each row retains its own paired traffic sample, n=100/50/20 for main/robustness/observation studies. Binary rates use marginal Wilson95% intervals. RMSE is mean (sample SD) when present; no RMSE is invented for observation delay. LaTeX requires booktabs/longtable. Tables preserve failures and do not pool actor repetitions. An asterisk on denser traffic in the Merge robustness table identifies the approved sampler amendment; other conditions retain the original sampler.\n')
print('COMPLETE publication tables',flush=True)
