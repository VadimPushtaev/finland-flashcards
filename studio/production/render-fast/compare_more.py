"""Read-only decoded prototype fidelity and continuous-motion measurements."""
from pathlib import Path
import json,sys
import av,numpy as np
from PIL import Image
OUT=Path('/tmp/hb-render-fast');alpha=np.asarray(Image.open(OUT/'card.png').getchannel('A'));opaque=alpha==255;transparent=alpha==0
names=['perspective-scale1-start0','pillow-paste-scale1-start0'];report={}
for name in names:
 if not (OUT/(name+'.mp4')).exists():continue
 base=av.open(str(OUT/'pillow-scale1-start0.mp4'));other=av.open(str(OUT/(name+'.mp4')));sums={k:[] for k in ('all_mae','opaque_mae','background_mae','background_p99')};temporal=[];baseline_temporal=[];previous=None;previousbase=None;count=0
 for i,(a,b) in enumerate(zip(base.decode(video=0),other.decode(video=0))):
  a=a.to_ndarray(format='rgb24');b=b.to_ndarray(format='rgb24');diff=np.abs(a.astype(np.int16)-b.astype(np.int16));sums['all_mae'].append(float(diff.mean()));sums['opaque_mae'].append(float(diff[opaque].mean()));sums['background_mae'].append(float(diff[transparent].mean()));sums['background_p99'].append(float(np.percentile(diff[transparent],99)))
  patch=b[:,0:65].astype(np.int16);patcha=a[:,0:65].astype(np.int16)
  if previous is not None:temporal.append(float(np.abs(patch-previous).mean()));baseline_temporal.append(float(np.abs(patcha-previousbase).mean()))
  previous=patch;previousbase=patcha;count+=1
  if i in (0,59,119):
   Image.fromarray(b).save(OUT/(name+f'-{i:03d}.png'))
   if name==names[0]:Image.fromarray(a).save(OUT/(f'baseline-{i:03d}.png'))
 base.close();other.close();report[name]={k:float(np.mean(v)) for k,v in sums.items()};report[name].update(frames=count,temporal_patch_mean=float(np.mean(temporal)),temporal_patch_std=float(np.std(temporal)),baseline_temporal_patch_mean=float(np.mean(baseline_temporal)),baseline_temporal_patch_std=float(np.std(baseline_temporal)),frozen_patch_adjacent_frames=sum(t==0 for t in temporal))
 print(name,report[name],flush=True)
(OUT/'fidelity-more.json').write_text(json.dumps(report,indent=2)+'\n')
