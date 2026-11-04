"""Compose source-specific leisure participation,public spaces and qualified youth-work rules."""
from pathlib import Path
import json,yaml,hashlib,re,math
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parents[3];SID='hb-c11-fritid';E=R/'studio/episodes'/SID;M=R/'studio/media'/SID;O=M/'pictures';O.mkdir(parents=True,exist_ok=True)
ns={'__file__':str(Path(__file__))};exec(compile((R/'studio/production/hb-c10/author_utkomststod.py').read_text().split('specs=')[0],'access-primitives','exec'),ns);code=(R/'studio/production/hb-c10/prepare_folkhalsa_pictures.py').read_text();exec(compile(code[code.index('def heart'):code.index('photos=json.loads')],'health-objects','exec'),ns);code=(R/'studio/production/hb-c10/prepare_vard_pictures.py').read_text();exec(compile(code[code.index('def envelope'):code.index('photos=json.loads',code.index('def envelope'))],'care-objects','exec'),ns)
ns.update(BG='#243c32',PANEL='#2d4d40',FG='#faf3e8',SOFT='#c5dfce',GOLD='#e3c58c',LINE='#4d7560')
canvas,label,house,person,coins,paper,arrow,heart,shield,cross,book,clinic,clock,group,magnify,record,folder,envelope,phone,card,no,calendar,doctor,hardhat=[ns[k] for k in ['canvas','label','house','person','coins','paper','arrow','heart','shield','cross','book','clinic','clock','group','magnify','record','folder','envelope','phone','card','no','calendar','doctor','hardhat']];FG,SOFT,GOLD,LINE,PANEL,BG=[ns[k] for k in ['FG','SOFT','GOLD','LINE','PANEL','BG']]
def info(p):return dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def globe(d,x,y,s=1):
    d.ellipse((x-75*s,y-75*s,x+75*s,y+75*s),outline=SOFT,width=5);d.ellipse((x-35*s,y-75*s,x+35*s,y+75*s),outline=GOLD,width=4);d.line((x-75*s,y,x+75*s,y),fill=GOLD,width=4)
def librarycard(d,x,y,s=1):
    d.rounded_rectangle((x-105*s,y-65*s,x+105*s,y+65*s),radius=14,outline=SOFT,width=5);book(d,x-35*s,y,.42*s);d.line((x+20*s,y-15*s,x+75*s,y-15*s),fill=LINE,width=5);d.line((x+20*s,y+15*s,x+75*s,y+15*s),fill=GOLD,width=5)
ball=ns['ball']
def guitar(d,x,y,s=1):
    d.ellipse((x-45*s,y-5*s,x+45*s,y+75*s),outline=SOFT,width=5);d.ellipse((x-35*s,y-50*s,x+35*s,y+20*s),outline=SOFT,width=5);d.rectangle((x-9*s,y-135*s,x+9*s,y-25*s),outline=GOLD,width=4);d.ellipse((x-12*s,y-13*s,x+12*s,y+11*s),outline=GOLD,width=4);d.line((x,y-125*s,x,y+55*s),fill=GOLD,width=2)
def pool(d,x,y,s=1):
    d.rectangle((x-90*s,y-65*s,x+90*s,y+65*s),outline=SOFT,width=5)
    for yy in [-30,10,45]:
        d.arc((x-75*s,y+(yy-12)*s,x-25*s,y+(yy+12)*s),0,180,fill=GOLD,width=4);d.arc((x-25*s,y+(yy-12)*s,x+25*s,y+(yy+12)*s),180,360,fill=GOLD,width=4);d.arc((x+25*s,y+(yy-12)*s,x+75*s,y+(yy+12)*s),0,180,fill=GOLD,width=4)
def sauna(d,x,y,s=1):
    d.rectangle((x-105*s,y-110*s,x+105*s,y+110*s),outline=LINE,width=5);d.line((x-75*s,y+35*s,x+20*s,y+35*s,x+20*s,y+80*s),fill=SOFT,width=6);d.rectangle((x+45*s,y-5*s,x+80*s,y+75*s),outline=GOLD,width=4)
    for xx in [45,65,85]:d.arc((x+(xx-15)*s,y-70*s,x+(xx+5)*s,y-10*s),90,270,fill=GOLD,width=4)
