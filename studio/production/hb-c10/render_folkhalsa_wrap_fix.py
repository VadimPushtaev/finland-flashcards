"""Apply the separately inspected wrap repair and render in a future assigned slot.

Do not launch without the coordinator's encoder allocation. The original complete
preview,reports,selected takes and mix are preserved before this entry point.
"""
from pathlib import Path
import json
import hashlib
import shutil
import subprocess
import yaml
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent;STAGE=P/'folkhalsa-wrap-fix';SID='hb-c10-folkhalsa';E=R/'studio/episodes'/SID;M=R/'studio/media'/SID;manifest=json.loads((STAGE/'manifest.json').read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def takes_unchanged():
    for row in manifest['selected_narration']:assert sha(R/row['path'])==row['sha256'],row['path']
old_output=R/'videos/homebrew/hb-c10-03-folkhalsa.mp4';assert sha(old_output)==manifest['old_export_sha256'];assert sha(E/'script.yaml')==manifest['script_sha256'];assert sha(E/'assets.yaml')==manifest['assets_sha256'];assert sha(P/'prepare_folkhalsa_pictures.py')==manifest['old_helper_sha256'];takes_unchanged()
assert sha(STAGE/'sentence-57.png')==manifest['new_picture_sha256'];assert sha(STAGE/'prepare_folkhalsa_pictures.py')==manifest['new_helper_sha256'];shutil.copyfile(STAGE/'sentence-57.png',M/'pictures/sentence-57.png');shutil.copyfile(STAGE/'prepare_folkhalsa_pictures.py',P/'prepare_folkhalsa_pictures.py')
file_record=dict(path='studio/media/'+SID+'/pictures/sentence-57.png',sha256=manifest['new_picture_sha256'],bytes=(M/'pictures/sentence-57.png').stat().st_size)
foreground=json.loads((E/'foreground-assets.json').read_text());assets=yaml.safe_load((E/'assets.yaml').read_text())
for collection in [foreground,assets['assets']]:
    picture=next(a for a in collection if a['asset_id']=='picture-057');picture['files']=[file_record];picture.setdefault('creation_method',{})['revision']='Wrap the same source label onto two lines inside its existing node. Geometry,word sequence,timing and narration unchanged.'
(E/'foreground-assets.json').write_text(json.dumps(foreground,ensure_ascii=False,indent=2)+'\n');(E/'assets.yaml').write_text(yaml.safe_dump(assets,allow_unicode=True,sort_keys=False,width=100))
b=yaml.safe_load((E/'brief.yaml').read_text());b.update(production_status='assets_ready',issues=['Corrected node wrap is rendering; previous complete preview and reports preserved under revisions/pre-node-wrap. Reverification pending.']);(E/'brief.yaml').write_text(yaml.safe_dump(b,allow_unicode=True,sort_keys=False,width=100))
if (E/'production-handoff.json').exists():
    handoff=json.loads((E/'production-handoff.json').read_text());handoff.update(status='correction_rendering',current_claim='Previous preview is preserved; corrected canonical export is not yet verified.');(E/'production-handoff.json').write_text(json.dumps(handoff,ensure_ascii=False,indent=2)+'\n')
print('Applied only the inspected label wrap; all58selected takes unchanged. Starting assigned full render.',flush=True)
subprocess.run([str(R/'studio/runtime/.venv/bin/python'),'studio/tools/validate_assets.py',SID],cwd=R,check=True)
subprocess.run([str(R/'studio/runtime/.venv/bin/python'),'studio/tools/render.py',SID],cwd=R,check=True)
current=json.loads((E/'render.json').read_text());assert current['timeline']==manifest['unchanged_timeline'];assert current['frames']==manifest['frames'];assert sha(M/'render/mix.wav')==manifest['mix_sha256'];takes_unchanged();assert current['sha256']!=manifest['old_export_sha256']
proof=dict(section_id=SID,old_export_sha256=manifest['old_export_sha256'],new_export_sha256=current['sha256'],frames=current['frames'],seconds=current['seconds'],timeline_identical=True,selected_narration_hashes_identical=True,mix_wav_sha256=manifest['mix_sha256'],mix_bit_identical=True,changed_picture='picture-057',new_picture_sha256=manifest['new_picture_sha256'],repair='Same label wrapped onto two lines; no source wording,geometry outside label region,timing or audio change.',full_verification_pending=True)
(E/'wrap-correction-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n');print(json.dumps(proof),flush=True)
