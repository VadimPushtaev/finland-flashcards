"""Build review contacts only from every actual verifier-decoded export frame."""
from pathlib import Path
import json,yaml,hashlib,math,sys
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent;O=P/'full-export-audit';O.mkdir(exist_ok=True);owned=[s for s in json.loads((P/'worker-checkpoint.json').read_text())['exclusive_episodes']if s not in['hb-c11-trafik','hb-c11-nodsituationer']];out=[]
for sid in owned:
 E=R/'studio/episodes'/sid;brief=yaml.safe_load((E/'brief.yaml').read_text())
 if len(sys.argv)>1 and sid not in sys.argv[1:]:continue
 if brief.get('production_status')!='preview_ready'and sid not in sys.argv[1:]:continue
 r=json.loads((E/'render.json').read_text());v=json.loads((E/'render-check.json').read_text());assert r['sha256']==v['sha256']==hashlib.sha256((R/r['output']).read_bytes()).hexdigest();assert v['full_decode']=='passed';D=O/sid;D.mkdir(exist_ok=True);frames=[R/'studio/media'/sid/'render'/f'export-frame-{i:02}.png'for i in range(len(r['timeline']))];assert all(p.exists()for p in frames);contacts=[]
 for start in range(0,len(frames),20):
  chunk=frames[start:start+20];canvas=Image.new('RGB',(1920,math.ceil(len(chunk)/4)*294),'#ddd');d=ImageDraw.Draw(canvas)
  for n,p in enumerate(chunk):
   im=Image.open(p).convert('RGB');im.thumbnail((480,270));x=(n%4)*480;y=(n//4)*294;canvas.paste(im,(x,y));d.text((x+6,y+272),p.name,fill='black')
  dest=D/f'actual-{start:03}.jpg';canvas.save(dest);contacts.append(str(dest.relative_to(R)))
 # Up to12 evenly distributed actual body frames,plus actual source credit,at real640pixel viewport.
 body=[i for i,t in enumerate(r['timeline'])if t['kind']=='sentence'];selected=sorted(set(body[round(i*(len(body)-1)/min(11,len(body)-1))]for i in range(min(12,len(body))))) if len(body)>1 else body
 credit=next(i for i,t in enumerate(r['timeline'])if t['kind']=='credits');selected+= [credit];phone=Image.new('RGB',(1280,math.ceil(len(selected)/2)*384),'#ddd');d=ImageDraw.Draw(phone)
 for n,i in enumerate(selected):
  im=Image.open(frames[i]).convert('RGB').resize((640,360));x=n%2*640;y=n//2*384;phone.paste(im,(x,y));d.text((x+6,y+362),frames[i].name,fill='black')
 ph=D/'actual-phones.jpg';phone.save(ph);out.append(dict(section_id=sid,export=r['output'],export_sha256=r['sha256'],full_decode='passed',all_actual_decoded_frames=len(frames),contacts=contacts,simulated_phone_frames=selected,simulated_phone_contact=str(ph.relative_to(R)),frames=[dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())for p in frames],reviewed=False,physical_device_playback=False,whole_video_listening=False));print(sid,len(frames),len(contacts),flush=True)
target=P/'full-export-audit-candidates.json'
if len(sys.argv)>1 and target.exists():out=[r for r in json.loads(target.read_text())if r['section_id']not in sys.argv[1:]]+out
target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
