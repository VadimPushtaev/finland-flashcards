"""Audit current batch picture coverage, registered bytes and source identities."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlencode, urlsplit
import unicodedata

import yaml

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'studio/production/remaining'


def read(path):
    return yaml.load(path.read_text(), Loader=getattr(yaml, 'CSafeLoader', yaml.SafeLoader))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(url):
    if not url:
        return None
    parts = urlsplit(url)
    path = unquote(parts.path)
    if 'commons.wikimedia.org' in parts.netloc:
        for marker in ('/wiki/File:', '/wiki/Special:FilePath/'):
            if marker in path:
                title = path.split(marker, 1)[1].replace('_', ' ')
                return 'commons:' + unicodedata.normalize('NFC', title).casefold()
    return parts.netloc.lower() + path + '?' + urlencode(sorted(parse_qsl(parts.query)))


def main():
    queue = read(BASE / 'queue.yaml')['episodes']
    backgrounds, tracks, foregrounds = defaultdict(list), defaultdict(list), defaultdict(list)
    rows, collisions, sentence_ids, checked = [], [], [], {}
    for entry in queue:
        section = entry['section_id']
        episode = ROOT / 'studio/episodes' / section
        script = read(episode / 'script.yaml')
        assets = read(episode / 'assets.yaml')['assets']
        files = {}
        for asset in assets:
            for record in asset['files']:
                path = record['path']
                if path not in checked:
                    actual = digest(ROOT / path)
                    assert actual == record['sha256'], 'Changed registered media: ' + path
                    checked[path] = actual
                assert checked[path] == record['sha256']
                files[path] = asset
        background = next(a for a in assets if a['kind'] == 'background')
        music = next(a for a in assets if a['kind'] == 'music')
        bg = identity(background['source_url'])
        track = identity(music['source_url'])
        assert bg and track, section
        backgrounds[bg].append(section)
        tracks[track].append(section)
        pictures, photos = set(), 0
        for sentence in script['sentences']:
            sentence_ids.append(sentence['sentence_id'])
            image_path = sentence['render_image']
            assert image_path in files and files[image_path]['kind'] == 'foreground', section
            asset = files[image_path]
            pictures.add(image_path)
            if asset.get('visual_type') == 'photograph':
                photos += 1
                source = identity(asset.get('source_url'))
                assert source, 'Missing photo identity: ' + image_path
                foregrounds[source].append(dict(section_id=section, sentence_id=sentence['sentence_id']))
                if source == bg:
                    collisions.append(dict(section_id=section, image=image_path, source=source))
        rows.append(dict(section_id=section, owner=entry['owner'], sentences=len(script['sentences']),
                         pictured_sentences=len(script['sentences']), registered_picture_paths=len(pictures),
                         photographed_slides=photos, background_source=bg, music_source=track,
                         script_sha256=digest(episode / 'script.yaml'), assets_sha256=digest(episode / 'assets.yaml')))
    duplicates = [s for s, count in Counter(sentence_ids).items() if count > 1]
    report = dict(updated_utc=datetime.now(timezone.utc).isoformat(), episodes=len(rows),
                  body_pairs=len(sentence_ids), pictured_body_pairs=sum(r['pictured_sentences'] for r in rows),
                  registered_files_checked=len(checked), distinct_background_sources=len(backgrounds),
                  distinct_music_sources=len(tracks), duplicate_sentence_ids=duplicates,
                  reused_background_sources={k: v for k, v in backgrounds.items() if len(v) > 1},
                  reused_music_sources={k: v for k, v in tracks.items() if len(v) > 1},
                  same_episode_background_foreground_collisions=collisions,
                  cross_episode_photo_reuse={k: v for k, v in foregrounds.items()
                                            if len({x['section_id'] for x in v}) > 1},
                  episodes_current_inputs=rows,
                  limits='Registered bytes/source identities establish integrity and coverage, not meaningful visual distinctness. Conservative geometry/semantic reviews remain separate; useful source-photo reuse across episodes is recorded honestly.')
    (BASE / 'batch-picture-identity-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    assert len(rows) == 88 and len(sentence_ids) == 3730 and not duplicates
    assert len(backgrounds) == len(tracks) == 88 and not collisions
    print('PASS88episodes/3730picturedpairs;', len(checked), 'registered files;88distinct backgrounds/music;0same-episodebackground/foregroundcollisions.')


if __name__ == '__main__':
    main()
