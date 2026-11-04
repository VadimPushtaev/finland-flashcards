"""Summarize completed every-card reviews without changing episode media."""
from pathlib import Path
import json

R=Path(__file__).resolve().parents[3]
P=Path(__file__).resolve().parent
owned=json.loads((P/'worker-checkpoint.json').read_text())['exclusive_episodes']
rows=[]
for sid in owned:
    if sid in ['hb-c11-trafik','hb-c11-nodsituationer']:
        continue
    e=R/'studio/episodes'/sid
    path=e/'actual-export-review.json'
    if not path.exists():
        continue
    r=json.loads(path.read_text())
    c=json.loads((e/'render-check.json').read_text())
    assert r['reviewed'] and r['export_sha256']==c['sha256']
    rows.append(dict(section_id=sid,reviewed=True,cards=r['all_actual_decoded_frames'],
        simulated_phone_samples=len(r['simulated_phone_frames']),canonical_sha256=r['export_sha256']))
out=dict(scope='Current owned completed exports;all actual decoded title/body/credit cards and simulatedphone contacts visually inspected. No whole-video/listening/device/useracceptance claim.',
    episodes=rows,complete_episodes=len(rows),actual_cards=sum(r['cards']for r in rows),
    simulated_phone_samples=sum(r['simulated_phone_samples']for r in rows))
(P/'full-actual-export-review-checkpoint.json').write_text(json.dumps(out,indent=2)+'\n')
print(out['complete_episodes'],out['actual_cards'],out['simulated_phone_samples'])
