"""Draw isolated objects and qualified reproductive-health relationships without depicting acts."""
from pathlib import Path
import json,yaml,hashlib,re,math
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parents[3];SID='hb-c10-psykisk';E=R/'studio/episodes'/SID;M=R/'studio/media'/SID;O=M/'pictures';O.mkdir(parents=True,exist_ok=True)
ns={'__file__':str(Path(__file__))};exec(compile((R/'studio/production/hb-c10/author_utkomststod.py').read_text().split('specs=')[0],'access-primitives','exec'),ns);code=(R/'studio/production/hb-c10/prepare_folkhalsa_pictures.py').read_text();exec(compile(code[code.index('def heart'):code.index('photos=json.loads')],'health-objects','exec'),ns);code=(R/'studio/production/hb-c10/prepare_vard_pictures.py').read_text();exec(compile(code[code.index('def envelope'):code.index('photos=json.loads',code.index('def envelope'))],'care-objects','exec'),ns)
canvas,label,house,person,coins,paper,arrow,heart,shield,cross,book,clinic,clock,group,magnify,record,folder,envelope,phone,card,no,calendar,doctor,hardhat=[ns[k] for k in ['canvas','label','house','person','coins','paper','arrow','heart','shield','cross','book','clinic','clock','group','magnify','record','folder','envelope','phone','card','no','calendar','doctor','hardhat']];FG,SOFT,GOLD,LINE,PANEL,BG=[ns[k] for k in ['FG','SOFT','GOLD','LINE','PANEL','BG']]
def info(p):return dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def globe(d,x,y,s=1):
    d.ellipse((x-75*s,y-75*s,x+75*s,y+75*s),outline=SOFT,width=5);d.ellipse((x-35*s,y-75*s,x+35*s,y+75*s),outline=GOLD,width=4);d.line((x-75*s,y,x+75*s,y),fill=GOLD,width=4)
