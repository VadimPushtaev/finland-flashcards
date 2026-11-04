"""Record the fully checked library preview without implying listening/acceptance."""
from pathlib import Path
import json,hashlib,yaml
R=Path(__file__).resolve().parents[3];SID='hb-c11-bibliotek';E=R/'studio/episodes'/SID;M=R/'studio/media'/SID
s=yaml.safe_load((E/'script.yaml').read_text());r=json.loads((E/'render.json').read_text());c=json.loads((E/'render-check.json').read_text());coverage=json.loads((E/'picture-coverage.json').read_text());assert r['sha256']==c['sha256']==hashlib.sha256((R/r['output']).read_bytes()).hexdigest();assert coverage['picture_fraction']==1
metrics=json.loads((M/'narration/metrics.json').read_text());asr={a['file']:a for a in json.loads((M/'narration/asr.json').read_text())};assert len(metrics)==len(asr)==len(s['sentences'])==28
for a,b in zip(metrics,s['sentences']):assert a['sentence_id']==b['sentence_id'];assert asr[a['path']]['sha256']==hashlib.sha256((R/a['path']).read_bytes()).hexdigest()
report=dict(section_id=SID,status='preview_ready',output=r['output'],seconds=r['seconds'],sha256=r['sha256'],source_section_sha256=s['source_section_sha256'],translation_file_sha256=s['translation_file_sha256'],pairs=28,actual_body_picture_fraction=1,distinct_pictures=28,photographs=12,original_diagrams=16,full_decode='passed',encoded_audio_correlation=c['encoded_audio_matches_mix']['correlation'],sampled_export_frames=['export-frame-02.png','export-frame-13.png','export-frame-24.png','export-frame-28.png','export-frame-29.png'],visual_review=['All source photos and all37preflight title/body/credit stills','Source-identified reading-room replacements,attributed actual disc photo','Conditional time-limited card without Finnish identity code','Free-service diagram spacing','Guardian permission linked to child card','Actual InfoFinland publisher/source card','Actual exported frame02at640x360'],independent_preflight_review='studio/production/remaining/peer-review-hb-c11-bibliotek.json',whole_video_listening=False,physical_device_playback=False,user_acceptance=False,issues=['Whole-video pronunciation and voice/music balance require listening; compounds,ID-kort and personbeteckning flagged in audio-diagnostics.json.'])
(E/'production-handoff.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');b=yaml.safe_load((E/'brief.yaml').read_text());b.update(production_status='preview_ready',output_path=r['output'],issues=['Technically verified preview;whole-video listening and user acceptance pending.']+report['issues']);(E/'brief.yaml').write_text(yaml.safe_dump(b,allow_unicode=True,sort_keys=False,width=100))
(E/'review.md').write_text(f'''# Episode review

Section ID: {SID}

Producer/date: Chapter10/11 worker,2026-11-03.

Preview: `{r['output']}` — 5:50.292 at1920×1080/24fps.

- [x] All28exact archived Swedish/current reviewed Russian pairs retained once,in source order;source/heading/review/credit checks pass.
- [x] All28local F1 selected clips and actual input/settings/durations/hashes retained;all current ASR hashes checked and transcripts read diagnostically.
- [x] All28body pairs fit default48/40. All37preflight stills and actual exported02,13,24,28,29 inspected;actual exported02at640×360 inspected.
- [x] Pictures cover100%of measured actual body time:28distinct sources,12licensed actual photographs and16source-specific diagrams. No unchanged repeated body picture.
- [x] Source-identified reading rooms replace unsuitable circulation-area photos;an attributed actual DVD photo replaces a stylized unattributed disc icon. Books,computers,book bus,return machine and rooms identify their real categories.
- [x] Academic/special-library access remains qualified;no Finnish identity code leads to a time-limited card without invented duration;ordinary free services/card remain distinct from replacement/overdue fees;usual one-month loan and over80languages preserved;child card requires guardian permission.
- [x] Foreign game objects and Finnish university/library pictures are accurately identified,without relabelling a branch as the Multilingual Library or adding a current schedule/stock/entry guarantee.
- [x] Actual publisher card derives from sources.yaml and names InfoFinland;full matching sidecar attribution retained.
- [x] Independent preflight visual review passed in `{report['independent_preflight_review']}`. This does not replace export/listening review.
- [x] Complete export decode passed:{c['decoded_video_frames']}frames,{c['decoded_audio_seconds']}seconds audio. Actual mix correlation:{c['encoded_audio_matches_mix']['correlation']:.6f}. Stream,duration,timeline,sentence coverage and continuous background-motion checks pass,bound to current export hash.
- [ ] Whole-video pronunciation/accent and voice/music balance listened to.
- [ ] Physical phone/laptop playback or headphone/speaker checks.
- [ ] Complete end-to-end user review and acceptance.

Export SHA-256:`{r['sha256']}`. No commit or upload.
''');print(json.dumps(report,ensure_ascii=False))
