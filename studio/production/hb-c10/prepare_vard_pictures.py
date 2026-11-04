"""Compose varied exact-source public/private healthcare explanations and photographs."""
from pathlib import Path
import json,yaml,hashlib,re,math
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parents[3];SID='hb-c10-vard';E=R/'studio/episodes'/SID;M=R/'studio/media'/SID;O=M/'pictures';O.mkdir(parents=True,exist_ok=True)
ns={'__file__':str(Path(__file__))};exec(compile((R/'studio/production/hb-c10/author_utkomststod.py').read_text().split('specs=')[0],'care-primitives','exec'),ns);common=(R/'studio/production/hb-c10/prepare_folkhalsa_pictures.py').read_text();exec(compile(common[common.index('def heart'):common.index('photos=json.loads')],'medical-objects','exec'),ns)
canvas,label,house,person,coins,paper,arrow,heart,shield,cross,book,clinic,clock,group,magnify,record,folder=[ns[k] for k in ['canvas','label','house','person','coins','paper','arrow','heart','shield','cross','book','clinic','clock','group','magnify','record','folder']];FG,SOFT,GOLD,LINE,PANEL,BG=[ns[k] for k in ['FG','SOFT','GOLD','LINE','PANEL','BG']]
def info(p):return dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def envelope(d,x,y,s=1):
    d.rectangle((x-85*s,y-55*s,x+85*s,y+55*s),outline=SOFT,width=5);d.line([(x-85*s,y-55*s),(x,y+10*s),(x+85*s,y-55*s)],fill=GOLD,width=5)
def phone(d,x,y,s=1):
    d.rounded_rectangle((x-60*s,y-100*s,x+60*s,y+100*s),radius=15,outline=SOFT,width=5);d.rectangle((x-40*s,y-70*s,x+40*s,y+55*s),outline=LINE,width=4);d.ellipse((x-9*s,y+73*s,x+9*s,y+91*s),fill=GOLD)
def card(d,x,y,s=1):
    d.rounded_rectangle((x-100*s,y-65*s,x+100*s,y+65*s),radius=13,outline=SOFT,width=5);cross(d,x-55*s,y,.45*s);label(d,(x+25*s,y-15*s),'FPA',int(30*s));d.line((x-70*s,y+45*s,x+70*s,y+45*s),fill=LINE,width=4)
def no(d,x,y,r):d.ellipse((x-r,y-r,x+r,y+r),outline=GOLD,width=6);d.line((x-r*.7,y-r*.7,x+r*.7,y+r*.7),fill=GOLD,width=7)
def calendar(d,x,y,s=1):
    d.rounded_rectangle((x-90*s,y-90*s,x+90*s,y+90*s),radius=12,outline=SOFT,width=5);d.line((x-90*s,y-40*s,x+90*s,y-40*s),fill=GOLD,width=5)
    for xx in[-50,0,50]:
        for yy in[-5,40]:d.rounded_rectangle((x+(xx-12)*s,y+(yy-12)*s,x+(xx+12)*s,y+(yy+12)*s),radius=3,outline=LINE,width=3)
def doctor(d,x,y,s=1):person(d,x,y,s);cross(d,x+55*s,y+45*s,.35*s)
def hardhat(d,x,y,s=1):
    d.arc((x-65*s,y-60*s,x+65*s,y+45*s),180,360,fill=GOLD,width=7);d.line((x-85*s,y-5*s,x+85*s,y-5*s),fill=SOFT,width=7);d.line((x,y-60*s,x,y-12*s),fill=GOLD,width=6)
