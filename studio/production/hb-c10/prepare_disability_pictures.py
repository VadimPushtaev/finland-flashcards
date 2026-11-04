"""Draw exact source-qualified ageing support relationships and preserve licensed photographs."""
from pathlib import Path
import json,yaml,hashlib,re,math
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parents[3];SID='hb-c10-funktionsnedsattning';E=R/'studio/episodes'/SID;M=R/'studio/media'/SID;O=M/'pictures';O.mkdir(parents=True,exist_ok=True)
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


photos=json.loads((E/'selected-photos.json').read_text());script=yaml.safe_load((E/'script.yaml').read_text());plans=json.loads((E/'picture-plan.json').read_text());assets=[];downloads=[];screen=[];by_index={};aliases={19:17,37:7,59:57}
def door(d,x,y,s=1):
    d.rectangle((x-65*s,y-100*s,x+65*s,y+110*s),outline=SOFT,width=5);d.ellipse((x+35*s,y,x+43*s,y+8*s),fill=GOLD)

def eu_card(d,x,y,s=1,mark=False):
    d.rounded_rectangle((x-100*s,y-65*s,x+100*s,y+65*s),radius=15,outline=SOFT,width=5);person(d,x-45*s,y,.35*s);d.line((x+10*s,y-15*s,x+75*s,y-15*s),fill=GOLD,width=5);d.line((x+10*s,y+20*s,x+75*s,y+20*s),fill=LINE,width=5)
    if mark:txt(d,x+45*s,y-45*s,'A',int(35*s),80*s,GOLD)
def wheelchair(d,x,y,s=1):
    d.ellipse((x-70*s,y-25*s,x+30*s,y+75*s),outline=SOFT,width=6);d.ellipse((x-58*s,y-13*s,x+18*s,y+63*s),outline=GOLD,width=4);d.line([(x-15*s,y-75*s),(x-15*s,y+15*s),(x+55*s,y+15*s),(x+75*s,y+65*s),(x+105*s,y+65*s)],fill=SOFT,width=6);d.line((x-40*s,y-85*s,x-15*s,y-75*s),fill=GOLD,width=5);d.ellipse((x+60*s,y+60*s,x+90*s,y+90*s),outline=SOFT,width=5)
def bus(d,x,y,s=1):
    d.rounded_rectangle((x-100*s,y-65*s,x+100*s,y+55*s),radius=12,outline=SOFT,width=5)
    for dx in[-70,-10,50]:d.rectangle((x+dx*s,y-45*s,x+(dx+35)*s,y-5*s),outline=GOLD,width=4)
    for dx in[-60,60]:d.ellipse((x+(dx-25)*s,y+35*s,x+(dx+25)*s,y+85*s),outline=SOFT,width=5)
def car(d,x,y,s=1):
    d.line([(x-100*s,y+40*s),(x-100*s,y),(x-60*s,y-15*s),(x-35*s,y-60*s),(x+45*s,y-60*s),(x+75*s,y-10*s),(x+100*s,y),(x+100*s,y+40*s),(x-100*s,y+40*s)],fill=SOFT,width=5)
    for dx in[-60,60]:d.ellipse((x+(dx-22)*s,y+20*s,x+(dx+22)*s,y+65*s),outline=GOLD,width=5)
def brush(d,x,y,s=1):
    d.line((x-35*s,y+70*s,x+20*s,y-25*s),fill=SOFT,width=8);d.polygon([(x+5*s,y-40*s),(x+35*s,y-90*s),(x+50*s,y-35*s),(x+20*s,y-10*s)],outline=GOLD,width=5)
def bell(d,x,y,s=1):
    d.arc((x-50*s,y-70*s,x+50*s,y+40*s),180,360,fill=SOFT,width=5);d.line((x-50*s,y-15*s,x-65*s,y+45*s,x+65*s,y+45*s,x+50*s,y-15*s),fill=SOFT,width=5);d.ellipse((x-15*s,y+50*s,x+15*s,y+75*s),outline=GOLD,width=5)
