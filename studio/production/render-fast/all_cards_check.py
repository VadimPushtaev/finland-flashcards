"""Check cached-mask compositing for every card type and the six-frame photo transition."""
from pathlib import Path
import json,sys
import numpy as np,yaml
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'studio/tools'));import render
s=yaml.safe_load((ROOT/'studio/episodes/hb-c08-hux/script.yaml').read_text());r=json.loads((ROOT/'studio/episodes/hb-c08-hux/render.json').read_text());render.configure_style(s);rows={x['sentence_id']:x for x in s['sentences']};images={p:Image.open(ROOT/p).convert('RGB') for p in {x['render_image'] for x in rows.values()}|{s['render']['background_image']}};back=render.prepare_background(images[s['render']['background_image']],s['render']['background_style']);out=[];previous=None
for i,item in enumerate(r['timeline']):
 card,_=render.make_card(s,item,rows,images);variants=[card]
 if previous is not None and item['kind']=='sentence' and r['timeline'][i-1]['kind']=='sentence':
  for transition in range(6):
   overlay=card.copy();overlay.paste(Image.blend(previous.crop((90,180,850,900)),card.crop((90,180,850,900)),(transition+1)/6),(90,180));variants.append(overlay)
 for j,overlay in enumerate(variants):
  t=(item['start_frame']+j)/(r['frames']-1);a=Image.alpha_composite(render.background_frame(back,t,s['render']['background_style']),overlay).convert('RGB');b=back.resize((1920,1080),Image.Resampling.BILINEAR,box=render.background_extent(back.size,t,s['render']['background_style']));b.paste(overlay.convert('RGB'),(0,0),overlay.getchannel('A'));delta=np.abs(np.asarray(a).astype(np.int16)-np.asarray(b).astype(np.int16));out.append(dict(card=i,kind=item['kind'],transition=j,max_error=int(delta.max()),mean_error=float(delta.mean()),different_channels=int(np.count_nonzero(delta))))
 previous=card
report=dict(checks=len(out),all_byte_identical=all(x['max_error']==0 for x in out),results=out);Path('/tmp/hb-render-fast/all-cards-pixel-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='results'}))
