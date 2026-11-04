"""Preserve an already verified owned source as another relevant foreground."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--section', required=True)
parser.add_argument('--index', type=int, required=True)
parser.add_argument('--from-episode', required=True)
parser.add_argument('--from-index', type=int)
parser.add_argument('--caption', required=True)
parser.add_argument('--context', required=True)
args = parser.parse_args()
assert args.section.startswith('hb-c09-') and args.from_episode.startswith('hb-c09-')
root = Path.cwd()
origin = root / 'studio/episodes' / args.from_episode
if args.from_index:
    source_record = origin / f'photo-source-{args.from_index:03}.json'
    record = json.loads(source_record.read_text())
    raw_source = root / record['raw_path']
    assert hashlib.sha256(raw_source.read_bytes()).hexdigest() == record['download_sha256']
else:
    source_record = origin / 'media-sources.json'
    sources = json.loads(source_record.read_text())
    info = sources['photo']
    metadata = info['extmetadata']
    clean = lambda value: re.sub('<[^>]+>', '', value).strip()
    license_name = clean(metadata['LicenseShortName']['value'])
    assert license_name.startswith('CC ') or license_name == 'Public domain'
    record = dict(
        title=sources['photo_title'], imageinfo=info,
        attribution=sources.get('attribution_override') or clean(metadata['Artist']['value']),
        license=license_name,
        license_url=clean(metadata.get('LicenseUrl', {}).get(
            'value', 'https://commons.wikimedia.org/wiki/Commons:Public_domain')),
        description=clean(metadata.get('ImageDescription', {}).get('value', '')),
    )
    raw_source = root / 'studio/media' / args.from_episode / 'sources/background.jpg'
raw = root / 'studio/media' / args.section / 'sources' / f'photo-{args.index:03}.jpg'
assert raw_source != raw
shutil.copy2(raw_source, raw)
record.update(index=args.index, raw_path=str(raw.relative_to(root)),
              caption=args.caption, context=args.context,
              metadata_source=f'Unchanged verified source record: {source_record.relative_to(root)}',
              download_sha256=hashlib.sha256(raw.read_bytes()).hexdigest())
(root / 'studio/episodes' / args.section / f'photo-source-{args.index:03}.json').write_text(
    json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print(args.section, args.index, record['title'])
