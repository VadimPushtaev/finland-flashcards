"""Compose exact library access,lending and language relationships with actual photographs."""
from pathlib import Path
import json,yaml,hashlib,re,math
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parents[3];SID='hb-c11-bibliotek';E=R/'studio/episodes'/SID;M=R/'studio/media'/SID;O=M/'pictures';O.mkdir(parents=True,exist_ok=True)
ns={'__file__':str(Path(__file__))};exec(compile((R/'studio/production/hb-c10/author_utkomststod.py').read_text().split('specs=')[0],'access-primitives','exec'),ns);code=(R/'studio/production/hb-c10/prepare_folkhalsa_pictures.py').read_text();exec(compile(code[code.index('def heart'):code.index('photos=json.loads')],'health-objects','exec'),ns);code=(R/'studio/production/hb-c10/prepare_vard_pictures.py').read_text();exec(compile(code[code.index('def envelope'):code.index('photos=json.loads',code.index('def envelope'))],'care-objects','exec'),ns)
ns.update(BG='#243c32',PANEL='#2d4d40',FG='#faf3e8',SOFT='#c5dfce',GOLD='#e3c58c',LINE='#4d7560')
canvas,label,house,person,coins,paper,arrow,heart,shield,cross,book,clinic,clock,group,magnify,record,folder,envelope,phone,card,no,calendar,doctor,hardhat=[ns[k] for k in ['canvas','label','house','person','coins','paper','arrow','heart','shield','cross','book','clinic','clock','group','magnify','record','folder','envelope','phone','card','no','calendar','doctor','hardhat']];FG,SOFT,GOLD,LINE,PANEL,BG=[ns[k] for k in ['FG','SOFT','GOLD','LINE','PANEL','BG']]
def info(p):return dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def globe(d,x,y,s=1):
    d.ellipse((x-75*s,y-75*s,x+75*s,y+75*s),outline=SOFT,width=5);d.ellipse((x-35*s,y-75*s,x+35*s,y+75*s),outline=GOLD,width=4);d.line((x-75*s,y,x+75*s,y),fill=GOLD,width=4)
def librarycard(d,x,y,s=1):
    d.rounded_rectangle((x-105*s,y-65*s,x+105*s,y+65*s),radius=14,outline=SOFT,width=5);book(d,x-35*s,y,.42*s);d.line((x+20*s,y-15*s,x+75*s,y-15*s),fill=LINE,width=5);d.line((x+20*s,y+15*s,x+75*s,y+15*s),fill=GOLD,width=5)
