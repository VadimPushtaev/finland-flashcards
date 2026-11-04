"""Bind current owned previews to their recorded real-export review evidence."""
from pathlib import Path
import datetime
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
PROD = Path(__file__).parent
load = lambda path: json.loads(path.read_text())
def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()
rows = []
for row in load(PROD / 'batch-handoff.json')['completed_previews']:
    sid = row['section_id']
    ep = ROOT / 'studio/episodes' / sid
    r = load(ep / 'producer-export-review.json')
    render = load(ep / 'render.json')
    check = load(ep / 'render-check.json')
    handoff = load(ep / 'production-handoff.json')
    canonical = ROOT / render['output']
    assert sha(canonical) == render['sha256'] == check['sha256'] == r['export_sha256'] == handoff['sha256'], sid
    assert check['full_decode'] == 'passed', sid
    assert (ep / 'CREDITS.md').read_bytes() == canonical.with_suffix('.CREDITS.md').read_bytes(), sid
    historical_script = r.get('source_script_sha256', r.get('script_sha256'))
    if historical_script:
        assert sha(ep / 'script.yaml') == historical_script, sid
    assert sha(ep / 'assets.yaml') == r['assets_sha256'], sid
    frames = r.get('frame_hashes', r.get('actual_export_frames_inspected', r.get('actual_exported_frames_inspected')))
    actual = list((ROOT / 'studio/media' / sid / 'render').glob('export-frame-*.png'))
    assert len(frames) == check['frame_exports'] == len(actual), sid
    historical_frame_hashes = all(isinstance(item, dict) for item in frames)
    if historical_frame_hashes:
        for item in frames:
            assert sha(ROOT / item['path']) == item['sha256'], (sid, item['path'])
    else:
        assert sorted(frames) == list(range(len(actual))), sid
    current_frame_hashes = [dict(path=str(path.relative_to(ROOT)),sha256=sha(path)) for path in sorted(actual)]
    amendment = r.get('source_note_metadata_amendment', {})
    for filename, key in [('sources.yaml', 'sources_sha256'), ('CREDITS.md', 'credits_sha256')]:
        expected = amendment.get(key, r.get(key))
        if expected:
            assert sha(ep / filename) == expected, (sid, filename)
    rows.append(dict(section_id=sid, canonical_output=render['output'], sha256=render['sha256'],
        seconds=render['seconds'], source_sentences=handoff['source_sentences'],
        historical_review_script_binding_present=bool(historical_script),
        script_sha256=sha(ep / 'script.yaml'), assets_sha256=sha(ep / 'assets.yaml'),
        sources_sha256=sha(ep / 'sources.yaml'), credits_sha256=sha(ep / 'CREDITS.md'),
        producer_review=dict(path=str((ep / 'producer-export-review.json').relative_to(ROOT)),sha256=sha(ep / 'producer-export-review.json')),
        historical_review_frame_hashes_present=historical_frame_hashes, current_frame_hashes=current_frame_hashes,
        actual_reviewed_export_frames=len(frames), picture_fraction=handoff['picture_fraction'],
        mix_sha256=check['encoded_audio_matches_mix']['mix_sha256']))
out = dict(checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    status='passed', current_previews=len(rows), source_pairs=sum(x['source_sentences'] for x in rows),
    seconds=sum(x['seconds'] for x in rows), actual_reviewed_frames=sum(x['actual_reviewed_export_frames'] for x in rows),
    episodes=rows, pending_replacements=load(PROD / 'batch-handoff.json').get('pending_replacements', []),
    checks='Current canonical hashes/decode evidence/credits equality/script+asset hashes/current source-credit amendments/all available historical actual-export PNG hashes checked, all current actual-export PNG hashes captured (two older reviews recorded frame indices only).',
    limits='Evidence consistency only; no new audio playback, whole-video listening, physical-device playback or user acceptance. Historical revisions are preserved.')
(PROD / 'current-export-binding-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print({k:v for k,v in out.items() if k not in ['episodes','pending_replacements']})
