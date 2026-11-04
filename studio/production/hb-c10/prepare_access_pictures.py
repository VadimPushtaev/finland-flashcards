"""Draw qualified care-access and patient-rights relationships with concrete photographs."""
from pathlib import Path
import json,yaml,hashlib,re,math
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parents[3];SID='hb-c10-tillgang';E=R/'studio/episodes'/SID;M=R/'studio/media'/SID;O=M/'pictures';O.mkdir(parents=True,exist_ok=True)
ns={'__file__':str(Path(__file__))};exec(compile((R/'studio/production/hb-c10/author_utkomststod.py').read_text().split('specs=')[0],'access-primitives','exec'),ns);code=(R/'studio/production/hb-c10/prepare_folkhalsa_pictures.py').read_text();exec(compile(code[code.index('def heart'):code.index('photos=json.loads')],'health-objects','exec'),ns);code=(R/'studio/production/hb-c10/prepare_vard_pictures.py').read_text();exec(compile(code[code.index('def envelope'):code.index('photos=json.loads',code.index('def envelope'))],'care-objects','exec'),ns)
canvas,label,house,person,coins,paper,arrow,heart,shield,cross,book,clinic,clock,group,magnify,record,folder,envelope,phone,card,no,calendar,doctor,hardhat=[ns[k] for k in ['canvas','label','house','person','coins','paper','arrow','heart','shield','cross','book','clinic','clock','group','magnify','record','folder','envelope','phone','card','no','calendar','doctor','hardhat']];FG,SOFT,GOLD,LINE,PANEL,BG=[ns[k] for k in ['FG','SOFT','GOLD','LINE','PANEL','BG']]
def info(p):return dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def globe(d,x,y,s=1):
    d.ellipse((x-75*s,y-75*s,x+75*s,y+75*s),outline=SOFT,width=5);d.ellipse((x-35*s,y-75*s,x+35*s,y+75*s),outline=GOLD,width=4);d.line((x-75*s,y,x+75*s,y),fill=GOLD,width=4)
