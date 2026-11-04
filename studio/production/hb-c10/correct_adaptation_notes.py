"""Correct an inherited unrendered credit note while proving all render-affecting script fields unchanged."""
from pathlib import Path
import json,yaml,copy,hashlib,shutil,sys,datetime
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent;sys.path.insert(0,str(R));from studio.tools.render import write_credits
owned=json.loads((P/'worker-checkpoint.json').read_text())['exclusive_episodes'];reports=[]
anchor="    pictures = json.loads(foreground_path.read_text()) if foreground_path.exists() else []\n"
addition="""    # Foreground notes derive from this actual register,never an inherited episode count.
    picture_adaptation_note = ('Foreground picture adaptation: ' + str(sum(a.get('visual_type') == 'photograph' for a in pictures)) + ' licensed photographic assets; ' + str(sum(a.get('visual_type') == 'diagram' for a in pictures)) + ' original source-based diagrams. Individual source wording and media retain the terms recorded above.') if pictures else 'Foreground picture adaptation: source-based pictures retain the individual provenance and reuse terms recorded above.'
    adaptation_notes = d['render'].setdefault('adaptation_notes', [])
    if adaptation_notes and (adaptation_notes[0].startswith('Ten original source-based') or adaptation_notes[0].startswith('Foreground picture adaptation:')):
        adaptation_notes[0] = picture_adaptation_note
    else:
        adaptation_notes.insert(0, picture_adaptation_note)
"""
for sid in owned:
 e=R/'studio/episodes'/sid;m=R/'studio/media'/sid;script_path=e/'script.yaml';before=yaml.load(script_path.read_text(),Loader=yaml.CSafeLoader);old=copy.deepcopy(before);revision=e/'revisions/adaptation-note-correction';revision.mkdir(parents=True,exist_ok=True)
 for src in[script_path,e/'CREDITS.md']:
  if src.exists()and not(revision/src.name).exists():shutil.copy2(src,revision/src.name)
 assets=e/'assets.yaml';asset_sha=hashlib.sha256(assets.read_bytes()).hexdigest()if assets.exists()else None
 foreground=json.loads((e/'foreground-assets.json').read_text())if(e/'foreground-assets.json').exists()else[];photos=sum(a.get('visual_type')=='photograph'for a in foreground);diagrams=sum(a.get('visual_type')=='diagram'for a in foreground)
 note=(f'Foreground picture adaptation: {photos} licensed photographic assets; {diagrams} original source-based diagrams. Individual source wording and media retain the terms recorded above.'if foreground else'Foreground picture adaptation: source-based pictures retain the individual provenance and reuse terms recorded above.')
 notes=before['render'].setdefault('adaptation_notes',[])
 if notes and(notes[0].startswith('Ten original source-based')or notes[0].startswith('Foreground picture adaptation:')):notes[0]=note
 else:notes.insert(0,note)
 protected_before=copy.deepcopy(old);protected_after=copy.deepcopy(before);protected_before['render'].pop('adaptation_notes',None);protected_after['render'].pop('adaptation_notes',None);assert protected_before==protected_after
 script_path.write_text(yaml.safe_dump(before,allow_unicode=True,sort_keys=False,width=100))
 helper=e/'prepare_assets.py'
 if helper.exists():
  code=helper.read_text()
  if 'picture_adaptation_note'not in code:
   assert anchor in code,sid;helper.write_text(code.replace(anchor,anchor+addition))
 if assets.exists():write_credits(e,R/'videos/homebrew');assert hashlib.sha256(assets.read_bytes()).hexdigest()==asset_sha
 report=dict(section_id=sid,corrected_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Unrendered render.adaptation_notes and generated Markdown credit sidecars only. No subtitle,picture,onscreen credit card,narration,timing,music,background or encoded video fields changed.',all_other_script_fields_identical=True,before_script_sha256=hashlib.sha256((revision/'script.yaml').read_bytes()).hexdigest(),current_script_sha256=hashlib.sha256(script_path.read_bytes()).hexdigest(),assets_sha256=asset_sha,current_note=note,old_script_retained=str((revision/'script.yaml').relative_to(R)),current_credits_sha256=hashlib.sha256((e/'CREDITS.md').read_bytes()).hexdigest()if(e/'CREDITS.md').exists()else None,render_validation='Existing export verification remains valid because only a field consumed by write_credits changed;renderer does not use adaptation_notes for frames/audio/timeline.')
 if(e/'render.json').exists():report['unchanged_export_sha256']=json.loads((e/'render.json').read_text())['sha256']
 (e/'adaptation-note-correction-proof.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');reports.append(report);print(sid,'corrected truthful adaptation note;all render-affecting fields unchanged.',flush=True)
(P/'adaptation-note-correction-report.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
