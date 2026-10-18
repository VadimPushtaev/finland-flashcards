"""Audit a chapter's source fidelity, distinct media and verified video exports."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import wave

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from studio.tools import script as scripts
from studio.tools.outputs import export_stem


def digest(path):
    """Hash a deliverable or retained production asset."""
    checksum = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            checksum.update(block)
    return checksum.hexdigest()


def audit(chapter_id):
    """Require every inventory section to have a source-validated, verified export."""
    inventory = scripts.read(ROOT / 'studio/episodes.yaml')
    episodes = [e for e in inventory['episodes'] if e['chapter_id'] == chapter_id]
    scripts.require(episodes, 'Unknown or empty chapter: ' + chapter_id)
    canonical = scripts.read(ROOT / episodes[0]['source_path'])
    scripts.require([e['section_id'] for e in episodes] == [s['id'] for s in canonical['sections']],
                    'Inventory omits or reorders chapter sections')
    rows, backgrounds, tracks, music_sources = [], set(), set(), set()
    for entry in episodes:
        section = entry['section_id']
        episode = ROOT / 'studio/episodes' / section
        context = scripts.load_context(section)
        script = scripts.read(episode / 'script.yaml')
        scripts.validate(script, context, ready=True)
        scripts.require(scripts.read(episode / 'sources.yaml') == scripts.source_snapshot(context), 'Stale provenance: ' + section)
        scripts.require((episode / 'SCRIPT.md').read_text() == scripts.review_markdown(script, context), 'Stale readable script: ' + section)
        assets = scripts.read(episode / 'assets.yaml')['assets']
        files = {f['path']: f for a in assets for f in a['files']}
        for path, record in files.items():
            scripts.require(digest(ROOT / path) == record['sha256'], 'Changed asset: ' + path)
        for key, seen in [('background_image', backgrounds), ('music_path', tracks)]:
            path = script['render'][key]
            scripts.require(path in files, 'Unregistered render media: ' + path)
            checksum = digest(ROOT / path)
            scripts.require(checksum not in seen, 'Reused chapter media: ' + path)
            seen.add(checksum)
        music = next(a for a in assets if a['kind'] == 'music')
        source = music['source_url']
        scripts.require(source not in music_sources, 'Reused source track: ' + section)
        music_sources.add(source)
        metrics = json.loads((ROOT / 'studio/media' / section / 'narration/metrics.json').read_text())
        scripts.require([m['sentence_id'] for m in metrics] == [s['sentence_id'] for s in script['sentences']], 'Incomplete narration metrics: ' + section)
        for metric, sentence in zip(metrics, script['sentences']):
            scripts.require(metric['engine'] == 'supertonic' and metric['voice'] == 'F1' and metric['speed'] == .95 and metric['seed'] == 42, 'Voice differs from direction: ' + section)
            scripts.require(metric['text'] == (sentence.get('speech_override') or {}).get('text', sentence['sv']), 'Stale narration input: ' + section)
        report = json.loads((episode / 'render.json').read_text())
        scripts.require((report['width'], report['height'], report['fps']) == (1920, 1080, 24),
                        'Unexpected video format: ' + section)
        scripts.require(report['audio']['music_gain_adjustment_db'] == 2,
                        'Music gain differs from accepted setting: ' + section)
        video = ROOT / report['output']
        stem = export_stem(section)
        scripts.require(video == ROOT / 'videos/homebrew' / (stem + '.mp4'), 'Video outside canonical location')
        scripts.require(digest(video) == report['sha256'], 'Changed export: ' + section)
        check = json.loads((episode / 'render-check.json').read_text())
        scripts.require(check['full_decode'] == 'passed' and check['decoded_video_frames'] == report['frames'] and check['source_sentences'] == len(script['sentences']), 'Missing full decode evidence: ' + section)
        scripts.require(check['sha256'] == report['sha256'] and check['output'] == report['output'],
                        'Decode evidence refers to a different export: ' + section)
        if entry['production_status'] != 'complete':
            scripts.require(check.get('encoded_audio_matches_mix'),
                            'New export lacks audio-to-mix verification: ' + section)
        speech = [t for t in report['timeline'] if t['kind'] == 'sentence']
        scripts.require([t['sentence_id'] for t in speech] == [s['sentence_id'] for s in script['sentences']], 'Incomplete timeline: ' + section)
        for sentence, item in zip(script['sentences'], speech):
            with wave.open(str(ROOT / sentence['audio_path'])) as clip:
                duration = clip.getnframes() / clip.getframerate()
            scripts.require(abs(item['speech_start_seconds'] - sentence['start_seconds']) < .000001 and abs(item['speech_end_seconds'] - sentence['end_seconds']) < .000001, 'Stale sentence timing: ' + section)
            scripts.require(abs(item['speech_end_seconds'] - item['speech_start_seconds'] - duration) < .000001, 'Timeline does not use full narration: ' + section)
        credits = ROOT / 'videos/homebrew' / (stem + '.CREDITS.md')
        scripts.require(credits.read_bytes() == (episode / 'CREDITS.md').read_bytes(), 'Stale accompanying credits: ' + section)
        scripts.require(script['title_sv'] in credits.read_text(), 'Incorrect credit title: ' + section)
        rows.append(dict(section_id=section, sentences=len(script['sentences']), seconds=report['seconds'], output=report['output'], sha256=report['sha256'], production_status=entry['production_status']))
        print('PASS:', section, flush=True)
    result = dict(chapter_id=chapter_id, episodes=len(rows), sentences=sum(r['sentences'] for r in rows), distinct_backgrounds=len(backgrounds), distinct_music_tracks=len(tracks), results=rows,
                  review_note='Automated production audit. Whole-video user acceptance is recorded separately per episode.')
    destination = ROOT / 'studio' / (chapter_id + '-audit.json')
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('chapter_id')
    print(json.dumps(audit(parser.parse_args().chapter_id), ensure_ascii=False, indent=2))