photos=json.loads((E/'selected-photos.json').read_text());credit_overrides=json.loads((E/'credit-author-overrides.json').read_text()) if (E/'credit-author-overrides.json').exists() else {};old=json.loads((E/'retained-photo-assets.json').read_text());script=yaml.safe_load((E/'script.yaml').read_text());plans=json.loads((E/'picture-plan.json').read_text());assets=[];downloads=[];screen=[];by_index={};aliases={43:20}
for i,row in enumerate(script['sentences']):
    if i in aliases:continue
    key=f'picture-{i+1:03}';dest=O/f'sentence-{i+1:02}.png'
    if str(i) in photos or str(i) in old:
        if str(i) in photos:
            p=photos[str(i)];pi=p['imageinfo'];meta=pi['extmetadata'];clean=lambda k:re.sub('<[^>]+>','',meta.get(k,{}).get('value','')).strip();raw=R/p['path'];creator=credit_overrides.get(pi['descriptionurl'],{}).get('creator',clean('Artist'));terms=clean('LicenseShortName')+' '+clean('LicenseUrl');source=pi['descriptionurl'];credit=p['title'].removeprefix('File:')+' — '+creator+'. '+terms+'. '+source+'. Complete photograph proportionally resized and letterboxed; original terms retained.';context=p['context'];url=p['download_url'];screen.append(p['title'].removeprefix('File:')+' — '+creator+' · '+clean('LicenseShortName'))
        else:
            p=old[str(i)];a=p['asset_record'];raw=R/p['path'];creator=a['creator'];terms=a['reuse_terms'];source=a['source_url'];credit=a['required_credits'];context=p['context'];url=p['url'];screen.append(__import__('urllib.parse',fromlist=['unquote']).unquote(source.rsplit('/wiki/',1)[-1]).replace('_',' ').removeprefix('File:')+' — '+creator+' · '+terms.split('https:')[0])
        image=ImageOps.exif_transpose(Image.open(raw)).convert('RGB');image.thumbnail((760,720),Image.Resampling.LANCZOS);im=Image.new('RGB',(760,720),BG);im.paste(image,((760-image.width)//2,(720-image.height)//2));im.save(dest);downloads.append(dict(**info(raw),url=url));a=dict(asset_id=key,kind='foreground',visual_type='photograph',files=[info(dest)],creator=creator,reuse_terms=terms,source_url=source,required_credits=credit,relevance_verification=context,creation_method=dict(tool=str(Path(__file__).relative_to(R)),transform='Complete source photograph proportionally resized,EXIF orientation respected,letterboxed.'))
    else:
        im,d=canvas(plans[i]['title'])
        if i==1:
            clinic(d,190,260,1);clinic(d,570,260,1);coins(d,190,500,2);no(d,190,490,75);coins(d,570,500,2);d.line((380,190,380,585),fill=LINE,width=5);label(d,(190,590),'avgiftsfria',30);label(d,(570,590),'klientavgift',30)
        elif i==2:
            coins(d,170,315,4);label(d,(170,440),'skattepengar',30);arrow(d,(270,350),(455,350));clinic(d,575,280,1.1);label(d,(575,465),'hälsovårdstjänster',27);label(d,(380,605),'statens finansiering',28)
        elif i==3:
            clinic(d,150,230,.8);clock(d,385,250,.8);envelope(d,600,290,.8);arrow(d,(245,275),(300,275));arrow(d,(465,275),(505,275));person(d,600,490,.6);d.line((600,365,600,420),fill=GOLD,width=5);label(d,(380,600),'fakturan kommer i efterhand',28)
        elif i==4:
            d.rounded_rectangle((230,175,530,310),radius=20,outline=GOLD,width=5);label(d,(380,205),'välfärdsområdet',31)
            for x in[160,380,600]:d.line((380,315,x,395),fill=LINE,width=5);clinic(d,x,450,.8)
            label(d,(380,605),'ordnar offentliga tjänster',29)
        elif i==5:
            label(d,(155,255),'21',95)
            for j in range(21):
                x=320+j%7*55;y=235+j//7*90;d.ellipse((x-12,y-12,x+12,y+12),outline=SOFT,width=4)
            d.line((100,510,660,510),fill=LINE,width=5);label(d,(380,565),'välfärdsområden',35);label(d,(380,615),'baserade på landskapen',25)
        elif i==7:
            clinic(d,380,270,1.15)
            for x,y in[(165,480),(380,480),(595,480)]:d.line((380,385,x,y-60),fill=LINE,width=5)
            doctor(d,165,475,.6);folder(d,380,480,'vård',.7);group(d,595,475,.5);label(d,(380,610),'till exempel följande tjänster',27)
        elif i==11:
            d.ellipse((100,200,330,435),outline=LINE,width=5);d.ellipse((430,200,660,435),outline=LINE,width=5);person(d,210,255,.55);heart(d,210,385,.55);person(d,545,255,.55);shield(d,545,380,.55);d.arc((245,420,515,545),0,180,fill=GOLD,width=5);label(d,(210,510),'psykiatri',28);label(d,(545,510),'missbrukarvård',27);label(d,(380,610),'vård och stöd',28)
        elif i==12:
            person(d,180,300,.85);person(d,570,300,.85);paper(d,380,465,170,150);d.rounded_rectangle((245,180,515,290),radius=25,outline=GOLD,width=5);d.polygon([(315,290),(300,330),(355,290)],outline=GOLD,width=4);d.line((250,410,510,410),fill=LINE,width=5);label(d,(380,590),'socialarbete och handledning',28)
        elif i==17:
            label(d,(380,155),'flyttat till eller arbetar i Finland',27);house(d,175,280,.9);hardhat(d,580,340,.8);label(d,(380,320),'eller',27);arrow(d,(175,425),(290,500));arrow(d,(580,425),(470,500));card(d,380,540,.8);label(d,(380,615),'kan ansöka om FPA-kort',28)
        elif i==18:
            card(d,165,330,.95);arrow(d,(280,345),(425,345));d.rectangle((455,205,670,460),outline=LINE,width=5);cross(d,560,265,.65);doctor(d,560,375,.48);label(d,(560,500),'apotek',26);label(d,(380,550),'de flesta privata läkarstationer',25);label(d,(380,605),'visa kortet → direktersättning',27)
        elif i==19:
            for x,text in[(150,'priset'),(380,'ersättning'),(610,'självrisk')]:paper(d,x,325,145,190);label(d,(x,445),text,28)
            d.line((255,325,290,325),fill=GOLD,width=6);d.line((480,315,520,315),fill=GOLD,width=5);d.line((480,335,520,335),fill=GOLD,width=5);label(d,(380,560),'den ersättning kunden har rätt till',25);label(d,(380,605),'kunden betalar självrisken',28)
        elif i==20:
            card(d,180,260,.8);no(d,180,260,105);clock(d,570,260,.9);paper(d,180,510,150,170);envelope(d,550,510,.9);arrow(d,(295,510),(440,510));label(d,(380,615),'kan ansöka i efterhand',29)
        elif i==22:
            phone(d,160,310,.95);arrow(d,(250,330),(350,330));person(d,430,285,.85);d.line((430,460,610,405),fill=LINE,width=5);d.line((430,460,610,535),fill=LINE,width=5);doctor(d,610,320,.55);person(d,610,500,.55);label(d,(380,605),'bedömning → rätt yrkesperson',27)
        elif i==24:
            clinic(d,380,190,.75);d.line((380,300,195,385),fill=LINE,width=5);d.line((380,300,575,385),fill=LINE,width=5);person(d,195,410,.8);person(d,575,410,.8);label(d,(195,575),'sjukskötare',29);label(d,(575,575),'hälsovårdare',29);label(d,(380,625),'vanligtvis båda yrkena',26)
        elif i==25:
            clock(d,200,285,.95);cross(d,200,435,.75);shield(d,565,310,1.15);heart(d,565,315,.6);d.line((380,185,380,550),fill=LINE,width=4);label(d,(200,535),'mer akut',28);label(d,(565,535),'mer förebyggande',25);label(d,(200,600),'sjukskötare',26);label(d,(565,600),'hälsovårdare',26)
        elif i==26:
            calendar(d,380,300,1.6);d.ellipse((270,335,325,390),outline=GOLD,width=6);d.ellipse((430,335,485,390),outline=SOFT,width=6);person(d,180,480,.55);doctor(d,580,480,.55);d.line((215,460,295,395),fill=GOLD,width=5);d.line((545,460,455,395),fill=LINE,width=5);label(d,(380,600),'ofta snabbare till vårdaren',28)
        elif i==27:
            person(d,160,300,.85);doctor(d,590,300,.85);d.rounded_rectangle((285,215,475,405),radius=18,outline=GOLD,width=5);label(d,(380,245),'OM läkare',25);label(d,(380,295),'behövs',29);arrow(d,(240,350),(285,350));arrow(d,(475,350),(520,350));label(d,(380,585),'vårdaren skickar vidare',29)
        elif i==28:
            label(d,(380,160),'OM specialist behövs',31);calendar(d,175,355,1);doctor(d,565,310,1);arrow(d,(290,355),(455,355));label(d,(175,515),'boka först',29);label(d,(565,515),'allmänläkare',29)
        elif i==29:
            paper(d,380,355,315,365);label(d,(380,215),'REMISS',43);cross(d,380,320,.9);d.line((285,435,475,435),fill=GOLD,width=5);label(d,(380,560),'allmänläkarens bedömning',28);label(d,(380,610),'vid behov till specialist',27)
        elif i==30:
            person(d,160,300,.9);calendar(d,565,355,1.2);arrow(d,(250,355),(455,355));d.line((365,255,365,450),fill=GOLD,width=10);no(d,365,350,100);label(d,(565,530),'specialist',29);label(d,(380,610),'inte boka själv',32)
        elif i==32:
            clock(d,170,295,1);calendar(d,590,330,1.1);d.line((290,330,460,330),fill=LINE,width=5);d.line((365,240,365,425),fill=GOLD,width=9);clinic(d,380,480,.7);label(d,(170,490),'omedelbar vård',26);label(d,(590,490),'kan inte vänta',26);label(d,(380,615),'till följande vardag',27)
        elif i==36:
            for x in[155,335,515]:person(d,x,230,.55)
            d.line((90,385,650,385),fill=LINE,width=6);d.polygon([(630,365),(670,385),(630,405)],fill=LINE);d.line((150,480,600,480),fill=GOLD,width=6);d.line((150,465,150,495),fill=GOLD,width=5);label(d,(380,550),'brådskande behov styr ordningen',28);label(d,(380,610),'ankomstordning avgör inte',27)
        elif i==37:
            doctor(d,160,295,1);paper(d,530,355,215,290)
            for y in[290,355,420]:d.line((470,y,590,y),fill=GOLD,width=5)
            arrow(d,(255,350),(390,350));d.arc((560,255,665,440),270,90,fill=SOFT,width=5);label(d,(380,605),'läkaren bestämmer ordningen',28)
        elif i==39:
            clock(d,380,275,1.3);d.line((380,375,180,455),fill=GOLD,width=5);d.line((380,375,580,455),fill=LINE,width=5);doctor(d,180,455,.65);clinic(d,580,440,.7);label(d,(180,580),'privatläkare',27);label(d,(580,580),'offentlig vård',27);label(d,(380,165),'ofta snabbare tid privat',30)
        elif i==40:
            paper(d,255,330,230,290);coins(d,560,325,3);arrow(d,(560,435),(560,220));label(d,(255,505),'privata tjänster',29);label(d,(380,585),'mycket dyrare än offentliga',29)
        elif i==41:
            doctor(d,170,310,.9);house(d,580,280,1.25);arrow(d,(265,350),(440,350));coins(d,580,535,2);label(d,(180,490),'en del privatläkare',25);label(d,(380,610),'hembesök kan vara dyra',28)
        elif i==42:
            card(d,165,280,.9);label(d,(165,430),'OM FPA-kort',27);paper(d,580,300,165,210);label(d,(580,450),'privatläkaravgift',26);arrow(d,(515,520),(265,520));label(d,(380,575),'kan få tillbaka en liten del',28)
        elif i==45:
            hardhat(d,185,280,1.1);heart(d,185,440,.75);folder(d,560,300,'hälsokontroller',1);magnify(d,560,510,.6);d.line((290,350,430,350),fill=LINE,width=5);label(d,(380,610),'arbetsrelaterade symtom',29)
        elif i==46:
            d.rounded_rectangle((240,175,520,275),radius=20,outline=GOLD,width=5);label(d,(380,200),'kan ordnas',31);d.line((380,280,180,375),fill=LINE,width=5);d.line((380,280,580,375),fill=LINE,width=5);clinic(d,180,425,.9);d.rectangle((510,380,650,515),outline=SOFT,width=6);cross(d,580,445,.6);label(d,(180,590),'vårdcentral',28);label(d,(580,590),'privat läkarcentral',25);label(d,(380,410),'eller',26)
        elif i==47:
            label(d,(380,155),'OFTA KAN tjänsterna omfatta',28)
            for x,y in[(185,280),(575,280),(185,505),(575,505)]:d.rounded_rectangle((x-115,y-75,x+115,y+85),radius=20,outline=LINE,width=4)
            folder(d,185,255,'hälsokontroller',.55);doctor(d,575,245,.55);label(d,(575,330),'läkare',24);person(d,185,475,.55);d.arc((135,420,235,500),180,360,fill=GOLD,width=4);person(d,575,475,.55);d.line((600,505,655,505),fill=GOLD,width=6);d.ellipse((642,492,668,518),outline=GOLD,width=4);label(d,(185,605),'psykolog',26);label(d,(575,605),'fysioterapeut',26)
        elif i==48:
            book(d,210,320,1.35);shield(d,555,335,1.45);cross(d,555,335,.8);label(d,(380,590),'offentlig vård · vårdgaranti',29)
        elif i==49:
            house(d,160,235,.9);book(d,390,270,.85);clock(d,610,280,.8);label(d,(180,365),'permanent bosatt',27);d.line((160,420,610,420),fill=LINE,width=5);clinic(d,390,485,.7);label(d,(380,610),'icke-brådskande · rimlig tid',28)
        elif i==50:
            clock(d,150,310,1.1);arrow(d,(255,350),(450,350));clinic(d,585,290,1.05);label(d,(150,510),'akut vård',30);label(d,(585,510),'genast',35);label(d,(380,600),'när akut vård behövs',28)
        else:raise ValueError('Missing explicit source-specific care visual '+str(i))
        im.save(dest);a=dict(asset_id=key,kind='foreground',visual_type='diagram',files=[info(dest)],creator='Homebrew video studio',reuse_terms='Original schematic artwork under repository MIT license; archived source text retains publisher terms.',required_credits='Original source-based healthcare illustrations: Homebrew video studio; archived source wording credited in sources.yaml and CREDITS.md.',relevance_verification=plans[i]['request']+' Individually composed exact-source explanation. Qualifiers remain visible; no invented deadline,regional border,price,percentage,triage score,clinical procedure or entitlement.',creation_method=dict(tool=str(Path(__file__).relative_to(R)),source_sentence_ids=[row['sentence_id']]))
    assets.append(a);by_index[i]=a
for i,row in enumerate(script['sentences']):
    a=by_index[aliases.get(i,i)];row.update(asset_ids=['episode_background',a['asset_id']],render_image=a['files'][0]['path'],render_caption=False)
    if i in aliases:a['creation_method'].setdefault('source_sentence_ids',[script['sentences'][aliases[i]]['sentence_id']]).append(row['sentence_id']);row['visual_cue']='The same exact-source no-card/afterwards application mechanism retains its meaningful pictorial explanation; '+plans[i]['request']
script['asset_requests']=script['asset_requests'][:3]+[dict(id=a['asset_id'],kind='foreground',description=a['relevance_verification'],fallback='Accurate useful source-specific pictorial alternative; document omission after reasonable research if necessary.') for a in assets];script['render']['credits']=script['render']['credits'][:2]
for j in range(0,len(screen),2):script['render']['credits'].append(dict(heading='Förgrundsbilder · Изображения',paragraphs=screen[j:j+2]+['Original schematisk grafik: Homebrew video studio.','Fullständiga källor och licenser i CREDITS.md.']))
for decision in script['episode_decisions']:
    if decision['id']=='visuals':decision['decision']='Relevant pictures cover every source sentence:17 actual licensed photographs and33 individually composed source diagrams;50distinct sources for51slides. The repeated no-card reimbursement-application mechanism deliberately retains its meaningful picture twice. No cosmetic template variants or invented clinical/legal/numerical rules.'
(E/'script.yaml').write_text(yaml.safe_dump(script,allow_unicode=True,sort_keys=False,width=100));(E/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');(E/'foreground-downloads.json').write_text(json.dumps(downloads,ensure_ascii=False,indent=2)+'\n');(E/'prepare_assets.py').write_text((R/'studio/episodes/hb-c10-utkomststod/prepare_assets.py').read_text());print('Prepared',len(assets),'distinct pictures;',len(screen),'photographs for51slides.')