photos=json.loads((E/'selected-photos.json').read_text());old=json.loads((E/'retained-photo-assets.json').read_text());script=yaml.safe_load((E/'script.yaml').read_text());plans=json.loads((E/'picture-plan.json').read_text());assets=[];downloads=[];screen=[];by_index={};aliases={14:13,35:33,49:48,57:56,68:67}

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
titles={0:'Handlingskraft och förändringar',1:'Exempel på skyddande faktorer',2:'Lika viktigt att ta hand om',3:'Välbefinnande för nyanlända',4:'Belastande erfarenheter',5:'Flera möjliga belastningar',6:'Nytt språk och kulturella frågor',8:'Exempel på mentala störningar',9:'Boka först en tid',10:'Vilken hjälp behövs?',11:'En möjlig remiss',12:'Samtal och ofta medicinering',15:'Privat vård kostar mer',18:'Om ett barn behöver stöd',20:'Yrkesutbildade inom elevhälsan',22:'Källans rusmedelskontext',23:'Olagliga droger',24:'Innehav och försäljning',25:'Hjälp vid beroende',26:'Problem kan beröra flera',28:'Vård och rehabilitering',29:'Också närstående',30:'Gratis vård på A-kliniken',31:'Under behandlingen',32:'Hälsorådgivning i många städer',34:'Social- och hälsorådgivning',36:'Risk med smutsiga sprutor',37:'Via rådgivningen till vård',39:'Krävande livssituationer',40:'Kris och livsförändringar',41:'Också en positiv förändring',42:'Ibland först efteråt',43:'Tala med familj eller vänner',44:'Ibland professionell hjälp',45:'Vilket stöd passar dig?',46:'Olika möjliga behandlingar',48:'Ett konfidentiellt samtal',50:'Separat tillstånd till utlämnande',51:'Om du är orolig för en närstående',52:'Mycket allvarliga eller akuta symtom',53:'Exempel på allvarliga symtom',54:'Tvångsvård kan bli aktuell',55:'Läkarens remiss krävs',58:'Du behöver inte uppge namn',59:'Samtal i en stödande atmosfär',60:'Sök hjälp efter svåra upplevelser',61:'Exempel på traumatiska upplevelser',62:'Kan orsaka posttraumatisk stress',63:'Påträngande minnesbilder',64:'Återhämtning är möjlig',66:'Remiss vid behov',69:'A-kliniken kan hjälpa',70:'Exempel på A-klinikens tjänster',71:'På olika orter',72:'Konfidentiell behandling',73:'Ungdomsstationens hjälp',74:'I många städer',75:'Ensam eller med föräldrar',76:'Kamratföreningen AA',77:'Grupper på många orter',78:'Stöd för närstående'}
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
            person(d,180,300,1.05);shield(d,180,355,1.4);d.line([(340,440),(425,360),(505,425),(610,265)],fill=LINE,width=8);arrow(d,(285,360),(400,360));txt(d,380,580,'klara svårigheter och förändringar',29,620)
        elif i==1:
            group(d,205,295,.85);heart(d,570,285,1.2);d.line((120,520,650,520),fill=GOLD,width=5);txt(d,205,465,'goda relationer',27,285);txt(d,570,465,'hälsosamma vanor',26,285);txt(d,380,590,'TILL EXEMPEL',30,620)
        elif i==2:
            shield(d,200,340,1.5);person(d,560,305,1.1);d.line((335,325,425,325),fill=GOLD,width=6);d.line((335,365,425,365),fill=GOLD,width=6);txt(d,200,535,'mental hälsa',29);txt(d,560,535,'fysiskt välbefinnande',25);txt(d,380,610,'lika viktigt',31,620)
        elif i==3:
            house(d,190,235,.9);group(d,575,225,.65);book(d,190,465,.85);scale(d,575,470,.65)
            for x,y,t in[(190,365,'leva med familjen'),(575,365,'gemenskap'),(190,570,'religiös övertygelse'),(575,570,'jämlikt bemött')]:txt(d,x,y,t,24,290)
            txt(d,380,145,'OFTA · TILL EXEMPEL',29,620)
        elif i==4:
            person(d,380,330,1.1);d.line((120,260,280,330),fill=LINE,width=10);d.line((640,260,480,330),fill=LINE,width=10);shield(d,380,470,.8);txt(d,380,180,'diskriminering och rasism',29,620);txt(d,380,610,'erfarenheter kan belasta',28,620)
        elif i==5:
            person(d,160,300,.8);coins(d,380,330,2);clinic(d,610,280,.8);d.line((540,430,675,430),fill=LINE,width=8)
            for x,t in[(160,'ensamhet'),(380,'ekonomisk osäkerhet'),(610,'svårt att få tjänster')]:txt(d,x,490,t,25,210)
            txt(d,380,610,'belastningar på mental hälsa',28,620)
        elif i==6:
            book(d,200,330,1.35);bubble(d,570,225,'nytt språk',220);d.line([(460,420),(500,390),(545,445),(600,390)],fill=LINE,width=5);txt(d,200,535,'inlärning och användning',25,280);txt(d,570,535,'kulturella utmaningar',25,280);txt(d,380,610,'KAN orsaka svårigheter',30,620)
        elif i==8:
            # Four anonymous clinical-category files, never a symptom checklist.
            for x,y,t in[(200,250,'depression'),(560,250,'ångest'),(200,465,'ätstörningar'),(560,465,'kraftiga rädslor')]:
                paper(d,x,y,170,135);cross(d,x-55,y-35,.25);txt(d,x,y+90,t,27,280)
            txt(d,380,155,'KAN vara · TILL EXEMPEL',29,620)
        elif i==9:
            calendar(d,180,310,1.15);arrow(d,(300,345),(450,345));doctor(d,575,300,1);txt(d,380,160,'OM du behöver tjänsterna',30,620);txt(d,575,485,'hälsovårdare eller läkare',25,280);txt(d,380,600,'FÖRST en tid på egen hälsostation',28,620)
        elif i==10:
            doctor(d,200,320,1.2);magnify(d,490,320,1.1);txt(d,610,260,'?',85,130);txt(d,380,590,'läkaren utreder behovet av hjälp',29,620)
        elif i==11:
            doctor(d,140,320,.9);paper(d,350,325,140,185);txt(d,350,460,'remiss',28,170);d.line((440,320,560,235),fill=GOLD,width=5);d.line((440,350,560,460),fill=GOLD,width=5);clinic(d,615,210,.65);clinic(d,615,455,.65);txt(d,615,335,'poliklinik',23,180);txt(d,615,575,'annan tjänst',23,180);txt(d,380,610,'KAN skriva remiss',30,620)
        elif i==12:
            chairs(d,220,335,1.25);bubble(d,220,175,'samtal',200);capsule(d,575,345,1.2);txt(d,220,520,'i allmänhet',29);txt(d,575,520,'vanligtvis också',27);txt(d,380,610,'psykolog / psykoterapeut och medicin',26,620)
        elif i==15:
            clinic(d,200,275,1.1);clinic(d,565,275,1.1);coins(d,200,450,1);coins(d,565,450,4);txt(d,200,530,'offentlig',29);txt(d,565,530,'privat',29);txt(d,380,610,'privatläkare kostar mycket mer',29,620)
        elif i==18:
            person(d,175,300,.9);person(d,245,355,.45);arrow(d,(335,360),(450,360));house(d,590,285,1.2);txt(d,175,500,'föräldrar',28);txt(d,590,485,'familjerådgivning',26);txt(d,380,165,'OM barnet / den unga har problem',28,620);txt(d,380,610,'egna välfärdsområdet',29,620)
        elif i==20:
            for x,y,t in[(205,250,'kurator'),(565,250,'psykolog'),(205,465,'hälsovårdare'),(565,465,'läkare')]:
                doctor(d,x,y,.65)if t in['hälsovårdare','läkare']else person(d,x,y,.65);txt(d,x,y+105,t,28,290)
        elif i==22:
            # A book anchors the six archived category names to the source list.
            # No prescribed-medicine photo,product or route is declared illicit.
            book(d,160,320,1.35);txt(d,470,185,'cannabis · opioider',29,430);txt(d,470,285,'amfetamin · ecstasy',28,430);txt(d,470,385,'kokain · khat',29,430);txt(d,380,555,'de vanligaste drogerna enligt källan',27,620);txt(d,380,610,'rusmedelskontext',28,620)
        elif i==23:
            scale(d,230,330,1.25);d.rounded_rectangle((485,240,645,440),radius=12,outline=SOFT,width=5);d.line((495,260,635,260),fill=LINE,width=4);txt(d,565,320,'droger',29,145);no(d,565,330,110);txt(d,380,535,'droger i källans rusmedelskontext',28,620);txt(d,380,610,'olagliga i Finland',31,620)
        elif i==24:
            paper(d,175,300,170,220);coins(d,175,475,3);d.rectangle((480,245,650,465),outline=SOFT,width=5)
            for x in[515,550,585,620]:d.line((x,250,x,460),fill=GOLD,width=5)
            txt(d,380,320,'ELLER',29,160);txt(d,175,550,'böter',31);txt(d,565,550,'fängelse',31);txt(d,380,165,'innehav och försäljning',30,620)
        elif i==25:
            person(d,380,260,.8)
            for x in[150,380,610]:d.line((380,360,x,425),fill=GOLD,width=4);clinic(d,x,430,.65)
            for x,t in[(150,'social- och hälsovård'),(380,'studerandehälsovård'),(610,'företagshälsovård')]:txt(d,x,550,t,23,210)
            txt(d,380,150,'vid beroende KAN du få hjälp',27,620)
        elif i==26:
            person(d,200,330,1);group(d,575,310,.6);d.line((315,370,455,370),fill=LINE,width=6);txt(d,200,530,'personen själv',28);txt(d,575,530,'närstående',29);txt(d,380,610,'beroende KAN orsaka problem för båda',27,620)
        elif i==28:
            aclinic(d,380,280,1.45);heart(d,190,485,.7);person(d,575,460,.65);txt(d,190,580,'vård',30);txt(d,575,580,'rehabilitering',28)
        elif i==29:
            aclinic(d,180,270,1.15);arrow(d,(295,345),(450,345));group(d,575,310,.7);heart(d,575,470,.55);txt(d,380,600,'också närstående KAN få hjälp och stöd',26,620)
        elif i==30:
            aclinic(d,190,270,1.2);coins(d,565,280,2);no(d,565,280,90);shield(d,565,495,.8);txt(d,190,565,'vård',30);txt(d,565,585,'också avgiftning',28);txt(d,380,150,'A-klinikerna: gratis vård',29,620)
        elif i==31:
            d.rounded_rectangle((80,185,680,600),radius=20,outline=GOLD,width=5);clinic(d,200,280,1.1);bottle(d,550,330,1);no(d,550,335,120);txt(d,380,190,'UNDER BEHANDLINGEN',30,560);txt(d,380,540,'slutar helt använda rusmedel',29,560)
        elif i==32:
            # A city setting distinguishes geographic service availability.
            for x,top,w in[(140,245,100),(290,195,100),(650,285,90)]:
                d.rectangle((x-w/2,top,x+w/2,490),outline=SOFT,width=5)
                for yy in range(top+30,470,60):
                    for xx in[x-20,x+20]:d.rectangle((xx-7,yy,xx+7,yy+18),outline=LINE,width=3)
            clinic(d,480,335,1.25);d.line((75,520,690,520),fill=LINE,width=6);txt(d,380,155,'MÅNGA städer',32,620);txt(d,380,590,'hälsorådgivning för drogmissbrukare',26,620)
        elif i==34:
            clinic(d,380,240,1.1);book(d,205,460,1.1);bubble(d,565,415,'råd',180);txt(d,380,590,'social- och hälsorådgivning och stöd',27,620)
        elif i==36:
            medical(d,'syringe',190,325,1.1,stroke=SOFT);d.ellipse((170,305,200,335),outline=LINE,width=5);d.ellipse((200,345,230,375),outline=LINE,width=5);d.line((310,350,455,350),fill=LINE,width=6);shield(d,580,350,1.35);d.line((510,260,650,440),fill=GOLD,width=5);txt(d,190,535,'smutsiga sprutor',27);txt(d,580,535,'sjukdomar kan spridas',25);txt(d,380,610,'OM de används',30,620)
        elif i==37:
            clinic(d,190,285,1.2);arrow(d,(305,355),(450,355));clinic(d,575,285,1.2);shield(d,575,490,.55);txt(d,190,510,'rådgivning',29);txt(d,575,575,'avgiftning',29);txt(d,380,170,'via rådgivningen KAN man få vård',28,620)
        elif i==39:
            suitcase(d,170,315,1.1);hardhat(d,390,290,.8);paper(d,600,300,140,190);no(d,600,300,90)
            for x,t in[(170,'flytta mellan länder'),(390,'problem på arbetet'),(600,'förlora arbetet')]:txt(d,x,500,t,25,210)
            txt(d,380,610,'TILL EXEMPEL',30,620)
        elif i==40:
            group(d,170,255,.6);d.line((285,175,285,410),fill=LINE,width=4);candle(d,405,280,.85);clinic(d,610,255,.75);d.line((100,480,660,480),fill=GOLD,width=5);txt(d,170,530,'familj / skilsmässa',24,200);txt(d,405,530,'dödsfall',27,160);txt(d,610,530,'sjukdom',27,180);txt(d,380,610,'KAN vara krissituationer',28,620)
        elif i==41:
            baby(d,210,320,1.4);heart(d,210,220,.5);arrow(d,(340,370),(455,370));person(d,580,310,1);shield(d,580,450,.65);txt(d,380,565,'också en positiv livsförändring',28,620);txt(d,380,610,'KAN innebära behov av stöd',28,620)
        elif i==42:
            d.line((100,400,660,400),fill=SOFT,width=7);arrow(d,(595,400),(660,400));d.line([(140,300),(185,255),(225,335),(265,290)],fill=LINE,width=6);person(d,560,280,.9);txt(d,190,470,'svårt har hänt',27,260);txt(d,560,470,'situationen lugn',27,260);txt(d,380,590,'IBLAND mår man dåligt först efteråt',27,620)
        elif i==43:
            group(d,205,325,.75);person(d,580,300,1);bubble(d,580,170,'prata',180);heart(d,380,460,.7);txt(d,380,590,'OFTA hjälper samtal med närstående',27,620)
        elif i==44:
            person(d,200,310,1.1);doctor(d,565,310,1.1);d.line((305,355,460,355),fill=GOLD,width=5);txt(d,380,180,'IBLAND också',32,620);txt(d,380,590,'professionell hjälp behövs',30,620)
        elif i==45:
            chairs(d,380,350,1.55);bubble(d,380,170,'vilket stöd?',250);heart(d,180,510,.55);shield(d,580,510,.6);txt(d,380,600,'tillsammans med hälsovårdare / läkare',26,620)
        elif i==46:
            # Three source alternatives:therapy,medicine,or their combination.
            d.ellipse((100,200,430,500),outline=SOFT,width=5);d.ellipse((330,200,660,500),outline=GOLD,width=5);chairs(d,220,330,.65);capsule(d,540,330,.8);txt(d,380,320,'båda',25,90);txt(d,205,535,'terapi',29,220);txt(d,555,535,'medicinering',28,240);txt(d,380,155,'ELLER en kombination',29,620);txt(d,380,610,'OFTA hjälper',29,620)
        elif i==48:
            person(d,190,330,1);doctor(d,570,330,1);bubble(d,380,165,'samtal',200);lock(d,380,420,.85);txt(d,380,610,'konfidentiellt',32,620)
        elif i==50:
            folder(d,160,285,'dina uppgifter',.9);person(d,390,310,.8);doctor(d,615,315,.8);d.line((260,350,515,350),fill=LINE,width=4);bubble(d,390,175,'tillstånd?',200);txt(d,380,555,'OM en annan sakkunnig behöver uppgifter',26,620);txt(d,380,610,'du tillfrågas SEPARAT',29,620)
        elif i==51:
            group(d,180,310,.65);bubble(d,180,175,'orolig?',200);arrow(d,(300,370),(450,370));doctor(d,580,320,1);txt(d,380,565,'OM du tror att närstående behöver hjälp',26,620);txt(d,380,610,'KAN du be om råd',29,620)
        elif i==52:
            phone(d,380,340,1.4);txt(d,380,295,'112',48,210);txt(d,380,160,'OM mycket allvarliga ELLER akuta symtom',26,620);txt(d,380,610,'ring nödnumret',31,620)
        elif i==53:
            shield(d,380,340,2);d.polygon([(380,235),(310,400),(450,400)],outline=GOLD,width=6);txt(d,380,315,'!',55,140);txt(d,380,500,'självdestruktivitet',29,620);txt(d,380,555,'kraftig våldsamhet',29,620);txt(d,380,610,'TILL EXEMPEL · föregående akutvillkor',25,620)
        elif i==54:
            d.rounded_rectangle((65,160,695,615),radius=20,outline=GOLD,width=5);person(d,175,295,.8);clinic(d,570,270,.95);txt(d,175,465,'mycket dåligt skick',26,260);txt(d,570,425,'behov av AKUT psykiatrisk sjukhusvård',23,225);txt(d,380,320,'OCH',27,170);txt(d,380,565,'KAN vårdas mot sin vilja',29,570)
        elif i==55:
            doctor(d,190,315,1.1);arrow(d,(300,360),(450,360));paper(d,580,330,190,255);txt(d,580,505,'remiss för tvångsvård',26,280);txt(d,380,610,'läkarens remiss KRÄVS',30,620)
        elif i==58:
            phone(d,180,330,1);paper(d,565,330,180,210);person(d,565,300,.4);no(d,565,330,120);txt(d,565,505,'uppge namn',29);txt(d,380,610,'behövs INTE på kristelefonen',28,620)
        elif i==59:
            phone(d,190,330,1.05);person(d,570,300,.95);bubble(d,570,170,'samtal',200);shield(d,380,480,.85);txt(d,380,590,'tillåtande och stödande atmosfär',29,620)
        elif i==60:
            person(d,200,320,1.1);d.line([(100,200),(145,170),(200,220),(250,180)],fill=LINE,width=6);arrow(d,(305,375),(455,375));doctor(d,580,320,1.05);txt(d,380,560,'efter svåra traumatiska upplevelser',27,620);txt(d,380,610,'viktigt att söka hjälp',30,620)
        elif i==61:
            # Source examples are not reenacted: no actual victim,act or injury.
            shield(d,300,315,1.6);d.line((210,220,390,440),fill=LINE,width=8);book(d,120,335,.65);txt(d,565,210,'förföljelse / diskriminering',24,230);txt(d,565,330,'våld / våldtäkt',25,230);txt(d,565,450,'krig / tortyr',25,230);txt(d,380,610,'KAN vara förknippade · TILL EXEMPEL',26,620)
        elif i==62:
            paper(d,180,300,175,230);d.line([(140,260),(170,285),(205,250)],fill=LINE,width=6);d.line((290,350,450,350),fill=GOLD,width=5);person(d,580,300,1);shield(d,580,445,.7);txt(d,380,550,'upplevelser KAN orsaka',29,620);txt(d,380,610,'posttraumatiskt stressyndrom',28,620)
        elif i==63:
            person(d,380,325,1.2)
            for x,y in[(160,220),(600,220),(160,475)]:paper(d,x,y,105,135);arrow(d,(x+(60 if x<380 else-60),y),(380+(80 if x>380 else-80),320))
            d.arc((280,180,480,400),215,125,fill=LINE,width=6);txt(d,380,575,'minnesbilder tränger sig på',29,620);txt(d,380,615,'kraftig ångest',28,620)
        elif i==64:
            person(d,180,320,1.1);heart(d,560,315,1.25);shield(d,560,430,.85);d.arc((115,190,650,560),190,350,fill=GOLD,width=5);txt(d,380,575,'det GÅR att tillfriskna',30,620);txt(d,380,620,'du KAN få hjälp',28,620)
        elif i==66:
            doctor(d,180,320,1.1);paper(d,390,330,140,190);txt(d,390,475,'remiss',28,170);arrow(d,(485,360),(555,360));clinic(d,625,310,.65);txt(d,380,610,'VID BEHOV till fortsatt vård',29,620)
        elif i==69:
            aclinic(d,210,285,1.4);person(d,570,320,1.1);heart(d,570,490,.6);txt(d,380,610,'KAN hjälpa vid beroendeproblem',29,620)
        elif i==70:
            for x in[160,380,600]:clinic(d,x,260,.75)
            bubble(d,160,445,'poliklinik',200);capsule(d,380,475,.75);shield(d,600,475,.75);txt(d,380,540,'substitutionsbehandling',23,240);txt(d,600,570,'avgiftning',26,210);txt(d,380,160,'BLAND ANNAT',30,620)
        elif i==71:
            for x,y in[(170,250),(380,450),(590,250)]:aclinic(d,x,y,.8)
            txt(d,380,165,'olika orter i Finland',30,620)
        elif i==72:
            aclinic(d,210,290,1.4);lock(d,565,310,1.25);txt(d,380,610,'behandlingen är konfidentiell',29,620)
        elif i==73:
            person(d,180,300,.85);bottle(d,145,500,.45);monitor(d,265,505,.45);arrow(d,(315,350),(450,350));clinic(d,580,285,1.15);txt(d,580,500,'ungdomsstation',26);txt(d,380,165,'OM alkohol-,drog- eller spelproblem',27,620);txt(d,380,610,'KAN få hjälp',30,620)
        elif i==74:
            for x,y in[(160,250),(380,450),(600,250)]:clinic(d,x,y,.8)
            txt(d,380,165,'MÅNGA städer',32,620);txt(d,380,610,'ungdomsstationer',30,620)
        elif i==75:
            person(d,160,310,.9);group(d,570,285,.75);txt(d,380,340,'ELLER',29,160);txt(d,160,520,'ensam',31);txt(d,570,520,'med föräldrar',29);txt(d,380,610,'den unga KAN komma',29,620)
        elif i==76:
            # Anonymous symbols preserve the anonymity of actual AA participants.
            for x,y in[(190,270),(570,270),(190,440),(570,440)]:person(d,x,y,.65)
            d.ellipse((295,275,465,445),outline=GOLD,width=5);txt(d,380,320,'AA',46,160);txt(d,380,550,'dela erfarenheter och hjälpa varandra',27,620);txt(d,380,610,'kamratförening',30,620)
        elif i==77:
            group(d,180,300,.65);d.rectangle((460,230,520,450),outline=SOFT,width=5);d.rectangle((530,165,595,450),outline=SOFT,width=5);d.rectangle((605,265,665,450),outline=SOFT,width=5);bubble(d,560,480,'English',180);txt(d,180,495,'många orter',28);txt(d,380,610,'engelska grupper i STÖRRE städer',28,620)
        elif i==78:
            person(d,180,315,.95);group(d,570,300,.75);d.line((280,370,460,370),fill=GOLD,width=5);heart(d,570,475,.6);txt(d,180,520,'Al-Anon',32);txt(d,570,565,'närstående',30);txt(d,380,610,'stöd till närstående till en alkoholist',27,620)
        else:raise ValueError('Missing source-specific mental-health composition '+str(i))
        im.save(dest);refs=[row['sentence_id']]
        if i in[53,55]:refs.insert(0,script['sentences'][i-1]['sentence_id'])
        if i in[22,23,24]:refs=list(dict.fromkeys([r['sentence_id']for r in script['sentences'][21:i+1]]))
        a=dict(asset_id=key,kind='foreground',visual_type='diagram',files=[info(dest)],creator='Homebrew video studio',reuse_terms='Original schematic artwork under repository MIT license;archived source wording retains publisher terms.',required_credits='Original source-based health illustrations: Homebrew video studio;source wording credited in sources.yaml and CREDITS.md.',relevance_verification=plans[i]['request']+' Individually composed qualified exact-source relationship. Anonymous symbols and isolated objects;no real diagnosis,patient,trauma,substance-use status,injection,use instruction,drug dose,new eligibility criterion or guaranteed treatment outcome.',creation_method=dict(tool=str(Path(__file__).relative_to(R)),source_sentence_ids=refs,medical_object_primitives=dict(path=str(object_module.relative_to(R)),sha256=hashlib.sha256(object_module.read_bytes()).hexdigest())))
    assets.append(a);by_index[i]=a
