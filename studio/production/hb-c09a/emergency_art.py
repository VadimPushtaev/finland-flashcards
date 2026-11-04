"""Moss emergency object diagrams with source-bound labels and no invented incidents."""
import json,math,sys
from pathlib import Path
import yaml
from PIL import Image,ImageDraw,ImageFont
import family_art as base
R=Path(__file__).resolve().parents[3]
base.BG='#243c32';base.PANEL='#2e493b';base.MUTED='#c5dfce';base.GOLD='#e3c58c';base.LINE='#60816c';base.INK='#172a23'
original_art=base.art

def art(d,kind,x,y,s=1):
 def line(ps,fill=base.GOLD,w=7):d.line([(x+a*s,y+b*s) for a,b in ps],fill=fill,width=max(1,int(w*s)))
 def box(a,b,fill=base.TEAL,r=10):d.rounded_rectangle((x+a[0]*s,y+a[1]*s,x+b[0]*s,y+b[1]*s),radius=r*s,fill=fill)
 def label(t,yy,size=45):d.text((x,y+yy*s),t,font=ImageFont.truetype(base.BOLD,int(size*s)),fill=base.TEXT,anchor='mm')
 if kind in ('no_coins','no_alert'):
  original_art(d,'coins' if kind=='no_coins' else 'alert',x,y,s);line([(-96,104),(96,-104)],base.LINE,11)
 elif kind=='service_languages':
  for xx,yy,word in [(-25,-69,'finska'),(25,0,'svenska'),(-15,69,'engelska')]:
   box((xx-96,yy-28),(xx+96,yy+28),base.LINE if yy else base.TEAL);d.text((x+xx*s,y+yy*s),word,font=ImageFont.truetype(base.BOLD,int(29*s)),fill=base.TEXT,anchor='mm')
 elif kind in ('digits112','dial_prefix','no_prefix'):
  box((-100,-68),(100,68),base.LINE);label('112' if kind=='digits112' else '+…',0,76)
  if kind=='no_prefix':line([(-94,79),(94,-79)],base.GOLD,11)
 elif kind in ('headset','question'):
  if kind=='question':label('?',0,140)
  else:
   original_art(d,'person',x,y,.72*s);d.arc((x-65*s,y-113*s,x+65*s,y-6*s),180,360,fill=base.GOLD,width=max(1,int(9*s)));box((-70,-68),(-44,-17));box((44,-68),(70,-17));line([(64,-20),(64,10),(20,10)]);box((5,0),(29,19),base.GOLD)
 elif kind in ('address','apartment'):
  if kind=='address':
   original_art(d,'house',x,y,.85*s);box((-94,42),(94,98),base.LINE);label('…',69,45)
  else:
   box((-78,-108),(78,108),base.MUTED)
   for xx in [-48,0,48]:
    for yy in [-75,-22,31]:box((xx-14,yy-15),(xx+14,yy+15),base.TEAL,r=2)
   box((-16,77),(16,108),base.LINE,r=2)
 elif kind=='check':
  d.ellipse((x-83*s,y-83*s,x+83*s,y+83*s),fill=base.TEAL);line([(-43,1),(-9,32),(49,-35)],base.TEXT,14)
 elif kind in ('end_call','no_phone'):
  original_art(d,'phone',x,y,s);line([(-91,98),(91,-98)],base.GOLD,10)
 elif kind=='trace':
  original_art(d,'phone',x-25*s,y,.68*s)
  for rr in [43,65,87]:d.arc((x-rr*s,y-rr*s,x+rr*s,y+rr*s),285,75,fill=base.GOLD,width=max(1,int(5*s)))
 elif kind=='languages':
  box((-106,-78),(47,33),base.LINE);box((-40,-16),(108,92),base.TEAL);label('A',-27,58);d.text((x+37*s,y+46*s),'Я',font=ImageFont.truetype(base.BOLD,int(58*s)),fill=base.TEXT,anchor='mm')
 elif kind=='support_vehicle':
  box((-108,-37),(56,64));d.polygon([(x+56*s,y-37*s),(x+95*s,y-6*s),(x+108*s,y+64*s),(x+56*s,y+64*s)],fill=base.MUTED);box((67,-10),(88,12),base.INK,r=2)
  for xx in [-63,66]:d.ellipse((x+(xx-25)*s,y+43*s,x+(xx+25)*s,y+93*s),fill=base.INK,outline=base.GOLD,width=max(1,int(4*s)))
 elif kind=='plug':
  box((-56,-58),(56,38));line([(-30,-58),(-30,-108)]);line([(30,-58),(30,-108)]);line([(0,38),(0,73),(52,73),(52,111)])
 elif kind=='fire':
  pts=[(-78,78),(-88,25),(-52,-24),(-40,19),(-9,-112),(36,-55),(60,-74),(91,15),(64,78)];d.polygon([(x+a*s,y+b*s) for a,b in pts],fill=base.GOLD);d.polygon([(x-34*s,y+73*s),(x-35*s,y+24*s),(x+1*s,y-24*s),(x+34*s,y+30*s),(x+28*s,y+73*s)],fill=base.LINE)
 elif kind=='tap':
  line([(-95,-36),(55,-36),(55,8)],base.MUTED,28);line([(-26,-39),(-26,-75)],base.GOLD,13);line([(-60,-75),(10,-75)],base.GOLD,13);d.polygon([(x+56*s,y+33*s),(x+31*s,y+76*s),(x+56*s,y+97*s),(x+81*s,y+76*s)],fill=base.TEAL)
 elif kind=='flood':
  original_art(d,'house',x,y-22*s,.68*s)
  for yy in [23,53,83]:line([(-108,yy),(-75,yy-10),(-40,yy+5),(0,yy-9),(40,yy+5),(75,yy-10),(108,yy)],base.TEAL,9)
 elif kind=='switch':
  line([(-105,0),(13,0),(71,-60)]);line([(13,0),(71,60)]);line([(-80,90),(85,-90)],base.LINE,10)
 elif kind=='eu':
  box((-112,-79),(112,79),'#284e80')
  for j in range(12):
   a=2*math.pi*j/12;cx=x+49*s*math.sin(a);cy=y-49*s*math.cos(a);d.ellipse((cx-5*s,cy-5*s,cx+5*s,cy+5*s),fill=base.GOLD)
 else:original_art(d,kind,x,y,s)
