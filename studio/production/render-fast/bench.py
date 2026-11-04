"""Isolated throughput/fidelity prototype; writes only /tmp, never canonical exports."""
from pathlib import Path
import argparse,gc,hashlib,json,math,os,resource,subprocess,sys,time
import av,imageio_ffmpeg,numpy as np,yaml
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'studio/tools'));import render
OUT=Path('/tmp/hb-render-fast');OUT.mkdir(exist_ok=True)
def rss(pid):
 try:
  txt=Path(f'/proc/{pid}/status').read_text();return int(next(x for x in txt.splitlines() if x.startswith('VmHWM:')).split()[1])
 except (FileNotFoundError,StopIteration):return 0

def main():
 a=argparse.ArgumentParser();a.add_argument('--variant',choices=['pillow','pillow-half','pillow-paste','pillow-paste-half','ffmpeg','perspective'],required=True);a.add_argument('--scale',type=int,default=1);a.add_argument('--frames',type=int,default=120);a.add_argument('--start',type=int,default=0);a.add_argument('--audio',action='store_true');args=a.parse_args();sid='hb-c08-hux';script=yaml.safe_load((ROOT/'studio/episodes'/sid/'script.yaml').read_text());report=json.loads((ROOT/'studio/episodes'/sid/'render.json').read_text());render.configure_style(script);rows={r['sentence_id']:r for r in script['sentences']};first=report['timeline'][1];images={p:Image.open(ROOT/p).convert('RGB') for p in {script['render']['background_image'],script['sentences'][0]['render_image']}};back=render.prepare_background(images[script['render']['background_image']],script['render']['background_style']);card,_=render.make_card(script,first,rows,images);cardpath=OUT/'card.png';card.save(cardpath);basepath=OUT/'background.png';prep=time.perf_counter();back.convert('RGB').resize((2200*args.scale,1238*args.scale),Image.Resampling.BICUBIC).save(basepath);prep=time.perf_counter()-prep
 ff=imageio_ffmpeg.get_ffmpeg_exe();stem=f'{args.variant}-scale{args.scale}-start{args.start}'+('-audio' if args.audio else '');video=OUT/(stem+'.mp4');logpath=OUT/(stem+'.log');common=[ff,'-y','-hide_banner','-loglevel','error','-threads','1','-filter_threads','1','-filter_complex_threads','1'];enc=['-an','-c:v','libx264','-preset','fast','-crf','20','-threads','1','-pix_fmt','yuv420p','-frames:v',str(args.frames),str(video)];phase=f'(0.5+0.5*sin(2*PI*{script["render"]["background_style"]["motion_cycles"]}*((on+{args.start})/{report["frames"]-1})))';z=f'(1.06+(1.219-1.06)*{phase})';x=f'((iw-iw/zoom)*(0.15+0.7*{phase}))';y=f'((ih-ih/zoom)*(0.15+0.7*{phase}))'
 if args.variant.startswith('pillow'):cmd=common+['-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-']+enc
 else:
  filt=f"[0:v]format=gbrp,zoompan=z='{z}':x='{x}':y='{y}':d={args.frames}:s=1920x1080:fps=24,format=rgb24[bg];[1:v]format=rgba[card];[bg][card]overlay=x=0:y=0:format=rgb:alpha=straight:shortest=1,format=yuv420p[v]"
  if args.variant=='perspective':
   left=f'(W-W/{z})*(0.15+0.7*{phase})';top=f'(H-H/{z})*(0.15+0.7*{phase})';right=f'({left})+W/{z}';bottom=f'({top})+H/{z}';filt=f"[0:v]format=gbrp,loop=loop=-1:size=1:start=0,setpts=N/(24*TB),perspective=x0='{left}':y0='{top}':x1='{right}':y1='{top}':x2='{left}':y2='{bottom}':x3='{right}':y3='{bottom}':sense=source:eval=frame:interpolation=linear,scale=1920:1080:flags=bilinear,format=rgb24[bg];[1:v]format=rgba[card];[bg][card]overlay=x=0:y=0:format=rgb:alpha=straight:shortest=1,format=yuv420p[v]"
  cmd=common+['-i',str(basepath),'-f','rawvideo','-pix_fmt','rgba','-s','1920x1080','-r','24','-i','-','-filter_complex',filt,'-map','[v]']+enc
 if args.variant in ('pillow-half','pillow-paste-half'):back=back.resize((1100,619),Image.Resampling.LANCZOS)
 card_rgb=card.convert('RGB');card_alpha=card.getchannel('A')
 if args.audio:
  insertion=cmd.index('-an');cmd[insertion:insertion+1]=['-i',str(ROOT/'studio/media'/sid/'render/mix.wav'),'-c:a','aac','-b:a','192k','-movflags','+faststart']
 started=time.perf_counter();peak_child=0
 with logpath.open('wb') as err:
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=err,cwd=ROOT);cached=card.tobytes()
  try:
   for i in range(args.frames):
    if args.variant.startswith('pillow-paste'):
     img=back.resize((1920,1080),Image.Resampling.BILINEAR,box=render.background_extent(back.size,(args.start+i)/(report['frames']-1),script['render']['background_style']));img.paste(card_rgb,(0,0),card_alpha);frame=img.tobytes()
    elif args.variant.startswith('pillow'):frame=Image.alpha_composite(render.background_frame(back,(args.start+i)/(report['frames']-1),script['render']['background_style']),card).convert('RGB').tobytes()
    else:frame=cached
    p.stdin.write(frame);peak_child=max(peak_child,rss(p.pid))
   p.stdin.close();code=p.wait()
  except BaseException:
   p.kill();p.wait();raise
 elapsed=time.perf_counter()-started
 if code:raise RuntimeError(logpath.read_text())
 result=dict(variant=args.variant,scale=args.scale,start_frame=args.start,frames=args.frames,seconds=elapsed,fps=args.frames/elapsed,prepare_upscaled_background_seconds=prep,python_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,ffmpeg_peak_rss_kib=peak_child,source_output_sha256=report['sha256'],output=str(video),video_sha256=hashlib.sha256(video.read_bytes()).hexdigest(),command=cmd,background_source=str(ROOT/script['render']['background_image']),limitations=['Prototype reuses one exact bilingual card for throughput measurement; no canonical file or narration modified.'])
 (OUT/(stem+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
