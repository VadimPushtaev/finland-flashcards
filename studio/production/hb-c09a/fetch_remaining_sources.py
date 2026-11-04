"""Acquire only the coordinator-confirmed remaining Chapter 9 source masters."""
from pathlib import Path
import hashlib,json,subprocess,time,urllib.parse
import av,yaml
from PIL import Image
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
proposals=json.loads((P/'remaining-source-proposals.json').read_text());registry=json.loads((R/'studio/production/remaining/media-reservations.json').read_text());catalog=json.loads(Path('/tmp/hb-c06-current-music-catalogue.json').read_text());failures={};state={}
def info(path,url):return dict(path=str(path.relative_to(R)),url=url,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size)
def download(url,path,pinned=None):
    command=[str(R/'.venv/bin/python'),str(R/'studio/production/remaining/download.py'),'--url',url,'--output',str(path)]
    if pinned:command+=['--sha256',pinned]
    process=subprocess.Popen(command,cwd=R)
    while True:
        try:rc=process.wait(timeout=30);break
        except subprocess.TimeoutExpired:print('Source acquisition still running:',path,flush=True)
    if rc:raise RuntimeError('Shared downloader deferred or rejected '+str(path))
for sid,proposal in proposals.items():
    assert sid.startswith('hb-c09-');reservation=registry[sid];assert reservation['background_file']==proposal['background_file']
    track=next(m for m in catalog if m['isrc']==reservation['music_isrc']);assert track['title']==reservation['music_title']
    ep=R/'studio/episodes'/sid;sources=R/'studio/media'/sid/'sources';sources.mkdir(parents=True,exist_ok=True);pi=proposal['background_metadata'];photo_url=pi.get('thumburl',pi['url']);music_url='https://incompetech.com/music/royalty-free/mp3-royaltyfree/'+urllib.parse.quote(track['filename']);manifest=R/'studio/runtime'/f'{sid}-downloads.yaml';pins={x['path']:x['sha256'] for x in yaml.safe_load(manifest.read_text())['downloads']} if manifest.exists() else {}
    state[sid]=dict(status='acquiring',background=reservation['background_file'],music=track['title'],started=time.time());(P/'source-acquisition-progress.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
    try:
        download(photo_url,sources/'background.jpg',pins.get(str((sources/'background.jpg').relative_to(R))))
        with Image.open(sources/'background.jpg') as image:image.verify()
        download(music_url,sources/'music.mp3',pins.get(str((sources/'music.mp3').relative_to(R))))
        with av.open(str(sources/'music.mp3')) as audio:
            assert len(audio.streams.audio)==1;seconds=audio.duration/av.time_base;assert seconds>10
            music_tags=dict(audio.metadata)
        evidence=dict(photo_title=reservation['background_file'],photo=pi,music=track,context=proposal['context'],music_file_probe=dict(seconds=seconds,metadata=music_tags),reservation_snapshot=reservation)
        (ep/'media-sources.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
        manifest.write_text(yaml.safe_dump(dict(schema_version=1,downloads=[info(sources/'background.jpg',photo_url),info(sources/'music.mp3',music_url)]),allow_unicode=True,sort_keys=False))
        state[sid].update(status='acquired',finished=time.time(),music_seconds=seconds);print(sid,'acquired confirmed background and',track['title'],flush=True)
    except Exception as error:
        failures[sid]=str(error);state[sid].update(status='deferred',error=str(error));print(sid,'source acquisition deferred:',error,flush=True)
    (P/'source-acquisition-progress.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
if failures:raise SystemExit(json.dumps(failures,ensure_ascii=False))
(P/'remaining-sources-completed.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
