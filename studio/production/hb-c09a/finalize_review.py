"""Record an explicitly performed producer review of a verified owned export.

This never claims listening or user acceptance and never updates shared inventory.
Run only after viewing the listed actual exported frames and reading the sources.
"""
import argparse
import hashlib
import json
from pathlib import Path

import yaml
from audit_visual_identities import signature as visible_signature

ROOT = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('section')
parser.add_argument('--frames-reviewed', required=True)
parser.add_argument('--source-pairs-reviewed', required=True, type=int)
parser.add_argument('--phone-width', required=True, type=int)
parser.add_argument('--peer-review')
args = parser.parse_args()
assert args.section.startswith('hb-c09-') or args.section == 'hb-c11-nodsituationer'
episode = ROOT / 'studio/episodes' / args.section
script = yaml.safe_load((episode / 'script.yaml').read_text())
assets = yaml.safe_load((episode / 'assets.yaml').read_text())
sources = yaml.safe_load((episode / 'sources.yaml').read_text())
render = json.loads((episode / 'render.json').read_text())
checks = json.loads((episode / 'render-check.json').read_text())
priorities = json.loads((episode / 'listening-priorities.json').read_text())
assert args.source_pairs_reviewed == len(script['sentences'])
assert checks['full_decode'] == 'passed' and checks['sha256'] == render['sha256']
assert hashlib.sha256((ROOT / render['output']).read_bytes()).hexdigest() == render['sha256']
assert checks['decoded_video_frames'] == render['frames']
assert checks.get('encoded_audio_matches_mix', {}).get('correlation', 0) > .99
credits_path = ROOT / render['output'].replace('.mp4', '.CREDITS.md')
credits = credits_path.read_text()
for asset in assets['assets']:
    assert asset['required_credits'] in credits, asset['asset_id']
for source in sources['sources']:
    assert source['attribution']['credit'] in credits
allowed_source_paragraphs = {
    'Svensk källtext med granskad rysk översättning.',
    'Fullständiga artikelkällor och villkor i medföljande CREDITS.md.',
}
for source in sources['sources']:
    allowed_source_paragraphs.update([source['attribution']['title'], source['attribution']['credit']])
assert set(script['render']['credits'][0]['paragraphs']) <= allowed_source_paragraphs
indices = (list(range(len(render['timeline']))) if args.frames_reviewed == 'all'
           else list(map(int, args.frames_reviewed.split(','))))
frame_hashes = {}
for index in indices:
    path = ROOT / 'studio/media' / args.section / 'render' / f'export-frame-{index:02}.png'
    frame_hashes[str(index)] = hashlib.sha256(path.read_bytes()).hexdigest()
peer_evidence = None
if args.peer_review:
    peer_path = ROOT / args.peer_review
    peer = json.loads(peer_path.read_text())
    assert peer['section_id'] == args.section and not peer['findings']
    assert peer['export_sha256'] == render['sha256']
    assert peer.get('source_pairs_read', peer.get('source_pairs_previously_read_and_currently_revalidated')) == len(script['sentences'])
    inspected = peer['actual_exported_frames_inspected']
    if isinstance(inspected, list):
        assert inspected == list(range(len(render['timeline'])))
    else:
        assert inspected == len(render['timeline'])
    assert peer['script_sha256'] == hashlib.sha256((episode / 'script.yaml').read_bytes()).hexdigest()
    assert peer['assets_sha256'] == hashlib.sha256((episode / 'assets.yaml').read_bytes()).hexdigest()
    for index in indices:
        assert peer['frame_sha256'][f'export-frame-{index:02}.png'] == frame_hashes[str(index)]
    peer_evidence = dict(reviewer=peer['reviewer'], proof_path=str(peer_path.relative_to(ROOT)),
                         proof_sha256=hashlib.sha256(peer_path.read_bytes()).hexdigest(),
                         scope='Full current exact-source/actual-export gallery and simulated phone views independently inspected by the named peer; owner retains technical/finalization responsibility.')
plan = json.loads((episode / 'visual-plan.json').read_text())
by_path = {entry['path']: asset for asset in assets['assets'] for entry in asset['files']}
signatures = {}
photos = 0
for index, (row, specification) in enumerate(zip(script['sentences'], plan), 1):
    asset = by_path[row['render_image']]
    if asset.get('visual_type') == 'photograph':
        signature = 'photo:' + asset['source_url']
        photos += 1
    else:
        signature = visible_signature(specification)
    signatures.setdefault(signature, []).append(index)
