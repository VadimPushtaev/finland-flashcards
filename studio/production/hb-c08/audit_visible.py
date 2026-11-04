"""Conservative caption-independent audit of owned visual structures/source identities."""
from pathlib import Path
import json,collections,datetime
ROOT=Path(__file__).resolve().parents[3];IDS=['hb-c08-'+s for s in ['utveckling','smabarn','forskola','grundskola','stod','gymnasium','yrkesutbildning','hux','hogskolor','vuxna','finansiering']]+['hb-c12-'+s for s in ['integration','tjanster','sprak','tolkning','myndigheter','egna-arenden','personuppgifter','hemkommun','e-tjanster','norden-eu']]
alias={}
for name,words in [('path','path calendarpath year continuous autonomy change cause'),('social','meeting conversation team social class family'),('split','clock week day halfday contrast split balance grade gradeletters scale'),('arc','growth garden discovery tools language subjects globe lifelong'),('diagonal','meal materials municipality qualification obligation support choice exam merge')]:
 for word in words.split():alias[word]=name
results=[]
for sid in IDS:
 ep=ROOT/'studio/episodes'/sid;plans=json.loads((ep/'picture-plan.json').read_text());assets={a['asset_id']:a for a in json.loads((ep/'foreground-assets.json').read_text())};groups=collections.defaultdict(list)
 for key,spec in plans.items():
  a=assets[key]
  if a.get('visual_type') in ['photograph','flag']:sig=(a['visual_type'],a.get('source_url'),tuple(a.get('additional_source_urls',[])))
  else:
   c=spec['composition'];c='path' if sid.startswith('hb-c12-') and c=='bridge' else alias.get(c,c if c in ['influence','separate','threeways','twoway','applicationpath','needs_branch','cumulative'] else 'plain');sig=(c,tuple((n['icon'],bool(n.get('crossed'))) for n in spec['nodes']))
  groups[str(sig)].append(key)
 r=dict(section_id=sid,slides=len(plans),distinct_visible_structures=len(groups),ratio=len(groups)/len(plans),repeated_groups=[v for v in groups.values() if len(v)>1]);results.append(r);print(sid,f'{len(groups)}/{len(plans)}',round(r['ratio'],3))
(ROOT/'studio/production/hb-c08/conservative-visible-diversity.json').write_text(json.dumps({'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Ignore all labels/IDs/qualifier captions; normalize every actual geometry alias; count concrete objects/crossings/relations or verified photo/flag source identity. Strict proxy, not a relevance judgment.','episodes':results},indent=2)+'\n')
