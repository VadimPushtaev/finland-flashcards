"""Validate owned sources and bind a metadata-only central attribution correction."""
from pathlib import Path
import hashlib,json,subprocess,time,yaml
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
proof=ROOT/'studio/production/remaining/source-note-correction.json'
p=json.loads(proof.read_text()); changes={r['path']:r for r in p['changes']}
sids=sorted(q.name for q in (ROOT/'studio/episodes').glob('hb-c09-*'))+['hb-c11-nodsituationer']
report={'central_proof':str(proof.relative_to(ROOT)),'central_proof_sha256':hashlib.sha256(proof.read_bytes()).hexdigest(),'episodes':{}}
for sid in sids:
 ep=ROOT/'studio/episodes'/sid
 r=subprocess.run(['.venv/bin/python','studio/tools/script.py','validate',sid,'--ready'],cwd=ROOT,capture_output=True,text=True)
 if r.returncode:raise RuntimeError(sid+' '+r.stdout+r.stderr)
 current={}
 for path in [ep/'sources.yaml',ep/'CREDITS.md']:
  if not path.exists():continue
  rel=str(path.relative_to(ROOT));sha=hashlib.sha256(path.read_bytes()).hexdigest()
  if rel in changes:assert sha==changes[rel]['after_sha256']
  current[rel]=sha
 handoff=ep/'production-handoff.json'
 if handoff.exists():
  h=json.loads(handoff.read_text());exportcredit=ROOT/h['credits_path']
  current[str(exportcredit.relative_to(ROOT))]=hashlib.sha256(exportcredit.read_bytes()).hexdigest()
  h['metadata_attribution_revision']={'proof':str(proof.relative_to(ROOT)),'current_metadata_sha256':current,'media_regeneration':False}
  handoff.write_text(json.dumps(h,ensure_ascii=False,indent=2)+'\n')
 slug=sid.removeprefix('hb-c09-');freeze=HERE/(slug+'-frozen-candidate.json')
 if freeze.exists() and yaml.safe_load((ep/'brief.yaml').read_text())['production_status']=='assets_ready':
  f=json.loads(freeze.read_text())
  for k,path in [('script_sha256',ep/'script.yaml'),('assets_sha256',ep/'assets.yaml'),('narration_metrics_sha256',ROOT/'studio/media'/sid/'narration/metrics.json'),('preflight_review_sha256',ep/'producer-preflight-review.json')]:assert f[k]==hashlib.sha256(path.read_bytes()).hexdigest(),sid+' '+k
 report['episodes'][sid]={'source_validation':'passed','current_metadata_sha256':current,'existing_four_input_freeze':'unchanged' if freeze.exists() else 'not yet frozen'}
 (HERE/'source-note-rebind.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(sid,'source validation and metadata binding passed',flush=True)
report['completed_at']=time.time();(HERE/'source-note-rebind.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
