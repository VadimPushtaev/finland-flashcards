"""Reuse the licensed stethoscope source as a health-care object, never a patient."""
from pathlib import Path
import json,hashlib,shutil,re,yaml,requests
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];EP=Path(__file__).resolve().parent;MEDIA=ROOT/'studio/media/hb-c06-vald'
original=ROOT/'studio/episodes/hb-c05-barn/foreground-plan.json'
rec=next(r for r in json.loads(original.read_text()) if r['key']=='health');pi=rec['imageinfo'];meta=pi['extmetadata']
clean=lambda k:re.sub('<[^>]+>','',meta.get(k,{}).get('value','')).strip()
manifest=yaml.safe_load((ROOT/'studio/runtime/hb-c05-barn-downloads.yaml').read_text())
entry=next(e for e in manifest['downloads'] if e['path'].endswith('picture-health.jpg'))
raw=MEDIA/'sources/picture-health.jpg';raw.parent.mkdir(parents=True,exist_ok=True)
if not raw.exists():
 response=requests.get(entry['url'],headers={'User-Agent':'HomebrewVideoStudio/1.0'},timeout=90);response.raise_for_status();raw.write_bytes(response.content)
assert hashlib.sha256(raw.read_bytes()).hexdigest()==entry['sha256']
picture=MEDIA/'pictures/photo-health.png';im=Image.open(raw).convert('RGBA');im.thumbnail((1100,1000),Image.Resampling.LANCZOS);im.save(picture)
def info(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
assets=json.loads((EP/'foreground-assets.json').read_text());assets=[a for a in assets if a['asset_id']!='photo_health']
assets.append({'asset_id':'photo_health','kind':'foreground','visual_type':'photograph','files':[info(picture)],'source_url':pi['descriptionurl'],'creator':clean('Artist'),'reuse_terms':clean('LicenseShortName')+' '+clean('LicenseUrl'),'required_credits':'2023 Stetoskop.jpg — '+clean('Artist')+'. '+clean('LicenseShortName')+'. '+pi['descriptionurl']+' '+clean('LicenseUrl')+'. Complete image proportionally downscaled; original license retained.','relevance_verification':'Visible medical instrument for source sentences about effects on health and recovery. No patient, diagnosis or actual victim is depicted; no claim of a named support centre. Commons source metadata and original pinned download hash verified.','creation_method':{'tool':str(Path(__file__).relative_to(ROOT)),'transform':'Complete source proportionally downscaled only.'}})
(EP/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n')
(EP/'foreground-downloads.json').write_text(json.dumps([dict(info(raw),url=entry['url'])],indent=2)+'\n')
d=yaml.safe_load((EP/'script.yaml').read_text())
for r in d['sentences']:
 if r['sentence_id'] in ['hb-c06-u0052-s002','hb-c06-u0052-s003']:
  r.update(render_image=str(picture.relative_to(ROOT)),asset_ids=['episode_background','photo_health'],visual_cue='Verified stethoscope photograph as an illustrative medical object for the source health consequences; not a patient or actual victim. Complete image, no caption.')
d['asset_requests']=[a for a in d['asset_requests'] if a['id']!='photo_health']
d['asset_requests'].append({'id':'photo_health','kind':'foreground','description':'Licensed stethoscope photograph as a visible health-care object, no individual identity.','fallback':'Use source-based health illustration without a patient identity or new medical claim.'})
used={a for r in d['sentences'] for a in r['asset_ids']};d['asset_requests']=[a for a in d['asset_requests'] if a['kind'] not in ['foreground','background'] or a['id'] in used]
# The unused health diagram is retained as a regenerable alternative, not registered as visible coverage.
assets=[a for a in assets if a['asset_id'] in used];(EP/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n')
d['render']['credits'].append({'heading':'Förgrund · Изображения','paragraphs':['Stetoskop — Jacek Halicki · CC BY-SA4.0','Bilden proportionellt förminskad; licens behålls.','Källa och fullständig licens i medföljande CREDITS.md.']})
(EP/'script.yaml').write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False,width=100))
