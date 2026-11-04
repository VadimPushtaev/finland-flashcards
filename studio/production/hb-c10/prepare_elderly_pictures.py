"""Draw exact source-qualified ageing support relationships and preserve licensed photographs."""
from pathlib import Path
import json,yaml,hashlib,re,math
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parents[3];SID='hb-c10-aldre';E=R/'studio/episodes'/SID;M=R/'studio/media'/SID;O=M/'pictures';O.mkdir(parents=True,exist_ok=True)
ns={'__file__':str(Path(__file__))};exec(compile((R/'studio/production/hb-c10/author_utkomststod.py').read_text().split('specs=')[0],'access-primitives','exec'),ns);code=(R/'studio/production/hb-c10/prepare_folkhalsa_pictures.py').read_text();exec(compile(code[code.index('def heart'):code.index('photos=json.loads')],'health-objects','exec'),ns);code=(R/'studio/production/hb-c10/prepare_vard_pictures.py').read_text();exec(compile(code[code.index('def envelope'):code.index('photos=json.loads',code.index('def envelope'))],'care-objects','exec'),ns)
canvas,label,house,person,coins,paper,arrow,heart,shield,cross,book,clinic,clock,group,magnify,record,folder,envelope,phone,card,no,calendar,doctor,hardhat=[ns[k] for k in ['canvas','label','house','person','coins','paper','arrow','heart','shield','cross','book','clinic','clock','group','magnify','record','folder','envelope','phone','card','no','calendar','doctor','hardhat']];FG,SOFT,GOLD,LINE,PANEL,BG=[ns[k] for k in ['FG','SOFT','GOLD','LINE','PANEL','BG']]
def info(p):return dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def globe(d,x,y,s=1):
    d.ellipse((x-75*s,y-75*s,x+75*s,y+75*s),outline=SOFT,width=5);d.ellipse((x-35*s,y-75*s,x+35*s,y+75*s),outline=GOLD,width=4);d.line((x-75*s,y,x+75*s,y),fill=GOLD,width=4)
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

photos=json.loads((E/'selected-photos.json').read_text());script=yaml.safe_load((E/'script.yaml').read_text());plans=json.loads((E/'picture-plan.json').read_text());assets=[];downloads=[];screen=[];by_index={};aliases={6:5,28:27,33:32,36:0,37:35,52:51,71:70}
def brain(d,x,y,s=1):
    d.line([(x,y-80*s),(x-30*s,y-95*s),(x-75*s,y-65*s),(x-90*s,y-10*s),(x-75*s,y+45*s),(x-35*s,y+75*s),(x,y+65*s),(x+35*s,y+75*s),(x+75*s,y+45*s),(x+90*s,y-10*s),(x+75*s,y-65*s),(x+30*s,y-95*s),(x,y-80*s)],fill=SOFT,width=5);d.line((x,y-75*s,x,y+60*s),fill=GOLD,width=4)
    for dx in[-45,45]:
        d.arc((x+(dx-25)*s,y-50*s,x+(dx+25)*s,y+5*s),20,300,fill=GOLD,width=4);d.arc((x+(dx-25)*s,y,x+(dx+25)*s,y+50*s),80,340,fill=GOLD,width=4)
def eye(d,x,y,s=1):
    d.line([(x-75*s,y),(x-40*s,y-40*s),(x,y-55*s),(x+40*s,y-40*s),(x+75*s,y),(x+40*s,y+40*s),(x,y+55*s),(x-40*s,y+40*s),(x-75*s,y)],fill=SOFT,width=5);d.ellipse((x-25*s,y-25*s,x+25*s,y+25*s),outline=GOLD,width=5)
def lungs(d,x,y,s=1):
    d.line((x,y-90*s,x,y-15*s),fill=GOLD,width=6)
    for sign in[-1,1]:
        d.line([(x,y-15*s),(x+sign*35*s,y-55*s),(x+sign*65*s,y-35*s),(x+sign*85*s,y+70*s),(x+sign*25*s,y+90*s),(x+sign*15*s,y+25*s),(x,y-15*s)],fill=SOFT,width=5)
def ear(d,x,y,s=1):
    d.arc((x-50*s,y-80*s,x+55*s,y+60*s),160,490,fill=SOFT,width=6);d.line([(x-40*s,y+5*s),(x-15*s,y+55*s),(x+10*s,y+80*s),(x+40*s,y+40*s)],fill=SOFT,width=5);d.arc((x-20*s,y-45*s,x+30*s,y+25*s),170,460,fill=GOLD,width=5)
def cane(d,x,y,s=1):
    d.arc((x-45*s,y-90*s,x+35*s,y-10*s),180,360,fill=SOFT,width=7);d.line((x+35*s,y-50*s,x+35*s,y+110*s),fill=SOFT,width=7);d.line((x+20*s,y+110*s,x+50*s,y+110*s),fill=GOLD,width=8)
