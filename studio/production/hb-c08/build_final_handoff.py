"""Summarize the 22 owned, verified and actually frame-reviewed preview exports."""
from pathlib import Path
import datetime
import hashlib
import json

ROOT=Path(__file__).resolve().parents[3]
PROD=Path(__file__).parent
load=lambda path:json.loads(path.read_text())
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
binding=load(PROD/'current-export-binding-audit.json')
diversity=load(PROD/'conservative-visible-diversity.json')
assert binding['current_previews']==22 and binding['source_pairs']==987
assert not binding['pending_replacements']
assert len(diversity['episodes'])==22 and diversity['total_slides']==987
rows=[]
for row in binding['episodes']:
 sid=row['section_id'];ep=ROOT/'studio/episodes'/sid
 handoff=load(ep/'production-handoff.json');review=load(ep/'producer-export-review.json')
 actual_diversity=next(x for x in diversity['episodes'] if x['section_id']==sid)
 for filename in ['script.yaml','assets.yaml']:
  assert sha(ep/filename)==actual_diversity['bindings'][filename]['sha256']
 assert handoff['production_status']=='preview_ready' and handoff['picture_fraction']==1.0
 assert row['sha256']==review['export_sha256']
 rows.append(dict(**row,selected_wav_and_current_asr=handoff['source_sentences'],
  uncertain_asr_priorities=len(load(ep/'listening-priorities.json')['unresolved']),
  distinct_picture_sources=handoff['distinct_picture_sources'],photographs=handoff['photographed_slides'],
  conservative_visible_structures=actual_diversity['distinct_visible_structures'],
  conservative_visible_fraction=actual_diversity['ratio'],repeated_groups=actual_diversity['repeated_groups']))
source_order={item['section_id']:index for index,item in enumerate(diversity['episodes'])}
rows.sort(key=lambda row:source_order[row['section_id']])
chapter=load(PROD/'chapter-handoff.json')
chapter['updated_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
chapter['status']='all_11_verified_actual_export_reviewed_previews'
chapter['current_audit']='passed_after_two_picture_repair'
chapter.pop('pending_replacement',None)
chapter['episodes']=[]
for row in rows:
 if row['section_id'].startswith('hb-c08-'):
  h=load(ROOT/'studio/episodes'/row['section_id']/'production-handoff.json')
  h.update(actual_export_review=f"studio/episodes/{row['section_id']}/producer-export-review.json",
   uncertain_asr_priorities=row['uncertain_asr_priorities'],
   conservative_visible_structures=row['conservative_visible_structures'])
  chapter['episodes'].append(h)
chapter['limits']=['All593selectedWAV/currentASRchecks and all current actual-export still galleries reviewed per episode. No audio playback or whole-video listening.',
 'No physical-device playback/user acceptance/commit/upload. Keep every episode preview_ready.',
 'Final stricter geometric diversity audit ignores captions/colours/scale and collapses mirrored or aliased structures. Stöd107/133underthismethod; meaningful repeats retained honestly.']
(PROD/'chapter-handoff.json').write_text(json.dumps(chapter,ensure_ascii=False,indent=2)+'\n')
report=dict(completed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner='/root/chapter08',
 status='all_22_current_verified_and_actual_export_frame_reviewed_previews',
 episodes=rows,episode_count=22,source_pairs=987,selected_wav_and_current_asr=987,
 seconds=sum(x['seconds'] for x in rows),actual_export_frames_reviewed=sum(x['actual_reviewed_export_frames'] for x in rows),
 pictured_body_fraction=1.0,distinct_picture_sources=sum(x['distinct_picture_sources'] for x in rows),
 photographed_slides=sum(x['photographs'] for x in rows),
 conservative_visible_structures=sum(x['conservative_visible_structures'] for x in rows),
 conservative_method=diversity['method'],uncertain_asr_priorities=sum(x['uncertain_asr_priorities'] for x in rows),
 chapter8_audit=dict(path='studio/hb-c08-audit.json',sha256=sha(ROOT/'studio/hb-c08-audit.json')),
 source_note_correction='studio/production/remaining/source-note-correction.json',
 current_binding_audit=dict(path=str((PROD/'current-export-binding-audit.json').relative_to(ROOT)),sha256=sha(PROD/'current-export-binding-audit.json')),
 picture_audit=dict(path=str((PROD/'conservative-visible-diversity.json').relative_to(ROOT)),sha256=sha(PROD/'conservative-visible-diversity.json')),
 retained_revisions=['Språk redundant-background foreground repair','Stöd negative-context two-picture repair','Traffic025 meaningful car-object refinement','all original/selected narration takes and WAV-bound measured display-boundary evidence'],
 limitations=['No audio playback or whole-video listening, physical-device playback or user acceptance. Keep preview_ready.',
 'ASR diagnostics do not establish spoken fluency, pronunciation or accent; priorities remain for whole-video listening.',
 'Conservative picture structure counts are per episode, ignore captions/colours/scale and collapse mirrored/aliased geometry; meaningful recaps remain.',
 'No commits, pushes or uploads. All canonical MP4s and matching credits are local.'])
(PROD/'final-owned-handoff.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print({k:v for k,v in report.items() if k not in ['episodes','conservative_method']})
