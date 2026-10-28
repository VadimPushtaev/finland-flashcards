"""Acquire coordinator-reserved background/music sources and retain primary metadata."""
from pathlib import Path
import json,requests,urllib.parse,re
ROOT=Path(__file__).resolve().parents[3]
SEARCH=Path('/tmp/c06-protection-commons-search.json')
PLAN={
'hb-c06-vald':('File:Meilahden sairaala-alue Helsinki 2022-09-19 02.jpg','Parting of the Ways - Part 1','Health-care setting for recovery/support passages; decorative context only, not a named Seri centre or depiction of a victim.'),
'hb-c06-manniskohandel':('File:Finlayson, kuusvooninkinen.jpg','Numinous Shine','Documented Finnish industrial workplace architecture as a restrained work-related motif; never evidence of exploitation, a trafficking event or an offender at this location.'),
'hb-c06-brottsoffer':('File:Ruosilankujan pelastusasema 2020-05-19.jpg','White','Identified Helsinki fire station as emergency/help infrastructure; decorative background, not a claim that this building houses victim support services.'),
'hb-c06-rattshjalp':('File:Tampereen käräjäoikeus.jpg','Water Prelude','Identified Pirkanmaa district-court building in Tampere, illustrating legal institutions; not identified as the public legal-aid office or asylum-advice office.')}
D=json.loads(SEARCH.read_text()); pages={p['title']:p for group in D.values() for p in group.get('query',{}).get('pages',{}).values()}
response=requests.get('https://incompetech.com/music/royalty-free/pieces.json',timeout=90);response.raise_for_status();catalog=response.json()
for sid,(title,music,context) in PLAN.items():
 ep=ROOT/'studio/episodes'/sid;source=ROOT/'studio/media'/sid/'sources';source.mkdir(parents=True,exist_ok=True)
 pi=pages[title]['imageinfo'][0];url=pi.get('thumburl',pi['url']).split('?')[0];pi['download_url']=url
 track=next(m for m in catalog if m['title']==music)
 pageurl='https://incompetech.com/music/royalty-free/index.html?isrc='+track['isrc']
 r=requests.get(pageurl,timeout=90);r.raise_for_status();html=r.text
 (source/'music-license-page.html').write_text(html)
 (ep/'music-source.json').write_text(json.dumps(track,ensure_ascii=False,indent=2)+'\n')
 if 'creativecommons.org/licenses/by/4.0' not in html:raise ValueError('Primary page lacks CC BY4.0 license')
 for dest,uri in [(source/'background.jpg',url),(source/'music.mp3','https://incompetech.com/music/royalty-free/mp3-royaltyfree/'+urllib.parse.quote(track['filename']))]:
  if not dest.exists():
   r=requests.get(uri,headers={'User-Agent':'HomebrewVideoStudio/1.0 (educational documentary production)'},timeout=120);r.raise_for_status();dest.write_bytes(r.content)
 evidence={'photo_title':title,'photo':pi,'music':track,'context':context,'primary_music_page':pageurl,'primary_music_page_checked':'Track-page template retained in ignored sources/music-license-page.html; official pieces.json record retained in music-source.json. Exact track title/ISRC and CC BY4.0 license template checked; descriptor read by producer.'}
 (ep/'media-sources.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
 print(sid,title,music,track.get('instruments'),track.get('description'),flush=True)
