"""Alternating compositor microbenchmark; no encoder or mutable production paths."""
exec(open('studio/production/render-fast/pixel_check.py').read().split('for frame in [')[0])
import gc,statistics
results={m:[] for m in ['current','paste']}
for batch in range(8):
 for method in (['current','paste'] if batch%2==0 else ['paste','current']):
  start=time.perf_counter()
  for frame in range(24):
   t=(frame+batch*24)/(r['frames']-1)
   if method=='current':b=Image.alpha_composite(render.background_frame(back,t,s['render']['background_style']),card).convert('RGB').tobytes()
   else:
    b=back.resize((1920,1080),Image.Resampling.BILINEAR,box=render.background_extent(back.size,t,s['render']['background_style']));b.paste(rgb,(0,0),mask);b=b.tobytes()
  results[method].append(time.perf_counter()-start)
  gc.collect()
report={k:dict(batch_seconds=v,median_fps=24/statistics.median(v)) for k,v in results.items()};print(json.dumps(report,indent=2));Path('/tmp/hb-render-fast/compose-benchmark.json').write_text(json.dumps(report,indent=2)+'\n')
