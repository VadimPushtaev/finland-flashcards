"""Audit current owned readiness without claiming unfinished whole-chapter acceptance."""
from pathlib import Path
import json,hashlib,time,yaml
from audit_visual_identities import audit
R=Path.cwd();H=R/'studio/production/hb-c09a';report={'at':time.time(),'scope':'C9 25 episodes; preflight readiness audit, not whole-video acceptance','episodes':{},'selected_clips':0,'preview_ready':0,'assets_ready':0}
for ep in sorted((R/'studio/episodes').glob('hb-c09-*')):
 sid=ep.name;s=yaml.safe_load((ep/'script.yaml').read_text());b=yaml.safe_load((ep/'brief.yaml').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=json.loads((R/'studio/media'/sid/'narration/metrics.json').read_text());a={Path(x['file']).stem:x for x in json.loads((R/'studio/media'/sid/'narration/asr.json').read_text())};assert len(m)==len(s['sentences']);assert [x['sentence_id'] for x in m]==[x['sentence_id'] for x in s['sentences']]
 for row,met in zip(s['sentences'],m):assert met['text']==(row.get('speech_override') or {}).get('text',row['sv']) and sha(R/met['path'])==a[met['sentence_id']]['sha256']
 preflight=ep/'producer-preflight-review.json';p=json.loads(preflight.read_text()) if preflight.exists() else {}
 if b['production_status']=='assets_ready':assert p['script_sha256']==sha(ep/'script.yaml') and p['assets_sha256']==sha(ep/'assets.yaml'),sid+' current preflight'
 v=audit(sid);assert v['fraction']>=.9;c=json.loads((ep/'picture-coverage-planned.json').read_text());assert c['picture_fraction']==1
 row={'status':b['production_status'],'selected_current_wav_asr':len(m),'all_timed_preflight_frames_reviewed':len(p.get('preflight_frames_inspected',{})),'conservative_composition_audit':v,'planned_picture_duration_fraction':c['picture_fraction'],'whole_video_listening':'pending','user_acceptance':False}
 if b['production_status']=='preview_ready':
  h=json.loads((ep/'production-handoff.json').read_text());r=json.loads((ep/'render.json').read_text());ck=json.loads((ep/'render-check.json').read_text());rv=json.loads((ep/'producer-export-review.json').read_text());assert h['export_sha256']==r['sha256']==ck['sha256']==rv['export_sha256'];assert rv['script_sha256']==sha(ep/'script.yaml') and rv['assets_sha256']==sha(ep/'assets.yaml'),sid+' current final review';assert len(rv['actual_export_frames_inspected'])==len(s['sentences'])+3;row.update(export_sha256=r['sha256'],full_decode=ck['full_decode'],actual_export_frames_reviewed=len(rv['actual_export_frames_inspected']),measured_export_picture_fraction=json.loads((ep/'picture-coverage.json').read_text())['picture_fraction'])
 else:
  assert b['production_status']=='assets_ready';f=json.loads((H/(sid.removeprefix('hb-c09-')+'-frozen-candidate.json')).read_text());assert f['script_sha256']==sha(ep/'script.yaml') and f['assets_sha256']==sha(ep/'assets.yaml') and f['narration_metrics_sha256']==sha(R/'studio/media'/sid/'narration/metrics.json') and f['preflight_review_sha256']==sha(ep/'producer-preflight-review.json');row['current_four_input_freeze']='passed'
 report['selected_clips']+=len(m);report[b['production_status']]+=1;report['episodes'][sid]=row;print(sid,'audit passed',flush=True)
assert len(report['episodes'])==25 and report['selected_clips']==1083
(H/'chapter-current-readiness-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('CURRENT',report['preview_ready'],'previews,',report['assets_ready'],'ready,1083 clips',flush=True)
