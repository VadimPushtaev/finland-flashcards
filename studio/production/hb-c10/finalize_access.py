"""Bind the verified patient-rights preview to its actual export and selected audio."""
from pathlib import Path
import json,yaml,hashlib
R=Path(__file__).resolve().parents[3];SID='hb-c10-tillgang';E=R/'studio/episodes'/SID;M=R/'studio/media'/SID
s=yaml.safe_load((E/'script.yaml').read_text());r=json.loads((E/'render.json').read_text());c=json.loads((E/'render-check.json').read_text());p=json.loads((E/'picture-coverage.json').read_text());d=json.loads((E/'picture-diversity.json').read_text());metrics=json.loads((M/'narration/metrics.json').read_text());asr={a['file']:a for a in json.loads((M/'narration/asr.json').read_text())}
assert r['sha256']==c['sha256']==hashlib.sha256((R/r['output']).read_bytes()).hexdigest();assert c['full_decode']=='passed' and p['picture_fraction']==1 and len(metrics)==len(s['sentences'])==32
for a,b in zip(metrics,s['sentences']):assert a['sentence_id']==b['sentence_id'] and hashlib.sha256((R/a['path']).read_bytes()).hexdigest()==asr[a['path']]['sha256']
report=dict(section_id=SID,status='preview_ready',output=r['output'],seconds=r['seconds'],sha256=r['sha256'],source_section_sha256=s['source_section_sha256'],translation_file_sha256=s['translation_file_sha256'],pairs=32,selected_narration_clips=32,current_asr_hashes=32,actual_body_picture_fraction=1,distinct_pictures=30,photographs=10,original_diagrams=20,distinct_picture_fraction=30/32,full_decode='passed',decoded_video_frames=c['decoded_video_frames'],encoded_audio_correlation=c['encoded_audio_matches_mix']['correlation'],sampled_export_frames=['export-frame-07.png','export-frame-16.png','export-frame-19.png','export-frame-33.png'],phone_preview='640x360 resized actual exported long-pair frame07 inspected;no physical device playback',source_fidelity_notes=['Full32source/current reviewed Russian pairs preserved in stored order,default48/40.','Uncertain home-municipality situation points to DVV;no invented origin-country entitlement policy.','Missed-appointment fee is gated by missed AND not cancelled;under18 asylum example retains BOTH conditions.','Two meaningful continuations retain their images:emergency-care access/cost and consent/before-care.','Ten actual source photographs and20individually composed diagrams;no actual person assigned diagnosis,immigration status or entitlement.','Actual source card includes InfoFinland and orientation-guide publishers derived from sources.yaml.'],whole_video_listening=False,physical_device_playback=False,user_acceptance=False,issues=['Whole-video pronunciation and voice/music balance require listening;Finnish agency names flagged for attention.'])
(E/'production-handoff.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');b=yaml.safe_load((E/'brief.yaml').read_text());b.update(production_status='preview_ready',output_path=r['output'],issues=report['issues']+['Technically verified preview;whole-video user acceptance pending.']);(E/'brief.yaml').write_text(yaml.safe_dump(b,allow_unicode=True,sort_keys=False,width=100))
(E/'review.md').write_text(f'''# Episode review

Section ID: {SID}

Producer/date: Chapter10 worker,2026-11-03.

Preview: `{r['output']}` — {r['seconds']:.3f}seconds,1920×1080/24fps.

- [x] All32exact Swedish sentences and current reviewed Russian records retained once in stored order;current ready source validation passes.
- [x] All32selected local F1 WAV hashes match current filename-keyed ASR records;actual synthesis inputs and invocation metrics retained. ASR is diagnostic only.
- [x] All preflight pictures and bilingual stills inspected. Actual exported long DVV-name pair07,missed-AND-not-cancelled pair16,under18-AND-asylum example19,and source publisher card33 inspected without clipping.
- [x] A640×360 resized actual exported long-pair frame07 inspected;no physical device playback claimed.
- [x] Actual measured body picture coverage100%;30distinct pictures across32pairs,with10licensed photographs and20individually composed diagrams. Two direct source continuations retain useful pictures.
- [x] Source/photograph/music attribution retained in canonical sidecar;source card derives actual publishers from sources.yaml.
- [x] Complete export decode passed:{c['decoded_video_frames']}frames,{c['decoded_audio_seconds']}seconds audio. Encoded mix correlation{c['encoded_audio_matches_mix']['correlation']:.6f}. Timeline,mix and continuous background motion checks bind to the current export hash.
- [ ] Whole-video pronunciation/accent and voice/music balance listened to.
- [ ] Headphone/speaker checks or physical phone/laptop playback.
- [ ] Complete video watched/heard end to end and accepted by user.

Finnish agency names require whole-video listening. No new origin-country eligibility policy,fee,booking time,medical diagnosis or legal exception has been added. No photographed person is assigned immigration status,illness or entitlement.

Export SHA-256:`{r['sha256']}`. No commit or upload.
''');print(json.dumps(report,ensure_ascii=False))
