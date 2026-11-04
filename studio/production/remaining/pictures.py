"""Render explicitly planned source-specific diagrams and registered photographs."""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import re
import sys

from PIL import Image,ImageDraw,ImageFont
import yaml

ROOT=Path(__file__).resolve().parents[3]
SPEC=importlib.util.spec_from_file_location('studio_original_primitives',ROOT/'studio/episodes/hb-c07-ekonomi/prepare_foregrounds.py')
P=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(P)
REGULAR='/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
BOLD=REGULAR.replace('Regular','Bold')
KNOWN={'parties','person','people','work','court','prohibited','police','document','calendar','database','coins','shop','window','traffic','car','house','shield','bank','hospital','factory','field','plant','tree','ship','laptop','phone','flask','gear','bulb','ball'}


def file_info(path):
    return dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size)


def prepare(section):
    episode=ROOT/'studio/episodes'/section
    script=yaml.safe_load((episode/'script.yaml').read_text())
    plans=json.loads((episode/'picture-plan.json').read_text())
    evidence=json.loads((episode/'media-sources.json').read_text()) if (episode/'media-sources.json').exists() else {}
    colors=script['render']['palette']
    bg,fg,accent,second,line=[colors[key] for key in ('background','text','highlight','secondary','separator')]
    P.BG,P.TEXT,P.ACCENT,P.SECOND,P.LINE=bg,fg,accent,second,line
    out=ROOT/'studio/media'/section/'pictures'
    out.mkdir(parents=True,exist_ok=True)
    assets=[]
    for key,plan in plans.items():
        im=Image.new('RGB',(760,720),bg)
        d=ImageDraw.Draw(im)

        def stroke(points,color=accent,width=6):
            d.line(points,fill=color,width=width,joint='curve')

        def icon(kind,cx,cy,s=1):
            def point(x,y):return cx+x*s,cy+y*s
            def ln(points,color=accent,width=5):stroke([point(*p) for p in points],color,max(2,round(width*s)))
            def rect(x1,y1,x2,y2,color=accent):d.rounded_rectangle((*point(x1,y1),*point(x2,y2)),radius=8*s,outline=color,width=max(2,round(4*s)))
            def circle(x,y,r,color=accent):d.ellipse((*point(x-r,y-r),*point(x+r,y+r)),outline=color,width=max(2,round(4*s)))
            if kind in KNOWN:
                P.icon(d,kind,cx,cy,s)
            elif kind=='family':
                P.icon(d,'people',cx,cy-15,s)
                P.icon(d,'person',cx,cy+48,s*.5)
            elif kind=='child':P.icon(d,'person',cx,cy,s*.7)
            elif kind=='key':
                circle(-36,-16,34);ln([(-7,4),(73,75)],width=9);ln([(35,42),(54,22)],width=8);ln([(52,60),(70,41)],width=8)
            elif kind=='water':
                d.polygon([point(0,-88),point(-53,-8),point(-66,29),point(-48,69),point(0,87),point(48,69),point(66,29),point(53,-8)],outline=accent,width=max(2,round(5*s)))
                ln([(-35,26),(-28,48),(-10,59)],second,4)
            elif kind=='globe':
                circle(0,0,78)
                d.ellipse((*point(-36,-78),*point(36,78)),outline=second,width=max(2,round(3*s)))
                for y in (-39,0,39):ln([(-math.sqrt(78**2-y**2),y),(math.sqrt(78**2-y**2),y)],second,3)
            elif kind=='thermometer':
                circle(0,52,28);rect(-12,-79,12,35);ln([(0,52),(0,-55)],width=8)
                for y in(-55,-25,5):ln([(18,y),(43,y)],second,3)
            elif kind=='warning':
                d.polygon([point(0,-85),point(-83,72),point(83,72)],outline=accent,width=max(2,round(5*s)))
                ln([(0,-31),(0,25)],width=9);circle(0,49,4)
            elif kind=='germ':
                circle(0,0,48)
                for j in range(10):
                    a=j*2*math.pi/10
                    ln([(math.cos(a)*48,math.sin(a)*48),(math.cos(a)*77,math.sin(a)*77)],width=4)
                for x,y in[(-17,-13),(18,8),(-6,23)]:circle(x,y,5,second)
            elif kind=='flower':
                ln([(0,12),(0,84)],width=5)
                for j in range(6):
                    a=j*math.pi/3;circle(math.cos(a)*36,math.sin(a)*36-18,22)
                circle(0,-18,15,second);ln([(0,54),(-44,31)],second,4)
            elif kind=='paw':
                d.ellipse((*point(-40,-4),*point(40,61)),outline=accent,width=max(2,round(5*s)))
                for x,y,r in[(-55,-26,18),(-20,-50,18),(20,-50,18),(55,-26,18)]:circle(x,y,r)
            elif kind=='bin':
                rect(-52,-51,52,75);ln([(-71,-62),(71,-62)],width=7);rect(-21,-82,21,-64)
                for x in(-25,0,25):ln([(x,-26),(x,51)],second,3)
            elif kind=='battery':
                rect(-71,-39,62,39);rect(62,-18,79,18);ln([(-47,0),(-11,0)],width=5);ln([(-29,-18),(-29,18)],width=5);ln([(19,0),(48,0)],width=5)
            elif kind=='bottle':
                rect(-18,-84,18,-62);ln([(-18,-62),(-18,-42),(-42,-13),(-42,72),(42,72),(42,-13),(18,-42),(18,-62)])
                ln([(-40,7),(40,7)],second,3)
            elif kind=='cardboard':
                ln([(-69,-34),(0,-69),(69,-34),(0,0),(-69,-34),(-69,51),(0,84),(69,51),(69,-34)])
                ln([(0,0),(0,84)],second,4);ln([(-34,-51),(35,-16)],second,5)
            elif kind=='paper':
                rect(-60,-76,60,76)
                for y in(-45,-16,13,42):ln([(-36,y),(36,y)],second,3)
                ln([(-69,67),(-78,67),(-78,-61)],second,3)
            elif kind in ('can','paint_can'):
                d.ellipse((*point(-59,-64),*point(59,-34)),outline=accent,width=max(2,round(4*s)))
                ln([(-59,-49),(-59,64),(59,64),(59,-49)])
                d.arc((*point(-59,48),*point(59,78)),0,180,fill=accent,width=max(2,round(4*s)))
                for y in(-15,16,43):ln([(-45,y),(45,y)],second,3)
                if kind=='paint_can':d.arc((*point(-79,-43),*point(79,68)),180,360,fill=accent,width=max(2,round(4*s)))
            elif kind=='spray_can':
                rect(-42,-48,42,77);rect(-22,-74,22,-48);rect(-10,-87,29,-73)
                for dx,dy in[(48,-82),(65,-69),(70,-91)]:ln([(34,-79),(dx,dy)],second,3)
            elif kind=='cup':
                ln([(-60,-68),(-43,72),(43,72),(60,-68),(-60,-68)])
                ln([(-53,-23),(53,-23)],second,3)
            elif kind=='mirror':
                d.ellipse((*point(-58,-80),*point(58,65)),outline=accent,width=max(2,round(5*s)))
                ln([(0,65),(0,89),(-37,89),(37,89)],second,4)
                ln([(-31,-38),(18,13)],second,3)
            elif kind=='food':
                d.ellipse((*point(-76,-12),*point(76,69)),outline=accent,width=max(2,round(5*s)))
                circle(-28,-32,31);circle(31,-18,24);ln([(-27,-64),(-11,-81)],second,4)
                ln([(-67,40),(67,40)],second,3)
            elif kind=='sink':
                rect(-77,-5,77,75);ln([(-71,16),(71,16)],second,3)
                ln([(-29,-4),(-29,-63),(22,-63),(22,-35)],width=8)
                ln([(3,-35),(41,-35)],second,4)
            elif kind=='bag':
                rect(-61,-37,61,77);d.arc((*point(-31,-85),*point(31,9)),180,360,fill=accent,width=max(2,round(5*s)))
            elif kind=='shirt':
                ln([(-31,-72),(-78,-40),(-51,-2),(-34,-17),(-34,78),(34,78),(34,-17),(51,-2),(78,-40),(31,-72)])
                d.arc((*point(-31,-99),*point(31,-48)),0,180,fill=accent,width=max(2,round(4*s)))
            elif kind=='chair':
                rect(-49,-82,49,4);rect(-59,11,59,33)
                for x in(-45,45):ln([(x,33),(x,88)],width=7)
            elif kind=='medicine':
                rect(-48,-53,48,77);rect(-54,-77,54,-53)
                ln([(-25,7),(25,7)],second,7);ln([(0,-18),(0,32)],second,7)
            elif kind=='collection':
                P.icon(d,'house',cx-25*s,cy,s*.82);icon('bin',cx+58*s,cy+29*s,s*.43)
            elif kind=='truck':
                rect(-86,-48,24,48);ln([(24,-19),(62,-19),(88,11),(88,48),(24,48)])
                circle(-48,53,20);circle(57,53,20);ln([(35,-8),(54,-8),(73,13),(35,13),(35,-8)],second,3)
            elif kind=='bin_warning':
                icon('bin',cx-12*s,cy+6*s,s*.87);icon('warning',cx+50*s,cy-49*s,s*.4)
            elif kind=='landfill_down':
                ln([(-86,68),(-57,23),(-20,35),(8,-18),(48,14),(77,68)],second,5)
                ln([(38,-79),(38,-15)],width=7);ln([(18,-35),(38,-15),(58,-35)],width=7)
            elif kind=='soil':
                rect(-77,-5,77,72)
                for y in(14,39,61):ln([(-60,y),(-20,y-7),(18,y+4),(58,y-4)],second,3)
                ln([(0,-5),(0,-62)],width=5);ln([(0,-38),(-28,-59)],second,4);ln([(0,-20),(29,-43)],second,4)
            elif kind=='milk_carton':
                ln([(-51,-42),(-24,-79),(30,-79),(55,-42),(55,75),(-51,75),(-51,-42),(55,-42)])
                ln([(-24,-79),(-24,-42)],second,3)
            elif kind=='flat_cardboard':
                ln([(-83,4),(23,-38),(84,1),(-20,43),(-83,4)])
                ln([(-20,43),(-20,57),(84,14),(84,1)],second,4)
            elif kind=='book_pages':
                ln([(0,-49),(-71,-64),(-71,59),(0,77),(71,59),(71,-64),(0,-49),(0,77)])
                for y in(-31,-4,23,50):ln([(-59,y-13),(-13,y)],second,3);ln([(13,y),(59,y-13)],second,3)
            elif kind=='plastic_bottle':
                icon('bottle',cx,cy,s)
                for y in(21,35,49):ln([(-39,y),(39,y)],second,3)
            elif kind=='pellets':
                for x,y in[(-48,-39),(0,-56),(47,-31),(-59,12),(-10,0),(41,23),(-20,57),(35,67)]:circle(x,y,14)
            elif kind=='jar':
                rect(-64,-51,64,72);rect(-70,-76,70,-51)
            elif kind=='foil':
                ln([(-84,-42),(53,-64),(82,50),(-53,78),(-84,-42)])
                ln([(-62,-27),(-18,-6),(16,-32),(52,13),(4,39),(-26,17),(-44,55)],second,3)
            elif kind=='wipe':
                ln([(-79,-32),(45,-65),(82,44),(-44,79),(-79,-32)])
                ln([(-44,79),(-11,8),(82,44)],second,3)
            elif kind=='pharmacy':
                P.icon(d,'shop',cx,cy+11*s,s*.85)
                ln([(-19,-86),(19,-86)],second,8);ln([(0,-105),(0,-67)],second,8)
            elif kind=='medicine_bag':
                icon('bag',cx,cy,s)
                icon('medicine',cx,cy+20*s,s*.57)
                ln([(-55,-18),(55,-18)],second,4)
            elif kind=='cow':
                d.ellipse((*point(-48,-55),*point(48,65)),outline=accent,width=max(2,round(5*s)))
                d.ellipse((*point(-38,14),*point(38,60)),outline=second,width=max(2,round(4*s)))
                for x in(-20,20):circle(x,-9,5,second);circle(x,36,4,second)
                ln([(-43,-29),(-77,-46),(-66,-12),(-45,-3)])
                ln([(43,-29),(77,-46),(66,-12),(45,-3)])
                ln([(-29,-52),(-39,-82),(-13,-62)],second,4)
                ln([(29,-52),(39,-82),(13,-62)],second,4)
            elif kind=='pet':
                P.icon(d,'house',cx,cy,s)
                icon('paw',cx,cy+24*s,s*.45)
            elif kind=='fire':
                d.polygon([point(5,-88),point(-9,-25),point(-48,-54),point(-66,14),point(-45,65),point(0,86),point(49,65),point(68,13),point(40,-38),point(32,15)],outline=accent,width=max(2,round(5*s)))
                ln([(-19,45),(0,5),(22,51)],second,4)
            elif kind=='plug':
                rect(-42,-28,42,35);ln([(-22,-70),(-22,-28)],width=8);ln([(22,-70),(22,-28)],width=8);ln([(0,35),(0,66),(52,66),(52,89)],width=7)
            elif kind=='flag_fi':
                d.rectangle((*point(-81,-53),*point(81,53)),fill='#f4f4ef')
                d.rectangle((*point(-28,-53),*point(-5,53)),fill='#194c85')
                d.rectangle((*point(-81,-11),*point(81,13)),fill='#194c85')
            elif kind=='flag_eu':
                d.rectangle((*point(-81,-53),*point(81,53)),fill='#183c8e')
                for j in range(12):
                    a=j*math.pi/6-math.pi/2;x=math.cos(a)*36;y=math.sin(a)*36
                    star=[]
                    for k in range(10):
                        b=k*math.pi/5-math.pi/2;r=6 if k%2==0 else 2.6;star.append(point(x+math.cos(b)*r,y+math.sin(b)*r))
                    d.polygon(star,fill='#f4d15b')
            elif kind=='apartment':
                rect(-65,-100,65,90);rect(-13,52,13,90)
                for x in(-39,0,39):
                    for y in(-69,-28,13):rect(x-9,y-10,x+9,y+10,second)
            elif kind=='office':
                rect(-78,-89,78,88)
                for x in(-52,-17,18,53):
                    for y in(-59,-20,19):rect(x-9,y-10,x+9,y+10,second)
                rect(-21,54,21,88)
            elif kind=='room':
                ln([(-85,-70),(85,-70),(85,78),(-85,78),(-85,-70)],width=5)
                ln([(-85,-70),(-38,-27),(38,-27),(85,-70)],second,4)
                ln([(-38,-27),(-38,35),(-85,78)],second,4);ln([(38,-27),(38,35),(85,78)],second,4);ln([(-38,35),(38,35)],second,4)
            elif kind=='floorplan':
                rect(-75,-66,75,65);ln([(-75,-4),(75,-4)],second,3);ln([(13,-66),(13,-4)],second,3)
                ln([(-73,88),(73,88)],width=4);ln([(-73,80),(-73,96)],width=3);ln([(73,80),(73,96)],width=3)
                ln([(-96,-65),(-96,65)],width=4);ln([(-104,-65),(-88,-65)],width=3);ln([(-104,65),(-88,65)],width=3)
            elif kind=='stairs':
                ln([(-85,73),(-85,32),(-43,32),(-43,-9),(0,-9),(0,-50),(43,-50),(43,-90),(85,-90)],width=7)
                ln([(-83,-8),(58,-111)],second,4)
            elif kind=='speaker':
                ln([(-74,-28),(-36,-28),(8,-69),(8,69),(-36,28),(-74,28),(-74,-28)],width=5)
                for radius in(44,72):d.arc((*point(-21,-radius),*point(21+radius*1.7,radius)),-58,58,fill=second,width=max(2,round(4*s)))
            elif kind=='wall_surface':
                rect(-82,-70,82,74)
                for x in(-28,28):ln([(x,-65),(x,69)],second,3)
                for y in(-24,24):ln([(-77,y),(77,y)],second,3)
            elif kind=='cabinet':
                rect(-76,-73,76,74);ln([(0,-70),(0,70)],second,3)
                for x in(-13,13):ln([(x,-7),(x,23)],width=4)
                for x in(-60,60):ln([(x,-73),(x,-91),(x-17,-91)],second,4)
            elif kind=='noticeboard':
                rect(-85,-76,85,78)
                for x,y in[(-48,-42),(25,-42),(-48,25),(25,25)]:
                    rect(x-23,y-23,x+23,y+23,second);ln([(x-14,y-5),(x+14,y-5)],second,3);ln([(x-14,y+8),(x+8,y+8)],second,3)
            elif kind=='balcony':
                rect(-73,-79,73,51);ln([(-95,21),(95,21),(95,80),(-95,80),(-95,21)],width=5)
                for x in(-67,-33,0,33,67):ln([(x,26),(x,75)],second,3)
            elif kind=='shelter':
                ln([(-88,-18),(0,-84),(88,-18)],width=5);rect(-73,-18,73,83)
                rect(-48,19,48,56);rect(-39,7,-6,22);ln([(-48,56),(-48,73)],width=4);ln([(48,56),(48,73)],width=4)
            elif kind=='city':
                for x,y,h in[(-66,-23,105),(0,-92,174),(65,-51,133)]:
                    rect(x-28,y,x+28,y+h)
                    for yy in range(int(y+22),int(y+h-12),31):ln([(x-15,yy),(x+15,yy)],second,4)
            elif kind=='mouse':
                d.ellipse((*point(-61,-11),*point(46,60)),outline=accent,width=max(2,round(5*s)))
                circle(35,-9,25);circle(62,10,3,second);ln([(-61,33),(-86,24),(-94,-2),(-81,-24)],second,4)
                ln([(44,47),(77,21),(44,-3)],width=4)
            elif kind=='rat':
                d.ellipse((*point(-69,-17),*point(43,49)),outline=accent,width=max(2,round(5*s)))
                circle(30,-16,16);ln([(35,-15),(80,17),(36,41)],width=4);circle(57,10,3,second)
                ln([(-67,20),(-99,22),(-112,-1),(-103,-33)],second,4)
            elif kind=='bedbug':
                d.ellipse((*point(-43,-54),*point(43,60)),outline=accent,width=max(2,round(5*s)));circle(0,-68,16)
                for y in(-29,0,29):
                    ln([(-38,y),(-70,y-20)],second,4);ln([(38,y),(70,y-20)],second,4)
                for y in(-22,0,22,44):ln([(-32,y),(32,y)],second,3)
            elif kind=='school':
                ln([(-85,-45),(0,-85),(85,-45),(-85,-45)],width=5)
                rect(-76,-43,76,77);rect(-15,20,15,77)
                for x in(-48,48):
                    for y in(-20,30):rect(x-12,y-12,x+12,y+12,second)
                ln([(0,-85),(0,-115),(40,-107),(0,-99)],width=4)
            elif kind=='plastic_box':
                rect(-72,-31,72,61);ln([(-81,-40),(81,-40)],width=6);rect(-26,-58,26,-42)
            elif kind=='tube_light':
                rect(-79,-18,79,18)
                for x in(-65,65):ln([(x,-17),(x,17)],second,3)
                for x in(-38,0,38):ln([(x,-29),(x,-48)],second,3)
            elif kind=='fruit_peel':
                ln([(-65,48),(-38,12),(-8,-41),(13,-64)],width=9)
                ln([(-65,48),(-16,63),(29,47),(56,12),(62,-24),(46,-57),(13,-64)],width=5)
                ln([(-65,48),(-6,26),(30,-13),(46,-57)],second,4)
            elif kind=='eggshell':
                d.arc((*point(-62,-81),*point(62,84)),0,180,fill=accent,width=max(2,round(5*s)))
                ln([(-62,1),(-39,17),(-19,-3),(2,15),(23,-7),(45,13),(62,1)],width=5)
            elif kind=='glasses':
                circle(-42,0,33);circle(42,0,33);ln([(-9,-6),(9,-6)],width=4);ln([(-75,-8),(-92,-34)],width=4);ln([(75,-8),(92,-34)],width=4)
            elif kind=='clock':
                circle(0,0,78);ln([(0,-53),(0,0),(37,24)],width=6)
                for j in range(12):
                    a=j*math.pi/6;ln([(math.sin(a)*64,-math.cos(a)*64),(math.sin(a)*72,-math.cos(a)*72)],second,3)
            elif kind=='radiator':
                for x in(-60,-30,0,30,60):rect(x-10,-57,x+10,65)
                ln([(-78,-39),(78,-39)],second,4);ln([(-78,46),(78,46)],second,4)
            elif kind=='washing_machine':
                rect(-70,-85,70,85);ln([(-70,-48),(70,-48)],second,3);circle(0,18,48);circle(0,18,35,second)
                for x in(-45,-20):circle(x,-66,4)
            elif kind=='sauna':
                ln([(-72,7),(72,7),(72,68),(-72,68),(-72,7)],width=6)
                for y in(25,43,61):ln([(-66,y),(66,y)],second,3)
                for x in(-42,0,42):ln([(x,-13),(x-8,-32),(x+7,-51),(x,-72)],width=4)
            elif kind=='cigarette':
                rect(-77,-5,68,26);ln([(36,-5),(36,26)],second,4);ln([(-61,-22),(-70,-40),(-59,-58),(-68,-77)],width=4)
            else:raise ValueError('Unknown planned pictorial object: '+kind)

        def label(text,x,y,width=300,size=31):
            return P.wrapped(d,text,x,y,width,size=size,color=fg,bold=True)

        photo=evidence.get('foreground_photos',{}).get(key)
        if photo:
            source=ROOT/'studio/media'/section/'sources'/('foreground-'+key+'.jpg')
            picture=Image.open(source).convert('RGB');picture.thumbnail((760,720),Image.Resampling.LANCZOS)
            im.paste(picture,((760-picture.width)//2,(720-picture.height)//2))
        else:
            nodes=plan['nodes'];composition=plan['composition'];count=len(nodes)
            if not 1<=count<=3:raise ValueError('Plan must explicitly compose between one and three objects: '+key)
            # Bars are positioned by horizontal column. The two destinations of
            # a vertical branch share that column, so a lower-only qualifier
            # must be stated in its own node caption instead.
            if composition in ('branch','split') and count==3:
                for condition in plan.get('conditions',[]):
                    if 2 in condition['node_indices'] and 1 not in condition['node_indices']:
                        raise ValueError('Lower-only branch qualifier needs an explicit node caption: '+key)
            if count==1:
                locations=[(380,315)];labels=[(380,565)];scale=1.9
            elif count==2:
                locations=[(200,290),(560,290)];labels=[(200,458),(560,458)];scale=1.28
            else:
                locations=[(150,265),(380,265),(610,265)];labels=[(150,438),(380,438),(610,438)];scale=.95
            if composition in ('flow','blocked_flow'):
                for a,b in zip(locations,locations[1:]):
                    x=a[0]+104;y=a[1];end=b[0]-103
                    stroke([(x,y),(end,y)],accent,6);d.polygon([(end,y),(end-15,y-11),(end-15,y+11)],fill=accent)
                    if composition=='blocked_flow':
                        mid=(x+end)/2
                        stroke([(mid-17,y-27),(mid+17,y+27)],'#e8b3af',8)
                        stroke([(mid-17,y+27),(mid+17,y-27)],'#e8b3af',8)
            elif composition=='merge' and count==3:
                locations=[(180,205),(180,466),(575,335)]
                labels=[(180,318),(180,579),(575,475)]
                scale=.9
                stroke([(277,205),(385,205),(385,466),(277,466)],second,5)
                stroke([(385,335),(475,335)],accent,6)
                d.polygon([(475,335),(457,322),(457,348)],fill=accent)
                if plan.get('connective'):
                    d.ellipse((343,296,427,374),fill=bg,outline=second,width=3)
                    label(plan['connective'],385,318,width=80,size=24)
            elif composition in ('branch','split') and count==3:
                locations=[(180,335),(575,205),(575,466)]
                labels=[(180,475),(575,318),(575,579)]
                scale=.9
                stroke([(278,335),(385,335),(385,205),(475,205)],second,5)
                stroke([(385,335),(385,466),(475,466)],second,5)
                for y in(205,466):d.polygon([(475,y),(457,y-12),(457,y+12)],fill=accent)
                if plan.get('connective'):
                    d.ellipse((343,296,427,374),fill=bg,outline=second,width=3)
                    label(plan['connective'],385,318,width=80,size=24)
            elif composition=='reuse':
                d.arc((316,224,444,356),20,175,fill=second,width=6)
                d.arc((316,224,444,356),200,355,fill=second,width=6)
                d.polygon([(317,284),(329,264),(339,284)],fill=accent)
                d.polygon([(443,298),(431,318),(421,298)],fill=accent)
            elif composition=='group':
                d.rounded_rectangle((42,115,718,626),radius=34,outline=line,width=5)
            elif composition=='or_and' and count==3:
                locations=[(135,265),(355,265),(630,265)]
                labels=[(135,438),(355,438),(630,438)]
                d.rounded_rectangle((22,155,465,640),radius=24,outline=line,width=4)
                d.rounded_rectangle((530,155,740,640),radius=24,outline=line,width=4)
                label('eller',245,315,width=70,size=24)
                label('och',498,315,width=65,size=24)
            elif composition=='contrast':
                for cx in (200,560):d.rounded_rectangle((cx-158,140,cx+158,622),radius=22,outline=line,width=4)
            elif composition=='protect':
                d.polygon([(380,97),(696,196),(659,521),(380,650),(101,521),(64,196)],outline=accent,width=7)
                locations=[(240,320),(520,320)] if count==2 else locations
                labels=[(240,481),(520,481)] if count==2 else labels
                scale=1.1
            elif composition=='timeline':
                stroke([(110,575),(650,575)],line,12)
                for x in (145,615):d.ellipse((x-12,563,x+12,587),fill=accent)
            elif composition=='warning':
                if not plan.get('conditions'):
                    d.polygon([(380,73),(456,206),(304,206)],outline='#e8b3af',width=6)
                    d.text((380,162),'!',font=ImageFont.truetype(BOLD,58),fill=accent,anchor='mm')
                locations=[(200,375),(560,375)] if count==2 else locations
                labels=[(200,545),(560,545)] if count==2 else labels
            for node,(x,y),(lx,ly) in zip(nodes,locations,labels):
                icon(node['icon'],x,y,scale)
                if node.get('crossed'):
                    stroke([(x-94*scale,y+92*scale),(x+94*scale,y-92*scale)],'#e8b3af',8)
                label(node['label'],lx,ly,width=(250 if composition=='protect' else 300) if count<=2 else (200 if composition=='or_and' else 220),size=plan.get('label_size',31 if count<=2 else 27))
            for condition in plan.get('conditions',[]):
                selected=[locations[index][0] for index in condition['node_indices']]
                left=max(28,min(selected)-120);right=min(732,max(selected)+120)
                d.rounded_rectangle((left,36,right,127),radius=14,outline=second,width=4)
                label(condition['label'],(left+right)/2,53,width=right-left-24,size=25)
        path=out/(key+'.png');im.save(path)
        asset=dict(asset_id=key,kind='foreground',visual_type='diagram',files=[file_info(path)],
            creator='Homebrew video studio',reuse_terms='Original schematic artwork under repository MIT license; source wording retains publisher terms.',
            required_credits='Original source-based pictorial composition: Homebrew video studio. Source text credits in sources.yaml.',
            relevance_verification=plan['description']+' Exact source records: '+', '.join(plan['source_sentence_ids'])+'. Only source-stated objects and relationships; no inferred amounts or additional rules.',
            creation_method=dict(tool='studio/production/remaining/pictures.py',specification=str((episode/'picture-plan.json').relative_to(ROOT)),source_sentence_ids=plan['source_sentence_ids']))
        if photo:
            pi=photo['imageinfo'][0];meta=pi['extmetadata']
            clean=lambda key:re.sub('<[^>]+>','',meta.get(key,{}).get('value','')).strip()
            creator=photo.get('credit_creator',clean('Artist'))
            asset.update(visual_type='photograph',source_url=pi['descriptionurl'],creator=creator,
                reuse_terms=clean('LicenseShortName')+' '+clean('LicenseUrl'),
                required_credits=photo['title']+' — '+creator+' · '+clean('LicenseShortName')+'. '+pi['descriptionurl']+' '+clean('LicenseUrl')+'. Proportionally resized; source license retained.',
                relevance_verification=plan['description']+' Verified source identity: '+clean('ImageDescription')+'. Contextual photograph; not proof of a current rule or of a photographed individual status.')
        assets.append(asset)
    (episode/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n')
    print(section,len(assets),'individual source-specific pictures prepared')


if __name__=='__main__':
    prepare(sys.argv[1])
