"""Build labeled visual review sheets for the acquired foreground photographs."""
from pathlib import Path
import json,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];files=[]
for ep in sorted((ROOT/'studio/episodes').glob('hb-c12-*')):
 p=ep/'photograph-plan.json'
 if not p.exists():continue
 for k in json.loads(p.read_text()):
  image=ROOT/'studio/media'/ep.name/'pictures'/(k+'.png')
  if image.exists():files.append((ep.name,k,image))
for part in range(math.ceil(len(files)/12)):
 batch=files[part*12:(part+1)*12];out=Image.new('RGB',(1280,320*math.ceil(len(batch)/4)),'#222222');d=ImageDraw.Draw(out)
 for i,(sid,k,p) in enumerate(batch):
  im=Image.open(p).convert('RGB');im.thumbnail((310,285));x=(i%4)*320;y=(i//4)*320;out.paste(im,(x+(320-im.width)//2,y+30));d.text((x+4,y+3),sid.removeprefix('hb-c12-')+' '+k,font=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',16),fill='white')
 out.save(ROOT/'studio/production/hb-c12a'/f'photo-contact-{part}.png')
print(len(files),'actual source photos in contact sheets')
