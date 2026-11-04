"""Compose exact-source medicine,oral-care and import rules with actual objects."""
from pathlib import Path
import json,yaml,hashlib,re,math
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parents[3];SID='hb-c10-lakemedel';E=R/'studio/episodes'/SID;M=R/'studio/media'/SID;O=M/'pictures';O.mkdir(parents=True,exist_ok=True)
ns={'__file__':str(Path(__file__))};exec(compile((R/'studio/production/hb-c10/author_utkomststod.py').read_text().split('specs=')[0],'access-primitives','exec'),ns);code=(R/'studio/production/hb-c10/prepare_folkhalsa_pictures.py').read_text();exec(compile(code[code.index('def heart'):code.index('photos=json.loads')],'health-objects','exec'),ns);code=(R/'studio/production/hb-c10/prepare_vard_pictures.py').read_text();exec(compile(code[code.index('def envelope'):code.index('photos=json.loads',code.index('def envelope'))],'care-objects','exec'),ns)
canvas,label,house,person,coins,paper,arrow,heart,shield,cross,book,clinic,clock,group,magnify,record,folder,envelope,phone,card,no,calendar,doctor,hardhat=[ns[k] for k in ['canvas','label','house','person','coins','paper','arrow','heart','shield','cross','book','clinic','clock','group','magnify','record','folder','envelope','phone','card','no','calendar','doctor','hardhat']];FG,SOFT,GOLD,LINE,PANEL,BG=[ns[k] for k in ['FG','SOFT','GOLD','LINE','PANEL','BG']]
def info(p):return dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def globe(d,x,y,s=1):
    d.ellipse((x-75*s,y-75*s,x+75*s,y+75*s),outline=SOFT,width=5);d.ellipse((x-35*s,y-75*s,x+35*s,y+75*s),outline=GOLD,width=4);d.line((x-75*s,y,x+75*s,y),fill=GOLD,width=4)
def medicine(d,x,y,s=1):
    d.rounded_rectangle((x-68*s,y-80*s,x+68*s,y+80*s),radius=12,outline=SOFT,width=5);d.line((x-68*s,y-25*s,x+68*s,y-25*s),fill=GOLD,width=5);cross(d,x,y+25*s,.55*s)
def tooth(d,x,y,s=1):
    d.line([(x-60*s,y-60*s),(x-25*s,y-75*s),(x,y-60*s),(x+25*s,y-75*s),(x+60*s,y-60*s),(x+55*s,y+10*s),(x+30*s,y+90*s),(x+10*s,y+35*s),(x-10*s,y+35*s),(x-30*s,y+90*s),(x-55*s,y+10*s),(x-60*s,y-60*s)],fill=SOFT,width=6)
def database(d,x,y,s=1):
    d.ellipse((x-70*s,y-65*s,x+70*s,y-25*s),outline=SOFT,width=5);d.line((x-70*s,y-45*s,x-70*s,y+70*s),fill=SOFT,width=5);d.line((x+70*s,y-45*s,x+70*s,y+70*s),fill=SOFT,width=5)
    for yy in [5,45,85]:d.arc((x-70*s,y+(yy-40)*s,x+70*s,y+yy*s),0,180,fill=GOLD,width=4)
def syringe(d,x,y,s=1):
    d.rectangle((x-50*s,y-25*s,x+30*s,y+25*s),outline=SOFT,width=4);d.line((x+30*s,y,x+85*s,y),fill=GOLD,width=4);d.line((x-75*s,y,x-50*s,y),fill=SOFT,width=5);d.line((x-75*s,y-30*s,x-75*s,y+30*s),fill=SOFT,width=5)
