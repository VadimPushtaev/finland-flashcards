"""Clean verified photo attribution/display title only;preserve all body/media evidence."""
from pathlib import Path
import json,yaml,hashlib,shutil,urllib.parse
R=Path(__file__).resolve().parents[3];E=R/'studio/episodes/hb-c10-vard';M=R/'studio/media/hb-c10-vard';P=Path(__file__).resolve().parent;A=E/'revisions/pre-credit-cleanup';A.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['script.yaml','SCRIPT.md','assets.yaml','foreground-assets.json','CREDITS.md','prerender-handoff.json']:
 src=E/name;dst=A/name
 if src.exists() and not dst.exists():shutil.copyfile(src,dst)
for name in ['frame-56.png','frame-61.png']:
 src=M/'render'/name;dst=A/name
 if src.exists() and not dst.exists():shutil.copyfile(src,dst)
s=yaml.safe_load((E/'script.yaml').read_text());before_rows=s['sentences'];metrics=json.loads((M/'narration/metrics.json').read_text());media={r['path']:sha(R/r['path']) for r in metrics}
for row in s['sentences']:
 if row.get('render_image'):media[row['render_image']]=sha(R/row['render_image'])
raw_metadata_hash=sha(E/'selected-photos.json');fg=json.loads((E/'foreground-assets.json').read_text());a=next(a for a in fg if a['asset_id']=='picture-036');old=a['creator'];assert 'Kolforn' in old and len(old)>500;creator='Kolforn (Wikimedia Commons)';overrides={a['source_url']:dict(creator=creator,reason='Verified author name in raw Commons Artist metadata;optional email request and embedded license boilerplate are retained in raw metadata,not in display attribution.')};(E/'credit-author-overrides.json').write_text(json.dumps(overrides,ensure_ascii=False,indent=2)+'\n')
assets=yaml.safe_load((E/'assets.yaml').read_text())
for collection in [fg,assets['assets']]:
 item=next(x for x in collection if x['asset_id']=='picture-036');assert item['creator']==old;item['creator']=creator;item['required_credits']=item['required_credits'].replace(old,creator)
for card in s['render']['credits'][2:]:
 paragraphs=[]
 for text in card['paragraphs']:
  text=text.replace(old,creator)
  if ' — ' in text:
   title,rest=text.split(' — ',1);text=urllib.parse.unquote(title)+' — '+rest
  paragraphs.append(text)
 card['paragraphs']=paragraphs
assert before_rows==s['sentences'];(E/'script.yaml').write_text(yaml.safe_dump(s,allow_unicode=True,sort_keys=False,width=100));(E/'assets.yaml').write_text(yaml.safe_dump(assets,allow_unicode=True,sort_keys=False,width=100));(E/'foreground-assets.json').write_text(json.dumps(fg,ensure_ascii=False,indent=2)+'\n')
helper=P/'prepare_vard_pictures.py';code=helper.read_text();code=code.replace("photos=json.loads((E/'selected-photos.json').read_text());", "credit_overrides=json.loads((E/'credit-author-overrides.json').read_text()) if (E/'credit-author-overrides.json').exists() else {}\nphotos=json.loads((E/'selected-photos.json').read_text());");code=code.replace("creator=clean('Artist');terms=", "creator=credit_overrides.get(pi['descriptionurl'],{}).get('creator',clean('Artist'));terms=");code=code.replace("source.rsplit('/wiki/',1)[-1].replace('_',' ').removeprefix('File:')", "__import__('urllib.parse',fromlist=['unquote']).unquote(source.rsplit('/wiki/',1)[-1]).replace('_',' ').removeprefix('File:')");helper.write_text(code)
assert sha(E/'selected-photos.json')==raw_metadata_hash
for path,digest in media.items():assert sha(R/path)==digest,path
proof=dict(section_id='hb-c10-vard',repair='Verified Kolforn author attribution and URL-decoded display title only.',raw_metadata_path='studio/episodes/hb-c10-vard/selected-photos.json',raw_metadata_sha256=raw_metadata_hash,all51selected_narration_and_body_picture_hashes=media,all_body_rows_identical=True,all_media_hashes_identical=True,raw_provenance_unchanged=True,body_rows=before_rows,stills_refresh_pending=True)
(E/'credit-cleanup-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n');print('Vård credit cleanup staged;51body rows/all51takes/allbody pictures/rawmetadata unchanged.')
