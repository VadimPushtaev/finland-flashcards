"""Pin unchanged downloaded foreground masters before generating asset registers."""
from pathlib import Path
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[3]


def main(section):
    episode=ROOT/'studio/episodes'/section
    evidence=json.loads((episode/'media-sources.json').read_text())
    photos=evidence.get('foreground_photos',{})
    if evidence.get('foreground_photo'):
        photos={**photos,'shopping':evidence['foreground_photo']}
    manifest=episode/'foreground-downloads.json'
    records=json.loads(manifest.read_text()) if manifest.exists() else []
    indexed={row['path']:row for row in records}
    for key,photo in photos.items():
        source=ROOT/'studio/media'/section/'sources'/('foreground-'+key+'.jpg')
        info=photo['imageinfo'][0]
        row=dict(path=str(source.relative_to(ROOT)),bytes=source.stat().st_size,
                 sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                 url=info.get('thumburl',info['url']))
        previous=indexed.get(row['path'])
        if previous and (previous['sha256']!=row['sha256'] or previous['url']!=row['url']):
            raise ValueError('Previously pinned foreground changed; reconcile source deliberately: '+row['path'])
        indexed[row['path']]=row
    manifest.write_text(json.dumps(list(indexed.values()),ensure_ascii=False,indent=2)+'\n')
    print(section,len(indexed),'foreground masters pinned')


if __name__=='__main__':main(sys.argv[1])
