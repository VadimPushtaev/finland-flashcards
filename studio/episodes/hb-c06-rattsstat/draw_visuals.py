"""Reproduce Chapter6 source-based pictorial diagrams without adding factual claims."""
from pathlib import Path
import json,hashlib,re
from PIL import Image,ImageDraw,ImageFont,ImageOps
import yaml
ROOT=Path(__file__).resolve().parents[3]
FONT='/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
BOLD='/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
BG='#252747';FG='#faf3e8';MUTED='#cbd1ec';ACC='#e3c58b';LINE='#515a82'
def info(path):return dict(path=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size)
def make(kind,path):
 im=Image.new('RGB',(760,720),BG);d=ImageDraw.Draw(im)
 def txt(x,y,text,size=30,bold=False,fill=FG):d.text((x,y),text,font=ImageFont.truetype(BOLD if bold else FONT,size),fill=fill,anchor='mm')
 def line(points,fill=ACC,width=5):d.line(points,fill=fill,width=width)
 def box(rect):d.rounded_rectangle(rect,16,fill='#33395d',outline=LINE,width=3)
 def person(x,y,professional=False):
  d.ellipse((x-24,y-25,x+24,y+23),fill=MUTED)
  d.rounded_rectangle((x-40,y+35,x+40,y+120),12,fill=ACC if professional else LINE)
  line([(x-22,y+120),(x-22,y+175)],FG,9);line([(x+22,y+120),(x+22,y+175)],FG,9)
 def court(x,y,scale=1):
  d.polygon([(x-85*scale,y),(x,y-60*scale),(x+85*scale,y)],fill=ACC)
  for off in (-55,0,55):d.rectangle((x+(off-10)*scale,y+15*scale,x+(off+10)*scale,y+120*scale),fill=MUTED)
  d.rectangle((x-90*scale,y+120*scale,x+90*scale,y+135*scale),fill=ACC)
 def book(x,y,label='LAG'):
  d.rounded_rectangle((x-90,y-110,x+90,y+110),12,fill='#384766',outline=ACC,width=4);line([(x-65,y-105),(x-65,y+105)],MUTED,3);txt(x+10,y,label,34,True)
 if kind=='powers':
  txt(380,65,'Maktfördelning',42,True)
  for x,label in [(140,'Lagstiftande'),(380,'Verkställande'),(620,'Dömande')]:
   box((x-105,140,x+105,590));court(x,235,.7);txt(x,455,label,26,True);txt(x,500,'makt',28)
  # Separate pillars visualize separate powers; no hierarchy or inferred agency.
 elif kind=='norms':
  txt(380,65,'Värderingar och normer',38,True)
  for x,y in [(140,230),(380,190),(620,230)]:person(x,y)
  line([(140,440),(380,490),(620,440)],MUTED,4)
  book(380,590,'LAG')
  txt(380,430,'Samhället',34,True)
 elif kind=='lawbook':
  txt(380,80,'Lagar',44,True);book(380,310)
  for i,x in enumerate((180,380,580)):person(x,485)
 elif kind=='bribery':
  txt(380,70,'Mutor och korruption',40,True)
  d.rectangle((95,280,245,420),fill=MUTED);d.rectangle((80,260,260,290),fill=ACC)
  line([(170,260),(170,420)],ACC,13);d.ellipse((128,220,170,263),outline=ACC,width=6);d.ellipse((171,220,215,263),outline=ACC,width=6)
  person(585,270,True);txt(585,530,'Myndighet',30,True)
  line([(280,350),(460,350)],MUTED,7);d.polygon([(460,350),(440,336),(440,364)],fill=MUTED)
  d.ellipse((307,287,433,413),outline='#e09b9b',width=10);line([(326,392),(415,308)],'#e09b9b',10)
  txt(380,625,'Att ge och ta emot mutor är brott',28)
 elif kind in ('report','tips'):
  txt(380,65,'Brottsanmälan' if kind=='report' else 'Tips till polisen',42,True)
  if kind=='report':court(155,225,.9);txt(155,455,'Polisstation',28,True)
  else:person(155,245);txt(155,455,'Tips',28,True)
  # Telephone and screen/mail symbols correspond to the explicit reporting channels.
  d.rounded_rectangle((305,215,415,390),17,outline=MUTED,width=7);d.ellipse((353,365,368,380),fill=ACC);txt(360,455,'Telefon',28,True)
  d.rectangle((500,235,690,360),outline=MUTED,width=7);line([(500,235),(595,315),(690,235)],ACC,4);txt(595,455,'Internet' if kind=='report' else 'E-post',28,True)
  if kind=='tips':txt(380,580,'Anonymt',32)
 elif kind=='levels':
  txt(380,58,'Domstolar',42,True)
  for y,label in [(190,'Högsta domstolen'),(370,'Hovrätter'),(550,'Tingsrätter')]:
   box((115,y-65,645,y+65));court(185,y-20,.35);txt(425,y,label,32,True)
  for y in (280,460):line([(380,y+15),(380,y-15)],MUTED,6);d.polygon([(380,y-27),(368,y-9),(392,y-9)],fill=MUTED)
  txt(380,666,'Separat: förvaltnings- och specialdomstolar',25)
 elif kind=='bench':
  txt(380,65,'Nämndemannasammansättning',33,True)
  for x,pro in [(150,False),(380,True),(610,False)]:person(x,225,pro)
  d.rectangle((70,435,690,500),fill=ACC)
  txt(150,550,'Nämndeman',27);txt(380,550,'Yrkesdomare',27);txt(610,550,'Nämndeman',27)
  txt(380,650,'Samma makt i beslutsfattandet',29)
 elif kind=='video':
  txt(380,70,'Vittnen och sakkunniga',38,True)
  d.rounded_rectangle((70,175,470,470),18,outline=MUTED,width=7)
  person(270,245);line([(270,470),(270,525),(360,525)],MUTED,7)
  person(605,285);line([(490,300),(535,300)],ACC,6)
  txt(380,625,'Telefon eller videoförbindelse',31)
 elif kind=='screen':
  txt(380,70,'Skydd för vittnen',40,True)
  person(180,275);person(595,275)
  d.rounded_rectangle((337,170,425,560),8,fill=LINE,outline=ACC,width=5)
  for y in range(190,550,25):line([(350,y),(412,y)],MUTED,2)
  txt(180,615,'Vittne',32);txt(595,615,'Åtalad',32)
 else:raise ValueError(kind)
 path.parent.mkdir(parents=True,exist_ok=True);im.save(path)

