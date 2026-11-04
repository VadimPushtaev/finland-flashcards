"""Bind all eighteen owned verified previews and current review evidence."""
from pathlib import Path
import hashlib
import json
import yaml

R=Path(__file__).resolve().parents[3]
P=Path(__file__).resolve().parent
owned=json.loads((P/'worker-checkpoint.json').read_text())['exclusive_episodes']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for sid in owned:
    e=R/'studio/episodes'/sid
    s=yaml.load((e/'script.yaml').read_text(),Loader=yaml.CSafeLoader)
    b=yaml.safe_load((e/'brief.yaml').read_text())
    h=json.loads((e/'production-handoff.json').read_text())
    r=json.loads((e/'render.json').read_text())
    v=json.loads((e/'render-check.json').read_text())
    a=json.loads((e/'actual-export-review.json').read_text())
    c=json.loads((e/'picture-coverage.json').read_text())
    d=json.loads((e/'visible-structure-audit.json').read_text()) if(e/'visible-structure-audit.json').exists()else None
    assert b['production_status']==h['status']=='preview_ready'
    assert a['reviewed'] and a['export_sha256']==h['sha256']==r['sha256']==v['sha256']
    assert v['full_decode']=='passed'and c['picture_fraction']==1
    assert c['script_sha256']==sha(e/'script.yaml')and c['assets_sha256']==sha(e/'assets.yaml')
    rows.append(dict(section_id=sid,desired_inventory_status='preview_ready',output=r['output'],
        seconds=r['seconds'],sha256=r['sha256'],sentences=len(s['sentences']),
        picture_timeline_fraction=1,distinct_source_pictures=h['distinct_pictures'],
        conservative_visible_compositions=d['distinct_visible_structures']if d else h['conservative_visible_structures'],
        conservative_visible_fraction=d['ratio']if d else h['conservative_visible_fraction'],
        actual_decoded_cards_reviewed=a['all_actual_decoded_frames'],simulated_phone_samples=len(a['simulated_phone_frames']),
        technical_audio_correlation=v['encoded_audio_matches_mix']['correlation'],
        handoff=str((e/'production-handoff.json').relative_to(R)),handoff_sha256=sha(e/'production-handoff.json'),
        current_hashes={n:sha(e/n)for n in ['script.yaml','assets.yaml','sources.yaml','CREDITS.md']},
        whole_video_listening=False,physical_device_playback=False,user_acceptance=False))
assert len(rows)==18
out=dict(owner='/root/chapter10',owned_episodes=18,all_verified_previews=True,
    source_pairs=sum(r['sentences']for r in rows),seconds=sum(r['seconds']for r in rows),
    all_actual_decoded_cards_reviewed=sum(r['actual_decoded_cards_reviewed']for r in rows),
    simulated_phone_samples=sum(r['simulated_phone_samples']for r in rows),episodes=rows,
    diversity_aggregate='studio/production/hb-c10/conservative-diversity-aggregate.json',
    actual_review_aggregate='studio/production/hb-c10/full-actual-export-review-checkpoint.json',
    encoder_release='studio/production/hb-c10/final-encoder-release-proof.json',
    transferred_episodes=dict(traffic='/root/chapter08',emergency='/root/chapter09a'),
    tts_asr='All owned selected narration and current diagnostics complete,preserved and allocations released;no more media jobs.',
    chapter_audit='studio/hb-c10-audit.json',whole_video_listening=False,
    physical_device_playback=False,user_acceptance=False,commit=False,upload=False)
(P/'final-owned-handoff.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(len(rows),'previews;',out['source_pairs'],'pairs;',out['seconds'],'seconds;',out['all_actual_decoded_cards_reviewed'],'actual cards.')
