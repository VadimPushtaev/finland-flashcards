"""Replace concrete-subject diagram fallbacks with verified photographs."""
from pathlib import Path
import json,hashlib,re,sys
import yaml
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path.cwd();P=R/'studio/production/hb-c09a';FONT='/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
def info(p):return dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
for sid in sys.argv[1:]:
    ep=R/'studio/episodes'/sid;d=yaml.safe_load((ep/'script.yaml').read_text());assets=json.loads((ep/'foreground-assets.json').read_text());downloads=[]
    for file in sorted(ep.glob('photo-source-*.json')):
        rec=json.loads(file.read_text());index=rec['index'];row=d['sentences'][index-1];raw=R/rec['raw_path'];assert hashlib.sha256(raw.read_bytes()).hexdigest()==rec['download_sha256']
        im=Image.open(raw).convert('RGB');im.thumbnail((730,595),Image.Resampling.LANCZOS);canvas=Image.new('RGB',(760,720),'#243c32');canvas.paste(im,((760-im.width)//2,(630-im.height)//2+10))
        title=rec.get('caption',rec['title'].removeprefix('File:').rsplit('.',1)[0]);title=re.sub(r'\s*\((?:JOKA|HK|AM)[^)]+\)','',title)
        draw=ImageDraw.Draw(canvas);font=ImageFont.truetype(FONT,24);words=title.split();lines=[];line=''
        for word in words:
            test=(line+' '+word).strip()
            if line and draw.textlength(test,font=font)>700:lines.append(line);line=word
            else:line=test
        if line:lines.append(line)
        for k,line in enumerate(lines[:2]):draw.text((380,648+k*28),line,font=font,fill='#c5dfce',anchor='mt')
        path=R/row['render_image'];pending=path.with_name(path.stem+'.writing.png');canvas.save(pending);pending.replace(path)
        asset=dict(asset_id='picture_'+str(index).zfill(3),kind='foreground',visual_type='photograph',files=[info(path)],source_url=rec['imageinfo']['descriptionurl'],creator=rec['attribution'],reuse_terms=rec['license']+' '+rec['license_url'],required_credits=rec['title'].removeprefix('File:')+' — '+rec['attribution']+(' / '+rec['collection_credit'] if rec.get('collection_credit') else '')+'. '+rec['license']+'. '+rec['imageinfo']['descriptionurl']+' '+rec['license_url']+'. Proportionally resized without cropping; captioned on a neutral canvas; original source and license retained.',relevance_verification=rec['context']+' Primary object identity and reuse terms are preserved in '+str(file.relative_to(R))+'. Source metadata description: '+rec['description'],creation_method=dict(tool='studio/production/hb-c09a/prepare_photo_overrides.py',source_record=str(file.relative_to(R)),source_sentence_ids=[row['sentence_id']],transform='Complete source photograph proportionally reduced; short source-identity caption added below.'))
        assets[index-1]=asset;row['visual_cue']=rec['context']+' The complete source photograph is shown with its source-identity caption; no sensitive personal attributes are inferred.'
        downloads.append(dict(**info(raw),url=rec['imageinfo'].get('thumburl',rec['imageinfo']['url'])))
    for name,value in [('foreground-assets.json',json.dumps(assets,ensure_ascii=False,indent=2)+'\n'),('foreground-downloads.json',json.dumps(downloads,ensure_ascii=False,indent=2)+'\n'),('script.yaml',yaml.safe_dump(d,allow_unicode=True,sort_keys=False,width=100))]:
        pending=ep/(name+'.writing');pending.write_text(value);pending.replace(ep/name)
    print(sid,len(downloads),'source-photograph overrides prepared',flush=True)
