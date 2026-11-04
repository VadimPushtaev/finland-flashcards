"""Compose exact sickness/disability/care-allowance gates with distinct relevant objects."""
from pathlib import Path
import json,yaml,hashlib,re,math
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parents[3];SID='hb-c10-sjukdom';E=R/'studio/episodes'/SID;M=R/'studio/media'/SID;O=M/'pictures';O.mkdir(parents=True,exist_ok=True)
ns={'__file__':str(Path(__file__))};exec(compile((R/'studio/production/hb-c10/author_utkomststod.py').read_text().split('specs=')[0],'access-primitives','exec'),ns);code=(R/'studio/production/hb-c10/prepare_folkhalsa_pictures.py').read_text();exec(compile(code[code.index('def heart'):code.index('photos=json.loads')],'health-objects','exec'),ns);code=(R/'studio/production/hb-c10/prepare_vard_pictures.py').read_text();exec(compile(code[code.index('def envelope'):code.index('photos=json.loads',code.index('def envelope'))],'care-objects','exec'),ns)
canvas,label,house,person,coins,paper,arrow,heart,shield,cross,book,clinic,clock,group,magnify,record,folder,envelope,phone,card,no,calendar,doctor,hardhat=[ns[k] for k in ['canvas','label','house','person','coins','paper','arrow','heart','shield','cross','book','clinic','clock','group','magnify','record','folder','envelope','phone','card','no','calendar','doctor','hardhat']];FG,SOFT,GOLD,LINE,PANEL,BG=[ns[k] for k in ['FG','SOFT','GOLD','LINE','PANEL','BG']]
def info(p):return dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def globe(d,x,y,s=1):
    d.ellipse((x-75*s,y-75*s,x+75*s,y+75*s),outline=SOFT,width=5);d.ellipse((x-35*s,y-75*s,x+35*s,y+75*s),outline=GOLD,width=4);d.line((x-75*s,y,x+75*s,y),fill=GOLD,width=4)
def warning(d,x,y,s=1):
    d.polygon([(x,y-70*s),(x+75*s,y+60*s),(x-75*s,y+60*s)],outline=GOLD,width=5);d.line((x,y-25*s,x,y+15*s),fill=SOFT,width=8);d.ellipse((x-5*s,y+35*s,x+5*s,y+45*s),fill=SOFT)
