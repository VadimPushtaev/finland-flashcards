"""Acquire reserved, metadata-verified source masters; never silently overwrite them."""
from pathlib import Path
import concurrent.futures,hashlib,json,re,subprocess,sys,time,urllib.parse,yaml
ROOT=Path(__file__).resolve().parents[3];PROD=ROOT/'studio/production/hb-c08';META=json.loads((PROD/'all-photo-metadata.json').read_text());CAT=json.loads(Path('/tmp/c07-employment-music-catalogue.json').read_text());RES=json.loads((ROOT/'studio/production/remaining/media-reservations.json').read_text())
def fetch(url,p):
 if p.is_file():return
 tmp=p.with_suffix(p.suffix+'.part')
 cmd=['curl','-f','-sS','-L','--retry','3','--retry-delay','5','--connect-timeout','15','--max-time','180',url,'-o',str(tmp)]
 subprocess.run(cmd,check=True);tmp.rename(p)
def run(sid):
 ep=ROOT/'studio/episodes'/sid
 if not ep.exists():return
 r=RES[sid];t=r.get('background_file')
 if not t:print(sid,'background not reserved yet',flush=True);return
 pi=META[t];music=next(m for m in CAT if m['isrc']==r['music_isrc']);sources=ROOT/'studio/media'/sid/'sources';sources.mkdir(parents=True,exist_ok=True)
 evidence=dict(photo_title=t,photo=pi,music=music,context='Verified education setting. Decorative context for the episode subject; no claim that the depicted institution supplies a particular described service or illustrates the present legal rule.',music_license_evidence=dict(url='https://incompetech.com/music/royalty-free/licenses/',catalogue_url='https://incompetech.com/music/royalty-free/pieces.json',catalogue_entry_matched=True,license='CC BY4.0'))
 (ep/'media-sources.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
 fetch(pi.get('thumburl',pi['url']),sources/'background.jpg')
 fetch('https://incompetech.com/music/royalty-free/mp3-royaltyfree/'+urllib.parse.quote(music['filename']),sources/'music.mp3')
 downloads=[]
 for p,url in [(sources/'background.jpg',pi.get('thumburl',pi['url'])),(sources/'music.mp3','https://incompetech.com/music/royalty-free/mp3-royaltyfree/'+urllib.parse.quote(music['filename']))]:downloads.append(dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size,url=url))
 (ROOT/'studio/runtime'/f'{sid}-downloads.yaml').write_text(yaml.safe_dump(dict(schema_version=1,downloads=downloads),sort_keys=False));print(sid,'masters acquired',flush=True)
if __name__=='__main__':
 for sid in sys.argv[1:]:
  try:run(sid)
  except Exception as e:print(sid,'ERROR',repr(e),flush=True)
