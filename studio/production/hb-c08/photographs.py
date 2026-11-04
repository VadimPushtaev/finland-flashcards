"""Resolve specific licensed photographs into existing per-sentence picture plans."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,yaml
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];PROD=ROOT/'studio/production/hb-c08'
def info(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def main(sid):
 ep=ROOT/'studio/episodes'/sid;media=ROOT/'studio/media'/sid;meta={r['title']:r['imageinfo'][0] for p in (PROD/'research').glob('*.json') for r in json.loads(p.read_text()).get('query',{}).get('pages',{}).values() if r.get('imageinfo')};plans=json.loads((ep/'photograph-plan.json').read_text());assets=json.loads((ep/'foreground-assets.json').read_text()) if (ep/'foreground-assets.json').exists() else [];assets=[a for a in assets if a['asset_id'] not in plans];downloads=[]
 for key,entry in plans.items():
  pi=meta[entry['title']];raw=media/'sources'/(key+'-original.jpg');raw.parent.mkdir(parents=True,exist_ok=True);url=pi.get('thumburl',pi['url'])
  if not raw.exists():
   subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'studio/production/remaining/download.py'),'--url',url,'--output',str(raw)],check=True)
  dest=media/'pictures'/(key+'.png');dest.parent.mkdir(parents=True,exist_ok=True);im=Image.open(raw).convert('RGB');im.thumbnail((1200,1050),Image.Resampling.LANCZOS);im.save(dest)
  m=pi['extmetadata'];clean=lambda k:re.sub('<[^>]+>','',str(m.get(k,{}).get('value',''))).strip();license=clean('LicenseShortName');licenseurl=clean('LicenseUrl');creator=clean('Artist')
  if license=='Attribution':
   license='Attribution-only permission: use and adaptations for any purpose with proper creator credit';licenseurl=pi['descriptionurl']+'#Licensing'
  assets.append(dict(asset_id=key,kind='foreground',visual_type='photograph',files=[info(dest)],source_url=pi['descriptionurl'],creator=creator,reuse_terms=license+' '+licenseurl,required_credits=entry['title'].removeprefix('File:')+' — '+creator+'. '+license+'. '+pi['descriptionurl']+' '+licenseurl+'. Proportionally resized; entire photograph retained. Source license retained.',relevance_verification=entry['context']+' Source metadata: '+clean('ImageDescription'),creation_method=dict(tool=str(Path(__file__).relative_to(ROOT)),original_file=info(raw),transform='Proportional downscale; complete image preserved.')));downloads.append(dict(**info(raw),url=url));print(sid,key,entry['title'],flush=True)
 (ep/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');(ep/'foreground-downloads.json').write_text(json.dumps(downloads,ensure_ascii=False,indent=2)+'\n')
 d=yaml.safe_load((ep/'script.yaml').read_text());d['render']['credits']=d['render']['credits'][:2]
 # Full per-picture attribution in sidecar avoids adding minutes of duplicate credit cards.
 d['render']['credits'].append(dict(heading='Förgrundsbilder · Изображения',paragraphs=['Verifierade fotografier från Wikimedia Commons.','Varje upphovsperson, länk och licens finns i CREDITS.md.','Original källbaserad illustrationsgrafik: Homebrew video studio.']))
 for r in d['sentences']:
  key=r['asset_ids'][-1]
  if key in plans:r['visual_cue']='Verified relevant foreground photograph: '+plans[key]['context']+' Exact bilingual source text remains on the fixed right panel.'
 (ep/'script.yaml').write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False,width=100))
if __name__=='__main__':
 for sid in sys.argv[1:]:main(sid)