photos=json.loads((E/'selected-photos.json').read_text());advice=json.loads((E/'advisory-picture-plan.json').read_text());old=json.loads((E/'retained-photo-assets.json').read_text());script=yaml.safe_load((E/'script.yaml').read_text());plans=json.loads((E/'picture-plan.json').read_text());assets=[];downloads=[];screen=[];by_index={};aliases={7:6,8:6,9:6,10:6}
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
            cross(d,160,265,.9);warning(d,375,265,.85);label(d,(267,255),'eller',27);arrow(d,(265,375),(435,425));house(d,540,425,1);label(d,(380,155),'OM sjukdom eller olycka',30);label(d,(380,610),'rätt att stanna hemma från arbetet',27)
        elif i==1:
            shield(d,165,285,.9);clock(d,380,285,.8);label(d,(165,415),'sjukförsäkrad',26);label(d,(380,415),'efter självrisktid',23);label(d,(270,285),'och',25);arrow(d,(165,470),(365,535));arrow(d,(380,470),(380,525));d.ellipse((373,533,387,547),fill=GOLD);paper(d,565,530,140,140);label(d,(565,415),'FPA',34);arrow(d,(395,540),(475,540));label(d,(380,615),'rätt att söka sjukdagpenning',28)
        elif i==2:
            label(d,(380,150),'VANLIGEN',33);calendar(d,150,300,.9);cross(d,150,305,.55);label(d,(150,435),'insjuknandedag',23);label(d,(320,300),'+',56)
            for j in range(9):
                x=425+j%3*75;y=240+j//3*85;d.rounded_rectangle((x-22,y-22,x+22,y+22),radius=8,outline=GOLD,width=4)
            label(d,(505,505),'nio följande vardagar',27);label(d,(380,610),'självrisktiden',32)
        elif i==3:
            label(d,(380,150),'OM anställningen varat',29);calendar(d,190,300,1.05);label(d,(190,445),'över en månad',28);label(d,(190,485),'före insjuknandet',25);arrow(d,(310,335),(450,335));coins(d,565,335,4);label(d,(565,450),'full lön',34);label(d,(380,610),'arbetsgivaren betalar för självrisktiden',25)
        elif i==4:
            calendar(d,380,315,1.8);d.rectangle((245,275,515,415),fill=PANEL);label(d,(380,290),'300',75);label(d,(380,430),'vardagar',32);d.line((180,540,580,540),fill=GOLD,width=6);d.line((580,515,580,565),fill=GOLD,width=7);label(d,(380,590),'högst',36)
        elif i==5:
            cross(d,160,285,.8);label(d,(160,405),'insjuknande',27);paper(d,580,285,160,200);label(d,(580,430),'ansökan',30);arrow(d,(255,315),(470,315));d.line((250,490,655,490),fill=GOLD,width=6);d.line((655,470,655,515),fill=GOLD,width=6);label(d,(450,525),'inom två månader',28);label(d,(380,610),'efter insjuknandet',31)
        elif i==6:
            # Retain this complete cumulative overview over header+four list items.
            label(d,(380,125),'Villkoren i följande lista',30)
            boxes=[(195,260),(565,260),(195,485),(565,485)]
            for x,y in boxes:d.rounded_rectangle((x-145,y-90,x+145,y+90),radius=16,outline=LINE,width=4)
            shield(d,195,230,.42);calendar(d,565,225,.4);person(d,195,435,.36);hardhat(d,565,440,.45)
            label(d,(195,290),'sjukförsäkring',24);label(d,(565,280),'18–67 år',30);label(d,(195,490),'arbetsoförmögen',22);label(d,(195,520),'på grund av sjukdom',21);label(d,(565,490),'någon av grupperna',21);label(d,(565,520),'i källtexten',23);label(d,(380,360),'och',27);label(d,(380,615),'listans grupper är alternativa inom sista villkoret',22)
        elif i==11:
            label(d,(380,150),'OM lön under sjukledigheten',29);hardhat(d,175,310,.95);person(d,580,285,.75);coins(d,380,275,2);arrow(d,(275,345),(455,345));paper(d,380,520,155,170);arrow(d,(175,430),(280,520));label(d,(175,470),'arbetsgivaren',24);label(d,(380,615),'arbetsgivaren ansöker om sjukdagpenning',24)
        elif i==12:
            label(d,(380,150),'OM lön under sjukledigheten',29);paper(d,175,305,170,220);label(d,(175,260),'FPA',36);coins(d,380,330,3);arrow(d,(285,335),(465,335));hardhat(d,590,310,1.1);label(d,(590,495),'arbetsgivaren',25);label(d,(380,610),'sjukdagpenningen betalas till arbetsgivaren',24)
        elif i==13:
            label(d,(380,150),'OM båda gäller',30)
            for x in [190,570]:d.rounded_rectangle((x-135,220,x+135,405),radius=18,outline=LINE,width=4)
            clock(d,190,275,.5);coins(d,570,290,2);no(d,570,280,57);label(d,(190,430),'sjuk en lång tid',27);label(d,(570,430),'arbetsgivaren betalar',22);label(d,(570,465),'inte längre lön',25);label(d,(380,290),'och',26);arrow(d,(190,510),(300,560));arrow(d,(570,510),(460,560));person(d,380,550,.35);label(d,(380,610),'FPA betalar till dig',30)
        elif i==15:
            folder(d,180,300,'läkarintyg',.95);paper(d,575,300,185,230);d.line((145,500,610,500),fill=GOLD,width=5);arrow(d,(290,340),(450,340));label(d,(180,470),'arbetsoförmåga',25);label(d,(575,470),'ansökan',30);label(d,(380,610),'intyget bifogas ansökan',30)
        elif i==16:
            label(d,(380,140),'partiell sjukdagpenning',31);calendar(d,170,285,.8);label(d,(170,420),'18–67 år',30);hardhat(d,560,280,.9);label(d,(560,410),'heltidsarbetande anställda',21);label(d,(560,445),'eller företagare',25);shield(d,380,530,.6);label(d,(380,610),'och social trygghet i Finland',28);d.line((285,325,430,325),fill=LINE,width=4);label(d,(350,280),'och',24)
        elif i==18:
            label(d,(380,150),'diskutera FÖRST',32);doctor(d,180,300,.85);hardhat(d,580,310,.95);person(d,380,475,.55);d.line((250,350,315,450),fill=LINE,width=4);d.line((510,350,445,450),fill=LINE,width=4);label(d,(180,470),'företagshälsovårdsläkare',20);label(d,(580,470),'arbetsgivare',27);label(d,(380,610),'möjligheten att söka partiell sjukdagpenning',23)
        elif i==20:
            person(d,175,325,.75);calendar(d,575,325,.9);d.line((100,500,660,500),fill=GOLD,width=12);d.line((100,485,100,520),fill=SOFT,width=5);d.line((660,485,660,520),fill=SOFT,width=5);label(d,(380,155),'nedsatt funktion på grund av',27);label(d,(380,200),'funktionsnedsättning eller sjukdom',26);label(d,(380,545),'sammanhängande minst ett år',29);label(d,(380,615),'kan få handikappbidrag',29)
        elif i==21:
            folder(d,190,310,'läkarintyg',1);paper(d,570,315,180,235);arrow(d,(305,350),(455,350));d.line((475,235,510,270,540,220),fill=GOLD,width=5);label(d,(570,480),'ansöka om bidrag',26);label(d,(380,610),'läkarintyg krävs',33)
        elif i==22:
            label(d,(380,140),'BÅDA villkoren',32);shield(d,190,280,.8);calendar(d,565,270,.85);label(d,(190,405),'rätt till FPA:s förmåner',23);label(d,(565,390),'bott minst tre år',27);label(d,(380,280),'och',27);d.rounded_rectangle((100,480,660,595),radius=18,outline=GOLD,width=4);label(d,(380,495),'Finland eller annat EU-/EES-land',27);label(d,(380,540),'eller Schweiz',29)
        elif i==23:
            person(d,380,280,1.05);d.line((165,510,595,510),fill=GOLD,width=6);d.line((165,490,165,535),fill=GOLD,width=5);d.line((595,490,595,535),fill=GOLD,width=5);label(d,(165,545),'16',40);label(d,(595,545),'64',40);label(d,(380,460),'år',31);label(d,(380,615),'handikappbidrag för vuxna',29)
        elif i==24:
            person(d,190,285,.8);group(d,565,285,.7);label(d,(190,450),'olägenhet',30);label(d,(565,450),'hjälp och handledning',24);arrow(d,(190,500),(310,555));arrow(d,(565,500),(450,555));coins(d,380,555,2);label(d,(380,615),'beloppet beror på behoven',29)
        elif i==25:
            label(d,(380,125),'OM du vårdar en närstående',28);label(d,(380,165),'med funktionsnedsättning hemma',27);house(d,190,275,1.1);person(d,145,400,.45);person(d,235,400,.45);label(d,(190,520),'vårdar närstående hemma',23);arrow(d,(315,345),(440,345));house(d,570,265,1.05);coins(d,570,480,2);label(d,(570,540),'ditt välfärdsområde',24);label(d,(380,610),'kan få stöd för närståendevård',28)
        elif i==27:
            label(d,(380,140),'OM alla villkor gäller',30);person(d,175,275,.55);calendar(d,570,280,.85);label(d,(175,405),'under 16 år',30);label(d,(570,405),'minst sex månader',26);d.line((380,200,380,430),fill=LINE,width=4);label(d,(380,475),'på grund av funktionsnedsättning eller sjukdom',22);label(d,(380,520),'regelbunden vård, omsorg och rehabilitering',23);label(d,(380,615),'kan få handikappförmån',29)
        elif i==29:
            calendar(d,380,345,1.6);d.line((175,515,585,515),fill=GOLD,width=10);d.line((175,490,175,540),fill=SOFT,width=6);d.line((585,490,585,540),fill=SOFT,width=6);label(d,(380,145),'VANLIGTVIS',34);label(d,(380,600),'en bestämd period',33)
        elif i==30:
            clock(d,190,315,1.1);d.line((280,220,280,455),fill=LINE,width=7);arrow(d,(340,345),(455,345));paper(d,580,305,170,230);envelope(d,580,500,.75);label(d,(190,510),'perioden slut',27);label(d,(380,610),'kan ansöka om förlängning',29)
        elif i==31:
            label(d,(380,140),'OM båda gäller',32);person(d,155,275,.75);person(d,250,320,.4);label(d,(200,430),'måste delta i barnets',23);label(d,(200,465),'vård eller rehabilitering',23);hardhat(d,570,290,.85);no(d,570,290,85);label(d,(570,430),'kan inte arbeta',26);label(d,(570,465),'på grund av det',25);label(d,(380,520),'barn med svår sjukdom',27);label(d,(380,560),'eller funktionsnedsättning',26);label(d,(380,615),'kan ansöka om specialvårdspenning',26)
        elif i==32:
            paper(d,185,315,185,245);paper(d,575,315,185,245);label(d,(185,490),'specialvårdspenning',25);label(d,(575,490),'rehabiliteringspenning',24);label(d,(380,310),'eller',29);label(d,(380,575),'alternativ under barnets rehabilitering',26)
        elif i==33:
            paper(d,380,270,165,190);label(d,(380,245),'FPA',35)
            for x,y in [(125,465),(255,520),(380,465),(505,520),(635,465)]:d.line((380,380,x,y-45),fill=LINE,width=4);d.ellipse((x-30,y-30,x+30,y+30),outline=GOLD,width=4)
            label(d,(380,125),'kan få om följande fall',27);label(d,(380,615),'specialvårdspenning: källans situationer',25)
        elif i==35:
            person(d,165,285,.6);clinic(d,570,265,.9);label(d,(165,420),'barn 7–15 år',29);label(d,(570,420),'sjukhus eller poliklinik',23);d.rounded_rectangle((130,480,630,565),radius=16,outline=GOLD,width=4);label(d,(380,500),'med svår sjukdom',30);label(d,(380,615),'deltar i vården — ett av de angivna fallen',23)
        elif i==36:
            person(d,190,285,.7);person(d,290,325,.45);shield(d,570,320,1.15);cross(d,570,320,.55);arrow(d,(355,360),(440,360));label(d,(245,495),'barn 0–15 år',31);label(d,(570,495),'rehabilitering',28);label(d,(380,615),'du deltar i barnets rehabilitering',27)
        elif i==37:
            house(d,175,270,1.1);clinic(d,575,270,1.1);d.line((290,325,450,325),fill=GOLD,width=6);label(d,(380,360),'kopplad till',26);label(d,(175,455),'hemvård',30);label(d,(575,455),'sjukhus eller poliklinik',23);label(d,(380,535),'barn under 16 år med svår sjukdom',27);label(d,(380,615),'du vårdar barnet hemma',28)
        elif i==38:
            house(d,180,255,1.05);book(d,180,445,.7);clock(d,560,305,.95);person(d,560,485,.55);label(d,(180,535),'skol- eller dagvårdsförsök',22);label(d,(560,590),'i beredskap',29);label(d,(380,150),'i anslutning till svår sjukdom',28)
        elif i==40:
            person(d,180,375,.9);shield(d,580,390,1.2);d.line((280,390,460,390),fill=LINE,width=5);label(d,(380,155),'vårdbidrag för pensionstagare',25);label(d,(380,200),'nedsatt funktionsförmåga',25);label(d,(380,245),'sammanlagt minst ett år',26);label(d,(380,510),'regelbunden hjälp eller handledning',27);label(d,(380,555),'och övervakning',30);label(d,(380,615),'kan få stöd',30)
        elif i==41:
            group(d,190,315,.85);arrow(d,(315,350),(440,350));coins(d,575,350,3);label(d,(575,245),'?',64);label(d,(190,500),'hur mycket hjälp',27);label(d,(575,500),'stödets storlek',28);label(d,(380,615),'vårdbidrag för pensionstagare',27)
        else:raise ValueError('Missing source-specific sickness composition '+str(i))
        im.save(dest);a=dict(asset_id=key,kind='foreground',visual_type='diagram',files=[info(dest)],creator='Homebrew video studio',reuse_terms='Original schematic artwork under repository MIT license; archived source wording retains publisher terms.',required_credits='Original source-based sickness/disability/care-allowance illustrations: Homebrew video studio; source wording credited in sources.yaml and CREDITS.md.',relevance_verification=plans[i]['request']+' Individually composed exact-source relationship. No invented amount,current eligibility update,medical diagnosis,care procedure,calendar date,work-capacity finding or grant guarantee.',creation_method=dict(tool=str(Path(__file__).relative_to(R)),source_sentence_ids=advice[i]['source_sentence_ids']+([script['sentences'][j]['sentence_id'] for j in range(34,39)] if i==33 else [])))
    assets.append(a);by_index[i]=a
