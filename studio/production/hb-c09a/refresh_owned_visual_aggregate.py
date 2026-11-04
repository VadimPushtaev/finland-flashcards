"""Bind current 26 owned picture-composition counts; labels never prove uniqueness."""
from pathlib import Path
import hashlib,json,time,yaml
from audit_visual_identities import audit,signature,ALIASES
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
report={'at':time.time(),'method':'Per-episode foreground photographs use primary source identity. Diagrams normalize glyph aliases and actual edge styles; labels, titles, source IDs and PNG hashes do not establish uniqueness. Actual four/six-node emergency grids use their visible arrangement. These counts supplement source-specific visual review and do not measure playback duration.','episodes':{}}
for ep in sorted((ROOT/'studio/episodes').glob('hb-c09-*')):
    row=audit(ep.name);row['script_sha256']=hashlib.sha256((ep/'script.yaml').read_bytes()).hexdigest();row['assets_sha256']=hashlib.sha256((ep/'assets.yaml').read_bytes()).hexdigest();report['episodes'][ep.name]=row
section='hb-c11-nodsituationer';ep=ROOT/'studio/episodes'/section;script=yaml.safe_load((ep/'script.yaml').read_text());plan=json.loads((ep/'visual-plan.json').read_text());assets=json.loads((ep/'foreground-assets.json').read_text());by_path={f['path']:a for a in assets for f in a['files']};groups={};photos=0
for index,(sentence,spec) in enumerate(zip(script['sentences'],plan),1):
    asset=by_path[sentence['render_image']]
    if asset['visual_type']=='photograph':identity='photo:'+asset['source_url'];photos+=1
    elif len(spec['objects'])>3:identity=json.dumps({'objects':[ALIASES.get(k,k) for k,label in spec['objects']],'layout':'grid2x2' if len(spec['objects'])==4 else 'grid3x2','edges':[]},sort_keys=True)
    else:identity=signature(spec)
    groups.setdefault(identity,[]).append(index)
report['episodes'][section]={'sentences':len(plan),'photographs':photos,'distinct_visible_identities':len(groups),'fraction':len(groups)/len(plan),'repeated_sentence_groups':[v for v in groups.values() if len(v)>1],'script_sha256':hashlib.sha256((ep/'script.yaml').read_bytes()).hexdigest(),'assets_sha256':hashlib.sha256((ep/'assets.yaml').read_bytes()).hexdigest()}
assert len(report['episodes'])==26 and sum(r['sentences'] for r in report['episodes'].values())==1132
assert all(row['fraction']>=.9 for row in report['episodes'].values())
(HERE/'conservative-owned-visual-diversity.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Current26 owned sections bound;1132 source pairs; Nods48/49; all per-episode fractions>=90%.')
