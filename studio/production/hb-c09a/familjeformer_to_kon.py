"""Use the root-assigned successor slot only after exact current render success."""
from pathlib import Path
import json,hashlib,subprocess,time
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
while True:
 st=json.loads((H/'familjeformer-render-host-state.json').read_text())
 assert st['supervisor_pid']==291294
 if st['status']=='finished':
  assert st['returncode']==0 and not st['missing_outputs'];break
 assert st['status']=='running';print('Familjeformer291294 still rendering; no successor launched.',flush=True);time.sleep(30)
# Current canonical artifact and current render report are required.
assert (R/'videos/homebrew/hb-c09-02-familjeformer.mp4').is_file()
assert (R/'studio/episodes/hb-c09-familjeformer/render.json').is_file()
ep=R/'studio/episodes/hb-c09-kon';f=json.loads((H/'kon-frozen-candidate.json').read_text())
for k,p in [('script_sha256',ep/'script.yaml'),('assets_sha256',ep/'assets.yaml'),('narration_metrics_sha256',R/'studio/media/hb-c09-kon/narration/metrics.json'),('preflight_review_sha256',ep/'producer-preflight-review.json')]:assert hashlib.sha256(p.read_bytes()).hexdigest()==f[k],k
live=[]
for q in Path('/proc').glob('[0-9]*/cmdline'):
 try:
  a=q.read_bytes().split(b'\0')
  if b'studio/tools/render.py' in a and b'--stills-only' not in a:live.append({'pid':int(q.parent.name),'args':[x.decode() for x in a if x]})
 except OSError:pass
assert len(live)<5,live
proof={'predecessor':st,'host_full_renderers_before_launch':live,'budget':5,'frozen_kon_inputs':f,'checked_at':time.time()}
for slug,stage in [('kon','render'),('familjeformer','verify')]:
 c=H/f'{slug}-{stage}-job.json';p=subprocess.run(['.venv/bin/python','studio/production/remaining/job.py','start',str(c.relative_to(R))],cwd=R,capture_output=True,text=True,check=True);proof[slug+'_'+stage+'_launch']=p.stdout
(H/'familjeformer-kon-slot-handoff.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2),flush=True)
