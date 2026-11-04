"""Inspect exact bilingual card layouts before narration timing is available."""
from pathlib import Path
import hashlib,json,os,sys,yaml
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'studio/tools'));import render
SLUGS=['stod','grundskola','yrkesutbildning','finansiering','vuxna']
for slug in (sys.argv[1:] or SLUGS):
 sid='hb-c08-'+slug;ep=ROOT/'studio/episodes'/sid;s=yaml.safe_load((ep/'script.yaml').read_text());render.configure_style(s);rows={r['sentence_id']:r for r in s['sentences']};paths={r['render_image'] for r in rows.values()}|{s['render']['background_image']};images={p:Image.open(ROOT/p).convert('RGB') for p in paths};back=render.prepare_background(images[s['render']['background_image']],s['render']['background_style']);out=ROOT/'studio/media'/sid/'preflight-body';out.mkdir(exist_ok=True);checks=[]
 for i,row in enumerate(s['sentences']):
  if os.environ.get('PREFLIGHT_INDICES') and i not in {int(n) for n in os.environ['PREFLIGHT_INDICES'].split(',')}:continue
  for j,segment in enumerate(row.get('display_segments') or [None]):
   item=dict(kind='sentence',sentence_id=row['sentence_id'])
   if segment:item['segment_index']=j
   card,_=render.make_card(s,item,rows,images);frame=Image.alpha_composite(render.background_frame(back,i/max(1,len(rows)-1),s['render']['background_style']),card).convert('RGB');dest=out/(f'frame-{i:03d}-segment-{j:02d}.png');frame.save(dest);checks.append(dict(sentence_id=row['sentence_id'],segment=j,path=str(dest.relative_to(ROOT)),sha256=hashlib.sha256(dest.read_bytes()).hexdigest()))
 existing=ep/'preflight-layout.json'
 if os.environ.get('PREFLIGHT_INDICES') and existing.exists():
  combined={r['path']:r for r in json.loads(existing.read_text())['frames']};combined.update({r['path']:r for r in checks});checks=sorted(combined.values(),key=lambda r:r['path'])
 (ep/'preflight-layout.json').write_text(json.dumps(dict(source_script_sha256=hashlib.sha256((ep/'script.yaml').read_bytes()).hexdigest(),timing_status='Pre-narration card layout; illustrative pan position only, final display times not yet assigned.',frames=checks),indent=2)+'\n');print(sid,len(checks),'card variants fit',flush=True)
