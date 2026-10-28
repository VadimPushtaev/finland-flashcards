"""Draw non-graphic pictorial diagrams of the four episodes' source relationships."""
from pathlib import Path
import hashlib,json,math,yaml
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
SIDS=['hb-c06-vald','hb-c06-manniskohandel','hb-c06-brottsoffer','hb-c06-rattshjalp']
BG='#252747';FG='#faf3e8';MUT='#cbd1ec';GOLD='#e3c58b';LINE='#515a82'
FONT='/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
TITLES={'rights':'mänskliga rättigheter','health':'hälsa','boundary':'våld','justice':'rättshjälp','prosecution':'allmänt åtal','consent':'självbestämmande','choice':'samtycke','sleep':'kan inte samtycka','scope':'samtycke','age':'barn och unga','support':'stöd','recovery':'återhämta sig','work':'arbete','restriction':'kontroll','people':'män · kvinnor · barn','contact':'kontakta','emergency':'112','shelter':'skyddshem','services':'hjälp','documents':'rättshjälp','marriage':'äktenskap','budget':'inkomster','no_consent':'utan samtycke','fear':'rädd för att säga nej','child':'under 16 år','peers':'samma ålder','website':'ihmiskauppa.fi','coercion':'tvinga'}
for sid in SIDS:
 ep=ROOT/'studio/episodes'/sid;media=ROOT/'studio/media'/sid
 d=yaml.safe_load((ep/'script.yaml').read_text());pictures=[a for a in json.loads((ep/'foreground-assets.json').read_text()) if a.get('visual_type')=='photograph'] if (ep/'foreground-assets.json').exists() else []
 for key in dict.fromkeys(Path(r['render_image']).stem for r in d['sentences'] if r.get('render_image') and Path(r['render_image']).stem in TITLES):
  im=Image.new('RGB',(760,720),BG);dr=ImageDraw.Draw(im)
  def line(points,color=FG,width=6):dr.line(points,fill=color,width=width)
  def text(x,y,t,size=30,color=FG):
   while dr.textlength(t,font=ImageFont.truetype(FONT,size))>675:size-=1
   dr.text((x,y),t,font=ImageFont.truetype(FONT,size),fill=color,anchor='mm')
  def person(x,y,s=1,color=FG):
   dr.ellipse((x-22*s,y-22*s,x+22*s,y+22*s),fill=color)
   line([(x,y+30*s),(x,y+115*s)],color,max(2,int(12*s)))
   line([(x-40*s,y+65*s),(x+40*s,y+65*s)],color,max(2,int(10*s)))
   line([(x,y+110*s),(x-30*s,y+165*s)],color,max(2,int(10*s)))
   line([(x,y+110*s),(x+30*s,y+165*s)],color,max(2,int(10*s)))
  def arrow(a,b,color=GOLD):
   line([a,b],color,7);ang=math.atan2(b[1]-a[1],b[0]-a[0]);dr.polygon([b,(b[0]-22*math.cos(ang-.5),b[1]-22*math.sin(ang-.5)),(b[0]-22*math.cos(ang+.5),b[1]-22*math.sin(ang+.5))],fill=color)
  def document(x,y):
   dr.rounded_rectangle((x-55,y,x+55,y+150),radius=8,outline=FG,width=6)
   for yy in range(y+30,y+125,25):line([(x-30,yy),(x+30,yy)],MUT,4)
  def bubble(x,y,word=''):
   dr.rounded_rectangle((x-70,y-35,x+70,y+35),radius=15,outline=GOLD,width=5)
   line([(x-25,y+35),(x-40,y+55),(x+5,y+35)],GOLD,5)
   if word:text(x,y,word,30)
  def building(x,y,kind='legal'):
   if kind=='home':
    dr.polygon([(x-90,y+35),(x,y-25),(x+90,y+35)],outline=GOLD,width=7)
    dr.rectangle((x-65,y+35,x+65,y+145),outline=FG,width=6)
    dr.rectangle((x-20,y+85,x+20,y+145),outline=MUT,width=5)
   else:
    dr.polygon([(x-85,y),(x,y-45),(x+85,y)],outline=GOLD,width=6)
    for xx in [x-55,x,x+55]:line([(xx,y+10),(xx,y+125)],FG,9)
    line([(x-85,y+140),(x+85,y+140)],FG,8)
  text(380,65,TITLES[key],37,GOLD);line([(55,110),(705,110)],LINE,3)
  if key in ['rights','boundary','coercion']:
   dr.polygon([(380,180),(535,235),(510,425),(380,535),(250,425),(225,235)],outline=GOLD,width=9)
   person(380,255,.95)
   if key in ['boundary','coercion']:
    line([(185,565),(575,565)],MUT,7)
    dr.ellipse((115,535,185,605),outline=FG,width=5)
    line([(125,595),(175,545)],FG,5)
  elif key=='health':
   dr.arc((185,200,475,470),0,180,fill=FG,width=12)
   line([(185,335),(185,225)],FG,10);line([(475,335),(475,225)],FG,10)
   line([(330,470),(330,540),(510,540),(555,490)],GOLD,10)
   dr.ellipse((530,435,600,505),outline=GOLD,width=12)
   dr.rounded_rectangle((300,180,360,220),radius=12,fill=MUT)
  elif key in ['justice','prosecution']:
   building(380,225);person(180,425,.7);person(580,425,.7)
   document(380,425);arrow((220,550),(295,550));arrow((540,550),(465,550))
  elif key in ['consent','choice','scope']:
   person(200,250);person(560,250);bubble(200,190,'ja' if key=='choice' else '');bubble(560,190)
   line([(285,400),(475,400)],GOLD,6)
   dr.ellipse((335,455,425,545),outline=GOLD,width=6)
   if key=='scope':
    line([(350,530),(410,470)],FG,6);text(380,600,'varje gång',31)
   else:
    line([(350,495),(375,520),(415,470)],FG,8)
  elif key=='sleep':
   dr.rounded_rectangle((155,340,600,455),radius=18,outline=FG,width=8)
   dr.ellipse((180,315,245,380),fill=MUT)
   line([(255,360),(540,360)],FG,28)
   line([(155,455),(155,520)],FG,10);line([(600,455),(600,520)],FG,10)
   dr.ellipse((320,190,440,310),outline=GOLD,width=7);line([(337,292),(425,207)],GOLD,7)
  elif key in ['no_consent','fear']:
   person(200,285,.85);person(560,285,.85);bubble(200,205,'nej' if key=='fear' else '');bubble(560,205)
   dr.ellipse((320,445,440,565),outline=GOLD,width=7);line([(337,547),(425,462)],GOLD,8)
  elif key=='child':
   dr.polygon([(380,180),(535,235),(510,425),(380,535),(250,425),(225,235)],outline=GOLD,width=9)
   person(380,290,.65);text(380,605,'under 16 år',38)
  elif key=='peers':
   person(230,265,.85);person(530,265,.85)
   line([(350,360),(410,360)],GOLD,7);line([(350,390),(410,390)],GOLD,7)
  elif key=='age':
   person(200,275,.85);person(540,275,.85)
   line([(100,565),(650,565)],GOLD,7)
   for x,label in [(200,'16'),(540,'17')]:line([(x,540),(x,590)],MUT,6);text(x,625,label,40)
  elif key in ['support','recovery']:
   person(220,300,.85);person(535,300,.85);bubble(380,235)
   line([(90,540),(665,540)],GOLD,8)
   dr.arc((120,175,640,690),190,350,fill=GOLD,width=7)
   if key=='recovery':arrow((225,610),(535,610))
  elif key=='work':
   person(170,300,.85)
   dr.rounded_rectangle((405,300,650,470),radius=18,outline=FG,width=8)
   line([(475,300),(475,260),(580,260),(580,300)],GOLD,8)
   arrow((240,400),(350,400));dr.ellipse((290,485,370,565),outline=MUT,width=5)
  elif key=='marriage':
   person(200,245,.8);person(560,245,.8)
   dr.ellipse((260,405,400,545),outline=GOLD,width=9);dr.ellipse((355,405,495,545),outline=MUT,width=9)
   line([(280,590),(480,590)],FG,6);line([(345,565),(415,615)],GOLD,7)
  elif key=='budget':
   person(190,285,.9);document(560,320)
   for x,y in [(350,450),(350,425),(350,400)]:dr.ellipse((x-55,y-20,x+55,y+20),outline=GOLD,width=5)
   arrow((400,455),(475,455))
  elif key=='restriction':
   person(380,250,.9)
   for a,b in [((290,400),(160,400)),((470,400),(600,400))]:arrow(a,b,MUT)
   for x in [125,635]:line([(x,335),(x,465)],GOLD,13)
   bubble(380,540);line([(330,570),(430,510)],MUT,7)
  elif key=='people':
   for x,s in [(170,1),(385,.65),(590,1)]:person(x,290,s)
   line([(85,550),(680,550)],GOLD,6)
  elif key=='contact':
   person(380,215,.65)
   for x in [160,380,600]:arrow((380,365),(x,440))
   dr.rounded_rectangle((115,485,205,610),radius=17,outline=FG,width=6);line([(140,585),(180,585)],MUT,4)
   bubble(380,535);building(600,485,'home' if key=='services' else 'legal')
  elif key=='services':
   person(380,215,.65)
   for x in [150,380,610]:arrow((380,365),(x,435))
   building(150,480);text(150,650,'kommunen',25)
   dr.rectangle((320,480,440,600),outline=FG,width=6);line([(380,505),(380,565)],GOLD,7);line([(350,535),(410,535)],GOLD,7);text(380,650,'hälsocentralen',25)
   building(610,480,'home');line([(610,425),(610,470)],GOLD,6);line([(590,440),(630,440)],GOLD,6);text(610,650,'församlingarna',25)
  elif key=='emergency':
   dr.rounded_rectangle((230,180,530,600),radius=35,outline=FG,width=10)
   dr.rounded_rectangle((260,235,500,520),radius=12,outline=MUT,width=5)
   text(380,350,'112',83,GOLD);dr.ellipse((355,550,405,590),outline=GOLD,width=6)
  elif key=='shelter':
   building(380,260,'home');person(220,420,.65);person(535,455,.45)
   dr.arc((125,165,635,690),190,350,fill=GOLD,width=7)
  elif key=='website':
   dr.rounded_rectangle((110,205,650,565),radius=18,outline=FG,width=7)
   line([(110,280),(650,280)],MUT,5)
   for x in [145,180,215]:dr.ellipse((x-7,235,x+7,249),fill=GOLD)
   text(380,360,'ihmiskauppa.fi',39,GOLD);document(380,405)
  elif key=='documents':
   person(180,280,.8);document(400,250);document(575,355)
   arrow((235,425),(320,425));line([(100,570),(650,570)],GOLD,6)
  else:raise ValueError(key)
  p=media/'pictures'/f'{key}.png';p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
  pictures.append({'asset_id':'picture_'+key,'kind':'foreground','visual_type':'diagram','files':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}],'creator':'Homebrew video studio original pictorial layout','reuse_terms':'Original geometric illustration under repository license; source labels retain anthology attribution.','required_credits':'Original source-based pictorial diagrams; exact text source credits in sources.yaml.','relevance_verification':'Non-graphic diagram of '+key+' relationships from the associated exact source sentences. Generic roles and objects only, never actual victim/suspect identity. No added legal thresholds, provider promises or current-law claims.','creation_method':{'tool':str(Path(__file__).relative_to(ROOT)),'canvas':'760x720','fonts':'Liberation Sans'}})
 (ep/'foreground-assets.json').write_text(json.dumps(pictures,ensure_ascii=False,indent=2)+'\n')
 print(sid,len(pictures),'source-based pictorial diagrams')