photos=json.loads((E/'selected-photos.json').read_text());old=json.loads((E/'retained-photo-assets.json').read_text());script=yaml.safe_load((E/'script.yaml').read_text());plans=json.loads((E/'picture-plan.json').read_text());assets=[];downloads=[];screen=[];by_index={};aliases={}
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
        if i==8:
            book(d,190,320,1.4);d.line((380,180,380,540),fill=LINE,width=4);group(d,570,335,.8);d.ellipse((500,220,640,440),outline=GOLD,width=4);label(d,(190,510),'kan vara begränsad',24);label(d,(570,510),'oftast öppet för alla',24);label(d,(380,605),'vetenskaps- och specialbibliotek',26)
        elif i==9:
            book(d,195,325,1.35);arrow(d,(325,350),(445,350));librarycard(d,565,340,1.05);label(d,(380,585),'bibliotekskort behövs för lån',29)
        elif i==10:
            person(d,170,300,.8);house(d,570,280,1.1);librarycard(d,570,490,.75);arrow(d,(280,350),(450,350));label(d,(380,610),'få kortet på biblioteket',30)
        elif i==11:
            d.rounded_rectangle((145,215,615,500),radius=20,outline=SOFT,width=6);d.rectangle((185,260,345,445),outline=LINE,width=4);person(d,265,325,.65)
            for y in [295,345,395]:d.line((395,y,560,y),fill=LINE,width=5)
            label(d,(380,580),'ID-kort med bild',34);label(d,(380,625),'schematiskt anonymt exempel',22)
        elif i==12:
            paper(d,175,320,160,215);no(d,175,320,115);arrow(d,(290,350),(440,350));librarycard(d,565,290,.95);clock(d,565,500,.85);label(d,(175,500),'utan finländsk',24);label(d,(175,535),'personbeteckning',24);label(d,(565,600),'giltigt en bestämd tid',24)
        elif i==13:
            librarycard(d,220,340,1.25);coins(d,565,350,3);no(d,565,335,110);label(d,(380,590),'bibliotekskortet är avgiftsfritt',29)
        elif i==14:
            librarycard(d,180,270,.85);label(d,(180,435),'borttappat',28);label(d,(380,280),'?',68);arrow(d,(300,350),(440,350));librarycard(d,565,310,.9);coins(d,565,510,3);label(d,(380,610),'ett nytt kort kostar',32)
        elif i==16:
            book(d,190,325,1.25);calendar(d,565,330,1.3);label(d,(565,330),'1',60);d.line((475,295,655,295),fill=GOLD,width=5);arrow(d,(320,350),(430,350));label(d,(380,570),'vanligtvis en månad',32);label(d,(380,615),'lånetid för böcker',29)
        elif i==18:
            book(d,180,315,1.25);clock(d,380,320,.9);arrow(d,(480,350),(535,350));coins(d,610,345,4);label(d,(380,590),'försenat lån → förseningsavgift',28)
        elif i==19:
            for x,y in [(120,280),(165,310),(210,340)]:book(d,x,y,.55)
            calendar(d,570,320,.95);label(d,(175,470),'antal böcker',29);label(d,(570,470),'antal dagar',29);arrow(d,(175,515),(315,575));arrow(d,(570,515),(445,575));coins(d,380,560,2);label(d,(380,615),'avgiftens storlek',28)
        elif i==20:
            book(d,380,345,2.15);d.line((245,285,330,285),fill=GOLD,width=5);d.line((245,320,330,320),fill=GOLD,width=5);d.line((245,355,330,355),fill=GOLD,width=5);label(d,(380,575),'klarspråk',35);label(d,(380,620),'böcker på lättläst finska',28)
        elif i==21:
            book(d,185,325,1.4);arrow(d,(325,350),(445,350));person(d,565,305,.85);d.rounded_rectangle((465,175,665,255),radius=15,outline=GOLD,width=4);label(d,(565,192),'finska',31);label(d,(380,590),'lämpliga för språkstudier',30)
        elif i==23:
            house(d,380,190,1);book(d,165,390,.9);phone(d,380,395,.6);d.ellipse((530,345,640,455),outline=SOFT,width=4);d.ellipse((575,390,595,410),outline=GOLD,width=3);coins(d,380,555,2);no(d,380,550,55);label(d,(380,625),'bibliotekets tjänster kostnadsfria',25)
        elif i==24:
            for x,y in [(180,285),(380,235),(580,285)]:book(d,x,y,.9)
            d.rounded_rectangle((160,420,600,540),radius=20,outline=GOLD,width=5);label(d,(380,440),'över 80 språk',44);label(d,(380,610),'Flerspråkiga biblioteket',30)
        elif i==25:
            book(d,380,240,1.2)
            for x in [150,380,610]:house(d,x,475,.75);arrow(d,(380,360),(x,420))
            label(d,(380,610),'lån från hela Finland',31)
        elif i==27:
            person(d,170,280,.9);person(d,365,315,.6);d.rounded_rectangle((85,455,450,540),radius=15,outline=GOLD,width=4);label(d,(265,475),'vårdnadshavarens tillstånd',24);arrow(d,(450,495),(550,405));librarycard(d,615,335,.75);label(d,(380,610),'barnets eget bibliotekskort',28)
        else:raise ValueError('Missing source-specific library composition '+str(i))
        im.save(dest);a=dict(asset_id=key,kind='foreground',visual_type='diagram',files=[info(dest)],creator='Homebrew video studio',reuse_terms='Original schematic artwork under repository MIT license; archived source wording retains publisher terms.',required_credits='Original source-based library illustrations: Homebrew video studio; source wording credited in sources.yaml and CREDITS.md.',relevance_verification=plans[i]['request']+' Individually composed exact-source relationship. No invented current opening hours,fee,card validity duration,language inventory,renewal limit or official identity document.',creation_method=dict(tool=str(Path(__file__).relative_to(R)),source_sentence_ids=[row['sentence_id']]))
    assets.append(a);by_index[i]=a
for i,row in enumerate(script['sentences']):
    a=by_index[aliases.get(i,i)];row.update(asset_ids=['episode_background',a['asset_id']],render_image=a['files'][0]['path'],render_caption=False)
    if i in aliases:a['creation_method'].setdefault('source_sentence_ids',[script['sentences'][aliases[i]]['sentence_id']]).append(row['sentence_id']);row['visual_cue']='Retain the relevant preceding picture across this direct source continuation: '+plans[i]['request']
script['asset_requests']=script['asset_requests'][:3]+[dict(id=a['asset_id'],kind='foreground',description=a['relevance_verification'],fallback='Accurate useful original pictorial explanation limited to the source; document omission after reasonable research if necessary.') for a in assets];script['render']['credits']=script['render']['credits'][:2]
for j in range(0,len(screen),2):script['render']['credits'].append(dict(heading='Förgrundsbilder · Изображения',paragraphs=screen[j:j+2]+['Original schematisk grafik: Homebrew video studio.','Fullständiga källor och licenser i CREDITS.md.']))
for decision in script['episode_decisions']:
    if decision['id']=='visuals':decision['decision']='All28body slides show28distinct relevant pictures:12actual photographs and16original source-specific diagrams. Actual room identities inspected; fees,guardian consent,ordinary loan duration and conditional admission remain qualified. No photographed person assigned pupil status.'
(E/'script.yaml').write_text(yaml.safe_dump(script,allow_unicode=True,sort_keys=False,width=100));(E/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');(E/'foreground-downloads.json').write_text(json.dumps(downloads,ensure_ascii=False,indent=2)+'\n');(E/'prepare_assets.py').write_text((R/'studio/episodes/hb-c10-utkomststod/prepare_assets.py').read_text());print('Prepared',len(assets),'distinct pictures;',len(screen),'photographic/object sources for28slides.')
