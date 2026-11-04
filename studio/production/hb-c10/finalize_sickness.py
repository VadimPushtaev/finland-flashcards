"""Bind the illness-benefit preview to its complete verified export and diagnostic evidence."""
from pathlib import Path
import json,yaml,hashlib
R=Path(__file__).resolve().parents[3];SID='hb-c10-sjukdom';E=R/'studio/episodes'/SID;M=R/'studio/media'/SID
s=yaml.load((E/'script.yaml').read_text(),Loader=yaml.CSafeLoader);r=json.loads((E/'render.json').read_text());c=json.loads((E/'render-check.json').read_text());p=json.loads((E/'picture-coverage.json').read_text());d=json.loads((E/'picture-diversity.json').read_text());pre=json.loads((E/'prerender-handoff.json').read_text());metrics=json.loads((M/'narration/metrics.json').read_text());asr={a['file']:a for a in json.loads((M/'narration/asr.json').read_text())};assert r['sha256']==c['sha256']==hashlib.sha256((R/r['output']).read_bytes()).hexdigest();assert c['full_decode']=='passed'and p['picture_fraction']==1 and len(metrics)==len(s['sentences'])==43
for a,b in zip(metrics,s['sentences']):assert a['sentence_id']==b['sentence_id']and hashlib.sha256((R/a['path']).read_bytes()).hexdigest()==asr[a['path']]['sha256']
assert d['distinct_picture_sources']==39;issues=['Whole-video pronunciation/accent and voice/music balance require listening;Finnish benefit names,age ranges and long work-incapacity compounds remain diagnostic priorities.']
report=dict(section_id=SID,status='preview_ready',output=r['output'],seconds=r['seconds'],sha256=r['sha256'],source_section_sha256=s['source_section_sha256'],translation_file_sha256=s['translation_file_sha256'],pairs=43,selected_narration_clips=43,current_asr_hashes=43,actual_body_picture_fraction=1,distinct_pictures=39,photographs=8,original_diagrams=31,distinct_picture_fraction=39/43,conservative_visible_structures=39,conservative_visible_fraction=39/43,full_decode='passed',decoded_video_frames=c['decoded_video_frames'],encoded_audio_correlation=c['encoded_audio_matches_mix']['correlation'],sampled_export_frames=['export-frame-28.png','export-frame-32.png','export-frame-41.png','export-frame-44.png'],phone_preview='640x360 resized actual exported long pair02 inspected;no physical device playback.',source_fidelity_notes=pre['source_fidelity_notes']+['Root independent all43SVRU/all50preflight stills/native28/32/41+12simulatedphones passed;actual export28/32/41/44andphone02 checked.','Three long source pairs1,27,31use44/36;othersdefault48/40.Four-condition list overview intentionally spans five successive sourcefragments.','Central attribution-note correction is metadata-only;current source snapshot/credits ready validation passed and historical revisions retained.'],source_note_correction=json.loads((E/'source-note-correction-binding.json').read_text()),whole_video_listening=False,physical_device_playback=False,user_acceptance=False,issues=issues)
(E/'production-handoff.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');b=yaml.safe_load((E/'brief.yaml').read_text());b.update(production_status='preview_ready',output_path=r['output'],issues=issues+['Technically verified preview;whole-video user acceptance pending.']);(E/'brief.yaml').write_text(yaml.safe_dump(b,allow_unicode=True,sort_keys=False,width=100))
(E/'review.md').write_text(f'''# Episode review

Section ID: {SID}

Producer/date: Chapter10 worker,2026-11-03.

Preview: `{r['output']}` — {r['seconds']:.3f}seconds,1920×1080/24fps.

- [x] All43exact Swedish/current reviewed Russian pairs once in stored sourceorder,including u0272before u0212. Current ready/source/snapshot checks passed after central attribution-note cleanup.
- [x] All43selected F1 WAVs match actual filename-keyed ASR hashes;all diagnostic transcripts read and settings/inputs/durations retained. No listening claim.
- [x] All50preflight stills and8actualphoto masters inspected;independent root all43SVRU/all50stills review passed. Actual exported28under16ANDregularcare>=6months,32childcareANDcannotworkBECAUSEcare,41TOTAL>=1yearpensionercare,44InfoFinland sourcecredits and640×360actual long02 checked.
- [x] Picturetimeline100%;39distinct pictures(8photos31specificdiagrams)/43pairs=90.70%. One useful unchanged four-conditionoverview is retained across five adjacent listfragments.
- [x] Salarywaitingperiod,weekdaycounts,continuous-versus-totalyear,care/age gates and sourcebenefit alternatives retain exactconditions.No invented euroamount,rate,diagnosis,medicalprocedure or photographedbenefitstatus.
- [x] Complete decode:{c['decoded_video_frames']}video frames,{c['decoded_audio_seconds']}s audio. Encodedmix correlation{c['encoded_audio_matches_mix']['correlation']:.6f};timeline,mix,motion andcoverage bind current exporthash.
- [ ] Whole-video pronunciation/accent and mix listened to.
- [ ] Physical laptop/phone/headphone/speaker playback.
- [ ] User watched/heard andaccepted completevideo.

Export SHA-256: `{r['sha256']}`. No commit orupload.
''');print(SID,r['seconds'],r['sha256'])
