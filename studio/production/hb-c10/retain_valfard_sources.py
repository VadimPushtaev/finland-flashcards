"""Retain each reused photograph's pinned raw master independently in this episode."""
from pathlib import Path
import yaml,json,urllib.parse,re,hashlib,shutil
ROOT=Path(__file__).resolve().parents[3];EP=ROOT/'studio/episodes/hb-c10-valfard';OUT=ROOT/'studio/media/hb-c10-valfard/sources';retained=json.loads((EP/'retained-photo-sources.json').read_text());photos=json.loads((ROOT/'studio/production/hb-c10/existing-foreground-photos.json').read_text());indices=[8,7,54,59,10,39,25,119,34,85]
manifest=[]
for p in (ROOT/'studio/runtime').glob('*-downloads.yaml'):
    for e in yaml.safe_load(p.read_text()).get('downloads',[]):
        if 'url' in e:manifest.append(e)
def title(url):
    tail=urllib.parse.unquote(urllib.parse.urlsplit(url).path.rsplit('/',1)[-1]);tail=tail.removeprefix('File:');return re.sub(r'^\d+px-','',tail).replace('_',' ')
for idx in indices:
    if str(idx) in retained:continue
    a=photos[idx]['asset'];name=title(a['source_url']);matches=[m for m in manifest if title(m['url'])==name]
    if not matches:raise ValueError('No pinned original source manifest for '+name)
    src=next((e for e in matches if (ROOT/e['path']).is_file()),None)
    if src is None:raise ValueError('Restore pinned source before copying: '+name)
    raw=ROOT/src['path'];digest=hashlib.sha256(raw.read_bytes()).hexdigest();assert digest==src['sha256'],name
    dest=OUT/f'retained-{idx}{Path(src["path"]).suffix}';shutil.copyfile(raw,dest);retained[str(idx)]=dict(path=str(dest.relative_to(ROOT)),sha256=digest,bytes=dest.stat().st_size,url=src['url'])
(EP/'retained-photo-sources.json').write_text(json.dumps(retained,ensure_ascii=False,indent=2)+'\n');print('Pinned independent raw sources retained:',len(retained))