photos=json.loads((E/'selected-photos.json').read_text());old=json.loads((E/'retained-photo-assets.json').read_text());script=yaml.safe_load((E/'script.yaml').read_text());plans=json.loads((E/'picture-plan.json').read_text());assets=[];downloads=[];screen=[];by_index={};aliases={10:9,24:23}
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
        if i==1:
            for x,y in[(185,265),(575,265),(185,505),(575,505)]:d.rounded_rectangle((x-115,y-85,x+115,y+90),radius=20,outline=LINE,width=4)
            globe(d,185,250,.7);hardhat(d,575,260,.65);house(d,185,470,.65);calendar(d,575,500,.65);label(d,(380,615),'följande omständigheter',28)
        elif i==2:
            globe(d,220,330,1.5);paper(d,590,330,150,220);d.line((350,330,470,330),fill=GOLD,width=5);label(d,(380,570),'från vilket land?',33)
        elif i==3:
            hardhat(d,200,310,1.15);book(d,570,335,1.15);d.line((380,185,380,535),fill=LINE,width=5);label(d,(200,505),'arbete',32);label(d,(570,505),'studier',32);label(d,(380,610),'till exempel',27)
        elif i==4:
            house(d,200,280,1.3);d.rounded_rectangle((500,265,650,445),radius=20,outline=SOFT,width=6);d.arc((545,235,610,300),180,360,fill=GOLD,width=5);label(d,(200,510),'stadigvarande',28);label(d,(575,510),'tillfälligt',28);label(d,(380,610),'hur du ska bo eller vistas',28)
        elif i==5:
            calendar(d,260,335,1.5);clock(d,565,335,1.15);d.line((100,540,650,540),fill=GOLD,width=5);d.line((100,525,100,555),fill=GOLD,width=4);d.line((650,525,650,555),fill=GOLD,width=4);label(d,(380,590),'hur länge vistelsen varar',29)
        elif i==6:
            label(d,(380,160),'OM du är osäker',31);person(d,150,320,.85);label(d,(350,290),'?',66);paper(d,590,315,170,220);label(d,(590,450),'DVV',40);arrow(d,(265,360),(450,360));label(d,(380,610),'kontrollera din situation',29)
        elif i==8:
            paper(d,210,330,205,275);envelope(d,570,355,1.1);arrow(d,(340,350),(450,350));d.rounded_rectangle((100,500,660,590),radius=20,outline=GOLD,width=5);label(d,(380,523),'separat ansökan om rätten',30)
        elif i==12:
            paper(d,220,325,210,280);coins(d,565,340,3);arrow(d,(565,460),(565,210));label(d,(220,505),'privat vård',31);label(d,(380,600),'avsevärt dyrare än offentlig',28)
        elif i==15:
            label(d,(380,155),'OM båda gäller',31)
            for x in[190,570]:d.rounded_rectangle((x-125,230,x+125,405),radius=20,outline=LINE,width=5)
            calendar(d,190,290,.55);phone(d,570,295,.45);no(d,190,290,60);no(d,570,290,60);label(d,(190,430),'inte kommit',28);label(d,(570,430),'inte avbokat',28);label(d,(380,300),'och',28);arrow(d,(190,480),(310,545));arrow(d,(570,480),(450,545));coins(d,380,565,2);label(d,(380,615),'avgift',32)
        elif i==17:
            person(d,185,330,.6);house(d,580,280,.9);no(d,580,315,115);d.line((280,350,440,350),fill=LINE,width=5);shield(d,380,520,.7);label(d,(380,610),'rätt även utan hemkommun i vissa fall',25)
        elif i==18:
            paper(d,190,320,190,250);label(d,(190,475),'asylsökande',29);person(d,570,315,.7);label(d,(570,475),'under 18 år',31);d.line((380,230,380,300),fill=GOLD,width=5);d.line((380,395,380,430),fill=GOLD,width=5);label(d,(380,335),'och',27);label(d,(380,160),'TILL EXEMPEL',29);arrow(d,(190,520),(310,570));arrow(d,(570,520),(450,570));clinic(d,380,570,.35)
        elif i==20:
            book(d,215,330,1.4);shield(d,565,330,1.4);person(d,565,285,.55);label(d,(380,600),'lagens minimirättigheter',30)
        elif i==21:
            person(d,380,310,.9);shield(d,380,345,1.7);heart(d,150,260,.6);book(d,610,265,.7);paper(d,150,510,130,165);d.rounded_rectangle((535,470,680,560),radius=20,outline=GOLD,width=5);d.polygon([(565,560),(550,590),(610,560)],outline=GOLD,width=4);label(d,(380,615),'följande exempel på rättigheter',27)
        elif i==23:
            person(d,170,285,.9);d.line([(125,470),(160,500),(225,420)],fill=GOLD,width=10);arrow(d,(280,345),(450,345));clinic(d,580,285,1.1);label(d,(170,560),'samtycke',31);label(d,(580,560),'vård inleds',31);label(d,(380,610),'samtycket säkerställs först',28)
        elif i==25:
            person(d,175,300,.9);clinic(d,580,285,1.1);arrow(d,(270,350),(460,350));d.line((375,240,375,465),fill=GOLD,width=13);d.ellipse((315,255,435,430),outline=GOLD,width=5);label(d,(380,590),'rätt att vägra vård',32)
        elif i==26:
            folder(d,175,300,'patientjournal',1);magnify(d,175,480,.75);paper(d,560,320,200,255);d.line((505,280,615,280),fill=SOFT,width=5);d.line((505,315,615,315),fill=GOLD,width=8);d.line((505,350,615,350),fill=SOFT,width=5);arrow(d,(310,350),(430,350));label(d,(560,510),'få fel korrigerade',27);label(d,(380,610),'kontrollera dina uppgifter',29)
        elif i==27:
            group(d,380,215,.6);book(d,380,415,1.25);clinic(d,160,390,.8);d.rectangle((545,365,675,485),outline=SOFT,width=5);cross(d,610,425,.6);d.line((300,550,460,550),fill=GOLD,width=5);d.line((300,575,460,575),fill=GOLD,width=5);label(d,(160,555),'offentlig',27);label(d,(610,555),'privat',27);label(d,(380,620),'likvärdiga tjänster enligt lagen',27)
        elif i==28:
            label(d,(380,155),'VID BEHOV',33);person(d,150,350,.8);person(d,380,305,.8);doctor(d,610,350,.8);d.rounded_rectangle((275,195,485,280),radius=20,outline=GOLD,width=5);label(d,(380,210),'tolk',31);arrow(d,(220,420),(300,420));arrow(d,(460,420),(540,420));label(d,(380,600),'på mottagningen',31)
        elif i==30:
            person(d,180,315,.9);paper(d,180,500,145,150);coins(d,565,340,3);no(d,565,335,125);label(d,(380,610),'patientombudsmannens tjänster är gratis',25)
        elif i==31:
            person(d,380,245,.9);d.line((380,390,180,470),fill=LINE,width=5);d.line((380,390,580,470),fill=LINE,width=5);paper(d,180,505,150,170);envelope(d,580,515,.8);label(d,(180,615),'anmärkning',28);label(d,(580,615),'ansöka om ersättning',23);label(d,(380,155),'hjälp och råd',31)
        else:raise ValueError('Missing source-specific access composition '+str(i))
        im.save(dest);a=dict(asset_id=key,kind='foreground',visual_type='diagram',files=[info(dest)],creator='Homebrew video studio',reuse_terms='Original schematic artwork under repository MIT license; archived source wording retains publisher terms.',required_credits='Original source-based care-access and patient-rights illustrations: Homebrew video studio; source wording credited in sources.yaml and CREDITS.md.',relevance_verification=plans[i]['request']+' Individually composed exact-source relationship. No new origin-country policy,age limit,fee,deadline,appointment time,legal exception,medical diagnosis or eligibility promise.',creation_method=dict(tool=str(Path(__file__).relative_to(R)),source_sentence_ids=[row['sentence_id']]))
    assets.append(a);by_index[i]=a
