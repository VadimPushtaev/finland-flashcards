"""Restore selected non-graphic licensed healthcare masters with shared throttling."""
from pathlib import Path
import json,subprocess,urllib.parse
ROOT=Path(__file__).resolve().parents[3];PROD=Path(__file__).resolve().parent;SID='hb-c10-konsstympning';EP=ROOT/'studio/episodes'/SID;S=ROOT/'studio/media'/SID/'sources';S.mkdir(parents=True,exist_ok=True)
def fetch(url,path):
    url=url.replace('https://thumb.wikimedia.org/','https://upload.wikimedia.org/').split('?')[0]
    subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'studio/production/remaining/download.py'),'--url',url,'--output',str(path),'--timeout','300'],check=True)
    return url
x=json.loads((PROD/'jorvi-research.json').read_text());bg=next(p for p in x['query']['pages'].values() if p['title']=='File:Jorvi.jpg');pi=bg['imageinfo'][0];pi['download_url']=fetch(pi.get('thumburl',pi['url']),S/'background.jpg')
track=next(t for t in json.loads(Path('/tmp/c07-employment-music-catalogue.json').read_text()) if t.get('isrc')=='USUAN1900005');fetch('https://incompetech.com/music/royalty-free/mp3-royaltyfree/'+urllib.parse.quote(track['filename']),S/'music.mp3')
(EP/'media-sources.json').write_text(json.dumps(dict(photo_title=bg['title'],photo=pi,music=track,context='Verified Jorvi Hospital in Espoo; distinct decorative healthcare setting, not evidence that a specific procedure is offered at this site.'),ensure_ascii=False,indent=2)+'\n')
fg=json.loads((PROD/'konsstympning-medical-metadata.json').read_text());selected={1:('File:2023 Stetoskop.jpg','Actual stethoscope represents medical assessment of health problems, not evidence of a particular diagnosis.'),7:('File:Kalasataman terveys- ja hyvinvointikeskus - Helsinki - 1.jpg','Verified actual Kalasatama health and welfare centre illustrates an outpatient setting, without claiming any particular surgery is offered at that centre.'),8:('File:Meilahden tornisairaala.jpg','Verified Meilahti hospital building illustrates hospital-based reconstructive care, without claiming specific procedures at that building.')};records={}
for idx,(title,context) in selected.items():
    p=next(p for p in fg['query']['pages'].values() if p['title']==title);pi=p['imageinfo'][0];path=S/f'photo-{idx+1:02}.jpg';url=fetch(pi.get('thumburl',pi['url']),path);records[str(idx)]=dict(title=title,imageinfo=pi,path=str(path.relative_to(ROOT)),context=context,download_url=url)
(EP/'selected-photos.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
