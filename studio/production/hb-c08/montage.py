"""Build small labeled contact sheets of actual preflight/export stills."""
from pathlib import Path
import sys
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];sid=sys.argv[1];idx=[int(x) for x in sys.argv[2:]];folder=ROOT/'studio/media'/sid/'render';out=Image.new('RGB',(1280,360*((len(idx)+1)//2)),'#111111');d=ImageDraw.Draw(out)
for i,n in enumerate(idx):
 p=folder/f'frame-{n:02d}.png';im=Image.open(p).convert('RGB');im.thumbnail((640,340));x=(i%2)*640;y=(i//2)*360;out.paste(im,(x,y+20));d.text((x+8,y+2),p.name,font=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',16),fill='white')
p=ROOT/'studio/production/hb-c08'/(sid+'-preflight.png');out.save(p);print(p)