def prepare(sid):
 ep=ROOT/'studio/episodes'/sid;media=ROOT/'studio/media'/sid;d=yaml.safe_load((ep/'script.yaml').read_text());photos=json.loads((ep/'foreground-sources.json').read_text());assets=[]
 for request in d['asset_requests']:
  key=request['id']
  if request['kind']!='foreground':continue
  path=media/'pictures'/f'{key}.png';path.parent.mkdir(parents=True,exist_ok=True)
  if key in photos:
   p=photos[key];im=Image.open(ROOT/p['path']).convert('RGB');im.thumbnail((760,720));canvas=Image.new('RGB',(760,720),BG);canvas.paste(im,((760-im.width)//2,(720-im.height)//2));canvas.save(path)
   pi=p['imageinfo'];meta=pi['extmetadata'];clean=lambda n:re.sub('<[^>]+>','',meta.get(n,{}).get('value','')).strip()
   license=clean('LicenseShortName');creator=clean('Artist');url=pi['descriptionurl'];licenseurl=clean('LicenseUrl')
   asset=dict(asset_id=key,kind='foreground',visual_type='photograph' if not p['title'].endswith('.svg') else 'flag',files=[info(path)],creator=creator or 'See Commons source',reuse_terms=f'{license}; {licenseurl}',required_credits=f"{p['title']} — {creator}. {license}. {url} License: {licenseurl}. Scaled and letterboxed; photograph adaptation retains its source license.",source_url=url,relevance_verification='Identity verified from Commons image description: '+clean('ImageDescription')+' Used as identified illustrative institution/object, not evidence of an unpictured historical event.')
  else:
   make(key,path)
   asset=dict(asset_id=key,kind='foreground',visual_type='diagram',files=[info(path)],creator='Homebrew video studio',reuse_terms='Original source-based explanatory illustration; repository MIT license. Source wording retains anthology attribution.',required_credits='Original Homebrew studio explanatory diagram; text and relationships follow the exact Swedish source and its recorded attribution.',relevance_verification='Pictorial diagram of source-stated relationships using institution, person, book, telephone, mail or screen shapes. Labels repeat source concepts; no invented outcome, statistics or identities.',creation_method=dict(tool='studio/episodes/hb-c06-rattsstat/draw_visuals.py',size='760x720',fonts='Liberation Sans'))
  assets.append(asset)
  for row in d['sentences']:
   if key in row['asset_ids']:row['render_image']=path.relative_to(ROOT).as_posix()
 (ep/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2))
 d['render']['credits']=[c for c in d['render']['credits'] if c['heading']!='Bilder · Изображения']
 d['render']['credits'].append(dict(heading='Bilder · Изображения',paragraphs=['Originaldiagram: Homebrew video studio; relationer ur källtexten.','Fotografier och flagga: Wikimedia Commons; fulla upphovs- och licensuppgifter i CREDITS-filen.']))
 (ep/'script.yaml').write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False,width=100))
 print('Prepared',sid,len(assets),'foregrounds')
if __name__=='__main__':
 import sys
 for sid in sys.argv[1:]:prepare(sid)
