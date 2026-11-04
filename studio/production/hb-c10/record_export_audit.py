"""Record completed human visual review only for explicitly named actual-frame contact sets."""
from pathlib import Path
import sys,json,hashlib,datetime,shutil
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent;items=json.loads((P/'full-export-audit-candidates.json').read_text());wanted=set(sys.argv[1:]);assert wanted
for r in items:
 sid=r['section_id']
 if sid not in wanted:continue
 E=R/'studio/episodes'/sid;v=json.loads((E/'render-check.json').read_text());assert v['sha256']==r['export_sha256']==hashlib.sha256((R/r['export']).read_bytes()).hexdigest()
 for f in r['frames']:assert hashlib.sha256((R/f['path']).read_bytes()).hexdigest()==f['sha256']
 r.update(reviewed=True,reviewed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='All verifier-decoded title/body/credit card images visually inspected through listed actual-frame contacts. Every exact source pair and qualifier was separately source/preflight reviewed. Listed simulated640pixel body/sourcecredit samples also visually inspected. Static-frame visual review is not continuous end-to-end watch/listening or physicaldevice playback.',findings=[],physical_device_playback=False,whole_video_listening=False,user_acceptance=False,current_metadata_hashes={n:hashlib.sha256((E/n).read_bytes()).hexdigest()for n in ['script.yaml','assets.yaml','sources.yaml','CREDITS.md']});target=E/'actual-export-review.json';target.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
 h=E/'production-handoff.json'
 if h.exists():
  rev=E/'revisions/before-full-export-audit/production-handoff.json';rev.parent.mkdir(parents=True,exist_ok=True)
  if not rev.exists():shutil.copyfile(h,rev)
  j=json.loads(h.read_text());j['full_actual_export_review']=dict(path=str(target.relative_to(R)),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),export_sha256=r['export_sha256'],all_actual_card_frames=r['all_actual_decoded_frames'],simulated_phone_frames=len(r['simulated_phone_frames']),findings=[]);h.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
 review=E/'review.md';text=review.read_text()if review.exists()else'';marker='## Full actual export frame review'
 if marker not in text:review.write_text(text+'\n'+marker+'\n\nAll '+str(r['all_actual_decoded_frames'])+'actual decoded title/body/credit cards and '+str(len(r['simulated_phone_frames']))+'simulated640pixel samples inspected with no findings. Current export/frame/source/credit bindings are in `actual-export-review.json`. No continuous whole-video watch/listening,physical device playback or user acceptance is claimed.\n')
 print('Reviewed',sid,r['all_actual_decoded_frames'],len(r['simulated_phone_frames']))
assert wanted<={r['section_id']for r in items};(P/'full-export-audit-candidates.json').write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n')
