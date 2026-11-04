"""Retain exactly reserved backgrounds and catalogue-verified music without model work."""
from pathlib import Path
import json,subprocess,urllib.parse
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
CHOICES={'hb-c10-pension':('pension-institution-research.json','File:Opastinsilta 7, former Eläketurvakeskus office building (Itä-Pasila, Helsinki, Finland) Apr 9, 2026.jpg','Verified FORMER Finnish Centre for Pensions headquarters,Opastinsilta7,Helsinki,photographed2026. Decorative historical institutional context only; no current office,address,contact or benefit-service promise.')}
RESERVATIONS=json.loads((R/'studio/production/remaining/media-reservations.json').read_text());CATALOGUE=json.loads(Path('/tmp/c07-employment-music-catalogue.json').read_text())
def fetch(url,out):
    subprocess.run([str(R/'.venv/bin/python'),str(R/'studio/production/remaining/download.py'),'--url',url,'--output',str(out),'--timeout','300'],cwd=R,check=True)
for sid,(metadata,title,context) in CHOICES.items():
    e=R/'studio/episodes'/sid;s=R/'studio/media'/sid/'sources';s.mkdir(parents=True,exist_ok=True)
    record=RESERVATIONS[sid];assert record.get('background_file',title)==title
    pages=json.loads((P/metadata).read_text())['query']['pages'].values();page=next(p for p in pages if p.get('title')==title);pi=page['imageinfo'][0];url=pi.get('thumburl',pi['url']).replace('https://thumb.wikimedia.org/','https://upload.wikimedia.org/').split('?')[0];fetch(url,s/'background.jpg');pi['download_url']=url
    music=next(t for t in CATALOGUE if t.get('isrc')==record['music_isrc']);url='https://incompetech.com/music/royalty-free/mp3-royaltyfree/'+urllib.parse.quote(music['filename']);fetch(url,s/'music.mp3')
    (e/'media-sources.json').write_text(json.dumps(dict(photo_title=title,photo=pi,music=music,context=context),ensure_ascii=False,indent=2)+'\n');print(sid,'retained exact reserved background and music',flush=True)
