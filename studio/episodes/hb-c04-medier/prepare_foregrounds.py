"""Restore contained foreground pictures from pinned, unchanged source files."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageOps,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
EPISODE=Path(__file__).resolve().parent
catalog=json.loads((EPISODE/'foregrounds.json').read_text())
for key,record in catalog['metadata'].items():
 raw=ROOT/record['raw_path']
 if hashlib.sha256(raw.read_bytes()).hexdigest()!=record['sha256']:
  raise ValueError('Restore pinned foreground source: '+str(raw))
 canvas=Image.new('RGB',(760,720),'#382d24')
 photo=ImageOps.contain(Image.open(raw).convert('RGB'),(720,610),Image.Resampling.LANCZOS)
 canvas.paste(photo,((760-photo.width)//2,30+(610-photo.height)//2))
 ImageDraw.Draw(canvas).text((380,674),record['caption'],font=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',28),anchor='mm',fill='#dfcfbb')
 output=ROOT/record['render_path'];output.parent.mkdir(parents=True,exist_ok=True);canvas.save(output)
 expected=next(f['sha256'] for a in catalog['assets'] for f in a['files'] if f['path']==record['render_path'])
 if hashlib.sha256(output.read_bytes()).hexdigest()!=expected:
  raise ValueError('Foreground render differs from reviewed version; review and refresh its asset record deliberately: '+str(output))
 print(key,'contained foreground restored')
