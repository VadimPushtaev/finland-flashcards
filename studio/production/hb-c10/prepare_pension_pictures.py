"""Draw exact source-qualified pension relationships and preserve licensed photographs."""
from pathlib import Path
import json,yaml,hashlib,re,math
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parents[3];SID='hb-c10-pension';E=R/'studio/episodes'/SID;M=R/'studio/media'/SID;O=M/'pictures';O.mkdir(parents=True,exist_ok=True)
ns={'__file__':str(Path(__file__))};exec(compile((R/'studio/production/hb-c10/author_utkomststod.py').read_text().split('specs=')[0],'access-primitives','exec'),ns);code=(R/'studio/production/hb-c10/prepare_folkhalsa_pictures.py').read_text();exec(compile(code[code.index('def heart'):code.index('photos=json.loads')],'health-objects','exec'),ns);code=(R/'studio/production/hb-c10/prepare_vard_pictures.py').read_text();exec(compile(code[code.index('def envelope'):code.index('photos=json.loads',code.index('def envelope'))],'care-objects','exec'),ns)
canvas,label,house,person,coins,paper,arrow,heart,shield,cross,book,clinic,clock,group,magnify,record,folder,envelope,phone,card,no,calendar,doctor,hardhat=[ns[k] for k in ['canvas','label','house','person','coins','paper','arrow','heart','shield','cross','book','clinic','clock','group','magnify','record','folder','envelope','phone','card','no','calendar','doctor','hardhat']];FG,SOFT,GOLD,LINE,PANEL,BG=[ns[k] for k in ['FG','SOFT','GOLD','LINE','PANEL','BG']]
def info(p):return dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def globe(d,x,y,s=1):
    d.ellipse((x-75*s,y-75*s,x+75*s,y+75*s),outline=SOFT,width=5);d.ellipse((x-35*s,y-75*s,x+35*s,y+75*s),outline=GOLD,width=4);d.line((x-75*s,y,x+75*s,y),fill=GOLD,width=4)
photos=json.loads((E/'selected-photos.json').read_text());old=json.loads((E/'retained-photo-assets.json').read_text());script=yaml.safe_load((E/'script.yaml').read_text());plans=json.loads((E/'picture-plan.json').read_text());assets=[];downloads=[];screen=[];by_index={};aliases={10:9,19:18,35:34,44:42,56:55,61:23,76:75,84:13,89:7}

import runpy,textwrap
object_module=R/'studio/production/health-plans/medical_object_icons.py'
medical=runpy.run_path(str(object_module))['draw_medical_object']
def txt(d,x,y,text,size=28,width=300,color=FG):
    f=ImageFont.truetype(ns['FONT'],size);lines=[];line=''
    for word in text.split():
        candidate=(line+' '+word).strip()
        if line and d.textlength(candidate,font=f)>width:lines.append(line);line=word
        else:line=candidate
    if line:lines.append(line)
    for j,line in enumerate(lines):d.text((x,y+j*(size+6)),line,font=f,fill=color,anchor='mt')
def bubble(d,x,y,text,width=180):
    d.rounded_rectangle((x-width/2,y,x+width/2,y+80),radius=17,outline=GOLD,width=4);d.line([(x-15,y+80),(x-25,y+100),(x+15,y+80)],fill=GOLD,width=4);txt(d,x,y+20,text,28,width-20)
def boundary(d,x,y,s=.9):
    person(d,x,y,s);d.ellipse((x-100*s,y-100*s,x+100*s,y+155*s),outline=GOLD,width=5)
def baby(d,x,y,s=1):
    d.ellipse((x-25*s,y-68*s,x+25*s,y-18*s),outline=SOFT,width=5);d.polygon([(x,y-10*s),(x+55*s,y+35*s),(x,y+115*s),(x-55*s,y+35*s)],outline=GOLD,width=5);d.line((x-40*s,y+25*s,x+25*s,y+65*s),fill=SOFT,width=4)
def blister(d,x,y,s=1):
    d.rounded_rectangle((x-65*s,y-90*s,x+65*s,y+90*s),radius=15,outline=SOFT,width=5)
    for dx in[-30,30]:
        for dy in[-55,0,55]:d.ellipse((x+(dx-13)*s,y+(dy-18)*s,x+(dx+13)*s,y+(dy+18)*s),outline=GOLD,width=4)
def tick(d,x,y):d.line([(x-22,y),(x-4,y+20),(x+30,y-25)],fill=GOLD,width=7)

def bottle(d,x,y,s=1):
    d.line([(x-16*s,y-85*s),(x-16*s,y-40*s),(x-40*s,y-15*s),(x-40*s,y+95*s),(x+40*s,y+95*s),(x+40*s,y-15*s),(x+16*s,y-40*s),(x+16*s,y-85*s),(x-16*s,y-85*s)],fill=SOFT,width=5);d.rectangle((x-23*s,y+15*s,x+23*s,y+55*s),outline=GOLD,width=4)
def lock(d,x,y,s=1):
    d.rounded_rectangle((x-55*s,y,x+55*s,y+85*s),radius=12,outline=GOLD,width=5);d.arc((x-35*s,y-65*s,x+35*s,y+20*s),180,360,fill=SOFT,width=5);d.ellipse((x-6*s,y+28*s,x+6*s,y+40*s),fill=GOLD);d.line((x,y+38*s,x,y+57*s),fill=GOLD,width=5)
def capsule(d,x,y,s=1):
    d.rounded_rectangle((x-65*s,y-30*s,x+65*s,y+30*s),radius=30*s,outline=SOFT,width=5);d.line((x,y-28*s,x,y+28*s),fill=GOLD,width=5)