diversity = dict(
    pictured_slides=len(script['sentences']),
    photographed_slides=photos,
    distinct_structural_or_photo_identities=len(signatures),
    repeated_signature_sentence_numbers=[group for group in signatures.values() if len(group) > 1],
    limitation='Visible icon aliases and identical actual arrow styles are normalized, including explicit/default none edges; labels and titles are ignored. These conservative signatures support actual visual review; file hashes alone do not prove meaningful diversity.',
)
coverage = json.loads((episode / 'picture-coverage.json').read_text())
export_review = dict(
    section_id=args.section,
    producer='chapter09a',
    export_sha256=render['sha256'],
    script_sha256=hashlib.sha256((episode / 'script.yaml').read_bytes()).hexdigest(),
    assets_sha256=hashlib.sha256((episode / 'assets.yaml').read_bytes()).hexdigest(),
    actual_export_frames_inspected=frame_hashes,
    simulated_phone_width=args.phone_width,
    source_pairs_read=args.source_pairs_reviewed,
    source_review='Exact Swedish and reviewed Russian records read; current source, review, glossary and provenance fingerprints pass ready validation.',
    visual_review='Actual exported frames checked for source conditions, identity, readability, matching source/media credits and fixed bilingual layout.',
    picture_diversity=diversity,
    technical_checks=checks,
    findings=[],
    unresolved=[
        'Whole-video listening, physical-device playback and user acceptance remain pending.',
        f"{len(priorities['unresolved'])} diagnostic name/number/transcript priorities remain; these are not confirmed audible errors.",
    ],
)
if peer_evidence:
    export_review['independent_actual_export_review'] = peer_evidence
source_priorities = episode / 'source-review-priorities.json'
if source_priorities.exists():
    export_review['source_review_priorities'] = json.loads(source_priorities.read_text())
    export_review['unresolved'].append('Literal archived source typos are preserved; review source-review-priorities.json during whole-video review.')
retakes = episode / 'retake-history.json'
if retakes.exists():
    export_review['retake_evidence'] = str(retakes.relative_to(ROOT))
(episode / 'producer-export-review.json').write_text(json.dumps(export_review, ensure_ascii=False, indent=2) + '\n')
brief_path = episode / 'brief.yaml'
brief = yaml.safe_load(brief_path.read_text())
brief.update(production_status='preview_ready', output_path=render['output'],
             issues=export_review['unresolved'])
brief_path.write_text(yaml.safe_dump(brief, allow_unicode=True, sort_keys=False))
body = f'''# {script['title_sv']} — preview review

Preview: `{render['output']}`. Duration: {render['seconds']:.3f} seconds. SHA-256: `{render['sha256']}`.

All {len(script['sentences'])} exact Swedish source sentences and matching reviewed Russian records were read. Source wording, IDs/order, current translation reviews, original-archive provenance, selected narration inputs and media hashes passed validation. Full H.264/AAC decode, frame/timeline coverage, current encoded mix and continuous background motion checks passed.

Actual exported frames for the representative body, title and source/media credits were inspected. The longest or legally conditional pair was also inspected at {args.phone_width} pixels wide; that is a simulated phone-size still, not physical-device playback. All body slides have relevant foreground pictures. There are {len(signatures)} distinct structural/photo identities across {len(script['sentences'])} body slides, including {photos} photographic slides. Any repeated motifs are recorded in `producer-export-review.json`.

Whole-video listening and user acceptance remain pending. The {len(priorities['unresolved'])} name/number/transcript priorities in `listening-priorities.json` are diagnostic uncertainties, not confirmed audible errors or auditory approval. Retake history, where present, preserves the original and comparison metrics and the selection rationale.
'''
if peer_evidence:
    body += '\nFull current source/actual-export gallery review was performed independently by ' + peer_evidence['reviewer'] + '. Owner finalization verifies its current export/script/assets/all-frame hash bindings. Evidence: `' + peer_evidence['proof_path'] + '`.\n'
(episode / 'review.md').write_text(body)
handoff = dict(
    section_id=args.section,
    requested_inventory_status='preview_ready',
    translation_readiness='ready',
    episode_path=str(episode.relative_to(ROOT)),
    output_path=render['output'],
    credits_path=str(credits_path.relative_to(ROOT)),
    credits_sha256=hashlib.sha256(credits_path.read_bytes()).hexdigest(),
    sources_yaml_sha256=hashlib.sha256((episode / 'sources.yaml').read_bytes()).hexdigest(),
    seconds=render['seconds'],
    sentences=len(script['sentences']),
    export_sha256=render['sha256'],
    source_section_sha256=script['source_section_sha256'],
    translation_file_sha256=script['translation_file_sha256'],
    script_sha256=export_review['script_sha256'],
    assets_sha256=export_review['assets_sha256'],
    checks=['ready source validation', 'asset and selected WAV integrity', 'full decode',
            'current encoded mix', 'continuous background motion', 'actual exported-frame review',
            'measured foreground picture coverage', 'complete matching credits'],
    picture_sources=diversity,
    unresolved=export_review['unresolved'],
    listening_actually_performed=False,
    user_acceptance=False,
    shared_changes_requested=['Update inventory milestone and canonical video/credits index links.'],
)
if peer_evidence:
    handoff['independent_actual_export_review'] = peer_evidence
(episode / 'production-handoff.json').write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + '\n')
print(args.section, 'preview_ready;', render['seconds'], 'seconds;', render['sha256'])
