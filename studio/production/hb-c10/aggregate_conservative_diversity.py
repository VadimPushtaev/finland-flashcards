"""Aggregate human structural audits, never substitute file counts for assessment."""
from pathlib import Path
import hashlib
import json
import yaml

R=Path(__file__).resolve().parents[3]
P=Path(__file__).resolve().parent
owned=json.loads((P/'worker-checkpoint.json').read_text())['exclusive_episodes']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
method=('Conservative human review of visible objects,composition,edges,crossings and attached conditions. '
        'Ignore text,IDs,institution-role aliases,minor positioning,colours and alternate crops of one source. '
        'Exact source-picture/file uniqueness is reported separately and does not establish a distinct meaningful composition.')
for sid in owned:
    e=R/'studio/episodes'/sid
    s=yaml.load((e/'script.yaml').read_text(),Loader=yaml.CSafeLoader)
    n=len(s['sentences'])
    h=e/'production-handoff.json'
    if not h.exists():
        h=e/'prerender-handoff.json'
    handoff=json.loads(h.read_text())
    row=dict(section_id=sid,sentences=n,method=method,
        current_script_sha256=sha(e/'script.yaml'),current_assets_sha256=sha(e/'assets.yaml'),
        handoff=dict(path=str(h.relative_to(R)),sha256=sha(h)),
        distinct_source_pictures=handoff['distinct_pictures'],
        source_picture_fraction=handoff['distinct_picture_fraction']if 'distinct_picture_fraction'in handoff else handoff['distinct_pictures']/n,
        actual_export_review=(str((e/'actual-export-review.json').relative_to(R))if(e/'actual-export-review.json').exists()else None))
    audit=e/'visible-structure-audit.json'
    if audit.exists():
        a=json.loads(audit.read_text())
        row.update(assessment_status='assessed',distinct_meaningful_visible_compositions=a['distinct_visible_structures'],
            fraction=a['ratio'],repeated_groups=a['repeated_groups'],
            repeated_group_indexing=a.get('group_indexing','zero-based stored source order'),
            audit=dict(path=str(audit.relative_to(R)),sha256=sha(audit)),
            limits='Producer structural grouping;independent source/preflight review separate. Audit current inputs rebound by this aggregate,without changing geometry.')
    elif sid=='hb-c10-sjukdom':
        row.update(assessment_status='assessed',distinct_meaningful_visible_compositions=39,fraction=39/43,
            repeated_group_indexing='zero-based stored source order',
            repeated_groups=[dict(indices=[6,7,8,9,10],reason='One unchanged four-condition overview retained through source list introduction and four fragments;no distinctness claimed from changing right-panel text.')],
            limits='All50actual export cards inspected;39/43 conservative count from one five-slide unchanged overview,not a raw file-uniqueness inference.')
    else:
        row.update(assessment_status='not_separately_assessed',distinct_meaningful_visible_compositions=None,
            fraction=None,repeated_groups=None,
            limits='Source relevance and every actual exported card reviewed;separate conservative cross-composition grouping not completed. Do not interpret source-picture count as meaningful visible structure count.')
    rows.append(row)
assert len(rows)==18
out=dict(owner='/root/chapter10',episodes=rows,method=method,
    assessed_episodes=sum(r['assessment_status']=='assessed'for r in rows),
    unassessed_episodes=[r['section_id']for r in rows if r['assessment_status']!='assessed'],
    known_honest_exceptions=['Pension83/94','Äldre77/86','Läkemedel41/46'],
    no_cosmetic_changes=True,whole_video_listening=False,user_acceptance=False)
(P/'conservative-diversity-aggregate.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(len(rows),'episodes;',out['assessed_episodes'],'structurally assessed;',len(out['unassessed_episodes']),'explicitly unassessed.')
