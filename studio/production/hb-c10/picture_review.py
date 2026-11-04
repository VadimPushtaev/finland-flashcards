"""Create contact sheets for human visual inspection, without changing sources."""
from pathlib import Path
import json,sys
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];sid=sys.argv[1];ep=ROOT/'studio/episodes'/sid;assets=json.loads((ep/'foreground-assets.json').read_text());cols=6;rows=(len(assets)+cols-1)//cols;im=Image.new('RGB',(cols*260,rows*250),'#101820');draw=ImageDraw.Draw(im)
for i,a in enumerate(assets):
    x=Image.open(ROOT/a['files'][0]['path']).convert('RGB');x.thumbnail((250,225));ox=i%cols*260;oy=i//cols*250;im.paste(x,(ox+(260-x.width)//2,oy));draw.text((ox+10,oy+228),str(i+1),fill='white')
out=ROOT/'studio/media'/sid/'pictures/contact.jpg';im.save(out);print(out)
