"""Build a current batch ledger without treating technical checks as acceptance."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
import hashlib
import yaml
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'studio/production/remaining'
def read(path):
    return yaml.load(path.read_text(),Loader=getattr(yaml,'CSafeLoader',yaml.SafeLoader))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def main(require_complete=False):
    rows=[];pending=[];problems=[]
    for item in read(BASE/'queue.yaml')['episodes']:
        section=item['section_id'];ep=ROOT/'studio/episodes'/section;brief=read(ep/'brief.yaml')
        if brief['production_status']!='preview_ready':
            pending.append({'section_id':section,'status':brief['production_status']});continue
        render=json.loads((ep/'render.json').read_text());check=json.loads((ep/'render-check.json').read_text());coverage=json.loads((ep/'picture-coverage.json').read_text());script=read(ep/'script.yaml')
        assert render['sha256']==check['sha256']==coverage['export_sha256'],section
        assert check['full_decode']=='passed' and check['encoded_audio_matches_mix'],section
        assert coverage['sentences']==len(script['sentences']) and coverage['picture_fraction']==1,section
        output=ROOT/render['output'];assert output.is_file(),section
        assert output.with_suffix('.CREDITS.md').read_bytes()==(ep/'CREDITS.md').read_bytes(),section
        proofs=[p for p in [ep/'producer-export-review.json',ep/'actual-export-review.json'] if p.exists()]
        current=[]
        for p in proofs:
            proof=json.loads(p.read_text())
            if proof.get('export_sha256')==render['sha256']:
                current.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p),whole_video_listening=proof.get('whole_video_listening',False),physical_device_playback=proof.get('physical_device_playback',False),user_acceptance=proof.get('user_acceptance',False)))
        if not current:problems.append({'section_id':section,'problem':'Current actual-export visual review proof missing'})
        rows.append(dict(section_id=section,owner=item['owner'],sentences=len(script['sentences']),output=render['output'],export_sha256=render['sha256'],seconds=render['seconds'],picture_fraction=coverage['picture_fraction'],decoded_video_frames=check['decoded_video_frames'],exported_still_samples=check['frame_exports'],current_actual_export_reviews=current,script_sha256=sha(ep/'script.yaml'),assets_sha256=sha(ep/'assets.yaml'),credits_sha256=sha(ep/'CREDITS.md')))
    report=dict(updated_utc=datetime.now(timezone.utc).isoformat(),requested_episodes=88,verified_preview_briefs=len(rows),pending=pending,review_evidence_problems=problems,episodes=rows,limits='Records current source/asset metadata hashes and checks matching verifier/coverage/export records and credits, and recorded actual-export visual review. Canonical MP4 hashes/assets/source fidelity are independently checked by chapter audits. Does not establish listening, physical-device playback or user acceptance.')
    (BASE/'batch-export-evidence.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(f'{len(rows)}/88 preview briefs; {len(pending)} pending; {len(problems)} current visual-proof gaps')
    if require_complete:assert len(rows)==88 and not pending and not problems, 'Batch evidence incomplete'
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--require-complete',action='store_true');main(p.parse_args().require_complete)
