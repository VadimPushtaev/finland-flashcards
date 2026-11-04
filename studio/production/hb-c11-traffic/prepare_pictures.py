"""Create source-specific traffic diagrams and licensed photographic foregrounds."""
from pathlib import Path
import importlib.util,json,hashlib,math,re,sys,yaml
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parents[3];EP=ROOT/'studio/episodes/hb-c11-trafik';MEDIA=ROOT/'studio/media/hb-c11-trafik';OUT=MEDIA/'pictures';OUT.mkdir(parents=True,exist_ok=True)
sp=importlib.util.spec_from_file_location('traffic_object_primitives',ROOT/'studio/production/hb-c12a/pictures.py');P=importlib.util.module_from_spec(sp);sp.loader.exec_module(P)
P.BG='#243c32';P.PANEL='#315244';P.FG='#faf3e8';P.SOFT='#c5dfce';P.GOLD='#e3c58c';P.LINE='#4d7560'
BG,FG,SOFT,GOLD,LINE=P.BG,P.FG,P.SOFT,P.GOLD,P.LINE;F=P.F;B=P.B
script=yaml.safe_load((EP/'script.yaml').read_text());photos=json.loads((EP/'selected-photos.json').read_text()) if (EP/'selected-photos.json').exists() else {};assets=[];plans={}
info=lambda p:dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def text(d,t,x,y,w=650,size=26,fill=FG,bold=False):
 font=ImageFont.truetype(B if bold else F,size);words=t.split();lines=['']
 for word in words:
  test=(lines[-1]+' '+word).strip()
  if d.textlength(test,font=font)>w and lines[-1]:lines.append(word)
  else:lines[-1]=test
 for j,line in enumerate(lines):d.text((x,y+j*(size+7)),line,font=font,fill=fill,anchor='mt')
 return len(lines)*(size+7)
def arrow(d,a,b):
 d.line([a,b],fill=GOLD,width=5);ang=math.atan2(b[1]-a[1],b[0]-a[0]);d.polygon([b,(b[0]-17*math.cos(ang-.5),b[1]-17*math.sin(ang-.5)),(b[0]-17*math.cos(ang+.5),b[1]-17*math.sin(ang+.5))],fill=GOLD)
def node(d,kind,label,x,y,s=.85,width=230,cross=False):
 if kind=='fuel':
  d.rounded_rectangle((x-44*s,y-60*s,x+37*s,y+66*s),radius=8,outline=GOLD,width=4);d.rectangle((x-29*s,y-43*s,x+22*s,y-10*s),outline=SOFT,width=3);d.line([(x+37*s,y-26*s),(x+64*s,y-7*s),(x+64*s,y+61*s),(x+48*s,y+61*s)],fill=GOLD,width=4)
 elif kind=='lamp':
  d.rounded_rectangle((x-60*s,y-28*s,x+16*s,y+34*s),radius=12,outline=GOLD,width=4)
  for off in(-36,0,36):d.line([(x+27*s,y+off*.5*s),(x+82*s,y+off*s)],fill=GOLD,width=4)
 elif kind=='medical_document':
  P.icon(d,'document',x,y,s);d.line((x-22*s,y-56*s,x-22*s,y-25*s),fill=GOLD,width=6);d.line((x-37*s,y-41*s,x-7*s,y-41*s),fill=GOLD,width=6)
 elif kind=='police':
  P.icon(d,'car',x,y,s);d.rectangle((x-22*s,y-77*s,x+22*s,y-61*s),outline=SOFT,width=4)
 else:P.icon(d,kind,x,y,s)
 if cross:d.ellipse((x-83*s,y-83*s,x+83*s,y+83*s),outline=FG,width=5);d.line((x-59*s,y+59*s,x+59*s,y-59*s),fill=FG,width=7)
 text(d,label,x,y+100*s,w=width,size=25)
def row(d,nodes,y=290,link=None):
 xs=[380] if len(nodes)==1 else [190,570] if len(nodes)==2 else [145,380,615] if len(nodes)==3 else [105,290,475,660]
 for (kind,label,*opts),x in zip(nodes,xs):node(d,kind,label,x,y,.85 if len(nodes)<4 else .62,220 if len(nodes)<4 else 170,cross=bool(opts and opts[0]))
 if link:
  for a,b in zip(xs,xs[1:]):text(d,link,(a+b)/2,y-5,w=110,size=25,fill=GOLD,bold=True)