def game(d,x,y,s=1):
    d.rectangle((x-70*s,y-70*s,x+70*s,y+70*s),outline=SOFT,width=5)
    for j in [-1,0,1]:d.line((x-70*s,y+j*35*s,x+70*s,y+j*35*s),fill=LINE,width=3);d.line((x+j*35*s,y-70*s,x+j*35*s,y+70*s),fill=LINE,width=3)
    for xx,yy in [(-35,-35),(35,35),(0,35)]:d.ellipse((x+(xx-9)*s,y+(yy-9)*s,x+(xx+9)*s,y+(yy+9)*s),fill=GOLD)
photos=json.loads((E/'selected-photos.json').read_text());old=json.loads((E/'retained-photo-assets.json').read_text());script=yaml.safe_load((E/'script.yaml').read_text());plans=json.loads((E/'picture-plan.json').read_text());assets=[];downloads=[];screen=[];by_index={};aliases={26:25,31:30}
for i,row in enumerate(script['sentences']):
    if i in aliases:continue
    key=f'picture-{i+1:03}';dest=O/f'sentence-{i+1:02}.png'
    if str(i) in photos or str(i) in old:
        if str(i) in photos:
            p=photos[str(i)];pi=p['imageinfo'];meta=pi['extmetadata'];clean=lambda k:re.sub('<[^>]+>','',meta.get(k,{}).get('value','')).strip();raw=R/p['path'];creator=clean('Artist');terms=clean('LicenseShortName')+' '+clean('LicenseUrl');source=pi['descriptionurl'];credit=p['title'].removeprefix('File:')+' — '+creator+'. '+terms+'. '+source+'. Complete photograph proportionally resized and letterboxed; original terms retained.';context=p['context'];url=p['download_url'];screen.append(p['title'].removeprefix('File:')+' — '+creator+' · '+clean('LicenseShortName'))
        else:
            p=old[str(i)];a=p['asset_record'];raw=R/p['path'];creator=a['creator'];terms=a['reuse_terms'];source=a['source_url'];credit=a['required_credits'];context=p['context'];url=p['url'];screen.append('HTC Keilaniemi office buildings — '+creator+' · '+terms.split('https:')[0])
        image=ImageOps.exif_transpose(Image.open(raw)).convert('RGB');image.thumbnail((760,720),Image.Resampling.LANCZOS);im=Image.new('RGB',(760,720),BG);im.paste(image,((760-image.width)//2,(720-image.height)//2));im.save(dest);downloads.append(dict(**info(raw),url=url));a=dict(asset_id=key,kind='foreground',visual_type='photograph',files=[info(dest)],creator=creator,reuse_terms=terms,source_url=source,required_credits=credit,relevance_verification=context,creation_method=dict(tool=str(Path(__file__).relative_to(R)),transform='Complete source photograph proportionally resized,EXIF orientation respected,letterboxed.'))
    else:
        im,d=canvas(plans[i]['title'])
        if i==2:
            group(d,205,300,.8);person(d,570,290,.85);d.line((380,180,380,545),fill=LINE,width=5);ball(d,205,470,.7);guitar(d,570,470,.65);label(d,(205,585),'organiserad verksamhet',25);label(d,(570,585),'på egen hand',29)
        elif i==6:
            label(d,(380,155),'officiellt mål',33)
            for x in [165,380,595]:person(d,x,300,.6);d.line((x,405,x,455),fill=GOLD,width=5)
            ball(d,165,520,.65);guitar(d,380,520,.65);book(d,595,520,.65);label(d,(380,615),'alla barn och unga: minst en rolig hobby',24)
        elif i==7:
            house(d,175,255,1.15);book(d,175,440,.65);clock(d,380,315,.85);arrow(d,(280,335),(300,335));arrow(d,(460,335),(510,335));ball(d,600,335,.85);coins(d,600,535,2);no(d,600,525,60);label(d,(380,610),'kostnadsfritt i samband med skoldagen',25)
        elif i==9:
            calendar(d,210,315,1.3);clock(d,565,315,1.05);d.line((380,190,380,460),fill=LINE,width=4);coins(d,380,550,3);label(d,(380,450),'andra tider',31);label(d,(380,615),'kan vara avgiftsbelagda',30)
        elif i==14:
            for x,y in [(220,265),(540,265),(380,435)]:person(d,x,y,.65)
            d.ellipse((160,205,600,570),outline=LINE,width=5);book(d,380,325,.65);label(d,(380,615),'föreningsverksamhet',32)
        elif i==16:
            house(d,380,190,.9);arrow(d,(335,320),(200,405));arrow(d,(425,320),(570,405));coins(d,200,480,1);coins(d,570,480,2);no(d,570,465,75);label(d,(200,585),'förmånligt',31);label(d,(570,585),'kostnadsfritt',30);label(d,(380,360),'eller',28)
        elif i==21:
            label(d,(380,145),'i allmänhet sänkta priser',29)
            for x,y,t in [(180,270,'barn'),(570,270,'pensionärer'),(180,460,'studerande'),(570,460,'arbetslösa')]:
                person(d,x,y,.45);label(d,(x,y+85),t,27)
            coins(d,380,395,2);d.line((300,395,240,330),fill=LINE,width=4);d.line((460,395,510,330),fill=LINE,width=4);d.line((300,395,240,480),fill=LINE,width=4);d.line((460,395,510,480),fill=LINE,width=4);label(d,(380,615),'kommunernas motionstjänster',27)
        elif i==22:
            pool(d,210,320,1.25);calendar(d,565,315,1.05);d.rounded_rectangle((105,480,655,585),radius=20,outline=GOLD,width=4);label(d,(380,495),'vissa tider endast för kvinnor',28);label(d,(380,165),'i en del simhallar',31)
        elif i==24:
            for x,t in [(205,'män'),(555,'kvinnor')]:
                sauna(d,x,320,.9);label(d,(x,485),t,32)
            d.line((380,190,380,540),fill=LINE,width=5);label(d,(380,565),'separata bastur',32);label(d,(380,615),'vanligtvis badar man naken',28)
        elif i==27:
            d.ellipse((80,200,330,495),outline=LINE,width=4);d.ellipse((430,200,680,495),outline=LINE,width=4);group(d,205,325,.65);group(d,555,325,.65);label(d,(205,535),'klubbar',33);label(d,(555,535),'fria grupper',30);label(d,(380,615),'till exempel',27)
        elif i==35:
            group(d,190,280,.7);group(d,575,280,.7);coins(d,190,490,3);coins(d,575,490,2);no(d,575,480,80);d.line((380,190,380,560),fill=LINE,width=4);label(d,(190,595),'avgiftsbelagda',28);label(d,(575,595),'gratis',31);label(d,(380,155),'en del hobbyer',31)
        elif i==39:
            d.rounded_rectangle((90,180,670,560),radius=18,outline=LINE,width=5);d.rectangle((160,345,440,395),outline=SOFT,width=5);d.line((185,395,185,490),fill=SOFT,width=5);d.line((415,395,415,490),fill=SOFT,width=5);book(d,290,310,.6);game(d,565,340,.7);guitar(d,560,485,.55);label(d,(380,615),'tid och aktiviteter på ungdomsgården',25)
        elif i==40:
            person(d,180,280,1);group(d,555,365,.8);d.rounded_rectangle((95,465,285,550),radius=15,outline=GOLD,width=4);label(d,(190,490),'ledd',31);arrow(d,(300,350),(430,350));label(d,(380,155),'ALLTID också',32);label(d,(380,615),'ledd verksamhet på ungdomsgården',26)
        elif i==41:
            group(d,245,320,.95);coins(d,565,355,3);no(d,565,340,105);label(d,(380,525),'största delen',35);label(d,(380,585),'av verksamheten är gratis',29)
        elif i==42:
            person(d,210,300,1.05);label(d,(210,520),'alltid en vuxen',29);d.line((390,200,390,550),fill=LINE,width=5);paper(d,575,315,180,220);label(d,(575,470),'oftast kommunens',24);label(d,(575,510),'ungdomsarbetare',24);label(d,(575,550),'eller ungdomsledare',23)
        elif i==43:
            for x in [165,380,595]:house(d,x,260,.7);calendar(d,x,470,.55);label(d,(x,445),'?',35)
            label(d,(380,615),'åldersgränserna varierar',31)
        elif i==44:
            group(d,165,330,.8);d.rounded_rectangle((75,155,290,240),radius=20,outline=GOLD,width=4);d.polygon([(185,240),(180,270),(225,240)],outline=GOLD,width=4);label(d,(182,175),'önskemål',29);arrow(d,(300,350),(440,350));game(d,560,300,.75);ball(d,560,495,.65);label(d,(380,615),'unga påverkar innehållet',30)
        elif i==45:
            phone(d,175,330,.95);arrow(d,(275,350),(430,350));house(d,565,285,1.1);label(d,(565,480),'ungdomsväsendet',25);label(d,(380,610),'i din hemkommun',30)
        elif i==48:
            ball(d,205,300,1);group(d,565,325,.8);arrow(d,(440,350),(325,350));heart(d,565,515,.6);label(d,(380,155),'idrottssällskap',31);label(d,(380,615),'ofta med frivilligarbete',31)
        else:raise ValueError('Missing source-specific leisure composition '+str(i))
        im.save(dest);a=dict(asset_id=key,kind='foreground',visual_type='diagram',files=[info(dest)],creator='Homebrew video studio',reuse_terms='Original schematic artwork under repository MIT license; archived source wording retains publisher terms.',required_credits='Original source-based leisure illustrations: Homebrew video studio; source wording credited in sources.yaml and CREDITS.md.',relevance_verification=plans[i]['request']+' Individually composed exact-source relationship. No invented price,age limit,opening hours,event,discount amount,participation guarantee or claim about a photographed person.',creation_method=dict(tool=str(Path(__file__).relative_to(R)),source_sentence_ids=[row['sentence_id']]))
    assets.append(a);by_index[i]=a
for i,row in enumerate(script['sentences']):
    a=by_index[aliases.get(i,i)];row.update(asset_ids=['episode_background',a['asset_id']],render_image=a['files'][0]['path'],render_caption=False)
    if i in aliases:a['creation_method'].setdefault('source_sentence_ids',[script['sentences'][aliases[i]]['sentence_id']]).append(row['sentence_id']);row['visual_cue']='Retain the relevant preceding picture across this direct source continuation: '+plans[i]['request']
script['asset_requests']=script['asset_requests'][:3]+[dict(id=a['asset_id'],kind='foreground',description=a['relevance_verification'],fallback='Accurate useful original pictorial explanation limited to the source; document omission after reasonable research if necessary.') for a in assets];script['render']['credits']=script['render']['credits'][:2]
for j in range(0,len(screen),2):script['render']['credits'].append(dict(heading='Förgrundsbilder · Изображения',paragraphs=screen[j:j+2]+['Original schematisk grafik: Homebrew video studio.','Fullständiga källor och licenser i CREDITS.md.']))
for decision in script['episode_decisions']:
    if decision['id']=='visuals':decision['decision']='All51body slides show49distinct relevant pictures:30actual photographs and19original source-specific diagrams. Two direct source continuations retain a useful relevant unchanged place photograph. Current service availability,ownership and programme schedules are not inferred from photos.'
(E/'script.yaml').write_text(yaml.safe_dump(script,allow_unicode=True,sort_keys=False,width=100));(E/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');(E/'foreground-downloads.json').write_text(json.dumps(downloads,ensure_ascii=False,indent=2)+'\n');(E/'prepare_assets.py').write_text((R/'studio/episodes/hb-c10-utkomststod/prepare_assets.py').read_text().replace('Textgrafik: exakta ord och tal ur källtexten.','Original källbaserad schematisk grafik: Homebrew video studio.'));print('Prepared',len(assets),'distinct pictures;',len(screen),'photographic/object sources for51slides.')
