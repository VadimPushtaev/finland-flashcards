"""Rebind stale picture reports after documented metadata-only script notes."""
from pathlib import Path
import hashlib
import json
import shutil
import sys

R=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(R))
from studio.tools.picture_coverage import build_report
from studio.production.remaining.picture_diversity import report

P=Path(__file__).resolve().parent
owned=json.loads((P/'worker-checkpoint.json').read_text())['exclusive_episodes']
rows=[]
for sid in owned:
    if sid in ['hb-c11-trafik','hb-c11-nodsituationer']:
        continue
    e=R/'studio/episodes'/sid
    if not (e/'actual-export-review.json').exists():
        continue
    render=json.loads((e/'render.json').read_text())
    review=json.loads((e/'actual-export-review.json').read_text())
    assert review['export_sha256']==render['sha256']
    coverage=e/'picture-coverage.json'
    rev=e/'revisions/before-picture-report-rebind'
    old=json.loads(coverage.read_text())
    new=build_report(sid)
    existing_diversity=json.loads((e/'picture-diversity.json').read_text())
    diversity_current=(existing_diversity.get('script_sha256')==new['script_sha256']
                       and existing_diversity.get('assets_sha256')==new['assets_sha256']
                       and existing_diversity.get('export_sha256')==render['sha256'])
    if old==new and diversity_current and not(rev/'picture-coverage.json').exists():
        continue
    if (rev/'picture-coverage.json').exists():
        old=json.loads((rev/'picture-coverage.json').read_text())
    same=lambda d:{k:v for k,v in d.items()if k not in ['script_sha256','assets_sha256','export_sha256']}
    assert old.get('export_sha256')==new['export_sha256']==render['sha256']
    assert same(old)==same(new),(sid,'Substantive coverage change;do not silently rebind')
    rev.mkdir(parents=True,exist_ok=True)
    for name in ['picture-coverage.json','picture-diversity.json']:
        if (e/name).exists()and not(rev/name).exists():
            shutil.copyfile(e/name,rev/name)
    coverage.write_text(json.dumps(new,indent=2)+'\n')
    previous=json.loads((rev/'picture-diversity.json').read_text())
    current=report(sid)
    assert previous.get('export_sha256')in[None,render['sha256']]
    assert current['export_sha256']==render['sha256']
    assert same(previous)==same(current),(sid,'Substantive diversity change;original retained')
    rows.append(dict(section_id=sid,old_script_sha256=old['script_sha256'],current_script_sha256=new['script_sha256'],
        previous_diversity_script_sha256=previous['script_sha256'],
        coverage_measures_unchanged=True,picture_diversity_unchanged=True,canonical_sha256=render['sha256'],
        earlier_diversity_was_planned_without_export_hash=previous.get('export_sha256')is None,
        current_coverage_sha256=hashlib.sha256(coverage.read_bytes()).hexdigest()))
out=dict(reason='Documented adaptation/source preparation metadata notes changed script hashes only;recalculate current picture reports against unchanged measured export timeline. Original reports retained. No script/assets/picture/audio/MP4 writes.',episodes=rows)
(P/'picture-report-binding-refresh.json').write_text(json.dumps(out,indent=2)+'\n')
print('Rebound',len(rows),'metadata-only picture report fingerprints;all measures unchanged.')
