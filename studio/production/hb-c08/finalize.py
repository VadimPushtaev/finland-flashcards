"""Record technically verified previews without claiming listening or user acceptance."""
from pathlib import Path
import hashlib,json,sys,yaml
ROOT=Path(__file__).resolve().parents[3]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(sid):
 ep=ROOT/'studio/episodes'/sid;script=yaml.safe_load((ep/'script.yaml').read_text());render=json.loads((ep/'render.json').read_text());check=json.loads((ep/'render-check.json').read_text());coverage=json.loads((ep/'picture-coverage.json').read_text());diversity=json.loads((ep/'picture-diversity.json').read_text());output=ROOT/render['output'];assert check['sha256']==digest(output)==render['sha256'];assert check['full_decode']=='passed';assert coverage['picture_fraction']>=.9
 metrics=json.loads((ROOT/'studio/media'/sid/'narration/metrics.json').read_text());asr=json.loads((ROOT/'studio/media'/sid/'narration/asr.json').read_text());assert len(metrics)==len(script['sentences']);assert {r['sentence_id'] for r in metrics}=={r['sentence_id'] for r in script['sentences']};assert len(asr)==len(metrics)
 for r in asr:assert digest(ROOT/r['file'])==r['sha256']
 brief=yaml.safe_load((ep/'brief.yaml').read_text());brief['production_status']='preview_ready';brief['issues']=['Complete video technically verified; whole-video listening and user acceptance pending.','Local ASR transcript differences are diagnostic only; see narration diagnostics and review priorities.'];(ep/'brief.yaml').write_text(yaml.safe_dump(brief,allow_unicode=True,sort_keys=False))
 result=dict(section_id=sid,production_status='preview_ready',translation_readiness='ready',episode_path=str(ep.relative_to(ROOT)),output=render['output'],sha256=render['sha256'],seconds=render.get('seconds',render.get('duration_seconds')),source_section_sha256=script['source_section_sha256'],translation_file_sha256=script['translation_file_sha256'],source_sentences=len(script['sentences']),picture_fraction=coverage['picture_fraction'],distinct_picture_sources=diversity['distinct_picture_sources'],photographed_slides=diversity['photographed_slides'],checks=dict(source_fidelity='passed',assets='passed',complete_decode='passed',audio_mix=check.get('encoded_audio_matches_mix'),asr_clips=len(asr)),review_limits=['No full-video listening review performed.','No whole-video user acceptance.','Actual export frame review must be recorded separately; automated checks are not visual review.'])
 (ep/'production-handoff.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':
 for sid in sys.argv[1:]:main(sid)
