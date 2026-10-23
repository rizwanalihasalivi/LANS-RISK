"""Render the verified Markdown report as a portable, printable HTML document."""
from pathlib import Path
import html,re,json
OUT=Path('/workspace/recovery/operations/final_verified_results')
assert json.loads((OUT/'FINAL_INDEPENDENT_VALIDATION.json').read_text())['status']=='PASS'
def inline(s):
 s=html.escape(s)
 s=re.sub(r'`([^`]+)`',r'<code>\1</code>',s)
 s=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',s)
 return s
lines=(OUT/'SCIENTIFIC_REPORT.md').read_text().splitlines();chunks=[];paragraph=[];i=0
def flush():
 if paragraph:chunks.append('<p>'+inline(' '.join(paragraph))+'</p>');paragraph.clear()
while i<len(lines):
 line=lines[i]
 if not line.strip():flush();i+=1;continue
 if line.startswith('#'):
  flush();level=len(line)-len(line.lstrip('#'));chunks.append(f'<h{level}>'+inline(line[level:].strip())+f'</h{level}>');i+=1;continue
 if line.startswith('|'):
  flush();rows=[]
  while i<len(lines) and lines[i].startswith('|'):
   cells=[v.strip() for v in lines[i].strip('|').split('|')]
   if not all(re.fullmatch(r'[-: ]+',v) for v in cells):rows.append(cells)
   i+=1
  chunks.append('<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+inline(v)+'</th>' for v in rows[0])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+inline(v)+'</td>' for v in row)+'</tr>' for row in rows[1:])+'</tbody></table></div>');continue
 paragraph.append(line);i+=1
flush()
figures='''<h2>Selected figures and publication tables</h2>
<p>Full captions are in <a href="FIGURE_CAPTIONS.md">FIGURE_CAPTIONS.md</a>. Lines and shaded ranges summarize actor seeds; shading is not a confidence interval.</p>'''
for name,title in [('extended_baselines/fixed_fifo','Main confirmation'),('stress_study/denser_traffic','Denser traffic — dense Merge uses the approved amendment'),('stress_study/weaker_actuation','Weaker actuation'),('observation_profiles','Observation delay'),('runtime','Runtime diagnostics')]:
 figures+=f'<figure><a href="{name}.pdf"><img src="{name}.png" alt="{html.escape(title)}"></a><figcaption>{html.escape(title)} · click for vector PDF</figcaption></figure>'
figures+='<p>Per-seed tables: '+ ' · '.join(f'<a href="{folder}/publication_tables.pdf">{label}</a>' for folder,label in [('extended_baselines','Main'),('stress_study','Robustness'),('observation_delay_study','Observation')])+'</p>'
doc='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>LANS-RISK — verified final report</title><style>
body{font:16px/1.65 system-ui,sans-serif;color:#172637;background:#f4f6f8;margin:0}main{max-width:1050px;margin:32px auto;padding:36px 48px;background:white;border:1px solid #dde4eb}h1{font-size:30px;line-height:1.25}h2{font-size:22px;margin-top:36px;border-top:1px solid #dfe5eb;padding-top:20px}p{margin:16px 0}code{font-size:13px;overflow-wrap:anywhere}table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;padding:9px;border-bottom:1px solid #dbe2e9}th{background:#eaf0f6}tr:nth-child(even){background:#f7f9fb}.table-wrap{overflow:auto}a{color:#1557a0}figure{margin:28px 0}img{width:100%;height:auto}figcaption{font-size:14px;color:#435569}@media print{body{background:white;font-size:11pt}main{margin:0;padding:0;border:0}h2{break-after:avoid}figure,table{break-inside:avoid}a{color:inherit}}@media(max-width:600px){main{padding:20px;margin:0}h1{font-size:25px}}
</style><main>'''+''.join(chunks)+figures+'</main></html>'
(OUT/'SCIENTIFIC_REPORT.html').write_text(doc)
print('Created portable printable scientific report with local figure/table links')