def flow(d,heading,nodes,output,join='OCH'):
 text(d,heading,380,100,size=26,bold=True);row(d,nodes,y=270,link=join);arrow(d,(250,437),(350,490));arrow(d,(510,437),(410,490));node(d,output[0],output[1],380,535,.62,width=600,cross=bool(len(output)>2 and output[2]))
def timeline(d,condition,start,end,label,kind='card',cross_end=False):
 text(d,condition,380,96,size=26,bold=True);P.icon(d,kind,190,280,.86);P.icon(d,'calendar',570,280,.86);arrow(d,(130,440),(640,440));d.line((165,424,165,457),fill=FG,width=4);d.line((598,424,598,457),fill=FG,width=4);text(d,start,180,478,w=290,size=25);text(d,end,580,478,w=280,size=25);text(d,label,380,582,w=660,size=25,fill=GOLD,bold=True)
 if cross_end:d.line((510,215,628,335),fill=FG,width=7)
# Every entry has a distinct stated object/relation; all full source pairs remain beside it.
for n,rowdata in enumerate(script['sentences'],1):
 key=f'picture-{n:03}';im=Image.new('RGB',(760,720),BG);d=ImageDraw.Draw(im);d.rounded_rectangle((20,20,740,700),radius=24,outline=LINE,width=3);sv=rowdata['sv'];desc='';composition='';r=photos.get(str(n)) if n!=5 else None
 if r:
  raw=Image.open(ROOT/r['raw_path']).convert('RGB');raw.thumbnail((470,450) if n==12 else (704,530));im.paste(raw,((100+(470-raw.width)//2 if n==12 else (760-raw.width)//2),100+(450-raw.height)//2 if n==12 else 75+(530-raw.height)//2));meta=r['imageinfo'][0]['extmetadata'];clean=lambda k:re.sub('<[^>]*>','',meta.get(k,{}).get('value','')).strip();creator=clean('Artist');license=clean('LicenseShortName');url=r['imageinfo'][0]['descriptionurl'];title=r['title'].removeprefix('File:');text(d,'cykelhjälm' if n==12 else title,380,619,w=690,size=19,fill=SOFT)
  if n==12:
   # Helmet photograph remains an object, while a small lamp states the second conditional object.
   node(d,'lamp','när det är mörkt',625,320,.55,width=190)
  path=OUT/(key+'.png');im.save(path);assets.append(dict(asset_id=key,kind='foreground',visual_type='photograph',files=[info(path)],creator=creator,reuse_terms=license+' '+clean('LicenseUrl'),required_credits=f'{title} — {creator}. {license}. {url} {clean("LicenseUrl")}. Proportionally resized without cropping on a neutral canvas;'+(' source-based lamp symbol added for the exact darkness condition.' if n==12 else ' contextual source title retained.'),source_url=url,relevance_verification='Actual object/place in retained primary Commons metadata; source sentence '+rowdata['sentence_id']+'. No policy/availability/personal-status assertion about the pictured subject. Full exact condition remains in bilingual text.',creation_method=dict(tool=str(Path(__file__).relative_to(ROOT)),source_sentence_ids=[rowdata['sentence_id']],source_metadata=r['research'],raw_sha256=r['download_sha256'])));desc=f'Actual licensed source photograph: {title}; concrete context, not proof of current rule.';composition='photograph'
 else:
  composition={1:'road_right',5:'rural_road_context',6:'road_left',9:'child_sidewalk',11:'missing_cyclepath',18:'sparse_service',19:'cost_objects',22:'rules_obligation',23:'conditional_fine',24:'alcohol_prohibited',25:'promille',26:'insurance_obligation',27:'insurance_provider',28:'inspection_and_register',30:'registration_examples',31:'web_registration',32:'valid_card_gate',33:'recognized_country',34:'residence_at_issue',35:'latin_or_translation',36:'age_and_health',37:'eu_validity',38:'exchange_residence_or_studies',39:'exchange_after_expiry',40:'expired_medical',41:'convention_country_limit',42:'named_country_limit',43:'permanent_exchange',44:'exchange_after_move',45:'valid_at_exchange',46:'medical_additional',47:'late_or_invalid_exam',48:'nonconvention_registration_anchor',49:'after_year_exam'}.get(n,'source_objects')
  if n in(1,6):
   text(d,'högertrafik' if n==1 else 'den vänstra kanten av körbanan',380,90,size=30,bold=True);d.rectangle((240,170,655,560),fill=LINE)
   for y in range(180,540,70):d.line((447,y,447,y+35),fill=FG,width=4)
   if n==1:
    arrow(d,(550,500),(550,220));arrow(d,(344,220),(344,500));P.icon(d,'car',550,360,.64);P.icon(d,'car',344,360,.64);text(d,'Finland',380,604,size=28)
   else:
    P.icon(d,'adult',270,350,.75);arrow(d,(325,510),(325,210));text(d,'fotgängare',270,580,w=240,size=26);text(d,'färdriktning',270,140,w=245,size=23);text(d,'vänstra kanten',470,604,w=390,size=27);d.line((235,170,235,560),fill=GOLD,width=7)
  elif n==5:
   text(d,'På landsbygden',380,100,size=30,bold=True);d.polygon([(250,570),(510,570),(430,230),(330,230)],fill=LINE);P.icon(d,'tree',150,330,.8);P.icon(d,'tree',610,430,.9);P.icon(d,'house',630,230,.6);text(d,'inte så ofta trottoarer längs vägarna',380,608,w=650,size=27)
  elif n==9:
   text(d,'Endast små barn',380,100,size=30,bold=True);row(d,[('child','små barn'),('bike','cykla på trottoaren')],link='→');d.rounded_rectangle((100,515,660,590),radius=15,outline=GOLD,width=3);text(d,'trottoaren',380,535,size=28)
  elif n==11:flow(d,'Om sådana saknas',[('bike','separat cykelbana',True),('bike','separat cykelfält',True)],('car','cyklar man på körbanan'),'OCH')
  elif n==18:
   text(d,'En del av trafiken',380,100,size=30,bold=True);row(d,[('bus','trafiken'),('clock','endast sällan')]);d.line((110,555,650,555),fill=LINE,width=5)
   for x in(150,610):d.ellipse((x-9,546,x+9,564),fill=GOLD)
  elif n==19:
   text(d,'dyra i Finland',380,100,size=30,bold=True);row(d,[('car','Egen bil'),('fuel','bensin'),('document','försäkringsavgifter'),('gear','bilservice')]);node(d,'coins','skatter',380,550,.6,width=600)
  elif n==22:row(d,[('car','kör med bil'),('document','noggrant följa de trafikregler')],link='→');text(d,'gäller i Finland',380,535,size=28,fill=GOLD)
  elif n==23:flow(d,'om de bryter mot reglerna',[('police','Polisen'),('document','reglerna')],('coins','ger böter'),'→')
  elif n==24:
   text(d,'Man får inte köra bil',380,100,size=30,bold=True);row(d,[('flask','druckit alkohol'),('car','inte köra bil',True)],link='→')
  elif n==25:
   text(d,'Gränsvärdet',380,100,size=30,bold=True);d.ellipse((165,205,595,600),outline=LINE,width=7);text(d,'0,5 ‰',380,285,w=620,size=98,fill=GOLD,bold=True);text(d,'0,5 promille',380,460,size=34);P.icon(d,'car',380,540,.64);text(d,'för att få köra',380,624,size=27)
  elif n==26:flow(d,'Om du har en bil',[('car','en bil'),('document','måste du teckna')],('shield','trafikförsäkring'),'→')
  elif n==27:row(d,[('town','försäkringsbolag'),('document','Trafikförsäkringen')],link='→');text(d,'tecknar du hos',380,536,size=28)
  elif n==28:
   text(d,'I Finland måste bilen',380,100,size=29,bold=True);row(d,[('magnify','besiktigas'),('database','registreras')],link='OCH');node(d,'car','bilen',380,555,.56,width=500)
  elif n==30:
   text(d,'till exempel',380,100,size=29,bold=True);row(d,[('magnify','besiktningsstationer'),('town','försäkringsbolag'),('business','bilhandlare')]);node(d,'database','Registreringen',380,555,.58,width=600)
  elif n==31:row(d,[('laptop','Traficoms webbplats'),('database','registrera bilen')],link='→')
  elif n==32:flow(d,'endast om',[('card','giltigt körkort'),('car','köra i Finland')],('shield','endast om du har ett giltigt körkort'),'→')
  elif n==33:
   text(d,'stater som Finland har erkänt',380,100,size=28,bold=True);row(d,[('globe','stater'),('card','alla körkort')],link='→');text(d,'I Finland accepteras',380,554,size=28)
  elif n==34:flow(d,'bott i Finland vid den tidpunkt som kortet beviljades',[('house','bott i Finland'),('calendar','vid den tidpunkt')],('card','accepteras inte',True),'OCH')
  elif n==35:
   text(d,'latinska bokstäver eller en översättning',380,100,size=27,bold=True);row(d,[('card','latinska bokstäver'),('book','finska, svenska eller engelska')],link='ELLER');text(d,'körkortet',380,553,size=30)
  elif n==36:
   text(d,'Du måste också uppfylla',380,100,size=28,bold=True);row(d,[('calendar','ålders-'),('hospital','hälsokrav')],link='OCH');text(d,'som gäller i Finland',380,556,size=28)
  elif n==37:timeline(d,'EU- eller EES-land','körkort','så länge kortet är giltigt','kan du köra med detta kort i Finland')
  elif n==38:flow(d,'Du kan du byta ut kortet',[('house','bor stadigvarande'),('school','studerat i Finland i minst sex månader')],('card','ett finländskt körkort'),'ELLER')
  elif n==39:
   timeline(d,'bytas mot ett finskt körkort','giltighetstid har gått ut','inom två år','BYTE av kort — inte en ny giltighetstid');d.ellipse((112,202,268,358),outline=FG,width=5);d.line((135,335,245,225),fill=FG,width=7)
  elif n==40:
   text(d,'Om kortets giltighetstid gått ut',380,100,size=28,bold=True);row(d,[('card','giltighetstid gått ut',True),('medical_document','behöver du ett läkarutlåtande')],link='→')
  elif n==41:flow(d,'körkort som utfärdats i ett land',[('globe','utanför EU'),('document','anslutet till Genève- eller Wienkonventionerna')],('calendar','högst två år i Finland'),'OCH')
  elif n==42:
   text(d,'Hongkong, Macao eller Taiwan',380,100,size=29,bold=True);row(d,[('globe','Hongkong, Macao eller Taiwan'),('calendar','högst två år')]);text(d,'får du likaså köra bil',380,552,size=28)
  elif n==43:flow(d,'när du bor stadigvarande i Finland',[('house','bor stadigvarande'),('card','utländska körkort')],('card','ett finskt körkort'),'→')
  elif n==44:timeline(d,'flyttat till Finland OCH bor här stadigvarande','När du har flyttat','två år på dig','byta ditt körkort mot ett finskt körkort','house')
  elif n==45:
   text(d,'vid den tidpunkt när du byter det',380,100,size=28,bold=True);row(d,[('card','Ditt körkort'),('calendar','tidpunkt när du byter det')],link='OCH');text(d,'måste vara giltigt',380,550,size=30,fill=GOLD)
  elif n==46:
   text(d,'Du behöver också',380,100,size=30,bold=True);node(d,'medical_document','ett läkarutlåtande',380,355,1.3,width=650)
  elif n==47:flow(d,'måste du avlägga förarexamen',[('calendar','inte byter ut ditt kort i tid'),('card','kort inte längre gäller',True)],('book','teori- och körprov i Finland'),'ELLER')
  elif n==48:timeline(d,'inte anslutet till Genève- eller Wienkonventionerna','registrerad i befolkningsdatasystemet','under ett års tid','EFTER registrering i Finland','database')
  elif n==49:flow(d,'Därefter',[('calendar','Därefter'),('car','om du vill fortsätta köra bil')],('book','måste du avlägga förarexamen i Finland'),'OCH')
  else:raise ValueError(('Unplanned actual missing photograph',n))
  text(d,'Schematisk illustration',380,674,size=21,fill=SOFT);path=OUT/(key+'.png');im.save(path);desc=f'Individually authored source-specific {composition} diagram; exact condition in '+rowdata['sentence_id'];assets.append(dict(asset_id=key,kind='foreground',visual_type='illustration',files=[info(path)],creator='Homebrew video studio',reuse_terms='Original schematic artwork under repository MIT license; source text retains its publisher terms.',required_credits='Original source-based pictorial diagrams: Homebrew video studio. Exact source credits in sources.yaml and accompanying sidecar.',relevance_verification=desc,creation_method=dict(tool=str(Path(__file__).relative_to(ROOT)),source_sentence_ids=[rowdata['sentence_id']],composition=composition)))
 rowdata.update(asset_ids=['episode_background',key],render_image=str(path.relative_to(ROOT)),render_caption=False,visual_cue=desc);plans[key]=dict(id=key,composition=composition,description=desc,source_sentence_ids=[rowdata['sentence_id']])
(EP/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');(EP/'picture-implementation.json').write_text(json.dumps(plans,ensure_ascii=False,indent=2)+'\n');(EP/'script.yaml').write_text(yaml.safe_dump(script,allow_unicode=True,sort_keys=False,width=100));print(len(assets),'foreground pictures',sum(a['visual_type']=='photograph' for a in assets),'photographs')
