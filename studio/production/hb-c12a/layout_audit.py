"""Audit all exact bilingual sentence panels without claiming auditory review."""
from pathlib import Path
import json,sys,yaml
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'studio/tools'));import render
SLUGS=['integration','tjanster','sprak','tolkning','myndigheter','egna-arenden','personuppgifter','hemkommun','e-tjanster','norden-eu'];bad=[];checks=0
for slug in SLUGS:
 ep=ROOT/'studio/episodes'/('hb-c12-'+slug);s=yaml.safe_load((ep/'script.yaml').read_text());render.configure_style(s)
 for i,row in enumerate(s['sentences']):
  heights=[]
  for ss,rs in [(48,40),(44,36),(40,34)]:
   height=len(render.wrap(row['sv'],render.font(ss,True),900))*round(ss*1.3125)+len(render.wrap(row['ru'],render.font(rs),900))*round(rs*1.375)+56;heights.append(height)
  checks+=1
  if heights[0]>750:bad.append(dict(section_id=ep.name,index=i,sentence_id=row['sentence_id'],heights=heights,sv=row['sv'],ru=row['ru']))
print(json.dumps(dict(checked=checks,oversize=bad),ensure_ascii=False,indent=2));(ROOT/'studio/production/hb-c12a/layout-audit.json').write_text(json.dumps(dict(checked=checks,oversize=bad),ensure_ascii=False,indent=2)+'\n')
