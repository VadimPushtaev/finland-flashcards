"""Original source-bound family diagrams; no inferred numeric or legal claims."""
from pathlib import Path
import json,hashlib,math,re
import yaml
from PIL import Image,ImageDraw,ImageFont
from source_label_fit import draw_source_label
ROOT=Path(__file__).resolve().parents[3]
BG='#442d30';PANEL='#53393a';TEXT='#faf3e8';MUTED='#e5c5be';GOLD='#e6c384';LINE='#aa7874';INK='#2c2026';TEAL='#7fafab';SKIN='#dbab8c'
FONT='/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf';BOLD='/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
def info(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def text(d,s,xy,width,size=30,color=TEXT):
    f=ImageFont.truetype(BOLD,size);words=s.split();lines=[];line=''
    for w in words:
        test=(line+' '+w).strip()
        if line and d.textlength(test,font=f)>width:lines.append(line);line=w
        else:line=test
    if line:lines.append(line)
    if len(lines)>3 and size>22:return text(d,s,xy,width,size-2,color)
    for i,line in enumerate(lines):d.text((xy[0],xy[1]+i*(size+7)),line,font=f,fill=color,anchor='mt')
    return len(lines)*(size+7)
def art(d,kind,x,y,s=1):
    def box(a,b,fill=GOLD,outline=None,width=3,r=8):d.rounded_rectangle((x+a[0]*s,y+a[1]*s,x+b[0]*s,y+b[1]*s),radius=r*s,fill=fill,outline=outline,width=max(1,int(width*s)))
    def line(points,fill=GOLD,w=5):d.line([(x+a*s,y+b*s) for a,b in points],fill=fill,width=max(1,int(w*s)))
    def ellipse(a,b,fill=GOLD,outline=None,width=4):d.ellipse((x+a[0]*s,y+a[1]*s,x+b[0]*s,y+b[1]*s),fill=fill,outline=outline,width=max(1,int(width*s)))
    def person(px,py,sc=1,color=TEAL):
        # Clothing, face, arms and legs form a clear figurative silhouette.
        nonlocal x,y,s
        ox,oy,os=x,y,s;x+=px*s;y+=py*s;s*=sc
        ellipse((-20,-85),(20,-45),SKIN);box((-29,-39),(29,34),color,r=15);line([(-28,-20),(-47,26)],SKIN,12);line([(28,-20),(47,26)],SKIN,12);box((-25,27),(-4,87),MUTED,r=7);box((4,27),(25,87),MUTED,r=7);line([(-29,87),(-3,87)],INK,7);line([(4,87),(29,87)],INK,7);x,y,s=ox,oy,os
    if kind in ('person','adult','woman','man'):person(0,0,1)
    elif kind in ('couple','parents'):
        person(-46,0,.8,TEAL);person(46,0,.8,LINE);line([(-12,10),(12,10)],SKIN,7)
    elif kind=='child':person(0,20,.65,GOLD)
    elif kind=='children':
        person(-46,20,.58,GOLD);person(46,20,.58,GOLD)
    elif kind=='eye':
        ellipse((-103,-56),(103,56),None,TEAL,7)
        ellipse((-42,-42),(42,42),MUTED)
        ellipse((-21,-21),(21,21),INK)
    elif kind in ('happy_face','sad_face','fear'):
        ellipse((-83,-83),(83,83),MUTED,LINE,4);ellipse((-39,-29),(-23,-13),INK);ellipse((23,-29),(39,-13),INK)
        if kind=='happy_face':d.arc((x-44*s,y-11*s,x+44*s,y+51*s),0,180,fill=LINE,width=max(1,int(8*s)))
        elif kind=='sad_face':d.arc((x-44*s,y+27*s,x+44*s,y+70*s),180,360,fill=LINE,width=max(1,int(8*s)))
        else:ellipse((-19,20),(19,62),LINE)
    elif kind=='alert':
        d.polygon([(x,y-99*s),(x+110*s,y+85*s),(x-110*s,y+85*s)],fill=GOLD);line([(0,-36),(0,24)],BG,15);ellipse((-8,46),(8,62),BG)
    elif kind=='boundary':
        box((-105,-96),(105,96),None,TEAL,6,r=12);person(0,0,.65,GOLD)
    elif kind=='tree':
        box((-14,2),(14,98),LINE,r=2)
        for xx,yy,rr in [(-46,-25,60),(42,-27,63),(0,-73,62)]:ellipse((xx-rr,yy-rr),(xx+rr,yy+rr),TEAL)
    elif kind=='bed':
        box((-105,-19),(105,64),TEAL,r=5);box((-105,-55),(-27,7),MUTED,r=13);line([(-105,-60),(-105,103)],GOLD,10);line([(105,20),(105,103)],GOLD,10)
    elif kind=='weather':
        ellipse((9,-94),(89,-14),GOLD);ellipse((-99,-49),(9,49),MUTED);ellipse((-38,-68),(66,49),MUTED);box((-74,-7),(65,49),MUTED,r=6)
        for xx in (-53,0,53):line([(xx,67),(xx-12,96)],TEAL,7)
    elif kind=='traffic':
        box((-43,-101),(43,60),INK,GOLD,4,r=10);ellipse((-23,-82),(23,-36),LINE);ellipse((-23,-12),(23,34),TEAL);line([(0,63),(0,102)],MUTED,10)
    elif kind=='tobacco':
        box((-98,-14),(52,17),MUTED,r=3);box((51,-14),(99,17),LINE,r=2);line([(-103,-27),(-115,-53),(-102,-79)],TEAL,5)
    elif kind=='alcohol':
        box((-21,-100),(21,-42),MUTED,r=4);box((-52,-47),(52,96),TEAL,GOLD,3,r=19);box((-47,-9),(47,48),MUTED,r=3);line([(-21,-102),(21,-102)],GOLD,9)
    elif kind=='couple_support':
        person(-58,0,.75,TEAL);person(58,0,.75,LINE);ellipse((-15,-29),(15,1),GOLD);line([(0,-22),(0,-5)],BG,3);line([(-7,-14),(7,-14)],BG,3);line([(-28,24),(28,24)],GOLD,4);line([(-28,24),(-16,15)],GOLD,4);line([(-28,24),(-16,33)],GOLD,4);line([(28,24),(16,15)],GOLD,4);line([(28,24),(16,33)],GOLD,4)
    elif kind=='no_work':
        art(d,'work',x,y,s);line([(-95,96),(95,-96)],LINE,12)
    elif kind=='name_tag':
        box((-104,-68),(104,68),MUTED,LINE,4,r=12);box((-103,-67),(103,-25),TEAL,r=8);line([(-73,1),(73,1)],LINE,5);line([(-73,25),(33,25)],LINE,5)
    elif kind=='coffin':
        d.polygon([(x-55*s,y-96*s),(x+55*s,y-96*s),(x+82*s,y-38*s),(x+48*s,y+99*s),(x-48*s,y+99*s),(x-82*s,y-38*s)],fill=LINE,outline=GOLD,width=max(1,int(5*s)));line([(-39,-66),(39,-66)],MUTED,4)
    elif kind=='grave':
        box((-68,-91),(68,89),MUTED,LINE,4,r=53);box((-93,79),(93,100),TEAL,r=2);line([(-30,-35),(30,-35)],LINE,5);line([(-30,-15),(30,-15)],LINE,5)
    elif kind=='urn':
        d.polygon([(x-62*s,y-59*s),(x+62*s,y-59*s),(x+42*s,y+86*s),(x-42*s,y+86*s)],fill=TEAL,outline=GOLD,width=max(1,int(4*s)));ellipse((-65,-72),(65,-39),MUTED);box((-33,-88),(33,-69),GOLD,r=6);line([(-24,-4),(24,-4)],MUTED,5)
    elif kind in ('land','sea'):
        if kind=='land':
            ellipse((-105,-40),(105,80),TEAL);line([(-85,49),(-25,20),(31,35),(83,2)],GOLD,5)
        else:
            for yy in (-45,0,45):line([(-105,yy),(-70,yy-16),(-35,yy),(0,yy-16),(35,yy),(70,yy-16),(105,yy)],TEAL,7)
    elif kind=='microscope':
        line([(-76,92),(76,92)],GOLD,11);line([(-46,89),(-46,38),(13,-15)],TEAL,15);line([(-11,-95),(54,-34)],MUTED,21);line([(40,-41),(20,-13)],GOLD,13);line([(-65,25),(63,25)],GOLD,9);line([(13,33),(40,61),(40,88)],TEAL,12);ellipse((-70,29),(-32,67),MUTED)
    elif kind=='donation':
        art(d,'heart',x,y,s);line([(0,-21),(0,22)],BG,9);line([(-22,0),(22,0)],BG,9)
    elif kind=='elder':
        person(0,0,1);d.arc((x-24*s,y-91*s,x+24*s,y-44*s),180,350,fill=TEXT,width=max(1,int(12*s)))
    elif kind=='certificate':
        art(d,'document',x,y,s);ellipse((12,40),(50,78),GOLD,LINE,4);line([(23,70),(15,95),(32,85),(44,98),(44,68)],GOLD,7)
    elif kind=='phone':
        box((-54,-100),(54,100),TEAL,INK,4,r=16);box((-42,-76),(42,66),BG,r=3);ellipse((-9,76),(9,94),GOLD);line([(-15,-88),(15,-88)],GOLD,3)
    elif kind=='shelter':
        art(d,'house',x,y,s);art(d,'shield',x+49*s,y+34*s,.48*s)
    elif kind=='pregnant':
        person(-5,0,1);ellipse((-25,-22),(54,45),TEAL);line([(21,-8),(43,12),(21,30)],SKIN,8)
    elif kind=='maternity_box':
        box((-102,-44),(102,82),MUTED,LINE,4,r=5);d.polygon([(x-102*s,y-44*s),(x-68*s,y-79*s),(x+83*s,y-79*s),(x+102*s,y-44*s)],fill=TEAL);art(d,'clothes',x,y+9*s,.48*s);line([(-100,-43),(100,-43)],GOLD,5)
    elif kind=='twins':
        art(d,'baby',x-56*s,y,.65*s);art(d,'baby',x+56*s,y,.65*s)
    elif kind=='baby':
        ellipse((-50,-83),(50,92),MUTED);ellipse((-28,-69),(28,-13),SKIN);d.polygon([(x-48*s,y-14*s),(x+45*s,y+36*s),(x+25*s,y+84*s),(x-24*s,y+84*s)],fill=TEAL);line([(-36,13),(34,62)],GOLD,4)
    elif kind in ('family','family1','family2','family3','generations'):
        person(-67,-10,.85,TEAL);person(67,-10,.85,LINE)
        n={'family':1,'family1':1,'family2':2,'family3':3,'generations':1}[kind]
        for i in range(n):person((i-(n-1)/2)*45,53,.45,GOLD)
        if kind=='generations':person(-120,8,.72,MUTED);person(120,8,.72,MUTED)
    elif kind in ('house','homes'):
        d.polygon([(x-102*s,y-10*s),(x,y-100*s),(x+102*s,y-10*s)],fill=LINE);box((-80,-12),(80,100),MUTED,r=4);box((-19,28),(22,100),TEAL,r=2);box((-62,17),(-31,48),BG,r=1);box((38,17),(63,48),BG,r=1);line([(-46,19),(-46,46)],GOLD,2);line([(39,32),(61,32)],GOLD,2)
    elif kind in ('document','registry','will','contract','notice','receipt'):
        box((-63,-95),(63,95),MUTED,r=6)
        if kind=='registry':
            ellipse((-42,-70),(-13,-41),TEAL);box((-45,-37),(-9,-8),TEAL,r=3)
        elif kind=='will':
            line([(-35,-58),(-3,-58)],BG,5);line([(-35,-43),(31,-43)],BG,5)
        elif kind=='contract':
            line([(-38,-58),(38,-58)],TEAL,8)
        for yy in (-12,10,32):line([(-38,yy),(38,yy)],LINE,4)
        if kind in ('will','contract','receipt'):line([(-35,65),(-17,54),(-8,68),(9,54),(31,64)],TEAL,4)
        else:ellipse((10,47),(39,76),TEAL)
    elif kind=='money':
        for i in range(3):
            box((-78+i*8,-40-i*9),(62+i*8,45-i*9),TEAL,INK,2,r=5)
        ellipse((-20,-38),(30,20),GOLD);line([(4,-24),(4,8)],BG,4);line([(-6,-11),(14,-11)],BG,4)
    elif kind=='coins':
        for k in range(3):
            xx=-65+k*62
            for yy in range(3+k):ellipse((xx-25,53-yy*21),(xx+25,76-yy*21),GOLD,LINE,2)
    elif kind=='calendar':
        box((-78,-83),(78,95),MUTED,r=8);box((-78,-83),(78,-37),LINE,r=5)
        line([(-40,-100),(-40,-65)],GOLD,8);line([(40,-100),(40,-65)],GOLD,8)
        for xx in (-43,0,43):
            for yy in (-4,31,66):ellipse((xx-7,yy-7),(xx+7,yy+7),TEAL)
    elif kind in ('rings','marriage'):
        ellipse((-94,-52),(18,60),None,GOLD,13);ellipse((-18,-52),(94,60),None,MUTED,13)
    elif kind in ('no_rings','no_registry','no_will','no_shield'):
        art(d,{'no_rings':'rings','no_registry':'registry','no_will':'will','no_shield':'shield'}[kind],x,y,s)
        line([(-91,94),(91,-94)],LINE,12)
    elif kind=='rise':
        d.polygon([(x-32*s,y+88*s),(x+32*s,y+88*s),(x+32*s,y-12*s),(x+83*s,y-12*s),(x,y-99*s),(x-83*s,y-12*s),(x-32*s,y-12*s)],fill=TEAL)
    elif kind=='heart':
        pts=[]
        for i in range(121):
            a=2*math.pi*i/120;pts.append((x+5.6*16*math.sin(a)**3*s,y-5.6*(13*math.cos(a)-5*math.cos(2*a)-2*math.cos(3*a)-math.cos(4*a))*s))
        d.polygon(pts,fill=LINE)
    elif kind in ('scales','equality'):
        line([(0,-95),(0,84)],GOLD,8);line([(-70,85),(70,85)],GOLD,8);line([(-100,-55),(100,-55)],MUTED,6)
        for xx in (-78,78):
            line([(xx,-55),(xx-40,25)],MUTED,3);line([(xx,-55),(xx+40,25)],MUTED,3);d.pieslice((x+(xx-43)*s,y+3*s,x+(xx+43)*s,y+56*s),0,180,fill=TEAL)
    elif kind in ('unequal_scales','balance_options'):
        line([(0,-95),(0,84)],GOLD,8);line([(-70,85),(70,85)],GOLD,8);line([(-100,-77),(100,-35)],MUTED,6)
        for xx,yy in [(-78,-72),(78,-40)]:
            line([(xx,yy),(xx-40,yy+80)],MUTED,3);line([(xx,yy),(xx+40,yy+80)],MUTED,3);d.pieslice((x+(xx-43)*s,y+(yy+58)*s,x+(xx+43)*s,y+(yy+111)*s),0,180,fill=TEAL)
        if kind=='balance_options':d.text((x+93*s,y-103*s),'?',font=ImageFont.truetype(BOLD,max(15,int(43*s))),fill=GOLD,anchor='mm')
    elif kind=='shield':
        d.polygon([(x,y-100*s),(x+85*s,y-66*s),(x+70*s,y+36*s),(x,y+100*s),(x-70*s,y+36*s),(x-85*s,y-66*s)],fill=TEAL);line([(-40,-2),(-9,31),(44,-38)],MUTED,12)
    elif kind=='lock':
        d.arc((x-48*s,y-97*s,x+48*s,y+31*s),180,360,fill=GOLD,width=max(1,int(11*s)));line([(-48,-32),(-48,-9)],GOLD,11);line([(48,-32),(48,-9)],GOLD,11);box((-71,-15),(71,90),TEAL,r=10);ellipse((-10,18),(10,38),GOLD);line([(0,36),(0,61)],GOLD,8)
    elif kind in ('work','briefcase'):
        box((-41,-81),(41,-42),None,GOLD,9,r=8);box((-95,-48),(95,80),TEAL,r=12);line([(-95,-3),(95,-3)],MUTED,4);box((-17,-13),(17,17),GOLD,r=4)
    elif kind in ('court','institution'):
        d.polygon([(x-106*s,y-50*s),(x,y-106*s),(x+106*s,y-50*s)],fill=LINE)
        for xx in (-70,-23,23,70):box((xx-9,-43),(xx+9,76),MUTED,r=2)
        box((-104,77),(104,96),GOLD,r=2)
    elif kind=='hospital':
        box((-80,-85),(80,94),MUTED,r=6);box((-17,-66),(17,7),LINE,r=1);box((-44,-42),(44,-17),LINE,r=1);box((-20,43),(20,94),TEAL,r=3)
    elif kind=='book':
        d.polygon([(x-105*s,y-75*s),(x-13*s,y-52*s),(x,y-40*s),(x+13*s,y-52*s),(x+105*s,y-75*s),(x+105*s,y+72*s),(x+15*s,y+94*s),(x,y+83*s),(x-15*s,y+94*s),(x-105*s,y+72*s)],fill=MUTED)
        line([(0,-40),(0,80)],LINE,4)
        for yy in (-28,0,28,56):line([(-87,yy-10),(-21,yy+5)],TEAL,3);line([(21,yy+5),(87,yy-10)],TEAL,3)
    elif kind=='clock':
        ellipse((-94,-94),(94,94),MUTED);ellipse((-80,-80),(80,80),BG);line([(0,-56),(0,0),(45,29)],GOLD,8)
    elif kind=='key':
        ellipse((-82,-45),(-2,35),None,GOLD,15);line([(-7,0),(95,0)],GOLD,16);line([(59,0),(59,28)],GOLD,13);line([(85,0),(85,28)],GOLD,13)
    elif kind=='split':
        line([(-75,-80),(0,-15),(75,-80)],MUTED,7);line([(0,-15),(0,80)],GOLD,7)
    elif kind=='vote':
        box((-90,-25),(90,95),TEAL,r=8);box((-41,-113),(42,-14),MUTED,r=3);line([(-17,-75),(-1,-57),(28,-94)],LINE,8);line([(-52,-9),(52,-9)],BG,7)
    elif kind=='school':
        box((-99,-30),(99,90),MUTED,r=3);d.polygon([(x-109*s,y-30*s),(x,y-98*s),(x+109*s,y-30*s)],fill=LINE)
        for xx in (-68,-30,30,68):box((xx-9,-9),(xx+9,19),TEAL,r=1)
        box((-18,40),(18,90),TEAL,r=2)
    elif kind=='city':
        for xx,hh in [(-75,125),(-15,185),(47,145)]:
            box((xx-21,80-hh),(xx+27,88),MUTED,r=3)
            for yy in range(65-hh,60,31):box((xx-9,yy),(xx+5,yy+15),TEAL,r=1)
    elif kind in ('farm','factory'):
        if kind=='farm':
            box((-85,-23),(20,90),MUTED,r=2);d.polygon([(x-100*s,y-23*s),(x-33*s,y-92*s),(x+32*s,y-23*s)],fill=LINE);box((-51,26),(-12,90),TEAL,r=2);ellipse((32,24),(106,98),TEAL);line([(70,55),(70,-53)],GOLD,6)
        else:
            box((-97,-10),(98,90),MUTED,r=2);box((42,-101),(69,-9),LINE,r=2);d.polygon([(x-97*s,y-10*s),(x-97*s,y-56*s),(x-36*s,y-10*s),(x-36*s,y-56*s),(x+27*s,y-10*s)],fill=LINE)
            for xx in (-62,-7,53):box((xx-14,22),(xx+14,51),TEAL,r=1)
    elif kind=='food':
        ellipse((-73,-73),(73,73),MUTED);ellipse((-53,-53),(53,53),BG);ellipse((-30,-18),(8,23),TEAL);ellipse((0,-35),(32,-2),GOLD);line([(-104,-80),(-104,90)],GOLD,8);line([(105,-80),(105,90)],GOLD,8)
    elif kind=='speech':
        box((-110,-82),(110,55),MUTED,r=30);d.polygon([(x-62*s,y+35*s),(x-77*s,y+96*s),(x-10*s,y+50*s)],fill=MUTED)
        for xx in (-50,0,50):ellipse((xx-9,-25),(xx+9,-7),TEAL)
    elif kind=='missed_deadline':
        art(d,'clock',x,y,s);line([(-89,90),(89,-90)],LINE,12)
    elif kind=='finland':
        d.rectangle((x-108*s,y-66*s,x+108*s,y+66*s),fill='#ffffff');d.rectangle((x-48*s,y-66*s,x-12*s,y+66*s),fill='#002f6c');d.rectangle((x-108*s,y-18*s,x+108*s,y+18*s),fill='#002f6c')
    elif kind=='globe':
        ellipse((-90,-90),(90,90),TEAL);ellipse((-90,-90),(90,90),None,MUTED,4)
        d.ellipse((x-45*s,y-90*s,x+45*s,y+90*s),outline=MUTED,width=max(1,int(4*s)));line([(0,-90),(0,90)],MUTED,3);line([(-90,0),(90,0)],MUTED,3)
    elif kind=='singleparent':
        person(-27,-4,.95,TEAL);person(55,44,.5,GOLD)
    elif kind=='friends':
        person(-56,0,.8,TEAL);person(56,0,.8,LINE)
    elif kind in ('rainbow','rainbowfamily'):
        for j,color in enumerate(['#bf635b','#d49a5e','#e3c985','#94af85','#7fa4b5','#a38bb6']):
            radius=104-j*11;d.arc((x-radius*s,y-(radius+26)*s,x+radius*s,y+(radius-26)*s),180,360,fill=color,width=max(1,int(12*s)))
        if kind=='rainbowfamily':person(-50,16,.55,TEAL);person(50,16,.55,LINE);person(0,64,.35,GOLD)
    elif kind=='toys':
        box((-94,10),(20,60),TEAL,r=12);box((-74,-23),(-5,24),TEAL,r=8);ellipse((-76,45),(-40,81),GOLD);ellipse((-23,45),(13,81),GOLD);person(65,-13,.65,LINE)
    elif kind=='toycar':
        box((-98,-5),(98,57),TEAL,r=12);box((-67,-49),(50,12),TEAL,r=10);box((-51,-37),(-6,-7),MUTED,r=4);box((6,-37),(34,-7),MUTED,r=4);ellipse((-78,38),(-31,85),GOLD);ellipse((31,38),(78,85),GOLD)
    elif kind=='doll':
        person(0,10,.9,LINE);ellipse((-44,-77),(-19,-49),GOLD);ellipse((19,-77),(44,-49),GOLD)
    elif kind=='clothes':
        d.polygon([(x-49*s,y-81*s),(x-105*s,y-47*s),(x-78*s,y+1*s),(x-47*s,y-14*s),(x-47*s,y+94*s),(x+47*s,y+94*s),(x+47*s,y-14*s),(x+78*s,y+1*s),(x+105*s,y-47*s),(x+49*s,y-81*s),(x+20*s,y-63*s),(x-20*s,y-63*s)],fill=TEAL)
    elif kind=='cleaning':
        box((-65,10),(35,85),MUTED,r=8);d.arc((x-65*s,y-32*s,x+35*s,y+47*s),180,360,fill=GOLD,width=max(1,int(6*s)));line([(51,-99),(75,50)],GOLD,8);d.polygon([(x+39*s,y+48*s),(x+100*s,y+40*s),(x+109*s,y+88*s),(x+44*s,y+98*s)],fill=TEAL)
    elif kind=='cooking':
        box((-81,-2),(81,69),TEAL,r=16);line([(-110,8),(-80,8)],GOLD,8);line([(80,8),(110,8)],GOLD,8);line([(-92,-11),(92,-11)],MUTED,9);line([(-31,-25),(31,-25)],GOLD,7)
        for xx in (-38,3,44):line([(xx,-42),(xx-8,-62),(xx+4,-82)],MUTED,4)
    else:raise ValueError('Unknown pictorial object '+kind)
def arrow(d,a,b,relation):
    if relation=='none':return
    if relation=='or':
        cx=(a[0]+b[0])/2;cy=(a[1]+b[1])/2;d.text((cx,cy),'eller',font=ImageFont.truetype(BOLD,26),fill=GOLD,anchor='mm');return
    color=TEAL if relation in ('equal','together') else GOLD
    d.line((a,b),fill=color,width=5)
    if relation in ('flow','branch','support','inherit','notify'):
        ang=math.atan2(b[1]-a[1],b[0]-a[0]);sz=17
        d.polygon([b,(b[0]-sz*math.cos(ang-.5),b[1]-sz*math.sin(ang-.5)),(b[0]-sz*math.cos(ang+.5),b[1]-sz*math.sin(ang+.5))],fill=color)
    if relation in ('equal','together','minus'):
        cx=(a[0]+b[0])/2;cy=(a[1]+b[1])/2;d.rounded_rectangle((cx-20,cy-23,cx+20,cy+23),fill=BG,radius=5);d.text((cx,cy),'=' if relation=='equal' else ('−' if relation=='minus' else '+'),font=ImageFont.truetype(BOLD,42),fill=GOLD,anchor='mm')
    if relation=='blocked':
        cx=(a[0]+b[0])/2;cy=(a[1]+b[1])/2;d.ellipse((cx-24,cy-24,cx+24,cy+24),fill=BG,outline=LINE,width=5);d.line((cx-17,cy+17,cx+17,cy-17),fill=LINE,width=5)
def diagram(spec,path,source):
    objects=spec['objects'];relation=spec.get('relation','none');im=Image.new('RGB',(760,720),BG);d=ImageDraw.Draw(im)
    if spec.get('chart'):
        d.rounded_rectangle((15,15,745,705),radius=30,fill=PANEL,outline=LINE,width=2)
        text(d,'jordbruk',(380,46),650,38);art(d,'farm',380,170,.55);baseline=550
        d.line((110,baseline,650,baseline),fill=MUTED,width=3)
        for x,entry in zip((245,515),spec['chart']):
            assert entry['year'] in source and entry['source_value'] in source
            height=entry['percent']*4
            d.rounded_rectangle((x-62,baseline-height,x+62,baseline),radius=8,fill=GOLD if x==245 else TEAL)
            text(d,str(entry['percent'])+' %',(x,baseline-height-42),220,34);text(d,entry['year'],(x,569),220,30)
        text(d,'Finlands befolkning',(380,628),650,25,MUTED)
        d.text((380,674),'Källtextens andelar · diagram',font=ImageFont.truetype(FONT,21),fill=MUTED,anchor='mt');im.save(path);return

    d.rounded_rectangle((15,15,745,705),radius=30,fill=PANEL,outline=LINE,width=2)
    if spec.get('title'):text(d,spec['title'],(380,47),650,35)
    n=len(objects)
    if n==1:coords=[(380,330)];scale=1.4
    elif n==2:coords=[(204,320),(556,320)];scale=1.02;arrow(d,(317,320),(443,320),relation)
    elif n==3 and spec.get('layout')=='tree':
        coords=[(380,210),(210,480),(550,480)];scale=.8
        edge_start_y=spec.get('tree_edge_start_y',304)
        arrow(d,(345,edge_start_y),(250,385),relation);arrow(d,(415,edge_start_y),(510,385),relation)
    elif n==3:coords=[(133,330),(380,330),(627,330)];scale=.76;edge_relations=spec.get('relations',[relation,relation]);arrow(d,(228,330),(285,330),edge_relations[0]);arrow(d,(475,330),(532,330),edge_relations[1])
    else:raise ValueError('unsupported node count')
    for node,(x,y) in zip(objects,coords):
        kind,label=node;art(d,kind,x,y,scale)
        if spec.get('label_fit') == 'source_hyphenation':
            draw_source_label(d,label,(x,y+112*scale),220 if n>2 else 285,25 if n>2 else 28,BOLD,TEXT,580 if spec.get('footer') else 655)
        else:
            text(d,label,(x,y+112*scale),220 if n>2 else 285,25 if n>2 else 28)
    if spec.get('footer'):text(d,spec['footer'],(380,596),650,27,MUTED)
    d.text((380,669),'Schematisk illustration',font=ImageFont.truetype(FONT,22),fill=MUTED,anchor='mt')
    im.save(path)
def prepare(sid):
    ep=ROOT/'studio/episodes'/sid;script=yaml.safe_load((ep/'script.yaml').read_text());plan=json.loads((ep/'visual-plan.json').read_text());assets=[]
    if len(plan)!=len(script['sentences']):raise ValueError('Every sentence needs explicit individual plan')
    for i,(spec,row) in enumerate(zip(plan,script['sentences'])):
        path=ROOT/row['render_image'];path.parent.mkdir(parents=True,exist_ok=True)
        for _,label in spec['objects']:
            if label and label not in row['sv']:raise ValueError('Label absent exact source '+row['sentence_id']+': '+label)
        if spec.get('title') and spec['title'] not in row['sv']:raise ValueError('Title absent source '+row['sentence_id'])
        pending=path.with_name(path.stem+'.writing.png');diagram(spec,pending,row['sv']);pending.replace(path);asset_id='picture_'+str(i+1).zfill(3)
        assets.append(dict(asset_id=asset_id,kind='foreground',visual_type='diagram',files=[info(path)],creator='Homebrew video studio',reuse_terms='Original schematic artwork under repository MIT license; exact archived source text retains original publisher terms.',required_credits='Original source-based pictorial diagrams: Homebrew video studio. Source wording and publisher notices in sources.yaml and accompanying credits.',relevance_verification=spec['reason']+' Exact source record: '+row['sentence_id']+'. Schematic illustration; no inferred contemporary law or numerical values.',creation_method=dict(tool='studio/production/hb-c09a/family_art.py',specification=str((ep/'visual-plan.json').relative_to(ROOT)),source_sentence_ids=[row['sentence_id'],*spec.get('source_context_ids',[]) ])))
        if spec.get('label_fit') == 'source_hyphenation':
            assets[-1]['creation_method']['label_layout']='Explicit Swedish compound line-end hyphens and measured caption bounds; raw source labels and bilingual text are unchanged.'
        row['text_highlights']=spec.get('highlights',[label for _,label in spec['objects'] if 5<=len(label)<=44][:2])
        assert all(value in row['sv'] for value in row['text_highlights'])
        row['visual_cue']=spec['reason']+' Fixed bilingual panel; foreground stays steady. Picture labels repeat exact Swedish source substrings; no separate caption.'
    pending=ep/'foreground-assets.writing';pending.write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');pending.replace(ep/'foreground-assets.json')
    pending=ep/'script.writing';pending.write_text(yaml.safe_dump(script,allow_unicode=True,sort_keys=False,width=100));pending.replace(ep/'script.yaml')
    print(sid,len(assets),'source-bound pictorial diagrams; visible-identity audit is separate',flush=True)
if __name__=='__main__':
    import sys
    for sid in sys.argv[1:]:prepare(sid)