def suitcase(d,x,y,s=1):
    d.rounded_rectangle((x-65*s,y-60*s,x+65*s,y+75*s),radius=14,outline=SOFT,width=5);d.arc((x-25*s,y-90*s,x+25*s,y-40*s),180,360,fill=GOLD,width=5);d.ellipse((x-50*s,y+73*s,x-35*s,y+88*s),fill=GOLD);d.ellipse((x+35*s,y+73*s,x+50*s,y+88*s),fill=GOLD)
def scale(d,x,y,s=1):
    d.line((x,y-85*s,x,y+85*s),fill=SOFT,width=6);d.line((x-90*s,y-45*s,x+90*s,y-45*s),fill=GOLD,width=5)
    for xx in[x-70*s,x+70*s]:d.line((xx,y-45*s,xx-35*s,y+35*s,xx+35*s,y+35*s,xx,y-45*s),fill=SOFT,width=4)
    d.line((x-50*s,y+85*s,x+50*s,y+85*s),fill=SOFT,width=6)
def aclinic(d,x,y,s=1):clinic(d,x,y,s);txt(d,x,y+120*s,'A-klinik',28,220)
def candle(d,x,y,s=1):
    d.rectangle((x-25*s,y-15*s,x+25*s,y+100*s),outline=SOFT,width=5);d.ellipse((x-13*s,y-65*s,x+13*s,y-20*s),outline=GOLD,width=5)
def monitor(d,x,y,s=1):
    d.rounded_rectangle((x-90*s,y-65*s,x+90*s,y+45*s),radius=10,outline=SOFT,width=5);d.line((x,y+45*s,x,y+85*s),fill=SOFT,width=5);d.line((x-45*s,y+85*s,x+45*s,y+85*s),fill=GOLD,width=5)
def chairs(d,x,y,s=1):
    for dx in[-70,70]:
        xx=x+dx*s;d.rounded_rectangle((xx-35*s,y-60*s,xx+35*s,y+5*s),radius=10,outline=SOFT,width=5);d.line((xx-40*s,y+10*s,xx+40*s,y+10*s),fill=GOLD,width=6)
        for dd in[-28,28]:d.line((xx+dd*s,y+10*s,xx+dd*s,y+65*s),fill=SOFT,width=5)

def institution(d,x,y,s=1):
    d.polygon([(x-80*s,y-50*s),(x,y-95*s),(x+80*s,y-50*s)],outline=GOLD,width=5)
    for dx in[-55,0,55]:d.line((x+dx*s,y-35*s,x+dx*s,y+75*s),fill=SOFT,width=6)
    d.line((x-90*s,y+85*s,x+90*s,y+85*s),fill=GOLD,width=6)
def pension(d,x,y,s=1):
    paper(d,x,y,130*s,165*s);coins(d,x,y+100*s,2)
def pause(d,x,y,s=1):
    for dx in[-28,28]:d.rectangle((x+(dx-10)*s,y-50*s,x+(dx+10)*s,y+50*s),fill=GOLD)
def timeline(d,y):
    d.line((100,y,660,y),fill=SOFT,width=6);arrow(d,(600,y),(660,y))
def quarter(d,x,y,fraction):
    d.ellipse((x-95,y-95,x+95,y+95),outline=SOFT,width=5);d.pieslice((x-92,y-92,x+92,y+92),-90,-90+360*fraction,fill=GOLD)
