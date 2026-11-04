"""Download reserved welfare sources and selected distinct public foreground photos."""
from pathlib import Path
import json,subprocess
ROOT=Path(__file__).resolve().parents[3];PROD=Path(__file__).resolve().parent;EP=ROOT/'studio/episodes/hb-c10-valfard';S=ROOT/'studio/media/hb-c10-valfard/sources';S.mkdir(parents=True,exist_ok=True)
def fetch(url,path):
    url=url.replace('https://thumb.wikimedia.org/','https://upload.wikimedia.org/').split('?')[0]
    if not path.exists():subprocess.run(['curl','-4','-L','--fail','--retry','2','--connect-timeout','15','--max-time','90',url,'-o',str(path)],check=True)
    return url
x=json.loads((PROD/'valfard-background-metadata.json').read_text());photo=next(iter(x['query']['pages'].values()));pi=photo['imageinfo'][0];pi['download_url']=fetch(pi.get('thumburl',pi['url']),S/'background.jpg')
track=next(t for t in json.loads(Path('/tmp/c07-employment-music-catalogue.json').read_text()) if t.get('isrc')=='USUAN1200048');fetch('https://incompetech.com/music/royalty-free/mp3-royaltyfree/Healing.mp3',S/'music.mp3')
(EP/'media-sources.json').write_text(json.dumps(dict(photo_title=photo['title'],photo=pi,music=track,context='Verified Vuosaari health and welfare centre, housing health/family/Kela services; decorative institutional setting, not evidence of a particular benefit decision.'),ensure_ascii=False,indent=2)+'\n')
fg=json.loads((PROD/'valfard-foreground-metadata.json').read_text());out={}
for i,p in enumerate(fg['query']['pages'].values()):
    if 'imageinfo' not in p:continue
    pi=p['imageinfo'][0];path=S/f'photo-{i:02}.jpg';url=fetch(pi.get('thumburl',pi['url']),path);out[p['title']]=dict(title=p['title'],imageinfo=pi,path=str(path.relative_to(ROOT)),download_url=url)
(EP/'selected-photos.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
