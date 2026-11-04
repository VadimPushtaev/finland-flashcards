"""Reconcile archival photographer/collection credits against primary Finna records."""
from pathlib import Path
import json,re,subprocess,urllib.parse
ROOT=Path(__file__).resolve().parents[3];PROD=ROOT/'studio/production/hb-c12a';META={r['title']:r['imageinfo'][0] for p in PROD.glob('*.json') for r in json.loads(p.read_text()).get('query',{}).get('pages',{}).values() if r.get('imageinfo')};records={}
for ep in (ROOT/'studio/episodes').glob('hb-c12-*'):
 p=ep/'foreground-assets.json'
 if not p.exists() or not (ep/'photograph-plan.json').exists():continue
 assets=json.loads(p.read_text());changed=False
 for a in assets:
  if a.get('visual_type')!='photograph':continue
  pi=next(pi for pi in META.values() if pi['descriptionurl']==a['source_url']);m=pi['extmetadata'];raw=m.get('Credit',{}).get('value','');match=re.search(r'finna.fi/Record/([A-Za-z0-9_.:\-]+)',raw)
  if not match:continue
  ident=match.group(1);dest=PROD/('finna-'+ident+'.json');url='https://api.finna.fi/v1/record?id='+urllib.parse.quote(ident)
  if not dest.exists():subprocess.run(['curl','-4','-f','-sS','-L','--connect-timeout','15','--max-time','50',url,'-o',str(dest)],check=True)
  record=json.loads(dest.read_text())['records'][0];authors=[r.get('name','') for field in ('nonPresenterAuthors','presenters') for r in record.get(field,[]) if isinstance(r,dict)];authors=[x for x in authors if x];archive=list(dict.fromkeys(b['translated'] for b in record.get('buildings',[]) if b.get('translated')));assert archive,(ident,'Primary archive credit missing');named=re.sub('<[^>]+>','',m.get('Artist',{}).get('value','')).strip();creator=(named or '; '.join(authors) or 'Photographer not named in primary archive record')+'; '+', '.join(archive);a['creator']=creator;a['required_credits']=a['source_url'].rsplit('/',1)[-1].replace('_',' ').removeprefix('File:')+' — '+creator+'. '+a['reuse_terms']+'. Source: '+a['source_url']+'. Primary archive: https://finna.fi/Record/'+ident+'. Proportionally resized; complete photograph retained.';a['creation_method']['primary_archive_record']=str(dest.relative_to(ROOT));changed=True;records[a['source_url']]=dict(primary_record=url,authors=authors,archive=archive,license=record.get('imageRights'));print(ep.name,a['asset_id'],creator,flush=True)
 if changed:p.write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n')
(PROD/'archive-credit-evidence.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
