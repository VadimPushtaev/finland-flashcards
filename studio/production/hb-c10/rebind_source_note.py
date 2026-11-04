"""Validate current owned sources and rebind metadata-only attribution corrections."""
from pathlib import Path
import json,hashlib,sys,shutil,datetime
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent;sys.path.insert(0,str(R));from studio.tools import script
owned=[s for s in json.loads((P/'worker-checkpoint.json').read_text())['exclusive_episodes']if s not in ['hb-c11-trafik','hb-c11-nodsituationer']];assert len(owned)==18
proof=R/'studio/production/remaining/source-note-correction.json';assert proof.exists();results=[]
for sid in owned:
 e=R/'studio/episodes'/sid;context=script.load_context(sid);data=script.read(e/'script.yaml');script.validate(data,context,ready=True);script.require(script.read(e/'sources.yaml')==script.source_snapshot(context),'Stale source-credit snapshot:'+sid);readable=script.review_markdown(data,context);(e/'SCRIPT.md').write_text(readable,encoding='utf-8');script.require((e/'SCRIPT.md').read_text()==readable,'Readable script mismatch:'+sid)
 digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();hashes={n:digest(e/n)for n in ['script.yaml','sources.yaml','CREDITS.md']if(e/n).exists()};
 if(e/'assets.yaml').exists():hashes['assets.yaml']=digest(e/'assets.yaml')
 binding=dict(scope='Only irrelevant interview-coaching sentence removed from shared InfoFinland preparation metadata. Source bodies,translated panels,pictures,timing,audio and encodedMP4 unchanged.',shared_proof=str(proof.relative_to(R)),shared_proof_sha256=digest(proof),current_hashes=hashes,ready_source_validation='passed')
 for name in ['prerender-handoff.json','production-handoff.json']:
  path=e/name
  if not path.exists():continue
  backup=e/'revisions/source-note-correction'/name;backup.parent.mkdir(parents=True,exist_ok=True)
  if not backup.exists():shutil.copyfile(path,backup)
  j=json.loads(path.read_text());j['source_note_correction']=binding
  if 'hashes'in j:j['hashes'].update({n:h for n,h in hashes.items()if n in j['hashes']or n=='sources.yaml'})
  path.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
 (e/'source-note-correction-binding.json').write_text(json.dumps(binding,ensure_ascii=False,indent=2)+'\n');results.append(dict(section_id=sid,exact_pairs=len(data['sentences']),**binding));print('PASS',sid,len(data['sentences']),flush=True)
(P/'source-note-validation-rebind.json').write_text(json.dumps(dict(updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),episodes=results),ensure_ascii=False,indent=2)+'\n')