photos=json.loads((E/'selected-photos.json').read_text());old=json.loads((E/'retained-photo-assets.json').read_text());script=yaml.safe_load((E/'script.yaml').read_text());plans=json.loads((E/'picture-plan.json').read_text());assets=[];downloads=[];screen=[];by_index={};aliases={19:18,41:40,42:40,43:40}
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
        if i==0:
            medicine(d,190,335,1.1);paper(d,565,335,180,245);label(d,(565,270),'recept',32);arrow(d,(305,350),(450,350));label(d,(380,580),'behövs för många mediciner',30)
        elif i==1:
            doctor(d,145,300,.8);paper(d,365,320,150,190);label(d,(365,415),'e-recept',27);database(d,610,340,.85);arrow(d,(220,335),(275,335));arrow(d,(460,335),(510,335));label(d,(380,580),'nationella receptdatabasen',29)
        elif i==2:
            database(d,380,230,.8)
            for x,t in [(150,'FPA-kort'),(380,'identitetskort'),(610,'körkort')]:
                d.rounded_rectangle((x-88,425,x+88,540),radius=12,outline=SOFT,width=4);label(d,(x,465),t,25);d.line((x,425,380,335),fill=GOLD,width=4)
            label(d,(380,605),'farmaceuten kan kontrollera receptet',25)
        elif i==4:
            d.rectangle((90,220,315,445),outline=SOFT,width=5);d.line((90,270,315,270),fill=LINE,width=5);label(d,(202,305),'mataffär',30);no(d,202,330,100);clinic(d,565,285,1.1);label(d,(565,435),'apotek',32);medicine(d,380,555,.55);arrow(d,(445,555),(550,475));label(d,(380,615),'mediciner säljs endast på apotek',27)
        elif i==5:
            tooth(d,380,235,1.1);arrow(d,(325,340),(195,420));arrow(d,(435,340),(565,420));shield(d,195,490,.85);magnify(d,565,485,.8);label(d,(195,600),'förebyggande',29);label(d,(565,600),'korrigerande',29)
        elif i==8:
            person(d,185,310,.8);label(d,(185,485),'om man vill',29);arrow(d,(285,350),(450,350));shield(d,570,335,1.1);heart(d,570,335,.6);label(d,(570,510),'smärtlindring',28);label(d,(380,610),'vid vårdåtgärder',29)
        elif i==9:
            label(d,(380,150),'till exempel vid plombering',28);d.rounded_rectangle((75,235,325,490),radius=20,outline=LINE,width=4);d.rounded_rectangle((435,235,685,490),radius=20,outline=LINE,width=4);label(d,(200,260),'1',48);medicine(d,200,370,.65);label(d,(200,525),'ytbedövning',30);arrow(d,(345,375),(415,375));label(d,(560,260),'2',48);syringe(d,560,395,.75);label(d,(560,525),'lokalbedövning',29);label(d,(560,565),'injektion',25)
        elif i==14:
            for x,y in [(170,310),(320,340),(470,370)]:person(d,x,y,.7)
            clinic(d,610,270,.8);clock(d,380,535,.7);label(d,(380,615),'ofta kö till offentlig tandvård',28)
        elif i==15:
            clock(d,175,330,1.2);cross(d,175,330,.65);arrow(d,(275,350),(450,350));clinic(d,570,300,1.2);label(d,(380,590),'jouren: brådskande vårdbehov',29)
        elif i==16:
            tooth(d,200,335,1);tooth(d,565,290,1);d.line((480,430,650,430),fill=LINE,width=5);arrow(d,(565,395),(565,460));label(d,(200,525),'värker',32);label(d,(565,525),'lossnar',32);label(d,(380,605),'exempel på brådskande behov',28)
        elif i==17:
            phone(d,150,335,.95);arrow(d,(240,365),(320,365));person(d,410,310,.8);clock(d,610,365,.75);d.line((485,365,550,365),fill=GOLD,width=5);label(d,(380,570),'tidsbokningen bedömer per telefon',27);label(d,(380,615),'hur brådskande behovet är',27)
        elif i==18:
            label(d,(380,150),'OM tandkirurg behövs',30);doctor(d,160,315,.75);paper(d,390,350,150,200);doctor(d,610,315,.75);arrow(d,(235,350),(295,350));arrow(d,(485,350),(535,350));label(d,(160,500),'vanlig tandläkare',23);label(d,(390,500),'vid behov: remiss',22);label(d,(610,500),'specialist',25);label(d,(380,605),'boka vanlig tandläkare först',28)
        elif i==20:
            person(d,165,300,.65);label(d,(165,465),'under 18 år',29);clinic(d,565,300,1.1);coins(d,565,505,2);no(d,565,495,70);label(d,(380,595),'offentlig munhälsovård avgiftsfri',27)
        elif i==22:
            person(d,220,310,.7);person(d,310,350,.55);arrow(d,(390,370),(465,370));tooth(d,580,335,.9);shield(d,580,340,1.35);label(d,(380,595),'god mun- och tandhälsa från början',27);label(d,(380,155),'syftet med vården',30)
        elif i==23:
            label(d,(380,155),'OM båda villkoren gäller',29)
            for x in [190,570]:d.rounded_rectangle((x-130,245,x+130,435),radius=16,outline=LINE,width=4)
            tooth(d,190,325,.5);paper(d,570,325,90,115);label(d,(380,310),'och',28);label(d,(190,450),'funktionellt bettfel',24);label(d,(570,450),'uppfyller kriterierna',23);arrow(d,(190,505),(320,560));arrow(d,(570,505),(440,560));label(d,(380,580),'tandreglering',32)
        elif i==24:
            tooth(d,185,310,.8);d.line((140,310,230,310),fill=GOLD,width=6);label(d,(185,455),'korrigera bettfel',25);person(d,565,285,.6);label(d,(565,430),'under 18 år',28);coins(d,380,545,2);no(d,380,535,70);label(d,(380,615),'på social- och hälsovårdscentral',25)
        elif i==25:
            tooth(d,180,325,1);magnify(d,180,325,1.25);arrow(d,(300,350),(455,350));doctor(d,570,315,.85);label(d,(380,580),'också möjligt hos privattandläkare',27)
        elif i==26:
            card(d,175,310,.9);paper(d,570,300,190,245);coins(d,570,425,3);arrow(d,(280,330),(440,330));label(d,(175,480),'om FPA-kort',28);label(d,(570,495),'en del av avgiften',25);label(d,(380,610),'ersättning för privattandläkare',28)
        elif i==27:
            card(d,170,275,.75);no(d,170,275,100);clock(d,570,270,.9);paper(d,175,515,135,160);envelope(d,560,525,.8);arrow(d,(280,520),(450,520));label(d,(380,610),'utan kort: ansök hos FPA i efterhand',25)
        elif i==28:
            calendar(d,225,325,1.4);doctor(d,575,300,.9);arrow(d,(380,345),(455,345));label(d,(380,570),'vanligtvis snabbt en tid',30);label(d,(380,615),'hos privattandläkare',28)
        elif i==29:
            medicine(d,275,335,1.5);magnify(d,515,360,1.3);d.rounded_rectangle((140,500,620,580),radius=15,outline=GOLD,width=4);label(d,(380,525),'sista användningsdatum',31);label(d,(380,605),'står på förpackningen',28)
        elif i==30:
            medicine(d,235,335,1.35);calendar(d,565,335,1.15);no(d,235,335,115);label(d,(380,585),'föråldrat läkemedel: använd inte',28)
        elif i==32:
            medicine(d,180,285,.95);medicine(d,580,285,.95);d.line((325,270,435,270),fill=GOLD,width=5);d.line((325,295,435,295),fill=GOLD,width=5);label(d,(380,400),'OM samma verksamma ämne',29);coins(d,180,535,4);coins(d,580,535,2);arrow(d,(300,555),(450,555));label(d,(380,610),'kan bytas mot förmånligare',29)
        elif i==33:
            person(d,175,320,.8);person(d,590,320,.8);d.rounded_rectangle((290,190,485,355),radius=20,outline=GOLD,width=5);medicine(d,380,265,.5);coins(d,380,400,2);d.polygon([(485,320),(520,355),(485,350)],outline=GOLD,width=4);label(d,(380,575),'apotekspersonalen berättar',28);label(d,(380,615),'om billigare alternativ finns',27)
        elif i==35:
            medicine(d,210,335,1.25);d.line((420,200,420,520),fill=GOLD,width=10);shield(d,575,335,1.15);label(d,(380,590),'importen är begränsad',32)
        elif i==36:
            medicine(d,200,320,1.15);globe(d,570,335,1.2);arrow(d,(200,455),(305,540));arrow(d,(570,455),(455,540));label(d,(200,175),'vilken sorts läkemedel',25);label(d,(570,175),'från vilket land',27);paper(d,380,550,145,130);label(d,(380,615),'begränsningar',27)
        elif i==37:
            paper(d,185,300,180,230);paper(d,575,300,180,230);label(d,(185,450),'recept',30);label(d,(575,450),'läkarintyg',30);label(d,(380,300),'eller',27);arrow(d,(185,495),(305,560));arrow(d,(575,495),(455,560));person(d,380,530,.3);label(d,(380,610),'exempel: bevis för eget bruk',28)
        elif i==40:
            # One unchanged matrix remains over all four direct source rules40..43.
            label(d,(380,120),'Läkemedel för eget bruk',27)
            for x in [45,345,530,715]:d.line((x,175,x,560),fill=LINE,width=3)
            for y in [175,265,410,560]:d.line((45,y,715,y),fill=LINE,width=3)
            label(d,(440,190),'ta med',24);label(d,(620,190),'per post',24);label(d,(195,285),'EES eller',27);label(d,(195,325),'Nordirland',27);label(d,(440,300),'1 års',28);label(d,(440,340),'förbrukning',23);label(d,(620,300),'högst 3 mån.',24);label(d,(620,340),'förbrukning',23);label(d,(195,440),'utanför EES',27);label(d,(195,480),'och Nordirland',25);label(d,(440,445),'högst 3 mån.',24);label(d,(440,485),'förbrukning',23);envelope(d,620,480,.6);no(d,620,475,67);label(d,(380,590),'Narkotikaklassade läkemedel:',24);label(d,(380,620),'strängare begränsningar',25)
        elif i==44:
            medicine(d,200,335,1.3);label(d,(200,475),'OM narkotikaklassat',24);arrow(d,(320,350),(440,350));shield(d,570,330,1.15);label(d,(570,470),'strängare',29);label(d,(570,510),'begränsningar',27);label(d,(380,610),'ingen generell mängdgaranti',26)
        else:raise ValueError('Missing source-specific medicine composition '+str(i))
        im.save(dest);a=dict(asset_id=key,kind='foreground',visual_type='diagram',files=[info(dest)],creator='Homebrew video studio',reuse_terms='Original schematic artwork under repository MIT license; archived source wording retains publisher terms.',required_credits='Original source-based medicine and oral-care illustrations: Homebrew video studio; source wording credited in sources.yaml and CREDITS.md.',relevance_verification=plans[i]['request']+' Individually composed exact-source relationship. No invented dose,treatment technique,diagnosis,fee,deadline,import-country list or authorization.',creation_method=dict(tool=str(Path(__file__).relative_to(R)),source_sentence_ids=[row['sentence_id']]))
    assets.append(a);by_index[i]=a