for i,row in enumerate(script['sentences']):
    a=by_index[aliases.get(i,i)];row.update(asset_ids=['episode_background',a['asset_id']],render_image=a['files'][0]['path'],render_caption=False)
    if i in aliases:
        a['creation_method'].setdefault('source_sentence_ids',[script['sentences'][aliases[i]]['sentence_id']]).append(row['sentence_id']);row['visual_cue']='Retain the useful preceding picture for its direct source continuation: '+plans[i]['request']
script['asset_requests']=script['asset_requests'][:3]+[dict(id=a['asset_id'],kind='foreground',description=a['relevance_verification'],fallback='Faithful useful original pictorial explanation limited to source;document omission if research cannot produce one.')for a in assets];script['render']['credits']=script['render']['credits'][:2]
for j in range(0,len(screen),2):script['render']['credits'].append(dict(heading='Förgrundsbilder · Изображения',paragraphs=screen[j:j+2]+['Original schematisk grafik: Homebrew video studio.','Fullständiga källor och licenser i CREDITS.md.']))
for decision in script['episode_decisions']:
    if decision['id']=='visuals':decision['decision']='All79source slides pictured with74distinct pictures:13verified photographs and61individually composed qualified source diagrams. Five meaningful direct continuations retain useful photographs/diagrams. No real person assigned illness,dependency,migrant status,trauma or clinical diagnosis;no routes,doses,lawful-medicine prohibition or invented eligibility.'
(E/'script.yaml').write_text(yaml.safe_dump(script,allow_unicode=True,sort_keys=False,width=100));(E/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');(E/'foreground-downloads.json').write_text(json.dumps(downloads,ensure_ascii=False,indent=2)+'\n');(E/'prepare_assets.py').write_text((R/'studio/episodes/hb-c10-utkomststod/prepare_assets.py').read_text().replace('Textgrafik: exakta ord och tal ur källtexten.','Original källbaserad grafik: Homebrew video studio.'));print('Prepared',len(assets),'distinct pictures;',len(screen),'photos for79slides.')
