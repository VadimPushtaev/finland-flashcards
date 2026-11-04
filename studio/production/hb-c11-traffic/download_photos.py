"""Acquire individually selected, already researched traffic photographs."""
from pathlib import Path
import json,subprocess,datetime,hashlib
ROOT=Path(__file__).resolve().parents[3];EP=ROOT/'studio/episodes/hb-c11-trafik';PROD=Path(__file__).parent;RAW=ROOT/'studio/media/hb-c11-trafik/sources';RAW.mkdir(parents=True,exist_ok=True)
choices={2:('walk','File:Konepajansilta pedestrian bridge in Vallila, Helsinki, Finland, 2021 July.jpg'),3:('walk','File:Pedestrian bridge over Töölönlahti in Helsinki, Finland, 2020.jpg'),4:('crossing','File:Finnish pedestrian crossing in Vimpeli.jpg'),5:('rural','File:Seututie 204 Säkylä (01).jpg'),7:('bicycle','File:Bicycle by the main building of University of Helsinki in Kluuvi, Helsinki, Finland, 2022 April.jpg'),8:('winter','File:Nuottasaarenkatu cycling path.JPG'),10:('cyclepath',"File:Cycle highway 'Itäbaana' in Herttoniemi, Helsinki, Finland; 2025 July.jpg"),12:('cycle','File:Bicycle white helmet from ABUS.jpg'),13:('metro','File:Helsinki Metro bridge.jpg'),14:('localtrain','File:Sm5-07B-helsinki-11-2-2012-fws.jpg'),15:('ticket','File:HSL - Ticket machine - 20241130.jpg'),16:('ruralbus','File:Bus Sop of Village Vuontisjärjvi - panoramio.jpg'),17:('ferry','File:Ferry Suomenlinna II 01.jpg'),20:('tram','File:Artic (tram) in Helsinki 20170130.jpg'),21:('rural','File:Seututie 325 Pelisalmi 1.jpg'),29:('inspection','File:A-katsastus, Lielahti.JPG')}
selected={};downloads=[]
for n,(kind,title) in choices.items():
 research=ROOT/f'studio/production/hb-c11-safety/traffic-{kind}-research.json';pages=json.loads(research.read_text())['query']['pages'];pages=pages.values() if isinstance(pages,dict) else pages;row=next(r for r in pages if r['title']==title);info=row['imageinfo'][0];url=info.get('thumburl',info['url']);path=RAW/f'photo-{n:03}.jpg';print(datetime.datetime.now(datetime.timezone.utc).isoformat(),n,title,flush=True)
 if not path.exists():
  result=subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'studio/production/remaining/download.py'),'--url',url,'--output',str(path.relative_to(ROOT)),'--timeout','90'],cwd=ROOT)
  if result.returncode:
   print('DEFERRED',n,title,'download exit',result.returncode,flush=True)
   continue
 selected[str(n)]={**row,'research':str(research.relative_to(ROOT)),'raw_path':str(path.relative_to(ROOT)),'download_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'intended_sentence_index':n}
 downloads.append(dict(path=str(path.relative_to(ROOT)),url=url,sha256=selected[str(n)]['download_sha256'],bytes=path.stat().st_size));(EP/'selected-photos.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n');(EP/'foreground-downloads.json').write_text(json.dumps(downloads,ensure_ascii=False,indent=2)+'\n')
print('COMPLETE',len(selected),flush=True)
