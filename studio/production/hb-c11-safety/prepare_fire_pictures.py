"""Draw exact household fire-safety conditions and preserve actual objects."""
from pathlib import Path
import json,yaml,hashlib,re,math
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parents[3];SID='hb-c11-brandsakerhet';E=R/'studio/episodes'/SID;M=R/'studio/media'/SID;O=M/'pictures';O.mkdir(parents=True,exist_ok=True)
ns={'__file__':str(Path(__file__))};exec(compile((R/'studio/production/hb-c10/author_utkomststod.py').read_text().split('specs=')[0],'access-primitives','exec'),ns);code=(R/'studio/production/hb-c10/prepare_folkhalsa_pictures.py').read_text();exec(compile(code[code.index('def heart'):code.index('photos=json.loads')],'health-objects','exec'),ns);code=(R/'studio/production/hb-c10/prepare_vard_pictures.py').read_text();exec(compile(code[code.index('def envelope'):code.index('photos=json.loads',code.index('def envelope'))],'care-objects','exec'),ns)
ns.update(BG='#243c32',PANEL='#2d4d40',FG='#faf3e8',SOFT='#c5dfce',GOLD='#e3c58c',LINE='#4d7560')
canvas,label,house,person,coins,paper,arrow,heart,shield,cross,book,clinic,clock,group,magnify,record,folder,envelope,phone,card,no,calendar,doctor,hardhat=[ns[k] for k in ['canvas','label','house','person','coins','paper','arrow','heart','shield','cross','book','clinic','clock','group','magnify','record','folder','envelope','phone','card','no','calendar','doctor','hardhat']];FG,SOFT,GOLD,LINE,PANEL,BG=[ns[k] for k in ['FG','SOFT','GOLD','LINE','PANEL','BG']]
def info(p):return dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def globe(d,x,y,s=1):
    d.ellipse((x-75*s,y-75*s,x+75*s,y+75*s),outline=SOFT,width=5);d.ellipse((x-35*s,y-75*s,x+35*s,y+75*s),outline=GOLD,width=4);d.line((x-75*s,y,x+75*s,y),fill=GOLD,width=4)
def librarycard(d,x,y,s=1):
    d.rounded_rectangle((x-105*s,y-65*s,x+105*s,y+65*s),radius=14,outline=SOFT,width=5);book(d,x-35*s,y,.42*s);d.line((x+20*s,y-15*s,x+75*s,y-15*s),fill=LINE,width=5);d.line((x+20*s,y+15*s,x+75*s,y+15*s),fill=GOLD,width=5)
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

def shirt(d,x,y,s=1):
    d.polygon([(x-30*s,y-60*s),(x-75*s,y-35*s),(x-55*s,y+5*s),(x-30*s,y-5*s),(x-30*s,y+75*s),(x+30*s,y+75*s),(x+30*s,y-5*s),(x+55*s,y+5*s),(x+75*s,y-35*s),(x+30*s,y-60*s)],outline=SOFT,width=5);d.arc((x-25*s,y-75*s,x+25*s,y-35*s),0,180,fill=GOLD,width=5)


photos=json.loads((E/'selected-photos.json').read_text());script=yaml.safe_load((E/'script.yaml').read_text());plans=json.loads((E/'picture-plan.json').read_text());assets=[];downloads=[];screen=[];by_index={};aliases={42:41}
def alarm(d,x,y,s=1):
    d.ellipse((x-70*s,y-55*s,x+70*s,y+55*s),outline=SOFT,width=5);d.ellipse((x-18*s,y-15*s,x+18*s,y+20*s),outline=GOLD,width=5)
    for dx in[-45,-30,30,45]:d.line((x+dx*s,y-12*s,x+dx*s,y+12*s),fill=SOFT,width=4)
def stove(d,x,y,s=1):
    d.rectangle((x-95*s,y-75*s,x+95*s,y+110*s),outline=SOFT,width=5);d.line((x-90*s,y-25*s,x+90*s,y-25*s),fill=GOLD,width=4);d.rectangle((x-65*s,y+15*s,x+65*s,y+85*s),outline=SOFT,width=4)
    for dx in[-45,45]:d.ellipse((x+(dx-25)*s,y-60*s,x+(dx+25)*s,y-35*s),outline=GOLD,width=4)
