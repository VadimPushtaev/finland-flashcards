"""Measure fixed bilingual panel and record permitted per-pair font choices."""
from pathlib import Path
import sys,yaml,json
sys.path.insert(0,str(Path.cwd()/'studio/tools'));import render
for sid in sys.argv[1:]:
    ep=Path('studio/episodes')/sid;p=ep/'script.yaml';d=yaml.safe_load(p.read_text());render.configure_style(d);report=[]
    for row in d['sentences']:
        measurements=[]
        for sv,ru in [(48,40),(46,38),(44,36),(42,34),(40,34)]:
            height=len(render.wrap(row['sv'],render.font(sv,True),900))*round(sv*1.3125)+len(render.wrap(row['ru'],render.font(ru),900))*round(ru*1.375)+56
            measurements.append(dict(sv_size=sv,ru_size=ru,height=height))
            if height<=750:
                if (sv,ru)!=(48,40):row['text_style']={'sv_size':sv,'ru_size':ru}
                else:row.pop('text_style',None)
                break
        else:print('NEEDS MANUAL SEGMENTS',sid,row['sentence_id'],height,flush=True)
        report.append(dict(sentence_id=row['sentence_id'],measurements=measurements,selected=row.get('text_style',dict(sv_size=48,ru_size=40))))
    p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False,width=100));(ep/'layout-measurements.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(sid,'layout measured',len(report),'pairs',flush=True)
