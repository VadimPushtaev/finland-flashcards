"""Acquire centrally reserved Commons masters and official licensed music."""
from pathlib import Path
import requests,json,urllib.parse,time,hashlib,sys,subprocess
R=Path.cwd();P=R/'studio/production/hb-c09a';catalog=json.loads(Path('/tmp/hb-c06-current-music-catalogue.json').read_text())
config={
'forandring':('File:Fallkulla view 2016 7.jpg','Ebbs and Flows'),
'familjeformer':('File:Laivateollisuus housing by Erik Bryggman.jpg','Almost Bliss'),
'kon':('File:Skatudden helsinki - tove jansson parc - playground 2.jpg','Farm'),
'samlevnad':('File:Nykäsenranta Oulu 20220307.jpg','Swimmey Texture'),
'aktenskap':('File:Triple wedding in Porvoo 1965 (JOKAÖN3A B04-1).tif','Canon in D for Autoharp'),
'makar':('File:House with a garden in Vartiosaari, Helsinki, Finland, 2020 July.jpg','Simple Duet'),
'barnbidrag':('File:Kela welfare authority palace in Seinäjoki Finland.jpg','Melodie Victoria'),
'tolv':('File:Helsinki-traffic-park-1958.jpg','Somewhere Sunny'),
'underhall':('File:Office building of Ojahaanrinne 4 or Vaskivuorentie 25 in Myyrmäki, Vantaa, Finland, 2022 April.jpg',"Pepper's Theme")}
def fetch(url,p):
    if p.exists():return
    subprocess.run(['.venv/bin/python','studio/production/remaining/download.py','--url',url,'--output',str(p)],check=True)
for slug,(title,trackname) in config.items():
    if len(sys.argv)>1 and slug not in sys.argv[1:]:continue
    sid='hb-c09-'+slug
    reservations=json.loads((R/'studio/production/remaining/media-reservations.json').read_text())
    # Coordinator owns identities; do not consume an unreserved proposal.
    serialized=json.dumps(reservations,ensure_ascii=False)
    if title not in serialized or trackname not in serialized:print('WAITING RESERVATION',sid,flush=True);continue
    ep=R/'studio/episodes'/sid;sources=R/'studio/media'/sid/'sources';sources.mkdir(exist_ok=True,parents=True)
    meta=None
    for p in P.rglob('*.json'):
        try:d=json.loads(p.read_text())
        except:continue
        if isinstance(d,dict):
            for page in d.get('query',{}).get('pages',{}).values():
                if page['title']==title:meta=page['imageinfo'][0]
    if meta is None:raise ValueError('Missing Commons metadata '+title)
    track=next(m for m in catalog if m['title']==trackname)
    url=meta.get('thumburl',meta['url']);fetch(url,sources/'background.jpg')
    musicurl='https://incompetech.com/music/royalty-free/mp3-royaltyfree/'+urllib.parse.quote(track['filename']);fetch(musicurl,sources/'music.mp3')
    evidence=dict(photo_title=title,photo=meta,music=track,context='Source-identified Finnish residential/domestic setting used as a decorative family-topic backdrop; not an image of any particular individual family or proof of a legal claim.' if slug!='aktenskap' else 'Archival wedding scene in Porvoo,1965; decorative historical wedding context only, not a depiction of current legal conditions.')
    (ep/'media-sources.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    def inf(p,url):return dict(path=str(p.relative_to(R)),url=url,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
    import yaml
    (R/'studio/runtime'/f'{sid}-downloads.yaml').write_text(yaml.safe_dump(dict(schema_version=1,downloads=[inf(sources/'background.jpg',url),inf(sources/'music.mp3',musicurl)]),sort_keys=False))
    print(sid,title,trackname,'downloaded',flush=True)
