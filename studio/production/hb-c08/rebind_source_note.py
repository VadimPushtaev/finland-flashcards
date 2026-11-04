"""Rebind review metadata after the coordinator's proven sidecar-only correction."""
from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3];PROD=Path(__file__).parent;PROOF='studio/production/remaining/source-note-correction.json';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();ids=[r['section_id'] for r in load(PROD/'progress.json')['episodes']]+['hb-c11-trafik'];changes=[]
for sid in ids:
 ep=ROOT/'studio/episodes'/sid
 for name in ['producer-preflight-review.json','producer-export-review.json','production-handoff.json']:
  p=ep/name
  if not p.exists():continue
  j=load(p);old=sha(p);amend={'at':stamp,'proof':PROOF,'sources_sha256':sha(ep/'sources.yaml'),'credits_sha256':sha(ep/'CREDITS.md') if (ep/'CREDITS.md').exists() else None,'change':'Only irrelevant interview-coaching sentence removed from InfoFinland source-preparation note; media,script,assets,timeline,frames and audio unchanged.'}
  if 'credits_sha256' in j:j['credits_sha256']=amend['credits_sha256']
  if 'sources_sha256' in j:j['sources_sha256']=amend['sources_sha256']
  j['source_note_metadata_amendment']=amend;p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n');changes.append(dict(path=str(p.relative_to(ROOT)),before_sha256=old,after_sha256=sha(p)))
freezes=load(PROD/'ready-export-freezes.json')
for row in freezes['episodes']:
 inp=row['input_snapshots']['producer_preflight'];path=ROOT/inp['path'];actual=sha(path)
 if actual==inp['sha256']:continue
 row.setdefault('prior_metadata_bound_preflight',[]).append(inp.copy());dest=ROOT/'studio/production/hb-c08/freezes'/row['section_id']/f'producer_preflight-{actual}.json';dest.write_bytes(path.read_bytes());inp.update(sha256=actual,snapshot=str(dest.relative_to(ROOT)));row['metadata_amendment_proof']=PROOF
(PROD/'ready-export-freezes.json').write_text(json.dumps(freezes,ensure_ascii=False,indent=2)+'\n')
b=load(PROD/'batch-handoff.json')
for i,row in enumerate(b['completed_previews']):b['completed_previews'][i]=load(ROOT/row['episode_path']/'production-handoff.json')
b['updated_at']=stamp;b['source_note_metadata_amendment']=PROOF;(PROD/'batch-handoff.json').write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');(PROD/'source-note-review-rebinding.json').write_text(json.dumps(dict(at=stamp,central_proof=PROOF,changed_review_records=changes,remaining_media_unchanged=True),indent=2)+'\n');print(len(changes),'review records rebound; prior preflight snapshots retained')
