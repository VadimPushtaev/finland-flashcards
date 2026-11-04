"""Bind the mental-health preview to all decoded cards and the preserved one-take112 comparison."""
from pathlib import Path
import json,yaml,hashlib
R=Path(__file__).resolve().parents[3];SID='hb-c10-psykisk';E=R/'studio/episodes'/SID;M=R/'studio/media'/SID;s=yaml.load((E/'script.yaml').read_text(),Loader=yaml.CSafeLoader);r=json.loads((E/'render.json').read_text());c=json.loads((E/'render-check.json').read_text());p=json.loads((E/'picture-coverage.json').read_text());d=json.loads((E/'picture-diversity.json').read_text());pre=json.loads((E/'prerender-handoff.json').read_text());metrics=json.loads((M/'narration/metrics.json').read_text());asr={a['file']:a for a in json.loads((M/'narration/asr.json').read_text())};proof=json.loads((E/'emergency112-retake-proof.json').read_text());assert r['sha256']==c['sha256']==hashlib.sha256((R/r['output']).read_bytes()).hexdigest();assert c['full_decode']=='passed'and p['picture_fraction']==1 and len(metrics)==len(s['sentences'])==79
for a,b in zip(metrics,s['sentences']):assert a['sentence_id']==b['sentence_id']and hashlib.sha256((R/a['path']).read_bytes()).hexdigest()==asr[a['path']]['sha256']
assert proof['new_selected_take']and proof['all_other_78_selected_wavs_unchanged']and'ett ett två'in metrics[52]['text']and'112'in asr[metrics[52]['path']]['asr_text'];assert d['distinct_picture_sources']==74
issues=['Whole-video pronunciation/accent and voice/music balance require listening;Finnish service/peer-group names,short modal/negation words,compounds and literal archived AA on är remain priorities. One112speech override has matching diagnostic112,not auditory proof.']
report=dict(section_id=SID,status='preview_ready',output=r['output'],seconds=r['seconds'],sha256=r['sha256'],source_section_sha256=s['source_section_sha256'],translation_file_sha256=s['translation_file_sha256'],pairs=79,selected_narration_clips=79,current_asr_hashes=79,actual_body_picture_fraction=1,distinct_pictures=74,photographs=13,original_diagrams=61,distinct_picture_fraction=74/79,conservative_visible_structures=72,conservative_visible_fraction=72/79,full_decode='passed',decoded_video_frames=c['decoded_video_frames'],encoded_audio_correlation=c['encoded_audio_matches_mix']['correlation'],all_actual_decoded_card_frames_inspected=89,simulated_phone_samples=13,sampled_native_export_frames=['export-frame-53.png','export-frame-55.png','export-frame-68.png'],source_fidelity_notes=pre['source_fidelity_notes']+['All89actual decoded title/body/credit frames inspected in5contacts;13simulated640pixel samples inspected;native53urgentOR112,55bothacute-careconditions,68cause+MAYapply checked.','C8independent all79SVRU/all89preflightframes/13photo primarymetadata passed;unrendered illustration-count note resolved.Current central attribution-note correction sourcevalidation passed.'],retake_proof='studio/episodes/hb-c10-psykisk/emergency112-retake-proof.json',source_note_correction=json.loads((E/'source-note-correction-binding.json').read_text()),whole_video_listening=False,physical_device_playback=False,user_acceptance=False,issues=issues)
(E/'production-handoff.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');b=yaml.safe_load((E/'brief.yaml').read_text());b.update(production_status='preview_ready',output_path=r['output'],issues=issues+['Technically verified preview;whole-video user acceptance pending.']);(E/'brief.yaml').write_text(yaml.safe_dump(b,allow_unicode=True,sort_keys=False,width=100))
(E/'review.md').write_text(f'''# Episode review

Section ID: {SID}

Producer/date: Chapter10 worker,2026-11-03.

Preview: `{r['output']}` — {r['seconds']:.3f}seconds,1920×1080/24fps.

- [x] All79exactSwedish/current reviewedRussian pairs once in storedsourceorder.Current source/snapshot/readable-script checks passed.C8independent79/89preflight/13photo review passed.
- [x] All79current selectedF1WAVs match filename-keyedASRhashes;all diagnostictranscripts read.One bounded112explicitdigits take replaced only index52;originaltake retained,other78bit-identical,metricsfreshseed42invocation accuratelyrecorded.No listeningclaim.
- [x] All89actual verifier-decoded title/body/9credit cards inspected,plus13simulated640pixel samples.Native53urgentOR112,55cumulativeacute-careconditions,68due-to-cause+MAYAPPLY reviewed without clipping.
- [x] Actualbodypicturetimeline100%;74distinct sourcepictures(13photos61specificdiagrams).Conservative72/79=91.14%groups repeated motifs honestly.Five useful sourcecontinuations retain unchanged pictures.
- [x] No picturedperson assigned diagnosis,trauma,immigration or dependence status.No invented drug-use/injection/detoxsteps,medicalprocedure,clinicaleligibility or guarantee. Source archived AA on är retained.
- [x] Full decode{c['decoded_video_frames']}video frames,{c['decoded_audio_seconds']}saudio;mix correlation{c['encoded_audio_matches_mix']['correlation']:.6f};timeline,mix,motion andcoverage bindcurrenthash.
- [ ] Whole-video voice/accent/pronunciation andmix listenedto.
- [ ] Physical phone/laptop/headphone/speakerplayback.
- [ ] User watched/heard andaccepted completevideo.

ExportSHA256: `{r['sha256']}`. No commit orupload.
''');print(SID,r['seconds'],r['sha256'],c['encoded_audio_matches_mix']['correlation'])
