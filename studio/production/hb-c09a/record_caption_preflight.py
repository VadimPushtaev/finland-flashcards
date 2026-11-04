"""Record the producer's performed caption refresh review, without audio approval."""
from pathlib import Path
import hashlib
import json
import time

import yaml

ROOT = Path(__file__).resolve().parents[3]
REVIEWS = {
    'vardledighet': [11],
    'foraldraledighet': [9, 14],
    'familjeformer': [18],
    'kon': [57],
    'forandring': [59],
}
for slug, indices in REVIEWS.items():
    sid = 'hb-c09-' + slug
    episode = ROOT / 'studio/episodes' / sid
    proof_path = episode / 'producer-preflight-review.json'
    proof = json.loads(proof_path.read_text()) if proof_path.exists() else {}
    script = yaml.safe_load((episode / 'script.yaml').read_text())
    proof.update(
        section_id=sid,
        source_pairs_read=len(script['sentences']),
        prior_review='All source pairs and the earlier complete timed-still contact sheets were inspected; conditional and longest pairs were also inspected at simulated phone width.',
        caption_refresh_review=dict(
            inspected_at=time.time(),
            phone_width=768,
            sentence_numbers=indices,
            findings='Long source labels now fit using visible line-end hyphenation; exact bilingual source text and selected narration are unchanged.',
            actual_frame_sha256={str(index): hashlib.sha256((ROOT / 'studio/media' / sid / 'render' / f'frame-{index:02}.png').read_bytes()).hexdigest() for index in indices},
        ),
        script_sha256=hashlib.sha256((episode / 'script.yaml').read_bytes()).hexdigest(),
        assets_sha256=hashlib.sha256((episode / 'assets.yaml').read_bytes()).hexdigest(),
        listening=False,
        unresolved=['Whole-video listening, physical-device playback, export verification and user acceptance remain pending.'],
    )
    proof_path.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
    brief_path = episode / 'brief.yaml'
    brief = yaml.safe_load(brief_path.read_text())
    brief.update(production_status='assets_ready', issues=proof['unresolved'])
    brief_path.write_text(yaml.safe_dump(brief, allow_unicode=True, sort_keys=False))
    print(sid, 'assets_ready; producer caption refresh reviewed.')