def pot(d,x,y,s=1):
    d.rounded_rectangle((x-70*s,y-30*s,x+70*s,y+75*s),radius=13,outline=SOFT,width=5);d.line((x-95*s,y-10*s,x-70*s,y-10*s),fill=SOFT,width=6);d.line((x+70*s,y-10*s,x+95*s,y-10*s),fill=SOFT,width=6)
def flame(d,x,y,s=1):
    d.polygon([(x,y-75*s),(x+20*s,y-20*s),(x+45*s,y-40*s),(x+55*s,y+35*s),(x+25*s,y+70*s),(x-35*s,y+60*s),(x-55*s,y+20*s),(x-30*s,y-35*s),(x-20*s,y+10*s)],outline=GOLD,width=5)
def blanket(d,x,y,s=1):
    d.rectangle((x-60*s,y-100*s,x+60*s,y+80*s),outline=SOFT,width=5);flame(d,x,y-15*s,.4*s);d.line((x-25*s,y+80*s,x-25*s,y+120*s),fill=GOLD,width=6);d.line((x+25*s,y+80*s,x+25*s,y+120*s),fill=GOLD,width=6)
def extinguisher(d,x,y,s=1):
    d.rounded_rectangle((x-45*s,y-70*s,x+45*s,y+110*s),radius=27,outline=SOFT,width=5);d.line((x-20*s,y-70*s,x-20*s,y-100*s,x+25*s,y-110*s),fill=GOLD,width=6);d.line([(x+25*s,y-105*s),(x+85*s,y-95*s),(x+85*s,y+45*s)],fill=SOFT,width=5);d.line((x-30*s,y+20*s,x+30*s,y+20*s),fill=GOLD,width=5)
def heater(d,x,y,s=1):
    d.rectangle((x-70*s,y-40*s,x+70*s,y+100*s),outline=SOFT,width=5)
    for dx,dy in[(-35,-40),(10,-45),(40,-30),(-10,-15)]:d.ellipse((x+(dx-20)*s,y+(dy-15)*s,x+(dx+20)*s,y+(dy+15)*s),outline=GOLD,width=4)
    for dx in[-40,0,40]:d.line((x+dx*s,y+15*s,x+dx*s,y+75*s),fill=SOFT,width=4)
def box(d,x,y,s=1):
    d.rectangle((x-60*s,y-45*s,x+60*s,y+50*s),outline=SOFT,width=5);d.line((x-60*s,y-45*s,x,y-15*s,x+60*s,y-45*s),fill=GOLD,width=4)
def iron(d,x,y,s=1):
    d.line([(x-90*s,y+60*s),(x-15*s,y-50*s),(x+55*s,y-35*s),(x+90*s,y+60*s),(x-90*s,y+60*s)],fill=SOFT,width=5);d.arc((x-10*s,y-80*s,x+70*s,y+20*s),180,355,fill=GOLD,width=5)
def plug(d,x,y,s=1):
    d.rounded_rectangle((x-40*s,y-25*s,x+30*s,y+35*s),radius=12,outline=SOFT,width=5);d.line((x+30*s,y-10*s,x+65*s,y-10*s),fill=GOLD,width=6);d.line((x+30*s,y+20*s,x+65*s,y+20*s),fill=GOLD,width=6);d.line((x-40*s,y+5*s,x-95*s,y+5*s),fill=SOFT,width=5)
def outlet(d,x,y,s=1):
    d.rounded_rectangle((x-40*s,y-50*s,x+40*s,y+50*s),radius=10,outline=SOFT,width=5)
    for dy in[-15,15]:d.ellipse((x-4*s,y+(dy-4)*s,x+4*s,y+(dy+4)*s),fill=GOLD)
def drop(d,x,y,s=1):
    d.polygon([(x,y-70*s),(x+40*s,y),(x+45*s,y+35*s),(x+20*s,y+65*s),(x-20*s,y+65*s),(x-45*s,y+35*s),(x-40*s,y)],outline=SOFT,width=5)