def walking(d,x,y,s=1):
    d.ellipse((x-18*s,y-85*s,x+18*s,y-49*s),fill=SOFT);d.line([(x,y-42*s),(x-15*s,y+15*s),(x+20*s,y+60*s),(x+55*s,y+90*s)],fill=SOFT,width=7);d.line([(x-15*s,y+15*s),(x-48*s,y+72*s)],fill=SOFT,width=7);d.line([(x-2*s,y-22*s),(x+50*s,y-8*s)],fill=GOLD,width=6);d.line([(x-2*s,y-22*s),(x-40*s,y+8*s)],fill=SOFT,width=6)
def plate(d,x,y,s=1):
    d.ellipse((x-70*s,y-50*s,x+70*s,y+50*s),outline=SOFT,width=5);d.ellipse((x-45*s,y-30*s,x+45*s,y+30*s),outline=GOLD,width=4);d.line((x-100*s,y-70*s,x-100*s,y+70*s),fill=SOFT,width=5);d.line((x+100*s,y-70*s,x+100*s,y+70*s),fill=SOFT,width=5)
def shirt(d,x,y,s=1):
    d.polygon([(x-30*s,y-60*s),(x-75*s,y-35*s),(x-55*s,y+5*s),(x-30*s,y-5*s),(x-30*s,y+75*s),(x+30*s,y+75*s),(x+30*s,y-5*s),(x+55*s,y+5*s),(x+75*s,y-35*s),(x+30*s,y-60*s)],outline=SOFT,width=5);d.arc((x-25*s,y-75*s,x+25*s,y-35*s),0,180,fill=GOLD,width=5)
def bracelet(d,x,y,s=1):
    d.rounded_rectangle((x-105*s,y-45*s,x+105*s,y+45*s),radius=35,outline=SOFT,width=7);d.rounded_rectangle((x-45*s,y-62*s,x+45*s,y+62*s),radius=22,fill=PANEL,outline=GOLD,width=5);d.ellipse((x-25*s,y-25*s,x+25*s,y+25*s),outline=FG,width=5)
def room(d,x,y,s=1):
    d.rectangle((x-90*s,y-75*s,x+90*s,y+80*s),outline=SOFT,width=5);d.line((x-55*s,y+80*s,x-55*s,y+25*s,x-15*s,y+25*s,x-15*s,y+80*s),fill=GOLD,width=5)
def sofa(d,x,y,s=1):
    d.rounded_rectangle((x-100*s,y-55*s,x+100*s,y+30*s),radius=20,outline=SOFT,width=5);d.rounded_rectangle((x-120*s,y-5*s,x+120*s,y+70*s),radius=15,outline=SOFT,width=5);d.line((x,y-45*s,x,y+60*s),fill=GOLD,width=4)
def smile(d,x,y,s=1):
    d.ellipse((x-65*s,y-65*s,x+65*s,y+65*s),outline=SOFT,width=5)
    for dx in[-23,23]:d.ellipse((x+(dx-5)*s,y-25*s,x+(dx+5)*s,y-15*s),fill=GOLD)
    d.arc((x-35*s,y-20*s,x+35*s,y+40*s),0,180,fill=GOLD,width=5)
def supporthome(d,x,y,s=1):
    house(d,x,y,s);heart(d,x,y+45*s,.35*s)
def institutionhouse(d,x,y,s=1):
    clinic(d,x,y,s);cross(d,x,y-45*s,.3*s)
