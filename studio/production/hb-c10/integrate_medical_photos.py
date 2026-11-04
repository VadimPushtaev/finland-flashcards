"""Integrate verified foreground photographs without changing narration or text."""
from pathlib import Path
import yaml,json,hashlib,re
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];EP=ROOT/'studio/episodes/hb-c10-konsstympning';MEDIA=ROOT/'studio/media/hb-c10-konsstympning'
def info(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
a=json.loads((EP/'foreground-assets.json').read_text());d=yaml.safe_load((EP/'script.yaml').read_text());photos=json.loads((EP/'selected-photos.json').read_text());dl=[];credits=[]
for key,p in photos.items():
    idx=int(key);pi=p['imageinfo'];meta=pi['extmetadata'];clean=lambda k:re.sub('<[^>]*>','',meta.get(k,{}).get('value','')).strip();src=ROOT/p['path'];im=Image.open(src).convert('RGB');im.thumbnail((1100,1000));dest=MEDIA/'pictures'/f'photo-{idx+1:02}.png';im.save(dest)
    asset=dict(asset_id=f'picture-{idx+1:02}',kind='foreground',visual_type='photograph',files=[info(dest)],creator=clean('Artist'),source_url=pi['descriptionurl'],reuse_terms=clean('LicenseShortName')+' '+clean('LicenseUrl'),required_credits=p['title'].removeprefix('File:')+' — '+clean('Artist')+'. '+clean('LicenseShortName')+'. '+pi['descriptionurl']+' '+clean('LicenseUrl')+'. Proportionally resized; original photograph preserved and original license retained.',relevance_verification=p['context']+' Source metadata: '+clean('ImageDescription'),creation_method=dict(tool=str(Path(__file__).relative_to(ROOT)),transform='Proportionally downscaled, complete original photograph preserved.'))
    a[idx]=asset;d['sentences'][idx]['render_image']=str(dest.relative_to(ROOT));d['sentences'][idx]['visual_cue']=p['context'];dl.append(dict(**info(src),url=p['download_url']));credits.append(p['title'].removeprefix('File:')+' — '+clean('Artist')+' · '+clean('LicenseShortName'))
    for req in d['asset_requests']:
        if req['id']==asset['asset_id']:req['description']=p['context'];req['fallback']='Retain original source-based diagram if this exact licensed photograph cannot be restored.'
for dec in d['episode_decisions']:
    if dec['id']=='visuals':dec['decision']='Eleven distinct non-graphic medical foreground pictures: three verified photographs of a stethoscope and actual Finnish healthcare buildings, plus eight individually composed source-specific pictorial diagrams of consequences/care. No photographed person is identified as a survivor; no fabricated anatomical details or medical promises. Fixed left area and fixed bilingual panel right.'
d['render']['credits']=d['render']['credits'][:2]+[dict(heading='Förgrundsbilder · Изображения',paragraphs=credits+['Original schematisk grafik: Homebrew video studio.','Fullständiga källor och licenser i medföljande CREDITS.md.'])]
(EP/'foreground-assets.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n');(EP/'foreground-downloads.json').write_text(json.dumps(dl,ensure_ascii=False,indent=2)+'\n');(EP/'script.yaml').write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False,width=100))
