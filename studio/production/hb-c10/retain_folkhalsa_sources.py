"""Retain source-verified photographs independently for the public-health episode."""
from pathlib import Path
import yaml,json,urllib.parse,re,hashlib,shutil,subprocess
ROOT=Path(__file__).resolve().parents[3];EP=ROOT/'studio/episodes/hb-c10-folkhalsa';OUT=ROOT/'studio/media/hb-c10-folkhalsa/sources';OUT.mkdir(parents=True,exist_ok=True);photos=json.loads((ROOT/'studio/production/hb-c10/existing-foreground-photos.json').read_text());mapping={12:83,21:62,23:4,24:74,25:60,33:58,41:84,46:68};manifest=[]
for p in (ROOT/'studio/runtime').glob('*-downloads.yaml'):
    for e in yaml.safe_load(p.read_text()).get('downloads',[]):
        if 'url' in e:manifest.append(e)
def title(url):
    tail=urllib.parse.unquote(urllib.parse.urlsplit(url).path.rsplit('/',1)[-1]);return re.sub(r'^\d+px-','',tail.removeprefix('File:')).replace('_',' ')
records={}
for row,idx in mapping.items():
    a=photos[idx]['asset'];name=title(a['source_url']);matches=[m for m in manifest if title(m['url'])==name]
    if not matches:raise ValueError('Missing pinned source: '+name)
    e=next((m for m in matches if (ROOT/m['path']).is_file()),matches[0]);dest=OUT/f'retained-{row+1:02}{Path(e["path"]).suffix}';raw=ROOT/e['path']
    if not dest.exists():
        if raw.is_file():
            assert hashlib.sha256(raw.read_bytes()).hexdigest()==e['sha256'];shutil.copyfile(raw,dest)
        else:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'studio/production/remaining/download.py'),'--url',e['url'].replace('https://thumb.wikimedia.org/','https://upload.wikimedia.org/').split('?')[0],'--output',str(dest),'--sha256',e['sha256'],'--timeout','180'],check=True)
    assert hashlib.sha256(dest.read_bytes()).hexdigest()==e['sha256'];records[str(row)]=dict(asset_record=a,path=str(dest.relative_to(ROOT)),sha256=e['sha256'],url=e['url'],bytes=dest.stat().st_size)
(EP/'retained-photo-assets.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
# The shared reservation uses this actual medical-object photo as this episode's
# decorative background. It is never reused in this episode's foreground.
meta=json.loads((ROOT/'studio/production/hb-c10/konsstympning-medical-metadata.json').read_text());bg=next(p for p in meta['query']['pages'].values() if p['title']=='File:2023 Stetoskop.jpg');pi=bg['imageinfo'][0];shutil.copyfile(ROOT/'studio/media/hb-c10-konsstympning/sources/photo-02.jpg',OUT/'background.jpg')
track=next(t for t in json.loads(Path('/tmp/c07-employment-music-catalogue.json').read_text()) if t.get('isrc')=='USUAN1800008');url='https://incompetech.com/music/royalty-free/mp3-royaltyfree/'+urllib.parse.quote(track['filename']);subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'studio/production/remaining/download.py'),'--url',url,'--output',str(OUT/'music.mp3'),'--timeout','300'],check=True)
(EP/'media-sources.json').write_text(json.dumps(dict(photo_title=bg['title'],photo=pi,music=track,context='Actual source-identified stethoscope, used decoratively for the public-health topic. Not a diagnosis or photographed patient; this photo is not used in foreground picture coverage.'),ensure_ascii=False,indent=2)+'\n')
print('Retained8independentlicensedconcretephotographs plus reserved background/music.')
