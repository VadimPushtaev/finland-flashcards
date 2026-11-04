"""Record an actually performed owned source/still review, never listening."""
import argparse
import hashlib
import json
from pathlib import Path
import time

import yaml

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('section')
parser.add_argument('--phone-indices', required=True)
parser.add_argument('--findings', default='')
parser.add_argument('--pending-asr', action='store_true')
args = parser.parse_args()
ROOT = Path(__file__).resolve().parents[3]
assert args.section == 'hb-c11-nodsituationer'
episode = ROOT / 'studio/episodes' / args.section
script = yaml.safe_load((episode / 'script.yaml').read_text())
assets = yaml.safe_load((episode / 'assets.yaml').read_text())
directory = ROOT / 'studio/media' / args.section / 'render'
frames = sorted(directory.glob('frame-*.png'))
assert len(frames) == len(script['sentences']) + 3
for asset in assets['assets']:
    for entry in asset['files']:
        assert hashlib.sha256((ROOT / entry['path']).read_bytes()).hexdigest() == entry['sha256']
coverage = json.loads((episode / 'picture-coverage-planned.json').read_text())
assert coverage['picture_fraction'] >= .9
proof = dict(
    section_id=args.section,
    source_pairs_read=len(script['sentences']),
    source_review='Every exact Swedish sentence and current reviewed Russian pair was read during source-specific planning; conditional clauses were checked again in the paired stills.',
    preflight_frames_inspected={p.stem: hashlib.sha256(p.read_bytes()).hexdigest() for p in frames},
    phone_width=768,
    phone_indices=list(map(int, args.phone_indices.split(','))),
    script_sha256=hashlib.sha256((episode / 'script.yaml').read_bytes()).hexdigest(),
    assets_sha256=hashlib.sha256((episode / 'assets.yaml').read_bytes()).hexdigest(),
    findings=args.findings,
    picture_coverage=coverage['picture_fraction'],
    inspected_at=time.time(),
    listening=False,
    audio_diagnostics='pending' if args.pending_asr else 'recorded separately',
    unresolved=['Whole-video listening, physical-device playback, final export verification and user acceptance remain pending.'],
)
if args.pending_asr:
    proof['unresolved'].insert(0, 'The assigned ASR job is still running; diagnostic review remains pending.')
(episode / 'producer-preflight-review.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
brief_path = episode / 'brief.yaml'
brief = yaml.safe_load(brief_path.read_text())
brief.update(production_status='script_ready' if args.pending_asr else 'assets_ready', issues=proof['unresolved'])
brief_path.write_text(yaml.safe_dump(brief, allow_unicode=True, sort_keys=False))
timeline = json.loads((directory / 'timeline.json').read_text())
print(args.section, brief['production_status'], ';', len(frames), 'stills reviewed;', timeline[-1].get('end_seconds', timeline[-1]))