base.art=art

def diagram(spec,path,source):
 n=len(spec['objects'])
 if n<=3:return base.diagram(spec,path,source)
 im=Image.new('RGB',(760,720),base.BG);d=ImageDraw.Draw(im);d.rounded_rectangle((15,15,745,705),radius=30,fill=base.PANEL,outline=base.LINE,width=2)
 if spec.get('title'):base.text(d,spec['title'],(380,40),660,31)
 coords=[(210,240),(550,240),(210,477),(550,477)] if n==4 else [(145,230),(380,230),(615,230),(145,480),(380,480),(615,480)]
 for (kind,label),(x,y) in zip(spec['objects'],coords):
  art(d,kind,x,y,.59);base.text(d,label,(x,y+77),205 if n==6 else 285,23)
 d.text((380,674),'Schematisk illustration',font=ImageFont.truetype(base.FONT,22),fill=base.MUTED,anchor='mt');im.save(path)

def prepare():
 sid='hb-c11-nodsituationer';ep=R/'studio/episodes'/sid;s=yaml.safe_load((ep/'script.yaml').read_text());p=json.loads((ep/'visual-plan.json').read_text());assets=[]
 for i,(r,q) in enumerate(zip(s['sentences'],p),1):
  dest=R/r['render_image'];dest.parent.mkdir(parents=True,exist_ok=True);diagram(q,dest,r['sv']);r['visual_cue']=q['reason']+' Fixed bilingual panel; anonymous schematic illustration.'
  assets.append(dict(asset_id=f'picture_{i:03}',kind='foreground',visual_type='diagram',files=[base.info(dest)],creator='Homebrew video studio',reuse_terms='Original schematic artwork under repository MIT license; quoted source wording retains publisher terms.',required_credits='Original source-based emergency diagrams: Homebrew video studio. Exact source text and publisher notices in sources.yaml.',relevance_verification=q['reason'],creation_method={'tool':'studio/production/hb-c09a/emergency_art.py','specification':str((ep/'visual-plan.json').relative_to(R)),'source_sentence_ids':[r['sentence_id'],*q.get('source_context_ids',[])]}))
 (ep/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');(ep/'script.yaml').write_text(yaml.safe_dump(s,allow_unicode=True,sort_keys=False,width=100));print('49 emergency diagrams prepared',flush=True)
if __name__=='__main__':prepare()
