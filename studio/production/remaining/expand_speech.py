"""Meaning-preserving letter/date readings before a root narration run starts."""
from pathlib import Path
import json
import re
import sys

import yaml

ROOT=Path(__file__).resolve().parents[3]
ABBREVIATIONS={'EU':'E U','EES':'E E S','FPA':'F P A','Fpa':'F P A',
               'UNHCR':'U N H C R','FRK':'F R K'}
DATES={'24.2.2022':'den tjugofjärde februari tvåtusentjugotvå',
       '1.4.2019':'den första april tvåtusennitton'}


def main(section):
    episode=ROOT/'studio/episodes'/section
    metrics=ROOT/'studio/media'/section/'narration/metrics.json'
    state=ROOT/'studio/production/remaining'/(section+'-tts-state.json')
    assert not metrics.exists(),'Do not change selected completed narration inputs.'
    assert not (state.exists() and json.loads(state.read_text()).get('status')=='running'),'Never change an active generation stream.'
    path=episode/'script.yaml';script=yaml.safe_load(path.read_text());changes=[]
    for row in script['sentences']:
        assert not row['speech_override'],'Review existing custom overrides explicitly.'
        text=row['sv']
        for source,spoken in ABBREVIATIONS.items():
            text=re.sub(r'\b'+re.escape(source)+r'\b',spoken,text)
        for source,spoken in DATES.items():
            text=text.replace(source,spoken)
        if text!=row['sv']:
            row['speech_override']=dict(text=text,
                reason='Speech-only Swedish letter-name spacing and unambiguous calendar-date expansion; displayed archived Swedish/Russian,values and conditions remain unchanged.',
                review_status='pending')
            changes.append(dict(sentence_id=row['sentence_id'],displayed_source=row['sv'],spoken_text=text))
    path.write_text(yaml.safe_dump(script,allow_unicode=True,sort_keys=False,width=100))
    (episode/'speech-expansions.json').write_text(json.dumps(dict(section_id=section,
        changes=changes,source_display_changed=False,whole_video_listening=False),ensure_ascii=False,indent=2)+'\n')
    print(section,len(changes),'meaning-preserving letter/date readings prepared')


if __name__=='__main__':main(sys.argv[1])
