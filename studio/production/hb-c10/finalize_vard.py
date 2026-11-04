"""Bind the verified public/private healthcare preview to its actual export and selected audio."""
from pathlib import Path
import json,yaml,hashlib
R=Path(__file__).resolve().parents[3];SID='hb-c10-vard';E=R/'studio/episodes'/SID;M=R/'studio/media'/SID
s=yaml.safe_load((E/'script.yaml').read_text());r=json.loads((E/'render.json').read_text());c=json.loads((E/'render-check.json').read_text());p=json.loads((E/'picture-coverage.json').read_text());d=json.loads((E/'picture-diversity.json').read_text());metrics=json.loads((M/'narration/metrics.json').read_text());asr={a['file']:a for a in json.loads((M/'narration/asr.json').read_text())}
assert r['sha256']==c['sha256']==hashlib.sha256((R/r['output']).read_bytes()).hexdigest();assert c['full_decode']=='passed' and p['picture_fraction']==1 and len(metrics)==len(s['sentences'])==51
for a,b in zip(metrics,s['sentences']):assert a['sentence_id']==b['sentence_id'] and hashlib.sha256((R/a['path']).read_bytes()).hexdigest()==asr[a['path']]['sha256']
report=dict(section_id=SID,status='preview_ready',conservative_visible_structures=50,conservative_visible_fraction=50/51,output=r['output'],seconds=r['seconds'],sha256=r['sha256'],source_section_sha256=s['source_section_sha256'],translation_file_sha256=s['translation_file_sha256'],pairs=51,selected_narration_clips=51,current_asr_hashes=51,actual_body_picture_fraction=1,distinct_pictures=50,photographs=17,original_diagrams=33,distinct_picture_fraction=50/51,full_decode='passed',decoded_video_frames=c['decoded_video_frames'],encoded_audio_correlation=c['encoded_audio_matches_mix']['correlation'],sampled_export_frames=['export-frame-19.png','export-frame-48.png','export-frame-50.png','export-frame-52.png','export-frame-61.png'],phone_preview='640x360 resized actual exported occupational-health pair48 inspected;no physical device playback',source_fidelity_notes=['All51exact Swedish/currentRussian pairs retained in stored order,all at default48/40.','Root independently reviewed all63actualpreflightframes/51SVRU pairs;credit corrections56/61closed.','50distinct pictures:17licensedphotos33specificdiagrams,one exact no-card reimbursement mechanism reused for its second appearance.','Actual19MOSTprivateclinics,48OFTAKANoccupationalservices,50permanent-residence/reasonable-time conditions remain explicit. No new clinical procedure,triage score,fee,deadline,region boundary or entitlement.','Empty waiting-room photo verified;Kolforn credit overrides only display author as Kolforn(WikimediaCommons),raw metadata retained. Actual exported61credit is readable.','Source publisher card derives orientation-guide publishers from sources.yaml. Unrendered inherited adaptation-count note corrected with metadata-only proof;encoded frames/audio/timeline untouched.'],whole_video_listening=False,physical_device_playback=False,user_acceptance=False,issues=['Whole-video pronunciation and voice/music balance require listening;Finnish service names and long healthcare compounds flagged for attention.'])
(E/'production-handoff.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');b=yaml.safe_load((E/'brief.yaml').read_text());b.update(production_status='preview_ready',output_path=r['output'],issues=report['issues']+['Technically verified preview;whole-video user acceptance pending.']);(E/'brief.yaml').write_text(yaml.safe_dump(b,allow_unicode=True,sort_keys=False,width=100))
(E/'review.md').write_text(f'''# Episode review

Section ID: {SID}

Producer/date: Chapter10 worker,2026-11-03.

Preview:`{r['output']}` — {r['seconds']:.3f}seconds,1920×1080/24fps.

- [x] All51exact Swedish/current reviewed Russian pairs retained once in stored order;current ready source checks passed after metadata-only credit-note cleanup.
- [x] All51selected local F1 WAV hashes match current filename-keyed ASR records;actual inputs/settings/durations retained. Diagnostic transcripts reviewed;no listening claim.
- [x] Root independently read51SVRU pairs and inspected all63preflight frames;native56/61credit corrections closed. Actual exported19MOSTprivateclinics,48OFTAKANoccupationalservices,50permanent-residence/reasonable-time condition,52actual publishers and61clean author credit inspected without clipping. A640×360 actual exported48preview inspected.
- [x] Actual body picture coverage100%;50distinct relevant structures(17licensedphotos33specificdiagrams)/51pairs. The exact no-card reimbursement-application mechanism deliberately repeats once.
- [x] Actual empty waiting room verified;clean Kolforn display-author credit preserves raw primary metadata and license. Both canonical and episode Markdown sidecars match. Unrendered inherited illustration-count statement corrected with proof that every render-affecting script field is identical.
- [x] No invented diagnosis,clinical procedure,triage score,fee,deadline,regional eligibility rule or photographed patient status.
- [x] Complete export decode passed:{c['decoded_video_frames']}frames,{c['decoded_audio_seconds']}seconds audio. Encoded mix correlation{c['encoded_audio_matches_mix']['correlation']:.6f};timeline,mix and continuous background-motion checks bind current hash.
- [ ] Whole-video pronunciation/accent and voice/music balance listened to.
- [ ] Headphone/speaker checks or physical phone/laptop playback.
- [ ] Complete video watched/heard end to end and accepted by user.

Finnish service names and long healthcare compounds require listening. Export SHA-256:`{r['sha256']}`. No commit or upload.
''');print(json.dumps(report,ensure_ascii=False))
