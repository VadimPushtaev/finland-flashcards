"""Download this episode's reserved unchanged media sources."""
from pathlib import Path
import json, urllib.request, urllib.parse
ROOT=Path(__file__).resolve().parents[3]
EP=Path(__file__).resolve().parent
d=json.loads((EP/'media-sources.json').read_text())
out=ROOT/'studio/media'/EP.name/'sources';out.mkdir(parents=True,exist_ok=True)
for name,url in [('background.jpg',d['photo'].get('thumburl',d['photo']['url'])),('music.mp3','https://incompetech.com/music/royalty-free/mp3-royaltyfree/'+urllib.parse.quote(d['music']['filename'])),('foreground-shopping.jpg',d['foreground_photo']['imageinfo'][0].get('thumburl',d['foreground_photo']['imageinfo'][0]['url']))]:
 p=out/name
 if not p.exists():
  request=urllib.request.Request(url,headers={'User-Agent':'HomebrewVideoStudio/1.0 (licensed educational media)'})
  with urllib.request.urlopen(request,timeout=45) as response:p.write_bytes(response.read())
 print(name,p.stat().st_size)
