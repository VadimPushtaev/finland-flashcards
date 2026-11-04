"""Create concrete photographs and varied exact-source public-health illustrations."""
from pathlib import Path
import yaml,json,hashlib,re,copy,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];SID='hb-c10-folkhalsa';EP=ROOT/'studio/episodes'/SID;MEDIA=ROOT/'studio/media'/SID;OUT=MEDIA/'pictures';OUT.mkdir(parents=True,exist_ok=True)
code=(ROOT/'studio/production/hb-c10/author_utkomststod.py').read_text().split('specs=')[0];ns={'__file__':str(Path(__file__))};exec(compile(code,'health-primitives','exec'),ns)
canvas,label,house,person,coins,paper,arrow=[ns[k] for k in ['canvas','label','house','person','coins','paper','arrow']];FG,SOFT,GOLD,LINE,PANEL,BG=[ns[k] for k in ['FG','SOFT','GOLD','LINE','PANEL','BG']]
def info(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def heart(d,x,y,s=1):
    d.ellipse((x-55*s,y-30*s,x+2*s,y+26*s),fill=GOLD);d.ellipse((x-2*s,y-30*s,x+55*s,y+26*s),fill=GOLD);d.polygon([(x-52*s,y+7*s),(x+52*s,y+7*s),(x,y+76*s)],fill=GOLD)
def shield(d,x,y,s=1):d.polygon([(x-60*s,y-65*s),(x,y-85*s),(x+60*s,y-65*s),(x+50*s,y+25*s),(x,y+80*s),(x-50*s,y+25*s)],outline=SOFT,width=5)
def cross(d,x,y,s=1):d.rectangle((x-10*s,y-40*s,x+10*s,y+40*s),fill=GOLD);d.rectangle((x-40*s,y-10*s,x+40*s,y+10*s),fill=GOLD)
def book(d,x,y,s=1):
    d.polygon([(x,y-40*s),(x-75*s,y-65*s),(x-75*s,y+65*s),(x,y+90*s),(x+75*s,y+65*s),(x+75*s,y-65*s)],outline=SOFT,width=5);d.line((x,y-40*s,x,y+90*s),fill=GOLD,width=5)
    for yy in[-20,15,45]:d.line((x-58*s,y+yy*s,x-15*s,y+(yy+15)*s),fill=LINE,width=4);d.line((x+15*s,y+(yy+15)*s,x+58*s,y+yy*s),fill=LINE,width=4)
def ball(d,x,y,s=1):d.ellipse((x-55*s,y-55*s,x+55*s,y+55*s),outline=SOFT,width=5);d.line((x-55*s,y,x+55*s,y),fill=GOLD,width=4);d.arc((x-35*s,y-55*s,x+35*s,y+55*s),75,285,fill=GOLD,width=4)
def clinic(d,x,y,s=1):house(d,x,y,s);cross(d,x,y+25*s,.5*s)
def plate(d,x,y,s=1):
    d.ellipse((x-70*s,y-70*s,x+70*s,y+70*s),outline=SOFT,width=5);d.ellipse((x-50*s,y-50*s,x+50*s,y+50*s),outline=LINE,width=4);d.line((x-95*s,y-65*s,x-95*s,y+65*s),fill=GOLD,width=5);d.line((x+95*s,y-65*s,x+95*s,y+65*s),fill=GOLD,width=5)
def bed(d,x,y,s=1):
    d.line((x-80*s,y-50*s,x-80*s,y+70*s),fill=SOFT,width=6);d.rounded_rectangle((x-75*s,y-25*s,x+80*s,y+45*s),radius=12,outline=SOFT,width=5);d.rectangle((x-65*s,y-15*s,x-15*s,y+15*s),outline=GOLD,width=4);d.line((x+80*s,y+10*s,x+80*s,y+70*s),fill=SOFT,width=6)
def clock(d,x,y,s=1):d.ellipse((x-58*s,y-58*s,x+58*s,y+58*s),outline=SOFT,width=5);d.line((x,y-38*s,x,y,x+30*s,y+18*s),fill=GOLD,width=5)
def group(d,x,y,s=1):
    person(d,x,y,s)
    for dx in[-62,62]:person(d,x+dx*s,y+20*s,.65*s)
def magnify(d,x,y,s=1):d.ellipse((x-55*s,y-55*s,x+55*s,y+55*s),outline=GOLD,width=7);d.line((x+40*s,y+40*s,x+95*s,y+95*s),fill=GOLD,width=10)
def record(d,x,y,title='vaccinationer',s=1):
    paper(d,x,y,150*s,200*s);cross(d,x,y-58*s,.35*s);label(d,(x,y+120*s),title,25)
def folder(d,x,y,text,s=1):paper(d,x,y,160*s,180*s);cross(d,x,y-35*s,.4*s);label(d,(x,y+108*s),text,24)
def dot(d,x,y,r=5):d.ellipse((x-r,y-r,x+r,y+r),fill=GOLD)
photos=json.loads((EP/'selected-photos.json').read_text());old=json.loads((EP/'retained-photo-assets.json').read_text());objects=json.loads((EP/'object-photos.json').read_text());photos.pop('17',None);photos['45']=objects['vaccination'];aliases={8:9,38:37,43:42,52:51,54:53}
script=yaml.safe_load((EP/'script.yaml').read_text());plans=json.loads((EP/'picture-plan.json').read_text());assets=[];downloads=[];screen=[];by_index={}
legacy_context={12:'Verified actual Tornio health centre illustrates access to healthcare, not a named treatment or current service guarantee.',21:'Actual Oodi community digital workshop illustrates social interaction; nobody is identified as a patient or benefit recipient.',23:'Actual Finnish2019voting booth illustrates democratic participation, not a current ballot or party endorsement.',24:'Actual Vantaankoski classroom2010 illustrates education; no claim this is a current classroom or particular health lesson.',25:'Verified Ylimuonio community voluntary work illustrates useful activity, without attributing a medical condition.',33:'Verified Finnish Red Cross Blood Service premises illustrate a real health-related organization, without endorsement.',41:'Verified Helsinki Central Library Oodi photograph illustrates a source-listed information resource, without current opening-hour claims.',46:'Verified Jäkärlä health centre and neuvola illustrates a source child-health clinic setting, not a guarantee about particular current services.'}
for i,row in enumerate(script['sentences']):
    if i in aliases:continue
    key=f'picture-{i+1:03}';dest=OUT/f'sentence-{i+1:02}.png';asset=None
    if str(i) in photos or str(i) in old:
        if str(i) in photos:
            rec=photos[str(i)];pi=rec['imageinfo'];m=pi['extmetadata'];clean=lambda k:re.sub('<[^>]+>','',m.get(k,{}).get('value','')).strip();raw=ROOT/rec['path'];creator=clean('Artist');terms=clean('LicenseShortName')+' '+clean('LicenseUrl');credit=rec['title'].removeprefix('File:')+' — '+creator+'. '+terms+'. '+pi['descriptionurl']+'. Proportionally resized and letterboxed; source terms retained.';source=pi['descriptionurl'];context=rec['context'];downloads.append(dict(**info(raw),url=rec['download_url']))
        else:
            rec=old[str(i)];a=rec['asset_record'];raw=ROOT/rec['path'];creator=a['creator'];terms=a['reuse_terms'];credit=a['required_credits'];source=a['source_url'];context=legacy_context[i];downloads.append(dict(**info(raw),url=rec['url']))
        im=Image.open(raw).convert('RGB');im.thumbnail((760,720),Image.Resampling.LANCZOS);full=Image.new('RGB',(760,720),BG);full.paste(im,((760-im.width)//2,(720-im.height)//2));full.save(dest)
        asset=dict(asset_id=key,kind='foreground',visual_type='photograph',files=[info(dest)],creator=creator,source_url=source,reuse_terms=terms,required_credits=credit,relevance_verification=context,creation_method=dict(tool=str(Path(__file__).relative_to(ROOT)),transform='Complete source photograph proportionally resized and letterboxed in chapter palette.'))
        screen.append(source.rsplit('/wiki/',1)[-1].replace('_',' ').removeprefix('File:')+' — '+creator+' · '+terms.split('https:')[0].split('http:')[0])
    else:
        title=plans[i]['title'];im,d=canvas(title)
        if i==0:
            for x in[150,380,610]:d.ellipse((x-86,220,x+86,392),outline=LINE,width=5)
            heart(d,150,285,.7);person(d,380,270,.6);group(d,610,270,.43);d.line((150,440,610,440),fill=GOLD,width=5)
            for x,t in[(150,'fysiskt'),(380,'psykiskt'),(610,'socialt')]:label(d,(x,495),t,30)
        elif i==1:
            person(d,180,300,1.05);paper(d,510,330,210,280)
            for y in[245,310,375]:d.line([(440,y),(457,y+17),(485,y-20)],fill=GOLD,width=5)
            arrow(d,(270,345),(370,345));label(d,(380,570),'uppgifter och utmaningar',29)
        elif i==2:
            person(d,380,320,.9);shield(d,380,340,1.65);book(d,150,260,.65);ball(d,610,270,.7);group(d,610,470,.38);heart(d,150,455,.6);label(d,(380,590),'mer än frånvaro av sjukdom',27)
        elif i==3:
            house(d,175,320,1);person(d,420,300,.9);paper(d,610,300,115,155);d.line((100,520,660,520),fill=LINE,width=6);label(d,(380,570),'fungera i vardagen',31)
        elif i==4:
            for x,y in[(190,260),(570,260),(190,495),(570,495)]:d.rounded_rectangle((x-110,y-95,x+110,y+100),radius=20,outline=LINE,width=4)
            book(d,190,240,.7);ball(d,570,240,.8);paper(d,190,475,120,150);group(d,570,455,.43)
            for x,y,t in[(190,350,'studera'),(570,350,'hobbyer'),(190,590,'arbeta'),(570,590,'socialt liv')]:label(d,(x,y),t,26)
        elif i==5:
            person(d,175,295,1);ball(d,585,325,.9);d.line((280,330,350,330),fill=SOFT,width=6);d.line((435,330,490,330),fill=SOFT,width=6);d.rectangle((365,255,385,405),fill=GOLD);d.rectangle((405,255,425,405),fill=GOLD);cross(d,175,480,.7);label(d,(380,585),'kan behöva ge upp sådant',28)
        elif i==6:
            person(d,380,295,1);heart(d,380,450,.75);folder(d,150,300,'långvarig',.7);book(d,610,320,.75);d.arc((225,165,535,550),200,155,fill=SOFT,width=6);label(d,(380,600),'kan vara handlingskraftig',27)
        elif i==7:
            clinic(d,175,285,1);arrow(d,(275,330),(450,330));person(d,570,285,.95);heart(d,570,460,.7);label(d,(380,590),'kan leva ett gott liv',30)
        elif i==9:
            d.rounded_rectangle((220,200,540,475),radius=25,outline=SOFT,width=6);d.rounded_rectangle((260,245,500,350),radius=10,outline=GOLD,width=5);label(d,(380,260),'°C',55);d.line((280,430,480,430),fill=LINE,width=8);label(d,(380,580),'tillfälligt sjuk',33)
        elif i==17:
            d.polygon([(120,430),(180,385),(235,255),(315,250),(365,355),(540,405),(625,440),(630,495),(120,495)],outline=SOFT,width=7);d.line((135,465,615,465),fill=GOLD,width=6)
            for x,y in[(270,295),(290,325),(320,355)]:d.line((x-30,y,x+35,y-15),fill=GOLD,width=6)
            for y,x in[(250,150),(300,110),(350,70)]:d.line((x,y,x+75,y),fill=LINE,width=6)
            label(d,(380,585),'regelbunden motion',31)
        elif i==10:
            d.line((95,345,660,345),fill=SOFT,width=7);arrow(d,(590,345),(660,345));clock(d,175,280,.9);folder(d,490,275,'kroniska',.8);label(d,(380,535),'långvariga eller bestående',29)
        elif i==11:
            person(d,380,315,.85)
            for x,y in[(160,230),(600,230),(160,505),(600,505)]:d.line((380,360,x,y),fill=LINE,width=5)
            plate(d,160,230,.7);house(d,600,200,.7);bed(d,160,500,.7);group(d,600,460,.42)
        elif i==14:
            magnify(d,165,300,1.05);clock(d,380,285,.7);clinic(d,595,280,.85);arrow(d,(265,340),(495,340));label(d,(380,570),'tidigt skede → behandling',29)
        elif i==15:
            heart(d,380,310,1.2)
            for x,y in[(170,245),(590,245),(170,500),(590,500)]:d.line((380,380,x,y),fill=LINE,width=5)
            plate(d,170,245,.6);ball(d,590,245,.65);bed(d,170,500,.65);house(d,590,460,.65)
        elif i==19:
            coins(d,380,285,4);arrow(d,(350,360),(210,465));arrow(d,(410,360),(565,465));plate(d,190,500,.7);house(d,570,460,.7);label(d,(380,595),'tillräcklig utkomst',30)
        elif i==22:
            d.ellipse((250,230,460,405),outline=SOFT,width=6);d.polygon([(410,300),(575,220),(515,390),(430,405)],outline=SOFT,width=6);d.polygon([(260,325),(130,250),(165,430),(285,405)],outline=SOFT,width=6);d.ellipse((385,225,450,285),fill=SOFT);d.line((448,260,505,275),fill=GOLD,width=5);d.line((500,278,555,330),fill=GOLD,width=5);label(d,(380,550),'fred i samhället',31)
        elif i==26:
            group(d,380,305,.75);shield(d,380,355,1.7);clinic(d,145,235,.65);book(d,615,250,.65);house(d,145,480,.6);plate(d,610,520,.6)
        elif i==27:
            book(d,335,340,1.9);cross(d,545,275,1);label(d,(380,580),'lagar som främjar hälsa',29)
        elif i==28:
            d.ellipse((195,185,565,555),outline=GOLD,width=18);d.rounded_rectangle((245,365,510,415),radius=7,outline=SOFT,width=7);d.rectangle((440,370,505,410),fill=SOFT)
            for x in[280,335,390]:d.arc((x-20,250,x+25,350),90,280,fill=SOFT,width=5)
            d.line((250,230,510,510),fill=GOLD,width=18)
        elif i==29:
            person(d,180,300,.9);person(d,590,300,.9);d.line((240,280,300,280),fill=SOFT,width=6)
            for j in range(4):d.arc((285+j*45,210+j*6,385+j*45,330+j*6),200,90,fill=GOLD,width=5)
            cross(d,180,505,.6);cross(d,590,505,.6);label(d,(380,600),'rökaren och andra',29)
        elif i==30:
            for x,y in[(150,245),(150,450),(330,350)]:paper(d,x,y,95,125);cross(d,x,y-25,.3)
            arrow(d,(405,350),(495,350));d.rounded_rectangle((515,200,660,515),radius=30,outline=SOFT,width=6)
            for y in[230,330,430]:d.arc((515,y,660,y+55),0,180,fill=GOLD,width=5)
            label(d,(380,600),'forskningsdata',31)
        elif i==31:
            d.rounded_rectangle((130,190,630,515),radius=20,outline=SOFT,width=6);paper(d,245,300,125,160);heart(d,510,300,.65);arrow(d,(335,330),(420,330));d.line((250,520,215,590),fill=SOFT,width=7);d.line((510,520,545,590),fill=SOFT,width=7);label(d,(380,560),'planera och genomföra',28)
        elif i==32:
            heart(d,200,285,1.1);folder(d,565,310,'cancersjukdomar',1);d.line((100,455,660,455),fill=LINE,width=5);label(d,(200,490),'hjärt- och kärlsjukdomar',24);label(d,(380,600),'programmen kan gälla',28)
        elif i==34:
            group(d,160,300,.75);group(d,600,300,.75);book(d,380,320,.9);d.arc((250,195,510,480),185,355,fill=GOLD,width=6);label(d,(200,535),'stöd',30);label(d,(570,535),'information',30)
        elif i==35:
            d.rounded_rectangle((130,175,630,420),radius=15,outline=SOFT,width=7);label(d,(380,255),'hälsokunskap',35);heart(d,250,330,.45);shield(d,505,325,.45)
            for x in[200,380,560]:person(d,x,495,.55)
        elif i==36:
            book(d,380,245,1.1);d.line((170,380,590,380),fill=GOLD,width=5)
            heart(d,170,470,.6);person(d,380,450,.65);shield(d,590,465,.65)
            for x,t in[(170,'hälsa'),(380,'välbefinnande'),(590,'säkerhet')]:label(d,(x,585),t,25)
        elif i==39:
            magnify(d,380,220,.85)
            for x,text in[(155,'livmoderhalscancer'),(380,'bröstcancer'),(605,'tarmcancer')]:
                d.line((380,285,x,365),fill=LINE,width=5);folder(d,x,445,text,.75)
        elif i==40:
            clock(d,155,290,1);arrow(d,(255,330),(450,330));heart(d,565,310,1);label(d,(155,490),'tidigt skede',27);label(d,(565,490),'bättre resultat',27)
        elif i==42:
            label(d,(380,150),'välfärdsområden · organisationer · företag',23)
            d.line((110,225,650,225),fill=GOLD,width=5)
            for x,y in[(190,350),(570,350),(190,540),(570,540)]:d.line((380,225,x,y-60),fill=LINE,width=4)
            clinic(d,190,305,.6);ball(d,570,350,.65);book(d,190,510,.65);person(d,570,490,.55)
            for x,y,t in[(190,420,'vård'),(570,420,'motion'),(190,615,'rådgivning'),(570,615,'kultur')]:label(d,(x,y),t,24)
        elif i==44:
            house(d,220,300,1.2);d.line((150,300,290,300),fill=GOLD,width=8);label(d,(220,470),'skolan',30);paper(d,550,330,180,230)
            for y in[275,325,375]:d.line((500,y,600,y),fill=GOLD,width=5)
            arrow(d,(335,350),(430,350));label(d,(380,590),'struktur i vardagen',29)
        elif i==47:
            group(d,200,315,.75);shield(d,540,315,1.25);d.line((315,335,430,335),fill=GOLD,width=5);coins(d,540,530,2);d.line((485,490,595,570),fill=GOLD,width=9);label(d,(380,610),'vaccinationsprogrammet',29)
        elif i==48:
            person(d,380,245,.85);arrow(d,(340,390),(205,485));arrow(d,(420,390),(555,485));d.ellipse((125,465,285,615),outline=SOFT,width=5);d.ellipse((475,465,635,615),outline=SOFT,width=5);label(d,(205,505),'ja',39);label(d,(555,505),'nej',39);label(d,(380,165),'frivilliga',32)
        elif i==49:
            for x in[215,380,545]:person(d,x,300,.72)
            shield(d,380,385,1.75);label(d,(380,595),'de flesta barn',32)
        elif i==50:
            record(d,210,320,'barnets tidigare vaccinationer',1.05);arrow(d,(350,350),(475,350));person(d,590,300,.9);cross(d,590,445,.5);label(d,(590,560),'hälsovårdare',26)
        elif i==51:
            labels=['polio','stelkramp','difteri','kikhosta','mässling','påssjuka'];coords=[(150,225),(380,200),(610,225),(150,505),(380,545),(610,505)];shield(d,380,365,.8)
            for (x,y),text in zip(coords,labels):d.line((380,365,x,y),fill=LINE,width=4);d.rounded_rectangle((x-88,y-35,x+88,y+45),radius=16,outline=SOFT,width=4);label(d,(x,y-14),text,24)
            label(d,(380,615),'bland annat',27)
        elif i==53:
            d.rounded_rectangle((145,175,615,265),radius=20,outline=GOLD,width=5);label(d,(380,197),'riskgrupp för influensa',30);arrow(d,(380,285),(380,365));shield(d,380,435,.9);person(d,180,420,.8);person(d,590,455,.5);label(d,(180,570),'vuxna',27);label(d,(590,570),'barn',27);label(d,(380,620),'kan få avgiftsfri vaccination',25)
        elif i==55:
            record(d,190,315,'dina vaccinationer',1);record(d,570,315,'programmet',1);magnify(d,380,460,.8);d.line((300,320,465,320),fill=LINE,width=5);label(d,(380,610),'vilka saknas?',30)
        elif i==56:
            d.rounded_rectangle((75,185,335,330),radius=20,outline=SOFT,width=5);d.rounded_rectangle((425,185,685,330),radius=20,outline=SOFT,width=5);label(d,(205,215),'inte fått alla vaccinationer',24);label(d,(555,215),'stadigvarande flytt',24);label(d,(380,245),'och',27);label(d,(380,145),'OM',28);arrow(d,(205,355),(330,465));arrow(d,(555,355),(430,465));shield(d,380,535,.8);label(d,(380,620),'kan få dem kostnadsfritt',27)
        elif i==57:
            label(d,(380,160),'OM ansökt om asyl eller tillfälligt skydd',24);d.line((110,220,650,220),fill=GOLD,width=5);person(d,215,340,.55);person(d,555,320,.9);d.ellipse((550,335,615,405),outline=SOFT,width=5);label(d,(215,500),'minderårig',27);label(d,(555,500),'gravid',27);label(d,(380,330),'eller',28);arrow(d,(215,535),(330,600));arrow(d,(555,535),(430,600));shield(d,380,600,.45)
        else:raise ValueError('Missing explicit visual composition: '+str(i))
        im.save(dest);asset=dict(asset_id=key,kind='foreground',visual_type='diagram',files=[info(dest)],creator='Homebrew video studio',reuse_terms='Original schematic artwork under repository MIT license; source text retains its publisher terms.',required_credits='Original source-based public-health illustrations: Homebrew video studio. Source text attribution in sources.yaml and CREDITS.md.',relevance_verification=plans[i]['request']+' Individually composed source relationship/object illustration; no invented diagnosis, numerical dataset, dose or eligibility rule.',creation_method=dict(tool=str(Path(__file__).relative_to(ROOT)),source_sentence_ids=[row['sentence_id']]))
    assets.append(asset);by_index[i]=asset
for i,row in enumerate(script['sentences']):
    j=aliases.get(i,i);a=by_index[j];row['asset_ids']=['episode_background',a['asset_id']];row['render_image']=a['files'][0]['path'];row['render_caption']=False
    if i!=j:
        a.setdefault('creation_method',{}).setdefault('source_sentence_ids',[script['sentences'][j]['sentence_id']]).append(row['sentence_id']);row['visual_cue']='Retain the preceding/paired relevant picture across this source continuation: '+plans[i]['request']
requests=script['asset_requests'][:3]
for i,a in by_index.items():requests.append(dict(id=a['asset_id'],kind='foreground',description=a['relevance_verification'],fallback='Accurate source-specific pictorial explanation; omit only with documented relevance/license reason.'))
script['asset_requests']=requests;script['render']['credits']=script['render']['credits'][:2]
for j in range(0,len(screen),2):script['render']['credits'].append(dict(heading='Förgrundsbilder · Изображения',paragraphs=screen[j:j+2]+['Original schematisk grafik: Homebrew video studio.','Fullständiga källor och licenser i CREDITS.md.']))
for decision in script['episode_decisions']:
    if decision['id']=='visuals':decision['decision']='Relevant foreground pictures cover every body sentence. Fifty-three distinct pictures for58slides; five closely related source continuations deliberately retain their relevant picture. Photographs show concrete objects/settings; individually composed diagrams show source relationships without fabricated data, anatomy or eligibility rules.'
(EP/'script.yaml').write_text(yaml.safe_dump(script,allow_unicode=True,sort_keys=False,width=100));(EP/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');(EP/'foreground-downloads.json').write_text(json.dumps(downloads,ensure_ascii=False,indent=2)+'\n');(EP/'prepare_assets.py').write_text((ROOT/'studio/episodes/hb-c10-utkomststod/prepare_assets.py').read_text());print('Prepared',len(assets),'distinct pictures for58sentences;',sum(a['visual_type']=='photograph' for a in assets),'distinct photographs.')
