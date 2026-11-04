"""Bounded one-CPU, lossless-background/RGBA-hold cache experiment; temp exports only."""
from pathlib import Path
import bisect,copy,hashlib,json,os,subprocess,sys,time
import av,imageio_ffmpeg,numpy as np,yaml
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'studio/tools'));import render
OUT=Path('/tmp/hb-cycle-cache');OUT.mkdir(exist_ok=True);REPORT=ROOT/'studio/production/render-fast/cycle-cache-results.json';CPU=min(os.sched_getaffinity(0));os.sched_setaffinity(0,{CPU});FF=imageio_ffmpeg.get_ffmpeg_exe();N=192;P=96;FPS=24;SIZE=1920*1080*3
sid='hb-c08-hux';ep=ROOT/'studio/episodes'/sid;s=yaml.safe_load((ep/'script.yaml').read_text());render.configure_style(s);rows={r['sentence_id']:r for r in s['sentences']};tl,total=render.build_timeline(s);START=tl[2]['start_frame']-48;style=copy.deepcopy(s['render']['background_style']);style['motion_cycles']=N/P
images={p:Image.open(ROOT/p).convert('RGB') for p in {r['render_image'] for r in rows.values()}|{s['render']['background_image']}};base=render.prepare_background(images[s['render']['background_image']],style);cards=[render.make_card(s,item,rows,images)[0] for item in tl];starts=[r['start_frame'] for r in tl]
report={'source_episode':sid,'production_unchanged':True,'cpu_affinity':[CPU],'fixture_frames':N,'fps':FPS,'fixture_start_frame_in_existing_timeline':START,'accelerated_cache_period_frames':P,'fixture_seconds':N/FPS,'measurements':{}};tim=time.monotonic()
def save():REPORT.write_text(json.dumps(report,indent=2)+'\n')
def log(*x):print(round(time.monotonic()-tim,2),*x,flush=True)
def ffbase():return [FF,'-y','-v','error','-threads','1','-filter_threads','1','-filter_complex_threads','1']
def audio():return ['-ss',str(START/FPS),'-i',str(ROOT/'studio/media'/sid/'render/mix.wav')]
def enc(dest):return ['-c:v','libx264','-threads','1','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t',str(N/FPS),'-frames:v',str(N),'-movflags','+faststart',str(dest)]
def pipe_frames(cmd,frames):
 before=time.monotonic()
 with (OUT/(Path(cmd[-1]).stem+'.log')).open('wb') as h:
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=h)
  try:
   for frame in frames:p.stdin.write(frame)
   p.stdin.close();assert p.wait(timeout=180)==0,(OUT/(Path(cmd[-1]).stem+'.log')).read_text()
  except BaseException:p.kill();p.wait();raise
 return time.monotonic()-before
# Static cards are made once; only the original six-frame left-picture transition is blended.
cache={};sequence=[];holds=[];t=time.monotonic()
for f in range(N):
 absolute=START+f;i=bisect.bisect_right(starts,absolute)-1;local=absolute-tl[i]['start_frame'];transition=i>0 and tl[i]['kind']==tl[i-1]['kind']=='sentence' and local<6;key=(i,local if transition else -1)
 if key not in cache:
  overlay=cards[i]
  if transition:
   overlay=overlay.copy();overlay.paste(Image.blend(cards[i-1].crop((90,180,850,900)),overlay.crop((90,180,850,900)),(local+1)/6),(90,180))
  path=OUT/f'card-{len(cache):02d}.png';overlay.save(path);cache[key]=(overlay,path)
 sequence.append(key)
 if not holds or holds[-1][0]!=key:holds.append([key,1])
 else:holds[-1][1]+=1
report['measurements']['foreground_png_prepare_seconds']=time.monotonic()-t;report['foreground_pngs']=len(cache);concat=['ffconcat version 1.0']
for key,count in holds:concat += ["file '"+str(cache[key][1])+"'",'option framerate 24',f'duration {count/24:.15f}']
concat += ["file '"+str(cache[holds[-1][0]][1])+"'",'option framerate 24'];(OUT/'cards.ffconcat').write_text('\n'.join(concat)+'\n');log('cards prepared',len(cache))
# One accelerated cycle, sampled without duplicating its endpoint; FFV1 is lossless RGB.
cycle_style=copy.deepcopy(style);cycle_style['motion_cycles']=1;cycle_hash=[]
def cycle_frames():
 for f in range(P):
  raw=render.background_frame(base,f/P,cycle_style,mode='RGB').tobytes();cycle_hash.append(hashlib.sha256(raw).hexdigest());yield raw
cmd=ffbase()+['-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-an','-c:v','ffv1','-level','3','-threads','1','-pix_fmt','bgr0',str(OUT/'cycle.mkv')];report['measurements']['cache_create_seconds']=pipe_frames(cmd,cycle_frames());log('cache encoded');save()
with av.open(str(OUT/'cycle.mkv')) as c:
 c.streams.video[0].thread_count=1;decoded=[hashlib.sha256(fr.to_ndarray(format='rgb24').tobytes()).hexdigest() for fr in c.decode(video=0)]
