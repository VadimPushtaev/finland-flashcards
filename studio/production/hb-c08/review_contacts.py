"""Build read-only review contacts in the owner's production directory."""
from pathlib import Path
import json,sys
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];sid=sys.argv[1];mode=sys.argv[2];start=int(sys.argv[3]);count=int(sys.argv[4]);font=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',18)
if mode=='export':paths=sorted((ROOT/'studio/media'/sid/'render').glob('export-frame-*.png'),key=lambda path:int(path.stem.rsplit('-',1)[-1]))
else:paths=[ROOT/a['files'][0]['path'] for a in json.loads((ROOT/'studio/episodes'/sid/'foreground-assets.json').read_text())]
paths=paths[start:start+count];w,h=(480,292) if mode=='export' else (400,425);cols=3;out=Image.new('RGB',(cols*w,((len(paths)+cols-1)//cols)*h),'#171717');d=ImageDraw.Draw(out)
for k,p in enumerate(paths):
 im=Image.open(p).convert('RGB');im.thumbnail((w,h-25));x=(k%cols)*w;y=(k//cols)*h;out.paste(im,(x,y+25));d.text((x+5,y+2),p.name,font=font,fill='white')
p=ROOT/'studio/production/hb-c08'/f'{sid}-{mode}-review-{start}.jpg';out.save(p,quality=94);print(p)
