from pathlib import Path
import json
import hashlib
from collections import defaultdict
root=Path('studio/episodes')
results=[]
for path in sorted(root.glob('hb-c1*/picture-plan.json')):
 section=path.parent.name
 if section not in json.loads(Path('studio/production/remaining/tts-control.json').read_text())['sections']:continue
 plans=json.loads(path.read_text());media=json.loads((path.parent/'media-sources.json').read_text());groups=defaultdict(list)
 for key,plan in plans.items():
  photo=media.get('foreground_photos',{}).get(key)
  if photo:sig=('photo',photo['imageinfo'][0]['descriptionurl'])
  else:
   icons=tuple(({'bank':'court'}.get(n['icon'],n['icon']),bool(n.get('crossed'))) for n in plan['nodes'])
   composition=plan['composition'];composition={'split':'branch'}.get(composition,composition)
   if composition=='warning' and plan.get('conditions'):composition='plain_warning_positions'
   sig=(composition,icons,plan.get('connective') if composition in ['merge','branch'] else None,tuple(tuple(c['node_indices']) for c in plan.get('conditions',[])))
  groups[str(sig)].append(key)
 repeats=[keys for keys in groups.values() if len(keys)>1]
 record=dict(section_id=section,slides=len(plans),distinct_visible_structures=len(groups),ratio=len(groups)/len(plans),repeated_groups=repeats,
             picture_plan_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
             media_sources_sha256=hashlib.sha256((path.parent/'media-sources.json').read_bytes()).hexdigest())
 results.append(record);print(section,len(groups),'/',len(plans),repeats)
Path('studio/production/remaining/conservative-visible-diversity.json').write_text(json.dumps({'method':'Ignore labels and IDs; normalize bank/court architectural objects and branch/split layout aliases. Count actual diagram composition, objects, crossings, edges and condition attachment, or verified photo source identity. No claim that source identities alone establish relevance.','episodes':results},indent=2)+'\n')
