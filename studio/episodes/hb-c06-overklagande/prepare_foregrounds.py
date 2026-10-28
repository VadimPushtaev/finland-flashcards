"""Prepare source-backed pictorial schematics and institution photographs.

Run with studio/runtime/.venv/bin/python. Photos retain their registered terms;
original diagrams depict only relationships in the selected Swedish source.
"""
from pathlib import Path
import json,hashlib,re
from PIL import Image,ImageDraw,ImageFont,ImageOps
import yaml
ROOT=Path(__file__).resolve().parents[3];EP=Path(__file__).resolve().parent;SID=EP.name;MEDIA=ROOT/'studio/media'/SID
BG='#252747';TEXT='#faf3e8';SECOND='#cbd1ec';GOLD='#e3c58b';BLUE='#8db3da';MUTED='#515a82';RED='#d68c9a'
FONT='/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf';BOLD='/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
def info(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def f(n=36,b=False):return ImageFont.truetype(BOLD if b else FONT,n)
def line(d,xy,fill=GOLD,width=8):d.line(xy,fill=fill,width=width)
def label(d,xy,t,size=32,fill=TEXT):d.text(xy,t,font=f(size),anchor='mm',fill=fill)
def person(d,x,y,scale=1,color=SECOND):
 r=24*scale;d.ellipse((x-r,y-r,x+r,y+r),fill=color);d.rounded_rectangle((x-35*scale,y+36*scale,x+35*scale,y+140*scale),radius=20*scale,fill=color)
 line(d,(x-23*scale,y+130*scale,x-27*scale,y+200*scale),color,int(18*scale));line(d,(x+23*scale,y+130*scale,x+27*scale,y+200*scale),color,int(18*scale))
def document(d,x,y,w=150,h=190,color=TEXT,check=False):
 d.rounded_rectangle((x,y,x+w,y+h),radius=14,fill=BG,outline=color,width=6)
 for j in range(4):line(d,(x+25,y+42+j*30,x+w-25,y+42+j*30),color,5)
 if check:line(d,(x+w-65,y+h-48,x+w-45,y+h-25,x+w-15,y+h-72),GOLD,9)
def building(d,x,y,w=220,h=190,color=BLUE):
 d.polygon([(x,y+45),(x+w/2,y),(x+w,y+45)],fill=color)
 line(d,(x,y+h,x+w,y+h),color,9)
 for j in range(4):d.rectangle((x+25+j*(w-50)/3-8,y+65,x+25+j*(w-50)/3+8,y+h-15),fill=color)
def arrow(d,a,b,color=GOLD):
 import math
 line(d,(*a,*b),color,8);dx=b[0]-a[0];dy=b[1]-a[1];ang=math.atan2(dy,dx)
 d.polygon([b,(b[0]-25*math.cos(ang-.5),b[1]-25*math.sin(ang-.5)),(b[0]-25*math.cos(ang+.5),b[1]-25*math.sin(ang+.5))],fill=color)
def coin(d,x,y,r=38):d.ellipse((x-r,y-r,x+r,y+r),fill=GOLD);label(d,(x,y),'€',int(r*1.3),BG)
def balance(d,x,y):
 line(d,(x,y,x,y+210),GOLD,10);line(d,(x-135,y+220,x+135,y+220),GOLD,12);line(d,(x-170,y+35,x+170,y+35),GOLD,8)
 for side in [-1,1]:
  xx=x+side*150;line(d,(xx,y+35,xx-62,y+115),SECOND,4);line(d,(xx,y+35,xx+62,y+115),SECOND,4);d.arc((xx-68,y+65,xx+68,y+170),0,180,fill=SECOND,width=6)
def clock(d,x,y):
 d.ellipse((x-90,y-90,x+90,y+90),outline=GOLD,width=8);line(d,(x,y,x,y-58),TEXT,6);line(d,(x,y,x+48,y+25),TEXT,6)
def save_panel(im,path):
    fit=ImageOps.contain(im,(760,720),Image.Resampling.LANCZOS)
    canvas=Image.new('RGB',(760,720),BG);canvas.paste(fit,((760-fit.width)//2,(720-fit.height)//2));canvas.save(path)
def diagram(key,path):
 im=Image.new('RGB',(1000,900),BG);d=ImageDraw.Draw(im);d.rounded_rectangle((14,14,986,886),radius=30,outline=MUTED,width=3)
 label(d,(500,66),'Illustration',28,SECOND)
 if key=='corruption':
  person(d,200,230);building(d,675,285,210,190);coin(d,480,340,52);arrow(d,(285,340),(400,340));arrow(d,(560,340),(655,340));d.ellipse((330,185,650,505),outline=RED,width=14);line(d,(380,465,600,225),RED,14)
  label(d,(500,600),'mutor',44);label(d,(500,670),'korruption',38)
 elif key in ['equality','principles']:
  balance(d,500,230);person(d,230,470,.8);person(d,770,470,.8)
  label(d,(500,720),'jämlikt' if key=='equality' else 'rättvis · objektiv',40)
  if key=='principles':label(d,(500,780),'rätt proportion',32)
 elif key=='competence':
  document(d,105,250,180,240,check=True);arrow(d,(320,370),(430,370));building(d,490,300,220,190);label(d,(190,590),'lag',40);label(d,(610,590),'behörighet',38)
 elif key=='rules':
  document(d,425,220,150,210,check=True)
  for x in [220,500,780]:person(d,x,520,.75)
  for x in [220,500,780]:arrow(d,(500,445),(x,490))
  label(d,(500,780),'alla ska behandlas lika',38)
 elif key=='advice':
  person(d,215,305);person(d,785,305);d.rounded_rectangle((340,220,650,430),radius=28,outline=GOLD,width=6);d.polygon([(380,430),(375,480),(440,430)],fill=GOLD)
  document(d,435,250,110,145);arrow(d,(345,545),(665,545));label(d,(500,670),'rådgivning',40)
 elif key=='discretion':
  d.rounded_rectangle((165,180,835,610),radius=30,outline=GOLD,width=8);document(d,425,230,150,180,check=True)
  for x in [300,500,700]:arrow(d,(500,440),(x,550))
  label(d,(500,690),'helhetsbedömning',40);label(d,(500,750),'inom lagen',32)
 elif key=='written':
  person(d,180,300);document(d,425,230,185,250,check=True);arrow(d,(645,350),(790,350));d.rounded_rectangle((800,270,910,450),radius=16,outline=BLUE,width=7);d.line((825,310,885,310),fill=BLUE,width=4)
  label(d,(500,650),'skriftligt beslut',42);label(d,(500,730),'motivering',36)
 elif key=='waiting':
  clock(d,260,350);document(d,600,235,170,230);arrow(d,(410,350),(555,350));label(d,(500,650),'uppskattning',42);label(d,(500,730),'handläggningstid',36)
 elif key=='correction':
  document(d,150,240,180,240);document(d,670,240,180,240,check=True);arrow(d,(380,360),(620,360));label(d,(240,575),'beslut',36);label(d,(760,575),'nytt beslut',36);label(d,(500,730),'rättelse',42)
 elif key=='complaint':
  document(d,125,240,180,240);building(d,650,285,220,190);arrow(d,(350,355),(610,355));label(d,(500,630),'klagomål',44);label(d,(500,715),'myndighetens verksamhet',34)
 elif key=='appeal':
  building(d,90,350,230,190);building(d,670,280,230,190);arrow(d,(365,415),(610,390));label(d,(205,650),'tingsrätten',38);label(d,(785,580),'hovrätten',38)
 elif key=='costs':
  building(d,110,270,210,190);person(d,520,290,.8);person(d,835,290,.8)
  for x in [210,520,835]:coin(d,x,620,45)
  label(d,(210,740),'avgift',36);label(d,(520,740),'biträde',36);label(d,(835,740),'vittne',36)
 elif key=='civilcosts':
  person(d,205,250);person(d,795,250);balance(d,500,235);coin(d,335,610,44);coin(d,665,610,44);arrow(d,(390,610),(610,610));label(d,(500,750),'rättegångskostnader',40)
 elif key=='owncosts':
  person(d,205,250);person(d,795,250);balance(d,500,235);coin(d,205,620,44);coin(d,795,620,44);label(d,(500,750),'respektive kostnader',40)
 elif key=='criminalcosts':
  document(d,425,200,150,200,check=True);person(d,235,480,.8);person(d,765,480,.8);arrow(d,(470,430),(300,500));arrow(d,(530,430),(700,500));coin(d,500,650,50);label(d,(235,770),'skyldig',36);label(d,(765,770),'oskyldig',36)
 else:raise ValueError(key)
 save_panel(im,path)
def main():
 d=yaml.safe_load((EP/'script.yaml').read_text());pictures=MEDIA/'pictures';pictures.mkdir(exist_ok=True,parents=True)
 assets=[];downloads=[];creditlines=[]
 photos={r['key']:r for r in json.loads((EP/'foreground-plan.json').read_text())}
 for key in sorted({Path(r['render_image']).stem for r in d['sentences']}):
  p=pictures/(key+'.png')
  if key.startswith('photo_'):
   r=photos[key];pi=r['imageinfo'];raw=MEDIA/'sources'/(key+'.jpg');im=Image.open(raw).convert('RGB');save_panel(im,p)
   clean=lambda name:re.sub('<[^>]+>','',str(pi['extmetadata'].get(name,{}).get('value',''))).strip()
   creator=clean('Artist') or clean('Credit');lic=clean('LicenseShortName');licurl=clean('LicenseUrl');source=pi['descriptionurl'];title=r['title'].removeprefix('File:')
   assets.append(dict(asset_id='picture_'+key,kind='foreground',visual_type='photograph',files=[info(p)],source_url=source,creator=creator,reuse_terms=lic+' '+licurl,required_credits=f'{title} — {creator}. {lic}. {source} {licurl}. Proportionally resized; original image and license retained.',relevance_verification=r['context']+' '+clean('ImageDescription'),creation_method=dict(tool=__file__,transform='Proportional resize, complete original photograph retained.')))
   downloads.append(dict(**info(raw),url=pi.get('thumburl',pi['url'])));creditlines.append(title+' — '+creator+' · '+lic)
  else:
   diagram(key,p)
   ids=[r['sentence_id'] for r in d['sentences'] if Path(r['render_image']).stem==key]
   assets.append(dict(asset_id='picture_'+key,kind='foreground',visual_type='diagram',files=[info(p)],creator='Homebrew video studio',reuse_terms='Original pictorial schematic; underlying source text retains its recorded terms.',required_credits='Source-backed schematic illustration by Homebrew video studio; source credits in sources.yaml.',relevance_verification='Anonymous figures, documents, civic buildings, clocks, balances and arrows illustrate only the selected source relationships. No real event, person, amount or time limit inferred. Source sentence IDs: '+', '.join(ids),creation_method=dict(tool=str(Path(__file__).relative_to(ROOT)),labels='Only selected Swedish source terms; Illustration marks schematic nature.')))
 (EP/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2))
 (EP/'foreground-downloads.json').write_text(json.dumps(downloads,ensure_ascii=False,indent=2))
 d['render']['credits']=d['render']['credits'][:2]
 for i in range(0,len(creditlines),2):d['render']['credits'].append(dict(heading='Förgrundsbilder · Изображения',paragraphs=creditlines[i:i+2]+['Fullständiga källor och licenser i CREDITS.md.']))
 (EP/'script.yaml').write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False,width=100))
 print(SID,len(assets),'foreground pictures prepared')
if __name__=='__main__':main()
