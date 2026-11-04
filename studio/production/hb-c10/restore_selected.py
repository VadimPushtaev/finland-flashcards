"""Restore four pinned legacy photo sources into this episode's exclusive media area."""
from pathlib import Path
import subprocess,yaml,json,hashlib
ROOT=Path(__file__).resolve().parents[3];EP=ROOT/'studio/episodes/hb-c10-valfard';OUT=ROOT/'studio/media/hb-c10-valfard/sources';chosen={100:('hb-c05-rasism','antiracism.jpg'),8:('hb-c05-likabehandling','education.jpg'),125:('hb-c05-jamstalldhet','researchers.png'),10:('hb-c05-barn','picture-family.jpg')};records={}
for idx,(sid,name) in chosen.items():
    item=next(x for x in yaml.safe_load((ROOT/'studio/runtime'/f'{sid}-downloads.yaml').read_text())['downloads'] if Path(x['path']).name==name);dest=OUT/f'retained-{idx}{Path(name).suffix}';url=item['url'].replace('https://thumb.wikimedia.org/','https://upload.wikimedia.org/').split('?')[0]
    if not dest.exists():subprocess.run(['curl','-4','-L','--fail','--retry','2','--connect-timeout','15','--max-time','60',url,'-o',str(dest)],check=True)
    sha=hashlib.sha256(dest.read_bytes()).hexdigest()
    if sha!=item['sha256']:raise ValueError('Pinned photograph changed: '+name)
    records[str(idx)]=dict(path=str(dest.relative_to(ROOT)),sha256=sha,bytes=dest.stat().st_size,url=url)
(EP/'retained-photo-sources.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
