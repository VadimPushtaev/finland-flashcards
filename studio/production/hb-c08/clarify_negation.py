"""Clarify exact negative conditions in unexported source-specific pictures only."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys,yaml
ROOT=Path(__file__).resolve().parents[3];PY=ROOT/'studio/runtime/.venv/bin/python';PROD=ROOT/'studio/production/hb-c08'
work={'hb-c08-grundskola':{59:{0:dict(crossed=True),1:dict(label='eleverna',icon='children')},62:{0:dict(crossed=True),1:dict(label='eleverna',icon='children')}},'hb-c08-yrkesutbildning':{19:{1:dict(crossed=True)}},'hb-c08-vuxna':{34:{1:dict(icon='document',crossed=True)},44:{1:dict(crossed=True)}},'hb-c08-finansiering':{37:{0:dict(crossed=True)},39:{0:dict(crossed=True)}},'hb-c12-tjanster':{10:{1:dict(icon='adult',crossed=True)},54:{1:dict(crossed=True)}},'hb-c12-e-tjanster':{9:{0:dict(crossed=True)}},'hb-c12-norden-eu':{1:{1:dict(crossed=True)},5:{1:dict(crossed=True)},10:{1:dict(crossed=True)},16:{1:dict(crossed=True)}}}
audit=[]
for sid,rows in work.items():
 ep=ROOT/'studio/episodes'/sid;p=ep/'picture-plan.json';data=json.loads(p.read_text());keys=[f'picture-{n:03d}' for n in rows]
 for n,changes in rows.items():
  key=f'picture-{n:03d}';before=json.loads(json.dumps(data[key]));
  for i,change in changes.items():data[key]['nodes'][i].update(change)
  audit.append(dict(section_id=sid,picture=key,before=before,after=data[key]))
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');env=dict(os.environ,PICTURE_KEYS=','.join(keys));family='hb-c12a' if sid.startswith('hb-c12-') else 'hb-c08';subprocess.run([str(PY),str(PROD.parent/family/'pictures.py'),sid],cwd=ROOT,env=env,check=True)
 assets=ep/'assets.yaml'
 if assets.exists():
  d=yaml.safe_load(assets.read_text());by={a['asset_id']:a for a in json.loads((ep/'foreground-assets.json').read_text())};d['assets']=[by[a['asset_id']] if a['asset_id'] in keys else a for a in d['assets']];assets.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False))
 if sid=='hb-c08-grundskola':
  with (PROD/(sid+'-negation-stills.log')).open('w') as h:subprocess.run([str(PY),'studio/tools/render.py',sid,'--stills-only'],cwd=ROOT,stdout=h,stderr=subprocess.STDOUT,check=True)
  subprocess.run([str(PY),'studio/tools/validate_assets.py',sid],cwd=ROOT,check=True)
 elif family=='hb-c08':subprocess.run([str(PY),str(PROD/'preflight.py'),sid.removeprefix('hb-c08-')],cwd=ROOT,env=dict(os.environ,PREFLIGHT_INDICES=','.join(str(n-1) for n in rows)),check=True)
 else:subprocess.run([str(PY),str(PROD.parent/family/'preflight.py'),sid.removeprefix('hb-c12-')],cwd=ROOT,check=True)
 print(datetime.datetime.now(datetime.timezone.utc).isoformat(),sid,'clarified',keys,flush=True)
(PROD/'negation-clarifications.json').write_text(json.dumps(dict(updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Unexported pictures only; no sentence, audio or already exported video changed.',changes=audit),ensure_ascii=False,indent=2)+'\n')
