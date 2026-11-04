"""Isolated bilinear/bicubic comparison on blurred actual production sources."""
from pathlib import Path
import copy,hashlib,json,math,os,resource,statistics,subprocess,sys,time
import av,imageio_ffmpeg,numpy as np,yaml
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'studio/tools'));import render
OUT=Path('/tmp/hb-resampler-comparison');OUT.mkdir(exist_ok=True);REPORT=ROOT/'studio/production/render-fast/resampler-results';REPORT.mkdir(exist_ok=True)
CASES=['hb-c08-utveckling','hb-c08-smabarn','hb-c08-hogskolor','hb-c12-sprak','hb-c12-e-tjanster'];POSITIONS=[0,.1,.25,.5,.75,.9,1];FRAMES=96

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def memory(pid):
 try:return int(next(x for x in Path(f'/proc/{pid}/status').read_text().splitlines() if x.startswith('VmHWM:')).split()[1])
 except (FileNotFoundError,StopIteration):return 0

def composite(base,t,style,rgb,mask,sampler):
 frame=base.resize((1920,1080),resample=sampler,box=render.background_extent(base.size,t,style));frame.paste(rgb,(0,0),mask);return frame

def run(sid,case_index):
 ep=ROOT/'studio/episodes'/sid;script=yaml.safe_load((ep/'script.yaml').read_text());render.configure_style(script);style=copy.deepcopy(script['render']['background_style']);assert style['blur_pixels']==2.5 and style['darken']==.42;original_style=copy.deepcopy(style)
 # Actual full timeline when it exists,otherwise the settled140second motion cycle.
 rp=ep/'render.json'
 if rp.exists():r=json.loads(rp.read_text());total=r['frames'];clock='actual completed export frame clock'
 else:total=24*140;style['motion_cycles']=1;clock='140second reference cycle; no source or production timing changed'
 bgpath=ROOT/script['render']['background_image'];fgpath=ROOT/script['sentences'][0]['render_image'];images={script['render']['background_image']:Image.open(bgpath).convert('RGB'),script['sentences'][0]['render_image']:Image.open(fgpath).convert('RGB')};base=render.prepare_background(images[script['render']['background_image']],style);rows={r['sentence_id']:r for r in script['sentences']};card,_=render.make_card(script,dict(kind='sentence',sentence_id=script['sentences'][0]['sentence_id']),rows,images);rgb=card.convert('RGB');mask=card.getchannel('A');alpha=np.asarray(mask);opaque=alpha==255;exposed=alpha==0;samplers={'bilinear':Image.Resampling.BILINEAR,'bicubic':Image.Resampling.BICUBIC};samples=[]
 for position in POSITIONS:
  a=composite(base,position,style,rgb,mask,samplers['bicubic']);b=composite(base,position,style,rgb,mask,samplers['bilinear']);delta=np.abs(np.asarray(a).astype(np.int16)-np.asarray(b).astype(np.int16));samples.append(dict(progress=position,all_mae=float(delta.mean()),background_mae=float(delta[exposed].mean()),background_max=int(delta[exposed].max()),background_p99=float(np.percentile(delta[exposed],99)),all_max=int(delta.max()),opaque_max=int(delta[opaque].max()),channels_difference_over2=float((delta>2).mean()),channels_difference_over5=float((delta>5).mean())))
  if position==.25:
   a.save(OUT/(sid+'-bicubic.png'));b.save(OUT/(sid+'-bilinear.png'));crop=(0,0,800,160);a.crop(crop).resize((1600,320)).save(OUT/(sid+'-bicubic-detail.png'));b.crop(crop).resize((1600,320)).save(OUT/(sid+'-bilinear-detail.png'))
 timings={k:[] for k in samplers}
 for repeat in range(4):
  order=['bilinear','bicubic'] if repeat%2==0 else ['bicubic','bilinear']
  for name in order:
   start=time.perf_counter();cpu=time.process_time()
   for frame in range(12):composite(base,(frame+repeat*12)/(total-1),style,rgb,mask,samplers[name]).tobytes()
   timings[name].append(dict(wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,frames=12))
 encodings={};ff=imageio_ffmpeg.get_ffmpeg_exe();start_global=24*15
 for name in (['bilinear','bicubic'] if case_index%2==0 else ['bicubic','bilinear']):
  destination=OUT/(sid+'-'+name+'.mp4');cmd=[ff,'-y','-v','error','-threads','1','-filter_threads','1','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-an','-c:v','libx264','-preset','fast','-crf','20','-threads','1','-pix_fmt','yuv420p','-frames:v',str(FRAMES),str(destination)];start=time.perf_counter();cpu=time.process_time();peak=0;temporal=[];previous=None
  with (OUT/(sid+'-'+name+'.log')).open('wb') as log:
   p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
   for n in range(FRAMES):
    frame=composite(base,(start_global+n)/(total-1),style,rgb,mask,samplers[name]);patch=np.asarray(frame)[:,0:65].astype(np.int16)
    if previous is not None:temporal.append(float(np.abs(patch-previous).mean()))
    previous=patch;p.stdin.write(frame.tobytes());peak=max(peak,memory(p.pid))
   p.stdin.close();assert p.wait()==0
  encodings[name]=dict(frames=FRAMES,fps=FRAMES/(time.perf_counter()-start),wall_seconds=time.perf_counter()-start,python_cpu_seconds=time.process_time()-cpu,ffmpeg_peak_rss_kib=peak,output=str(destination),sha256=digest(destination),raw_exposed_temporal_mean=float(np.mean(temporal)),raw_exposed_temporal_std=float(np.std(temporal)))
  print(sid,name,'encoded',round(encodings[name]['fps'],2),'fps',flush=True)
 # Fully decode both samples and measure independent lossy-encoding differences.
 a=av.open(str(OUT/(sid+'-bicubic.mp4')));b=av.open(str(OUT/(sid+'-bilinear.mp4')));decoded=[]
 for fa,fb in zip(a.decode(video=0),b.decode(video=0)):
  delta=np.abs(fa.to_ndarray(format='rgb24').astype(np.int16)-fb.to_ndarray(format='rgb24').astype(np.int16));decoded.append(dict(all_mae=float(delta.mean()),background_mae=float(delta[exposed].mean()),opaque_mae=float(delta[opaque].mean())))
 a.close();b.close();assert len(decoded)==FRAMES
 result=dict(section_id=sid,source_background=str(bgpath.relative_to(ROOT)),source_sha256=digest(bgpath),original_style=original_style,comparison_style=style,clock=clock,pixel_samples=samples,timing_batches=timings,timing_summary={k:dict(median_compositor_fps=12/statistics.median(x['wall_seconds'] for x in v),median_cpu_seconds_per_frame=statistics.median(x['cpu_seconds']/12 for x in v)) for k,v in timings.items()},encodings=encodings,decoded_frames=len(decoded),decoded_mean_errors={k:float(np.mean([d[k] for d in decoded])) for k in decoded[0]},python_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,limits='No production file,narration,mix or shared renderer changed. Same exact static card and floating crop extent. Encoded samples omit audio; earlier compositor experiment verified source-audio equivalence. No expert playback-level perceptual acceptance claimed.')
 (REPORT/(sid+'.json')).write_text(json.dumps(result,indent=2)+'\n');return result
results=[]
for i,sid in enumerate(CASES):results.append(run(sid,i))
(REPORT/'summary.json').write_text(json.dumps(dict(episodes=results,completed=True),indent=2)+'\n')
print('Five-source comparison complete',flush=True)
