"""Record the technically verified nature-access preview and honest review limits."""
from pathlib import Path
import json
import yaml
import hashlib
R = Path(__file__).resolve().parents[3]
SID = 'hb-c11-allemansratten'
E = R / 'studio/episodes' / SID
M = R / 'studio/media' / SID
script = yaml.safe_load((E / 'script.yaml').read_text())
render = json.loads((E / 'render.json').read_text())
check = json.loads((E / 'render-check.json').read_text())
coverage = json.loads((E / 'picture-coverage.json').read_text())
assert render['sha256'] == check['sha256'] == hashlib.sha256((R / render['output']).read_bytes()).hexdigest()
assert coverage['picture_fraction'] == 1
metrics = json.loads((M / 'narration/metrics.json').read_text())
asr = {row['file']: row for row in json.loads((M / 'narration/asr.json').read_text())}
assert len(metrics) == len(asr) == 21
for row in metrics:
    assert asr[row['path']]['sha256'] == hashlib.sha256((R / row['path']).read_bytes()).hexdigest()
report = dict(section_id=SID, status='preview_ready', output=render['output'], seconds=render['seconds'],
              sha256=render['sha256'], source_section_sha256=script['source_section_sha256'],
              translation_file_sha256=script['translation_file_sha256'], pairs=21,
              actual_body_picture_fraction=1, distinct_pictures=21, photographs=15,
              original_diagrams=6, full_decode='passed',
              encoded_audio_correlation=check['encoded_audio_matches_mix']['correlation'],
              sampled_export_frames=['export-frame-05.png', 'export-frame-20.png', 'export-frame-22.png'],
              planned_visual_review=['All 21 distinct pictures, including three clearer photo replacements',
                                     'Long camping pair at default 48/40', 'Corrected diagram footer spacing',
                                     'Actual source publishers from sources.yaml'],
              phone_preview='640x360 resized actual exported camping frame05 inspected; no physical device playback',
              whole_video_listening=False, physical_device_playback=False, user_acceptance=False,
              issues=['Whole-video Swedish compound pronunciation and voice/music balance require listening.'])
(E / 'production-handoff.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
b = yaml.safe_load((E / 'brief.yaml').read_text())
b.update(production_status='preview_ready', output_path=render['output'],
         issues=['Technically verified preview; whole-video listening and user acceptance pending.'])
(E / 'brief.yaml').write_text(yaml.safe_dump(b, allow_unicode=True, sort_keys=False, width=100))
(E / 'review.md').write_text(f'''# Episode review

Section ID: {SID}

Producer/date: Chapter 10/11 worker, 2026-11-03.

Preview: `{render['output']}` — 5:29.333 at 1920×1080/24 fps.

- [x] All 21 exact source sentences and current reviewed Russian records retained once, in stored order. Current heading-review and provenance checks pass.
- [x] All 21 local F1 clips retained with actual inputs/settings, measured durations, current WAV hashes and ASR diagnostics.
- [x] All planned body pairs fit at default 48/40. Actual exported camping, March–August/qualifier and publisher-source cards were inspected without clipping. A 640×360 resized actual export preview was inspected.
- [x] All 21 foreground pictures are distinct: 15 licensed nature/activity/object photographs and six individually composed source-based diagrams. Actual measured body picture coverage is 100%.
- [x] No invented camping distance, calendar day, edibility advice, protected-species rule, permission exception or municipal legal sign. The source's sufficient-distance and permitted-area qualifications remain exact.
- [x] Camping, fire and vehicle photographs are illustrative, not allegations of actual offences or evidence of site-specific permission. Winter photos never establish present ice safety. No photographed person is assigned a medical or immigration status.
- [x] Source credits derive from sources.yaml and correctly name both InfoFinland and orientation-guide publishers. Full matching sidecar credits retained.
- [x] Complete export decode passed: {check['decoded_video_frames']} frames, {check['decoded_audio_seconds']} seconds audio. Encoded mix correlation is {check['encoded_audio_matches_mix']['correlation']:.6f}.
- [x] Continuous opening/background-boundary motion checks passed and bind to the current export hash.
- [ ] Whole-video pronunciation/accent and voice/music balance listened to.
- [ ] Headphone/speaker checks or physical phone/laptop playback.
- [ ] Complete video watched/heard end to end and accepted by the user.

Export SHA-256: `{render['sha256']}`. No commit or upload.
''')
print(json.dumps(report, ensure_ascii=False))
