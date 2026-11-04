"""Bind the welfare preview handoff to its verified export and preserved selected takes."""
from pathlib import Path
import json
import yaml
import hashlib
ROOT = Path(__file__).resolve().parents[3]
SID = 'hb-c10-valfard'
EP = ROOT / 'studio/episodes' / SID
MEDIA = ROOT / 'studio/media' / SID
script = yaml.safe_load((EP / 'script.yaml').read_text())
render = json.loads((EP / 'render.json').read_text())
check = json.loads((EP / 'render-check.json').read_text())
coverage = json.loads((EP / 'picture-coverage.json').read_text())
assert render['sha256'] == check['sha256'] == hashlib.sha256((ROOT / render['output']).read_bytes()).hexdigest()
assert coverage['picture_fraction'] == 1
metrics = json.loads((MEDIA / 'narration/metrics.json').read_text())
assert len(metrics) == 43
for row in metrics:
    wav = ROOT / row['path']
    asr = {r['file']: r for r in json.loads((wav.parent / 'asr.json').read_text())}
    assert asr[row['path']]['sha256'] == hashlib.sha256(wav.read_bytes()).hexdigest()
preservation = json.loads((EP / 'narration-preservation.json').read_text())
for row in preservation['selected_takes']:
    assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256']
report = dict(section_id=SID, status='preview_ready', output=render['output'],
              seconds=render['seconds'], sha256=render['sha256'],
              source_section_sha256=script['source_section_sha256'],
              translation_file_sha256=script['translation_file_sha256'], pairs=43,
              actual_body_picture_fraction=1, distinct_pictures=43, photographs=11,
              original_diagrams=32, full_decode='passed',
              encoded_audio_correlation=check['encoded_audio_matches_mix']['correlation'],
              sampled_export_frames=['export-frame-33.png', 'export-frame-40.png', 'export-frame-44.png'],
              planned_visual_review=['All 43 latest pictures including nine recomposed source diagrams',
                                     'Actual photos and primary source identities', 'Default or permitted long-pair text fits'],
              phone_preview='640x360 resized actual exported frame40 inspected; no physical device playback',
              narration_preservation='All 43 selected takes and ASR hashes rechecked. Initial 13 and first-resume 2 complete takes retained unchanged; missing-only durable chunks preserve actual invocation metadata.',
              whole_video_listening=False, physical_device_playback=False, user_acceptance=False,
              issues=['Whole-video pronunciation and voice/music balance need listening.',
                      'Archived source hb-c10-u0019-s003 contains the wording "kan du har rätt"; exact Swedish and reviewed Russian are retained under source-fidelity rules.'])
(EP / 'production-handoff.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
brief = yaml.safe_load((EP / 'brief.yaml').read_text())
brief.update(production_status='preview_ready', output_path=render['output'],
             issues=['Technically verified preview; whole-video listening and user acceptance pending.'] + report['issues'])
(EP / 'brief.yaml').write_text(yaml.safe_dump(brief, allow_unicode=True, sort_keys=False, width=100))
(EP / 'review.md').write_text(f'''# Episode review

Section ID: {SID}

Producer/date: Chapter 10 worker, 2026-11-03.

Preview: `{render['output']}` — 9:37.000 at 1920×1080/24 fps.

- [x] All 43 exact source sentences and current reviewed Russian records retained once, in stored order. Current heading-review and provenance checks pass.
- [x] All 43 selected local F1 clips retained with actual inputs, seed scopes, invocation settings and measured durations. Selected WAV hashes match current ASR records.
- [x] Original 13 complete takes and the first resume's two complete takes retained unchanged. Later durable missing-only chunks complete the same source sequence; no repeated speculative retakes or overwritten complete clips.
- [x] All 43 body cards fit at default or permitted long-pair sizes. Exported conditional permit and foreign-student pairs and the actual publisher-source card were inspected without clipping. A 640×360 resized actual export preview was inspected.
- [x] All 43 pictures are distinct and relevant: 11 licensed photographs and 32 individually composed source explanations. Nine schematic compositions were specifically recomposed during review to improve meaningful visual variety. Actual measured body picture coverage is 100%.
- [x] Qualitative comparisons add no numerical tax ratio, benefit sum, border, deadline or eligibility condition. Benefits diagrams retain source conditions and qualified outcomes.
- [x] Current source credits derive from sources.yaml and name both InfoFinland and orientation-guide publishers. Matching complete sidecar credits are retained.
- [x] Complete export decode passed: {check['decoded_video_frames']} frames, {check['decoded_audio_seconds']} seconds audio. Encoded mix correlation is {check['encoded_audio_matches_mix']['correlation']:.6f}.
- [x] Continuous opening/background-boundary motion checks passed and bind to the current export hash.
- [ ] Whole-video pronunciation/accent and voice/music balance listened to.
- [ ] Headphone/speaker checks or physical phone/laptop playback.
- [ ] Complete video watched/heard end to end and accepted by the user.

The archived source sentence `hb-c10-u0019-s003` contains “kan du har rätt”; its exact wording remains unchanged. This is a source wording issue, not a new subtitle or narration substitution.

Export SHA-256: `{render['sha256']}`. No commit or upload.
''')
print(json.dumps(report, ensure_ascii=False))