titles={0:'Ofta själva eller med make',1:'En historisk förändring · 1957',2:'Den historiska folkpensionslagen',3:'Tidigare · flera generationer',4:'Familjen tog hand om varandra',5:'Tidigare · om familj saknades',7:'Historiska förändringar',8:'Nya möjligheter till självständighet',10:'Hälsa, välbefinnande och förmåga',11:'Förändringar när man åldras',12:'Rörlighet och krafter KAN förändras',13:'Minnet KAN påverkas',14:'Sjukdom och funktionsförmåga',15:'Exempel ur källan',16:'Levnadsvanor genom hela livet',17:'Kontakt och aktivitet',19:'Klara vardagen',20:'Förändringar påverkar humöret',21:'En bra vardag och psykisk hälsa',22:'Ofta sämre minne',24:'Aktivitet och möten ger glädje',25:'Kommunal fritidsverksamhet',26:'Föreningar, organisationer, församlingar',27:'Frivilligt arbete',29:'Två exempel på frivilligarbete',30:'Välfärdsområdets ansvar',31:'Boende, social- och hälsovård',32:'En individuell bedömning',34:'Tjänster utifrån individuella behov',38:'Ensamboende KAN bli utmanande',39:'Exempel på möjliga svårigheter',40:'Anpassningar i hemmet',41:'Två exempel på ändringar',42:'Trygg i sitt hem',43:'Hemvård ELLER hemsjukvård',44:'Hjälp med sådant man inte klarar själv',45:'Exempel på vardaglig hjälp',46:'Hemsjukvård vid behov',48:'Offentliga och privata utförare',49:'Servicesedel · en möjlighet',50:'Ett alternativ till områdets tjänst',54:'Ett trygghetsarmband',55:'Kontakt med larmcentralen',56:'Familjen vill IBLAND vårda hemma',57:'Stöd till närståendevårdaren',58:'Båda villkoren för närståendevårdsstöd',59:'Rätt till lediga dagar',61:'Stöd för både boende och vårdare',62:'Gemenskap på dagcentret',65:'En separat transportavgift KAN tas ut',66:'När boende hemma inte längre går',67:'Även privata servicehus',68:'Ett tryggt och meningsfullt liv',69:'Vanligtvis egen betalning',72:'Egen bostad ELLER eget rum',74:'När varken hem eller servicehus går',75:'Kontinuerligt krävande vård',76:'Exempel på stort vårdbehov',77:'Familjen KAN delta om den vill',78:'Institutionsvårdens syfte',79:'Låna hjälpmedel vid hälsostationen',82:'Tjänster som stöder vardagen',83:'Hemkommun i Finland',84:'Ansöka om hemvård',85:'Hemvårdens tre delar'}
for i,row in enumerate(script['sentences']):
    if i in aliases:continue
    key=f'picture-{i+1:03}';dest=O/f'sentence-{i+1:02}.png'
    if str(i)in photos:
        p=photos[str(i)];pi=p['imageinfo'];meta=pi['extmetadata'];clean=lambda k:re.sub('<[^>]+>','',meta.get(k,{}).get('value','')).strip();raw=R/p['path'];creator=clean('Artist');terms=clean('LicenseShortName')+' '+clean('LicenseUrl');source=pi['descriptionurl'];credit=p['title'].removeprefix('File:')+' — '+creator+'. '+terms+'. '+source+'. Complete photograph proportionally resized and letterboxed;original terms retained.';screen.append(p['title'].removeprefix('File:')+' — '+creator+' · '+clean('LicenseShortName'));image=ImageOps.exif_transpose(Image.open(raw)).convert('RGB');image.thumbnail((760,720),Image.Resampling.LANCZOS);im=Image.new('RGB',(760,720),BG);im.paste(image,((760-image.width)//2,(720-image.height)//2));im.save(dest);downloads.append(dict(**info(raw),url=p['download_url']));a=dict(asset_id=key,kind='foreground',visual_type='photograph',files=[info(dest)],creator=creator,reuse_terms=terms,source_url=source,required_credits=credit,relevance_verification=p['context'],creation_method=dict(tool=str(Path(__file__).relative_to(R)),transform='Full photograph EXIF respected,proportionally resized and letterboxed.'))
    else:
        im,d=canvas(titles[i])
        if i==0:
            house(d,380,275,1);arrow(d,(300,360),(200,435));arrow(d,(460,360),(565,435));person(d,190,485,.7);person(d,520,485,.65);person(d,615,485,.65);txt(d,380,405,'ELLER',28,170);txt(d,380,155,'OFTA',33,620)
        elif i==1:
            book(d,190,310,1.3);txt(d,190,300,'1957',40,200);arrow(d,(310,355),(445,355));house(d,565,280,1);person(d,565,470,.7);txt(d,380,610,'historisk lag → möjlighet till eget liv',27,620)
        elif i==2:
            book(d,380,285,.85);txt(d,380,155,'LAGEN SOM TRÄDDE I KRAFT 1957',27,620);person(d,180,465,.75);person(d,580,465,.75);hardhat(d,180,370,.5);hardhat(d,580,370,.5);no(d,580,370,52);coins(d,180,580,2);coins(d,580,580,2);d.line((300,335,180,370),fill=GOLD,width=4);d.line((460,335,580,370),fill=GOLD,width=4);txt(d,380,610,'även personer som inte hade arbetat',27,620)
        elif i==3:
            house(d,380,270,1.2);d.rounded_rectangle((110,380,650,605),radius=18,outline=GOLD,width=4);person(d,220,465,.65);person(d,380,455,.8);person(d,540,490,.45);txt(d,380,155,'TIDIGARE · flera generationer KUNDE bo ihop',26,620)
        elif i==4:
            for x,y in[(180,300),(570,300),(380,505)]:person(d,x,y,.7)
            arrow(d,(270,300),(450,300));arrow(d,(460,340),(270,340));heart(d,380,350,.8);d.line((180,420,300,500),fill=GOLD,width=4);d.line((570,420,460,500),fill=GOLD,width=4);txt(d,380,610,'omsorg om varandra',31,620)
        elif i==5:
            txt(d,380,155,'TIDIGARE · OM ingen familj',29,620);group(d,180,300,.7);no(d,180,340,100);arrow(d,(300,355),(445,355));house(d,575,295,1.2);txt(d,575,520,'kommunalhem',29,290);txt(d,380,610,'historiska, anspråkslösa förhållanden',27,620)
        elif i==7:
            hardhat(d,180,275,1);group(d,570,275,.6);txt(d,180,430,'kvinnor började arbeta utanför hemmet',25,280);txt(d,570,430,'familjer blev mindre',25,280);arrow(d,(210,530),(310,565));arrow(d,(550,530),(450,565));supporthome(d,380,540,.5);txt(d,380,610,'svårare att vårda äldre hemma',27,620)
        elif i==8:
            house(d,190,315,1.2);arrow(d,(190,470),(190,220));arrow(d,(320,355),(445,355));person(d,570,315,1.2);txt(d,190,535,'högre levnadsstandard',27,290);txt(d,570,535,'självständigt liv',27,290);txt(d,380,155,'NYA MÖJLIGHETER',31,620)
        elif i==10:
            heart(d,170,290,.9);smile(d,380,290,.9);walking(d,590,290,.95);txt(d,170,475,'hälsa',30,190);txt(d,380,475,'välbefinnande',24,210);txt(d,590,475,'funktionsförmåga',24,225);d.line((100,570,660,570),fill=GOLD,width=5);txt(d,380,610,'allt större betydelse när man åldras',27,620)
        elif i==11:
            clock(d,175,310,1.2);arrow(d,(295,350),(450,350));person(d,580,315,1.4);d.arc((465,195,695,550),285,80,fill=GOLD,width=5);txt(d,380,610,'kroppen förändras med åldern',28,620)
        elif i==12:
            walking(d,190,315,1.3);cane(d,565,315,1.15);txt(d,380,155,'KAN · KANSKE',33,620);txt(d,190,520,'svårare att röra sig',27,290);txt(d,565,520,'mindre krafter',29,290)
        elif i==13:
            brain(d,300,380,1.7);bubble(d,570,420,'?',125);txt(d,380,155,'KAN',36,620);txt(d,380,610,'problem med minnet',32,620)
        elif i==14:
            record(d,180,290,'sjukdom',1);arrow(d,(300,355),(450,355));person(d,580,295,1);d.arc((490,200,670,490),290,70,fill=GOLD,width=5);txt(d,380,155,'KAN',36,620);txt(d,380,610,'ändrad kropp · sämre funktionsförmåga',27,620)
        elif i==15:
            brain(d,170,280,.7);heart(d,380,280,.75);lungs(d,590,280,.7);txt(d,170,395,'minnessjukdomar',22,200);txt(d,380,395,'hjärtsjukdomar',22,200);txt(d,590,395,'lungsjukdomar',22,200);d.rectangle((200,490,260,550),outline=SOFT,width=5);txt(d,230,575,'diabetes',26,260);d.ellipse((480,490,550,560),outline=SOFT,width=5);d.ellipse((500,510,525,535),outline=GOLD,width=4);txt(d,515,575,'cancer',27,230);txt(d,380,155,'TILL EXEMPEL',32,620)
        elif i==16:
            timeline(d,300);txt(d,380,155,'GENOM HELA LIVET',31,620);plate(d,180,450,.7);walking(d,380,450,.75);heart(d,580,450,.9);txt(d,380,610,'levnadsvanor KAN påverka',29,620)
        elif i==17:
            person(d,145,290,.8);person(d,270,290,.8);bubble(d,205,165,'...',135);walking(d,580,295,1.1);txt(d,380,315,'OCH',27,150);txt(d,205,485,'träffa andra',28,280);txt(d,580,485,'vara aktiv',29,280);txt(d,380,610,'bibehållen funktionsförmåga',29,620)
        elif i==19:
            person(d,170,310,.9);shirt(d,380,290,.95);house(d,595,280,1);d.line((100,515,660,515),fill=GOLD,width=5);txt(d,170,545,'vardagen',26,200);txt(d,380,545,'sig själv',27,200);txt(d,595,545,'sitt hem',27,200)
        elif i==20:
            candle(d,165,290,.9);paper(d,380,280,140,180);d.line((500,260,530,300,550,240,590,315,620,270),fill=GOLD,width=5);arrow(d,(380,430),(380,500));person(d,380,535,.55);txt(d,380,155,'kriser · förändringar · förluster',28,620);txt(d,380,610,'påverkar humöret',31,620)
        elif i==21:
            house(d,180,290,1.1);clock(d,180,490,.65);arrow(d,(305,350),(450,350));heart(d,580,330,1.2);brain(d,580,330,.6);txt(d,380,610,'bra vardag → psykisk hälsa',30,620)
        elif i==22:
            brain(d,190,315,1.2);paper(d,570,320,180,220);txt(d,570,295,'?',60,150);txt(d,380,155,'OFTA',34,620);d.line((300,355,445,355),fill=GOLD,width=5);txt(d,380,610,'sämre minne · glömmer saker',29,620)
        elif i==24:
            walking(d,165,300,.95);group(d,570,280,.7);arrow(d,(240,450),(315,505));arrow(d,(520,450),(445,505));smile(d,380,535,.65);txt(d,380,155,'aktivt liv OCH möten',31,620);txt(d,380,610,'glädje i vardagen',31,620)
        elif i==25:
            institution(d,190,300,1.2);arrow(d,(315,350),(445,350));book(d,580,285,1);walking(d,580,480,.65);txt(d,190,520,'kommunen',30,290);txt(d,380,610,'fritidsverksamhet för äldre',29,620)
        elif i==26:
            group(d,160,290,.6);book(d,380,290,.9);house(d,600,270,.9);cross(d,600,205,.22);txt(d,160,455,'föreningar',25,205);txt(d,380,455,'organisationer',24,205);txt(d,600,455,'församlingar',24,205);d.line((160,520,600,520),fill=GOLD,width=5);txt(d,380,580,'verksamhet och klubbar',30,620)
        elif i==27:
            person(d,380,315,1.1);heart(d,380,465,.7);group(d,165,315,.55);house(d,600,295,.75);arrow(d,(300,355),(240,355));arrow(d,(460,355),(510,355));txt(d,380,155,'MÅNGA ÄLDRE VILL',30,620);txt(d,380,610,'vara aktiva och påverka samhället',28,620)
        elif i==29:
            person(d,380,255,.8);arrow(d,(300,350),(210,435));arrow(d,(460,350),(565,435));person(d,140,490,.65);baby(d,245,490,.5);person(d,580,485,.75);txt(d,380,420,'ELLER',27,160);txt(d,180,600,'barnfamiljer',27,280);txt(d,580,600,'ensamma människor',25,285);txt(d,380,155,'TILL EXEMPEL HJÄLPA',29,620)
        elif i==30:
            institution(d,380,320,1.3);txt(d,380,155,'VÄLFÄRDSOMRÅDET',31,620);d.line((380,435,380,450),fill=GOLD,width=5);person(d,290,505,.65);person(d,465,505,.65);heart(d,380,525,.5);txt(d,380,610,'ansvar för tjänster till äldre',28,620)
        elif i==31:
            supporthome(d,190,310,1.1);clinic(d,570,300,1.15);txt(d,380,335,'OCH',27,150);txt(d,190,535,'boendeservice',28,285);txt(d,570,535,'social- och hälsovård',26,290);txt(d,380,155,'VÄLFÄRDSOMRÅDETS TJÄNSTER',28,620)
        elif i==32:
            person(d,150,320,.9);paper(d,390,320,170,230);magnify(d,440,380,.8);doctor(d,620,310,.8);arrow(d,(230,355),(285,355));txt(d,380,155,'OM behov av tjänster',30,620);txt(d,380,610,'myndigheten bedömer individuellt vårdbehov',25,620)
        elif i==34:
            person(d,180,310,1);paper(d,380,310,160,220);d.line((275,355,285,355),fill=GOLD,width=5);supporthome(d,600,265,.6);clinic(d,600,460,.6);d.line((470,315,530,270),fill=GOLD,width=4);d.line((470,380,530,460),fill=GOLD,width=4);txt(d,380,155,'UTIFRÅN INDIVIDUELLT BEHOV',28,620);txt(d,380,610,'beviljade tjänster',31,620)
        elif i==38:
            house(d,285,300,1.6);person(d,285,350,.8);d.line((520,480,560,480,560,430,600,430,600,380,640,380),fill=SOFT,width=6);txt(d,590,260,'?',70,150);txt(d,380,155,'KAN',36,620);txt(d,380,610,'ensamboende kan bli utmanande',29,620)
        elif i==39:
            walking(d,180,275,.85);eye(d,565,275,.85);ear(d,180,490,.7);brain(d,565,490,.8);txt(d,380,155,'KAN · TILL EXEMPEL',31,620);txt(d,180,380,'rörlighet',26,280);txt(d,565,380,'syn',28,280);txt(d,180,595,'hörsel',28,280);txt(d,565,595,'minne',28,280)
        elif i==40:
            house(d,190,300,1.15);house(d,570,300,1.15);d.line((85,480,295,480),fill=SOFT,width=6);d.line((465,480,675,480),fill=GOLD,width=9);arrow(d,(320,355),(445,355));txt(d,380,155,'ÄNDRINGAR KAN GÖRAS',30,620);txt(d,380,610,'i bostaden eller dess omgivning',29,620)
        elif i==41:
            d.rectangle((110,215,280,500),outline=SOFT,width=6);arrow(d,(125,260),(265,260));arrow(d,(265,310),(125,310));txt(d,195,540,'bredda dörrar',28,290);d.line((440,460,500,460,500,420,580,420,580,460,650,460),fill=SOFT,width=6);no(d,540,425,80);txt(d,550,540,'ta bort trösklar',28,290);txt(d,380,155,'TILL EXEMPEL',31,620)
        elif i==42:
            house(d,380,310,1.7);shield(d,380,355,1.8);person(d,380,350,.7);txt(d,380,610,'känna sig trygg hemma',31,620)
        elif i==43:
            institution(d,380,300,1);supporthome(d,180,470,.9);clinic(d,580,460,.9);arrow(d,(300,355),(245,415));arrow(d,(460,355),(515,415));txt(d,380,410,'ELLER',26,150);txt(d,180,595,'hemvård',28,280);txt(d,580,595,'hemsjukvård',28,280);txt(d,380,155,'VÄLFÄRDSOMRÅDET KAN ORDNA',28,620)
        elif i==44:
            house(d,190,280,1);person(d,190,325,.7);person(d,565,315,1);heart(d,565,465,.65);arrow(d,(460,355),(310,355));txt(d,380,155,'ANSTÄLLDA HJÄLPER',30,620);txt(d,380,610,'sådant man inte längre klarar själv',28,620)
        elif i==45:
            plate(d,180,280,.7);shirt(d,565,270,.85);d.line((125,470,125,515,245,515,245,470),fill=SOFT,width=5);d.arc((125,455,245,535),0,180,fill=GOLD,width=5);d.line((225,460,225,425,260,425),fill=SOFT,width=5);d.arc((510,455,620,525),180,360,fill=GOLD,width=5)
            for x in[530,565,600]:d.line((x,505,x-10,555),fill=SOFT,width=4)
            txt(d,180,375,'äta',28,280);txt(d,565,375,'klä sig',28,280);txt(d,180,595,'toalett',28,280);txt(d,565,595,'duscha',28,280);txt(d,380,155,'TILL EXEMPEL',31,620)
        elif i==46:
            house(d,190,280,1.1);cross(d,190,300,.4);doctor(d,570,320,1);arrow(d,(445,355),(320,355));txt(d,380,155,'OM hemsjukvård behövs',30,620);txt(d,380,610,'KAN få besök av sjukskötare',29,620)
        elif i==48:
            institution(d,180,270,.9);house(d,580,245,.8);hardhat(d,580,250,.4);supporthome(d,180,500,.65);clinic(d,580,490,.65);d.line((180,380,180,410,580,410,580,360),fill=GOLD,width=5);txt(d,180,155,'välfärdsområdet',26,290);txt(d,580,155,'privata företag',26,290);txt(d,380,610,'BÅDA ordnar hemservice och hemsjukvård',26,620)
        elif i==49:
            institution(d,160,300,.9);paper(d,380,320,160,180);txt(d,380,285,'service- sedel',28,150);supporthome(d,620,300,.8);arrow(d,(255,355),(285,355));arrow(d,(475,355),(525,355));txt(d,380,155,'VÄLFÄRDSOMRÅDET KAN GE',29,620);txt(d,380,610,'köpa vårdtjänster av företag',29,620)
        elif i==50:
            paper(d,180,275,150,185);supporthome(d,180,490,.7);institution(d,580,300,1.1);supporthome(d,580,510,.55);txt(d,380,360,'ELLER',29,165);txt(d,380,155,'ALTERNATIV',33,620);txt(d,380,610,'servicesedel ELLER områdets tjänst',28,620)
        elif i==54:
            bracelet(d,380,345,2);txt(d,380,155,'TILL EXEMPEL',32,620);txt(d,380,610,'trygghetsarmband med knapp',30,620)
        elif i==55:
            bracelet(d,180,315,1);arrow(d,(310,355),(450,355));phone(d,580,290,1.05);clock(d,580,495,.75);txt(d,380,155,'TRYCK PÅ KNAPPEN → KONTAKT',28,620);txt(d,180,495,'trygghetsarmband',24,290);txt(d,580,600,'larmcentral · dygnet runt',25,300)
        elif i==56:
            group(d,190,290,.8);arrow(d,(315,350),(450,350));supporthome(d,580,295,1.2);txt(d,380,155,'IBLAND · FAMILJEN VILL',30,620);txt(d,380,610,'ta hand om den äldre hemma',29,620)
        elif i==57:
            institution(d,160,270,.85);coins(d,365,330,3);person(d,590,300,.85);person(d,590,510,.55);heart(d,590,405,.35);arrow(d,(250,340),(290,340));arrow(d,(455,340),(505,340));txt(d,590,155,'EN familjemedlem vårdar',25,295);txt(d,160,475,'välfärdsområdet',24,250);txt(d,380,610,'stödet betalas till VÅRDAREN',30,620)
        elif i==58:
            d.rounded_rectangle((65,200,695,550),radius=20,outline=GOLD,width=5);clock(d,190,300,1);heart(d,570,300,1);txt(d,380,315,'OCH',28,160);txt(d,190,455,'hjälp behövs HELA TIDEN',25,275);txt(d,570,455,'bindande OCH krävande vård',25,275);txt(d,380,610,'KAN få stöd för närståendevård',29,620)
        elif i==59:
            person(d,190,310,1);calendar(d,570,300,1.25);d.line((315,355,445,355),fill=GOLD,width=5);txt(d,190,505,'närståendevårdare',26,290);txt(d,570,505,'lediga dagar',30,290);txt(d,380,610,'också rätt till ledighet',30,620)
        elif i==61:
            house(d,380,275,1.1);txt(d,380,155,'DAGVERKSAMHET',30,620);supporthome(d,170,485,.9);person(d,590,465,.8);heart(d,590,530,.45);arrow(d,(300,355),(235,415));arrow(d,(460,355),(525,415));txt(d,170,605,'klara sig hemma',26,280);txt(d,590,605,'vårdaren orkar',27,280)
        elif i==62:
            room(d,380,330,2);person(d,260,390,.7);person(d,500,390,.7);bubble(d,380,220,'...',150);txt(d,380,610,'tid tillsammans på dagcentret',29,620)
        elif i==65:
            coins(d,190,300,3);d.rectangle((445,265,675,380),outline=SOFT,width=5)
            for x in[490,630]:d.ellipse((x-25,365,x+25,415),outline=GOLD,width=5)
            txt(d,380,155,'KAN',36,620);txt(d,190,495,'separat avgift',29,290);txt(d,570,495,'färdtjänst',30,290)
        elif i==66:
            house(d,380,285,1);no(d,380,285,95);house(d,180,470,.9);institutionhouse(d,580,470,.9);arrow(d,(300,355),(245,410));arrow(d,(460,355),(515,410));txt(d,380,415,'ELLER',26,150);txt(d,180,600,'servicehus',28,280);txt(d,580,600,'inrättning',28,280);txt(d,380,155,'NÄR boende hemma inte längre går',28,620)
        elif i==67:
            house(d,190,285,1);hardhat(d,190,285,.45);arrow(d,(315,350),(445,350));supporthome(d,575,295,1.2);txt(d,190,505,'privata företag',28,285);txt(d,575,535,'serviceboende',29,285);txt(d,380,610,'också privata företag',29,620)
        elif i==68:
            house(d,380,285,1.1);shield(d,190,470,1);book(d,380,470,.7);heart(d,580,470,.8);txt(d,380,155,'SYFTET MED SERVICEBOENDE',29,620);txt(d,190,605,'tryggt',28,215);txt(d,485,605,'meningsfullt liv',28,310)
        elif i==69:
            person(d,180,300,1);coins(d,380,350,3);supporthome(d,600,300,1);arrow(d,(270,350),(290,350));arrow(d,(470,350),(490,350));txt(d,380,155,'I ALLMÄNHET',33,620);txt(d,380,610,'den äldre betalar själv',30,620)
        elif i==72:
            d.rectangle((85,215,675,560),outline=SOFT,width=5);d.line((370,215,370,560),fill=GOLD,width=5);d.line((85,400,675,400),fill=SOFT,width=5);room(d,225,305,.65);room(d,520,305,.65);person(d,225,310,.3);person(d,520,310,.3);sofa(d,380,480,.8);txt(d,380,155,'egen bostad ELLER eget rum',29,620);txt(d,380,610,'många gemensamma utrymmen',29,620)
        elif i==74:
            house(d,175,300,.9);no(d,175,300,90);supporthome(d,580,300,.9);no(d,580,300,90);txt(d,380,315,'OCH',26,150);arrow(d,(230,420),(310,465));arrow(d,(530,420),(450,465));institutionhouse(d,380,510,.7);txt(d,380,155,'VARKEN HEMMA ELLER PÅ SERVICEHUS',27,620);txt(d,380,610,'då institutionsvård',31,620)
        elif i==75:
            clock(d,175,285,1.1);doctor(d,580,280,.9);txt(d,175,465,'kontinuerligt',28,285);txt(d,580,465,'krävande vård',28,285);shield(d,380,530,.6);txt(d,380,155,'VÅRDBEHOVET',32,620);txt(d,380,610,'kan INTE ordnas säkert någon annanstans',26,620)
        elif i==76:
            record(d,160,300,'sjukdom',.9);person(d,380,310,.9);doctor(d,580,235,.55);doctor(d,650,430,.55);doctor(d,500,510,.55);d.line((255,355,295,355),fill=GOLD,width=5);txt(d,380,155,'TILL EXEMPEL · KAN BEHÖVA',29,620);txt(d,380,610,'många vårdare varje dag',30,620)
        elif i==77:
            group(d,180,300,.75);arrow(d,(300,355),(450,355));institutionhouse(d,580,310,1.1);heart(d,580,485,.6);txt(d,380,155,'OM FAMILJEN VILL',32,620);txt(d,380,610,'KAN delta i vården',32,620)
        elif i==78:
            institutionhouse(d,380,300,1);walking(d,170,480,.8);heart(d,380,480,.8);smile(d,590,480,.8);txt(d,380,155,'SYFTET MED INSTITUTIONSVÅRD',28,620);txt(d,170,610,'förmåga',27,200);txt(d,380,610,'livskvalitet',25,200);txt(d,590,610,'mående',27,200)
        elif i==79:
            clinic(d,190,300,1.2);cane(d,550,280,.85);paper(d,550,500,130,135);arrow(d,(315,350),(445,350));txt(d,380,155,'KAN LÅNA',33,620);txt(d,380,610,'hjälpmedel vid hälsostationen',29,620)
        elif i==82:
            plate(d,155,260,.65);bracelet(d,380,270,.65);cane(d,605,270,.65);house(d,380,510,.85);d.line((155,370,300,450),fill=GOLD,width=4);d.line((380,370,380,410),fill=GOLD,width=4);d.line((605,370,460,450),fill=GOLD,width=4);txt(d,380,155,'TJÄNSTER SOM UNDERLÄTTAR',29,620);txt(d,380,610,'vardagen och boende hemma',29,620)
        elif i==83:
            house(d,175,300,1.2);paper(d,175,500,120,130);institution(d,580,300,1.2);arrow(d,(315,355),(445,355));txt(d,380,155,'OM HEMKOMMUN I FINLAND',30,620);txt(d,380,610,'rätt till områdets tjänster för äldre',27,620)
        elif i==84:
            record(d,180,275,'dålig hälsa',.85);person(d,570,275,.8);heart(d,570,430,.45);txt(d,380,305,'OCH',28,160);txt(d,570,470,'behöver hjälp i vardagen',25,285);paper(d,380,550,135,115);txt(d,380,155,'BÅDA VILLKOREN',31,620);txt(d,380,620,'KAN ANSÖKA hos socialtjänsterna',27,620)
        elif i==85:
            house(d,380,215,1);plate(d,170,465,.65);doctor(d,380,465,.75);bracelet(d,590,465,.6);d.line((380,350,170,385),fill=GOLD,width=4);d.line((380,350,380,385),fill=GOLD,width=4);d.line((380,350,590,385),fill=GOLD,width=4);txt(d,170,595,'hemtjänster',24,205);txt(d,380,595,'hemsjukvård',24,205);txt(d,590,595,'stödtjänster',24,205)
        else:raise ValueError('Missing source-specific ageing composition '+str(i))
        im.save(dest);a=dict(asset_id=key,kind='foreground',visual_type='diagram',files=[info(dest)],creator='Homebrew video studio',reuse_terms='Original schematic artwork under repository MIT license;source wording retains publisher terms.',required_credits='Original source-based ageing-support illustrations: Homebrew video studio;source wording credited in sources.yaml and CREDITS.md.',relevance_verification=plans[i]['request']+' Individually composed source-specific relation;no universal diagnosis,age-only admission,service schedule,fee amount,care technique or new entitlement invented.',creation_method=dict(tool=str(Path(__file__).relative_to(R)),source_sentence_ids=[row['sentence_id']]))
    assets.append(a);by_index[i]=a
for i,row in enumerate(script['sentences']):
    a=by_index[aliases.get(i,i)];row.update(asset_ids=['episode_background',a['asset_id']],render_image=a['files'][0]['path'],render_caption=False)
    if i in aliases:
        a['creation_method'].setdefault('source_sentence_ids',[script['sentences'][aliases[i]]['sentence_id']]).append(row['sentence_id']);row['visual_cue']='Retain the useful source picture for this directly related continuation: '+plans[i]['request']
script['asset_requests']=script['asset_requests'][:3]+[dict(id=a['asset_id'],kind='foreground',description=a['relevance_verification'],fallback='Accurate useful source-based pictorial explanation;record honest omission if reasonable research cannot produce it.')for a in assets];script['render']['credits']=script['render']['credits'][:2]
for j in range(0,len(screen),2):script['render']['credits'].append(dict(heading='Förgrundsbilder · Изображения',paragraphs=screen[j:j+2]+['Original schematisk grafik: Homebrew video studio.','Fullständiga källor och licenser i CREDITS.md.']))
for decision in script['episode_decisions']:
    if decision['id']=='visuals':decision['decision']=f'All86source slides pictured with{len(assets)}sourcepictures:{len(screen)}actual licensed photographs and{len(assets)-len(screen)}individually composed diagrams.Seven useful historical/assessment/support/home continuations retain unchanged pictures.1957andkommunalhem remain historical;individual assessment,caregiving conditions,servicehousing andinstitutionalcare stay distinct.No actualperson assigned age,diagnosis,dependency or benefitstatus.'
(E/'script.yaml').write_text(yaml.safe_dump(script,allow_unicode=True,sort_keys=False,width=100));(E/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');(E/'foreground-downloads.json').write_text(json.dumps(downloads,ensure_ascii=False,indent=2)+'\n');(E/'prepare_assets.py').write_text((R/'studio/episodes/hb-c10-utkomststod/prepare_assets.py').read_text().replace('Textgrafik: exakta ord och tal ur källtexten.','Original källbaserad grafik: Homebrew video studio.'));print('Prepared',len(assets),'sourcepictures;',len(screen),'photos for86slides.')