for i,row in enumerate(script['sentences']):
    if i in aliases:continue
    key=f'picture-{i+1:03}';dest=O/f'sentence-{i+1:02}.png'
    if str(i)in photos:
        p=photos[str(i)];pi=p['imageinfo'];meta=pi['extmetadata'];clean=lambda k:re.sub('<[^>]+>','',meta.get(k,{}).get('value','')).strip();raw=R/p['path'];creator=clean('Artist');terms=clean('LicenseShortName')+' '+clean('LicenseUrl');source=pi['descriptionurl'];credit=p['title'].removeprefix('File:')+' — '+creator+'. '+terms+'. '+source+'. Full source proportionally resized,letterboxed;terms retained.';screen.append(p['title'].removeprefix('File:')+' — '+creator+' · '+clean('LicenseShortName'));image=ImageOps.exif_transpose(Image.open(raw)).convert('RGB');image.thumbnail((760,720),Image.Resampling.LANCZOS);im=Image.new('RGB',(760,720),BG);im.paste(image,((760-image.width)//2,(720-image.height)//2));im.save(dest);downloads.append(dict(**info(raw),url=p['download_url']));a=dict(asset_id=key,kind='foreground',visual_type='photograph',files=[info(dest)],creator=creator,reuse_terms=terms,source_url=source,required_credits=credit,relevance_verification=p['context'],creation_method=dict(tool=str(Path(__file__).relative_to(R)),transform='Complete photograph EXIF respected,proportionally resized,letterboxed.'))
    else:
        im,d=canvas(plans[i]['title'])
        if i==0:
            person(d,380,300,1.1);bubble(d,180,200,'VILKA?',190);bubble(d,580,200,'VAR?',170);bubble(d,380,485,'HUR?',180);txt(d,380,155,'OFTA · INFORMATION SAKNAS',29,620);txt(d,380,610,'tjänster · ansökan · användning',29,620)
        elif i==1:
            paper(d,185,295,165,225);house(d,575,280,1.2);txt(d,380,315,'OCH',29,160);txt(d,185,465,'uppehållstillstånd',26,290);txt(d,575,475,'hemkommun i Finland',26,290);d.rounded_rectangle((70,180,690,550),radius=20,outline=GOLD,width=5);txt(d,380,610,'rätt till olika tjänster · TILL EXEMPEL',26,620)
        elif i==2:
            person(d,170,300,.9);paper(d,380,320,170,220);person(d,590,300,.9);txt(d,380,155,'KAN GÖRAS UPP TILLSAMMANS',29,620);txt(d,170,490,'nyinflyttad person',25,285);txt(d,590,490,'områdets socialvård',25,285);txt(d,380,610,'klientplan för funktionshinderservice',27,620)
        elif i==4:
            shield(d,380,275,1);book(d,170,470,.9);house(d,380,450,.8);hardhat(d,590,460,1);d.line((380,340,170,390),fill=GOLD,width=4);d.line((380,340,380,360),fill=GOLD,width=4);d.line((380,340,590,390),fill=GOLD,width=4);txt(d,380,155,'LIKA RÄTT · TILL EXEMPEL',30,620);txt(d,170,605,'språkundervisning',22,215);txt(d,380,605,'utbildning',25,200);txt(d,590,605,'sysselsättning',23,215)
        elif i==6:
            institution(d,190,330,1.2);arrow(d,(315,355),(445,355));person(d,580,300,1.05);shield(d,580,355,.65);txt(d,380,155,'OMRÅDETS SKYLDIGHET',30,620);txt(d,380,610,'särskilda tjänster för funktionsnedsättning',25,620)
        elif i==8:
            record(d,380,290,'långtidssjuk',.8);house(d,180,455,.8);hardhat(d,580,465,.9);txt(d,380,435,'ELLER',27,160);txt(d,180,575,'svårt med dagliga aktiviteter',24,285);txt(d,580,575,'problem med arbetsförmåga',24,285);txt(d,380,155,'EN DEL TJÄNSTER · PÅ GRUND AV SJUKDOM',25,620)
        elif i==9:
            person(d,380,275,.7);clock(d,170,250,.7);hardhat(d,590,250,.7)
            for x,y,t in[(170,440,'diabetes'),(380,440,'epilepsi'),(590,440,'astma'),(270,560,'reumatism'),(510,560,'artros')]:record(d,x,y,'',.35);txt(d,x,y+50,t,25,205)
            txt(d,380,155,'KAN FÖRSÄMRA FÖRMÅGAN · TILL EXEMPEL',26,620)
        elif i==10:
            bus(d,180,290,.8);no(d,180,290,95);person(d,570,290,.8);person(d,655,315,.55);txt(d,380,315,'ELLER',27,160);car(d,380,525,.7);txt(d,380,155,'FUNKTIONSNEDSÄTTNING',29,620);txt(d,180,445,'kan inte använda kollektivtrafik',24,285);txt(d,580,445,'behöver hjälp utanför hemmet',24,285);txt(d,380,610,'färdtjänst',32,620)
        elif i==11:
            person(d,170,300,.9);plate(d,170,485,.6);arrow(d,(300,355),(445,355));person(d,540,320,.8);person(d,650,320,.8);heart(d,595,475,.6);txt(d,380,155,'DAGLIGT MAN INTE KLARAR SJÄLV',28,620);txt(d,380,610,'på grund av funktionsnedsättning ELLER sjukdom',24,650)
        elif i==13:
            institution(d,175,300,1);coins(d,390,345,3);person(d,600,300,1);arrow(d,(275,355),(300,355));arrow(d,(475,355),(515,355));txt(d,175,510,'välfärdsområdet',26,285);txt(d,600,510,'assistent',31,285);txt(d,380,610,'betalar ASSISTENTENS LÖN',29,620)
        elif i==14:
            institution(d,380,300,1);supporthome(d,180,470,.9);house(d,580,450,.9);person(d,580,475,.45);arrow(d,(300,355),(245,420));arrow(d,(460,355),(515,420));txt(d,180,600,'serviceboende',27,285);txt(d,580,600,'stött boende',28,285);txt(d,380,155,'VÄLFÄRDSOMRÅDET ORDNAR',29,620)
        elif i==15:
            person(d,180,300,1);coins(d,390,350,3);house(d,600,295,1.1);arrow(d,(270,355),(300,355));arrow(d,(475,355),(500,355));txt(d,380,155,'INVÅNAREN',33,620);txt(d,380,610,'betalar SJÄLV boendekostnaderna',29,620)
        elif i==16:
            house(d,380,275,1);plate(d,190,465,.7);person(d,570,465,.65);coins(d,380,500,2);no(d,380,500,65);txt(d,380,155,'SÄRSKILDA HEMTJÄNSTER OCH STÖD',27,620);txt(d,380,610,'dagliga sysslor hemma → AVGIFTSFRIA',27,620)
        elif i==20:
            person(d,180,300,1);shield(d,180,350,.8);arrow(d,(315,355),(445,355));paper(d,580,320,180,220);txt(d,580,295,'P',57,150);txt(d,380,155,'GRAVT HANDIKAPPAD · KAN FÅ',29,620);txt(d,380,610,'parkeringstillstånd för rörelsehindrade',27,620)
        elif i==22:
            d.rectangle((95,275,350,500),outline=SOFT,width=5);txt(d,220,325,'P',57,180);wheelchair(d,220,430,.45);d.rectangle((450,190,660,520),outline=SOFT,width=5);door(d,555,370,.8);d.line((360,440,430,440),fill=GOLD,width=5);txt(d,380,610,'markerad plats NÄRA ingången',29,620)
        elif i==23:
            ear(d,150,280,.65);d.rounded_rectangle((280,195,480,365),radius=14,outline=GOLD,width=4);ear(d,330,275,.5);eye(d,430,275,.4);bubble(d,610,235,'...',135);txt(d,150,400,'hörsel',26,180);txt(d,380,400,'syn OCH hörsel',24,220);txt(d,610,400,'tal',27,180);bubble(d,380,490,'TOLKNING',250);txt(d,380,155,'ELLER MELLAN DE TRE GRUPPERNA',27,620);txt(d,380,620,'KAN FÅ',24,620)
        elif i==25:
            institution(d,380,300,1);baby(d,170,465,.6);book(d,380,470,.75);house(d,590,450,.75);arrow(d,(300,355),(220,400));arrow(d,(460,355),(540,400));txt(d,380,155,'AV HEMKOMMUNEN · KAN FÅ',29,620);txt(d,170,600,'småbarnspedagogik',21,220);txt(d,380,600,'förskola',26,200);txt(d,590,600,'grundläggande undervisning',21,220)
        elif i==26:
            paper(d,190,335,190,230);tick(d,190,335);arrow(d,(315,355),(445,355));bubble(d,570,280,'tolk',190);coins(d,570,490,2);no(d,570,490,70);txt(d,380,155,'OM RÄTTEN HAR BEVILJATS',30,620);txt(d,380,610,'tolkningstjänst GRATIS',31,620)
        elif i==28:
            person(d,180,300,1);shield(d,180,355,.7);record(d,580,300,'svår sjukdom',1);txt(d,380,315,'ELLER',27,160);txt(d,380,155,'GRAV FUNKTIONSNEDSÄTTNING',29,620);arrow(d,(230,500),(310,540));arrow(d,(530,500),(450,540));doctor(d,380,545,.45);txt(d,380,620,'KAN få rehabilitering',30,620)
        elif i==29:
            person(d,190,350,.65);person(d,580,315,1.2);txt(d,380,350,'OCH',29,160);txt(d,190,535,'barn',33,280);txt(d,580,535,'vuxna',33,280);txt(d,380,610,'BÅDA kan få rehabilitering',29,620)
        elif i==30:
            person(d,160,300,1);group(d,590,280,.75);doctor(d,380,510,.7);d.line((160,430,300,510),fill=GOLD,width=4);d.line((590,430,460,510),fill=GOLD,width=4);txt(d,380,315,'OCH',27,160);txt(d,160,470,'personen',28,240);txt(d,590,470,'familjen',28,240);txt(d,380,610,'erbjuds rehabilitering',30,620)
        elif i==31:
            doctor(d,380,300,.8);d.ellipse((110,430,230,550),outline=GOLD,width=5);chairs(d,380,470,.6);bubble(d,610,430,'...',140);brush(d,610,570,.45);txt(d,380,155,'LEDD AV YRKESPERSON · EXEMPEL',28,620);txt(d,170,585,'fysioterapi',23,200);txt(d,380,585,'psykoterapi',23,200);txt(d,610,615,'tal- / ergoterapi',22,240)
        elif i==32:
            book(d,190,320,1.3);arrow(d,(315,355),(445,355));person(d,580,380,1);bubble(d,580,195,'tolk',170);txt(d,380,155,'MÖJLIGT',33,620);txt(d,380,610,'tolk för rehabiliteringskurser',29,620)
        elif i==34:
            person(d,160,310,.85);paper(d,370,320,150,190);eu_card(d,610,340,.85);arrow(d,(245,355),(275,355));arrow(d,(465,355),(500,355));txt(d,380,155,'KAN ANSÖKA I FINLAND',31,620);txt(d,380,610,'EU:s funktionshinderkort',30,620)
        elif i==35:
            person(d,180,275,.85);record(d,580,270,'långvarig sjukdom',.85);txt(d,180,425,'permanent funktionsnedsättning',24,285);txt(d,380,285,'ELLER',27,160);eu_card(d,380,550,.75);txt(d,380,155,'KORTET BEVILJAS',31,620)
        elif i==38:
            eu_card(d,190,340,1.1,True);arrow(d,(315,355),(445,355));person(d,560,320,.8);bubble(d,650,290,'...',100);coins(d,580,485,2);no(d,580,485,65);txt(d,380,155,'MÅNGA STÄLLEN · KORTET VISAS OCH HAR A',25,650);txt(d,190,535,'funktionshinderkort',25,285);txt(d,580,585,'assistent ELLER tolk gratis',25,285)
        elif i==39:
            chairs(d,380,340,1.25);book(d,380,520,.7);shield(d,380,260,.65);txt(d,380,155,'HANDIKAPP- OCH PATIENTORGANISATIONER',25,650);txt(d,380,610,'bevakar medlemmarnas intressen',28,620)
        elif i==40:
            person(d,150,370,.8);bubble(d,150,190,'...',150);group(d,380,300,.6);institution(d,620,300,.8);arrow(d,(235,355),(285,355));arrow(d,(470,355),(525,355));txt(d,380,155,'MÖJLIGT ATT PÅVERKA',31,620);txt(d,380,610,'via organisationerna → samhället',28,620)
        elif i==41:
            door(d,180,305,.8);d.line((480,225,480,425,620,425),fill=SOFT,width=7);d.line((480,225,620,225),fill=GOLD,width=5);txt(d,380,325,'ELLER',27,160);txt(d,180,480,'nödvändiga ändringar',25,285);txt(d,570,480,'fasta hjälpmedel',27,285);coins(d,380,565,3);txt(d,380,155,'OM DET MÅSTE GÖRAS',30,620);txt(d,380,620,'KAN få ersättning',30,620)
        elif i==42:
            house(d,380,300,1.4);d.line((190,485,570,485),fill=GOLD,width=6);wheelchair(d,380,475,1);txt(d,380,155,'TILL EXEMPEL',32,620);txt(d,380,610,'bostad där rullstol kan användas',29,620)
        elif i==43:
            d.line((110,225,110,470,285,470),fill=SOFT,width=7);d.line((110,225,285,225),fill=GOLD,width=6);d.line((220,225,220,350),fill=SOFT,width=4);d.arc((180,325,260,405),0,180,fill=GOLD,width=5);bell(d,570,280,.8);d.ellipse((525,435,615,525),outline=GOLD,width=5)
            for x,y in[(500,420),(640,420),(500,540),(640,540)]:d.line((x,y,x+(10 if x<570 else-10),y+(10 if y<480 else-10)),fill=GOLD,width=5)
            txt(d,380,155,'TILL EXEMPEL FASTA HJÄLPMEDEL',28,620);txt(d,190,555,'lyftanordning',26,285);txt(d,570,575,'ljus ersätter ljud i larm / dörrklocka',24,295)
        elif i==44:
            person(d,170,300,.9);person(d,580,300,.9);paper(d,380,330,160,200);house(d,380,530,.65);txt(d,380,155,'BEDÖMNING TILLSAMMANS MED DIG',28,620);txt(d,170,495,'socialarbetare',26,285);txt(d,580,495,'du',32,285);txt(d,380,620,'behövs ändringar hemma?',29,620)
        elif i==45:
            person(d,160,300,.85);bus(d,380,310,.85);no(d,380,310,95);car(d,610,330,.7);arrow(d,(485,355),(515,355));txt(d,380,155,'PÅ GRUND AV FUNKTIONSNEDSÄTTNING',27,620);txt(d,380,610,'kan inte använda kollektivtrafik → KAN ha rätt',24,650)
        elif i==46:
            person(d,260,310,1);person(d,510,310,1);suitcase(d,385,480,.65);txt(d,380,155,'VID BEHOV · KAN FÖLJA MED',30,620);txt(d,380,610,'ledsagare assisterar på resor',29,620)
        elif i==48:
            person(d,150,310,.8);paper(d,380,320,160,200);institution(d,620,300,.9);arrow(d,(235,355),(275,355));arrow(d,(475,355),(515,355));txt(d,380,155,'KAN ANSÖKA OM FÄRDTJÄNST',29,620);txt(d,380,610,'egna områdets funktionshinderservice',27,620)
        elif i==49:
            car(d,180,300,.95);bus(d,580,300,.95);coins(d,180,480,2);coins(d,580,480,2);txt(d,380,455,'≤',74,150);txt(d,180,585,'färdtjänst',28,285);txt(d,580,585,'kollektivtrafikens taxa',24,285);txt(d,380,155,'DU BETALAR HÖGST SAMMA TAXA',29,620)
        elif i==50:
            d.rounded_rectangle((65,205,695,535),radius=18,outline=GOLD,width=5);person(d,155,300,.65);record(d,300,300,'sjukdom',.55);txt(d,230,410,'svår funktionsnedsättning ELLER sjukdom',23,320);calendar(d,570,290,.85);txt(d,570,430,'UNDER 65 ÅR',28,270);txt(d,405,310,'OCH',25,100);txt(d,380,155,'OM BÅDA VILLKOREN',30,620);institution(d,180,570,.4);coins(d,565,575,2);txt(d,380,610,'FPA KAN ordna och ersätta EN DEL',27,620)
        elif i==51:
            record(d,380,280,'',.7);house(d,160,450,.75);hardhat(d,380,450,.85);book(d,600,450,.75);d.line((380,350,160,390),fill=GOLD,width=4);d.line((380,350,380,390),fill=GOLD,width=4);d.line((380,350,600,390),fill=GOLD,width=4);txt(d,380,155,'PÅ GRUND AV FUNKTIONSNEDSÄTTNING / SJUKDOM',24,650);txt(d,380,610,'STORA svårigheter i hemmet ELLER jobbet ELLER skolan',23,650)
        elif i==52:
            institutionhouse(d,190,300,1.1);house(d,580,270,1);person(d,580,345,.6);arrow(d,(520,485),(640,485));txt(d,380,315,'ELLER',27,160);txt(d,190,535,'rehabiliteringsinrättning',24,290);txt(d,580,550,'bo hemma och besöka rehabilitering',24,285)
        elif i==54:
            person(d,180,350,.65);shield(d,180,405,.75);doctor(d,580,320,1.05);arrow(d,(315,355),(445,355));txt(d,380,155,'BARN MED SVÅR FUNKTIONSNEDSÄTTNING',27,650);txt(d,380,610,'KAN få krävande medicinsk rehabilitering',26,620)
        elif i==58:
            brain(d,180,290,.9);heart(d,580,290,.8);txt(d,380,315,'OCH',28,160);txt(d,180,445,'intellektuell funktionsnedsättning',23,285);txt(d,580,445,'behöver vård',29,285);house(d,380,535,.7);txt(d,380,610,'KAN bo i familjehem',31,620)
        elif i==60:
            house(d,380,310,1.7);person(d,285,380,.65);person(d,475,380,.65);heart(d,380,495,.65);txt(d,380,155,'KAN ÄVEN ORDNAS',32,620);txt(d,380,610,'familjevård i EGET HEM',31,620)
        elif i==61:
            brain(d,170,275,.65);clock(d,580,275,.75);txt(d,170,390,'intellektuell funktionsnedsättning',22,275);txt(d,580,390,'kontinuerligt vårdbehov',24,285);txt(d,380,300,'OCH',26,120);house(d,190,540,.6);no(d,190,540,70);supporthome(d,570,540,.6);no(d,570,540,70);txt(d,380,535,'OCH',26,130);txt(d,380,155,'KAN BO PÅ ANSTALT OM ALLT GÄLLER',28,650);txt(d,380,620,'VARKEN vård hemma ELLER i servicebostad går',25,650)
        elif i==62:
            institutionhouse(d,190,315,1.15);calendar(d,580,310,1.15);d.line((315,355,445,355),fill=GOLD,width=5);txt(d,380,155,'KAN OCKSÅ',33,620);txt(d,380,610,'korta tider i en anstalt',31,620)
        elif i==65:
            person(d,180,280,.85);shield(d,180,340,.65);brush(d,580,315,.95);no(d,580,315,100);txt(d,380,315,'OCH',28,160);txt(d,180,475,'svår funktionsnedsättning',24,285);txt(d,580,475,'kan inte delta i arbetsverksamhet',24,285);txt(d,380,155,'DAGVERKSAMHET AVSEDD FÖR',29,620);txt(d,380,610,'båda villkoren',31,620)
        else:raise ValueError('Missing source-specific disability-service picture '+str(i))
        im.save(dest);a=dict(asset_id=key,kind='foreground',visual_type='diagram',files=[info(dest)],creator='Homebrew video studio',reuse_terms='Original schematic artwork under repository MIT license;source wording retains publisher terms.',required_credits='Original source-based disability-service illustrations: Homebrew video studio;source wording credited in sources.yaml and CREDITS.md.',relevance_verification=plans[i]['request']+' Individually composed source-specific relationship,no invented clinicalprocedure,diagnosis,agecutoff,fee,approvalguarantee,countryacceptance list,officialcardtemplate or currentnamedprogramme.',creation_method=dict(tool=str(Path(__file__).relative_to(R)),source_sentence_ids=[row['sentence_id']]))
    assets.append(a);by_index[i]=a
for i,row in enumerate(script['sentences']):
    a=by_index[aliases.get(i,i)];row.update(asset_ids=['episode_background',a['asset_id']],render_image=a['files'][0]['path'],render_caption=False)
    if i in aliases:a['creation_method'].setdefault('source_sentence_ids',[script['sentences'][aliases[i]]['sentence_id']]).append(row['sentence_id']);row['visual_cue']='Retain actual source photograph for its useful related statement: '+plans[i]['request']
script['asset_requests']=script['asset_requests'][:3]+[dict(id=a['asset_id'],kind='foreground',description=a['relevance_verification'],fallback='Useful exact-source original pictorial explanation;record honest omission if reasonable research fails.')for a in assets];script['render']['credits']=script['render']['credits'][:2]
for j in range(0,len(screen),2):script['render']['credits'].append(dict(heading='Förgrundsbilder · Изображения',paragraphs=screen[j:j+2]+['Original schematisk grafik: Homebrew video studio.','Fullständiga källor och licenser i CREDITS.md.']))
for decision in script['episode_decisions']:
    if decision['id']=='visuals':decision['decision']=f'All67source slides pictured with{len(assets)}sourcepictures:{len(screen)}licensed actualphotos and{len(assets)-len(screen)}specific original diagrams.Three useful aid/access/home continuations retain actualphotos.No actualperson assigneddiagnosis,immigration,benefitstatus or serviceapproval;no genericfakecountrymap,officialpermittemplate or inventedprocedure.'
(E/'script.yaml').write_text(yaml.safe_dump(script,allow_unicode=True,sort_keys=False,width=100));(E/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');(E/'foreground-downloads.json').write_text(json.dumps(downloads,ensure_ascii=False,indent=2)+'\n');(E/'prepare_assets.py').write_text((R/'studio/episodes/hb-c10-utkomststod/prepare_assets.py').read_text().replace('Textgrafik: exakta ord och tal ur källtexten.','Original källbaserad grafik: Homebrew video studio.'));print('Prepared',len(assets),'sourcepictures;',len(screen),'photos for67slides.')