for i,row in enumerate(script['sentences']):
    a=by_index[aliases.get(i,i)];row.update(asset_ids=['episode_background',a['asset_id']],render_image=a['files'][0]['path'],render_caption=False)
    if i in aliases:a['creation_method'].setdefault('source_sentence_ids',[script['sentences'][aliases[i]]['sentence_id']]).append(row['sentence_id']);row['visual_cue']='Retain the relevant preceding picture across this direct source continuation: '+plans[i]['request']
script['asset_requests']=script['asset_requests'][:3]+[dict(id=a['asset_id'],kind='foreground',description=a['relevance_verification'],fallback='Accurate useful original pictorial explanation limited to the source; document omission after reasonable research if necessary.') for a in assets];script['render']['credits']=script['render']['credits'][:2]
for j in range(0,len(screen),2):script['render']['credits'].append(dict(heading='Förgrundsbilder · Изображения',paragraphs=screen[j:j+2]+['Original schematisk grafik: Homebrew video studio.','Fullständiga källor och licenser i CREDITS.md.']))
for decision in script['episode_decisions']:
    if decision['id']=='visuals':decision['decision']='Relevant foreground pictures cover all32source slides with30distinct pictures:10verified photographic/object sources and20individually composed qualified source diagrams. Two closely related source continuations retain their useful picture instead of cosmetic variants. No photographed person is assigned a diagnosis,immigration status or entitlement.'
(E/'script.yaml').write_text(yaml.safe_dump(script,allow_unicode=True,sort_keys=False,width=100));(E/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');(E/'foreground-downloads.json').write_text(json.dumps(downloads,ensure_ascii=False,indent=2)+'\n');(E/'prepare_assets.py').write_text((R/'studio/episodes/hb-c10-utkomststod/prepare_assets.py').read_text());print('Prepared',len(assets),'distinct pictures;',len(screen),'photographic/object sources for32slides.')
