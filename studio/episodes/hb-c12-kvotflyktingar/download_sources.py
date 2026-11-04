"""Fetch episode-selected public media through the studio shared throttle."""
from pathlib import Path
import json,subprocess,sys,urllib.parse
ROOT=Path(__file__).resolve().parents[3];EP=Path(__file__).resolve().parent
d=json.loads((EP/'media-sources.json').read_text())
out=ROOT/'studio/media'/EP.name/'sources'
rows=[('background.jpg',d['photo'].get('thumburl',d['photo']['url'])),('music.mp3','https://incompetech.com/music/royalty-free/mp3-royaltyfree/'+urllib.parse.quote(d['music']['filename']))]
for name,photo in d.get('foreground_photos',{}).items():
 pi=photo['imageinfo'][0];rows.append(('foreground-'+name+'.jpg',pi.get('thumburl',pi['url'])))
for name,url in rows:
 subprocess.run([sys.executable,str(ROOT/'studio/production/remaining/download.py'),'--url',url,'--output',str(out/name),'--timeout','300'],check=True)