def door(d,x,y,s=1):
    d.rectangle((x-65*s,y-100*s,x+65*s,y+110*s),outline=SOFT,width=5);d.ellipse((x+35*s,y,x+43*s,y+8*s),fill=GOLD)
def vent(d,x,y,s=1):
    d.ellipse((x-85*s,y-65*s,x+85*s,y+65*s),outline=SOFT,width=5);d.ellipse((x-55*s,y-40*s,x+55*s,y+40*s),outline=GOLD,width=5)
    for dx in[-30,0,30]:d.line((x+dx*s,y-30*s,x+dx*s,y+30*s),fill=SOFT,width=4)
def apartment(d,x,y,s=1):
    d.rectangle((x-85*s,y-115*s,x+85*s,y+120*s),outline=SOFT,width=5)
    for dx in[-45,20]:
        for dy in[-75,-10,55]:d.rectangle((x+dx*s,y+dy*s,x+(dx+25)*s,y+(dy+30)*s),outline=GOLD,width=4)
def snow(d,x,y,s=1):
    for angle in[0,60,120]:
        a=math.radians(angle);dx=35*s*math.cos(a);dy=35*s*math.sin(a);d.line((x-dx,y-dy,x+dx,y+dy),fill=SOFT,width=4)
for i,row in enumerate(script['sentences']):
    if i in aliases:continue
    key=f'picture-{i+1:03}';dest=O/f'sentence-{i+1:02}.png'
    if str(i)in photos:
        p=photos[str(i)];pi=p['imageinfo'];meta=pi['extmetadata'];clean=lambda k:re.sub('<[^>]+>','',meta.get(k,{}).get('value','')).strip();raw=R/p['path'];creator=clean('Artist');terms=clean('LicenseShortName')+' '+clean('LicenseUrl');source=pi['descriptionurl'];credit=p['title'].removeprefix('File:')+' — '+creator+'. '+terms+'. '+source+'. Full photograph resized and letterboxed;terms retained.';screen.append(p['title'].removeprefix('File:')+' — '+creator+' · '+clean('LicenseShortName'));image=ImageOps.exif_transpose(Image.open(raw)).convert('RGB');image.thumbnail((760,720),Image.Resampling.LANCZOS);im=Image.new('RGB',(760,720),BG);im.paste(image,((760-image.width)//2,(720-image.height)//2));im.save(dest);downloads.append(dict(**info(raw),url=p['download_url']));a=dict(asset_id=key,kind='foreground',visual_type='photograph',files=[info(dest)],creator=creator,reuse_terms=terms,source_url=source,required_credits=credit,relevance_verification=p['context'],creation_method=dict(tool=str(Path(__file__).relative_to(R)),transform='Complete photograph,EXIF orientation respected,proportionally resized,letterboxed.'))
    else:
        im,d=canvas('Borta eller hemma · säkerhetslås'if i==41 else plans[i]['title'])
        if i==3:
            d.rectangle((150,190,610,550),outline=SOFT,width=5);alarm(d,380,315,1.5);txt(d,380,465,'60 m²',48,430);txt(d,380,610,'en brandvarnare',31,620)
        elif i==4:
            d.rectangle((110,200,650,550),outline=SOFT,width=5);alarm(d,240,335,1);alarm(d,520,335,1);txt(d,380,155,'TILL EXEMPEL',31,620);txt(d,380,470,'65 m² → TVÅ brandvarnare',31,540)
        elif i==5:
            d.rectangle((120,210,640,560),outline=SOFT,width=5);d.line((120,385,640,385),fill=GOLD,width=6);txt(d,380,265,'yta för denna våning',28,430);txt(d,380,445,'yta för denna våning',28,430);txt(d,380,155,'OM FLER ÄN EN VÅNING',30,620);txt(d,380,610,'räkna SEPARAT',32,620)
        elif i==6:
            d.rectangle((150,190,610,560),outline=SOFT,width=5);d.line((150,375,610,375),fill=GOLD,width=6);alarm(d,380,280,.9);alarm(d,380,470,.9);txt(d,380,610,'på VARJE våning',32,620)
        elif i==10:
            heater(d,220,385,1.5);box(d,220,220,.8);no(d,220,210,85);txt(d,570,315,'även när bastun inte används',29,285);txt(d,380,610,'ALDRIG föremål på bastuugnen',29,620)
        elif i==11:
            heater(d,380,400,1.2);shirt(d,200,230,.65);shirt(d,600,420,.65);no(d,200,230,75);no(d,600,420,75);txt(d,190,370,'ovanför',28,240);txt(d,590,545,'nära',28,220);txt(d,380,610,'torka INTE tvätt här',31,620)
        elif i==12:
            d.rectangle((100,180,660,570),outline=SOFT,width=5);d.line((120,485,430,485,430,535),fill=GOLD,width=7);heater(d,570,420,.7);box(d,260,330,1.1);no(d,260,330,110);txt(d,380,610,'bastun är INTE förråd',31,620)
        elif i==13:
            heater(d,200,330,1.5);arrow(d,(325,355),(445,355));d.ellipse((475,240,675,440),outline=GOLD,width=6);txt(d,575,310,'AV',52,180);txt(d,380,155,'ELEKTRISK BASTUUGN',30,620);txt(d,380,610,'ALLTID efter användning',31,620)
        elif i==14:
            heater(d,170,345,1.05);clock(d,380,275,.9);d.rounded_rectangle((510,240,660,430),radius=10,outline=SOFT,width=5);d.rectangle((555,295,615,375),outline=GOLD,width=5);d.line((540,455,630,455),fill=GOLD,width=7);txt(d,380,155,'OM ELAGGREGATET INTE ANVÄNDS LÄNGE',25,620);txt(d,580,505,'säkring',30,250);txt(d,380,610,'avlägsna säkringen',29,620)
        elif i==15:
            house(d,150,230,.65);arrow(d,(230,280),(310,280));stove(d,170,440,.7);iron(d,570,440,.8);d.ellipse((325,385,435,495),outline=GOLD,width=5);txt(d,380,415,'AV',35,100);txt(d,380,155,'NÄR DU GÅR HEMIFRÅN',30,620);txt(d,380,610,'spis OCH ugn · TILL EXEMPEL strykjärn',26,620)
        elif i==17:
            apartment(d,190,330,1.25);d.line((440,490,480,490,480,440,520,440,520,390,560,390),fill=SOFT,width=6);extinguisher(d,600,300,.75);txt(d,380,155,'I VISSA HÖGHUS',32,620);txt(d,380,610,'också i trappuppgången',30,620)
        elif i==18:
            magnify(d,190,335,1.45);arrow(d,(315,350),(445,350));extinguisher(d,580,360,1.35);txt(d,380,155,'VAR FINNS DEN NÄRMASTE?',30,620);txt(d,380,610,'ta reda på platsen',31,620)
        elif i==20:
            stove(d,250,340,1.3);blanket(d,590,335,.95);txt(d,380,155,'TILL EXEMPEL',32,620);txt(d,380,610,'släckningsfilt nära spisen',30,620)
        elif i==21:
            stove(d,220,380,1.1);pot(d,220,245,.8);person(d,580,350,1.1);eye_x=580;d.line((490,300,390,270),fill=GOLD,width=5);txt(d,380,155,'HET SPIS · MATLAGNING',30,620);txt(d,380,610,'lämna INTE utan uppsikt',31,620)
        elif i==22:
            d.ellipse((100,195,260,355),outline=SOFT,width=5);d.ellipse((145,170,285,310),fill=PANEL);pot(d,560,350,1.4);txt(d,380,155,'OM DU LAGAR MAT PÅ NATTEN',29,620);txt(d,380,610,'var SÄRSKILT försiktig',31,620)
        elif i==23:
            bottle(d,180,330,1.25);pot(d,570,350,1.25);no(d,570,350,120);txt(d,380,155,'OM BERUSAD',33,620);txt(d,380,610,'laga INTE mat',34,620)
        elif i==25:
            person(d,150,270,.7);person(d,380,300,.4);d.ellipse((565,280,635,330),outline=SOFT,width=5);d.ellipse((610,250,650,290),outline=SOFT,width=4);d.polygon([(615,255),(615,230),(630,255)],outline=GOLD,width=4);txt(d,265,290,'ELLER',24,100);txt(d,475,290,'ELLER',24,100);d.ellipse((325,440,435,550),outline=GOLD,width=5);d.line((380,495,405,465),fill=SOFT,width=6);arrow(d,(380,370),(380,420));txt(d,380,610,'KAN AV MISSTAG vrida på spisen',28,620)
        elif i==26:
            stove(d,220,385,1.15);box(d,220,255,.6);arrow(d,(350,355),(445,355));flame(d,580,330,1.3);txt(d,380,155,'SPISEN PÅ AV MISSTAG + FÖREMÅL',27,620);txt(d,380,610,'föremålen KAN fatta eld',30,620)
        elif i==27:
            pot(d,380,300,1.1);flame(d,380,250,.55);d.arc((100,430,320,510),180,360,fill=SOFT,width=6);d.line((100,470,320,470),fill=SOFT,width=6);d.arc((190,400,230,450),180,360,fill=GOLD,width=5);blanket(d,570,465,.65);txt(d,380,450,'ELLER',27,160);txt(d,380,155,'OM MATFETT BRINNER',31,620);txt(d,210,555,'kastrullock',29,280);txt(d,570,595,'släckningsfilt',28,280)
        elif i==28:
            pot(d,190,340,1.25);flame(d,190,265,.6);drop(d,570,340,1.2);no(d,570,340,120);txt(d,380,155,'BRINNANDE MATFETT',31,620);txt(d,380,610,'använd INTE vatten',32,620)
        elif i==30:
            iron(d,175,315,1.2);plug(d,420,365,.75);outlet(d,620,365,.8);d.line((280,375,345,375),fill=SOFT,width=5);txt(d,380,155,'STRYKJÄRNET',33,620);txt(d,380,610,'kopplas OCKSÅ LOSS från vägguttaget',28,620)
        elif i==31:
            iron(d,180,320,.95);d.line((425,330,485,330,510,300),fill=SOFT,width=5);d.line((535,350,560,330,640,330),fill=SOFT,width=5);no(d,180,330,110);no(d,530,330,110);txt(d,380,330,'ELLER',26,150);txt(d,180,510,'apparat i dåligt skick',26,290);txt(d,570,510,'trasig sladd',29,290);txt(d,380,610,'använd INTE',34,620)
        elif i==32:
            iron(d,190,375,1.1);flame(d,190,265,.6);drop(d,570,340,1.25);no(d,570,340,120);txt(d,380,155,'OM ELAPPARAT BRINNER',30,620);txt(d,380,610,'använd INTE vatten',32,620)
        elif i==33:
            iron(d,180,375,1);flame(d,180,265,.6);arrow(d,(310,355),(445,355));extinguisher(d,580,335,1.3);txt(d,380,155,'ELAPPARAT BRINNER',31,620);txt(d,380,610,'TILL EXEMPEL brandsläckare',29,620)
        elif i==35:
            house(d,380,325,1.8);d.rectangle((285,355,455,380),outline=SOFT,width=5);d.line((420,355,420,380),fill=GOLD,width=5);no(d,380,365,110);txt(d,380,610,'rök INTE inomhus',33,620)
        elif i==37:
            candle(d,200,350,1.2);d.line((485,205,660,205),fill=GOLD,width=6)
            for x in[500,540,580,620,660]:d.line((x,210,x-10,490),fill=SOFT,width=5)
            no(d,380,340,75);person(d,600,565,.35);txt(d,380,155,'INTE NÄRA TILL EXEMPEL GARDINER',27,620);txt(d,380,610,'ÄVEN OM du är i rummet',30,620)
        elif i==39:
            apartment(d,165,290,.8);house(d,385,285,.65);txt(d,270,315,'ELLER',24,100);phone(d,610,340,1);d.line((380,450,510,450),fill=GOLD,width=5);txt(d,380,155,'OM HÖGHUS ELLER RADHUS',29,620);txt(d,380,610,'läckage → servicebolagets JOURNUMMER GENAST',23,650)
        elif i==40:
            house(d,190,290,1.2);arrow(d,(315,355),(445,355));phone(d,580,315,1.2);txt(d,380,155,'OM DU BOR I VILLA',31,620);txt(d,380,610,'läckage → jourhavande RÖRFIRMA',28,620)
        elif i==41:
            d.line((380,165,380,595),fill=LINE,width=4);house(d,180,260,.7);arrow(d,(180,360),(265,360));lock(d,190,450,.85);d.line((190-35*.85,450-22.5*.85,190-35*.85,460),fill=SOFT,width=4);d.line((190+35*.85,450-22.5*.85,190+35*.85,460),fill=SOFT,width=4);house(d,580,260,.7);person(d,580,300,.45);lock(d,580,465,.75);no(d,580,495,80);txt(d,180,155,'OM säkerhetslås · BORTA',25,300);txt(d,580,155,'HEMMA',31,280);txt(d,180,585,'lås ALLTID',28,285);txt(d,580,585,'lås INTE',28,285)
        elif i==43:
            house(d,190,310,1.2);d.line((140,350,180,310,200,355,235,320),fill=GOLD,width=6);arrow(d,(315,355),(445,355));phone(d,580,315,1.2);txt(d,580,305,'112',43,160);txt(d,380,155,'OM NÅGON BRYTER SIG IN',30,620);txt(d,380,610,'ring nödnumret',32,620)
        elif i==44:
            house(d,380,340,2);snow(d,135,265,.8);snow(d,635,445,.7)
            for x in[330,380,430]:d.arc((x-15,330,x+20,455),230,60,fill=GOLD,width=4)
            txt(d,380,155,'VINTER',32,620);txt(d,380,610,'täta hus håller värmen inne',29,620)
        elif i==45:
            drop(d,170,320,1.2);arrow(d,(285,355),(445,355));d.line((495,220,495,490,675,490),fill=SOFT,width=8);d.line((545,250,560,300,540,345,565,395),fill=GOLD,width=5);txt(d,380,155,'FUKT I TÄTA HUS',31,620);txt(d,380,610,'KAN snabbt orsaka problem i väggar och golv',25,620)
        elif i==47:
            drop(d,175,315,1.05);d.rectangle((470,300,650,410),outline=SOFT,width=5);d.line((465,435,675,435),fill=GOLD,width=6);arrow(d,(285,355),(440,355));txt(d,380,155,'OM VÄGGAR ELLER GOLV BLIR VÅTA',28,620);txt(d,380,610,'torka NOGGRANT',33,620)
        elif i==48:
            vent(d,220,335,1.5);drop(d,490,335,.65);arrow(d,(570,355),(670,355));txt(d,380,155,'VENTILATION',32,620);txt(d,380,610,'fuktig luft UT',33,620)
        elif i==49:
            vent(d,190,315,1.25);calendar(d,580,300,1.2);txt(d,190,485,'ÖPPNA OCH RENA',27,290);txt(d,580,485,'ÅRET OM',31,290);txt(d,380,610,'får INTE stängas',32,620)
        elif i==50:
            house(d,190,330,1.15);flame(d,190,265,.6);arrow(d,(315,355),(445,355));phone(d,580,315,1.2);txt(d,580,305,'112',43,160);txt(d,380,155,'OM DET BRINNER I HUSET',30,620);txt(d,380,610,'ring GENAST nödnumret',31,620)
        elif i==51:
            d.rectangle((90,235,360,550),outline=SOFT,width=5);person(d,220,375,.85);door(d,360,400,.7);d.line((460,525,500,525,500,475,540,475,540,425,580,425,580,375,620,375),fill=SOFT,width=5)
            for x,y in[(500,285),(555,250),(610,290)]:d.arc((x-40,y-30,x+40,y+45),45,320,fill=SOFT,width=5)
            txt(d,380,155,'HÖGHUS + RÖK I TRAPPUPPGÅNGEN',28,620);txt(d,380,610,'lämna INTE bostaden',32,620)
        elif i==52:
            d.rectangle((205,210,555,540),outline=SOFT,width=5);d.line((380,215,380,535),fill=GOLD,width=5);no(d,380,375,155);flame(d,625,480,.7);txt(d,380,155,'OM BRAND I HUSET',31,620);txt(d,380,610,'använd INTE hissen',32,620)
        elif i==53:
            person(d,165,325,.8);person(d,320,355,.5);book(d,570,330,1.3);arrow(d,(395,355),(445,355));txt(d,380,155,'ALLA BOENDE · OCKSÅ BARN',29,620);txt(d,380,610,'vet hur man ska göra vid brand',29,620)
        elif i==54:
            d.rectangle((130,210,630,565),outline=SOFT,width=5);door(d,380,340,.85);d.rounded_rectangle((280,450,480,545),radius=12,outline=SOFT,width=5);no(d,380,495,90);txt(d,380,155,'BALKONGDÖRREN',32,620);txt(d,380,610,'INGA möbler framför · ut OM behov',28,620)
        else:raise ValueError('Missing source-specific household-safety composition '+str(i))
        im.save(dest);refs=[row['sentence_id']]
        if i in[27,28]:refs=[script['sentences'][j]['sentence_id']for j in[27,28]]
        if i in[32,33]:refs=[script['sentences'][j]['sentence_id']for j in[32,33]]
        a=dict(asset_id=key,kind='foreground',visual_type='diagram',files=[info(dest)],creator='Homebrew video studio',reuse_terms='Original schematic artwork under repository MIT license;source wording retains publisher terms.',required_credits='Original source-based household-safety illustrations: Homebrew video studio;source wording credited in sources.yaml and CREDITS.md.',relevance_verification=plans[i]['request']+' Individually composed source-specific relationship,no invented safety distance,procedure,alarmtestinterval,appliancecompatibility,plumbingdirection,evacuationroute or emergencycontact.',creation_method=dict(tool=str(Path(__file__).relative_to(R)),source_sentence_ids=refs))
    assets.append(a);by_index[i]=a
for i,row in enumerate(script['sentences']):
    a=by_index[aliases.get(i,i)];row.update(asset_ids=['episode_background',a['asset_id']],render_image=a['files'][0]['path'],render_caption=False)
    if i in aliases:a['creation_method']['source_sentence_ids'].append(row['sentence_id']);row['visual_cue']='Retain the useful two-state security-lock source picture: '+plans[i]['request']
script['asset_requests']=script['asset_requests'][:3]+[dict(id=a['asset_id'],kind='foreground',description=a['relevance_verification'],fallback='Useful exact-source original pictorial explanation;record honest omission if reasonable research fails.')for a in assets];script['render']['credits']=script['render']['credits'][:2]
for j in range(0,len(screen),2):script['render']['credits'].append(dict(heading='Förgrundsbilder · Изображения',paragraphs=screen[j:j+2]+['Original schematisk grafik: Homebrew video studio.','Fullständiga källor och licenser i CREDITS.md.']))
for decision in script['episode_decisions']:
    if decision['id']=='visuals':decision['decision']=f'All55exactsource slides pictured with{len(assets)}sourcepictures:{len(screen)}licensed actual photos and{len(assets)-len(screen)}specific original household-safety diagrams.Security-lock two-state comparison is meaningfully retained for two adjacentsource sentences.No stagedlivehazards,invented electrical/plumbingprocedure,safedistance,evacuationroute or contactnumber.'
(E/'script.yaml').write_text(yaml.safe_dump(script,allow_unicode=True,sort_keys=False,width=100));(E/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');(E/'foreground-downloads.json').write_text(json.dumps(downloads,ensure_ascii=False,indent=2)+'\n');(E/'prepare_assets.py').write_text((R/'studio/episodes/hb-c10-utkomststod/prepare_assets.py').read_text().replace('Textgrafik: exakta ord och tal ur källtexten.','Original källbaserad grafik: Homebrew video studio.'));print('Prepared',len(assets),'sourcepictures;',len(screen),'photos for55slides.')
