"""Retain source-verified actual library facilities and concrete objects for inspection."""
from pathlib import Path
import json,subprocess
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent;SID='hb-c11-bibliotek';E=R/'studio/episodes'/SID;S=R/'studio/media'/SID/'sources';S.mkdir(parents=True,exist_ok=True)
CHOICES={
0:('library-research.json','File:Main library Metso1.jpg','Verified Tampere municipal main library Metso; illustration of municipal-library category,no current opening hours.'),
1:('library-research.json','File:Tampere City Library interior.jpg','Verified actual Tampere library interior illustrates source library uses; visible equipment verified separately,no invented event.'),
2:('library-palokka-research.json','File:Palokka Library.jpg','Verified Palokka Library,Jyväskylä. Distinct actual municipal-library exterior,no unverified current opening hours.'),
3:('library-games-research.json','File:Board games at the FIMS Graduate Library.jpg','Actual board games in the source-identified FIMS Graduate Library. Illustrative game objects,not a claim of a Finnish location or current Finnish children event.'),
4:('library-lukusali-research.json','File:Tikkurilan kirjasto lukusali.jpg','Verified actual Tikkurila library reading room; actual quiet desk furniture visually inspected,no current opening-hours claim.'),
5:('library-lukusali-research.json','File:Kansalliskirjaston lukusali.jpg','Verified National Library of Finland reading room; actual reading furniture visually inspected,no pupil status/current unrestricted admission claim.'),
6:('library-computer-research.json','File:Palokka Library 2.jpg','Primary description identifies actual computers in Palokka Library,Jyväskylä. Computer-use illustration,no fabricated Finnish language-café schedule or guidance event.'),
7:('library-university-research.json','File:University of Helsinki roof 001.jpg','Primary metadata identifies Kaisa House,Helsinki University Library. Actual academic-library building context,no fabricated access restriction or membership policy.'),
15:('library-bookbus-research.json','File:Kirjastoauto Wäinö 1.jpg','Verified actual library bus Wäinö,Jyväskylä,not an ordinary bus; no current stop/schedule claim.'),
17:('library-palokka-research.json','File:Palokka Library - return machine.jpg','Primary description identifies actual book-return machine,Palokka Library. Illustrates returning,one of source return OR renew options; no invented machine instructions or renewal limits.'),
22:('library-dvd-research.json','File:DVD 2.jpg','Actual photographed optical discs by photo Moma SM,CC BY-SA4.0,one source media category,no particular library holding claim.'),
26:('library-children-research.json','File:Saami-language kids books at Iso Omena Library 7AUG2026.jpg','Source-identified actual children books in Saami languages,Iso Omena Library,August2026. Illustrates children collection,not assertion this branch is the Multilingual Library or an invented current inventory.')}
selected={}
for idx,(metadata,title,context) in CHOICES.items():
    pages=json.loads((P/metadata).read_text())['query']['pages'].values();page=next(p for p in pages if p.get('title')==title);pi=page['imageinfo'][0];url=pi.get('thumburl',pi['url']).replace('https://thumb.wikimedia.org/','https://upload.wikimedia.org/').split('?')[0];dest=S/(f'foreground-reading-{idx+1:02}.jpg' if idx in [4,5] else f'foreground-disc-{idx+1:02}.jpg' if idx==22 else f'foreground-{idx+1:02}.jpg');subprocess.run([str(R/'.venv/bin/python'),str(R/'studio/production/remaining/download.py'),'--url',url,'--output',str(dest),'--timeout','300'],cwd=R,check=True);selected[str(idx)]=dict(title=title,imageinfo=pi,path=str(dest.relative_to(R)),download_url=url,context=context);(E/'selected-photos.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n');print(idx,title,flush=True)
(E/'retained-photo-assets.json').write_text('{}\n')
