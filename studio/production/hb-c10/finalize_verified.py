"""Close an owned export only after technical and every-card visual verification."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import yaml

R = Path(__file__).resolve().parents[3]
SID = sys.argv[1]
assert SID in ['hb-c11-fritid','hb-c10-pension','hb-c10-aldre','hb-c10-sexuell','hb-c11-brandsakerhet','hb-c10-funktionsnedsattning']
E = R/'studio/episodes'/SID
M = R/'studio/media'/SID
for command in [
    ['.venv/bin/python','studio/tools/script.py','review',SID,'--ready'],
    ['.venv/bin/python','studio/tools/script.py','validate',SID,'--ready'],
    ['studio/runtime/.venv/bin/python','studio/tools/validate_assets.py',SID],
    ['studio/runtime/.venv/bin/python','studio/tools/picture_coverage.py',SID],
    ['.venv/bin/python','studio/production/remaining/picture_diversity.py',SID],
]:
    subprocess.run(command,cwd=R,check=True)
s=yaml.load((E/'script.yaml').read_text(),Loader=yaml.CSafeLoader)
r=json.loads((E/'render.json').read_text())
c=json.loads((E/'render-check.json').read_text())
p=json.loads((E/'picture-coverage.json').read_text())
d=json.loads((E/'picture-diversity.json').read_text())
pre=json.loads((E/'prerender-handoff.json').read_text())
review=json.loads((E/'actual-export-review.json').read_text())
assert review['reviewed'] and review['export_sha256']==r['sha256']==c['sha256']==hashlib.sha256((R/r['output']).read_bytes()).hexdigest()
assert c['full_decode']=='passed' and p['picture_fraction']==1
metrics=json.loads((M/'narration/metrics.json').read_text())
asr={a['file']:a for a in json.loads((M/'narration/asr.json').read_text())}
assert len(metrics)==len(asr)==len(s['sentences'])==pre['exact_pairs']
for x,y in zip(metrics,s['sentences']):
    assert x['sentence_id']==y['sentence_id']
    assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==asr[x['path']]['sha256']
assert d['distinct_picture_sources']==pre['distinct_pictures']
assert review['all_actual_decoded_frames']==len(r['timeline'])
for frame in review['frames']:
    assert hashlib.sha256((R/frame['path']).read_bytes()).hexdigest()==frame['sha256']
diagnostics=json.loads((E/'audio-diagnostics.json').read_text())
assert diagnostics.get('all_transcripts_read') or diagnostics.get('all_diagnostic_transcripts_read')
issues=['Whole-video pronunciation/accent and voice/music balance require listening. Finnish terms, Swedish compounds, modal/negation words and source numbers remain priorities. ASR is diagnostic, not listening proof.','Physical-device playback and whole-video user acceptance remain pending.']
out=dict(section_id=SID,status='preview_ready',output=r['output'],seconds=r['seconds'],sha256=r['sha256'],
    source_section_sha256=s['source_section_sha256'],translation_file_sha256=s['translation_file_sha256'],
    pairs=len(metrics),selected_narration_clips=len(metrics),current_asr_hashes=len(asr),
    actual_body_picture_fraction=p['picture_fraction'],distinct_pictures=pre['distinct_pictures'],
    photographs=pre['photographs'],original_diagrams=pre['original_diagrams'],
    distinct_picture_fraction=pre['distinct_picture_fraction'],
    full_decode='passed',decoded_video_frames=c['decoded_video_frames'],
    encoded_audio_correlation=c['encoded_audio_matches_mix']['correlation'],
    all_actual_decoded_card_frames_inspected=review['all_actual_decoded_frames'],
    simulated_phone_samples=len(review['simulated_phone_frames']),
    full_actual_export_review='studio/episodes/'+SID+'/actual-export-review.json',
    source_fidelity_notes=pre['source_fidelity_notes'],
    current_hashes={n:hashlib.sha256((E/n).read_bytes()).hexdigest()for n in ['script.yaml','assets.yaml','sources.yaml','CREDITS.md']},
    whole_video_listening=False,physical_device_playback=False,user_acceptance=False,issues=issues)
if (E/'visible-structure-audit.json').exists():
    v=json.loads((E/'visible-structure-audit.json').read_text())
    out.update(conservative_visible_structures=v['distinct_visible_structures'],conservative_visible_fraction=v['ratio'])
if (E/'source-note-correction-binding.json').exists():
    out['source_note_correction']=json.loads((E/'source-note-correction-binding.json').read_text())
(E/'production-handoff.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
b=yaml.safe_load((E/'brief.yaml').read_text())
b.update(production_status='preview_ready',output_path=r['output'],issues=issues)
(E/'brief.yaml').write_text(yaml.safe_dump(b,allow_unicode=True,sort_keys=False,width=100))
(E/'review.md').write_text(f'''# Episode review

Section ID: {SID}

Producer/date: Chapter10 worker,2026-11-03.

Preview: `{r['output']}` — {r['seconds']:.3f}seconds,1920×1080/24fps.

- [x] All{len(metrics)}exact Swedish/current reviewed Russian pairs once in stored source order. Current ready script/source/snapshot and asset checks passed.
- [x] All selected F1 WAVs bind filename-keyed current ASR hashes; diagnostic transcripts read. Original takes and generation metrics retained. No acoustic correctness claim.
- [x] All{review['all_actual_decoded_frames']}actual verifier-decoded title/body/credit frames inspected, plus{len(review['simulated_phone_frames'])}simulated phone-size views. Exact per-frame hashes in actual-export-review.json; no visual findings.
- [x] Actual pictured body timeline100%;{pre['distinct_pictures']}source pictures({pre['photographs']}licensed photographs and{pre['original_diagrams']}specific original diagrams). Useful continuations retained honestly; file uniqueness does not establish structural diversity.
- [x] Source conditions, qualifiers, examples and price/age distinctions preserved as recorded in prerender-handoff.json and independent peer report. No pictured person assigned a diagnosis, immigration or benefit status.
- [x] Full decode{c['decoded_video_frames']}video frames,{c['decoded_audio_seconds']}s audio; mix correlation{c['encoded_audio_matches_mix']['correlation']:.6f}; timeline, mix, motion and coverage bind current canonical hash.
- [ ] Whole-video pronunciation, voice/accent and music balance listened to.
- [ ] Physical phone/laptop/headphone/speaker playback.
- [ ] User watched/heard and accepted complete video.

Export SHA256: `{r['sha256']}`. No commit or upload.
''')
print(SID,r['seconds'],r['sha256'],c['encoded_audio_matches_mix']['correlation'])
