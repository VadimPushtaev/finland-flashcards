"""Compose distinct welfare relationships where generic icon pairs repeat too closely."""
from pathlib import Path
import json,yaml,hashlib,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];EP=ROOT/'studio/episodes/hb-c10-valfard';MEDIA=ROOT/'studio/media/hb-c10-valfard'
code=(ROOT/'studio/production/hb-c10/author_utkomststod.py').read_text().split('specs=')[0];ns={'__file__':str(Path(__file__))};exec(compile(code,'welfare-drawing-primitives','exec'),ns)
canvas,label,house,person,coins,paper,arrow=[ns[k] for k in ['canvas','label','house','person','coins','paper','arrow']];FG,SOFT,GOLD,LINE,PANEL,BG=[ns[k] for k in ['FG','SOFT','GOLD','LINE','PANEL','BG']]
def info(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def envelope(draw,x,y,w=145,h=95):
    draw.rounded_rectangle((x-w/2,y-h/2,x+w/2,y+h/2),radius=8,outline=SOFT,width=5);draw.line([(x-w/2,y-h/2),(x,y+12),(x+w/2,y-h/2)],fill=GOLD,width=4)
def bag(draw,x,y):
    draw.rounded_rectangle((x-80,y-55,x+80,y+90),radius=18,outline=SOFT,width=6);draw.arc((x-32,y-88,x+32,y-30),180,360,fill=GOLD,width=6)
def clinic(draw,x,y):
    house(draw,x,y,.75);draw.rectangle((x-8,y+8,x+8,y+56),fill=GOLD);draw.rectangle((x-25,y+24,x+25,y+40),fill=GOLD)
assets=json.loads((EP/'foreground-assets.json').read_text());d=yaml.safe_load((EP/'script.yaml').read_text());changes={}
for idx,title in [(5,'Skatt i en välfärdsstat'),(9,'Upprätthålla välfärdsstaten'),(16,'Självriskdelen i räkningen'),(22,'Bidragens belopp och grunder'),(23,'Utred din egen situation'),(28,'Situationer för bedömningen'),(35,'Flytten är inte stadigvarande'),(37,'Studiernas längd och ursprung'),(41,'Ackumulerade försäkringsperioder')]:
    im,draw=canvas(title)
    if idx==5:
        bag(draw,215,320);bag(draw,545,320);coins(draw,215,300,1);coins(draw,545,300,1);arrow(draw,(215,210),(215,155));label(draw,(215,465),'Välfärdsstat',29);label(draw,(545,465),'Många andra länder',26);label(draw,(215,535),'mer skatt',30)
    elif idx==9:
        draw.line((380,215,380,535),fill=GOLD,width=10);draw.polygon([(315,595),(445,595),(380,510)],fill=GOLD);draw.line((180,295,580,295),fill=SOFT,width=9)
        for x in[210,550]:draw.line([(x,295),(x-90,445),(x+90,445),(x,295)],fill=SOFT,width=5);draw.arc((x-90,410,x+90,480),0,180,fill=GOLD,width=6)
        coins(draw,210,410,3);clinic(draw,550,355);label(draw,(210,505),'betala',29);label(draw,(550,505),'välfärd',29)
    elif idx==16:
        paper(draw,380,350,365,370);label(draw,(380,205),'Räkning',32)
        for y in[295,340,385]:draw.line((250,y,505,y),fill=LINE,width=7)
        draw.rounded_rectangle((235,430,525,495),radius=12,outline=GOLD,width=5);label(draw,(380,444),'självriskdelen',29);arrow(draw,(550,465),(650,465));coins(draw,650,520,2)
    elif idx==22:
        for x,y in[(160,280),(380,365),(600,280)]:envelope(draw,x,y,155,115);paper(draw,x,y+130,75,90)
        label(draw,(380,560),'belopp och grunder varierar',30)
    elif idx==23:
        paper(draw,325,340,230,305);draw.ellipse((400,325,585,510),outline=GOLD,width=12);draw.line((560,485,650,580),fill=GOLD,width=15);person(draw,315,335,.5);label(draw,(315,545),'din egen situation',30)
    elif idx==28:
        for x in[150,380,610]:draw.rounded_rectangle((x-90,215,x+90,535),radius=20,outline=LINE,width=4)
        bag(draw,150,325);paper(draw,380,325,115,155);person(draw,590,310,.55);person(draw,645,335,.4)
        label(draw,(150,560),'återflyttare',25);label(draw,(380,560),'fast anställning',24);label(draw,(610,560),'familjeförhållande',22)
    elif idx==35:
        bag(draw,210,350);house(draw,535,295,1.1);draw.line((315,360,435,360),fill=LINE,width=5);draw.ellipse((350,220,420,290),outline=GOLD,width=4);label(draw,(385,226),'?',38)
        envelope(draw,535,540,170,90);draw.line((455,500,615,580),fill=GOLD,width=7);label(draw,(210,550),'flytt till Finland',25);label(draw,(380,610),'vanligen inte rätt till förmåner',27)
    elif idx==37:
        draw.polygon([(380,275),(210,225),(210,470),(380,520),(550,470),(550,225)],outline=SOFT,width=7);draw.line((380,275,380,520),fill=GOLD,width=7)
        for y in[300,345,390]:draw.line((235,y,350,y+25),fill=LINE,width=5);draw.line((410,y+25,525,y),fill=LINE,width=5)
        draw.ellipse((85,160,220,295),outline=GOLD,width=5);draw.line((153,180,153,228,184,246),fill=GOLD,width=5);draw.ellipse((560,165,695,300),outline=GOLD,width=5);draw.arc((585,165,670,300),90,270,fill=SOFT,width=4);draw.line((560,232,695,232),fill=SOFT,width=4)
        label(draw,(170,560),'hur länge studierna varar',23);label(draw,(580,560),'från vilket land',25)
    elif idx==41:
        draw.line((100,285,660,285),fill=SOFT,width=5)
        draw.rounded_rectangle((110,230,300,340),radius=16,outline=GOLD,width=5);draw.rounded_rectangle((410,230,600,340),radius=16,outline=GOLD,width=5)
        label(draw,(205,250),'period',28);label(draw,(505,250),'period',28);arrow(draw,(205,370),(320,485));arrow(draw,(505,370),(440,485));paper(draw,380,520,210,135);label(draw,(380,515),'ackumulerat',27);label(draw,(380,610),'i andra EU-länder',27)
    path=MEDIA/'pictures'/f'sentence-{idx+1:02}.png';im.save(path);a=assets[idx];a['files']=[info(path)];a['creation_method'].update(tool=str(Path(__file__).relative_to(ROOT)),source_sentence_ids=[d['sentences'][idx]['sentence_id']]);a['relevance_verification']='Individually composed source-specific pictorial explanation of '+d['sentences'][idx]['sentence_id']+'. '+a['relevance_verification'];changes[str(idx+1)]=title
(EP/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');(EP/'specialized-picture-compositions.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n');print('Specialized9meaningfullydistinct compositions; retained all11licensedphotographs.')
