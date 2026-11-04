"""Combine conservative visible-picture assessments with current input bindings."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import yaml
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'studio/production'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    queue=yaml.safe_load((BASE/'remaining/queue.yaml').read_text())['episodes'];rows=[]
    reports=[('hb-c08/conservative-visible-diversity.json','c8'),('hb-c09a/conservative-owned-visual-diversity.json','c9'),('hb-c10/conservative-diversity-aggregate.json','c10'),('remaining/conservative-visible-diversity.json','root'),('remaining/legacy-visible-diversity.json','legacy')]
    for rel,kind in reports:
        path=BASE/rel;report=json.loads(path.read_text());episodes=report['episodes'];episodes=[dict(section_id=k,**v) for k,v in episodes.items()]if isinstance(episodes,dict)else episodes
        for entry in episodes:
            sec=entry['section_id'];ep=ROOT/'studio/episodes'/sec
            if kind=='c10':n=entry['sentences'];count=entry['distinct_meaningful_visible_compositions'];groups=entry['repeated_groups']
            elif kind=='c9':n=entry['sentences'];count=entry['distinct_visible_identities'];groups=entry['repeated_sentence_groups']
            else:n=entry['slides'];count=entry['distinct_visible_structures'];groups=entry['repeated_groups']
            assert isinstance(count,int)and 0<count<=n,sec
            bindings=entry.get('bindings',{})
            for binding in bindings.values():assert binding['sha256']==digest(ROOT/binding['path']),'Stale explicit diversity binding '+sec
            helper=entry.get('actual_drawing_helper')
            if helper:assert helper['sha256']==digest(ROOT/helper['path']),'Changed drawing helper '+sec
            for field,name in [('script_sha256','script.yaml'),('current_script_sha256','script.yaml'),('assets_sha256','assets.yaml'),('current_assets_sha256','assets.yaml'),('picture_plan_sha256','picture-plan.json'),('media_sources_sha256','media-sources.json')]:
                if field not in entry:continue
                if field=='picture_plan_sha256' and bindings:
                    plans=[v for k,v in bindings.items()if k in ['picture-plan.json','picture-implementation.json']]
                    assert len(plans)==1 and entry[field]==plans[0]['sha256'],'Ambiguous plan binding '+sec
                else:assert entry[field]==digest(ep/name),'Stale diversity input '+sec+' '+field
            rows.append(dict(section_id=sec,sentences=n,distinct_meaningful_visible_compositions=count,fraction=count/n,repeated_groups=groups,method=entry.get('method',report.get('method')),assessment_path=str(path.relative_to(ROOT)),assessment_sha256=digest(path),script_sha256=digest(ep/'script.yaml'),assets_sha256=digest(ep/'assets.yaml')))
    ids=[r['section_id']for r in rows];wanted=[r['section_id']for r in queue];missing=sorted(set(wanted)-set(ids));assert len(ids)==len(set(ids)),'Duplicate episode assessment'
    n=sum(r['sentences']for r in rows);distinct=sum(r['distinct_meaningful_visible_compositions']for r in rows)
    report=dict(updated_utc=datetime.now(timezone.utc).isoformat(),assessed_episodes=len(rows),requested_episodes=88,missing=missing,assessed_body_pairs=n,distinct_compositions_summed_within_episodes=distinct,within_episode_diversity_fraction=distinct/n,episodes_below_90_percent=[r['section_id']for r in rows if r['fraction']<.9],episodes=rows,limits='Counts are conservative assessments of meaningful visible compositions within each episode. Ignore filenames,hashes,labels,colour and minor positions; each method records additional normalized aliases. This is not global cross-episode uniqueness. Relevant recurring diagrams and cross-episode photo reuse are preserved and reported honestly. All body-picture coverage is checked separately against measured timelines.')
    (BASE/'remaining/batch-visible-diversity.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(len(rows),'assessed;',n,'bodypairs;',distinct,'within-episode compositions;',f'{distinct/n:.2%}','missing',missing)
if __name__=='__main__':main()
