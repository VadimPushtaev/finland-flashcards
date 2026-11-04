"""Preserve the verified preview and stage a foreground-only label wrap correction."""
from pathlib import Path
import json
import hashlib
import shutil
import sys
import yaml
from PIL import Image,ImageChops
R=Path(__file__).resolve().parents[3];SID='hb-c10-folkhalsa';E=R/'studio/episodes'/SID;M=R/'studio/media'/SID;P=Path(__file__).resolve().parent;STAGE=P/'folkhalsa-wrap-fix';STAGE.mkdir(exist_ok=True);REV=E/'revisions/pre-node-wrap';REV.mkdir(parents=True,exist_ok=True);MEDIA_REV=M/'revisions/pre-node-wrap';MEDIA_REV.mkdir(parents=True,exist_ok=True)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def preserve(source,dest):
    if dest.exists():assert sha(source)==sha(dest),(source,dest)
    else:shutil.copy2(source,dest)
report=json.loads((E/'render.json').read_text());assert report['sha256']=='eeafb11a2009556ebc4c9904c3fc8db1e81a08f22d3db66ec3c1c92862a3ff6c';assert sha(R/report['output'])==report['sha256']
preserve(R/report['output'],MEDIA_REV/'preview.mp4');preserve(M/'render/mix.wav',MEDIA_REV/'mix.wav')
for name in ['script.yaml','assets.yaml','render.json','render-check.json','picture-coverage.json','picture-diversity.json','production-handoff.json','brief.yaml','review.md','SCRIPT.md','CREDITS.md','foreground-assets.json','audio-diagnostics.json']:
    path=E/name
    if path.exists():preserve(path,REV/name)
for name in ['metrics.json','asr.json']:preserve(M/'narration'/name,REV/('narration-'+name))
preserve(M/'pictures/sentence-57.png',REV/'sentence-57.png');preserve(M/'render/frame-57.png',REV/'planned-frame-57.png');preserve(M/'render/export-frame-57.png',REV/'export-frame-57.png')
helper=P/'prepare_folkhalsa_pictures.py';old=helper.read_text();needle="label(d,(205,215),'inte fått alla vaccinationer',24)";assert old.count(needle)==1
new=old.replace(needle,"label(d,(205,215),'inte fått alla',24);label(d,(205,248),'vaccinationer',24)");(STAGE/'prepare_folkhalsa_pictures.py').write_text(new);preserve(helper,REV/'prepare_folkhalsa_pictures.py')
ns={'__file__':str(__file__)};exec(compile((P/'author_utkomststod.py').read_text().split('specs=')[0],'wrap-fix-primitives','exec'),ns);canvas,label,arrow=[ns[k] for k in ['canvas','label','arrow']];SOFT,GOLD=[ns[k] for k in ['SOFT','GOLD']]
# Use the original shield geometry rather than approximating it.
code=(P/'prepare_folkhalsa_pictures.py').read_text();exec(compile(code[code.index('def heart'):code.index('photos=json.loads')],'wrap-fix-health-objects','exec'),ns)
# Redraw from source commands,matching every unchanged pixel exactly.
im,d=canvas('Saknade vaccinationer');d.rounded_rectangle((75,185,335,330),radius=20,outline=SOFT,width=5);d.rounded_rectangle((425,185,685,330),radius=20,outline=SOFT,width=5);label(d,(205,215),'inte fått alla',24);label(d,(205,248),'vaccinationer',24);label(d,(555,215),'stadigvarande flytt',24);label(d,(380,245),'och',27);label(d,(380,145),'OM',28);arrow(d,(205,355),(330,465));arrow(d,(555,355),(430,465));ns['shield'](d,380,535,.8);label(d,(380,620),'kan få dem kostnadsfritt',27);im.save(STAGE/'sentence-57.png')
old_image=Image.open(M/'pictures/sentence-57.png').convert('RGB');difference=ImageChops.difference(old_image,im);box=difference.getbbox();assert box and box[0]>=30 and box[1]>=210 and box[2]<=380 and box[3]<=280,box
script=yaml.safe_load((E/'script.yaml').read_text());sys.path.insert(0,str(R/'studio/tools'));import render
render.configure_style(script);rows={r['sentence_id']:r for r in script['sentences']};row=script['sentences'][56];item=next(t for t in report['timeline'] if t.get('sentence_id')==row['sentence_id']);bg=script['render']['background_image'];images={row['render_image']:im,bg:Image.open(R/bg).convert('RGB')};card,_=render.make_card(script,item,rows,images);style=script['render']['background_style'];backdrop=render.prepare_background(images[bg],style);full=render.composite_rgb_frame(backdrop,(item['start_frame']+item['frames']/2)/(report['frames']-1),style,card.convert('RGB'),card.getchannel('A'));full.save(STAGE/'frame-57.png');full.resize((640,360)).save(STAGE/'phone-57.png')
clips=[dict(path=m['path'],sha256=sha(R/m['path'])) for m in json.loads((M/'narration/metrics.json').read_text())]
manifest=dict(section_id=SID,status='staged_not_applied',old_export_sha256=report['sha256'],old_export_backup=str((MEDIA_REV/'preview.mp4').relative_to(R)),report_backup=str(REV.relative_to(R)),script_sha256=sha(E/'script.yaml'),assets_sha256=sha(E/'assets.yaml'),old_picture_sha256=sha(M/'pictures/sentence-57.png'),new_picture_sha256=sha(STAGE/'sentence-57.png'),old_helper_sha256=sha(helper),new_helper_sha256=sha(STAGE/'prepare_folkhalsa_pictures.py'),unchanged_pixels_outside_bbox=box,unchanged_timeline=report['timeline'],frames=report['frames'],mix_sha256=sha(M/'render/mix.wav'),selected_narration=clips,source_word_sequence='inte fått alla vaccinationer',layout_change='Wrap that label onto two lines inside its existing node; no wording change.',encoder_started=False)
(STAGE/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print('Preserved original preview/reports and58takes. Staged pixel change bbox:',box)
