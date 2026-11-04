"""Replace eleven unexported repeated structures with additional exact-source objects/relations."""
from pathlib import Path
import json,datetime,subprocess,os,yaml
ROOT=Path(__file__).resolve().parents[3];PY=ROOT/'studio/runtime/.venv/bin/python';PROD=ROOT/'studio/production/hb-c08'
def node(label,icon):return dict(label=label,icon=icon)
work={
'hb-c08-vuxna':{
5:dict(composition='threeways',nodes=[node('läs- och skrivkunnighet','book'),node('finska eller svenska och engelska','speech'),node('matematik','pencils')]),
38:dict(composition='applicationpath',nodes=[node('viss mängd studier','book'),node('separat ansökan','document'),node('hel examen','diploma')],qualifier='Inom vissa områden'),
58:dict(composition='threeways',nodes=[node('grundexamen','diploma'),node('yrkesexamen','diploma'),node('specialyrkesexamen','diploma')]),
54:dict(composition='tools',nodes=[node('yrkesfärdigheterna','gear'),node('företagarfärdigheterna','business')])},
'hb-c08-finansiering':{
7:dict(composition='threeways',nodes=[node('studiepenningen','coins'),node('statsborgen för studielån','bank'),node('bostadstillägg','house')]),
48:dict(composition='threeways',nodes=[node('något annat land','globe'),node('uppehållstillstånd för studerande','document'),node('rätt att arbeta','work')],qualifier='på vissa villkor'),
53:dict(composition='applicationpath',nodes=[node('deltidsarbete','work'),node('finansierar','coins'),node('sina studier','book')],qualifier='Det är vanligt')},
'hb-c12-tjanster':{
34:dict(composition='needs_branch',nodes=[node('varje deltagares behov','adult'),node('omkring ett år','calendar'),node('omfattning och innehåll','book')]),
39:dict(composition='needs_branch',nodes=[node('finländsk arbetsplats','work'),node('språket bättre','speech'),node('yrkeskompetens','gear')])},
'hb-c12-egna-arenden':{13:dict(composition='cumulative',nodes=[node('låter bli att korrigera fel','document'),node('inte meddelar en inkomst','coins'),node('straffbar handling','court')],qualifier='kan man göra sig skyldig')},
'hb-c12-e-tjanster':{19:dict(composition='threeways',nodes=[node('öppnar ett bankkonto','bank'),node('fråga','speech'),node('koderna','lock')],qualifier='I allmänhet')}
}
audit=[]
for sid,changes in work.items():
 ep=ROOT/'studio/episodes'/sid;p=ep/'picture-plan.json';data=json.loads(p.read_text());script=yaml.safe_load((ep/'script.yaml').read_text());by={r['sentence_id']:r['sv'] for r in script['sentences']};keys=[]
 for n,change in changes.items():
  key=f'picture-{n:03d}';keys.append(key);before=json.loads(json.dumps(data[key]));text=' '.join(by[i] for i in data[key]['source_sentence_ids']).casefold()
  for obj in change['nodes']:assert obj['label'].casefold() in text,(sid,n,obj)
  if change.get('qualifier'):assert change['qualifier'].casefold() in text
  data[key].update(change);audit.append(dict(section_id=sid,picture=key,before=before,after=data[key]))
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');family='hb-c12a' if sid.startswith('hb-c12-') else 'hb-c08';env=dict(os.environ,PICTURE_KEYS=','.join(keys));subprocess.run([str(PY),str(PROD.parent/family/'pictures.py'),sid],cwd=ROOT,env=env,check=True)
 assetpath=ep/'assets.yaml'
 if assetpath.exists():
  d=yaml.safe_load(assetpath.read_text());fg={a['asset_id']:a for a in json.loads((ep/'foreground-assets.json').read_text())};d['assets']=[fg[a['asset_id']] if a['asset_id'] in keys else a for a in d['assets']];assetpath.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False))
 if (ROOT/'studio/media'/sid/'render/timeline.json').exists():
  subprocess.run([str(PY),str(PROD/'refresh_stills.py'),sid,*[str(n) for n in changes]],cwd=ROOT,check=True);subprocess.run([str(PY),'studio/tools/validate_assets.py',sid],cwd=ROOT,check=True)
 subprocess.run([str(PY),str(PROD.parent/family/'preflight.py'),sid.removeprefix('hb-c12-' if family=='hb-c12a' else 'hb-c08-')],cwd=ROOT,env=dict(os.environ,PREFLIGHT_INDICES=','.join(str(n-1) for n in changes)),check=True)
 print(datetime.datetime.now(datetime.timezone.utc).isoformat(),sid,'REFINED',keys,flush=True)
(PROD/'source-specific-refinements.json').write_text(json.dumps(dict(updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Eleven unexported pictures only, adding source-specific objects and logical relationships; no source text, reviewed Russian, existing take or exported video changed.',changes=audit),ensure_ascii=False,indent=2)+'\n')
