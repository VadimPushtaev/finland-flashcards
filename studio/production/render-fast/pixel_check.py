"""Check unchanged background sampler with cached RGB/mask compositing."""
from pathlib import Path
import json,sys,time
import numpy as np,yaml
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'studio/tools'));import render
s=yaml.safe_load((ROOT/'studio/episodes/hb-c08-hux/script.yaml').read_text());r=json.loads((ROOT/'studio/episodes/hb-c08-hux/render.json').read_text());render.configure_style(s);rows={x['sentence_id']:x for x in s['sentences']};images={p:Image.open(ROOT/p).convert('RGB') for p in [s['render']['background_image'],s['sentences'][0]['render_image']]};back=render.prepare_background(images[s['render']['background_image']],s['render']['background_style']);card,_=render.make_card(s,r['timeline'][1],rows,images);rgb=card.convert('RGB');mask=card.getchannel('A');out=[]
for frame in [0,1,119,650,1000,1300,1633,2000,2400,2900,3266]:
 t=frame/(r['frames']-1);a=Image.alpha_composite(render.background_frame(back,t,s['render']['background_style']),card).convert('RGB');b=back.resize((1920,1080),Image.Resampling.BILINEAR,box=render.background_extent(back.size,t,s['render']['background_style']));b.paste(rgb,(0,0),mask);delta=np.abs(np.asarray(a).astype(np.int16)-np.asarray(b).astype(np.int16));out.append(dict(frame=frame,max_error=int(delta.max()),mean_error=float(delta.mean()),different_channels=int(np.count_nonzero(delta))))
print(json.dumps(out,indent=2));Path('/tmp/hb-render-fast/paste-pixel-check.json').write_text(json.dumps(out,indent=2)+'\n')