titles={0:'Ålderspension vid pensionsålder',1:'Födelseåret påverkar',2:'Ett exempel ur källan',4:'Arbetspensionens utbetalare',5:'Lön och andra arbetsinkomster',6:'Om arbetspensionen är liten',8:'Arbetsinkomst och ålderspension',9:'Ny intjänad pension',11:'Kontrollera dina pensionsåldrar',12:'Du måste själv ansöka',15:'Inkomst och arbetsår',16:'Tre typer av pensionsanstalter',17:'Centraliserade pensionsfrågor',18:'Kontrollera arbetspensionsutdraget',20:'Ansöka om folkpension',21:'Tid i Finland',22:'Flera faktorer påverkar beloppet',24:'Båda villkoren för att ansöka',25:'Tid i ett annat EU- eller EES-land',26:'Existensminimum',27:'Garantipensionens belopp',28:'När övriga pensioner överstiger',29:'Företagarens pensionsförsäkring',30:'Familjepension efter dödsfall',31:'FöPL påverkar flera belopp',32:'Möjligt tillägg från FPA',34:'Länder utan socialskyddsavtal',37:'Tillfälligt utomlands',38:'Flytta utomlands över ett år',39:'Garantipension till utlandet',40:'Undantag i vissa fall',41:'Exempel på avtalsländer',42:'Partiell förtida ålderspension',43:'Födelseåret avgör åldersgränsen',45:'En fjärdedel eller hälften',46:'Heltid eller kortare arbetstid',47:'Du kan också sluta arbeta',48:'Permanent mindre slutlig pension',50:'Först vanligtvis sjukdagpenning',51:'Om du inte kan återgå till arbetet',52:'Delvis nedsatt arbetsförmåga',53:'Hälften av sjukpensionen',54:'Fråga om tillåten arbetsinkomst',55:'Låta pensionen vila',57:'Pausens längd',58:'Rätten finns kvar under pausen',60:'Vårdbidrag för pensionstagare',63:'Fyllda 65 år och identitetsbevis',64:'Pensionär under 65 år',67:'Pensionssystemets tre delar',68:'Exempel på kombinerad pension',69:'Största delen är arbetspension',70:'Avgifter från lönen',71:'Arbetstagare och arbetsgivare',72:'Lön och arbetsår påverkar',73:'Arbetspensionsanstalten betalar',74:'Företagare betalar själva',75:'Invalidpension vid arbetsoförmåga',77:'Full eller partiell invalidpension',78:'Partiell pension och deltidsarbete',79:'Lön och pension tillsammans',80:'Pension från flera länder',81:'I allmänhet genom arbete',82:'Samma blankett i en del länder',83:'Direkt ansökan i andra länder',85:'Meddela FPA om utlandsflytt',86:'Utbetalning utomlands på villkor',87:'Kontrollera villkoren i förväg',88:'Pension i Finland från annat land',90:'Arbete ökar arbetspensionen',91:'Deltid eller heltid som pensionär',92:'Begränsat arbete vid invalidpension',93:'Inkomstgräns och avbruten betalning'}
for i,row in enumerate(script['sentences']):
    if i in aliases:continue
    key=f'picture-{i+1:03}';dest=O/f'sentence-{i+1:02}.png'
    if str(i) in photos or str(i) in old:
        if str(i) in photos:
            p=photos[str(i)];pi=p['imageinfo'];meta=pi['extmetadata'];clean=lambda k:re.sub('<[^>]+>','',meta.get(k,{}).get('value','')).strip();raw=R/p['path'];creator=clean('Artist');terms=clean('LicenseShortName')+' '+clean('LicenseUrl');source=pi['descriptionurl'];credit=p['title'].removeprefix('File:')+' — '+creator+'. '+terms+'. '+source+'. Complete photograph proportionally resized and letterboxed; original terms retained.';context=p['context'];url=p['download_url'];screen.append(p['title'].removeprefix('File:')+' — '+creator+' · '+clean('LicenseShortName'))
        else:
            p=old[str(i)];a=p['asset_record'];raw=R/p['path'];creator=a['creator'];terms=a['reuse_terms'];source=a['source_url'];credit=a['required_credits'];context=p['context'];url=p['url'];screen.append(Path(raw).stem+' — '+creator+' · '+terms.split('https:')[0])
        image=ImageOps.exif_transpose(Image.open(raw)).convert('RGB');image.thumbnail((760,720),Image.Resampling.LANCZOS);im=Image.new('RGB',(760,720),BG);im.paste(image,((760-image.width)//2,(720-image.height)//2));im.save(dest);downloads.append(dict(**info(raw),url=url));a=dict(asset_id=key,kind='foreground',visual_type='photograph',files=[info(dest)],creator=creator,reuse_terms=terms,source_url=source,required_credits=credit,relevance_verification=context,creation_method=dict(tool=str(Path(__file__).relative_to(R)),transform='Complete source photograph proportionally resized,EXIF orientation respected,letterboxed.'))
    else:
        im,d=canvas(titles[i])
        if i==0:
            timeline(d,380);clock(d,220,270,1.15);pension(d,580,300,1.1);d.line((440,225,440,500),fill=GOLD,width=6);txt(d,260,485,'pensionsålder',31,280);txt(d,580,545,'KAN få pension',29,280)
        elif i==1:
            calendar(d,195,315,1.3);txt(d,195,490,'födelseår',31);arrow(d,(315,350),(445,350));clock(d,575,320,1.25);txt(d,575,490,'åldersgräns',30);txt(d,380,605,'beror på när du är född',29,620)
        elif i==2:
            txt(d,380,165,'TILL EXEMPEL',32,620);calendar(d,195,340,1.35);txt(d,195,345,'1964',41,220);arrow(d,(330,350),(440,350));d.ellipse((475,250,675,450),outline=GOLD,width=6);txt(d,575,310,'65 år',43,190);txt(d,380,585,'födelseår → pensionsålder',30,620)
        elif i==4:
            institution(d,200,300,1.2);arrow(d,(320,355),(450,355));pension(d,580,310,1.1);txt(d,200,510,'arbetspensionsanstalt',25,300);txt(d,580,550,'arbetspension',28)
        elif i==5:
            coins(d,175,275,3);paper(d,580,270,165,200);txt(d,175,390,'lön',30);txt(d,580,395,'andra arbetsinkomster',25,290);arrow(d,(175,440),(300,535));arrow(d,(580,440),(460,535));pension(d,380,530,.6);txt(d,380,150,'arbetspensionens grund',30,620)
        elif i==6:
            coins(d,190,330,1);txt(d,190,475,'liten arbetspension',27,290);arrow(d,(310,355),(450,355));institution(d,575,315,1.1);txt(d,575,470,'FPA',36);txt(d,380,590,'KAN också få pension från FPA',29,620)
        elif i==8:
            hardhat(d,175,280,1);coins(d,175,460,3);pension(d,570,295,1.1);d.line((330,330,435,330),fill=GOLD,width=6);d.line((330,375,435,375),fill=GOLD,width=6);txt(d,380,160,'OM du får ÅLDERSPENSION',29,620);txt(d,380,595,'arbetsinkomst ändrar inte dess storlek',27,620)
        elif i==9:
            timeline(d,315);hardhat(d,175,235,.8);paper(d,360,245,115,150);txt(d,360,405,'ny pension',27,200);d.line((510,160,510,530),fill=GOLD,width=7);pension(d,620,330,.65);txt(d,310,535,'högsta pensionsåldern',30,570);txt(d,380,590,'ny intjäning slutar · intjänad pension betalas',25,620)
        elif i==11:
            monitor(d,380,295,1.55);txt(d,380,270,'lägsta / högsta',30,260);institution(d,190,485,.65);institution(d,580,485,.65);txt(d,190,595,'Pensionsskyddscentralen',22,300);txt(d,580,595,'arbetspensionsanstalten',22,300);txt(d,380,155,'TILL EXEMPEL räknare hos',29,620)
        elif i==12:
            person(d,140,310,.8);paper(d,365,320,150,200);institution(d,620,300,.85);arrow(d,(225,355),(265,355));arrow(d,(465,355),(525,355));txt(d,365,470,'ansökan',30,200);txt(d,380,550,'DU måste själv ansöka',31,620);txt(d,380,610,'utbetalning börjar INTE automatiskt',27,620)
        elif i==15:
            coins(d,175,285,3);arrow(d,(245,330),(245,190));calendar(d,570,285,.95);d.line((485,445,655,445),fill=GOLD,width=6);arrow(d,(600,445),(655,445));txt(d,175,395,'högre lön / företagarinkomst',25,285);txt(d,570,485,'längre arbete',28,285);arrow(d,(230,520),(320,570));arrow(d,(530,530),(440,570));pension(d,380,570,.45);txt(d,380,150,'större arbetspension',31,620)
        elif i==16:
            for x in[160,380,600]:institution(d,x,290,.8)
            for x,t in[(160,'försäkringsbolag'),(380,'pensionskassor'),(600,'pensionsstiftelser')]:txt(d,x,455,t,25,210)
            txt(d,380,585,'arbetspensionsförsäkringar',29,620)
        elif i==17:
            institution(d,380,320,1.15);txt(d,380,160,'Pensionsskyddscentralen',31,620)
            for x,y in[(160,255),(600,255),(160,505),(600,505)]:paper(d,x,y,100,125);d.line((x+(65 if x<380 else-65),y,380+(105 if x>380 else-105),350),fill=LINE,width=4)
            txt(d,380,610,'centraliserade frågor om pensionsskydd',26,620)
        elif i==18:
            paper(d,240,300,215,280);magnify(d,330,390,1.2);txt(d,240,510,'alla förvärvsinkomster',26,310);institution(d,595,325,.95);d.line((440,330,490,330),fill=GOLD,width=5);txt(d,555,200,'OM fel',30,220);txt(d,595,500,'kontakta pensionsanstalt',24,255);txt(d,380,610,'följ själv upp ditt utdrag',29,620)
        elif i==20:
            coins(d,190,270,2);no(d,190,260,95);coins(d,570,270,1);txt(d,190,415,'ingen arbetspension',26,290);txt(d,570,415,'väldigt liten',28,290);txt(d,380,280,'ELLER',29,180);arrow(d,(190,470),(300,535));arrow(d,(570,470),(460,535));paper(d,380,535,155,100);txt(d,380,615,'KAN ANSÖKA om folkpension',28,620)
        elif i==21:
            house(d,175,260,.9);hardhat(d,575,285,.9);txt(d,380,285,'ELLER',27,180);calendar(d,380,475,.9);d.line((175,405,295,475),fill=LINE,width=4);d.line((575,405,465,475),fill=LINE,width=4);txt(d,380,155,'tid bosatt eller arbetat i Finland',28,620);txt(d,380,610,'påverkar folkpensionens belopp',28,620)
        elif i==22:
            group(d,190,275,.7);pension(d,570,290,.8);txt(d,190,440,'familjeförhållanden',26,290);txt(d,570,470,'andra kontinuerliga pensioner',25,290);arrow(d,(190,505),(300,560));arrow(d,(570,525),(460,560));coins(d,380,560,2);txt(d,380,610,'påverkar folkpensionens belopp',28,620)
        elif i==24:
            d.rounded_rectangle((65,155,695,615),radius=20,outline=GOLD,width=5);shield(d,190,290,1.05);calendar(d,570,275,.95);txt(d,380,285,'OCH',29,170);txt(d,190,445,'finländska socialskyddet',25,260);txt(d,570,420,'minst 3 år i Finland efter fyllda 16 år',25,260);txt(d,380,555,'KAN ANSÖKA om folk-/garantipension',26,570)
        elif i==25:
            globe(d,190,320,1.25);calendar(d,565,305,1.05);d.line((305,350,455,350),fill=GOLD,width=5);txt(d,190,515,'annat EU- eller EES-land',25,290);txt(d,565,485,'bosättningstid',28,290);txt(d,380,610,'KAN DELVIS beaktas',31,620)
        elif i==26:
            pension(d,180,320,.95);shield(d,555,340,1.8);house(d,555,315,.65);d.line((300,355,440,355),fill=GOLD,width=5);txt(d,380,590,'garantipension tryggar existensminimum',27,620)
        elif i==27:
            # Same unnumbered basis:other pensions plus the gap to the full guarantee.
            d.rectangle((170,190,360,560),outline=SOFT,width=5);d.rectangle((176,365,354,554),fill=LINE);d.rectangle((176,196,354,359),fill=GOLD);d.line((380,190,660,190),fill=GOLD,width=5);txt(d,540,215,'full garantipension',28,290);txt(d,545,325,'garantipension',29,290);txt(d,545,430,'övriga pensioner',28,290);d.line((370,275,435,325),fill=GOLD,width=4);d.line((370,460,435,460),fill=SOFT,width=4);txt(d,380,615,'skillnaden till fulla beloppet',28,620)
        elif i==28:
            d.line((90,355,665,355),fill=GOLD,width=5);d.rectangle((160,205,300,530),outline=SOFT,width=5);d.rectangle((166,211,294,524),fill=LINE);txt(d,510,370,'full garantipension',27,310);txt(d,230,560,'övriga pensioner',27,280);coins(d,565,230,2);no(d,565,230,95);txt(d,380,155,'OM övriga pensioner är ÖVER fulla beloppet',25,620);txt(d,380,610,'kan INTE få garantipension',29,620)
        elif i==29:
            pension(d,190,285,.95);hardhat(d,570,285,1);no(d,570,305,100);txt(d,190,440,'sjukpension ELLER ålderspension',25,275);txt(d,570,440,'företagsverksamheten upphör',25,275);txt(d,380,305,'OCH',28,170);arrow(d,(190,515),(310,560));arrow(d,(570,515),(450,560));coins(d,380,555,2);txt(d,380,155,'BÅDA VILLKOREN',30,620);txt(d,380,610,'FöPL tryggar försörjningen',29,620)
        elif i==30:
            candle(d,190,320,1.1);group(d,565,285,.75);arrow(d,(300,365),(440,365));pension(d,565,500,.6);txt(d,190,520,'företagaren avlider',27,290);txt(d,380,610,'anhöriga KAN få familjepension',28,620)
        elif i==31:
            paper(d,380,260,140,140);txt(d,380,365,'FöPL',33,220)
            txt(d,380,155,'påverkar belopp · TILL EXEMPEL',29,620)
            d.line((190,410,570,410),fill=LINE,width=3);d.line((380,410,380,530),fill=LINE,width=3);d.line((190,530,570,530),fill=LINE,width=3)
            for x,y,t in[(190,445,'arbetspension'),(570,445,'sjukdagpenning'),(190,565,'arbetslöshetsförmån'),(570,565,'föräldradagpenning')]:
                coins(d,x,y,1);txt(d,x,y+40,t,23,300)
        elif i==32:
            coins(d,180,290,1);txt(d,180,440,'liten arbetspension',26,270);institution(d,570,285,1);d.line((285,350,460,350),fill=GOLD,width=5);pension(d,470,490,.55);pension(d,650,490,.55);txt(d,560,470,'ELLER',25,140);txt(d,460,605,'folkpension',23,190);txt(d,650,605,'garantipension',22,190);txt(d,380,155,'KAN få tillägg från FPA',29,620)
        elif i==34:
            globe(d,170,290,1);paper(d,590,300,130,150);no(d,590,300,80);txt(d,590,410,'inget socialskyddsavtal',25,290);magnify(d,170,465,.8);paper(d,390,485,130,120);d.line((250,475,305,485),fill=GOLD,width=4);txt(d,380,155,'OM du arbetat i ett land utan avtal',28,620);txt(d,380,605,'utred rätten själv → ansök OM rätt finns',26,620)
        elif i==37:
            globe(d,180,300,1.15);calendar(d,560,275,1.1);txt(d,560,440,'UNDER 1 år',31,280);pension(d,380,510,.65);txt(d,380,610,'FPA betalar VANLIGTVIS som vanligt',27,620)
        elif i==38:
            globe(d,175,295,1.15);calendar(d,570,275,1.05);txt(d,570,435,'ÖVER 1 år',32,280);pension(d,380,510,.6);no(d,380,535,85);txt(d,380,155,'flytta utomlands',31,620);txt(d,380,610,'VANLIGTVIS INTE FPA:s ålders-/invalidpension',24,620)
        elif i==39:
            pension(d,185,310,1.1);globe(d,580,335,1.3);d.line((320,350,450,350),fill=LINE,width=5);no(d,385,350,55);txt(d,185,535,'garantipension',29,280);txt(d,580,535,'utlandet',31,280);txt(d,380,610,'FPA betalar INTE garantipension dit',27,620)
        elif i==40:
            paper(d,190,320,185,240);txt(d,190,485,'socialskyddsavtal',27,285);globe(d,580,300,1.25);pension(d,580,500,.6);arrow(d,(310,355),(450,355));txt(d,380,155,'I VISSA FALL',32,620);txt(d,380,610,'FPA KAN betala pension till avtalsländer',26,620)
        elif i==41:
            globe(d,380,275,1.3)
            for x,y,t in[(160,445,'USA'),(380,445,'Kanada'),(600,445,'Israel'),(270,535,'Chile'),(510,535,'Australien')]:txt(d,x,y,t,30,200)
            txt(d,380,155,'EXEMPEL · inte en fullständig lista',28,620)
        elif i==42:
            timeline(d,365);txt(d,200,245,'61 ELLER 62 år',32,280);d.line((510,205,510,500),fill=GOLD,width=6);pension(d,220,445,.6);txt(d,555,525,'lägsta pensionsålder',25,270);txt(d,380,155,'åldersgräns BEROR PÅ födelseår',28,620);txt(d,380,610,'PARTIELL FÖRTIDA ålderspension',28,620)
        elif i==43:
            calendar(d,380,245,1.1);txt(d,380,390,'födelseår',30,300);arrow(d,(300,420),(210,500));arrow(d,(460,420),(550,500));txt(d,200,525,'61 år',37,220);txt(d,570,525,'62 år',37,220);txt(d,380,535,'ELLER',26,130);txt(d,380,610,'gränsen för partiell förtida pension',27,620)
        elif i==45:
            quarter(d,200,340,.25);quarter(d,565,340,.5);txt(d,200,495,'25 procent',32,280);txt(d,565,495,'50 procent',32,280);txt(d,380,335,'ELLER',26,150);txt(d,380,155,'DU VÄLJER',32,620);txt(d,380,610,'av månatlig ARBETSPENSION',29,620)
        elif i==46:
            person(d,170,290,.9);clock(d,170,460,.65);person(d,525,285,.8);person(d,635,285,.8);paper(d,580,480,160,150);txt(d,380,340,'ELLER',27,160);txt(d,170,565,'fortsätta heltid',27,270);txt(d,580,575,'avtal om kortare arbetstid',25,280);txt(d,380,155,'OM DU VILL',32,620)
        elif i==47:
            hardhat(d,210,315,1.3);no(d,210,335,125);person(d,570,305,1.15);txt(d,380,155,'du KAN också',31,620);txt(d,380,610,'sluta arbeta',33,620)
        elif i==48:
            pension(d,250,315,1.5);arrow(d,(450,245),(450,470));lock(d,610,320,1.05);txt(d,380,155,'partiell FÖRTIDA ålderspension',29,620);txt(d,380,565,'slutlig ålderspension minskar',29,620);txt(d,380,615,'PERMANENT',31,620)
        elif i==50:
            record(d,175,280,'långvarigt sjuk',.9);arrow(d,(295,350),(450,350));calendar(d,570,285,1.1);coins(d,570,485,2);txt(d,380,155,'VANLIGTVIS FÖRST sjukdagpenning',28,620);txt(d,380,610,'UNGEFÄR ett år',32,620)
        elif i==51:
            hardhat(d,150,280,.85);no(d,150,300,100);txt(d,150,445,'sjukdom / skada',25,220);paper(d,370,300,140,190);txt(d,370,445,'ansökan',27,180);d.line((460,300,565,220),fill=GOLD,width=4);d.line((460,330,565,460),fill=GOLD,width=4);pension(d,615,220,.55);paper(d,615,470,110,140);txt(d,615,355,'sjukpension',23,190);txt(d,615,570,'rehabiliteringsstöd',21,230);txt(d,380,155,'OM du inte kan återgå till arbetet',28,620);txt(d,380,610,'KAN ansöka om det ena ELLER andra',27,620)
        elif i==52:
            person(d,190,285,.9);d.line((110,445,270,445),fill=GOLD,width=5);clock(d,570,310,1);txt(d,190,485,'nedsatt arbetsförmåga',25,280);txt(d,570,485,'kan ändå arbeta deltid',25,280);txt(d,380,315,'OCH',28,160);pension(d,380,540,.45);txt(d,380,610,'partiell sjukpension tryggar försörjningen',25,620)
        elif i==53:
            quarter(d,210,335,.5);pension(d,570,300,1.15);txt(d,210,500,'hälften',32,270);txt(d,570,550,'sjukpension',29,280);txt(d,380,155,'partiell sjukpension',32,620);txt(d,380,610,'samma grund: hälften av sjukpensionen',26,620)
        elif i==54:
            hardhat(d,175,260,.9);pension(d,175,465,.75);coins(d,440,300,3);txt(d,590,275,'?',80,130);d.line((390,430,640,430),fill=GOLD,width=5);institution(d,470,530,.5);institution(d,640,530,.5);txt(d,380,155,'OM arbete / företag samtidigt som sjukpension',25,620);txt(d,380,610,'fråga FPA ELLER pensionsanstalten: hur mycket?',24,620)
        elif i==55:
            coins(d,190,300,4);arrow(d,(300,350),(450,350));pension(d,575,300,1.1);pause(d,575,505,.8);txt(d,190,460,'tillräckligt hög månadsinkomst',25,280);txt(d,380,155,'OM arbetsinkomsten räcker',29,620);txt(d,380,610,'KAN låta pensionens utbetalning vila',27,620)
        elif i==57:
            timeline(d,365);pause(d,380,270,1);d.line((190,340,190,390),fill=GOLD,width=7);d.line((570,340,570,390),fill=GOLD,width=7);txt(d,190,445,'MINST 3 månader',29,280);txt(d,570,445,'HÖGST 2 år',30,280);txt(d,380,610,'paus i pensionens utbetalning',29,620)
        elif i==58:
            pension(d,210,300,1.2);shield(d,210,350,1.8);pause(d,580,305,1.2);coins(d,580,475,2);txt(d,210,550,'rätten KVAR',30,280);txt(d,580,555,'utbetalning pausad',27,280);txt(d,380,610,'UNDER denna paus',30,620)
        elif i==60:
            record(d,190,270,'långtidssjuk',.9);person(d,570,275,.85);shield(d,570,330,.85);txt(d,570,450,'handikapp',27,280);txt(d,380,305,'ELLER',27,160);arrow(d,(190,500),(300,555));arrow(d,(570,500),(460,555));coins(d,380,555,2);txt(d,380,610,'FPA KAN betala vårdbidrag för pensionstagare',25,620)
        elif i==63:
            person(d,180,300,1);txt(d,180,485,'fyllt 65 år',32,270);paper(d,570,315,190,250);person(d,570,280,.45);txt(d,570,500,'identitetsbevis',29,280);txt(d,380,330,'OCH',28,170);txt(d,380,610,'uppvisa bevis för reserabatt',29,620)
        elif i==64:
            txt(d,380,155,'pensionär UNDER 65 år',31,620);paper(d,160,330,145,230);txt(d,160,495,'personbevis',28,245);d.rounded_rectangle((370,205,730,580),radius=18,outline=GOLD,width=5);paper(d,455,330,110,180);paper(d,650,330,110,180);txt(d,455,470,'arbetspensionskort',19,180);txt(d,650,470,'folkpensionärskort',19,180);txt(d,550,315,'ELLER',24,80);txt(d,300,330,'OCH',26,100);txt(d,380,610,'personbevis OCH ett av de två korten',27,620)
        elif i==67:
            for x,t in[(160,'arbetspension'),(380,'folkpension'),(600,'garantipension')]:pension(d,x,300,.85);txt(d,x,510,t,26,215)
            d.line((80,585,680,585),fill=GOLD,width=5);txt(d,380,610,'pensionssystemets TRE delar',29,620)
        elif i==68:
            pension(d,200,285,1);pension(d,570,330,.6);txt(d,380,325,'+',54,140);txt(d,200,505,'arbetspension',28,285);txt(d,570,505,'PARTIELL folkpension',26,285);txt(d,380,155,'OFTA flera typer · TILL EXEMPEL',29,620);txt(d,380,610,'partiell FOLKPENSION i detta exempel',26,620)
        elif i==69:
            # A qualitative grouping gives no numerical share.
            pension(d,210,300,1.05);pension(d,570,300,.65);d.arc((95,190,325,535),180,355,fill=GOLD,width=6);txt(d,210,540,'arbetspensioner',29,285);txt(d,570,540,'andra pensioner',27,285);txt(d,380,610,'största delen är arbetspensioner',28,620)
        elif i==70:
            paper(d,160,270,155,200);txt(d,160,420,'lön',32,220);coins(d,390,325,3);pension(d,625,300,.8);arrow(d,(260,330),(300,330));arrow(d,(475,330),(545,330));txt(d,390,490,'betalda pensionsavgifter',25,260);txt(d,380,610,'grund för arbetspensionens belopp',28,620)
        elif i==71:
            person(d,190,275,.9);institution(d,570,280,.95);coins(d,380,510,3);arrow(d,(190,445),(300,505));arrow(d,(570,440),(460,505));txt(d,190,420,'arbetstagaren',27,280);txt(d,570,430,'arbetsgivaren',27,280);txt(d,380,605,'en del av avgifterna från vardera',28,620)
        elif i==72:
            coins(d,190,280,3);calendar(d,570,285,1.1);txt(d,190,420,'lönens nivå',29,280);txt(d,570,465,'antal arbetsår',29,280);d.line((190,495,380,550,570,510),fill=GOLD,width=5);pension(d,380,550,.45);txt(d,380,155,'BLAND ANNAT',31,620);txt(d,380,610,'påverkar pensionens belopp',29,620)
        elif i==73:
            institution(d,380,260,1.4);d.line((380,390,380,470),fill=GOLD,width=5);coins(d,380,520,4);txt(d,380,150,'arbetspensionsanstalten',30,620);txt(d,380,610,'betalar ARBETSPENSION',30,620)
        elif i==74:
            person(d,175,340,.8);hardhat(d,175,245,.55);coins(d,395,385,3);institution(d,620,340,.8);arrow(d,(265,400),(305,400));arrow(d,(475,400),(535,400));txt(d,380,155,'företagare KAN få arbetspension',29,620);txt(d,380,565,'pensionsavgifterna betalas SJÄLV',29,620)
        elif i==75:
            hardhat(d,175,285,1.1);no(d,175,310,115);record(d,390,290,'sjukdom / skada',.8);pension(d,620,310,.85);arrow(d,(475,355),(535,355));txt(d,380,155,'OM du inte längre kan arbeta på grund av',26,620);txt(d,380,610,'KAN få invalidpension från pensionsanstalt',25,620)
        elif i==77:
            pension(d,210,300,1.15);pension(d,570,300,.65);txt(d,380,325,'ELLER',28,170);txt(d,210,550,'full',32,280);txt(d,570,550,'partiell',32,280);txt(d,380,155,'invalidpension KAN vara',30,620)
        elif i==78:
            person(d,190,290,.9);clock(d,190,470,.75);pension(d,570,310,.75);d.line((300,360,455,360),fill=GOLD,width=5);txt(d,190,565,'deltidsarbete',29,280);txt(d,570,540,'partiell invalidpension',25,285)
        elif i==79:
            coins(d,190,300,3);pension(d,570,290,.9);txt(d,380,325,'+',57,130);d.rounded_rectangle((125,490,635,590),radius=18,outline=GOLD,width=5);txt(d,380,520,'inkomst = lön + pension',31,470)
        elif i==80:
            globe(d,380,240,1.15)
            for x,y in[(170,445),(380,490),(590,445)]:house(d,x,y,.5);hardhat(d,x,y-70,.45);d.line((380,335,x,y-110),fill=LINE,width=4)
            txt(d,380,610,'KAN tjäna in pension där man bott och arbetat',25,620)
        elif i==81:
            hardhat(d,220,275,1.2);calendar(d,220,455,.8);arrow(d,(340,355),(450,355));pension(d,580,315,1.1);txt(d,380,155,'I ALLMÄNHET',32,620);txt(d,380,610,'tjäna in pension genom arbete',29,620)
        elif i==82:
            paper(d,380,345,185,210);txt(d,380,515,'SAMMA blankett',30,330);globe(d,170,300,.7);house(d,610,265,.8);d.line((240,335,280,335),fill=GOLD,width=5);d.line((480,335,530,335),fill=GOLD,width=5);txt(d,380,155,'EN DEL länder',32,620);txt(d,380,610,'som vid ansökan om pension i Finland',27,620)
        elif i==83:
            person(d,160,310,.8);paper(d,380,300,140,190);institution(d,620,290,.85);arrow(d,(245,350),(285,350));arrow(d,(470,350),(525,350));globe(d,620,510,.55);txt(d,380,155,'EN DEL andra länders pensioner',29,620);txt(d,380,610,'ansök DIREKT hos det landets pensionsanstalt',25,620)
        elif i==85:
            house(d,170,265,.85);suitcase(d,380,320,.95);globe(d,590,280,.9);d.line((250,350,300,350),fill=GOLD,width=5);d.line((460,350,510,350),fill=GOLD,width=5);envelope(d,380,520,.8);txt(d,380,155,'OM pensionären flyttar utomlands',28,620);txt(d,380,610,'ALLTID anmäla det till FPA',30,620)
        elif i==86:
            pension(d,190,310,1.15);globe(d,580,335,1.3);d.line((320,350,445,350),fill=LINE,width=5);paper(d,380,500,135,150);txt(d,380,610,'KAN fås utomlands PÅ VISSA VILLKOR',27,620)
        elif i==87:
            suitcase(d,175,325,1.2);clock(d,380,300,.8);paper(d,590,300,175,235);magnify(d,625,445,.85);txt(d,590,520,'villkor',31,280);txt(d,380,610,'ta reda på I FÖRVÄG om de uppfylls',27,620)
        elif i==88:
            globe(d,180,295,1.15);person(d,180,440,.55);paper(d,390,320,145,200);house(d,610,275,.9);arrow(d,(285,355),(295,355));arrow(d,(485,355),(515,355));txt(d,610,465,'Finland',31,250);txt(d,380,155,'I VISSA FALL',32,620);txt(d,380,610,'KAN ANSÖKA vid pensionering i annat land',25,620)
        elif i==90:
            hardhat(d,175,290,1.15);arrow(d,(300,350),(450,350));pension(d,575,310,1.15);arrow(d,(670,470),(670,230));txt(d,380,155,'arbete som pensionär',31,620);txt(d,380,610,'ökar arbetspensionens belopp',29,620)
        elif i==91:
            calendar(d,200,300,1.25);clock(d,570,300,1.3);txt(d,200,515,'deltid',32,280);txt(d,570,515,'heltid',32,280);txt(d,380,325,'ELLER',28,160);txt(d,380,610,'som pensionär KAN man arbeta',29,620)
        elif i==92:
            pension(d,195,310,.9);hardhat(d,570,280,1);d.line((450,180,450,530),fill=GOLD,width=9);clock(d,570,465,.6);txt(d,380,155,'OM invalidpension',31,620);txt(d,380,610,'arbete ENDAST i begränsad utsträckning',26,620)
        elif i==93:
            coins(d,170,300,4);d.line((290,200,290,470),fill=GOLD,width=6);arrow(d,(235,325),(355,325));pause(d,550,310,1.1);pension(d,550,475,.65);txt(d,380,155,'OM arbetsinkomsten ÖVERSKRIDER viss gräns',25,620);txt(d,170,490,'inkomstgräns',27,240);txt(d,380,610,'utbetalningen KAN avbrytas',29,620)
        else:raise ValueError('Missing source-specific pension composition '+str(i))
        im.save(dest);refs=[row['sentence_id']]
        linked={9:[9,10],18:[18,19],34:[34,35],42:[42,43,44],43:[42,43],64:[62,63,64],68:[67,68],75:[75,76],77:[75,77],78:[77,78],79:[77,78,79]}
        if i in linked:refs=[script['sentences'][j]['sentence_id']for j in linked[i]]
        a=dict(asset_id=key,kind='foreground',visual_type='diagram',files=[info(dest)],creator='Homebrew video studio',reuse_terms='Original schematic artwork under repository MIT license;archived source wording retains publisher terms.',required_credits='Original source-based pension illustrations: Homebrew video studio;source wording credited in sources.yaml and CREDITS.md.',relevance_verification=plans[i]['request']+' Individually composed exact-source relationship. No invented pension age,contribution/tax rate,euro amount,foreign-country policy,earnings ceiling,diagnosis or award guarantee. Partial early old-age,partial national,and disability pension remain distinct.',creation_method=dict(tool=str(Path(__file__).relative_to(R)),source_sentence_ids=refs))
    assets.append(a);by_index[i]=a
for i,row in enumerate(script['sentences']):
    a=by_index[aliases.get(i,i)];row.update(asset_ids=['episode_background',a['asset_id']],render_image=a['files'][0]['path'],render_caption=False)
    if i in aliases:
        a['creation_method'].setdefault('source_sentence_ids',[script['sentences'][aliases[i]]['sentence_id']]).append(row['sentence_id']);row['visual_cue']='Retain this useful unchanged source picture for the directly related continuation/recap: '+plans[i]['request']
script['asset_requests']=script['asset_requests'][:3]+[dict(id=a['asset_id'],kind='foreground',description=a['relevance_verification'],fallback='Faithful useful original pictorial explanation limited to source;document omission if reasonable research cannot produce one.')for a in assets];script['render']['credits']=script['render']['credits'][:2]
for j in range(0,len(screen),2):script['render']['credits'].append(dict(heading='Förgrundsbilder · Изображения',paragraphs=screen[j:j+2]+['Original schematisk grafik: Homebrew video studio.','Fullständiga källor och licenser i CREDITS.md.']))
for decision in script['episode_decisions']:
    if decision['id']=='visuals':decision['decision']='All94source slides pictured with85distinct source pictures:13actual licensed photographs and72individually composed source diagrams. Nine meaningful direct continuations/recaps retain useful unchanged pictures. No real person assigned age,pension,illness,status or entitlement. Example1964→65is never universal;conditional applications,abroad rules,partial-pension categories and unspecified ceilings retain exact source scope.'
(E/'script.yaml').write_text(yaml.safe_dump(script,allow_unicode=True,sort_keys=False,width=100));(E/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');(E/'foreground-downloads.json').write_text(json.dumps(downloads,ensure_ascii=False,indent=2)+'\n');(E/'prepare_assets.py').write_text((R/'studio/episodes/hb-c10-utkomststod/prepare_assets.py').read_text().replace('Textgrafik: exakta ord och tal ur källtexten.','Original källbaserad grafik: Homebrew video studio.'));print('Prepared',len(assets),'distinct source pictures;',len(screen),'photos for94slides.')
