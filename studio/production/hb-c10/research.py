"""Read public Wikimedia Commons metadata for Chapter 10 asset research."""
import json,sys,requests
from pathlib import Path
q=sys.argv[1]
r=requests.get('https://commons.wikimedia.org/w/api.php',params={'action':'query','format':'json','generator':'search','gsrsearch':q,'gsrnamespace':6,'gsrlimit':10,'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':1920},headers={'User-Agent':'HomebrewVideoStudio/1.0'},timeout=45)
r.raise_for_status(); x=r.json()
Path('studio/production/hb-c10/research-'+str(abs(hash(q)))+'.json').write_text(json.dumps(x,ensure_ascii=False,indent=2))
for p in x.get('query',{}).get('pages',{}).values():
    print(p['title'])
    print(p.get('imageinfo',[{}])[0].get('descriptionurl'))
    print(p.get('imageinfo',[{}])[0].get('extmetadata',{}).get('ImageDescription',{}).get('value','')[:250])
