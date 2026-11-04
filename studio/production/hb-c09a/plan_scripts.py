"""Plan exact Chapter 9 scripts with individual source-bound foreground requests."""
from pathlib import Path
import yaml,json,copy,re,sys
ROOT=Path.cwd();pal={'background':'#442d30','text':'#faf3e8','secondary':'#e5c5be','highlight':'#e6c384','separator':'#80575a'}
slugs=sys.argv[1:] or ['forandring','familjeformer','kon','samlevnad','aktenskap','makar']
base=yaml.safe_load((ROOT/'studio/episodes/hb-c07-arbetsavtal/script.yaml').read_text())
for slug in slugs:
    sid='hb-c09-'+slug;ep=ROOT/'studio/episodes'/sid;p=ep/'script.yaml'
    if not p.exists():continue
    d=yaml.safe_load(p.read_text())
    if d['episode_decisions']:continue
    d['episode_decisions']=[dict(id=k,decision=v,status='proposed',resolve_during=stage) for k,v,stage in [
    ('opening','Exact unspoken bilingual heading for three seconds, then every archived body sentence and list fragment once in stored order.','script'),
    ('layout','Fixed right bilingual panel at 1920x1080/24 fps with Liberation Sans, Swedish48 and Russian40; Chapter9 terracotta palette. Foreground remains steady while decorative background moves continuously.','script'),
    ('story_structure','Paragraph and source-list groups retain their original progression. Source-specific illustrations explain the exact relationships without adding contemporary law or statistics.','script'),
    ('voice_selection','Local Swedish Supertonic3/F1, steps32, speed0.95, seed42, 44100Hz mono PCM16; initial ONNX threads2. Full-video pronunciation and user listening review remain pending.','script'),
    ('foreground_selection','A distinct source-bound foreground picture is planned for almost every sentence. Physical objects/institutions prioritize verified photography; legal and familial relationships use original explicit pictorial diagrams. No repeated generic image or text-only quota filler.','script'),
    ('pace','Show sentence pair0.25s before narration, retain through measured full speech and 1.5s regular pause;2.2s at source-topic ends and2.5s for long pairs. No arbitrary runtime target.','script'),
    ('visual_motion','Distinct reserved episode photograph. Continuous full-episode diagonal pan with15% relative zoom, starting in motion; 140second smooth cycles. Final photograph identity/settings resolved during assets.','assets'),
    ('music_selection','Distinct centrally reserved instrumental with full composer/source/license credits; accepted+2dB setting, narration ducking and gentle fades. Crossfade repeats only when required by measured duration.','assets'),
    ('closing','Readable source/media credit cards and complete accompanying source and reuse notices.','script'),
    ('exceptions','No source wording, reviewed Russian text, ordering or IDs are changed; foreground scarcity will be explicitly documented instead of irrelevant filler.','script')]]
    d['scenes']=[];d['asset_requests']=[dict(id=k,kind=kind,description=desc,fallback=fall) for k,kind,desc,fall in [
    ('episode_background','background','Distinct source-verified topic-related photograph reserved centrally.','Select another verified licensed image and update central identity reservation.'),
    ('music_bed','music','Distinct reserved licensed calm instrumental.','Select another centrally reserved instrumental with verified reuse terms.'),
    ('narration','narration','One exact full-source local SwedishF1clip per sentence.','Diagnostic-driven targeted retake in separate folder; retain original takes and metrics.')]]
    last=None
    for i,row in enumerate(d['sentences']):
        unit=row['sentence_id'].rsplit('-s',1)[0]
        if unit!=last:
            d['scenes'].append(dict(id='scene-'+str(len(d['scenes'])+1),description=row['sv']));last=unit
        pic='picture_'+str(i+1).zfill(3)
        row.update(scene_id=d['scenes'][-1]['id'],asset_ids=['episode_background',pic],visual_cue='Distinct original pictorial explanation or verified photograph of the objects and relationships stated in this exact source pair; individual composition in visual-plan.json. Keep bilingual panel fixed; omit redundant captions.',text_highlights=[],pause_after_seconds=2.5 if len(row['sv'])+len(row['ru'])>280 else 1.5,render_image=f'studio/media/{sid}/pictures/{pic}.png',render_caption=False)
        if i+1==len(d['sentences']) or d['sentences'][i+1]['sentence_id'].rsplit('-s',1)[0]!=unit:row['pause_after_seconds']=max(row['pause_after_seconds'],2.2)
        d['asset_requests'].append(dict(id=pic,kind='foreground',description='A source-bound illustration of: '+row['sv'],fallback='Verified relevant photograph or explanatory source-based diagram; record any genuinely unsuitable sentence and leave foreground empty rather than invent information.'))
    d['render']=copy.deepcopy(base['render']);r=d['render'];r.update(music_path=f'studio/media/{sid}/sources/music-bed.flac',background_image=f'studio/media/{sid}/sources/background.jpg',palette=pal)
    r.pop('background_identity',None);r['background_style']['motion_cycles']=1;r['credits']=r['credits'][:2];r['credits'][1]['paragraphs']=['Fullständiga bildkällor och licenser i medföljande CREDITS.md.','Original schematisk illustration: Homebrew video studio.','Lokal svensk berättarröst: Supertonic 3 · F1.']
    p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False,width=100));b=yaml.safe_load((ep/'brief.yaml').read_text());b['production_status']='script_ready';b['issues']=['Picture acquisition and final layout inspection pending. Whole-video listening and user acceptance pending.'];(ep/'brief.yaml').write_text(yaml.safe_dump(b,allow_unicode=True,sort_keys=False));print(sid,len(d['sentences']),flush=True)
