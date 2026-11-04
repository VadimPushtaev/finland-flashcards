"""Record the corrected verified public-health preview with preserved narration."""
from pathlib import Path
import json
import yaml
import hashlib
R = Path(__file__).resolve().parents[3]
SID = 'hb-c10-folkhalsa'
E = R / 'studio/episodes' / SID
M = R / 'studio/media' / SID
script = yaml.safe_load((E / 'script.yaml').read_text())
render = json.loads((E / 'render.json').read_text())
check = json.loads((E / 'render-check.json').read_text())
coverage = json.loads((E / 'picture-coverage.json').read_text())
assert render['sha256'] == check['sha256'] == hashlib.sha256((R / render['output']).read_bytes()).hexdigest()
assert coverage['picture_fraction'] == 1
proof = json.loads((E / 'wrap-correction-proof.json').read_text())
assert proof['new_export_sha256'] == render['sha256'], proof
assert proof['mix_bit_identical'] and proof['timeline_identical'], proof
metrics = json.loads((M / 'narration/metrics.json').read_text())
asr = {row['file']: row for row in json.loads((M / 'narration/asr.json').read_text())}
assert len(metrics) == len(asr) == 58
for row in metrics:
    assert asr[row['path']]['sha256'] == hashlib.sha256((R / row['path']).read_bytes()).hexdigest()
report = dict(section_id=SID,status='preview_ready',output=render['output'],seconds=render['seconds'],
              sha256=render['sha256'],source_section_sha256=script['source_section_sha256'],
              translation_file_sha256=script['translation_file_sha256'],pairs=58,
              actual_body_picture_fraction=1,distinct_pictures=53,photographs=14,original_diagrams=39,
              full_decode='passed',encoded_audio_correlation=check['encoded_audio_matches_mix']['correlation'],
              sampled_export_frames=['export-frame-43.png','export-frame-57.png','export-frame-59.png'],
              planned_visual_review=['All foreground pictures contact sheet','Rejected ambient thermometer and ground-shadow exercise images replaced accurately','Conditional vaccine gates','Actual orientation and InfoFinland publishers'],
              phone_preview='640x360 resized actual exported long bilingual pair43 inspected; no physical device playback',
              retained_picture_pairs=[[8,9],[37,38],[42,43],[51,52],[53,54]],pair_indexing='zero-based direct source continuations',
              whole_video_listening=False,physical_device_playback=False,user_acceptance=False,
              issues=['Whole-video pronunciation and voice/music balance require listening.'])
(E / 'production-handoff.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
b = yaml.safe_load((E / 'brief.yaml').read_text())
b.update(production_status='preview_ready',output_path=render['output'],issues=['Technically verified preview; whole-video listening and user acceptance pending.']+report['issues'])
(E / 'brief.yaml').write_text(yaml.safe_dump(b,allow_unicode=True,sort_keys=False,width=100))
(E / 'review.md').write_text(f'''# Episode review

Section ID: {SID}

Producer/date: Chapter 10 worker,2026-11-03.

Preview: `{render['output']}` — 11:15.333 at 1920×1080/24 fps.

- [x] All 58 exact source sentences and current reviewed Russian records retained once,in stored order. Current heading-review/provenance checks pass.
- [x] All 58 local F1 clips retained with actual inputs/settings,measured durations,current WAV hashes and ASR diagnostics.
- [x] All body text fits at default 48/40 except the long pair43 at permitted44/36. Actual exported long pair43,vaccine gate57 and publisher-source card59 were inspected. A640×360 resized actual export preview was inspected.
- [x] Relevant pictures cover every body sentence:53 distinct pictures for58 slides,14 licensed photographs and39 individually composed source diagrams. Five direct source continuations deliberately retain their useful picture. Actual measured body picture coverage is100%.
- [x] No photographed person is assigned a diagnosis,pregnancy,patient or benefit status. Buildings and foreign clinical/object photos are illustrative,without current named-site treatment promises.
- [x] No invented vaccine dose,age schedule,diagnosis,screening procedure or eligibility criterion. Permanent relocation AND missing vaccinations,and asylum/temporary protection plus minor OR pregnant conditions remain explicit.
- [x] Source credits derive from sources.yaml and correctly name InfoFinland and orientation-guide publishers. Full matching sidecar credits retained.
- [x] Complete export decode passed:{check['decoded_video_frames']} frames,{check['decoded_audio_seconds']} seconds audio. Encoded mix correlation is{check['encoded_audio_matches_mix']['correlation']:.6f}.
- [x] Continuous opening/background-boundary motion checks passed and bind to the current export hash.
- [ ] Whole-video pronunciation/accent and voice/music balance listened to.
- [ ] Headphone/speaker checks or physical phone/laptop playback.
- [ ] Complete video watched/heard end to end and accepted by the user.

Corrected image57: the vaccination label now wraps within its node border. Corrected actual export and phone-size still inspected. The previous complete preview and reports are retained under revisions/pre-node-wrap; exact timeline, all58 selected narration WAV hashes and bit-identical mixed audio are preserved in wrap-correction-proof.json.

Export SHA-256:`{render['sha256']}`. No commit or upload.
''')
print(json.dumps(report,ensure_ascii=False))
