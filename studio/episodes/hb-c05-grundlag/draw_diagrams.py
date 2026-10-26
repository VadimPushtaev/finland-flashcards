"""Draw original source-based explanatory illustrations, not photographs or data charts."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math
ROOT=Path(__file__).resolve().parents[3]
BG='#39252b';FG='#faf3e8';ACC='#dfbd82';SEC='#e2c8cf'
FONT='/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
def make(kind,label,path):
 im=Image.new('RGB',(760,720),BG);d=ImageDraw.Draw(im)
 def person(x,y,s=1,color=FG):
  d.ellipse((x-20*s,y-75*s,x+20*s,y-35*s),fill=color)
  d.rounded_rectangle((x-30*s,y-25*s,x+30*s,y+45*s),radius=int(20*s),fill=color)
  d.line((x-15*s,y+30*s,x-22*s,y+95*s),fill=color,width=int(13*s));d.line((x+15*s,y+30*s,x+22*s,y+95*s),fill=color,width=int(13*s))
 def equal(x,y):
  d.line((x-35,y-12,x+35,y-12),fill=ACC,width=9);d.line((x-35,y+12,x+35,y+12),fill=ACC,width=9)
 if kind=='universal':
  d.ellipse((230,180,530,480),outline=ACC,width=6);d.ellipse((300,180,460,480),outline=ACC,width=3);d.line((230,330,530,330),fill=ACC,width=3)
  for x,y in [(130,330),(630,330),(380,145),(380,555)]:person(x,y,.65)
 elif kind=='inalienable':
  d.polygon([(210,155),(550,155),(550,365),(500,465),(380,550),(260,465),(210,365)],outline=ACC,width=8);person(380,325,1.4)
 elif kind=='indivisible':
  for x,y in [(230,230),(530,230),(230,460),(530,460)]:
   d.line((380,345,x,y),fill=ACC,width=9);d.ellipse((x-78,y-78,x+78,y+78),fill=BG,outline=SEC,width=6)
  d.rectangle((180,195,280,270),outline=FG,width=5);d.line((230,195,230,270),fill=FG,width=3)
  person(530,235,.55)
  d.polygon([(180,460),(230,415),(280,460)],outline=FG,width=5);d.rectangle((193,460,267,505),outline=FG,width=5)
  d.line((490,440,570,440),fill=FG,width=6);d.line((530,420,530,500),fill=FG,width=6);d.arc((487,433,520,475),0,180,fill=FG,width=5);d.arc((540,433,573,475),0,180,fill=FG,width=5)
  d.ellipse((350,315,410,375),fill=ACC)
 elif kind=='foundation':
  for x in [220,380,540]:person(x,290,1)
  for y in [420,465,510]:d.rounded_rectangle((140,y,620,y+30),radius=5,fill=ACC)
 elif kind=='equality':
  person(215,295,1.2);person(545,295,1.2);equal(380,295)
  d.line((140,465,620,465),fill=ACC,width=8);d.polygon([(380,490),(340,560),(420,560)],fill=ACC)
 elif kind=='merit':
  for x in [150,470]:
   d.rounded_rectangle((x,170,x+145,405),radius=12,outline=FG,width=6)
   for y in [220,260,300]:d.line((x+25,y,x+120,y),fill=SEC,width=5)
   d.ellipse((x+48,330,x+95,377),outline=ACC,width=5)
  equal(380,290)
 elif kind=='pay':
  person(215,230,.85);person(545,230,.85);equal(380,420)
  for x in [215,545]:
   for y in [420,445,470]:d.ellipse((x-65,y-20,x+65,y+20),fill=BG,outline=ACC,width=5)
 elif kind=='privacy':
  d.polygon([(170,290),(380,115),(590,290)],outline=FG,width=8);d.rectangle((210,290,550,540),outline=FG,width=8)
  d.rounded_rectangle((315,365,445,475),radius=12,fill=ACC);d.arc((335,315,425,405),180,360,fill=ACC,width=12)
 elif kind=='choice':
  person(380,240,1.15)
  d.line((380,350,210,490),fill=ACC,width=8);d.line((380,350,550,490),fill=ACC,width=8)
  d.polygon([(210,490),(217,450),(250,483)],fill=ACC);d.polygon([(550,490),(510,483),(543,450)],fill=ACC)
  d.ellipse((170,515,250,595),outline=FG,width=7);d.ellipse((215,515,295,595),outline=FG,width=7)
  person(550,565,.55)
 elif kind=='care':
  person(245,265,1.1);person(515,265,1.1);person(380,390,.6)
  d.arc((190,230,570,570),0,180,fill=ACC,width=11)
 font=ImageFont.truetype(FONT,42)
 while d.textlength(label,font=font)>660:font=ImageFont.truetype(FONT,font.size-1)
 d.text((380,45),label,anchor='mt',font=font,fill=FG)
 path.parent.mkdir(parents=True,exist_ok=True);im.save(path)
if __name__=='__main__':
 for kind,label in [('universal','universella'),('inalienable','oförytterliga'),('indivisible','odelbara'),('foundation','fundamentala')]:make(kind,label,ROOT/'studio/media/hb-c05-grundlag/pictures'/f'{kind}.png')