for i,row in enumerate(script['sentences']):
    a=by_index[aliases.get(i,i)];row.update(asset_ids=['episode_background',a['asset_id']],render_image=a['files'][0]['path'],render_caption=False)
    if i in aliases:a['creation_method'].setdefault('source_sentence_ids',[script['sentences'][aliases[i]]['sentence_id']]).extend([row['sentence_id']] if row['sentence_id'] not in a['creation_method']['source_sentence_ids'] else []);row['visual_cue']='Retain the relevant preceding picture across this direct source continuation: '+plans[i]['request']
script['asset_requests']=script['asset_requests'][:3]+[dict(id=a['asset_id'],kind='foreground',description=a['relevance_verification'],fallback='Accurate useful original pictorial explanation limited to the source; document omission after reasonable research if necessary.') for a in assets];script['render']['credits']=script['render']['credits'][:2]
for j in range(0,len(screen),2):script['render']['credits'].append(dict(heading='Förgrundsbilder · Изображения',paragraphs=screen[j:j+2]+['Original schematisk grafik: Homebrew video studio.','Fullständiga källor och licenser i CREDITS.md.']))
for decision in script['episode_decisions']:
    if decision['id']=='visuals':decision['decision']='All43body slides show39distinct relevant pictures:8actual object/place photographs and31source-specific diagrams. The complete cumulative sickness-allowance eligibility overview remains unchanged over its header and four list items. No photographed person is assigned illness,disability,benefit or pension status.'
(E/'script.yaml').write_text(yaml.safe_dump(script,allow_unicode=True,sort_keys=False,width=100));(E/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');(E/'foreground-downloads.json').write_text(json.dumps(downloads,ensure_ascii=False,indent=2)+'\n');(E/'prepare_assets.py').write_text((R/'studio/episodes/hb-c10-utkomststod/prepare_assets.py').read_text().replace('Textgrafik: exakta ord och tal ur källtexten.','Original källbaserad schematisk grafik: Homebrew video studio.'));print('Prepared',len(assets),'distinct pictures;',len(screen),'photographic/object sources for43slides.')
