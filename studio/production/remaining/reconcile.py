"""Reconcile actual producer milestones and verified local preview links."""
from collections import Counter
from pathlib import Path
import json
import re

import yaml

ROOT=Path(__file__).resolve().parents[3]


def stamp(seconds):
    value=round(seconds)
    return f'{value//3600}:{value//60%60:02d}:{value%60:02d}' if value>=3600 else f'{value//60}:{value%60:02d}'


def main():
    path=ROOT/'studio/episodes.yaml'
    inventory=yaml.safe_load(path.read_text())
    outputs=[]
    for entry in inventory['episodes']:
        if int(entry['chapter_id'][-2:])<8:continue
        episode=ROOT/'studio/episodes'/entry['section_id']
        brief_path=episode/'brief.yaml'
        if not brief_path.exists():continue
        brief=yaml.safe_load(brief_path.read_text())
        entry.update(production_status=brief['production_status'],episode_path=str(episode.relative_to(ROOT)),
                     translation_readiness='ready',issues=brief.get('issues',[]))
        if entry['production_status']!='preview_ready':continue
        report=json.loads((episode/'render.json').read_text())
        check=json.loads((episode/'render-check.json').read_text())
        coverage=json.loads((episode/'picture-coverage.json').read_text())
        if not report['sha256']==check['sha256']==coverage['export_sha256']:
            raise ValueError('Current export evidence does not match: '+entry['section_id'])
        video=ROOT/report['output']
        if not video.is_file() or not video.with_suffix('.CREDITS.md').is_file():
            raise ValueError('Missing canonical video or sidecar: '+entry['section_id'])
        outputs.append(dict(section_id=entry['section_id'],chapter_id=entry['chapter_id'],
            order=entry['section_order'],title=entry['title_sv'],seconds=report['seconds'],
            output=report['output'],sha256=report['sha256'],picture_fraction=coverage['picture_fraction'],
            pictured_slides=coverage['picture_sentences'],sentences=coverage['sentences']))
    path.write_text(yaml.safe_dump(inventory,allow_unicode=True,sort_keys=False,width=95))
    queue_path=ROOT/'studio/production/remaining/queue.yaml'
    queue=yaml.safe_load(queue_path.read_text())
    for row in queue['episodes']:
        entry=next(e for e in inventory['episodes'] if e['section_id']==row['section_id'])
        row['stage']=entry['production_status']
    queue_path.write_text(yaml.safe_dump(queue,allow_unicode=True,sort_keys=False))
    index=ROOT/'videos/homebrew/README.md'
    text=re.sub(r'(?ms)^## Chapter (?:8|9|10|11|12) —.*?(?=^## |\Z)','',index.read_text()).rstrip()+'\n'
    manifest=yaml.safe_load((ROOT/'data/homebrew/manifest.yaml').read_text())
    for chapter in manifest['chapters']:
        selected=[r for r in outputs if r['chapter_id']==chapter['id']]
        if not selected:continue
        source=yaml.safe_load((ROOT/'data/homebrew'/chapter['path']).read_text())
        number=int(chapter['id'][-2:])
        text+=f'\n## Chapter {number} — {source["title"]}\n\n'
        if len(selected)==len(source['sections']):
            text+='All local previews are available. Whole-video listening, physical-device playback and user acceptance remain pending.\n\n'
        else:
            text+='Production is in progress. These local previews await whole-video listening, physical-device playback and user acceptance.\n\n'
        text+='| Video and credits | Duration | Foreground pictures | Status |\n|---|---:|---:|---|\n'
        for row in sorted(selected,key=lambda r:r['order']):
            name=Path(row['output']).name
            credits=Path(name).with_suffix('.CREDITS.md').name
            text+=f'| [{number}.{row["order"]} {row["title"]}]({name}) · [credits]({credits}) | {stamp(row["seconds"])} | {row["picture_fraction"]:.0%}; {row["pictured_slides"]}/{row["sentences"]} slides | Ready for whole-video review |\n'
    index.write_text(text)
    selected=[e for e in inventory['episodes'] if int(e['chapter_id'][-2:])>=8]
    progress=dict(requested_episodes=len(selected),verified_previews=len(outputs),
        verified_seconds=sum(r['seconds'] for r in outputs),
        milestones=dict(Counter(e['production_status'] for e in selected)),
        outputs=outputs,whole_video_acceptance='Pending; technical checks and producer/peer reviews do not constitute user acceptance.')
    (ROOT/'studio/production/remaining/progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n')
    print(progress['verified_previews'],'/',progress['requested_episodes'],'verified local previews;',stamp(progress['verified_seconds']))


if __name__=='__main__':main()
