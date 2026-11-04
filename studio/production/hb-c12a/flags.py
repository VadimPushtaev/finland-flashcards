"""Compose accurate Nordic country flags from verified public-domain originals."""
from pathlib import Path
import hashlib,json,re,subprocess
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];SID='hb-c12-norden-eu';EP=ROOT/'studio/episodes'/SID;MEDIA=ROOT/'studio/media'/SID;F='/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf';PAGES=json.loads((ROOT/'studio/production/hb-c12a/nordic-flag-sources.json').read_text())['query']['pages'];META={p['title']:p['imageinfo'][0] for p in PAGES.values()};COUNTRIES=[('Finland','Finland'),('Sweden','Sverige'),('Norway','Norge'),('Denmark','Danmark'),('Iceland','Island')]
def info(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def main():
 raw=MEDIA/'sources/flags';raw.mkdir(parents=True,exist_ok=True);downloads=[]
 for en,sv in COUNTRIES:
  m=META['File:Flag of '+en+'.svg'];p=raw/(en+'.png');url=m['thumburl'];subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'studio/production/remaining/download.py'),'--url',url,'--output',str(p)],check=True);downloads.append(dict(**info(p),url=url))
 assets=json.loads((EP/'foreground-assets.json').read_text());assets=[a for a in assets if a['asset_id'] not in ('picture-003','picture-006')]
 for key,countries in [('picture-003',COUNTRIES),('picture-006',COUNTRIES[1:])]:
  im=Image.new('RGB',(760,720),'#352e49');draw=ImageDraw.Draw(im);locations=[(95,105),(405,105),(95,310),(405,310),(250,515)] if len(countries)==5 else [(95,165),(405,165),(95,415),(405,415)]
  credits=[];source_urls=[];originals=[]
  for (en,sv),(x,y) in zip(countries,locations):
   p=raw/(en+'.png');flag=Image.open(p).convert('RGB');flag.thumbnail((260,135),Image.Resampling.LANCZOS);im.paste(flag,(x+(260-flag.width)//2,y));draw.text((x+130,y+145),sv,font=ImageFont.truetype(F,31),fill='#faf3e8',anchor='mt');m=META['File:Flag of '+en+'.svg'];artist=re.sub('<[^>]+>','',m['extmetadata'].get('Artist',{}).get('value','Not named'));credits.append(f'{sv} flag: {artist}. Public domain. {m["descriptionurl"]}. Proportionally resized and arranged; flag design unchanged.');source_urls.append(m['descriptionurl']);originals.append(info(p))
  dest=MEDIA/'pictures'/(key+'.png');im.save(dest);assets.append(dict(asset_id=key,kind='foreground',visual_type='flag',files=[info(dest)],source_url=source_urls[0],additional_source_urls=source_urls[1:],creator='Public-domain source flag artists; composition by Homebrew video studio',reuse_terms='Public domain flag designs; original arrangement under repository MIT license.',required_credits=' '.join(credits),relevance_verification='Actual source country flags, with exact Swedish country names from this sentence. No additional territories or legal assumptions inferred.',creation_method=dict(tool=str(Path(__file__).relative_to(ROOT)),source_originals=originals,transform='Flags proportionally downscaled and arranged without changing their designs.')))
 (EP/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');(EP/'flag-downloads.json').write_text(json.dumps(downloads,indent=2)+'\n');print('Accurate Nordic flag compositions saved',flush=True)
if __name__=='__main__':main()