for i,row in enumerate(script['sentences']):
    a=by_index[aliases.get(i,i)];row.update(asset_ids=['episode_background',a['asset_id']],render_image=a['files'][0]['path'],render_caption=False)
    if i in aliases:a['creation_method'].setdefault('source_sentence_ids',[script['sentences'][aliases[i]]['sentence_id']]).append(row['sentence_id']);row['visual_cue']='Retain the relevant preceding picture across this direct source continuation: '+plans[i]['request']
script['asset_requests']=script['asset_requests'][:3]+[dict(id=a['asset_id'],kind='foreground',description=a['relevance_verification'],fallback='Accurate useful original pictorial explanation limited to the source; document omission after reasonable research if necessary.') for a in assets];script['render']['credits']=script['render']['credits'][:2]
for j in range(0,len(screen),2):script['render']['credits'].append(dict(heading='Förgrundsbilder · Изображения',paragraphs=screen[j:j+2]+['Original schematisk grafik: Homebrew video studio.','Fullständiga källor och licenser i CREDITS.md.']))
for decision in script['episode_decisions']:
    if decision['id']=='visuals':decision['decision']='Relevant pictures cover all46source slides with42distinct pictures:13verified photographs and29source-specific original diagrams. One exact referral continuation and one four-rule import matrix deliberately retain meaningful unchanged pictures. No photographed person is assigned a diagnosis or patient status.'
(E/'script.yaml').write_text(yaml.safe_dump(script,allow_unicode=True,sort_keys=False,width=100));(E/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');(E/'foreground-downloads.json').write_text(json.dumps(downloads,ensure_ascii=False,indent=2)+'\n');(E/'prepare_assets.py').write_text((R/'studio/episodes/hb-c10-utkomststod/prepare_assets.py').read_text());print('Prepared',len(assets),'distinct pictures;',len(screen),'photographic/object sources for46slides.')
