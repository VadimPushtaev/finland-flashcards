"""Bind the verified medicine/oral-care preview to its actual export and selected audio."""
from pathlib import Path
import json,yaml,hashlib
R=Path(__file__).resolve().parents[3];SID='hb-c10-lakemedel';E=R/'studio/episodes'/SID;M=R/'studio/media'/SID
s=yaml.safe_load((E/'script.yaml').read_text());r=json.loads((E/'render.json').read_text());c=json.loads((E/'render-check.json').read_text());p=json.loads((E/'picture-coverage.json').read_text());d=json.loads((E/'picture-diversity.json').read_text());metrics=json.loads((M/'narration/metrics.json').read_text());asr={a['file']:a for a in json.loads((M/'narration/asr.json').read_text())}
assert r['sha256']==c['sha256']==hashlib.sha256((R/r['output']).read_bytes()).hexdigest();assert c['full_decode']=='passed' and p['picture_fraction']==1 and len(metrics)==len(s['sentences'])==46
for a,b in zip(metrics,s['sentences']):assert a['sentence_id']==b['sentence_id'] and hashlib.sha256((R/a['path']).read_bytes()).hexdigest()==asr[a['path']]['sha256']
report=dict(section_id=SID,status='preview_ready',conservative_visible_structures=41,conservative_visible_fraction=41/46,output=r['output'],seconds=r['seconds'],sha256=r['sha256'],source_section_sha256=s['source_section_sha256'],translation_file_sha256=s['translation_file_sha256'],pairs=46,selected_narration_clips=46,current_asr_hashes=46,actual_body_picture_fraction=1,distinct_pictures=42,photographs=13,original_diagrams=29,distinct_picture_fraction=42/46,full_decode='passed',decoded_video_frames=c['decoded_video_frames'],encoded_audio_correlation=c['encoded_audio_matches_mix']['correlation'],sampled_export_frames=['export-frame-07.png','export-frame-33.png','export-frame-41.png','export-frame-47.png'],phone_preview='640x360 resized actual exported preventive-oral-care long-pair frame07 inspected;no physical device playback',source_fidelity_notes=['All46exact source/currentRussian pairs preserved in stored order;long preventive-care pair07 at44/36,others default48/40.','All13actual photograph/object masters and29individually composed diagrams reviewed. No actual patient status,dose,diagnosis,brand recommendation or new clinical procedure.','Medicines sold only in pharmacies;generic substitution IFsameactiveingredient;public/private dental care,age/referral/functional-bite gates retain exact scope.','Import-for-own-use matrix preserves EESorNorthernIreland one-year bring vs<=3months post,outside<=3months bring and postal prohibition;stricter narcotic limits are explicit. No new country-membership map,amount or legal exception.','One referral continuation and four source import rules retain useful unchanged graphics.42distinct source pictures;conservative geometry audit groups medicine/restriction motif additionally:41/46=89.13%,close to90%without cosmetic variants.','Actual source card derives both InfoFinland and orientation-guide publishers from sources.yaml;complete canonical sidecar retained.'],whole_video_listening=False,physical_device_playback=False,user_acceptance=False,issues=['Whole-video pronunciation and voice/music balance require listening;Finnish dental/service terms and medicine/import compounds flagged for attention.'])
(E/'production-handoff.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');b=yaml.safe_load((E/'brief.yaml').read_text());b.update(production_status='preview_ready',output_path=r['output'],issues=report['issues']+['Technically verified preview;whole-video user acceptance pending.']);(E/'brief.yaml').write_text(yaml.safe_dump(b,allow_unicode=True,sort_keys=False,width=100))
(E/'review.md').write_text(f'''# Episode review

Section ID: {SID}

Producer/date: Chapter10 worker,2026-11-03.

Preview:`{r['output']}` — {r['seconds']:.3f}seconds,1920×1080/24fps.

- [x] All46exact Swedish/current reviewed Russian pairs retained once in stored order;current ready source validation passes.
- [x] All46selected local F1 WAV hashes match current filename-keyed ASR records;actual inputs/settings/durations retained. Diagnostic transcript differences read separately;no listening claim.
- [x] All13actual photograph/object masters,42foreground pictures and56preflight stills inspected. Actual exported long pair07,generic substitution33,import matrix41,and both-publisher card47 inspected without clipping;640×360 actual exported07 inspected.
- [x] Actual body picture coverage100%;42distinct source pictures(13photos,29diagrams). One referral continuation and a useful unchanged four-rule import matrix deliberately repeat. Conservative underlying-geometry audit additionally groups the medicine/restriction motif:41/46=89.13%,without cosmetic variants.
- [x] All source gates preserve archived meaning;no new dose,diagnosis,current clinical advice,fee,deadline,country list or import permission. Raw licensed masters/metadata and canonical sidecar retained.
- [x] Complete export decode passed:{c['decoded_video_frames']}frames,{c['decoded_audio_seconds']}seconds audio. Encoded mix correlation{c['encoded_audio_matches_mix']['correlation']:.6f};timeline,mix and background-motion checks bind current hash.
- [ ] Whole-video pronunciation/accent and voice/music balance listened to.
- [ ] Headphone/speaker checks or physical phone/laptop playback.
- [ ] Complete video watched/heard end to end and accepted by user.

Finnish dental/service terms and medicine/import compounds require listening. Export SHA-256:`{r['sha256']}`. No commit or upload.
''');print(json.dumps(report,ensure_ascii=False))
