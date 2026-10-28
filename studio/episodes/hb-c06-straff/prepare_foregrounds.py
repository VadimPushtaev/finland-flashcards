"""Prepare this episode's verified photographs and source-based pictorial diagrams."""
from pathlib import Path
import json,hashlib,re,math
import yaml
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];EP=Path(__file__).resolve().parent;SID=EP.name;MEDIA=ROOT/'studio/media'/SID
BG='#252747';PANEL='#303453';TEXT='#faf3e8';SECOND='#cbd1ec';ACCENT='#e3c58b';LINE='#66749f'
FONT='/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf';BOLD='/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
def info(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def wrapped(draw,text,x,y,width,size=29,color=TEXT,bold=False):
 words=text.split()
 while size>20 and any(draw.textlength(word,font=ImageFont.truetype(BOLD if bold else FONT,size))>width for word in words):size-=1
 font=ImageFont.truetype(BOLD if bold else FONT,size);lines=[];line=''
 for word in words:
  candidate=(line+' '+word).strip()
  if draw.textlength(candidate,font=font)>width and line:lines.append(line);line=word
  else:line=candidate
 if line:lines.append(line)
 for j,line in enumerate(lines):draw.text((x,y+j*(size+7)),line,font=font,fill=color,anchor='mt')
 return len(lines)*(size+7)
def icon(d,kind,cx,cy,scale=1.0):
 def pt(x,y):return(cx+x*scale,cy+y*scale)
 def line(points,fill=ACCENT,w=5):d.line([pt(*p) for p in points],fill=fill,width=max(2,int(w*scale)))
 def box(a,b,fill=None):d.rounded_rectangle((*pt(*a),*pt(*b)),radius=8*scale,outline=ACCENT,width=max(2,int(4*scale)),fill=fill)
 def circle(x,y,r,fill=None):d.ellipse((*pt(x-r,y-r),*pt(x+r,y+r)),outline=ACCENT,width=max(2,int(4*scale)),fill=fill)
 if kind=='parties':
  for x in (-38,38):
   circle(x,-35,17);line([(x,-18),(x,43)]);line([(x-24,11),(x,-2),(x+24,11)]);line([(x-22,76),(x,43),(x+22,76)])
 elif kind in ('person','people','work'):
  circle(0,-35,19);line([(0,-16),(0,48)]);line([(-34,13),(0,0),(34,13)]);line([(-28,80),(0,48),(28,80)])
  if kind=='people':
   for sign in (-1,1):circle(62*sign,-15,14);line([(62*sign,0),(62*sign,55)],SECOND,3)
  if kind=='work':line([(35,-30),(60,70)]);line([(38,67),(85,67)]);line([(45,67),(42,82)]);line([(60,67),(59,82)]);line([(76,67),(76,82)])
 elif kind=='court':
  line([(-75,-28),(0,-75),(75,-28),(-75,-28)]);line([(-78,69),(78,69)])
  for x in(-52,-18,18,52):line([(x,-20),(x,56)],w=8)
  line([(-70,58),(70,58)])
 elif kind=='prohibited':
  circle(0,0,70);circle(0,-28,16);line([(0,-12),(0,32)]);line([(-25,15),(0,-2),(25,15)]);line([(-21,58),(0,32),(21,58)]);line([(-50,50),(50,-50)],w=7)
 elif kind=='police':
  line([(-48,-64),(48,-64),(55,-6),(37,44),(0,79),(-37,44),(-55,-6),(-48,-64)])
  for angle in range(5):
   a=angle*2*math.pi/5-math.pi/2;b=a+4*math.pi/5
   line([(math.cos(a)*30,math.sin(a)*30),(math.cos(b)*30,math.sin(b)*30)],w=3)
 elif kind in('document','calendar','database'):
  box((-55,-74),(55,74))
  for y in(-25,0,25,50):line([(-34,y),(34,y)],SECOND,3)
  if kind=='calendar':line([(-55,-38),(55,-38)]);line([(-30,-87),(-30,-60)]);line([(30,-87),(30,-60)])
  if kind=='database':
   d.ellipse((*pt(-55,-75),*pt(55,-45)),outline=ACCENT,width=4)
   d.arc((*pt(-55,40),*pt(55,74)),0,180,fill=ACCENT,width=4)
 elif kind=='coins':
  for i,(x,height) in enumerate([(-38,2),(0,3),(38,4)]):
   for y in range(height):d.ellipse((*pt(x-22,55-y*22),*pt(x+22,75-y*22)),outline=ACCENT,width=4)
 elif kind=='shop':
  box((-72,-15),(72,75));line([(-82,-17),(-62,-65),(62,-65),(82,-17),(-82,-17)])
  for x in range(-60,61,30):line([(x,-60),(x,-20)],SECOND,3)
  box((-15,17),(28,75));box((-56,12),(-29,43))
 elif kind=='window':
  box((-64,-75),(64,75));line([(0,-75),(0,75)],SECOND,3);line([(-64,0),(64,0)],SECOND,3)
  line([(-52,-55),(-20,-20),(-32,6),(7,26),(26,65)])
  line([(-20,-20),(27,-40),(47,-19)])
 elif kind=='traffic':
  circle(0,-12,63);line([(-29,19),(0,-48),(29,19),(-29,19)]);line([(0,25),(0,78)],SECOND,3)
 elif kind=='car':
  box((-77,-12),(77,45));line([(-61,-12),(-35,-56),(35,-56),(61,-12)])
  circle(-49,47,17);circle(49,47,17)
 elif kind in('house','shield'):
  if kind=='house':line([(-78,-10),(0,-76),(78,-10)]);box((-59,-10),(59,76));box((-14,30),(16,76))
  else:
   line([(-57,-62),(0,-80),(57,-62),(48,22),(0,76),(-48,22),(-57,-62)])
   line([(-24,0),(-5,24),(31,-27)],SECOND,6)
 else:raise ValueError(kind)
def arrow(d,a,b):
 d.line((a,b),fill=LINE,width=5);ang=math.atan2(b[1]-a[1],b[0]-a[0]);s=15
 d.polygon([b,(b[0]-s*math.cos(ang-.5),b[1]-s*math.sin(ang-.5)),(b[0]-s*math.cos(ang+.5),b[1]-s*math.sin(ang+.5))],fill=LINE)
def diagram(spec,path):
 layout,title,nodes,footer=spec;im=Image.new('RGB',(760,720),BG);d=ImageDraw.Draw(im)
 d.rounded_rectangle((14,14,746,706),radius=26,fill=PANEL,outline=LINE,width=2)
 wrapped(d,title,380,48,680,38,bold=True);d.line((80,115,680,115),fill=ACCENT,width=4)
 if layout=='decision':
  coords=[(380,190),(205,425),(555,425)];arrow(d,(325,350),(225,358));arrow(d,(435,350),(535,358))
 elif len(nodes)==2:coords=[(220,310),(540,310)]
 else:coords=[(130,310),(380,310),(630,310)]
 if layout=='flow':
  for a,b in zip(coords,coords[1:]):arrow(d,(a[0]+85,a[1]),(b[0]-85,b[1]))
 for idx,((kind,label),(x,y)) in enumerate(zip(nodes,coords)):
  icon(d,kind,x,y,.75 if layout=='decision' else (.83 if len(nodes)>2 else 1))
  wrapped(d,label,x,y+90,270 if layout=='decision' else (215 if len(nodes)>2 else 265),26 if layout=='decision' else 29,color=TEXT,bold=True)
 if layout=='income':
  # Different schematic column heights express the source comparison, not amounts.
  d.rectangle((172,500,268,535),fill=SECOND);d.rectangle((492,455,588,535),fill=ACCENT)
 if footer:wrapped(d,footer,380,610 if layout=='decision' else 578,665,27,color=SECOND)
 d.text((380,669),'Schematisk illustration',font=ImageFont.truetype(FONT,22),fill=SECOND,anchor='mt');im.save(path)
def main():
 specs=json.loads((EP/'pictorial-plan.json').read_text());photos=json.loads((EP/'foreground-photo-sources.json').read_text())
 groups=json.loads((EP/'production-plan.json').read_text());d=yaml.safe_load((EP/'script.yaml').read_text());assets=[];downloads=[];screencredits=[]
 for key,spec in specs.items():
  dest=MEDIA/'pictures'/f'{key}.png';dest.parent.mkdir(parents=True,exist_ok=True)
  rows=[r for i,r in enumerate(d['sentences']) if groups[max(j for j,g in enumerate(groups) if g[0]<=i)][2]==key]
  if spec[0]=='photo':
   rec=photos[spec[1]];pi=rec['imageinfo'];raw=ROOT/rec['raw_path'];im=Image.open(raw).convert('RGB');im.thumbnail((1100,1000),Image.Resampling.LANCZOS);im.save(dest)
   meta=pi['extmetadata'];clean=lambda k:re.sub('<[^>]+>','',str(meta.get(k,{}).get('value',''))).strip()
   creator=clean('Artist');license=clean('LicenseShortName');licenseurl=clean('LicenseUrl')
   assets.append(dict(asset_id='visual_'+key,kind='foreground',visual_type='photograph',files=[info(dest)],source_url=pi['descriptionurl'],creator=creator,reuse_terms=license+' '+licenseurl,required_credits=rec['title'].removeprefix('File:')+' — '+creator+'. '+license+'. '+pi['descriptionurl']+' '+licenseurl+'. Proportionally resized, original image preserved; original license retained.',relevance_verification=rec['context']+' Source metadata: '+clean('ImageDescription'),creation_method=dict(tool=str(Path(__file__).relative_to(ROOT)),transform='Proportional downscale; complete source photograph preserved.')))
   downloads.append(dict(**info(raw),url=pi.get('thumburl',pi['url'])))
   screencredits.append(rec['title'].removeprefix('File:')+' — '+creator+' · '+license)
  else:
   diagram(spec,dest)
   assets.append(dict(asset_id='visual_'+key,kind='foreground',visual_type='diagram',files=[info(dest)],creator='Homebrew video studio',reuse_terms='Original schematic artwork under repository MIT license; source wording retains original publisher terms.',required_credits='Original schematic diagram: Homebrew video studio. Source wording credited in sources.yaml and accompanying CREDITS.md.',relevance_verification='Original pictorial diagram reviewed against exact source records '+', '.join(r['sentence_id'] for r in rows)+'. Objects and relationships visualize only selected source statements; schematic comparisons contain no currency amounts or extra legal rules.',creation_method=dict(tool=str(Path(__file__).relative_to(ROOT)),diagram_specification=str((EP/'pictorial-plan.json').relative_to(ROOT)),source_sentence_ids=[r['sentence_id'] for r in rows])))
  print(SID,key,flush=True)
 (EP/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');(EP/'foreground-downloads.json').write_text(json.dumps(downloads,ensure_ascii=False,indent=2)+'\n')
 d['render']['credits']=d['render']['credits'][:2]
 for i in range(0,len(screencredits),2):d['render']['credits'].append(dict(heading='Förgrundsbilder · Изображения',paragraphs=screencredits[i:i+2]+['Original schematisk grafik: Homebrew video studio.','Fullständiga licenser i medföljande CREDITS.md.']))
 (EP/'script.yaml').write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False,width=100))
if __name__=='__main__':main()
