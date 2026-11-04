"""Fetch explicitly selected licensed source photographs using curl."""
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];PROD=Path(__file__).resolve().parent;EP=ROOT/'studio/episodes/hb-c10-utkomststod';MEDIA=ROOT/'studio/media/hb-c10-utkomststod'
selected={1:('groceries-research.json','File:Healthy Grocery Shopping (Unsplash).jpg','Food photograph illustrates one of the necessary expense categories. The photograph is illustrative, not evidence of all expenses or benefit eligibility.'),2:('housing-research.json','File:Helsinginkatu 20 apartment building in Kallio, Helsinki, Finland, 2020.jpg','Accurately identified Helsinki residential building illustrates living in Finland; it is not a legal definition of permanent residence.')}
photos={}
for idx,(file,title,context) in selected.items():
    p=next(p for p in json.loads((PROD/file).read_text())['query']['pages'].values() if p['title']==title);pi=p['imageinfo'][0];path=MEDIA/'sources'/f'photo-{idx+1:02}.jpg';url=pi.get('thumburl',pi['url']).replace('https://thumb.wikimedia.org/','https://upload.wikimedia.org/').split('?')[0]
    if not path.exists():subprocess.run(['curl','-4','-L','--fail','--retry','2','--connect-timeout','15','--max-time','60',url,'-o',str(path)],check=True)
    photos[str(idx)]=dict(title=title,imageinfo=pi,path=str(path.relative_to(ROOT)),context=context,download_url=url)
(EP/'selected-photos.json').write_text(json.dumps(photos,ensure_ascii=False,indent=2)+'\n')
