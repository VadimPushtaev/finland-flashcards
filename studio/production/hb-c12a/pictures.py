"""Draw original integration and public-service illustrations from exact source-based composition plans."""
from pathlib import Path
import hashlib,json,math,os,sys,yaml
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];F='/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf';B=F.replace('Regular','Bold');BG='#352e49';PANEL='#463d5c';FG='#faf3e8';SOFT='#d7cce7';GOLD='#e2c58b';LINE='#685881'
def icon(d,kind,cx,cy,s=1):
 def p(x,y):return(cx+x*s,cy+y*s)
 def line(pts,w=5,fill=GOLD):d.line([p(*q) for q in pts],width=max(2,int(w*s)),fill=fill,joint='curve')
 def ellipse(x,y,rx,ry=None,fill=None):
  if ry is None:ry=rx
  d.ellipse((*p(x-rx,y-ry),*p(x+rx,y+ry)),outline=GOLD,width=max(2,int(4*s)),fill=fill)
 def box(x,y,w,h,fill=PANEL):d.rounded_rectangle((*p(x,y),*p(x+w,y+h)),radius=8*s,outline=GOLD,width=max(2,int(4*s)),fill=fill)
 def person(x,y,small=False):
  t=.72 if small else 1;ellipse(x,y-38*t,17*t);line([(x,y-20*t),(x,y+35*t)],4);line([(x-29*t,y+2*t),(x,y-10*t),(x+29*t,y+2*t)],4);line([(x-20*t,y+67*t),(x,y+35*t),(x+20*t,y+67*t)],4)
 if kind in('adult','teacher','child','children','family'):
  if kind=='family':person(-46,0);person(46,0);person(0,35,True)
  elif kind=='children':person(-37,8,True);person(37,8,True)
  else:person(0,0,kind=='child')
  if kind=='teacher':box(40,-67,34,45);line([(47,-51),(65,-51)],2,SOFT);line([(47,-40),(65,-40)],2,SOFT)
 elif kind in('school','town'):
  line([(-82,-36),(0,-94),(82,-36),(-82,-36)]);box(-68,-36,136,113);box(-15,28,30,49)
  for x in(-44,25):
   for y in(-17,15):box(x,y,20,20)
  if kind=='town':line([(-90,86),(90,86)],7,SOFT)
 elif kind in('book','diploma','pencils'):
  if kind=='book':
   line([(0,-48),(-70,-66),(-70,60),(0,78),(70,60),(70,-66),(0,-48),(0,78)])
   for y in(-35,-8,19,46):line([(-55,y-12),(-14,y)],3,SOFT);line([(14,y),(55,y-12)],3,SOFT)
  elif kind=='diploma':
   box(-72,-60,144,100);ellipse(34,37,20);line([(23,52),(16,86),(35,75),(48,87),(45,54)],4);line([(-51,-30),(47,-30)],3,SOFT);line([(-51,-10),(8,-10)],3,SOFT)
  else:
   for j in(-1,0,1):
    x=j*42;line([(x-12,53),(x-12,-48),(x,-72),(x+12,-48),(x+12,53),(x-12,53)]);line([(x-12,-48),(x+12,-48)],3,SOFT)
 elif kind in('calendar','clock','sun'):
  if kind=='calendar':
   box(-72,-63,144,135);line([(-72,-27),(72,-27)]);line([(-37,-80),(-37,-43)]);line([(37,-80),(37,-43)])
   for x in(-42,0,42):
    for y in(0,29,58):ellipse(x,y,4,fill=SOFT)
  elif kind=='clock':
   ellipse(0,0,78)
   for i in range(12):
    a=i*math.pi/6;line([(math.sin(a)*65,-math.cos(a)*65),(math.sin(a)*71,-math.cos(a)*71)],2,SOFT)
   line([(0,-47),(0,0),(42,24)],6)
  else:
   ellipse(0,0,46)
   for i in range(12):
    a=i*math.pi/6;line([(math.sin(a)*61,math.cos(a)*61),(math.sin(a)*81,math.cos(a)*81)],4)
 elif kind=='freecoins':
  icon(d,'coins',cx,cy,s)
  ellipse(0,0,86);line([(-61,61),(61,-61)],8,FG)
 elif kind=='coins':
  for x,h in((-43,2),(3,3),(49,4)):
   for i in range(h):ellipse(x,60-i*23,25,10)
 elif kind=='meal':
  ellipse(0,5,58);ellipse(0,5,42);line([(-88,-60),(-88,80)]);line([(-104,-60),(-104,-25),(-72,-25),(-72,-60)]);line([(90,-60),(90,80)]);line([(90,-60),(72,-27),(90,-15)])
 elif kind=='speech':
  box(-80,-58,160,102);line([(-38,44),(-50,78),(-10,44)])
  for x in(-37,0,37):ellipse(x,-6,6,fill=SOFT)
 elif kind=='target':
  for r in(75,50,25):ellipse(0,0,r)
  line([(-8,8),(74,-74)]);line([(50,-74),(74,-74),(74,-50)])
 elif kind=='plant':
  line([(0,80),(0,-57)],6);line([(0,-25),(-57,-61)],5);line([(0,15),(56,-23)],5)
  d.ellipse((*p(-70,-72),*p(-27,-30)),outline=GOLD,width=4);d.ellipse((*p(25,-45),*p(72,-5)),outline=GOLD,width=4);line([(-75,87),(75,87)],5,SOFT)
 elif kind=='play':
  # A stacking pyramid and a ball make a complete play-object still life.
  for y,w in((58,116),(23,88),(-12,58)):box(-w/2,y,w,29)
  ellipse(65,-36,27);line([(43,-54),(87,-18)],3,SOFT)
 elif kind=='puzzle':
  box(-66,-62,132,124);line([(-66,0),(-15,0)]);line([(15,0),(66,0)]);ellipse(0,0,17);line([(0,-62),(0,-18)]);line([(0,18),(0,62)])
 elif kind=='magnify':
  ellipse(-12,-14,50);line([(23,23),(75,78)],11);line([(-39,-14),(15,-14)],3,SOFT);line([(-12,-42),(-12,14)],3,SOFT)
 elif kind=='hands':
  line([(-80,42),(-48,5),(-27,-1),(0,23),(27,-1),(48,5),(80,42)]);line([(-80,42),(-44,81),(0,53),(44,81),(80,42)]);line([(-27,-1),(-16,-17),(0,-6),(16,-17),(27,-1)])

 elif kind=='moon':
  ellipse(0,0,73,fill=GOLD);d.ellipse((*p(-8,-87),*p(87,45)),fill=BG)
  for x,y in((-58,-66),(63,65),(-53,61)):line([(x-7,y),(x+7,y)],3,SOFT);line([(x,y-7),(x,y+7)],3,SOFT)
 elif kind=='church':
  line([(-67,72),(-67,-18),(0,-65),(67,-18),(67,72),(-67,72)]);box(-14,26,28,46);line([(0,-65),(0,-102)]);line([(-17,-86),(17,-86)])
  for x in(-42,30):box(x,-3,15,28)
 elif kind=='house':
  line([(-82,-8),(0,-84),(82,-8)]);box(-66,-8,132,88);box(-14,29,28,51);box(-48,9,23,23)
 elif kind=='bulb':
  ellipse(0,-19,49);box(-23,30,46,28);line([(-18,72),(18,72)])
  for a in(-2.7,-2.0,-1.2,-.5):line([(math.cos(a)*68,math.sin(a)*68-20),(math.cos(a)*91,math.sin(a)*91-20)],3,SOFT)
 elif kind=='document':
  box(-60,-82,120,164)
  for y in(-44,-13,18,49):line([(-38,y),(38,y)],3,SOFT)
 elif kind=='work':
  box(-75,-40,150,115);box(-29,-69,58,29);line([(-75,-3),(75,-3)],3,SOFT);box(-12,-14,24,25)
 elif kind=='balance':
  line([(0,-88),(0,76)]);line([(-50,78),(50,78)],6);line([(-78,-53),(78,-53)])
  for x in(-66,66):
   line([(x,-53),(x-25,10),(x+25,10),(x,-53)]);d.arc((*p(x-25,-8),*p(x+25,26)),0,180,fill=GOLD,width=4)
 elif kind=='globe':
  ellipse(0,0,81);d.ellipse((*p(-39,-81),*p(39,81)),outline=GOLD,width=3);line([(-81,0),(81,0)],3,SOFT);d.arc((*p(-75,-49),*p(75,16)),180,360,fill=SOFT,width=3);d.arc((*p(-75,-15),*p(75,50)),0,180,fill=SOFT,width=3)
 elif kind=='laptop':
  box(-73,-62,146,110);line([(-94,75),(94,75),(73,48),(-73,48),(-94,75)]);line([(-29,63),(29,63)],3,SOFT)
 elif kind=='tree':
  line([(0,6),(0,83)],8);d.polygon([p(-72,24),p(0,-94),p(72,24)],fill=LINE,outline=GOLD);d.polygon([p(-50,-21),p(0,-105),p(50,-21)],fill=SOFT)
 elif kind=='flask':
  line([(-22,-80),(22,-80),(22,-23),(72,65),(72,78),(-72,78),(-72,65),(-22,-23),(-22,-80)]);line([(-46,30),(46,30)],4,SOFT)

 elif kind=='shield':
  line([(-58,-70),(0,-90),(58,-70),(50,20),(0,82),(-50,20),(-58,-70)]);line([(-29,-3),(-7,24),(32,-28)],6,SOFT)
 elif kind in('court','bank'):
  line([(-78,-32),(0,-88),(78,-32),(-78,-32)]);line([(-81,80),(81,80)],7)
  for x in(-52,-18,18,52):line([(x,-20),(x,61)],8)
  line([(-69,64),(69,64)],5)
 elif kind=='hospital':
  box(-68,-75,136,154);line([(-24,-33),(24,-33)],10);line([(0,-57),(0,-9)],10)
  for x in(-42,0,42):box(x-9,25,18,25)
 elif kind=='phone':
  box(-48,-88,96,176);line([(-17,-65),(17,-65)],3,SOFT);ellipse(0,65,8)
 elif kind=='sport':
  ellipse(0,0,75);line([(-75,0),(75,0)],3);line([(0,-75),(0,75)],3);d.arc((*p(-39,-75),*p(39,75)),75,285,fill=SOFT,width=3)
 elif kind=='shirt':
  line([(-31,-73),(-76,-47),(-95,3),(-59,21),(-50,-1),(-50,81),(50,81),(50,-1),(59,21),(95,3),(76,-47),(31,-73)]);d.arc((*p(-31,-93),*p(31,-35)),0,180,fill=GOLD,width=4)
 elif kind=='music':
  line([(-30,-67),(-30,47)],7);line([(-30,-67),(59,-88),(59,26)],7);line([(-30,-42),(59,-63)],7);ellipse(-47,53,25,18,fill=SOFT);ellipse(42,33,25,18,fill=SOFT)
 elif kind=='bus':
  box(-79,-64,158,113);box(-62,-47,124,53);ellipse(-49,57,19);ellipse(49,57,19);line([(-60,27),(-33,27)],5,SOFT);line([(33,27),(60,27)],5,SOFT)
 elif kind=='gear':
  ellipse(0,0,51);ellipse(0,0,21)
  for i in range(8):
   a=i*math.pi/4;line([(math.cos(a)*51,math.sin(a)*51),(math.cos(a)*79,math.sin(a)*79)],12)
 elif kind=='scissors':
  ellipse(-39,46,23);ellipse(39,46,23);line([(-23,28),(56,-83)],7);line([(23,28),(-56,-83)],7)

 elif kind=='bike':
  ellipse(-53,36,38);ellipse(53,36,38);line([(-53,36),(-15,-26),(19,36),(-53,36)]);line([(-15,-26),(37,-26),(19,36)]);line([(37,-26),(53,36)]);line([(27,-48),(42,-48),(37,-26)]);line([(-28,-36),(-5,-36)])
 elif kind=='car':
  box(-82,-16,164,64);line([(-64,-16),(-36,-62),(36,-62),(64,-16)]);ellipse(-49,52,20);ellipse(49,52,20)
 elif kind=='headphones':
  d.arc((*p(-77,-91),*p(77,63)),180,360,fill=GOLD,width=8);box(-84,-20,33,88);box(51,-20,33,88)

 elif kind=='lock':
  box(-64,-5,128,91);d.arc((*p(-46,-92),*p(46,17)),180,360,fill=GOLD,width=7);ellipse(0,29,12);line([(0,39),(0,61)],7,SOFT)
 elif kind=='card':
  box(-92,-62,184,124);ellipse(-48,-15,18);d.arc((*p(-80,4),*p(-17,51)),180,360,fill=GOLD,width=4)
  for y in(-27,-3,21):line([(0,y),(69,y)],4,SOFT)
 elif kind=='passport':
  box(-63,-86,126,172);ellipse(0,-6,37);line([(-37,-6),(37,-6)],3);d.ellipse((*p(-17,-43),*p(17,31)),outline=GOLD,width=3);line([(-36,58),(36,58)],4,SOFT)
 elif kind=='envelope':
  box(-91,-56,182,112);line([(-91,-56),(0,18),(91,-56)]);line([(-91,56),(-25,1)],3,SOFT);line([(91,56),(25,1)],3,SOFT)
 elif kind=='pair':
  person(-43,8,False);person(43,8,False)
 elif kind=='people':
  for x,y in((-55,15),(0,-10),(55,15)):person(x,y,False)

 elif kind=='warning':
  line([(-82,73),(0,-80),(82,73),(-82,73)],6);line([(0,-39),(0,21)],8);ellipse(0,48,6,fill=GOLD)
 elif kind=='sealed':
  d.arc((*p(-44,-94),*p(44,-6)),180,360,fill=GOLD,width=6);line([(-44,-50),(-44,-10)],6);line([(44,-50),(44,-10)],6);box(-64,-10,128,100);ellipse(0,31,10);line([(0,41),(0,61)],5)
 elif kind=='business':
  box(-69,-73,138,155)
  for x in(-46,-7,32):
   for y in(-46,-8,30):box(x,y,23,22)
  box(-15,56,30,26)
 elif kind=='database':
  d.ellipse((*p(-74,-81),*p(74,-34)),fill=PANEL,outline=GOLD,width=4);line([(-74,-57),(-74,61)],4);line([(74,-57),(74,61)],4)
  for y in(-20,20,59):d.arc((*p(-74,y-21),*p(74,y+22)),0,180,fill=GOLD,width=4)
 else:raise ValueError(kind)