assert decoded==cycle_hash;report['lossless_cache_exact_frames']=len(decoded)
# Reference retains the renderer's current per-frame fractional crop and exact card transition.
refraw=OUT/'reference.rgb'
def reference_frames():
 with refraw.open('wb') as h:
  for f,key in enumerate(sequence):
   card=cache[key][0];frame=render.composite_rgb_frame(base,f/(N-1),style,card.convert('RGB'),card.getchannel('A'));raw=frame.tobytes();h.write(raw);yield raw
cmd=ffbase()+['-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-']+audio()+enc(OUT/'reference.mp4');report['measurements']['reference_encode_seconds']=pipe_frames(cmd,reference_frames());log('reference encoded');save()
# Cache A is one frame behind B. Frame-specific scalar blending matches analytic phase q=f+f/(F-1).
commands=[f'{(f-.5)/24:.15f} blend@clock all_opacity {1-f/(N-1):.17f};' for f in range(1,N)];(OUT/'clock.txt').write_text('\n'.join(commands)+'\n')
filt=f'[0:v]settb=1/24,setpts=N,split[a][b];[b]trim=start_frame=1,setpts=N[b1];[a]sendcmd=f={OUT}/clock.txt[a1];[a1][b1]blend@clock=all_mode=normal:all_opacity=1,format=gbrp[bg];[1:v]fps=24:round=near:eof_action=pass,settb=1/24,setpts=N,format=rgba[card];[bg][card]overlay=format=rgb:alpha=straight:shortest=1,format=rgb24[v]'
inputs=ffbase()+['-stream_loop','-1','-i',str(OUT/'cycle.mkv'),'-f','concat','-safe','0','-i',str(OUT/'cards.ffconcat')]
cmd=inputs+audio()+['-filter_complex',filt,'-map','[v]','-map','2:a']+enc(OUT/'cached.mp4');t=time.monotonic();r=subprocess.run(cmd,capture_output=True,timeout=180);(OUT/'cached.log').write_bytes(r.stderr);assert r.returncode==0,r.stderr.decode();report['measurements']['cached_encode_seconds']=time.monotonic()-t;log('candidate encoded');save()
# Independently measure unencoded RGB and every opaque foreground pixel, including transitions.
cmd=inputs+['-filter_complex',filt,'-map','[v]','-an','-frames:v',str(N),'-f','rawvideo','-pix_fmt','rgb24',str(OUT/'cached.rgb')];t=time.monotonic();r=subprocess.run(cmd,capture_output=True,timeout=180);assert r.returncode==0,r.stderr.decode();report['measurements']['cached_rgb_validation_seconds']=time.monotonic()-t;assert (OUT/'cached.rgb').stat().st_size==refraw.stat().st_size==SIZE*N
ref=np.memmap(refraw,dtype=np.uint8,mode='r',shape=(N,1080,1920,3));other=np.memmap(OUT/'cached.rgb',dtype=np.uint8,mode='r',shape=ref.shape);maes=[];opaque_max=0;maxdiff=0;probes=[]
for f,key in enumerate(sequence):
 delta=np.abs(ref[f].astype(np.int16)-other[f].astype(np.int16));mask=np.asarray(cache[key][0].getchannel('A'))==255;opaque_max=max(opaque_max,int(delta[mask].max(initial=0)));maxdiff=max(maxdiff,int(delta.max()));maes.append(float(delta.mean()))
 if f in [0,1,P-1,P,P+1,N-2,N-1]:probes.append({'frame':f,'mean_abs_error':maes[-1],'max':int(delta.max())});Image.fromarray(ref[f]).resize((854,480)).save(OUT/f'ref-{f}.png');Image.fromarray(other[f]).resize((854,480)).save(OUT/f'cache-{f}.png')
report['unencoded']={'opaque_max_difference':opaque_max,'mean_abs_difference':float(np.mean(maes)),'max_channel_difference':maxdiff,'wrap_and_endpoint_probes':probes}
def decoded_stats(path):
 with av.open(str(path)) as c:
  c.streams.video[0].thread_count=1;frames=[fr.pts for fr in c.decode(video=0)]
 with av.open(str(path)) as c:
  packets=[bytes(p) for p in c.demux(audio=0) if p.size]
 return {'frames':len(frames),'video_pts':frames,'AAC_packets':len(packets),'AAC_payload_sha256':hashlib.sha256(b''.join(packets)).hexdigest()}
report['encoded']={'reference':decoded_stats(OUT/'reference.mp4'),'cached':decoded_stats(OUT/'cached.mp4')};report['encoded']['identical_AAC_packets']=report['encoded']['reference']['AAC_payload_sha256']==report['encoded']['cached']['AAC_payload_sha256'];report['encoded']['identical_video_timestamps']=report['encoded']['reference']['video_pts']==report['encoded']['cached']['video_pts'];report['temporary_bytes']=sum(p.stat().st_size for p in OUT.iterdir() if p.is_file());report['throughput_ratio_encode_only']=report['measurements']['reference_encode_seconds']/report['measurements']['cached_encode_seconds'];report['throughput_ratio_fixture_including_cache']=report['measurements']['reference_encode_seconds']/(report['measurements']['cached_encode_seconds']+report['measurements']['cache_create_seconds']+report['measurements']['foreground_png_prepare_seconds']);report['elapsed_seconds']=time.monotonic()-tim;save();log('COMPLETE',report['unencoded'],report['throughput_ratio_encode_only'])
