"""Record a manually inspected preview after full technical checks have passed."""
from pathlib import Path
import sys,json,hashlib
import yaml
ROOT=Path(__file__).resolve().parents[3]
def main(section,indices):
 ep=ROOT/'studio/episodes'/section;render=json.loads((ep/'render.json').read_text());check=json.loads((ep/'render-check.json').read_text());coverage=json.loads((ep/'picture-coverage.json').read_text());script=yaml.safe_load((ep/'script.yaml').read_text());diagnostics=json.loads((ep/'narration-check.json').read_text())
 checksum=hashlib.sha256((ROOT/render['output']).read_bytes()).hexdigest()
 assert checksum==render['sha256']==check['sha256'] and check['full_decode']=='passed'
 assert check['encoded_audio_matches_mix'] and len(diagnostics['sentences'])==len(script['sentences'])
 frames=[]
 for i in indices:
  f=ROOT/'studio/media'/section/'render'/f'export-frame-{i:02}.png';frames.append({'path':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 report={'section_id':section,'review_date':'2026-10-26','output':render['output'],'export_sha256':checksum,'source_section_sha256':script['source_section_sha256'],'translation_file_sha256':script['translation_file_sha256'],'reviewed_export_frames':frames,'sizes_inspected':['1920x1080 exported source frames','476x268 or 640x360 contact-sheet previews'],'findings':'Representative exported title, long or numerical source pairs, foreground pictures/diagrams and both credits inspected after rendering; no clipping, orphaned captions or misleading picture identity found.','picture_fraction':coverage['picture_fraction'],'motion':'Decoder checks bind continuous background boundaries and visible 5/10 second motion to this export. Whole-motion playback not performed.','auditory_review_performed':False,'physical_device_playback_performed':False,'user_acceptance':False}
 (ep/'visual-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 brief=yaml.safe_load((ep/'brief.yaml').read_text());brief['production_status']='preview_ready';brief['output_path']=render['output'];brief['issues']=['Whole-video listening, physical-device playback and user acceptance pending.']+diagnostics.get('priority_review',[]);(ep/'brief.yaml').write_text(yaml.safe_dump(brief,allow_unicode=True,sort_keys=False,width=100))
 p=ep/'review.md';old=p.read_text();old=old.replace('- [ ] Final exported video decoded and representative exported frames reviewed.','- [x] Final exported video fully decoded and representative exported frames reviewed.');p.write_text(old+f"\nVerified preview: `{render['output']}`, {render['seconds']:.3f} seconds, SHA256 `{checksum}`. Full {render['frames']}-frame decode and current audio-mix match passed; all {len(script['sentences'])} retained clips have hash-bound local ASR diagnostics. Final picture coverage {coverage['picture_fraction']*100:.1f}%. See render-check.json, visual-review.json, narration-check.json and picture-coverage.json. Whole-video listening, physical-device playback and user acceptance remain pending.\n")
 job=ROOT/'studio/media'/section/'jobs';job.mkdir(exist_ok=True);(job/'production-status.json').write_text(json.dumps({'stage':'preview_ready','output':render['output'],'sha256':checksum,'seconds':render['seconds'],'listening_pending':True},indent=2)+'\n')
 print(section,render['seconds'],checksum,coverage['picture_fraction'])
if __name__=='__main__':main(sys.argv[1],[int(v) for v in sys.argv[2].split(',')])