def wrap(d,text,x,y,width,size=31):
 while size>22 and any(d.textlength(w,font=ImageFont.truetype(B,size))>width for w in text.split()):size-=1
 f=ImageFont.truetype(B,size);lines=[];buf=''
 for word in text.split():
  z=(buf+' '+word).strip()
  if d.textlength(z,font=f)>width and buf:lines.append(buf);buf=word
  else:buf=z
 if buf:lines.append(buf)
 for j,l in enumerate(lines):d.text((x,y+j*(size+8)),l,font=f,fill=FG,anchor='mt')
def info(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def main(sid):
 ep=ROOT/'studio/episodes'/sid;out=ROOT/'studio/media'/sid/'pictures';out.mkdir(parents=True,exist_ok=True);specs=json.loads((ep/'picture-plan.json').read_text());existing=json.loads((ep/'foreground-assets.json').read_text()) if (ep/'foreground-assets.json').exists() else [];selected=set(os.environ.get('PICTURE_KEYS','').split(','))-{''};assets=[a for a in existing if a.get('visual_type')=='photograph' or str(a.get('creation_method',{}).get('tool','')).endswith('/flags.py') or (selected and a['asset_id'] not in selected)];photo_keys={a['asset_id'] for a in assets}
 for idx,(key,spec) in enumerate(specs.items()):
  if selected and key not in selected:continue
  if key in photo_keys:continue
  im=Image.new('RGB',(760,720),BG);d=ImageDraw.Draw(im);composition=spec['composition'];nodes=spec['nodes']
  # Designs are chosen for the source relation: timelines, classroom encounters,
  # day schedules, comparisons, and still lives have different geometry.
  if composition=='blocked_transfer':
   xy=[(220,300),(540,300)];labels=[(220,440),(540,440)];d.line((315,300,445,300),fill=GOLD,width=5);d.polygon([(445,300),(430,290),(430,310)],fill=GOLD);d.ellipse((342,262,418,338),outline=FG,width=5);d.line((352,328,408,272),fill=FG,width=7)
  elif composition=='needs_branch':
   xy=[(200,350),(550,205),(550,480)];labels=[(200,475),(550,315),(550,585)]
   d.line((295,350,380,350),fill=LINE,width=5);d.line((380,205,380,480),fill=LINE,width=5)
   for y in(205,480):d.line((380,y,448,y),fill=GOLD,width=5);d.polygon([(448,y),(434,y-9),(434,y+9)],fill=GOLD)
  elif composition=='cumulative':
   xy=[(200,205),(200,490),(565,350)];labels=[(200,315),(200,575),(565,490)]
   d.line((295,205,360,205,360,490,295,490),fill=LINE,width=5);d.line((360,350,465,350),fill=GOLD,width=5);d.polygon([(465,350),(450,341),(450,359)],fill=GOLD);d.text((405,305),'och',font=ImageFont.truetype(B,28),fill=FG,anchor='mt')
  elif composition=='threeways':
   xy=[(150,290),(380,290),(610,290)];labels=[(150,430),(380,430),(610,430)]
   for x,y in xy:d.ellipse((x-99,y-99,x+99,y+99),fill=PANEL,outline=LINE,width=3)
  elif composition=='twoway':
   xy=[(200,290),(560,290)];labels=[(200,445),(560,445)];d.line((308,260,451,260),fill=LINE,width=6);d.polygon([(451,260),(432,248),(432,272)],fill=GOLD);d.line((308,337,451,337),fill=LINE,width=6);d.polygon([(308,337),(327,325),(327,349)],fill=GOLD)
  elif composition in('path','calendarpath','year','bridge','continuous','autonomy','change','cause'):
   d.line((95,420,665,420),fill=LINE,width=15)
   for x in(190,570):d.ellipse((x-12,408,x+12,432),fill=GOLD)
   xy=[(190,265),(570,265)];labels=[(190,470),(570,470)];d.polygon([(401,403),(426,420),(401,437)],fill=GOLD)
  elif composition in('meeting','conversation','team','social','class','family'):
   d.ellipse((48,109,712,610),fill=PANEL,outline=LINE,width=3);xy=[(230,290),(530,290)];labels=[(230,432),(530,432)];d.line((325,289,434,289),fill=GOLD,width=5);d.ellipse((368,268,392,292),fill=SOFT)
  elif composition in('clock','week','day','halfday','contrast','split','balance','grade','gradeletters','scale'):
   d.rounded_rectangle((28,68,732,637),radius=27,outline=LINE,width=3);d.line((380,94,380,610),fill=LINE,width=3);xy=[(210,272),(550,272)];labels=[(210,427),(550,427)]
  elif composition in('growth','garden','discovery','tools','language','subjects','globe','lifelong'):
   d.arc((53,105,700,620),180,350,fill=LINE,width=8);xy=[(220,265),(550,365)];labels=[(220,410),(550,505)]
  elif composition in('meal','materials','municipality','qualification','obligation','support','choice','exam','merge'):
   xy=[(220,245),(540,375)];labels=[(220,390),(540,520)];d.line((305,280,445,344),fill=LINE,width=6)
  else:xy=[(220,300),(540,300)];labels=[(220,440),(540,440)]
  if spec.get('qualifier'):wrap(d,spec['qualifier'],565 if composition=='cumulative' else 380,130 if composition=='cumulative' else 110,270 if composition=='cumulative' else 600,26 if composition=='cumulative' else 28)
  for node,(x,y),(tx,ty) in zip(nodes,xy,labels):
   icon(d,node['icon'],x,y,.85 if composition in('needs_branch','cumulative') else 1.0 if composition=='threeways' else 1.1)
   if node.get('crossed'):
    radius=node.get('cross_radius',103);diagonal=int(radius*.75)
    d.ellipse((x-radius,y-radius,x+radius,y+radius),outline=FG,width=6);d.line((x-diagonal,y+diagonal,x+diagonal,y-diagonal),fill=FG,width=9)
   wrap(d,node['label'],tx,ty,250 if composition in('needs_branch','cumulative') else 210 if composition=='threeways' else 295)
  d.line((72,62,182,62),fill=GOLD,width=5);d.text((380,675),'Schematisk illustration',font=ImageFont.truetype(F,22),fill=SOFT,anchor='mt')
  dest=out/(key+'.png');im.save(dest);assets.append(dict(asset_id=key,kind='foreground',visual_type='illustration',files=[info(dest)],creator='Homebrew video studio',reuse_terms='Original illustrative artwork under repository MIT license; source wording retains original publisher terms.',required_credits='Original source-based illustrations: Homebrew video studio. Exact source credits and terms in sources.yaml and accompanying CREDITS.md.',relevance_verification='A symbolic educational scene illustrating only the exact source statement '+', '.join(spec['source_sentence_ids'])+'. Labels are exact source substrings; not a documentary photograph or numerical chart.',creation_method=dict(tool=str(Path(__file__).relative_to(ROOT)),specification=str((ep/'picture-plan.json').relative_to(ROOT)),source_sentence_ids=spec['source_sentence_ids'],composition=composition)))
 (ep/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');print(sid,len(assets),'distinct pictorial illustrations')
if __name__=='__main__':
 for sid in sys.argv[1:]:main(sid)
