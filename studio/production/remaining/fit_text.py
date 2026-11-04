"""Choose among the studio's three permitted bilingual type sizes.

Source text is never rewritten. Oversized pairs are reported for manual,
audio-aligned segmentation instead of being made illegibly small.
"""
from pathlib import Path
import json
import sys

import yaml

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from studio.tools import render


def main(section):
    path=ROOT/'studio/episodes'/section/'script.yaml'
    script=yaml.safe_load(path.read_text())
    render.configure_style(script)
    selected=[]
    oversized=[]
    for row in script['sentences']:
        if row.get('display_segments'):
            continue
        for sv,ru in [(48,40),(44,36),(40,34)]:
            height=(len(render.wrap(row['sv'],render.font(sv,True),900))*round(sv*1.3125)
                    +len(render.wrap(row['ru'],render.font(ru),900))*round(ru*1.375)+56)
            if height<=750:
                row['text_style']=dict(sv_size=sv,ru_size=ru)
                selected.append(dict(sentence_id=row['sentence_id'],sv_size=sv,ru_size=ru,height=height))
                break
        else:
            oversized.append(row['sentence_id'])
    if oversized:
        raise ValueError('Manually align display segments: '+', '.join(oversized))
    path.write_text(yaml.safe_dump(script,allow_unicode=True,sort_keys=False,width=100))
    report=dict(section_id=section,selections=selected,source_text_changed=False,
                note='Typeface geometry check; actual full-size and phone previews require separate visual review.')
    (path.parent/'text-fit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(section,len(selected),'pairs fit within allowed 48/40,44/36,40/34 sizes')


if __name__=='__main__':main(sys.argv[1])
