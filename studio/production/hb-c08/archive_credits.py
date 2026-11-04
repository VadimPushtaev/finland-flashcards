"""Resolve credits directly from primary archive records when Commons lacks Artist."""
from pathlib import Path
import json,re,subprocess,urllib.parse
ROOT=Path(__file__).resolve().parents[3];PROD=ROOT/'studio/production/hb-c08';META={r['title']:r['imageinfo'][0] for p in (PROD/'research').glob('*.json') for r in json.loads(p.read_text()).get('query',{}).get('pages',{}).values() if r.get('imageinfo')};records={}
for ep in (ROOT/'studio/episodes').glob('hb-c08-*'):
 p=ep/'foreground-assets.json'
 if not p.exists():continue
 assets=json.loads(p.read_text());changed=False
 for a in assets:
  if a.get('visual_type')!='photograph' or a.get('creator'):continue
  pi=next(pi for pi in META.values() if pi['descriptionurl']==a['source_url']);m=pi['extmetadata'];clean=lambda k:re.sub('<[^>]+>','',str(m.get(k,{}).get('value',''))).strip();attribution=clean('Attribution');credit=clean('Credit')
  if attribution:
   a['creator']='Photographer not identified in retrieved metadata; required attribution: '+attribution
  elif 'finna.fi/Record/' in credit:
   ident=credit.split('/Record/',1)[1];dest=PROD/'research'/('finna-'+ident+'.json')
   if not dest.exists():subprocess.run(['curl','-4','-f','-sS','-L','--connect-timeout','15','--max-time','50','https://api.finna.fi/v1/record?id='+urllib.parse.quote(ident),'-o',str(dest)],check=True)
   record=json.loads(dest.read_text())['records'][0];authors=[r.get('name','') for r in record.get('nonPresenterAuthors',[]) if isinstance(r,dict)];authors+= [r.get('name','') for r in record.get('presenters',[]) if isinstance(r,dict)];authors=[x for x in authors if x];archive=list(dict.fromkeys(b['translated'] for b in record.get('buildings',[]) if b.get('translated')));a['creator']=('; '.join(authors) if authors else 'Photographer not named in primary archive record')+'; '+', '.join(archive);records[a['source_url']]=dict(primary_record=credit,record_path=str(dest.relative_to(ROOT)),authors=authors,archive=archive,license=record.get('imageRights'))
  else:raise ValueError('Credit needs source review: '+a['source_url'])
  a['required_credits']=a['source_url'].rsplit('/',1)[-1].replace('_',' ').removeprefix('File:')+' — '+a['creator']+'. '+a['reuse_terms']+'. Source: '+a['source_url']+'. Primary archive: '+credit+'. Proportionally resized; complete photograph retained.';a['relevance_verification']+=' Missing machine-readable photographer credit reconciled against explicit required attribution/primary archive record; no photographer name invented.';changed=True;print(ep.name,a['asset_id'],a['creator'],flush=True)
 if changed:p.write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n')
(PROD/'archive-credit-evidence.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
