"""Acquire varied actual leisure objects/venues,then require contact-sheet inspection."""
from pathlib import Path
import json,subprocess
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent;SID='hb-c11-fritid';E=R/'studio/episodes'/SID;S=R/'studio/media'/SID/'sources';S.mkdir(parents=True,exist_ok=True)
CHOICES={0: ('leisure-park-research.json',
     'File:Esplanadin puisto Helsinki 2022-09-16 01.jpg',
     'Verified Helsinki Esplanadi park,ordinary leisure setting,no current event or route-safety claim.'),
 1: ('leisure-art-research.json',
     'File:Simple painting equipment!.jpg',
     'Actual painting materials,one illustrative hobby for different ages; no pictured people assigned an '
     'age group or class participation.'),
 3: ('library-research.json',
     'File:Tampere City Library interior 2.jpg',
     'Verified actual Tampere municipal-library interior,one listed local-service example. Earlier rejected '
     'ONLY as a reading-room image; appropriate here as visible collection/library setting.'),
 4: ('../hb-c10/leisure-remaining-background-research.json',
     'File:Nuorisotalo Feenix.jpg',
     'Verified Feenix youth-centre building,Petäjävesi,one listed local-service type. No current '
     'event,opening-hour or age-admission guarantee.'),
 5: ('leisure-theatre-research.json',
     'File:Oulun teatteri.jpg',
     'Verified Oulu theatre,actual cultural venue,not a fabricated scheduled event or ticket-price claim.'),
 8: ('leisure-guitar-research.json',
     'File:2 Kay K235 acoustic-guitar.jpg',
     'Actual source-identified acoustic guitar,one music-club/hobby object,no brand endorsement or '
     'particular lesson guarantee.'),
 10: ('leisure-gym-research.json',
      'File:Design and equipment in modern gym.jpg',
      'Actual gym equipment,ordinary exercise-setting illustration,no photographed person assigned health '
      'status or specific exercise advice.'),
 11: ('leisure-jogging2-research.json',
      'File:Young woman jogging, Portugal 2010.jpg',
      'Source-identified visible jogging in Portugal,2010. Illustrative ordinary activity,not a Finnish '
      'location,medical recommendation or fitness assessment.'),
 12: ('leisure-institute-research.json',
      'File:Linnalan kansalaisopisto.jpg',
      'Verified Linnala adult-education institute,Savonlinna,2025. Institutional category,no current '
      'sports-course availability or price claim.'),
 13: ('leisure-art-research.json',
      'File:Xuan Brushes for Chinese Brush painting and calligraphy.jpg',
      'Actual painting/calligraphy brush objects,one source art-course type; no claim these are Finnish '
      'course materials or recommendation of a technique.'),
 15: ('leisure-field-research.json',
      'File:Nummelan urheilukenttä 1.jpg',
      'Verified Nummela sports field,Vihti,2024,one recreation-facility type,no individual site availability '
      'or free-use guarantee.'),
 17: ('leisure-community-research.json',
      'File:Asukastalo LAVA - panoramio.jpg',
      'Source-identified actual resident-house setting,no assertion of a specific current operator,opening '
      'schedule or hire policy.'),
 18: ('leisure-gym-research.json',
      'File:Outdoor gym equipment - geograph.org.uk - 3432704.jpg',
      'Actual outdoor exercise equipment,UK context; illustrates exercise-activity category without claiming '
      'pictured operator is a Finnish association/private company.'),
 19: ('leisure-pool-research.json',
      'File:Alavus - uimahalli.jpg',
      'Verified Alavus swimming hall,Kunto-Lutra; actual facility category,no current price,schedule or '
      'site-specific concession promise.'),
 20: ('leisure-field-research.json',
      'File:Palosaaren urheilukenttä.jpg',
      'Verified Palosaari sports field,one source field category,no current hire availability or particular '
      'owner claim.'),
 23: ('leisure-sauna-research.json',
      'File:Modern sauna.jpg',
      'Actual modern sauna interior,illustrative sauna-object/room category only; not claimed to be a '
      'specific Finnish swimming-hall sauna or current access promise.'),
 25: ('leisure-community-research.json',
      'File:Asukastalo Renki at Piianpuisto in Malminkartano, Helsinki, Finland, 2022 July.jpg',
      'Verified Renki resident house,Helsinki,2022. Source community-space category,no invented activity '
      'schedule.'),
 28: ('leisure-hall-research.json',
      'File:Mount Colliery community hall, interior, 2021.jpg',
      'Actual Australian community-hall interior,illustrative room type for possible private use; no claim '
      'of Finnish location,current hire terms or pictured family event.'),
 29: ('leisure-park-research.json',
      'File:Armi Ratian puisto Helsinki 2022-09-18 01.jpg',
      'Verified Armi Ratia park,Helsinki,one listed maintained green-area example,no water-quality or '
      'current safety claim.'),
 30: ('leisure-beach-research.json',
      'File:Papinjärven uimaranta Oulunsalossa 27.10.2022. 2.jpg',
      'Verified Papinjärvi bathing beach,Oulunsalo,2022. Public-beach category,no present '
      'water-quality,ice-bearing or swimming-safety assurance.'),
 32: ('leisure-litter-research.json',
      'File:Picking up Litter (4976627765).jpg',
      'Source-identified Youth Conservation Corps litter cleanup near maintenance buildings. Illustrative '
      'cleanup action,no claim participants created the litter or are in Finland.'),
 33: ('leisure-dance-research.json',
      'File:Ballet Dancers Class Black and White.jpg',
      'Source-identified children learning ballet in Russia,ordinary dance-hobby example. No Finnish '
      'location,immigration,medical or current-class claim.'),
 34: ('leisure-theatre-research.json',
      'File:Maskun teatteri.JPG',
      'Source-identified Masku theatre stage/auditorium,one artistic-hobby venue category,no assertion of a '
      'current youth production or availability.'),
 36: ('leisure-institute-research.json',
      'File:Mäntsälän Kansalaisopisto.jpg',
      'Verified Mäntsälä adult-education institute building,one listed organising-institution category,no '
      'current particular youth-course promise.'),
 37: ('../hb-c10/leisure-remaining-background-research.json',
      'File:Nuorisotalo Ristikka.jpg',
      'Verified Ristikka youth-centre building,Vaasa,source youth-work institution type,no invented local '
      'age limits.'),
 38: ('../hb-c10/leisure-remaining-background-research.json',
      'File:Iisalmen nuorisotalo - aiempi Suojeluskuntatalo (1923) - Kirkkopuistonkatu 25 - Iisalmi - 1.jpg',
      'Source-identified Iisalmi youth-centre building and historical earlier use. No claim of a particular '
      'current club,age threshold or event.'),
 46: ('leisure-youth-research.json',
      'File:Keravan pappila, Wbabbila, nuorisotila.jpg',
      'Source identifies Kerava parish building/youth space. Illustrates parish youth-work context,no new '
      'opening-hours,current programme or entry guarantee.'),
 47: ('leisure-group-research.json',
      'File:Running group, Mullaghmore - geograph.org.uk - 6622883.jpg',
      'Source-identified actual running group,Mullaghmore. Exercise/social opportunity illustration only,no '
      'claim participants are friends,volunteers or in Finland.'),
 49: ('leisure-pool-research.json',
      'File:Kuntolaakso swimming pool (Kuntolaakson uimahalli, Kuopio, Finland) Aug 25, 2026.jpg',
      'Verified Kuntolaakso swimming-pool building,Kuopio,2026. One sports-facility category,no guarantee of '
      'current unrestricted admission or specific price.'),
 50: ('leisure-computer-research.json',
      'File:HP laptop keyboard.jpg',
      'Actual laptop keyboard,ordinary website-information object,not an official government '
      'interface,device endorsement or invented online instruction.')}
selected={}
for idx,(metadata,title,context) in CHOICES.items():
    pages=json.loads((P/metadata).read_text())['query']['pages'].values();p=next(q for q in pages if q.get('title')==title);pi=p['imageinfo'][0];assert pi['extmetadata'].get('Artist',{}).get('value'),title;assert pi['extmetadata'].get('LicenseShortName',{}).get('value'),title;url=pi.get('thumburl',pi['url']).replace('https://thumb.wikimedia.org/','https://upload.wikimedia.org/').split('?')[0];dest=S/(f'foreground-replacement-{idx+1:02}.jpg' if idx==19 else f'foreground-final-{idx+1:02}.jpg' if idx in [32,47] else f'foreground-{idx+1:02}.jpg');subprocess.run([str(R/'.venv/bin/python'),str(R/'studio/production/remaining/download.py'),'--url',url,'--output',str(dest),'--timeout','300'],cwd=R,check=True);selected[str(idx)]=dict(title=title,imageinfo=pi,path=str(dest.relative_to(R)),download_url=url,context=context);(E/'selected-photos.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n');print(idx,title,flush=True)
(E/'retained-photo-assets.json').write_text('{}\n')
