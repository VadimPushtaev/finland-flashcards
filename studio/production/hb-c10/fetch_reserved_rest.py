"""Retain exactly reserved backgrounds and catalogue-verified music without model work."""
from pathlib import Path
import json,subprocess,urllib.parse
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
CHOICES={
'hb-c11-trafik':('traffic-remaining-background-research.json','File:Pohjolan Liikenne 1060 20260503.jpg','Verified actual Helsinki electric bus,2026. Decorative Finnish transport setting,no current route/timetable guarantee.'),
'hb-c11-brandsakerhet':('fire-remaining-background-research.json','File:Erottajan paloasema Helsinki.jpg','Verified Erottaja fire station,Helsinki. Decorative fire-safety institution,no current phone/address/service claim.'),
'hb-c11-nodsituationer':('fire-remaining-background-research.json','File:Kajaanin paloasema ja kaupungin varikko Kuntokatu 7 Kajaani.jpg','Verified Kajaani fire-station setting. Decorative responder institution,no new contact/location recommendation or response-time promise.'),
'hb-c10-funktionsnedsattning':('disability-remaining-background-research.json','File:Validia Ammattiopiston Kuntola-rakennus.jpg','Source explicitly identifies accessible Kuntola educational building with gym,teaching kitchens and art classroom. Decorative accessible-participation context,no provider endorsement/current service promise.'),
'hb-c10-psykisk':('mental-remaining-background-research.json','File:Kellokosken sairaalan portti.jpg','Verified gate of FORMER Kellokoski psychiatric hospital. Decorative historical institutional setting,no current treatment/service/contact claim or real patient diagnosis.'),
'hb-c10-sexuell':('sexual-remaining-background-research.json','File:Halikon terveysasema.JPG','Verified Halikko municipal health centre. Decorative public-health setting,no claim of current particular sexual-health service or appointment availability.'),
'hb-c10-sjukdom':('sickness-remaining-background-research.json','File:Porvoon sairaala.jpg','Verified Porvoo hospital,Finland. Decorative health-institution setting,no current availability or individual treatment promise.'),
'hb-c10-aldre':('elderly-remaining-background-research.json','File:Rosenkullan palvelutalo.JPG','Verified Rosenkulla retirement home,Liljendal. Decorative elder-care housing setting,no individual resident identity,current admission or service-quality claim.'),
'hb-c11-fritid':('leisure-remaining-background-research.json','File:Nuorisotalo Fanny, Vaasa.jpg','Verified Fanny youth-centre building,Vaasa. Decorative leisure/community setting,no current event schedule or age-eligibility inference.'),
'hb-c11-bibliotek':('../hb-c11-safety/library-research.json','File:Pääkirjasto Metso.jpg','Verified Tampere main library Metso. Distinct decorative library setting,no current opening-hours guarantee.')}
RESERVATIONS=json.loads((R/'studio/production/remaining/media-reservations.json').read_text());CATALOGUE=json.loads(Path('/tmp/c07-employment-music-catalogue.json').read_text())
def fetch(url,out):
    subprocess.run([str(R/'.venv/bin/python'),str(R/'studio/production/remaining/download.py'),'--url',url,'--output',str(out),'--timeout','300'],cwd=R,check=True)
for sid,(metadata,title,context) in CHOICES.items():
    e=R/'studio/episodes'/sid;s=R/'studio/media'/sid/'sources';s.mkdir(parents=True,exist_ok=True)
    record=RESERVATIONS[sid];assert record.get('background_file',title)==title
    pages=json.loads((P/metadata).read_text())['query']['pages'].values();page=next(p for p in pages if p.get('title')==title);pi=page['imageinfo'][0];url=pi.get('thumburl',pi['url']).replace('https://thumb.wikimedia.org/','https://upload.wikimedia.org/').split('?')[0];fetch(url,s/'background.jpg');pi['download_url']=url
    music=next(t for t in CATALOGUE if t.get('isrc')==record['music_isrc']);url='https://incompetech.com/music/royalty-free/mp3-royaltyfree/'+urllib.parse.quote(music['filename']);fetch(url,s/'music.mp3')
    (e/'media-sources.json').write_text(json.dumps(dict(photo_title=title,photo=pi,music=music,context=context),ensure_ascii=False,indent=2)+'\n');print(sid,'retained exact reserved background and music',flush=True)
